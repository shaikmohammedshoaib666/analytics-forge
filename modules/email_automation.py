"""SMTP outbound + IMAP inbound CSV automation for Analytics Forge."""
from __future__ import annotations

import email
import imaplib
import json
import re
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Optional

from config.settings import (
    EMAIL_FROM,
    EMAIL_IMAP_FOLDER,
    EMAIL_IMAP_HOST,
    EMAIL_IMAP_PORT,
    EMAIL_PASSWORD,
    EMAIL_SMTP_HOST,
    EMAIL_SMTP_PORT,
    EMAIL_SMTP_USE_TLS,
    EMAIL_USER,
    INBOUND_DIR,
    RUNS_DIR,
)
from core import db
from core.pack import build_html_pack
from core.pipeline import run_pipeline
from modules.ml_runner import run_model


class EmailConfigError(RuntimeError):
    pass


def email_configured() -> bool:
    return bool(EMAIL_USER and EMAIL_PASSWORD and EMAIL_SMTP_HOST and EMAIL_IMAP_HOST)


def config_status() -> dict[str, Any]:
    return {
        "configured": email_configured(),
        "user": EMAIL_USER or "(missing)",
        "from": EMAIL_FROM or EMAIL_USER or "(missing)",
        "smtp": f"{EMAIL_SMTP_HOST}:{EMAIL_SMTP_PORT}" if EMAIL_SMTP_HOST else "(missing)",
        "imap": f"{EMAIL_IMAP_HOST}:{EMAIL_IMAP_PORT}" if EMAIL_IMAP_HOST else "(missing)",
        "folder": EMAIL_IMAP_FOLDER,
    }


def _require_config() -> None:
    if not email_configured():
        raise EmailConfigError(
            "Email not configured. Set EMAIL_USER, EMAIL_PASSWORD, EMAIL_SMTP_HOST, "
            "EMAIL_IMAP_HOST in .env (Gmail: use an App Password)."
        )


def send_email(
    to_addr: str,
    subject: str,
    body: str,
    attachments: Optional[list[tuple[str, bytes, str]]] = None,
    run_id: Optional[int] = None,
) -> dict[str, Any]:
    """
    Send email via SMTP.
    attachments: list of (filename, content_bytes, mime_main/sub) e.g. ('a.html', b'...', 'text/html')
    """
    _require_config()
    to_addr = (to_addr or "").strip()
    if not to_addr or "@" not in to_addr:
        raise ValueError("Valid recipient email required")

    paths: list[str] = []
    attach_dir = RUNS_DIR / "email_out"
    attach_dir.mkdir(parents=True, exist_ok=True)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM or EMAIL_USER
    msg["To"] = to_addr
    msg.set_content(body)

    for filename, content, mime in attachments or []:
        maintype, _, subtype = mime.partition("/")
        if not subtype:
            maintype, subtype = "application", "octet-stream"
        msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)
        out_path = attach_dir / filename
        out_path.write_bytes(content)
        paths.append(str(out_path))

    context = ssl.create_default_context()
    if EMAIL_SMTP_USE_TLS:
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=60) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
    else:
        with smtplib.SMTP_SSL(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, context=context, timeout=60) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

    eid = db.queue_email(
        to_addr=to_addr,
        subject=subject,
        body=body,
        run_id=run_id,
        direction="out",
        from_addr=EMAIL_FROM or EMAIL_USER,
        attachment_paths=paths,
    )
    db.update_email_status(eid, "sent")
    return {
        "ok": True,
        "email_id": eid,
        "to": to_addr,
        "attachments": [a[0] for a in (attachments or [])],
    }


def build_report_attachments(
    *,
    domain: str,
    source_name: str,
    clean_log: list,
    kpis: dict,
    insights: list,
    charts: list,
    ml_metrics: Optional[dict],
    briefing: str,
    clean_df=None,
) -> list[tuple[str, bytes, str]]:
    html = build_html_pack(
        domain=domain or "generic",
        source_name=source_name or "dataset",
        clean_log=clean_log or [],
        kpis=kpis or {},
        insights=insights or [],
        charts=charts or [],
        ml_metrics=ml_metrics,
        briefing=briefing or "",
    )
    attachments: list[tuple[str, bytes, str]] = [
        ("analytics_forge_report.html", html if isinstance(html, bytes) else html.encode("utf-8"), "text/html"),
    ]
    if clean_df is not None:
        csv_bytes = clean_df.to_csv(index=False).encode("utf-8")
        attachments.append(("clean_data.csv", csv_bytes, "text/csv"))
    return attachments


def send_current_report(
    to_addr: str,
    *,
    domain: str,
    source_name: str,
    clean_log: list,
    kpis: dict,
    insights: list,
    charts: list,
    ml_metrics: Optional[dict],
    briefing: str,
    clean_df=None,
    run_id: Optional[int] = None,
    subject: Optional[str] = None,
    extra_body: str = "",
) -> dict[str, Any]:
    attachments = build_report_attachments(
        domain=domain,
        source_name=source_name,
        clean_log=clean_log,
        kpis=kpis,
        insights=insights,
        charts=charts,
        ml_metrics=ml_metrics,
        briefing=briefing,
        clean_df=clean_df,
    )
    body = (
        "Analytics Forge report\n\n"
        f"Source: {source_name}\n"
        f"Detected field: {domain}\n\n"
        f"{briefing}\n\n"
        "Attachments:\n"
        "- analytics_forge_report.html (full guide pack + dashboard summary)\n"
        "- clean_data.csv (cleaned dataset)\n\n"
        f"{extra_body}"
    )
    return send_email(
        to_addr=to_addr,
        subject=subject or f"[Analytics Forge] Report — {domain} — {source_name}",
        body=body,
        attachments=attachments,
        run_id=run_id,
    )


def _extract_attachments(msg: email.message.Message) -> list[tuple[str, bytes]]:
    files: list[tuple[str, bytes]] = []
    for part in msg.walk():
        if part.get_content_disposition() != "attachment":
            # also accept inline csv sometimes
            filename = part.get_filename()
            if not filename:
                continue
        else:
            filename = part.get_filename()
        if not filename:
            continue
        lower = filename.lower()
        if not lower.endswith((".csv", ".xlsx", ".xls")):
            continue
        payload = part.get_payload(decode=True)
        if payload:
            files.append((filename, payload))
    return files


def _sender_address(msg: email.message.Message) -> str:
    raw = msg.get("From", "")
    match = re.search(r"[\w.+-]+@[\w.-]+", raw)
    return match.group(0) if match else raw


def process_inbound_mailbox(limit: int = 10) -> dict[str, Any]:
    """
    Poll IMAP for unread emails with CSV/Excel attachments.
    For each: run full pipeline (+ baseline ML), email HTML report + clean CSV back to sender.
    """
    _require_config()
    INBOUND_DIR.mkdir(parents=True, exist_ok=True)
    db.init_db()

    results: list[dict[str, Any]] = []
    context = ssl.create_default_context()
    with imaplib.IMAP4_SSL(EMAIL_IMAP_HOST, EMAIL_IMAP_PORT, ssl_context=context) as imap:
        imap.login(EMAIL_USER, EMAIL_PASSWORD)
        imap.select(EMAIL_IMAP_FOLDER)
        status, data = imap.search(None, "UNSEEN")
        if status != "OK":
            return {"ok": False, "message": "IMAP search failed", "processed": []}

        ids = data[0].split() if data and data[0] else []
        ids = ids[-limit:]

        for num in ids:
            status, msg_data = imap.fetch(num, "(RFC822)")
            if status != "OK" or not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            message_id = msg.get("Message-ID") or f"imap-{num.decode() if isinstance(num, bytes) else num}"
            if db.is_imap_processed(message_id):
                imap.store(num, "+FLAGS", "\\Seen")
                continue

            sender = _sender_address(msg)
            subject = msg.get("Subject", "(no subject)")
            files = _extract_attachments(msg)

            # log inbound
            in_id = db.queue_email(
                to_addr=EMAIL_USER,
                subject=subject,
                body=f"Inbound from {sender}; attachments={[f for f, _ in files]}",
                direction="in",
                from_addr=sender,
            )

            if not files:
                db.update_email_status(in_id, "ignored_no_csv")
                db.mark_imap_processed(message_id, in_id, note="no csv/xlsx")
                imap.store(num, "+FLAGS", "\\Seen")
                results.append({"from": sender, "status": "ignored_no_csv", "subject": subject})
                continue

            fname, content = files[0]
            save_path = INBOUND_DIR / fname
            save_path.write_bytes(content)

            try:
                pipe = run_pipeline(file_bytes=content, filename=fname, persist=True)
                ml = None
                try:
                    # baseline model depending on domain
                    domain = pipe["domain"]
                    model_id = "RandomForestRegressor"
                    if domain in {"customer_segmentation"}:
                        model_id = "KMeans"
                    elif domain in {"marketing_campaign", "hospital_medical"}:
                        model_id = "RandomForestClassifier"
                    ml = run_model(pipe["clean_df"], model_id)
                    if ml.get("ok") and pipe.get("run_id"):
                        db.save_ml_run(
                            pipe["run_id"],
                            model_id,
                            metrics=ml.get("metrics") or {},
                            task=str(ml.get("task") or ""),
                            target_col=str(ml.get("target") or ml.get("target_col") or ""),
                        )
                        from core.kpis import compute_kpis

                        pipe["kpis"] = compute_kpis(
                            pipe["clean_df"],
                            domain=domain,
                            ml_metrics=ml.get("metrics"),
                        )
                except Exception as ml_exc:  # noqa: BLE001
                    ml = {"ok": False, "message": str(ml_exc), "error": str(ml_exc), "metrics": {}}

                briefing = pipe.get("briefing") or ""
                if not isinstance(briefing, str):
                    briefing = json.dumps(briefing, default=str)

                send_result = send_current_report(
                    sender,
                    domain=pipe["domain"],
                    source_name=pipe["source_name"],
                    clean_log=pipe.get("clean_log") or [],
                    kpis=pipe.get("kpis") or {},
                    insights=[briefing],
                    charts=[],
                    ml_metrics=ml if ml and ml.get("ok") else None,
                    briefing=briefing,
                    clean_df=pipe["clean_df"],
                    run_id=pipe.get("run_id"),
                    subject=f"[Analytics Forge] Auto-report for {fname}",
                    extra_body="This report was generated automatically from your CSV email.",
                )
                db.update_email_status(in_id, "processed")
                db.mark_imap_processed(message_id, in_id, note=f"replied email_id={send_result.get('email_id')}")
                imap.store(num, "+FLAGS", "\\Seen")
                results.append(
                    {
                        "from": sender,
                        "status": "processed",
                        "file": fname,
                        "domain": pipe["domain"],
                        "run_id": pipe.get("run_id"),
                        "reply_email_id": send_result.get("email_id"),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                db.update_email_status(in_id, f"error:{exc}")
                db.mark_imap_processed(message_id, in_id, note=str(exc))
                imap.store(num, "+FLAGS", "\\Seen")
                results.append({"from": sender, "status": "error", "error": str(exc), "subject": subject})

    return {"ok": True, "processed": results, "count": len(results)}

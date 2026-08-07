"""SQLite persistence for runs, artifacts, and email queue."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

from config.settings import DB_PATH


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                source_name TEXT,
                domain TEXT,
                domain_confidence REAL,
                row_count INTEGER,
                col_count INTEGER,
                notes TEXT
            );
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                name TEXT,
                path TEXT,
                n_rows INTEGER,
                n_cols INTEGER,
                schema_json TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS cleaning_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                step_order INTEGER,
                tool TEXT,
                description TEXT,
                detail TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS kpi_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                domain TEXT,
                created_at TEXT,
                payload TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                chart_type TEXT,
                lib TEXT,
                title TEXT,
                config TEXT,
                pinned INTEGER DEFAULT 0,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS ml_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                model_id TEXT,
                task TEXT,
                target_col TEXT,
                metrics TEXT,
                created_at TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                question TEXT,
                answer TEXT,
                created_at TEXT,
                pinned INTEGER DEFAULT 0,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS dashboard_layouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                name TEXT,
                payload TEXT,
                updated_at TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS email_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                direction TEXT,
                from_addr TEXT,
                to_addr TEXT,
                subject TEXT,
                body TEXT,
                status TEXT,
                attachment_paths TEXT,
                run_id INTEGER,
                created_at TEXT,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS imap_processed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                email_row_id INTEGER,
                note TEXT,
                created_at TEXT
            );
            """
        )


def create_run(
    source_name: str = "",
    domain: str = "generic",
    confidence: float = 0.0,
    notes: str = "",
    row_count: int = 0,
    col_count: int = 0,
    **kwargs: Any,
) -> int:
    """Create an analysis run. Accepts both positional and keyword styles used by callers."""
    domain = kwargs.get("domain", domain)
    source_name = kwargs.get("source_name", source_name)
    row_count = int(kwargs.get("row_count", row_count) or 0)
    col_count = int(kwargs.get("col_count", col_count) or 0)
    notes = kwargs.get("notes", notes)
    confidence = float(kwargs.get("confidence", kwargs.get("domain_confidence", confidence)) or 0.0)
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO runs
            (created_at, source_name, domain, domain_confidence, row_count, col_count, notes)
            VALUES (?,?,?,?,?,?,?)
            """,
            (_utc(), source_name, domain, confidence, row_count, col_count, notes),
        )
        return int(cur.lastrowid)


def save_dataset(
    run_id: int,
    name: str = "",
    path: str = "",
    n_rows: int = 0,
    n_cols: int = 0,
    schema: Optional[dict] = None,
    **kwargs: Any,
) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO datasets (run_id, name, path, n_rows, n_cols, schema_json)
            VALUES (?,?,?,?,?,?)
            """,
            (
                run_id,
                name or kwargs.get("name", ""),
                path,
                n_rows,
                n_cols,
                json.dumps(schema or {}),
            ),
        )
        return int(cur.lastrowid)


def save_cleaning_steps(run_id: int, steps: list[dict[str, Any]]) -> None:
    add_cleaning_steps(run_id, steps)


def add_cleaning_steps(run_id: int, steps: list[dict[str, Any]]) -> None:
    with connect() as conn:
        for i, step in enumerate(steps):
            tool = step.get("tool") or step.get("operation") or ""
            description = step.get("description") or str(step.get("detail", ""))
            detail = step.get("detail", step)
            conn.execute(
                "INSERT INTO cleaning_steps (run_id, step_order, tool, description, detail) VALUES (?,?,?,?,?)",
                (
                    run_id,
                    i,
                    tool,
                    description if isinstance(description, str) else json.dumps(description),
                    json.dumps(detail) if not isinstance(detail, str) else detail,
                ),
            )


def save_kpis(run_id: int, domain: str, kpis: dict[str, Any]) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO kpi_snapshots (run_id, domain, created_at, payload) VALUES (?,?,?,?)",
            (run_id, domain, _utc(), json.dumps(kpis)),
        )


def save_kpi_snapshot(run_id: int, kpis: dict[str, Any], domain: str = "") -> None:
    save_kpis(run_id, domain, kpis)


def save_chart(
    run_id: int,
    chart_type: str = "",
    lib: str = "plotly",
    title: str = "",
    config: Optional[dict] = None,
    **kwargs: Any,
) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO charts (run_id, chart_type, lib, title, config, pinned)
            VALUES (?,?,?,?,?,?)
            """,
            (
                run_id,
                chart_type or kwargs.get("chart_id", ""),
                lib,
                title,
                json.dumps(config or {}),
                int(kwargs.get("pinned", 0)),
            ),
        )
        return int(cur.lastrowid)


def save_ml_run(
    run_id: int,
    model_id: str,
    metrics: Optional[dict[str, Any]] = None,
    task: str = "",
    target_col: str = "",
    **kwargs: Any,
) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO ml_runs (run_id, model_id, task, target_col, metrics, created_at)
            VALUES (?,?,?,?,?,?)
            """,
            (
                run_id,
                model_id,
                task or kwargs.get("task", ""),
                target_col or kwargs.get("target_col", ""),
                json.dumps(metrics or {}),
                _utc(),
            ),
        )
        return int(cur.lastrowid)


def save_insight(run_id: int, question: str, answer: Any, pinned: bool = False) -> int:
    if not isinstance(answer, str):
        answer = json.dumps(answer)
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO insights (run_id, question, answer, created_at, pinned) VALUES (?,?,?,?,?)",
            (run_id, question, answer, _utc(), int(pinned)),
        )
        return int(cur.lastrowid)


def save_dashboard_layout(run_id: int, name: str = "default", layout: Optional[dict] = None) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO dashboard_layouts (run_id, name, payload, updated_at)
            VALUES (?,?,?,?)
            """,
            (run_id, name, json.dumps(layout or {}), _utc()),
        )
        return int(cur.lastrowid)


def queue_email(
    to_addr: str = "",
    subject: str = "",
    body: str = "",
    run_id: int | None = None,
    direction: str = "out",
    from_addr: str = "analytics-forge@local",
    attachment_paths: list[str] | None = None,
    *args: Any,
    **kwargs: Any,
) -> int:
    """
    Queue an outbound email.
    Compatible with:
      queue_email(to, subject, body)
      queue_email(to_addr=..., subject=..., body=..., run_id=...)
      queue_email(direction, to_addr, subject, body, run_id=...)
    """
    # Positional: (to, subject, body) OR (direction, to, subject, body)
    if args:
        if len(args) == 2:
            # called as queue_email(to, subject, body) with body in kwargs? unlikely
            subject = args[0]
            body = args[1]
        elif len(args) >= 3:
            # direction was first positional from older API: queue_email("out", to, subj, body)
            if args[0] in {"out", "in", "inbound", "outbound"} and "@" not in str(args[0]):
                direction = str(args[0])
                to_addr = str(args[1])
                subject = str(args[2])
                body = str(args[3]) if len(args) > 3 else body
            else:
                to_addr = str(args[0]) if not to_addr else to_addr
                subject = str(args[1]) if len(args) > 1 else subject
                body = str(args[2]) if len(args) > 2 else body

    to_addr = kwargs.get("to_addr", to_addr)
    subject = kwargs.get("subject", subject)
    body = kwargs.get("body", body)
    run_id = kwargs.get("run_id", run_id)
    direction = kwargs.get("direction", direction)
    from_addr = kwargs.get("from_addr", from_addr)

    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO email_messages
            (direction, from_addr, to_addr, subject, body, status, attachment_paths, run_id, created_at)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                direction,
                from_addr,
                to_addr,
                subject,
                body,
                "queued",
                json.dumps(attachment_paths or kwargs.get("attachment_paths") or []),
                run_id,
                _utc(),
            ),
        )
        return int(cur.lastrowid)


def list_queued_emails(limit: int = 50) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM email_messages
            WHERE status = 'queued'
            ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def list_emails(limit: int = 50) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM email_messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def update_email_status(email_id: int, status: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE email_messages SET status = ? WHERE id = ?",
            (status, email_id),
        )


def is_imap_processed(message_id: str) -> bool:
    with connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM imap_processed WHERE message_id = ? LIMIT 1",
            (message_id,),
        ).fetchone()
        return row is not None


def mark_imap_processed(message_id: str, email_row_id: int | None = None, note: str = "") -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO imap_processed (message_id, email_row_id, note, created_at)
            VALUES (?,?,?,?)
            """,
            (message_id, email_row_id, note, _utc()),
        )

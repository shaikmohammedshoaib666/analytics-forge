"""
Analytics Forge — Phase 1 Streamlit app.
Upload → Clean → Field → KPIs → Charts → ML → AI → Dashboard → Email
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure project root on path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import SAMPLES_DIR, UPLOADS_DIR
from core import db
from core.classify import classify, load_domains
from core.kpis import compute_kpis
from core.pack import build_html_pack
from core.pipeline import run_pipeline
from modules.ai_guide import ask_ai
from modules.charts import build_chart, load_charts_catalog
from modules.ml_registry import list_models
from modules.ml_runner import run_model
from ui.components import (
    download_df_button,
    download_html_pack_button,
    kpi_cards,
    show_ml_metrics,
)
from ui.session import init_session_state, reset_analysis_state
from ui.theme import inject_css, page_hero

st.set_page_config(
    page_title="Analytics Forge",
    page_icon="⚒️",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = [
    "Upload",
    "Clean",
    "Field",
    "Auto KPIs",
    "Charts",
    "ML Studio",
    "Ask / AI",
    "Dashboard",
    "Email",
]


def ensure_samples() -> None:
    """Create sample CSVs if missing (also ships with repo samples)."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    pdm = SAMPLES_DIR / "sample_predictive_maintenance.csv"
    sales = SAMPLES_DIR / "sample_sales.csv"
    if not pdm.exists():
        # Minimal regenerate
        rows = []
        for mid in range(1, 6):
            for h in range(8):
                rows.append(
                    {
                        "machine_id": f"M-{mid:03d}",
                        "timestamp": f"2024-01-0{1 + h // 4} {h % 4 * 6:02d}:00:00",
                        "temperature": 70 + mid * 2 + h,
                        "vibration": 0.3 + mid * 0.05 + h * 0.08,
                        "pressure": 102 - h * 0.8,
                        "failure": 1 if h == 7 and mid % 2 else 0,
                        "rul": 0 if h == 7 and mid % 2 else 200 - h * 10,
                    }
                )
        pd.DataFrame(rows).to_csv(pdm, index=False)
    if not sales.exists():
        import numpy as np

        rng = np.random.default_rng(42)
        regions = ["North", "South", "East", "West"]
        cats = ["Electronics", "Furniture", "Office Supplies"]
        rows = []
        for d in range(1, 31):
            rows.append(
                {
                    "order_date": f"2024-01-{d:02d}",
                    "region": regions[d % 4],
                    "category": cats[d % 3],
                    "revenue": float(rng.integers(100, 5000)),
                    "units": int(rng.integers(1, 30)),
                }
            )
        pd.DataFrame(rows).to_csv(sales, index=False)


def apply_pipeline_to_state(result: dict) -> None:
    st.session_state.messy_df = result["messy_df"]
    st.session_state.clean_df = result["clean_df"]
    st.session_state.clean_log = result["clean_log"]
    st.session_state.source_name = result["source_name"]
    st.session_state.domain = result["domain"]
    st.session_state.classification = result["classification"]
    st.session_state.kpis = result["kpis"]
    st.session_state.briefing = result["briefing"]
    st.session_state.schema = result["schema"]
    st.session_state.run_id = result.get("run_id")
    st.session_state.pipeline_done = True
    st.session_state.dashboard_insights = [result["briefing"]]


def page_upload() -> None:
    page_hero(
        "Upload",
        "Drop your CSV/Excel or try a sample. Any industry file works — not only sales or PdM.",
        st.session_state.get("domain"),
    )
    st.write("Load a CSV/Excel file or start with a built-in sample.")

    ensure_samples()
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    c1, c2 = st.columns(2)
    with c1:
        uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls", "tsv"])
        if uploaded is not None:
            data = uploaded.getvalue()
            dest = UPLOADS_DIR / uploaded.name
            dest.write_bytes(data)
            if st.button("Run pipeline on upload", type="primary", key="run_upload"):
                with st.spinner("Running pipeline…"):
                    result = run_pipeline(
                        file_bytes=data,
                        filename=uploaded.name,
                        domain_override=st.session_state.domain_override,
                        persist=True,
                    )
                apply_pipeline_to_state(result)
                st.success(f"Loaded **{uploaded.name}** · domain `{result['domain']}`")
                st.dataframe(result["clean_df"].head(20), use_container_width=True)

    with c2:
        sample_choice = st.selectbox(
            "Or use sample data",
            [
                "sample_predictive_maintenance.csv",
                "sample_sales.csv",
            ],
        )
        if st.button("Load sample & run pipeline", key="run_sample"):
            path = SAMPLES_DIR / sample_choice
            with st.spinner("Running pipeline…"):
                result = run_pipeline(
                    source=path,
                    domain_override=st.session_state.domain_override,
                    persist=True,
                )
            apply_pipeline_to_state(result)
            st.success(f"Sample loaded · domain `{result['domain']}`")
            st.dataframe(result["clean_df"].head(20), use_container_width=True)

    if st.session_state.pipeline_done:
        st.divider()
        st.subheader("Current dataset")
        st.write(
            f"**{st.session_state.source_name}** — "
            f"{len(st.session_state.clean_df):,} rows × {st.session_state.clean_df.shape[1]} cols · "
            f"domain `{st.session_state.domain}` · run_id `{st.session_state.run_id}`"
        )
        if st.button("Reset analysis", key="reset_all"):
            reset_analysis_state()
            st.rerun()


def page_clean() -> None:
    page_hero(
        "Clean",
        "Messy vs clean side-by-side — see exactly what pandas cleaned for you.",
        st.session_state.get("domain"),
    )
    if st.session_state.messy_df is None:
        st.warning("Upload or load a sample first.")
        return

    left, right = st.columns(2)
    with left:
        st.subheader("Messy (raw)")
        st.dataframe(st.session_state.messy_df.head(50), use_container_width=True)
        st.caption(f"{len(st.session_state.messy_df):,} rows")
        download_df_button(
            st.session_state.messy_df,
            "Download raw CSV",
            "messy.csv",
            key="dl_messy",
        )
    with right:
        st.subheader("Clean")
        st.dataframe(st.session_state.clean_df.head(50), use_container_width=True)
        st.caption(f"{len(st.session_state.clean_df):,} rows")
        download_df_button(
            st.session_state.clean_df,
            "Download clean CSV",
            "clean.csv",
            key="dl_clean",
        )

    st.subheader("Cleaning log (pandas ops)")
    log = st.session_state.clean_log or []
    st.dataframe(pd.DataFrame(log), use_container_width=True)


def page_field() -> None:
    page_hero(
        "Field detection",
        "Auto-detects warehouse, sales, PdM, hospital, and more — then suggests models & next steps.",
        st.session_state.get("domain"),
    )
    if st.session_state.clean_df is None:
        st.warning("Upload or load a sample first.")
        return

    domains = load_domains()
    labels = {k: v.get("label", k) for k, v in domains.items()}
    clf = st.session_state.classification or classify(st.session_state.clean_df)

    st.write(f"**Auto-detected:** `{clf.get('domain')}` — {clf.get('label')}")
    scores = clf.get("scores") or {}
    score_df = (
        pd.DataFrame(
            [{"domain": d, "label": labels.get(d, d), "score": round(s, 3)} for d, s in scores.items()]
        )
        .sort_values("score", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(score_df, use_container_width=True)

    override = st.selectbox(
        "Override domain",
        options=list(domains.keys()),
        format_func=lambda x: f"{labels.get(x, x)} ({x})",
        index=list(domains.keys()).index(st.session_state.domain)
        if st.session_state.domain in domains
        else list(domains.keys()).index("generic"),
    )
    if st.button("Apply domain override", type="primary"):
        st.session_state.domain_override = override
        clf2 = classify(st.session_state.clean_df, override=override)
        st.session_state.classification = clf2
        st.session_state.domain = clf2["domain"]
        st.session_state.kpis = compute_kpis(
            st.session_state.clean_df,
            domain=clf2["domain"],
            ml_metrics=(st.session_state.ml_result or {}).get("metrics"),
        )
        from core.briefing import build_briefing

        st.session_state.briefing = build_briefing(
            clf2["domain"],
            st.session_state.clean_df.shape,
            kpis=st.session_state.kpis,
            classification=clf2,
        )
        st.success(f"Domain set to `{clf2['domain']}`")
        st.rerun()

    st.info("Recommended models: " + ", ".join(clf.get("recommended_models") or []))


def page_kpis() -> None:
    page_hero(
        "Auto KPIs",
        "Scoreboard numbers for your detected field — including sales-on-latest-day style metrics.",
        st.session_state.get("domain"),
    )
    if st.session_state.clean_df is None:
        st.warning("Upload or load a sample first.")
        return

    if st.button("Recompute KPIs"):
        ml_m = None
        if st.session_state.ml_result and st.session_state.ml_result.get("ok"):
            ml_m = st.session_state.ml_result
        st.session_state.kpis = compute_kpis(
            st.session_state.clean_df,
            domain=st.session_state.domain,
            ml_metrics=ml_m,
        )

    kpi_cards(st.session_state.kpis or {})
    st.subheader("All KPIs")
    rows = []
    for kid, item in (st.session_state.kpis or {}).items():
        if isinstance(item, dict):
            rows.append(
                {
                    "id": kid,
                    "name": item.get("name"),
                    "value": item.get("value"),
                    "formula": item.get("formula", ""),
                }
            )
        else:
            rows.append({"id": kid, "name": kid, "value": item, "formula": ""})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    if st.session_state.domain == "predictive_maintenance" and st.session_state.ml_result:
        st.subheader("PdM ML metrics")
        show_ml_metrics(st.session_state.ml_result)

    st.markdown(st.session_state.briefing or "")


def page_charts() -> None:
    page_hero(
        "Charts",
        "Build colorful views, download one chart, or pin several into your final dashboard.",
        st.session_state.get("domain"),
    )
    if st.session_state.clean_df is None:
        st.warning("Upload or load a sample first.")
        return

    df = st.session_state.clean_df
    catalog = load_charts_catalog()
    chart_types = list(catalog.keys())
    cols = list(df.columns)

    c1, c2, c3 = st.columns(3)
    with c1:
        chart_type = st.selectbox("Chart type", chart_types, format_func=lambda t: catalog[t].get("label", t))
    with c2:
        libs = catalog.get(chart_type, {}).get("libs", ["plotly", "matplotlib", "seaborn"])
        lib = st.selectbox("Library", libs)
    with c3:
        title = st.text_input("Title", value=f"{catalog[chart_type].get('label', chart_type)}")

    needs = catalog.get(chart_type, {}).get("needs", [])
    x = y = names = values = None
    r1, r2 = st.columns(2)
    with r1:
        if "x" in needs or chart_type in ("bar", "line", "scatter", "histogram", "box", "area"):
            x = st.selectbox("X column", cols, key="chart_x")
        if "names" in needs:
            names = st.selectbox("Names", cols, key="chart_names")
    with r2:
        num_cols = df.select_dtypes("number").columns.tolist() or cols
        if "y" in needs or chart_type in ("bar", "line", "scatter", "box", "area"):
            y = st.selectbox("Y column", num_cols if num_cols else cols, key="chart_y")
        if "values" in needs:
            values = st.selectbox("Values", num_cols if num_cols else cols, key="chart_vals")

    if st.button("Render chart", type="primary"):
        try:
            fig = build_chart(
                df,
                chart_type=chart_type,
                lib=lib,
                x=x,
                y=y,
                names=names,
                values=values,
                title=title,
            )
            st.session_state["_last_fig"] = fig
            st.session_state["_last_fig_meta"] = {
                "chart_type": chart_type,
                "lib": lib,
                "title": title,
                "x": x,
                "y": y,
                "names": names,
                "values": values,
            }
        except Exception as exc:
            st.error(str(exc))

    fig = st.session_state.get("_last_fig")
    meta = st.session_state.get("_last_fig_meta")
    if fig is not None and meta:
        if meta.get("lib") == "plotly":
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.pyplot(fig)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("Add to dashboard"):
                entry = {**meta}
                st.session_state.dashboard_charts.append(entry)
                if st.session_state.run_id:
                    db.save_chart(
                        st.session_state.run_id,
                        chart_type=meta["chart_type"],
                        lib=meta["lib"],
                        title=meta["title"],
                        config=meta,
                    )
                st.success("Added to dashboard")
        with b2:
            # download: plotly html or note
            if meta.get("lib") == "plotly":
                try:
                    html_bytes = fig.to_html(include_plotlyjs="cdn").encode("utf-8")
                    st.download_button(
                        "Download chart HTML",
                        data=html_bytes,
                        file_name=f"{meta['chart_type']}_chart.html",
                        mime="text/html",
                        key="dl_chart_html",
                    )
                except Exception:
                    st.caption("Chart download unavailable for this figure.")


def page_ml() -> None:
    page_hero(
        "ML Studio",
        "Pick analyst / I4.0 models and read R², RMSE, MAE, accuracy — colorful metrics strip included.",
        st.session_state.get("domain"),
    )
    if st.session_state.clean_df is None:
        st.warning("Upload or load a sample first.")
        return

    models = list_models(include_soft_fail=True)
    domain = st.session_state.domain
    domains = load_domains()
    recommended = domains.get(domain, {}).get("recommended_models", [])
    model_ids = list(models.keys())
    # put recommended first
    model_ids = [m for m in recommended if m in models] + [m for m in model_ids if m not in recommended]

    model_id = st.selectbox(
        "Model",
        model_ids,
        format_func=lambda m: f"{models[m].get('label', m)} [{models[m].get('task')}]"
        + (" ★" if m in recommended else ""),
    )
    meta = models[model_id]
    st.caption(meta.get("note") or f"Library: {meta.get('library')}")

    df = st.session_state.clean_df
    cols = list(df.columns)
    target = st.selectbox(
        "Target (optional — auto if blank-ish)",
        options=["(auto)"] + cols,
    )
    target_arg = None if target == "(auto)" else target

    if st.button("Run model", type="primary"):
        with st.spinner("Training…"):
            result = run_model(df, model_id=model_id, target=target_arg)
        st.session_state.ml_result = result
        if result.get("ok"):
            # refresh KPIs with ML metrics
            st.session_state.kpis = compute_kpis(
                df, domain=domain, ml_metrics=result
            )
            if st.session_state.run_id:
                db.save_ml_run(
                    st.session_state.run_id,
                    model_id=model_id,
                    task=result.get("task", ""),
                    target_col=str(result.get("target") or ""),
                    metrics=result.get("metrics") or {},
                )
            st.success("Model finished")
        else:
            st.error(result.get("error", "Failed"))

    show_ml_metrics(st.session_state.ml_result)

    if st.session_state.ml_result and st.session_state.ml_result.get("ok"):
        preview = st.session_state.ml_result.get("predictions_preview")
        if preview is not None:
            st.subheader("Predictions preview")
            st.dataframe(preview, use_container_width=True)
            download_df_button(
                preview,
                "Download predictions CSV",
                "ml_predictions_preview.csv",
                key="dl_preds",
            )

        # Adaptive PdM tables
        if domain == "predictive_maintenance":
            st.subheader("Adaptive PdM view")
            metrics = st.session_state.ml_result.get("metrics") or {}
            mcols = st.columns(3)
            if "r2" in metrics:
                mcols[0].metric("R²", f"{metrics['r2']:.4f}")
            if "rmse" in metrics:
                mcols[1].metric("RMSE", f"{metrics['rmse']:.4f}")
            if "mae" in metrics:
                mcols[2].metric("MAE", f"{metrics['mae']:.4f}")
            if "accuracy" in metrics:
                mcols[0].metric("Accuracy", f"{metrics['accuracy']:.4f}")

            sensor_cols = [
                c
                for c in df.columns
                if str(c).lower() in {"temperature", "vibration", "pressure", "rul", "failure"}
            ]
            if sensor_cols:
                st.dataframe(df[sensor_cols].describe(), use_container_width=True)
            if "machine_id" in [c.lower() for c in df.columns]:
                mid = next(c for c in df.columns if str(c).lower() == "machine_id")
                fail_col = next(
                    (c for c in df.columns if str(c).lower() == "failure"), None
                )
                if fail_col:
                    agg = (
                        df.groupby(mid)
                        .agg(
                            rows=(mid, "count"),
                            failures=(fail_col, "sum"),
                            avg_temp=(
                                next(
                                    (c for c in df.columns if "temp" in str(c).lower()),
                                    fail_col,
                                ),
                                "mean",
                            ),
                        )
                        .reset_index()
                    )
                    st.dataframe(agg, use_container_width=True)


def page_ai() -> None:
    page_hero(
        "Ask / AI Guide",
        "Ask in plain English — e.g. “what are sales today?” — and get guided next steps.",
        st.session_state.get("domain"),
    )
    if st.session_state.clean_df is None:
        st.warning("Upload or load a sample first.")
        return

    from modules.ai_guide import gemini_configured, openai_configured, provider_status

    status = provider_status()
    c1, c2, c3 = st.columns(3)
    c1.metric("Gemini", "Ready" if status["gemini"] else "No key")
    c2.metric("OpenAI", "Ready" if status["openai"] else "No key")
    c3.metric("Offline", "Always on")

    if status["gemini"] or status["openai"]:
        st.success("Cloud AI available — pick a provider below.")
    else:
        st.warning(
            "No cloud AI keys yet — offline answers still work.\n\n"
            "Add to `.env` (local) or Streamlit Secrets (cloud):\n"
            "`GEMINI_API_KEY=...` (free tier) and/or `OPENAI_API_KEY=...`"
        )

    selectable = ["auto"]
    if gemini_configured():
        selectable.append("gemini")
    if openai_configured():
        selectable.append("openai")
    selectable.append("offline")
    provider = st.selectbox("AI provider", selectable, index=0, help="Gemini often has a free tier.")

    st.caption(
        "Try: `which model did I use?` · `show kpis` · `which machine will fail?` · `how to reduce machine failure?`"
    )
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about your data…")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        result = ask_ai(
            prompt,
            domain=st.session_state.domain,
            schema=st.session_state.schema,
            kpis=st.session_state.kpis,
            df=st.session_state.clean_df,
            briefing=st.session_state.briefing or "",
            history=st.session_state.chat_history[:-1],
            ml_result=st.session_state.ml_result,
            provider=provider,
        )
        answer = result.get("answer", "")
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
            st.caption(f"source: {result.get('source')}")


def page_dashboard() -> None:
    page_hero(
        "Dashboard",
        "Your selected charts + insights. Auto KPIs stay on the right. Download the final pack anytime.",
        st.session_state.get("domain"),
    )
    if st.session_state.clean_df is None:
        st.warning("Upload or load a sample first.")
        return

    center, right = st.columns([3, 1])
    with right:
        st.subheader("Auto KPIs")
        kpi_cards(st.session_state.kpis or {}, max_cards=10)

    with center:
        st.subheader("Insights")
        for insight in st.session_state.dashboard_insights or [st.session_state.briefing]:
            st.markdown(insight or "_No insights yet._")

        st.subheader("Charts")
        charts = st.session_state.dashboard_charts or []
        if not charts:
            st.info("Add charts from the Charts page.")
        df = st.session_state.clean_df
        for i, meta in enumerate(charts):
            st.markdown(f"**{meta.get('title', meta.get('chart_type'))}**")
            try:
                fig = build_chart(
                    df,
                    chart_type=meta.get("chart_type", "bar"),
                    lib=meta.get("lib", "plotly"),
                    x=meta.get("x"),
                    y=meta.get("y"),
                    names=meta.get("names"),
                    values=meta.get("values"),
                    title=meta.get("title"),
                )
                if meta.get("lib") == "plotly":
                    st.plotly_chart(fig, use_container_width=True, key=f"dash_plotly_{i}")
                else:
                    st.pyplot(fig)
            except Exception as exc:
                st.warning(f"Could not render chart: {exc}")

        if st.session_state.domain == "predictive_maintenance" and st.session_state.ml_result:
            st.subheader("PdM model quality")
            show_ml_metrics(st.session_state.ml_result)

    st.divider()
    pack = build_html_pack(
        domain=st.session_state.domain,
        source_name=st.session_state.source_name or "",
        clean_log=st.session_state.clean_log,
        kpis=st.session_state.kpis,
        insights=st.session_state.dashboard_insights,
        charts=st.session_state.dashboard_charts,
        ml_metrics=st.session_state.ml_result,
        briefing=st.session_state.briefing or "",
    )
    download_html_pack_button(pack, key="dash_pack")
    if st.session_state.run_id and st.button("Save dashboard layout to SQLite"):
        db.save_dashboard_layout(
            st.session_state.run_id,
            name="default",
            layout={
                "charts": st.session_state.dashboard_charts,
                "insights": st.session_state.dashboard_insights,
            },
        )
        st.success("Layout saved")


def page_email() -> None:
    page_hero(
        "Email automation",
        "Send the report pack now, or auto-process inbound CSV emails and reply with insights.",
        st.session_state.get("domain"),
    )
    st.caption(
        "Send the dashboard/report pack to any email. "
        "Or click Check inbox: unread emails with CSV/Excel are cleaned, analyzed, and auto-replied with the report."
    )

    from modules.email_automation import (
        EmailConfigError,
        config_status,
        email_configured,
        process_inbound_mailbox,
        send_current_report,
    )

    status = config_status()
    if status["configured"]:
        st.success(f"Email ready · SMTP {status['smtp']} · IMAP {status['imap']} · as {status['from']}")
    else:
        st.warning(
            "Email not configured yet. Add these to `.env` then restart Streamlit:\n\n"
            "EMAIL_USER=you@gmail.com\n"
            "EMAIL_PASSWORD=your_app_password\n"
            "EMAIL_FROM=you@gmail.com\n"
            "EMAIL_SMTP_HOST=smtp.gmail.com\n"
            "EMAIL_SMTP_PORT=587\n"
            "EMAIL_IMAP_HOST=imap.gmail.com\n"
            "EMAIL_IMAP_PORT=993\n\n"
            "Gmail: enable 2FA → create an App Password (not your normal password)."
        )

    st.subheader("1) Send current report to me / anyone")
    if not st.session_state.get("pipeline_done"):
        st.info("Load and clean a dataset first (Upload), then you can email the report.")
    with st.form("email_send_form"):
        to_addr = st.text_input("Recipient email", placeholder="you@gmail.com")
        subject = st.text_input(
            "Subject",
            value=f"[Analytics Forge] Report — {st.session_state.get('domain') or 'analytics'}",
        )
        note = st.text_area("Extra note (optional)", value="")
        send_clicked = st.form_submit_button("Send report now (HTML pack + clean CSV)", type="primary")
        if send_clicked:
            if not st.session_state.get("pipeline_done"):
                st.error("No analysis loaded. Upload/clean data first.")
            elif not to_addr.strip():
                st.error("Enter a recipient email.")
            else:
                try:
                    briefing = st.session_state.briefing or ""
                    if not isinstance(briefing, str):
                        import json as _json

                        briefing = _json.dumps(briefing, default=str)
                    result = send_current_report(
                        to_addr.strip(),
                        domain=st.session_state.domain or "generic",
                        source_name=st.session_state.source_name or "dataset",
                        clean_log=st.session_state.clean_log or [],
                        kpis=st.session_state.kpis or {},
                        insights=st.session_state.dashboard_insights or [],
                        charts=st.session_state.dashboard_charts or [],
                        ml_metrics=st.session_state.ml_result,
                        briefing=briefing,
                        clean_df=st.session_state.clean_df,
                        run_id=st.session_state.run_id,
                        subject=subject,
                        extra_body=note,
                    )
                    st.success(
                        f"Sent to {result['to']} (email_id={result['email_id']}). "
                        f"Attachments: {', '.join(result.get('attachments') or [])}"
                    )
                except EmailConfigError as exc:
                    st.error(str(exc))
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Send failed: {exc}")

    st.subheader("2) Inbound automation (CSV email → auto report reply)")
    st.markdown(
        "Email a **CSV or Excel** file to your configured inbox (`EMAIL_USER`). "
        "Then click the button below. Forge will: clean → detect field → KPIs → baseline ML → "
        "email the HTML report + clean CSV back to the sender."
    )
    if st.button("Check inbox & auto-process unread CSV emails", type="primary"):
        try:
            with st.spinner("Checking IMAP inbox..."):
                out = process_inbound_mailbox(limit=10)
            st.success(f"Processed {out.get('count', 0)} message(s).")
            if out.get("processed"):
                st.dataframe(pd.DataFrame(out["processed"]), use_container_width=True)
            else:
                st.info("No new unread CSV emails found.")
        except EmailConfigError as exc:
            st.error(str(exc))
        except Exception as exc:  # noqa: BLE001
            st.error(f"Inbox processing failed: {exc}")

    st.subheader("Email log (SQLite)")
    try:
        rows = db.list_emails(100)
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.info("No emails logged yet.")
    except Exception:
        st.info("Email log empty.")


def main() -> None:
    init_session_state()
    inject_css()
    db.init_db()
    ensure_samples()

    st.sidebar.markdown("### ⚒️ Analytics Forge")
    st.sidebar.caption("Colorful · reusable analytics OS")
    page = st.sidebar.radio("Navigate", PAGES, index=PAGES.index(st.session_state.page) if st.session_state.page in PAGES else 0)
    st.session_state.page = page

    if st.session_state.pipeline_done:
        st.sidebar.success(
            f"{st.session_state.source_name or 'dataset'}\n\n"
            f"`{st.session_state.domain}` · {len(st.session_state.clean_df):,} rows"
        )
    else:
        st.sidebar.info("Load data on Upload to begin.")

    try:
        from modules.email_automation import email_configured as _email_ok

        st.sidebar.caption("Email: configured" if _email_ok() else "Email: set .env to enable send/inbox")
    except Exception:
        pass

    if page == "Upload":
        page_upload()
    elif page == "Clean":
        page_clean()
    elif page == "Field":
        page_field()
    elif page == "Auto KPIs":
        page_kpis()
    elif page == "Charts":
        page_charts()
    elif page == "ML Studio":
        page_ml()
    elif page == "Ask / AI":
        page_ai()
    elif page == "Dashboard":
        page_dashboard()
    elif page == "Email":
        page_email()


if __name__ == "__main__":
    main()

"""End-to-end analytics pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd

from core import db
from core.briefing import build_briefing
from core.classify import classify
from core.clean import clean_dataframe
from core.ingest import load_bytes, load_file, schema_summary
from core.kpis import compute_kpis


def run_pipeline(
    source: Optional[Union[str, Path]] = None,
    raw_df: Optional[pd.DataFrame] = None,
    filename: str = "dataset",
    file_bytes: Optional[bytes] = None,
    domain_override: Optional[str] = None,
    persist: bool = True,
    ml_metrics: Optional[dict] = None,
) -> dict[str, Any]:
    """
    Orchestrate ingest -> clean -> classify -> kpis, optionally save to SQLite.
    """
    if raw_df is not None:
        messy = raw_df.copy()
        source_name = filename
    elif file_bytes is not None:
        messy = load_bytes(file_bytes, filename)
        source_name = filename
    elif source is not None:
        messy = load_file(source)
        source_name = Path(source).name
    else:
        raise ValueError("Provide source, raw_df, or file_bytes")

    clean_df, clean_log = clean_dataframe(messy)
    classification = classify(clean_df, override=domain_override)
    domain = classification["domain"]
    kpis = compute_kpis(clean_df, domain=domain, ml_metrics=ml_metrics)
    briefing = build_briefing(
        domain,
        clean_df.shape,
        kpis=kpis,
        classification=classification,
    )
    schema = schema_summary(clean_df)

    result: dict[str, Any] = {
        "source_name": source_name,
        "messy_df": messy,
        "clean_df": clean_df,
        "clean_log": clean_log,
        "classification": classification,
        "domain": domain,
        "kpis": kpis,
        "briefing": briefing,
        "schema": schema,
        "run_id": None,
    }

    if persist:
        db.init_db()
        run_id = db.create_run(
            domain=domain,
            source_name=source_name,
            row_count=len(clean_df),
            col_count=clean_df.shape[1],
            notes="pipeline",
        )
        db.save_dataset(
            run_id,
            name=source_name,
            path=str(source) if source else "",
            n_rows=len(clean_df),
            n_cols=clean_df.shape[1],
            schema=schema,
        )
        db.save_cleaning_steps(run_id, clean_log)
        db.save_kpis(run_id, domain, kpis)
        db.save_insight(run_id, "briefing", briefing)
        result["run_id"] = run_id

    return result

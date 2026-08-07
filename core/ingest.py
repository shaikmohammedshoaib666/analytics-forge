"""Load CSV / Excel files into DataFrames."""
from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd


PathLike = Union[str, Path]


def _suffix(path: PathLike) -> str:
    return Path(path).suffix.lower()


def load_file(path: PathLike, **kwargs) -> pd.DataFrame:
    """Load a CSV or Excel file into a DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt", ".tsv"}:
        sep = "\t" if suffix == ".tsv" else kwargs.pop("sep", ",")
        return pd.read_csv(path, sep=sep, **kwargs)
    if suffix in {".xlsx", ".xls", ".xlsm"}:
        return pd.read_excel(path, **kwargs)
    if suffix == ".parquet":
        return pd.read_parquet(path, **kwargs)

    # Fallback: try CSV
    try:
        return pd.read_csv(path, **kwargs)
    except Exception as exc:
        raise ValueError(f"Unsupported file type: {suffix}") from exc


def load_bytes(data: bytes, filename: str, **kwargs) -> pd.DataFrame:
    """Load uploaded bytes by filename extension."""
    from io import BytesIO

    bio = BytesIO(data)
    suffix = Path(filename).suffix.lower()
    if suffix in {".csv", ".txt", ".tsv"}:
        sep = "\t" if suffix == ".tsv" else kwargs.pop("sep", ",")
        return pd.read_csv(bio, sep=sep, **kwargs)
    if suffix in {".xlsx", ".xls", ".xlsm"}:
        return pd.read_excel(bio, **kwargs)
    if suffix == ".parquet":
        return pd.read_parquet(bio, **kwargs)
    bio.seek(0)
    return pd.read_csv(bio, **kwargs)


def schema_summary(df: pd.DataFrame) -> dict:
    """Lightweight schema for persistence / AI context."""
    cols = {}
    for c in df.columns:
        s = df[c]
        cols[str(c)] = {
            "dtype": str(s.dtype),
            "nulls": int(s.isna().sum()),
            "nunique": int(s.nunique(dropna=True)),
            "sample": [str(x) for x in s.dropna().head(3).tolist()],
        }
    return {"columns": cols, "n_rows": int(len(df)), "n_cols": int(df.shape[1])}

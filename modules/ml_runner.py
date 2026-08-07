"""Run sklearn (and soft-fail) models with heuristic feature/target selection."""
from __future__ import annotations

import importlib
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from modules.ml_registry import get_model


TARGET_PRIORITY_REG = [
    "rul",
    "remaining_useful_life",
    "revenue",
    "sales",
    "amount",
    "units",
    "price",
    "score",
    "value",
    "target",
    "y",
]
TARGET_PRIORITY_CLF = [
    "failure",
    "failed",
    "churn",
    "converted",
    "conversion",
    "label",
    "target",
    "class",
    "status",
]


def _resolve_class(dotted: str):
    module_path, _, cls_name = dotted.rpartition(".")
    mod = importlib.import_module(module_path)
    return getattr(mod, cls_name)


def pick_target(df: pd.DataFrame, task: str) -> Optional[str]:
    cols_lower = {str(c).lower(): c for c in df.columns}
    priority = TARGET_PRIORITY_CLF if task == "classification" else TARGET_PRIORITY_REG
    for name in priority:
        if name in cols_lower:
            return cols_lower[name]
    nums = df.select_dtypes(include=[np.number]).columns.tolist()
    if task == "classification":
        # low-cardinality numeric or object
        for c in df.columns:
            nun = df[c].nunique(dropna=True)
            if 2 <= nun <= 10:
                return c
        return None
    if nums:
        # prefer last numeric as target heuristic
        return nums[-1]
    return None


def pick_features(df: pd.DataFrame, target: str) -> list[str]:
    feats = []
    for c in df.columns:
        if c == target:
            continue
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            continue
        # skip high-cardinality ids
        cl = str(c).lower()
        if cl.endswith("_id") or cl in {"id", "uuid", "guid"}:
            if df[c].nunique() > max(50, len(df) * 0.5):
                continue
        feats.append(c)
    return feats


def _build_estimator(model_id: str, meta: dict):
    dotted = meta.get("class") or meta.get("estimator") or ""
    library = (meta.get("library") or "").lower()
    if (
        meta.get("soft_fail")
        or meta.get("requires_license")
        or dotted in {"stub", "gurobipy", "ortools"}
        or model_id in {"gurobi_stub", "OptimizationGurobi", "ORTools"}
        or library in {"gurobipy", "ortools"}
    ):
        raise RuntimeError(
            f"{model_id} is optional / not executable in Phase 1 (soft-fail)."
        )
    if library == "prophet" or model_id.lower() == "prophet" or "prophet" in dotted.lower():
        try:
            from prophet import Prophet  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "Prophet is not installed. pip install prophet (optional)."
            ) from exc
        raise RuntimeError(
            "Prophet forecasting requires a date + y frame; use sklearn models in Phase 1 ML Studio."
        )
    if not dotted or "." not in dotted:
        raise RuntimeError(f"Model {model_id} has no importable estimator class.")
    # Default params for common models that need them
    params = dict(meta.get("default_params") or {})
    if model_id == "KMeans" and "n_clusters" not in params:
        params["n_clusters"] = 3
    if model_id == "LogisticRegression" and "max_iter" not in params:
        params["max_iter"] = 1000
    cls = _resolve_class(dotted)
    try:
        return cls(**params)
    except TypeError:
        return cls()


def run_model(
    df: pd.DataFrame,
    model_id: str,
    target: Optional[str] = None,
    features: Optional[list[str]] = None,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict[str, Any]:
    """
    Train/evaluate a catalog model.
    Returns metrics (R2/RMSE/MAE or accuracy), predictions preview, and metadata.
    """
    meta = get_model(model_id)
    if not meta:
        return {"ok": False, "error": f"Unknown model: {model_id}"}

    task = meta.get("task", "regression")

    if task == "clustering":
        return _run_clustering(df, model_id, meta, features)

    try:
        estimator = _build_estimator(model_id, meta)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "model_id": model_id, "task": task}

    tgt = target or pick_target(df, task)
    if not tgt or tgt not in df.columns:
        return {"ok": False, "error": "Could not determine target column.", "task": task}

    feats = features or pick_features(df, tgt)
    if not feats:
        return {"ok": False, "error": "No usable feature columns.", "target": tgt}

    work = df[feats + [tgt]].copy()
    work = work.dropna(subset=[tgt])
    if len(work) < 10:
        return {"ok": False, "error": "Need at least 10 rows after dropping null targets."}

    X = work[feats]
    y = work[tgt]
    if task == "classification":
        # ensure y is suitable
        if y.dtype == float and y.nunique() > 20:
            return {
                "ok": False,
                "error": "Target looks continuous; pick a classifier target or use a regressor.",
                "target": tgt,
            }
    else:
        y = pd.to_numeric(y, errors="coerce")
        mask = y.notna()
        X, y = X.loc[mask], y.loc[mask]

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]

    pre = ColumnTransformer(
        transformers=[
            (
                "num",
                SimpleImputer(strategy="median"),
                num_cols,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        (
                            "oh",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                cat_cols,
            ),
        ],
        remainder="drop",
    )

    # sklearn < 1.2 compatibility for sparse_output
    try:
        pipe = Pipeline([("pre", pre), ("model", estimator)])
    except TypeError:
        pre = ColumnTransformer(
            transformers=[
                ("num", SimpleImputer(strategy="median"), num_cols),
                (
                    "cat",
                    Pipeline(
                        [
                            ("impute", SimpleImputer(strategy="most_frequent")),
                            ("oh", OneHotEncoder(handle_unknown="ignore", sparse=False)),
                        ]
                    ),
                    cat_cols,
                ),
            ]
        )
        pipe = Pipeline([("pre", pre), ("model", estimator)])

    stratify = y if task == "classification" and y.nunique() > 1 and y.value_counts().min() >= 2 else None
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=stratify
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)

    metrics: dict[str, float] = {}
    if task == "classification":
        metrics["accuracy"] = float(accuracy_score(y_test, preds))
        try:
            metrics["rmse"] = float(np.sqrt(mean_squared_error(y_test.astype(float), preds.astype(float))))
        except Exception:
            pass
    else:
        metrics["r2"] = float(r2_score(y_test, preds))
        metrics["rmse"] = float(np.sqrt(mean_squared_error(y_test, preds)))
        metrics["mae"] = float(mean_absolute_error(y_test, preds))

    preview = pd.DataFrame({"y_true": y_test.values, "y_pred": preds})
    preview = preview.head(25).reset_index(drop=True)

    return {
        "ok": True,
        "model_id": model_id,
        "task": task,
        "target": tgt,
        "features": feats,
        "metrics": metrics,
        "predictions_preview": preview,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }


def _run_clustering(
    df: pd.DataFrame,
    model_id: str,
    meta: dict,
    features: Optional[list[str]] = None,
) -> dict[str, Any]:
    try:
        estimator = _build_estimator(model_id, meta)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "model_id": model_id, "task": "clustering"}

    nums = df.select_dtypes(include=[np.number]).columns.tolist()
    feats = features or nums[:8]
    feats = [f for f in feats if f in df.columns]
    if len(feats) < 2:
        return {"ok": False, "error": "Need at least 2 numeric features for clustering."}

    X = df[feats].apply(pd.to_numeric, errors="coerce").dropna()
    if len(X) < 5:
        return {"ok": False, "error": "Not enough rows for clustering."}

    labels = estimator.fit_predict(X)
    preview = X.head(25).copy()
    preview["cluster"] = labels[: len(preview)]

    return {
        "ok": True,
        "model_id": model_id,
        "task": "clustering",
        "target": None,
        "features": feats,
        "metrics": {
            "n_clusters": int(getattr(estimator, "n_clusters", len(set(labels)))),
            "inertia": float(getattr(estimator, "inertia_", np.nan))
            if hasattr(estimator, "inertia_")
            else None,
        },
        "predictions_preview": preview.reset_index(drop=True),
        "n_train": int(len(X)),
        "n_test": 0,
    }

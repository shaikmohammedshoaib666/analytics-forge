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
        meta.get("requires_license")
        or dotted in {"stub", "gurobipy", "ortools"}
        or model_id in {"gurobi_stub", "OptimizationGurobi", "ORTools", "PyTorchStub", "PySparkStub"}
        or library in {"gurobipy", "ortools", "torch", "pyspark"}
        or meta.get("task") in {"deep_learning", "big_data", "optimization"}
    ):
        raise RuntimeError(
            f"{model_id} needs a stronger host / license. "
            "Available now for I4.0 on this app: RandomForest, IsolationForest, XGBoost, LightGBM, Prophet."
        )
    # Prophet handled in dedicated runner
    if library == "prophet" or model_id.lower() == "prophet":
        raise RuntimeError("PROPHET_ROUTE")
    if not dotted or "." not in dotted:
        raise RuntimeError(f"Model {model_id} has no importable estimator class.")
    params = dict(meta.get("default_params") or {})
    if model_id == "KMeans" and "n_clusters" not in params:
        params["n_clusters"] = 3
    if model_id == "LogisticRegression" and "max_iter" not in params:
        params["max_iter"] = 1000
    if model_id == "IsolationForest":
        params.setdefault("contamination", 0.05)
        params.setdefault("random_state", 42)
    if model_id.startswith("ExtraTrees"):
        params.setdefault("n_estimators", 80)
        params.setdefault("random_state", 42)
    # soft optional imports
    if library == "xgboost":
        import xgboost  # noqa: F401
    if library == "lightgbm":
        import lightgbm  # noqa: F401
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
    if task == "anomaly" or model_id == "IsolationForest":
        return _run_anomaly(df, model_id, meta, features)
    if task == "forecast" or model_id == "Prophet":
        return _run_prophet(df)
    if task in {"optimization", "deep_learning", "big_data"}:
        return {
            "ok": False,
            "model_id": model_id,
            "task": task,
            "error": meta.get("note")
            or f"{model_id} requires stronger host/license (not Streamlit free tier).",
        }

    try:
        estimator = _build_estimator(model_id, meta)
    except Exception as exc:
        msg = str(exc)
        if msg == "PROPHET_ROUTE":
            return _run_prophet(df)
        return {"ok": False, "error": msg, "model_id": model_id, "task": task}

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


def _run_anomaly(
    df: pd.DataFrame,
    model_id: str,
    meta: dict,
    features: Optional[list[str]] = None,
) -> dict[str, Any]:
    try:
        estimator = _build_estimator(model_id, meta)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "model_id": model_id, "task": "anomaly"}

    nums = df.select_dtypes(include=[np.number]).columns.tolist()
    feats = features or [c for c in nums if not str(c).endswith("_outlier_flag")][:10]
    feats = [f for f in feats if f in df.columns]
    if not feats:
        return {"ok": False, "error": "Need numeric columns for IsolationForest / anomaly detection."}

    X = df[feats].apply(pd.to_numeric, errors="coerce").dropna()
    if len(X) < 10:
        return {"ok": False, "error": "Need at least 10 clean numeric rows for anomaly detection."}

    labels = estimator.fit_predict(X)
    scores = None
    if hasattr(estimator, "decision_function"):
        scores = estimator.decision_function(X)
    anomaly_count = int((labels == -1).sum())
    preview = X.head(25).copy()
    preview["anomaly_label"] = labels[: len(preview)]
    if scores is not None:
        preview["anomaly_score"] = scores[: len(preview)]

    return {
        "ok": True,
        "model_id": model_id,
        "task": "anomaly",
        "target": None,
        "features": feats,
        "metrics": {
            "anomaly_count": anomaly_count,
            "anomaly_rate_pct": round(float(anomaly_count / len(X) * 100), 3),
            "n_rows": int(len(X)),
        },
        "predictions_preview": preview.reset_index(drop=True),
        "n_train": int(len(X)),
        "n_test": 0,
    }


def _run_prophet(df: pd.DataFrame) -> dict[str, Any]:
    try:
        from prophet import Prophet
    except Exception as exc:
        return {
            "ok": False,
            "model_id": "Prophet",
            "task": "forecast",
            "error": f"Prophet not installed ({exc}). On Streamlit Cloud it may need a packages.txt with build tools; locally: pip install prophet.",
        }

    date_cols = [
        c
        for c in df.columns
        if np.issubdtype(df[c].dtype, np.datetime64) or any(h in str(c).lower() for h in ("date", "time", "timestamp"))
    ]
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not date_cols or not num_cols:
        return {
            "ok": False,
            "model_id": "Prophet",
            "task": "forecast",
            "error": "Prophet needs a date/time column and a numeric metric column.",
        }

    # prefer revenue/rul-like metric
    ycol = next(
        (c for c in num_cols if any(k in str(c).lower() for k in ("revenue", "sales", "rul", "units", "y"))),
        num_cols[0],
    )
    tmp = pd.DataFrame(
        {
            "ds": pd.to_datetime(df[date_cols[0]], errors="coerce"),
            "y": pd.to_numeric(df[ycol], errors="coerce"),
        }
    ).dropna()
    if len(tmp) < 10:
        return {"ok": False, "model_id": "Prophet", "task": "forecast", "error": "Need >= 10 dated rows for Prophet."}

    m = Prophet()
    m.fit(tmp)
    future = m.make_future_dataframe(periods=min(14, max(7, len(tmp) // 5)))
    fc = m.predict(future)
    merged = tmp.merge(fc[["ds", "yhat"]], on="ds", how="inner").dropna()
    metrics = {
        "r2": round(float(r2_score(merged["y"], merged["yhat"])), 4),
        "rmse": round(float(mean_squared_error(merged["y"], merged["yhat"]) ** 0.5), 4),
        "mae": round(float(mean_absolute_error(merged["y"], merged["yhat"])), 4),
        "target": ycol,
        "horizon": int(len(future) - len(tmp)),
    }
    preview = fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(20).reset_index(drop=True)
    return {
        "ok": True,
        "model_id": "Prophet",
        "task": "forecast",
        "target": ycol,
        "features": [date_cols[0], ycol],
        "metrics": metrics,
        "predictions_preview": preview,
        "n_train": int(len(tmp)),
        "n_test": int(metrics["horizon"]),
    }

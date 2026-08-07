"""Analytics Forge settings and paths."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOADS_DIR = UPLOAD_DIR  # alias used by app.py
RUNS_DIR = DATA_DIR / "runs"
SAMPLES_DIR = DATA_DIR / "samples"
DB_PATH = DATA_DIR / "analytics_forge.db"
CONFIG_DIR = ROOT / "config"
MODELS_CATALOG_YAML = CONFIG_DIR / "models_catalog.yaml"
CHARTS_CATALOG_YAML = CONFIG_DIR / "charts_catalog.yaml"

for d in (RAW_DIR, CLEAN_DIR, UPLOAD_DIR, RUNS_DIR, SAMPLES_DIR):
    d.mkdir(parents=True, exist_ok=True)


def _secret(name: str, default: str = "") -> str:
    """Read from env, then Streamlit secrets if available."""
    val = os.getenv(name, "").strip()
    if val:
        return val
    try:
        import streamlit as st

        if hasattr(st, "secrets") and name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        pass
    return default


OPENAI_API_KEY = _secret("OPENAI_API_KEY")
OPENAI_MODEL = _secret("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
GEMINI_API_KEY = _secret("GEMINI_API_KEY")
GEMINI_MODEL = _secret("GEMINI_MODEL", "gemini-2.0-flash") or "gemini-2.0-flash"
AI_DEFAULT_PROVIDER = (_secret("AI_DEFAULT_PROVIDER", "gemini") or "gemini").lower()

# Email automation (SMTP send + IMAP inbound CSV)
EMAIL_USER = _secret("EMAIL_USER")
EMAIL_PASSWORD = _secret("EMAIL_PASSWORD")
EMAIL_FROM = _secret("EMAIL_FROM") or EMAIL_USER
EMAIL_SMTP_HOST = _secret("EMAIL_SMTP_HOST", "smtp.gmail.com") or "smtp.gmail.com"
EMAIL_SMTP_PORT = int(_secret("EMAIL_SMTP_PORT", "587") or 587)
EMAIL_SMTP_USE_TLS = _secret("EMAIL_SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
EMAIL_IMAP_HOST = _secret("EMAIL_IMAP_HOST", "imap.gmail.com") or "imap.gmail.com"
EMAIL_IMAP_PORT = int(_secret("EMAIL_IMAP_PORT", "993") or 993)
EMAIL_IMAP_FOLDER = _secret("EMAIL_IMAP_FOLDER", "INBOX") or "INBOX"
INBOUND_DIR = DATA_DIR / "inbound"
INBOUND_DIR.mkdir(parents=True, exist_ok=True)

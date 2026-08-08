# Analytics Forge

Reusable Streamlit analytics OS (8 fields) with OpenAI + Gemini Ask/AI, ML studio, dashboard pack, and email automation.

## Local run

```bash
cd analytics-forge
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Open http://localhost:8501

## AI keys (OpenAI + Gemini)

In `.env` (local) or Streamlit Cloud **Secrets**:

```
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.0-flash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
AI_DEFAULT_PROVIDER=gemini
```

- Gemini key: https://aistudio.google.com/apikey (free tier available)
- OpenAI key: https://platform.openai.com/api-keys

**Never commit real `.env` or secrets to GitHub.**

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub
2. Go to https://share.streamlit.io → New app (or open an existing app’s **⚙️ settings**)
3. Select repo, branch `main`, main file `app.py`
4. **Required — pin Python 3.12:** open **Advanced settings** → set **Python version** to **3.12** → Save  
   (Community Cloud does **not** honor `runtime.txt` for the runtime; the UI dropdown is the source of truth. This repo still ships `runtime.txt` with `python-3.12.8` as a local/docs signal.)
5. Add secrets from `.streamlit/secrets.toml.example`
6. Deploy / **Reboot** the app once after changing Python or `requirements.txt`

If logs show `Using Python 3.13` / `3.14` and install hangs after `uv pip install` / `Resolved … packages`, switch the UI to **3.12** and reboot — many ML wheels are unreliable on bleeding-edge Python.

## Hosts & data limits

| Host | Good for | Typical upload / data size |
|------|----------|----------------------------|
| **Streamlit Community Cloud (free)** | This app: CSV analytics, sklearn/XGBoost/LightGBM (Prophet optional locally) | Usually **tens of MB CSV** per session (memory ~1GB class). Avoid multi-GB files |
| **Streamlit Cloud / paid tier** | Same app, more RAM | Larger CSVs (hundreds of MB) depending on plan |
| **AWS / GCP / Azure VM or GPU** | PyTorch deep learning | GBs + GPU training |
| **Databricks / EMR / Spark cluster** | PySpark big data | GBs–TBs across cluster |
| **Local strong PC** | Gurobi (with license), heavier models | Depends on your RAM |

### Why PyTorch / PySpark are listed but not installed here
They are **too heavy** for Streamlit free cloud and need special infrastructure. They appear in ML Studio as **enterprise stubs** with guidance.

### I4.0 models now runnable in this app
RandomForest, ExtraTrees, **IsolationForest**, GradientBoosting, KMeans, DBSCAN, **PCA**, sklearn baselines.

**Separate packages in main `requirements.txt`** (college / Streamlit Cloud after push + reboot): **XGBoost**, **LightGBM**, **statsmodels OLS**, **PuLP**. Soft-fail remains if import still fails. **Prophet** lives in `requirements-optional.txt` so Cloud builds do not hang on cmdstan; install locally with `pip install -r requirements-optional.txt` if you need forecasts.

Gurobi / OR-Tools / PyTorch / PySpark = stronger host + license/cluster (not in requirements).

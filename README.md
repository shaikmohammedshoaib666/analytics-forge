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
2. Go to https://share.streamlit.io → New app
3. Select repo, branch `main`, main file `app.py`
4. Add secrets from `.streamlit/secrets.toml.example`
5. Deploy

## Hosts & data limits

| Host | Good for | Typical upload / data size |
|------|----------|----------------------------|
| **Streamlit Community Cloud (free)** | This app: CSV analytics, sklearn/XGBoost/LightGBM/Prophet | Usually **tens of MB CSV** per session (memory ~1GB class). Avoid multi-GB files |
| **Streamlit Cloud / paid tier** | Same app, more RAM | Larger CSVs (hundreds of MB) depending on plan |
| **AWS / GCP / Azure VM or GPU** | PyTorch deep learning | GBs + GPU training |
| **Databricks / EMR / Spark cluster** | PySpark big data | GBs–TBs across cluster |
| **Local strong PC** | Gurobi (with license), heavier models | Depends on your RAM |

### Why PyTorch / PySpark are listed but not installed here
They are **too heavy** for Streamlit free cloud and need special infrastructure. They appear in ML Studio as **enterprise stubs** with guidance.

### I4.0 models now runnable in this app
RandomForest, ExtraTrees, **IsolationForest**, GradientBoosting, KMeans, DBSCAN, **PCA**, sklearn baselines.

**Separate packages, shipped in main `requirements.txt`** (so college / Streamlit Cloud installs get them after push + redeploy): **XGBoost**, **LightGBM**, **statsmodels OLS**, **PuLP**, **Prophet**. They are separate libraries — that does **not** mean they cannot run; once `pip install -r requirements.txt` succeeds, they work. Soft-fail remains only if import still fails after install. Prophet usually has wheels but can occasionally flake on Cloud (cmdstan build); redeploy or use holdout regression if that happens.

Gurobi / OR-Tools / PyTorch / PySpark = stronger host + license/cluster (not in requirements).

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

## Workflow

Upload → Clean → Field → Auto KPIs → Charts → ML Studio → Ask/AI (Gemini/OpenAI/Offline) → Dashboard → Email


# Marktplaats Flip Helper (Compliant Edition)

A tiny Flask web app you can deploy on Render that:
- Searches PUBLIC Marktplaats listings for a keyword (e.g., "koffiemachine kapot").
- Uses Gemini to analyze for flip potential.
- Generates ready-to-copy **message & negotiation suggestions** per listing.
- **Does not** auto-message sellers or auto-negotiate.

## Quick start (local)
1) Python 3.10+ recommended.
2) `pip install -r requirements.txt`
3) Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
4) `python app.py`
5) Open http://localhost:5000

## Deploy to Render
- Push this folder to a new GitHub repo.
- On Render, create a **Web Service** and connect the repo.
- Add env var: `GEMINI_API_KEY` (required). Optional: `DEFAULT_LANGUAGE`, `MAX_SUGGESTIONS`.
- Render uses `render.yaml` (build: `pip install -r requirements.txt`, start: `gunicorn app:app`).

## Environment variables
- `GEMINI_API_KEY` (required)
- `DEFAULT_LANGUAGE` default `nl`
- `MAX_SUGGESTIONS` default `8`

MIT License

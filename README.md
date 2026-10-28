# AbroMap

AbroMap is an Azerbaijani-first study abroad discovery platform. Students can complete a profile without an account, search a real university catalog, compare source-checked programs with an explainable compatibility screen, browse scholarships, save and compare programs, and track an application checklist. The interface supports Azerbaijani, English, and Russian.

## Data integrity

The bundled ROR v2.15 snapshot contains 10,256 selected real institution identities across the supported countries. The startup catalog includes four of them and four master's programs checked against official university pages. A manual GitHub Action imports the full snapshot into Supabase. ROR identity alone does **not** verify degree programs or admission requirements, so catalog-only institutions are labeled accordingly. Unknown fees and requirements remain blank. The score measures compatibility with known facts, **not admission probability**; unverified requirements cap it at 69 and historical verified requirements at 79. See [DATA_SOURCES.md](DATA_SOURCES.md) and [PHASE2_PROGRESS.md](PHASE2_PROGRESS.md).

## Stack

- Next.js App Router, React, TypeScript, Tailwind CSS, next-intl, Lucide
- FastAPI, Pydantic, SQLAlchemy, Alembic
- SQLite for local development; PostgreSQL via `DATABASE_URL` for deployment
- Optional server-side OpenAI Responses API

## Run locally on Windows PowerShell

Use two terminals.

### Backend

```powershell
cd D:\AbroMap\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m scripts.import_fields
python -m scripts.import_universities --dump data/ror_official_sample.json --execute --source-version v2.15
python -m scripts.import_official_sample --execute
python -m uvicorn app.main:app --reload --port 8000
```

API documentation: [http://localhost:8000/docs](http://localhost:8000/docs).

### Frontend

```powershell
cd D:\AbroMap\frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). New visitors are routed to `/az`. The language selector switches to `/en` or `/ru` and persists through the locale path/cookie.

### PostgreSQL option

```powershell
cd D:\AbroMap
docker compose up -d db
```

Set `DATABASE_URL=postgresql+psycopg://abromap:localdev@localhost:5432/abromap` in `backend/.env`, then run the Alembic and import commands above. Configure a strong password outside local development.

## Checks

```powershell
cd D:\AbroMap\backend
python -m pytest -q

cd D:\AbroMap\frontend
npm run typecheck
npm run lint
npm run build
```

## What works

- Responsive landing page and locale-based public routes
- Eight-step onboarding with browser persistence, editable answers, and exam scores that can be left blank
- Database-backed university and program discovery, server pagination, field search, source and academic-year display
- Local saved programs, comparison cards, and per-program roadmap checklist
- One source-checked Erasmus Mundus scholarship scheme
- AI chat endpoint with a graceful no-key response; when `OPENAI_API_KEY` is configured, the key stays on the backend and the prompt is restricted to available program context
- Backend token check on the admin summary endpoint

## Current limits

Program coverage is currently four master's degrees, even after importing thousands of ROR universities. Student accounts, Supabase/Google sign-in, protected personal dashboard, review UI, and a scholarship eligibility engine are planned in [TODO.md](TODO.md). Saved items and profile data are stored only in the current browser. The legal pages are drafts requiring legal review before public launch. The AI endpoint has not been validated with a live API key.

For deployment, set the frontend API URL, backend CORS origin, and production PostgreSQL URL. Render startup applies the migrations and loads the small official sample; the GitHub Action imports the full ROR institution snapshot. Use HTTPS and managed secrets. Program requirements still need a wider source review before relying on the platform for applications.

See [DEPLOY.md](DEPLOY.md) for the Vercel + Supabase + Render walkthrough, [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for database details, and [DATA_INGESTION.md](DATA_INGESTION.md) for catalog refreshes.

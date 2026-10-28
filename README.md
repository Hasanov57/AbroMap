# AbroMap

AbroMap is an Azerbaijani-first study abroad discovery MVP. Students can complete a profile without an account, evaluate database programs with an explainable rule-based score, inspect program requirements, browse scholarships, save and compare programs, and track an application checklist. The interface supports Azerbaijani, English, and Russian.

## Data integrity

The bundled five universities, fifteen degree programs (five each at bachelor's, master's and PhD level), one scholarship, and all associated fees and requirements are **synthetic demonstration records**. They are visibly labeled in the UI and must not guide real applications. Bachelor's and PhD demo records intentionally leave tuition and admission requirements unknown. The matching score measures compatibility with the stored data, **not an admission probability**. Unverified data caps the score at 69; historical verified requirements cap it at 79. Different GPA scales are never converted automatically. No real institutional partnership or ranking is implied.

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
python -m scripts.seed
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

Set `DATABASE_URL=postgresql+psycopg://abromap:localdev@localhost:5432/abromap` in `backend/.env`, then run the Alembic and seed commands above. Configure a strong password outside local development.

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
- Database-backed university and program discovery, filters, program-level matching, source and academic-year display
- Local saved programs, comparison cards, and per-program roadmap checklist
- Scholarship discovery from the demonstration database
- AI chat endpoint with a graceful no-key response; when `OPENAI_API_KEY` is configured, the key stays on the backend and the prompt is restricted to available program context
- Backend token check on the admin summary endpoint

## Current limits

There is no verified real university dataset yet, so source links are absent from bundled demo records. Student accounts, Supabase/Google sign-in, protected personal dashboard, full admin editing, ingestion/review jobs, and an authoritative scholarship eligibility engine are planned in [TODO.md](TODO.md). Saved items and profile data are stored only in the current browser. The legal pages are drafts requiring legal review before public launch. The AI endpoint has not been validated with a live API key.

For deployment, set the frontend API URL, backend CORS origin, production PostgreSQL URL, and optional AI key. Apply Alembic migrations before starting the backend. Use HTTPS and managed secrets. The bundled demo dataset should be replaced by sourced and verified records before public use.

See [DEPLOY.md](DEPLOY.md) for the Vercel + Supabase + Render free-tier walkthrough.

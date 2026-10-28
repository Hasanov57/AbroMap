#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?Set DATABASE_URL to the Supabase session-pooler connection string}"
: "${FRONTEND_ORIGIN:?Set FRONTEND_ORIGIN to your Vercel site URL}"

python -m alembic upgrade head
python -m scripts.seed
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"

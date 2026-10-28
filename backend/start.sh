#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?Set DATABASE_URL to the Supabase session-pooler connection string}"
: "${FRONTEND_ORIGIN:?Set FRONTEND_ORIGIN to your Vercel site URL}"

python -m alembic upgrade head
python -m scripts.import_fields
python -m scripts.import_universities --dump data/ror_official_sample.json --execute --source-version v2.15
python -m scripts.import_official_sample --execute
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"

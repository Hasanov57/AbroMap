# Supabase database setup

AbroMap uses Supabase as a managed PostgreSQL database. Supabase Auth and Storage are not used in this phase. Keep the database URL on the backend and in a GitHub Actions secret; the Next.js frontend only needs the public Render API URL.

1. Create a Supabase Free project at [supabase.com/dashboard](https://supabase.com/dashboard/projects). Choose a region near your users and save the database password in a password manager.
2. In the project, open **Connect** and copy the **Session pooler** URI on port `5432`. This is the IPv4-compatible choice for Render. Replace the password placeholder and percent-encode special characters in the password. Add `?sslmode=require` to the URI, or `&sslmode=require` if it already contains a query string.
3. Add this full URI as `DATABASE_URL` in the Render backend service's **Environment** settings. Do not add it to Vercel or to any `NEXT_PUBLIC_` variable.
4. In the GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name the secret `SUPABASE_DATABASE_URL` and paste the same URI. The manual catalog import workflow reads this secret.
5. Render's `backend/start.sh` applies Alembic migrations, loads the country and field catalog, then loads four ROR institutions and four source-checked programs. After Render reports healthy, run **Actions → Import verified ROR university catalog → Run workflow** to load the bundled full ROR snapshot. The job is repeatable and records each run in `import_runs`.

The database and API must remain online during the import. The current snapshot is ROR v2.15, released 2026-10-20; refresh it with the documented build script when a newer ROR release is needed.

For an existing database containing Phase 1 demo records, first make a PostgreSQL backup with a local `pg_dump` client. Then use `python -m scripts.cleanup_demo` for a dry run, followed by `python -m scripts.cleanup_demo --execute --confirm DELETE_DEMO_RECORDS --backup-file <backup-path>`. The script refuses a PostgreSQL deletion without a backup file. New Supabase projects have no demo records to remove.

To verify a deployment, visit the Render `/api/v1/health` and `/api/v1/countries` endpoints. The university directory count should grow after the Action finishes. Matching results remain limited to the four programs whose official degree pages were checked. See [DATA_INGESTION.md](DATA_INGESTION.md) for import commands and [DEPLOY.md](DEPLOY.md) for the full walkthrough.

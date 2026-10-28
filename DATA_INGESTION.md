# Catalog ingestion

Run commands from `backend` after installing `requirements.txt` and setting `DATABASE_URL` in `.env` or the environment.

```powershell
python -m alembic upgrade head
python -m scripts.import_fields
python -m scripts.import_universities --dump data/ror_official_sample.json
python -m scripts.import_universities --dump data/ror_official_sample.json --execute --source-version v2.15
python -m scripts.import_official_sample --execute
```

The ROR command is a dry run unless `--execute` is supplied. It validates active education records and supported country codes, deduplicates by exact ROR ID, stores aliases/identifiers/source metadata, and queues same-name conflicts for review. It does not infer or create degree programs. The official program script is also a dry run by default; it requires the matching ROR institutions and field catalog.

To import the full bundled catalog locally, run:

```powershell
python -m scripts.import_universities --dump data/ror_europe_china.zip --execute --source-version v2.15 --batch-size 250
```

The same command runs in the manual GitHub Action after `SUPABASE_DATABASE_URL` is configured. Re-running is safe: known ROR IDs update their metadata, and the existing program sample updates by official URL. `import_runs` records counts and status. A failed run can be repeated after fixing the cause. Nine same-name conflicts in the current release were held for review in the local test; the production count may vary with existing data. Review candidates require a human decision before merging.

The compact snapshot is derived from the official ROR ZIP. To refresh it, run `python -m scripts.build_ror_snapshot`, then `python -m scripts.extract_official_ror_sample`, inspect the updated manifest and counts, review a country sample, and update the `--source-version` arguments in `backend/start.sh` and `.github/workflows/import-ror.yml`. The build script follows the ROR Zenodo concept DOI, checks the release MD5, streams the JSON and writes only accepted records. It does not scrape university websites.

For a new source-backed program, verify the official degree page and its target intake, then extend `backend/data/official_sample.json` or create a reviewed importer. Leave a fact empty when the page does not state it. Requirements carry their academic year, applicant category, source URL, publisher and review date. The current schema supports one requirement row per program and academic year; separate rows for multiple applicant categories in the same year remain future work.

Demo cleanup is explicit. `python -m scripts.cleanup_demo` prints what would be removed. For SQLite it creates a local backup before deletion. For PostgreSQL, create a `pg_dump` backup first and provide its path to the script. Only known Phase 1 demo slugs and records marked `is_demo` are eligible.

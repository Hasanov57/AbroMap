# Phase 2 progress — 2026-10-28

## Completed and tested locally

- Added 52 supported country records, the full ISCED-F 2013 hierarchy (11 broad, 29 narrow, 80 detailed fields), 260 curated specific majors, multilingual search aliases for common fields, and 21 bidirectional related-major pairs.
- Built a checksum-verified ROR v2.15 snapshot with 10,256 selected active education institutions. A fresh local SQLite import added 10,247 institutions and placed nine same-name collisions in a review queue. The compressed snapshot is bundled with the repository so it can be imported into Supabase through a manual GitHub Action.
- Replaced synthetic startup seeding with four ROR institutions, four source-checked master's programs, four requirement records, two explicit exam requirements and one Erasmus Mundus scholarship scheme. Other ROR institutions remain catalog-only until their programs are verified.
- Added additive Alembic migrations, source/provenance fields, import logs, explicit demo cleanup with backups, and a source-aware matching screen. Matching filters candidates in the database, pages results, handles HSK/CEFR where documented and marks missing/historical/uncertain requirements.
- Updated onboarding, country cards, university directory/details, results, program details, scholarship display, and saved-program loading for the larger catalog. The empty results message explains that verified program coverage is still limited.
- Verified 16 backend tests, including an upgrade from the Phase 1 SQLite schema and safe demo cleanup, and passed frontend typecheck, lint and production build. The full local snapshot import and API smoke check completed. A live Supabase/Render/Vercel deployment check remains.

## Not yet complete

- Supabase credentials have not been provided in this workspace, so the PostgreSQL migration and GitHub Action have not been exercised against the user's project. Docker Desktop's local engine could not start without service access, so no local PostgreSQL run was possible.
- The directory has broad ROR institution coverage, but only four programs have verified source pages. Bachelor's and PhD program coverage is still absent. No tuition or admission threshold has been invented to fill gaps.
- Many specific majors lack reviewed Azerbaijani/Russian translations. The 260-major layer is curated for search; it is not an official UNESCO extension.
- The review queue has no admin UI. Periodic ROR refresh, source change monitoring, program ingestion at scale, multi-category requirement rows, scholarship eligibility logic, accounts and Supabase Auth remain future work.
- The compatibility score is a screening aid, not an admissions chance or a university decision. An official program page should be checked again before applying.

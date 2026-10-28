# Deploy AbroMap with Supabase, Render and Vercel

This is a free-tier hobby deployment: Supabase holds PostgreSQL data, Render runs FastAPI, and Vercel hosts Next.js. The public app starts with four source-checked programs. A manual GitHub Action then imports the bundled ROR institution directory. ROR institutions with no checked program pages appear as catalog-only entries.

## 1. Create the Supabase database

1. Create a Free project at [Supabase](https://supabase.com/dashboard/projects) and save its database password.
2. Open **Connect → Session pooler**. Copy its PostgreSQL URI on port `5432`. This mode works from IPv4-only services. Replace the password placeholder and URL-encode special characters in the password.
3. Add `?sslmode=require` to the URI, or `&sslmode=require` if it already contains a query string. Keep this entire URI private. [Supabase's connection guide](https://supabase.com/docs/guides/database/connecting-to-postgres) explains the pooler and SSL settings.

## 2. Deploy the API on Render

1. At [Render](https://dashboard.render.com/), choose **New → Web Service** and connect the [Hasanov57/AbroMap](https://github.com/Hasanov57/AbroMap) repository.
2. Use branch `main`, root directory `backend`, Python runtime and the **Free** instance type. Set build command `pip install -r requirements.txt` and start command `bash start.sh`.
3. Add these environment variables in Render:

   | Name | Value |
   | --- | --- |
   | `DATABASE_URL` | Supabase Session pooler URI from step 1, with SSL enabled |
   | `FRONTEND_ORIGIN` | `http://localhost:3000` initially; replace with the exact Vercel origin in step 4 |

4. Set health check path to `/api/v1/health` if Render offers the setting. Deploy and copy the assigned `https://…onrender.com` URL. The start script runs migrations and loads the four ROR institutions, four source-checked programs and one Erasmus Mundus scheme. Visit `<Render URL>/api/v1/health` and `<Render URL>/api/v1/countries` to verify the API.

`OPENAI_API_KEY` is optional and should stay unset for a free launch. The AI feature responds with a source-oriented fallback when the key is absent.

## 3. Deploy the frontend on Vercel

1. At [Vercel](https://vercel.com/new), import the same GitHub repository as a new project.
2. Set framework to Next.js and root directory to `frontend`. Keep the detected install and build settings.
3. Add `NEXT_PUBLIC_API_URL` as a **Production** environment variable. Its value is the exact Render origin, for example `https://your-api.onrender.com`, with no trailing slash.
4. Deploy and copy the assigned `https://…vercel.app` URL. Vercel embeds this variable during build, so redeploy the frontend if it changes. [Vercel's monorepo guide](https://vercel.com/docs/monorepos) covers the root-directory setting.

## 4. Allow the frontend to call the API

1. In Render **Environment**, replace `FRONTEND_ORIGIN` with the exact Vercel production origin, for example `https://your-site.vercel.app` (no path or trailing slash). Save so Render redeploys.
2. Open the Vercel site. It should route `/` to `/az`. Try **Master's → Computer Science → Germany** or **Hungary** in discovery. The results should display source links; other fields or countries may have no verified program yet.
3. Open the university directory to confirm the four initial institutions appear. A catalog-only page must say that its degree programs have not been verified.

## 5. Import the full ROR university directory

1. In GitHub, open the repository's **Settings → Secrets and variables → Actions** and add a repository secret called `SUPABASE_DATABASE_URL`. Paste the same Supabase Session pooler URI used in Render.
2. Open **Actions → Import verified ROR university catalog → Run workflow** on `main`. The workflow imports the bundled, checksum-verified ROR v2.15 snapshot. It can be run again after a partial failure or a snapshot update.
3. Wait for the workflow to finish, then refresh the university directory. The local test imported 10,247 institutions and held nine same-name conflicts for review; production counts may differ if the database already has records. The program count remains four until more official program pages are reviewed.

## Existing Phase 1 database

If this Supabase project was used by the earlier demo release, the old synthetic records remain in the database after migration, but public endpoints filter them out. Before deleting them, make a PostgreSQL backup and follow [DATA_INGESTION.md](DATA_INGESTION.md)'s cleanup procedure. A new Supabase project does not need this step.

## Free-tier behavior

[Render Free web services](https://render.com/docs/free) spin down after 15 minutes without traffic and may take about a minute to wake. Their local filesystem is temporary, so the persistent catalog belongs in Supabase. Check [Supabase Free project status](https://supabase.com/docs/guides/platform/free-project-pausing) if the API later cannot reach a paused database. This setup is suitable for a pilot; program and requirement coverage is still limited and should be checked at each university before a real application.

New commits to `main` trigger Render and Vercel redeploys. `start.sh` reapplies migrations and updates the small official sample without duplicating it. See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for database details and [PHASE2_PROGRESS.md](PHASE2_PROGRESS.md) for current coverage.

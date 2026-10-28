# Deploy AbroMap with free services

This walkthrough uses **Vercel Hobby** for the Next.js frontend, **Render Free Web Service** for FastAPI, and **Supabase Free** for PostgreSQL. The public site will show clearly labeled synthetic demo data. Student profiles and saved items remain in each visitor's browser; Supabase Auth is not implemented yet.

## 1. Create the Supabase database

1. Create a Free project at [Supabase](https://supabase.com/dashboard/projects). Save the database password securely.
2. In the project dashboard, choose **Connect** → **Session pooler**. Copy the PostgreSQL URI on port **5432**. Replace any `[YOUR-PASSWORD]` placeholder with your database password; URL-encode special characters in the password. Session pooling suits Render's long-running service and works over IPv4. The app accepts the copied `postgresql://` URI and selects the installed `psycopg` driver automatically.
3. If the URI has no `sslmode` parameter, add `?sslmode=require` (or `&sslmode=require` if it already has query parameters). Keep the whole URI private.

## 2. Deploy the API on Render

1. In [Render](https://dashboard.render.com/), choose **New → Web Service** and connect the `Hasanov57/AbroMap` GitHub repository.
2. Set **Branch** to `main`, **Root Directory** to `backend`, **Language** to `Python 3`, and **Instance Type** to `Free`. The repository pins Python in `backend/.python-version`.
3. Set **Build Command** to `pip install -r requirements.txt`.
4. Set **Start Command** to `bash start.sh`.
5. Add environment variables:

   | Name | Value |
   | --- | --- |
   | `DATABASE_URL` | Supabase **Session pooler** URI from step 1 |
   | `FRONTEND_ORIGIN` | `http://localhost:3000` temporarily; replace with your Vercel URL in step 4 |

   Leave `OPENAI_API_KEY` unset for the free demo. Never place `DATABASE_URL` in Vercel's `NEXT_PUBLIC_` variables or GitHub files.

6. Set **Health Check Path** to `/api/v1/health` if Render offers the field, then create the service. Startup applies Alembic migrations and seeds the labeled demo records once per missing record. Copy the assigned `https://…onrender.com` URL.
7. Open `<Render URL>/api/v1/health` and `<Render URL>/api/v1/countries`. The latter should return DE, HU, and IT with 6, 3, and 6 demo programs. If deployment fails, inspect Render's deploy logs; most first-run errors are an incorrect database URI or password.

## 3. Deploy the frontend on Vercel

1. In [Vercel](https://vercel.com/new), import the same GitHub repository as a new project.
2. Set **Framework Preset** to `Next.js` and **Root Directory** to `frontend`. Keep the detected install, build, and output settings.
3. Add one environment variable for **Production** (and Preview if you want preview deployments):

   | Name | Value |
   | --- | --- |
   | `NEXT_PUBLIC_API_URL` | Exact Render URL, such as `https://your-api.onrender.com`, without a trailing slash |

4. Deploy. Copy the assigned production `https://…vercel.app` URL. `NEXT_PUBLIC_API_URL` is embedded at build time, so changing it later requires a new Vercel deployment.

## 4. Enable browser access to the API

1. In the Render service's **Environment** settings, replace `FRONTEND_ORIGIN` with the exact Vercel production origin, for example `https://your-site.vercel.app` (no path or trailing slash).
2. Save and deploy the updated Render service.
3. Open the Vercel site. It should route `/` to `/az`. Try onboarding with **Master's → Computer Science → Not sure yet** for country and university. The results should come from the API. A bachelor's or PhD choice in one of the five focus fields also returns an explicitly uncertain demo result.

## Free-tier behavior and current limits

- Render Free services [spin down after 15 minutes of inactivity](https://render.com/docs/free). The next API request may take about a minute; a visitor might need to retry while it wakes up. Render's local filesystem is temporary, which is why this deployment uses Supabase instead of SQLite.
- Supabase Free projects [can pause after low activity](https://supabase.com/docs/guides/platform/free-project-pausing). Resume a paused project from its dashboard.
- Vercel Hobby is [for personal, non-commercial projects](https://vercel.com/docs/plans/hobby). Check the plan terms before using AbroMap commercially.
- No paid AI service is required. The assistant displays a fallback message without `OPENAI_API_KEY`. Add that key only after rate limiting and abuse controls are implemented.
- The bundled universities, programs, admission examples, and scholarship are synthetic. Replace them with verified and sourced records before relying on them for real applications.

## Future updates

Push new commits to `main`; Render and Vercel will redeploy their respective folders. If you add database models, create and commit an Alembic migration before pushing. Render's `start.sh` will apply it at startup.

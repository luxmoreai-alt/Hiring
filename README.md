# Luxmor TalentForge

A Luxmor AI campus recruitment portal with preferred work-location capture, timed assessments, coding evaluation, proctoring, confidential candidate results, recruiter filtering, and post-assessment Technical/HR/selection workflow tracking.

## Local setup

1. Copy `.env.example` to `.env` and add the Neon connection URL. The provided development `.env` is ignored by Git.
2. Install backend dependencies and prepare the database:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   .\.venv\Scripts\python backend\manage.py migrate
   .\.venv\Scripts\python backend\manage.py seed_questions
   .\.venv\Scripts\python backend\manage.py createsuperuser
   ```

3. Start Django with `.\.venv\Scripts\python backend\manage.py runserver`.
4. In a second terminal, run `cd frontend`, `npm install`, then `npm run dev`.

Open `http://localhost:5173`. Recruiters use `http://localhost:5173/admin`; candidates use the landing page. Django's internal administration is available separately at `http://localhost:8000/django-admin/`.

For deployment, set `FRONTEND_URL=https://your-domain.com` and configure the web host to serve `frontend/dist/index.html` for client routes such as `/admin` and `/admin/dashboard`.

## Production note

The built-in code runner is suitable for controlled development. Before accepting untrusted public submissions, run it as a separate worker inside a network-disabled, resource-limited container (or replace it with Judge0/Piston). Browser fullscreen APIs can detect and respond to exits but cannot disable operating-system shortcuts.

## Deploy to Vercel

The repository is configured as one Vercel project: Vite is served from the CDN and Django runs through `api/index.py` as a Python Function. Keep the Vercel project **Root Directory** at the repository root and use the settings from `vercel.json`.

In Vercel project settings, set **Framework Preset** to `Other` and leave **Install Command**, **Build Command**, and **Output Directory** using the values detected from `vercel.json`. Do not set the Root Directory to `frontend`.

The install phase explicitly installs both `requirements.txt` and the frontend npm packages so Django is available when the build phase runs `collectstatic`.

Add these variables in **Vercel → Project → Settings → Environment Variables** for Production, Preview, and Development:

- `DATABASE_URL`: the Neon pooled PostgreSQL URL
- `DJANGO_SECRET_KEY`: a new long random value
- `DEBUG`: `false`

`VERCEL_URL` is supplied automatically and is used for allowed-host, CSRF, and frontend URL configuration. `DATABASE_URL` is intentionally not committed.

Deploy from the repository root with:

```powershell
npx vercel
npx vercel --prod
```

The API runs at `/api`, the recruiter console at `/admin`, and React routes are handled by the SPA fallback. Database migrations are not run during a Vercel build; apply them deliberately from a trusted machine with the production `DATABASE_URL` before deploying schema changes.

Vercel Python Functions are not a secure multi-language code sandbox. For production coding rounds, configure a separate Judge0/Piston-style evaluator; otherwise the language list is limited to runtimes detected inside the function.

# NEXUS CITY AI
**One Platform. Every Problem. Smarter Cities.**

A React + TypeScript + Vite frontend and FastAPI backend for civic infrastructure reporting, tracking, and monitoring.

> **Deployment status:** No public deployment has been created yet. Replace these placeholders after you deploy:
> - Frontend: `https://<your-vercel-project>.vercel.app`
> - API: `https://<your-render-service>.onrender.com`

## Features
- Civic issue reporting, public report tracking, dashboards, analytics, and a Leaflet/OpenStreetMap incident map.
- Rule-based preliminary analysis (not a trained or cloud AI model).
- Installable Progressive Web App (PWA) with an offline-cached app shell.
- Offline report drafts stored in this browser's IndexedDB and retried on reconnect, app reopen, or by pressing **Sync now**.
- PostgreSQL in production; SQLite remains the local development default.

## Local development (Windows / PowerShell)

Use Node.js 20.19+ (Node 24 recommended) and Python 3.13 for the deployment runtime.

### Backend
```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.seed
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API health: http://127.0.0.1:8000/api/health

### Frontend
In a second terminal:
```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev -- --host 127.0.0.1
```
Open the Vite URL, normally http://127.0.0.1:5173. The service worker is enabled in production builds. To preview a production-style PWA against a local backend:
```powershell
$env:VITE_API_URL = "http://127.0.0.1:8000"
npm run build -- --mode pwa-test
npm run preview
```
The special `pwa-test` mode permits a local HTTP API for local testing only; actual production builds require an HTTPS API URL.

## Deploy the frontend to Vercel

1. Import `hemanth-13-hub/NEXUS-CITY-AI` into your Vercel account. This first deployment establishes your actual frontend domain; it may show API errors until the backend is deployed.
2. Set **Root Directory** to `frontend`.
3. Select Vite (or use the detected defaults):
   - Install command: `npm ci`
   - Build command: `npm run build`
   - Output directory: `dist`
4. For this initial deployment, set `VITE_API_URL` to a temporary HTTPS placeholder such as `https://api-pending.example`. Vite requires an HTTPS URL during a production build.
5. Deploy and record the actual HTTPS frontend origin. Do not use the example domains literally.

`frontend/vercel.json` provides client-side route fallback. Vite embeds `VITE_API_URL` at build time, so rebuild after changing it.

## Deploy the backend to Render

1. Create a **managed PostgreSQL** database in Render, preferably in the same region as the web service. Copy its **internal connection string** for services in the same Render region. PostgreSQL may be a paid resource; review the current plan, price, and retention policy in Render before creating it. No hosting or database resource is created by this repository.
2. Create a Render Web Service from this repository and use the included `render.yaml` Blueprint, or enter:
   - Root directory: `backend`
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/api/health`
3. Set these service environment variables in Render:
   - `APP_ENV` = `production`
   - `DATABASE_URL` = the managed PostgreSQL connection string (never commit it)
   - `FRONTEND_ORIGINS` = the exact deployed Vercel origin, e.g. `https://<your-vercel-project>.vercel.app`. For a custom domain, include that exact origin too, comma-separated. Do not include a wildcard, path, or trailing slash.
   - `PYTHON_VERSION` = `3.13.4` if the service does not use the repository's `backend/.python-version`.
4. Deploy and verify `https://<your-render-service>.onrender.com/api/health` returns HTTP 200 and `"database":"connected"`.
5. If you change the Vercel/custom domain, update `FRONTEND_ORIGINS` and redeploy the backend. Preview domains are not automatically allowed.

Finally, replace the temporary Vercel `VITE_API_URL` with the actual Render API origin (no `/api` suffix) and redeploy Vercel. Confirm `FRONTEND_ORIGINS` on Render exactly matches the Vercel production origin.

Production startup intentionally fails if PostgreSQL or an explicit CORS origin is missing. SQLite is for local development only. Render's free web service can sleep when idle; use a service plan appropriate for your availability needs. Keep backups for the managed database.

## Verify the live deployment

1. Open the actual Vercel HTTPS URL on a laptop and a phone.
2. Open the app's report form and submit a test issue. Confirm the success message appears only after the API confirms the report and that it has a server-generated `NX-...` ID.
3. Visit the API health URL; check the browser developer console/network panel for failed API calls or CORS errors.
4. Install the PWA:
   - Android/Chrome: use **Install app** or **Add to Home screen** in the browser menu.
   - iPhone/iPad: in Safari use **Share → Add to Home Screen**.
5. After one successful visit, enable airplane mode and reopen the app. The cached shell should load. Create a test report and verify it says **Pending sync**; it is stored only on that device at this point.
6. Restore connectivity and keep the app open, reopen it, or press **Sync now**. Wait for the server-confirmed report ID before treating a queued report as submitted.

## Offline behavior and limitations

- After the first online visit, the service worker precaches the app shell and same-origin static build assets. It does **not** cache API responses, uploads, report details, or other private/server data.
- Offline report fields and an optional photo are saved in IndexedDB on that browser/device. The app retries when connectivity returns or when it is reopened; a manual **Sync now** action is available. The backend uses a UUID idempotency key to avoid duplicate reports when a response is lost and retried.
- Pending drafts are not encrypted by the browser database. Do not use shared devices or enter sensitive personal information; browser data removal will delete pending drafts.
- Dashboard data, report tracking, live map tiles, report submission, geolocation, and backend rule-based analysis require network access (geolocation also requires permission). Map tiles come from OpenStreetMap and are not available offline.
- Production status-changing/admin API routes are disabled because this project has no authentication or authorization. Add real authentication and role checks before enabling operations.
- Production photo upload is disabled until durable object storage is configured. Local uploads on a web-service filesystem are not durable.
- This is a prototype, not an emergency service. Public report endpoints and dashboard views are not designed for confidential records. Add authentication, privacy review, and data minimization before collecting real sensitive or personal information.

## Configuration and secrets

- Frontend: `VITE_API_URL` is mandatory for production builds; the localhost fallback is development-only.
- Backend: `DATABASE_URL`, `FRONTEND_ORIGINS`, and `APP_ENV` are read from environment variables. Local examples are in `backend/.env.example` and `frontend/.env.example`.
- Never commit `.env` files, database credentials, API keys, passwords, or production personal data. `.gitignore` excludes local databases, virtual environments, dependencies, caches, build outputs, and secrets while retaining `.env.example`.
- The current AI mode is rule-based; `AI_API_KEY` is not needed by this implementation.

## Tests and production build

Backend:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

Frontend:
```powershell
cd frontend
npm ci
npm run build
npm run preview
```

## Troubleshooting

- **Browser reports a CORS error:** `FRONTEND_ORIGINS` must match the full HTTPS origin exactly. Update it after changing the Vercel domain and redeploy the API.
- **Frontend still calls localhost or the previous API:** set `VITE_API_URL` in Vercel's project settings, then make a new deployment.
- **API fails at startup:** check Render logs and confirm `APP_ENV=production`, `DATABASE_URL` is a reachable PostgreSQL URL, and `FRONTEND_ORIGINS` is non-empty and not `*`.
- **First API request is slow:** a free Render service may be waking from sleep.
- **Offline page is blank or old:** first load the site successfully online, then refresh. If needed, update/reinstall the PWA from browser site settings. Do not clear browser storage while reports are pending.
- **A queued report keeps failing:** restore network access, check the API health URL and the pending-sync error, then retry. A report is not confirmed until a server response is shown.

## Current security and migration notes

- No authentication exists. Production hides the operations screen and disables report status mutations, reanalysis, and photo-upload endpoints; do not expose admin functions until authentication is implemented.
- The production database setup uses additive schema creation for this prototype. Before expanding the schema or running a production migration, add and test a formal migration workflow and take a database backup.

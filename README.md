# NEXUS CITY AI
**One Platform. Every Problem. Smarter Cities.**

A student-friendly full-stack civic infrastructure reporting prototype. It includes a React + TypeScript frontend, FastAPI backend, SQLite development database, rule-based AI assistance, report tracking, a Leaflet/OpenStreetMap incident map, and data-driven dashboard analytics.

> **Honest status:** this is a local development prototype. The built-in analyzer is a rule-based fallback, not a trained model. Seed records are fictional demonstrations. No municipal, emergency, sensor, or government integrations are implied.

## Features
- Citizen issue submission with category, location, optional coordinates and image.
- Persistent report records and unique report IDs.
- Rule-based category, severity, summary, and department suggestions with an explanation.
- Interactive map using supplied/seeded coordinates.
- Dashboard and analytics calculated from database records.
- Admin demonstration workflow to change statuses and departments.
- Citizen tracking by report ID (demo-level public data only).
- SQLite by default; PostgreSQL can be configured with `DATABASE_URL` and `psycopg` installed.

## Run on Windows (VS Code)
### Backend (PowerShell terminal 1)
```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open API docs at http://127.0.0.1:8000/docs and health at http://127.0.0.1:8000/api/health.

### Frontend (PowerShell terminal 2)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev -- --host 127.0.0.1
```
Open the exact local URL printed by Vite (normally http://127.0.0.1:5173).

## Demo workflow
1. Open Report Issue and submit a report.
2. Open Dashboard or Live Map to see stored reports.
3. Open Admin Reports to review/update status and department.
4. Use Track Report with the public report ID shown after submission.

No demo administrator credentials are required by this prototype; admin endpoints are intentionally development-only and must be protected with real authentication before deployment.

## Environment
- `DATABASE_URL`: defaults to local SQLite.
- `FRONTEND_ORIGINS`: comma-separated allowed browser origins.
- `AI_PROVIDER`: `rule-based` unless a real provider adapter is implemented and configured.
- Never commit `.env`, API keys, or real personal information.

## Tests
```powershell
cd backend
.venv\Scripts\Activate.ps1
pytest -q
```

## Known limitations
- The current admin workflow is not production-authenticated; do not expose it publicly.
- Image upload is validated and stored locally in the development `uploads` directory; production should use private object storage and malware scanning.
- The AI module uses transparent rules only. It does not analyze image pixels or produce calibrated confidence scores.
- Map tiles require internet access and are subject to OpenStreetMap tile usage policies.
- Anonymous tracking uses a report identifier for this demo and is not sufficient for sensitive production records.

## Dependency-free preview
The FastAPI server also serves a lightweight, responsive browser preview at `http://127.0.0.1:8000/`. It uses the same API and supports live report counts, report submission, tracking, and a coordinate plot without requiring npm packages. The full React/Vite interface is in `frontend/`; run it on the Vite URL after `npm install` succeeds.

## Verification performed in the build workspace
- Backend test suite: 5 tests passed (health, report creation/tracking, validation, status history persistence, image signature validation).
- FastAPI health endpoint returned HTTP 200.
- Root browser preview returned HTTP 200 and HTML.
- OpenAPI schema includes the image upload endpoint.
- The React source files passed TypeScript parser syntax checks. A full React type-check/build could not be completed in the build workspace because npm registry DNS/network access was unavailable, so the React bundle has not been browser-verified here.

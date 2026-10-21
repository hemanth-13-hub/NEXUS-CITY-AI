# API overview

Development base URL: `http://127.0.0.1:8000`. In production, use the deployed API origin configured as `VITE_API_URL`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check verifies the database connection |
| POST | `/api/reports` | Validate and create an issue report |
| GET | `/api/reports` | List reports; supports `status`, `category`, `severity`, `q`, `limit`, `offset` |
| GET | `/api/reports/{report_id}` | Retrieve report by public ID or internal numeric ID |
| PATCH | `/api/reports/{report_id}` | Development-only update to status, severity, or department; disabled in production |
| POST | `/api/reports/{report_id}/image` | Development-only validated image upload up to 5 MiB; disabled in production until durable storage is configured |
| POST | `/api/reports/{report_id}/analyze` | Refresh rule-based analysis; disabled in production |
| GET | `/api/reports/{report_id}/history` | View report status history |
| POST | `/api/track` | Return limited public tracking fields for a report ID (demo only) |
| GET | `/api/dashboard/summary` | Status and severity counts |
| GET | `/api/dashboard/analytics` | Trends, category/status/severity counts, department workload, resolution time |
| GET | `/api/map/reports` | Reports with valid coordinates |

### Idempotent offline report submission

`POST /api/reports` accepts an optional `Idempotency-Key` header containing a UUID. Offline synchronization uses the same key on every retry. Repeated requests with the same key and payload return the original report instead of creating duplicates; reusing a key with a different payload returns HTTP 409. Existing clients may omit the header.

Production accepts only configured `FRONTEND_ORIGINS` and requires PostgreSQL. Admin mutations, analysis refreshes, and local-file image uploads are disabled in production because this prototype has no authentication/authorization and local hosting filesystems are not durable.

Interactive OpenAPI docs are available at `/docs` when the backend is running. Protect or disable the docs endpoint as part of a production security review if required by your deployment.

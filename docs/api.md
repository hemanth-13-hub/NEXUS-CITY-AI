# API overview

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API health and active fallback mode |
| POST | `/api/reports` | Validate and create an issue report |
| GET | `/api/reports` | List reports; supports `status`, `category`, `severity`, `q`, `limit`, `offset` |
| GET | `/api/reports/{report_id}` | Retrieve report by public ID or internal numeric ID |
| PATCH | `/api/reports/{report_id}` | Development-only update to status, severity, or department |
| POST | `/api/reports/{report_id}/image` | Upload validated image up to 5 MiB |
| POST | `/api/reports/{report_id}/analyze` | Refresh rule-based analysis |
| GET | `/api/reports/{report_id}/history` | View report status history |
| POST | `/api/track` | Return limited public tracking fields for a report ID (demo only) |
| GET | `/api/dashboard/summary` | Status and severity counts |
| GET | `/api/dashboard/analytics` | Trends, category/status/severity counts, department workload, resolution time |
| GET | `/api/map/reports` | Reports with valid coordinates |

Interactive OpenAPI docs are available at `/docs` when the backend is running.

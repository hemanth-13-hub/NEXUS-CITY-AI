# Architecture

```mermaid
flowchart TD
  Citizen[Citizen / Browser] --> UI[React + TypeScript + Vite]
  Admin[Operations user / Browser] --> UI
  UI -->|JSON REST requests| API[FastAPI]
  API --> Reports[Report routes]
  API --> Analytics[Dashboard and map routes]
  Reports --> AI[Rule-based analysis service]
  Reports --> ORM[SQLAlchemy]
  Analytics --> ORM
  ORM --> DB[(SQLite development DB)]
  Reports --> Files[Local uploads directory]
  UI --> Map[Leaflet + OpenStreetMap tiles]
```

## Trust boundaries
- The browser is untrusted; backend Pydantic schemas validate submitted fields.
- Uploaded images are limited by size and validated by declared type plus file signature. Production deployments still need malware scanning, private object storage, and authorization.
- Rule-based analysis is an explainable fallback, not a trained AI model.
- Administrative status changes are currently a development-only endpoint without authentication. Do not expose this prototype publicly.
- Map markers are citizen reports or explicitly fictional seed data, not verified hazards.

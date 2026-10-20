# Database notes

The default development database is SQLite at `backend/nexus_city.db`. SQLAlchemy creates the `reports` and `report_history` tables on startup; no GUI-based table creation is needed.

## reports
Stores public report ID, title, description, citizen category, AI-suggested category, location and coordinates, preliminary severity and explanation, summary, department, status, optional image reference, and timestamps.

## report_history
Stores report ID, previous status, new status, actor label, optional change note, and timestamp.

For PostgreSQL, set `DATABASE_URL` to a valid SQLAlchemy PostgreSQL URL and install an appropriate PostgreSQL driver. Schema migrations are not yet configured; production use should add Alembic migrations.

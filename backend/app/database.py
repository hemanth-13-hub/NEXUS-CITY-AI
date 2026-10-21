from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


def ensure_schema():
    Base.metadata.create_all(bind=engine)
    report_columns = {
        column["name"] for column in inspect(engine).get_columns("reports")
    }
    with engine.begin() as connection:
        if "idempotency_key" not in report_columns:
            connection.execute(
                text("ALTER TABLE reports ADD COLUMN idempotency_key VARCHAR(36)")
            )
        if "idempotency_payload_hash" not in report_columns:
            connection.execute(
                text(
                    "ALTER TABLE reports "
                    "ADD COLUMN idempotency_payload_hash VARCHAR(64)"
                )
            )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "uq_reports_idempotency_key ON reports (idempotency_key)"
            )
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

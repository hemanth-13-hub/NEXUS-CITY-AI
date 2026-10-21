import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'nexus_city.db'}").strip()
if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    parsed_database_url = urlsplit(DATABASE_URL)
    DATABASE_URL = urlunsplit(
        ("postgresql+psycopg", *parsed_database_url[1:])
    )

frontend_origins_setting = os.getenv("FRONTEND_ORIGINS")
FRONTEND_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in (
        frontend_origins_setting
        if frontend_origins_setting is not None
        else "http://127.0.0.1:5173,http://localhost:5173"
    ).split(",")
    if origin.strip()
]
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

if APP_ENV == "production":
    if frontend_origins_setting is None or not FRONTEND_ORIGINS:
        raise ValueError("FRONTEND_ORIGINS must contain the deployed frontend origin")
    if any("*" in origin for origin in FRONTEND_ORIGINS):
        raise ValueError("Wildcard CORS origins are not allowed in production")
    if any(
        urlsplit(origin).scheme != "https"
        or not urlsplit(origin).netloc
        or urlsplit(origin).path
        or urlsplit(origin).query
        or urlsplit(origin).fragment
        for origin in FRONTEND_ORIGINS
    ):
        raise ValueError("Production FRONTEND_ORIGINS must be HTTPS origins only")
    if DATABASE_URL.startswith("sqlite"):
        raise ValueError("Production requires a durable PostgreSQL DATABASE_URL")

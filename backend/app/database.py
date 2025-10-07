# backend/app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _normalize_url(url: str) -> str:
    """
    Ensure the SQLAlchemy URL uses the psycopg (v3) driver.
    - Converts ...+psycopg2 -> ...+psycopg
    - Converts postgres://... -> postgresql+psycopg://...
    - If driver not specified, adds +psycopg
    """
    if "+psycopg2" in url:
        return url.replace("+psycopg2", "+psycopg")
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


# Default points to local dev on port 5433 since your Postgres runs there.
# Override via the DATABASE_URL env var if needed.
DEFAULT_URL = "postgresql+psycopg://postgres:postgres@localhost:5433/qms"
DB_URL = _normalize_url(os.getenv("DATABASE_URL", DEFAULT_URL))

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,  # drops dead connections cleanly
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
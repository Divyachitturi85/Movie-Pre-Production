import logging
from typing import Dict, Any
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger("movie_preprod_backend.database")

def normalize_database_url(url: str) -> str:
    """
    Normalizes PostgreSQL database URLs for SQLAlchemy 2.0 compatibility.
    Render typically injects `postgres://...` which is deprecated in SQLAlchemy 2.0
    and must be converted to `postgresql+psycopg2://...`.
    Unadorned `postgresql://...` is also converted to explicit `postgresql+psycopg2://...`.
    """
    if not url or not url.strip():
        return "sqlite:///./movie_preproduction.db"

    url = url.strip()

    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return url

def get_sanitized_db_url(url: str) -> str:
    """Returns a sanitized DB URL masking embedded passwords for secure logging."""
    try:
        parsed = urlparse(url)
        if parsed.password:
            netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            return parsed._replace(netloc=netloc).geturl()
        return url
    except Exception:
        return "sqlite:///./movie_preproduction.db"

# Resolve normalized database URL
db_url = normalize_database_url(settings.DATABASE_URL)

engine_kwargs: Dict[str, Any] = {"echo": False}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production PostgreSQL connection pooling configuration
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    db_url,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

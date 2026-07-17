"""Database engine construction."""

from sqlalchemy import Engine, create_engine

from lotto_analysis.config import Settings


def create_database_engine(settings: Settings) -> Engine:
    """Create a future-style SQLAlchemy engine for PostgreSQL."""
    if not settings.postgres_password:
        raise ValueError("POSTGRES_PASSWORD is required for database access")
    return create_engine(settings.database_url, pool_pre_ping=True)

"""FastAPI dependencies for settings and repositories."""

from functools import lru_cache

from sqlalchemy import Engine

from lotto_analysis.config import Settings
from lotto_analysis.database import create_database_engine
from lotto_analysis.repositories import DrawRepository, PostgresDrawRepository


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return process-wide environment settings."""
    return Settings.from_env()


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return one process-wide PostgreSQL connection pool."""
    return create_database_engine(get_settings())


def get_draw_repository() -> DrawRepository:
    """Build a draw repository backed by the shared engine."""
    return PostgresDrawRepository(get_engine())


def dispose_engine() -> None:
    """Dispose the cached pool at API shutdown without creating a new engine."""
    if get_engine.cache_info().currsize:
        get_engine().dispose()
        get_engine.cache_clear()
    get_settings.cache_clear()

"""SQLAlchemy database infrastructure."""

from lotto_analysis.database.session import create_database_engine

__all__ = ["create_database_engine"]

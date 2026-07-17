"""Draw data repository interfaces and adapters."""

from lotto_analysis.repositories.base import DrawRepository
from lotto_analysis.repositories.csv_draw import CsvDrawRepository
from lotto_analysis.repositories.memory_draw import InMemoryDrawRepository
from lotto_analysis.repositories.postgres_draw import PostgresDrawRepository

__all__ = [
    "CsvDrawRepository",
    "DrawRepository",
    "InMemoryDrawRepository",
    "PostgresDrawRepository",
]

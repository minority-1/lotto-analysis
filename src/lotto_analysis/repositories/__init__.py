"""Draw data repository interfaces and adapters."""

from lotto_analysis.repositories.base import DrawRepository
from lotto_analysis.repositories.csv_draw import CsvDrawRepository

__all__ = ["CsvDrawRepository", "DrawRepository"]


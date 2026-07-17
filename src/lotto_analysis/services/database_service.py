"""Synchronize processed CSV data with PostgreSQL and verify parity."""

from lotto_analysis.analysis import analyze_draws
from lotto_analysis.models.database import (
    DatabaseImportResult,
    DatabaseVerificationResult,
)
from lotto_analysis.repositories import CsvDrawRepository, PostgresDrawRepository


class DatabaseService:
    """Coordinate CSV import and repository equivalence checks."""

    def __init__(
        self,
        csv_repository: CsvDrawRepository,
        postgres_repository: PostgresDrawRepository,
    ) -> None:
        self._csv_repository = csv_repository
        self._postgres_repository = postgres_repository

    def import_draws(self) -> DatabaseImportResult:
        """Upsert every validated CSV draw and report resulting counts."""
        draws = self._csv_repository.list_draws()
        synchronized = self._postgres_repository.upsert_draws(draws)
        database_count = len(self._postgres_repository.list_draws())
        return DatabaseImportResult(len(draws), synchronized, database_count)

    def verify(self) -> DatabaseVerificationResult:
        """Compare normalized rows and their basic analysis results."""
        csv_draws = self._csv_repository.list_draws()
        database_draws = self._postgres_repository.list_draws()
        draw_matches = csv_draws == database_draws
        analysis_matches = False
        if csv_draws and database_draws:
            analysis_matches = analyze_draws(csv_draws) == analyze_draws(database_draws)
        return DatabaseVerificationResult(
            csv_count=len(csv_draws),
            database_count=len(database_draws),
            draw_data_matches=draw_matches,
            basic_analysis_matches=analysis_matches,
        )

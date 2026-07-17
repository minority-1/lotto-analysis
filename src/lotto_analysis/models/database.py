"""Results for database synchronization and verification."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseImportResult:
    """Summarize one idempotent CSV-to-PostgreSQL synchronization."""

    source_count: int
    synchronized_count: int
    database_count: int


@dataclass(frozen=True)
class DatabaseVerificationResult:
    """Report data and analysis equivalence between CSV and PostgreSQL."""

    csv_count: int
    database_count: int
    draw_data_matches: bool
    basic_analysis_matches: bool

    @property
    def matches(self) -> bool:
        """Return whether both stored data and calculated analysis agree."""
        return self.draw_data_matches and self.basic_analysis_matches

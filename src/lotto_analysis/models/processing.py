"""Models describing validated draws and batch processing results."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from lotto_analysis.models.draw import LottoDraw


@dataclass(frozen=True)
class ValidationIssue:
    """Describe one raw file that could not become a validated draw."""

    source_file: str
    reason: str
    draw_number: Optional[int] = None


@dataclass(frozen=True)
class ProcessingSummary:
    """Summarize one complete raw-to-processed run."""

    total_files: int
    draws: Tuple[LottoDraw, ...]
    issues: Tuple[ValidationIssue, ...]
    duplicate_draws: Tuple[int, ...]
    missing_draws: Tuple[int, ...]
    csv_path: Path
    report_path: Path

    @property
    def valid_count(self) -> int:
        """Return the number of rows written to the processed CSV."""
        return len(self.draws)

    @property
    def error_count(self) -> int:
        """Return the number of invalid or duplicate raw files."""
        return len(self.issues)


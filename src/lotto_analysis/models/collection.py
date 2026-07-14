"""Models describing a range collection run."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CollectionFailure:
    """Describe one draw that could not be collected."""

    draw_number: int
    reason: str


@dataclass(frozen=True)
class CollectionSummary:
    """Summarize a completed sequential collection run."""

    start_draw: int
    end_draw: int
    successful_draws: Tuple[int, ...]
    skipped_draws: Tuple[int, ...]
    failures: Tuple[CollectionFailure, ...]

    @property
    def success_count(self) -> int:
        """Return the number of successfully collected draws."""
        return len(self.successful_draws)

    @property
    def failure_count(self) -> int:
        """Return the number of failed draws."""
        return len(self.failures)

    @property
    def skipped_count(self) -> int:
        """Return the number of valid existing draws skipped for resume."""
        return len(self.skipped_draws)

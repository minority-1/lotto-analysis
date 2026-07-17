"""Models used by the initial read-only dashboard."""

from dataclasses import dataclass
from typing import Optional, Tuple

from lotto_analysis.models.draw import LottoDraw


@dataclass(frozen=True)
class DashboardSummary:
    """Describe normalized draw coverage and the latest available draw."""

    total_draws: int
    first_draw_number: Optional[int]
    latest_draw: Optional[LottoDraw]
    missing_draw_numbers: Tuple[int, ...]

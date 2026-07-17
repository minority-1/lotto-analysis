"""Read-only application service for dashboard draw coverage."""

from lotto_analysis.models.dashboard import DashboardSummary
from lotto_analysis.repositories import DrawRepository


class DashboardService:
    """Build dashboard data without coupling it to Streamlit."""

    def __init__(self, repository: DrawRepository) -> None:
        self._repository = repository

    def summarize(self) -> DashboardSummary:
        """Return draw coverage, missing numbers, and the latest draw."""
        draws = self._repository.list_draws()
        if not draws:
            return DashboardSummary(
                total_draws=0,
                first_draw_number=None,
                latest_draw=None,
                missing_draw_numbers=(),
            )
        available = {draw.draw_number for draw in draws}
        first = draws[0].draw_number
        latest = draws[-1]
        missing = tuple(
            draw_number
            for draw_number in range(1, latest.draw_number + 1)
            if draw_number not in available
        )
        return DashboardSummary(
            total_draws=len(draws),
            first_draw_number=first,
            latest_draw=latest,
            missing_draw_numbers=missing,
        )

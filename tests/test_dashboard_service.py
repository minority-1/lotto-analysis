from datetime import date

from lotto_analysis.models import LottoDraw
from lotto_analysis.repositories import InMemoryDrawRepository
from lotto_analysis.services import DashboardService


def _draw(draw_number: int) -> LottoDraw:
    return LottoDraw(
        draw_number=draw_number,
        draw_date=date(2026, 7, 1),
        numbers=(1, 2, 3, 4, 5, 6),
        bonus_number=7,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_dashboard_summary_reports_latest_draw_and_missing_numbers() -> None:
    result = DashboardService(
        InMemoryDrawRepository((_draw(2), _draw(3), _draw(5)))
    ).summarize()

    assert result.total_draws == 3
    assert result.first_draw_number == 2
    assert result.latest_draw == _draw(5)
    assert result.missing_draw_numbers == (1, 4)


def test_dashboard_summary_supports_empty_repository() -> None:
    result = DashboardService(InMemoryDrawRepository(())).summarize()

    assert result.total_draws == 0
    assert result.first_draw_number is None
    assert result.latest_draw is None
    assert result.missing_draw_numbers == ()

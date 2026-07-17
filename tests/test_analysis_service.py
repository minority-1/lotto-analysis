from datetime import date
from typing import Tuple

from lotto_analysis.models import LottoDraw
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services import AnalysisService


class StubRepository(DrawRepository):
    def __init__(self) -> None:
        self.requested_recent = -1

    def list_draws(self, recent: int = 0) -> Tuple[LottoDraw, ...]:
        self.requested_recent = recent
        return (
            LottoDraw(
                draw_number=1,
                draw_date=date(2026, 7, 1),
                numbers=(1, 2, 3, 4, 5, 6),
                bonus_number=7,
                first_prize_winners=1,
                first_prize_amount=100,
                total_sales_amount=1000,
                collected_at=None,
            ),
        )


def test_analysis_service_passes_range_to_repository() -> None:
    repository = StubRepository()

    result = AnalysisService(repository).analyze(recent=50)

    assert repository.requested_recent == 50
    assert result.total_draws == 1


def test_analysis_service_requires_two_complete_comparison_periods() -> None:
    repository = StubRepository()

    try:
        AnalysisService(repository).compare(recent=1)
    except ValueError as exc:
        assert "two complete periods" in str(exc)
    else:
        raise AssertionError("comparison should require two periods")


def test_analysis_service_passes_relationship_options_to_repository() -> None:
    repository = StubRepository()

    result = AnalysisService(repository).relationships(recent=100, anchor_number=1)

    assert repository.requested_recent == 100
    assert result.anchor_number == 1
    assert result.anchor_appearance_count == 1


def test_analysis_service_passes_matrix_range_to_repository() -> None:
    repository = StubRepository()

    result = AnalysisService(repository).matrix(recent=30)

    assert repository.requested_recent == 30
    assert result.total_draws == 1


def test_analysis_service_requires_two_complete_matrix_periods() -> None:
    repository = StubRepository()

    try:
        AnalysisService(repository).compare_matrices(recent=1)
    except ValueError as exc:
        assert "two complete matrix periods" in str(exc)
    else:
        raise AssertionError("matrix comparison should require two periods")


def test_analysis_service_passes_pattern_range_to_repository() -> None:
    repository = StubRepository()

    result = AnalysisService(repository).patterns(recent=20)

    assert repository.requested_recent == 20
    assert result.total_draws == 1

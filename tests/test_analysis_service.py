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

    result = AnalysisService(repository).analyze(recent=1)

    assert repository.requested_recent == 1
    assert result.total_draws == 1


def test_analysis_service_analyzes_inclusive_draw_and_date_ranges() -> None:
    repository = StubRepository()
    service = AnalysisService(repository)

    by_draw = service.analyze_range(start_draw=1, end_draw=1)
    by_date = service.analyze_range(
        start_date=date(2026, 7, 1), end_date=date(2026, 7, 1)
    )

    assert by_draw.total_draws == 1
    assert by_date.total_draws == 1


def test_analysis_service_rejects_incomplete_or_mixed_custom_ranges() -> None:
    service = AnalysisService(StubRepository())

    for arguments in (
        {"start_draw": 1},
        {"start_date": date(2026, 7, 1)},
        {
            "start_draw": 1,
            "end_draw": 1,
            "start_date": date(2026, 7, 1),
            "end_date": date(2026, 7, 1),
        },
    ):
        try:
            service.analyze_range(**arguments)  # type: ignore[arg-type]
        except ValueError:
            pass
        else:
            raise AssertionError("invalid custom range should fail")


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

    result = AnalysisService(repository).relationships(recent=1, anchor_number=1)

    assert repository.requested_recent == 1
    assert result.anchor_number == 1
    assert result.anchor_appearance_count == 1


def test_analysis_service_passes_matrix_range_to_repository() -> None:
    repository = StubRepository()

    result = AnalysisService(repository).matrix(recent=1)

    assert repository.requested_recent == 1
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

    result = AnalysisService(repository).patterns(recent=1)

    assert repository.requested_recent == 1
    assert result.total_draws == 1


def test_analysis_service_passes_similarity_range_to_repository() -> None:
    repository = StubRepository()

    result = AnalysisService(repository).similarity(recent=1)

    assert repository.requested_recent == 1
    assert result.total_draws == 1


def test_analysis_service_rejects_recent_above_available_count() -> None:
    repository = StubRepository()

    try:
        AnalysisService(repository).patterns(recent=2)
    except ValueError as exc:
        assert str(exc) == "recent 2 exceeds available draw count 1"
    else:
        raise AssertionError("short recent result should fail")

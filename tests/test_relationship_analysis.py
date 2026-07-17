from datetime import date

import pytest

from lotto_analysis.analysis import analyze_relationships
from lotto_analysis.models import LottoDraw


def _draw(draw_number: int, numbers: tuple) -> LottoDraw:
    return LottoDraw(
        draw_number=draw_number,
        draw_date=date(2026, 7, draw_number),
        numbers=numbers,
        bonus_number=45,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_relationship_analysis_counts_and_sorts_combinations() -> None:
    result = analyze_relationships(
        (
            _draw(1, (1, 2, 3, 4, 5, 6)),
            _draw(2, (1, 2, 3, 7, 8, 9)),
        ),
        anchor_number=1,
    )

    assert result.total_draws == 2
    assert result.pairs[0].numbers == (1, 2)
    assert result.pairs[0].count == 2
    assert result.pairs[0].draw_rate == 1.0
    assert result.triples[0].numbers == (1, 2, 3)
    assert result.triples[0].count == 2
    assert result.anchor_appearance_count == 2
    assert result.companions[0].number == 2
    assert result.companions[0].conditional_rate == 1.0
    assert tuple(item.number for item in result.companions[:2]) == (2, 3)
    assert result.distances[0].distance == 1
    assert result.distances[0].count == 9
    assert result.distances[0].observation_rate == 9 / 30
    assert result.adjacent_pair_count == 9
    assert result.adjacent_draw_count == 2
    assert result.adjacent_draw_rate == 1.0
    assert result.consecutive_groups[0].numbers == (1, 2, 3)
    assert result.lag_overlaps[0].compared_draws == 1
    assert result.lag_overlaps[0].overlap_distribution[3] == 1
    assert result.lag_overlaps[0].average_overlap == 3.0


def test_relationship_analysis_returns_no_companions_when_anchor_is_absent() -> None:
    result = analyze_relationships(
        (_draw(1, (1, 2, 3, 4, 5, 6)),), anchor_number=44
    )

    assert result.anchor_appearance_count == 0
    assert result.companions == ()


def test_relationship_analysis_counts_same_last_digits_and_consecutive_groups() -> None:
    result = analyze_relationships((_draw(1, (1, 2, 11, 12, 21, 22)),))

    assert result.same_last_digit_pair_count == 6
    assert result.same_last_digit_draw_count == 1
    assert result.same_last_digit_draw_rate == 1.0
    assert tuple(item.numbers for item in result.consecutive_groups) == (
        (1, 2),
        (11, 12),
        (21, 22),
    )


def test_relationship_analysis_uses_exact_draw_numbers_for_lags() -> None:
    result = analyze_relationships(
        (
            _draw(1, (1, 2, 3, 4, 5, 6)),
            _draw(3, (1, 7, 8, 9, 10, 11)),
        )
    )

    assert result.lag_overlaps[0].compared_draws == 0
    assert result.lag_overlaps[1].compared_draws == 1
    assert result.lag_overlaps[1].average_overlap == 1.0


@pytest.mark.parametrize("anchor", [0, 46, True])
def test_relationship_analysis_rejects_invalid_anchor(anchor: object) -> None:
    with pytest.raises(ValueError):
        analyze_relationships(
            (_draw(1, (1, 2, 3, 4, 5, 6)),), anchor_number=anchor  # type: ignore[arg-type]
        )

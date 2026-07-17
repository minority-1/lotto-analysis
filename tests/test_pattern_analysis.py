from datetime import date

import pytest

from lotto_analysis.analysis import analyze_patterns
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


def test_pattern_analysis_calculates_draw_properties() -> None:
    result = analyze_patterns((_draw(1, (1, 2, 3, 4, 5, 6)),))
    item = result.draws[0]

    assert item.ac_value == 0
    assert item.adjacent_gaps == (1, 1, 1, 1, 1)
    assert item.prime_count == 3
    assert item.composite_count == 2
    assert item.square_count == 2
    assert item.has_square is True
    assert item.number_sum == 21
    assert (item.sum_band_minimum, item.sum_band_maximum) == (21, 100)
    assert item.last_digit_sum == 21


def test_pattern_analysis_aggregates_distributions() -> None:
    result = analyze_patterns(
        (
            _draw(1, (1, 2, 3, 4, 5, 6)),
            _draw(2, (1, 2, 4, 8, 16, 32)),
        )
    )

    assert result.draws[1].ac_value == 10
    assert result.draws[1].adjacent_gaps == (1, 2, 4, 8, 16)
    assert tuple((item.value, item.count) for item in result.ac_distribution) == (
        (0, 1),
        (10, 1),
    )
    assert sum(item.count for item in result.gap_distribution) == 10
    assert result.prime_count_distribution[1].count == 1
    assert result.prime_count_distribution[3].count == 1
    assert result.composite_count_distribution[4].count == 1
    assert result.square_count_distribution[3].count == 1
    assert result.sum_band_distribution[0].count == 2
    assert result.last_digit_sum_minimum == 21
    assert result.last_digit_sum_maximum == 23
    assert result.last_digit_sum_mean == 22.0


def test_pattern_analysis_requires_draws() -> None:
    with pytest.raises(ValueError, match="at least one draw"):
        analyze_patterns(())

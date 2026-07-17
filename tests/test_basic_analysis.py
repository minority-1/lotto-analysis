from datetime import date

import pytest

from lotto_analysis.analysis import analyze_draws
from lotto_analysis.models import LottoDraw


def draw(number: int, numbers: tuple, bonus: int) -> LottoDraw:
    return LottoDraw(
        draw_number=number,
        draw_date=date(2026, 7, number),
        numbers=numbers,  # type: ignore[arg-type]
        bonus_number=bonus,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_analyze_draws_calculates_number_statistics() -> None:
    result = analyze_draws(
        (draw(1, (1, 2, 3, 4, 5, 6), 7), draw(2, (1, 8, 9, 10, 11, 12), 2))
    )

    number1 = result.number_statistics[0]
    number2 = result.number_statistics[1]
    number45 = result.number_statistics[44]
    assert result.total_draws == 2
    assert (result.start_draw, result.end_draw) == (1, 2)
    assert (number1.main_count, number1.main_rate) == (2, 1.0)
    assert (number1.last_draw_number, number1.absence_draws) == (2, 0)
    assert number2.bonus_count == 1
    assert (number45.main_count, number45.absence_draws) == (0, 2)


def test_analyze_draws_calculates_draw_characteristics() -> None:
    result = analyze_draws(
        (draw(1, (1, 2, 3, 4, 5, 6), 7), draw(2, (1, 8, 9, 10, 11, 12), 2))
    )

    first, second = result.draw_statistics
    assert first.number_sum == 21
    assert first.number_mean == 3.5
    assert first.number_median == 3.5
    assert (first.odd_count, first.even_count) == (3, 3)
    assert (first.low_count, first.high_count) == (6, 0)
    assert first.section_counts == (6, 0, 0, 0, 0)
    assert first.consecutive_pair_count == 5
    assert first.previous_draw_overlap is None
    assert second.section_counts == (4, 2, 0, 0, 0)
    assert second.previous_draw_overlap == 1
    assert result.summary.sum_min == 21
    assert result.summary.sum_max == 51
    assert result.summary.sum_mean == 36
    assert result.summary.odd_count_distribution[3] == 2
    assert result.summary.section_totals == (10, 2, 0, 0, 0)
    assert result.summary.consecutive_draw_count == 2


def test_analyze_draws_rejects_empty_or_duplicate_input() -> None:
    with pytest.raises(ValueError, match="at least one"):
        analyze_draws(())
    duplicate = draw(1, (1, 2, 3, 4, 5, 6), 7)
    with pytest.raises(ValueError, match="duplicate"):
        analyze_draws((duplicate, duplicate))

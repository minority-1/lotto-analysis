from datetime import date

from lotto_analysis.analysis import compare_periods
from lotto_analysis.models import LottoDraw


def draw(number: int, numbers: tuple) -> LottoDraw:
    return LottoDraw(
        draw_number=number,
        draw_date=date(2026, 7, number),
        numbers=numbers,  # type: ignore[arg-type]
        bonus_number=45,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_compare_periods_calculates_rate_and_rank_changes() -> None:
    result = compare_periods(
        (draw(1, (1, 2, 3, 4, 5, 6)),),
        (draw(2, (1, 7, 8, 9, 10, 11)),),
        "previous",
        "recent",
    )

    number1 = result.numbers[0]
    number2 = result.numbers[1]
    number7 = result.numbers[6]
    assert (number1.baseline_rate, number1.comparison_rate) == (1.0, 1.0)
    assert number1.rate_difference == 0
    assert (number2.rate_difference, number2.rank_change) == (-1.0, -6)
    assert (number7.rate_difference, number7.rank_change) == (1.0, 6)

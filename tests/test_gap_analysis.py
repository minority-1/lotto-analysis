from datetime import date

from lotto_analysis.analysis import analyze_gaps
from lotto_analysis.models import LottoDraw


def draw(number: int, includes_one: bool) -> LottoDraw:
    numbers = (1, 2, 3, 4, 5, 6) if includes_one else (2, 3, 4, 5, 6, 7)
    return LottoDraw(
        draw_number=number,
        draw_date=date(2026, 7, number),
        numbers=numbers,
        bonus_number=45,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_analyze_gaps_calculates_historical_gap_distribution() -> None:
    draws = tuple(
        draw(number, number in (1, 3, 6)) for number in range(1, 7)
    )

    result = analyze_gaps(draws)
    number1 = result.numbers[0]
    number45 = result.numbers[44]

    assert number1.appearance_draws == (1, 3, 6)
    assert number1.gaps == (2, 3)
    assert number1.mean_gap == 2.5
    assert number1.median_gap == 2.5
    assert (number1.minimum_gap, number1.maximum_gap) == (2, 3)
    assert (number1.latest_gap, number1.current_absence) == (3, 0)
    assert number1.gap_standard_deviation == 0.5
    assert number45.mean_gap is None
    assert number45.current_absence == 6


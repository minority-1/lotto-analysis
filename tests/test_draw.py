from datetime import date, datetime, timezone

import pytest

from lotto_analysis.models import LottoDraw


def make_draw(**overrides: object) -> LottoDraw:
    values = {
        "draw_number": 1,
        "draw_date": date(2002, 12, 7),
        "numbers": (10, 23, 29, 33, 37, 40),
        "bonus_number": 16,
        "first_prize_winners": 0,
        "first_prize_amount": 0,
        "total_sales_amount": 3_681_782_000,
        "collected_at": datetime(2026, 7, 14, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return LottoDraw(**values)  # type: ignore[arg-type]


def test_lotto_draw_accepts_valid_data() -> None:
    draw = make_draw()

    assert draw.draw_number == 1
    assert draw.numbers == (10, 23, 29, 33, 37, 40)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"draw_number": 0}, "positive integer"),
        ({"numbers": (1, 2, 3, 4, 5, 46)}, "between 1 and 45"),
        ({"numbers": (1, 2, 3, 4, 5, 5)}, "unique"),
        ({"numbers": (2, 1, 3, 4, 5, 6)}, "ascending"),
        ({"bonus_number": 10}, "differ"),
        ({"first_prize_amount": -1}, "non-negative"),
    ],
)
def test_lotto_draw_rejects_invalid_data(overrides: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_draw(**overrides)  # type: ignore[arg-type]


from datetime import date, datetime, timezone

import pytest

from lotto_analysis.collectors import DrawCollector
from lotto_analysis.models import LottoDraw


class StubCollector(DrawCollector):
    def collect_draw(self, draw_number: int) -> LottoDraw:
        return LottoDraw(
            draw_number=draw_number,
            draw_date=date(2002, 12, 7),
            numbers=(10, 23, 29, 33, 37, 40),
            bonus_number=16,
            first_prize_winners=0,
            first_prize_amount=0,
            total_sales_amount=3_681_782_000,
            collected_at=datetime(2026, 7, 14, tzinfo=timezone.utc),
        )


def test_collector_interface_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        DrawCollector()


def test_collector_implementation_returns_one_draw() -> None:
    draw = StubCollector().collect_draw(1)

    assert draw.draw_number == 1


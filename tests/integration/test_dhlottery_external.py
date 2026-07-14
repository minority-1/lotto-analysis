import os

import pytest

from lotto_analysis.collectors import DhlotteryDrawCollector


pytestmark = [
    pytest.mark.external,
    pytest.mark.skipif(
        os.environ.get("LOTTO_RUN_EXTERNAL_TESTS") != "1",
        reason="set LOTTO_RUN_EXTERNAL_TESTS=1 to call the official website",
    ),
]


def test_collect_known_draw_from_official_website() -> None:
    draw = DhlotteryDrawCollector().collect_draw(1070)

    assert draw.numbers == (3, 6, 14, 22, 30, 41)
    assert draw.bonus_number == 36
    assert draw.total_sales_amount == 107_222_802_000


def test_get_latest_draw_number_from_official_website() -> None:
    latest = DhlotteryDrawCollector().get_latest_draw_number()

    assert latest >= 1232

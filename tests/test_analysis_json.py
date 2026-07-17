import json
from datetime import date
from pathlib import Path

import pytest

from lotto_analysis.analysis import analyze_draws
from lotto_analysis.models import LottoDraw
from lotto_analysis.storage.analysis_json import write_analysis_json


def draw() -> LottoDraw:
    return LottoDraw(
        draw_number=1,
        draw_date=date(2026, 7, 1),
        numbers=(1, 2, 3, 4, 5, 6),
        bonus_number=7,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_write_analysis_json_serializes_dataclass_and_dates(tmp_path: Path) -> None:
    result = analyze_draws((draw(),))

    path = write_analysis_json(tmp_path / "analysis.json", result)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["result"]["total_draws"] == 1
    assert payload["result"]["number_statistics"][0]["last_draw_date"] == "2026-07-01"


def test_write_analysis_json_requires_dataclass(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="dataclass"):
        write_analysis_json(tmp_path / "invalid.json", {})

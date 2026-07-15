import json
from pathlib import Path

import pytest

from lotto_analysis.processors import RawDrawValidationError, parse_raw_draw


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "dhlottery_1070.json"


def requested_record() -> dict:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return next(item for item in payload["data"]["list"] if item["ltEpsd"] == 1070)


def test_parse_raw_draw_normalizes_valid_official_record() -> None:
    draw = parse_raw_draw(requested_record())

    assert draw.draw_number == 1070
    assert draw.draw_date.isoformat() == "2023-06-03"
    assert draw.numbers == (3, 6, 14, 22, 30, 41)
    assert draw.collected_at is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tm1WnNo", 46),
        ("tm2WnNo", 3),
        ("bnsWnNo", 3),
        ("rnk1WnAmt", 1.5),
        ("ltRflYmd", "20230230"),
    ],
)
def test_parse_raw_draw_rejects_invalid_record(field: str, value: object) -> None:
    record = requested_record()
    record[field] = value

    with pytest.raises(RawDrawValidationError):
        parse_raw_draw(record)


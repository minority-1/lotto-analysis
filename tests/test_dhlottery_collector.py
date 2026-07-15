from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock

import pytest
import requests

from lotto_analysis.collectors import (
    CollectorConnectionError,
    DhlotteryDrawCollector,
    DrawNotFoundError,
    ResponseFormatError,
)
from lotto_analysis.config import Settings
from lotto_analysis.storage import RawJsonStore


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "dhlottery_1070.json"
COLLECTED_AT = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def load_payload() -> Dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def make_collector(payload: Any) -> tuple[DhlotteryDrawCollector, Mock]:
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    session = Mock()
    session.get.return_value = response
    collector = DhlotteryDrawCollector(session=session, now=lambda: COLLECTED_AT)
    return collector, session


def test_collect_draw_selects_and_normalizes_requested_draw() -> None:
    collector, session = make_collector(load_payload())

    draw = collector.collect_draw(1070)

    assert draw.draw_number == 1070
    assert draw.draw_date.isoformat() == "2023-06-03"
    assert draw.numbers == (3, 6, 14, 22, 30, 41)
    assert draw.bonus_number == 36
    assert draw.first_prize_winners == 14
    assert draw.first_prize_amount == 1_859_116_929
    assert draw.total_sales_amount == 107_222_802_000
    assert draw.collected_at == COLLECTED_AT
    session.get.assert_called_once_with(
        "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do",
        params={"srchDir": "center", "srchLtEpsd": "1070"},
        headers={"Accept": "application/json", "User-Agent": "lotto-analysis/0.1"},
        timeout=10.0,
    )


def test_collect_draw_stores_only_requested_official_record(tmp_path: Path) -> None:
    response = Mock()
    response.json.return_value = load_payload()
    response.raise_for_status.return_value = None
    session = Mock()
    session.get.return_value = response
    raw_store = RawJsonStore(tmp_path)
    collector = DhlotteryDrawCollector(
        session=session,
        raw_store=raw_store,
        now=lambda: COLLECTED_AT,
    )

    collector.collect_draw(1070)

    stored = json.loads(raw_store.path_for(1070).read_text(encoding="utf-8"))
    assert stored["ltEpsd"] == 1070
    assert "data" not in stored


def test_collect_draw_does_not_store_record_that_fails_normalization(
    tmp_path: Path,
) -> None:
    raw_store = RawJsonStore(tmp_path)
    response = Mock()
    response.json.return_value = {"data": {"list": [{"ltEpsd": 1070}]}}
    response.raise_for_status.return_value = None
    session = Mock()
    session.get.return_value = response
    collector = DhlotteryDrawCollector(
        session=session,
        raw_store=raw_store,
        now=lambda: COLLECTED_AT,
    )

    with pytest.raises(ResponseFormatError):
        collector.collect_draw(1070)

    assert not raw_store.path_for(1070).exists()
    assert not raw_store.has_valid_draw(1070)


def test_collect_draw_rejects_invalid_draw_number_before_request() -> None:
    collector, session = make_collector(load_payload())

    with pytest.raises(ValueError, match="positive"):
        collector.collect_draw(0)

    session.get.assert_not_called()


def test_collect_draw_uses_provided_settings(tmp_path: Path) -> None:
    settings = Settings.from_env(
        environ={
            "LOTTO_SOURCE_BASE_URL": "https://example.test/",
            "LOTTO_REQUEST_TIMEOUT_SECONDS": "2.5",
            "LOTTO_USER_AGENT": "custom-agent",
        },
        project_root=tmp_path,
    )
    response = Mock()
    response.json.return_value = load_payload()
    response.raise_for_status.return_value = None
    session = Mock()
    session.get.return_value = response
    collector = DhlotteryDrawCollector(
        settings=settings, session=session, now=lambda: COLLECTED_AT
    )

    collector.collect_draw(1070)

    session.get.assert_called_once_with(
        "https://example.test/lt645/selectPstLt645InfoNew.do",
        params={"srchDir": "center", "srchLtEpsd": "1070"},
        headers={"Accept": "application/json", "User-Agent": "custom-agent"},
        timeout=2.5,
    )


def test_collect_draw_reports_missing_requested_draw() -> None:
    collector, _ = make_collector(load_payload())

    with pytest.raises(DrawNotFoundError, match="9999"):
        collector.collect_draw(9999)


def test_get_latest_draw_number_from_official_page_markup() -> None:
    response = Mock()
    response.text = '<input type="hidden" id="opt_val" value="1232">'
    response.raise_for_status.return_value = None
    session = Mock()
    session.get.return_value = response
    collector = DhlotteryDrawCollector(session=session, sleep=lambda _: None)

    assert collector.get_latest_draw_number() == 1232


def test_get_latest_draw_number_rejects_changed_markup() -> None:
    response = Mock()
    response.text = "<html></html>"
    response.raise_for_status.return_value = None
    session = Mock()
    session.get.return_value = response
    collector = DhlotteryDrawCollector(session=session)

    with pytest.raises(ResponseFormatError, match="latest draw number"):
        collector.get_latest_draw_number()


def test_collect_draw_wraps_network_errors() -> None:
    session = Mock()
    session.get.side_effect = requests.Timeout("timed out")
    collector = DhlotteryDrawCollector(session=session, sleep=lambda _: None)

    with pytest.raises(CollectorConnectionError, match="1070"):
        collector.collect_draw(1070)

    assert session.get.call_count == 4


def test_collect_draw_retries_transient_error_then_succeeds(tmp_path: Path) -> None:
    settings = Settings.from_env(
        environ={
            "LOTTO_REQUEST_MAX_RETRIES": "2",
            "LOTTO_REQUEST_RETRY_BACKOFF_SECONDS": "0.25",
        },
        project_root=tmp_path,
    )
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = load_payload()
    session = Mock()
    session.get.side_effect = [requests.Timeout("temporary"), response]
    sleeps = []
    collector = DhlotteryDrawCollector(
        settings=settings,
        session=session,
        sleep=sleeps.append,
        now=lambda: COLLECTED_AT,
    )

    draw = collector.collect_draw(1070)

    assert draw.draw_number == 1070
    assert session.get.call_count == 2
    assert sleeps == [0.25]


def test_collect_draw_does_not_retry_non_transient_http_error() -> None:
    response = requests.Response()
    response.status_code = 404
    session = Mock()
    session.get.return_value = response
    collector = DhlotteryDrawCollector(session=session, sleep=lambda _: None)

    with pytest.raises(CollectorConnectionError):
        collector.collect_draw(1070)

    assert session.get.call_count == 1


def test_collect_draw_rejects_invalid_json() -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = requests.JSONDecodeError("invalid", "", 0)
    session = Mock()
    session.get.return_value = response
    collector = DhlotteryDrawCollector(session=session)

    with pytest.raises(ResponseFormatError, match="invalid JSON"):
        collector.collect_draw(1070)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"data": {}},
        {"data": {"list": ["not-an-object"]}},
        {"data": {"list": [{"ltEpsd": 1070}]}},
    ],
)
def test_collect_draw_rejects_malformed_payload(payload: Dict[str, Any]) -> None:
    collector, _ = make_collector(payload)

    with pytest.raises(ResponseFormatError):
        collector.collect_draw(1070)


@pytest.mark.parametrize("invalid_value", [1.5, "1.5", "", None, True])
def test_collect_draw_rejects_non_integer_numeric_field(invalid_value: Any) -> None:
    payload = load_payload()
    requested = next(
        item for item in payload["data"]["list"] if item["ltEpsd"] == 1070
    )
    requested["rnk1WnNope"] = invalid_value
    collector, _ = make_collector(payload)

    with pytest.raises(ResponseFormatError, match="rnk1WnNope"):
        collector.collect_draw(1070)

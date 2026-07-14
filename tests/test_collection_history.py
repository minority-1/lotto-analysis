from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from lotto_analysis.models import CollectionFailure, CollectionSummary
from lotto_analysis.storage import CollectionHistoryStore


STARTED_AT = datetime(2026, 7, 15, 0, 0, tzinfo=timezone.utc)
COMPLETED_AT = STARTED_AT + timedelta(seconds=3.25)


def test_history_store_persists_summary_and_failed_draws(tmp_path: Path) -> None:
    store = CollectionHistoryStore(tmp_path)
    summary = CollectionSummary(
        start_draw=1,
        end_draw=3,
        successful_draws=(1,),
        skipped_draws=(2,),
        failures=(CollectionFailure(draw_number=3, reason="network error"),),
    )

    path = store.save(
        command="collect-range 1 3",
        started_at=STARTED_AT,
        completed_at=COMPLETED_AT,
        summary=summary,
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] == "partial_failure"
    assert payload["duration_seconds"] == 3.25
    assert payload["counts"] == {"successful": 1, "skipped": 1, "failed": 1}
    assert payload["failures"] == [
        {"draw_number": 3, "reason": "network error"}
    ]


def test_history_store_persists_command_level_failure(tmp_path: Path) -> None:
    store = CollectionHistoryStore(tmp_path)

    path = store.save(
        command="collect-all",
        started_at=STARTED_AT,
        completed_at=COMPLETED_AT,
        error="latest draw lookup failed",
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] == "failed"
    assert payload["range"] is None
    assert payload["error"] == "latest draw lookup failed"


def test_history_store_never_overwrites_same_timestamp(tmp_path: Path) -> None:
    store = CollectionHistoryStore(tmp_path)

    first = store.save(
        "collect-all", STARTED_AT, COMPLETED_AT, error="first"
    )
    second = store.save(
        "collect-all", STARTED_AT, COMPLETED_AT, error="second"
    )

    assert first != second
    assert first.is_file()
    assert second.is_file()


def test_history_store_requires_timezone_aware_timestamps(tmp_path: Path) -> None:
    store = CollectionHistoryStore(tmp_path)

    with pytest.raises(ValueError, match="timezone"):
        store.save(
            "collect-all",
            datetime(2026, 7, 15),
            datetime(2026, 7, 15, 0, 1),
            error="failed",
        )

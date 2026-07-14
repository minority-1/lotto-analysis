from pathlib import Path
from typing import List, Optional

from lotto_analysis.collectors import CollectorError
from lotto_analysis.models import LottoDraw
from lotto_analysis.services import CollectionService
from lotto_analysis.storage import RawDataConflictError
from lotto_analysis.storage import RawJsonStore


class StubCollector:
    def __init__(
        self, failing_draws: Optional[List[int]] = None, latest: int = 3
    ) -> None:
        self.failing_draws = failing_draws or []
        self.latest = latest
        self.calls: List[int] = []

    def collect_draw(self, draw_number: int) -> LottoDraw:
        self.calls.append(draw_number)
        if draw_number in self.failing_draws:
            raise CollectorError("expected failure")
        return None  # type: ignore[return-value]

    def get_latest_draw_number(self) -> int:
        return self.latest


def test_collect_range_continues_after_known_failure() -> None:
    collector = StubCollector(failing_draws=[2])
    sleeps: List[float] = []
    service = CollectionService(
        collector,  # type: ignore[arg-type]
        raw_store=RawJsonStore(Path("unused")),
        request_interval_seconds=0.5,
        sleep=sleeps.append,
    )

    summary = service.collect_range(1, 3)

    assert collector.calls == [1, 2, 3]
    assert summary.successful_draws == (1, 3)
    assert summary.failure_count == 1
    assert summary.failures[0].draw_number == 2
    assert sleeps == [0.5, 0.5]


def test_collect_all_uses_latest_draw_number() -> None:
    collector = StubCollector(latest=2)
    service = CollectionService(
        collector,  # type: ignore[arg-type]
        raw_store=RawJsonStore(Path("unused")),
        request_interval_seconds=0,
    )

    summary = service.collect_all()

    assert collector.calls == [1, 2]
    assert summary.start_draw == 1
    assert summary.end_draw == 2


def test_collect_range_records_raw_file_conflict_and_continues(
    tmp_path: Path,
) -> None:
    collector = StubCollector()

    def collect_with_conflict(draw_number: int) -> LottoDraw:
        collector.calls.append(draw_number)
        if draw_number == 2:
            raise RawDataConflictError(2, {"value"}, tmp_path / "conflict.json")
        return None  # type: ignore[return-value]

    collector.collect_draw = collect_with_conflict  # type: ignore[assignment]
    service = CollectionService(
        collector,  # type: ignore[arg-type]
        raw_store=RawJsonStore(Path("unused")),
        request_interval_seconds=0,
    )

    summary = service.collect_range(1, 3)

    assert collector.calls == [1, 2, 3]
    assert summary.successful_draws == (1, 3)
    assert "changed fields: value" in summary.failures[0].reason


def test_collect_range_skips_valid_existing_draws(tmp_path: Path) -> None:
    raw_store = RawJsonStore(tmp_path)
    raw_store.save(1, {"ltEpsd": 1})
    collector = StubCollector(latest=2)
    service = CollectionService(
        collector,  # type: ignore[arg-type]
        raw_store=raw_store,
        request_interval_seconds=0,
    )

    summary = service.collect_range(1, 2)

    assert collector.calls == [2]
    assert summary.skipped_draws == (1,)


def test_collect_incremental_starts_after_greatest_stored_draw(
    tmp_path: Path,
) -> None:
    raw_store = RawJsonStore(tmp_path)
    raw_store.save(1, {"ltEpsd": 1})
    raw_store.save(2, {"ltEpsd": 2})
    collector = StubCollector(latest=4)
    service = CollectionService(
        collector,  # type: ignore[arg-type]
        raw_store=raw_store,
        request_interval_seconds=0,
    )

    summary = service.collect_incremental()

    assert collector.calls == [3, 4]
    assert summary.successful_draws == (3, 4)


def test_collect_missing_requests_only_gaps(tmp_path: Path) -> None:
    raw_store = RawJsonStore(tmp_path)
    raw_store.save(1, {"ltEpsd": 1})
    raw_store.save(3, {"ltEpsd": 3})
    collector = StubCollector(latest=3)
    service = CollectionService(
        collector,  # type: ignore[arg-type]
        raw_store=raw_store,
        request_interval_seconds=0,
    )

    summary = service.collect_missing()

    assert collector.calls == [2]
    assert summary.successful_draws == (2,)


def test_collect_range_reports_progress_for_each_processed_draw(
    tmp_path: Path,
) -> None:
    raw_store = RawJsonStore(tmp_path)
    raw_store.save(1, {"ltEpsd": 1})
    collector = StubCollector(failing_draws=[3])
    progress = []
    service = CollectionService(
        collector,  # type: ignore[arg-type]
        raw_store=raw_store,
        request_interval_seconds=0,
        progress=lambda processed, total, draw, status: progress.append(
            (processed, total, draw, status)
        ),
    )

    service.collect_range(1, 3)

    assert progress == [
        (1, 3, 1, "skipped"),
        (2, 3, 2, "collected"),
        (3, 3, 3, "failed"),
    ]

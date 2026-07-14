"""Orchestration for resumable Lotto draw collection."""

import logging
import time
from typing import Callable, Iterable, List, Optional

from lotto_analysis.collectors import CollectorError, DhlotteryDrawCollector
from lotto_analysis.models import CollectionFailure, CollectionSummary
from lotto_analysis.storage import RawDataConflictError, RawJsonStore


LOGGER = logging.getLogger(__name__)


class CollectionService:
    """Collect ranges, resume work, and discover incremental or missing draws."""

    def __init__(
        self,
        collector: DhlotteryDrawCollector,
        raw_store: RawJsonStore,
        request_interval_seconds: float = 0.5,
        sleep: Callable[[float], None] = time.sleep,
        progress: Optional[Callable[[int, int, int, str], None]] = None,
    ) -> None:
        if request_interval_seconds < 0:
            raise ValueError("request_interval_seconds cannot be negative")
        self._collector = collector
        self._raw_store = raw_store
        self._request_interval_seconds = request_interval_seconds
        self._sleep = sleep
        self._progress = progress

    def collect_all(self, resume: bool = True) -> CollectionSummary:
        """Collect draw 1 through latest, skipping valid files by default."""
        latest = self._collector.get_latest_draw_number()
        return self.collect_range(1, latest, resume=resume)

    def collect_range(
        self, start_draw: int, end_draw: int, resume: bool = True
    ) -> CollectionSummary:
        """Collect an inclusive range and continue after known failures."""
        if start_draw <= 0:
            raise ValueError("start_draw must be positive")
        if end_draw < start_draw:
            raise ValueError("end_draw must be greater than or equal to start_draw")
        return self._collect_numbers(
            range(start_draw, end_draw + 1),
            start_draw=start_draw,
            end_draw=end_draw,
            resume=resume,
        )

    def collect_incremental(self) -> CollectionSummary:
        """Collect only draws after the greatest valid stored draw."""
        latest = self._collector.get_latest_draw_number()
        stored = self._raw_store.list_draw_numbers()
        start_draw = max(stored) + 1 if stored else 1
        if start_draw > latest:
            return self._empty_summary(latest, latest)
        return self._collect_numbers(
            range(start_draw, latest + 1),
            start_draw=start_draw,
            end_draw=latest,
            resume=False,
        )

    def collect_missing(self) -> CollectionSummary:
        """Collect absent or invalid files between draw 1 and latest."""
        latest = self._collector.get_latest_draw_number()
        stored = self._raw_store.list_draw_numbers()
        missing = (number for number in range(1, latest + 1) if number not in stored)
        return self._collect_numbers(
            missing,
            start_draw=1,
            end_draw=latest,
            resume=False,
        )

    def _collect_numbers(
        self,
        draw_numbers: Iterable[int],
        start_draw: int,
        end_draw: int,
        resume: bool,
    ) -> CollectionSummary:
        requested_draws = tuple(draw_numbers)
        total_draws = len(requested_draws)
        successful_draws: List[int] = []
        skipped_draws: List[int] = []
        failures: List[CollectionFailure] = []
        made_request = False

        for processed, draw_number in enumerate(requested_draws, start=1):
            if resume and self._raw_store.has_valid_draw(draw_number):
                skipped_draws.append(draw_number)
                LOGGER.info("Skipping stored draw %s", draw_number)
                self._report_progress(processed, total_draws, draw_number, "skipped")
                continue

            if made_request and self._request_interval_seconds:
                self._sleep(self._request_interval_seconds)
            made_request = True

            try:
                self._collector.collect_draw(draw_number)
                successful_draws.append(draw_number)
                LOGGER.info("Collected draw %s", draw_number)
                self._report_progress(processed, total_draws, draw_number, "collected")
            except (CollectorError, RawDataConflictError, OSError) as exc:
                LOGGER.error("Failed to collect draw %s: %s", draw_number, exc)
                failures.append(
                    CollectionFailure(draw_number=draw_number, reason=str(exc))
                )
                self._report_progress(processed, total_draws, draw_number, "failed")

        return CollectionSummary(
            start_draw=start_draw,
            end_draw=end_draw,
            successful_draws=tuple(successful_draws),
            skipped_draws=tuple(skipped_draws),
            failures=tuple(failures),
        )

    def _report_progress(
        self, processed: int, total: int, draw_number: int, status: str
    ) -> None:
        if self._progress is not None:
            self._progress(processed, total, draw_number, status)

    @staticmethod
    def _empty_summary(start_draw: int, end_draw: int) -> CollectionSummary:
        return CollectionSummary(
            start_draw=start_draw,
            end_draw=end_draw,
            successful_draws=(),
            skipped_draws=(),
            failures=(),
        )

"""Persistent JSON history for collection command executions."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict, Optional

from lotto_analysis.models import CollectionSummary


class CollectionHistoryStore:
    """Store one immutable JSON report for each collection execution."""

    def __init__(self, directory: Path) -> None:
        self._directory = Path(directory)

    def save(
        self,
        command: str,
        started_at: datetime,
        completed_at: datetime,
        summary: Optional[CollectionSummary] = None,
        error: Optional[str] = None,
    ) -> Path:
        """Persist a completed, partially failed, or aborted collection run."""
        if summary is None and error is None:
            raise ValueError("summary or error is required")
        if started_at.tzinfo is None or completed_at.tzinfo is None:
            raise ValueError("collection history timestamps must include timezone")
        if completed_at < started_at:
            raise ValueError("completed_at cannot be earlier than started_at")

        payload = self._build_payload(
            command=command,
            started_at=started_at,
            completed_at=completed_at,
            summary=summary,
            error=error,
        )
        timestamp = completed_at.astimezone(timezone.utc).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )
        safe_command = re.sub(r"[^a-zA-Z0-9_-]+", "-", command).strip("-")
        target = self._unique_path(
            self._directory
            / "{0}_{1}.json".format(timestamp, safe_command or "collection")
        )
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        self._atomic_write(target, content)
        return target

    @staticmethod
    def _unique_path(target: Path) -> Path:
        if not target.exists():
            return target
        counter = 2
        while True:
            candidate = target.with_name(
                "{0}_{1}{2}".format(target.stem, counter, target.suffix)
            )
            if not candidate.exists():
                return candidate
            counter += 1

    @staticmethod
    def _build_payload(
        command: str,
        started_at: datetime,
        completed_at: datetime,
        summary: Optional[CollectionSummary],
        error: Optional[str],
    ) -> Dict[str, Any]:
        failures = []
        if summary is not None:
            failures = [
                {"draw_number": failure.draw_number, "reason": failure.reason}
                for failure in summary.failures
            ]

        if error is not None:
            status = "failed"
        elif failures:
            status = "partial_failure"
        else:
            status = "success"

        return {
            "schema_version": 1,
            "command": command,
            "status": status,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_seconds": (completed_at - started_at).total_seconds(),
            "range": (
                {
                    "start_draw": summary.start_draw,
                    "end_draw": summary.end_draw,
                }
                if summary is not None
                else None
            ),
            "counts": (
                {
                    "successful": summary.success_count,
                    "skipped": summary.skipped_count,
                    "failed": summary.failure_count,
                }
                if summary is not None
                else None
            ),
            "successful_draws": (
                list(summary.successful_draws) if summary is not None else []
            ),
            "skipped_draws": (
                list(summary.skipped_draws) if summary is not None else []
            ),
            "failures": failures,
            "error": error,
        }

    @staticmethod
    def _atomic_write(target: Path, content: str) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)

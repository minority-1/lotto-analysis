"""Orchestrate raw file validation and processed artifact creation."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Dict, List, Optional, Set

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.processing import ProcessingSummary, ValidationIssue
from lotto_analysis.processors import RawDrawValidationError, parse_raw_draw
from lotto_analysis.storage.processed_csv import (
    write_processed_csv,
    write_validation_report,
)


DRAW_FILE_PATTERN = re.compile(r"^draw_(\d+)\.json$")


class ProcessingService:
    """Validate every canonical raw draw and write deterministic output."""

    def __init__(self, raw_dir: Path, processed_dir: Path) -> None:
        self._raw_dir = Path(raw_dir)
        self._processed_dir = Path(processed_dir)

    def process(self) -> ProcessingSummary:
        """Process all raw files while isolating invalid records."""
        started_at = datetime.now(timezone.utc)
        paths = sorted(
            path
            for path in self._raw_dir.glob("draw_*.json")
            if DRAW_FILE_PATTERN.match(path.name)
        )
        draws_by_number: Dict[int, LottoDraw] = {}
        issues: List[ValidationIssue] = []
        duplicates: Set[int] = set()
        if not paths:
            issues.append(
                ValidationIssue(
                    source_file=str(self._raw_dir),
                    reason="no raw draw files found",
                )
            )

        for path in paths:
            match = DRAW_FILE_PATTERN.match(path.name)
            assert match is not None
            declared_number = int(match.group(1))
            payload: object = None
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    raise RawDrawValidationError("raw JSON must contain an object")
                draw = parse_raw_draw(payload)
                if draw.draw_number != declared_number:
                    raise RawDrawValidationError(
                        "file name and record draw number differ"
                    )
                if draw.draw_number in draws_by_number:
                    duplicates.add(draw.draw_number)
                    raise RawDrawValidationError("duplicate draw number")
                draws_by_number[draw.draw_number] = draw
            except (OSError, ValueError) as exc:
                issues.append(
                    ValidationIssue(
                        source_file=path.name,
                        reason=str(exc),
                        draw_number=_safe_draw_number(payload),
                    )
                )

        draws = tuple(draws_by_number[number] for number in sorted(draws_by_number))
        missing = _missing_draws(set(draws_by_number))
        csv_path = self._processed_dir / "lotto_draws.csv"
        report_path = self._processed_dir / "validation_report.json"
        write_processed_csv(csv_path, draws)
        completed_at = datetime.now(timezone.utc)
        write_validation_report(
            report_path,
            {
                "schema_version": 1,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_seconds": (completed_at - started_at).total_seconds(),
                "total_files": len(paths),
                "valid_count": len(draws),
                "error_count": len(issues),
                "duplicate_draws": sorted(duplicates),
                "missing_draws": list(missing),
                "csv_path": str(csv_path),
                "issues": [
                    {
                        "source_file": issue.source_file,
                        "draw_number": issue.draw_number,
                        "reason": issue.reason,
                    }
                    for issue in issues
                ],
            },
        )
        return ProcessingSummary(
            total_files=len(paths),
            draws=draws,
            issues=tuple(issues),
            duplicate_draws=tuple(sorted(duplicates)),
            missing_draws=missing,
            csv_path=csv_path,
            report_path=report_path,
        )


def _missing_draws(draw_numbers: Set[int]) -> tuple[int, ...]:
    if not draw_numbers:
        return ()
    return tuple(
        number for number in range(1, max(draw_numbers) + 1)
        if number not in draw_numbers
    )


def _safe_draw_number(payload: object) -> Optional[int]:
    if not isinstance(payload, dict):
        return None
    value = payload.get("ltEpsd")
    return value if type(value) is int else None

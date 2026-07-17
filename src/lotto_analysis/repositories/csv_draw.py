"""CSV-backed repository for normalized Lotto draws."""

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Mapping, Optional, Tuple

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.repositories.base import DrawRepository
from lotto_analysis.storage.processed_csv import CSV_COLUMNS


class CsvDrawRepository(DrawRepository):
    """Load validated draws from the processed CSV artifact."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def list_draws(self, recent: int = 0) -> Tuple[LottoDraw, ...]:
        """Return unique draws sorted by number and optionally limited."""
        if type(recent) is not int or recent < 0:
            raise ValueError("recent must be a non-negative integer")
        try:
            with self._path.open(encoding="utf-8", newline="") as source:
                reader = csv.DictReader(source)
                if reader.fieldnames != list(CSV_COLUMNS):
                    raise ValueError("processed CSV columns do not match the schema")
                draws = tuple(self._to_draw(row) for row in reader)
        except FileNotFoundError as exc:
            raise ValueError(
                "processed CSV does not exist; run 'lotto-analysis process' first"
            ) from exc

        ordered = tuple(sorted(draws, key=lambda draw: draw.draw_number))
        numbers = tuple(draw.draw_number for draw in ordered)
        if len(numbers) != len(set(numbers)):
            raise ValueError("processed CSV contains duplicate draw numbers")
        if recent:
            return ordered[-recent:]
        return ordered

    @staticmethod
    def _to_draw(row: Mapping[str, str]) -> LottoDraw:
        try:
            return LottoDraw(
                draw_number=_integer(row, "draw_number"),
                draw_date=date.fromisoformat(_text(row, "draw_date")),
                numbers=tuple(
                    _integer(row, "num{0}".format(index))
                    for index in range(1, 7)
                ),  # type: ignore[arg-type]
                bonus_number=_integer(row, "bonus_number"),
                first_prize_winners=_integer(row, "first_prize_winners"),
                first_prize_amount=_integer(row, "first_prize_amount"),
                total_sales_amount=_integer(row, "total_sales_amount"),
                collected_at=_optional_datetime(row.get("collected_at", "")),
            )
        except (TypeError, ValueError) as exc:
            draw_number = row.get("draw_number", "unknown")
            raise ValueError(
                "processed CSV draw {0} is invalid: {1}".format(draw_number, exc)
            ) from exc


def _integer(row: Mapping[str, str], field: str) -> int:
    value = row.get(field)
    if value is None or not value.strip().lstrip("+-").isdigit():
        raise ValueError("{0} must be an integer".format(field))
    return int(value)


def _text(row: Mapping[str, str], field: str) -> str:
    value = row.get(field)
    if value is None or not value:
        raise ValueError("{0} is required".format(field))
    return value


def _optional_datetime(value: str) -> Optional[datetime]:
    return datetime.fromisoformat(value) if value else None


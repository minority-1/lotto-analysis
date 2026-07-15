"""Writers for validated CSV data and JSON validation reports."""

import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from lotto_analysis.models.draw import LottoDraw


CSV_COLUMNS = (
    "draw_number", "draw_date", "num1", "num2", "num3", "num4", "num5",
    "num6", "bonus_number", "first_prize_winners", "first_prize_amount",
    "total_sales_amount", "collected_at",
)


def write_processed_csv(path: Path, draws: Iterable[LottoDraw]) -> Path:
    """Replace the processed CSV atomically with validated draws."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for draw in draws:
            writer.writerow(_draw_row(draw))
    temporary.replace(path)
    return path


def write_validation_report(path: Path, payload: Mapping[str, Any]) -> Path:
    """Replace the JSON validation report atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return path


def _draw_row(draw: LottoDraw) -> Dict[str, Any]:
    return {
        "draw_number": draw.draw_number,
        "draw_date": draw.draw_date.isoformat(),
        "num1": draw.numbers[0], "num2": draw.numbers[1],
        "num3": draw.numbers[2], "num4": draw.numbers[3],
        "num5": draw.numbers[4], "num6": draw.numbers[5],
        "bonus_number": draw.bonus_number,
        "first_prize_winners": draw.first_prize_winners,
        "first_prize_amount": draw.first_prize_amount,
        "total_sales_amount": draw.total_sales_amount,
        "collected_at": _format_datetime(draw.collected_at),
    }


def _format_datetime(value: Any) -> str:
    return value.isoformat() if isinstance(value, datetime) else ""


"""Convert one official raw record into the normalized domain model."""

from datetime import datetime
import re
from typing import Any, Mapping

from lotto_analysis.models.draw import LottoDraw


class RawDrawValidationError(ValueError):
    """Report a raw record that cannot be normalized safely."""


def parse_raw_draw(record: Mapping[str, Any]) -> LottoDraw:
    """Validate and normalize one raw official draw record."""
    try:
        numbers = tuple(
            _required_int(record, "tm{0}WnNo".format(index))
            for index in range(1, 7)
        )
        draw_date = datetime.strptime(
            _required_text(record, "ltRflYmd"), "%Y%m%d"
        ).date()
        return LottoDraw(
            draw_number=_required_int(record, "ltEpsd"),
            draw_date=draw_date,
            numbers=numbers,  # type: ignore[arg-type]
            bonus_number=_required_int(record, "bnsWnNo"),
            first_prize_winners=_required_int(record, "rnk1WnNope"),
            first_prize_amount=_required_int(record, "rnk1WnAmt"),
            total_sales_amount=_required_int(record, "wholEpsdSumNtslAmt"),
            collected_at=None,
        )
    except (TypeError, ValueError) as exc:
        raise RawDrawValidationError(str(exc)) from exc


def _required_int(record: Mapping[str, Any], field: str) -> int:
    value = record.get(field)
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?[0-9]+", value.strip()):
        return int(value.strip())
    raise RawDrawValidationError("field {0} must be an integer".format(field))


def _required_text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise RawDrawValidationError("field {0} must be non-empty text".format(field))
    return value


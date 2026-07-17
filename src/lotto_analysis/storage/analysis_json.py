"""JSON export for serializable analysis result models."""

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
import json
from pathlib import Path
from typing import Any


def write_analysis_json(path: Path, result: object) -> Path:
    """Atomically write one versioned analysis result as JSON."""
    if not is_dataclass(result):
        raise ValueError("analysis result must be a dataclass")
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(),
        "result": asdict(result),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError("value is not JSON serializable")


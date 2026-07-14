"""Storage for one raw official record per Lotto draw."""

from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping, Optional, Set


DRAW_FILE_PATTERN = re.compile(r"^draw_(\d+)\.json$")


class RawDataConflictError(RuntimeError):
    """Report a changed official record without replacing stored raw data."""

    def __init__(
        self,
        draw_number: int,
        changed_fields: Set[str],
        conflict_path: Path,
    ) -> None:
        self.draw_number = draw_number
        self.changed_fields = frozenset(changed_fields)
        self.conflict_path = conflict_path
        fields = ", ".join(sorted(changed_fields)) or "unknown"
        super().__init__(
            "Raw data conflict for draw {0}; changed fields: {1}; saved to {2}".format(
                draw_number, fields, conflict_path
            )
        )


class RawJsonStore:
    """Store and inspect immutable official draw records as JSON files."""

    def __init__(self, directory: Path) -> None:
        self._directory = Path(directory)

    def path_for(self, draw_number: int) -> Path:
        """Return the canonical path for one draw number."""
        if draw_number <= 0:
            raise ValueError("draw_number must be positive")
        return self._directory / "draw_{0:04d}.json".format(draw_number)

    def has_valid_draw(self, draw_number: int) -> bool:
        """Return whether a readable raw record exists for the draw."""
        try:
            record = self.load(draw_number)
        except (OSError, ValueError):
            return False
        return record is not None and _record_draw_number(record) == draw_number

    def list_draw_numbers(self) -> Set[int]:
        """Return draw numbers represented by valid canonical files."""
        if not self._directory.exists():
            return set()

        draw_numbers: Set[int] = set()
        for path in self._directory.glob("draw_*.json"):
            match = DRAW_FILE_PATTERN.match(path.name)
            if match is None:
                continue
            draw_number = int(match.group(1))
            if self.has_valid_draw(draw_number):
                draw_numbers.add(draw_number)
        return draw_numbers

    def load(self, draw_number: int) -> Optional[Mapping[str, Any]]:
        """Load one record, including the legacy surrounding-list format."""
        target = self.path_for(draw_number)
        if not target.exists():
            return None
        payload = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("raw JSON must contain an object")

        if "ltEpsd" in payload:
            return payload

        data = payload.get("data")
        items = data.get("list") if isinstance(data, Mapping) else None
        if isinstance(items, list):
            for item in items:
                if isinstance(item, Mapping) and _record_draw_number(item) == draw_number:
                    return item
        raise ValueError("raw JSON does not contain the requested draw")

    def save(self, draw_number: int, record: Mapping[str, Any]) -> Path:
        """Save one source record or preserve a changed record as a conflict."""
        if _record_draw_number(record) != draw_number:
            raise ValueError("raw record draw number does not match the requested draw")

        target = self.path_for(draw_number)
        content = _serialize(record)
        if target.exists():
            try:
                stored_record = self.load(draw_number)
            except (OSError, ValueError):
                stored_record = None

            if stored_record == record:
                if target.read_text(encoding="utf-8") != content:
                    self._atomic_write(target, content)
                return target

            changed_fields = _changed_fields(stored_record, record)
            conflict_path = self._write_conflict(draw_number, content)
            raise RawDataConflictError(
                draw_number=draw_number,
                changed_fields=changed_fields,
                conflict_path=conflict_path,
            )

        self._atomic_write(target, content)
        return target

    def _write_conflict(self, draw_number: int, content: str) -> Path:
        digest = sha256(content.encode("utf-8")).hexdigest()[:12]
        path = (
            self._directory
            / "conflicts"
            / "draw_{0:04d}_{1}.json".format(draw_number, digest)
        )
        if not path.exists():
            self._atomic_write(path, content)
        return path

    @staticmethod
    def _atomic_write(target: Path, content: str) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)


def _serialize(record: Mapping[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _record_draw_number(record: Mapping[str, Any]) -> Optional[int]:
    value = record.get("ltEpsd")
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _changed_fields(
    stored: Optional[Mapping[str, Any]], incoming: Mapping[str, Any]
) -> Set[str]:
    if stored is None:
        return {"<stored file unreadable>"}
    keys = set(stored) | set(incoming)
    return {key for key in keys if stored.get(key) != incoming.get(key)}

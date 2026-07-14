import json
from pathlib import Path

import pytest

from lotto_analysis.storage import RawDataConflictError, RawJsonStore


def test_raw_json_store_writes_utf8_json(tmp_path: Path) -> None:
    store = RawJsonStore(tmp_path / "raw")

    path = store.save(1, {"ltEpsd": 1, "message": "공식 응답"})

    assert path == tmp_path / "raw" / "draw_0001.json"
    assert json.loads(path.read_text(encoding="utf-8"))["message"] == "공식 응답"


def test_raw_json_store_accepts_identical_existing_response(tmp_path: Path) -> None:
    store = RawJsonStore(tmp_path)
    first_path = store.save(1, {"ltEpsd": 1, "value": "same"})

    second_path = store.save(1, {"ltEpsd": 1, "value": "same"})

    assert second_path == first_path


def test_raw_json_store_rejects_changed_existing_response(tmp_path: Path) -> None:
    store = RawJsonStore(tmp_path)
    store.save(1, {"ltEpsd": 1, "version": 1})

    with pytest.raises(RawDataConflictError) as error:
        store.save(1, {"ltEpsd": 1, "version": 2})

    assert error.value.changed_fields == {"version"}
    assert error.value.conflict_path.is_file()
    assert json.loads(error.value.conflict_path.read_text())["version"] == 2
    assert json.loads(store.path_for(1).read_text())["version"] == 1


def test_raw_json_store_lists_only_valid_canonical_draws(tmp_path: Path) -> None:
    store = RawJsonStore(tmp_path)
    store.save(1, {"ltEpsd": 1})
    (tmp_path / "draw_0002.json").write_text("not-json", encoding="utf-8")
    (tmp_path / "unrelated.json").write_text("{}", encoding="utf-8")

    assert store.list_draw_numbers() == {1}


def test_raw_json_store_normalizes_legacy_surrounding_list(tmp_path: Path) -> None:
    path = tmp_path / "draw_0001.json"
    path.write_text(
        json.dumps({"data": {"list": [{"ltEpsd": 2}, {"ltEpsd": 1}]}}),
        encoding="utf-8",
    )
    store = RawJsonStore(tmp_path)

    store.save(1, {"ltEpsd": 1})

    assert json.loads(path.read_text(encoding="utf-8")) == {"ltEpsd": 1}

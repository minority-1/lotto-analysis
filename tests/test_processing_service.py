import csv
import json
from pathlib import Path

from lotto_analysis.services import ProcessingService


def raw_record(draw_number: int, numbers: tuple = (1, 2, 3, 4, 5, 6)) -> dict:
    return {
        "ltEpsd": draw_number,
        "ltRflYmd": "20260711",
        "tm1WnNo": numbers[0], "tm2WnNo": numbers[1],
        "tm3WnNo": numbers[2], "tm4WnNo": numbers[3],
        "tm5WnNo": numbers[4], "tm6WnNo": numbers[5],
        "bnsWnNo": 7,
        "rnk1WnNope": 1,
        "rnk1WnAmt": 100,
        "wholEpsdSumNtslAmt": 1000,
    }


def write_raw(directory: Path, file_number: int, record: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "draw_{0:04d}.json".format(file_number)).write_text(
        json.dumps(record), encoding="utf-8"
    )


def test_process_writes_sorted_csv_and_success_report(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    write_raw(raw_dir, 2, raw_record(2))
    write_raw(raw_dir, 1, raw_record(1))

    summary = ProcessingService(raw_dir, processed_dir).process()

    assert summary.valid_count == 2
    assert summary.error_count == 0
    assert summary.missing_draws == ()
    with summary.csv_path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    assert [row["draw_number"] for row in rows] == ["1", "2"]
    assert rows[0]["collected_at"] == ""
    report = json.loads(summary.report_path.read_text(encoding="utf-8"))
    assert report["valid_count"] == 2
    assert report["issues"] == []
    assert report["duration_seconds"] >= 0


def test_process_isolates_invalid_file_and_reports_missing_draw(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    write_raw(raw_dir, 1, raw_record(1))
    write_raw(raw_dir, 2, {"ltEpsd": 2})
    write_raw(raw_dir, 3, raw_record(3))

    summary = ProcessingService(raw_dir, tmp_path / "processed").process()

    assert summary.valid_count == 2
    assert summary.error_count == 1
    assert summary.missing_draws == (2,)
    assert summary.issues[0].source_file == "draw_0002.json"


def test_process_reports_file_and_record_number_mismatch(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    write_raw(raw_dir, 1, raw_record(2))

    summary = ProcessingService(raw_dir, tmp_path / "processed").process()

    assert summary.valid_count == 0
    assert summary.error_count == 1
    assert "differ" in summary.issues[0].reason


def test_process_reports_empty_raw_directory(tmp_path: Path) -> None:
    summary = ProcessingService(
        tmp_path / "missing-raw", tmp_path / "processed"
    ).process()

    assert summary.total_files == 0
    assert summary.valid_count == 0
    assert summary.error_count == 1
    assert summary.issues[0].reason == "no raw draw files found"

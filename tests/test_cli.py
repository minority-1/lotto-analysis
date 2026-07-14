from lotto_analysis.cli import _print_progress


def test_print_progress_reports_periodic_and_final_updates(capsys: object) -> None:
    _print_progress(1, 1000, 1, "collected")
    _print_progress(10, 1000, 10, "collected")
    _print_progress(11, 1000, 11, "collected")
    _print_progress(1000, 1000, 1000, "skipped")

    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "10/1000" in output
    assert "1000/1000" in output
    assert "1/1000" not in output
    assert "11/1000" not in output


def test_print_progress_always_reports_failure(capsys: object) -> None:
    _print_progress(7, 1000, 7, "failed")

    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "draw 7: failed" in output

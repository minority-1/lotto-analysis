import json
from pathlib import Path

from lotto_analysis import cli
from lotto_analysis.cli import _print_progress
from lotto_analysis.config import Settings


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


def test_main_records_logging_initialization_failure(
    tmp_path: Path, monkeypatch: object, capsys: object
) -> None:
    settings = Settings.from_env(project_root=tmp_path, environ={})
    monkeypatch.setattr(cli.Settings, "from_env", lambda: settings)  # type: ignore[attr-defined]

    def fail_logging(*args: object, **kwargs: object) -> None:
        raise OSError("log directory unavailable")

    monkeypatch.setattr(cli, "configure_logging", fail_logging)  # type: ignore[attr-defined]

    exit_code = cli.main(["collect-one", "1"])

    assert exit_code == 1
    assert "Command failed: log directory unavailable" in capsys.readouterr().out  # type: ignore[attr-defined]
    history_paths = list(settings.collection_history_dir.glob("*.json"))
    assert len(history_paths) == 1
    history = json.loads(history_paths[0].read_text(encoding="utf-8"))
    assert history["status"] == "failed"
    assert history["error"] == "log directory unavailable"


def test_main_reports_settings_failure_without_traceback(
    monkeypatch: object, capsys: object
) -> None:
    def fail_settings() -> Settings:
        raise ValueError("invalid setting")

    monkeypatch.setattr(cli.Settings, "from_env", fail_settings)  # type: ignore[attr-defined]

    assert cli.main(["collect-one", "1"]) == 1
    assert "Command failed: invalid setting" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_parser_accepts_process_command() -> None:
    assert cli.build_parser().parse_args(["process"]).command == "process"


def test_parser_accepts_recent_analysis_command() -> None:
    args = cli.build_parser().parse_args(["analyze", "--recent", "50"])

    assert args.command == "analyze"
    assert args.recent == 50


def test_parser_accepts_comparison_and_gap_commands() -> None:
    comparison = cli.build_parser().parse_args(
        ["compare", "50", "--against-all", "--export"]
    )
    gaps = cli.build_parser().parse_args(["gaps", "--recent", "100"])

    assert comparison.recent == 50
    assert comparison.against_all is True
    assert comparison.export is True
    assert gaps.recent == 100


def test_parser_accepts_database_commands() -> None:
    parser = cli.build_parser()

    assert parser.parse_args(["db-upgrade"]).command == "db-upgrade"
    assert parser.parse_args(["db-import"]).command == "db-import"
    assert parser.parse_args(["db-verify"]).command == "db-verify"


def test_parser_accepts_relationship_command() -> None:
    args = cli.build_parser().parse_args(
        ["relationships", "--recent", "100", "--number", "7", "--top", "10", "--export"]
    )

    assert args.recent == 100
    assert args.number == 7
    assert args.top == 10
    assert args.export is True


def test_parser_accepts_matrix_command() -> None:
    args = cli.build_parser().parse_args(["matrix", "--recent", "50", "--export"])

    assert args.command == "matrix"
    assert args.recent == 50
    assert args.export is True


def test_parser_accepts_matrix_comparison_command() -> None:
    args = cli.build_parser().parse_args(["matrix-compare", "50", "--export"])

    assert args.command == "matrix-compare"
    assert args.recent == 50
    assert args.export is True


def test_parser_accepts_pattern_command() -> None:
    args = cli.build_parser().parse_args(["patterns", "--recent", "100", "--export"])

    assert args.command == "patterns"
    assert args.recent == 100
    assert args.export is True


def test_parser_accepts_similarity_command() -> None:
    args = cli.build_parser().parse_args(
        ["similarity", "--recent", "100", "--top", "10", "--export"]
    )

    assert args.command == "similarity"
    assert args.recent == 100
    assert args.top == 10
    assert args.export is True


def test_parser_accepts_generation_command() -> None:
    args = cli.build_parser().parse_args(
        [
            "generate",
            "--count",
            "3",
            "--strategy",
            "frequency",
            "--weight-recent",
            "50",
            "--seed",
            "42",
            "--include",
            "1,2",
            "--exclude",
            "44,45",
            "--odd-min",
            "2",
            "--odd-max",
            "4",
        ]
    )

    assert args.command == "generate"
    assert args.count == 3
    assert args.strategy == "frequency"
    assert args.weight_recent == 50
    assert args.seed == 42
    assert args.include == (1, 2)
    assert args.exclude == (44, 45)
    assert args.odd_min == 2
    assert args.odd_max == 4


def test_parser_accepts_backtest_command() -> None:
    args = cli.build_parser().parse_args(
        [
            "backtest",
            "--strategy",
            "frequency",
            "--targets",
            "10",
            "--combinations",
            "5",
            "--weight-recent",
            "50",
            "--seed",
            "7",
            "--export",
        ]
    )

    assert args.command == "backtest"
    assert args.strategy == "frequency"
    assert args.targets == 10
    assert args.combinations == 5
    assert args.weight_recent == 50
    assert args.seed == 7
    assert args.export is True

"""Command-line entry point for the current collection features."""

import argparse
from datetime import datetime, timezone
from statistics import mean
from typing import Optional, Sequence

from lotto_analysis.collectors import CollectorError, DhlotteryDrawCollector
from lotto_analysis.config import Settings
from lotto_analysis.logging_config import configure_logging
from lotto_analysis.models import BasicAnalysisResult, CollectionSummary
from lotto_analysis.repositories import CsvDrawRepository
from lotto_analysis.services import AnalysisService, CollectionService, ProcessingService
from lotto_analysis.storage import CollectionHistoryStore, RawJsonStore


def build_parser() -> argparse.ArgumentParser:
    """Build the project command-line parser."""
    parser = argparse.ArgumentParser(prog="lotto-analysis")
    subparsers = parser.add_subparsers(dest="command", required=True)

    one_parser = subparsers.add_parser("collect-one", help="collect one draw")
    one_parser.add_argument("draw_number", type=int)

    range_parser = subparsers.add_parser(
        "collect-range", help="collect an inclusive draw range"
    )
    range_parser.add_argument("start_draw", type=int)
    range_parser.add_argument("end_draw", type=int)
    range_parser.add_argument(
        "--refresh", action="store_true", help="request already stored draws again"
    )

    all_parser = subparsers.add_parser(
        "collect-all", help="collect draw 1 through latest"
    )
    all_parser.add_argument(
        "--refresh", action="store_true", help="request already stored draws again"
    )
    subparsers.add_parser(
        "collect-incremental", help="collect draws after the greatest stored draw"
    )
    subparsers.add_parser(
        "collect-missing", help="collect missing draws through latest"
    )
    subparsers.add_parser(
        "process", help="validate raw draws and create processed CSV"
    )
    analyze_parser = subparsers.add_parser(
        "analyze", help="calculate basic descriptive statistics"
    )
    analyze_parser.add_argument(
        "--recent",
        type=_positive_int,
        default=0,
        help="analyze only the latest N draws",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Execute one application command and return a process exit code."""
    args = build_parser().parse_args(argv)
    command = _describe_command(args)
    started_at = datetime.now(timezone.utc)
    history_store: Optional[CollectionHistoryStore] = None
    try:
        settings = Settings.from_env()
        history_store = CollectionHistoryStore(settings.collection_history_dir)
        configure_logging(
            settings.log_level,
            log_file=settings.log_file,
            max_bytes=settings.log_max_bytes,
            backup_count=settings.log_backup_count,
        )
        if args.command == "process":
            return _run_processing(settings)
        if args.command == "analyze":
            return _run_analysis(settings, recent=args.recent)
        raw_store = RawJsonStore(settings.raw_data_dir)
        collector = DhlotteryDrawCollector(
            settings=settings,
            raw_store=raw_store,
        )
        service = CollectionService(
            collector,
            raw_store=raw_store,
            request_interval_seconds=settings.request_interval_seconds,
            progress=_print_progress,
        )
        summary = _execute_command(args, service)
    except (CollectorError, OSError, ValueError) as exc:
        print("Command failed: {0}".format(exc))
        _save_failure_history(history_store, command, started_at, exc)
        return 1

    assert history_store is not None
    try:
        history_path = history_store.save(
            command=command,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            summary=summary,
        )
    except (OSError, ValueError) as exc:
        print("Collection completed, but history could not be saved: {0}".format(exc))
        return 1

    print(
        "Collected {0} draws; {1} skipped; {2} failed ({3}-{4})".format(
            summary.success_count,
            summary.skipped_count,
            summary.failure_count,
            summary.start_draw,
            summary.end_draw,
        )
    )
    for failure in summary.failures:
        print("- draw {0}: {1}".format(failure.draw_number, failure.reason))
    print("History: {0}".format(history_path))
    return 1 if summary.failures else 0


def _run_processing(settings: Settings) -> int:
    """Execute raw validation and report the generated artifacts."""
    summary = ProcessingService(
        raw_dir=settings.raw_data_dir,
        processed_dir=settings.processed_data_dir,
    ).process()
    print(
        "Processed {0} files; {1} valid; {2} errors; {3} missing".format(
            summary.total_files,
            summary.valid_count,
            summary.error_count,
            len(summary.missing_draws),
        )
    )
    print("CSV: {0}".format(summary.csv_path))
    print("Report: {0}".format(summary.report_path))
    return 1 if summary.issues or summary.missing_draws else 0


def _run_analysis(settings: Settings, recent: int) -> int:
    """Calculate and print first-stage descriptive statistics."""
    result = AnalysisService(
        CsvDrawRepository(settings.processed_data_dir / "lotto_draws.csv")
    ).analyze(recent=recent)
    _print_analysis(result)
    return 0


def _print_analysis(result: BasicAnalysisResult) -> None:
    """Print a compact, prediction-neutral analysis report."""
    draw_stats = result.draw_statistics
    print(
        "Analyzed {0} draws ({1}-{2})".format(
            result.total_draws, result.start_draw, result.end_draw
        )
    )
    print(
        "Draw summary: average sum {0:.2f}; consecutive {1}/{2}; "
        "average odd {3:.2f}; average low(1-22) {4:.2f}".format(
            mean(item.number_sum for item in draw_stats),
            sum(item.has_consecutive_numbers for item in draw_stats),
            result.total_draws,
            mean(item.odd_count for item in draw_stats),
            mean(item.low_count for item in draw_stats),
        )
    )
    section_averages = tuple(
        mean(item.section_counts[index] for item in draw_stats)
        for index in range(5)
    )
    overlaps = tuple(
        item.previous_draw_overlap
        for item in draw_stats
        if item.previous_draw_overlap is not None
    )
    print(
        "Sections average (1-10/11-20/21-30/31-40/41-45): "
        "{0:.2f}/{1:.2f}/{2:.2f}/{3:.2f}/{4:.2f}; previous overlap {5}".format(
            section_averages[0],
            section_averages[1],
            section_averages[2],
            section_averages[3],
            section_averages[4],
            "{0:.2f}".format(mean(overlaps)) if overlaps else "n/a",
        )
    )
    print("Number  Main  Rate     Bonus  Last  Absent")
    for item in result.number_statistics:
        print(
            "{0:>6}  {1:>4}  {2:>7.2%}  {3:>5}  {4:>4}  {5:>6}".format(
                item.number,
                item.main_count,
                item.main_rate,
                item.bonus_count,
                item.last_draw_number if item.last_draw_number is not None else "-",
                item.absence_draws,
            )
        )


def _positive_int(value: str) -> int:
    """Parse one strictly positive CLI integer."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _save_failure_history(
    history_store: Optional[CollectionHistoryStore],
    command: str,
    started_at: datetime,
    error: Exception,
) -> None:
    """Save a failure when possible without hiding the original error."""
    if history_store is None:
        print("History unavailable: settings could not be loaded")
        return
    try:
        history_path = history_store.save(
            command=command,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            error=str(error),
        )
    except (OSError, ValueError) as history_error:
        print("History unavailable: {0}".format(history_error))
        return
    print("History: {0}".format(history_path))


def _execute_command(
    args: argparse.Namespace, service: CollectionService
) -> CollectionSummary:
    """Dispatch parsed CLI arguments to the collection service."""
    if args.command == "collect-one":
        return service.collect_range(args.draw_number, args.draw_number, resume=False)
    if args.command == "collect-range":
        return service.collect_range(
            args.start_draw, args.end_draw, resume=not args.refresh
        )
    if args.command == "collect-all":
        return service.collect_all(resume=not args.refresh)
    if args.command == "collect-incremental":
        return service.collect_incremental()
    return service.collect_missing()


def _describe_command(args: argparse.Namespace) -> str:
    """Return a stable human-readable command description for history."""
    if args.command == "collect-one":
        return "collect-one {0}".format(args.draw_number)
    if args.command == "collect-range":
        refresh = " --refresh" if args.refresh else ""
        return "collect-range {0} {1}{2}".format(
            args.start_draw, args.end_draw, refresh
        )
    if args.command == "collect-all" and args.refresh:
        return "collect-all --refresh"
    return args.command


def _print_progress(
    processed: int, total: int, draw_number: int, status: str
) -> None:
    """Print bounded progress updates without flooding long collection runs."""
    if total <= 0:
        return
    interval = max(total // 100, 1)
    if processed != total and processed % interval != 0 and status != "failed":
        return
    percentage = processed / total * 100
    print(
        "Progress: {0}/{1} ({2:5.1f}%) draw {3}: {4}".format(
            processed, total, percentage, draw_number, status
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())

"""Command-line entry point for the current collection features."""

import argparse
from datetime import datetime, timezone
from typing import Optional, Sequence

from lotto_analysis.collectors import CollectorError, DhlotteryDrawCollector
from lotto_analysis.config import Settings
from lotto_analysis.logging_config import configure_logging
from lotto_analysis.models import CollectionSummary
from lotto_analysis.services import CollectionService
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
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Execute one collection command and return a process exit code."""
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()
    configure_logging(
        settings.log_level,
        log_file=settings.log_file,
        max_bytes=settings.log_max_bytes,
        backup_count=settings.log_backup_count,
    )
    raw_store = RawJsonStore(settings.raw_data_dir)
    history_store = CollectionHistoryStore(settings.collection_history_dir)
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
    command = _describe_command(args)
    started_at = datetime.now(timezone.utc)
    try:
        summary = _execute_command(args, service)
    except (CollectorError, OSError) as exc:
        history_path = history_store.save(
            command=command,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            error=str(exc),
        )
        print("Collection failed: {0}".format(exc))
        print("History: {0}".format(history_path))
        return 1

    history_path = history_store.save(
        command=command,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc),
        summary=summary,
    )

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

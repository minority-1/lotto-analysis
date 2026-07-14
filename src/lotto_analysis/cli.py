"""Command-line entry point for the current collection features."""

import argparse
from typing import Optional, Sequence

from lotto_analysis.collectors import DhlotteryDrawCollector
from lotto_analysis.config import Settings
from lotto_analysis.logging_config import configure_logging
from lotto_analysis.services import CollectionService
from lotto_analysis.storage import RawJsonStore


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
    configure_logging(settings.log_level)
    raw_store = RawJsonStore(settings.raw_data_dir)
    collector = DhlotteryDrawCollector(
        settings=settings,
        raw_store=raw_store,
    )

    if args.command == "collect-one":
        print(collector.collect_draw(args.draw_number))
        return 0

    service = CollectionService(
        collector,
        raw_store=raw_store,
        request_interval_seconds=settings.request_interval_seconds,
    )
    if args.command == "collect-range":
        summary = service.collect_range(
            args.start_draw, args.end_draw, resume=not args.refresh
        )
    elif args.command == "collect-all":
        summary = service.collect_all(resume=not args.refresh)
    elif args.command == "collect-incremental":
        summary = service.collect_incremental()
    else:
        summary = service.collect_missing()

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
    return 1 if summary.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

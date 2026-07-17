"""Command-line entry point for the current collection features."""

import argparse
from datetime import datetime, timezone
from statistics import mean
from typing import Optional, Sequence

from sqlalchemy.exc import SQLAlchemyError

from lotto_analysis.collectors import CollectorError, DhlotteryDrawCollector
from lotto_analysis.config import Settings
from lotto_analysis.database import create_database_engine
from lotto_analysis.database.migrations import upgrade_database
from lotto_analysis.logging_config import configure_logging
from lotto_analysis.models import (
    BasicAnalysisResult,
    CollectionSummary,
    GapAnalysisResult,
    MatrixAnalysisResult,
    MatrixComparisonResult,
    PatternAnalysisResult,
    PeriodComparisonResult,
    RelationshipAnalysisResult,
)
from lotto_analysis.repositories import CsvDrawRepository, PostgresDrawRepository
from lotto_analysis.services import (
    AnalysisService,
    CollectionService,
    DatabaseService,
    ProcessingService,
)
from lotto_analysis.storage import CollectionHistoryStore, RawJsonStore
from lotto_analysis.storage.analysis_json import write_analysis_json


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
    analyze_parser.add_argument(
        "--export", action="store_true", help="write the complete result as JSON"
    )
    compare_parser = subparsers.add_parser(
        "compare", help="compare recent draws with another period"
    )
    compare_parser.add_argument("recent", type=_positive_int)
    compare_parser.add_argument(
        "--against-all", action="store_true", help="compare all history with recent N"
    )
    compare_parser.add_argument("--export", action="store_true")
    gaps_parser = subparsers.add_parser(
        "gaps", help="calculate historical number appearance gaps"
    )
    gaps_parser.add_argument("--recent", type=_positive_int, default=0)
    gaps_parser.add_argument("--export", action="store_true")
    relationships_parser = subparsers.add_parser(
        "relationships", help="analyze pair, triple, and companion frequencies"
    )
    relationships_parser.add_argument("--recent", type=_positive_int, default=0)
    relationships_parser.add_argument("--number", type=_lotto_number)
    relationships_parser.add_argument("--top", type=_positive_int, default=20)
    relationships_parser.add_argument("--export", action="store_true")
    matrix_parser = subparsers.add_parser(
        "matrix", help="analyze a 7 by 7 number-frequency matrix"
    )
    matrix_parser.add_argument("--recent", type=_positive_int, default=0)
    matrix_parser.add_argument("--export", action="store_true")
    matrix_compare_parser = subparsers.add_parser(
        "matrix-compare", help="compare previous and recent 7 by 7 matrices"
    )
    matrix_compare_parser.add_argument("recent", type=_positive_int)
    matrix_compare_parser.add_argument("--export", action="store_true")
    patterns_parser = subparsers.add_parser(
        "patterns", help="analyze mathematical combination patterns"
    )
    patterns_parser.add_argument("--recent", type=_positive_int, default=0)
    patterns_parser.add_argument("--export", action="store_true")
    subparsers.add_parser("db-upgrade", help="upgrade PostgreSQL schema")
    subparsers.add_parser("db-import", help="upsert processed CSV into PostgreSQL")
    subparsers.add_parser(
        "db-verify", help="compare CSV and PostgreSQL data and analysis"
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
            return _run_analysis(settings, recent=args.recent, export=args.export)
        if args.command == "compare":
            return _run_comparison(
                settings, args.recent, args.against_all, args.export
            )
        if args.command == "gaps":
            return _run_gaps(settings, args.recent, args.export)
        if args.command == "relationships":
            return _run_relationships(
                settings, args.recent, args.number, args.top, args.export
            )
        if args.command == "matrix":
            return _run_matrix(settings, args.recent, args.export)
        if args.command == "matrix-compare":
            return _run_matrix_comparison(settings, args.recent, args.export)
        if args.command == "patterns":
            return _run_patterns(settings, args.recent, args.export)
        if args.command == "db-upgrade":
            upgrade_database(settings.project_root)
            print("Database schema upgraded to head")
            return 0
        if args.command == "db-import":
            return _run_database_import(settings)
        if args.command == "db-verify":
            return _run_database_verification(settings)
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
    except (CollectorError, OSError, SQLAlchemyError, ValueError) as exc:
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


def _run_analysis(settings: Settings, recent: int, export: bool = False) -> int:
    """Calculate and print first-stage descriptive statistics."""
    result = AnalysisService(
        CsvDrawRepository(settings.processed_data_dir / "lotto_draws.csv")
    ).analyze(recent=recent)
    _print_analysis(result)
    if export:
        suffix = "recent_{0}".format(recent) if recent else "all"
        path = write_analysis_json(
            settings.analysis_data_dir / "basic_analysis_{0}.json".format(suffix),
            result,
        )
        print("Export: {0}".format(path))
    return 0


def _run_comparison(
    settings: Settings, recent: int, against_all: bool, export: bool
) -> int:
    """Compare two periods and optionally export the complete result."""
    result = AnalysisService(
        CsvDrawRepository(settings.processed_data_dir / "lotto_draws.csv")
    ).compare(recent=recent, against_all=against_all)
    _print_comparison(result)
    if export:
        baseline = "all" if against_all else "previous"
        path = write_analysis_json(
            settings.analysis_data_dir
            / "comparison_{0}_recent_{1}.json".format(baseline, recent),
            result,
        )
        print("Export: {0}".format(path))
    return 0


def _run_gaps(settings: Settings, recent: int, export: bool) -> int:
    """Calculate number gaps and optionally export the complete result."""
    result = AnalysisService(
        CsvDrawRepository(settings.processed_data_dir / "lotto_draws.csv")
    ).gaps(recent=recent)
    _print_gaps(result)
    if export:
        suffix = "recent_{0}".format(recent) if recent else "all"
        path = write_analysis_json(
            settings.analysis_data_dir / "gap_analysis_{0}.json".format(suffix),
            result,
        )
        print("Export: {0}".format(path))
    return 0


def _run_relationships(
    settings: Settings,
    recent: int,
    anchor_number: Optional[int],
    top: int,
    export: bool,
) -> int:
    """Analyze PostgreSQL relationship data and optionally export it."""
    engine = create_database_engine(settings)
    try:
        result = AnalysisService(PostgresDrawRepository(engine)).relationships(
            recent=recent, anchor_number=anchor_number
        )
    finally:
        engine.dispose()
    _print_relationships(result, top)
    if export:
        suffix = "recent_{0}".format(recent) if recent else "all"
        if anchor_number is not None:
            suffix += "_number_{0}".format(anchor_number)
        path = write_analysis_json(
            settings.analysis_data_dir
            / "relationship_analysis_{0}.json".format(suffix),
            result,
        )
        print("Export: {0}".format(path))
    return 0


def _run_matrix(settings: Settings, recent: int, export: bool) -> int:
    """Analyze the PostgreSQL draw data as a 7 by 7 matrix."""
    engine = create_database_engine(settings)
    try:
        result = AnalysisService(PostgresDrawRepository(engine)).matrix(recent=recent)
    finally:
        engine.dispose()
    _print_matrix(result)
    if export:
        suffix = "recent_{0}".format(recent) if recent else "all"
        path = write_analysis_json(
            settings.analysis_data_dir / "matrix_analysis_{0}.json".format(suffix),
            result,
        )
        print("Export: {0}".format(path))
    return 0


def _run_matrix_comparison(settings: Settings, recent: int, export: bool) -> int:
    """Compare previous and recent matrix periods from PostgreSQL."""
    engine = create_database_engine(settings)
    try:
        result = AnalysisService(PostgresDrawRepository(engine)).compare_matrices(
            recent
        )
    finally:
        engine.dispose()
    _print_matrix_comparison(result)
    if export:
        path = write_analysis_json(
            settings.analysis_data_dir
            / "matrix_comparison_previous_recent_{0}.json".format(recent),
            result,
        )
        print("Export: {0}".format(path))
    return 0


def _run_patterns(settings: Settings, recent: int, export: bool) -> int:
    """Analyze mathematical patterns from PostgreSQL draw data."""
    engine = create_database_engine(settings)
    try:
        result = AnalysisService(PostgresDrawRepository(engine)).patterns(recent=recent)
    finally:
        engine.dispose()
    _print_patterns(result)
    if export:
        suffix = "recent_{0}".format(recent) if recent else "all"
        path = write_analysis_json(
            settings.analysis_data_dir / "pattern_analysis_{0}.json".format(suffix),
            result,
        )
        print("Export: {0}".format(path))
    return 0


def _database_service(settings: Settings) -> DatabaseService:
    """Build the CSV/PostgreSQL synchronization service."""
    engine = create_database_engine(settings)
    return DatabaseService(
        CsvDrawRepository(settings.processed_data_dir / "lotto_draws.csv"),
        PostgresDrawRepository(engine),
    )


def _run_database_import(settings: Settings) -> int:
    """Synchronize the processed CSV with PostgreSQL."""
    result = _database_service(settings).import_draws()
    print(
        "Database import: {0} source; {1} synchronized; {2} stored".format(
            result.source_count,
            result.synchronized_count,
            result.database_count,
        )
    )
    return 0 if result.source_count == result.database_count else 1


def _run_database_verification(settings: Settings) -> int:
    """Verify PostgreSQL data and basic analysis against the CSV source."""
    result = _database_service(settings).verify()
    print(
        "Database verification: CSV {0}; PostgreSQL {1}; data {2}; analysis {3}".format(
            result.csv_count,
            result.database_count,
            "match" if result.draw_data_matches else "differ",
            "match" if result.basic_analysis_matches else "differ",
        )
    )
    return 0 if result.matches else 1


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


def _print_comparison(result: PeriodComparisonResult) -> None:
    """Print number-rate differences between two historical periods."""
    print(
        "Compared {0} ({1}-{2}, {3} draws) with {4} ({5}-{6}, {7} draws)".format(
            result.baseline_label,
            result.baseline_start_draw,
            result.baseline_end_draw,
            result.baseline_total_draws,
            result.comparison_label,
            result.comparison_start_draw,
            result.comparison_end_draw,
            result.comparison_total_draws,
        )
    )
    print("Number  Base rate  Recent rate  Difference  Rank change")
    for item in sorted(
        result.numbers, key=lambda value: (-abs(value.rate_difference), value.number)
    ):
        print(
            "{0:>6}  {1:>9.2%}  {2:>11.2%}  {3:>+10.2%}  {4:>+11}".format(
                item.number,
                item.baseline_rate,
                item.comparison_rate,
                item.rate_difference,
                item.rank_change,
            )
        )


def _print_gaps(result: GapAnalysisResult) -> None:
    """Print historical appearance-gap statistics for numbers 1 through 45."""
    print(
        "Gap analysis for {0} draws ({1}-{2})".format(
            result.total_draws, result.start_draw, result.end_draw
        )
    )
    print("Number  Appearances  Mean  Median  Min  Max  Latest  Absent  Std dev")
    for item in result.numbers:
        print(
            "{0:>6}  {1:>11}  {2:>4}  {3:>6}  {4:>3}  {5:>3}  "
            "{6:>6}  {7:>6}  {8:>7}".format(
                item.number,
                len(item.appearance_draws),
                _format_optional(item.mean_gap),
                _format_optional(item.median_gap),
                _format_optional(item.minimum_gap),
                _format_optional(item.maximum_gap),
                _format_optional(item.latest_gap),
                item.current_absence,
                _format_optional(item.gap_standard_deviation),
            )
        )


def _print_relationships(result: RelationshipAnalysisResult, top: int) -> None:
    """Print the most frequent historical pairs, triples, and companions."""
    print(
        "Relationship analysis for {0} draws ({1}-{2})".format(
            result.total_draws, result.start_draw, result.end_draw
        )
    )
    print("Top pairs: Numbers  Count  Draw rate")
    for item in result.pairs[:top]:
        print(
            "{0!s:>12}  {1:>5}  {2:>9.2%}".format(
                item.numbers, item.count, item.draw_rate
            )
        )
    print("Top triples: Numbers  Count  Draw rate")
    for item in result.triples[:top]:
        print(
            "{0!s:>12}  {1:>5}  {2:>9.2%}".format(
                item.numbers, item.count, item.draw_rate
            )
        )
    print(
        "Adjacent: {0} pairs in {1} draws ({2:.2%}); same last digit: "
        "{3} pairs in {4} draws ({5:.2%})".format(
            result.adjacent_pair_count,
            result.adjacent_draw_count,
            result.adjacent_draw_rate,
            result.same_last_digit_pair_count,
            result.same_last_digit_draw_count,
            result.same_last_digit_draw_rate,
        )
    )
    print("Top distances: Distance  Count  Pair share")
    for item in sorted(
        result.distances, key=lambda value: (-value.count, value.distance)
    )[:top]:
        print(
            "{0:>8}  {1:>5}  {2:>10.2%}".format(
                item.distance, item.count, item.observation_rate
            )
        )
    print("Top consecutive groups: Numbers  Count  Draw rate")
    for item in result.consecutive_groups[:top]:
        print(
            "{0!s:>12}  {1:>5}  {2:>9.2%}".format(
                item.numbers, item.count, item.draw_rate
            )
        )
    print("Previous draw overlaps: Lag  Compared  Average  Distribution(0-6)")
    for item in result.lag_overlaps:
        print(
            "{0:>3}  {1:>8}  {2:>7.2f}  {3}".format(
                item.lag,
                item.compared_draws,
                item.average_overlap,
                item.overlap_distribution,
            )
        )
    print("Bonus to future main: Lag  Eligible  Appearances  Rate")
    for item in result.bonus_followups:
        print(
            "{0:>3}  {1:>8}  {2:>11}  {3:>7.2%}".format(
                item.lag,
                item.eligible_draws,
                item.main_appearances,
                item.appearance_rate,
            )
        )
    if result.anchor_number is not None:
        print(
            "Companions for {0} ({1} anchor appearances): Number  Count  Rate".format(
                result.anchor_number, result.anchor_appearance_count
            )
        )
        for item in result.companions[:top]:
            print(
                "{0:>6}  {1:>5}  {2:>9.2%}".format(
                    item.number, item.count, item.conditional_rate
                )
            )


def _print_matrix(result: MatrixAnalysisResult) -> None:
    """Print number counts in their fixed 7 by 7 positions."""
    print(
        "7x7 matrix for {0} draws ({1}-{2}); cell format number:count".format(
            result.total_draws, result.start_draw, result.end_draw
        )
    )
    for row in range(7):
        row_cells = result.cells[row * 7 : (row + 1) * 7]
        print(
            "  ".join(
                "  -:  -"
                if cell.number is None
                else "{0:>2}:{1:>3}".format(cell.number, cell.count)
                for cell in row_cells
            )
            + "  | row {0}: {1}".format(row + 1, result.row_totals[row])
        )
    print(
        "Column totals: {0}".format(
            " / ".join(str(total) for total in result.column_totals)
        )
    )
    print(
        "Average distinct rows {0:.2f}; columns {1:.2f}".format(
            result.average_distinct_rows, result.average_distinct_columns
        )
    )
    for diagonal in result.diagonals:
        print(
            "{0} diagonal {1}: {2} appearances in {3} draws ({4:.2%})".format(
                diagonal.name.capitalize(),
                diagonal.numbers,
                diagonal.total_appearances,
                diagonal.draw_count,
                diagonal.draw_rate,
            )
        )


def _print_matrix_comparison(result: MatrixComparisonResult) -> None:
    """Print cell rate differences as a fixed 7 by 7 matrix."""
    print(
        "Matrix comparison: previous {0}-{1} vs recent {2}-{3}; "
        "cell format number:rate difference".format(
            result.baseline_start_draw,
            result.baseline_end_draw,
            result.comparison_start_draw,
            result.comparison_end_draw,
        )
    )
    for row in range(7):
        row_cells = result.cells[row * 7 : (row + 1) * 7]
        print(
            "  ".join(
                "  -:    -"
                if cell.number is None
                else "{0:>2}:{1:>+5.1%}".format(cell.number, cell.rate_difference)
                for cell in row_cells
            )
        )


def _print_patterns(result: PatternAnalysisResult) -> None:
    """Print compact mathematical pattern distributions."""
    print(
        "Pattern analysis for {0} draws ({1}-{2})".format(
            result.total_draws, result.start_draw, result.end_draw
        )
    )
    print("AC distribution: {0}".format(_frequency_text(result.ac_distribution)))
    print(
        "Adjacent gap distribution: {0}".format(
            _frequency_text(result.gap_distribution)
        )
    )
    print(
        "Prime counts: {0}".format(_frequency_text(result.prime_count_distribution))
    )
    print(
        "Composite counts: {0}".format(
            _frequency_text(result.composite_count_distribution)
        )
    )
    print(
        "Square counts: {0}".format(
            _frequency_text(result.square_count_distribution)
        )
    )
    print(
        "Sum bands: {0}".format(
            " / ".join(
                "{0}-{1}:{2}".format(item.minimum, item.maximum, item.count)
                for item in result.sum_band_distribution
            )
        )
    )
    print(
        "Last-digit sum: min {0}; max {1}; mean {2:.2f}".format(
            result.last_digit_sum_minimum,
            result.last_digit_sum_maximum,
            result.last_digit_sum_mean,
        )
    )


def _frequency_text(items: Sequence[object]) -> str:
    """Format value/count result objects without coupling to their model type."""
    return " / ".join(
        "{0}:{1}".format(getattr(item, "value"), getattr(item, "count"))
        for item in items
    )


def _format_optional(value: object) -> str:
    """Format an optional numeric statistic for compact CLI output."""
    if value is None:
        return "-"
    if isinstance(value, float):
        return "{0:.2f}".format(value)
    return str(value)


def _positive_int(value: str) -> int:
    """Parse one strictly positive CLI integer."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _lotto_number(value: str) -> int:
    """Parse one Lotto number from 1 through 45."""
    parsed = int(value)
    if not 1 <= parsed <= 45:
        raise argparse.ArgumentTypeError("value must be from 1 through 45")
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

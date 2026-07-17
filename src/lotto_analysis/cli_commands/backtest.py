"""CLI commands for individual and repeated generation backtests."""

import argparse
from typing import Tuple

from lotto_analysis.config import Settings
from lotto_analysis.database import create_database_engine
from lotto_analysis.models import BacktestExperimentResult, BacktestResult
from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import BacktestExperimentService, BacktestService
from lotto_analysis.storage.analysis_json import write_analysis_json


def register_backtest_commands(subparsers: object) -> None:
    """Register individual and experiment backtest argument parsers."""
    backtest = subparsers.add_parser(  # type: ignore[attr-defined]
        "backtest", help="evaluate generation strategies without future leakage"
    )
    backtest.add_argument(
        "--strategy", choices=("uniform", "frequency"), default="uniform"
    )
    backtest.add_argument("--targets", type=_positive_int, default=20)
    backtest.add_argument("--combinations", type=_positive_int, default=5)
    backtest.add_argument("--seed", type=int, default=42)
    backtest.add_argument("--weight-recent", type=_positive_int, default=0)
    backtest.add_argument("--max-attempts", type=_positive_int, default=10000)
    backtest.add_argument("--export", action="store_true")

    experiment = subparsers.add_parser(  # type: ignore[attr-defined]
        "backtest-experiment", help="repeat comparable strategies, counts, and seeds"
    )
    experiment.add_argument("--targets", type=_positive_int, default=20)
    experiment.add_argument(
        "--combinations", type=_positive_int_list, default=(1, 5, 10, 50)
    )
    experiment.add_argument("--seeds", type=_int_list, default=(41, 42, 43))
    experiment.add_argument("--frequency-recent", type=_positive_int, default=50)
    experiment.add_argument("--max-attempts", type=_positive_int, default=10000)
    experiment.add_argument("--export", action="store_true")


def run_backtest(settings: Settings, args: argparse.Namespace) -> int:
    """Run and optionally export one detailed historical backtest."""
    engine = create_database_engine(settings)
    try:
        result = BacktestService(PostgresDrawRepository(engine)).run(
            strategy_name=args.strategy,
            target_count=args.targets,
            combinations_per_target=args.combinations,
            base_seed=args.seed,
            weight_recent=args.weight_recent,
            maximum_attempts=args.max_attempts,
        )
    finally:
        engine.dispose()
    _print_backtest(result)
    if args.export:
        scope = (
            "recent_{0}".format(args.weight_recent)
            if args.strategy == "frequency" and args.weight_recent
            else "all"
        )
        path = write_analysis_json(
            settings.analysis_data_dir
            / "backtest_{0}_{1}_targets_{2}_combinations_{3}_seed_{4}.json".format(
                args.strategy, scope, args.targets, args.combinations, args.seed
            ),
            result,
        )
        print("Export: {0}".format(path))
    return 0 if result.complete_targets == result.target_count else 1


def run_backtest_experiment(settings: Settings, args: argparse.Namespace) -> int:
    """Run and optionally export a repeated comparable experiment grid."""
    engine = create_database_engine(settings)
    try:
        result = BacktestExperimentService(PostgresDrawRepository(engine)).run(
            target_count=args.targets,
            combination_counts=args.combinations,
            seeds=args.seeds,
            frequency_recent=args.frequency_recent,
            maximum_attempts=args.max_attempts,
        )
    finally:
        engine.dispose()
    _print_experiment(result)
    if args.export:
        combinations = "-".join(str(value) for value in args.combinations)
        seeds = "-".join(str(value) for value in args.seeds)
        path = write_analysis_json(
            settings.analysis_data_dir
            / (
                "backtest_experiment_targets_{0}_combinations_{1}_seeds_{2}"
                "_recent_{3}.json"
            ).format(
                args.targets, combinations, seeds, args.frequency_recent
            ),
            result,
        )
        print("Export: {0}".format(path))
    return 0 if all(
        item.complete_runs == item.run_count for item in result.summaries
    ) else 1


def _print_backtest(result: BacktestResult) -> None:
    print(
        "Backtest strategy {0}; {1} targets; {2} combinations/target; "
        "seed {3}; weight recent {4}".format(
            result.strategy,
            result.target_count,
            result.combinations_per_target,
            result.base_seed,
            result.weight_recent or "all",
        )
    )
    print(
        "Generated {0}; complete targets {1}/{2}; bonus matches {3}".format(
            result.total_generated_combinations,
            result.complete_targets,
            result.target_count,
            result.bonus_match_count,
        )
    )
    print("All combination main matches 0-6: {0}".format(result.main_match_distribution))
    print("Target best matches 0-6: {0}".format(result.best_match_distribution))
    print("Target  Training       Generated  Best  Seed")
    for item in result.targets:
        print(
            "{0:>6}  {1:>4}-{2:<4}  {3:>4}/{4:<4}  {5:>4}  {6}".format(
                item.target_draw_number,
                item.training_start_draw,
                item.training_end_draw,
                item.generated_combinations,
                item.requested_combinations,
                item.best_main_match,
                item.seed,
            )
        )


def _print_experiment(result: BacktestExperimentResult) -> None:
    print(
        "Backtest experiment: {0} targets; seeds {1}; combinations {2}".format(
            result.target_count, result.seeds, result.combination_counts
        )
    )
    print("Strategy             Combos  Runs  Generated  Avg match  Avg best  Bonus")
    for item in result.summaries:
        print(
            "{0:<20}  {1:>6}  {2:>4}/{3:<4}  {4:>9}  {5:>9.3f}  {6:>8.3f}  {7:>5}".format(
                item.strategy_label,
                item.combinations_per_target,
                item.complete_runs,
                item.run_count,
                item.total_generated_combinations,
                item.average_main_match,
                item.average_best_match,
                item.bonus_match_count,
            )
        )


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _int_list(value: str) -> Tuple[int, ...]:
    try:
        values = tuple(int(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("values must be comma-separated integers") from exc
    if not values or len(set(values)) != len(values):
        raise argparse.ArgumentTypeError("values must be non-empty and unique")
    return values


def _positive_int_list(value: str) -> Tuple[int, ...]:
    values = _int_list(value)
    if any(item <= 0 for item in values):
        raise argparse.ArgumentTypeError("values must be positive")
    return values

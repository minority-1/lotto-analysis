"""Repeated comparable backtest experiments across strategies and seeds."""

from typing import Tuple

from lotto_analysis.models.backtest import (
    BacktestExperimentResult,
    BacktestExperimentSummary,
    BacktestResult,
)
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services.backtest_service import BacktestService


class BacktestExperimentService:
    """Run a fixed experiment grid and aggregate stable comparison metrics."""

    def __init__(self, repository: DrawRepository) -> None:
        self._backtests = BacktestService(repository)

    def run(
        self,
        target_count: int,
        combination_counts: Tuple[int, ...],
        seeds: Tuple[int, ...],
        frequency_recent: int,
        maximum_attempts: int = 10000,
    ) -> BacktestExperimentResult:
        """Evaluate uniform, all-frequency, and recent-frequency variants."""
        if not combination_counts or any(
            type(value) is not int or value <= 0 for value in combination_counts
        ):
            raise ValueError("combination_counts must contain positive integers")
        if len(set(combination_counts)) != len(combination_counts):
            raise ValueError("combination_counts must not contain duplicates")
        if not seeds or any(type(seed) is not int for seed in seeds):
            raise ValueError("seeds must contain integers")
        if len(set(seeds)) != len(seeds):
            raise ValueError("seeds must not contain duplicates")
        if type(frequency_recent) is not int or frequency_recent <= 0:
            raise ValueError("frequency_recent must be a positive integer")

        variants = (
            ("uniform", "uniform", 0),
            ("frequency_all", "frequency", 0),
            (
                "frequency_recent_{0}".format(frequency_recent),
                "frequency",
                frequency_recent,
            ),
        )
        summaries = []
        for label, strategy, weight_recent in variants:
            for combinations in combination_counts:
                runs = tuple(
                    self._backtests.run(
                        strategy,
                        target_count,
                        combinations,
                        seed,
                        weight_recent=weight_recent,
                        maximum_attempts=maximum_attempts,
                    )
                    for seed in seeds
                )
                summaries.append(_aggregate(label, runs))
        return BacktestExperimentResult(
            target_count=target_count,
            seeds=seeds,
            combination_counts=combination_counts,
            frequency_recent=frequency_recent,
            summaries=tuple(summaries),
        )


def _aggregate(
    strategy_label: str, runs: Tuple[BacktestResult, ...]
) -> BacktestExperimentSummary:
    main_distribution = tuple(
        sum(run.main_match_distribution[index] for run in runs) for index in range(7)
    )
    best_distribution = tuple(
        sum(run.best_match_distribution[index] for run in runs) for index in range(7)
    )
    total_generated = sum(run.total_generated_combinations for run in runs)
    total_targets = sum(run.target_count for run in runs)
    return BacktestExperimentSummary(
        strategy_label=strategy_label,
        strategy=runs[0].strategy,
        weight_recent=runs[0].weight_recent,
        combinations_per_target=runs[0].combinations_per_target,
        run_count=len(runs),
        complete_runs=sum(run.complete_targets == run.target_count for run in runs),
        total_generated_combinations=total_generated,
        main_match_distribution=main_distribution,  # type: ignore[arg-type]
        best_match_distribution=best_distribution,  # type: ignore[arg-type]
        bonus_match_count=sum(run.bonus_match_count for run in runs),
        average_main_match=(
            sum(index * count for index, count in enumerate(main_distribution))
            / total_generated
            if total_generated
            else 0.0
        ),
        average_best_match=(
            sum(index * count for index, count in enumerate(best_distribution))
            / total_targets
        ),
    )

"""Leakage-safe historical evaluation of number generation strategies."""

from typing import Tuple

from lotto_analysis.generators import (
    FrequencyWeightedStrategy,
    NumberGenerationStrategy,
    UniformRandomStrategy,
    build_frequency_weights,
)
from lotto_analysis.models.backtest import (
    BacktestCombination,
    BacktestResult,
    BacktestTargetResult,
)
from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.generation import GeneratedCombination, GenerationConditions
from lotto_analysis.repositories import DrawRepository, InMemoryDrawRepository
from lotto_analysis.services.generation_service import GenerationService


class BacktestService:
    """Generate from prior draws only and compare candidates with each target."""

    def __init__(self, repository: DrawRepository) -> None:
        self._repository = repository

    def run(
        self,
        strategy_name: str,
        target_count: int,
        combinations_per_target: int,
        base_seed: int,
        weight_recent: int = 0,
        maximum_attempts: int = 10000,
    ) -> BacktestResult:
        """Backtest one strategy over the latest requested historical targets."""
        if strategy_name not in ("uniform", "frequency"):
            raise ValueError("strategy_name must be uniform or frequency")
        for name, value in (
            ("target_count", target_count),
            ("combinations_per_target", combinations_per_target),
            ("maximum_attempts", maximum_attempts),
        ):
            if type(value) is not int or value <= 0:
                raise ValueError("{0} must be a positive integer".format(name))
        if type(base_seed) is not int:
            raise ValueError("base_seed must be an integer")
        if type(weight_recent) is not int or weight_recent < 0:
            raise ValueError("weight_recent must be a non-negative integer")
        if strategy_name == "uniform" and weight_recent:
            raise ValueError("weight_recent requires the frequency strategy")

        draws = self._repository.list_draws()
        if target_count >= len(draws):
            raise ValueError(
                "target_count {0} requires more than {1} available draws".format(
                    target_count, len(draws)
                )
            )
        first_target_index = len(draws) - target_count
        if strategy_name == "frequency" and weight_recent > first_target_index:
            raise ValueError(
                "weight_recent {0} exceeds first training draw count {1}".format(
                    weight_recent, first_target_index
                )
            )

        target_results = []
        main_distribution = [0] * 7
        best_distribution = [0] * 7
        bonus_matches = 0
        for target_index in range(first_target_index, len(draws)):
            target = draws[target_index]
            training = draws[:target_index]
            strategy = self._strategy(strategy_name, training, weight_recent)
            seed = base_seed + target.draw_number
            generation = GenerationService(
                InMemoryDrawRepository(training), strategy
            ).generate(
                GenerationConditions(
                    count=combinations_per_target,
                    maximum_attempts=maximum_attempts,
                    seed=seed,
                )
            )
            evaluated = _evaluate_combinations(generation.combinations, target)
            for item in evaluated:
                main_distribution[item.main_match_count] += 1
                bonus_matches += item.bonus_match
            best_match = max(
                (item.main_match_count for item in evaluated), default=0
            )
            best_distribution[best_match] += 1
            target_results.append(
                BacktestTargetResult(
                    target_draw_number=target.draw_number,
                    training_start_draw=training[0].draw_number,
                    training_end_draw=training[-1].draw_number,
                    training_draws=len(training),
                    actual_numbers=target.numbers,
                    actual_bonus_number=target.bonus_number,
                    seed=seed,
                    requested_combinations=combinations_per_target,
                    generated_combinations=len(evaluated),
                    attempts=generation.attempts,
                    complete=generation.complete,
                    best_main_match=best_match,
                    combinations=evaluated,
                )
            )

        targets = tuple(target_results)
        return BacktestResult(
            strategy=strategy_name,
            target_count=target_count,
            combinations_per_target=combinations_per_target,
            base_seed=base_seed,
            weight_recent=weight_recent,
            total_generated_combinations=sum(
                item.generated_combinations for item in targets
            ),
            complete_targets=sum(item.complete for item in targets),
            main_match_distribution=tuple(main_distribution),  # type: ignore[arg-type]
            best_match_distribution=tuple(best_distribution),  # type: ignore[arg-type]
            bonus_match_count=bonus_matches,
            targets=targets,
        )

    @staticmethod
    def _strategy(
        name: str, training: Tuple[LottoDraw, ...], weight_recent: int
    ) -> NumberGenerationStrategy:
        if name == "uniform":
            return UniformRandomStrategy()
        weight_draws = training[-weight_recent:] if weight_recent else training
        return FrequencyWeightedStrategy(
            build_frequency_weights(weight_draws), len(weight_draws)
        )


def _evaluate_combinations(
    combinations: Tuple[GeneratedCombination, ...], target: LottoDraw
) -> Tuple[BacktestCombination, ...]:
    target_numbers = set(target.numbers)
    return tuple(
        BacktestCombination(
            numbers=item.numbers,
            main_match_count=len(set(item.numbers) & target_numbers),
            bonus_match=target.bonus_number in item.numbers,
        )
        for item in combinations
    )

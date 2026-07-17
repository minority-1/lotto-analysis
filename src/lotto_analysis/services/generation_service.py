"""Coordinate bounded candidate generation, filtering, and explanations."""

from collections import Counter
from random import Random
from typing import Optional

from lotto_analysis.generators import (
    NumberGenerationStrategy,
    UniformRandomStrategy,
    describe_combination,
    rejection_reason,
)
from lotto_analysis.models.generation import GenerationConditions, GenerationResult
from lotto_analysis.repositories import DrawRepository


class GenerationService:
    """Generate unique combinations without coupling strategy and filters."""

    def __init__(
        self,
        repository: DrawRepository,
        strategy: Optional[NumberGenerationStrategy] = None,
    ) -> None:
        self._repository = repository
        self._strategy = strategy or UniformRandomStrategy()

    def generate(self, conditions: GenerationConditions) -> GenerationResult:
        """Generate as many requested combinations as possible within the limit."""
        draws = self._repository.list_draws()
        historical = tuple(frozenset(draw.numbers) for draw in draws)
        available = tuple(
            number
            for number in range(1, 46)
            if number not in conditions.excluded_numbers
        )
        random = Random(conditions.seed)
        generated = []
        generated_sets = []
        rejection_counts: Counter[str] = Counter()
        attempts = 0

        while attempts < conditions.maximum_attempts and len(generated) < conditions.count:
            attempts += 1
            numbers = self._strategy.generate_candidate(
                random, available, conditions.required_numbers
            )
            if frozenset(numbers) in generated_sets:
                rejection_counts["duplicate_result"] += 1
                continue
            combination = describe_combination(numbers, historical)
            reason = rejection_reason(combination, conditions, generated_sets)
            if reason is not None:
                rejection_counts[reason] += 1
                continue
            generated.append(combination)
            generated_sets.append(frozenset(numbers))

        complete = len(generated) == conditions.count
        message = None
        if not complete:
            common = ", ".join(
                "{0}={1}".format(reason, count)
                for reason, count in rejection_counts.most_common(3)
            )
            message = (
                "Generated {0} of {1} combinations after {2} attempts. "
                "Conditions may conflict; most common rejections: {3}."
            ).format(len(generated), conditions.count, attempts, common or "none")
        return GenerationResult(
            strategy=self._strategy.name,
            strategy_details=self._strategy.details,
            requested_count=conditions.count,
            combinations=tuple(generated),
            attempts=attempts,
            maximum_attempts=conditions.maximum_attempts,
            rejection_counts=tuple(sorted(rejection_counts.items())),
            seed=conditions.seed,
            complete=complete,
            message=message,
        )

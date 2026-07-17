"""Condition checks and transparent characteristics for generated candidates."""

from itertools import combinations
from typing import Iterable, Optional, Tuple

from lotto_analysis.analysis.patterns import PRIMES
from lotto_analysis.models.generation import GeneratedCombination, GenerationConditions


def describe_combination(
    numbers: Tuple[int, int, int, int, int, int],
    historical_numbers: Iterable[frozenset],
) -> GeneratedCombination:
    """Calculate reusable filter characteristics for one candidate."""
    historical = tuple(historical_numbers)
    odd_count = sum(number % 2 for number in numbers)
    low_count = sum(number <= 22 for number in numbers)
    differences = {second - first for first, second in combinations(numbers, 2)}
    consecutive_pairs = sum(
        second == first + 1 for first, second in zip(numbers, numbers[1:])
    )
    candidate_set = frozenset(numbers)
    maximum_overlap = max(
        (len(candidate_set & previous) for previous in historical), default=0
    )
    return GeneratedCombination(
        numbers=numbers,
        odd_count=odd_count,
        even_count=6 - odd_count,
        low_count=low_count,
        high_count=6 - low_count,
        number_sum=sum(numbers),
        prime_count=sum(number in PRIMES for number in numbers),
        ac_value=len(differences) - 5,
        consecutive_pair_count=consecutive_pairs,
        maximum_historical_overlap=maximum_overlap,
    )


def rejection_reason(
    combination: GeneratedCombination,
    conditions: GenerationConditions,
    generated_numbers: Iterable[frozenset],
) -> Optional[str]:
    """Return the first failed condition, or None when all filters pass."""
    numbers = set(combination.numbers)
    if not set(conditions.required_numbers) <= numbers:
        return "required_numbers"
    if set(conditions.excluded_numbers) & numbers:
        return "excluded_numbers"
    if not conditions.odd_minimum <= combination.odd_count <= conditions.odd_maximum:
        return "odd_count"
    if not conditions.low_minimum <= combination.low_count <= conditions.low_maximum:
        return "low_count"
    if not conditions.sum_minimum <= combination.number_sum <= conditions.sum_maximum:
        return "number_sum"
    if not conditions.prime_minimum <= combination.prime_count <= conditions.prime_maximum:
        return "prime_count"
    if not conditions.ac_minimum <= combination.ac_value <= conditions.ac_maximum:
        return "ac_value"
    if combination.consecutive_pair_count > conditions.maximum_consecutive_pairs:
        return "consecutive_pairs"
    if conditions.exclude_exact_historical and combination.maximum_historical_overlap == 6:
        return "exact_historical"
    if combination.maximum_historical_overlap > conditions.maximum_historical_overlap:
        return "historical_overlap"
    candidate = frozenset(combination.numbers)
    if any(
        len(candidate & previous) > conditions.maximum_result_overlap
        for previous in generated_numbers
    ):
        return "result_overlap"
    return None

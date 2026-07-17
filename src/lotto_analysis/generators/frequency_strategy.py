"""Smoothed and capped historical-frequency weighted strategy."""

from collections import Counter
from random import Random
from typing import Iterable, Tuple

from lotto_analysis.generators.base import NumberGenerationStrategy
from lotto_analysis.models.draw import LottoDraw


def build_frequency_weights(draws: Iterable[LottoDraw]) -> Tuple[float, ...]:
    """Build 45 additive-smoothed weights capped around their mean."""
    draw_tuple = tuple(draws)
    if not draw_tuple:
        raise ValueError("at least one draw is required for frequency weights")
    counts = Counter(number for draw in draw_tuple for number in draw.numbers)
    raw = tuple(counts[number] + 1.0 for number in range(1, 46))
    average = sum(raw) / 45
    minimum = average * 0.5
    maximum = average * 1.5
    return tuple(min(max(weight, minimum), maximum) for weight in raw)


class FrequencyWeightedStrategy(NumberGenerationStrategy):
    """Sample without replacement using bounded historical-frequency weights."""

    name = "frequency_weighted"

    def __init__(self, weights: Tuple[float, ...], source_draws: int) -> None:
        if len(weights) != 45 or any(weight <= 0 for weight in weights):
            raise ValueError("weights must contain 45 positive values")
        if type(source_draws) is not int or source_draws <= 0:
            raise ValueError("source_draws must be a positive integer")
        self._weights = weights
        self._source_draws = source_draws

    @property
    def details(self) -> Tuple[Tuple[str, str], ...]:
        return (
            ("source_draws", str(self._source_draws)),
            ("smoothing", "count+1"),
            ("weight_cap", "0.5x-1.5x mean"),
        )

    def generate_candidate(
        self,
        random: Random,
        available_numbers: Tuple[int, ...],
        required_numbers: Tuple[int, ...],
    ) -> Tuple[int, int, int, int, int, int]:
        remaining = [
            number for number in available_numbers if number not in required_numbers
        ]
        selected = list(required_numbers)
        while len(selected) < 6:
            weights = [self._weights[number - 1] for number in remaining]
            number = random.choices(remaining, weights=weights, k=1)[0]
            selected.append(number)
            remaining.remove(number)
        return tuple(sorted(selected))  # type: ignore[return-value]

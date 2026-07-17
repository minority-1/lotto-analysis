"""Uniform random Lotto candidate strategy."""

from random import Random
from typing import Tuple

from lotto_analysis.generators.base import NumberGenerationStrategy


class UniformRandomStrategy(NumberGenerationStrategy):
    """Sample every allowed six-number candidate with uniform probability."""

    name = "uniform_random"

    def generate_candidate(
        self,
        random: Random,
        available_numbers: Tuple[int, ...],
        required_numbers: Tuple[int, ...],
    ) -> Tuple[int, int, int, int, int, int]:
        remaining = tuple(
            number for number in available_numbers if number not in required_numbers
        )
        sampled = random.sample(remaining, 6 - len(required_numbers))
        return tuple(sorted(required_numbers + tuple(sampled)))  # type: ignore[return-value]

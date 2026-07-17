"""Strategy interface for producing unfiltered Lotto candidates."""

from abc import ABC, abstractmethod
from random import Random
from typing import Tuple


class NumberGenerationStrategy(ABC):
    """Produce candidate combinations independently from filter rules."""

    name: str

    @abstractmethod
    def generate_candidate(
        self,
        random: Random,
        available_numbers: Tuple[int, ...],
        required_numbers: Tuple[int, ...],
    ) -> Tuple[int, int, int, int, int, int]:
        """Return one sorted six-number candidate."""
        raise NotImplementedError

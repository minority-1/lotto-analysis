"""Models for condition-based Lotto combination generation."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class GenerationConditions:
    """Define filters and execution bounds for one generation request."""

    count: int = 5
    required_numbers: Tuple[int, ...] = ()
    excluded_numbers: Tuple[int, ...] = ()
    odd_minimum: int = 0
    odd_maximum: int = 6
    low_minimum: int = 0
    low_maximum: int = 6
    sum_minimum: int = 21
    sum_maximum: int = 255
    prime_minimum: int = 0
    prime_maximum: int = 6
    ac_minimum: int = 0
    ac_maximum: int = 10
    maximum_consecutive_pairs: int = 5
    exclude_exact_historical: bool = True
    maximum_historical_overlap: int = 4
    maximum_result_overlap: int = 4
    maximum_attempts: int = 10000
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        """Reject impossible or ambiguous generation conditions."""
        if type(self.count) is not int or self.count <= 0:
            raise ValueError("count must be a positive integer")
        _validate_numbers("required_numbers", self.required_numbers)
        _validate_numbers("excluded_numbers", self.excluded_numbers)
        if set(self.required_numbers) & set(self.excluded_numbers):
            raise ValueError("required and excluded numbers must not overlap")
        if len(self.required_numbers) > 6:
            raise ValueError("required_numbers must contain at most six numbers")
        if 45 - len(self.excluded_numbers) < 6:
            raise ValueError("excluded_numbers leave fewer than six candidates")
        for name, minimum, maximum, lower, upper in (
            ("odd", self.odd_minimum, self.odd_maximum, 0, 6),
            ("low", self.low_minimum, self.low_maximum, 0, 6),
            ("sum", self.sum_minimum, self.sum_maximum, 21, 255),
            ("prime", self.prime_minimum, self.prime_maximum, 0, 6),
            ("ac", self.ac_minimum, self.ac_maximum, 0, 10),
        ):
            _validate_range(name, minimum, maximum, lower, upper)
        for name, value, upper in (
            ("maximum_consecutive_pairs", self.maximum_consecutive_pairs, 5),
            ("maximum_historical_overlap", self.maximum_historical_overlap, 6),
            ("maximum_result_overlap", self.maximum_result_overlap, 6),
        ):
            if type(value) is not int or not 0 <= value <= upper:
                raise ValueError("{0} must be from 0 through {1}".format(name, upper))
        if type(self.maximum_attempts) is not int or self.maximum_attempts <= 0:
            raise ValueError("maximum_attempts must be a positive integer")
        if self.seed is not None and type(self.seed) is not int:
            raise ValueError("seed must be an integer or None")


@dataclass(frozen=True)
class GeneratedCombination:
    """Contain one generated combination and its transparent characteristics."""

    numbers: Tuple[int, int, int, int, int, int]
    odd_count: int
    even_count: int
    low_count: int
    high_count: int
    number_sum: int
    prime_count: int
    ac_value: int
    consecutive_pair_count: int
    maximum_historical_overlap: int


@dataclass(frozen=True)
class GenerationResult:
    """Describe a bounded generation run and whether it fully completed."""

    strategy: str
    requested_count: int
    combinations: Tuple[GeneratedCombination, ...]
    attempts: int
    maximum_attempts: int
    rejection_counts: Tuple[Tuple[str, int], ...]
    seed: Optional[int]
    complete: bool
    message: Optional[str]


def _validate_numbers(name: str, numbers: Tuple[int, ...]) -> None:
    if not isinstance(numbers, tuple):
        raise ValueError("{0} must be a tuple".format(name))
    if any(type(number) is not int or not 1 <= number <= 45 for number in numbers):
        raise ValueError("{0} must contain integers from 1 through 45".format(name))
    if len(set(numbers)) != len(numbers):
        raise ValueError("{0} must not contain duplicates".format(name))


def _validate_range(
    name: str, minimum: int, maximum: int, lower: int, upper: int
) -> None:
    if type(minimum) is not int or type(maximum) is not int:
        raise ValueError("{0} range values must be integers".format(name))
    if not lower <= minimum <= maximum <= upper:
        raise ValueError(
            "{0} range must satisfy {1} <= minimum <= maximum <= {2}".format(
                name, lower, upper
            )
        )

"""Serializable models for mathematical Lotto combination patterns."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ValueFrequency:
    """Describe the frequency of one integer-valued pattern."""

    value: int
    count: int
    rate: float


@dataclass(frozen=True)
class SumBandFrequency:
    """Describe draw counts in one inclusive number-sum band."""

    minimum: int
    maximum: int
    count: int
    draw_rate: float


@dataclass(frozen=True)
class DrawPatternStatistics:
    """Describe mathematical properties of one winning combination."""

    draw_number: int
    ac_value: int
    adjacent_gaps: Tuple[int, int, int, int, int]
    prime_count: int
    composite_count: int
    square_count: int
    has_square: bool
    number_sum: int
    sum_band_minimum: int
    sum_band_maximum: int
    last_digit_sum: int


@dataclass(frozen=True)
class PatternAnalysisResult:
    """Contain draw-level and aggregate mathematical pattern statistics."""

    total_draws: int
    start_draw: int
    end_draw: int
    draws: Tuple[DrawPatternStatistics, ...]
    ac_distribution: Tuple[ValueFrequency, ...]
    gap_distribution: Tuple[ValueFrequency, ...]
    prime_count_distribution: Tuple[ValueFrequency, ...]
    composite_count_distribution: Tuple[ValueFrequency, ...]
    square_count_distribution: Tuple[ValueFrequency, ...]
    sum_band_distribution: Tuple[SumBandFrequency, ...]
    last_digit_sum_minimum: int
    last_digit_sum_maximum: int
    last_digit_sum_mean: float

"""Immutable result models for descriptive Lotto statistics."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple


@dataclass(frozen=True)
class NumberStatistics:
    """Describe historical appearances of one number."""

    number: int
    main_count: int
    main_rate: float
    bonus_count: int
    last_draw_number: Optional[int]
    last_draw_date: Optional[date]
    absence_draws: int


@dataclass(frozen=True)
class DrawStatistics:
    """Describe numerical characteristics of one winning combination."""

    draw_number: int
    number_sum: int
    number_mean: float
    number_median: float
    number_min: int
    number_max: int
    number_span: int
    odd_count: int
    even_count: int
    low_count: int
    high_count: int
    section_counts: Tuple[int, int, int, int, int]
    consecutive_pair_count: int
    has_consecutive_numbers: bool
    previous_draw_overlap: Optional[int]


@dataclass(frozen=True)
class BasicAnalysisResult:
    """Contain the complete first-stage descriptive analysis result."""

    total_draws: int
    start_draw: int
    end_draw: int
    number_statistics: Tuple[NumberStatistics, ...]
    draw_statistics: Tuple[DrawStatistics, ...]


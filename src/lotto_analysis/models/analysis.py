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
class AnalysisSummary:
    """Aggregate draw-level distributions for one analysis range."""

    sum_min: int
    sum_max: int
    sum_mean: float
    sum_median: float
    sum_standard_deviation: float
    odd_count_distribution: Tuple[int, int, int, int, int, int, int]
    low_count_distribution: Tuple[int, int, int, int, int, int, int]
    section_totals: Tuple[int, int, int, int, int]
    last_digit_counts: Tuple[int, int, int, int, int, int, int, int, int, int]
    consecutive_draw_count: int
    consecutive_draw_rate: float
    previous_overlap_distribution: Tuple[int, int, int, int, int, int, int]


@dataclass(frozen=True)
class BasicAnalysisResult:
    """Contain the complete first-stage descriptive analysis result."""

    total_draws: int
    start_draw: int
    end_draw: int
    number_statistics: Tuple[NumberStatistics, ...]
    draw_statistics: Tuple[DrawStatistics, ...]
    summary: AnalysisSummary


@dataclass(frozen=True)
class NumberComparison:
    """Compare one number's appearance rates in two periods."""

    number: int
    baseline_count: int
    comparison_count: int
    baseline_rate: float
    comparison_rate: float
    rate_difference: float
    baseline_rank: int
    comparison_rank: int
    rank_change: int


@dataclass(frozen=True)
class PeriodComparisonResult:
    """Contain a prediction-neutral comparison of two draw periods."""

    baseline_label: str
    comparison_label: str
    baseline_start_draw: int
    baseline_end_draw: int
    comparison_start_draw: int
    comparison_end_draw: int
    baseline_total_draws: int
    comparison_total_draws: int
    numbers: Tuple[NumberComparison, ...]


@dataclass(frozen=True)
class NumberGapStatistics:
    """Describe historical draw-number gaps for one Lotto number."""

    number: int
    appearance_draws: Tuple[int, ...]
    gaps: Tuple[int, ...]
    mean_gap: Optional[float]
    median_gap: Optional[float]
    minimum_gap: Optional[int]
    maximum_gap: Optional[int]
    latest_gap: Optional[int]
    current_absence: int
    gap_standard_deviation: Optional[float]


@dataclass(frozen=True)
class GapAnalysisResult:
    """Contain gap statistics for numbers 1 through 45."""

    total_draws: int
    start_draw: int
    end_draw: int
    numbers: Tuple[NumberGapStatistics, ...]

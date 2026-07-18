"""Basic descriptive-analysis API schemas."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class NumberStatisticsResponse(BaseModel):
    """Describe one number's historical appearances."""

    model_config = ConfigDict(from_attributes=True)

    number: int
    main_count: int
    main_rate: float
    bonus_count: int
    last_draw_number: Optional[int]
    last_draw_date: Optional[date]
    absence_draws: int


class DrawStatisticsResponse(BaseModel):
    """Describe one draw's basic numerical characteristics."""

    model_config = ConfigDict(from_attributes=True)

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
    section_counts: List[int]
    consecutive_pair_count: int
    has_consecutive_numbers: bool
    previous_draw_overlap: Optional[int]


class AnalysisSummaryResponse(BaseModel):
    """Describe aggregate distributions for a selected draw range."""

    model_config = ConfigDict(from_attributes=True)

    sum_min: int
    sum_max: int
    sum_mean: float
    sum_median: float
    sum_standard_deviation: float
    odd_count_distribution: List[int]
    low_count_distribution: List[int]
    section_totals: List[int]
    last_digit_counts: List[int]
    consecutive_draw_count: int
    consecutive_draw_rate: float
    previous_overlap_distribution: List[int]


class BasicAnalysisResponse(BaseModel):
    """Return complete first-stage descriptive analysis."""

    model_config = ConfigDict(from_attributes=True)

    total_draws: int
    start_draw: int
    end_draw: int
    number_statistics: List[NumberStatisticsResponse]
    draw_statistics: List[DrawStatisticsResponse]
    summary: AnalysisSummaryResponse


class NumberComparisonResponse(BaseModel):
    """Compare one number across baseline and recent periods."""

    model_config = ConfigDict(from_attributes=True)

    number: int
    baseline_count: int
    comparison_count: int
    baseline_rate: float
    comparison_rate: float
    rate_difference: float
    baseline_rank: int
    comparison_rank: int
    rank_change: int


class PeriodComparisonResponse(BaseModel):
    """Return normalized appearance-rate and rank comparisons."""

    model_config = ConfigDict(from_attributes=True)

    baseline_label: str
    comparison_label: str
    baseline_start_draw: int
    baseline_end_draw: int
    comparison_start_draw: int
    comparison_end_draw: int
    baseline_total_draws: int
    comparison_total_draws: int
    numbers: List[NumberComparisonResponse]


class NumberGapStatisticsResponse(BaseModel):
    """Describe historical appearance gaps for one number."""

    model_config = ConfigDict(from_attributes=True)

    number: int
    appearance_draws: List[int]
    gaps: List[int]
    mean_gap: Optional[float]
    median_gap: Optional[float]
    minimum_gap: Optional[int]
    maximum_gap: Optional[int]
    latest_gap: Optional[int]
    current_absence: int
    gap_standard_deviation: Optional[float]


class GapAnalysisResponse(BaseModel):
    """Return descriptive appearance-gap statistics for numbers 1 through 45."""

    model_config = ConfigDict(from_attributes=True)

    total_draws: int
    start_draw: int
    end_draw: int
    numbers: List[NumberGapStatisticsResponse]

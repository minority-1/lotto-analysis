"""Advanced descriptive-analysis API response schemas."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CombinationFrequencyResponse(BaseModel):
    """Describe one historical pair, triple, or consecutive group."""

    model_config = ConfigDict(from_attributes=True)
    numbers: List[int]
    count: int
    draw_rate: float


class CompanionFrequencyResponse(BaseModel):
    """Describe one number appearing with an anchor number."""

    model_config = ConfigDict(from_attributes=True)
    number: int
    count: int
    conditional_rate: float


class DistanceFrequencyResponse(BaseModel):
    """Describe one number-pair distance frequency."""

    model_config = ConfigDict(from_attributes=True)
    distance: int
    count: int
    observation_rate: float


class LagOverlapResponse(BaseModel):
    """Describe overlaps with one exact preceding draw lag."""

    model_config = ConfigDict(from_attributes=True)
    lag: int
    compared_draws: int
    overlap_distribution: List[int]
    average_overlap: float


class BonusFollowupResponse(BaseModel):
    """Describe bonus-number appearances in a later main-number set."""

    model_config = ConfigDict(from_attributes=True)
    lag: int
    eligible_draws: int
    main_appearances: int
    appearance_rate: float


class RelationshipAnalysisResponse(BaseModel):
    """Return historical number and draw relationship aggregates."""

    model_config = ConfigDict(from_attributes=True)
    total_draws: int
    start_draw: int
    end_draw: int
    pairs: List[CombinationFrequencyResponse]
    triples: List[CombinationFrequencyResponse]
    anchor_number: Optional[int]
    anchor_appearance_count: int
    companions: List[CompanionFrequencyResponse]
    distances: List[DistanceFrequencyResponse]
    adjacent_pair_count: int
    adjacent_draw_count: int
    adjacent_draw_rate: float
    same_last_digit_pair_count: int
    same_last_digit_draw_count: int
    same_last_digit_draw_rate: float
    consecutive_groups: List[CombinationFrequencyResponse]
    lag_overlaps: List[LagOverlapResponse]
    bonus_followups: List[BonusFollowupResponse]


class MatrixCellResponse(BaseModel):
    """Describe one fixed 7 by 7 matrix cell."""

    model_config = ConfigDict(from_attributes=True)
    row: int
    column: int
    number: Optional[int]
    count: int
    draw_rate: float


class DiagonalStatisticsResponse(BaseModel):
    """Describe one fixed matrix diagonal."""

    model_config = ConfigDict(from_attributes=True)
    name: str
    numbers: List[int]
    total_appearances: int
    draw_count: int
    draw_rate: float


class MatrixAnalysisResponse(BaseModel):
    """Return a fixed 7 by 7 historical number matrix."""

    model_config = ConfigDict(from_attributes=True)
    total_draws: int
    start_draw: int
    end_draw: int
    cells: List[MatrixCellResponse]
    row_totals: List[int]
    column_totals: List[int]
    average_distinct_rows: float
    average_distinct_columns: float
    diagonals: List[DiagonalStatisticsResponse]


class MatrixCellComparisonResponse(BaseModel):
    """Compare one fixed cell across previous and recent periods."""

    model_config = ConfigDict(from_attributes=True)
    row: int
    column: int
    number: Optional[int]
    baseline_count: int
    comparison_count: int
    baseline_rate: float
    comparison_rate: float
    rate_difference: float


class MatrixComparisonResponse(BaseModel):
    """Return previous-versus-recent matrix rate differences."""

    model_config = ConfigDict(from_attributes=True)
    baseline_start_draw: int
    baseline_end_draw: int
    comparison_start_draw: int
    comparison_end_draw: int
    baseline_total_draws: int
    comparison_total_draws: int
    cells: List[MatrixCellComparisonResponse]


class ValueFrequencyResponse(BaseModel):
    """Describe one integer-valued pattern frequency."""

    model_config = ConfigDict(from_attributes=True)
    value: int
    count: int
    rate: float


class SumBandFrequencyResponse(BaseModel):
    """Describe one inclusive number-sum band."""

    model_config = ConfigDict(from_attributes=True)
    minimum: int
    maximum: int
    count: int
    draw_rate: float


class DrawPatternStatisticsResponse(BaseModel):
    """Describe mathematical properties of one winning combination."""

    model_config = ConfigDict(from_attributes=True)
    draw_number: int
    ac_value: int
    adjacent_gaps: List[int]
    prime_count: int
    composite_count: int
    square_count: int
    has_square: bool
    number_sum: int
    sum_band_minimum: int
    sum_band_maximum: int
    last_digit_sum: int


class PatternAnalysisResponse(BaseModel):
    """Return mathematical pattern details and distributions."""

    model_config = ConfigDict(from_attributes=True)
    total_draws: int
    start_draw: int
    end_draw: int
    draws: List[DrawPatternStatisticsResponse]
    ac_distribution: List[ValueFrequencyResponse]
    gap_distribution: List[ValueFrequencyResponse]
    prime_count_distribution: List[ValueFrequencyResponse]
    composite_count_distribution: List[ValueFrequencyResponse]
    square_count_distribution: List[ValueFrequencyResponse]
    sum_band_distribution: List[SumBandFrequencyResponse]
    last_digit_sum_minimum: int
    last_digit_sum_maximum: int
    last_digit_sum_mean: float


class DrawSimilarityResponse(BaseModel):
    """Describe one draw's similarity to earlier selected draws."""

    model_config = ConfigDict(from_attributes=True)
    draw_number: int
    compared_draws: int
    maximum_overlap: int
    most_similar_draws: List[int]
    maximum_jaccard: Optional[float]
    overlap_3_count: int
    overlap_4_count: int
    overlap_5_count: int
    overlap_6_count: int


class SimilarityAnalysisResponse(BaseModel):
    """Return unordered-pair overlap distribution and per-draw maxima."""

    model_config = ConfigDict(from_attributes=True)
    total_draws: int
    start_draw: int
    end_draw: int
    pair_comparisons: int
    overlap_distribution: List[int]
    draws: List[DrawSimilarityResponse]

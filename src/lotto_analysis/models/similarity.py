"""Serializable models for historical winning-combination similarity."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class DrawSimilarityStatistics:
    """Describe one draw's similarity to earlier draws in the selected range."""

    draw_number: int
    compared_draws: int
    maximum_overlap: int
    most_similar_draws: Tuple[int, ...]
    maximum_jaccard: Optional[float]
    overlap_3_count: int
    overlap_4_count: int
    overlap_5_count: int
    overlap_6_count: int


@dataclass(frozen=True)
class SimilarityAnalysisResult:
    """Contain draw-level maxima and all unordered-pair overlap counts."""

    total_draws: int
    start_draw: int
    end_draw: int
    pair_comparisons: int
    overlap_distribution: Tuple[int, int, int, int, int, int, int]
    draws: Tuple[DrawSimilarityStatistics, ...]

"""Serializable result models for Lotto number relationship analysis."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class CombinationFrequency:
    """Describe how often one pair or triple appeared in historical draws."""

    numbers: Tuple[int, ...]
    count: int
    draw_rate: float


@dataclass(frozen=True)
class CompanionFrequency:
    """Describe how often another number appeared with an anchor number."""

    number: int
    count: int
    conditional_rate: float


@dataclass(frozen=True)
class DistanceFrequency:
    """Describe one absolute distance among all number-pair observations."""

    distance: int
    count: int
    observation_rate: float


@dataclass(frozen=True)
class LagOverlapStatistics:
    """Describe overlaps with an exactly preceding draw-number lag."""

    lag: int
    compared_draws: int
    overlap_distribution: Tuple[int, int, int, int, int, int, int]
    average_overlap: float


@dataclass(frozen=True)
class RelationshipAnalysisResult:
    """Contain pair, triple, and optional anchor-number relationships."""

    total_draws: int
    start_draw: int
    end_draw: int
    pairs: Tuple[CombinationFrequency, ...]
    triples: Tuple[CombinationFrequency, ...]
    anchor_number: Optional[int]
    anchor_appearance_count: int
    companions: Tuple[CompanionFrequency, ...]
    distances: Tuple[DistanceFrequency, ...]
    adjacent_pair_count: int
    adjacent_draw_count: int
    adjacent_draw_rate: float
    same_last_digit_pair_count: int
    same_last_digit_draw_count: int
    same_last_digit_draw_rate: float
    consecutive_groups: Tuple[CombinationFrequency, ...]
    lag_overlaps: Tuple[LagOverlapStatistics, ...]

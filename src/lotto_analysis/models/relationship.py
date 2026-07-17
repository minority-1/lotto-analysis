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

"""Pure calculations for pair, triple, and companion relationships."""

from collections import Counter
from itertools import combinations
from typing import Iterable, Optional, Tuple

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.relationship import (
    CombinationFrequency,
    CompanionFrequency,
    RelationshipAnalysisResult,
)


def analyze_relationships(
    draws: Iterable[LottoDraw], anchor_number: Optional[int] = None
) -> RelationshipAnalysisResult:
    """Count main-number relationships without assigning predictive meaning."""
    ordered_draws = tuple(sorted(draws, key=lambda draw: draw.draw_number))
    if not ordered_draws:
        raise ValueError("at least one draw is required")
    if anchor_number is not None and (
        type(anchor_number) is not int or not 1 <= anchor_number <= 45
    ):
        raise ValueError("anchor_number must be an integer from 1 through 45")

    pair_counts: Counter[Tuple[int, ...]] = Counter()
    triple_counts: Counter[Tuple[int, ...]] = Counter()
    companion_counts: Counter[int] = Counter()
    anchor_appearances = 0

    for draw in ordered_draws:
        pair_counts.update(combinations(draw.numbers, 2))
        triple_counts.update(combinations(draw.numbers, 3))
        if anchor_number is not None and anchor_number in draw.numbers:
            anchor_appearances += 1
            companion_counts.update(
                number for number in draw.numbers if number != anchor_number
            )

    total_draws = len(ordered_draws)
    return RelationshipAnalysisResult(
        total_draws=total_draws,
        start_draw=ordered_draws[0].draw_number,
        end_draw=ordered_draws[-1].draw_number,
        pairs=_combination_frequencies(pair_counts, total_draws),
        triples=_combination_frequencies(triple_counts, total_draws),
        anchor_number=anchor_number,
        anchor_appearance_count=anchor_appearances,
        companions=_companion_frequencies(companion_counts, anchor_appearances),
    )


def _combination_frequencies(
    counts: Counter[Tuple[int, ...]], total_draws: int
) -> Tuple[CombinationFrequency, ...]:
    return tuple(
        CombinationFrequency(numbers, count, count / total_draws)
        for numbers, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    )


def _companion_frequencies(
    counts: Counter[int], anchor_appearances: int
) -> Tuple[CompanionFrequency, ...]:
    if not anchor_appearances:
        return ()
    return tuple(
        CompanionFrequency(number, count, count / anchor_appearances)
        for number, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    )

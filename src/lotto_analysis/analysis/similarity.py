"""Pure historical similarity calculations for winning combinations."""

from typing import Iterable

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.similarity import (
    DrawSimilarityStatistics,
    SimilarityAnalysisResult,
)


def analyze_similarity(draws: Iterable[LottoDraw]) -> SimilarityAnalysisResult:
    """Compare each combination only with earlier draws in the selected range."""
    ordered_draws = tuple(sorted(draws, key=lambda draw: draw.draw_number))
    if not ordered_draws:
        raise ValueError("at least one draw is required")

    overlap_distribution = [0] * 7
    results = []
    earlier_sets = []
    for draw in ordered_draws:
        current = frozenset(draw.numbers)
        overlaps = []
        for earlier_draw, earlier_numbers in earlier_sets:
            overlap = len(current & earlier_numbers)
            overlap_distribution[overlap] += 1
            overlaps.append((earlier_draw.draw_number, overlap))

        maximum_overlap = max((overlap for _, overlap in overlaps), default=0)
        most_similar = tuple(
            draw_number
            for draw_number, overlap in overlaps
            if overlap == maximum_overlap
        )
        results.append(
            DrawSimilarityStatistics(
                draw_number=draw.draw_number,
                compared_draws=len(overlaps),
                maximum_overlap=maximum_overlap,
                most_similar_draws=most_similar,
                maximum_jaccard=(
                    maximum_overlap / (12 - maximum_overlap) if overlaps else None
                ),
                overlap_3_count=sum(overlap == 3 for _, overlap in overlaps),
                overlap_4_count=sum(overlap == 4 for _, overlap in overlaps),
                overlap_5_count=sum(overlap == 5 for _, overlap in overlaps),
                overlap_6_count=sum(overlap == 6 for _, overlap in overlaps),
            )
        )
        earlier_sets.append((draw, current))

    total_draws = len(ordered_draws)
    return SimilarityAnalysisResult(
        total_draws=total_draws,
        start_draw=ordered_draws[0].draw_number,
        end_draw=ordered_draws[-1].draw_number,
        pair_comparisons=total_draws * (total_draws - 1) // 2,
        overlap_distribution=tuple(overlap_distribution),  # type: ignore[arg-type]
        draws=tuple(results),
    )

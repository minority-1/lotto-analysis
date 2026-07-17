"""Historical appearance-gap analysis for Lotto numbers."""

from statistics import mean, median, pstdev
from typing import Sequence

from lotto_analysis.models.analysis import GapAnalysisResult, NumberGapStatistics
from lotto_analysis.models.draw import LottoDraw


def analyze_gaps(draws: Sequence[LottoDraw]) -> GapAnalysisResult:
    """Calculate draw-number gaps as descriptive historical statistics."""
    if not draws:
        raise ValueError("at least one draw is required for gap analysis")
    ordered = tuple(sorted(draws, key=lambda draw: draw.draw_number))
    latest = ordered[-1].draw_number
    results = []
    for number in range(1, 46):
        appearances = tuple(
            draw.draw_number for draw in ordered if number in draw.numbers
        )
        gaps = tuple(
            current - previous
            for previous, current in zip(appearances, appearances[1:])
        )
        results.append(
            NumberGapStatistics(
                number=number,
                appearance_draws=appearances,
                gaps=gaps,
                mean_gap=mean(gaps) if gaps else None,
                median_gap=median(gaps) if gaps else None,
                minimum_gap=min(gaps) if gaps else None,
                maximum_gap=max(gaps) if gaps else None,
                latest_gap=gaps[-1] if gaps else None,
                current_absence=(latest - appearances[-1] if appearances else len(ordered)),
                gap_standard_deviation=pstdev(gaps) if gaps else None,
            )
        )
    return GapAnalysisResult(
        total_draws=len(ordered),
        start_draw=ordered[0].draw_number,
        end_draw=ordered[-1].draw_number,
        numbers=tuple(results),
    )


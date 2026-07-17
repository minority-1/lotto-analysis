"""Aggregate summaries for first-stage draw statistics."""

from statistics import mean, median, pstdev
from typing import Sequence

from lotto_analysis.models.analysis import AnalysisSummary, DrawStatistics
from lotto_analysis.models.draw import LottoDraw


def summarize_draws(
    draws: Sequence[LottoDraw], statistics: Sequence[DrawStatistics]
) -> AnalysisSummary:
    """Aggregate descriptive distributions for one draw range."""
    sums = tuple(item.number_sum for item in statistics)
    odd = [0] * 7
    low = [0] * 7
    sections = [0] * 5
    endings = [0] * 10
    overlaps = [0] * 7
    for draw, item in zip(draws, statistics):
        odd[item.odd_count] += 1
        low[item.low_count] += 1
        for index, count in enumerate(item.section_counts):
            sections[index] += count
        for number in draw.numbers:
            endings[number % 10] += 1
        if item.previous_draw_overlap is not None:
            overlaps[item.previous_draw_overlap] += 1
    consecutive = sum(item.has_consecutive_numbers for item in statistics)
    return AnalysisSummary(
        sum_min=min(sums),
        sum_max=max(sums),
        sum_mean=mean(sums),
        sum_median=median(sums),
        sum_standard_deviation=pstdev(sums),
        odd_count_distribution=tuple(odd),  # type: ignore[arg-type]
        low_count_distribution=tuple(low),  # type: ignore[arg-type]
        section_totals=tuple(sections),  # type: ignore[arg-type]
        last_digit_counts=tuple(endings),  # type: ignore[arg-type]
        consecutive_draw_count=consecutive,
        consecutive_draw_rate=consecutive / len(statistics),
        previous_overlap_distribution=tuple(overlaps),  # type: ignore[arg-type]
    )

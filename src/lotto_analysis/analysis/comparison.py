"""Appearance-rate comparisons between two draw periods."""

from typing import Dict, Sequence, Tuple

from lotto_analysis.models.analysis import NumberComparison, PeriodComparisonResult
from lotto_analysis.models.draw import LottoDraw


def compare_periods(
    baseline: Sequence[LottoDraw],
    comparison: Sequence[LottoDraw],
    baseline_label: str,
    comparison_label: str,
) -> PeriodComparisonResult:
    """Compare number rates and ranks without treating changes as predictions."""
    if not baseline or not comparison:
        raise ValueError("both comparison periods must contain draws")
    baseline_ordered = tuple(sorted(baseline, key=lambda draw: draw.draw_number))
    comparison_ordered = tuple(sorted(comparison, key=lambda draw: draw.draw_number))
    baseline_counts = _counts(baseline_ordered)
    comparison_counts = _counts(comparison_ordered)
    baseline_rates = {
        number: baseline_counts[number] / len(baseline_ordered)
        for number in range(1, 46)
    }
    comparison_rates = {
        number: comparison_counts[number] / len(comparison_ordered)
        for number in range(1, 46)
    }
    baseline_ranks = _ranks(baseline_rates)
    comparison_ranks = _ranks(comparison_rates)
    numbers = tuple(
        NumberComparison(
            number=number,
            baseline_count=baseline_counts[number],
            comparison_count=comparison_counts[number],
            baseline_rate=baseline_rates[number],
            comparison_rate=comparison_rates[number],
            rate_difference=comparison_rates[number] - baseline_rates[number],
            baseline_rank=baseline_ranks[number],
            comparison_rank=comparison_ranks[number],
            rank_change=baseline_ranks[number] - comparison_ranks[number],
        )
        for number in range(1, 46)
    )
    return PeriodComparisonResult(
        baseline_label=baseline_label,
        comparison_label=comparison_label,
        baseline_start_draw=baseline_ordered[0].draw_number,
        baseline_end_draw=baseline_ordered[-1].draw_number,
        comparison_start_draw=comparison_ordered[0].draw_number,
        comparison_end_draw=comparison_ordered[-1].draw_number,
        baseline_total_draws=len(baseline_ordered),
        comparison_total_draws=len(comparison_ordered),
        numbers=numbers,
    )


def _counts(draws: Sequence[LottoDraw]) -> Dict[int, int]:
    counts = {number: 0 for number in range(1, 46)}
    for draw in draws:
        for number in draw.numbers:
            counts[number] += 1
    return counts


def _ranks(rates: Dict[int, float]) -> Dict[int, int]:
    return {
        number: 1 + sum(other_rate > rate for other_rate in rates.values())
        for number, rate in rates.items()
    }

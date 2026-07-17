"""Pure mathematical pattern analysis for Lotto combinations."""

from collections import Counter
from itertools import combinations
from statistics import mean
from typing import Counter as CounterType, Iterable, Tuple

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.pattern import (
    DrawPatternStatistics,
    PatternAnalysisResult,
    SumBandFrequency,
    ValueFrequency,
)

PRIMES = frozenset((2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43))
SQUARES = frozenset((1, 4, 9, 16, 25, 36))
SUM_BANDS = ((21, 100), (101, 120), (121, 140), (141, 160), (161, 180), (181, 255))


def analyze_patterns(draws: Iterable[LottoDraw]) -> PatternAnalysisResult:
    """Calculate prediction-neutral mathematical properties for draw numbers."""
    ordered_draws = tuple(sorted(draws, key=lambda draw: draw.draw_number))
    if not ordered_draws:
        raise ValueError("at least one draw is required")

    statistics = tuple(_draw_patterns(draw) for draw in ordered_draws)
    total_draws = len(statistics)
    ac_counts = Counter(item.ac_value for item in statistics)
    gap_counts = Counter(gap for item in statistics for gap in item.adjacent_gaps)
    prime_counts = Counter(item.prime_count for item in statistics)
    composite_counts = Counter(item.composite_count for item in statistics)
    square_counts = Counter(item.square_count for item in statistics)
    last_digit_sums = tuple(item.last_digit_sum for item in statistics)
    return PatternAnalysisResult(
        total_draws=total_draws,
        start_draw=ordered_draws[0].draw_number,
        end_draw=ordered_draws[-1].draw_number,
        draws=statistics,
        ac_distribution=_value_frequencies(ac_counts, total_draws),
        gap_distribution=_value_frequencies(gap_counts, total_draws * 5),
        prime_count_distribution=_fixed_frequencies(prime_counts, total_draws),
        composite_count_distribution=_fixed_frequencies(
            composite_counts, total_draws
        ),
        square_count_distribution=_fixed_frequencies(square_counts, total_draws),
        sum_band_distribution=tuple(
            SumBandFrequency(
                minimum,
                maximum,
                sum(item.sum_band_minimum == minimum for item in statistics),
                sum(item.sum_band_minimum == minimum for item in statistics)
                / total_draws,
            )
            for minimum, maximum in SUM_BANDS
        ),
        last_digit_sum_minimum=min(last_digit_sums),
        last_digit_sum_maximum=max(last_digit_sums),
        last_digit_sum_mean=mean(last_digit_sums),
    )


def _draw_patterns(draw: LottoDraw) -> DrawPatternStatistics:
    differences = {second - first for first, second in combinations(draw.numbers, 2)}
    gaps = tuple(
        second - first for first, second in zip(draw.numbers, draw.numbers[1:])
    )
    number_sum = sum(draw.numbers)
    band_minimum, band_maximum = next(
        band for band in SUM_BANDS if band[0] <= number_sum <= band[1]
    )
    square_count = sum(number in SQUARES for number in draw.numbers)
    return DrawPatternStatistics(
        draw_number=draw.draw_number,
        ac_value=len(differences) - 5,
        adjacent_gaps=gaps,  # type: ignore[arg-type]
        prime_count=sum(number in PRIMES for number in draw.numbers),
        composite_count=sum(
            number > 1 and number not in PRIMES for number in draw.numbers
        ),
        square_count=square_count,
        has_square=square_count > 0,
        number_sum=number_sum,
        sum_band_minimum=band_minimum,
        sum_band_maximum=band_maximum,
        last_digit_sum=sum(number % 10 for number in draw.numbers),
    )


def _value_frequencies(
    counts: CounterType[int], denominator: int
) -> Tuple[ValueFrequency, ...]:
    return tuple(
        ValueFrequency(value, count, count / denominator)
        for value, count in sorted(counts.items())
    )


def _fixed_frequencies(
    counts: CounterType[int], denominator: int
) -> Tuple[ValueFrequency, ...]:
    return tuple(
        ValueFrequency(value, counts[value], counts[value] / denominator)
        for value in range(7)
    )

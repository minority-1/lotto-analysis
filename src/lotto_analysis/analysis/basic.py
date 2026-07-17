"""First-stage descriptive statistics for Lotto draw history."""

from statistics import mean, median
from typing import Dict, Optional, Sequence, Tuple

from lotto_analysis.models.analysis import (
    BasicAnalysisResult,
    DrawStatistics,
    NumberStatistics,
)
from lotto_analysis.models.draw import LottoDraw


def analyze_draws(draws: Sequence[LottoDraw]) -> BasicAnalysisResult:
    """Calculate number and draw statistics without making predictions."""
    if not draws:
        raise ValueError("at least one draw is required for analysis")
    ordered = tuple(sorted(draws, key=lambda draw: draw.draw_number))
    draw_numbers = tuple(draw.draw_number for draw in ordered)
    if len(draw_numbers) != len(set(draw_numbers)):
        raise ValueError("analysis input contains duplicate draw numbers")
    return BasicAnalysisResult(
        total_draws=len(ordered),
        start_draw=ordered[0].draw_number,
        end_draw=ordered[-1].draw_number,
        number_statistics=_number_statistics(ordered),
        draw_statistics=_draw_statistics(ordered),
    )


def _number_statistics(draws: Tuple[LottoDraw, ...]) -> Tuple[NumberStatistics, ...]:
    counts: Dict[int, int] = {number: 0 for number in range(1, 46)}
    bonus_counts: Dict[int, int] = {number: 0 for number in range(1, 46)}
    last_positions: Dict[int, int] = {}
    last_draws: Dict[int, LottoDraw] = {}
    for position, draw in enumerate(draws):
        for number in draw.numbers:
            counts[number] += 1
            last_positions[number] = position
            last_draws[number] = draw
        bonus_counts[draw.bonus_number] += 1

    latest_position = len(draws) - 1
    results = []
    for number in range(1, 46):
        last_draw = last_draws.get(number)
        last_position: Optional[int] = last_positions.get(number)
        results.append(
            NumberStatistics(
                number=number,
                main_count=counts[number],
                main_rate=counts[number] / len(draws),
                bonus_count=bonus_counts[number],
                last_draw_number=(last_draw.draw_number if last_draw else None),
                last_draw_date=(last_draw.draw_date if last_draw else None),
                absence_draws=(
                    latest_position - last_position
                    if last_position is not None
                    else len(draws)
                ),
            )
        )
    return tuple(results)


def _draw_statistics(draws: Tuple[LottoDraw, ...]) -> Tuple[DrawStatistics, ...]:
    results = []
    previous_numbers: Optional[set[int]] = None
    for draw in draws:
        numbers = draw.numbers
        odd_count = sum(number % 2 for number in numbers)
        section_counts = tuple(
            sum(lower <= number <= upper for number in numbers)
            for lower, upper in ((1, 10), (11, 20), (21, 30), (31, 40), (41, 45))
        )
        consecutive_pairs = sum(
            right - left == 1 for left, right in zip(numbers, numbers[1:])
        )
        current_numbers = set(numbers)
        results.append(
            DrawStatistics(
                draw_number=draw.draw_number,
                number_sum=sum(numbers),
                number_mean=mean(numbers),
                number_median=median(numbers),
                number_min=numbers[0],
                number_max=numbers[-1],
                number_span=numbers[-1] - numbers[0],
                odd_count=odd_count,
                even_count=6 - odd_count,
                low_count=sum(number <= 22 for number in numbers),
                high_count=sum(number >= 23 for number in numbers),
                section_counts=section_counts,  # type: ignore[arg-type]
                consecutive_pair_count=consecutive_pairs,
                has_consecutive_numbers=consecutive_pairs > 0,
                previous_draw_overlap=(
                    len(current_numbers & previous_numbers)
                    if previous_numbers is not None
                    else None
                ),
            )
        )
        previous_numbers = current_numbers
    return tuple(results)


"""Pure calculations for pair, triple, and companion relationships."""

from collections import Counter
from itertools import combinations
from typing import Iterable, Optional, Tuple

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.relationship import (
    BonusFollowupStatistics,
    CombinationFrequency,
    CompanionFrequency,
    DistanceFrequency,
    LagOverlapStatistics,
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
    distance_counts: Counter[int] = Counter()
    consecutive_group_counts: Counter[Tuple[int, ...]] = Counter()
    anchor_appearances = 0
    adjacent_draws = 0
    same_last_digit_pairs = 0
    same_last_digit_draws = 0

    for draw in ordered_draws:
        pairs = tuple(combinations(draw.numbers, 2))
        pair_counts.update(pairs)
        triple_counts.update(combinations(draw.numbers, 3))
        distances = tuple(second - first for first, second in pairs)
        distance_counts.update(distances)
        if 1 in distances:
            adjacent_draws += 1
        same_last_in_draw = sum(
            first % 10 == second % 10 for first, second in pairs
        )
        same_last_digit_pairs += same_last_in_draw
        if same_last_in_draw:
            same_last_digit_draws += 1
        consecutive_group_counts.update(_consecutive_groups(draw.numbers))
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
        distances=_distance_frequencies(distance_counts, total_draws * 15),
        adjacent_pair_count=distance_counts[1],
        adjacent_draw_count=adjacent_draws,
        adjacent_draw_rate=adjacent_draws / total_draws,
        same_last_digit_pair_count=same_last_digit_pairs,
        same_last_digit_draw_count=same_last_digit_draws,
        same_last_digit_draw_rate=same_last_digit_draws / total_draws,
        consecutive_groups=_combination_frequencies(
            consecutive_group_counts, total_draws
        ),
        lag_overlaps=_lag_overlap_statistics(ordered_draws),
        bonus_followups=_bonus_followup_statistics(ordered_draws),
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


def _distance_frequencies(
    counts: Counter[int], total_observations: int
) -> Tuple[DistanceFrequency, ...]:
    return tuple(
        DistanceFrequency(distance, counts[distance], counts[distance] / total_observations)
        for distance in range(1, 45)
    )


def _consecutive_groups(numbers: Tuple[int, ...]) -> Tuple[Tuple[int, ...], ...]:
    groups = []
    current = [numbers[0]]
    for number in numbers[1:]:
        if number == current[-1] + 1:
            current.append(number)
        else:
            if len(current) > 1:
                groups.append(tuple(current))
            current = [number]
    if len(current) > 1:
        groups.append(tuple(current))
    return tuple(groups)


def _lag_overlap_statistics(
    draws: Tuple[LottoDraw, ...]
) -> Tuple[LagOverlapStatistics, ...]:
    draws_by_number = {draw.draw_number: draw for draw in draws}
    results = []
    for lag in (1, 2, 3):
        overlaps = []
        for draw in draws:
            previous = draws_by_number.get(draw.draw_number - lag)
            if previous is not None:
                overlaps.append(len(set(draw.numbers) & set(previous.numbers)))
        distribution = tuple(overlaps.count(value) for value in range(7))
        results.append(
            LagOverlapStatistics(
                lag=lag,
                compared_draws=len(overlaps),
                overlap_distribution=distribution,  # type: ignore[arg-type]
                average_overlap=sum(overlaps) / len(overlaps) if overlaps else 0.0,
            )
        )
    return tuple(results)


def _bonus_followup_statistics(
    draws: Tuple[LottoDraw, ...]
) -> Tuple[BonusFollowupStatistics, ...]:
    draws_by_number = {draw.draw_number: draw for draw in draws}
    results = []
    for lag in (1, 2, 3):
        eligible = 0
        appearances = 0
        for draw in draws:
            following = draws_by_number.get(draw.draw_number + lag)
            if following is not None:
                eligible += 1
                appearances += draw.bonus_number in following.numbers
        results.append(
            BonusFollowupStatistics(
                lag=lag,
                eligible_draws=eligible,
                main_appearances=appearances,
                appearance_rate=appearances / eligible if eligible else 0.0,
            )
        )
    return tuple(results)

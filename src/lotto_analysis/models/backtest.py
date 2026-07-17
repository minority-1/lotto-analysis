"""Serializable models for leakage-safe generation strategy backtests."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class BacktestCombination:
    """Record one generated combination and its target-draw matches."""

    numbers: Tuple[int, int, int, int, int, int]
    main_match_count: int
    bonus_match: bool


@dataclass(frozen=True)
class BacktestTargetResult:
    """Describe generation and evaluation for one historical target draw."""

    target_draw_number: int
    training_start_draw: int
    training_end_draw: int
    training_draws: int
    actual_numbers: Tuple[int, int, int, int, int, int]
    actual_bonus_number: int
    seed: int
    requested_combinations: int
    generated_combinations: int
    attempts: int
    complete: bool
    best_main_match: int
    combinations: Tuple[BacktestCombination, ...]


@dataclass(frozen=True)
class BacktestResult:
    """Contain comparable aggregate and target-level strategy results."""

    strategy: str
    target_count: int
    combinations_per_target: int
    base_seed: int
    weight_recent: int
    total_generated_combinations: int
    complete_targets: int
    main_match_distribution: Tuple[int, int, int, int, int, int, int]
    best_match_distribution: Tuple[int, int, int, int, int, int, int]
    bonus_match_count: int
    targets: Tuple[BacktestTargetResult, ...]

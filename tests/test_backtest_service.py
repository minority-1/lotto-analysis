from datetime import date
from typing import Tuple

import pytest

from lotto_analysis.models import LottoDraw
from lotto_analysis.repositories import InMemoryDrawRepository
from lotto_analysis.services import BacktestExperimentService, BacktestService


def _draw(draw_number: int, numbers: tuple, bonus: int = 45) -> LottoDraw:
    return LottoDraw(
        draw_number=draw_number,
        draw_date=date(2026, 7, draw_number),
        numbers=numbers,
        bonus_number=bonus,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def _draws() -> Tuple[LottoDraw, ...]:
    return (
        _draw(1, (1, 2, 3, 4, 5, 6)),
        _draw(2, (7, 8, 9, 10, 11, 12)),
        _draw(3, (13, 14, 15, 16, 17, 18)),
        _draw(4, (19, 20, 21, 22, 23, 24)),
        _draw(5, (25, 26, 27, 28, 29, 30)),
    )


def test_backtest_uses_only_draws_before_each_target() -> None:
    result = BacktestService(InMemoryDrawRepository(_draws())).run(
        strategy_name="uniform",
        target_count=2,
        combinations_per_target=3,
        base_seed=100,
    )

    assert result.target_count == 2
    assert result.total_generated_combinations == 6
    assert result.complete_targets == 2
    assert sum(result.main_match_distribution) == 6
    assert sum(result.best_match_distribution) == 2
    assert result.targets[0].target_draw_number == 4
    assert result.targets[0].training_start_draw == 1
    assert result.targets[0].training_end_draw == 3
    assert result.targets[0].training_draws == 3
    assert result.targets[0].seed == 104
    assert result.targets[1].target_draw_number == 5
    assert result.targets[1].training_end_draw == 4
    assert result.targets[1].seed == 105


def test_frequency_backtest_is_reproducible() -> None:
    service = BacktestService(InMemoryDrawRepository(_draws()))

    first = service.run("frequency", 2, 2, 10, weight_recent=3)
    second = service.run("frequency", 2, 2, 10, weight_recent=3)

    assert first == second
    assert first.strategy == "frequency"
    assert first.weight_recent == 3


def test_backtest_rejects_weight_window_larger_than_first_training_period() -> None:
    with pytest.raises(ValueError, match="exceeds first training draw count 3"):
        BacktestService(InMemoryDrawRepository(_draws())).run(
            "frequency", 2, 1, 1, weight_recent=4
        )


def test_backtest_requires_training_draws_before_targets() -> None:
    with pytest.raises(ValueError, match="requires more than 5 available draws"):
        BacktestService(InMemoryDrawRepository(_draws())).run(
            "uniform", 5, 1, 1
        )


def test_backtest_experiment_builds_comparable_strategy_grid() -> None:
    result = BacktestExperimentService(InMemoryDrawRepository(_draws())).run(
        target_count=2,
        combination_counts=(1, 2),
        seeds=(10, 20),
        frequency_recent=3,
    )

    assert len(result.summaries) == 6
    assert result.seeds == (10, 20)
    assert result.combination_counts == (1, 2)
    for summary in result.summaries:
        assert summary.run_count == 2
        assert summary.complete_runs == 2
        assert sum(summary.main_match_distribution) == (
            2 * 2 * summary.combinations_per_target
        )
        assert sum(summary.best_match_distribution) == 4
    labels = {item.strategy_label for item in result.summaries}
    assert labels == {"uniform", "frequency_all", "frequency_recent_3"}

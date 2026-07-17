from datetime import date
from random import Random
from typing import Tuple

import pytest

from lotto_analysis.generators import (
    FrequencyWeightedStrategy,
    NumberGenerationStrategy,
    build_frequency_weights,
)
from lotto_analysis.models import GenerationConditions, LottoDraw
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services import GenerationService


class StubRepository(DrawRepository):
    def list_draws(self, recent: int = 0) -> Tuple[LottoDraw, ...]:
        return (
            LottoDraw(
                draw_number=1,
                draw_date=date(2026, 7, 1),
                numbers=(1, 2, 3, 4, 5, 6),
                bonus_number=7,
                first_prize_winners=1,
                first_prize_amount=100,
                total_sales_amount=1000,
                collected_at=None,
            ),
        )


class FixedStrategy(NumberGenerationStrategy):
    name = "fixed"

    def generate_candidate(
        self,
        random: Random,
        available_numbers: Tuple[int, ...],
        required_numbers: Tuple[int, ...],
    ) -> Tuple[int, int, int, int, int, int]:
        return (1, 2, 3, 4, 5, 6)


def test_generation_is_reproducible_and_respects_core_filters() -> None:
    conditions = GenerationConditions(
        count=3,
        required_numbers=(10,),
        excluded_numbers=(11, 12),
        odd_minimum=2,
        odd_maximum=4,
        sum_minimum=80,
        sum_maximum=200,
        maximum_attempts=1000,
        seed=42,
    )

    first = GenerationService(StubRepository()).generate(conditions)
    second = GenerationService(StubRepository()).generate(conditions)

    assert first == second
    assert first.complete is True
    assert len(first.combinations) == 3
    for item in first.combinations:
        assert 10 in item.numbers
        assert 11 not in item.numbers
        assert 12 not in item.numbers
        assert 2 <= item.odd_count <= 4
        assert 80 <= item.number_sum <= 200
        assert item.maximum_historical_overlap <= 4
    generated_sets = [set(item.numbers) for item in first.combinations]
    assert all(
        len(generated_sets[left] & generated_sets[right]) <= 4
        for left in range(len(generated_sets))
        for right in range(left)
    )


def test_generation_stops_and_explains_impossible_filters() -> None:
    result = GenerationService(StubRepository(), FixedStrategy()).generate(
        GenerationConditions(
            count=1,
            required_numbers=(1, 2, 3, 4, 5, 6),
            maximum_attempts=5,
            seed=1,
        )
    )

    assert result.complete is False
    assert result.combinations == ()
    assert result.attempts == 5
    assert result.rejection_counts == (("exact_historical", 5),)
    assert result.message is not None
    assert "Generated 0 of 1" in result.message


def test_frequency_weights_apply_smoothing_and_mean_cap() -> None:
    draws = StubRepository().list_draws()

    weights = build_frequency_weights(draws)

    assert len(weights) == 45
    assert weights[:6] == pytest.approx((1.7,) * 6)
    assert weights[6:] == pytest.approx((1.0,) * 39)


def test_frequency_strategy_is_reproducible_without_replacement() -> None:
    draws = StubRepository().list_draws()
    strategy = FrequencyWeightedStrategy(build_frequency_weights(draws), len(draws))
    conditions = GenerationConditions(
        count=2,
        required_numbers=(10,),
        excluded_numbers=(45,),
        seed=77,
    )

    first = GenerationService(StubRepository(), strategy).generate(conditions)
    second = GenerationService(StubRepository(), strategy).generate(conditions)

    assert first == second
    assert first.strategy == "frequency_weighted"
    assert first.strategy_details[0] == ("source_draws", "1")
    assert all(len(set(item.numbers)) == 6 for item in first.combinations)
    assert all(10 in item.numbers and 45 not in item.numbers for item in first.combinations)


@pytest.mark.parametrize(
    "conditions, message",
    [
        (
            {"required_numbers": (1,), "excluded_numbers": (1,)},
            "must not overlap",
        ),
        ({"odd_minimum": 5, "odd_maximum": 4}, "odd range"),
        ({"maximum_historical_overlap": 7}, "from 0 through 6"),
        ({"maximum_attempts": 0}, "positive integer"),
    ],
)
def test_generation_conditions_reject_invalid_values(
    conditions: dict, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        GenerationConditions(**conditions)

"""Application orchestration for selecting and running generation strategies."""

from lotto_analysis.generators import (
    FrequencyWeightedStrategy,
    NumberGenerationStrategy,
    build_frequency_weights,
)
from lotto_analysis.models import GenerationConditions, GenerationResult
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services.generation_service import GenerationService


class GenerationApplicationService:
    """Select a public strategy and run the existing generation engine."""

    def __init__(self, repository: DrawRepository) -> None:
        self._repository = repository

    def generate(
        self,
        strategy_name: str,
        weight_recent: int,
        conditions: GenerationConditions,
    ) -> GenerationResult:
        """Generate candidates using uniform or bounded historical frequencies."""
        if strategy_name not in ("uniform", "frequency"):
            raise ValueError("strategy must be uniform or frequency")
        if type(weight_recent) is not int or weight_recent < 0:
            raise ValueError("weight_recent must be a non-negative integer")
        if strategy_name == "uniform" and weight_recent:
            raise ValueError("weight_recent requires the frequency strategy")
        strategy = (
            self._frequency_strategy(weight_recent)
            if strategy_name == "frequency"
            else None
        )
        return GenerationService(self._repository, strategy).generate(conditions)

    def _frequency_strategy(self, recent: int) -> NumberGenerationStrategy:
        draws = self._repository.list_draws(recent=recent)
        if recent and len(draws) < recent:
            raise ValueError(
                "weight_recent {0} exceeds available draw count {1}".format(
                    recent, len(draws)
                )
            )
        return FrequencyWeightedStrategy(
            build_frequency_weights(draws), len(draws)
        )

"""Leakage-safe individual and repeated backtest routes."""

from fastapi import APIRouter, Depends

from lotto_analysis.api.dependencies import get_draw_repository
from lotto_analysis.api.schemas import (
    BacktestExperimentRequest,
    BacktestExperimentResponse,
    BacktestRequest,
    BacktestResponse,
)
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services import BacktestExperimentService, BacktestService


router = APIRouter(prefix="/backtests", tags=["backtests"])


@router.post("/run", response_model=BacktestResponse)
def run_backtest(
    request: BacktestRequest,
    repository: DrawRepository = Depends(get_draw_repository),
) -> BacktestResponse:
    """Run one strategy without exposing target or future draws to training."""
    result = BacktestService(repository).run(
        strategy_name=request.strategy,
        target_count=request.target_count,
        combinations_per_target=request.combinations_per_target,
        base_seed=request.base_seed,
        weight_recent=request.weight_recent,
        maximum_attempts=request.maximum_attempts,
    )
    return BacktestResponse.model_validate(result)


@router.post("/experiment", response_model=BacktestExperimentResponse)
def run_experiment(
    request: BacktestExperimentRequest,
    repository: DrawRepository = Depends(get_draw_repository),
) -> BacktestExperimentResponse:
    """Run uniform and frequency variants under the same comparable grid."""
    result = BacktestExperimentService(repository).run(
        target_count=request.target_count,
        combination_counts=tuple(request.combination_counts),
        seeds=tuple(request.seeds),
        frequency_recent=request.frequency_recent,
        maximum_attempts=request.maximum_attempts,
    )
    return BacktestExperimentResponse.model_validate(result)

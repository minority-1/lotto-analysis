"""Condition-based number generation route."""

from fastapi import APIRouter, Depends

from lotto_analysis.api.dependencies import get_draw_repository
from lotto_analysis.api.schemas import GenerationRequest, GenerationResponse
from lotto_analysis.models import GenerationConditions
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services import GenerationApplicationService


router = APIRouter(prefix="/combinations", tags=["generation"])


@router.post("/generate", response_model=GenerationResponse)
def generate_combinations(
    request: GenerationRequest,
    repository: DrawRepository = Depends(get_draw_repository),
) -> GenerationResponse:
    """Generate condition-matching candidates without predictive claims."""
    conditions = GenerationConditions(
        count=request.count,
        required_numbers=tuple(request.required_numbers),
        excluded_numbers=tuple(request.excluded_numbers),
        odd_minimum=request.odd_minimum,
        odd_maximum=request.odd_maximum,
        low_minimum=request.low_minimum,
        low_maximum=request.low_maximum,
        sum_minimum=request.sum_minimum,
        sum_maximum=request.sum_maximum,
        prime_minimum=request.prime_minimum,
        prime_maximum=request.prime_maximum,
        ac_minimum=request.ac_minimum,
        ac_maximum=request.ac_maximum,
        maximum_consecutive_pairs=request.maximum_consecutive_pairs,
        exclude_exact_historical=request.exclude_exact_historical,
        maximum_historical_overlap=request.maximum_historical_overlap,
        maximum_result_overlap=request.maximum_result_overlap,
        maximum_attempts=request.maximum_attempts,
        seed=request.seed,
    )
    result = GenerationApplicationService(repository).generate(
        strategy_name=request.strategy,
        weight_recent=request.weight_recent,
        conditions=conditions,
    )
    return GenerationResponse.model_validate(result)

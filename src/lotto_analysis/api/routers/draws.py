"""Normalized draw and dashboard routes."""

from typing import List

from fastapi import APIRouter, Depends, Query

from lotto_analysis.api.dependencies import get_draw_repository
from lotto_analysis.api.schemas import DashboardResponse, DrawResponse
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services import DashboardService


router = APIRouter(tags=["draws"])


@router.get("/draws", response_model=List[DrawResponse])
def list_draws(
    recent: int = Query(default=0, ge=0),
    repository: DrawRepository = Depends(get_draw_repository),
) -> List[DrawResponse]:
    """Return all normalized draws or the latest requested N in ascending order."""
    draws = repository.list_draws(recent=recent)
    if recent and len(draws) < recent:
        raise ValueError(
            "recent {0} exceeds available draw count {1}".format(recent, len(draws))
        )
    return [DrawResponse.model_validate(draw) for draw in draws]


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    repository: DrawRepository = Depends(get_draw_repository),
) -> DashboardResponse:
    """Return normalized data coverage and the latest draw."""
    return DashboardResponse.model_validate(DashboardService(repository).summarize())

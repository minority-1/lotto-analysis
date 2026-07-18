"""Normalized draw and dashboard routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from lotto_analysis.api.dependencies import get_draw_repository
from lotto_analysis.api.schemas import (
    DashboardResponse,
    DrawPageResponse,
    DrawResponse,
)
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


@router.get("/draws/latest", response_model=DrawResponse)
def latest_draw(
    repository: DrawRepository = Depends(get_draw_repository),
) -> DrawResponse:
    """Return the latest normalized draw."""
    draws = repository.list_draws(recent=1)
    if not draws:
        raise HTTPException(status_code=404, detail="draw not found")
    return DrawResponse.model_validate(draws[0])


@router.get("/draws/page", response_model=DrawPageResponse)
def list_draws_page(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    repository: DrawRepository = Depends(get_draw_repository),
) -> DrawPageResponse:
    """Return an ascending page of normalized draws."""
    draws = repository.list_draws_page(limit=limit, offset=offset)
    total = repository.count_draws()
    return DrawPageResponse(
        items=[DrawResponse.model_validate(draw) for draw in draws],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(draws) < total,
    )


@router.get("/draws/{draw_number}", response_model=DrawResponse)
def get_draw(
    draw_number: int = Path(ge=1),
    repository: DrawRepository = Depends(get_draw_repository),
) -> DrawResponse:
    """Return one normalized draw by draw number."""
    draw = repository.get_draw(draw_number)
    if draw is None:
        raise HTTPException(status_code=404, detail="draw not found")
    return DrawResponse.model_validate(draw)


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    repository: DrawRepository = Depends(get_draw_repository),
) -> DashboardResponse:
    """Return normalized data coverage and the latest draw."""
    return DashboardResponse.model_validate(DashboardService(repository).summarize())

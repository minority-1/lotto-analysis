"""Descriptive analysis routes."""

from fastapi import APIRouter, Depends, Query

from lotto_analysis.api.dependencies import get_draw_repository
from lotto_analysis.api.schemas import (
    BasicAnalysisResponse,
    GapAnalysisResponse,
    PeriodComparisonResponse,
)
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services import AnalysisService


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/basic", response_model=BasicAnalysisResponse)
def basic_analysis(
    recent: int = Query(default=0, ge=0),
    repository: DrawRepository = Depends(get_draw_repository),
) -> BasicAnalysisResponse:
    """Return basic descriptive statistics for all or recent draws."""
    result = AnalysisService(repository).analyze(recent=recent)
    return BasicAnalysisResponse.model_validate(result)


@router.get("/compare", response_model=PeriodComparisonResponse)
def compare_periods(
    recent: int = Query(ge=1),
    against_all: bool = Query(default=False),
    repository: DrawRepository = Depends(get_draw_repository),
) -> PeriodComparisonResponse:
    """Compare recent appearance rates with all or the preceding equal period."""
    result = AnalysisService(repository).compare(
        recent=recent, against_all=against_all
    )
    return PeriodComparisonResponse.model_validate(result)


@router.get("/gaps", response_model=GapAnalysisResponse)
def appearance_gaps(
    recent: int = Query(default=0, ge=0),
    repository: DrawRepository = Depends(get_draw_repository),
) -> GapAnalysisResponse:
    """Return prediction-neutral historical number appearance gaps."""
    result = AnalysisService(repository).gaps(recent=recent)
    return GapAnalysisResponse.model_validate(result)

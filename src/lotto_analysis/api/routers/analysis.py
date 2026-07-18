"""Descriptive analysis routes."""

from fastapi import APIRouter, Depends, Query

from lotto_analysis.api.dependencies import get_draw_repository
from lotto_analysis.api.schemas import BasicAnalysisResponse
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

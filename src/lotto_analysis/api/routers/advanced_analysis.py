"""Advanced descriptive analysis routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from lotto_analysis.api.dependencies import get_draw_repository
from lotto_analysis.api.schemas import (
    MatrixAnalysisResponse,
    MatrixComparisonResponse,
    PatternAnalysisResponse,
    RelationshipAnalysisResponse,
    SimilarityAnalysisResponse,
)
from lotto_analysis.repositories import DrawRepository
from lotto_analysis.services import AnalysisService


router = APIRouter(prefix="/analysis", tags=["advanced-analysis"])


@router.get("/relationships", response_model=RelationshipAnalysisResponse)
def relationships(
    recent: int = Query(default=0, ge=0),
    number: Optional[int] = Query(default=None, ge=1, le=45),
    repository: DrawRepository = Depends(get_draw_repository),
) -> RelationshipAnalysisResponse:
    """Return pair, triple, companion, distance, and draw-lag relationships."""
    result = AnalysisService(repository).relationships(
        recent=recent, anchor_number=number
    )
    return RelationshipAnalysisResponse.model_validate(result)


@router.get("/matrix", response_model=MatrixAnalysisResponse)
def matrix(
    recent: int = Query(default=0, ge=0),
    repository: DrawRepository = Depends(get_draw_repository),
) -> MatrixAnalysisResponse:
    """Return a fixed 7 by 7 number-frequency matrix."""
    return MatrixAnalysisResponse.model_validate(
        AnalysisService(repository).matrix(recent=recent)
    )


@router.get("/matrix/compare", response_model=MatrixComparisonResponse)
def matrix_comparison(
    recent: int = Query(ge=1),
    repository: DrawRepository = Depends(get_draw_repository),
) -> MatrixComparisonResponse:
    """Compare the recent matrix with the immediately preceding equal period."""
    return MatrixComparisonResponse.model_validate(
        AnalysisService(repository).compare_matrices(recent=recent)
    )


@router.get("/patterns", response_model=PatternAnalysisResponse)
def patterns(
    recent: int = Query(default=0, ge=0),
    repository: DrawRepository = Depends(get_draw_repository),
) -> PatternAnalysisResponse:
    """Return mathematical combination-pattern distributions."""
    return PatternAnalysisResponse.model_validate(
        AnalysisService(repository).patterns(recent=recent)
    )


@router.get("/similarity", response_model=SimilarityAnalysisResponse)
def similarity(
    recent: int = Query(default=0, ge=0),
    repository: DrawRepository = Depends(get_draw_repository),
) -> SimilarityAnalysisResponse:
    """Return historical unordered-pair combination similarity."""
    return SimilarityAnalysisResponse.model_validate(
        AnalysisService(repository).similarity(recent=recent)
    )

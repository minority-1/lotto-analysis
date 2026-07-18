"""API process health route."""

from fastapi import APIRouter

from lotto_analysis.api.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return process health without requiring database access."""
    return HealthResponse(status="ok")

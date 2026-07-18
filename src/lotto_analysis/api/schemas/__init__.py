"""Explicit API request and response schemas."""

from lotto_analysis.api.schemas.analysis import BasicAnalysisResponse
from lotto_analysis.api.schemas.common import ErrorResponse, HealthResponse
from lotto_analysis.api.schemas.draws import DashboardResponse, DrawResponse

__all__ = [
    "BasicAnalysisResponse",
    "DashboardResponse",
    "DrawResponse",
    "ErrorResponse",
    "HealthResponse",
]

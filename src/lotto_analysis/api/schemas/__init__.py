"""Explicit API request and response schemas."""

from lotto_analysis.api.schemas.analysis import (
    BasicAnalysisResponse,
    GapAnalysisResponse,
    PeriodComparisonResponse,
)
from lotto_analysis.api.schemas.common import ErrorResponse, HealthResponse
from lotto_analysis.api.schemas.draws import DashboardResponse, DrawResponse
from lotto_analysis.api.schemas.advanced_analysis import (
    MatrixAnalysisResponse,
    MatrixComparisonResponse,
    PatternAnalysisResponse,
    RelationshipAnalysisResponse,
    SimilarityAnalysisResponse,
)

__all__ = [
    "BasicAnalysisResponse",
    "DashboardResponse",
    "DrawResponse",
    "ErrorResponse",
    "HealthResponse",
    "GapAnalysisResponse",
    "PeriodComparisonResponse",
    "MatrixAnalysisResponse",
    "MatrixComparisonResponse",
    "PatternAnalysisResponse",
    "RelationshipAnalysisResponse",
    "SimilarityAnalysisResponse",
]

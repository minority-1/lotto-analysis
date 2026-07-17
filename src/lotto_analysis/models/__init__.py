"""Domain models."""

from lotto_analysis.models.collection import CollectionFailure, CollectionSummary
from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.database import DatabaseImportResult, DatabaseVerificationResult
from lotto_analysis.models.analysis import (
    AnalysisSummary,
    BasicAnalysisResult,
    DrawStatistics,
    GapAnalysisResult,
    NumberComparison,
    NumberGapStatistics,
    NumberStatistics,
    PeriodComparisonResult,
)
from lotto_analysis.models.processing import ProcessingSummary, ValidationIssue

__all__ = [
    "CollectionFailure",
    "CollectionSummary",
    "AnalysisSummary",
    "BasicAnalysisResult",
    "DrawStatistics",
    "DatabaseImportResult",
    "DatabaseVerificationResult",
    "GapAnalysisResult",
    "LottoDraw",
    "NumberStatistics",
    "NumberComparison",
    "NumberGapStatistics",
    "PeriodComparisonResult",
    "ProcessingSummary",
    "ValidationIssue",
]

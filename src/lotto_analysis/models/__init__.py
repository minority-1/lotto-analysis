"""Domain models."""

from lotto_analysis.models.collection import CollectionFailure, CollectionSummary
from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.matrix import (
    DiagonalStatistics,
    MatrixAnalysisResult,
    MatrixCell,
    MatrixCellComparison,
    MatrixComparisonResult,
)
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
from lotto_analysis.models.relationship import (
    BonusFollowupStatistics,
    CombinationFrequency,
    CompanionFrequency,
    DistanceFrequency,
    LagOverlapStatistics,
    RelationshipAnalysisResult,
)

__all__ = [
    "CollectionFailure",
    "CollectionSummary",
    "CombinationFrequency",
    "CompanionFrequency",
    "DistanceFrequency",
    "DiagonalStatistics",
    "AnalysisSummary",
    "BasicAnalysisResult",
    "BonusFollowupStatistics",
    "DrawStatistics",
    "DatabaseImportResult",
    "DatabaseVerificationResult",
    "GapAnalysisResult",
    "LottoDraw",
    "MatrixAnalysisResult",
    "MatrixCell",
    "MatrixCellComparison",
    "MatrixComparisonResult",
    "LagOverlapStatistics",
    "NumberStatistics",
    "NumberComparison",
    "NumberGapStatistics",
    "PeriodComparisonResult",
    "ProcessingSummary",
    "RelationshipAnalysisResult",
    "ValidationIssue",
]

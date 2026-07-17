"""Domain models."""

from lotto_analysis.models.collection import CollectionFailure, CollectionSummary
from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.analysis import (
    BasicAnalysisResult,
    DrawStatistics,
    NumberStatistics,
)
from lotto_analysis.models.processing import ProcessingSummary, ValidationIssue

__all__ = [
    "CollectionFailure",
    "CollectionSummary",
    "BasicAnalysisResult",
    "DrawStatistics",
    "LottoDraw",
    "NumberStatistics",
    "ProcessingSummary",
    "ValidationIssue",
]

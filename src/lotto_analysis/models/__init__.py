"""Domain models."""

from lotto_analysis.models.collection import CollectionFailure, CollectionSummary
from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.processing import ProcessingSummary, ValidationIssue

__all__ = [
    "CollectionFailure",
    "CollectionSummary",
    "LottoDraw",
    "ProcessingSummary",
    "ValidationIssue",
]

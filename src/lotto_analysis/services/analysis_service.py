"""Application service for descriptive Lotto analysis."""

from typing import Optional

from lotto_analysis.analysis import (
    analyze_draws,
    analyze_gaps,
    analyze_matrix,
    analyze_patterns,
    analyze_relationships,
    analyze_similarity,
    compare_matrices,
    compare_periods,
)
from lotto_analysis.models.analysis import (
    BasicAnalysisResult,
    GapAnalysisResult,
    PeriodComparisonResult,
)
from lotto_analysis.models.matrix import MatrixAnalysisResult, MatrixComparisonResult
from lotto_analysis.models.pattern import PatternAnalysisResult
from lotto_analysis.models.relationship import RelationshipAnalysisResult
from lotto_analysis.models.similarity import SimilarityAnalysisResult
from lotto_analysis.repositories import DrawRepository


class AnalysisService:
    """Load a requested draw range and calculate basic statistics."""

    def __init__(self, repository: DrawRepository) -> None:
        self._repository = repository

    def analyze(self, recent: int = 0) -> BasicAnalysisResult:
        """Analyze all draws or only the latest requested number of draws."""
        return analyze_draws(self._repository.list_draws(recent=recent))

    def compare(
        self, recent: int, against_all: bool = False
    ) -> PeriodComparisonResult:
        """Compare recent draws with all history or the preceding equal period."""
        if type(recent) is not int or recent <= 0:
            raise ValueError("recent must be a positive integer")
        draws = self._repository.list_draws()
        if len(draws) < recent:
            raise ValueError("recent exceeds the available draw count")
        comparison = draws[-recent:]
        if against_all:
            baseline = draws
            baseline_label = "all"
        else:
            if len(draws) < recent * 2:
                raise ValueError("two complete periods are required for comparison")
            baseline = draws[-recent * 2 : -recent]
            baseline_label = "previous_{0}".format(recent)
        return compare_periods(
            baseline,
            comparison,
            baseline_label=baseline_label,
            comparison_label="recent_{0}".format(recent),
        )

    def gaps(self, recent: int = 0) -> GapAnalysisResult:
        """Calculate appearance-gap statistics for all or recent draws."""
        return analyze_gaps(self._repository.list_draws(recent=recent))

    def relationships(
        self, recent: int = 0, anchor_number: Optional[int] = None
    ) -> RelationshipAnalysisResult:
        """Calculate pair, triple, and optional companion frequencies."""
        return analyze_relationships(
            self._repository.list_draws(recent=recent), anchor_number=anchor_number
        )

    def matrix(self, recent: int = 0) -> MatrixAnalysisResult:
        """Calculate a 7 by 7 number-frequency matrix for a draw range."""
        return analyze_matrix(self._repository.list_draws(recent=recent))

    def compare_matrices(self, recent: int) -> MatrixComparisonResult:
        """Compare the recent N-draw matrix with the immediately preceding N."""
        if type(recent) is not int or recent <= 0:
            raise ValueError("recent must be a positive integer")
        draws = self._repository.list_draws()
        if len(draws) < recent * 2:
            raise ValueError("two complete matrix periods are required")
        return compare_matrices(draws[-recent * 2 : -recent], draws[-recent:])

    def patterns(self, recent: int = 0) -> PatternAnalysisResult:
        """Calculate mathematical combination patterns for a draw range."""
        return analyze_patterns(self._repository.list_draws(recent=recent))

    def similarity(self, recent: int = 0) -> SimilarityAnalysisResult:
        """Compare winning combinations within all or recent selected draws."""
        return analyze_similarity(self._repository.list_draws(recent=recent))

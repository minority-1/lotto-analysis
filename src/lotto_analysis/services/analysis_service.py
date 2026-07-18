"""Application service for descriptive Lotto analysis."""

from datetime import date
from typing import Optional, Tuple

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
from lotto_analysis.models.draw import LottoDraw
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
        return analyze_draws(self._recent_draws(recent))

    def analyze_range(
        self,
        start_draw: Optional[int] = None,
        end_draw: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> BasicAnalysisResult:
        """Analyze one inclusive draw-number or draw-date range."""
        draw_range = start_draw is not None or end_draw is not None
        date_range = start_date is not None or end_date is not None
        if draw_range == date_range:
            raise ValueError("provide exactly one draw range or date range")
        if draw_range:
            if start_draw is None or end_draw is None:
                raise ValueError("start_draw and end_draw are both required")
            draws = self._repository.list_draws_by_number_range(start_draw, end_draw)
        else:
            if start_date is None or end_date is None:
                raise ValueError("start_date and end_date are both required")
            draws = self._repository.list_draws_by_date_range(start_date, end_date)
        if not draws:
            raise ValueError("selected range contains no draws")
        return analyze_draws(draws)

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
        return analyze_gaps(self._recent_draws(recent))

    def relationships(
        self, recent: int = 0, anchor_number: Optional[int] = None
    ) -> RelationshipAnalysisResult:
        """Calculate pair, triple, and optional companion frequencies."""
        return analyze_relationships(
            self._recent_draws(recent), anchor_number=anchor_number
        )

    def matrix(self, recent: int = 0) -> MatrixAnalysisResult:
        """Calculate a 7 by 7 number-frequency matrix for a draw range."""
        return analyze_matrix(self._recent_draws(recent))

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
        return analyze_patterns(self._recent_draws(recent))

    def similarity(self, recent: int = 0) -> SimilarityAnalysisResult:
        """Compare winning combinations within all or recent selected draws."""
        return analyze_similarity(self._recent_draws(recent))

    def _recent_draws(self, recent: int) -> Tuple[LottoDraw, ...]:
        """Load a requested range and reject silently shortened results."""
        if type(recent) is not int or recent < 0:
            raise ValueError("recent must be a non-negative integer")
        draws = self._repository.list_draws(recent=recent)
        if recent and len(draws) < recent:
            raise ValueError(
                "recent {0} exceeds available draw count {1}".format(
                    recent, len(draws)
                )
            )
        return draws

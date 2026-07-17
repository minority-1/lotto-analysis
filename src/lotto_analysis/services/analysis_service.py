"""Application service for descriptive Lotto analysis."""

from lotto_analysis.analysis import analyze_draws
from lotto_analysis.models.analysis import BasicAnalysisResult
from lotto_analysis.repositories import DrawRepository


class AnalysisService:
    """Load a requested draw range and calculate basic statistics."""

    def __init__(self, repository: DrawRepository) -> None:
        self._repository = repository

    def analyze(self, recent: int = 0) -> BasicAnalysisResult:
        """Analyze all draws or only the latest requested number of draws."""
        return analyze_draws(self._repository.list_draws(recent=recent))


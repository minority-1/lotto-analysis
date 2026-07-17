"""Pure statistical analysis functions."""

from lotto_analysis.analysis.basic import analyze_draws
from lotto_analysis.analysis.comparison import compare_periods
from lotto_analysis.analysis.gaps import analyze_gaps
from lotto_analysis.analysis.matrix import analyze_matrix, compare_matrices
from lotto_analysis.analysis.patterns import analyze_patterns
from lotto_analysis.analysis.relationships import analyze_relationships
from lotto_analysis.analysis.similarity import analyze_similarity

__all__ = [
    "analyze_draws",
    "analyze_gaps",
    "analyze_matrix",
    "analyze_patterns",
    "analyze_relationships",
    "analyze_similarity",
    "compare_periods",
    "compare_matrices",
]

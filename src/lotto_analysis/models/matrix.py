"""Serializable models for 7 by 7 Lotto number matrices."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class MatrixCell:
    """Describe one number or unused position in a 7 by 7 matrix."""

    row: int
    column: int
    number: Optional[int]
    count: int
    draw_rate: float


@dataclass(frozen=True)
class DiagonalStatistics:
    """Describe appearances on one fixed matrix diagonal."""

    name: str
    numbers: Tuple[int, ...]
    total_appearances: int
    draw_count: int
    draw_rate: float


@dataclass(frozen=True)
class MatrixAnalysisResult:
    """Contain number frequencies and row/column usage for one draw range."""

    total_draws: int
    start_draw: int
    end_draw: int
    cells: Tuple[MatrixCell, ...]
    row_totals: Tuple[int, int, int, int, int, int, int]
    column_totals: Tuple[int, int, int, int, int, int, int]
    average_distinct_rows: float
    average_distinct_columns: float
    diagonals: Tuple[DiagonalStatistics, DiagonalStatistics]


@dataclass(frozen=True)
class MatrixCellComparison:
    """Compare one matrix cell across two historical periods."""

    row: int
    column: int
    number: Optional[int]
    baseline_count: int
    comparison_count: int
    baseline_rate: float
    comparison_rate: float
    rate_difference: float


@dataclass(frozen=True)
class MatrixComparisonResult:
    """Contain a previous-period versus recent-period matrix comparison."""

    baseline_start_draw: int
    baseline_end_draw: int
    comparison_start_draw: int
    comparison_end_draw: int
    baseline_total_draws: int
    comparison_total_draws: int
    cells: Tuple[MatrixCellComparison, ...]

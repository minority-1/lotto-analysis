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

"""Pure 7 by 7 matrix analysis for Lotto numbers 1 through 45."""

from collections import Counter
from typing import Iterable, Tuple

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.matrix import (
    DiagonalStatistics,
    MatrixAnalysisResult,
    MatrixCell,
    MatrixCellComparison,
    MatrixComparisonResult,
)


def analyze_matrix(draws: Iterable[LottoDraw]) -> MatrixAnalysisResult:
    """Map historical main-number appearances onto a fixed 7 by 7 matrix."""
    ordered_draws = tuple(sorted(draws, key=lambda draw: draw.draw_number))
    if not ordered_draws:
        raise ValueError("at least one draw is required")

    number_counts: Counter[int] = Counter()
    distinct_row_total = 0
    distinct_column_total = 0
    for draw in ordered_draws:
        number_counts.update(draw.numbers)
        distinct_row_total += len({_matrix_position(number)[0] for number in draw.numbers})
        distinct_column_total += len(
            {_matrix_position(number)[1] for number in draw.numbers}
        )

    total_draws = len(ordered_draws)
    cells = tuple(
        _matrix_cell(position, number_counts, total_draws) for position in range(49)
    )
    return MatrixAnalysisResult(
        total_draws=total_draws,
        start_draw=ordered_draws[0].draw_number,
        end_draw=ordered_draws[-1].draw_number,
        cells=cells,
        row_totals=tuple(
            sum(cell.count for cell in cells if cell.row == row) for row in range(7)
        ),  # type: ignore[arg-type]
        column_totals=tuple(
            sum(cell.count for cell in cells if cell.column == column)
            for column in range(7)
        ),  # type: ignore[arg-type]
        average_distinct_rows=distinct_row_total / total_draws,
        average_distinct_columns=distinct_column_total / total_draws,
        diagonals=(
            _diagonal_statistics("main", (1, 9, 17, 25, 33, 41), ordered_draws),
            _diagonal_statistics(
                "anti", (7, 13, 19, 25, 31, 37, 43), ordered_draws
            ),
        ),
    )


def compare_matrices(
    baseline_draws: Iterable[LottoDraw], comparison_draws: Iterable[LottoDraw]
) -> MatrixComparisonResult:
    """Compare cell appearance rates between two non-empty draw periods."""
    baseline = analyze_matrix(baseline_draws)
    comparison = analyze_matrix(comparison_draws)
    cells = tuple(
        MatrixCellComparison(
            row=baseline_cell.row,
            column=baseline_cell.column,
            number=baseline_cell.number,
            baseline_count=baseline_cell.count,
            comparison_count=comparison_cell.count,
            baseline_rate=baseline_cell.draw_rate,
            comparison_rate=comparison_cell.draw_rate,
            rate_difference=comparison_cell.draw_rate - baseline_cell.draw_rate,
        )
        for baseline_cell, comparison_cell in zip(baseline.cells, comparison.cells)
    )
    return MatrixComparisonResult(
        baseline_start_draw=baseline.start_draw,
        baseline_end_draw=baseline.end_draw,
        comparison_start_draw=comparison.start_draw,
        comparison_end_draw=comparison.end_draw,
        baseline_total_draws=baseline.total_draws,
        comparison_total_draws=comparison.total_draws,
        cells=cells,
    )


def _matrix_position(number: int) -> Tuple[int, int]:
    position = number - 1
    return position // 7, position % 7


def _matrix_cell(
    position: int, counts: Counter[int], total_draws: int
) -> MatrixCell:
    number = position + 1 if position < 45 else None
    count = counts[number] if number is not None else 0
    return MatrixCell(
        row=position // 7,
        column=position % 7,
        number=number,
        count=count,
        draw_rate=count / total_draws,
    )


def _diagonal_statistics(
    name: str, numbers: Tuple[int, ...], draws: Tuple[LottoDraw, ...]
) -> DiagonalStatistics:
    number_set = set(numbers)
    appearances = tuple(len(number_set & set(draw.numbers)) for draw in draws)
    draw_count = sum(count > 0 for count in appearances)
    return DiagonalStatistics(
        name=name,
        numbers=numbers,
        total_appearances=sum(appearances),
        draw_count=draw_count,
        draw_rate=draw_count / len(draws),
    )

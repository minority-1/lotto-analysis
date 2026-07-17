"""Pure 7 by 7 matrix analysis for Lotto numbers 1 through 45."""

from collections import Counter
from typing import Iterable, Tuple

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.models.matrix import MatrixAnalysisResult, MatrixCell


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

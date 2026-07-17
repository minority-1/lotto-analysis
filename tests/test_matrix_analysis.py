from datetime import date

import pytest

from lotto_analysis.analysis import analyze_matrix, compare_matrices
from lotto_analysis.models import LottoDraw


def _draw(draw_number: int, numbers: tuple) -> LottoDraw:
    return LottoDraw(
        draw_number=draw_number,
        draw_date=date(2026, 7, draw_number),
        numbers=numbers,
        bonus_number=44,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_matrix_analysis_maps_numbers_and_aggregates_axes() -> None:
    result = analyze_matrix((_draw(1, (1, 7, 8, 14, 43, 45)),))

    assert result.total_draws == 1
    assert len(result.cells) == 49
    assert result.cells[0].number == 1
    assert result.cells[0].row == 0
    assert result.cells[0].column == 0
    assert result.cells[0].count == 1
    assert result.cells[44].number == 45
    assert result.cells[44].row == 6
    assert result.cells[44].column == 2
    assert all(cell.number is None and cell.count == 0 for cell in result.cells[45:])
    assert result.row_totals == (2, 2, 0, 0, 0, 0, 2)
    assert result.column_totals == (3, 0, 1, 0, 0, 0, 2)
    assert result.average_distinct_rows == 3.0
    assert result.average_distinct_columns == 3.0
    assert result.diagonals[0].name == "main"
    assert result.diagonals[0].numbers == (1, 9, 17, 25, 33, 41)
    assert result.diagonals[0].total_appearances == 1
    assert result.diagonals[0].draw_count == 1
    assert result.diagonals[1].numbers == (7, 13, 19, 25, 31, 37, 43)
    assert result.diagonals[1].total_appearances == 2


def test_matrix_analysis_calculates_draw_rates() -> None:
    result = analyze_matrix(
        (
            _draw(1, (1, 2, 3, 4, 5, 6)),
            _draw(2, (1, 7, 8, 9, 10, 11)),
        )
    )

    assert result.cells[0].count == 2
    assert result.cells[0].draw_rate == 1.0
    assert result.cells[1].count == 1
    assert result.cells[1].draw_rate == 0.5
    assert sum(result.row_totals) == 12
    assert sum(result.column_totals) == 12


def test_matrix_analysis_requires_draws() -> None:
    with pytest.raises(ValueError, match="at least one draw"):
        analyze_matrix(())


def test_matrix_comparison_calculates_cell_rate_differences() -> None:
    baseline = (_draw(1, (1, 2, 3, 4, 5, 6)),)
    comparison = (_draw(2, (1, 7, 8, 9, 10, 11)),)

    result = compare_matrices(baseline, comparison)

    assert result.baseline_start_draw == 1
    assert result.comparison_end_draw == 2
    assert result.cells[0].rate_difference == 0.0
    assert result.cells[1].baseline_count == 1
    assert result.cells[1].comparison_count == 0
    assert result.cells[1].rate_difference == -1.0
    assert result.cells[6].rate_difference == 1.0
    assert result.cells[45].number is None
    assert result.cells[45].rate_difference == 0.0

from datetime import date

from lotto_analysis.analysis import analyze_matrix
from lotto_analysis.models import LottoDraw
from streamlit_app.views.pattern_analysis import matrix_count_rows


def test_matrix_count_rows_formats_valid_and_empty_cells() -> None:
    draw = LottoDraw(
        draw_number=1,
        draw_date=date(2026, 7, 1),
        numbers=(1, 7, 8, 14, 43, 45),
        bonus_number=44,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )

    rows = matrix_count_rows(analyze_matrix((draw,)))

    assert len(rows) == 7
    assert rows[0]["열 1"] == "1 (1)"
    assert rows[6]["열 3"] == "45 (1)"
    assert rows[6]["열 4"] == "-"

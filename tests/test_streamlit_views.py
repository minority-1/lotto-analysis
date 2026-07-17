from datetime import date

from lotto_analysis.analysis import analyze_matrix
from lotto_analysis.models import LottoDraw
from lotto_analysis.ui.pattern_analysis import matrix_count_rows
from lotto_analysis.ui.relationship_analysis import combination_rows
from lotto_analysis.models import CombinationFrequency


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


def test_combination_rows_formats_pair_frequency() -> None:
    rows = combination_rows(
        (CombinationFrequency(numbers=(1, 2), count=3, draw_rate=0.25),)
    )

    assert rows == [{"번호": "1, 2", "출현": 3, "회차당 비율": 0.25}]

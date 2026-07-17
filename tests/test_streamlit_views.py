from datetime import date

import pytest

from lotto_analysis.analysis import analyze_gaps, analyze_matrix, compare_periods
from lotto_analysis.models import CombinationFrequency, LottoDraw
from lotto_analysis.ui.generation import parse_number_text, parse_optional_seed
from lotto_analysis.ui.pattern_analysis import matrix_count_rows
from lotto_analysis.ui.period_and_gaps import comparison_rows, gap_rows
from lotto_analysis.ui.relationship_analysis import combination_rows


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


def test_generation_input_parsers() -> None:
    assert parse_number_text("7, 2,21") == (2, 7, 21)
    assert parse_number_text("  ") == ()
    assert parse_optional_seed("42") == 42
    assert parse_optional_seed("") is None

    with pytest.raises(ValueError, match="중복"):
        parse_number_text("1,1")
    with pytest.raises(ValueError, match="1부터 45"):
        parse_number_text("46")
    with pytest.raises(ValueError, match="정수"):
        parse_optional_seed("abc")


def test_period_and_gap_rows_preserve_descriptive_values() -> None:
    baseline = analyze_draws_for_view(1, (1, 2, 3, 4, 5, 6))
    recent = analyze_draws_for_view(2, (1, 7, 8, 9, 10, 11))

    comparison = comparison_rows(
        compare_periods((baseline,), (recent,), "previous", "recent")
    )
    gaps = gap_rows(analyze_gaps((baseline, recent)))

    assert comparison[0]["출현률 차이"] == 0.0
    assert comparison[1]["출현률 차이"] == -1.0
    assert gaps[0]["평균 간격"] == 1
    assert gaps[44]["평균 간격"] == "-"


def analyze_draws_for_view(draw_number: int, numbers: tuple) -> LottoDraw:
    return LottoDraw(
        draw_number=draw_number,
        draw_date=date(2026, 7, draw_number),
        numbers=numbers,  # type: ignore[arg-type]
        bonus_number=45,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )

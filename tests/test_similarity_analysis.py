from datetime import date

import pytest

from lotto_analysis.analysis import analyze_similarity
from lotto_analysis.models import LottoDraw


def _draw(draw_number: int, numbers: tuple) -> LottoDraw:
    return LottoDraw(
        draw_number=draw_number,
        draw_date=date(2026, 7, draw_number),
        numbers=numbers,
        bonus_number=45,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_similarity_analysis_counts_pairs_and_draw_maxima() -> None:
    result = analyze_similarity(
        (
            _draw(1, (1, 2, 3, 4, 5, 6)),
            _draw(2, (1, 2, 3, 7, 8, 9)),
            _draw(3, (1, 2, 3, 4, 7, 8)),
        )
    )

    assert result.pair_comparisons == 3
    assert result.overlap_distribution == (0, 0, 0, 1, 1, 1, 0)
    assert result.draws[0].compared_draws == 0
    assert result.draws[0].maximum_jaccard is None
    assert result.draws[1].maximum_overlap == 3
    assert result.draws[1].most_similar_draws == (1,)
    assert result.draws[1].maximum_jaccard == 3 / 9
    assert result.draws[2].maximum_overlap == 5
    assert result.draws[2].most_similar_draws == (2,)
    assert result.draws[2].maximum_jaccard == 5 / 7
    assert result.draws[2].overlap_4_count == 1
    assert result.draws[2].overlap_5_count == 1


def test_similarity_analysis_keeps_all_tied_most_similar_draws() -> None:
    result = analyze_similarity(
        (
            _draw(1, (1, 2, 3, 4, 5, 6)),
            _draw(2, (1, 2, 7, 8, 9, 10)),
            _draw(3, (1, 2, 11, 12, 13, 14)),
        )
    )

    assert result.draws[2].maximum_overlap == 2
    assert result.draws[2].most_similar_draws == (1, 2)


def test_similarity_analysis_requires_draws() -> None:
    with pytest.raises(ValueError, match="at least one draw"):
        analyze_similarity(())

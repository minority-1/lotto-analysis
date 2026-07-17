from datetime import date
from pathlib import Path

import pytest

from lotto_analysis.models import LottoDraw
from lotto_analysis.repositories import CsvDrawRepository
from lotto_analysis.storage.processed_csv import write_processed_csv


def draw(number: int) -> LottoDraw:
    return LottoDraw(
        draw_number=number,
        draw_date=date(2026, 7, number),
        numbers=(1, 2, 3, 4, 5, 6),
        bonus_number=7,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def test_repository_returns_sorted_draws_and_recent_subset(tmp_path: Path) -> None:
    path = tmp_path / "lotto_draws.csv"
    write_processed_csv(path, (draw(3), draw(1), draw(2)))
    repository = CsvDrawRepository(path)

    assert [item.draw_number for item in repository.list_draws()] == [1, 2, 3]
    assert [item.draw_number for item in repository.list_draws(recent=2)] == [2, 3]


def test_repository_reports_missing_processed_csv(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="process"):
        CsvDrawRepository(tmp_path / "missing.csv").list_draws()


def test_repository_rejects_changed_schema(tmp_path: Path) -> None:
    path = tmp_path / "lotto_draws.csv"
    path.write_text("draw_number\n1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="schema"):
        CsvDrawRepository(path).list_draws()


@pytest.mark.parametrize("recent", [-1, 1.5, True])
def test_repository_rejects_invalid_recent(recent: object, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="recent"):
        CsvDrawRepository(tmp_path / "unused.csv").list_draws(recent=recent)  # type: ignore[arg-type]


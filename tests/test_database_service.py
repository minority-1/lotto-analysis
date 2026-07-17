from datetime import date
from typing import Iterable, Tuple

from lotto_analysis.models import LottoDraw
from lotto_analysis.services import DatabaseService


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


class StubCsvRepository:
    def __init__(self, draws: Tuple[LottoDraw, ...]) -> None:
        self.draws = draws

    def list_draws(self, recent: int = 0) -> Tuple[LottoDraw, ...]:
        return self.draws[-recent:] if recent else self.draws


class StubPostgresRepository(StubCsvRepository):
    def upsert_draws(self, draws: Iterable[LottoDraw]) -> int:
        self.draws = tuple(draws)
        return len(self.draws)


def test_database_service_imports_and_verifies_equal_repositories() -> None:
    source = (draw(1), draw(2))
    postgres = StubPostgresRepository(())
    service = DatabaseService(StubCsvRepository(source), postgres)  # type: ignore[arg-type]

    imported = service.import_draws()
    verified = service.verify()

    assert imported.source_count == 2
    assert imported.synchronized_count == 2
    assert imported.database_count == 2
    assert verified.matches is True


def test_database_service_reports_different_data() -> None:
    service = DatabaseService(  # type: ignore[arg-type]
        StubCsvRepository((draw(1), draw(2))),
        StubPostgresRepository((draw(1),)),
    )

    result = service.verify()

    assert result.draw_data_matches is False
    assert result.basic_analysis_matches is False
    assert result.matches is False

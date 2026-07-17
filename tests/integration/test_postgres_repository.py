import os
from datetime import date

import pytest
from sqlalchemy import delete

from lotto_analysis.config import Settings
from lotto_analysis.database import create_database_engine
from lotto_analysis.database.migrations import upgrade_database
from lotto_analysis.database.models import LottoDrawRecord
from lotto_analysis.models import LottoDraw
from lotto_analysis.repositories import PostgresDrawRepository


pytestmark = pytest.mark.postgres


@pytest.mark.skipif(
    os.getenv("LOTTO_RUN_POSTGRES_TESTS") != "1",
    reason="set LOTTO_RUN_POSTGRES_TESTS=1 to use local PostgreSQL",
)
def test_postgres_repository_upserts_and_reads_draw() -> None:
    settings = Settings.from_env()
    upgrade_database(settings.project_root)
    engine = create_database_engine(settings)
    repository = PostgresDrawRepository(engine)
    test_draw = LottoDraw(
        draw_number=999999,
        draw_date=date(2026, 7, 17),
        numbers=(1, 2, 3, 4, 5, 6),
        bonus_number=7,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )
    try:
        assert repository.upsert_draws((test_draw,)) == 1
        assert repository.list_draws(recent=1) == (test_draw,)
    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(LottoDrawRecord).where(
                    LottoDrawRecord.draw_number == test_draw.draw_number
                )
            )
        engine.dispose()

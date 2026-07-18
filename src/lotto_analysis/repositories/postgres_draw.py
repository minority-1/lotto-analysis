"""PostgreSQL implementation of the normalized draw repository."""

from typing import Iterable, Optional, Tuple

from sqlalchemy import Engine, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from lotto_analysis.database.models import LottoDrawRecord
from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.repositories.base import DrawRepository


class PostgresDrawRepository(DrawRepository):
    """Read and upsert normalized draws using SQLAlchemy."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def list_draws(self, recent: int = 0) -> Tuple[LottoDraw, ...]:
        """Return draws in ascending order, optionally limited to latest N."""
        if type(recent) is not int or recent < 0:
            raise ValueError("recent must be a non-negative integer")
        statement = select(LottoDrawRecord).order_by(LottoDrawRecord.draw_number)
        if recent:
            statement = select(LottoDrawRecord).order_by(
                LottoDrawRecord.draw_number.desc()
            ).limit(recent)
        with Session(self._engine) as session:
            records = tuple(session.scalars(statement))
        if recent:
            records = tuple(reversed(records))
        return tuple(_to_domain(record) for record in records)

    def get_draw(self, draw_number: int) -> Optional[LottoDraw]:
        """Return one draw using its primary key."""
        if type(draw_number) is not int or draw_number < 1:
            raise ValueError("draw_number must be a positive integer")
        statement = select(LottoDrawRecord).where(
            LottoDrawRecord.draw_number == draw_number
        )
        with Session(self._engine) as session:
            record = session.scalar(statement)
        return _to_domain(record) if record is not None else None

    def list_draws_page(self, limit: int, offset: int = 0) -> Tuple[LottoDraw, ...]:
        """Return an ascending page without loading the full draw history."""
        if type(limit) is not int or limit < 1:
            raise ValueError("limit must be a positive integer")
        if type(offset) is not int or offset < 0:
            raise ValueError("offset must be a non-negative integer")
        statement = (
            select(LottoDrawRecord)
            .order_by(LottoDrawRecord.draw_number)
            .limit(limit)
            .offset(offset)
        )
        with Session(self._engine) as session:
            records = tuple(session.scalars(statement))
        return tuple(_to_domain(record) for record in records)

    def count_draws(self) -> int:
        """Count normalized draws in PostgreSQL."""
        statement = select(func.count()).select_from(LottoDrawRecord)
        with Session(self._engine) as session:
            return int(session.scalar(statement) or 0)

    def upsert_draws(self, draws: Iterable[LottoDraw]) -> int:
        """Insert or synchronize draws in one transaction by draw number."""
        values = tuple(_to_values(draw) for draw in draws)
        if not values:
            return 0
        statement = insert(LottoDrawRecord).values(values)
        excluded = statement.excluded
        statement = statement.on_conflict_do_update(
            index_elements=[LottoDrawRecord.draw_number],
            set_={
                "draw_date": excluded.draw_date,
                "num1": excluded.num1,
                "num2": excluded.num2,
                "num3": excluded.num3,
                "num4": excluded.num4,
                "num5": excluded.num5,
                "num6": excluded.num6,
                "bonus_number": excluded.bonus_number,
                "first_prize_winners": excluded.first_prize_winners,
                "first_prize_amount": excluded.first_prize_amount,
                "total_sales_amount": excluded.total_sales_amount,
                "collected_at": excluded.collected_at,
                "updated_at": func.now(),
            },
        )
        with self._engine.begin() as connection:
            connection.execute(statement)
        return len(values)


def _to_values(draw: LottoDraw) -> dict:
    return {
        "draw_number": draw.draw_number,
        "draw_date": draw.draw_date,
        "num1": draw.numbers[0],
        "num2": draw.numbers[1],
        "num3": draw.numbers[2],
        "num4": draw.numbers[3],
        "num5": draw.numbers[4],
        "num6": draw.numbers[5],
        "bonus_number": draw.bonus_number,
        "first_prize_winners": draw.first_prize_winners,
        "first_prize_amount": draw.first_prize_amount,
        "total_sales_amount": draw.total_sales_amount,
        "collected_at": draw.collected_at,
    }


def _to_domain(record: LottoDrawRecord) -> LottoDraw:
    return LottoDraw(
        draw_number=record.draw_number,
        draw_date=record.draw_date,
        numbers=(
            record.num1,
            record.num2,
            record.num3,
            record.num4,
            record.num5,
            record.num6,
        ),
        bonus_number=record.bonus_number,
        first_prize_winners=record.first_prize_winners,
        first_prize_amount=record.first_prize_amount,
        total_sales_amount=record.total_sales_amount,
        collected_at=record.collected_at,
    )

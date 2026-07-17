"""Persistent SQLAlchemy models for normalized Lotto data."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from lotto_analysis.database.base import Base


class LottoDrawRecord(Base):
    """Store one unique normalized Korean Lotto draw."""

    __tablename__ = "lotto_draws"
    __table_args__ = (
        UniqueConstraint("draw_number", name="lotto_draws_draw_number_key"),
        CheckConstraint("draw_number > 0", name="ck_lotto_draws_draw_positive"),
        CheckConstraint(
            "num1 between 1 and 45 and num2 between 1 and 45 and "
            "num3 between 1 and 45 and num4 between 1 and 45 and "
            "num5 between 1 and 45 and num6 between 1 and 45 and "
            "bonus_number between 1 and 45",
            name="ck_lotto_draws_number_ranges",
        ),
        CheckConstraint(
            "num1 < num2 and num2 < num3 and num3 < num4 and "
            "num4 < num5 and num5 < num6",
            name="ck_lotto_draws_numbers_sorted_unique",
        ),
        CheckConstraint(
            "bonus_number not in (num1, num2, num3, num4, num5, num6)",
            name="ck_lotto_draws_bonus_unique",
        ),
        CheckConstraint(
            "first_prize_winners >= 0 and first_prize_amount >= 0 and "
            "total_sales_amount >= 0",
            name="ck_lotto_draws_non_negative_amounts",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    draw_number: Mapped[int] = mapped_column(Integer, index=True)
    draw_date: Mapped[date] = mapped_column(Date, index=True)
    num1: Mapped[int] = mapped_column(Integer)
    num2: Mapped[int] = mapped_column(Integer)
    num3: Mapped[int] = mapped_column(Integer)
    num4: Mapped[int] = mapped_column(Integer)
    num5: Mapped[int] = mapped_column(Integer)
    num6: Mapped[int] = mapped_column(Integer)
    bonus_number: Mapped[int] = mapped_column(Integer)
    first_prize_winners: Mapped[int] = mapped_column(Integer)
    first_prize_amount: Mapped[int] = mapped_column(BigInteger)
    total_sales_amount: Mapped[int] = mapped_column(BigInteger)
    collected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

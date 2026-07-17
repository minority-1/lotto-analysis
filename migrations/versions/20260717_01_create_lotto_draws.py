"""Create the normalized Lotto draw table."""

from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260717_01"
down_revision: Optional[str] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create lotto_draws with integrity constraints and indexes."""
    op.create_table(
        "lotto_draws",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("draw_number", sa.Integer(), nullable=False),
        sa.Column("draw_date", sa.Date(), nullable=False),
        sa.Column("num1", sa.Integer(), nullable=False),
        sa.Column("num2", sa.Integer(), nullable=False),
        sa.Column("num3", sa.Integer(), nullable=False),
        sa.Column("num4", sa.Integer(), nullable=False),
        sa.Column("num5", sa.Integer(), nullable=False),
        sa.Column("num6", sa.Integer(), nullable=False),
        sa.Column("bonus_number", sa.Integer(), nullable=False),
        sa.Column("first_prize_winners", sa.Integer(), nullable=False),
        sa.Column("first_prize_amount", sa.BigInteger(), nullable=False),
        sa.Column("total_sales_amount", sa.BigInteger(), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("draw_number > 0", name="ck_lotto_draws_draw_positive"),
        sa.CheckConstraint(
            "num1 between 1 and 45 and num2 between 1 and 45 and "
            "num3 between 1 and 45 and num4 between 1 and 45 and "
            "num5 between 1 and 45 and num6 between 1 and 45 and "
            "bonus_number between 1 and 45",
            name="ck_lotto_draws_number_ranges",
        ),
        sa.CheckConstraint(
            "num1 < num2 and num2 < num3 and num3 < num4 and "
            "num4 < num5 and num5 < num6",
            name="ck_lotto_draws_numbers_sorted_unique",
        ),
        sa.CheckConstraint(
            "bonus_number not in (num1, num2, num3, num4, num5, num6)",
            name="ck_lotto_draws_bonus_unique",
        ),
        sa.CheckConstraint(
            "first_prize_winners >= 0 and first_prize_amount >= 0 and "
            "total_sales_amount >= 0",
            name="ck_lotto_draws_non_negative_amounts",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("draw_number", name="lotto_draws_draw_number_key"),
    )
    op.create_index("ix_lotto_draws_draw_date", "lotto_draws", ["draw_date"])
    op.create_index("ix_lotto_draws_draw_number", "lotto_draws", ["draw_number"])


def downgrade() -> None:
    """Drop the normalized Lotto draw table."""
    op.drop_index("ix_lotto_draws_draw_number", table_name="lotto_draws")
    op.drop_index("ix_lotto_draws_draw_date", table_name="lotto_draws")
    op.drop_table("lotto_draws")

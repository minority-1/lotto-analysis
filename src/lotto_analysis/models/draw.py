"""Domain model for a Korean Lotto 6/45 draw."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Tuple


@dataclass(frozen=True)
class LottoDraw:
    """Represent the normalized data for one Lotto 6/45 draw."""

    draw_number: int
    draw_date: date
    numbers: Tuple[int, int, int, int, int, int]
    bonus_number: int
    first_prize_winners: int
    first_prize_amount: int
    total_sales_amount: int
    collected_at: datetime

    def __post_init__(self) -> None:
        """Validate invariants that every normalized draw must satisfy."""
        if isinstance(self.draw_number, bool) or self.draw_number <= 0:
            raise ValueError("draw_number must be a positive integer")
        if len(self.numbers) != 6:
            raise ValueError("numbers must contain exactly six values")
        if any(isinstance(number, bool) or not 1 <= number <= 45 for number in self.numbers):
            raise ValueError("all winning numbers must be between 1 and 45")
        if len(set(self.numbers)) != 6:
            raise ValueError("winning numbers must be unique")
        if tuple(sorted(self.numbers)) != self.numbers:
            raise ValueError("winning numbers must be sorted in ascending order")
        if isinstance(self.bonus_number, bool) or not 1 <= self.bonus_number <= 45:
            raise ValueError("bonus_number must be between 1 and 45")
        if self.bonus_number in self.numbers:
            raise ValueError("bonus_number must differ from winning numbers")
        if any(
            isinstance(value, bool) or value < 0
            for value in (
                self.first_prize_winners,
                self.first_prize_amount,
                self.total_sales_amount,
            )
        ):
            raise ValueError("winner counts and amounts must be non-negative integers")


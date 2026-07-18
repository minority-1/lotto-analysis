"""Repository interface for normalized Lotto draws."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Tuple

from lotto_analysis.models.draw import LottoDraw


class DrawRepository(ABC):
    """Provide normalized draws without exposing the storage implementation."""

    @abstractmethod
    def list_draws(self, recent: int = 0) -> Tuple[LottoDraw, ...]:
        """Return draws in ascending order, optionally limited to the latest N."""
        raise NotImplementedError

    def get_draw(self, draw_number: int) -> Optional[LottoDraw]:
        """Return one draw by number, or None when it does not exist."""
        if type(draw_number) is not int or draw_number < 1:
            raise ValueError("draw_number must be a positive integer")
        return next(
            (draw for draw in self.list_draws() if draw.draw_number == draw_number),
            None,
        )

    def list_draws_page(self, limit: int, offset: int = 0) -> Tuple[LottoDraw, ...]:
        """Return an ascending page of draws using a zero-based offset."""
        if type(limit) is not int or limit < 1:
            raise ValueError("limit must be a positive integer")
        if type(offset) is not int or offset < 0:
            raise ValueError("offset must be a non-negative integer")
        return self.list_draws()[offset : offset + limit]

    def count_draws(self) -> int:
        """Return the number of normalized draws."""
        return len(self.list_draws())

    def list_draws_by_number_range(
        self, start_draw: int, end_draw: int
    ) -> Tuple[LottoDraw, ...]:
        """Return draws inside an inclusive draw-number range."""
        if type(start_draw) is not int or start_draw < 1:
            raise ValueError("start_draw must be a positive integer")
        if type(end_draw) is not int or end_draw < start_draw:
            raise ValueError("end_draw must be greater than or equal to start_draw")
        return tuple(
            draw
            for draw in self.list_draws()
            if start_draw <= draw.draw_number <= end_draw
        )

    def list_draws_by_date_range(
        self, start_date: date, end_date: date
    ) -> Tuple[LottoDraw, ...]:
        """Return draws inside an inclusive draw-date range."""
        if type(start_date) is not date or type(end_date) is not date:
            raise ValueError("start_date and end_date must be dates")
        if end_date < start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return tuple(
            draw
            for draw in self.list_draws()
            if start_date <= draw.draw_date <= end_date
        )

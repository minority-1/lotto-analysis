"""In-memory repository for bounded historical slices such as backtests."""

from typing import Iterable, Tuple

from lotto_analysis.models.draw import LottoDraw
from lotto_analysis.repositories.base import DrawRepository


class InMemoryDrawRepository(DrawRepository):
    """Expose an immutable sorted draw slice through the Repository interface."""

    def __init__(self, draws: Iterable[LottoDraw]) -> None:
        self._draws = tuple(sorted(draws, key=lambda draw: draw.draw_number))

    def list_draws(self, recent: int = 0) -> Tuple[LottoDraw, ...]:
        if type(recent) is not int or recent < 0:
            raise ValueError("recent must be a non-negative integer")
        return self._draws[-recent:] if recent else self._draws

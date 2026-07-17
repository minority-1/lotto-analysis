"""Repository interface for normalized Lotto draws."""

from abc import ABC, abstractmethod
from typing import Tuple

from lotto_analysis.models.draw import LottoDraw


class DrawRepository(ABC):
    """Provide normalized draws without exposing the storage implementation."""

    @abstractmethod
    def list_draws(self, recent: int = 0) -> Tuple[LottoDraw, ...]:
        """Return draws in ascending order, optionally limited to the latest N."""
        raise NotImplementedError


"""Base interface for collecting one Lotto draw."""

from abc import ABC, abstractmethod

from lotto_analysis.models import LottoDraw


class CollectorError(RuntimeError):
    """Raised when a collector cannot obtain or interpret draw data."""


class DrawCollector(ABC):
    """Define the contract implemented by a single-draw collector."""

    @abstractmethod
    def collect_draw(self, draw_number: int) -> LottoDraw:
        """Collect and return one normalized draw."""
        raise NotImplementedError


"""Interfaces and implementations for draw data collectors."""

from lotto_analysis.collectors.base import (
    CollectorConnectionError,
    CollectorError,
    DrawCollector,
    DrawNotFoundError,
    ResponseFormatError,
)
from lotto_analysis.collectors.dhlottery import DhlotteryDrawCollector

__all__ = [
    "CollectorConnectionError",
    "CollectorError",
    "DhlotteryDrawCollector",
    "DrawCollector",
    "DrawNotFoundError",
    "ResponseFormatError",
]

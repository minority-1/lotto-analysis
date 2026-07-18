"""Common API response schemas."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Describe API process availability."""

    status: Literal["ok"]


class ErrorResponse(BaseModel):
    """Return a stable public error shape."""

    detail: str

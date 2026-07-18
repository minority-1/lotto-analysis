"""Draw and dashboard API schemas."""

from datetime import date, datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, ConfigDict


class DrawResponse(BaseModel):
    """Represent one normalized Lotto draw in API responses."""

    model_config = ConfigDict(from_attributes=True)

    draw_number: int
    draw_date: date
    numbers: Tuple[int, int, int, int, int, int]
    bonus_number: int
    first_prize_winners: int
    first_prize_amount: int
    total_sales_amount: int
    collected_at: Optional[datetime]


class DashboardResponse(BaseModel):
    """Describe normalized draw coverage and latest data."""

    model_config = ConfigDict(from_attributes=True)

    total_draws: int
    first_draw_number: Optional[int]
    latest_draw: Optional[DrawResponse]
    missing_draw_numbers: List[int]

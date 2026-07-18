"""Number generation API request and response schemas."""

from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field


class GenerationRequest(BaseModel):
    """Define one bounded condition-based generation request."""

    strategy: Literal["uniform", "frequency"] = "uniform"
    weight_recent: int = Field(default=0, ge=0)
    count: int = Field(default=5, ge=1, le=100)
    required_numbers: List[int] = Field(default_factory=list, max_length=6)
    excluded_numbers: List[int] = Field(default_factory=list, max_length=39)
    odd_minimum: int = Field(default=0, ge=0, le=6)
    odd_maximum: int = Field(default=6, ge=0, le=6)
    low_minimum: int = Field(default=0, ge=0, le=6)
    low_maximum: int = Field(default=6, ge=0, le=6)
    sum_minimum: int = Field(default=21, ge=21, le=255)
    sum_maximum: int = Field(default=255, ge=21, le=255)
    prime_minimum: int = Field(default=0, ge=0, le=6)
    prime_maximum: int = Field(default=6, ge=0, le=6)
    ac_minimum: int = Field(default=0, ge=0, le=10)
    ac_maximum: int = Field(default=10, ge=0, le=10)
    maximum_consecutive_pairs: int = Field(default=5, ge=0, le=5)
    exclude_exact_historical: bool = True
    maximum_historical_overlap: int = Field(default=4, ge=0, le=6)
    maximum_result_overlap: int = Field(default=4, ge=0, le=6)
    maximum_attempts: int = Field(default=10000, ge=1, le=1000000)
    seed: Optional[int] = None


class GeneratedCombinationResponse(BaseModel):
    """Return one candidate and its transparent characteristics."""

    model_config = ConfigDict(from_attributes=True)
    numbers: Tuple[int, int, int, int, int, int]
    odd_count: int
    even_count: int
    low_count: int
    high_count: int
    number_sum: int
    prime_count: int
    ac_value: int
    consecutive_pair_count: int
    maximum_historical_overlap: int


class GenerationResponse(BaseModel):
    """Return a complete or partial bounded generation run."""

    model_config = ConfigDict(from_attributes=True)
    strategy: str
    strategy_details: List[Tuple[str, str]]
    requested_count: int
    combinations: List[GeneratedCombinationResponse]
    attempts: int
    maximum_attempts: int
    rejection_counts: List[Tuple[str, int]]
    seed: Optional[int]
    complete: bool
    message: Optional[str]

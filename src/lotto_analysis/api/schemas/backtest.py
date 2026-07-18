"""Leakage-safe backtest API request and response schemas."""

from typing import Annotated, List, Literal, Tuple

from pydantic import BaseModel, ConfigDict, Field, model_validator


CombinationCount = Annotated[int, Field(ge=1, le=50)]


class BacktestRequest(BaseModel):
    """Define one detailed historical generation backtest."""

    strategy: Literal["uniform", "frequency"] = "uniform"
    target_count: int = Field(default=20, ge=1, le=100)
    combinations_per_target: int = Field(default=5, ge=1, le=50)
    base_seed: int = 42
    weight_recent: int = Field(default=0, ge=0)
    maximum_attempts: int = Field(default=10000, ge=1, le=10000)

    @model_validator(mode="after")
    def validate_total_work(self) -> "BacktestRequest":
        """Limit synchronous target-by-combination work per request."""
        if self.target_count * self.combinations_per_target > 5000:
            raise ValueError("backtest target and combination product exceeds 5000")
        return self


class BacktestCombinationResponse(BaseModel):
    """Return one generated combination's target matches."""

    model_config = ConfigDict(from_attributes=True)
    numbers: Tuple[int, int, int, int, int, int]
    main_match_count: int
    bonus_match: bool


class BacktestTargetResponse(BaseModel):
    """Return one target draw's leakage-safe training and evaluation result."""

    model_config = ConfigDict(from_attributes=True)
    target_draw_number: int
    training_start_draw: int
    training_end_draw: int
    training_draws: int
    actual_numbers: Tuple[int, int, int, int, int, int]
    actual_bonus_number: int
    seed: int
    requested_combinations: int
    generated_combinations: int
    attempts: int
    complete: bool
    best_main_match: int
    combinations: List[BacktestCombinationResponse]


class BacktestResponse(BaseModel):
    """Return aggregate and target-level results for one strategy run."""

    model_config = ConfigDict(from_attributes=True)
    strategy: str
    target_count: int
    combinations_per_target: int
    base_seed: int
    weight_recent: int
    total_generated_combinations: int
    complete_targets: int
    main_match_distribution: List[int]
    best_match_distribution: List[int]
    bonus_match_count: int
    targets: List[BacktestTargetResponse]


class BacktestExperimentRequest(BaseModel):
    """Define a comparable repeated strategy experiment grid."""

    target_count: int = Field(default=20, ge=1, le=100)
    combination_counts: List[CombinationCount] = Field(
        default_factory=lambda: [1, 5, 10, 50], min_length=1, max_length=4
    )
    seeds: List[int] = Field(
        default_factory=lambda: [41, 42, 43], min_length=1, max_length=10
    )
    frequency_recent: int = Field(default=50, ge=1)
    maximum_attempts: int = Field(default=10000, ge=1, le=10000)

    @model_validator(mode="after")
    def validate_experiment_grid(self) -> "BacktestExperimentRequest":
        """Reject duplicate axes and excessive synchronous experiment grids."""
        if len(set(self.combination_counts)) != len(self.combination_counts):
            raise ValueError("combination_counts must not contain duplicates")
        if len(set(self.seeds)) != len(self.seeds):
            raise ValueError("seeds must not contain duplicates")
        work = self.target_count * sum(self.combination_counts) * len(self.seeds) * 3
        if work > 100000:
            raise ValueError("backtest experiment work exceeds 100000 combinations")
        return self


class BacktestExperimentSummaryResponse(BaseModel):
    """Return repeated summaries for one strategy and combination count."""

    model_config = ConfigDict(from_attributes=True)
    strategy_label: str
    strategy: str
    weight_recent: int
    combinations_per_target: int
    run_count: int
    complete_runs: int
    total_generated_combinations: int
    main_match_distribution: List[int]
    best_match_distribution: List[int]
    bonus_match_count: int
    average_main_match: float
    average_best_match: float


class BacktestExperimentResponse(BaseModel):
    """Return a comparable strategy, count, and seed grid."""

    model_config = ConfigDict(from_attributes=True)
    target_count: int
    seeds: List[int]
    combination_counts: List[int]
    frequency_recent: int
    summaries: List[BacktestExperimentSummaryResponse]

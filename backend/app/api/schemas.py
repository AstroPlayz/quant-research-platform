from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class BacktestRequest(BaseModel):
    symbol: str = Field(default="AAPL", min_length=1)
    period: str = Field(default="1y")
    interval: str = Field(default="1d")
    strategy: Literal["ma_crossover", "rsi", "combined"] = "ma_crossover"
    params: dict[str, float | int] = Field(default_factory=dict)
    initial_cash: float = Field(default=10000.0, gt=0)
    transaction_cost_bps: float = Field(default=10.0, ge=0)
    slippage_bps: float = Field(default=5.0, ge=0)


class GridSearchRequest(BaseModel):
    symbol: str = Field(default="AAPL")
    period: str = Field(default="1y")
    interval: str = Field(default="1d")
    strategy: Literal["ma_crossover", "rsi", "combined"] = "ma_crossover"
    param_grid: dict[str, list[float | int]]
    objective: Literal["return", "max_drawdown", "sharpe", "sortino", "win_rate", "profit_factor"] = "sharpe"


class GeneSpecRequest(BaseModel):
    min_value: float
    max_value: float
    is_int: bool = True


class GeneticRequest(BaseModel):
    symbol: str = Field(default="AAPL")
    period: str = Field(default="1y")
    interval: str = Field(default="1d")
    strategy: Literal["ma_crossover", "rsi", "combined"] = "ma_crossover"
    gene_space: dict[str, GeneSpecRequest]
    objective: Literal["return", "max_drawdown", "sharpe", "sortino", "win_rate", "profit_factor"] = "sharpe"
    population_size: int = 18
    generations: int = 12
    mutation_rate: float = 0.2
    seed: int = 42


class ConditionPayload(BaseModel):
    left: str
    operator: Literal[">", "<", ">=", "<=", "=="]
    right: float | str


class StrategyBuilderRequest(BaseModel):
    symbol: str = Field(default="AAPL")
    period: str = Field(default="1y")
    interval: str = Field(default="1d")
    indicators: dict[str, Any] = Field(default_factory=dict)
    buy_conditions: list[ConditionPayload]
    sell_conditions: list[ConditionPayload]


class SaveStrategyRequest(BaseModel):
    name: str
    payload: dict[str, Any]

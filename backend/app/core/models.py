from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd

SignalValue = Literal[-1, 0, 1]


@dataclass(slots=True)
class StrategyConfig:
    name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Trade:
    timestamp: pd.Timestamp
    side: Literal["buy", "sell"]
    quantity: float
    price: float
    fee: float
    slippage_cost: float
    pnl: float = 0.0


@dataclass(slots=True)
class PortfolioState:
    cash: float
    position: int
    shares: float
    entry_price: float | None
    last_price: float

    @property
    def equity(self) -> float:
        return self.cash + (self.shares * self.last_price)


@dataclass(slots=True)
class BacktestResult:
    strategy_name: str
    params: dict[str, Any]
    equity_curve: list[float]
    drawdown_curve: list[float]
    buy_hold_equity: list[float]
    timestamps: list[str]
    trades: list[dict[str, Any]]
    metrics: dict[str, float]
    indicators: dict[str, list[float | None]]

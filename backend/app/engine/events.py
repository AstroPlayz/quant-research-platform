from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class MarketEvent:
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class SignalEvent:
    timestamp: pd.Timestamp
    signal: int


@dataclass(slots=True)
class OrderEvent:
    timestamp: pd.Timestamp
    side: str
    quantity: float


@dataclass(slots=True)
class FillEvent:
    timestamp: pd.Timestamp
    side: str
    quantity: float
    price: float
    fee: float
    slippage_cost: float

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass(slots=True)
class Condition:
    left: str
    operator: Literal[">", "<", ">=", "<=", "=="]
    right: float | str


def evaluate_condition(indicators: pd.DataFrame, condition: Condition) -> pd.Series:
    left = indicators[condition.left]
    right = indicators[condition.right] if isinstance(condition.right, str) else condition.right

    if condition.operator == ">":
        return left > right
    if condition.operator == "<":
        return left < right
    if condition.operator == ">=":
        return left >= right
    if condition.operator == "<=":
        return left <= right
    return left == right


def build_signal(indicators: pd.DataFrame, buy_conditions: list[Condition], sell_conditions: list[Condition]) -> pd.Series:
    buy_mask = pd.Series(True, index=indicators.index)
    sell_mask = pd.Series(False, index=indicators.index)

    for cond in buy_conditions:
        buy_mask &= evaluate_condition(indicators, cond)

    for cond in sell_conditions:
        sell_mask |= evaluate_condition(indicators, cond)

    signal = pd.Series(0, index=indicators.index, dtype="int64")
    signal[buy_mask] = 1
    signal[sell_mask] = -1
    return signal

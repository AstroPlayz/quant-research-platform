from __future__ import annotations

import math

import numpy as np


def max_drawdown(equity: list[float]) -> float:
    if not equity:
        return 0.0
    arr = np.array(equity, dtype=float)
    peaks = np.maximum.accumulate(arr)
    dd = (arr / peaks) - 1.0
    return float(dd.min())


def sharpe_ratio(returns: np.ndarray, annualization: int = 252) -> float:
    if returns.size == 0:
        return 0.0
    std = float(np.std(returns))
    if std == 0:
        return 0.0
    return float((np.mean(returns) / std) * math.sqrt(annualization))


def sortino_ratio(returns: np.ndarray, annualization: int = 252) -> float:
    if returns.size == 0:
        return 0.0
    downside = returns[returns < 0]
    if downside.size == 0:
        return 0.0
    downside_std = float(np.std(downside))
    if downside_std == 0:
        return 0.0
    return float((np.mean(returns) / downside_std) * math.sqrt(annualization))


def win_rate(trade_pnls: list[float]) -> float:
    if not trade_pnls:
        return 0.0
    wins = len([p for p in trade_pnls if p > 0])
    return float(wins / len(trade_pnls))


def profit_factor(trade_pnls: list[float]) -> float:
    gross_profit = sum(p for p in trade_pnls if p > 0)
    gross_loss = abs(sum(p for p in trade_pnls if p < 0))
    if gross_loss == 0:
        return float(gross_profit) if gross_profit > 0 else 0.0
    return float(gross_profit / gross_loss)


def all_metrics(equity: list[float], trade_pnls: list[float]) -> dict[str, float]:
    if not equity:
        return {
            "return": 0.0,
            "max_drawdown": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
        }

    returns = np.diff(np.array(equity)) / np.array(equity[:-1]) if len(equity) > 1 else np.array([], dtype=float)
    total_return = float((equity[-1] / equity[0]) - 1.0) if equity[0] > 0 else 0.0
    return {
        "return": total_return,
        "total_return": total_return,
        "max_drawdown": max_drawdown(equity),
        "sharpe": sharpe_ratio(returns),
        "sharpe_ratio": sharpe_ratio(returns),
        "sortino": sortino_ratio(returns),
        "sortino_ratio": sortino_ratio(returns),
        "win_rate": win_rate(trade_pnls),
        "profit_factor": profit_factor(trade_pnls),
    }

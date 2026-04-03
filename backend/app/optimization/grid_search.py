from __future__ import annotations

import itertools
from dataclasses import dataclass

import pandas as pd

from app.engine.backtester import BacktestConfig, EventDrivenBacktester


@dataclass(slots=True)
class GridSearchResult:
    best_params: dict[str, float | int]
    best_score: float
    leaderboard: list[dict[str, float | int]]


def run_grid_search(
    frame: pd.DataFrame,
    strategy_name: str,
    param_grid: dict[str, list[float | int]],
    objective: str = "sharpe",
) -> GridSearchResult:
    keys = list(param_grid.keys())
    values_product = itertools.product(*(param_grid[k] for k in keys))

    bt = EventDrivenBacktester()
    leaderboard: list[dict[str, float | int]] = []

    best_params: dict[str, float | int] = {}
    best_score = float("-inf")

    for combo in values_product:
        params = {k: v for k, v in zip(keys, combo, strict=False)}
        res = bt.run(frame, BacktestConfig(strategy_name=strategy_name, strategy_params=params))
        score = float(res.metrics.get(objective, 0.0))

        entry = {**params, "score": score}
        leaderboard.append(entry)

        if score > best_score:
            best_score = score
            best_params = params

    leaderboard.sort(key=lambda x: float(x["score"]), reverse=True)
    return GridSearchResult(best_params=best_params, best_score=best_score, leaderboard=leaderboard[:30])

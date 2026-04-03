from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.data.strategy_store import list_strategies, load_strategy, save_strategy
from app.data.yahoo_data import fetch_ohlcv
from app.engine.backtester import BacktestConfig, EventDrivenBacktester
from app.engine.indicators import bollinger_bands, ma, macd, rsi
from app.engine.strategy_builder import Condition, build_signal
from app.optimization.genetic import GeneSpec, run_genetic_optimization
from app.optimization.grid_search import run_grid_search

from .schemas import (
    BacktestRequest,
    GeneticRequest,
    GridSearchRequest,
    HealthResponse,
    SaveStrategyRequest,
    StrategyBuilderRequest,
)

router = APIRouter()


def _serialize_backtest(result):
    return {
        "strategy": result.strategy_name,
        "params": result.params,
        "timestamps": result.timestamps,
        "equity_curve": result.equity_curve,
        "drawdown_curve": result.drawdown_curve,
        "drawdown": result.drawdown_curve,
        "buy_hold_equity": result.buy_hold_equity,
        "trades": result.trades,
        "metrics": result.metrics,
        "indicators": result.indicators,
    }


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/api/backtest")
def run_backtest(payload: BacktestRequest):
    frame = fetch_ohlcv(payload.symbol, payload.period, payload.interval, use_cache=True)
    bt = EventDrivenBacktester()
    result = bt.run(
        frame,
        BacktestConfig(
            strategy_name=payload.strategy,
            strategy_params=payload.params,
            initial_cash=payload.initial_cash,
            transaction_cost_bps=payload.transaction_cost_bps,
            slippage_bps=payload.slippage_bps,
        ),
    )

    serialized = _serialize_backtest(result)

    return {
        "symbol": payload.symbol.upper(),
        "candles": {
            "dates": [ts.isoformat() for ts in frame["Datetime"]],
            "open": [float(v) for v in frame["Open"]],
            "high": [float(v) for v in frame["High"]],
            "low": [float(v) for v in frame["Low"]],
            "close": [float(v) for v in frame["Close"]],
            "volume": [float(v) for v in frame["Volume"]],
        },
        "result": serialized,
        "equity_curve": serialized["equity_curve"],
        "drawdown": serialized["drawdown"],
        "trades": serialized["trades"],
        "metrics": serialized["metrics"],
        "buy_hold_equity": serialized["buy_hold_equity"],
    }


@router.post("/api/optimize/grid")
def optimize_grid(payload: GridSearchRequest):
    frame = fetch_ohlcv(payload.symbol, payload.period, payload.interval, use_cache=True)
    result = run_grid_search(frame, payload.strategy, payload.param_grid, objective=payload.objective)
    return {
        "best_params": result.best_params,
        "best_score": result.best_score,
        "leaderboard": result.leaderboard,
    }


@router.post("/api/optimize/genetic")
def optimize_genetic(payload: GeneticRequest):
    frame = fetch_ohlcv(payload.symbol, payload.period, payload.interval, use_cache=True)
    gene_space = {
        k: GeneSpec(min_value=v.min_value, max_value=v.max_value, is_int=v.is_int)
        for k, v in payload.gene_space.items()
    }

    result = run_genetic_optimization(
        frame,
        strategy_name=payload.strategy,
        gene_space=gene_space,
        objective=payload.objective,
        population_size=payload.population_size,
        generations=payload.generations,
        mutation_rate=payload.mutation_rate,
        seed=payload.seed,
    )

    return {
        "best_params": result.best_params,
        "best_score": result.best_score,
        "generations": result.generations,
    }


@router.post("/api/strategy-builder/run")
def strategy_builder_run(payload: StrategyBuilderRequest):
    frame = fetch_ohlcv(payload.symbol, payload.period, payload.interval, use_cache=True).set_index("Datetime")

    indicators = frame[["Close"]].copy()
    close = frame["Close"]

    if "ma_short" in payload.indicators:
        indicators["ma_short"] = ma(close, int(payload.indicators["ma_short"]))
    if "ma_long" in payload.indicators:
        indicators["ma_long"] = ma(close, int(payload.indicators["ma_long"]))
    if "rsi" in payload.indicators:
        indicators["rsi"] = rsi(close, int(payload.indicators["rsi"]))
    if "macd" in payload.indicators:
        m = macd(close)
        for col in m.columns:
            indicators[col] = m[col]
    if "bollinger" in payload.indicators:
        b = bollinger_bands(close)
        for col in b.columns:
            indicators[col] = b[col]

    buy_conditions = [Condition(left=c.left, operator=c.operator, right=c.right) for c in payload.buy_conditions]
    sell_conditions = [Condition(left=c.left, operator=c.operator, right=c.right) for c in payload.sell_conditions]

    signal = build_signal(indicators.fillna(method="ffill").fillna(method="bfill"), buy_conditions, sell_conditions)

    bt = EventDrivenBacktester()
    temp = frame.reset_index()
    temp["Close"] = frame["Close"].values

    from app.engine.strategies import STRATEGY_REGISTRY, StrategyOutput

    class BuilderStrategy:
        name = "builder"

        def generate(self, _frame, _params):
            return StrategyOutput(signal=signal, indicators=indicators)

    STRATEGY_REGISTRY["builder"] = BuilderStrategy()
    result = bt.run(temp, BacktestConfig(strategy_name="builder", strategy_params={}))
    return {"result": _serialize_backtest(result)}


@router.post("/api/strategies/save")
def save_strategy_endpoint(payload: SaveStrategyRequest):
    save_strategy(payload.name, payload.payload)
    return {"saved": True, "name": payload.name}


@router.get("/api/strategies")
def list_strategies_endpoint():
    return {"strategies": list_strategies()}


@router.get("/api/strategies/{name}")
def load_strategy_endpoint(name: str):
    try:
        return {"name": name, "payload": load_strategy(name)}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Strategy '{name}' not found") from exc


@router.post("/api/export")
def export_result(payload: dict):
    return payload

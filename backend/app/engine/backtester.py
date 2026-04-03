from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from app.core.models import BacktestResult

from .metrics import all_metrics, max_drawdown
from .portfolio import Portfolio, PortfolioConfig
from .strategies import STRATEGY_REGISTRY

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BacktestConfig:
    strategy_name: str
    strategy_params: dict[str, float | int]
    initial_cash: float = 10000.0
    transaction_cost_bps: float = 10.0
    slippage_bps: float = 5.0


class EventDrivenBacktester:
    def run(self, frame: pd.DataFrame, config: BacktestConfig) -> BacktestResult:
        strategy = STRATEGY_REGISTRY.get(config.strategy_name)
        if strategy is None:
            raise ValueError(f"Unknown strategy: {config.strategy_name}")

        indexed = frame.set_index("Datetime").copy()
        strategy_out = strategy.generate(indexed, config.strategy_params)

        buy_signals = int((strategy_out.signal == 1).sum())
        sell_signals = int((strategy_out.signal == -1).sum())
        logger.info("Signal counts for %s: buy=%s sell=%s", config.strategy_name, buy_signals, sell_signals)

        portfolio = Portfolio(
            PortfolioConfig(
                initial_cash=config.initial_cash,
                transaction_cost_bps=config.transaction_cost_bps,
                slippage_bps=config.slippage_bps,
            )
        )

        equity_curve: list[float] = []
        drawdown_curve: list[float] = []
        buy_hold_equity: list[float] = []
        trades: list[dict[str, float | str]] = []
        trade_pnls: list[float] = []
        timestamps: list[str] = []

        first_price = float(indexed.iloc[0]["Close"])
        buy_hold_shares = config.initial_cash / first_price if first_price > 0 else 0.0

        for ts, row in indexed.iterrows():
            price = float(row["Close"])
            signal = int(strategy_out.signal.loc[ts])

            trade = portfolio.execute_signal(ts, signal, price)
            if trade is not None:
                trades.append(
                    {
                        "timestamp": trade.timestamp.isoformat(),
                        "side": trade.side,
                        "quantity": float(trade.quantity),
                        "price": float(trade.price),
                        "fee": float(trade.fee),
                        "slippage_cost": float(trade.slippage_cost),
                        "pnl": float(trade.pnl),
                    }
                )
                if trade.side == "sell":
                    trade_pnls.append(trade.pnl)

            portfolio.mark_price(price)
            equity = portfolio.state.equity
            equity_curve.append(float(equity))
            timestamps.append(ts.isoformat())
            drawdown_curve.append(max_drawdown(equity_curve))
            buy_hold_equity.append(float(buy_hold_shares * price))

        if portfolio.state.position == 1:
            final_ts = indexed.index[-1]
            final_price = float(indexed.iloc[-1]["Close"])
            close_trade = portfolio.execute_signal(final_ts, -1, final_price)
            if close_trade is not None:
                trades.append(
                    {
                        "timestamp": close_trade.timestamp.isoformat(),
                        "side": close_trade.side,
                        "quantity": float(close_trade.quantity),
                        "price": float(close_trade.price),
                        "fee": float(close_trade.fee),
                        "slippage_cost": float(close_trade.slippage_cost),
                        "pnl": float(close_trade.pnl),
                    }
                )
                trade_pnls.append(close_trade.pnl)
                equity_curve[-1] = float(portfolio.state.equity)
                drawdown_curve[-1] = max_drawdown(equity_curve)

        metrics = all_metrics(equity_curve, trade_pnls)
        logger.info(
            "Executed trades for %s: total=%s buys=%s sells=%s",
            config.strategy_name,
            len(trades),
            len([t for t in trades if t["side"] == "buy"]),
            len([t for t in trades if t["side"] == "sell"]),
        )

        indicators_payload: dict[str, list[float | None]] = {}
        for col in strategy_out.indicators.columns:
            indicators_payload[col] = [None if pd.isna(v) else float(v) for v in strategy_out.indicators[col].tolist()]

        return BacktestResult(
            strategy_name=config.strategy_name,
            params=config.strategy_params,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve,
            buy_hold_equity=buy_hold_equity,
            timestamps=timestamps,
            trades=trades,
            metrics=metrics,
            indicators=indicators_payload,
        )

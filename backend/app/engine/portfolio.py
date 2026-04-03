from __future__ import annotations

from dataclasses import dataclass

from app.core.models import PortfolioState, Trade


@dataclass(slots=True)
class PortfolioConfig:
    initial_cash: float = 10000.0
    trade_size_fraction: float = 1.0
    transaction_cost_bps: float = 10.0
    slippage_bps: float = 5.0


class Portfolio:
    def __init__(self, config: PortfolioConfig) -> None:
        self.config = config
        self.state = PortfolioState(
            cash=config.initial_cash,
            position=0,
            shares=0.0,
            entry_price=None,
            last_price=0.0,
        )

    def mark_price(self, price: float) -> None:
        self.state.last_price = price

    def execute_signal(self, timestamp, signal: int, price: float) -> Trade | None:
        self.mark_price(price)
        fee_rate = self.config.transaction_cost_bps / 10_000
        slip_rate = self.config.slippage_bps / 10_000

        if signal == 1 and self.state.position == 0:
            notional = self.state.cash * self.config.trade_size_fraction
            quantity = notional / price if price > 0 else 0.0
            if quantity <= 0:
                return None

            fee = notional * fee_rate
            slippage_cost = notional * slip_rate
            fill_price = price * (1 + slip_rate)
            total_cost = (quantity * fill_price) + fee

            if total_cost > self.state.cash:
                quantity = self.state.cash / (fill_price * (1 + fee_rate))
                total_cost = quantity * fill_price
                fee = total_cost * fee_rate
                total_cost += fee

            self.state.cash -= total_cost
            self.state.shares = quantity
            self.state.position = 1
            self.state.entry_price = fill_price

            return Trade(
                timestamp=timestamp,
                side="buy",
                quantity=quantity,
                price=fill_price,
                fee=fee,
                slippage_cost=slippage_cost,
                pnl=0.0,
            )

        if signal == -1 and self.state.position == 1:
            quantity = self.state.shares
            gross = quantity * price
            fee = gross * fee_rate
            slippage_cost = gross * slip_rate
            fill_price = price * (1 - slip_rate)
            proceeds = (quantity * fill_price) - fee
            self.state.cash += proceeds
            self.state.shares = 0.0
            self.state.position = 0

            entry = self.state.entry_price or fill_price
            buy_fee = (entry * quantity) * fee_rate
            pnl = ((fill_price - entry) * quantity) - fee - buy_fee
            self.state.entry_price = None

            return Trade(
                timestamp=timestamp,
                side="sell",
                quantity=quantity,
                price=fill_price,
                fee=fee,
                slippage_cost=slippage_cost,
                pnl=pnl,
            )

        return None

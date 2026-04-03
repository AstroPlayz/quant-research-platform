from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .indicators import bollinger_bands, ma, macd, rsi


@dataclass(slots=True)
class StrategyOutput:
    signal: pd.Series
    indicators: pd.DataFrame


class BaseStrategy:
    name: str = "base"

    def generate(self, frame: pd.DataFrame, params: dict[str, float | int]) -> StrategyOutput:
        raise NotImplementedError


class MACrossoverStrategy(BaseStrategy):
    name = "ma_crossover"

    def generate(self, frame: pd.DataFrame, params: dict[str, float | int]) -> StrategyOutput:
        close = frame["Close"]
        short_window = int(params.get("short_window", 20))
        long_window = int(params.get("long_window", 50))

        ma_short = ma(close, short_window)
        ma_long = ma(close, long_window)

        signal = pd.Series(0, index=close.index, dtype="int64")
        signal[ma_short > ma_long] = 1
        signal[ma_short < ma_long] = -1

        indicators = pd.DataFrame({"ma_short": ma_short, "ma_long": ma_long}, index=close.index)
        return StrategyOutput(signal=signal, indicators=indicators)


class RSIStrategy(BaseStrategy):
    name = "rsi"

    def generate(self, frame: pd.DataFrame, params: dict[str, float | int]) -> StrategyOutput:
        close = frame["Close"]
        period = int(params.get("rsi_period", 14))
        lower = float(params.get("rsi_lower", 30.0))
        upper = float(params.get("rsi_upper", 70.0))

        rsi_values = rsi(close, period)
        signal = pd.Series(0, index=close.index, dtype="int64")
        signal[rsi_values < lower] = 1
        signal[rsi_values > upper] = -1

        return StrategyOutput(signal=signal, indicators=pd.DataFrame({"rsi": rsi_values}, index=close.index))


class CombinedStrategy(BaseStrategy):
    name = "combined"

    def generate(self, frame: pd.DataFrame, params: dict[str, float | int]) -> StrategyOutput:
        close = frame["Close"]
        ma_strategy = MACrossoverStrategy().generate(frame, params)
        rsi_strategy = RSIStrategy().generate(frame, params)
        rsi_values = rsi_strategy.indicators["rsi"]

        macd_df = macd(
            close,
            fast=int(params.get("macd_fast", 12)),
            slow=int(params.get("macd_slow", 26)),
            signal=int(params.get("macd_signal", 9)),
        )
        bb_df = bollinger_bands(
            close,
            window=int(params.get("bb_window", 20)),
            num_std=float(params.get("bb_num_std", 2.0)),
        )

        buy_filter = float(params.get("combined_rsi_filter_buy", 70.0))
        sell_filter = float(params.get("combined_rsi_filter_sell", 30.0))
        rsi_buy_trigger = float(params.get("combined_rsi_buy", 35.0))
        rsi_sell_trigger = float(params.get("combined_rsi_sell", 65.0))

        ma_buy = (ma_strategy.signal > 0) & (rsi_values < buy_filter)
        ma_sell = (ma_strategy.signal < 0) & (rsi_values > sell_filter)
        rsi_buy = rsi_values < rsi_buy_trigger
        rsi_sell = rsi_values > rsi_sell_trigger
        macd_buy = macd_df["macd"] > macd_df["macd_signal"]
        macd_sell = macd_df["macd"] < macd_df["macd_signal"]

        buy_cond = ma_buy | rsi_buy | macd_buy
        sell_cond = ma_sell | rsi_sell | macd_sell

        signal = pd.Series(0, index=close.index, dtype="int64")
        signal[buy_cond] = 1
        signal[sell_cond] = -1

        indicators = pd.concat(
            [ma_strategy.indicators, rsi_strategy.indicators, macd_df, bb_df],
            axis=1,
        )
        return StrategyOutput(signal=signal, indicators=indicators)


STRATEGY_REGISTRY: dict[str, BaseStrategy] = {
    MACrossoverStrategy.name: MACrossoverStrategy(),
    RSIStrategy.name: RSIStrategy(),
    CombinedStrategy.name: CombinedStrategy(),
}

from __future__ import annotations

import pandas as pd
import yfinance as yf

from .cache import load_cached, save_cached


def fetch_ohlcv(symbol: str, period: str = "1y", interval: str = "1d", use_cache: bool = True) -> pd.DataFrame:
    if use_cache:
        cached = load_cached(symbol, period, interval)
        if cached is not None and not cached.empty:
            cached["Datetime"] = pd.to_datetime(cached["Datetime"])
            return cached

    ticker = yf.Ticker(symbol)
    frame = ticker.history(period=period, interval=interval, auto_adjust=False)
    if frame.empty:
        raise ValueError(f"No data found for symbol '{symbol}'")

    frame = frame.reset_index()
    if "Date" in frame.columns:
        frame.rename(columns={"Date": "Datetime"}, inplace=True)

    frame = frame[["Datetime", "Open", "High", "Low", "Close", "Volume"]].copy()
    frame["Datetime"] = pd.to_datetime(frame["Datetime"])

    if use_cache:
        save_cached(symbol, period, interval, frame)

    return frame

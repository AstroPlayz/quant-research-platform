from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_key(symbol: str, period: str, interval: str) -> str:
    raw = f"{symbol.upper()}::{period}::{interval}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def cache_path(symbol: str, period: str, interval: str) -> Path:
    return CACHE_DIR / f"{cache_key(symbol, period, interval)}.data.json"


def metadata_path(symbol: str, period: str, interval: str) -> Path:
    return CACHE_DIR / f"{cache_key(symbol, period, interval)}.meta.json"


def load_cached(symbol: str, period: str, interval: str) -> pd.DataFrame | None:
    p = cache_path(symbol, period, interval)
    if not p.exists():
        return None
    return pd.read_json(p, orient="records")


def save_cached(symbol: str, period: str, interval: str, frame: pd.DataFrame) -> None:
    frame.to_json(cache_path(symbol, period, interval), orient="records", date_format="iso")
    metadata_path(symbol, period, interval).write_text(
        json.dumps({"symbol": symbol.upper(), "period": period, "interval": interval}, indent=2),
        encoding="utf-8",
    )

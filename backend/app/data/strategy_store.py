from __future__ import annotations

import json
from pathlib import Path

STORE_PATH = Path(__file__).resolve().parents[2] / "strategies"
STORE_PATH.mkdir(parents=True, exist_ok=True)


def save_strategy(name: str, payload: dict) -> None:
    path = STORE_PATH / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_strategy(name: str) -> dict:
    path = STORE_PATH / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(name)
    return json.loads(path.read_text(encoding="utf-8"))


def list_strategies() -> list[str]:
    return sorted([p.stem for p in STORE_PATH.glob("*.json")])

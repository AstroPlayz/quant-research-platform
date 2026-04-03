from __future__ import annotations

import random
from dataclasses import dataclass

import pandas as pd

from app.engine.backtester import BacktestConfig, EventDrivenBacktester


@dataclass(slots=True)
class GeneSpec:
    min_value: float
    max_value: float
    is_int: bool = True


@dataclass(slots=True)
class GeneticResult:
    best_params: dict[str, float | int]
    best_score: float
    generations: list[dict[str, float | int]]


def _sample_gene(spec: GeneSpec) -> float | int:
    value = random.uniform(spec.min_value, spec.max_value)
    return int(round(value)) if spec.is_int else value


def run_genetic_optimization(
    frame: pd.DataFrame,
    strategy_name: str,
    gene_space: dict[str, GeneSpec],
    objective: str = "sharpe",
    population_size: int = 18,
    generations: int = 12,
    mutation_rate: float = 0.2,
    seed: int = 42,
) -> GeneticResult:
    random.seed(seed)
    bt = EventDrivenBacktester()

    def random_candidate() -> dict[str, float | int]:
        return {k: _sample_gene(v) for k, v in gene_space.items()}

    def fitness(params: dict[str, float | int]) -> float:
        result = bt.run(frame, BacktestConfig(strategy_name=strategy_name, strategy_params=params))
        return float(result.metrics.get(objective, 0.0))

    population = [random_candidate() for _ in range(population_size)]
    history: list[dict[str, float | int]] = []

    best_params: dict[str, float | int] = {}
    best_score = float("-inf")

    for gen in range(generations):
        scored = [(candidate, fitness(candidate)) for candidate in population]
        scored.sort(key=lambda x: x[1], reverse=True)

        top_candidate, top_score = scored[0]
        if top_score > best_score:
            best_score = top_score
            best_params = dict(top_candidate)

        history.append({"generation": gen, "score": float(top_score), **top_candidate})

        elites = [params for params, _ in scored[: max(2, population_size // 4)]]
        new_population = elites.copy()

        while len(new_population) < population_size:
            p1 = random.choice(elites)
            p2 = random.choice(elites)
            child: dict[str, float | int] = {}
            for key, spec in gene_space.items():
                child[key] = p1[key] if random.random() < 0.5 else p2[key]
                if random.random() < mutation_rate:
                    child[key] = _sample_gene(spec)
            new_population.append(child)

        population = new_population

    return GeneticResult(best_params=best_params, best_score=float(best_score), generations=history)

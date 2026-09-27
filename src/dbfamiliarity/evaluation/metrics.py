from __future__ import annotations

import math
from typing import Sequence


def accuracy(values: Sequence[bool]) -> float:
    if not values:
        return float("nan")
    return sum(bool(v) for v in values) / len(values)


def familiarization_efficiency(accuracy_gain: float, exploration_cost: float) -> float:
    if exploration_cost <= 0:
        return float("inf")
    return accuracy_gain / exploration_cost


def memory_tokens_estimate(text: str) -> int:
    """Deterministic early proxy; replace with tokenizer counts in model runs."""
    return math.ceil(len(text) / 4)

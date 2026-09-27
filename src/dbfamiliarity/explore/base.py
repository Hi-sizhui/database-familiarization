from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import sqlite3

from dbfamiliarity.memory.model import DatabaseMemory


@dataclass
class ExplorationContext:
    conn: sqlite3.Connection
    database_name: str
    budget: int
    actions_used: int = 0
    log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def remaining(self) -> int:
        return max(0, self.budget - self.actions_used)

    def spend(self, action: str, payload: dict[str, Any] | None = None) -> None:
        if self.remaining <= 0:
            raise RuntimeError("Exploration budget exhausted")
        self.actions_used += 1
        self.log.append({"step": self.actions_used, "action": action, "payload": payload or {}})


class Explorer(ABC):
    @abstractmethod
    def explore(self, ctx: ExplorationContext) -> DatabaseMemory:
        raise NotImplementedError

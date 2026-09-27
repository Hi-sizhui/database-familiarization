from __future__ import annotations

import hashlib
import json
import math
import random
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ColumnProfile:
    table: str
    name: str
    dtype: str
    notnull: bool
    primary_key: bool
    foreign_key: bool
    null_rate: float | None = None
    distinct_count: int | None = None
    sample_values: tuple[str, ...] = ()
    min_value: float | None = None
    max_value: float | None = None
    mean_value: float | None = None
    role: str | None = None


@dataclass(frozen=True)
class JoinProfile:
    left_table: str
    left_column: str
    right_table: str
    right_column: str
    left_distinct: int
    right_distinct: int
    matched_distinct: int
    match_rate_left: float
    example_keys: tuple[str, ...] = ()

    @property
    def key(self) -> str:
        return f"{self.left_table}.{self.left_column}->{self.right_table}.{self.right_column}"


@dataclass
class DatabaseMemory:
    db_name: str
    structural: dict[str, Any] = field(default_factory=dict)
    empirical: dict[str, ColumnProfile] = field(default_factory=dict)
    relations: dict[str, JoinProfile] = field(default_factory=dict)
    actions: list[dict[str, Any]] = field(default_factory=list)
    frozen: bool = False

    def add_column(self, p: ColumnProfile) -> None:
        self.empirical[f"{p.table}.{p.name}"] = p

    def add_join(self, p: JoinProfile) -> None:
        self.relations[p.key] = p

    def add_action(self, action: dict[str, Any]) -> None:
        self.actions.append(action)

    def freeze(self) -> "DatabaseMemory":
        self.frozen = True
        return self

    def has_column_fact(self, table: str, column: str, fact: str = "profile") -> bool:
        p = self.empirical.get(f"{table}.{column}")
        if p is None:
            return False
        if fact == "sample":
            return bool(p.sample_values)
        if fact == "stats":
            return p.distinct_count is not None and p.null_rate is not None
        if fact == "role":
            return bool(p.role)
        return True

    def has_join(self, left_table: str, left_column: str, right_table: str, right_column: str) -> bool:
        keys = {
            f"{left_table}.{left_column}->{right_table}.{right_column}",
            f"{right_table}.{right_column}->{left_table}.{left_column}",
        }
        return any(k in self.relations for k in keys)

    def fact_count(self) -> int:
        return len(self.structural.get("tables", {})) + len(self.empirical) + len(self.relations)

    def to_json(self, path: str | Path) -> None:
        payload = {
            "db_name": self.db_name,
            "structural": self.structural,
            "empirical": {k: asdict(v) for k, v in self.empirical.items()},
            "relations": {k: asdict(v) for k, v in self.relations.items()},
            "actions": self.actions,
            "frozen": self.frozen,
        }
        Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> "DatabaseMemory":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        mem = cls(payload["db_name"], payload.get("structural", {}))
        mem.empirical = {
            k: ColumnProfile(**{**v, "sample_values": tuple(v.get("sample_values", ()))})
            for k, v in payload.get("empirical", {}).items()
        }
        mem.relations = {
            k: JoinProfile(**{**v, "example_keys": tuple(v.get("example_keys", ()))})
            for k, v in payload.get("relations", {}).items()
        }
        mem.actions = payload.get("actions", [])
        mem.frozen = payload.get("frozen", False)
        return mem


class SQLiteProfiler:
    """Deterministic preflight plus on-demand database probes."""

    def __init__(self, db_path: str | Path, sample_limit: int = 5) -> None:
        self.db_path = str(db_path)
        self.sample_limit = sample_limit

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def preflight(self) -> DatabaseMemory:
        conn = self.connect()
        try:
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )]
            structural: dict[str, Any] = {"tables": {}, "foreign_keys": []}
            for table in tables:
                columns = []
                for row in conn.execute(f'PRAGMA table_info("{table}")'):
                    columns.append({
                        "name": row[1],
                        "dtype": row[2],
                        "notnull": bool(row[3]),
                        "default": row[4],
                        "primary_key": bool(row[5]),
                    })
                fks = []
                for row in conn.execute(f'PRAGMA foreign_key_list("{table}")'):
                    ref = {
                        "table": table,
                        "column": row[3],
                        "ref_table": row[2],
                        "ref_column": row[4],
                    }
                    fks.append(ref)
                    structural["foreign_keys"].append(ref)
                row_count = int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
                structural["tables"][table] = {
                    "columns": columns,
                    "foreign_keys": fks,
                    "row_count": row_count,
                }
            return DatabaseMemory(db_name=Path(self.db_path).stem, structural=structural)
        finally:
            conn.close()

    def profile_column(self, table: str, column: str) -> ColumnProfile:
        mem = self.preflight()
        meta = mem.structural["tables"][table]
        col_meta = next(c for c in meta["columns"] if c["name"] == column)
        conn = self.connect()
        try:
            total = int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
            nulls = int(conn.execute(
                f'SELECT COUNT(*) FROM "{table}" WHERE "{column}" IS NULL'
            ).fetchone()[0])
            distinct = int(conn.execute(
                f'SELECT COUNT(DISTINCT "{column}") FROM "{table}"'
            ).fetchone()[0])
            rows = conn.execute(
                f'SELECT "{column}" FROM "{table}" '
                f'WHERE "{column}" IS NOT NULL ORDER BY "{column}" ASC LIMIT ?',
                (self.sample_limit,),
            ).fetchall()
            samples = tuple(str(r[0]) for r in rows)
            low = high = mean = None
            dtype = (col_meta["dtype"] or "").upper()
            if any(t in dtype for t in ("INT", "REAL", "NUM", "DEC", "DOUBLE", "FLOAT")):
                stats = conn.execute(
                    f'SELECT MIN("{column}"), MAX("{column}"), AVG("{column}") FROM "{table}"'
                ).fetchone()
                low, high, mean = stats[0], stats[1], stats[2]
            role = self._infer_role(table, column, col_meta["primary_key"])
            fk = any(f["column"] == column for f in meta["foreign_keys"])
            return ColumnProfile(
                table=table,
                name=column,
                dtype=col_meta["dtype"],
                notnull=col_meta["notnull"],
                primary_key=col_meta["primary_key"],
                foreign_key=fk,
                null_rate=(nulls / total) if total else 0.0,
                distinct_count=distinct,
                sample_values=samples,
                min_value=low,
                max_value=high,
                mean_value=mean,
                role=role,
            )
        finally:
            conn.close()

    def profile_join(self, left_table: str, left_column: str, right_table: str, right_column: str) -> JoinProfile:
        conn = self.connect()
        try:
            left_distinct = int(conn.execute(
                f'SELECT COUNT(DISTINCT "{left_column}") FROM "{left_table}" WHERE "{left_column}" IS NOT NULL'
            ).fetchone()[0])
            right_distinct = int(conn.execute(
                f'SELECT COUNT(DISTINCT "{right_column}") FROM "{right_table}" WHERE "{right_column}" IS NOT NULL'
            ).fetchone()[0])
            matched_distinct = int(conn.execute(
                f'''SELECT COUNT(DISTINCT l."{left_column}")
                    FROM "{left_table}" l
                    INNER JOIN "{right_table}" r
                    ON l."{left_column}" = r."{right_column}"
                    WHERE l."{left_column}" IS NOT NULL'''
            ).fetchone()[0])
            rows = conn.execute(
                f'''SELECT DISTINCT l."{left_column}"
                    FROM "{left_table}" l
                    INNER JOIN "{right_table}" r
                    ON l."{left_column}" = r."{right_column}"
                    WHERE l."{left_column}" IS NOT NULL
                    ORDER BY l."{left_column}" ASC
                    LIMIT ?''',
                (self.sample_limit,),
            ).fetchall()
            examples = tuple(str(r[0]) for r in rows)
            return JoinProfile(
                left_table, left_column, right_table, right_column,
                left_distinct, right_distinct, matched_distinct,
                (matched_distinct / left_distinct) if left_distinct else 0.0,
                examples,
            )
        finally:
            conn.close()

    @staticmethod
    def _infer_role(table: str, column: str, primary_key: bool) -> str:
        name = f"{table} {column}".lower()
        if primary_key or name.endswith(" id"):
            return "identifier"
        if any(x in name for x in ("date", "time")):
            return "temporal"
        if any(x in name for x in ("price", "cost", "amount", "total", "salary")):
            return "measure"
        if any(x in name for x in ("name", "title", "description", "address", "city", "country")):
            return "attribute"
        return "unknown"


def structural_signature(structural: dict[str, Any]) -> str:
    raw = json.dumps({
        "tables": structural.get("tables", {}),
        "foreign_keys": structural.get("foreign_keys", []),
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def detect_drift(memory: DatabaseMemory, profiler: SQLiteProfiler) -> dict[str, Any]:
    fresh = profiler.preflight()
    structural_changed = structural_signature(memory.structural) != structural_signature(fresh.structural)
    empirical_changed = []
    for key, old in memory.empirical.items():
        table, column = key.split(".", 1)
        try:
            new = profiler.profile_column(table, column)
        except Exception:
            empirical_changed.append({"type": "missing_column", "table": table, "column": column})
            continue
        if (
            old.distinct_count != new.distinct_count
            or old.sample_values != new.sample_values
            or old.null_rate != new.null_rate
            or old.min_value != new.min_value
            or old.max_value != new.max_value
        ):
            empirical_changed.append({"type": "column_change", "table": table, "column": column})
    return {
        "structural_changed": structural_changed,
        "empirical_changed": empirical_changed,
        "fresh_structural": fresh.structural,
    }


def targeted_relearn(memory: DatabaseMemory, profiler: SQLiteProfiler, drift: dict[str, Any]) -> tuple[DatabaseMemory, int]:
    refreshed = 0
    for item in drift.get("empirical_changed", []):
        if item["type"] != "column_change":
            continue
        memory.add_column(profiler.profile_column(item["table"], item["column"]))
        refreshed += 1
    if drift.get("structural_changed"):
        fresh = profiler.preflight()
        for fk in fresh.structural["foreign_keys"]:
            memory.add_join(profiler.profile_join(
                fk["table"], fk["column"], fk["ref_table"], fk["ref_column"]
            ))
            refreshed += 1
        memory.structural = fresh.structural
    return memory, refreshed


@dataclass(frozen=True)
class ProbeAction:
    kind: str
    target: tuple[str, ...]
    cost: float = 1.0

    @property
    def id(self) -> str:
        return self.kind + ":" + ".".join(self.target)


class Familiarizer:
    """Budgeted explorer with random, fixed-order and adaptive policies."""

    def __init__(self, profiler: SQLiteProfiler, policy: str = "adaptive", seed: int = 7) -> None:
        self.profiler = profiler
        self.policy = policy
        self.random = random.Random(seed)

    def candidate_actions(self, memory: DatabaseMemory) -> list[ProbeAction]:
        actions: list[ProbeAction] = []
        for table, meta in memory.structural["tables"].items():
            for c in meta["columns"]:
                if f"{table}.{c['name']}" not in memory.empirical:
                    actions.append(ProbeAction("column_profile", (table, c["name"]), 1.0))
            for fk in meta["foreign_keys"]:
                join = (table, fk["column"], fk["ref_table"], fk["ref_column"])
                if not memory.has_join(*join):
                    actions.append(ProbeAction("join_probe", join, 1.4))
        return actions

    def run(self, budget: int, memory: DatabaseMemory | None = None) -> DatabaseMemory:
        mem = memory or self.profiler.preflight()
        for step in range(budget):
            candidates = self.candidate_actions(mem)
            if not candidates:
                break
            action = self._select(candidates, mem)
            self._execute(action, mem)
            mem.add_action({"step": step + 1, "action": action.id, "policy": self.policy})
        return mem

    def _select(self, candidates: list[ProbeAction], memory: DatabaseMemory) -> ProbeAction:
        if self.policy == "random":
            return self.random.choice(candidates)
        if self.policy == "round_robin":
            return candidates[0]
        scored = [(self._utility(a, memory), a) for a in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def _utility(self, action: ProbeAction, memory: DatabaseMemory) -> float:
        executed = [a.get("action", "") for a in memory.actions]
        column_done = sum(1 for x in executed if x.startswith("column_profile:"))
        join_done = sum(1 for x in executed if x.startswith("join_probe:"))
        family_balance = max(-4, min(4, column_done - join_done))

        if action.kind == "join_probe":
            table = action.target[0]
            degree = sum(1 for fk in memory.structural["foreign_keys"] if fk["table"] == table)
            row_count = memory.structural["tables"][table]["row_count"]
            diversity_boost = 1.0 + 0.18 * max(0, family_balance)
            return (
                1.65 + min(degree, 3) * 0.28 + math.log1p(row_count) * 0.03
            ) * diversity_boost / action.cost

        table, column = action.target
        meta = memory.structural["tables"][table]
        centrality = sum(1 for fk in memory.structural["foreign_keys"] if fk["ref_table"] == table)
        name = column.lower()
        ambiguity = 1.55 if any(x in name for x in ("name", "title", "description", "country", "city")) else 1.0
        centrality_bonus = 1.0 + 0.18 * min(centrality, 4)
        row_bonus = 1.0 + min(math.log1p(meta["row_count"]) / 25.0, 0.4)
        diversity_boost = 1.0 + 0.18 * max(0, -family_balance)
        return (2.0 * ambiguity * centrality_bonus * row_bonus) * diversity_boost / action.cost

    def _execute(self, action: ProbeAction, memory: DatabaseMemory) -> None:
        if action.kind == "column_profile":
            memory.add_column(self.profiler.profile_column(*action.target))
        elif action.kind == "join_probe":
            memory.add_join(self.profiler.profile_join(*action.target))
        else:
            raise ValueError(action.kind)

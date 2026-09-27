from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from dbfamiliarity.explore.base import ExplorationContext
from dbfamiliarity.explore.heuristic import BudgetedHeuristicExplorer
from dbfamiliarity.evaluation.metrics import memory_tokens_estimate

DB = Path(__file__).with_name("tourism_demo.db")
OUT = Path(__file__).with_name("database_memory.json")


def main() -> None:
    if not DB.exists():
        raise SystemExit("Run build_db.py first")
    conn = sqlite3.connect(DB)
    explorer = BudgetedHeuristicExplorer(sample_rows_per_table=2)
    ctx = ExplorationContext(conn=conn, database_name="tourism_demo", budget=10)
    memory = explorer.explore(ctx)
    OUT.write_text(memory.to_json(), encoding="utf-8")

    print("=== Database Familiarization Demo ===")
    print(f"Exploration budget: {ctx.budget}")
    print(f"Actions used:       {ctx.actions_used}")
    print(f"Tables learned:     {[t.name for t in memory.tables]}")
    print(f"Memory tokens est.:  {memory_tokens_estimate(memory.to_json())}")
    print("
--- Learned memory ---")
    print(json.dumps(memory.to_dict(), ensure_ascii=False, indent=2))
    conn.close()
    print(f"
Saved frozen memory to: {OUT}")


if __name__ == "__main__":
    main()

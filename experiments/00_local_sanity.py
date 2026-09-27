from __future__ import annotations

import sqlite3
from pathlib import Path

from dbfamiliarity.explore.base import ExplorationContext
from dbfamiliarity.explore.heuristic import BudgetedHeuristicExplorer

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "examples" / "tourism_demo" / "tourism_demo.db"


def main() -> None:
    conn = sqlite3.connect(DB)
    for budget in (4, 7, 10):
        ctx = ExplorationContext(conn=conn, database_name="tourism_demo", budget=budget)
        memory = BudgetedHeuristicExplorer(sample_rows_per_table=1).explore(ctx)
        print({"budget": budget, "actions": ctx.actions_used, "tables_learned": [t.name for t in memory.tables]})
    conn.close()


if __name__ == "__main__":
    main()

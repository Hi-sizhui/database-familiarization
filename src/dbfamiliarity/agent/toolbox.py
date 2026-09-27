from __future__ import annotations

import sqlite3
from typing import Any

from dbfamiliarity.db.introspect import inspect_table, list_tables, sample_rows


class DatabaseToolbox:
    """Read-only database tools exposed to an exploration policy."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list_tables(self) -> dict[str, Any]:
        return {"tables": list_tables(self.conn)}

    def inspect_table(self, table: str) -> dict[str, Any]:
        return inspect_table(self.conn, table)

    def sample_rows(self, table: str, limit: int = 5) -> dict[str, Any]:
        return {"table": table, "rows": sample_rows(self.conn, table, limit)}

    def run_query(self, sql: str, limit: int = 20) -> dict[str, Any]:
        if not sql.strip().lower().startswith("select"):
            raise ValueError("Only SELECT statements are allowed")
        cur = self.conn.execute(sql)
        rows = cur.fetchmany(limit)
        return {"columns": [d[0] for d in cur.description or []], "rows": [list(r) for r in rows]}

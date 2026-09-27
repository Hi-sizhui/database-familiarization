from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass
class ColumnInfo:
    table: str
    name: str
    type: str
    notnull: bool
    primary_key: bool


@dataclass
class ForeignKeyInfo:
    table: str
    column: str
    ref_table: str
    ref_column: str


def list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def inspect_table(conn: sqlite3.Connection, table: str) -> dict[str, Any]:
    safe = '"' + table.replace('"', '""') + '"'
    columns = conn.execute(f"PRAGMA table_info({safe})").fetchall()
    fks = conn.execute(f"PRAGMA foreign_key_list({safe})").fetchall()
    count = conn.execute(f"SELECT COUNT(*) FROM {safe}").fetchone()[0]
    return {
        "table": table,
        "row_count": count,
        "columns": [
            {
                "name": r[1],
                "type": r[2],
                "notnull": bool(r[3]),
                "primary_key": bool(r[5]),
            }
            for r in columns
        ],
        "foreign_keys": [
            {"column": r[3], "ref_table": r[2], "ref_column": r[4]}
            for r in fks
        ],
    }


def sample_rows(conn: sqlite3.Connection, table: str, limit: int = 5) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("limit must be >= 1")
    safe = '"' + table.replace('"', '""') + '"'
    rows = conn.execute(f"SELECT * FROM {safe} LIMIT ?", (limit,)).fetchall()
    columns = [r[1] for r in conn.execute(f"PRAGMA table_info({safe})").fetchall()]
    return [dict(zip(columns, row)) for row in rows]

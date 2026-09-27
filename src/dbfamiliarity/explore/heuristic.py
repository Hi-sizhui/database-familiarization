from __future__ import annotations

from dbfamiliarity.db.introspect import inspect_table, list_tables, sample_rows
from dbfamiliarity.explore.base import ExplorationContext, Explorer
from dbfamiliarity.memory.model import DatabaseMemory, MemoryTable


class BudgetedHeuristicExplorer(Explorer):
    """Deterministic baseline for the research harness.

    This is intentionally not an LLM. It provides a reproducible lower-bound
    baseline and a stable representation for later LLM comparisons.
    """

    def __init__(self, sample_rows_per_table: int = 3):
        self.sample_rows_per_table = sample_rows_per_table

    def explore(self, ctx: ExplorationContext) -> DatabaseMemory:
        tables: list[MemoryTable] = []
        all_tables = list_tables(ctx.conn)
        ctx.spend("list_tables", {"n_tables": len(all_tables)})

        for table in all_tables:
            if ctx.remaining <= 0:
                break
            meta = inspect_table(ctx.conn, table)
            ctx.spend("inspect_table", {"table": table})

            rows = []
            if ctx.remaining > 0:
                rows = sample_rows(ctx.conn, table, self.sample_rows_per_table)
                ctx.spend("sample_rows", {"table": table, "limit": self.sample_rows_per_table})

            tables.append(
                MemoryTable(
                    name=meta["table"],
                    row_count=meta["row_count"],
                    columns=meta["columns"],
                    foreign_keys=meta["foreign_keys"],
                    sample_rows=rows,
                )
            )
        return DatabaseMemory(database_name=ctx.database_name, tables=tables, explored_actions=ctx.log)

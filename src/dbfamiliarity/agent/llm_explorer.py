from __future__ import annotations

import json

from dbfamiliarity.agent.prompt import make_prompt
from dbfamiliarity.agent.toolbox import DatabaseToolbox
from dbfamiliarity.explore.base import ExplorationContext, Explorer
from dbfamiliarity.llm.interface import LLMBackend
from dbfamiliarity.memory.model import DatabaseMemory, MemoryTable


class LLMDatabaseExplorer(Explorer):
    """Minimal agentic exploration loop for frontier-model experiments."""

    def __init__(self, backend: LLMBackend, max_steps: int | None = None):
        self.backend = backend
        self.max_steps = max_steps

    def explore(self, ctx: ExplorationContext) -> DatabaseMemory:
        tools = DatabaseToolbox(ctx.conn)
        memory: dict = {"tables": [], "facts": []}
        step_limit = self.max_steps or ctx.budget

        for _ in range(step_limit):
            if ctx.remaining <= 0:
                break
            raw = self.backend.complete(make_prompt(ctx.database_name, ctx.remaining, memory))
            try:
                decision = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Model did not return valid JSON: {raw}") from exc

            action = decision.get("action")
            args = decision.get("args") or {}
            if action == "finish":
                ctx.spend("finish", {"reason": decision.get("reason", "")})
                break
            if action == "list_tables":
                result = tools.list_tables()
            elif action == "inspect_table":
                result = tools.inspect_table(args["table"])
            elif action == "sample_rows":
                result = tools.sample_rows(args["table"], int(args.get("limit", 5)))
            elif action == "run_query":
                result = tools.run_query(args["sql"], int(args.get("limit", 20)))
            else:
                raise RuntimeError(f"Unsupported action from model: {action}")

            ctx.spend(action, {"args": args, "result": result, "reason": decision.get("reason", "")})
            memory["facts"].append({"action": action, "args": args, "result": result})
            if action == "inspect_table":
                existing = {t["table"] for t in memory["tables"]}
                if result["table"] not in existing:
                    memory["tables"].append(result)

        learned_tables = [
            MemoryTable(name=t["table"], row_count=t["row_count"],
                        columns=t["columns"], foreign_keys=t["foreign_keys"])
            for t in memory["tables"]
        ]
        return DatabaseMemory(database_name=ctx.database_name,
                              tables=learned_tables, explored_actions=ctx.log)

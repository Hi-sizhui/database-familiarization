# Database Familiarization

> **Can an AI agent actually learn a database?**

An open research project for **autonomous database familiarization**: an AI agent receives a database it has never seen, decides what to inspect, builds a compact persistent database memory, and is then evaluated on unseen questions **without receiving the full schema again**.

## Research question

Recent 2026 work already demonstrates autonomous schema exploration, agentic database exploration, database-specific knowledge bases, and reusable semantic memory. This project does **not** claim autonomous exploration itself as novel.

The research question is:

> **How should database familiarization be measured, budgeted, compressed, reused, and updated over time?**

We study four properties:

1. **Familiarization efficiency** — how much downstream capability is gained per unit exploration cost?
2. **Knowledge sufficiency** — which database knowledge is actually necessary?
3. **Persistent reuse** — can frozen database memory support unseen questions without re-reading the database?
4. **Continual maintenance** — when schema or business semantics change, what must be relearned?

## Core lifecycle

```text
Unfamiliar Database
      |
      v
Autonomous Exploration
      |  (budgeted tool calls)
      v
Database Memory
      |  (compact + persistent)
      v
Memory Frozen
      |
      v
Unseen Query Evaluation
      |
      +-- accuracy
      +-- semantic grounding
      +-- exploration cost
      +-- memory size
      +-- robustness to drift
```

The repository is the executable research instrument for the accompanying paper.

## Research position in 2026

We explicitly build on and distinguish from current work including:

- **AutoLink (AAAI 2026):** autonomous schema exploration/expansion.
- **APEX-SQL (2026):** agentic exploration, data profiling and hypothesis verification.
- **SQLAgent (ACL 2026 Findings):** exploration followed by a database-specific knowledge base.
- **AgentSM (2026):** reusable semantic memory for Text-to-SQL.
- **2026 semantic-layer systems:** business semantics separated from physical SQL through intermediate representations.

Our target is the **learning lifecycle after exploration**: how much an agent has learned, how compactly that knowledge can be represented, how long it remains useful, and how efficiently it can be updated.

## Prototype

The current repository contains a lightweight local harness that can:

1. Create a small tourism-style SQLite database.
2. Introspect tables, columns, PK/FK structure and row counts.
3. Execute a budgeted exploration policy.
4. Build a compact JSON database memory.
5. Freeze that memory for later evaluation.

The baseline explorer is intentionally deterministic and dependency-light. The next stage is to plug current frontier LLMs into the same interface.

## Experimental roadmap

### Phase 0 — Instrumentation
Reproducible logging of every exploration action and memory update.

### Phase 1 — Frontier-model baselines
Connect current LLMs through a provider-neutral interface and reproduce recent exploration baselines.

### Phase 2 — Familiarization benchmark
Separate evaluation of:
- schema understanding;
- join-path understanding;
- data-distribution understanding;
- metric/business-semantic understanding;
- temporal validity;
- unseen-query performance.

### Phase 3 — Budgeted familiarization
Compare fixed-budget, adaptive-budget and query-driven exploration.

### Phase 4 — Persistent memory
Freeze the learned memory and remove direct schema access.

### Phase 5 — Continual learning
Inject schema drift and business-rule changes. Measure memory staleness and targeted relearning cost.

### Phase 6 — Real tourism-statistics environment
Run the protocol on the real domain environment after the public benchmark harness is stable.

## Reproducibility principles

- No hidden manual semantic layer in the core benchmark.
- All exploration actions are logged.
- Raw database access is separated from frozen-memory evaluation.
- Evaluation queries are partitioned before onboarding.
- No result is presented as an empirical finding until the corresponding experiment has been run.

## Status

**Prototype / research harness.**

The central next step is to connect a current LLM and run the first controlled familiarization curve.

## References to reproduce or compare against

- AutoLink, AAAI 2026.
- APEX-SQL, 2026.
- SQLAgent, Findings of ACL 2026.
- AgentSM, 2026.

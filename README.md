# Database Familiarization

> **Can an AI agent actually learn a database?**

This repository is the research and engineering companion for studying **autonomous database familiarization**.

The target is deliberately domain-general. The agent is given an unfamiliar database, chooses what to inspect, builds a compact database memory, and is then tested on unseen questions. Domain-specific optimization is a later phase; the initial benchmark is intended to expose general mechanisms.

## Research question

Current 2026 systems already demonstrate autonomous schema exploration, agentic database exploration, database-specific knowledge bases and reusable semantic memory. This project does **not** claim those capabilities as new.

We study a narrower question:

> **How much does an agent actually need to learn about an unfamiliar database, how should it spend its exploration budget, what knowledge should become persistent memory, and how should that memory be reused and updated?**

The lifecycle is:

```text
Unfamiliar Database
      |
      v
Autonomous Exploration
      |  (budgeted tool calls)
      v
Persistent Database Memory
      |
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
      +-- adaptation cost
```

## Why this is not a Text-to-SQL model repository

The database is the object being learned.

Text-to-SQL is only one downstream test of whether the learned database memory is useful.

The primary experimental variables are:

- exploration budget;
- exploration policy;
- knowledge types acquired;
- memory size and structure;
- memory reuse without raw-database access;
- relearning after database drift.

## 2026 research context

Relevant contemporary work includes:

- **AutoLink (AAAI 2026):** autonomous schema exploration/expansion.
- **APEX-SQL (2026):** agentic exploration, data profiling and hypothesis verification.
- **SQLAgent (ACL 2026 Findings):** exploration followed by a database-specific knowledge base.
- **AgentSM (2026):** reusable semantic memory for Text-to-SQL.
- **LiveSQLBench-Large-v1 (2026):** industrial-scale databases, very large schemas and Business Rule Drift.
- **BIRD-INTERACT (ICLR 2026 Oral):** interactive and agentic database tasks.

Our question starts **after** those capabilities: what does it mean, experimentally, for an agent to have become familiar with a database?

## Public benchmark sources

The project is designed around public, domain-diverse resources:

| Resource | Scale / character | Role |
|---|---|---|
| **BIRD Mini-Dev** | 500 high-quality examples, 11 databases | initial accuracy + memory experiments |
| **LiveSQLBench-Base-Lite-SQLite** | 18 databases, 270 tasks, local SQLite | local agent/exploration benchmark |
| **BIRD-INTERACT Mini / Lite** | interactive/agentic tasks | dynamic interaction stress test |
| **Spider 2.0-Lite** | 547 tasks across BigQuery/Snowflake/SQLite | enterprise-style complexity |
| **Spider 2.0-DBT** | 68 DuckDB/DBT tasks | repository-level/code-agent extension |
| **LiveSQLBench-Large-v1** | 18 industrial-scale databases, ~1K columns/database | high-complexity final evaluation |

LiveSQLBench-Large-v1 is especially relevant for the long-term benchmark because it reports about 18 industrial-scale databases, roughly 1K columns per database, and explicit Business Rule Drift. It is not required for the first local prototype.

## Included public database

A copy of **Chinook SQLite v1.4.5** is included under `data/public/chinook/` as a small, reproducible local smoke-test database. The upstream project is MIT licensed.

This database is only a local engineering test fixture. It is not intended to represent the final research benchmark.

## First reproducible run

Clone the repository, then:

```bash
PYTHONPATH=src python examples/chinook/run_demo.py
```

This will:

1. open the included database;
2. expose read-only database tools;
3. run a budgeted baseline explorer;
4. build a persistent JSON database memory;
5. print the actions taken, learned tables and memory size.

To run the local sanity tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" -v
```

## Frontier-model experiments

The repository includes an OpenAI-compatible backend adapter. Configure:

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=...
export OPENAI_MODEL=...
```

Then use the LLM exploration policy rather than the deterministic heuristic baseline.

The code intentionally keeps the provider interface small so current models can be swapped without changing the benchmark protocol.

## Benchmark acquisition

Large benchmarks are **not copied wholesale into Git history**. Instead, `benchmarks/registry.yaml` records the official source, license, expected artifacts and a reproducible download command.

This is deliberate: some current benchmarks are tens of gigabytes, use Git LFS/Xet, Docker images or gated evaluation files. The repository therefore keeps the experiment code and small public fixtures in Git, while the benchmark data is materialized into `data/external/` locally.

## Research experiments

The first experiment family is:

1. **Familiarization curve** — downstream capability as exploration budget increases.
2. **Knowledge ablation** — schema, PK/FK, samples, profiles, join paths and business semantics.
3. **Frozen-memory evaluation** — evaluate unseen questions after raw database access is removed.
4. **Memory compression** — compare full context against compact learned memory.
5. **Continual learning** — modify schema/business semantics and measure targeted vs full relearning cost.

## Repository layout

```text
database-familiarization/
├── README.md
├── LICENSE
├── pyproject.toml
├── benchmarks/
│   └── registry.yaml
├── configs/
├── data/
│   ├── public/
│   │   └── chinook/
│   └── external/          # downloaded locally, ignored by Git
├── docs/
├── examples/
│   └── chinook/
├── experiments/
├── scripts/
├── src/dbfamiliarity/
└── tests/
```

## Reproducibility rules

- No hidden manual semantic layer in the core familiarization benchmark.
- Exploration actions are logged.
- Evaluation queries are separated from onboarding.
- Frozen-memory tests cannot silently re-open the raw database.
- No empirical result is documented until the experiment has actually been run.
- Real or licensed organizational data must not be committed to the public repository.

## Status

**Research prototype — public benchmark harness and local smoke test.**

The next milestone is the first frontier-model familiarization curve on a current public benchmark.

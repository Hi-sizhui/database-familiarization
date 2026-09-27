# Database Familiarization

> **How much should an agent learn from an unfamiliar database before it starts answering questions?**

This repository is an executable research prototype for studying **budgeted database familiarization**.

## Important 2026 novelty check

The broad idea **"let an agent explore an unfamiliar database before generating SQL" is not new**. Current 2026 work already includes:

- **SQLAgent (ACL 2026 Findings)** — separates database exploration from query generation and constructs a database-specific knowledge base.
- **AutoLink (AAAI 2026)** — autonomous schema exploration/expansion for schema linking.
- **APEX-SQL (KDD 2026)** — agentic exploration, profiling and hypothesis verification.
- **AgentSM (2026)** — structured semantic memory that reuses prior Text-to-SQL trajectories.

Therefore this project does **not** claim autonomous exploration, database-specific memory, or agentic Text-to-SQL as its own invention.

The research target is narrower:

> **Given a finite onboarding budget, how should the agent choose what to learn, what knowledge should be persisted, how much capability survives after the raw database is removed from the loop, and how can the agent selectively relearn only what changed after database drift?**

The intended lifecycle is:

`profile -> active probe -> consolidate -> freeze -> reuse -> detect drift -> targeted relearn`


### Novelty audit (updated 2026-09-27)

The public literature check found four important neighboring lines of work:

| Work | What is already established | What it means for this project |
|---|---|---|
| SQLAgent, ACL Findings 2026 | autonomous pre-query exploration and a database-specific knowledge base | do not claim exploration-before-generation as new |
| AutoLink, AAAI 2026 | autonomous schema exploration/expansion | do not claim autonomous schema inspection as new |
| AgentSM, 2026 | reusable semantic memory for agentic Text-to-SQL | do not claim persistent database memory as new |
| *From Test-Time Scaling to Reusable Memory: Measuring Crystallization in Text-to-SQL*, Aug. 2026 | held-out same-database transfer from reusable memory is explicitly measured | do not claim frozen-memory transfer evaluation as new |

The remaining candidate gap is narrower: **query-blind, budgeted database onboarding as an explicit resource-allocation problem, coupled with change-aware selective re-familiarization after drift**. This is a research hypothesis rather than a proof of originality; publication novelty must be re-checked against the final submission date.

## Current executable method

The prototype implements four modules in `src/dbfamiliarity/core.py`:

1. **Database Profiler**  
   Extracts schema, row counts, PK/FK structure and candidate exploration actions.

2. **Utility-driven Explorer**  
   Chooses empirical column-profile probes and join probes using an information-value-per-cost heuristic. The policy is intentionally database-intrinsic: it does not inspect held-out query labels.

3. **Persistent Database Memory**  
   Stores structural facts, empirical column profiles, join evidence and an action log. Memory can be serialized as JSON.

4. **Freeze + drift hooks**  
   A frozen memory artifact can be reloaded without reopening the database. A conservative drift detector compares memorized empirical facts and schema signatures, and a targeted relearning function refreshes only implicated facts.

Controlled baselines are:
- `random`
- `round_robin`
- `adaptive`

## First local experiment

The environment used for the first execution is a small **Chinook-derived SQLite fixture** built only for engineering validation. It is not the paper benchmark.

Run:

```bash
python scripts/build_chinook_fixture.py
PYTHONPATH=src python examples_oracle.py
PYTHONPATH=src python experiments_drift.py
PYTHONPATH=src python -m unittest discover -s tests -v
```

The oracle experiment compares the three exploration policies at the same onboarding budget. The downstream solver is deliberately perfect and memory-grounded, so this first experiment isolates **whether the onboarding policy acquires reusable evidence efficiently**. This is a controlled method test, not a claim about LLM Text-to-SQL accuracy.

The drift experiment:
- builds a frozen memory;
- creates a controlled semantic change (renaming one genre);
- detects the changed memorized fact;
- refreshes only that fact;
- confirms the original onboarding action log remains frozen.

## Public database for the real benchmark

For the actual research benchmark, use the official **Chinook v1.4.5 SQLite release**:

- upstream repository: https://github.com/lerocha/chinook-database
- release asset: `Chinook_Sqlite.sqlite`

The upstream repository describes Chinook as a multi-table sample database for demos/testing and provides the SQLite file in release v1.4.5. Verify the upstream license file before redistributing any copy in a research repository.

For publishable experiments, this fixture should be replaced or supplemented with current benchmark suites such as **LiveSQLBench-Large-v1**, **BIRD-family / BIRD-INTERACT**, and **Spider 2.0**, because the small Chinook fixture cannot establish generality.

## Research hypotheses

**P1. Budget allocation.**  
At equal onboarding budget, an information-directed exploration policy should acquire more transferable database knowledge than random or fixed-order exploration.

**P2. Diminishing returns.**  
Downstream capability should increase with onboarding budget, with marginal gains eventually decreasing.

**P3. Future-utility memory selection.**  
Under the same memory budget, evidence selected using onboarding-time utility signals should yield better held-out transfer per byte/probe than naive retention policies. This is the part that must be distinguished from the 2026 crystallization study, which measures reuse of verified repair episodes.

**P4. Targeted continual familiarization.**  
After controlled schema or business-rule drift, a change-aware agent should recover the stale capability with fewer probes than full database re-familiarization, while keeping unaffected memory intact.

P1-P4 are hypotheses. The repository must not treat them as established findings until they are tested on independent benchmark data.

## What the final paper should contain

The intended paper is not a software/documentation paper. The final experimental study should include:

```baseline agents
   -> equal onboarding budgets
   -> frozen-memory evaluation
   -> multiple database families
   -> memory / policy ablations
   -> multiple LLM backbones
   -> drift + targeted relearning
   -> cost / accuracy / memory-size trade-offs
```

The central comparison is not "our framework vs. every Text-to-SQL system". It is:

> **same underlying agent + same downstream solver, with different database familiarization policies and memory states.**

That isolates the contribution of the familiarization mechanism.

## Reproducibility rule

No empirical result should be presented in the paper until it has been produced by the repository's experiment code on a benchmark that is separated from the exploratory onboarding process.

Domain-specific datasets can be used later for private adaptation, but the public benchmark contribution is deliberately domain-general.

# Research Protocol: Database Familiarization

## 1. Core question

Can an agent acquire a compact, persistent and reusable understanding of an unfamiliar relational database through autonomous exploration?

## 2. Experimental unit

One run consists of:

```text
database D
+ exploration budget B
+ exploration policy pi
+ memory builder M
-> frozen memory M_D
-> unseen query set Q
-> downstream evaluation
```

## 3. What counts as learning?

A run is considered a **familiarization run** only if:

1. the agent receives a new database;
2. it is allowed a bounded set of read-only exploration actions;
3. it produces a persistent memory artifact;
4. the raw database is removed from the model context for the frozen-memory evaluation;
5. the evaluation questions were not used to choose the exploration actions.

## 4. Main empirical propositions

**P1. Familiarization curve:** increasing exploration budget improves downstream performance with diminishing returns.

**P2. Knowledge composition:** different knowledge types have non-uniform marginal value; structural metadata is not sufficient for all queries.

**P3. Persistence:** compact frozen memory can retain a substantial fraction of the performance obtained when the agent can repeatedly inspect the raw database.

**P4. Relearning:** after controlled schema or business-semantic changes, targeted re-exploration can restore performance with less cost than full relearning.

These are propositions to test, not conclusions.

## 5. Experimental layers

### Layer A — Local smoke test

Included Chinook database. This only validates the software path.

### Layer B — Public benchmark evaluation

Primary starting point:
- BIRD Mini-Dev
- LiveSQLBench-Base-Lite-SQLite

Secondary:
- BIRD-INTERACT Mini/Lite
- Spider 2.0-Lite / DBT

High-complexity:
- LiveSQLBench-Large-v1

### Layer C — Ablation

Compare memory components:
- schema structure;
- PK/FK;
- row samples;
- data profiles;
- join-path hypotheses;
- domain/business semantics;
- historical query examples.

### Layer D — Continual learning

Inject:
- schema additions/removals;
- renamed or retyped fields;
- changed join relationships;
- changed business definitions.

Compare:
- no relearning;
- full relearning;
- targeted relearning.

## 6. Metrics

### Capability
- Execution Accuracy where gold SQL/test cases are available.
- Semantic / task success where an official evaluator is provided.
- Schema-linking accuracy when annotations support it.

### Learning efficiency
- exploration actions;
- tool-call count;
- model tokens;
- wall-clock time;
- API cost.

### Memory
- serialized bytes;
- tokenizer token count;
- number of stored facts;
- redundancy.

### Continual learning
- retained accuracy after drift;
- relearning actions;
- relearning latency;
- accuracy recovered per unit cost.

## 7. Experimental split

For every database:

- **onboarding-visible:** schema introspection and allowed database reads;
- **evaluation-hidden:** final questions and gold answers;
- **frozen-memory:** raw database access removed.

Public benchmark fields that are intentionally withheld by the benchmark creators remain withheld; the harness must not bypass those restrictions.

## 8. First paper scope

The first paper should not promise a universal database-learning algorithm.

The initial claim should be empirical:

> database familiarization can be defined and measured as a budgeted learning process, and persistent database memory can be evaluated separately from query-time exploration.

A stronger algorithmic contribution should only be introduced if the first experiments expose a reproducible bottleneck.

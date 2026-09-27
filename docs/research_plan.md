# Research Plan: Database Familiarization

## 1. Research question

**Can an AI agent acquire a compact, persistent, reusable understanding of an unfamiliar database through autonomous exploration, and how much exploration is enough?**

## 2. What current work already solves

Recent work has already demonstrated autonomous database exploration, database-specific knowledge bases, reusable semantic memory, and semantic-layer-mediated SQL generation.

Therefore, this project does **not** claim that an agent can inspect a database before generating SQL as its novelty.

## 3. Proposed research gap

We treat **database familiarization itself as the object of study** and measure:

1. **Efficiency:** downstream task gain per unit exploration budget.
2. **Sufficiency:** which knowledge types are needed for unseen queries.
3. **Persistence:** how well frozen memory supports later tasks without raw-schema access.
4. **Continual maintenance:** how performance changes after schema/business-rule drift and how much relearning is required.

## 4. Empirical propositions

**P1.** Increasing exploration budget improves downstream performance but eventually exhibits diminishing returns.

**P2.** Knowledge composition matters: structural metadata alone is insufficient for domain-heavy tasks, while targeted profiling and business-semantic knowledge provide non-uniform gains.

**P3.** A compact frozen memory can retain a substantial fraction of the downstream performance of repeated raw-database exploration under a fixed cost budget.

**P4.** After schema or business-rule drift, selective re-exploration of affected knowledge can reduce adaptation cost relative to rebuilding the entire memory.

These are empirical propositions, not findings.

## 5. Experimental ladder

### A — Cold start

Compare:
- schema only;
- schema + examples;
- autonomous exploration;
- autonomous exploration + persistent memory.

Metrics:
- execution accuracy;
- semantic accuracy;
- exploration calls;
- tokens/cost.

### B — Familiarization curve

Run multiple exploration budgets, for example 10 / 25 / 50 / 100 / 200 actions, and plot downstream performance against exploration cost.

### C — Knowledge ablation

Independently add:
- schema structure;
- PK/FK;
- data profiles;
- value examples;
- join-path hypotheses;
- metric/business semantics.

Measure marginal downstream gains.

### D — Persistent memory

Freeze the learned memory and remove direct database introspection. Evaluate on unseen query sets.

### E — Continual drift

Modify:
- columns;
- join relationships;
- metric definitions;
- versioned business rules.

Compare full relearning, no relearning, and targeted relearning.

## 6. Evaluation split

The onboarding phase must not see the final evaluation questions. We distinguish:

- exploration-visible metadata;
- exploration-visible sample access;
- unseen evaluation questions;
- post-drift evaluation questions.

The final evaluation must not silently reintroduce the complete raw schema after memory is frozen.

## 7. Engineering milestone

The repository should first reproduce the complete local lifecycle:

```text
create demo DB
  -> inspect
  -> explore under fixed budget
  -> write persistent memory
  -> freeze memory
  -> evaluate learned knowledge
  -> report cost + retained capability
```

Only after this harness is stable do we add frontier LLMs and real-domain data.

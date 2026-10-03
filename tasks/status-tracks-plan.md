# Implementation plan: `status-tracks`

**Ideal:** [../docs/architecture/status-tracks-ideal.md](../docs/architecture/status-tracks-ideal.md) ·
**Map:** [../docs/architecture/status-tracks-map.md](../docs/architecture/status-tracks-map.md) ·
**Locked rule:** [../docs/architecture/decisions/combat.md](../docs/architecture/decisions/combat.md)
row *Status tracks — combat and out-of-combat* ·
**Tasks:** [status-tracks-todo.md](status-tracks-todo.md) ·
**Ledger:** [status-tracks-ledger.jsonl](status-tracks-ledger.jsonl) ·
**Decision packet:** [../docs/research/status-tracks/owner-decision-packet.md](../docs/research/status-tracks/owner-decision-packet.md)

**Status:** plan written 2026-10-02. **Pending owner approval** — no task may start until the map is
approved. `K1` (the seventh-pool question) gates `track-catalogue` only.

## Overview

The premise this plan answers: *this game needs two status systems — combat and outside combat.*

It does not, and building one would violate the locked rule recorded the same day. `StatusRuntime`
is already both: it holds the 24 shipped combat statuses, and it already hosts out-of-combat
projections (`nerve.*`, `exhaustion.*`, `wound.*`). What is missing is not a mechanism. It is:

1. an **authoring path** for combat statuses that is honest about what a new id costs, and
2. a **drive** for out-of-combat projections — `NervePolicy.Sync` has no production caller, and
   `ExhaustionPolicy.Sync`'s single caller is in the lawn, not the delve.

So the work is small and mostly test-shaped. This plan is honest that it is small: it would be a
defect to inflate it into an engine.

## What is already true, verified 2026-10-02

Read against `gk-core/src`, not recalled:

- `StatusRuntime.Tick` has exactly **two** callers — `EffectBag.cs:858` and `BattleEngine.cs:456`.
- `NervePolicy.Sync` has **zero** production callers; `ExhaustionPolicy.Sync` has **one**
  (`LawnExhaustionLifecycle.cs:93`).
- `ActorHudResources.Meters` **does** have a producer (`ActorHudBuilder.cs:51-54`), but its
  `meterId` vocabulary is `ResourceIds`, so a status can never publish a ratio.
- A new status id costs **six files**, not one: registry, bootstrap, injected JSON,
  `SingleDeclarationTests`, `ResistanceEvaluatorTests` count, and **both** doc count lines.
- The delve has **no** virtual tick: every pool call site passes `atTick: 0`
  (`spec-delve-attrition.md:122-123`).

Each of these was checked directly; the claims that changed my plan are the first two.

## Architecture decisions (from the map; not re-litigated)

1. **One runtime, two drives.** No second bag, tick, catalog or clock. A track that cannot be
   expressed as a catalog row plus a `Sync` is a defect.
2. **The scalar is authoritative; the status is a projection.** Never the reverse.
3. **`Sync` writes on transition only** — idempotent by pre-reading the live instance.
4. **No clock out of combat.** Decay is counted in events; wall time is refused by spec and by
   `guard-clock-seam.py`.
5. **Pool or projection is decided per need, by "does anything spend it?"** — and a seventh pool is
   an owner ADR, not this program's call.
6. **Repo hard rules apply unchanged:** no hand-edited generated data; tunables published as
   `v{n+1}`; one ActorHub compose; SOLID; tests assert contracts, not populations.

## Dependency graph

```
ST0  track-contract (ST0.1–ST0.4)
 └─ ST1  combat-track-authoring (ST1.1–ST1.3)   ─┐
 └─ ST1  projection-host      (ST1.4–ST1.7)     ─┴─ ST2  track-catalogue (ST2.1–ST2.3)
                                                        ⛔ blocked on K1 (owner)
```

`ST1.1–ST1.3` and `ST1.4–ST1.7` are parallel-safe: one touches the catalog surface, the other a new
Core host, and neither imports the other.

## Verification

One entry point, per [AGENTS.md](../AGENTS.md):

```
python gk-core/scripts/verify-change.py --paths <repo-relative files> --session <id>
```

Docs-only tasks use `python scripts/audit-doc-citations.py` and
`python gk-core/scripts/audit-program-pipeline.py`.

Every task closes with evidence recorded in [status-tracks-ledger.jsonl](status-tracks-ledger.jsonl)
and a pointer from its todo entry. **A tick is a claim, not evidence.**
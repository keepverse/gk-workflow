# Implementation plan: `effect-pipeline`

**Map:** [../docs/architecture/effect-pipeline-map.md](../docs/architecture/effect-pipeline-map.md) ·
**Specs:** `docs/architecture/effect-pipeline/spec-*.md` (12) ·
**Tasks:** [effect-pipeline-todo.md](effect-pipeline-todo.md) ·
**Written by:** `backlog-clean-up` `orphan-plan-authoring` (BCU2.6).

**Relationship to `seed-to-concrete`.** `effect-pipeline-map.md:28` already names
`tasks/seed-to-concrete-plan.md`/`-todo.md` as this program's plan for **modules 1–10** — verified
live: `seed-to-concrete-todo.md` T3.1–T3.6, T5.1, T5.2, T5.7, T6.1, T6.2, T7.1, T7.2 each cite their
`ep N` module id and are all `[x]` done. **`effect-pipeline` is not the C1 orphan the first audit
pass read it as — it is 10/12 modules built, one program's worth of work hiding behind a different
program's plan file (trap 1: plan names ≠ literally-named `tasks/effect-pipeline-*.md` files).** The
real gap is exactly **modules 11–12** (`affix-power-class`, `affix-channel-weights`), added by owner
decision 2026-09-03 — after `seed-to-concrete-todo.md` was substantially written, and never folded
into it. This plan covers only those two.

## Overview

L0 (modules 11–12) partitions one affix pool into many, weighted by an LLM-assigned power class
against a deterministic channel policy — so a boss, a set, a socket and a trash mob stop being the
same faucet, which matters specifically because `AGENTS.md`'s no-hard-ceilings rule means every
volume-only gate eventually opens. Module 11 classifies (a model call, 98 atom families, not per
affix); module 12 is pure deterministic policy, no model calls.

## Architecture decisions (from the map/specs; not re-litigated)

1. **L0 runs before L1 and consumes no RNG** — it composes the candidate list; L1's existing
   `affix.draw` stream draws from it. Adding it late must not shift a single historical roll.
2. **Classification is per atom **family** (98), never per affix (~980)** — tier already carries
   strength (`ssot-rarity.md` §3.3); classifying per-affix would ask a model for a magnitude judgement
   wearing an enum's clothes.
3. **`affixClass := MAX over the affix's refs of familyPowerClass(ref)`** — never sum/average, so a
   bundle cannot launder a `pinnacle` atom into a lower class.
4. **Module 12 owns every number; module 11 authors none** — the class is never a number, never a rate
   (`seedsmith-map.md` P1: the LLM writes identity, deterministic code writes magnitude).
5. **Renamed from `channel-pools`** — collides with shipped `channel-pool` (effect-atom E30, a
   different L2 concept). `affix-channel-weights` is the module's real name everywhere in this plan.
6. **The tree's own consumption of L0 (passive-tree-repair P10.3) is not this plan's job** —
   `passive-tree-repair-todo.md`'s own disposition defers it until a pick-quality measurement justifies
   it. This plan builds L0 for its original, owner-decided purpose: the six item acquisition channels.

## Already shipped (pointers, not tasks)

| Module | Evidence |
|---|---|
| `affix-schema` (1) | `seed-to-concrete-todo.md` T3.1, T3.2 — DONE. |
| `resolution-order` (2) | T3.3, T3.4 — DONE. |
| `affix-library` (3) | T3.5 — DONE. |
| `instance-producer` (4) | T3.6 — DONE. |
| `mods-absorption` (5) | T6.1 — DONE 2026-09-06. |
| `patron-absorption` (6) | T6.2 — DONE 2026-09-06. |
| `world-seed` (7) | T5.1 — DONE. |
| `eligibility-tags` (8) | T5.2 — DONE. |
| `affix-authoring` (9) | T7.1, T7.2 — CLOSED 2026-09-06. |
| `dev-reforge` (10) | T5.7 — DONE. |

## Dependency graph

```
affix-power-class (EPL1.1-1.3, module 11)  ──►  affix-channel-weights (EPL2.1-2.3, module 12)
   (deps: affix-schema[1], affix-library[3] — both already shipped)     (deps: eligibility-tags[8] — shipped, + module 11)
```

## Suggested order and parallel lanes

| Lane | Tasks | Notes |
|---|---|---|
| α classify | EPL1.1 (registry+schema) → EPL1.2 (classifier build) → EPL1.3 (the 98-call run) | Sequential; EPL1.3 is a K2-shaped model-calling task, own charter. |
| β weights | EPL2.1 (schema+tuning shape) → EPL2.2 (`poolFor` resolver) → EPL2.3 (L1 wiring) | Sequential; needs EPL1.3's real classifications to have real data, though the resolver itself can be built and tested against a fixture registry first. |

**Hard edges this plan honours:**
- **H7:** `data/tuning/affix-power-class.v1.json` (target shares) and the channel-weight policy file
  each land with every reader in the same commit.
- No golden move expected — L0 is additive ahead of L1's existing draw; if a golden moves, that is a
  defect to report (rule 1 above), never something to re-bless silently.

## Phases

| Wave | Modules | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| 1 | `affix-power-class` | EPL1.1–EPL1.3 | S–M, EPL1.3 is a model-calling run | sequential |
| 2 | `affix-channel-weights` | EPL2.1–EPL2.3 | S–M | sequential, after wave 1 |

## Checkpoints

| # | Checkpoint | Evidence |
|---|---|---|
| CEP1 | **98 families classified, structurally.** `basis` on every row; `blocked` counted separately, never coerced; re-running over unchanged families is byte-identical. | `seedsmith` test suite + the metrics report |
| CEP2 | **The pool is a property of the channel, not the source.** `poolFor(container, channel, rarity)` returns different weighted lists for `drop` vs `boss` vs `set`/`socket`/`unique`/`craft` on the same container; no channel's weight for a legal affix is exactly zero unless a comment names the structural exemption. | focused Core tests |

## Cross-program edges

- `passive-tree-repair` P10.1/P10.2/P10.3 — filed as this program's own modules, correctly not built
  there (session-boundary discipline). P10.3 (tree consumption) stays that program's own future task,
  gated on its own pick-quality measurement; not built here.
- `seed-to-concrete-todo.md` T3.1–T7.2 — the 10 already-shipped modules this plan points to. Not
  edited here (that file belongs to its own program's session).

## Tuning publishes

| Tunable | Owner task | Readers landing in the same commit |
|---|---|---|
| `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` (new, checked-in registry, not a tunable) | EPL1.1 | The C# `AffixPowerClass` enum mirror. |
| `data/tuning/affix-power-class.v1.json` (target shares) | EPL1.1 | The distribution-report metric. |
| The channel-weight policy file (`(powerClass × channel) → weight`) | EPL2.1 | `poolFor`'s resolver. |

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| EPL1.3's 98-call classification run starts without an owner charter | Named explicitly as a K2 model-calling task in its own todo entry, blocked on a charter the same way BCU2.10-13 are — not run silently. |
| A drop-channel weight rounds to exactly zero, making a legal affix unreachable | The spec's own 0.01% floor (a named minimum in the tuning file) — asserted in test, per `item-ideal.md` D7. |

## Defaults shipped behind (no gates)

- No owner gate on the shape of either module — both are fully specced and agent-buildable. The one
  real external dependency is EPL1.3's own model-call budget, which needs the same owner charter every
  model-calling run in this program needs (CLAUDE.md's multi-agent charter rule), not a design question.

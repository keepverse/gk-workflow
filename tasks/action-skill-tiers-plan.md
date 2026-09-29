# Implementation plan: `action-skill-tiers` (ST)

**Map:** [action-skill-tiers-map.md](../docs/architecture/action-skill-tiers-map.md) ·
**Specs:** [ST1 composer-tier-window](../docs/architecture/action-skill-tiers/spec-composer-tier-window.md) ·
[ST2 holder-rung-pricing](../docs/architecture/action-skill-tiers/spec-holder-rung-pricing.md) ·
[ST3 scope-window-tunables](../docs/architecture/action-skill-tiers/spec-scope-window-tunables.md) ·
[ST4 budget-calibration-report](../docs/architecture/action-skill-tiers/spec-budget-calibration-report.md) ·
[ST5 rung-table-activation](../docs/architecture/action-skill-tiers/spec-rung-table-activation.md) ·
**Tasks:** [action-skill-tiers-todo.md](action-skill-tiers-todo.md) ·
**Parent:** [summoner-convergence-plan.md](summoner-convergence-plan.md), lane A. This plan owns the ST
tasks. It honours parent hard edges H1 (golden order) and H7 (a publish lands with its reader switch),
and the `action-rungs` row of the parent's §5 tuning ledger.

**Task id scheme.** `ST<m>.<n>`: the number before the dot is the **module** (ST1–ST5, as in the
map), so `ST2.3` is module ST2's third task. Waves are listed in the phases table below. This
keeps a task id from reading as a different module's.

## Overview

A skill tier is the item program's tier discipline applied to actions. The atom tier `t1–t5` sets how
strong one effect is, and the rung (1–10) sets which tiers an action may carry. No new column or
curve. Every mechanism exists already, and this program wires the ones that do not reach production:

- the rung's tier window reaches the import-time roll (ST1);
- a holder's cost is scaled once, bounded by the window ceiling (ST2, a **live defect**: every costed
  action above rung 1 pays `costMulti²` today);
- the scope windows become a published tunable (ST3);
- the power budget is measured against real content and tuned per R8 (ST4);
- every reader loads the one budgeted table, so A-G1's check runs in production (ST5).

## Architecture decisions (from the map, not re-litigated)

- **Ruling 1:** tier = atom-tier window, rung = rarity. No `tier` field, column or vocabulary.
- **Ruling 2:** the rung stays 1–10 and `qPower = 1.75^((r-1)/2)`. No module changes a rung value.
- **R7:** the signature window is 1–10, and no window has a floor above 1 (A-U1 §3.2).
- **R8:** ST4's first report tunes `referencePower` (the smallest scalar that rejects no committed
  action, ST4 contract 6). v4 carries it. Leaving 1000 after the reading is not an option.
- **One scaling point:** `CostLedger` (ST2 contract 5). ST2 alone owns `ActionCompiler.cs:61`, and
  `action-enrich` never touches that line.
- **One rung resolver:** `BattleRunState.EffectiveRungOf` becomes an instance method, shared by
  `CostLedger` and the hit. Whichever of ST2.5 and `AE1.2` lands first creates it, and the second adds
  only its own line (ST2 contract 4, `spec-action-base.md` §Which rung).
- **One pricing path:** the ST4 report prices through the same helper as the A-G1 check (ST4 contract 1).
- **Reconciling H7 with map §5.1.** The map has ST4 publish v4 and ST5 move the readers afterwards.
  Parent H7 says a publish lands **in the same commit** as its host reader switch. Doing them in two
  commits would leave a published file that nothing reads. So ST4 produces the reading and the
  `recommendedReferencePower` (ST4.5). The v4 publish runs **inside** ST5.2's commit, together with every
  reader switch. The publish label still credits ST4/R8. R8's intent holds: nothing ever loads the
  untuned budget. ST3's v3 follows the same rule, since its one reader (the planner) switches in the same
  commit (ST3.1).
- **The guard asserts agreement, not "latest"** (ST5 contract 3). Pointing every reader back at an
  older version stays the revert path.

## Dependency graph (modules)

```
  ST2 holder-rung-pricing  ──(re-bless 1, H1)──┐
                                               ▼
  ST1 composer-tier-window ──(re-bless 2, H1)──► AE1.5 action-base re-bless (H1 #3, action-enrich)
        │
        ▼
  ST4 budget-calibration-report ──► ST4.5 first reading (recommendedReferencePower)
        ▲                                         │
  ST3 scope-window-tunables (v3) ─────────────────┤
                                                  ▼
                               ST5 rung-table-activation (publish v4 + all readers, one commit — H7)
                                                  │
                         AE2.2 (injector loads action-base) ──► ST5.4 action-base guard row
```

## Suggested order and parallel lanes (suggested, not enforced)

**Hard edges from the parent** (the only order a builder must honour):

- **H1:** ST2's golden re-bless (ST2.3) → ST1's re-bless (ST1.3) → `AE1.5`. Each is its own commit.
  A module whose change moves no golden records that and re-blesses nothing.
- **H7:** v3 is published in the same commit as the planner switch (ST3.1). v4 is published in the same
  commit as the server, injector and seedsmith reader switch (ST5.2).
- **§5 ledger** `action-rungs`: v3 (ST3) → v4 (ST4 value, published in ST5.2) → readers on v4 (ST5).
  v3 must exist before v4 is published, or `publish.py` numbers them the wrong way round.

**Suggested:**

| Lane | Sequence | Why |
|---|---|---|
| A1 (C# battle) | ST2.1 → ST2.2 → **ST2.3** → ST2.4 → ST2.5 | live defect first; the parent's lane-A first task |
| A2 (C# import) | ST1.1 → ST1.2 → **ST1.3** (after ST2.3) | re-bless second in H1 |
| A3 (Python) | ST3.1 → ST3.2 → ST3.3 → ST3.4 → ST3.5 | fully independent of A1/A2; run in parallel from day one |
| A4 (report) | ST4.1 ∥ ST4.2 ∥ ST4.4 → ST4.3 → ST4.5 (after ST1.2 and a server re-import) | tools can be built early. The **reading** must price post-window content |
| A5 (activation) | ST5.1 (any time) → ST5.2 (after ST3.1 and ST4.5) → ST5.3 → ST5.5; ST5.4 after `AE2.2` | last: it turns a live rejection on |

## Phases

| Wave | Module | Tasks | Sizes | Parallel-safe with |
|---|---|---|---|---|
| 1 | ST2 holder-rung-pricing | ST2.1–ST2.5 | XS, S, XS, S, S | wave 3, ST4.1/4.2/4.4, ST5.1 |
| 2 | ST1 composer-tier-window | ST1.1–ST1.3 | M, S, XS | wave 3 (ST1.1/1.2 can be built during wave 1; only ST1.3 waits on ST2.3) |
| 3 | ST3 scope-window-tunables | ST3.1–ST3.5 | M, S, S, S, S | waves 1, 2 |
| 4 | ST4 budget-calibration-report | ST4.1–ST4.5 | S, S, S, S, S | tools with waves 1–3; ST4.5 after ST1.2 |
| 5 | ST5 rung-table-activation | ST5.1–ST5.5 | S, M, S, XS, XS | ST5.1 any time |

23 tasks. None is L. Three tasks go over the five-file guideline on purpose, and each says why in its
entry. ST2.1 is an atomic mechanical rename that cannot compile if split. ST3.2 deletes `RUN_WINDOW`
from two stages at once. ST5.2 is H7's one-commit reader switch, where every edit is a filename token.

## Checkpoints (review points, not gates)

The map's checkpoints 1–5, placed at the end of each module in the todo:

1. **The tier window is real** (after ST1). Imported atoms lie inside the authored rung's window, and
   the container carries that window.
2. **One rung reading prices one holder** (after ST2). Cost is scaled once, and the rung never exceeds
   the window ceiling.
3. **The windows are tunable** (after ST3). A retune is one publish call and a re-run, and the shipped
   values give byte-identical output.
4. **The budget is measured** (after ST4). The report is committed and `recommendedReferencePower` is
   stated.
5. **A-G1 is live** (after ST5). One version runs everywhere, and "0 rejected" (or the rejected ids) is
   stated. This is also the program's final checkpoint, and it runs the full suite: ST5 crosses Server,
   Injector and seedsmith, which AGENTS.md lists as a full-suite point.

## Cross-program edges

| Edge | With | Kind |
|---|---|---|
| ST2.3 re-bless → ST1.3 re-bless → `AE1.5` → `SP` C1 fix → `SP` 6.1 → `EP` R23 | action-enrich, species-progression, empire-progression | **H1** |
| `EffectiveRungOf` instance resolver: ST2.5 or `AE1.2`, whichever lands first, creates it | action-enrich | shared seam, soft |
| ST5.4's `action-base` guard row needs `AE2.2` (the injector loads `action-base`) | action-enrich | soft dep |
| Holder rungs reach production battles only through action `T74` (A33 `battle-holder-wiring`), which needs `T62` (A26) | action | ST2 is correct but inert in production until then. It is not a blocker (map §7) |
| `scopeWindows` row in `ssot-power-scale.md` §11 (ST3.5) | power program (the file's owner) | review, not a dependency |
| A-G1 status "live" in `action-corpus-map.md` and the five specs that restate the gate (`spec-tier-access-gate.md` §7) | action-corpus | **follow-up owed to that program**, named in ST5.5, not done here |
| S5→S1 top-up and any A-P1/2/3 run | action-distribution-gaps, action-corpus | untouched. No ST task calls a model |

## Tuning publishes owned (parent §5, row `action-rungs`)

| Version | Task | Command | Reader switched in the same commit |
|---|---|---|---|
| v3 `scopeWindows` | ST3.1 | `publish.py action-rungs --add-key ':scopeWindows={…}'` | seedsmith planner (`generate_distribution_planner.py:60`) |
| v4 R8 retune | ST5.2 (the value comes from ST4.5) | `publish.py action-rungs --reprice-rung-power-budget <R> --mark-tuned` | `Program.cs`, `RpgHost.cs`, `pool.py` (×2), `generate_validate_heal.py`, `generate_distribution_planner.py` |

`action-base` v1 belongs to action-enrich (`AE1.1`), not this plan.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| ST2's cost fix and ST1's content change land in one working tree and share a re-bless | H1: separate commits. ST1.3 declares ST2.3 as a dependency. Whichever lands later rebases and re-blesses separately |
| The ST4 reading is taken before ST1 is imported, so it calibrates against atoms the window removes | ST4.5 depends on ST1.2, plus a server re-import of the corpus that is confirmed before the reading |
| v4 is published by itself, leaving a dark file (H7), or production is pointed at v3 and runs on the untuned 1000 | ST5.2 is one commit that publishes and switches. ST5 contract 1 says "never v3" |
| Renaming `ScaledAmount` touches 7 files the spec did not list (`CostLedger.cs`, `PoiseLedgerTests.cs`, `gk-core/tools/PoiseProbe/Program.cs`) | ST2.1 is a separate, zero-behaviour rename task that lists all 7 files |
| A Python loader refusal (floor ≠ 1, non-int) breaks a seedsmith run someone is in the middle of | the values shipped are the current ones, and ST3 is byte-identical by contract. Regenerate with `--dry-run` first |
| The guard probe file is left on disk (the `guard-probe-leftovers` hazard) | ST5.1 writes and removes the probe inside the test, in a `try/finally` whose delete failure fails the test |
| `verify-change.ps1` has no mapping for a new path (for example `gk-core/tools/tuning/test_publish_reprice.py`) | add the mapping in the same task (AGENTS.md). Never fall back to the full suite |

## Defaults shipped behind (no gates)

- The windows ship at `general 1–4 / family 1–7 / species 1–10` (the current values). A retune is a
  later, free publish (ruling 4).
- An action with a `null` band stays unbounded (ST2 contract 2). Bounding those actions is an "ask
  first" behaviour change, not part of this plan.
- A multi-tier rung window is **refused**, never given a default weight (ST1 contract 5).
- The first `referencePower` is the report's `recommendedReferencePower`. Any other value is an "ask
  first" (ST4 Boundaries).
- Holder wiring in production is action T74's job. Until it lands, cost reads the authored rung. The
  plan does not wait on it.

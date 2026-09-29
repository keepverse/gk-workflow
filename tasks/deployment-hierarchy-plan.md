# Implementation plan: `deployment-hierarchy`

**Map:** [../docs/architecture/deployment-hierarchy-map.md](../docs/architecture/deployment-hierarchy-map.md) ·
**Specs:** `docs/architecture/deployment-hierarchy/spec-*.md` (7) ·
**Tasks:** [deployment-hierarchy-todo.md](deployment-hierarchy-todo.md) ·
**Written by:** `backlog-clean-up` `orphan-plan-authoring` (BCU2.5).

**Relationship to `backlog-clean-up`.** This map (approved 2026-09-13) named this plan pair and it was
never written (cause C1). Four of its seven modules were, in fact, already built — by
`empire-development`, which needed them as its own external prerequisite and never looped back to
update this map (cause C3, confirmed by `backlog-clean-up` lane C). This plan records that work as
pointers and plans only the real remainder.

## Overview

A deployment child (lawn Bound spawn, delve party slot, siege combatant, expedition seat) should start
from what its parent actually has, and a real death should have weight (graded injury, a corpse-cache
holding the dead's gear, decay, and three ways to get it back). Modules 3–6 (the cache/decay/retrieval
chain) shipped inside `empire-development`. Module 7 (durability/repair) shipped its workbench-tier
slice inside `species-gear-chain`. What remains: module 1's real wiring (the inherit side is currently
inert), module 2 in full (injury tiers — nothing built), and module 7's own future work (battle wear,
field touch-up, commander-pouch parity).

## Architecture decisions (from the map; not re-litigated)

1. **Decisions.md rows P1 (`wound.*` joins the closed status vocabulary) and P2 (deployment hierarchy
   SSOT) are already approved and appended** (2026-09-13) — no further owner gate on the shape.
2. **Corpse-cache is its own table family** (`rpg_corpse_cache*`), never a repurposing of
   `rpg_item_assignment` — already built this way.
3. **Not a second ActorHub compose.** Pool/status inheritance is snapshotted at deploy time and applied
   through `ActorResourcePools`/`StatusRuntime.Apply`, exactly as today's single Bound path.
4. **Not a second power ladder.** Injury-tier severity reads `%HP lost` through existing combat math;
   `ssot-power-scale.md` §10 gains a reviewed row, never a private `f(level)`.
5. **World-map and siege are not gates on this plan** — their death paths do not exist yet; wiring to
   them is deferred, tracked work for whichever program builds those death paths.

## Already shipped (pointers, not tasks)

| Module | Evidence |
|---|---|
| `corpse-cache` (module 3) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CorpseCache.cs`; commit `1b6fd8de` "feat(empire): scoped inventory, corpse-cache, relic, wonder engine" (2026-09-16); deploy-time-snapshot anti-fraud gate `29459f9e` (2026-09-17). |
| `cache-decay-void` (module 4) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheDecay.cs`, same build family. |
| `cache-field-access` (module 5) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs` + `RpgStore.CacheFieldAccessDelve.cs`. |
| `cache-retrieval-mission` (module 6) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheRetrieval.cs` (the codebase's own `RpgStore.<Feature>.cs` partial-class convention, not a missing file); `CacheRetrievalTuning` in `DeploymentHierarchyTuning.cs:37`; commits `1b6fd8de`, `ecc18cf3` (2026-09-18), `276470b8` (2026-09-19). |
| `item-durability-repair` (module 7) §1/§2/§5-workbench/§6 | Pulled forward and shipped exactly to this program's own spec by `species-gear-chain` T10/T11 (`f67930ac`, 2026-09-16) and T23/T24 (`276470b8`, 2026-09-19). |

## Dependency graph

```
deploy-carry (DH1.1-1.3)
    │
    ▼
injury-tiers (DH2.1-2.3)   [module 3-6 chain already shipped elsewhere — no task here]
    │
    ▼ (soft link only — module 7's death-drop-decay sub-feature, not a hard block)
item-durability-repair remainder (DH3.1-3.3)
```

`DH3.1` (battle wear) has no external blocker and can build any time after `deploy-carry`'s battle
settlement hook exists. `DH3.2` (field touch-up) — **corrected 2026-09-20** (`backlog-clean-up` BCU2.8
review): `party-dungeon`'s `PackGrid` already shipped (D3.18-D3.23, all done); the real remaining seam
is `ICarriedSupplyCheck` having zero implementations and no caller wiring a `PackGrid` instance
through the resolver — buildable now, not blocked on an external program. `DH3.3` (commander-pouch
parity) is independent, small.

## Suggested order and parallel lanes (suggested, not enforced)

| Lane | Tasks | Notes |
|---|---|---|
| α wiring | DH1.1 → DH1.2 → DH1.3 | Sequential — each reads the prior's carry point. |
| β injury | DH2.1 → DH2.2 → DH2.3 | Sequential per the map's own G2 gate shape. |
| γ durability remainder | DH3.1, DH3.2, DH3.3 (all parallel) | All three buildable now — `PackGrid` already shipped; DH3.2 implements `ICarriedSupplyCheck` against it. |

**Hard edges this plan honours:**
- **H7:** any new tuning key (e.g. `wearPerBattleMilli`, the repair keys) lands in
  `gk-core/data/tuning/deployment-hierarchy.v1.json` — the **same file** `species-gear-chain` T10/T11 already
  established the shared schema for (see that program's own "Resolved 2026-09-15" note) — never a
  second file, and lands with its own reader in the same commit.
- No golden move expected: pool/status inheritance is additive to an inert field; a golden moving here
  is a defect to report, not something to re-bless silently.

## Phases

| Wave | Modules | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| 1 | `deploy-carry` | DH1.1–DH1.3 | S–M | sequential |
| 2 | `injury-tiers` | DH2.1–DH2.3 | M | sequential |
| 3 | `item-durability-repair` remainder | DH3.1–DH3.3 | S–M | all three parallel |

## Checkpoints

| # | Checkpoint | Evidence (map's own gate) |
|---|---|---|
| CD1 | **G1 — the tree carries.** A delve party redeployed into a second room starts from its `CarryOut` pools and status specs, not rest-max. | `deploy-carry`'s own tests, replay byte-identical |
| CD2 | **G2 — a wound is real.** A graded specimen fights measurably weaker on its next deployment; an untreated wound advances and can kill on its own clock; the anti-spiral check refuses a runaway stack. | `injury-tiers`'s own tests |
| CD3 | **G6 remainder — gear wears.** An item's `current` decrements once per battle (DH3.1); commander-pouch gear wears through the same path (DH3.3); field touch-up (DH3.2) resolves through a real `ICarriedSupplyCheck` implementation. | focused tests per task |

## Cross-program edges

- `party-dungeon`'s `PackGrid` — already shipped; DH3.2 (field touch-up) implements `ICarriedSupplyCheck`
  against it. Not edited here (read-only consumer).
- `empire-progression/spec-legion-commander.md:136-137,211` ships an explicit fallback ("a fallen
  commander member is detached and set `Recovering`… until `injury-tiers` lands") — DH2's own build
  is what lets that program drop its fallback, by that program's own choice, not this plan's edit.
- `species-gear-chain-todo.md` T10/T11/T23/T24 — the module 7 workbench slice this plan builds on top
  of. Not edited here.

## Tuning publishes

| Tunable | Owner task | Readers landing in the same commit |
|---|---|---|
| `data/tuning/deployment-hierarchy.v{n+1}.json` — `wearPerBattleMilli` | DH3.1 | The battle-settlement wear decrement this task adds. |
| Same file — repair keys (`repairDestroyChanceMilli`, `repairRatioMilli`, `tierCapMilli` for the field tier) | DH3.2 (when unblocked) | Field touch-up's own resolver. |
| Same file — injury-tier thresholds | DH2.2 | The tier-grading resolver. |

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| A second parser for `deployment-hierarchy.v1.json` appears | `species-gear-chain`'s "Resolved 2026-09-15" schema-agreement note is the one shared layout; every new key is an addition to it, never a second file. |
| `injury-tiers`' anti-spiral guarantee is assumed rather than tested | The map names this explicitly (P1 row) — DH2.1 ships its own opt-in constructor check, mirroring `ExhaustionPolicy.cs`/`NervePolicy.cs`, and a test proves the refusal. |
| DH3.2's "blocked on `party-dungeon`" claim goes stale again after `PackGrid` ships | Corrected 2026-09-20 by re-verifying against live code and the source todo rather than the map's own prose — the same discipline `BCU1.7` used elsewhere in this program. |

## Defaults shipped behind (no gates)

- No owner gate in this plan. Every module here is agent-buildable against its own spec; DH3.2's
  earlier "blocked on `party-dungeon`'s `PackGrid`" was a stale dependency claim, corrected 2026-09-20
  — `PackGrid` already shipped, so DH3.2 is buildable now, not an owner question either.

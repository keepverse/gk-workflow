# Spec: `world-difficulty-profile`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 14 of the
[world-continuity map](../world-continuity-map.md) (wave 4; depends on `world-creation`, `coarse-step`,
external trade-network `trade-foundation` · `world-stamp`). Ideal:
[world-continuity-ideal.md](../world-continuity-ideal.md) §6.10, W7 (one profile per world, default only
in v1). Storage owner of the profile **id**: trade-foundation `world-stamp`
(`docs/architecture/trade-network/trade-foundation-map.md` §2.4). House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

Each world carries one difficulty profile id, stored in the per-world stamp. This module owns the
profile **catalog** (v1: one `default` row) and the knobs **this program** reads: the coarse contest's
scale and pressure, and the AI escalation after victory. Trade owns its own knobs.

## Scope and non-goals

**In scope:** the catalog file, its loader and validation; the knob set; the rule that `default`
reproduces today's numbers; how coarse and AI read a profile.

**Not in scope:** where the id is stored (`world-stamp`); a player-facing difficulty picker (v1 has one
row); trade's knobs (`docs/architecture/trade-network-ideal.md` §14b, the difficulty row).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The only per-faction difficulty-shaped knob is the upkeep handicap | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:154-156` (`UpkeepHandicapMilli`); hashed per faction `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:29-30` |
| Tuning is loaded once per process into static policies | `gk-core/src/FusionRpg.Server/Program.cs:36`, `:48` (as cited in `trade-foundation-map.md` §1) |

### Wiring gap

`ruleset_version` is always the literal `1` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:243-245`); the
stamp that will carry the profile id does not exist yet (`world-stamp`).

### Real gap

No profile catalog anywhere in `src/` (`trade-foundation-map.md` §2.4 records the same search).

## Design

### 1. Catalog — a sibling file, not the number file

`data/tuning/world-difficulty-catalog.v1.json` (new): `{ "profiles": [ { "id": "default", "displayName": … } ] }`
— **identity and player words only**. Display names live in the catalog row (GG-62), never in
`world-continuity.v1.json` (tunables-ssot T7/T8: runtime catalogs are a sibling class). **Corrected by the
2026-09-20 audit:** the first draft put the knob numbers (`coarsePressureMilli`, …) inside the catalog
row. That is the mix tunables-ssot §1 forbids — *"never mixed into the number file for the same domain"*
runs both ways, so a catalog carries no balance number, and a rename must never be indistinguishable
from a rebalance (T7). The knobs live in the number file, keyed by profile id:
`world-continuity.v1.json` → `difficulty.profiles.{profileId}.{knob}`. A profile id in the catalog with no
knob block, or a knob block with no catalog row, is a load rejection naming it (T5, T8). Both files are
loaded by the host, injected into Core (Core never reads a file, PRINCIPLES.md §5).

### 2. Knobs this program reads

| Knob | Read by | `default` value |
|---|---|---|
| `coarseContestScale` | `coarse-step` §5 (`Sigmoid` scale, Θ units) | the scale `CombatProbability` contests use today — the same `CombatProbabilityPolicy` source the Sigmoid reads (`gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8-9`); no new number |
| `coarsePressureMilli` | `coarse-step` §5 (per-turn loss chance multiplier) | provisional 100 (a 10% ceiling per frontier per turn at a saturated gap), calibrated by the economy report's win-rate column |
| `escalationAfterVictoryMilli` override | `world-victory` §4 | absent → the `world-continuity.v1.json` value |

A knob that `default` does not set reads the program's tunable; a profile that sets a knob **overrides**
it for worlds stamped with that profile. `default` sets only what has no other home, so `default` worlds
reproduce today's numbers exactly.

### 3. Reading a profile

The coarse input builder (Data) reads the world's stamp → profile id → that profile's knob block in the
number file, and logs the knob values into `CoarseInputs` (`coarse-step` §1). Replay therefore never re-reads the catalog: a later
catalog edit cannot change a recorded catch-up. For full steps the AI reads the profile through the stamp
carried on `WorldState` (`world-stamp` puts the stamp on the state, so it is hashed state, not a hidden
input).

### 4. Invariants

- An unknown profile id is a load rejection (the world refuses to load with a named reason).
- A world's profile id never changes after creation (`world-stamp` writes it once).
- Tuning is process-global (`trade-foundation-map.md` §2.4 assumption X4): a catalog publish applies to
  every world with that id; the stamp records the catalog version so a mismatch is detected. What a
  mismatch does is `world-stamp`'s rule (a stamp names every tuning domain the server loaded,
  `trade-network/trade-foundation/spec-world-stamp.md` §6, the tuning manifest); this module loads both files through
  that recording loader so neither domain can be missing from a stamp.

## Acceptance (contract)

1. An unknown profile id rejects the load with `difficulty.unknown`.
2. The profile id of a world is identical at creation and after any number of turns and catch-ups.
3. A world on `default` produces byte-identical step hashes and coarse results to a build without this
   module.
4. Knob values used by a coarse record are the logged ones, not a re-read (replay with the catalog absent
   succeeds).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/DifficultyProfileTests.cs` (new): 1, 3.
- `tests/FusionRpg.Data.Tests/WorldCoarseReplayTests.cs` (extend): 2, 4.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python scripts\audit-magic-numbers.py --summary
```

## Hard edges

- **`rpg_worlds` schema:** none here (the id lives in `world-stamp`'s columns).
- **Replay:** knobs are logged coarse inputs; the stamp is hashed state.
- **Corpse-cache tick key:** none.

## Dependencies

`world-creation` (writes the id through the stamp), `coarse-step` (reads knobs); external `world-stamp`.

## Tunables

`data/tuning/world-difficulty-catalog.v1.json` (new; catalog class — ids and display names only) and the
`difficulty.profiles` block of `data/tuning/world-continuity.v1.json` (numbers, units stated per knob).
**Verification boundary (audit 2026-09-20):** neither file is mapped in
`gk-core/scripts/verification-boundaries.v1.json` (tuning files are mapped one by one, e.g. `:880-883`), so
`scripts/verify-change.ps1:118` throws for them; the module that first publishes them adds their mapping
in the same change, the precedent every mapped tuning file followed. First publish goes through
`gk-core/tools/tuning/publish.py`, which cannot yet publish a first version of a new domain
(`gk-core/tools/tuning/publish.py:60-68`); the module that first needs a new domain file extends the tool
(tunables-ssot T4), never hand-writes the JSON.

## Boundaries

- **Always:** one profile per world, fixed at creation; knobs logged.
- **Ask first:** a second profile or a player-facing picker (W7 says default only in v1).
- **Never:** display names in the number file; a balance number in the catalog file; a knob read live
  during replay.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `DifficultyCatalog.Get(id)` → knobs | `coarse-step` input builder, AI policy, `world-victory` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: tuning catalogs, coarse step, AI escalation, world stamp (external).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: trade-foundation-map.md §2.4; see spec-world-state-vocabulary.md. Not read:
    tunables-ssot.md in full (rules from PRINCIPLES.md §5 and DESIGN-GATE row).
[x] decisions.md checked: none on difficulty.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: handicap knob, publish.py first-version stop, CombatProbability.
[x] Surrounding sections read.
[ ] Constraint tested: acceptance 3 is to be run.
[x] No §2 invariant contradicted.
[x] Corrections propagated.
[x] No population pinned.
[x] No cache.
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork: one catalog; trade keeps its own knobs in its own section.
[x] No new cross-cutting rule.
```

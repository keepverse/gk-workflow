# Implementation plan: `species-progression`

**Map:** [species-progression-map.md](../docs/architecture/species-progression-map.md) ·
**Specs:** [species-progression/](../docs/architecture/species-progression/) (seven modules) ·
**Tasks:** [species-progression-todo.md](species-progression-todo.md) ·
**Parent:** [summoner-convergence-plan.md](summoner-convergence-plan.md), lane B, prefix `SP`. This plan
owns the program's own tasks. The parent owns cross-program order and the hard edges (H1–H7), and this
plan honours them.

**Binding inputs.** [spec-rulings-2026-09-18.md](../docs/architecture/spec-rulings-2026-09-18.md) R1–R4,
R16–R19, R21 and R23. The `decisions.md` *Class system* and *Actor layer stack* amendments landed on
2026-09-18 (map §9). Nothing here re-litigates a ruling or a map decision.

## Overview

The program builds layers **1b** (player-modified species) and **2b** (empire species progression) of the
actor layer stack. One Core projector serves 1a, 1b and 2b, and one registered `IActorStatSubsystem`
delivers all three to lawn, sheet and battle. It also builds Zomboss's commander clock from lawn-run
outcomes. Two live defects are fixed on the way:

- **C2 is in production today.** The eager boot roll makes every eligible fusion pick fail with
  `picks.already-materialised`. The fix is wave 0 and ships first, as soon as `save-identity`'s first
  slice lands.
- **C1:** world-turn uniques get a leaked species term. This is a defect correction in H1 position.

The program also carries the one explained re-bless (step 6.1, R2 + R16 + R21).

## Architecture decisions (from the map and specs, not re-litigated)

- **One selection rule.** `ProgressionLayerSelector` decides, for each actor, the commander term and
  either 2a or 2b, never both. Every compose path asks it. A specimen's empire is its **owner**, not its
  side (save-identity G5, map C10).
- **One scaling product.** `LadderScale.Micro` is the only `kMicro · P(Θ)` in `src/` (map C6). Because
  of it, a projected 2b atom equals the live resolve exactly.
- **One projector (R-S3).** `SpeciesLayerProjector` projects 1a (core), 1b (the non-core atoms of a
  ledger instance) and 2b (allocation → Θ-free rows). It absorbs `SpeciesPassiveAtomSource`, and the
  Data-layer atom builder moves into Core.
- **SourceIds come from GG-49.** The new ids are `species-base:`, `species-player:`, `species-empire:`
  and `aptitude.{scopeText}.{Share}`. The retired id is `species-passive:`. Each one gets an
  `actor-hub-ssot.md` §8.1 row in the change that introduces it.
- **1b is empire-scoped (save-identity G3).** `rpg_player_species_mod` is born keyed
  `(save_id, empire_id)`. The roll is **delayed, never eager**: a deterministic preview, never stored.
- **2b resolves alone (R2).** A per-`(SaveId, EmpireId, species)` container holds it. The container is
  re-projected exactly once through one hook for every empire (R1, R3), and withdrawn when empty.
- **Each layer resolves alone (R2 + R16).** The one resolver (`AptitudeResolver`) does this, with a
  tunable per-layer weight (R21, `read.layerWeightMilliByScope`, defaults 500/667/667/1000). It is one
  re-bless, in one commit.
- **Zomboss's commander clock** runs on the existing XP machinery, keyed `(SaveId, EmpireId.Zomboss)`
  (R3). Its two awards go in `progression`, not `species-progression` (map C8).
- **Not built here:** `species-level-grants` (owner-deferred), `zomboss-species-xp` (built by
  `EP ai-empire-species`), and species XP outside the lawn.

## Dependency graph (modules)

```text
                        [SE save-identity FIRST SLICE]
                                     │
                                     ▼
 WAVE 0  species-mod-ledger (C2 live-defect fix: ledger + delayed preview + eager roll removed)
                                     │  (the 1b rows exist; delivery waits for 6.2)
 WAVE 1  layer-source-selector ──────┼──────────────────────────────┐
          SP1.1 selector (any time)  │                              │
          SP1.2 C1 fix ◄── [AE action-base re-bless]  (H1)         │
 WAVE 2  ladder-scale-parity ────────┤                              │
 WAVE 3  species-layer-projector ◄───┘ (needs 1 + 2)                │
                     │                                              ▼
 WAVE 6  delivery ── SP6.0 R21 weights publish ─► SP6.1 THE RE-BLESS (H1: after SP1.2)
                     │                                    │
                     ├─► step 6.2 (1a/1b to lawn, sheet, battle) ◄── wave 0 + wave 3
                     │
 WAVE 5  empire-species-container ◄── [SE save-identity migration] + wave 3
                     │
                     └─► step 6.3 (2b cutover, value-neutral) ◄── wave 5 + step 6.2
 WAVE 7  zomboss-commander-clock ◄── [SE save-identity migration] (H2)
          └─► consumed by EP4.16 (Zomboss commander pool, R23)
```

Wave numbers follow module numbers (wave *n* = module *n*). The exception is module 4, which is wave 0
because it is the live defect. There is no wave 4.

**Map edge 3 → 4, as sequenced here.** The map lists `species-mod-ledger` after
`species-layer-projector`. The ledger's own files use nothing from module 3 (spec §Project Structure: a
table, a preview, a fusion repoint). Module 3 is needed only to *deliver* 1b, which is step 6.2. So
wave 0 does not wait on waves 1–3. Until step 6.2, the sheet reads the ledger instance through today's
`SpeciesPassiveAtomSource` (SP0.5). SP3.6 then replaces it with the projector, as module 3 requires. The
map's order is still honoured where it matters: 1b reaches the fold only through the projector and the
one subsystem.

## Suggested order and parallel lanes (suggested, not enforced)

Everything below is advice. It follows the dependencies, and whoever builds may reorder or split it.
Only the edges marked **H#** are the parent's hard edges.

| Lane | Tasks | Starts when | Notes |
|---|---|---|---|
| **B-fix** (first) | SP0.1 → SP0.2 → SP0.3 → SP0.4 → SP0.5 → SP0.6; SP0.7 in parallel | **SE4.11–SE4.14** (the `save-identity` first slice) have landed | The live defect (parent CC1). Needs no other SP wave |
| **B-core** (parallel with B-fix) | SP1.1, SP1.3, SP1.4, SP1.6; SP2.1 → SP2.2; SP3.1–SP3.3, SP3.8 now; then SP3.4 → SP3.5 → SP3.6 → SP3.7 | now: nothing external | SP1.1 uses today's `CommanderId` if `SE4.1` has not landed (spec: `commander-identity` re-types it) |
| **B-rebless** | SP1.2 → SP1.5; SP6.0 → SP6.1 | SP1.2: after `AE action-base`'s re-bless commit (**H1**). SP6.1: after SP1.2 (**H1**) | H1 order: `ST2` → `ST1` → `AE action-base` → **SP1.2** (C1, a defect correction) → **SP6.1** (the one re-bless) → `EP4.18` |
| **B-deliver** | SP6.2 → SP6.3 → SP6.4 → SP6.5 → SP6.6; SP6.7 ‖ SP6.8; then SP6.9 | waves 0 and 3 are done. Suggested after SP6.1, so goldens move once per cause | SP6.6 builds the one server→injector save-switch notice itself. No SE task provides it (see Risks) |
| **B-empire** | SP5.1 → SP5.2 → SP5.3 → SP5.4; SP5.5; then SP6.10 → SP6.11 | **SE4.20** + **SE4.21** have landed (the migration is active; the re-typed `TryApplyXpUnlocked` hook) | SP5.5 waits on `EP4.14`/`EP4.15`; SP5.3's R18 case waits on `EP respec-free-counter` |
| **B-clock** | SP7.1 → SP7.2 → SP7.3 | **SE4.20** (**H2**: SP7.2 writes `(save_id, empire_id)` rows of the re-keyed `rpg_actor_progression` / XP ledger) | Unblocks `EP4.16` |

**Hard edges this plan honours:**

| Edge | Parent | Tasks |
|---|---|---|
| `AE action-base` re-bless → SP1.2 (C1) → SP6.1 (re-bless) → `EP4.18` | **H1** | SP1.2, SP6.1 |
| `SE save-identity` migration (**SE4.20**) → any write of a `(save_id, empire_id)` row of `rpg_actor_progression` / XP ledger | **H2** | SP7.2 (the Zomboss award). SP5.2 hooks the re-typed writer, which exists only after the migration |
| A tuning publish and its host reader switch land in one commit | **H7** | SP6.0 (`Program.cs:247` **and** `RpgHost.cs:185`), SP7.1 (`Program.cs:137`; the injector does not load `progression`) |

The first slice is **not** under H2. `rpg_player_species_mod` is a new table born in the final shape;
`save-identity` never migrates it. So wave 0 needs only the slice (`SaveId`, `EmpireRef`,
`rpg_save_empires`, `HumanEmpireOf`).

**Shared file `RpgStore.WorldTurns.cs` `HubInputsFor`.** SP1.2 goes first, then `EP1.14`, then
`EP3.8`/`EP3.11`, then `EP4.18` (the order in `empire-progression-plan.md`). SP6.6 (the 1a/1b feed for
world-turn uniques) rebases onto whichever of those has landed.

## Phases

| Wave | Module(s) | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| 0 | `species-mod-ledger` (C2 live defect) | SP0.1–SP0.7 | 1 XS · 1 S · 5 M | with waves 1–3 (different files; SP0.5 and SP1.4 both touch `UniqueActorHubCompose.cs`, so rebase, no conflict of intent) |
| 1 | `layer-source-selector` (+ `ShareWithinScope`) | SP1.1–SP1.6 | 1 XS · 3 S · 2 M | SP1.1/1.3/1.4/1.6 now; SP1.2 in H1 position |
| 2 | `ladder-scale-parity` | SP2.1–SP2.2 | 1 S · 1 M | yes |
| 3 | `species-layer-projector` (+ SP3.8, step 6.1's scope-text prerequisite) | SP3.1–SP3.8 | 3 S · 5 M | SP3.1–3.3 and 3.8 now; SP3.4 after SP1.6 + SP2.1 |
| 5 | `empire-species-container` | SP5.1–SP5.5 | 3 S · 2 M | after the SE migration and wave 3 |
| 6 | `species-layer-delivery` 6.1 / 6.2 / 6.3 | SP6.0–SP6.1 (step 6.1), SP6.2–SP6.9 (step 6.2), SP6.10–SP6.11 (step 6.3) | 2 S · 10 M | the three steps are ordered; tasks inside step 6.2 partly parallel (SP6.7 ‖ SP6.8) |
| 7 | `zomboss-commander-clock` | SP7.1–SP7.3 | 1 XS · 1 S · 1 M | yes, after the SE migration |

**Task ↔ spec step map for delivery** (cross-program references say "SP6.1" for the re-bless):
step 6.1 = **SP6.0** (R21 weights published, no value moves) + **SP6.1** (the re-bless commit). Step 6.2
= SP6.2–SP6.9. Step 6.3 = SP6.10–SP6.11.

Totals: **43 tasks** (3 XS · 14 S · 26 M · 0 L), plus 5 checkpoints (0–4). SP6.1 alone exceeds five files, on purpose (see Risks).

## Checkpoints (review points, not gates)

| # | After | Evidence |
|---|---|---|
| **CP0 — picks work in production** (parent CC1, C2) | wave 0 | The boot → create-save → reboot → fuse regression is green for both saves. `player_species` has no reader or writer in `src/`. The §9 hand-over for C2 is filed |
| **CP1 — one rule, one product, one projector** | waves 1–3 (not SP1.2) | Six-cell selector matrix, four-path parity, the aptitude read byte-identical under `LadderScale`, atom-side movement listed. Projector parity is exact. The 1a/1b partition loses nothing. `guard-actor-hub.ps1` is green |
| **CP2 — the re-bless chain** (parent CC4, first half) | SP1.2, SP6.0, SP6.1 | The C1 commit follows `AE action-base`'s re-bless and is classified as a defect correction. The SP6.1 commit follows SP1.2, with its per-value table and the R21 per-layer rows. The three merge-contract tests are rewritten, not re-blessed |
| **CP3 — 1a/1b reach every path** | step 6.2 (SP6.2–SP6.9) | Per-path SourceId-family tests, cache triggers 1–6, a real `/execute` fusion that changes a lawn actor's composed value (live-probe standard), perf within budget |
| **CP4 — program complete** (parent CC4, second half) | waves 5, 7, step 6.3 (SP6.10–SP6.11) | Step 6.3 moves no composed value. Zomboss rows reach module 5 through the one hook once `EP4.14` has landed. The Zomboss clock advances per run, per save. Every §9 row is handed over or confirmed. **Full suite once** (AGENTS.md point 1: end of a large feature) |

## Cross-program edges

| Edge | From → to | Kind |
|---|---|---|
| `save-identity` **first slice**: SE4.11 (types), SE4.12 (`rpg_save_empires`, the seeder, `HumanEmpireOf`/`EmpiresOf`), SE4.13 (`SaveOfRun`), SE4.14 (`empire_id`, `OwnsSpecimenUnlocked`) | SE4.11/SE4.12 → SP0.1, SP0.3; SE4.14 → SP0.5 | hard (spec, G3). Wave 0 depends on **nothing else** in SE |
| `save-identity` **migration** SE4.20 (`Init` runs it) + SE4.21 (the `EmpireRef` store API: `TryApplyXpUnlocked`, `CommanderLevelOf`) + SE4.22 (Zomboss is an empire of the save) | SE4.20/SE4.21 → SP5.1, SP5.2; SE4.20–SE4.22 + SE4.13 → SP7.2; SE4.21 → SP7.3 | hard. **H2** (SE4.20) for SP7.2 |
| Save-switch signal to the injector (spec trigger 6) | **no SE task provides it**: the strengthened `save-identity` moved injector ownership to a per-spawn fact, and `NS1.8` covers only the web | SP6.6 builds the one generic notice (default). SE and NS reuse it and never add a second |
| Same-file edits | `SE4.34`/`SE4.35` ↔ SP1.2 (`RpgStore.WorldTurns.cs` provider); `SE4.32` ↔ SP6.3/SP6.10 (`AptitudeEndpoints.cs` fetch); `SE4.28` ↔ SP1.3 (the injector owner map); `SE4.38` ↔ SP0.6 (`player_species`) | whichever lands second rebases, and neither re-implements the other. If SP0.6 lands first, SE4.38 has no `player_species` site left |
| `save-identity` owner column `rpg_unique_actors.empire_id` (G5, SE4.14) and the ownership predicate | SE4.14 → SP1.2, SP1.3 re-typing | soft. Built first, SP1 uses today's equivalents behind one call site (spec) |
| `commander-identity` `EmpireId` | SE4.1–SE4.4 → SP1.1 | soft. Built first, SP1.1 uses `CommanderId` |
| `AE action-base` golden re-bless | AE → SP1.2 → SP6.1 | **H1** |
| `aptitudes` v9 retire-atk | `SE1.4` → SP6.0 | parent §5 order: SP6.0 publishes the revision after SE1.4's |
| C1 fix consumed by the siege seam (X5) | SP1.2 → `EP3.8` | hard for EP |
| `CommanderLevelOf` for Zomboss | SP7.3 → `EP4.16` | hard for EP |
| The re-bless | SP6.1 → `EP4.18` | **H1** for EP |
| Zombie species XP credited to Zomboss's empire (R1) | `EP4.14` + `EP4.15` (+ `EP4.3`, the empire-level credit hook) → SP5.5 | hard for SP5.5 only. Until then Zomboss 2b is the honest `Empty` |
| Priced empire respec (R18) | `EP specimen-respec-price` (EP1.6–EP1.10) + `EP respec-free-counter` (EP4.9–EP4.12) → SP5.3's refused-charge case | soft. SP5.3 ships the override re-projection. The R18 case is added once the charge exists |
| Per-save SignalR group | `NS player-routing` ↔ SP6.5/SP6.6 | coordinate. SP broadcasts through `AptitudeEndpoints.BroadcastBestEffort` and never adds a group |
| `progression` publishes | `EP4.2`, `creature-lawn-deploy` `lawn-deploy-progression`, SP7.1 | parent §5: next free version at landing |
| verify-change mapping for new paths | `TVB` ↔ every SP task | if a new path is unmapped, add the mapping or report it. Never fall back to the full suite |

## Tuning publishes this plan owns (parent §5)

| File | Revision | Task | Keys | Parent §5 row |
|---|---|---|---|---|
| `aptitudes` | next after `SE1.4`'s v9 (`publish.py` derives `n`) | SP6.0 | `read.layerWeightMilliByScope` = `commander` 500, `creatureType` 667, `aspect` 667, `uniqueCreature` 1000 (R21) | `aptitudes`: v9 retire-atk (`SE1.4`) → R21 (`SP` 6.1) |
| `progression` | next free at landing | SP7.1 | `awards.zombossRunVictoryXp` 100, `awards.zombossRunDefeatXp` 25 (working values) | `progression`: shared with `lawn-deploy-progression` and `EP empire-level` |

Every publish goes through `gk-core/tools/tuning/publish.py` and is never an in-place edit. Each lands in the same
commit as its host reader switch (H7).

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `save-identity`'s first slice lands late, so C2 stays live | High: every eligible fusion pick is refused in production | The parent orders the slice first in lane B. SE4.11–SE4.14 are the slice and have no dependency on the migration. SP0.7 re-confirms that. The map offers no interim fix, because removing the eager roll alone re-darkens picks the other way (W5) |
| Test files are owned by the active `solid-remediation-20260917` session (`tests/**`) | Med: the wave 0 and step 6.1 test rewrites cross another session's fence | SP0.7 and each rewrite task coordinate with that session before editing. If it is still active at build time, the rewrite is handed over as an exact disposition list (spec "Tests to rewrite"), never edited silently |
| SP6.1 touches more than five files | Med: one large commit | Allowed on purpose: H1/T7 require every value the re-bless moves to be in **one** commit. The code side is three files. The rest are the three named merge-contract tests plus the re-blessed pins |
| `ladder-scale-parity` moves an atom-side golden by one unit | Low | Measure and list the moves. If a golden moves, stop at the spec's Ask-first. Never fold the move into SP6.1 |
| Lawn per-hit perf regresses once `rpg.species-layer` is added | Med | The memo is bounded per row list. SP6.9 and SP6.11 probe against the recorded baseline. A regression is fixed, never flagged off |
| `EP4.14` is late, so Zomboss has no 2b | Low: the honest `Empty`, by design | SP5.5 is the only task that waits. Every other SP5/SP6 task ships and is tested on the human empire |
| Trigger 6 has no provider: the delivery spec cites `save-identity`'s "T2" signal, which the strengthened `save-identity` dropped | Med: without it, a save switch leaves another save's rows in the injector cache | SP6.6 ships the one generic save-switch notice (the default). It is reported to the SE and NS owners so they reuse it and never add a second one |
| A concurrent `progression` or `aptitudes` publish takes the version this plan expected | Low | `publish.py` derives the number. The later publisher rebases (parent §5). No task pins a version literal |

## Defaults shipped behind (no gates)

- **R21 weights:** 500/667/667/1000, derived from the shipped rate table and marked UNMEASURED.
  Residual-fit and squad-harness own the real values, and a later change is a `publish.py` publish.
- **Zomboss clock awards:** 100/25, working values. Tune from play.
- **Before `save-identity` G5 lands:** a specimen with a human owner row maps to `HumanEmpireOf`, a
  Zomboss-minted one to `EmpireId.Zomboss`, and the commander key stays `player:{id}`. Each sits behind
  one call site that the SE rename sweep re-types.
- **Before `EP4.14`:** there are no Zomboss containers and Zomboss's 2b is `Empty`.
- **Before `EP respec-free-counter`:** the override path re-projects without a charge. The R18 case is
  added when the charge exists.
- **Ask-first items in the specs are review points, not pre-work gates.** They are: the two new tables
  (`rpg_player_species_mod`, `rpg_species_layer_projection`), `ContainerKind.SpeciesProgression`, the
  §8.1 amendments and a moved atom-side golden. Each is additive or measured, and each is shown in its
  task's commit review. Dropping `player_species` is destructive. It is **not** in this plan: the table
  is left in place, unread, until the owner asks.

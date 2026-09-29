# Implementation plan: `empire-progression`

**Map:** [docs/architecture/empire-progression-map.md](../docs/architecture/empire-progression-map.md) ·
**Specs:** [docs/architecture/empire-progression/](../docs/architecture/empire-progression/) (14 modules) ·
**Tasks:** [empire-progression-todo.md](empire-progression-todo.md) · **Task prefix:** `EP` ·
**Parent:** [summoner-convergence-plan.md](summoner-convergence-plan.md), lane B. This plan owns the order
of `empire-progression`'s own tasks. The parent owns cross-program order, and this plan honours its hard
edges H1, H2 and H7. Its sub-program [`build-preset`](build-preset-plan.md) is built after it.

## Overview

`empire-progression` is the **assignment layer**. It decides who puts a progression point where: a human
through a server-owned assignment ladder and an auto-assign control, a unique specimen through a silent
default computed at read, and an AI empire through the same ladder. It also prices a respec for every
unique creature, the commander included (R18). It adds an empire level that pays earned free empire
respecs (R19). It gives a unique creature the commander role, which the creature exercises seated on the
lawn and fighting in a legion. And it re-leads the build-favour corpus so a species' build says something
about that species. None of it is a second progression system: every number reaches an actor through the
existing allocation seams and the one ActorHub compose.

The work is fourteen modules in four waves (A–D) plus one deferred module: **68 tasks** in total, 65
scheduled and 3 deferred. Seven checkpoints follow CP0–CP6 from the map. **No pre-work gate.** Every
external dependency is a real code dependency, and every tunable ships behind a working value published
through `gk-core/tools/tuning/publish.py`.

**Verified against code 2026-09-18 (plan session `plan-ep-bp-20260918`):** none of the 14 modules is
built. `AssignLadder.cs`, `EffectiveAllocation.cs`, `RpgStore.AllocationRespec.cs`,
`BuildFavourMeasure.cs`, `RpgStore.EmpireLevel.cs`, `RpgStore.EmpireFreeRespec.cs`,
`RpgStore.CommanderRole.cs`, `RpgStore.EmpireSpecies.cs` and `ICommanderRoster.cs` are all absent. The
live defects the specs name are present:
- `AptitudeAutoAssign.cs:90` still returns `autoAssign.favour.incomplete` (W3).
- `aptitude.autoAssign` has two listeners (`AptitudesTab.tsx:261`, `SpeciesBuildPanel.tsx:116`) and no
  emitter (W2).
- `UniqueCreatureAllocation.Baseline` has no production caller.

Every tuning domain touched here is still at `v1`: `species-build.v1.json`, `progression.v1.json`,
`aptitude-presets.v1.json`. The pins are all in the server `Program.cs`. The injector's `RpgHost` loads
none of these three domains, so H7 reduces to the server pin plus the tool and test pins.

## Architecture decisions (from the map; not re-litigated)

- **D1. A default is computed at read and never persisted.** The player's own commander pool gets no
  silent default. An AI empire's pool does (R23).
- **D2. An explicit allocation replaces the default wholesale.** It never tops the default up.
- **D3. The ladder returns a distribution, never points.** The default uses `*.Baseline` (largest
  remainder), and the draft uses `AptitudePresetMaterialize` (floor). No third favour-to-points
  function is written.
- **D4. Pass 2 writes the anchor with provenance.** It never writes an overlay file.
- **D5. A lawn commander is a deployment child** (`Roster → ActiveBound`, no tile, no ptr). The
  `decisions.md` row P1 has landed.
- **D6. The build scorer reuses `Considerations.Score`.**
- **Rulings applied:**
  - R1: zombie species XP goes to Zomboss's empire.
  - R3/R17: every empire row is keyed `(SaveId, EmpireId)`, and the player row is the save.
  - R4: when a creature commander leads, the empire's commander pool still applies side-wide and the
    creature adds only its aura.
  - R6: the threat-rung signal ships at weight 0.
  - R16/R21: specimen points resolve alone; the per-layer weight is `species-progression`'s.
  - R18: a unique creature and a commander always pay to respec. Only the empire (species) respec may
    spend an earned free respec, and the player picks which to spend.
  - R19: a new empire-level track.
  - R23: Zomboss's commander pool mirrors the player's.
- **`decisions.md` rows P1–P5 landed in commit `1575db58`.** No task here re-lands them.
- **Rows owed at build, each tasked in the change that needs it:**
  - the `ssot-power-scale.md` §10.1 row for the empire level (EP4.2);
  - the `empire-resource-ssot.md` §3 Accrual-meter row for the free empire respec (EP4.11);
  - the supersession line on `aptitude-sheet` E3 (EP1.18).

## Dependency graph (modules)

```
Wave A   assign-ladder ─┬─► default-build ──────────┐
                        ├─► auto-assign-control      │  (after its /idea-ui pass, EP1.19)
                        │                            │
         specimen-respec-price (independent) ────────┼──────────────────────────────┐
                                                     │                              │
Wave B   favour-detector ─► per-species-lean ─► lead-relabel-pass ─► Phase 4 gate   │
         (independent of A; lead-relabel waits for creature-seed-rederive to commit)│
                                                                                    │
Wave C   [SE commander-identity SE4.1–4.4] + [SE save-identity first slice SE4.11–4.14]│
           └─► commander-roster ─┬─► lawn-commander-seat                            │
                                 └─► legion-commander ◄── [SP layer-source-selector]│
                                                                                    │
Wave D   [SE4.20 migration, SE4.21] ──H2──► empire-level ─► respec-free-counter ◄───┘
                                          └─► ai-empire-species ◄── assign-ladder
                                               R23 half ◄── [SP zomboss-commander-clock] + [SP6.1] (H1)
         ai-build-scorer (DEFERRED: waits on sector-development's INeedVector)
```

## Suggested order and parallel lanes (suggested, not enforced)

Everything below is advice except the edges marked **H#**, which are the parent's hard edges.

| Lane | Tasks | Can start | Notes |
|---|---|---|---|
| **B1 — ladder and default** | EP1.1 → EP1.2 → EP1.3 → EP1.4 → EP1.5; EP1.12 → EP1.13 → EP1.14 → EP1.15 → EP1.16 → EP1.17 → EP1.18; EP1.19 → EP1.20 → EP1.21 | now | EP1.1 is the **fix-first** task (W3, a live defect). EP1.14 moves goldens (see "Golden moves") |
| **B2 — respec price** | EP1.6 → EP1.7 → EP1.8 → EP1.9 → EP1.10 → EP1.11 | now | fully independent of B1, except that EP1.10 (`RpgStore.AptitudePresets.cs`) and EP1.4/EP1.16 (`AptitudePresetEndpoints.cs`) sit in the same preset feature, so rebase rather than race. EP1.8 needs the `save-identity` first slice (`SE4.11`–`SE4.14`: `EmpireRef`, `OwnsSpecimenUnlocked`, `empireId` on specimens) for its payer check (save-identity mismatch 1) |
| **B3 — favour corpus** | EP2.1 → EP2.2 → EP2.3 → EP2.4 → EP2.5 → EP2.6 → EP2.7; EP2.8 → EP2.9 → EP2.10 → EP2.11 → EP2.12 → EP2.13 + EP2.14 | now (EP2.9 onward after `creature-seed-rederive` commits) | Wave B is independent of wave A. EP2.7 and EP2.13 + EP2.14 (one commit) regenerate the plan, which moves the species defaults, so each of those two is its own golden-moving commit |
| **B4 — commanders** | EP3.1 → EP3.2 → EP3.3 → {EP3.4 → EP3.5 → EP3.6} ‖ {EP3.7 → EP3.8 → EP3.9 → EP3.10 → EP3.11 → EP3.12} | after `SE4.1`–`SE4.4` (commander-identity) and the `save-identity` first slice `SE4.11`–`SE4.14`, so `rpg_commander_role` is born keyed (map S8). EP3.3 and `SE4.32` both edit `CommanderEndpoints.cs`: `SE4.32` lands the per-`EmpireRef` listing shape, and EP3.3 plugs `ICommanderRoster.ForEmpire` into it | EP3.8 onward also waits on `SP1.2` (layer-source-selector), because it is the first writer of a legion member's `InstanceId` |
| **B5 — empire level and AI empire** | EP4.1 → EP4.2 → EP4.3 → EP4.4 → EP4.5 → EP4.6 → EP4.7 → EP4.8; EP4.9 → EP4.10 → EP4.11 → EP4.12; EP4.13 → EP4.14 + EP4.15 → EP4.16 → EP4.17 → EP4.18 | EP4.1 and EP4.2 now; EP4.3 onward after `SE4.20` (the migration, **H2**) and `SE4.21` (the Tier A API takes `EmpireRef`); EP4.14 also after `SE4.22` (Zomboss is an empire of the match's save) | the R23 wiring (EP4.18) is **last in H1**: after `SP6.1` |

**Hard edges this plan honours:**

| Edge | Tasks | Parent edge |
|---|---|---|
| `SE4.20` (the migration runs in `Init`) lands before any write of a `(save_id, empire_id)`-keyed `rpg_actor_progression` row | EP4.3, EP4.5, EP4.6, EP4.14 | **H2** |
| The R23 Zomboss commander-pool golden layer comes last in the re-bless chain, after `SP6.1` | EP4.18 | **H1** |
| A tuning publish and its host reader switch land in one commit | EP1.3, EP1.7, EP2.6, EP2.7, EP2.8, EP4.2, EP4.4 | **H7** (server `Program.cs` only; the injector loads none of these domains) |

**Spec-level hard edges** (not parent edges; wrong order means wrong code):
- EP3.8 onward waits on `SP1.2` (layer-source-selector) (map S7).
- Wave C waits on `SE4.1`–`SE4.4` and the `save-identity` first slice `SE4.11`–`SE4.14` (map S8: the role table is born keyed). None of wave C writes a re-keyed Tier A row, so H2 does not apply to it.
- EP2.9 onward waits for the `creature-seed-rederive` session to commit and close. That session holds
  the same anchor paths, and the session-boundary rule forbids editing another session's files.
- EP2.13 and EP2.14 land in **one commit**, so `main` never carries a red gate.
- EP4.14 and EP4.15 land in **one commit**: the credit and the read ship together (`ai-empire-species`
  self-audit).

## Phases

| Wave | Modules | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| **A** (`EP1`) | assign-ladder, specimen-respec-price, default-build, auto-assign-control | EP1.1–EP1.21 | 3 XS · 13 S · 5 M | Lanes B1 and B2 run in parallel. The /idea-ui pass (EP1.19) runs in parallel with everything |
| **B** (`EP2`) | favour-detector, per-species-lean, lead-relabel-pass | EP2.1–EP2.14 | 1 XS · 8 S · 5 M | Parallel with the whole of wave A |
| **C** (`EP3`) | commander-roster, lawn-commander-seat, legion-commander | EP3.1–EP3.12 | 6 S · 6 M | The seat branch and the legion branch run in parallel after EP3.3 |
| **D** (`EP4`) | empire-level, respec-free-counter, ai-empire-species | EP4.1–EP4.18 | 1 XS · 8 S · 9 M | The empire-level/respec-free-counter branch and the ai-empire-species branch run in parallel. `empire-level`'s side rule (S3) makes their landing order irrelevant |
| **Deferred** (`EP5`) | ai-build-scorer | EP5.1–EP5.3 | 3 S | Scheduled only when `sector-development` gives `INeedVector` a non-neutral implementation |

## Checkpoints (review points, not gates)

| # | After | Evidence |
|---|---|---|
| **CP0 — review** | before build | Satisfied by the ruled and strengthened map (rulings R1–R24, strengthen pass S1–S17) and the parent plan. It is a review point, not a gate. `decisions.md` P1–P5 are in `1575db58` |
| **CP1 — the default exists** | EP1.1–EP1.18 | 1. A levelled specimen with no explicit allocation composes its species favour through Hub. 2. An explicit allocation replaces it. 3. The FE computes no shares. 4. A take-back from a specimen or the commander pool charges souls through `PriceOf`, while spending unspent points stays free. 5. Full suite green once. `default-build` crosses Core, Data and Server, which is AGENTS.md full-suite condition 2. 6. Every moved golden is listed |
| **CP2 — the player can reach it** | EP1.19–EP1.21 | The Playwright run `aptitude-auto-assign.spec.ts` is green: a draft fills from a named rule, and nothing persists until Confirm |
| **CP3 — favour is diverse** | EP2.1–EP2.14 | 1. `CreatureBuildPlanGen --check` passes with the lead cap and the shape cap **gating**. 2. The parity band still gates. 3. Every vector is at 1000‰. 4. Every `relead` block carries its provenance |
| **CP4 — a creature commands** | EP3.1–EP3.12 | 1. A creature commander leads a lawn run seated, earns duration XP only, and is refused as a lawn Bound. 2. It leads a legion into a siege and fights as its own specimen with no `CreatureType` points. 3. Full suite green once (legion-commander crosses Core, Data and Server) |
| **CP5 — the AI empire owns its progression** | EP4.13–EP4.18 | 1. Zombie species levels from both XP paths land on Zomboss's empire of the run's save. 2. Two saves hold independent levels. 3. Zomboss's species default resolves non-empty. 4. His commander pool applies side-wide, and the R23 golden commit lists every moved pin as a new layer delivered |
| **CP6 — the empire levels and earns** | EP4.1–EP4.12 | 1. Species level-ups on both paths raise their own empire's level once per species level, surviving compaction. 2. Each empire level adds free empire respecs. 3. A species respec asks the player to spend or pay, and the preview shows both. 4. Zomboss levels on his own track. 5. The §10.1 and §3 rows have landed |

The parent's CC5 ("Empire progression live") is CP1 through CP6 together.

## Cross-program edges

| Edge | Other program's task | Direction | Kind |
|---|---|---|---|
| `EmpireId`, `CommanderRef`, `ICommanderDirectory` | `SE4.1`–`SE4.4` (commander-identity) | SE → EP wave C, EP4.13 onward | hard (spec) |
| `SaveId`, `EmpireRef`, `rpg_save_empires`, `HumanEmpireOf`, `SaveOfRun`/`SaveOfMatch`, `empire_id` on specimens, `OwnsSpecimenUnlocked`: the **first slice** | `SE4.11`–`SE4.14` (SE Checkpoint 4a) | SE → EP1.8, EP3.1, EP4.5, and BP1.11 | hard |
| The `rpg_actor_progression` re-key (`SE4.20`), the Tier A store API taking `EmpireRef` (`SE4.21`), and Zomboss as an empire of the match's save (`SE4.22`) | `SE4.20`, `SE4.21`, `SE4.22` | SE → EP4.3, EP4.5, EP4.6, EP4.13, EP4.14 (**H2**) | hard |
| The Tier B batch covering presets and respec | `SE4.40` | EP1.8 is born with an `EmpireRef` signature, so `SE4.40` has nothing to re-type there. If `SE4.37` has landed, EP1.8 reuses its shared `RequireHumanEmpire` | order |
| The REST and SignalR `empireId` additions | `SE4.31`–`SE4.33` | EP4.7 (level route) and EP4.15 (`AptitudesUpdated.empire`) follow their shape | order |
| The siege seam stops handing a unique the species fallback (X5 = SP C1) | `SP1.2` (layer-source-selector) | SP → EP3.8 | hard (spec) |
| Zomboss's commander level (`CommanderLevelOf`) | `SP7.3` (zomboss-commander-clock) | SP → EP4.16 | hard (spec) |
| The per-layer resolve and weight, and the one explained re-bless | `SP6.1` | SP → EP4.18 (**H1**) | hard |
| `species-progression`'s deferred level-up grants call `assign-ladder` and never a second fill | the future SP sub-program | EP1.2 → SP | ask (map) |
| Per-mode aura scale (`modeScalePermille`) | `aura-skill` `aura-magnitude` | ask filed; not built here | none |
| Specimen XP from delve, siege and world assault | `party-dungeon`, `base-defense` | ask filed; not built here | none |
| The one generic server-to-injector save-switch notice (on `PUT /api/players/current`) | `SP6.6` | any EP cache that must refresh on a save switch reuses it and never adds a second notice | order |
| `EmpireLevelUp` rendered as a player notice | `NS` (notification-ssot) | EP4.7 emits → NS renders | order |
| The `progression` publish order | `creature-lawn-deploy` `lawn-deploy-progression`, `SP7.3` (zomboss-commander-clock) | parent §5 | next-free at landing |
| The `RespecPolicy.Quote` / `TryReallocateUnlocked` / `QuoteSpeciesRespecUnlocked` / `payWith` contract | `BP` (build-preset) | EP1.6, EP1.8, EP1.10, EP4.9, EP4.10 → BP1.4, BP1.5, BP2.5 | hard for BP |

**Shared-file sequencing: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`.** Four changes edit this
file's `HubInputsFor` region (`:559-593`). Suggested landing order:
1. `SP1.2` (layer-source-selector) (the C1 fix, `:581-590`).
2. EP1.14 (the specimen read at `:585-586` goes through the resolver).
3. EP3.8, EP3.11 (admission checks and the `commander.away` skip).
4. EP4.18 (R23 commander read, `:573-576`).

Each change rebases onto the one before it. None re-implements another's change.

## Tuning publishes this plan owns (parent §5)

The rows below follow the map's "Tuning version sequence" table. Every publish runs through
`gk-core/tools/tuning/publish.py`, takes the **next free version at landing**, and moves every pin in the same
commit (H7). Pins are found by
`rg -l "<domain>\.v[0-9]+\.json" src tools tests --glob "*.cs"`.

| File | Order | Task | Keys | Parent §5 row |
|---|---|---|---|---|
| `species-build` | 1 | EP1.7 (`specimen-respec-price`, wave A) | `uniqueRespecBasePrice`, `uniqueRespecEscalationPermille`, `uniqueRespecDecayDays` | `species-build` (5 publishes, 4 modules) |
| `species-build` | 2 | EP2.6 (`per-species-lean` publish 1) | `leanSignalWeights` at zero | same |
| `species-build` | 3 | EP2.7 (`per-species-lean` publish 2) | balance weights, `crowdingFactor` | same |
| `species-build` | 4 | EP2.8 (`lead-relabel-pass`, before stage L) | `leadCapPermille`, `leadCapTolerancePermille`, `shapeCapPermille` | same |
| `species-build` | 5 | EP4.4 (`respec-free-counter`, wave D) | `freeRespecsPerEmpireLevel` | same |
| `progression` | next free at landing | EP4.2 (`empire-level`) | `xpCurve.empire`, `awards.speciesLevelUp` | `progression`: shared with `lawn-deploy-progression` and `SP7.3` (zomboss-commander-clock) |
| `aptitude-presets` | v2 | EP1.3 (`assign-ladder`) | `assignLadder.order` | **not in parent §5.** This plan is its single publisher, so no ordering is needed. Flagged so the parent can add the row |
| `ai` | next free (deferred) | EP5.2 (`ai-build-scorer`) | `buildScorer` block | not in §5; deferred |

Rows 1 and 2–4 may land in either order, because waves A and B are parallel. The next-free rule settles
any race.

## Golden moves (T7: one cause per commit)

| Task | Cause | In parent H1? |
|---|---|---|
| EP1.14 | A levelled specimen with no explicit allocation now composes its species default (`default-build`) | **No.** Flagged to the parent. Land it as its own commit, never combined with an H1 re-bless. The suggested slot is before `ST2`'s re-bless, or between two H1 steps, rebased and re-measured |
| EP2.7, EP2.14 | A regenerated `_species-build-plan.json` changes the species distributions every species and default read reads | **No.** Same handling. The planner change itself is byte-identical at zero weights (EP2.6) |
| EP3.11 | Only fixtures that already build an `InstanceId` legion member can move | No. Named per spec test 7 |
| EP4.18 | R23: Zomboss-side actors with a non-zero commander budget gain a commander layer ("new layer delivered") | **Yes, last in H1**, after `SP6.1` |

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Two goldens move for causes not in H1 (EP1.14, and the plan regenerations in EP2.7 and EP2.14) | Med: a mixed-cause re-bless is unreviewable (T7) | Each is its own commit with a listed moved-pin table. Reported to the parent to be added to H1 |
| `RpgStore.WorldTurns.cs` is edited by four changes across two programs | Med | The sequencing table above; each change rebases, and none re-implements another |
| The lead cap cannot be met by relabelling, so the gate stays red | Med | Spec self-audit: publish a re-tuned cap as a recorded balance step, and never force a relabel. The report names it |
| `creature-seed-rederive` stays active for a long time | Low: it blocks only EP2.9 onward | EP2.1–EP2.8 proceed. `lead-relabel-pass` waits only on that session's commit, never on a decision |
| `species-build` or `progression` version races between lanes | Low | The next-free rule and the parent §5 tie-break. A publish that finds its number taken re-publishes through the tool |
| The pin sets are larger than five files (`progression` has about 15 Server test fixtures) | Low: mechanical | Pin moves are one-line and forced into the publish commit by T5 and H7. They are exempt from the five-file budget, and each such task says so |
| The model pass (EP2.13) spends model calls | Low | The `seedsmith-preflight` skill runs first. `--dry-run` and `--limit` are exercised in EP2.12. Only over-cap species are asked |

## Defaults shipped behind (no gates)

| Unknown | Default | Corrected by |
|---|---|---|
| /idea-ui placement for the auto-assign control | The contract C1–C7 is fixed. The control is built only after EP1.19 records placement. Nothing else waits on it | EP1.19 |
| `leadCapPermille`, `leadCapTolerancePermille`, `shapeCapPermille` | Working values read off the measure artifact, labelled "working values", as the file's own `_meta` sanctions | a later balance publish |
| Lean weights (`specialisation`, `pure`, `threatRung` = 0, `crowdingFactor`) | Zero first (byte-identical), then a first-guess balance publish | a later balance publish |
| `xpCurve.empire` `{first: 10, step: 5}`, `awards.speciesLevelUp` = 1, `freeRespecsPerEmpireLevel` = 1 | The spec's working values | a balance publish |
| Unique respec price keys | Equal to the species keys (50 / 500 / 3) | a balance publish |
| `injury-tiers` not landed | A fallen commander member is detached and set `Recovering` (the delve's non-lethal default) | `deployment-hierarchy` `injury-tiers` |
| `sector-development` not landed | `ai-build-scorer` stays deferred. The AI takes the ladder's first legal rung | EP5.1–EP5.3 |

## Spec content not turned into a task (and why)

- **`ai-build-scorer`** is written as deferred tasks EP5.1–EP5.3, not scheduled. Its own spec forbids
  building it over neutral needs: a complete, tested mechanism whose content is a constant.
- **The asks filed with `aura-skill`, `party-dungeon` and `base-defense`** belong to those programs.
  They are cross-referenced above, not tasked here.
- **The `save-identity` consumer-row edit** (X13: the stock ledger is keyed for every empire) is
  `solid-enforcement`'s doc. It is noted in EP4.5's acceptance so the builder files it, but it is not
  an EP task.

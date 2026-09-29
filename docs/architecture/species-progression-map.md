# Capability map: `species-progression`

**Status:** capability map + module specs, 2026-09-18, **strengthened the same day** (adversarial pass:
code re-verified, R1–R4 and R16–R19 applied, `save-identity` keying, the one re-bless ordered, cache
triggers completed). **Specs only. No build authorized** until the owner reviews this map (module
boundaries, dependency direction, build order). Its three original OWNER questions were answered by
[spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) R1, R2 and R3, applied in §7; the strengthen pass
raised **one** new owner question (§7, OQ-S1), **answered by R21** the same day (a tunable weight per
layer; session `rulings-r20-r24-20260918`). R23 (Zomboss's pool mirrors the player's) is applied to
`zomboss-commander-clock`.

**Source:** [species-progression-ideal.md](species-progression-ideal.md) — owner rulings **R-S1–R-S4**
(2026-09-17) and the two corrections of 2026-09-18 are binding and are not reopened here.
**Module specs:** [species-progression/](species-progression/), one per module id below.
**Plan / tasks (not yet written):** `tasks/species-progression-plan.md` / `tasks/species-progression-todo.md`.

---

## 1. What this program is, in one paragraph

Layers **1b** (player-modified species, per `(player, species)`, append-only) and **2b** (empire species
progression, per `(empire, species)`, re-projected on level change) of the actor layer stack
(`decisions.md` **Actor layer stack** row), built as the ideal's **one projector mechanism** serving 1a,
1b and 2b (R-S3), delivered into the one `ActorHub` fold on every compose path, plus Zomboss's commander
clock from lawn-run outcomes (R-S2 part 1). A species level grants **allocation** (R-S1) — the same
aptitude-shaped points a specimen gets, through the same selection rule — and general and unique
creatures share that one progression, differing by equipment and the layers above it (R-S4).

## 2. What already landed elsewhere (reconcile, do not duplicate)

`solid-remediation` is an active program and owns its own documents; this map references them and
specs only what they do not cover.

| solid-remediation item | What it landed (verified in code this session) | What it leaves for this program |
|---|---|---|
| T4.1 S1/S3 — empire on the species key ([spec-species-empire-scope.md](solid-remediation/spec-species-empire-scope.md)) | `SpeciesAllocation.ScopeKey(playerId, empire, speciesId)` (`SpeciesAllocation.cs:28-31`), `EmpireForSide` (`:38-39`), the resolve seam (`SpeciesAllocationSource.cs:106-116`), the transport delegate (`CheatState.cs:182-185`) | Zomboss owns no rows, so a lawn zombie resolves `Empty` on every term (`RpgStore.Aptitudes.cs:229-233`, `:266-267`). R1: Zomboss's empire earns them, written by `empire-progression` `ai-empire-species`; R3: keyed `(SaveId, EmpireId)`, so T4.1's interim key under the human's player id (`SpeciesAllocation.cs:28-31`) is re-keyed by `solid-enforcement` `save-identity` |
| T4.2 — species cache trigger set | Three triggers through one fetch (`RpgClient.cs:554-569`) | Three new edges: a species level-up and a 1b write (this program creates both), and the **save switch** — under R3 the cache holds one save's rows, so `PUT /api/players/current` (`gk-core/src/FusionRpg.Server/Program.cs`, which broadcasts nothing today) is its key-set edge. All three in `species-layer-delivery` (triggers 4–6) |
| T4.3 D9 — kill attribution | `KillAttribution.EmpireOf` | Nothing — attribution is the fact; who earns is R1 (the side's empire) |
| T4.4 S2 — species term in battle | `RpgStore.WorldTurns.cs:581-593` builds `commander + species + specimen` | **A leak, see §6 C1** — `layer-source-selector` |
| T4.4 S7 — a level-4 type composes like level 1 | **Not closed; owner-deferred** to the *species level-up grants* sub-program (ideal, "Deferred sub-program") | Tracked here as a deferred row, not specced (§3) |
| T4.5 S5 — `MaterialisePlayerSpecies` caller | An eager boot roll (`gk-core/src/FusionRpg.Server/Program.cs:725-728`) | **Contradicts the "delay the roll" ruling and re-darkens picks, see §6 C2** — `species-mod-ledger` |
| T4.6 S4 — picks reach a stat | `SpeciesPassiveAtomSource` joined into the sheet compose only (`UniqueActorHubCompose.cs:65-68`) | 1b reaches no lawn actor and no battle actor; its SourceId is minted outside `ContributionSourceIds` (§6 C3) — `species-layer-projector`, `species-layer-delivery` |
| T4.6 S6 — second carrier | Deletion refused: `trait.species-magnitude-{id}` is live | Nothing; the 1a magnitude half stays with its owners (§5) |

## 3. Modules

| # | Module id | Responsibility | Depends on | Gate |
|---|---|---|---|---|
| 1 | [`layer-source-selector`](species-progression/spec-layer-source-selector.md) | One Core rule that decides, per actor, whether it carries 2a or 2b and which empire it reads; every compose path calls it instead of re-deriving it | — | none |
| 2 | [`ladder-scale-parity`](species-progression/spec-ladder-scale-parity.md) | One `P(Θ)` scaling function shared by the aptitude magnitude read and the atom compiler's `powerLadder` `kMicro` branch, so a projected atom and a live resolve are the same arithmetic | — | none |
| 3 | [`species-layer-projector`](species-progression/spec-species-layer-projector.md) | The one projector (R-S3): numeric state → Θ-free projected rows → container, for 1a (species-passive core), 1b (a ledger instance) and 2b (an allocation). New `ContainerKind` and GG-49 SourceIds | 1, 2 | none |
| 4 | [`species-mod-ledger`](species-progression/spec-species-mod-ledger.md) | Layer 1b's own append-only table with provenance, **born keyed `(save_id, empire_id)`** (`save-identity` G3); fusion picks repointed into it; the roll delayed (deterministic preview, never eager) — **closes the production bug C2**; `player_species` retired | 3; external `save-identity` **first slice only** (`SaveId`, `EmpireRef`, `rpg_save_empires`, `HumanEmpireOf` — no Tier A migration) | that slice |
| 5 | [`empire-species-container`](species-progression/spec-empire-species-container.md) | Layer 2b persisted as a per-`(SaveId, EmpireId, species)` container holding the species term **alone** (R2), re-projected exactly once per level/override/tuning/projector change through **one** hook for every empire, withdrawn when empty | 1, 3; external `save-identity` | external `save-identity` (R3) |
| 6 | [`species-layer-delivery`](species-progression/spec-species-layer-delivery.md) | Three ordered steps. **6.1** the per-layer resolve in the one aptitude resolver — R2 and R16 for general, Bound, sheet, web squad and world-turn actors at once — and the program's **one explained re-bless**. **6.2** one registered `IActorStatSubsystem` delivers 1a/1b rows to lawn, sheet and battle. **6.3** the 2b cutover, value-neutral by parity. The lawn cache's full trigger set | 6.1: 1 + `action-enrich` `action-base`'s re-bless; 6.2: 4; 6.3: 5 | 6.3 inherits module 5's |
| 7 | [`zomboss-commander-clock`](species-progression/spec-zomboss-commander-clock.md) | R-S2 part 1: Zomboss's commander level advances from lawn-run outcomes on the existing XP machinery, on Zomboss's empire of the run's save (R3), and is readable as `Θ_content`'s `zombossLevel` input | external `save-identity` | external `save-identity` (R3) |

**Not specced, tracked here so they are not re-derived:**

| Row | Why it has no spec | Unblocked by |
|---|---|---|
| `species-level-grants` | **Owner-deferred sub-program** (ideal §"Deferred sub-program", 2026-09-17: *"track it and defer"*). Closes S7. Carries the seedsmith distribution-matrix extension | The owner scheduling it |
| `zomboss-species-xp` | **Ruled R1** (zombie species XP → Zomboss's empire). Specced once, in `empire-progression` [`ai-empire-species`](empire-progression/spec-ai-empire-species.md), which owns the crediting branch (both zombie XP paths) and the one level reader `SpeciesLevelOf`; storage is `save-identity`'s one re-keyed `rpg_actor_progression` (the separate AI table is superseded there). This program consumes the rows through module 5's single trigger-1 hook and does not re-specify them | `ai-empire-species` building |
| Species XP outside the lawn (ideal R5) | R-S2: *"for now, only lawn run can ship"* | A later program |

Build order:

```text
layer-source-selector (C1 fix) ─┬──────────────────────────────────────────► delivery 6.1  (THE re-bless:
[action-enrich action-base re-bless] ───────────────────────────────────────┘                R2 + R16)
ladder-scale-parity ─┐
selector ────────────┴─► species-layer-projector ─► species-mod-ledger ──────► delivery 6.2  (1a/1b)
[save-identity first slice] ────────────────────────┘
                                     projector ─► empire-species-container ──► delivery 6.3  (2b cutover,
[save-identity] ────────────────────────────────────┘   (R3 key)                              value-neutral)
[save-identity] ─► zomboss-commander-clock
empire-progression ai-empire-species (R1) ─► Zomboss rows reach module 5 through its one trigger-1 hook
```

No OWNER gate remains (OQ-S1 ruled R21). The external gates: `solid-enforcement` `save-identity`
(R3) — its **first slice** for module 4, the whole module for modules 5 and 7 — `empire-progression`
`ai-empire-species` (R1), which routes Zomboss's species awards, and `action-enrich` `action-base`, whose
golden re-bless precedes step 6.1. Modules 1–3 wait on none of them. R-S3 ("1b and 2b ship together") is
satisfied at the program boundary: the program is not done until 6.2 and 6.3 are both delivered.

**C2 is a live production bug** (picks refused for every eligible species), and its fix (module 4) waits
on `save-identity`'s first slice, because `save-identity` G3 rules the 1b table is born keyed
`(save_id, empire_id)`. That slice is additive (a new table seeded per save, two seams, no key rewrite),
so this program **requests** that `solid-enforcement` build it ahead of its Tier A migration; the request
is recorded in §9 for that program's map. No interim fix is offered: removing the eager roll alone would
re-darken picks the other way (`picks.source-not-materialised`, ideal W5).

### Re-bless order (decided in the strengthen pass)

Three changes move pinned composed values. They land in this order, each in its own commit naming its
reason, and none re-blesses another's values:

| # | Change | Class | Why here |
|---|---|---|---|
| 1 | `action-enrich` `action-base` ([spec](action-enrich/spec-action-base.md), acceptance 4) | re-bless (its own ruling) | no dependency; changes the damage formula itself. Aptitude edges target `progression.bonus.atk`, so re-blessing the split first would explain `atk`-driven damage that this change then moves again |
| 2 | `layer-source-selector` C1 | **defect correction**, not a re-bless | removes the leaked species term from world-turn uniques; must precede 3 or those uniques move twice |
| 3 | `species-layer-delivery` step 6.1 | **the one re-bless** (R2 + R16) | covers general, Bound, sheet, web squad and world-turn actors in one commit, through the one resolver |

`ladder-scale-parity`'s at-most-one-unit atom rounding is not in this list: if it moves a golden it stops
at its own Ask-first. Steps 6.2 and 6.3 never re-bless (6.2 delivers new layers, 6.3 is value-neutral).
`action-enrich`'s map must record the same order for item 1 (its spec defers to "the map's §Golden
re-bless order"); that entry is owed by that program's session.

### Tuning versions (sequenced, never pinned)

`zomboss-commander-clock` publishes two keys into `progression`. So do `empire-progression`
`empire-level` (R19: `xpCurve.empire`, `awards.speciesLevelUp`) and `creature-lawn-deploy`
`lawn-deploy-progression`. No spec names a literal version: each publishes `publish.py`'s next
`progression.v{n+1}` at its own build, whichever lands first; no two are hand-merged into one file.

## 4. The five layer questions, answered (DESIGN-GATE §1 actor-layer row)

| | **1a — base species (species-passive core only)** | **1b — player-modified species** | **2b — empire species progression** |
|---|---|---|---|
| 1. Which layer | 1a, already in the closed list | 1b, already in the closed list | 2b, already in the closed list |
| 2. Scope | global, one row per species | per `(SaveId, EmpireId, species)` — the empire that paid (`save-identity` G3); zombies read Zomboss's (none — Zomboss does not fuse) | per `(SaveId, EmpireId, species)` (R3); plants read the human empire, zombies Zomboss's (R1) |
| 3. Lifetime | frozen (generator output) | append-only; most players have no row for most species | mutable level/override; re-projected on change |
| 4. Carrier | the seedsmith `species-passive.{id}` container's fixed `atoms` | a ledger instance (`effect_instance`) referenced by `rpg_player_species_mod` (new, keyed `(save_id, empire_id)`) | a `species-progression.*` container (new kind) |
| 5. SourceId (GG-49, §8.1 amendment owed) | `species-base:{speciesId}` (new) | `species-player:{speciesId}:{mechanism}` (new; replaces T4.6's `species-passive:{speciesId}`) | `species-empire:{empireToken}:{speciesId}:{aptitudeId}` (new) |

All three are delivered by one registered `IActorStatSubsystem` (carrier kind 2 of the two legitimate
ones) reading one projected-row shape. None reads another layer's composed value.

**2a and the commander are not in this table, but R16 touches them.** Their points stay in `rpg.aptitude`;
step 6.1 makes every `AllocationScope` resolve alone and mints `aptitude.{scopeText}.{Share}` for every
scope but `Commander`, which keeps `aptitude.{Share}`. That is the program's fourth §8.1 row.

## 5. Out of scope, with the owner of each

| Item | Owner |
|---|---|
| Layer 1a **magnitudes** (`trait.species-magnitude-{id}`, bound to uniques at deploy) and their reach to general lawn actors | `species-gear-chain` (binder) · `lawn-tuning-profile` `species-flavour-lawn` (general lawn carrier, bake quality R6) |
| Whether 1a should become one container instead of two (`species-passive` + `trait.species-magnitude`) | cross-program consolidation named by S6's disposition; not decided here |
| Who fills 2b shares (auto-assign, AI assignment, build favour pipeline) | `empire-progression` (its ideal: *"this document owns who fills the shares"*) |
| A closed layer registry / provenance assertion | `actor-layer-compose` follow-ups |
| Battle-engine reconcile (effect hits bypass the resolver) | deferred by the owner (ideal §"What this deliberately does not decide") |
| Θ freshness (L5), lawn zombie Θ | `lawn-tuning-profile` / power program |
| Wild-faction world forces | `creature-system-map.md` species-gear-chain ask #1 (a third creature category) |

## 6. Contradictions found while verifying (code beats docs)

| # | Where | Contradiction | Disposition |
|---|---|---|---|
| **C1** | `RpgStore.WorldTurns.cs:568-593` | T4.4's S2 fix hands a **unique** member (`InstanceId` set — `WorldState.cs:277-278`: *"Roster specimen"*) `commander + species + specimen`, i.e. **both 2a and 2b**. Violates `decisions.md` *Creature progression source* row (*"never receives the empire species fallback"*), `actor-hub-ssot.md` §8.2, and the ideal's own 2a/2b exclusivity table | Technical defect, fixed by `layer-source-selector` (one selection rule, SOLID-S/DRY) |
| **C2** | `gk-core/src/FusionRpg.Server/Program.cs:725-727` + `RpgStore.Fusion.cs:237-238` + `:243-244` | T4.5 eagerly materialises every species that has a `species-passive` container at boot. Picks require the output species to have that container (`picks.no-target-container`) **and** not to be materialised yet (`picks.already-materialised`). Every eligible output is therefore already materialised for the current player: **picks are refused in production for every species that can take them**. It also contradicts the 2026-09-16 ruling *"don't make roll gone but delay it"* (`decisions.md` Actor layer stack: *"the roll is delayed, not removed, and a player who never fuses has no row at all"*) | Ruled already; fixed by `species-mod-ledger` (delayed deterministic preview + ledger). `spec-player-materialise.md`'s eager trigger is superseded by that ruling and owes an amendment (not in this session's paths) |
| **C3** | `SpeciesPassiveAtomSource.cs:42` (retired by SP3.6 — file gone, superseded by `SpeciesLayerProjector`) vs `ContributionSourceIds.cs` / `actor-hub-ssot.md` §8.1 | T4.6 mints `species-passive:{speciesId}` locally; §8.1 says *"Producers must mint via the helpers above"*, and no `FictionLabel` arm exists. The same id would also be ambiguous between 1a and 1b once 1a binds `species-passive` | Fixed by `species-layer-projector` (three `ContributionSourceIds` helpers + §8.1 amendment) |
| **C4** | Ideal "The shape" / `actor-layer-compose-ideal.md` OQ1 (*"The math does not change; where it runs does"*) vs `AptitudeAllocation.cs:118-122` and `CheatState.cs:55` | `Share` normalises over the **merged** commander + species total, so a 2b contribution is not separable from the commander term: projecting 2b as an independent container **changes numbers** for every general actor whose commander has points | **Ruled R2:** 2b resolves alone; numbers change once, with one explained re-bless owned by `species-layer-delivery` |
| **C5** | Ideal line 81 / `actor-layer-compose-ideal.md` ("zombies read player 3's rows", `EnsureZombossPlayer` `RpgStore.ZombossDeploy.cs:25-29`, one row found by name) vs T4.1 `ScopeKey` (`SpeciesAllocation.cs:28-31`: Zomboss's empire keyed **under the human player's id**) | Two incompatible answers to "whose row is Zomboss's progression": one global row shared by every save slot, or one Zomboss empire per human player | **Ruled R3:** neither. A Save owns its empires, keyed `(SaveId, EmpireId)`; Zomboss stops being a player row. Specified by `solid-enforcement` `save-identity`; both readings in the ideal and T4.1 are superseded |
| **C6** | `AtomCompiler.cs:618-624` vs `AptitudeReadFunctions.cs:48-68` | The same `k · P(Θ)` product is computed twice with different arithmetic: truncation and an unwidened `long` multiply (`kMicro`), and a checked `(int)` narrowing (`kMilli`), against decimal-widened round-away-from-zero | Technical; `ladder-scale-parity` unifies the `kMicro` branch. The `kMilli` `(int)` narrowing is a cap under the repo's caps rule and is **filed for the overflow audit, not fixed here** |
| **C7** | Ideal R2 / `actor-layer-compose-ideal.md` L1 ("0 authored", "`Magnitudes` empty") | Stale: 904 of 906 species carry magnitudes and the magnitude carrier is live (spec-species-carrier §S6) | Already recorded by solid-remediation; nothing owed |
| **C8** | Ideal tunables table ("Zomboss's progression clock → `species-progression.v{n}`") vs `tunables-ssot.md` §2 ("belongs to whichever **owns the concept**") | Zomboss's clock is a `player`-kind XP award, which `progression.v1.json` `awards` owns | Technical; `zomboss-commander-clock` publishes into `progression`, not `species-progression` |
| **C9** | `decisions.md` — 'Class system (2026-08-26)' *Class system* (*"`share` is taken **on the sum**, never per scope"*), `AptitudeAllocation.cs:17-21`, `CheatState.cs:51-54` vs R2 + R16 | The locked merge contract and two code comments state the opposite of the rulings | Ruled; step 6.1 changes the one resolver and rewrites both comments. The `decisions.md` row landed 2026-09-18 (§9) |
| **C10** | `UniqueActorHubCompose.cs:48-49` (sheet: the human commander for **any** human-owned unique) vs `SpeciesAllocationSource.cs:114-116` (lawn: commander only for a plant-side ctx) | A zombie-side human-owned unique composes a commander term on its sheet but not on the lawn — a two-path disagreement of the kind C1 was | Technical; `layer-source-selector` keys a specimen's empire by its **owner** (`save-identity` G5), so both paths answer as the sheet does (R4: the side's commander applies side-wide) |
| **C11** | T4.2's `The_key_set_edge_is_resolved_per_read_and_therefore_needs_no_fourth_trigger` and `A_match_edge_is_not_a_species_trigger_…` vs R3 | Once the cache holds a save's rows, a save switch moves the whole key set; nothing fires on `PUT /api/players/current` today | Technical; `species-layer-delivery` trigger 6, tested in both orders, plus the mid-run rule from `decisions.md` "Mid-match switch" |

## 7. OWNER questions

The three this map raised are answered below. The strengthen pass raised one, now **ruled R21**:

**~~OQ-S1~~ Ruled R21 — does any layer weighting survive resolve-alone?** `decisions.md` — 'Class system (2026-08-26)' (*Class system*) weights
scopes *"commander smallest, unique largest — a commander allocation replicates across the whole roster,
so a dominant one is the worst case"*, and that weighting works only through the merged denominator.
Both aptitude reads depend on a layer's **share**, never its point total (`AptitudeReadFunctions.cs:33-44`,
`:48-68`), so once each layer resolves alone (R2, R16) a commander with a single point contributes a full
layer's worth of every funded edge to every actor on the roster, and the per-scope point rates
(`aptitudes.v8.json` `pointEconomy.aptitudePointsPerThetaMilliByScope`) no longer weight one layer against
another. **Question:** is the class-system weighting intent retired by R2/R16, or should each layer carry
a weight (a tunable in `aptitudes.v{n+1}`, never a const)? ~~**Default if unanswered:** retired~~
**Ruled R21 (2026-09-18): a tunable weight per layer** (commander, species, specimen) in tuning, so the
intent is kept as data; step 6.1's re-bless measures it. Applied in
[spec-species-layer-delivery.md](species-progression/spec-species-layer-delivery.md) § *Per-layer weight
(R21)*: key `read.layerWeightMilliByScope` (`commander` / `creatureType` / `aspect` / `uniqueCreature`,
per-mille) in the next `aptitudes` revision published by `gk-core/tools/tuning/publish.py`; applied to each
layer's read output in the one resolver (`AptitudeResolver.cs:23`); defaults **500 / 667 / 667 / 1000**
= the shipped rate table `{3,4,4,6}` (`aptitudes.v8.json:25-28`) normalised to its largest scope; the
weight ships inside the one 6.1 re-bless, whose table reports each layer's weighted and unweighted
contribution.

### Rulings applied 2026-09-18

Source: [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) (binding, not reopened here).

| Was | Ruling | What changed in this program |
|---|---|---|
| **Q1** — 2b alone or merged with the commander? (C4) | **R2: alone.** *"Each species container resolves only its own points; the commander is its own layer. General actors' numbers change once, with one explained re-bless"* | `empire-species-container`: gate lifted, projects the species term only, the commander-reallocation trigger retired. `species-layer-delivery`: cutover is the standalone shape; the one re-bless is specified (§"The one explained re-bless"). `species-layer-projector`: input named, no behaviour change |
| **Q2** — zombie species XP to Zomboss? | **R1: Zomboss's empire.** Plant species progress for the player's empire, zombie species for Zomboss's | `zomboss-species-xp` row closed and pointed at `empire-progression` `ai-empire-species` (one spec, not two). The owner's acceptance sentence now holds for zombies as well as plants, once that module credits them. `species-layer-delivery`'s cache answers both empires from the first build |
| **OQ-S1** — does any layer weighting survive resolve-alone? | **R21: a tunable weight per layer**, kept as data, measured by 6.1's re-bless | `species-layer-delivery` step 6.1: `read.layerWeightMilliByScope` in the next `aptitudes` revision, applied in `AptitudeResolver`; re-bless table reports the per-layer effect; `decisions.md` — 'Class system (2026-08-26)' amendment text in §9 — landed in decisions.md *Class system* 2026-09-18 |
| **R23** — Zomboss's commander pool: assign-ladder default and side-wide like the player's (R4)? | **R23: yes, mirror the player** | `zomboss-commander-clock`: the pool `zomboss:{save}` gets the assign-ladder computed default and applies side-wide to his members; keyed `(SaveId, EmpireId.Zomboss)` |
| **Q3** — Zomboss one global row or one per save? (C5) | **R3: add a save identity.** A Save owns its empires, keyed `(SaveId, EmpireId)`; the player row stops doubling as an empire; Zomboss stops being a player row | `zomboss-commander-clock` and `empire-species-container` now depend on `solid-enforcement` `save-identity` and are keyed `(SaveId, EmpireId)`. Neither option (A) nor (B) is built |

### Gaps and contradictions the rulings expose

Named so they are not re-derived; none is fixed by this program unless its row says so.

| # | Where | Finding | Owner |
|---|---|---|---|
| **G1** | R2 vs `SpeciesAllocationSource.cs:122` and `RpgStore.WorldTurns.cs:590` | R2's reason (*"the commander is its own layer"*) applies to 2b only as ruled. A Bound unique still resolves `commander + unique` as one merged allocation on the lawn, and a battle unique `commander + species + specimen`; so layer 2a still shares the commander's denominator. The species half of the battle line is removed by `layer-source-selector` (C1); the 2a merge is not ruled and is **not** changed here | ✅ **Ruled R16 (2026-09-18): 2a resolves alone too.** Commander, species and specimen each resolve only their own points; `species-layer-delivery`'s one explained re-bless covers Bound and battle uniques as well |
| **G2** | R1 vs `RpgStore.Progression.cs:31-45` (per-placement award, fed by `RpgXpAwardMap.cs:68-71`) and `:113-120` (run completion) | **Both** zombie species XP paths credit `playerId`. R1 needs both re-routed to Zomboss's empire, not only the run-completion one | ✅ **Closed in spec:** `ai-empire-species` names both paths (its crediting table) and writes both through the one re-keyed `TryApplyXpUnlocked`; `empire-species-container` trigger 1 is that single hook, so both paths re-project Zomboss's 2b with no second hook |
| **G3** | R3 vs `species-mod-ledger` (`rpg_player_species_mod(player_id, …)`) | Layer 1b is keyed by player. Whether a player's fusion picks belong to the player or to the save's player empire is a `save-identity` keying decision | ✅ **Decided by `save-identity` G3 and applied (strengthen pass):** 1b belongs to the empire that paid; the table is born keyed `(save_id, empire_id, …)`; module 4 depends on `save-identity`'s first slice |
| **G4** | R3 vs `ApplyRpgProgressionFromActivityUnlocked(db, playerId, runId, …)` (`RpgStore.Progression.cs:20-23`) and the fetch `/api/aptitudes/{playerId}` (`AptitudeEndpoints.cs:155`) | Runs, progression facts and the injector's one fetch are keyed by player. Every R1/R3 write needs the run's save; the fetch needs the save's empires | `save-identity` (run→save mapping; route key) |
| **G5** | R3 vs `MintForZomboss` (`RpgStore.ZombossDeploy.cs:42-47`) and `SpecimenOwnershipOracle.cs` | Zomboss's uniques are minted under his player row, and ownership is told apart by `player_id`. Retiring Zomboss's player row reaches the `zomboss-deploy-ai` ownership model | `save-identity` |

## 8. Seedsmith and generators, per module

Another active session (`creature-seed-rederive-20260918`) owns `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/**`
code; any change there is a coordination dependency, never an edit from this program's build.

| Module | Generated content it touches | Stage | Change |
|---|---|---|---|
| `layer-source-selector` | none | — | none |
| `ladder-scale-parity` | none (tree-binder's committed `kMicro` corpus is read unchanged) | `gk-forge/tools/TreeBinder` | none |
| `species-layer-projector` | reads `species-passive.*` containers and `_species-build-plan.json` | seedsmith `species-effects` (`adapters/creatures/effects/prompts.py:114`, id prefix `:24`); `gk-forge/tools/CreatureBuildPlanGen` (`SpeciesBuildPlanner`) | none — consumer only |
| `species-mod-ledger` | reads `species-passive.*` pools for the delayed preview roll | seedsmith `species-effects` | none |
| `empire-species-container` | reads `_species-build-plan.json` shares | `gk-forge/tools/CreatureBuildPlanGen` | none |
| `species-layer-delivery` | none | — | none |
| `zomboss-commander-clock` | none | — | none |
| `species-level-grants` (deferred) | the primary-stat distribution matrix per build favour | seedsmith deterministic engine / `SpeciesBuildPlanner` | owed by that sub-program |

No module adds or changes a seed field, so no module owes a regeneration. The consumer modules name the
input checks to run when a generator's output changes (`dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`,
`gk-forge/tools/seedsmith/tests/test_species_effects.py`); generated `species-passive` and plan content is never
hand-edited to make a projection or a pick work.

## 9. Amendments owed by other sessions (exact lines; not edited here)

`solid-remediation-20260917` is **active** and owns its documents and `decisions.md`; `tests/**` is also in
its paths. This program reads them and never edits them. Each line below now contradicts a ruling or
this program's specs and must be amended **by the session that owns it**, in the same change that lands
the named module (or earlier).

| File:line (2026-09-18) | Now says | Contradicted by | Amend to | Owner / when |
|---|---|---|---|---|
| `docs/architecture/decisions.md` — 'Class system (2026-08-26)' (*Class system*) | *"weighted **commander smallest, unique largest** … `share` is taken **on the sum**, never per scope"* | R2, R16, R21 | **Amendment text (R2/R16/R21, 2026-09-18):** *"⚠️ AMENDED 2026-09-18 (rulings R2, R16, R21): each allocation scope (layer) — commander, creature type (species), aspect, unique creature (specimen) — resolves **alone**, its `share` taken over that scope's own total, never on the sum. The ordering **commander smallest, unique largest** is kept as data: a tunable per-layer weight `read.layerWeightMilliByScope` in `data/tuning/aptitudes.v{n}.json` scales each layer's read output in `AptitudeResolver` (defaults 500 / 667 / 667 / 1000). Applied by species-progression `species-layer-delivery` step 6.1 in one explained re-bless."* | ✅ **landed in decisions.md *Class system (2026-08-26)* 2026-09-18** (merged with `empire-progression` P4 into one amendment, parts (a)/(b); owner-authorised docs session `decisions-rows-20260918`). The row is now at line 122 |
| `docs/architecture/decisions.md:52` (*Actor layer stack*) | *"1b player-modified species (per `(player, species)` …)"* | R3 → `save-identity` G3 | per `(save, empire, species)`, the empire that paid | ✅ **landed in decisions.md *Actor layer stack (2026-09-16)* 2026-09-18** (amendment clause at the row's end; session `decisions-rows-20260918`) |
| `docs/architecture/solid-remediation/spec-species-carrier.md:16`, `:38-50`, `:65`, `:84`, `:187` | S5 fixed by an eager `Program.cs` caller; success criterion *"`MaterialisePlayerSpecies` has a production caller, and a test that fails if it loses one again"* | the 2026-09-16 *"delay the roll"* ruling (`decisions.md:52`); map C2 | T4.5's eager caller superseded; S5 closed by `species-mod-ledger` (delayed preview + ledger) | solid-remediation session; with module 4 |
| `docs/architecture/solid-remediation/spec-species-carrier.md:150` | GG-49 id `species-passive:{speciesId}` | map C3 | retired; `species-base:` (1a) + `species-player:` (1b) | solid-remediation session; with module 3 |
| `docs/architecture/solid-remediation/spec-species-empire-scope.md:75` | Zomboss's species key under the human's `playerId` (`ScopeKey(playerId, empire, …)`) | R3 | re-keyed by `save-identity` (`EmpireRef` encoder; the persisted strings stay) | solid-remediation session; with `save-identity` |
| `docs/architecture/solid-remediation/spec-species-empire-scope.md:150-165` | *"that set is exactly `{Dave}`"*; adding the empire *"added **no** fourth trigger"*; `The_cache_holds_exactly_one_empires_rows_…` | R1, R3; map C11 | every empire of the save from the first build; the save switch is a key-set trigger | **✅ delivery 6.2 landed 2026-09-20 (SP6.2-SP6.9), handed to `solid-remediation` to apply.** `speciesLayers.mod` (SP6.3, `RpgStore.SpeciesLayerTransport`) is keyed by every empire of the save with ledger rows, never `{Dave}` alone; the save-switch key-set trigger is built (SP6.6: `PUT /api/players/current` broadcasts `AptitudesUpdated(scope: "save")`). `gk-core/tests/FusionRpg.Guard.Tests/SpeciesAllocationCacheTriggerTests.cs`'s own `The_cache_holds_exactly_one_empires_rows_and_refuses_to_answer_for_another` is REPLACED by `The_cache_answers_each_side_from_its_own_empire_and_never_the_other` (proving the NEWER `speciesLayers` cache, not the retired claim about the OLD `_speciesAllocations` cache this line's citation named). `solid-remediation` still owns applying the amend-to text to its own file |
| `docs/architecture/solid-remediation/spec-species-empire-scope.md:175-179` | *"a match edge is not a species trigger"* | R3 + `decisions.md:81` *Mid-match switch*; map C11 | true except the `board.start` after a mid-run save switch | **✅ delivery 6.2 landed 2026-09-20 (SP6.6), handed to `solid-remediation` to apply.** `MatchHost.Apply`'s `board.start` block now consumes a deferred save-switch flag (`_pendingSaveSwitchRefresh`), the one real exception; `A_match_edge_is_not_a_species_trigger_and_the_trigger_set_was_not_copied`'s own comment (same Guard.Tests file) is amended to name it. `solid-remediation` still owns applying the amend-to text to its own file |
| `docs/architecture/solid-remediation-map.md:109` | S5 *"fixed — T4.5"* | map C2 | S5 re-darkened by T4.5 (picks refused); closed by `species-mod-ledger` | solid-remediation session; now |
| `tasks/solid-remediation-todo.md:697` (T4.5), `:963` | eager caller restored; *"Fusion picks change a player's actors"* ticked | map C2 | note the re-darkening and the owning fix | solid-remediation session; now |
| `docs/architecture/creature-seed/spec-player-materialise.md:52` | *"the new ones are rolled on next load and appended"* | the 2026-09-16 ruling | superseded: no eager roll; the delayed preview | creature-seed program (no active session claims it); with module 4 |
| `docs/architecture/actor-hub-ssot.md` §8.1 (table at `:818-828`) | no `species-base:` / `species-player:` / `species-empire:` rows; `aptitude.{Share}` only | modules 3 and 6.1 | three species rows + `aptitude.{scopeText}.{Share}` | the building session, in each module's change |
| `docs/architecture/actor-hub-ssot.md:836` (§8.2) | *"`commander + UniqueCreature(instanceId)`"* (merged) | R16 | commander and `UniqueCreature` each resolve alone | the building session; with step 6.1 |
| `docs/architecture/solid-enforcement-map.md` (`save-identity` row) | build order: `save-identity` whole, Wave 4 | this map §3 (C2 waits on it) | ship `save-identity`'s first slice (types, `rpg_save_empires`, `HumanEmpireOf`) ahead of its migration | `solid-enforcement` session; a request, not a ruling |
| `docs/architecture/action-enrich-map.md` (its "Golden re-bless order") | not yet written | this map §3 "Re-bless order" | `action-base` first; `species-layer-delivery` 6.1 after it | `action-enrich` session |

## 10. DESIGN-GATE §5 checklist

```
[x] Subsystems: Stats / ActorHub, actor layer stack, Power, Tunables, Creature (general vs unique,
    seed generation), Effect atoms/containers, Data.
[x] Session boundary recorded: tasks/sessions/species-progression-spec-20260918.json;
    session-boundary-check.py reports no drift involving this record's paths.
[~] §1 rows read this session: the-game.md, the-loops.md, DESIGN-GATE.md, actor-layer-compose-ideal.md,
    creature-system-map.md, decisions.md (ActorHub sole Hot, Actor layer stack, Creature progression
    source, SOLID rows), actor-hub-ssot.md §6 and §8/§8.1/§8.2, stat-system.md (first half),
    software-architecture.md §3-§6, ssot-power-scale.md §5 and §10.1, tunables-ssot.md §2-§3,
    empire-progression-ideal.md (gaps, shape, still-open), both solid-remediation specs and its T4.x
    task records. NOT read in full this session: design/spec-derived-stat-sheet.md,
    design/spec-magnitude-and-units.md, combat-power-number-ideal.md, creature-seed-map.md,
    contributing/session-boundary.md, effect-atom/definitions.md. Claims touching those are
    code-verified, not doc-verified.
[x] decisions.md checked: Actor layer stack, ActorHub sole Hot, Creature progression source rows.
[x] Every factual claim cites file:line; audit-doc-citations.py run on every file written.
[x] Verified against code, not comments (C1-C8 are code-vs-doc findings).
[x] Surrounding sections read for every quoted rule.
[ ] Constraints tested: none claimed. "Goldens move" is NOT asserted anywhere; ladder-scale-parity
    requires running the suites before any such claim.
[x] No §2 invariant contradicted; §2.16 trigger sets enumerated in species-layer-delivery.
[x] No population counts pinned; closed vocabularies pinned with reasons.
[x] ActorHub: every contribution goes through one registered IActorStatSubsystem with GG-49 ids.
[x] No SOLID-violating path extended: C1 and C3 are fixed before anything builds on them.
```

**Strengthen pass, 2026-09-18** (session `strengthen-sp-20260918`), re-run of the same checklist:

```
[x] Session boundary: tasks/sessions/strengthen-sp-20260918.json; paths = this map, the ideal and the
    seven specs; no path an active session claims.
[~] §1 rows read this session: DESIGN-GATE.md §1/§2/§5, actor-hub-ssot.md §8.1-§8.3, decisions.md
    rows Players, Mid-match switch, Actor layer stack, Class system; spec-rulings-2026-09-18.md;
    spec-save-identity.md (classification, contracts, seams, G3-G5, consumers); spec-action-base.md;
    spec-commander-identity.md (types, literal sweep); spec-ai-empire-species.md (crediting);
    spec-empire-level.md (tuning); both solid-remediation species specs. Not re-read this session:
    stat-system.md, actor-layer-compose-ideal.md, ssot-power-scale.md, tunables-ssot.md (read by the
    first pass; no claim here depends on a part of them the first pass did not cite).
[x] Every file:line in the seven specs and this map re-checked against code on features/mega-merge;
    drifted ones corrected (Program.cs:725-728, UniqueActorHubCompose.cs:84, others unchanged).
[x] Verified against code, not comments: C9-C11 are code-vs-doc findings; the eager-roll bug (C2)
    re-traced through RpgStore.PlayerSpecies.cs:57-78 and RpgStore.Fusion.cs:237-244.
[~] Constraints tested: one reading taken (every committed passive-tree kMicro is non-negative). No
    suite was run; no "goldens move" claim is made — step 6.1's procedure measures it.
[x] §2.16: species-layer cache triggers 1-7 incl. the save-switch key-set edge, both orders tested.
[x] No population pinned: the selector's empire axis is a relation (human / not), not an EmpireId count.
[x] ActorHub: one resolver split (6.1), one subsystem (6.2); no per-path split, no private fold.
[x] SOLID: one owner per seam (the resolver for R2/R16, one TryApplyXpUnlocked hook for every empire's
    re-projection, one scope-text vocabulary, one fetch).
```

## Reconciliation — 2026-09-18 (orchestrator review)

- **C1 = `empire-progression` X5.** `layer-source-selector` is the single owner; `empire-progression`
  `legion-commander` consumes it.
- **Q2 (zombie species XP → Zomboss) = `empire-progression` Q1.** Asked once; answered once by R1
  (2026-09-18, §7).
- **R3 → `solid-enforcement` [`save-identity`](solid-enforcement/spec-save-identity.md).** It supplies the `(SaveId, EmpireId)` key, `SaveOfRunUnlocked` and `CommanderLevelOf` that `empire-species-container` and `zomboss-commander-clock` build on, decides G3 (1b is the save's human empire, so `species-mod-ledger` is born keyed `(save_id, empire_id, …)`), G4 (run → save is `GetRunPlayerId`, typed) and G5 (Zomboss's specimens are owned by `EmpireRef(save of the match, zomboss)`), and keeps `species-layer-delivery`'s one fetch.


# Capability map: empire-progression

**Status: spec phase, written 2026-09-18. Not yet reviewed by the owner. No build authorized.**
Owner rulings R1, R3, R4, R5 and R6 of [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) answered
all four of this map's OWNER questions the same day; R18 (respec pricing, with the owner's correction that a
commander pays) and R19 (the empire-level track) followed, and **R23** (Zomboss's commander pool mirrors
the player's; closes the strengthen pass's Q-S1, session `rulings-r20-r24-20260918`). All are applied
below ("Rulings applied 2026-09-18"). In this map, "ruling R*n*" means a row of that file; a bare R-number (as in "R1: a
non-player empire owns …") is the ideal's gap id (`empire-progression-ideal.md` §gaps).
Ideal: [empire-progression-ideal.md](empire-progression-ideal.md), which carries ten binding owner
rulings (R-Q3, R-Q5, R-Q6, R-Q8, R-C1 to R-C6). This map does not reopen any of them. Module specs live
in [empire-progression/](empire-progression/), one per module id.

**Program id: `empire-progression`.** It is the **assignment layer**: who decides where a progression
point goes, for a human, for a general creature, and for an AI empire, plus what a commander *does*
once a commander is a unique creature. It is **not** a second progression system.
[`species-progression-ideal.md`](species-progression-ideal.md) owns what a level grants; this program
owns who fills the shares.

**Loops (the-loops.md):** Spine A "Level up and power" (*"Aptitude points go where you want — you have
no class. Later: trees and commander presence"*), Spine C "Build presets", and Places 3 to 6 on the
commander side. No new loop, currency, class or stamina gate. The free empire respec stock (R18) is an
**Accrual meter** in the resource registry's sense, not a currency (see `respec-free-counter`).

---

## What the gate reading found in code (2026-09-18)

Every row below was re-read in code this session. Code beats the ideal where they disagree, and the
disagreements are listed at the end.

| Fact | Evidence |
|---|---|
| Auto-assign's six rules exist and `Fill` had zero production callers (W1, as of 2026-09-18) — **closed by EP1.4/EP1.5**: `Fill*` now has a real caller (`POST /api/aptitude-presets/suggest`), and the FE's TypeScript mirror this row originally cited is deleted, not moved | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAutoAssign.cs:110` (still the `Fill*` entry point, now called from `AptitudePresetEndpoints.cs`'s `/suggest` route); the FE is a thin caller, `gk-web/web/fusion-rpg-web/src/features/aptitudes/runAutoAssign.ts:30-42` |
| `species-favour` refuses every real 5-key plan row (W3) | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAutoAssign.cs:89-90`; the FE seed path zero-fills, `gk-web/web/fusion-rpg-web/src/features/aptitudes/evenPermille.ts:13-18` |
| Nothing emits `aptitude.autoAssign` (W2) | handlers only: `gk-web/web/fusion-rpg-web/src/ui/actor/AptitudesTab.tsx:261`, `gk-web/web/fusion-rpg-web/src/features/species-build/SpeciesBuildPanel.tsx:116` |
| `systemCopy` is validated and never produced (W4) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:53,193` |
| A unique specimen's favour baseline is **built and has no production caller** | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/UniqueCreatureAllocation.cs:43` |
| General creatures already get a silent favour default (compute-at-read baseline, override wins) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:214-239` |
| A non-Dave empire resolves Empty for species allocation (R1) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:229-233,266-267` |
| The lean is a function of the primary aptitude only (12 values corpus-wide) — **pre-build reading; EP2.5 keyed the lean to the species** | `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs:44-79` |
| Species respec: first override free, replace priced, count decays | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:164-243`; price `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs:36-48` |
| A multiplicative, zero-veto, arity-compensated scorer **already exists**, inert | `gk-core/src/FusionRpg.Core/World/Ai/Utility/Consideration.cs:23,37-75` |
| The lawn duration XP receipt reads a **Bound** session | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:944-1000` (reads `bound_active_ms` at :960) |
| A siege member carrying an `InstanceId` already composes through Hub | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:409-415`; provider `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:559-592` |
| `WorldEntityMemberRole` is `{ Fighter, Bearer }` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:269-273` |

---

## Modules

Stable kebab-case ids, chosen once.

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `assign-ladder` | One server-owned assignment ladder: an ordered, data-driven walk over the closed rule set (active preset, species favour, posture lean, even), always ending on `even`. Zero-fills the 5-key favour shape (W3). Gives `AptitudeAutoAssign` its production caller (W1) and retires the FE's duplicate implementation | — | **A** |
| 2 | `default-build` | R-Q3's silent default for the scope that lacks one: a unique specimen resolves to "explicit allocation, else the ladder's default", computed at read and never persisted. One resolver replaces the direct `LoadAllocation` reads of that scope. Produces `systemCopy` presets (W4). The player's own commander pool is deliberately excluded (see D1) | `assign-ladder` | **A** |
| 3 | `respec-free-counter` | Ruling R18: an **earned** stock of free empire respecs per `(SaveId, EmpireId)`, filled by `empire-level`'s grant (`freeRespecsPerEmpireLevel` in `species-build.v{n+1}.json`). At each species respec the player chooses to spend one or pay souls; the preview shows both. Replaces R-Q3's fixed `respecFreeCount` 25, which was never built | `empire-level`, `specimen-respec-price`; external `save-identity` | **D** |
| 4 | `auto-assign-control` | The FE producer of `aptitude.autoAssign` (W2). Placement comes from an `/idea-ui` pass; this spec fixes the contract only | `assign-ladder`; `/idea-ui` pass | **A** |
| 5 | `favour-detector` | Measure the build-favour corpus the way the ideal requires: lead histogram, shape histogram, lean spread. Emits a generated measure artifact. Report-only until module 7 makes it green, then it gates | — | **B** |
| 6 | `per-species-lean` | R-Q8: the lean reads per-species signals (base-stat specialisation, `Pure`, threat rung) instead of only the primary's crowding. `crowdingFactor` is kept and may fall to 0. Byte-identical at zero weights. Ruling R6: a higher threat rung sharpens the build; that signal ships at weight 0 and a tuning publish turns it on | `favour-detector` | **B** |
| 7 | `lead-relabel-pass` | The build favour pipeline's pass 2: code measures crowding, the model re-labels a crowded species' primary aptitude (label only), code accepts under a per-aptitude quota, the planner re-runs. Then R-Q6's one-sided lead cap and the shape cap gate in CI | `per-species-lean`; after the active `creature-seed-rederive` session commits (same anchors, S11) | **B** |
| 8 | `ai-empire-species` | R1: a non-player empire owns species progression rows and reads its own species default through the ladder. Ruling R1: zombie species XP, on both XP paths, credits Zomboss's empire; ruling R3: every row keyed `(SaveId, EmpireId)`. **Ruling R23: Zomboss's commander pool gets the ladder's computed default at his commander level's budget and applies side-wide to his members** | `assign-ladder`; external `commander-identity`, `save-identity`; for R23 `species-progression` `zomboss-commander-clock` and after its `species-layer-delivery` step 6.1 | **D** |
| 9 | `commander-roster` | A unique creature can hold the commander role: a role binding, a directory source that serves those rows, and a roster listing per `EmpireRef` (X11). Ruling R4: the empire's commander pool keeps applying side-wide; a creature commander adds only its aura | external `commander-identity`, `save-identity` | **C** |
| 10 | `lawn-commander-seat` | R-C1 and R-C4 on the lawn: the run's leading creature commander is **seated** (a deployment child with no board tile), earns the existing duration receipt only, and cannot also be a lawn Bound | `commander-roster` | **C** |
| 11 | `legion-commander` | R-C1 and R-C5 on the world map: `WorldEntityMemberRole.Commander`, an attach and detach command that writes the member's `InstanceId`, and a consumer-side assertion that a unique member never reads the empire species fallback (the seam fix itself is `layer-source-selector`'s) | `commander-roster`; external `species-progression` `layer-source-selector` (hard) | **C** |
| 12 | `ai-build-scorer` | R-Q5: a build scorer for an AI empire, **reusing** `Considerations.Score` rather than writing one. Deferred until an economy exists to score against | `ai-empire-species`; external `sector-development` | **D (deferred)** |
| 13 | `empire-level` | Ruling R19: a level per empire, fed only by that empire's species level-ups (one credit per species per level, once ever, keyed on the species row's `highest_level` because compaction trims the XP ledger; only species whose side maps to that empire under ruling R1 count), stored as a `kind = 'empire'` row of `rpg_actor_progression` keyed `(SaveId, EmpireId)`, on the shared cost curve (`ssot-power-scale.md` §10.1 row 6's function; its own row owed at landing). Each level pays grants from a closed list whose one member today is free empire respecs; the list is the reserved world-stage hook. Zomboss's empire has the same track | external `save-identity`; `ai-empire-species` for Zomboss's feed only | **D** |
| 14 | `specimen-respec-price` | Ruling R18 and its correction: re-allocating **any unique creature, the commander included** (`UniqueCreature` and `Commander` scopes) costs souls when it takes points back, through the one `RespecPolicy.PriceOf` (re-typed to take its parameter set) and one `Quote`. Counter per specimen and per commander pool. Adding unspent points stays free. Never draws on free empire respecs | — | **A** |

**Not a module here, by ruling or by ownership:**

- **The `CommanderId` shape change.** Specified once, in `solid-enforcement`
  [`commander-identity`](solid-enforcement/spec-commander-identity.md) (its map, decision D5). Modules
  8 to 11 depend on it and never re-specify it.
- **The save identity** (ruling R3). *"A Save owns its empires … each keyed `(SaveId, EmpireId)`; the
  player row stops doubling as an empire, and Zomboss stops being a player row."* Specified once, in
  `solid-enforcement` `save-identity` (being written beside `commander-identity`). Module 8 depends on it
  and never re-specifies it; nothing in this program keys an empire by a player row or by the global
  by-name Zomboss row (`RpgStore.ZombossDeploy.cs:25-29`).
- **The build-preset loadout** (ruling R5): a new sub-program, `build-preset`, specced separately and
  built after this program.
- **The per-mode aura scale** (R-C3, R-C5: lawn 100%, siege 100%, world assault 100%, delve 10–15%).
  The ideal assigns the table to `aura-skill`. It is filed there (see "Asks filed"), not built here.
- **Delve participation.** A commander is a unique, so it joins a party like any unique (R-C2). The
  only per-mode difference is the aura scale, which `aura-skill` owns.
- **Commander economy buffs** (R-C6): out of scope, reserved shape `WonderEffectKind.EmpireBuff`.
- **Tree auto-assign** (ideal Q4): owned by the tree generator's coverage decision.
- **Zomboss's commander level from run outcomes** (`species-progression-ideal.md` R-S2 part 1) and
  **rubber-banding** (R-S2 part 2): `species-progression` and a future program respectively.

## Build order

```
Wave A  assign-ladder ─► default-build ─► auto-assign-control (after its /idea-ui pass)
        specimen-respec-price                                 (parallel, independent)

Wave B  favour-detector ─► per-species-lean ─► lead-relabel-pass ─► detector gates

Wave C  (after solid-enforcement commander-identity AND save-identity land)
        commander-roster ─► lawn-commander-seat
                        └─► legion-commander   (also after species-progression layer-source-selector)

Wave D  (after solid-enforcement commander-identity AND save-identity land; no OWNER gate — ruling R1)
        ai-empire-species
        empire-level ─► respec-free-counter   (empire-level after save-identity; Zomboss's feed arrives
                                               with ai-empire-species, the human side does not wait for it;
                                               the R1 side rule keeps the human's zombie history out, so
                                               the two may land in either order — S3)
        ai-build-scorer     (deferred: an economy to score against, per Consideration.cs:23)
```

**Why this order.**

- **The ladder comes first** because the default, the control and the AI empire all call it. Building
  any of them first would mean a second implementation of "which rule applies".
- **Wave B is independent of wave A.** It changes the plan's *content*, and the ladder reads whatever
  plan is committed. Running them in parallel is safe.
- **The detector comes before the passes it judges.** Otherwise there is no before-and-after
  measurement, and the ideal's warning is that the obvious metric reads a converged corpus as healthy.
- **The lean change precedes the re-labelling.** Re-labelling flattens the lead distribution, and while
  the lean still reads crowding, a flatter lead gives every species the same mid-band lean. The ideal
  names this risk. Fixing the lean first removes it.
- **Wave C waits on `commander-identity`.** A creature commander before the enum split would re-key
  species progression, the exact bug that module exists to prevent.
- **Wave C waits on `save-identity` too** (strengthen pass 2026-09-18). `commander-roster` creates
  `rpg_commander_role` and a roster listing that `save-identity` decides are an **empire's**
  (`ForEmpire(EmpireRef)`, X11; its consumer row re-keys the table to `save_id` beside `empire_id`).
  Building the table player-keyed first would buy a second migration of a brand-new table, the same
  argument that holds Wave D. `solid-enforcement` already orders `save-identity` straight after
  `commander-identity` (its Wave 4), so the wait is short.
- **`legion-commander` waits on `layer-source-selector`.** It is the first writer of a legion member's
  `InstanceId`, so it must not land while the siege seam still hands a unique the species fallback
  (X5). The fix has one owner, `species-progression`; this module only asserts it.
- **`specimen-respec-price` is Wave A** because it re-keys nothing: its counters use the allocation's own
  `(scope, scope_key)`. It lands the one `Quote` function the later modules and `build-preset` read.
- **`respec-free-counter` moved from A to D** (ruling R18). Its stock is earned per empire level and keyed
  `(SaveId, EmpireId)`, so it needs `empire-level`, which needs `save-identity`'s re-keyed progression table.
  Nothing is lost by the move: the fixed counter it replaces was never built.
- **Wave D waits on `save-identity` too.** Ruling R3 keys every empire row `(SaveId, EmpireId)`; building
  `ai-empire-species` first would mean a player-keyed table and a second migration. Ruling R1 removed the
  owner gate, so these two external modules are its only gates. `species-progression`'s
  `empire-species-container` and `species-layer-delivery` consume its Zomboss rows.

## Checkpoints

| Checkpoint | Proves | After |
|---|---|---|
| **CP0 — review** | Owner reviews this map, the rulings applied (all four original OWNER questions answered 2026-09-18), the one strengthen-pass OWNER question, and the five `decisions.md` rows below (landed 2026-09-18) | before any build |
| **CP1 — the default exists** | A levelled specimen with no explicit allocation composes a non-empty allocation from its species favour through Hub; an explicit allocation replaces it; the ladder is one C# implementation that the FE calls; taking points back from a specimen or the commander pool costs souls through `RespecPolicy.PriceOf`, while spending unspent points stays free | modules 1, 2, 14 |
| **CP2 — the player can reach it** | Playwright: the auto-assign control fills a draft from a named rule; nothing persists until Confirm | module 4 |
| **CP3 — favour is diverse** | `CreatureBuildPlanGen --check` passes with the lead cap and shape cap **gating**, parity band still gated, every vector at exactly 1000‰; the re-label artifact carries model provenance | modules 5–7 |
| **CP4 — a creature commands** | A creature commander leads a lawn run (seated, duration XP only, refused as a lawn Bound), and leads a legion into a siege where it fights as its own specimen through Hub | modules 9–11 |
| **CP5 — the AI empire owns its progression** | Ruling R1: zombie species levels, from both XP paths, land on Zomboss's empire of the run's save (ruling R3), never the human's row; two saves hold two independent Zomboss levels; its species default resolves non-empty | module 8 (after `save-identity`) |
| **CP6 — the empire levels and earns** | Rulings R18/R19: species level-ups on both XP paths raise their own empire's level on the shared curve, once per species level; each empire level adds free empire respecs; a species respec asks the player to spend one or pay souls, and the preview shows both; Zomboss's empire levels on its own track | modules 3, 13 (after `save-identity`; Zomboss's half after module 8) |

## Decisions this map records

**D1. The default is computed at read, never persisted.** This is the rule general creatures already
follow (`RpgStore.Aptitudes.cs:221-238`, audit finding A9 in its comment). A unique specimen follows it
too. So a default never needs a migration, a tuning change reaches every actor at once, and an explicit
allocation (the player's) always wins. **The player's own commander pool gets no silent default.** R-Q3's
own reasoning names the two cases it covers (*"general creatures … with nobody to click for them"* and
*"a unique actor's player can always disagree"*), and the commander pool is the player's own sheet,
read by eight call sites including passive-tree gates, where a silent spend would change tree
eligibility without a click. The draft button covers it. Overturns `aptitude-sheet`'s
**E3** (*"Empty UniqueCreature / empty commander stays empty"*, `spec-aptitude-auto-assign.md:55-56`)
for the default only, per R-Q3. The draft-only auto-assign button (E1) is unchanged.

**D2. An explicit allocation replaces the default wholesale.** It does not top up the remainder. This is
the shipped species contract (override wins when its total > 0, `RpgStore.Aptitudes.cs:223-224`), and
one contract across scopes is the L in SOLID. "Points go where you want" includes the choice to leave
points unspent.

**D3. The ladder picks a distribution; each scope's existing math turns it into points.** The default
path reuses `SpeciesAllocation.Baseline` and `UniqueCreatureAllocation.Baseline` (largest remainder,
sums to the budget). The draft path keeps `AptitudePresetMaterialize` (floor, leftover visible, E2).
No third favour-to-points function is written.

**D4. The build-favour pipeline writes the anchor, with provenance.** Pass 2 re-labels
`aptitudePrimary` through seedsmith's own anchor emit, keeping the pass-1 answer in provenance. The
alternative, an overlay file, would have to be applied at **seven** C# `AnchorRowReader.ReadAll` call
sites plus the seedsmith readers, which is a partial-application defect waiting to happen (S in SOLID).

**D5. A lawn commander is a deployment child: the "lawn commander seat".** R-C1 retires the double-XP
worry *because* a specimen is in exactly one place. That only holds if leading a lawn run occupies the
specimen. So the seat moves it `Roster → ActiveBound` for the run, with no board tile, and the existing
run-end settle recovers it (`RpgStore.UniqueActors.cs:1017-1031`). This needs a `decisions.md`
amendment (below).

**D6. The build scorer reuses `Considerations.Score`.** R-Q5 asked for multiplicative, zero-veto and
compensated scoring. That exact arithmetic ships inert at `Consideration.cs:37-75`. A second scorer
would be a parallel path for the same numbers.

## `decisions.md` rows owed, with their draft text

**All five landed in `decisions.md` on 2026-09-18** (owner ruling: land every drafted row before the plan phase; session `decisions-rows-20260918`). Each row below names where it landed. The draft text is kept as the record of what was merged; the line numbers in the table are the pre-landing ones (three rows were inserted that day, so later rows moved down by one to three lines).

Five rows. P1 to P3 are owed **before a wave-C build**; P4 before `specimen-respec-price` (Wave A) lands;
P5 before `empire-level` (Wave D) lands. Each lands in `docs/architecture/decisions.md` in the change that
needs it, worded as drafted here unless the owner edits it at CP0. Row numbers are line numbers in
`decisions.md` on 2026-09-18.

| # | Kind | Target | Owed before | Why |
|---|---|---|---|---|
| P1 | amend | "Deployment hierarchy SSOT (2026-09-13)", `docs/architecture/decisions.md:46` | Wave C (`lawn-commander-seat`) | D5; R-C1's *"must be on any base"*. ✅ **landed in decisions.md *Deployment hierarchy SSOT (2026-09-13)* 2026-09-18** |
| P2 | amend | "Unique lawn XP receipts (2026-09-08, strengthened)", `docs/architecture/decisions.md:113` | Wave C (`lawn-commander-seat`) | R-C4; the row pays participation only *"while it remains Bound"*. ✅ **landed in decisions.md *Unique lawn XP receipts (2026-09-08, strengthened)* 2026-09-18** (now line 114) |
| P3 | new | a "Commander role" row beside `docs/architecture/decisions.md:112-113` | Wave C (`commander-roster`) | R-C2, ruling R4, and the ideal's §"The clarification that settles the rest". ✅ **landed in decisions.md *Commander role (2026-09-18)* 2026-09-18** (line 115) |
| P4 | amend | "Class system (2026-08-26)", `docs/architecture/decisions.md` — 'Class system (2026-08-26)', its respec clause | Wave A (`specimen-respec-price`) | Ruling R18 and its correction: the row says respec is *"priced in a resource fighting also costs"* but not which scopes pay, or that an earned free stock exists. ✅ **landed in decisions.md *Class system (2026-08-26)* 2026-09-18** (now line 122), merged with species-progression's R2/R16/R21 amendment into one amendment: part (b) |
| P5 | new | an "Empire level" row | Wave D (`empire-level`) | Ruling R19 adds a progression kind and a closed grant vocabulary. A level that could reach `Θ` would be a second power ladder, so the "never" is locked here, not only in a spec. ✅ **landed in decisions.md *Empire level (2026-09-18)* 2026-09-18** (line 116) |

**P1, appended to the Deployment hierarchy row's child list:** *"A **lawn commander seat** is a
deployment child (2026-09-18, `empire-progression` D5): the unique creature leading a lawn run moves
`Roster → ActiveBound` for that run with no board tile, no ptr and no kill credit, and settles exactly
once through the lawn run-end path, idempotent on `(run, instanceId)`. Its parent is home or a legion
stationed in a sector; no child leaves from a legion on a lane. A specimen is in exactly one place, so a
seated commander is never also a lawn Bound, a delve slot or a siege combatant for that run."*

**P2, replacing the participation clause of the Unique lawn XP receipts row:** *"…and active lawn
participation while it remains Bound **or seated as that run's commander**. The seat writes the same
binding-session row a Bound deployment writes, and the receipt writer is unchanged. A seated commander
never has an attacker ptr, so it can never earn the kill term."*

**P3, new row "Commander role (2026-09-18)":** *"**The commander role is a removable binding on a unique
actor, never an actor kind.** `RpgActorKinds` gains no commander member, and a roster of commanders is a
population, listed per `EmpireRef`, never an enum. What a commander may do is decided by the **place**
(the deployment hierarchy), not by the role: it fights in delve, siege and world assault, and is seated,
non-combat, on the lawn. When a creature leads, the empire's commander allocation still applies
side-wide and the leading creature adds only its aura (ruling R4). Map:
[empire-progression-map.md](empire-progression-map.md)."*

**P4, replacing the respec clause of the Class system row:** *"No aptitude cap and no respec cap (PS-8):
respec is available, unlimited, and priced in souls through one price function (`RespecPolicy.PriceOf`)
and one quote (`RespecPolicy.Quote`), with one tunable parameter set per scope family. **Taking points
back** from the species, a unique creature or the commander pool is a respec; adding unspent points
never is. A commander is a unique creature and pays (ruling R18). Only the **empire respec** (species
scope) may instead be paid with an **earned free empire respec**, one grant per empire level, and the
player chooses which each time. A build preset charges exactly the by-hand price."*

**P5, new row "Empire level (2026-09-18)":** *"**An empire's level is a progression row of kind `empire`,
keyed `(SaveId, EmpireId)`, fed only by its own species reaching a new highest level** (plant species for
the player's empire, zombie species for Zomboss's, ruling R1). It uses the shared arithmetic cost ladder
with its own tunable pair (its own `ssot-power-scale.md` §10.1 row) and **never feeds `Θ` or `P(Θ)`**.
Each level pays grants from a closed vocabulary (`EmpireLevelGrantKind`; today only `FreeEmpireRespec`),
which is the reserved hook for world-stage rewards: a new reward is a reviewed enum member, and a reward
that reaches a magnitude does so through an existing layer and its own SourceId, never through this
level. A grant is never taken back."*

## Tuning version sequence

One file version has one publisher. Every module that publishes takes the **next free version at its
landing** and moves every pin of the version it replaces in the same change, found by search
(`rg -l "<domain>\.v[0-9]+\.json" src tools tests --glob "*.cs"`). On 2026-09-18 that search includes
test fixtures, such as `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs:182` and
`gk-core/tests/FusionRpg.Server.Tests/AptitudeEndpointsTests.cs:42`, which the specs' first drafts left out. This
table records the intended order so two branches never both write one number. A branch that finds its
number taken re-publishes on top of the winner through the tool, never by renaming a file.

| File | Order | Publisher | Keys |
|---|---|---|---|
| `species-build` | 1 | `specimen-respec-price` (Wave A) | `uniqueRespecBasePrice`, `uniqueRespecEscalationPermille`, `uniqueRespecDecayDays` |
| `species-build` | 2 | `per-species-lean`, publish 1 (Wave B) | `leanSignalWeights` at zero (plan byte-identical) |
| `species-build` | 3 | `per-species-lean`, publish 2 (Wave B) | the balance weights, `crowdingFactor` |
| `species-build` | 4 | `lead-relabel-pass` (Wave B, before stage L) | `leadCapPermille`, `leadCapTolerancePermille`, `shapeCapPermille` |
| `species-build` | 5 | `respec-free-counter` (Wave D) | `freeRespecsPerEmpireLevel` |
| `progression` | next free at landing, no number pinned | `species-progression` `zomboss-commander-clock`, `creature-lawn-deploy` `lawn-deploy-progression` and `empire-level` (all three specs say `v{n+1}`) | `awards.zombossRun*`; the lawn-deploy keys; `xpCurve.empire`, `awards.speciesLevelUp` |

**`empire-level` took `v3`** (2026-09-21, EP4.2): `progression.v3.json` is v2 plus `xpCurve.empire`
(`first` 10, `step` 5) and `awards.speciesLevelUp` (1), published through `gk-core/tools/tuning/publish.py` with
`--label "empire-level (R19): xpCurve.empire + awards.speciesLevelUp"`. **The same commit moved every reader
of the previous version, including the live host pin (`gk-core/src/FusionRpg.Server/Program.cs`) and
`gk-forge/tools/ProveHubCombat`/`gk-forge/tools/_TempSeedSpecies`, and made the two keys REQUIRED at parse** — the v1/v2
documents stay on disk for revert but no longer load. Neither remaining publisher has published since, so
`lawn-deploy-progression` and `zomboss-commander-clock` take the next free number if they ever do
(`zomboss-commander-clock` already took v2).
| `build-preset` | v1, a new file | `build-preset` `preset-store` | no collision |

Waves A and B run in parallel, so row 1 and rows 2 to 4 may land in either order; the rule above settles
it.

## Registry row owed: `empire-resource-ssot.md` §3

`respec-free-counter` lands this row in its own change (§5: *"a quantity is not finished until its row
lands"*). Draft, in the table's own columns:

| Id / family | Class | Held by | Faucets | Sinks | Conversions | Owner | Code |
|---|---|---|---|---|---|---|---|
| **free empire respec** | Accrual meter | Empire, `(SaveId, EmpireId)`; survives a world | One grant of `freeRespecsPerEmpireLevel` per empire level (`empire-level`) | One species (empire) respec, at the player's choice instead of souls. Never a unique or commander respec (ruling R18) | None; never traded | `empire-progression` · [spec-respec-free-counter.md](empire-progression/spec-respec-free-counter.md) | `rpg_empire_free_respec_ledger` (spec'd) |

The one difference from the registry's Accrual meter class (`docs/architecture/empire-resource-ssot.md:39`,
*"Progress toward one action; spent only by that action"*) is the holder: an empire, not a sector. The
row says so in "Held by". Zomboss's empire accrues the stock too (R19) and has no sink yet; the row's
"Sinks" column is the human's.

## Asks filed with other programs

| Ask | Owner program | Shape | Until it lands |
|---|---|---|---|
| **Per-mode aura scale table** | `aura-skill` (`aura-magnitude`) | `modeScalePermille: { lawn: 1000, siege: 1000, worldAssault: 1000, delve: <100..150> }` in the next `aura.v{n}.json`, applied once inside `AuraMagnitude`; every row tunable (R-C5) | The aura applies at the lawn value everywhere it reaches |
| **Specimen XP from a fight outside the lawn and expeditions** | `party-dungeon` (delve), `base-defense` / world map (siege, world assault) | The battle report already carries per-specimen XP (`BattleEngine.cs:758`); only expeditions consume it (`RpgStore.Expeditions.cs:318`). A delve or siege settle should award it to `InstanceId` members | A fighting commander, like **every** fighting unique, earns nothing in those modes. Not commander-specific (R-C2), so not built here |
| **`species-progression` level-up grants consume the ladder** | `species-progression` (deferred sub-program) | Its "auto-assigned from species favour and species build preset" calls `assign-ladder`, never a second fill | n/a, recorded so the sub-program does not write its own |
| **Superseded E3** | `aptitude-sheet` | `spec-aptitude-auto-assign.md:55-56` gets a one-line supersession pointing at D1 | readers may believe a unique stays empty |

## Open questions (OWNER)

The four original questions were answered on 2026-09-18 (see "Rulings applied"). One is open, raised by
the strengthen pass and listed under "OWNER questions (strengthen pass)" below.

## Rulings applied 2026-09-18

Source: [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) (binding, not reopened here).

| Was | Ruling | What changed in this program |
|---|---|---|
| **Q1** — zombie species XP to Zomboss's empire? | **Ruling R1: yes, Zomboss's empire.** Plant species progress for the player's empire, zombie species for Zomboss's | `ai-empire-species`: gate lifted; the "no" branch deleted; **both** XP paths re-routed (per-placement `zombie_spawn`, `RpgStore.Progression.cs:31-45`, and run completion, `:113-120`); the human's zombie rows kept as history. Wave D ungated by the owner. Same answer closes `species-progression` Q2 |
| *(no question here; `species-progression` Q3)* | **Ruling R3: add a save identity.** A Save owns its empires, keyed `(SaveId, EmpireId)` | `ai-empire-species` keyed `(SaveId, EmpireId)` over `save-identity`'s re-keyed `rpg_actor_progression` (the separate table first proposed is superseded), `SpeciesLevelOf(SaveId, EmpireId, typeId)`; external dependency on `solid-enforcement` `save-identity` added to module 8 and Wave D. `default-build`'s note on Zomboss's mints updated |
| **Q2** — whose commander allocation lifts the side when a creature leads? | **Ruling R4: both apply.** The leading creature adds only its aura | Recorded as decided in `commander-roster` and `legion-commander`; both had built this answer, so no behaviour changed. A creature commander's own side-wide allocation key is now a **Never** |
| **Q3** — does a higher threat rung sharpen the default build? | **Ruling R6: yes.** The signal still ships at weight 0; a tuning publish turns it on | `per-species-lean`: direction recorded (a positive `threatRung` weight); a non-zero weight is a balance publish, no longer an Ask-first |
| **Q4** — is the build-preset loadout in this program? | **Ruling R5: a new sub-program, `build-preset`**, specced now, built after `empire-progression` | Nothing here; listed under "Not a module here" |
| *(`build-preset` OWNER Q1)* — should commander and specimen re-allocation be priced? | **Ruling R18, with the owner's correction: yes, both.** *"The unique demon must pay for respec"*; *"commander is unique creature, it pays for respec."* The empire (species) respec stays priced, but its free respecs are earned, one grant per empire level, replacing `respecFreeCount` 25; at each empire respec the player chooses to spend a free respec or pay. Only the empire respec draws on free respecs | New module 14 `specimen-respec-price` (Wave A). Module 3 `respec-free-counter` rewritten from a fixed counter to an earned stock with a spend-or-pay choice, and moved to Wave D. `default-build`'s "allocating over a default is free" amended: still free, and a later take-back is priced. `build-preset`'s OWNER question closed |
| **Q-S1** (strengthen pass) — Zomboss's commander pool: ladder default and side-wide like the player's? | **Ruling R23: yes, mirror the player.** Symmetric empires | `ai-empire-species`: owns Zomboss's commander pool — the `assign-ladder` computed default at his commander level's budget, keyed `(SaveId, EmpireId.Zomboss)`, never persisted, applied side-wide on the lawn and siege seams; tests 10–14; golden impact stated (new layer delivered). `assign-ladder`: the commander-context caller (walks to `even`, skips named), test 9. `species-progression` `zomboss-commander-clock`: its level gains this consumer |
| *(new)* Which level is the "empire level"? | **Ruling R19: a new empire-level track**, fed by the empire's species level-ups; each level grants free empire respecs and is the reserved hook for world-stage rewards; Zomboss's empire gets the same track | New module 13 `empire-level` (Wave D) |

## Contradictions found while specifying

| # | Between | Finding | Resolution |
|---|---|---|---|
| X1 | ideal ↔ code | The ideal first cited `ResponseCurves.cs` and `INeedVector.cs` at lines past the end of both files. The curves are at `gk-core/src/FusionRpg.Core/World/Ai/Utility/ResponseCurves.cs:4-55`, `UniformNeeds` at `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31-41` | Fixed in the ideal since (its W5/W6 now cite `:47-53` and `:31-41`); recorded for the trail |
| X2 | ideal R-Q5 ↔ code | R-Q5 frames the build scorer as the repo's first multiplicative scorer. `Considerations.Score` already multiplies, short-circuits on zero, and compensates for arity (`Consideration.cs:37-75`) | Reuse it (D6). The ruling's substance is already met by shipped code |
| X3 | ideal ↔ code | Ideal: a commander that fights "earns XP the way every fighting unique actor already does" in delve, siege and world assault. Only expeditions award specimen XP outside the lawn (`RpgStore.Expeditions.cs:318`) | Filed as a cross-program ask. It applies to every unique, so it is not a commander feature |
| X4 | ideal ↔ code | Ideal: the lawn duration receipt "already works" for a commander. It reads `rpg_unique_lawn_sessions.bound_active_ms`, which only a Bound specimen has (`RpgStore.UniqueActors.cs:958-964`) | `lawn-commander-seat` writes a seat session, and the receipt writer is reused unchanged |
| X5 | `decisions.md` ↔ code | The "Creature progression source" row: a unique *"never receives the empire species fallback"*. The siege seam composes `commander + species + specimen` for an `InstanceId` member (`RpgStore.WorldTurns.cs:581-590`), and returns no Hub inputs at all for a member without one (`:561`). So solid-remediation T4.4's S2 fix reaches **only** the population the row forbids, and general troops still get no species allocation in a siege | `legion-commander` drops the species term for `InstanceId` members (it is the first feature to set `InstanceId`, so no production save moves). General troops receiving species allocation in a siege stays a separate gap for `species-progression`, where S2 was meant to land |
| X6 | ideal ↔ `creature-system-map.md` | Ideal says the map's Axis 2 amendment is still owed | Already done: `creature-system-map.md:71-141`. The ideal's "owed" line is stale |
| X7 | `commander-identity` ↔ this program | `ICommanderDirectory` resolves one commander but cannot list a player's roster | `commander-roster` adds a separate `ICommanderRoster` interface (I in SOLID) rather than widening the directory |
| X8 | `aptitude-sheet` E3 ↔ R-Q3 | E3 keeps an empty unique empty | D1: R-Q3 is the later ruling. Ask filed |
| X9 | ruling R3 ↔ code | The commander pool ruling R4 keeps side-wide is keyed by player: `player:{id}` (`RpgStore.WorldTurns.cs:573-576`; `commander-roster`'s `AllocationScopeKey`). Under R3 an empire's commander allocation is the empire's, keyed `(SaveId, EmpireId)` | Re-key is `save-identity`'s migration. R4's behaviour (the empire's pool applies) is unchanged by it; only the key moves |
| X10 | ruling R1 ↔ code | Zombie species XP reaches the human's row by **two** paths, not one: the per-placement award (`RpgXpAwardMap.cs:68-71`, applied at `RpgStore.Progression.cs:31-45`) and run completion (`:113-120`). The spec previously named the second and mentioned the first in passing | `ai-empire-species` now specifies both, each with a test |
| X11 | ruling R3 ↔ code | Runs, progression facts (`ApplyRpgProgressionFromActivityUnlocked(db, playerId, runId, …)`, `RpgStore.Progression.cs:20-23`) and the per-player roster listing of `commander-roster` are keyed by player. Every ruling-R1 credit needs the run's **save**; a roster of commanders is an empire's | The run→save mapping is a `save-identity` deliverable; `ai-empire-species` blocks on it. `save-identity` decided it: `ICommanderRoster` lists `ForEmpire(EmpireRef)`, and `commander-roster` is now born keyed `(save_id, empire_id)` (S8) |
| X13 | ruling R19 ↔ `save-identity` | `save-identity` classes respec tables as Tier B, human-empire only (`spec-save-identity.md` §"Consumers that must key by `(SaveId, EmpireId)`", `respec-free-counter` row). R19 gives Zomboss's empire the same level track, so its free respec **grants** accrue too | The stock ledger `rpg_empire_free_respec_ledger` is keyed `(save_id, empire_id)` for every empire (Tier A shape); the **spend** stays human-only, as does `rpg_species_respec`. `save-identity`'s consumer row should say so when that module is next edited; nothing in it has to change shape |
| X14 | ideal R-Q3 ↔ ruling R18 | The ideal still carries `respecFreeCount` 25 (`empire-progression-ideal.md:712`, `:1330-1356`) | Superseded by R18. The ideal is the reasoning trail and is not rewritten; it now carries superseded markers (S16), and this map and `respec-free-counter` carry the ruling |
| X15 | code ↔ `empire-level` | `ProgressionPipeline` is empty and runs **before** the ledger dedupe (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:18`, `:180` versus `:206`), so a handler registered there would fire again on a replayed fact | `empire-level` credits after the species ledger row lands, inside `TryApplyXpUnlocked`, and registers nothing in the pipeline |
| X12 | ruling R3 ↔ code | Zomboss's uniques are minted under his player row (`MintForZomboss`, `RpgStore.ZombossDeploy.cs:42-47`) and told apart by `player_id` (`SpecimenOwnershipOracle.cs`). R3 retires that row | `save-identity`; `default-build` is unaffected because its resolver keys by `instanceId` |

## Module specs

| Module | Spec |
|---|---|
| `assign-ladder` | [spec-assign-ladder.md](empire-progression/spec-assign-ladder.md) |
| `default-build` | [spec-default-build.md](empire-progression/spec-default-build.md) |
| `respec-free-counter` | [spec-respec-free-counter.md](empire-progression/spec-respec-free-counter.md) |
| `auto-assign-control` | [spec-auto-assign-control.md](empire-progression/spec-auto-assign-control.md) |
| `favour-detector` | [spec-favour-detector.md](empire-progression/spec-favour-detector.md) |
| `per-species-lean` | [spec-per-species-lean.md](empire-progression/spec-per-species-lean.md) |
| `lead-relabel-pass` | [spec-lead-relabel-pass.md](empire-progression/spec-lead-relabel-pass.md) |
| `ai-empire-species` | [spec-ai-empire-species.md](empire-progression/spec-ai-empire-species.md) |
| `commander-roster` | [spec-commander-roster.md](empire-progression/spec-commander-roster.md) |
| `lawn-commander-seat` | [spec-lawn-commander-seat.md](empire-progression/spec-lawn-commander-seat.md) |
| `legion-commander` | [spec-legion-commander.md](empire-progression/spec-legion-commander.md) |
| `ai-build-scorer` | [spec-ai-build-scorer.md](empire-progression/spec-ai-build-scorer.md) |
| `empire-level` | [spec-empire-level.md](empire-progression/spec-empire-level.md) |
| `specimen-respec-price` | [spec-specimen-respec-price.md](empire-progression/spec-specimen-respec-price.md) |

## Seedsmith and generator coverage

| Module | Generator involved | Where |
|---|---|---|
| `assign-ladder` | No new generation. It **reads** `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json` | output of `gk-forge/tools/CreatureBuildPlanGen` |
| `default-build` | None. Compute-at-read over the committed plan | — |
| `respec-free-counter` | None. One tuning key (`freeRespecsPerEmpireLevel`) | `gk-core/tools/tuning/publish.py` |
| `auto-assign-control` | None. FE only | — |
| `favour-detector` | `gk-forge/tools/CreatureBuildPlanGen` gains a generated measure artifact | `gk-forge/tools/CreatureBuildPlanGen/Program.cs` |
| `per-species-lean` | `gk-forge/tools/CreatureBuildPlanGen` reads the base-stat dump; planner change | `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs:44-79` |
| `lead-relabel-pass` | **Seedsmith**, a new creatures stage `build-favour`; then the C# generation cascade | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/` (new stage), `gk-forge/tools/seedsmith/seedsmith/report/cli.py:2685` |
| `ai-empire-species` | None. Runtime attribution | — |
| `commander-roster` | None. Authored registry rows belong to `commander-identity` | — |
| `lawn-commander-seat` | None | — |
| `legion-commander` | None | — |
| `ai-build-scorer` | None now. If it ever needs per-species weights, they come from a seedsmith deterministic stage, never a model | — |
| `empire-level` | None. Runtime attribution; two tuning keys | `gk-core/tools/tuning/publish.py` (`progression`) |
| `specimen-respec-price` | None. Three tuning keys | `gk-core/tools/tuning/publish.py` (`species-build`) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: aptitudes/allocation, species build favour, respec economy, commanders, deployment
    hierarchy, world legions, world AI scoring, seedsmith creatures.
[x] Session boundary recorded: tasks/sessions/empire-progression-spec-20260918.json (docs only).
    session-boundary-check reports drift in OTHER sessions' records, none crossing these paths.
[x] Read this session: DESIGN-GATE, the-game, the-loops, the ideal in full, species-progression-ideal
    rulings, creature-system-map, solid-enforcement-map, spec-commander-identity, commander-surface-map,
    aura-skill-map, deployment-hierarchy-map, spec-zomboss-adaptive, spec-aptitude-auto-assign,
    decisions.md rows 112-113.
[x] decisions.md checked: rows 46, 112-113 and 119. Five rows owed (P1-P5), text drafted in this map; all five landed in decisions.md 2026-09-18.
[x] Every factual claim cites file:line; unbuilt files carry "(new)".
[x] audit-doc-citations run on every file written (result in the hand-off).
[x] Claims verified against code, not comments (X1-X8 are the places they disagreed).
[x] Surrounding sections read for every rule quoted.
[ ] Tested constraints: none were run. This is a docs-only session. The golden movement that
    default-build predicts is a prediction, and that spec makes running the suite its first task.
[x] No §2 invariant contradicted. X5 is a decisions.md violation found in shipped code, fixed in scope.
[x] Corrections propagated to the map, specs, testing and boundaries sections.
[x] No population pin: detectors assert caps and closure, never counts of species or shapes.
[x] Edge-refreshed caches: default-build and lawn-commander-seat each enumerate their full trigger set,
    including the key-set edge.
[x] Order-independence stated where order varies (allocate vs level-up; attach vs seat).
[x] ActorHub: every module either contributes through existing allocation seams or consumes Hub. No new
    subsystem, no private fold.
[x] No SOLID-violating parallel path: D3, D4, D6 and X7 are the places one was avoided.
```

## Reconciliation — 2026-09-18 (orchestrator review)

- **X5 = `species-progression` C1.** One owner: `species-progression` `layer-source-selector`. Module 11
  (`legion-commander`) depends on it and does not patch `RpgStore.WorldTurns.cs:581-590` itself.
- **OWNER Q1 (zombie species XP → Zomboss) is the same question as `species-progression` Q2.** One answer
  closes both; it is asked once. Answered by ruling R1, 2026-09-18.
- **R3 → `solid-enforcement` [`save-identity`](solid-enforcement/spec-save-identity.md).** It decides X9 (the commander pool string `player:{save}` stays; its encoder takes an `EmpireRef`, behaviour unchanged), X11 (run → save mapping; `ICommanderRoster` lists per `EmpireRef`) and X12 (Zomboss's specimens owned by `EmpireRef(save of the match, zomboss)`), and re-keys `rpg_actor_progression` itself, so `ai-empire-species` reads every empire from that one table rather than a second one.

- **R5 → sub-program [`build-preset`](build-preset-map.md)** (OWNER Q4, the Spine C synergy loadout): specced 2026-09-18, built after this program; it reuses `RespecPolicy.Quote` (introduced by `specimen-respec-price`, fed a free stock by `respec-free-counter`), applies aptitude presets only through the existing activate gate, and waits on `commander-roster` / `save-identity` for its actor-reference grammar.
- **R18 / R19 applied 2026-09-18** (session `respec-rulings-20260918`): modules 13 and 14 added, module 3
  rewritten and moved to Wave D, CP1 re-stated, CP6 added, `default-build` amended, and `build-preset`'s
  pricing statements and its OWNER question closed. Owed at build, in each landing change: an
  `ssot-power-scale.md` §10.1 row for the empire level (`empire-level`), and an `empire-resource-ssot.md` §3
  Accrual-meter row for the free empire respec (`respec-free-counter`).

## Strengthen pass — 2026-09-18

An adversarial re-read of this map, its 14 specs and `build-preset` against current code and rulings
R1 to R19 (session `strengthen-ep-20260918`, docs only). Code had not moved under the specs since they
were written (the last `src/` commit predates them), so the findings are design gaps, not citation drift.
Each was argued the other way once; only the survivors are listed.

| # | Where | Finding | Resolution |
|---|---|---|---|
| S1 | `empire-level` | "Once per (species, level), ever" rested on the XP ledger's dedupe key, but compaction tail-trims `rpg_xp_ledger` per actor (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Compaction.cs:541-560`, delete at `:674`). The empire row gains a ledger row per species level, so its oldest keys are the first trimmed; after that a demote-and-reclimb pays again, and a re-run backfill double-pays | Credit only the levels in `(highestBefore, highestAfter]` of the species row's `highest_level`, which is never trimmed; the catch-up pass runs only for an empire with no empire row yet, one transaction per empire. Dedupe keys kept as the in-transaction replay guard |
| S2 | `empire-level` | The nested empire call returns an `RpgProgressionDirty` that nothing collected, and `EmpireLevelUp` had no emission point | A collector on `TryApplyXpUnlocked`; both species callers add the dirties as they add their own; events broadcast after commit |
| S3 | `empire-level` × ruling R1 | The human's pre-R1 zombie species rows stay on the human empire as history (`ai-empire-species`), so the credit and the backfill would have raised the human's empire level from zombie play | Side rule: a species credits an empire only when `KillAttribution.EmpireOf(side)` is that empire. Also makes the `empire-level` / `ai-empire-species` landing order irrelevant |
| S4 | all tuning publishers | `progression` has three publishers (`empire-level`, `species-progression` `zomboss-commander-clock`, `creature-lawn-deploy` `lawn-deploy-progression`); `species-build` has five publishes across four modules; `per-species-lean` still said `respec-free-counter` might take v2, which Wave D cannot | "Tuning version sequence" table above; each spec points at it |
| S5 | `specimen-respec-price`, `respec-free-counter`, `empire-level`, `per-species-lean` | Pin lists missed `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs:175`, `gk-forge/tools/_TempSeedSpecies/Program.cs:112` and the Server test fixtures that load `progression.v1.json`. New keys are required (T5), so the old version stops loading | Pins found by one search command, stated in each spec |
| S6 | `respec-free-counter` | The stock is `SUM(delta)` over a ledger; a compaction or archive sweep over it would silently change balances | The ledger is never compacted; an architecture test pins it |
| S7 | `legion-commander` | Header, project structure and boundaries still claimed the `RpgStore.WorldTurns.cs` species-term fix that the reconciliation gave to `layer-source-selector`, and the module had no dependency on it | Hard external dependency added (header, module row, build order); the spec only asserts the outcome |
| S8 | Wave C | `commander-roster` creates a table and a roster that `save-identity` re-keys per `EmpireRef` (X11); building it first costs a second migration | Wave C now also waits on `save-identity` |
| S9 | `ai-empire-species` | Stale text contradicted its own reconciled storage: a `rpg_empire_species_progression` credit target, a Dave/non-Dave read branch in "Code style", and debate items defending two tables | Rewritten to the one re-keyed `rpg_actor_progression` and one read path |
| S10 | `lead-relabel-pass` | The schema was described without the `_blocked_variant` wrapper; `audit_schema` refuses a schema with no way to decline (`gk-forge/tools/seedsmith/seedsmith/pipeline/model.py:202`), so the pass as written would not pass its own audit, and blocked samples had no voting rule | Wrapper required; a blocked sample is not a vote; tests for both |
| S11 | `favour-detector`, `per-species-lean`, `lead-relabel-pass` | `creature-seed` R-CS4 marks phantom rows `speciesKind: excluded`, *"never count as roster"*, but the measure, the ranks and stage A would all have counted them; the C# anchor reader does not carry the field | One filter, in the measure; every consumer reads its population. `lead-relabel-pass` starts after the active `creature-seed-rederive` session commits, since both write the same anchors |
| S12 | `specimen-respec-price` | Wave A can land before `save-identity`; its new table was not in that module's Tier B sweep | Stated: Tier B, signature change only, whichever lands second adapts |
| S12b | `specimen-respec-price`, `commander-roster`, `build-preset` `preset-store` | `save-identity`'s cross-program keying sweep (its mismatches 1 to 3) found: the respec payer read from the specimen's `player_id`, which a Zomboss specimen of the same save shares after the migration; the roster listed per player; `rpg_build_preset` born without `empire_id` | Payer resolved through `OwnsSpecimenUnlocked` with a named refusal; `ForEmpire(EmpireRef)` (S17); `empire_id` added at birth, human-only API kept |
| S13 | `build-preset` `piece-appliers` | The price-equality test compared soul and free-stock ledgers but not the churn counters that set the next price; tests were numbered out of order | Counters compared at one injected clock; renumbered; cross-linked with `specimen-respec-price` test 10 as the two halves of one contract |
| S14 | `build-preset-map.md` | "Commander scope, merged side-wide" read as the pre-R16 merged denominator | "Applied side-wide by ruling R4; resolved on its own points by ruling R16" |
| S15 | this map | `decisions.md` rows were one-liners and missed R18 and R19 | Five rows with drafted text and targets (P1 to P5) |
| S16 | `empire-progression-ideal.md` | Still read `respecFreeCount` 25, a free-respec counter keyed to the commander level, open question 2 and Q7a as open, and the Axis 2 amendment as owed | Superseded markers added in place; the reasoning trail is kept |
| S17 | `commander-roster` × `empire-level` | `commander-roster` said `RpgActorKinds` *"stays"* five members while `empire-level` adds a sixth (`empire`); and its table and roster were still player-keyed | The rule is restated as "no **commander** kind"; the table is born `(save_id, empire_id, instance_id)` and the roster lists `ForEmpire(EmpireRef)` |

### ~~Gap: Zomboss's commander allocation (the ideal's W7) has no owner~~ — owned by `ai-empire-species` (R23)

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


`save-identity` defers it here (`spec-save-identity.md` §"The progression gaps handed to this module", X9: giving
Zomboss's siege members his pool *"belongs to the feature that decides what an AI empire's commander
grants (`empire-progression`)"*), and so does `species-progression`
[`layer-source-selector`](species-progression/spec-layer-source-selector.md) (its *"Ask first"*). No module
here builds it. Meanwhile `zomboss-commander-clock` gives Zomboss's empire a commander **level**. Its points
therefore exist and resolve Empty, because nothing writes `zomboss:{save}` (`CommanderId.cs:71`) and the
siege seam hands every non-human member Empty (`RpgStore.WorldTurns.cs:573-576`). The level still acts
through `Θ_content`'s `zombossLevel` input, so the clock is not dark; only the allocation is.

The technical shape is not in doubt: `default-build`'s compute-at-read resolver, extended to the AI
commander pool, fed by `assign-ladder` (D1's reasoning, *"nobody to click"*, covers an AI exactly), and
read side-wide for his members as ruling R4 reads the player's. ~~The open part is a balance decision …
not built until ruled.~~ **Ruled R23 (2026-09-18): yes, mirror the player — symmetric empires.** Built by
`ai-empire-species` (§ *Zomboss's commander pool — R23*): computed at read, never persisted, keyed
`(SaveId, EmpireId.Zomboss)` per `save-identity`, applied on the lawn (`SpeciesAllocationSource.cs:114-116`)
and the siege seam (`RpgStore.WorldTurns.cs:573-576`). Golden impact: Zomboss-side actors with a non-zero
commander budget gain a commander layer once — classified as a new layer delivered and listed in the
commit; everything else byte-identical.

## OWNER questions (strengthen pass)

| # | Question | Why it is the owner's | Default if unanswered |
|---|---|---|---|
| ~~Q-S1~~ **Ruled R23** | Should Zomboss's commander pool (`zomboss:{save}`), whose level `zomboss-commander-clock` now raises, get the ladder's computed default and apply side-wide to his members, as the player's pool does under ruling R4? | It changes battle numbers on Zomboss's side, growing with his level, which is a difficulty decision no ruling covers. R4 ruled only that the player's pool keeps applying | ~~Stays Empty~~ **Ruled R23 (2026-09-18): yes, mirror the player.** Owned by `ai-empire-species` (Wave D); `assign-ladder` gains the caller, `zomboss-commander-clock` supplies the level |

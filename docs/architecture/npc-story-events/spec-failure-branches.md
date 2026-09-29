# Spec: failure-branches

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `failure-branches`, row 23 of the [npc-story-events map](../npc-story-events-map.md) (`:228`), wave 4. Depends
on `story-ledger` and `storylet-selection`. Implements ideal §6.8 (`npc-story-events-ideal.md`) and the loop
page's *"failure branches (Vision)"* (`docs/guide/the-loops.md:140-142`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Make failure open content instead of stacking a penalty. When the player **loses a sector**, **wipes in a delve** or
**loses a siege**, write a **failure fact** — by reading the durable record the owning program already commits, never
by hooking its code — and let that fact make **priority storylets** eligible: a questline, a new character, a branch
place with a way back. A failure branch **never takes back** what the game's own rules let the player keep.

Success looks like: with the game closed, a fixture turn in which the player's sector falls to loam fade writes one
`sector.lost` fact; the next pulse at a nearby host offers a priority storylet about it; a ceded sector writes nothing;
re-reading the same records writes nothing more; no storylet eligible on a failure fact can remove a roster creature,
souls or essence.

## Locked anchors

- **Failure branches** (ideal §6.8, `npc-story-events-ideal.md`): a failure writes a fact in the matching
  scope; the fact makes priority storylets eligible; *"No failure branch takes back what the game's own rules let you
  keep (roster, souls, essence). It offers content; it never adds a second penalty on top of the loss."* Prior art:
  Fallen London's menace areas with *"its own storylets and a way back"* (ideal §4.1, `:227`).
- **Read durable records, never hook** (map row 23, `:228`).
- **Record then drain; a beat one turn late is correct** (map principle 2, `:77-79`).
- **Fact kinds exist**: `sector.lost`, `delve.wiped`, `siege.failed` (`spec-narrative-vocabulary.md` §3).
- **The records**:
  - a sector faded out of supply: report entry `loam.lost:{sectorId}` with the former owner as subject
    (`gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:212-216`);
  - a district assault: report entry `district:{sectorId}:{exit}` (`gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:76-80`),
    `CoreTaken` meaning *"the base falls"* (`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeObjective.cs:9-13`);
  - a deliberate release: the `cede` order, *"the player's own deliberate release"*
    (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:36-41`) — **not** a failure;
  - a delve wipe: the delve's final state `Wiped` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:81`), written by
    `CloseDelve` (`:762`);
  - both pre- and post-turn world states are in hand in the commit (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601-607`:
    *"`world` (pre-step) and `result.World` (post-step) are exactly `previous` and `next`"*).

## Design

### 1. Failure facts and where each is read

| Fact | Scope | Read from (never written by this module) | When | Subject / attrs |
|---|---|---|---|---|
| `sector.lost` | world | a sector owned by the player faction in the pre-turn state and not in the post-turn state, **and** not named by a `cede` order of this turn; cause from the report: `loam.lost:` entry → `fade`; a `district:{id}:CoreTaken` or claim by another faction → `conquest` | `world-events-host`'s post-Step pass (`spec-world-events-host.md` §6), which already holds both states and the report | `sector:{sectorId}`, `{cause, byFactionId?}` |
| `siege.failed` | world | a `district:{sectorId}:CoreTaken` battle entry where the sector was the player's in the pre-turn state | same pass | `siege:{battleId}`, `{sectorId}` |
| `delve.wiped` | save | a delve whose final state is `Wiped` and has no `delve.wiped` fact yet | `FailureScan.Delves(playerId)` at each Sanctum entry (`sanctum-hub-host`) and at each delve-host room entry | `delve:{delveId}`, `{domainId}` |

- **Source refs make every write idempotent**: `turn:{worldId}:{turn}:sector:{sectorId}`, `turn:{worldId}:{turn}:{entryIndex}`,
  `delve:{delveId}:wiped` (`spec-story-ledger.md` §3). A replayed commit or a second scan writes nothing.
- **A siege loss is also a sector loss** when the base's sector changes hands; both facts are written (two different
  facts about one event: the siege story and the territory story), each with its own subject.
- **Ceded is not failure.** A sector released by a `cede` order this turn writes no failure fact — the player chose it.
- **Read, not hooked.** The world half runs inside `world-events-host`'s own pass (this program's code in the commit,
  reading `world`, `result.World` and `result.Report`); the delve half reads `rpg_delves`. Neither edits
  `LoamPhases`, `ClaimResolver`, `DistrictAssaultResolver` or `CloseDelve`.

### 2. What a failure fact opens

A failure fact is read by predicates (`narrative-predicates`' story-flag and fact leaves) and by
`storylet-selection`'s **priority tier**: a storylet whose eligibility names a failure fact is priority while that fact
is younger than `failure.priorityWindow.{clock}` host ticks (tuning, added here). Three shapes, all authored as
ordinary storylets and arcs (narrative-seed), none hard-coded here:

| Shape | Example | Runtime pieces used |
|---|---|---|
| **a questline** | "Take back {place}" | `quest.offer` of a `hold-sector` quest on the lost sector (`spec-quest-sources.md` §3) |
| **a new character** | a survivor who fled the lost sector, a scavenger at the wiped delve's domain | `cast-resolver` casts from present characters into the storylet's role; `met` on answer |
| **a branch place with a way back** | the lost sector becomes a hostile-held place with its own storylets (Fallen London's menace area) | storylets hosted on that sector's slots whose eligibility requires `sector.lost` for it; the way back is the reclaim quest; once the player holds the sector again the branch storylets' eligibility (`sector.lost` newer than the last ownership) stops holding |

The "way back" is structural: every failure-eligible arc must contain a storylet that offers a route out (preflight
rule below), so a branch is never a dead end.

### 3. Never a second penalty

Preflight rules added to `EventDeckPreflight.Run` for any storylet whose eligibility names a failure fact kind:

| Rule id | Refuses |
|---|---|
| `failure.takes-back` | an outcome effect that is a negative resource delta, or a consequence that removes a roster creature or spends a stock without a choice (an `offer:{stock}` **choice** is allowed — the player may choose to pay; an outcome that deducts is not) |
| `failure.no-way-back` | a failure-eligible arc with no link offering `quest.offer`, `recruit` or a `story.flag` that ends the branch |
| `storylet.lose-lose` (existing, `spec-storylet-contract.md` §5) | applies as for every storylet |
| `failure.enemy-personal` (Audit 2026-09-19, R13 rule 3) | a failure-eligible storylet that casts an enemy-role character (a warlord, the antagonist, a raider captain) into a speaking role, or whose eligibility or text keys read the failure fact's `byFactionId`/`siege:{battleId}` **together with** an enemy character — the conqueror never taunts *you* about *this* loss. Antagonist memory of a loss lives at **faction** level only: a storylet may read `byFactionId` to pick the faction's voice, never an individual enemy |

The fairness rule "no two negative storylets in a row on one host" (`storylet-selection`) applies; a failure branch is
not negative by construction (it opens content), and `IsNegative` is derived from its choices like any storylet's.

### 4. Scope

`sector.lost` and `siege.failed` are world-scoped: they live as long as their world exists (ideal §6.7). Owner ruling
2026-09-19 (round 4) — **world-scoped story state is never deleted**, and there is no "abandoned" world state
(world-continuity keeps every world; a fallen world stays revisitable as hostile ground, `world-continuity-map.md`
module 7 `world-fall` and reserved `world-reclaim`):

| World state | These facts and their branch storylets |
|---|---|
| `active` | live: written by the post-Step pass, drawn by selection |
| `hibernating` / `idle` | **dormant**: kept, not drawn, no writes except facts world-continuity's `coarse-step` emits; the priority window's `world.turn` clock counts only full-step turns, so a branch is still headline news when the player returns |
| `outcome = fallen` | **frozen read-only history**: never drawn in that world; `world-reclaim` may read and revive it later. The fall itself is a loss, so it is read like any other (below) |

Failure facts for losses that happen **inside a coarse step** (a dormant world losing a sector with no full `Step`)
are not written by this module's post-Step pass, which never runs there. Audit 2026-09-19: they are read from
world-continuity's own durable per-loss digest facts (`world-fall`, "per-loss digest facts") by the same
read-not-hook rule — a filed ask on world-continuity to name that record's shape; until it lands, a coarse-step loss
opens no branch (a wiring gap, not a design wall).
`delve.wiped` is save-scoped because delve domains persist per player (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs:76-80`).
A failure in one world never opens a branch in another.

## Data shapes

- No table; three existing fact kinds.
- Tuning **declared in `narrative.v1.json` at wave 0 (plan §4 D4; current version `v2`)**, not added in this
  module's build change:

| Key | Unit | Starting value and reason |
|---|---|---|
| `failure.priorityWindow.world.turn` | turns, `long` | 10: a loss stays the headline for a stretch comparable to the per-storylet world cooldown (`spec-narrative-vocabulary.md` §4), then joins the pool |
| `failure.priorityWindow.sanctum.return` | returns, `long` | 3: the next few homecomings react to a wipe, then it becomes ordinary history |
| `failure.priorityWindow.delve.room` | rooms, `long` | 20: roughly one delve's worth of rooms |

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| windows, clocks | `long` | host clocks are unbounded |
| turn | `int` from the engine, stored as `long` | the ledger's `host_clock` type |

## SOLID notes

- **S:** reading failure records and writing failure facts is this module; opening content is the engine's through
  ordinary eligibility.
- **O:** a new failure kind is one reader row and one fact kind.
- **D:** depends on committed records and the ledger; never on the owning programs' resolvers.
- No penalty engine, no second "menace" system: branches are storylets.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Failure/FailureFacts.cs','src/FusionRpg.Server/Narrative/FailureScan.cs','tests/FusionRpg.Core.Tests/Narrative/Failure/FailureFactsTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Failure"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~FailureScan"
```

## Structure

```
src/FusionRpg.Core/Narrative/Failure/FailureFacts.cs        (new: pure pre/post/report -> facts)
src/FusionRpg.Server/Narrative/FailureScan.cs               (new: delve scan; world half called from NarrativeWorldPass)
src/FusionRpg.Core/Narrative/Storylets/EventDeckPreflight.cs (edited: §3 rules)
tests/FusionRpg.Core.Tests/Narrative/Failure/FailureFactsTests.cs   (new)
tests/FusionRpg.Server.Tests/Narrative/FailureScanTests.cs          (new; in-memory store)
```

## Testing strategy

Game closed; fixture worlds, delves and corpus; in-memory store.

- **Fade loss:** a fixture turn whose report carries `loam.lost:S` for a player sector writes one `sector.lost` with
  cause `fade`.
- **Conquest and siege:** a `district:S:CoreTaken` on a player sector writes `siege.failed` and `sector.lost` with cause
  `conquest`.
- **Ceded writes nothing:** the same ownership change with a `cede` order for `S` this turn writes no fact.
- **Wipe:** a fixture delve closed `Wiped` writes one `delve.wiped` at the next scan; an `Extracted` delve writes none.
- **Idempotent:** replaying the commit pass and re-running the scan write nothing more; scanning before and after a
  second delve closes gives the same total facts (order-independent).
- **Priority window:** a failure-eligible storylet is in the priority tier inside the window and in the pool after it.
- **Way back ends the branch:** after the player re-holds `S`, branch storylets for `S` are ineligible.
- **No second penalty:** each §3 rule has a red fixture; a green failure branch's plans contain no negative resource
  step and no roster removal.
- **Scope:** a world-A loss is invisible to world B; a wipe is visible across worlds.
- **Dormant and fallen (round 4):** a branch in a hibernating fixture world is not drawn and its facts are unchanged
  when the world is active again; in a fallen fixture world the facts are still readable and never drawn.
- **No enemy remembers (R13 rule 3):** a fixture failure storylet casting a warlord into a speaking role fails
  `failure.enemy-personal`; one reading `byFactionId` for a faction voice passes.
- **No population:** fixtures only.

## Success criteria

1. Three failure facts are written from committed records, idempotently, without editing their owners. 2. Each opens
priority content through ordinary eligibility, with a way back. 3. No failure branch takes back roster, souls or
essence (preflight). 4. A deliberate release is not a failure.

## Boundaries

- **Always:** read committed records; dedupe by durable refs; open content, never penalize.
- **Ask first:** a new failure kind (for example a lost legion) that needs a record no program commits yet.
- **Never:** hook `LoamPhases`, `ClaimResolver`, the siege resolver or `CloseDelve`; stack a penalty on a loss; treat
  a `cede` as failure.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `FailureFacts.FromTurn(pre, post, report, commands, playerFactionId)` | `world-events-host` post-Step pass |
| `FailureScan.Delves(playerId)` | `sanctum-hub-host` (entry), `delve-host` (room entry) |
| `sector.lost`, `siege.failed`, `delve.wiped` facts | `storylet-selection`, `narrative-predicates`, `sanctum-hub-host` (reactions), `narrative-readings` |

## Contradictions found (report; not fixed here)

None.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: world map (reader of committed turns), base defense (reader of district outcomes), Delve (reader of
    close state), story ledger, storylet engine.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 23; ideal §4.1 (Fallen London), §6.7, §6.8; the-loops.md :140-142; sibling specs
    narrative-vocabulary, story-ledger, world-events-host, quest-sources; code: LoamPhases, BattleReporting,
    SiegeObjective, WorldCommand (cede), RpgStore.Delve (Wiped, CloseDelve), RpgStore.WorldTurns (pre/post state),
    RpgStore.Domains.
[x] Every claim cites file:line.
[x] No population pinned.
[x] No cache.
[x] Order: scan order vs delve close order tested.
[x] Actor numbers: none.
[x] No parallel path: branches are ordinary storylets.
[x] Registry row (Audit 2026-09-19): proposed `ns-failure-no-second-penalty` and `ns-failure-enemy-personal`, both
    guarded by the `EventDeckPreflight` fixture tests (see Standards audit).
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (World map, Economy, Standalone rows), §2 (1, 2, 9, 15), §3,
§5; `the-loops.md` failure branches; ideal §6.8; R13's six rules; round-3 and round-4 owner rulings.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | HIGH | **R13 rule 3 was open.** `sector.lost` carries `byFactionId` and `siege.failed` a battle id; nothing stopped a branch storylet from casting the conquering warlord and having it speak about *this* loss — an enemy remembering the player personally | **Fixed**: preflight `failure.enemy-personal` (§3), faction-level memory only; test added |
| 2 | HIGH | Round-4 ruling: §4 said world facts "retire … when fallen or abandoned"; there is no abandoned state and nothing is ever deleted | **Fixed** (§4): active → live, hibernating/idle → dormant, fallen → frozen read-only history |
| 3 | MEDIUM | A loss inside a world-continuity `coarse-step` never passes through the post-Step pass, so it would open no branch, silently | **Fixed as a stated wiring gap** (§4): read world-fall's per-loss digest facts; filed on world-continuity |
| 4 | LOW | Checklist left the registry box empty for two load-bearing rules | **Fixed**: rows proposed below |
| 5 | LOW | Ideal line citations drifted | **Fixed**: cited by section |

R13 rule-by-rule: 1 — a failure fact never grows an enemy (nothing here writes an enemy row); 2 — no hierarchy;
3 — fixed (#1); 4 — the "hostile-held place" is a storylet host, never a base built from enemy traits; 5 — local;
6 — no warlord write. Economy: a failure branch adds no faucet (its storylets pay through the host budget like any
other, `spec-outcome-routing.md` §3) and `failure.takes-back` bars a second penalty.

**Registry rows proposed** (shared file, not written): `ns-failure-no-second-penalty` → `EventDeckPreflightTests`
(`failure.takes-back`, `failure.no-way-back`); `ns-failure-enemy-personal` → `EventDeckPreflightTests`
(`failure.enemy-personal`). **Deferred:** the coarse-step loss record (#3) — world-continuity's to name.

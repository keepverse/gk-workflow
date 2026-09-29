# Spec: `advance-carry`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 10 of the
[world-continuity map](../world-continuity-map.md) (wave 3; depends on `world-state-vocabulary`,
`hibernation-clock`, `world-creation`, `world-victory`). Ideal:
[world-continuity-ideal.md](../world-continuity-ideal.md) §6.2, W2 (advance any time; smaller carry
without a win). Owner decision **Q2**: a fallen world advances with the not-won limit. House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

The advance verb. The player picks legions to cross, and what may cross is bounded by a **weight limit** —
a payload, like a spacecraft's (round 6 W1) — which is larger if the current world is `won`. Crossing is a
**move, never a copy**: the legions, their unique members and their cargo leave the
old world inside the old world's own turn and appear in the new world at creation, in one transaction, so
both worlds replay. Carried loam is stripped (loam never crosses); **trade goods do not cross with an advance
at all — they cross only over a `rift-trade` route** (round 6 S2); recruits never cross. The old world becomes
`hibernating`.

## Scope and non-goals

**In scope:** the `depart` and `advance` command kinds and their Snapshot resolver; the carry **weight**
admission rule (§2, round 6 W1); the arrival manifest; the cross-world re-key of legion cargo; the attention
swap; loam stripping.

**Not in scope:** the new world's template and stamp (`world-creation`); ~~the cargo kind for world stocks
(scoped-inventory owns cargo kinds — filed as an ask, §5)~~ — **withdrawn by round 6 S2**: goods never ride an
advance, so this module asks for no `world_stock` cargo kind (§5); cross-world trade and the movement of goods
between worlds (`rift-trade`, the only path — S2); **import and export through the rift gate and the gate's own
weight limits (`world-transit`, the named future program of round 6 W2 — no spec here implements it)**; the
per-unit carry capacity itself (`world.carry.capacity`, a derived channel registered by the named future
program `world-derived`, rolled up by `legion-build` `legion-power`); the FE dialog
(`multiverse-surface`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Legion cargo keyed `(world_id, entity_id, seq)` with an FK to the entity row | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:64-75` |
| Cargo capacity is computed from member count, `checked`, never stored | `gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs:39-49` |
| `rpg_item` / `rpg_item_stock` stay the one ownership root; a scope is an overlay; moves are single-transaction | `decisions.md` *Scoped inventory hierarchy SSOT* row |
| `CarriedLoam` on the legion | `gk-core/src/FusionRpg.Core/World/WorldState.cs:327` |
| Unique members carry an `InstanceId` | `WorldState.cs:280` |
| World stocks are `long` sector fields | `WorldState.cs:173`, `:181`, `:187`, `:234` |
| A world-level order with no entity has a precedent (`cede`) | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:74-80` |

### Wiring gap

Cargo kinds are only `instance` and `stack` item rows (`RpgStore.LegionCargo.cs:273-274`): a world stock
is a sector field and cannot ride cargo today. **Round 6 S2 turns this from a gap into the rule:** a world
stock is not supposed to ride an advance at all, so nothing here is owed (§5).

### Real gap

No advance verb; no carry limit; no cross-world entity move. Replay rebuilds a world from its template
alone (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:769`), so a world that received legions at
creation cannot be replayed as written.

## Design

### 1. Advance is an order resolved at End Turn — not a side-channel

Two new command kinds, filed by the player into the **active** world's open turn like any order:

| Kind | Payload | Meaning |
|---|---|---|
| `depart` | `EntityId` | this legion leaves with the advance |
| `advance` | — (world-level, like `cede`) | this turn ends with an advance |

Resolution runs in `Snapshot`, after `WardenResolver` (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:439`),
in a new `AdvanceResolver`: if an `advance` order is present, every `depart`ing legion that still exists
and is not routed is **removed** from the world, its `CarriedLoam` is zeroed with a report line
(`loam.stripped:<amount>`), and the removal is recorded as a typed **departure manifest** on
`TurnResult` (entity, members with `InstanceId`s, stance, cargo reference). Without `advance`, `depart`
orders drop `advance.not-filed`.

**The manifest carries the whole legion (audit 2026-09-20).** The first draft listed only members,
stance and cargo, but `legion-build` puts more hashed state on the entity and its members: `Count`,
`MemberId` and `Gear` on each member (`member-stack`, `legion-equipment`), and `Standard`, `History`,
`Doctrine` and `StandingOrder` on the entity (`legion-standards`, `legion-traditions`, `legion-doctrine`,
`standing-orders`). Owner ruling L2 resets standards and traditions **only on disband or rout**; an
advance is neither, so a manifest that dropped them would silently wipe what the player built. The
departure manifest is therefore the departing `WorldEntity` record verbatim, and each field's crossing
rule is one row of this table (a new entity field is a reviewed row here, and an unlisted field fails the
manifest round-trip test):

| Field | Crosses as |
|---|---|
| `EntityId` | re-keyed `{oldEntityId}@{newWorldId}` (§3) |
| `OwnerFactionId` | the new world's `Player`-kind faction id (templates may name it differently) |
| `AtSectorId`, `OnLaneId`, `OnLaneTowardSectorId`, `LaneProgressMilli` | the new world's `Home` sector; lane fields cleared, progress 0 |
| `Stance` | reset to `march` (a `warden` or `escort` stance names ground or a charge in the old world) |
| `MovementRemaining` | the new world's refill for `march` |
| `Routed` | `false` (a routed legion cannot depart, §1) |
| `CarriedLoam` | 0, with the `loam.stripped` line |
| `Members` (with `Count`, `MemberId`, `Wounds`, `Gear`) | unchanged |
| `Standard`, `History`, `Doctrine` | unchanged (L2: only disband or rout resets them) |
| `StandingOrder` | cleared, with a `standing.ended:advance` report line (its template names old-world sectors) |

Why inside the step: the old world's hash must reflect the legions leaving, and replay of the old world
must reproduce it — which only happens if it is a step result (warden-mortality §The shape: no
side-channel writes to hashed state). Two new kinds that no existing log contains: the new-kind no-bump
precedent (`TurnEngine.cs:131-140`).

### 2. The carry limit is a **weight**, not a legion count (round 6 W1) — admission, refused past, never clamped

**Owner decision W1 (2026-09-20):** *"A weight limit, like a spacecraft's payload. A carry is Σ(unit count ×
that unit type's carry capacity), read from the new `world.carry.capacity` derived channel. Both units and
goods draw on the same limit."* This answers the question this spec left open (the old *"what the carry limit
counts"*, below): a legion count bound almost nothing, because `member-stack` gives a legion unbounded `Count`
and `legion-count-cost` makes fewer, larger legions cheaper.

**The arithmetic.**

```
capacity(world)   = carryWeightContested  or  carryWeightWon        // fallen → contested (Q2)
load(departing)   = Σ over every departing member with Count > 0 of ( Count × unitCarryWeight(member) )
                  = LegionWorldChannels.SumPerUnit over the departing legions      // legion-power §6
admitted          iff  load ≤ capacity
```

- **`unitCarryWeight` is the `world.carry.capacity` derived channel**, composed in `ActorHub` like every
  other channel and rolled up by `legion-build` `legion-power`'s `LegionWorldChannels.SumPerUnit`
  (`legion-build/spec-legion-power.md` §6 states the roll-up for all six `world.*` channels). This module
  **reads** it and computes nothing: no private per-unit weight, no second fold, no `f(level)`.
- **Stated default until `world-derived` ships** (the named future program of D2 that registers the six
  channels): the channel reads a per-unit default from `data/tuning/world-continuity.v{n}.json`
  (`carryWeightPerUnitDefault`), so this module lands whole and behaves identically the day the channel
  registers — the call site does not move.
- **Both units and goods draw on the same limit** (W1). Today only units and their item cargo cross, so only
  those draw. When `world-transit` (W2) lands import and export through the gate, its goods term draws on
  **this** limit, never a second one.
- **A bearer counts.** The load walks every member with `Count > 0`, not only fighting roles: a bearer is
  payload and carries payload (which is exactly why `legion-power` gives the world channels their own
  function family).
- **Item cargo** stays bounded by each legion's own built capacity (`ScopedInventoryPolicy.cs:39-49`) as
  well — that is a *container* bound, not a second gate weight; the legion's units already paid their weight
  here.
- **Refused, never clamped, never silently dropped.** `WorldCommandAdmission` (the shared admission,
  `WorldCommandAdmission.cs:24`) refuses the `depart` that would take the load past capacity with
  `carry.limit`. **Which one is refused (audit 2026-09-20, unchanged by W1):** admission judges one command, so
  the check sums the `depart` orders already admitted for this turn — the store's open-turn list at
  submission, the in-step list at `Reveal` (`TurnEngine.cs:233`) — and refuses the first order that would
  exceed capacity, in command-id ordinal order at `Reveal`, so submission and replay refuse the same one. The
  player controls which legions cross by what they file; a fixed rule decides a tie, never arrival time.
- `world.Outcome` is hashed state (`world-victory` §1), so the check is deterministic in replay.
  `carryWeightWon ≥ carryWeightContested` is validated at tuning load. Weights are `long`, summed `checked`,
  widened before the `Count` multiply; **no cap on capacity growth** — it is a payload the player raises by
  bringing carriers, and the tunable is a starting allowance, not a ceiling.
- **Replay and the Hub.** The load needs the Hub (a derived channel), so it is computed the way
  `legion-power` says a Hub-derived figure reaches Core: Data-side inside the commit, injected as a delegate,
  and **logged** by this module in the turn record, so `Reveal` and replay read the logged load instead of
  recomposing live progression (`legion-build/spec-legion-power.md` §4 — the consumer's obligation, stated
  here as acceptance 10).

### 3. The commit — one transaction for both worlds

When `CommitWorldTurn` resolves a turn whose report carries `world.advanced` (after the log insert,
`RpgStore.WorldTurns.cs:663-681`, and in the same transaction):

1. Plan and create the next world through the **same** planner and store path `world-creation` uses
   (`WorldContinuityRules.NextWorld` → `CreateWorldUnlocked(db, tx, …)`), passing the departure manifest
   as the new world's **arrival manifest**: the legions are placed at the new world's `Home` sector with
   new entity ids (`{oldEntityId}@{newWorldId}`), the same members and `InstanceId`s.
2. Store the arrival manifest once in `rpg_world_genesis(world_id PRIMARY KEY, manifest_json)`.
   `WorldCreation.Rebuild(stamp, seed)` (`world-creation` §6) applies it, so the new world replays from
   template + manifest + its own log.
3. Re-key each departing legion's `rpg_world_entity_cargo` rows from `(oldWorld, oldEntity)` to
   `(newWorld, newEntity)` **after** the new graph is written (the FK needs the new entity row). Item and
   stack rows are never copied: the overlay moves, the ownership root does not (decisions.md *Scoped
   inventory hierarchy SSOT*).
4. Attention: old world → `hibernating` (clock mark current, `hibernation-clock` §4), new world →
   `active`. The partial unique index (`world-state-vocabulary` §2) holds at commit.

5. **Crossing-anchor views (answers `rift-trade-map.md` ask A9, round-4 reconciliation).** Steps 1–3 move
   legions into and out of two worlds Data-side, outside either world's step — the case `rift-trade`
   `crossing-anchor` lists as its trigger T5. In the same transaction, both worlds republish their
   crossing-anchor view through `rift-trade`'s own republish call (a crew legion leaving a depot changes the
   anchor's staffing). This module calls it; it computes nothing about crossings.

6. **Legion-scope bindings follow the legion (audit 2026-09-20).** `legion-build` `legion-owner-scope`
   binds layer-5c containers to the owner key `legion:{worldId}/{entityId}`, keyed by world. The move
   changes both halves of the key, so in the same transaction the reconcile runs for **both** worlds
   (`legion-owner-scope` §2, trigger T3): the old world's run withdraws every binding of the departed
   entity ("entity gone"), and the new world's run binds the desired set from the arrived entity's hashed
   state (standard, traditions, doctrine, cohesion). Nothing is copied row by row; the reconcile derives it.

All six writes and the old world's turn commit are one transaction: a failure leaves neither world
changed.

**Not a system-issued command.** `depart` and `advance` are the player's own orders in the active world
(§1), and the arrival is a genesis manifest, not a command. So the shared system-command path
`trade-foundation` owns (owner Q10) is not used here; an earlier line in `coarse-step` §3 and in the map's
module 10 text said otherwise and is corrected in the round-4 reconciliation.

### 4. What crosses, what does not

| Thing | Crosses? | How |
|---|---|---|
| Legions picked, up to the limit | yes | depart → manifest → arrival |
| Their unique members | yes | members move with the entity; `InstanceId` unchanged |
| Their item cargo | yes | cargo rows re-keyed (§3) |
| `CarriedLoam` | **no** | zeroed with a report line (ideal §3.6) |
| Rubble, ironwork, and every other trade good | **no** (round 6 S2) | ~~only as cargo; needs the `world_stock` cargo kind~~ — **withdrawn.** *"Trade goods cross only through rift-trade routes."* An advance moves units, their unique members and their item cargo; a good reaches another world over a `rift-trade` route, or not at all, until `world-transit` (W2) owns import and export |
| Recruits | **no** | a recruit is a sector stock that becomes a legion member when raised; the raised legion crosses, the unraised stock stays (the amended `the-game.md:73`) |
| Wallets, materials, roster, souls, essence | already banked | untouched (ideal §6.2) |

### 5. ~~Ask filed — a `world_stock` cargo kind~~ — withdrawn by round 6 S2

The ask (a `world_stock` cargo kind so rubble and ironwork could ride an advance) is **withdrawn**. Round 6
S2: *"Trade goods cross only through rift-trade routes. An advance is a weight-limited transit."* So this
module needs no new cargo kind, and scoped-inventory is asked for nothing here. It still crosses whatever
cargo kinds exist (item `instance` and `stack` rows, `RpgStore.LegionCargo.cs:273-274`); it does not add one.

**Where the withdrawn capability lives instead.**

| Want | Owner |
|---|---|
| A good moving between two worlds | `rift-trade`'s cross-world route (the only path, S2) |
| Import and export through the rift gate, and the gate's own weight limits | **`world-transit`** — the named future program of round 6 W2. Noted now, idea round later. **No spec in this family implements it**, and this module's §2 limit is what holds until it exists |
| The per-unit weight the limit is measured in | `world.carry.capacity`, registered by **`world-derived`** (D2), rolled up by `legion-build` `legion-power` |

A legion that loaded goods in the old world cannot advance with them: the `depart` resolver drops
`carry.goods-aboard` (a named refusal, nothing written) rather than silently voiding the cargo — the player
unloads or sells first. That is the honest reading of S2, and it is acceptance 11.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | legion cargo, capacity, single-transaction moves, `CarriedLoam` | reused |
| ~~Wiring gap~~ **not a gap** | cargo cannot carry world stocks | **Round 6 S2: nothing to close.** Goods never ride an advance; they cross only over a `rift-trade` route, and import/export through the gate is `world-transit`'s (§5) |
| Real gap | advance verb, the carry **weight** limit (round 6 W1), cross-world move, replayable arrival | §1–§3 |

## Acceptance (contract)

1. **Conservation:** for every item row, stack quantity and unique actor, the sum across the two worlds'
   overlays after the advance equals the sum before; nothing is copied; the only loss is `CarriedLoam`,
   zeroed with a report line carrying the amount.
2. **(Rewritten by round 6 W1)** The carry limit is a **weight**: `load = Σ (Count × world.carry.capacity)`
   over every departing member with `Count > 0`, refused past with `carry.limit`, never clamped; `won` uses
   the larger capacity, `fallen` and `contested` the smaller. A legion of *n* identical units loads exactly
   *n ×* one unit's weight; a bearer loads its weight; the figure equals
   `LegionWorldChannels.SumPerUnit` over the same legions (one roll-up, not two).
3. A unique actor is a member of at most one world's legion at every committed state (checked across all
   of the save's worlds after the transaction).
4. Both worlds replay to their stored hashes: the old world through its log (the removal is a step
   result), the new world through `Rebuild` + manifest + its log.
5. A failed advance (for example a creation refusal) leaves both worlds and every cargo row unchanged.
6. After the advance exactly one map world of the save is `active` — the new one.
7. `audit-overflow.py` reports no new finding on the cargo and manifest arithmetic.
8. (Audit 2026-09-20) **Manifest round-trip:** every `WorldEntity` and `WorldEntityMember` property is
   named in §1's crossing table (a reflection test fails on an unlisted property); a legion carrying a
   standard, traditions, a doctrine and fitted gear arrives with all four, and its 5c contributions in the
   new world equal those it had in the old (reconcile, §3 step 6); the old world holds no binding for it.
9. (Audit 2026-09-20) With the limit reached, the refused `depart` is the same one at submission and at
   `Reveal` in replay.
10. (Round 6 W1) The load is **logged** in the turn record and replay reads the logged value: a replay with
   the Hub delegate absent reproduces the same admission decisions and the same hash.
11. (Round 6 S2) No trade good crosses on an advance: a departing legion carrying a world stock is refused
   `carry.goods-aboard` with nothing written, and no code path moves a `RubbleStock`/`IronworkStock` value
   between two worlds. A conservation test over both worlds' goods shows every good unchanged.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/AdvanceResolverTests.cs` (new): removal, loam strip,
  manifest, `advance.not-filed`, carry-limit admission for each outcome.
- `tests/FusionRpg.Data.Tests/WorldAdvanceTests.cs` (new): 1, 3, 4, 5, 6 end to end in memory.
- `gk-core/tests/FusionRpg.Data.Tests/LegionCargo/` (extend): re-key keeps FK closure.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python gk-core/scripts/guard-dal.py
python scripts\audit-overflow.py --targets A3
```

Crosses Core and Data: the full suite once at module end.

## Hard edges

- **`rpg_worlds` schema:** none new; `rpg_world_genesis` is a new table. The partial unique index is
  exercised by the swap.
- **Replay:** the old world's removal is a step result; the new world's arrival is a stored manifest read
  by `Rebuild`; the carry load is logged (acceptance 10).
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave**, so a
  world's rules never change mid-life. This module is world-continuity **wave 3** and it grants a
  player-facing feature (the advance verb and its weight limit), so it does **not** claim "no bump": it rides
  **wave 3's single bump**, taken at landing, never pre-assigned (map *Audit 2026-09-20* R1) and recorded in
  [../trade-network/landing-order.md](../trade-network/landing-order.md). ~~No `RulesetVersion` bump (new kinds
  only).~~ The new-kinds precedent still explains why **no stored log carries them and no golden moves** — the
  bump is about the stamp, not the bytes (`../trade-network/trade-foundation/spec-world-stamp.md` §2).
- **Corpse-cache tick key:** the advancing commit advances the save counter once, like any End Turn.

## Dependencies

`world-state-vocabulary` (swap, index), `hibernation-clock` (mark), `world-creation` (planner, create
path, `Rebuild`), `world-victory` (`Outcome`). External: ~~scoped-inventory `legion-cargo` (the
`world_stock` kind, for stocks only)~~ — withdrawn by round 6 S2, §5; `legion-build` `legion-power`
(`LegionWorldChannels.SumPerUnit` and the `world.carry.capacity` read behind §2's stated default);
`rift-trade` `crossing-anchor`'s republish call (§3 step 5, only once
that module lands — before it, there is no view to republish); `legion-build` `legion-owner-scope`'s
reconcile (§3 step 6, only once that module lands) and the entity fields `legion-build` adds (§1's
crossing table grows with each). Named future programs this module **consumes, never implements**:
`world-transit` (import/export and the gate's weight limits, W2) and `world-derived` (the six `world.*`
channels, D2). Consumed by `multiverse-surface`; `rift-trade` later.

**Closed-cycle landing note (global audit M1).** M1 listed `advance-carry` → `rift-trade` `crossing-anchor`
(§3 step 5's republish) against `crossing-anchor` → `advance-carry` (its trigger T5) as a cycle. One line
closes it: **`advance-carry` lands first and publishes a post-move hook** (`AfterCrossWorldMove`), which
`crossing-anchor` **registers** into when it lands. Before `crossing-anchor` exists the hook has no
subscriber and the commit does nothing extra; neither spec waits on the other, and no capability flag spans
both (C1: separate waves, separate bumps).

**Answered (round 6 W1, 2026-09-20): what the carry limit counts.** ~~The limit counts **legions**
(`carryLegionsContested`, `carryLegionsWon`) … this spec keeps the legion count until answered.~~ The owner
answered: **a weight limit, like a spacecraft's payload** — `Σ(unit count × that unit type's carry capacity)`
from the new `world.carry.capacity` channel, with units and goods drawing on the same limit. §2 is rewritten
to it, the two legion-count tunables are replaced by weights, and the reasoning the question gave (a legion
count binds little once `member-stack` lands) is exactly why. No open question remains in this module.

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `carryWeightContested` | weight units (round 6 W1; replaces `carryLegionsContested`) | 120 | `data/tuning/world-continuity.v{n}.json` |
| `carryWeightWon` | weight units (≥ contested, validated) | 360 | same |
| `carryWeightPerUnitDefault` | weight per unit — the **stated default** read until `world-derived` registers `world.carry.capacity` | 10 | same |

The provisional values are a starting allowance chosen by principle, not a ceiling: at the default per-unit
weight they admit about twelve units contested and thirty-six after a win, which is the old 1-and-3-legion
feel at a typical stack size, and a player raises what crosses by bringing carriers (units and gear that
contribute `world.carry.capacity`). `world-continuity.v{n}.json` is published through
`gk-core/tools/tuning/publish.py`, never hand-edited; `v1` is created by whichever world-continuity module lands
first and every later spec writes `v{n+1}` (global audit M8's rule).

## Boundaries

- **Always:** move, never copy; one transaction; limit refused, never clamped.
- **Ask first:** letting loam or recruits cross; a cross-world move outside an End Turn.
- **Never:** writing the departure from the Data layer into hashed state; a second creation path.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `depart` / `advance` kinds, `carry.limit` reason | `multiverse-surface` |
| Departure/arrival manifest shape | `world-creation` (`Rebuild`), `away-digest` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn engine Snapshot and admission, world store commit and create, legion cargo.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: see spec-world-state-vocabulary.md; decisions.md Scoped inventory row;
    scoped-inventory-hierarchy-map.md module rows.
[x] decisions.md checked: Scoped inventory hierarchy SSOT (ownership root never copied).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: cargo DDL and FK, cargo kind check, capacity policy, CarriedLoam, cede's
    world-level admission.
[x] Surrounding sections read.
[ ] Constraint tested: none run.
[x] No §2 invariant contradicted: SQL in Data; loam never crosses; no silent clamp.
[x] Corrections propagated: world-creation's genesis is the arrival manifest named here.
[x] No population pinned.
[x] No cache.
[x] No ordering-fixed criterion (depart orders resolve together at Snapshot).
[x] No actor magnitude.
[x] No SOLID fork: one creation path, one ownership root.
[ ] Registry row: "no cross-world copy" — the conservation test is the guard; row added when built.
```

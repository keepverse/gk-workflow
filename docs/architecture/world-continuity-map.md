# Capability map: world-continuity

**Status: APPROVED 2026-09-19** (owner). Module specs written 2026-09-19 at
`docs/architecture/world-continuity/spec-<module-id>.md` — one per module, including a record of the
executed `continuity-doc-amendment`. No build authorized until the plan and task list exist at
`tasks/world-continuity-plan.md` · `tasks/world-continuity-todo.md` (the prefixed pair this repo's
parallel-program convention requires; the bare `tasks/plan.md` / `tasks/todo.md` pair belongs to another
stream and is never a fallback).

**Program id:** `world-continuity`.
**Ideal it implements:** [world-continuity-ideal.md](world-continuity-ideal.md) — the shape (§6), the
product-document list (§7) and owner decisions W1–W8 (§9). This map does not reopen W1–W8.
**Withdrawn predecessor whose seam is reused:** [warden-mortality-ideal.md](warden-mortality-ideal.md)
§The shape (system-issued `WorldCommand` reconciliation). Its free decay-freeze is forbidden (ideal §3.9).
**Session record:** `tasks/sessions/trade-network-idea-20260919.json` (this file is in its `paths`).
**DESIGN-GATE rows read this session:** Anything at all, Product vision, Economy, Data/SQL, World map,
Performance, Match/actor lifecycle; §2 invariants; §3 evidence rules; §5 checklist (end of this file).
**House style:** [world-action-economy-map.md](world-action-economy-map.md), widened with per-module
evidence because this program crosses Core, Data, Server and the product guide.

Vocabulary rule (owner, 2026-09-19): design text says *empire*, *enemy empires*, *legion*, *sector*.
Shipped enum ids (`WorldFactionKind.Zomboss`, `SectorTypeFlags.Boss`) keep their names.

---

## What this program is

Worlds stop ending. The world you stand on is **active**; when you take its dominant enemy empire's
seat it becomes **developing** and keeps running. You may **advance** at any time to a new world,
carrying what your legions can carry (more after a win). Worlds you leave **hibernate** on the
world-turn clock (lazy, coarse), or go **idle** on the expedition wall clock once a **warden** is
stationed there. Old worlds keep enemy pressure and upkeep, and can **fall**. A later module reclaims
them.

## What it is not

- Not a fourth clock (`the-loops.md:11-21`). Hibernating rides End Turn; idle rides the expedition
  wall clock.
- Not a second simulation. `CoarseStep` composes the **same** rule functions `TurnEngine.Step` calls,
  aggregated per faction; a re-implemented fade, upkeep or contest formula is a defect (ideal §3.1).
- Not cross-world trade — that is trade-network `rift-trade`, built on this program's states.
- Not reclaim — named (`world-reclaim`, reserved) so the states support it; designed later (ideal §6.7).

## Loops extended

Place 5 World stage, Place 4 World map, Place 2 Idle expeditions, Place 3 Farm/hunt/defend, Place 7
Quests and events (`the-loops.md:73-143`; ideal §1).

---

## Locked assumptions (correct before approving)

1. **Two axes, one column each — a refinement of the ideal's one five-value enum** (see Open question
   Q1). `rpg_worlds.state` is the **attention** axis, closed `active | hibernating | idle`; a new
   `outcome` column is the **result** axis, closed `contested | won | fallen`. The ideal's five player
   labels are derived: `active+contested` = *active*, `active+won` = *developing*, `hibernating+*`,
   `idle+*`, `*+fallen` = *fallen*. Reason: a won world that hibernates must still know it was won
   (event budget, carry limit), and one enum cannot hold both facts.
2. **"Exactly one active map world per save" is one fact in one place**: `state='active'` on
   `rpg_worlds`, enforced by a partial unique index on `(player_id) WHERE state='active' AND kind='map'`.
   No separate pointer table (a pointer beside a state column is two SSOTs for one fact).
3. **Pending hibernation turns are computed, never incremented per world.** A save-scoped monotonic
   End Turn counter advances once per committed turn; a hibernating world stores the counter value at
   which it went to sleep. `pending = counter − sleptAt`, capped by `catch_up_cap`. No per-world write
   on End Turn (ideal §3.2).
4. **Every cross-world effect is a system-issued `WorldCommand`** filed into the affected world's
   durable command list, never a side-channel SQL write to hashed world state — the seam
   `warden-mortality-ideal.md` §The shape established (`RpgStore.WorldTurns.cs:539`, the command list
   read before resolution). A coarse catch-up is a **logged record** replay reproduces.
5. **Numbers are tunables** in `data/tuning/world-continuity.v1.json` (new; ideal §8), published through
   `gk-core/tools/tuning/publish.py`. Values are decided by principle at spec time, not owner questions.
6. **One capability flag and one `RulesetVersion` bump per wave (round 6 C1).** A behavioural change to
   `TurnEngine.Step` needs a bump (today 13, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`), and round 6
   fixes *which* bump: **the wave's one bump**, shared by every module landing in that wave, taken at landing
   and never pre-assigned (R1 below), recorded once in
   [trade-network/landing-order.md](trade-network/landing-order.md). Every module names its wave; a module that
   grants a player-facing feature never claims "no bump" — a world's rules must never change mid-life. The
   **golden re-bless** stays with whichever module moves a golden, in its own change.
7. **Model-free throughout.** No module here calls a model. Storylet content is npc-story-events' and
   narrative-seed's.

## Principles restated (binding on every module)

RPG layer only; one turn engine; never step N full worlds per End Turn; leaving never pays better than
staying; determinism — a coarse step is a pure closed form of `(summary, seed, n, stamp, inputs)`;
bounded catch-up (a structural bound, commented as such, with a `ssot-power-scale.md` §11 row); loam
never crosses worlds; every faucet names its sink; the 500-hour test; **a warden never freezes decay**;
one ActorHub compose — a warden's strength is Hub output, contests read Θ difference
(`gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8`). Integer magnitudes (yields, stocks) are `long`,
`checked`; the background multiplier is a per-mille bounded ratio (exempt, commented); turn counters are
`long` (structural, never a magnitude).

---

## Cross-program dependencies

| Program · module | What this program needs | State |
|---|---|---|
| trade-network · `trade-foundation` | The per-world stamp record (ruleset, template version, tuning versions, **difficulty profile id**) stored in `rpg_worlds.ruleset_version`'s home (`trade-network-ideal.md:645`). **Owner of the difficulty id's storage: `trade-foundation`.** Round 4 (Q10): also **the one shared system-command path** (`release-warden`, rift kinds) | Map approved; system-command module owed (round-4 reconciliation) |
| trade-network · `sector-yield` | Warehouses and the *located material* registry class that background yield lands in (`trade-network-ideal.md:642` §14b) | **Map + specs written** (2026-09-19/20): `located-stock`, `warehouse-axis`, `bank-points`, `banking-fact`, `production-halt`, `legion-equipment-stock` (global audit m7 — the old *"Ideal only"* was stale). Banking itself waits on `material-ledger` / the save-identity re-key (round 6 C3) |
| trade-network · `rift-trade` | Consumes this program's states; **and, since round 6 S2, owns the only way a trade good crosses between worlds** (this program's advance carries none) | **Map + specs written** (2026-09-19/20) — `crossing-anchor`, `crossing-leg`, `crossing-goods` (global audit m7; the old *"Ideal only"* was stale). Import/export through the gate is the named future program `world-transit`'s (W2) |
| *(named future programs, round 6)* · `world-transit`, `world-derived` | `world-transit` owns import/export through the rift gate and the gate's weight limits (W2); `world-derived` registers the six `world.*` derived channels (D2), of which this program reads `world.carry.capacity` | **Named, not specced.** No module here implements either; `advance-carry` §2 and §5 state the default each is consumed behind |
| legion-build · stance vocabulary, `legion-power` | The `warden` **stance** on one legion architecture (`legion-build-ideal.md:51-52`, §6.3 `:134-143`); round 4 (P, Q9): warden defence = `legion-power`'s roll-up | Map approved; `legion-power` spec written in round 4 |
| scoped-inventory-hierarchy · `legion-cargo`, `cargo-transfer`, `cargo-fate` | The carrier for advance; fate of cargo when a legion dies en route | **Built**: `rpg_world_entity_cargo` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:64-75`), deposit/withdraw (`RpgStore.CargoTransfer.cs:62,136`) |
| npc-story-events · `storylet-selection`, `world-events-host`, `story-ledger`, `spine-progress` | Consumes the per-state budget; `spine-progress` reads the "world won" fact | Map awaiting approval (`npc-story-events-map.md:215,223,209,227`) |
| notification-ssot · `world-notify-source`, `notify-service` | Delivery of the away digest | Map draft (`notification-ssot-map.md:126,128`) |
| solid-enforcement · `save-identity` | `SaveId` and `rpg_save_empires` for the world-faction ↔ save-empire closure (`spec-save-identity.md:96-100`) | Core types only (`gk-core/src/FusionRpg.Core/Saves/SaveId.cs`); no table in `FusionRpg.Data` |
| world-map · `world-generator` | Templates above `medium` for the next world's size tier (`empire-economy-ssot.md:153-159`) | Not built; only hand-authored templates |
| world-stage · `world-confirms`, `world-playback`, `world-inspector` | Warden confirm reworded; playback rows for new report kinds | Built surfaces (`world-stage-map.md:76,82-83`) |

---

## Modules

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `world-state-vocabulary` | Closed `state` + `outcome` vocabularies; one-active-per-save index; replace `GetActiveWorld`'s first-by-id; state-gate commit/submit; select a world | — | 1 |
| 2 | `hibernation-clock` | Save-scoped End Turn counter; lazy pending turns; `catch_up_cap` read; re-key corpse-cache decay ticks off it | 1 | 1 |
| 3 | `seat-outcome` | Pure detector over `WorldState`: dominant enemy seat taken; player seat lost | — | 1 |
| 4 | `world-creation` | Production world creation (first world of a save, advance target); template ladder; stamps | 1; ext `trade-foundation` stamp | 1 |
| 5 | `world-victory` | `outcome → won` (developing) on the seat fact; durable world-won fact; escalation-slowdown hook | 1, 3 | 2 |
| 6 | `coarse-step` | `CoarseStep(summary, seed, n, stamp, inputs)` closed form; logged coarse record; replay interleave | 2, 3; ext `trade-foundation` | 2 |
| 7 | `world-fall` | `outcome → fallen` for any world (coarse or full step); per-loss digest facts; fallen world stays revisitable | 3, 6 | 2 |
| 8 | `world-warden` | Resumed warden: commander + legion stationed; defence = rolled-up power of the warden legions (0 until the power §10 row); upkeep; retires the per-sector verb (freeze removed by `d6931e43a`) | 6; ext legion-build `warden` stance, `legion-power`; `trade-foundation` system-command path | 3 |
| 9 | `idle-world` | `idle` state on the expedition wall-clock pattern; warden required; capped credited window; collect | 8 | 3 |
| 10 | `advance-carry` | The advance verb; carry limit (won / not won); legion cargo as carrier; loam stripped; world stocks as a cargo kind | 1, 2, 4, 5 | 3 |
| 11 | `background-yield` | 500-hour cure: multiplier < 1 decaying with hibernating-world count; yield into warehouses; collected, never auto-banked | 6; ext `sector-yield` | 4 |
| 12 | `world-event-budget` | Per-state event budget table; hibernating events resolve inside `CoarseStep` from the same deck | 1, 6; ext `storylet-selection` | 4 |
| 13 | `away-digest` | While-you-were-away digest from coarse and idle records → report entries + notification drafts | 6, 7; ext `world-notify-source` | 4 |
| 14 | `world-difficulty-profile` | Default difficulty profile catalog and the knobs `CoarseStep` and AI read; the id rides `trade-foundation`'s stamp | 4, 6; ext `trade-foundation` | 4 |
| 15 | `multiverse-surface` (FE) | World list, switch, advance dialog, warden station, digest layer. `/idea-ui` first | 1, 10, 13 | 5 |
| 16 | `continuity-doc-amendment` | Every product/architecture document ideal §7 names, changed in one change | map approval | 0 |
| — | `world-reclaim` | **Reserved, not in this map's build.** Re-entering a fallen world as hostile ground | 7 | later |

**Build order:** `continuity-doc-amendment` (on approval, ideal §7 end) → `world-state-vocabulary` ∥
`seat-outcome` → `hibernation-clock` ∥ `world-creation` → `world-victory` ∥ `coarse-step` →
`world-fall` → `world-warden` → `idle-world` ∥ `advance-carry` → `background-yield` ∥
`world-event-budget` ∥ `away-digest` ∥ `world-difficulty-profile` → `multiverse-surface`.
External gates: `coarse-step` and `world-creation` wait on `trade-foundation`'s stamp (the ideal's
`world-continuity` row depends on it, `trade-network-ideal.md:562`); `background-yield` waits on
`sector-yield`; `world-warden` waits on legion-build's `warden` stance (its defence term on `legion-power`).

---

## Module detail

### 1 · `world-state-vocabulary`

**Capability.** Turns `rpg_worlds.state` from a column nothing but `GetActiveWorld` reads into a closed
vocabulary (`active | hibernating | idle`) plus an `outcome` column (`contested | won | fallen`), makes
"one active map world per save" a SQL-enforced fact, and gives the player a real "select this world"
transition. Every write path that advances or commands a world refuses a world that is not `active`.

| Bucket | Evidence |
|---|---|
| Built | `state TEXT NOT NULL DEFAULT 'active'` and index `(player_id, state)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:32,36`); `kind`/`parent_world_id` and index `(player_id, kind, state)` (`:204-206`); `WorldHeaderRow.State` read back (`:737-740`) |
| Wiring gap | `GetActiveWorld` is `ORDER BY world_id LIMIT 1` over `state='active'` — first by id, not chosen (`RpgStore.World.cs:416-431`); its only caller is `GET /api/world/{playerId}` (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:28-32`) and the web reads it at `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:584`. `CommitWorldTurn` checks `kind` but never `state` (`RpgStore.WorldTurns.cs:506-508`), so a non-active world can still be stepped. Nothing writes `state` after insert (`RpgStore.World.cs:243-245` is the only map insert; the only `UPDATE rpg_worlds` is the turn advance, `RpgStore.WorldTurns.cs:686-689`) |
| Real gap | No closed vocabulary type; no `outcome` column; no uniqueness of the active world; no select verb |

**Touches:** `gk-core/src/FusionRpg.Core/World/` (new `WorldAttention`/`WorldOutcome` closed vocabularies),
`RpgStore.World.cs` (`EnsureColumn`, partial unique index, `GetActiveWorld`, new `SelectWorld`),
`RpgStore.WorldTurns.cs` (commit/submit gate), `WorldEndpoints.cs` (select route), `decisions.md` row.
**Acceptance (contract):** both vocabularies are closed enums whose member lists are pinned with the
reason "closed vocabulary the code owns"; an unknown stored value is a load rejection; a second
`active` map world for one save is refused by the index; `GetActiveWorld` returns the unique active
row or none — never "first by id"; commit and submit on a non-active world return a named reason
(`world.not-active`); selecting world B makes A `hibernating` and B `active` in one transaction,
order-independent of which was created first; delve rows (`kind='delve'`) are untouched.
**Verification:** `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>` → Data.Tests (world
store), Server.Tests (world endpoints), `guard-dal.py`. No golden moves (header hash covers
`TemplateId, Seed, CurrentTurn` only, `decisions.md` — 'World store — delve worlds (2026-09-05)').

### 2 · `hibernation-clock`

**Capability.** A save-scoped monotonic End Turn counter, advanced inside `CommitWorldTurn`'s
transaction; a hibernating world records the counter value when it went to sleep; pending turns are a
subtraction, capped by `catch_up_cap`. The same counter becomes the tick key for corpse-cache decay,
which today collides across worlds.

| Bucket | Evidence |
|---|---|
| Built | `catch_up_cap INTEGER`, `turn_period_seconds INTEGER`, `last_advanced_utc TEXT` columns (`RpgStore.World.cs:26-29`); the commit is one transaction (`RpgStore.WorldTurns.cs:518-519`) |
| Wiring gap | `catch_up_cap` and `turn_period_seconds` are never read — the only `src/` hits are the DDL (`RpgStore.World.cs:26-27`); `last_advanced_utc` is written by the turn advance only (`RpgStore.WorldTurns.cs:688`) |
| Real gap | No save-scoped turn counter. **Defect found:** corpse-cache decay ticks per **save** keyed by the committing world's bare turn number (`RpgStore.WorldTurns.cs:700` → `RpgStore.CacheDecay.cs:130-145`, `owner_player_id = $p AND ... l.tick = $t`); with several worlds, world B's turn 3 and world A's turn 3 are the same tick, so a cache can skip or double its decay |

**Touches:** `RpgStore.WorldTurns.cs`, `RpgStore.CacheDecay.cs`, a save-scoped counter home (spec picks:
a column on the save row or a one-row-per-save table — never per world), `RpgStore.World.cs`.
**Acceptance:** committing N turns in the active world raises pending for every hibernating world by N
with zero writes to their rows; pending never exceeds `catch_up_cap`; decay ticks are unique per
`(cache, save counter)` whichever world committed; replaying a commit never re-ticks.
**Verification:** verify-change → Data.Tests (world turns, cache decay). `catch_up_cap` gains a
`ssot-power-scale.md` §11.4-style row (structural bound, commented).

### 3 · `seat-outcome`

**Capability.** One pure Core function over a committed `WorldState`: has the player taken the seat of
the world's dominant enemy empire, and has the player lost their own seat? Victory and fall are two
readings of one detector, so they cannot disagree.

| Bucket | Evidence |
|---|---|
| Built | Every world has exactly one `Home` sector owned by the player (`gk-core/src/FusionRpg.Core/World/WorldValidation.cs:201-212`; flag at `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:9,59-60`); the enemy's seat sector type `boss-lair` carries `SectorTypeFlags.Boss` (`SectorTypeCatalog.cs:98-99`); faction kinds are plural-ready (`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18`) |
| Wiring gap | `SectorTypeFlags.Fortress` exists (`SectorTypeCatalog.cs:15`) but no sector type sets it; only `DistrictLayout` reads it (`gk-core/src/FusionRpg.Core/World/District/DistrictLayout.cs:267`) |
| Real gap | No code detects victory or seat loss anywhere in `gk-core/src/FusionRpg.Core/World` (searched: no victory/fortress-taken predicate). "Dominant enemy empire" has no data definition when a world has many empires (W8) |

**Touches:** `gk-core/src/FusionRpg.Core/World/` (new detector), template validation (each template names its
dominant enemy by the faction that owns its `Boss`-flag seat at creation — data, not code).
**Acceptance:** the detector is pure (no store, no clock); for each template, taking the `Boss` seat
reports `won` and losing the `Home` seat reports `fallen`; a template with zero or two dominant seats
fails validation; the result is identical for a full step and a coarse step producing the same state.
**Verification:** verify-change → Core.Tests (World).

### 4 · `world-creation`

**Capability.** World creation leaves the test group: a new save gets its first world, and advancing
creates the next one. The template for the next world comes from a tunable size/intensity ladder
(`empire-economy-ssot.md:145-146`), falling back to the largest available template with a higher
Fracture intensity until `world-generator` supplies larger maps. Every new world records its stamp.

| Bucket | Evidence |
|---|---|
| Built | `CreateWorld` validates and writes header + graph in one transaction (`RpgStore.World.cs:219-253`); `WorldTemplateCatalog.Build` (called at `WorldEndpoints.cs:616`) |
| Wiring gap | The only caller is `POST /api/test/world/create` (`WorldEndpoints.cs:601-626`, mapped in the test group at `gk-core/src/FusionRpg.Server/SimEndpoints.cs:129,135`); the web never calls it (no hit under `gk-web/web/fusion-rpg-web/src`). `engine_version` and `ruleset_version` are written as the literal `1` (`RpgStore.World.cs:245`) |
| Real gap | No production creation path; no next-template rule; templates above `medium` do not exist (`empire-economy-ssot.md:157-159`) |

**Touches:** `RpgStore.World.cs`, a new application service in `FusionRpg.Server`, `WorldTemplateCatalog`,
tunables file. **Acceptance:** a new save has exactly one active world after onboarding reaches the
world chapter; creation writes the full stamp (never a literal); the next template is a pure function
of `(worlds won, worlds entered, tunable ladder, available templates)`; the test endpoint stays and
calls the same service. **Verification:** verify-change → Data.Tests, Server.Tests.

### 5 · `world-victory`

**Capability.** When `seat-outcome` reports `won` after a committed turn, the world's `outcome` becomes
`won` automatically (W1) in the same transaction; the full step keeps running; a durable, idempotent
"world won" fact is recorded for `spine-progress` (one time-machine piece per world won,
`npc-story-events-map.md:227`); escalation slows through a tunable the AI and Events phase read.

| Bucket | Evidence |
|---|---|
| Built | The commit transaction and turn log (`RpgStore.WorldTurns.cs:518-700`); remaining factions keep acting through `FillAiCommandersUnlocked` (`:527`) |
| Real gap | No transition, no fact, no escalation knob |

**Acceptance:** exactly one won-fact per world, replay-safe; `outcome` never goes `won → contested`;
the transition does not change the world hash (header state is outside the canonical row,
`decisions.md` — 'World store — delve worlds (2026-09-05)'); Advance's full carry limit unlocks. **Verification:** verify-change → Data.Tests,
Core.Tests.

### 6 · `coarse-step`

**Capability.** `CoarseStep(summary, seed, n, stamp, inputs)` advances a hibernating world `n` turns in
closed form, per faction and never per unit: production at the background multiplier into warehouses
(later, `background-yield`), upkeep and fading, hostile spread, one Θ-difference contest per enemy
frontier, calendar boundaries crossed (weekly recruit pulses, `world-graph-ideal.md` §3.11), and a
digest. It is composed from the rule functions `TurnEngine.Step` already calls. It runs when the world
is viewed or on a small background budget, writes the graph once, and appends one **coarse record** to
the turn log so replay reproduces it. Warden strength (Hub output) enters as a **logged input**, never a
live read.

| Bucket | Evidence |
|---|---|
| Built | Pure `Step(world, commands, seed, resolver, …)` (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-174`); pure lazy idle resolver shape (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:61-67`); Θ contest primitive (`CombatProbability.cs:8`); Hub inputs injected as a delegate from Data, never a store read in Core (`RpgStore.WorldTurns.cs:557-590`); graph write once per call (`RpgStore.World.cs:272`) |
| Wiring gap | Replay rebuilds from the template and calls `Step` once per turn (`RpgStore.WorldTurns.cs:769-775`) and refuses any log whose engine/ruleset differs (`:759-760`) — a coarse catch-up would be unreplayable as written |
| Real gap | No coarse step, no coarse record kind, no stamp-aware branch |

**Touches:** `gk-core/src/FusionRpg.Core/World/Turn/` (new `CoarseStep`), `RpgStore.WorldTurns.cs` (record +
replay interleave), tunables. **Acceptance:** determinism — same `(summary, seed, n, stamp, inputs)`
gives a byte-identical result and hash; cost is independent of `n` (closed form; asserted by a
structural test, not a timing); `n` is capped by `catch_up_cap`; `CoarseStep(n=a)` then `(n=b)` equals
`(n=a+b)` for production and upkeep terms (**order-independent** split); background production is
strictly below the full step's for the same state; replay of a world with coarse records reproduces
its hash; no wall-clock read inside (the world-map wave-1 guard, `world-map-program.md` checkpoint 4).
**Verification:** verify-change → Core.Tests (World/Turn), Data.Tests; a `RulesetVersion` note only if
`Step` itself changes.

### 7 · `world-fall`

**Capability.** When `seat-outcome` reports the player's seat lost — in a coarse step or a full step —
the world's `outcome` becomes `fallen`. Each frontier loss before it is a digest fact as it happens,
never a surprise wipe (ideal §6.5). A fallen world stays listed as hostile ground; its warden, legions
and cargo follow `cargo-fate`; nothing is deleted, so `world-reclaim` can read its history.

| Bucket | Evidence |
|---|---|
| Built | Sector capture and binding clear (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:101-107`); destroyed-legion cargo fate (scoped-inventory `cargo-fate`, `RpgStore.CargoFate.cs`) |
| Real gap | No fallen state; no rule for the active world losing its seat (see Q2) |

**Acceptance:** `outcome=fallen` is terminal for this program (only `world-reclaim` may leave it); a
fallen world is never `active` unless the player selects it for reclaim (later); every sector lost in a
coarse step emits one digest fact. **Verification:** verify-change → Core.Tests, Data.Tests.

### 8 · `world-warden`

**Capability.** A warden is a **commander with a legion** stationed on an old world (W5): a legion in
the `warden` **stance** (legion-build's stance vocabulary; spec `world-warden` §4) led by a commander-role
unique actor. During coarse steps and idle resolution, **the rolled-up power of the warden legions**
(round 4 P / Q9: `legion-build` `legion-power`, Hub output summed) enters the frontier and seat contests as
a Θ term that lowers loss odds — **0 until the power program's §10 contest row lands**. It costs upkeep
every period, and its commander and legion are unavailable in the active world. **It never freezes decay
or production losses.** The shipped freeze was removed by `d6931e43a` (`RulesetVersion` 13); this module
retires the per-sector verb's route and releases existing bindings through `trade-foundation`'s shared
system-command path (round 4 Q10).

| Bucket | Evidence |
|---|---|
| Built | `bind-warden` command and resolver (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:54`; `gk-core/src/FusionRpg.Core/World/Movement/WardenResolver.cs:21-63`); `WardenBindingId` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:218`), hashed (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:45`); commander role as a removable binding on a unique actor (`decisions.md` *Commander role* row) |
| **Wiring gap — the withdrawn freeze was live (closed by `d6931e43a`, 2026-09-19; the cites below are the pre-fix sites)** | A warded sector is skipped as a fade target (`gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:30-33`) and skipped on recovery, so *"its StabilityMilli neither rises nor falls while the binding holds"* (`gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:197-203`). It is reachable in production: `POST /api/world/{worldId}/bind-warden` (`gk-core/src/FusionRpg.Server/WorldWardenEndpoint.cs:40-82`) is mapped at `gk-core/src/FusionRpg.Server/Program.cs:938` and the web ships `gk-web/web/fusion-rpg-web/src/stages/world/confirms/BindWardenDialog.tsx`. The bind is **non-releasable "for the life of the world"** (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:276-283`) — under continuity a world never ends, so the binding slot is lost forever |
| Real gap | No world-scoped warden; no `ReleaseWarden` command (warden-mortality §The shape, never built); no warden upkeep |

**Touches:** `LoamPhases.cs`, `LoamForecast.cs`, `WardenResolver.cs`, `WorldCommand.cs`,
`RpgStore.Contracts.cs`, `WorldWardenEndpoint.cs`, world-stage `world-confirms`; `RulesetVersion` bump
and golden re-bless. **Acceptance:** with a warden present, `StabilityMilli` moves exactly as without
one (the freeze is gone); warden strength is read from Hub output only and logged as a coarse input;
loss odds with a warden are ≤ without, for every Θ gap (monotone); upkeep is charged every period the
warden is stationed; a stationed commander cannot be seated or deployed in the active world; existing
per-sector bindings are released by a system-issued `ReleaseWarden` resolved in `Snapshot` and their
contract slots freed (Q3). **Verification:** verify-change → Core.Tests (World/Loam, BindWarden
threading), Data.Tests (contracts), Server.Tests (`WorldBindWardenEndpointTests`), world goldens,
`guard-actor-hub.py`.

### 9 · `idle-world`

**Capability.** Stationing a warden may turn a hibernating world `idle`: it records when it went idle and
resolves on the expedition wall-clock pattern — pro-rated at collect, inside a capped credited window
(Melvor's shape, ideal §5). Idle resolution is "maintenance only" for events and never runs
`TurnEngine.Step`. Leaving idle (warden recalled or killed) returns the world to `hibernating`.

| Bucket | Evidence |
|---|---|
| Built | Wall-clock pro-rating: `elapsed = min(tickCount, (now − dispatched) / tickMinutes)`, floored at logged battles (`gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:98-101`); dispatch stamps `dispatched_utc`/`due_utc` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:71-93`); pure resolver (`ExpeditionResolver.cs:61`) |
| Wiring gap | `turn_period_seconds` exists and is never read (`RpgStore.World.cs:26`) — the natural home for the idle period |
| Real gap | No idle resolver for a world; no idle anchor timestamp |

**Acceptance:** idle requires a stationed warden (refused otherwise, named reason); credited time never
exceeds the window; resolution is pure over `(summary, seed, elapsed periods, stamp, inputs)`; a
collect is idempotent (a retry resolves the same periods); idle never pays more per period than
`hibernating` for the same world (ideal §3.3). **Verification:** verify-change → Core.Tests,
Data.Tests, Server.Tests.

### 10 · `advance-carry`

**Capability.** The advance verb (W2: any time). The player picks legions to cross; the carry limit is
larger if the current world is `won`. Crossing is a **move, never a copy**: legions, their unique
members and their cargo leave the old world by the player's own `depart`/`advance` orders resolved in its
step and enter the new world through a stored genesis manifest, so both worlds replay (spec §1, §3; round-4
correction — not a system-issued command). `CarriedLoam` is stripped (loam never
crosses). **Round 6 S2/W1/W2:** the limit is a **weight** (Σ unit count × that unit type's
`world.carry.capacity`, rolled up by `legion-build` `legion-power`), and world stocks (rubble, ironwork) and
every other trade good ~~may cross only as cargo~~ **do not cross with an advance at all — only over a
`rift-trade` route**; import/export through the gate is the named future program `world-transit`'s. Recruits
never cross. The old world
becomes `hibernating`.

| Bucket | Evidence |
|---|---|
| Built | Legion cargo keyed `(world_id, entity_id)` with FK to the entity (`RpgStore.LegionCargo.cs:64-75`); capacity from member count, `checked` (`gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs:39-49`); single-transaction scope moves (`decisions.md:47`); `CarriedLoam` field (`WorldState.cs:327`); unique members carry `InstanceId` (`WorldState.cs:280`) |
| Wiring gap | Cargo kinds are only `instance` and `stack` item rows (`RpgStore.LegionCargo.cs:273-274`) — world stocks are sector fields (`WorldState.cs:181,187`) and cannot ride cargo today |
| Real gap | No advance verb; no carry limit; no cross-world entity move; replay from template alone (`RpgStore.WorldTurns.cs:769`) cannot reproduce a world that received legions at creation |

**Touches:** Data (cross-world move in one transaction), Core (departure/genesis command kinds), cargo
kind for world stocks (a scoped-inventory ask), tunables. **Acceptance:** the sum of every moved row is
conserved across the two worlds (nothing copied, nothing lost except loam, which is zeroed with a
report line); the carry limit is refused past, never clamped silently; the won limit ≥ the not-won
limit; a unique actor is a member of at most one world's legion at any time; both worlds' hashes
replay after the move; advance is refused from a `fallen` world only if Q2 says so.
**Verification:** verify-change → Data.Tests (cargo, world), Core.Tests; `audit-overflow.py` on the
cargo magnitudes.

### 11 · `background-yield`

**Capability.** The 500-hour cure (ideal §6.6): coarse and idle production run at a per-mille multiplier
below 1000 that **decays as more worlds hibernate** (a soft curve, never reaching a hard floor of 0 by
fiat); output lands in that world's warehouses (trade-network `sector-yield`) and is collected by
visiting, by cargo, or by `rift-trade` — never straight into a wallet. Upkeep and enemy pressure keep
running, so a permanent structure is never free.

| Bucket | Evidence |
|---|---|
| Built | World stocks are map-scoped (`docs/architecture/empire-resource-ssot.md:38`); production phase (`TurnEngine.cs:301-313`) |
| Wiring gap | No shipped code banks sector yields today (`trade-network-ideal.md:472-473`), so "never auto-banked" is vacuously true until `sector-yield` lands |
| Real gap | Multiplier, its decay, warehouse landing, collection verb |

**Acceptance:** background yield per period < active yield for the same state, for every hibernating
count; adding a hibernating world never raises total background yield per period beyond the tunable
curve (P1 net-flow report, not a pinned number); no background path writes a wallet or material ledger
row; every faucet here names its sink in the same change (upkeep). **Verification:** verify-change →
Core.Tests; the trade-foundation economy report as a test once it exists.

### 12 · `world-event-budget`

**Capability.** A per-state event budget (ideal §6.9): full when active and contested, reduced when won,
low and coarse-only when hibernating, maintenance-only when idle. The storylet engine reads it; the
shipped calendar in the `Events` phase reads it; hibernating events resolve inside `CoarseStep` from the
**same** deck — never a second one.

| Bucket | Evidence |
|---|---|
| Built | `Events` phase calendar rolls (`TurnEngine.cs:355-374`); phase order locked (`decisions.md:7`) |
| Real gap | No budget; npc-story-events' map has no per-state budget and no hibernating host (`npc-story-events-map.md:215,223` — ask to file) |

**Acceptance:** the budget is a pure lookup over the two state columns; the sum of event pulls in a
coarse step never exceeds `budget × n`; the deck id used by a coarse draw equals the active draw's.
**Verification:** verify-change → Core.Tests.

### 13 · `away-digest`

**Capability.** "While you were away": each coarse record and idle collect produces a digest — losses,
gains, events, warden fights — shown on the turn report and sent as notification drafts. Losses are
reported as they happened, in order.

| Bucket | Evidence |
|---|---|
| Built | Turn report kinds (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10`); world-stage playback (`world-stage-map.md:82`) |
| Real gap | No digest; notification delivery is a draft map (`notification-ssot-map.md:128`) |

**Acceptance:** every sector lost, warden fight and storylet resolved in a coarse record appears once,
deduped on `(save, world, coarse record, fact)`; the digest is derived from the stored record, never
recomputed. **Verification:** verify-change → Core.Tests, Server.Tests.

### 14 · `world-difficulty-profile`

**Capability.** One difficulty profile id per world (W7), **stored in `trade-foundation`'s per-world
stamp** (owner of storage: trade-network `trade-foundation`, `trade-network-ideal.md:645`). This module
owns the profile **catalog** (v1: one `default` row) and the knobs this program reads: coarse loss
odds, AI escalation after victory. Trade owns its own knobs (`trade-network-ideal.md:665`).

| Bucket | Evidence |
|---|---|
| Wiring gap | `ruleset_version` is always `1` (`RpgStore.World.cs:245`) |
| Real gap | No profile catalog, no stamp |

**Acceptance:** an unknown profile id is a load rejection; a world's profile never changes after
creation; the default profile reproduces today's numbers. **Verification:** verify-change → Core.Tests.

### 15 · `multiverse-surface` (FE)

**Capability.** The player surfaces: a list of your worlds with their state, select/switch, the advance
dialog with the carry limit, station a warden, the digest layer. A layer over the World stage (GG-1),
never a new route. Designed through `/idea-ui` first; the multiverse map's drawing is undecided (ideal
§10). **Acceptance:** per `/idea-ui` output. **Verification:** `npm test`, `npm run build`, Playwright.

### 16 · `continuity-doc-amendment`

**Capability.** Change every document ideal §7 names **in one change, when this map is approved** (ideal
§7 end), plus the stale lines found while verifying. Guide mechanism pages are rendered: edit
`docs/guide/mechanisms/_content/<slug>.json`, then run `python docs/guide/mechanisms/_render.py` (it
writes the `.md`, the `site/mechanisms/*.html` twin and both README tables — `_render.py:1-13`). Pages
outside `_content` are edited by hand.

| # (ideal §7) | Document · line | What changes |
|---|---|---|
| 1 | `docs/guide/the-game.md:35-44` (Win/Lose table `:39-40`, slogan `:42`, *"Ending one world…"* `:44`), `:73` | Win = take the dominant enemy empire's seat → the world develops; Lose per Q2; slogan reworded (the owner's words, not *"You lose where you were"*) |
| 2 | `docs/guide/mechanisms/_content/new-world-prestige.json:3,9,11,24,41,74` → rendered `mechanisms/new-world-prestige.md:1,12,22,36,54,91` and `site/mechanisms/new-world-prestige.html:6-7,35,42,66,96,133` | Becomes *advancing to a new world* (slug kept or renamed in the same change with every link below) |
| 3 | `docs/guide/the-loops.md:11-21` | One row: old worlds ride the world-turn clock (hibernating) or the expedition clock (idle); count stays three |
| 4 | `docs/architecture/empire-resource-ssot.md:38` (class table *"No — dies with the map"*), `:74-75` (rule 5) | World stocks are map-scoped, never auto-bank; rule 5b ~~they cross only as cargo~~ → **round 6 S2: they cross only over a cross-world (`rift-trade`) route, never on an advance** |
| 5 | `docs/architecture/empire-economy-ssot.md:129-168` (§4, incl. *"state leaves 'active'"* `:145-146` and the three free things `:161-168`), `:227-245` (§7, incl. the wardens row `:240`) | §4 becomes the states and advance; §7 carries the new cure (ideal §6.6) and the warden's new cost |
| 6 | `docs/architecture/base-defense-ideal.md:95` (decision 18) | *"die with the map"* → map-scoped; **cross only over a `rift-trade` route** (round 6 S2, replacing *"only as cargo"*) |
| 7 | `docs/architecture/trade-network-ideal.md:88` | **Still stale:** principle 7 says rubble, ironwork and recruits *"die with the map"*. §2 (`:56-59`) and §8.6 (`:466-469`) are already amended |
| 8 | `docs/architecture/world-graph-ideal.md:26` | Victory becomes a state change, neutral wording |
| 9 | `docs/architecture/npc-story-events-ideal.md:466` (world scope *"Dies with the world, like loam"*), `:636`; `docs/architecture/npc-story-events-map.md:209` (world scope) | World-scoped story survives revisitable worlds; filed as an ask on the npc-story-events map, not edited by this program's session unless its `paths` allow |
| 10 | `docs/architecture/decisions.md` (new row: world states, outcome, one-active index, coarse record); `:48` (Multiverse wonder deferred for want of a world-surviving ledger — amend the reason); `:134` (`GetActiveWorld` filters `kind='map'` — add the active-uniqueness rule) | New row + two amendments |
| 11 | `docs/guide/features.md:58-59`; `docs/guide/how-you-play.md:103`; `docs/guide/the-rift.md:64,76-79,83,97`; `docs/guide/glossary.md:59` (Warden) + new rows (advance, developing, hibernating, idle, fallen); `docs/guide/site/index.html:291,557-561`; `_content/*.json` for `loam` (`:9,27,32,83`), `chronicle` (`:17,68`), `dave-level` (`:11,52`), `failure-branches` (`:41,60`), `sector-buildings` (`:65`), `souls` (`:20`), `essence` (`:26`), `unlock-chapters`, `specimens`, `world-generator`; `docs/guide/mechanisms/map-orders.md:23` (Warden = a creature bound to ground) | One-line rewrites; rerender |
| 12 | `docs/PRINCIPLES.md:348-350` (win/lose + slogan), `:389-391` (world stocks die with the map) | Same meaning as the sources, same change |

**Acceptance:** after the change, a search for *"lose where you were"*, *"dies with the map"*,
*"die with the map"* and *"into the next world"* across `docs/` returns only historical/superseded
contexts that say so; `python docs/guide/mechanisms/_render.py --check` passes;
`python scripts/audit-doc-citations.py --scope <each doc>` has no HIGH finding.
**Verification:** the render check and the citation audit; docs only.

---

## Tunables

`data/tuning/world-continuity.v1.json` (new): carry limit won / not won (legions; cargo is bounded by each legion's built capacity — `advance-carry` §2, audit 2026-09-20);
background multiplier per-mille and its decay curve per hibernating world; `catchUpCapTurns`; idle
period seconds and credited window; warden upkeep and defence weight; event budget per state; escalation
slowdown after victory; next-world template/intensity ladder; difficulty knobs per profile id. Difficulty
profile ids and display names in a sibling `world-difficulty-catalog.v1.json` (new, proposed; display names
never in the number file, numbers never in the catalog — audit 2026-09-20). Cross-world crossing cost is
`rift-trade`'s. **`gk-core/tools/tuning/publish.py` cannot publish a first version of a new domain** —
`latest_version` stops when no `<domain>.v*.json` exists (`gk-core/tools/tuning/publish.py:60-68`); the first
module that needs the file extends the tool (tunables-ssot T4), never hand-writes the JSON.

---

## Contradictions and propagations found

1. **The withdrawn free decay-freeze was still shipped — closed by `d6931e43a` (2026-09-19, `RulesetVersion`
   13)**; the cites that follow are the pre-fix sites (`LoamPhases.cs:197-203`, `LoamForecast.cs:30-33`,
   reachable via `WorldWardenEndpoint.cs:40` / `gk-core/src/FusionRpg.Server/Program.cs` / `BindWardenDialog.tsx`), while
   `warden-mortality-ideal.md:3-15` says it was withdrawn on 2026-09-13 and ideal §3.9 forbids it.
   `world-warden` removes it (ruleset bump).
2. **Two meanings of "warden".** The guide and shipped code mean *a creature bound to one sector*
   (`glossary.md:59`, `map-orders.md:23`, `WardenResolver.cs:12`); the ideal means *a commander and
   legion holding a world* (ideal §6.4). Q3 settles which survives.
3. **Non-releasable "for the life of the world"** (`RpgStore.Contracts.cs:276-283`) becomes "forever"
   once worlds persist; `empire-economy-ssot.md:240`'s cure for wardens relied on that.
4. **Corpse-cache decay tick collision across worlds** (`RpgStore.CacheDecay.cs:130-145` keyed by
   save + bare turn number, called from `RpgStore.WorldTurns.cs:700`). Fixed in `hibernation-clock`.
5. **Replay assumes template + per-turn `Step`** (`RpgStore.WorldTurns.cs:759-775`); coarse catch-ups and
   advance genesis break that assumption. `coarse-step` and `advance-carry` own the fix.
6. **Stamp retirement vs persistent worlds.** trade-network said *"old ruleset code retires when no
   active world carries it"* (`trade-network-ideal.md:645`). **Closed by the owner 2026-09-19:** old
   ruleset code retires only when no world in any state carries its stamp (see Owner decisions).
7. **The ideal's single five-value `state` enum mixes two facts** (attention and result). Assumption 1
   splits them; confirmed by the owner (Q1).
8. **npc-story-events map** has no per-state budget, no hibernating host, and a world scope that dies
   with the world (`npc-story-events-map.md:209`; ideal `:466`). Asks filed via `world-event-budget` and
   `continuity-doc-amendment`.
9. **`trade-network-ideal.md:88`** was missed by the round-3 amendment that fixed §2 and §8.6.
10. **`empire-economy-ssot.md:145-146`** says a world's `state` *"leaves 'active'"* at map end — no code
   ever did (`RpgStore.World.cs:243-245` insert, `RpgStore.WorldTurns.cs:686-689` the only update).

---

## Owner decisions (2026-09-19) — replaces the open questions

**Q1 · Two columns.** `state` (`active | hibernating | idle`) is split from a new `outcome` column
(`contested | won | fallen`). The ideal's five words — *active*, *developing*, *hibernating*, *idle*,
*fallen* — are **player-facing labels** derived from the pair (spec `world-state-vocabulary` §1).
Refined in spec: `outcome` is also a hashed `WorldState` field produced inside the step and persisted in
the column (spec `world-victory` §1), so replay reproduces it; `state` is never hashed.

**Q2 · Losing the active world.** It becomes `fallen`, the same rule as any world; **the save never
ends**. The Lose row in `docs/guide/the-game.md` is reworded (done, `the-game.md:40`). A fallen world
advances with the not-won carry limit (spec `world-fall` §3, `advance-carry` §2).

**Q3 · The per-sector warden.** The `bind-warden` verb is retired and every existing binding is released
through a system-issued `release-warden` command resolved by `WardenResolver`, freeing the contract slot
at no cost (spec `world-warden` §2–§3). **The live decay-freeze is removed by a separate implementer in
its own worktree (2026-09-19)**; `world-warden` records it as done and does not repeat it. *Warden* means
only the world warden from then on.

**Stamp retirement (contradiction 6, closed).** Old ruleset code retires only when **no world in any
state** — active, hibernating, idle or fallen — carries its stamp. (Supersedes the "no active world"
wording at `trade-network-ideal.md:645`; trade-foundation `world-stamp` owns the check.)

## Findings from the spec round (2026-09-19)

11. **No shipped template has a `boss-lair` seat.** `first-light` has no enemy-held sector;
    `two-hearths`' capital `z-home` is a `warcamp`. The dominant seat is a per-template declaration
    (`seat-outcome` §1); `first-light` gains an authored enemy capital in `world-creation` §5, with a
    template-version bump and golden re-bless. **Withdrawn in the round-4 reconciliation (R4-5):**
    `first-light` already has a guarded, unowned seat at `black-gate`, which is declared instead — no
    content change, no re-bless.
12. **Two more first-by-id reads**: corpse-cache decay start (`RpgStore.CacheDecay.cs:87-91`,
    `RpgStore.CargoFate.cs:175-179`) — fixed with the tick key in `hibernation-clock` §5.
13. **`MaxIntensityMilli = 3000` is an unregistered ceiling** on the advance ladder's intensity axis
    (`WorldValidation.cs:41`); `world-creation` §3 makes the step saturating and registers the bound.
14. **The realms axis has no source under continuity** (`ssot-power-scale.md:239` "one per retired
    world"; fed `0` at `ServerPowerIndexProvider.cs:49`). Recommendation to the power program:
    `realmsAdvanced` = worlds **won** (`world-victory` §5). **Superseded by owner Q8 (round 4): worlds
    held (not fallen)** — see the round-4 reconciliation.
15. **The warden's Hub strength has no Θ conversion on the closed power inventory** (`PowerLadder` has no
    inverse). The defence term waits on a `ssot-power-scale.md` §10 row (`world-warden` §5). **Round 4:**
    the strength is `legion-power`'s roll-up and the requested row converts a rolled-up power; the term is
    0 until it lands.
16. **The bind-warden endpoint's "no cross-store transaction" comment is wrong** — contracts and command
    logs share one database (`RpgStore.cs:4161`); the release migration uses one transaction.
17. **`coarse-step` needs trade-foundation `stock-deltas`** as its rate source, not only `world-stamp`.
18. **legion-build's stance list has no `warden`**; `world-warden` §4 adds it as a reviewed widening.

## Reconciliation 2026-09-19 (round 4)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) (binding; the register wins
where this map disagrees). Lines above line 276 were edited in place only, because
`npc-story-events/spec-story-ledger.md` cites this map by line number.

### Decisions applied

| Round-4 item | Change | Where |
|---|---|---|
| P / Q9 — warden strength is a power roll-up | Warden defence = Σ `legion-power` over the warden legions, computed Data-side and logged in the coarse record; `defenceΘ = ContestTheta(roll-up) × weight`, **0 until the power program's §10 row exists** | [spec-world-warden.md](world-continuity/spec-world-warden.md) §5; [spec-coarse-step.md](world-continuity/spec-coarse-step.md) §1, §5; `legion-build/spec-legion-power.md` |
| Q10 — system-issued commands | One shared path, built by `trade-foundation`: `release-warden` and the rift kinds register in its closed system-kind set; this program no longer defines `FileSystemCommandUnlocked`. `world-state-vocabulary` keeps only the not-active gate | [spec-world-warden.md](world-continuity/spec-world-warden.md) §3; [spec-world-state-vocabulary.md](world-continuity/spec-world-state-vocabulary.md) §5; spec-coarse-step §3 |
| Q8 — realms axis | `realmsAdvanced` = worlds **held** (outcome ≠ `fallen`), exposed as `CountWorldsHeld(save)`; the won-fact stays for the spine | [spec-world-victory.md](world-continuity/spec-world-victory.md) §5 |
| Q5 — both templates get a clan | The clans are `counterparties`' template versions (`first-light` v2, `two-hearths` v2). This program adds the rule both obey (every content edit is a new stamped version; a clan's seat never validates as the dominant seat; a clan stays off the win path) and moves **no** `first-light` content: its dominant seat is the existing, guarded `black-gate` | [spec-world-creation.md](world-continuity/spec-world-creation.md) §5; [spec-seat-outcome.md](world-continuity/spec-seat-outcome.md) §1, §3, §4 |

### Contradictions fixed

| # | Contradiction | Fix |
|---|---|---|
| R4-1 | `world-warden` §2 put the `bind-warden` refusal at submission "not in admission"; the shipped freeze fix (`d6931e43a`) put it in admission and bumped `RulesetVersion` to 13 (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:18-35`, `TurnEngine.cs:22-31`) | Spec corrected to the code; no second refusal |
| R4-2 | Assumption 6, `world-victory` §6 and `legion-build`'s `member-stack` said `RulesetVersion` is 12 | 13 (`TurnEngine.cs:125`) |
| R4-3 | Module 8 said the warden is a **standing order**; its spec (§4) makes it a **stance** | Map row, gate text and detail now say stance |
| R4-4 | Module 10 and `coarse-step` §3 said an advance departs by a **system-issued** command; `advance-carry` §1 resolves the player's own `depart`/`advance` orders and a genesis manifest | Map and `coarse-step` corrected |
| R4-5 | `seat-outcome` defined the dominant enemy as "whoever owns the declared seat", while `counterparties` `empire-roster` rule 1 defines it as the one `Zomboss`-kind faction; and `seat-outcome` missed `first-light`'s existing guarded seat `black-gate` (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:98-108`) | One definition (roster rule 1); `black-gate` declared; the authored enemy capital withdrawn, so `first-light` v2 is free for the clan |
| R4-6 | `world-state-vocabulary` §5 listed `hibernation-clock` as filing system commands; it files none | Removed |
| R4-7 | ~60 line citations into files the freeze fix changed (`TurnEngine.cs` +11/+13, `WorldCommandAdmission.cs`, `WorldState.cs` +2, `WorldCommand.cs` +3, `WardenResolver.cs` +7, `WorldWardenEndpoint.cs`, `LoamPhases.cs`) pointed at the pre-fix lines | Re-pointed in every file of this program and `legion-build` (one cite into removed code re-pointed by hand) |

### Asks answered (from `trade-network`)

| Ask | Answer | Where |
|---|---|---|
| rift A1 (`coarse-step` inputs carry route flows) | `CoarseInputs.RouteFlows`; applied in closed form on the anchor warehouse, each drain bounded by `throughput × n` and by stock | spec-coarse-step §1 |
| rift A2 (bounded, idempotent idle draw) | The route draw goes through the idle collect, bounded by the caller's amount, same transaction as the anchor | [spec-idle-world.md](world-continuity/spec-idle-world.md) §2 |
| rift A3 (digest folds `rift-facts`) | `rift.*` joins the closed digest prefix list | [spec-away-digest.md](world-continuity/spec-away-digest.md) §1 |
| rift A7 (one owner for the system-command seam) | **Owner decided Q10: `trade-foundation`** (not this program) | as above |
| rift A9 (republish the crossing-anchor view on a Data-side legion move) | `advance-carry` §3 step 5 calls `rift-trade`'s republish in its transaction; `world-warden` moves no legion Data-side, so it does not apply there | [spec-advance-carry.md](world-continuity/spec-advance-carry.md) §3 |
| rift A12 (rule 5b wording) | Accepted; the wording is recorded as owed in [spec-continuity-doc-amendment.md](world-continuity/spec-continuity-doc-amendment.md) — `empire-resource-ssot.md` is outside this session's edit fence | there |

### Cross-cluster conflicts (trade-network files — reported, not edited)

| # | Conflict | Recommended resolution |
|---|---|---|
| X-WC1 (**resolved, round 5 X11:** the system-only set is `release-warden`, `rift-window`, `rift-arrive`; `depart` and `advance` are the player's own orders) | The parallel `trade-foundation` reconciliation added `system-commands` (`trade-network/trade-foundation/spec-system-commands.md`), which is right, but it registers **"the `advance-carry` departure kind"** as a system kind (its §2) and lists `hibernation-clock` as a consumer (its interface table). `advance-carry`'s `depart`/`advance` are the **player's own** orders (`spec-advance-carry.md` §1) — as system kinds, admission would refuse them from every commander — and `hibernation-clock` files nothing | `system-commands`' closed set is `release-warden`, `rift-window`, `rift-arrive`; drop the departure kind and `hibernation-clock` from its consumer rows. `rift-route`'s "owner to be named" (ask A7) now cites `system-commands` |
| X-WC2 | `counterparties/spec-empire-roster.md` rule 3 exempts `first-light`'s landless dominant empire, which assumed this program would **not** add an enemy capital — while `world-creation` §5 still planned one as `first-light` v2 | Resolved on this side (R4-5): no capital is added; `black-gate` is declared; the exemption stays correct |
| X-WC3 | `logistics-flow/spec-lane-loss.md` switches escort to "a Hub-composed power index" from `general-member-hub`/`stack-combatant` | The index is `legion-build` `legion-power` (Σ of Hub output); the switch still waits on the power §10 row |

### Closed-vocabulary widenings (this program)

`away-digest` fact prefixes (+`rift.*`); system-command kinds (+`release-warden`, registered in
`trade-foundation`'s set, not a vocabulary of this program); legion-build stances (+`warden`, a reviewed
widening in legion-build's vocabulary, map finding 18).

### Owner questions (genuine)

**WC-R4-1 — DECIDED 2026-09-20 (round 5 D1): (a), held from creation.** *Original question:* Does a
world count as held from the moment it is created?
(a) Yes — the literal Q8 reading (outcome ≠ `fallen`). Each free advance adds one to `realmsAdvanced` at
once; what keeps it from being a free faucet is that every held world keeps full upkeep and pressure and
can fall. (b) Only once the world has been held through its first coarse record or N turns. (c) Only won
worlds that have not fallen (the draft recommendation, narrowed by Q8's "not fallen").
**Recommendation: (a).** It is the owner's words, and `Wf = Wa` puts the axis on both sides of every
contest, so an advance raises magnitudes on both sides rather than handing the player free contest odds.
If playtest shows advancing for Θ, (b) is a one-line change to `CountWorldsHeld`.

## DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches — world store, turn engine, loam phases, contracts,
    corpse-cache decay, expeditions (pattern only), legion cargo, product guide.
[x] Session boundary recorded: tasks/sessions/trade-network-idea-20260919.json lists this file in
    `paths` (direct, features/mega-merge). I did not re-run session-boundary-check.py myself; its
    recorded crossing note covers new files only.
[~] I read every doc in the §1 rows this session — read in full: the-game.md, the-loops.md,
    PRINCIPLES.md, world-continuity-ideal.md, warden-mortality-ideal.md, empire-resource-ssot.md,
    empire-economy-ssot.md §4-§7a, world-action-economy-map.md, world-map-program.md,
    data-architecture.md, DESIGN-GATE.md; decisions.md world rows (:7, :47, :48, :80, :134);
    spec-save-identity.md objective + decisions 1-2. NOT read this session: software-architecture.md,
    session-boundary.md, economy-principles.md, spec-soul-economy.md, contributing/architecture-map.md,
    world-map-runtime-ideal/spec/map/gaps + their two plans, perf-probe-plan.md, research/perf/
    00-baseline.md, match-runtime.md, unique-actor-runtime.md, unique-entity-effects.md. Gap stated;
    module specs must read them before writing.
[x] I checked decisions.md for a lock covering this — none locks world states; :134 and :48 amended.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run: 0 HIGH; 3 LOW D1 are proposed new files named as such, 1 LOW D3.
[x] I verified claims against CODE, not comments (e.g. the freeze via LoamPhases/LoamForecast bodies,
    the only UPDATE via grep, the tick key via the SQL text).
[x] I read the surrounding section of every rule I quoted.
[ ] Constraints tested — none run. "RulesetVersion bump" for world-warden is inferred from the Step
    behaviour change, not measured; "no golden moves" for world-state-vocabulary rests on decisions.md
    :134's header-hash statement, not a test run.
[x] Nothing contradicts a §2 invariant; contradictions with other docs are listed above.
[x] Corrections propagated: listed for continuity-doc-amendment; no other file edited by this change.
[x] No assertion pins a population count; closed enums (the two state vocabularies) are pinned with a
    stated reason.
[x] Event-refreshed caches: none introduced. Pending turns are computed, not cached.
[x] Orderings: select-world and CoarseStep splitting are specified order-independent.
[x] Actor magnitudes: warden strength consumes Hub output only (logged as an input); no private fold.
[x] No SOLID-violating parallel path: CoarseStep composes Step's rule functions; one active-world fact;
    one detector for victory and fall.
[ ] New rules need enforcement-registry rows (one-active-world index; no wall clock in CoarseStep; no
    background wallet write) — to be added by each module's spec, not by this map.
```

## Round 5 (2026-09-20)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) *Round 5* (R5-A, R5-X;
binding). Appended after the checklist; nothing above line 276 moved (the story-ledger line-number rule
above). Re-verified this session: the seat-sector slot lists
(`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:145-148`,
`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:45-47`, `:200-202`); the `Home` rule
(`gk-core/src/FusionRpg.Core/World/WorldValidation.cs:201-218`); `RulesetVersion` is 13
(`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`).

| Ruling | Change | Where |
|---|---|---|
| **A1** — every empire seat starts with a tier-1 Counting House and Storehouse | New §5a: the kit, selected by feature, placed in `WorldCreation.Rebuild` (replay-safe, legacy identity), refused when a seat has no free allowed slot; acceptance 8 | [spec-world-creation.md](world-continuity/spec-world-creation.md) §5a |
| **D1** — a new world counts as held from creation | WC-R4-1 closed; `CountWorldsHeld` unchanged (it already built the literal reading) | [spec-world-victory.md](world-continuity/spec-world-victory.md) §5 |
| **X6** — `RulesetVersion` is 13 | Already stated (R4-2) | — |
| **X7** — power roll-up owner is `legion-build` `legion-power` | Already cited by `world-warden` §5 and `coarse-step` §1 | — |
| **X11** — system-only kinds are `release-warden`, `rift-window`, `rift-arrive` | Already `coarse-step` §3's list; X-WC1 closed | — |

**Not applicable here:** A2–A4, B1–B4, C1–C4, X1–X5, X8–X10, X12–X16.

**Contradiction found and closed in the same round.** The A1 kit needs two free `Wildland` slots in every
empire seat sector; `first-light`'s `Home` has one, `two-hearths`' player home has none, and each `Zomboss`
seat on `two-hearths` has one. The recommended fix — the template versions `counterparties` already cuts
(`first-light` v2, `two-hearths` v2) add the slots, one golden re-bless for all three content changes — was
adopted concurrently in `trade-network/counterparties/spec-empire-roster.md` §3a. `world-creation` refuses a
template without them (`creation.start-kit-no-slot`) rather than skipping the kit.

Citation audit: `python scripts/audit-doc-citations.py --scope` run on this map and the two edited specs
after these edits.

## Audit 2026-09-20

An independent audit of this map and its sixteen specs against code and the binding documents
(`DESIGN-GATE.md` §2, §3, §5; `PRINCIPLES.md`; `tunables-ssot.md`; `validation-ssot.md`;
`contributing/testing-standard.md`; `economy-principles.md`; `power/ssot-power-scale.md` §10–§11;
`actor-hub-ssot.md` §8.1; `actor-layer-compose-ideal.md`; `battle-engine-ssot.md`;
`effect-atom/definitions.md` §1–§6; the seedsmith-design skill; `research/ai-native-generation/README.md`;
`trade-network/decisions-round-4.md`), all read in this session. Appended after the checklist; nothing
above line 276 moved (the story-ledger line-number rule). Every fix below is in the named spec.

### Findings

| # | Severity | Finding (evidence) | Status |
|---|---|---|---|
| A-WC1 | HIGH | `world-creation` minted ids `world-{n}` per save, but `rpg_worlds.world_id` is the table's **global** primary key (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:21`): the second save's `begin` would collide with the first save's `world-1` and fail | **Fixed** — ids `w{saveId}-{n}`; an existing id owned by another save is `world.id-collision`, never `ok.exists` (`world-creation` §1, acceptance 1) |
| A-WC2 | HIGH | `coarse-step` measured each rate once and multiplied it by `n`, but the Production phase also advances `WorldSlot.SlotDepletionMilli` every yielding turn and stops an exhausted slot (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:142-151`). A hibernating world's slots would never deplete and would keep yielding — a coarse step paying **more** than the full step, breaking its own acceptance 5 and diverging from `Step` | **Fixed** — per-slot closed-form depletion, and a rule that every hashed field a measured phase writes has a registered closed-form advance or `CoarseStep` refuses (§2 step 3, acceptance 11) |
| A-WC3 | HIGH | Past `catchUpCapTurns` the excess was forfeited — including that world's **upkeep and enemy pressure**. A player who never looked at an old world would stop paying for it: leaving would pay better than staying (this map's principle; economy-principles P2). A one-world-per-End-Turn background budget could not prevent it once several worlds hibernate | **Fixed** — the background pass catches up every world whose pending reaches the window, outside the budget; forfeiture becomes a structural safety bound, not the routine path (`coarse-step` §7, acceptance 13; `hibernation-clock` §3) |
| A-WC4 | HIGH | `advance-carry`'s manifest carried members, stance and cargo only. `legion-build` adds hashed legion state (`Count`, `MemberId`, `Gear`; `Standard`, `History`, `Doctrine`, `StandingOrder`), and owner ruling L2 resets standards and traditions **only on disband or rout** — an advance silently wiped them. Layer-5c bindings are keyed `legion:{worldId}/{entityId}` and were left behind in the old world | **Fixed** — the manifest is the whole entity with a per-field crossing table (a reflection test fails on an unlisted field); the legion reconcile runs in both worlds in the advance transaction (`advance-carry` §1, §3 step 6, acceptance 8) |
| A-WC5 | HIGH | `world-warden` Boundaries said *"Never: refusing `bind-warden` inside admission"* — the opposite of its own §2 and of the shipped code (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:18-22`) | **Fixed** — "never a second refusal at submission" |
| A-WC6 | MEDIUM | `world-warden` §4 capped wardens at one per world, while owner decision P defines defence as *"the sum of its warden legions"* and §5 sums them — a contradiction with a binding decision, and an unregistered count cap | **Fixed** — several warden legions, each commander-led (W5); the commander and the garrison upkeep are the price (§4, acceptance 10; `multiverse-surface` gate) |
| A-WC7 | MEDIUM | The first-loss draw `k = ⌈ln(1−u)/ln(1−p)⌉` divides by zero at `p = 0` and yields `k = 0` at `u = 0` | **Fixed** — edges stated and tested (`coarse-step` §5, acceptance 12) |
| A-WC8 | MEDIUM | The look trigger and the background trigger could simulate the same span twice | **Fixed** — expected-mark/turn guard; the loser writes nothing (`coarse-step` §7) |
| A-WC9 | MEDIUM | `world-difficulty-profile` put knob **numbers** in the catalog file; tunables-ssot §1 and T7 keep catalogs and number files apart in both directions | **Fixed** — ids and display names in the catalog; knobs under `difficulty.profiles.{id}` in the number file |
| A-WC10 | MEDIUM | With several `depart` orders past the carry limit, which one admission refuses was unstated (admission judges one command at a time) | **Fixed** — counts the turn's admitted departs; command-id ordinal order at `Reveal` (`advance-carry` §2, acceptance 9) |
| A-WC11 | MEDIUM | `coarse-step` acceptance 6 promised full replay, but the store re-derives step rows with the store-free resolver (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:769-775`), which cannot reproduce Hub-composed battles | **Fixed** — scoped to logs without a composed-battle flag; a flagged row refuses by name (`legion-build` `general-member-hub` Hard edges owns the flag) |
| A-WC12 | MEDIUM | DESIGN-GATE §2.16: the legion-scope reconcile ran only at the turn commit, so a world created with legions, and a coarse record that destroys one, were missed key-set edges | **Fixed** — creation and coarse records run it (`world-creation` §1, `coarse-step` §4); trigger table in `legion-build/spec-legion-owner-scope.md` §2 |
| A-WC13 | MEDIUM | The new tuning files (`world-continuity.v1.json`, `world-difficulty-catalog.v1.json`) have no mapping in `gk-core/scripts/verification-boundaries.v1.json` (tuning files are mapped one by one, for example `:880-883`), so `gk-core/scripts/verify-change.py:771` throws for them; no spec named the gap | **Fixed as an obligation** — rule R3 below; `world-difficulty-profile` Tunables |
| A-WC14 | LOW | The coarse record's platform stamp had no stated location | **Fixed** — `CoarseRecord.PlatformStamp`; replay refuses a mismatch (`coarse-step` §5) |
| A-WC15 | LOW | The decay tick method takes `int newTurn` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheDecay.cs:144`) but is handed the `long` save counter | **Fixed** — the parameter widens (`hibernation-clock` §5) |
| A-WC16 | LOW | `NextWorld` took `int` counts (`PRINCIPLES.md` §5: counts default to `long`) | **Fixed** (`world-creation` §2) |
| A-WC17 | LOW | `multiverse-surface`'s list cache named five invalidation triggers; `begin`, idle, recall and the End Turn's background catch-ups were missing | **Fixed** (its checklist) |
| A-WC18 | LOW | This map's Tunables line said the carry limit covers cargo weight; `advance-carry` §2 has no weight limit | **Fixed** in place |

Checked and **clean**: RPG layer only (no Unity field is written anywhere); one ActorHub read (warden
strength is the logged `legion-power` roll-up); `long` and `checked` on every magnitude;
`MaxIntensityMilli`, `catchUpCapTurns` and `idleCreditedWindowPeriods` registered as bounded or structural;
no population pin (the two state vocabularies, the nine-pair label product and the digest prefixes are
closed vocabularies with reasons); loam never crosses; no model call.

### Program rules added by this audit (binding on every module here)

- **R1 — `RulesetVersion` is taken at landing, never pre-assigned; and since round 6 C1 there is one bump
  per *wave*, not per module.** `world-victory`, `world-fall` and
  several `legion-build` modules each need the world ruleset bumped (13 today,
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`). Two branches that both wrote "13 → 14" would mint one
  number for two different rule sets, and replay's refusal (`RpgStore.WorldTurns.cs:759-760`) could no
  longer tell them apart. The module that lands second rebases onto the landed number, takes the next one,
  and re-blesses once more with the reason. Each bump's history line names its **wave** and the modules in it
  (round 6 C1): `world-victory` and `world-fall` share wave 2's bump rather than taking one each, and the
  family's whole order lives in [trade-network/landing-order.md](trade-network/landing-order.md).
- **R2 — store tests run in memory** (`contributing/testing-standard.md` R1): every Data test in this
  program builds its store through the shared in-memory helper; disk only where the disk is the subject.
- **R3 — a new tuning or seed file ships with its verification mapping** in
  `gk-core/scripts/verification-boundaries.v1.json`, in the change that publishes it.
- **R4 — owed enforcement-registry rows** (`gk-core/scripts/enforcement-registry.v1.json`; each lands with its
  module, never later): one active map world per save (the partial index is the guard); outcome written
  only by the step; no wall clock in `CoarseStep` (the determinism guard); no loop over `n` (acceptance 2);
  closed-form completeness (acceptance 11); no background wallet or banking write (source scan); no
  Data-side write to `WardenBindingId` (source scan); no cross-world copy (the conservation test).

### Reported, not fixable in this program's files

| Item | Owner | Fix |
|---|---|---|
| `stock-deltas` must name, per measured phase, every hashed field the phase writes (A-WC2's rule needs it as data, not prose) | `trade-network` `trade-foundation` `stock-deltas` | One field on the rate record; `coarse-step` §2 step 3 states the contract |
| A `ContestTheta` conversion row for a rolled-up power (warden defence stays 0 until it exists) | the power program (`ssot-power-scale.md` §10) | Already requested (round 4 P) |
| `effect-atom/definitions.md` §2 says a magnitude must fit `int` after curve scaling (`MagnitudeOverflow`) — an `int` range rule that `P(Θ)` outgrows at `Θ` ≈ 103,557 | the effect-atom program (that file wins over every spec) | Widen the rule to `long`, in the overflow standard's words |

### Owner question — answered (round 6 W1)

**A-WC-Q1 — What does the advance carry limit count?** ~~Open; recommendation (b), count units.~~
**Answered by the owner on 2026-09-20 (round 6 W1):** *"A weight limit, like a spacecraft's payload. A carry
is Σ(unit count × that unit type's carry capacity), read from the new `world.carry.capacity` derived channel.
Both units and goods draw on the same limit."* That is (b) with the unit's own **weight** instead of a flat
head — the reason the recommendation gave (a legion count binds nothing once stacks land) is the reason the
owner gave too. Applied in [spec-advance-carry.md](world-continuity/spec-advance-carry.md) §2 (the arithmetic,
the stated default, the logged load) and its tunables (`carryWeightContested`, `carryWeightWon`,
`carryWeightPerUnitDefault`, replacing the two legion counts). The roll-up is `legion-build` `legion-power`'s
`LegionWorldChannels.SumPerUnit` — never a private sum here. No open owner question remains in this program.

### DESIGN-GATE §5 (this audit)

`[x]` the §1 rows above read this session · `[x]` claims verified against code (the world id key, slot
depletion, the admission refusal, the re-derivation resolver, the decay tick signature) · `[x]`
`audit-doc-citations.py --scope` run on this map and every edited spec, no HIGH · `[ ]` no suite run
(documents only) · `[~]` session boundary: the edit fence is the caller's (this map and
`world-continuity/**`); `session-boundary-check.py` was not run by this audit · `[x]` corrections
propagated to the specs named in the table · `[x]` no population pin added.

---

## Round 6 (2026-09-20)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) *Round 6* (binding, the
owner's answers after the global standards audit). Where this section disagrees with anything above, it wins;
every change is made in the named spec, not only here.

| Ruling | Change in this program | Where |
|---|---|---|
| **S2** — trade goods cross worlds **only** by a `rift-trade` route | An advance carries **no** goods. `advance-carry`'s *"world stocks cross only as cargo"* is withdrawn, its `world_stock` cargo-kind ask to scoped-inventory is withdrawn, a departing legion with goods aboard is refused `carry.goods-aboard` (nothing written, never a silent void), and every place this program amended a document to *"cross only as cargo"* now owes the S2 sentence instead | [spec-advance-carry.md](world-continuity/spec-advance-carry.md) Objective, §4, §5, acceptance 11; [spec-continuity-doc-amendment.md](world-continuity/spec-continuity-doc-amendment.md) Objective + the owed-amendments table; §Modules row 10; the doc-amendment rows 4 and 6 |
| **W1** — the advance carry limit is a **weight**, like a spacecraft's payload | §2 rewritten: `load = Σ (Count × world.carry.capacity)` over every departing member with `Count > 0` (a bearer counts), against a `carryWeightContested` / `carryWeightWon` budget; refused past with `carry.limit`, **never clamped**, and the budget is an allowance a player raises by bringing carriers, not a ceiling. The roll-up is `legion-build` `legion-power`'s `LegionWorldChannels.SumPerUnit` — never a private sum. The load is **logged** so replay never recomposes live progression. The two legion-count tunables are replaced by three weight keys | spec-advance-carry §2, acceptance 2 and 10, Tunables; [spec-multiverse-surface.md](world-continuity/spec-multiverse-surface.md) (the dialog reads the budget and the load, computing neither) |
| **W2** — import/export through the rift gate is its own program, `world-transit` | Named as a future program this module **consumes, never implements**. Until it exists, an advance moves only what the weight limit allows and goods cross by rift route | spec-advance-carry §5 (the ownership table), Dependencies; §Cross-program dependencies |
| **D2** — six `world.*` channels compose in ActorHub and roll up like `legion-power`; `world-derived` registers them | This program reads exactly one of them, `world.carry.capacity`, behind a **stated default** (`carryWeightPerUnitDefault` in `world-continuity.v{n}.json`) until `world-derived` ships. Nothing here defines or folds a channel | spec-advance-carry §2, Tunables; §Cross-program dependencies; `legion-build/spec-legion-power.md` §6 |
| **C1** — one capability flag and one ruleset bump **per wave** | Locked assumption 6 rewritten. `world-victory` and `world-fall` no longer each take a bump: both ride **wave 2's** single bump with `coarse-step`, which also stops claiming *"no `RulesetVersion` bump"*; `world-warden` and `advance-carry` ride **wave 3's** and stop claiming "no bump" (they grant features). Every module's wave is the Wave column of §Modules, and the family's bump order is [trade-network/landing-order.md](trade-network/landing-order.md). A re-bless stays with whichever module moves a golden | Assumption 6; *Audit 2026-09-20* R1; [spec-world-victory.md](world-continuity/spec-world-victory.md) §6 + acceptance 4; [spec-world-fall.md](world-continuity/spec-world-fall.md) §5; [spec-coarse-step.md](world-continuity/spec-coarse-step.md) Hard edges; [spec-world-warden.md](world-continuity/spec-world-warden.md) Hard edges; spec-advance-carry Hard edges |
| **C2** — one neutral `StructureKind.Feature`; `StructureKind.Exchange` withdrawn | This program places feature buildings (the A1 start kit) but owns no kind. The kit's rows could never have loaded under the old `structureKind: none` rule (global audit C2 named the kit as a victim); C2 fixes it in `empire-seed`, and the kit's landing follows the wave that lands `sector-features` and the `Feature` member | [spec-world-creation.md](world-continuity/spec-world-creation.md) §5a |
| **S1** — a feature building counts for nobody until one faction owns both its sector and its slot | The start kit places both rows on slots of a sector the empire owns, setting both owners in the same creation write. The **rule** is read from `trade-foundation` `sector-features`, never restated here, and no gate in this program re-derives building ownership | spec-world-creation §5a |
| **C3** — banking waits on the save-identity re-key | Nothing in this program banks: `background-yield` lands yield in warehouses and is *"collected, never auto-banked"*, and an advance never banks. So nothing here waits — the wait belongs to `sector-yield`'s banking, `exchange` settlement and `legion-build`'s banked draws | — (stated; `background-yield` unchanged) |
| **m7** (global audit) — the cross-program table still called `sector-yield` and `rift-trade` *"Ideal only"* | Both rows updated to *map + specs written*, with the round-6 consequence named; a third row names `world-transit` and `world-derived` as named-but-unspecced | §Cross-program dependencies |
| **m12** (global audit) — numeric knobs in a `*-catalog` file | **Already fixed** by the 2026-09-20 cluster audit: the catalog carries identity and player words only, and the knobs live in `world-continuity.v{n}.json` keyed by profile id, with a load rejection when either side is missing. Re-checked this round, no change needed | [spec-world-difficulty-profile.md](world-continuity/spec-world-difficulty-profile.md) §1 |

### Closed-cycle landing note (global audit M1)

M1 listed `advance-carry` → `rift-trade` `crossing-anchor` (the republish call) against `crossing-anchor` →
`advance-carry` (its trigger T5) as a cycle. **One line closes it:** `advance-carry` lands first and publishes
a post-move hook (`AfterCrossWorldMove`); `crossing-anchor` **registers** into it when it lands. Before that
the hook has no subscriber and the commit does nothing extra. Neither spec waits on the other, and no
capability flag spans both (C1: separate waves, separate bumps). Recorded in spec-advance-carry Dependencies.

### DESIGN-GATE §5 (this round)

`[x]` Read this session: the register's Round 6 (whole), the global audit (C1–C3, M1–M8, minor table), this
map and every spec edited · `[x]` Verified against code: `WorldCommandAdmission.cs:24` (shared admission),
`TurnEngine.cs:233` (`Reveal` re-admission), `:125` (`RulesetVersion` 13), `ScopedInventoryPolicy.cs:39-49`
(cargo capacity from member count), `RpgStore.LegionCargo.cs:273-274` (the two cargo kinds),
`WorldValidation.cs:201-218` (the player's seat) · `[x]` citation audit run on every edited file · `[ ]` no
suite run (documents only) · `[~]` session boundary: the caller's fence (this map, `world-continuity/**` and
the other six named trees) · `[x]` corrections propagated (assumption 6, the cross-program table, the doc
amendments, R1, A-WC-Q1) · `[x]` no population pinned · `[x]` **no cap added** — the carry budget is an
allowance the player raises, refused past and never clamped · `[x]` no actor magnitude composed here (the
carry roll-up is `legion-power`'s over Hub output) · `[x]` every new number is a named tunable with a home
file.

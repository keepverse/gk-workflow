# Spec: delve-host

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `delve-host`, row 17 of the [npc-story-events map](../npc-story-events-map.md) (`:222`), wave 4. Depends on
`outcome-routing` and `cast-resolver`, and on this program's `delve-live-start` and `delve-live-rooms` (rows 28–29,
wave 1), which build the Delve's live path. Owner ruling 2026-09-19 (round 3): that path moved from party-dungeon
to this program and is placed before this module; it was an external dependency (map `:179-183`). Gate **G5** (`npc-story-events-map.md:300`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Make the Delve a storylet host with people and consequences:

1. **Room kind → host kind**: `curio`, `shrine`, `trap`, `wild`, `merchant`, `unknown` (and the `rest` ambush pool)
   map onto the `delve.*` host kinds, so widened storylets are selected by the one engine for Delve rooms.
2. **Characters in rooms**: a named **trader** in a `merchant` room, a **captive** in a `wild` room's cage variant, a
   **chronicler** at a `shrine`.
3. **Story chains advance** through `storylet-selection`'s priority tier: the next link after its predecessor was seen.

It **plugs into** the room-entry draw and answer route that `delve-live-rooms` builds
(`spec-delve-live-rooms.md` §1–§3; Owner ruling 2026-09-19 (round 3): formerly party-dungeon's). It does not build
them, does not change room kinds, the delve graph roll or the delve battle profile (map ownership table,
`:311-312`).

Success looks like: with the game closed, a fixture delve room of each event-capable kind yields a legacy
resolution or a widened offer through one call; a merchant room casts a named trader; an arc's link 2 is preferred
in a later room after link 1 was seen; the Delve's stream-identity fixture (`spec-storylet-reseam.md` Testing) is
still byte-identical for legacy rows. Once `delve-live-start` and `delve-live-rooms` land, G5 is proven through
real `/api/delve/*` routes against a real delve row.

## Locked anchors

- **One engine; the Delve is its first host** (NS1, map `:398`; `spec-storylet-reseam.md` §2 — `DelveStoryletHost`
  implements `IStoryletHost` and keeps `EventDeck.Resolve`/`Answer`'s exact signatures).
- **Room kind → event kind today**: `curio → curio`, `shrine → shrine`, `trap → trap`, `merchant → bargain`,
  `wild → story`, `rest → encounter-event`, and `unknown` = any (`gk-core/src/FusionRpg.Core/Delve/Events/EventFilters.cs:16-28`).
  Legacy rows learn their hosts from this map (`spec-storylet-contract.md` §3).
- **The Delve's live path is this program's `delve-live-start` and `delve-live-rooms`** (Owner ruling 2026-09-19
  (round 3); was party-dungeon's, map `:179-181`, `:311`). Today: `ImportDungeonDomains` has no caller
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs:225`); `/start` returns before `CreateDelve`
  (`gk-core/src/FusionRpg.Server/DelveEndpoints.cs:175-176`); `MarkRoom` and `RecordEventSeen` have no production caller
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:379`, `:440`); the registered wild routes are `/rooms/{id}/talk`,
  `/cage`, `/pray` (`gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs:62-67`).
- **The cage variant**: *"at first entry, `NextPerMille() < wild.cageMilli` on `dungeon:wild:{r}:{c}:cage` makes the
  room a cage room"* (`gk-core/src/FusionRpg.Core/Delve/Wild/Cage.cs:11-14`).
- **The merchant sells nothing yet** (`gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:17`); *"the trader's face and lines
  do not wait"* (map `:188`).
- **Live-probe standard** (DESIGN-GATE §1 Live probe row; `docs/contributing/live-probe-standard.md`): G5 is RPG Server
  scope — real routes, a real delve row, read back through the normal query path.

## Design

### 1. Host kinds and the host adapter

`DelveStoryletHost` (created by `storylet-reseam`) gains the widened half:

| Room kind | Host kind (`spec-narrative-vocabulary.md` §2) | Legacy event kind (unchanged) |
|---|---|---|
| `curio` | `delve.curio` | `curio` |
| `shrine` | `delve.shrine` | `shrine` |
| `trap` | `delve.trap` | `trap` |
| `wild` | `delve.wild` | `story` |
| `merchant` | `delve.merchant` | `bargain` |
| `unknown` | `delve.unknown` (after `UnknownPity` resolves to an event, unchanged) | any |
| `rest` | `delve.rest` (ambush pool, `AmbushDraw`) | `encounter-event` |

```csharp
namespace FusionRpg.Core.Delve.StoryletHost;

public abstract record DelveRoomStory
{
    /// A legacy row drew: today's EventResolution, byte-identical to EventDeck.Resolve.
    public sealed record Legacy(EventResolution Resolution) : DelveRoomStory;
    /// A widened storylet was selected: an offer the answer route resolves through ChoiceAnswerService.
    public sealed record Widened(StoryletOffer Offer) : DelveRoomStory;
    /// The room resolved to no event (an unknown room that became a cache, merchant or fight; a quiet room).
    public sealed record None(string Reason) : DelveRoomStory;
}

public static partial class DelveStoryletHost
{
    /// The one call delve-live-rooms' room-entry route makes (Owner ruling 2026-09-19 (round 3); was party-dungeon's). Legacy and widened rows share one pool; the engine's
    /// tiering decides which is drawn (priority links pre-empt; legacy rows sit in the pool tier).
    public static DelveRoomStory EnterRoom(DelveRoomFact room, DelveRoomContext ctx);
}
```

- **Legacy text is never blank** (Owner ruling 2026-09-19 (round 4)). A `Legacy` resolution is shown to the player
  through the `narrative-text` bridge from day one: narrative-seed's wave-0 `dungeon-generator-repair` regenerates the
  legacy events clean and keyed, so a legacy row carries text keys like any widened row, and `delve-event-regen`
  replaces those rows later. This module never renders a legacy row's raw seed text and never ships a legacy row
  without keys; a legacy row with no keyed text is `dungeon-generator-repair`'s defect to regenerate, never a
  hand-edit here (generated data is never hand-edited).
- **One pool.** Legacy and widened rows are one catalog (`spec-storylet-contract.md` §3). A room first runs
  `UnknownPity` exactly as today, then asks `storylet-selection` for the room's host kind. If the selected row is
  legacy, the adapter runs today's draw-and-instantiate path and returns `Legacy` — the stream-identity fixture proves
  this path is unchanged. If widened, it returns `Widened` with the offer.
- **Pulse = room entry.** Dense host: the Delve's `firing.delve.* = 1000/0` (`spec-narrative-vocabulary.md` §4) — the
  room kind already decided that an event happens; the engine decides which.
- **Host clock `delve.room`.** The per-player count of rooms marked visited across all delves at the moment of entry
  (derived from `rpg_delve_rooms.visited`, never stored separately). Cooldowns on this clock are absent on purpose:
  the Delve's recent-cells filter is its cooldown (`spec-narrative-vocabulary.md` §4, `cooldown` row).
- **Seen.** Every offer appends `storylet.seen` through the ledger wrapper that `RecordEventSeen` already became
  (`spec-story-ledger.md` §6); the per-delve `rpg_delve_rooms.event_id` record stays the room's own state
  (`spec-story-ledger.md` §1). Writing it is `MarkRoom`'s job in `delve-live-rooms`' entry route
(`spec-delve-live-rooms.md` §2).
- **Θ.** `HostContentTheta.ForDelveRoom(roomTheta)` — the room's already-composed Θ, never recomposed
  (`spec-host-content-theta.md` §3).
- **Budget.** `DelveHostBudget : IHostBudget` returns the room's `dungeon-room` loot source and the delve's existing
  event soul path; `SpendableStocks = [souls, supply]` (`spec-outcome-routing.md` §3). Effects apply to the party
  through `EventOutcomeDispatch` as today.

### 2. Characters in rooms

A character is placed in a room only when the room is entered, through `cast-resolver`:

| Room kind | Role cast | When | What it adds |
|---|---|---|---|
| `merchant` | `trader` | every merchant room | a named face and lines on the (still sell-nothing) merchant; `bargain` storylets cast the trader into their `trader` role |
| `wild` (cage variant only) | `captive` | the cage roll made the room a cage room (`Cage.IsCageRoom`) | the caged occupant **is** the captive character; freeing it is a `recruit` outcome → ownership transfer (the same specimen joins) |
| `shrine` | `chronicler` | every shrine room | chronicler storylets; spine fragments placed at shrines (`spine-progress`) |

**Residency.** Delve residents live in a domain: home `delve-domain:{domainId}` (`spec-character-registry.md` §3,
`home_kind`). Domain progress is per player — `rpg_domain_progress` is keyed `(player_id, domain_id)`
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs:76-80`) — so domain residents are **save-scoped**: a player who
returns to a domain meets the same trader. Casting a domain's residents happens on the domain's first delve, on the
stream `narrative:cast:delve-resident`, target `{domainId}:{roleId}:{index}`, through `CastCreatureCharacter`; a
replay is a no-op through the cast fact's dedupe key. How many residents per role per domain is
`casting.delveResidentsPerRole.{role}` (tuning, added here; starting 1 trader, 1 chronicler, 2 captives — a returning
player recognizes a face without every room being the same one).

**The captive and the Delve's wild-room engine.** The shipped wild path (`TalkTree` verbs, `Disposition`, `WildMemory`,
`RecruitMint`; routes at `DelveWildEndpoints.cs:62-67`) keeps handling **unnamed** wild creatures unchanged. A cage
room with a cast captive routes its storylet through the engine instead: the captive's disposition is its relation
band (`spec-relation-ledger.md`), not the wild room's per-encounter disposition, and joining is
`TransferCharacterToRoster`, not a fresh `RecruitMint`. One creature never has both: a cage room is either a cast
captive (widened storylet) or an unnamed occupant (shipped wild path), decided at first entry by whether
`cast-resolver` found a captive character for the domain.

### 3. Story chains

A widened arc link in the Delve is drawn in the **priority tier** once its predecessor was seen
(`storylet-selection`); the arc's cast and pins come from `arc.started` (`spec-cast-resolver.md` §4,
`spec-story-ledger.md` §4). Legacy `chainRef` chains are **not** advanced by this module: the committed corpus has two
dangling chains (ideal §3.4, `npc-story-events-ideal.md`) and G2 turns that into a preflight failure
(`spec-storylet-contract.md` §6); legacy chains retire with `delve-event-regen` (`narrative-seed-map.md:221`). So
"story chains go live" means widened arcs, which is the shape narrative-seed generates.

### 4. What the live-path routes call

Owner ruling 2026-09-19 (round 3): the routes are `delve-live-rooms`' and `delve-live-start`'s (this program), built
earlier in the build order; the party-dungeon task ids in brackets are the ones transferred to them.

| Route (module; former task) | Calls |
|---|---|
| `POST /api/delve/rooms/{id}/enter` (`delve-live-rooms`; D3.9 draw half) | `DelveStoryletHost.EnterRoom(room, ctx)`; persists `Legacy.Resolution.EventId` through `MarkRoom` as today, or the widened offer's storylet id |
| `POST /api/delve/rooms/{id}/answer` (`delve-live-rooms`; D3.9 answer route) | legacy: `DelveStoryletHost.Answer` (unchanged signature); widened: `ChoiceAnswerService.Answer(playerId, offerRef, slot)` (`spec-choice-resolution.md` Interface) then `OutcomeExecutor` |
| quest offer at `CreateDelve` (`delve-live-start`; D4.14 offer half) | unchanged; delve quests appear in the quest log through `quest-log-contract` |

This module adds **no route**. `delve-live-rooms` lands first and calls `DelveStoryletHost.Resolve`/`Answer` (legacy
only); this module then adds the `EnterRoom` branch without changing that route's signature.

## Data shapes

- No table. Residents are `rpg_narrative_character` rows (`spec-character-registry.md` §3).
- Tuning (**declared in `narrative.v1.json` at wave 0, plan §4 D4; current version `v2`**): `casting.delveResidentsPerRole.{trader,
  chronicler, captive}` (count, `long`).
- Resident roles per room kind (`merchant → trader`, `wild/cage → captive`, `shrine → chronicler`) are a catalog, added
  to `data/tuning/narrative-cast-catalog.v1.json` (new) (`spec-cast-resolver.md` Data shapes) as `residentRolesByRoomKind`.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `delve.room` clock | `long` | a count of rooms visited over a save's life |
| resident counts | `long` tuning, narrowed `checked` to `int` for a loop bound | a small count per domain |
| Θ | `int` | `RoomTheta.Theta`, passed through |

## SOLID notes

- **S:** the Delve decides **when** (room entry) and applies outcomes to its party; the engine decides **which**; casting
  decides **who**.
- **O:** new room-hosted content is seed data; this module does not change for it.
- **L:** legacy resolution through `EnterRoom` equals `EventDeck.Resolve` byte for byte (the reseam's fixture).
- **D:** depends on `storylet-selection`, `cast-resolver` and `IHostBudget`, never on a second deck.
- No second wild-room engine: unnamed wild creatures keep the shipped path; cast captives use the one storylet engine.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Delve/StoryletHost/DelveStoryletHost.cs','src/FusionRpg.Server/Narrative/DelveResidentCast.cs','tests/FusionRpg.Core.Tests/Delve/StoryletHost/DelveHostTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Delve.StoryletHost|FullyQualifiedName~Delve.Events|FullyQualifiedName~Delve.Wild"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Delve"
```

The G5 live proof is run once, after `delve-live-start` and `delve-live-rooms` land, immediately after a full-suite
run (AGENTS.md verification boundary, point 3).

## Structure

```
src/FusionRpg.Core/Delve/StoryletHost/DelveStoryletHost.cs      (edited: EnterRoom, DelveRoomStory)
src/FusionRpg.Core/Delve/StoryletHost/DelveHostBudget.cs        (new: IHostBudget)
src/FusionRpg.Server/Narrative/DelveResidentCast.cs             (new: domain resident casting on first delve)
data/tuning/narrative-cast-catalog.v1.json                      (edited: residentRolesByRoomKind)
tests/FusionRpg.Core.Tests/Delve/StoryletHost/DelveHostTests.cs           (new)
tests/FusionRpg.Server.Tests/Narrative/DelveResidentCastTests.cs          (new; in-memory store)
```

## Testing strategy

Game closed; fixture domain and corpus; in-memory store.

- **Legacy parity:** for 64 seeds × every event-capable room kind, `EnterRoom` on a legacy-only corpus returns
  `Legacy` with a resolution byte-equal to the reseam's recorded fixture.
- **No blank legacy event (round 4):** every `Legacy` resolution in the fixture corpus carries resolvable text keys
  through `narrative-text`; a fixture legacy row without keys is refused at load, not rendered empty.
- **Widened offer:** a fixture widened storylet hosted on `delve.merchant` is offered in a merchant room with the
  trader cast into its `trader` role.
- **Chain:** link 2 of a fixture arc is drawn in the priority tier in a later room after link 1's `storylet.seen`;
  before that it is never drawn. Seen in room A then entering B, and the reverse room order, give the same tiering.
- **Residents:** first delve in a domain casts the configured residents once; a second delve casts none and meets the
  same `characterId`s.
- **Cage split:** a cage room with a cast captive yields a widened storylet; a cage room with no captive available
  falls through to the shipped wild path untouched (its tests pass unchanged).
- **Captive joins as itself:** freeing a cast captive transfers the same `instanceId` (via `outcome-routing`).
- **No route added:** a reflection test over `DelveEndpoints`/`DelveWildEndpoints` route tables is unchanged by this
  module.
- **No population:** fixtures only.

**G5 live proof (after `delve-live-start` and `delve-live-rooms`):** RPG Server scope only. Start a real delve
through `POST /api/delve/start` for a real player and domain; enter a room through the real room-entry route
(`POST /api/delve/rooms/{id}/enter`); read
the room back through the normal delve read route and assert its event id; read `storylet.seen` and the resident
character through the quest-log route (`quest-log-contract`). No `debug.*` command and no fabricated room row is
evidence (`docs/contributing/live-probe-standard.md`).

## Success criteria

1. Every event-capable room kind maps to a host kind; legacy rows resolve byte-identically. 2. Merchant, cage and
shrine rooms carry named characters. 3. Widened arc links advance in the priority tier. 4. No route, room kind, graph
roll or battle profile changes. 5. G5 passes through real routes once `delve-live-start` and `delve-live-rooms` land.

## Boundaries

- **Always:** one pool for legacy and widened rows; residents cast once per domain; answer widened rows through
  `ChoiceAnswerService`.
- **Ask first:** changing a room kind or the cage roll; a second resident per merchant.
- **Never:** build the room-entry or answer route (`delve-live-rooms`'); advance a legacy `chainRef`; a second
  wild-room engine; a G5 proof from a debug surface.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `DelveStoryletHost.EnterRoom` → `DelveRoomStory` | `delve-live-rooms`' room-entry route (Owner ruling 2026-09-19 (round 3)) |
| `DelveHostBudget` | `outcome-routing` |
| `DelveResidentCast.EnsureDomainResidents(playerId, domainId)` | `delve-live-start`'s `/start` path, which now owns the live `CreateDelve` call (Owner ruling 2026-09-19 (round 3); was a filed ask on party-dungeon): call on first delve per domain |

## Contradictions found (report; not fixed here)

1. **Resident scope.** Map locked assumption 9 (`:157-158`) and ideal §6.3 make *local* characters world-scoped. A
   Delve domain's progress is per player, not per world (`RpgStore.Domains.cs:76-80`), so a domain resident is local
   to a domain the player keeps across worlds. This spec makes domain residents save-scoped; if party-dungeon later
   binds domains to a parent world, residents follow that scope with no code change beyond the cast call's scope
   argument.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: the Delve (host only), narrative engine, casting, characters, live probe.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map rows 17, G5, ownership table; ideal §3.2, §6.6; DESIGN-GATE Live probe row; sibling specs
    storylet-reseam, storylet-contract, story-ledger, cast-resolver, character-registry, host-content-theta,
    narrative-vocabulary; code: EventFilters, EventDeck, Cage, DelvePrices, DelveEndpoints, DelveWildEndpoints,
    RpgStore.Delve, RpgStore.Domains.
[x] Every claim cites file:line.
[x] Nothing assumed about goldens: legacy parity is a fixture test.
[x] No population pinned.
[x] No cache.
[x] Order: chain tiering tested in both room orders.
[x] Actor numbers: none; effects keep EventOutcomeDispatch.
[x] No parallel path: one pool, one engine; the shipped wild path keeps unnamed creatures only.
[ ] Registry row: none new (the NS1 guard is storylet-reseam's).
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (Battle engine SSOT, Economy, Standalone, Live-probe rows),
§2 (1, 2, 9, 15), §3, §5; `live-probe-standard.md` (RPG Server scope for G5); round-3 (Delve live path absorbed into
`delve-live-start`/`delve-live-rooms`) and round-4 rulings.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | MEDIUM | Round-4 ruling: the spec did not say how a legacy row's text reaches the player, leaving a blank or raw-text legacy event possible | **Fixed** (§1 bullet, test): keyed through `narrative-text` from day one via `dungeon-generator-repair`; `delve-event-regen` replaces later |
| 2 | LOW | `SpendableStocks = [souls, supply]`, while `offer:supply` is unpriced in v1 (`spec-choice-resolution.md` §5) — consistent (the choice is shown ineligible with its reason), stated so no reader reads `supply` as spendable today | Holds; noted |
| 3 | LOW | Ideal line citation drifted | **Fixed**: cited by section |

Checked and holding: routes are `delve-live-rooms`' (`POST /api/delve/rooms/{id}/enter`, `/answer` —
`spec-delve-live-rooms.md` §1, §3) and this module adds none; legacy resolution byte-identical; fights stay the
Delve's encounter path (battle-engine SSOT); rewards are the room's own budget (the one host where "out of, never on
top of" holds exactly); G5 is RPG Server scope through real routes and a real delve row, never `debug.*`; residents
are save-scoped with a stated reason.

**Registry row:** none new (NS1 is `storylet-reseam`'s). **Boundary ask:** `src/FusionRpg.Core/Delve/StoryletHost/**`
→ `FusionRpg.Core.Tests` filter `Delve.StoryletHost|Delve.Events|Delve.Wild`.

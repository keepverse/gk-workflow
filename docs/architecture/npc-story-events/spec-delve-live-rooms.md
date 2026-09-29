# Spec: delve-live-rooms

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `delve-live-rooms`, row 29 of the [npc-story-events map](../npc-story-events-map.md), **wave 1**. Created by
**Owner ruling 2026-09-19 (round 3): npc-story-events absorbs the Delve live-path wiring** from party-dungeon. Depends
on `delve-live-start` (a real delve row to play; code and tests are independent of it), on `narrative-text` (the lingui
codegen bridge that renders event text) and on narrative-seed's wave-0 `dungeon-generator-repair` having regenerated
the legacy event corpus clean and keyed (Owner ruling 2026-09-19 (round 4); §4). Prerequisite of `delve-host`
(row 17), which plugs its storylet branch into the two routes built here. Transfer note: the top of
`tasks/party-dungeon-todo.md`.

## Objective

Make a started delve's rooms **play** in production, wiring the event engine party-dungeon built and tested:

1. **Room entry.** No route moves a party: `MoveParty` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:321`) has no
   production caller, so rooms are never entered and `MarkRoom` (`:379`) is never called.
2. **The draw.** `EventDeck.Build`/`Resolve` (`gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:146`, `:218`) and the
   seen-writes (`MarkRoom`'s `eventId`, `RecordEventSeen`, `RpgStore.Delve.cs:440`) have no production caller, and the
   one fact the forced-outcome path still lacks — a real `holdsOverrideStock` sourced from the party's pack — is never
   supplied (`EventDeck.cs:99`, `:284`).
3. **The answer.** No route answers an event: the Delve's registered routes are `/recovery-ritual`, `/domains`,
   `/start`, `/{delveId}` (`gk-core/src/FusionRpg.Server/DelveEndpoints.cs:35-57`) and `/rooms/{id}/talk`, `/cage`, `/pray`
   (`gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs:62-67`); `DelveEventEndpoints.cs` is only named in
   `docs/architecture/party-dungeon/spec-event-deck.md:344`.
4. **Text on the wire.** The web's `EventView` carries no name or flavor and every field is `Pending`
   (`gk-web/web/fusion-rpg-web/src/contract/types.ts:1276-1282`).

Success looks like: a real party enters a real room through a route; the room's event is drawn once, its id written
at the draw, its seen scopes recorded; the steered party answers through a route; the result and the event's text
reach the web contract — with the game closed and replay-safe.

## Locked anchors

- **Party-dungeon designed the event deck; this module calls it.** Draw, seen scopes and answer persistence are
  `spec-event-deck.md` §8: *"Rows are written with the room's `event_id` at the **draw**, not at extraction — a wipe
  does not un-see an event"*; *"the answer in `decisions_json`"*; *"the answer persisted before it is applied"*
  (Boundaries). Nothing here re-decides a deck rule.
- **Room movement never steps a turn**: `MoveParty` updates the party's position and `visited` in one transaction and
  reuses `LaneGate.Refusal` (`RpgStore.Delve.cs:315-321`); the delve host never calls `TurnEngine.Step`
  (party-dungeon row P2).
- **One engine**: after `storylet-reseam` the deck lives at `src/FusionRpg.Core/Narrative/Storylets/` behind
  `DelveStoryletHost` with `Resolve`/`Answer`'s exact signatures (`spec-storylet-reseam.md` §2). Whichever of the two
  lands second carries the other's call sites along (map, *Dependency direction*).
- **The steering check** is today's `ProductionIsPartySteered` seam, which returns `true` unconditionally
  (`DelveWildEndpoints.cs:73`); this module uses the same seam and does not widen it.
- **Keyed text only**: story-scene decision S4 routes player text through lingui, and *"`msg({ message:
  someRuntimeString })` is a hard error"* (`gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts:13-19`).

## Design

### 1. Room entry — `POST /api/delve/rooms/{id}/enter`

Beside the wild routes' shape (`DelveWildEndpoints.cs:58-67`, body `{playerId, delveId, partyEntityId}`,
`:148-156`), plus a `correlationId`:

1. ownership and steering checks, as the wild routes do;
2. `MoveParty(delveId, worldId, partyEntityId, id, doorCatalog)` — a refused door returns its `LaneGate` reason;
3. on the room's **first** entry, if its kind is event-capable, the draw (§2); a room already drawn returns its
   stored `event_id` (the per-delve seen set, `LoadPerDelveEventSeen`, `RpgStore.Delve.cs:409`) and never draws twice;
4. `DelveUpdated{delveId, revision}` through the built but uncalled `NotifyDelveUpdatedAsync`
   (`DelveEndpoints.cs:194`), whose own comment names `MarkRoom` as its missing trigger (`:167-170`).

A replay with the same `correlationId` returns the first result. Fights, caches, rests and the wild room keep their
own paths: this route moves and draws; it does not resolve a battle.

### 2. The draw at entry

In one store transaction — Audit 2026-09-19: `MoveParty`, `MarkRoom` and `RecordEventSeen` each open their own
connection today (`RpgStore.Delve.cs:321-325`, `:379-385`), so "one transaction" needs one new Data method,
`RpgStore.EnterRoomWithDraw(...)`, composed of their unlocked variants (the `MintCreatureUnlocked` precedent). The pure
Core resolution is computed first from the reads below and handed in; the method re-checks inside its transaction that
the room has no stored `event_id` (else it returns the stored one and writes nothing). SQL stays in `FusionRpg.Data`
(guard-dal):

- build the room's `EventSeenSets` from `LoadPerDelveEventSeen` and `LoadPersistedEventSeen`
  (`RpgStore.Delve.cs:409`, `:463`);
- compute **`holdsOverrideStock` from the entering party's pack** — the one live fact the forced-outcome resolver
  still waits for (`EventDeck.cs:99`; party-dungeon D3.3/D3.5) — through the loot-pack read the pack UI already
  uses, never a guess;
- call `EventDeck.Resolve` (today; `DelveStoryletHost.Resolve` after the re-seam) on the room's named streams;
- write the drawn id and resolved kind/archetype with `MarkRoom` and each persisted scope with `RecordEventSeen` —
  at the draw, per `spec-event-deck.md` §8.

`delve-host` later swaps `Resolve` for `DelveStoryletHost.EnterRoom` (`spec-delve-host.md` §1) without changing this
route's signature.

### 3. The answer — `POST /api/delve/rooms/{id}/answer`

The file `spec-event-deck.md` names (`src/FusionRpg.Server/DelveEventEndpoints.cs`, `:344` there), body
`{playerId, delveId, partyEntityId, choice, correlationId}`:

1. refuse a non-steered party (the event-deck task's own Verify line: *"the answer endpoint refuses a non-steered
   party"*) and a room with no drawn event;
2. rebuild the resolution from `(seed, room, party state at entry, seen)` and assert it equals the stored
   `event_id` — the validate-on-load posture (`spec-event-deck.md` §8);
3. append the answer to `decisions_json` (`AppendDecision`, `RpgStore.Delve.cs:491`) **before** applying it;
4. `EventDeck.Answer(resolution, choice, party, …)` (`EventDeck.cs:339`) and apply its result to the party in the same
   transaction; a replayed `correlationId` returns the first result.

A widened storylet's answer is `delve-host`'s branch through `ChoiceAnswerService` (`spec-delve-host.md` §4); the
route is the same.

### 4. Text on the wire — players never see a blank event

`DelveEventDto` (new, `FusionRpg.Contracts`) — `{eventId, kind, choices[], banner?, warnings[], name, situation}`,
where `name` and `situation` are `NarrativeTextDto`s (`key` + token references, `spec-narrative-text.md` §2), rendered
by `narrative-text`. Audit 2026-09-19: this said `TextRefDto` "that `quest-log-contract` already defines" — a second
wire text shape; the program has one, `NarrativeTextDto`. The web adapter maps the DTO onto `EventView`, turning
today's `Pending` fields real.

**Legacy rows show clean, keyed text from day one — Owner ruling 2026-09-19 (round 4)** (replacing "a legacy row
carries no text / `Pending` until `delve-event-regen`"). Today's legacy `name`/`flavor` are unkeyed raw strings and 53
of 54 carry leaked Han characters (`narrative-seed-map.md` §3.4). narrative-seed's wave-0 `dungeon-generator-repair`
regenerates those legacy events clean (glossed motifs, the widened script check) — Owner ruling 2026-09-20: all 54,
the four `story` events included, with their ids and committed `chainRef`s kept — **and** gives their name and flavor
text keys — key and string authored together (`docs/architecture/item/seed-contract.md` §6). The keyed strings enter
lingui through `narrative-text`'s codegen bridge (`spec-narrative-text.md` §4 step 1), so a legacy row's `name` and
`situation` (its flavor) arrive as `NarrativeTextDto`s like a widened row's. Wave 6's `delve-event-regen` later
replaces the legacy rows with storylets. Order: `dungeon-generator-repair` (narrative-seed wave 0) and
`narrative-text` land before this module's text half ships; a row with no key is a load refusal naming the file,
never a blank or raw string on screen.

### 5. Per-room fight record — not here

`CloseDelve`'s quest verdicts need a `DelveReport` whose `Kills` slice has no persisted source (party-dungeon D4.14's
2026-09-08 note); that record, and the extraction and room-clear routes, stay party-dungeon's (see
`spec-delve-live-start.md` Contradictions 1).

## Data shapes

No new table or column: `rpg_delve_rooms.event_id`/`resolved_*`, the seen scopes and `decisions_json` exist
(party-dungeon D3.9's store layer). `DelveEventDto` is a wire record.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `revision` in `DelveUpdated` | `long` | the delve row's counter |
| seeds and streams | `ulong` / named streams | `SeededRng` as the deck already uses; never `System.Random` |

## SOLID notes

- **S:** routes and call sites only; the deck, the resolver and the store stay party-dungeon's code (then the one
  engine's, after the re-seam).
- **O:** `delve-host` adds the storylet branch behind the same routes.
- **L:** a legacy draw through the route equals `EventDeck.Resolve` byte for byte (the reseam's stream fixture).
- No second draw path, no second answer path, no second text path.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Server/DelveEventEndpoints.cs','src/FusionRpg.Contracts/Delve/DelveEventDto.cs','gk-web/web/fusion-rpg-web/src/contract/adapt.ts','tests/FusionRpg.Server.Tests/DelveEventEndpointsTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~DelveEventEndpoints"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Delve"
cd web\fusion-rpg-web; npm test -- delveViews
```

## Structure

```
src/FusionRpg.Server/DelveEventEndpoints.cs                  (new: /rooms/{id}/enter, /rooms/{id}/answer)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs                  (edited: EnterRoomWithDraw over unlocked variants; Audit 2026-09-19)
gk-core/src/FusionRpg.Server/Program.cs                              (edited: MapDelveEvents beside MapDelveWild)
src/FusionRpg.Contracts/Delve/DelveEventDto.cs               (new)
gk-web/web/fusion-rpg-web/src/contract/types.ts, adapt.ts           (edited: EventView from DelveEventDto; stale comment removed)
tests/FusionRpg.Server.Tests/DelveEventEndpointsTests.cs     (new; in-memory store, fixture delve)
gk-web/web/fusion-rpg-web/src/contract/delveViews.test.ts           (edited)
```

## Testing strategy

Game closed; in-memory store; a fixture delve built through `CreateDelve`.

- **Entry:** entering an event-capable room moves the party, marks it visited, draws once and writes `event_id` and
  the persisted scopes in one transaction; entering again returns the same id and writes nothing; a gated door
  refuses with `LaneGate`'s reason and writes nothing.
- **Seen at draw:** a wipe after the draw leaves the event seen (§8's rule), in both orders of "draw then wipe" and
  "wipe then re-enter".
- **Override fact:** a party carrying the room event's supply tag draws the forced outcome; one without it draws the
  ordinary one — the fact comes from the pack fixture.
- **Answer:** the answer is in `decisions_json` before its effects; a replay applies nothing twice; a non-steered
  party is refused (with the seam stubbed to return false); a rebuilt resolution that disagrees with the stored id
  refuses naming the room.
- **Text (Owner ruling 2026-09-19 (round 4)):** a widened fixture row's and a keyed legacy fixture row's
  `name`/`situation` both arrive as `NarrativeTextDto`s and render through the generated descriptors; an unkeyed legacy
  fixture row is refused at load naming the file; no raw seed string reaches the DTO and no field shows `Pending`.
- **One transaction:** a fault injected after `MarkRoom`'s write inside `EnterRoomWithDraw` leaves neither the move,
  the mark nor a seen row (in-memory store).
- **No population:** tests never count the committed event corpus.

## Success criteria

1. A party enters a room through a route. 2. The room's event is drawn once, recorded at the draw, with the real pack
fact. 3. A steered party answers through a route; the answer persists before it applies. 4. Event text reaches the
wire keyed, never raw, never blank — legacy rows included. 5. G5's prerequisites (`npc-story-events-map.md`, *Gates*)
are met.

### Live proof (Audit 2026-09-19: was missing)

After the full suite (AGENTS.md verification boundary, point 3), RPG Server scope only
(`docs/contributing/live-probe-standard.md`): on a delve created through `delve-live-start`'s real `/start`, enter an
event-capable room through `POST /api/delve/rooms/{id}/enter`, read the room back through `GET /api/delve/{id}` (the
normal query path, never the response body alone), answer through `/answer`, and read `decisions_json` back. No
`debug.*` command, no hand-inserted room or event row.

## Boundaries

- **Always:** call the built deck; write seen at the draw; persist the answer before applying it.
- **Ask first:** widening the steering seam.
- **Never (Owner ruling 2026-09-19 (round 4)):** show a blank or `Pending` event text, or an unkeyed legacy string.
- **Never:** resolve a battle here; build extraction or room-clear (party-dungeon's); put a raw seed string on the wire.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `POST /api/delve/rooms/{id}/enter` | `delve-stage` (FE); `delve-host` (swaps the draw for `EnterRoom`) |
| `POST /api/delve/rooms/{id}/answer` | `delve-stage`; `delve-host` (widened branch) |
| `DelveEventDto` | the web adapter (`EventView`); `storylet-card` |

## Transferred from party-dungeon (Owner ruling 2026-09-19 (round 3))

| party-dungeon task | What moves here | What stays with party-dungeon |
|---|---|---|
| **D3.9** (open) | the answer endpoint and the production callers of its store layer (`MarkRoom`'s `eventId`, `RecordEventSeen`) | the remaining preflight conjunct (*"non-event atom kind"*) |
| **D3.3** (open) | the live call site of `Resolve` with a real pack-sourced `holdsOverrideStock` | deck goldens per domain and the 256-seed sweep against real content |
| **D3.5** (open) | its integration clause (the event outcome's `Instantiator` call reached from a live draw) | nothing else — the resolver logic is built |
| — (no task) | the room-entry route calling `MoveParty`; the event DTO and `EventView` text | — |

## Contradictions found (report; not fixed here)

1. **`EventPanel.tsx`'s comment is stale** (*"`EventResolution`/`EventDeck` do not exist anywhere in `.cs` source"*,
   `gk-web/web/fusion-rpg-web/src/stages/delve/layers/EventPanel.tsx:10-17`; both exist, `EventDeck.cs:46`, `:218`). Map
   *Conflicts* item 3 gives the fix to `storylet-card`; the adapter half of the same stale claim in `types.ts`
   (`:1270-1275`) is fixed here because this module edits that type.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: the Delve (rooms, event deck, answer), web contract, live probe.
[x] Read this session: npc-story-events map; party-dungeon map; tasks/party-dungeon-todo.md D3.3, D3.5, D3.9, D4.14;
    spec-event-deck.md §8, §9, Structure, Boundaries; spec-delve-host.md; code: EventDeck.cs, RpgStore.Delve.cs
    (MoveParty, MarkRoom, seen readers, AppendDecision), DelveEndpoints.cs, DelveWildEndpoints.cs, types.ts EventView.
[x] Every claim cites file:line; no-caller claims re-checked by grep over src/.
[x] No population pinned. No cache. No actor number.
[x] No parallel path: one deck, one answer path, one text path (lingui through narrative-text).
[x] Order independence: draw vs wipe tested both ways; replays settle once.
[ ] Registry row: none. (Audit 2026-09-19: rows proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | Owner ruling 2026-09-19 (round 4): §4 planned legacy events with no text (`Pending` until `delve-event-regen`); players must never see a blank event | **Fixed:** repaired, keyed legacy text through the codegen bridge; dependency on `narrative-text` and the repaired corpus (map row 29 and build order updated) |
| 2 | medium | The wire text type was `TextRefDto` from `quest-log-contract`, a second text shape beside `narrative-text`'s `NarrativeTextDto` (SOLID S) | **Fixed here:** `NarrativeTextDto`. Propagation closed — Alignment 2026-09-20: `spec-quest-log-contract.md` and `spec-expedition-lead-host.md` use it too |
| 3 | medium | "In one store transaction" was not buildable: the three store methods each open their own connection | **Fixed:** one Data method over unlocked variants, with a fault-injection test |
| 4 | medium | No live-proof section although G5 is RPG Server scope | **Fixed:** real routes, read-back through the normal query path |
| 5 | low | Citations re-checked: route list (`DelveEndpoints.cs:35-57`, `DelveWildEndpoints.cs:62-67`), `ProductionIsPartySteered` returns `true` (`DelveWildEndpoints.cs:73`), `EventView` all-`Pending` (`gk-web/web/fusion-rpg-web/src/contract/types.ts:1276-1282`), `NotifyDelveUpdatedAsync` (`DelveEndpoints.cs:194`) — hold | no change |

**Propagation owed (outside this fence):** `narrative-seed/spec-dungeon-generator-repair.md` still says regenerating
the 54 committed events is out of scope; under round 4 it regenerates them clean and keyed.

**Proposed enforcement-registry rows:** `ns-no-blank-event-text` — every event DTO carries keyed `name`/`situation`;
guard `DelveEventEndpointsTests` (refusal of an unkeyed row) plus a web adapter test that `EventView` text is never
`Pending`. `ns-delve-one-answer-path` — one answer route for legacy and widened rows; guard: a Server route-table test
that `/api/delve/rooms/{id}/answer` is the only event-answer route. **Verification-boundary ask:** map
`src/FusionRpg.Server/DelveEventEndpoints.cs`, `src/FusionRpg.Contracts/Delve/**` and
`gk-web/web/fusion-rpg-web/src/contract/adapt.ts` to a delve boundary (web has none today).

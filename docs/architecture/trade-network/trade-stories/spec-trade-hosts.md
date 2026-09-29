# Spec: `trade-hosts`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 3, wave 2). Every `file:line` below was opened this session. Docs only.

## Objective

Give trade places the right to show a storylet: a trade hub, a depot, a trade lane carrying flow, and the
empire's trade as a whole. Each is a **host** on npc-story-events' one engine — it decides *when* to ask,
never *which* storylet or *what it pays* (npc-story-events-ideal §6.2).

## Locked anchors

- **Owner decision OD-3 (2026-09-19): narrative-seed owns the list of storylet host kinds.** The trade host
  kinds are rows in narrative-seed `storylet-vocab`'s registry `gk-data/packs/fusion/data/seed/narrative/_registry/host-kinds.v1.json`
  ([spec-storylet-vocab.md](../../narrative-seed/spec-storylet-vocab.md) §3.1); the runtime reads that one
  file. This closes the map's contradiction 1. (npc-story-events' `spec-narrative-vocabulary.md` §2 says
  the runtime defines the members; that line is owed a correction by its owner — propagation filed, not
  edited here.)
- **One engine, the host seam.** Trade hosts implement `IStoryletHost` (host kind, clock, stream root,
  kind fit — [spec-storylet-reseam.md](../../npc-story-events/spec-storylet-reseam.md) §2). No trade deck.
- **One place, one host.** A place is never asked twice per pulse (map contradiction 3; Design 3).
- **Streams are named per host kind** and never shared with a combat stream (`WorldSeed.DeriveRollSeed`,
  `gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24`).
- **World clock only:** every trade host's clock is `world.turn`.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The `Events` phase, where world hosts are asked | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:341-366` |
| The `Market` slot kind | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:18` |
| Lane fields a lane host can key on | `gk-core/src/FusionRpg.Core/World/WorldState.cs:256-260` |
| The event engine to host (Delve-only today) | `gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:252`; `EventFilters.cs:76` |

### Wiring gap

| What | Where | Closed by |
|---|---|---|
| `WorldEntityKind.Caravan` exists and is never constructed; caravans are legions on a standing order | `gk-core/src/FusionRpg.Core/World/WorldState.cs:66` | `legion-build` `caravan-kind-retire`; hosts key on the standing order, never on that kind |

### Real gap

No trade host kind in any registry; no host adapter; the engine's re-seam and `world-events-host` are
specced, unbuilt.

## Design

### 1. The host kinds (rows requested on `storylet-vocab`)

| Host kind (registry id) | Place | Asks, in the `Events` phase, for | `Θ_content` input (npc `host-content-theta`) |
|---|---|---|---|
| `world.trade-hub` | a sector whose `SectorFeatures.TierOf(sector, trade) ≥ 1` — any tier of the Trade building, Trading Post to Grand Exchange (round 4; a structure row, not the `Market` slot itself) | the hub's owner, and factions whose `LevelAt` that hub is `market` or better (`exchange` `trade-access` §2a: tier **and** treaty/band) | the sector's `DangerBand` |
| `world.depot` | a sector whose `SectorFeatures.TierOf(sector, caravans) ≥ 1` — the caravan building at either tier (Caravan Yard, Convoy Depot; round 4 — was "an active `convoy-depot`") | the owner only | the sector's `DangerBand` |
| `world.trade-lane` | a lane that carried flow this turn | each faction with flow on it | the higher endpoint `DangerBand` |
| `world.trade-turn` | the empire's trade as a whole | one pulse per empire per turn | the empire's highest held `DangerBand` |

Ids follow the registry's `place.kind` grammar (`world.market`, `world.shrine`, …); the map's short names
(`trade-hub`, `depot`, `trade-lane`, `trade-turn`) are these rows. Recommended `admits` (storylet kinds):
hub `bargain`, `story`; depot `story`; lane `story`, `encounter-event`; turn `story`. The row values are
narrative-seed's call; the recommendation rides the ask.

### 2. Host adapters

```csharp
// src/FusionRpg.Core/World/Trade/Stories/TradeStoryletHosts.cs (new)
public sealed class TradeHubHost   : IStoryletHost { HostKind => "world.trade-hub";  Clock => HostClockKind.WorldTurn; ... }
public sealed class DepotHost      : IStoryletHost { HostKind => "world.depot";      ... }
public sealed class TradeLaneHost  : IStoryletHost { HostKind => "world.trade-lane"; ... }
public sealed class TradeTurnHost  : IStoryletHost { HostKind => "world.trade-turn"; ... }
// StreamRoot(slotKey) = "event:" + HostKind + ":" + slotKey  (WorldSeed stream per host kind)
```

Each adapter builds a `StoryletDrawContext` for its eligible places, fog-correct (a foreign hub is asked
only for factions with access), and calls the one engine through the call site `world-events-host` adds to
the `Events` phase. Adapters reference no selection or reward type.

### 3. One place, one host

~~A sector whose `Market` slot holds an active `exchange`-role structure is hosted by `world.trade-hub`, and
`world-events-host` skips `world.market` for it (ask filed on npc-story-events `world-events-host`). A
`Market` slot without a hub stays `world.market`.~~ **Superseded by round 5 (2026-09-20).** Round 5 B1 lets
the Trading Post stand on a `Wildland` **or** a `Market` slot, so a sector can hold a hub on its Wildland
while its Market slot stays empty — under the old rule that one place got two hosts. The rule is now keyed
by the feature, never a slot or a role (round 5 X1): **a sector whose `SectorFeatures.TierOf(sector, trade)
≥ 1` is hosted by `world.trade-hub`, and `world-events-host` skips `world.market` for it, whichever slot the
hub stands on** (ask filed on npc-story-events `world-events-host`). A sector with a `Market` slot and no
hub stays `world.market`. A lane host and a sector host are different places.

### 4. Frequency

How often these hosts fire is `trade-story-pacing`'s (per-host firing rows, cooldowns, and the per-empire
budget in the one selection engine, OD-5). This module declares no rate.

## Contract exposed

Four host kind ids; four `IStoryletHost` adapters. Consumers: npc `world-events-host` (call site),
`storylet-selection`, `trade-story-pacing`, `trade-storylet-supply` (coverage cells).

## Acceptance (contract level)

1. **When, never which:** a static guard finds no reference from a trade host adapter to a selection,
   weight, outcome or reward type.
2. **Fog:** a foreign hub never asks for a faction whose `LevelAt` it is below `market` (fixture per access
   level, and one where only the faction's missing Trading Post keeps it below — round 4).
3. **One place, one host:** a Market-slot sector with an active hub produces exactly one ask per pulse —
   with the hub on the Market slot **and** with the hub on a Wildland slot beside an empty Market slot
   (round 5 B1).
4. **Streams:** every adapter's stream root starts `event:world.trade-`/`event:world.depot`, and no stream
   name equals a combat stream (a scan over stream names).
5. **Registry join:** every adapter's `HostKind` is a row in `host-kinds.v1.json`, and every trade row has an
   adapter.
6. **Clock:** every trade host's clock is `WorldTurn`.

## Test plan and verification boundary

Core adapter tests (fog, one-host, streams, registry join) — `core-fallback`. The registry file's own
tests are narrative-seed's (seedsmith).

## Hard edges

- Blocked on narrative-seed `storylet-vocab` accepting the rows, npc `storylet-reseam` (the seam),
  `world-events-host` (the call site), `host-content-theta`.
- The one-host rule edits `world-events-host`'s eligibility; filed as an ask, never worked around.

## Dependencies

`trade-fact-kinds`; narrative-seed `storylet-vocab`; npc-story-events `storylet-reseam`, `world-events-host`,
`host-content-theta`, `storylet-selection`; `exchange` `exchange-hub`, `trade-access`; `fleet` `depot`;
`logistics-flow` `lane-flow`.

## Boundaries

- **Always:** registry rows on narrative-seed; `world.turn` clock; one host per place.
- **Ask first:** a host that is not a place (a per-good host).
- **Never:** a trade deck; an adapter that picks or pays; a host keyed on `WorldEntityKind.Caravan`.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: storylet engine seam, host-kind registry (narrative-seed), world Events phase.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: npc-story-events-ideal §6.2/§6.6, spec-storylet-reseam §2, spec-narrative-vocabulary §2,
    spec-storylet-vocab §3.1, narrative-seed-ideal §6.1–§6.2, spec-host-content-theta (world rows).
[x] decisions.md: no lock on host kinds.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: Events phase, SlotKind.Market, lane fields, Caravan kind, WorldSeed stream.
[x] Surrounding sections read (registry ownership note in spec-storylet-vocab).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: OD-3 in the map; npc spec-narrative-vocabulary §2 correction filed as owed.
[x] No population pinned: four host kinds are declarations.
[x] No cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path: one engine, one registry file.
[ ] Registry row: "a host adapter references no selection/reward type" needs a guard row when built.
[x] Round 4 reconciliation (2026-09-19, [decisions-round-4.md](../decisions-round-4.md)): hosts attach by sector feature
    (`trade-foundation` `sector-features` `trade`, `caravans`), not by a row id or role; hub fog reads LevelAt.
[x] Round 5 (2026-09-20): §3 re-keyed on TierOf(trade) (X1) because B1 lets a hub stand on Wildland
    beside an empty Market slot; acceptance 3 covers both placements.
```

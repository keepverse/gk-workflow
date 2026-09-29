# Spec: petition-host

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `petition-host`, row 19 of the [npc-story-events map](../npc-story-events-map.md) (`:224`), wave 4. Depends on
`world-events-host` (the phase, the command and the settle pass it runs in), on `world-claim-loot` (Owner ruling
2026-09-20 (round 5), R17: the claim loot lines a petition quest's reward takes are minted there,
`spec-world-claim-loot.md`) and, for clan requests only, on clan
policy and real needs (external: world-map-program `ai-commander`, trade-network `counterparties`; map `:186`).
Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Give held sectors a voice. On a held sector's turn, a **resident** asks for what the sector needs, and — once clans
have policies and real needs — a **clan** makes a request **computed from world state**, never authored per clan
(`world-graph-ideal.md` §8.2). A petition is a storylet on the `world.petition` host: it fires through the one engine,
is answered with `event.choose`, and surfaces through world-stage's inspector and notify rail as a filed ask.

Success looks like: with the game closed, a fixture held sector whose loam component is about to be released fires a
resident petition naming that need; answering it offers a world quest whose objective is the need itself; no petition
fires on a sector the player does not hold; clan requests fire only when a clan's need vector is not flat.

## Locked anchors

- **Petitions** (ideal §6.6 World stage row, `npc-story-events-ideal.md`): *"a resident asks for something the
  sector needs. A clan's request is computed from world state, never authored per clan"*; `world-graph-ideal.md` §8.2
  (`docs/architecture/world-graph-ideal.md:400`): *"a clan's price is its personality"*.
- **Resource binding** (ideal §6.10, `:512-516`): *"[creature] asks for [supply] in [sector]"*, filled at runtime.
- **Clans have no policy and needs are flat today**: `FactionPolicies.ById` registers `StandFastPolicy` and
  `FrontierRulesPolicy` only (`gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18`); `UniformNeeds` returns neutral
  1000 for every slot kind and element (`gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:24-40`) — *"What is missing is the
  numbers, not the idea"* (`:29`).
- **Loam is never traded or converted — only moved** (`docs/architecture/empire-resource-ssot.md` §4 rule 4). A
  petition therefore never asks the player to *pay* loam.
- **No new stock; relations grant access** (map principles 8, 9).
- **Surfaces are world-stage's** (`docs/architecture/world-stage-map.md:76-82`: `world-inspector`, `world-notify`,
  `world-playback`); the rail flushes non-blocking items at End Turn
  (`gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts:16-25`).

## Design

### 1. A petition is a storylet whose ask is a need

A petition storylet declares host `world.petition` (`spec-narrative-vocabulary.md` §2). Its typical shape (enforced
by preflight, §4): a `quest.offer` choice whose quest objective **is** the need, an `offer:souls` choice where the
need can be bought off, and `leave`. Answering well is a relation fact with the resident or the clan; the reward for
meeting the need is the quest's reward, one window-roll of the sector's own loot **table** (`spec-quest-sources.md` §6).
~~Nothing a petition does is a new faucet.~~ Audit 2026-09-19: that roll is in addition to the sector's claim roll, so
it **is** a bounded faucet. **Owner ruling 2026-09-20 — superseded:** rewards come out of the host budget. The
petition's budget line is the world's claim loot lines (`world-sector`, `spec-outcome-routing.md` §3): a completed
petition quest's roll **takes** one claim line of the settling End Turn in that world (minted under that line's
correlation, with the quest's window), waiting as `reward.owed` when the turn has none. Nothing is added, so a
petition is not a faucet. A petition's `offer:souls` choice is a sink.

### 2. Needs, computed from world state

`SectorNeeds.For(WorldState world, string sectorId, string factionId)` (new, Core, pure) returns zero or more needs
from a **closed** vocabulary, each a reading of shipped world state:

| Need kind | Holds when | Read from | Met by (quest objective) |
|---|---|---|---|
| `loam-fading` | the sector's supply component would be released at the next pressure pass | `LoamForecast.WillRelease` (`gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:72`) | `hold-sector` on that sector for `need` turns (`spec-quest-sources.md` §3): the player keeps it — by moving loam (`sustain`) or building a source, the player's choice |
| `hazard-standing` | the sector has a `Hazard` slot (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:21-22`) | `WorldSlot.SlotTypeId` | `develop-sector` on that sector (`spec-quest-sources.md` §3), met by the `develop.completed` report entry (`gk-core/src/FusionRpg.Core/World/Growth/GrowthPhases.cs:132`) |
| `undeveloped` | `WorldSector.DevelopmentLevel` is below the world's median held development | `gk-core/src/FusionRpg.Core/World/WorldState.cs:164` | the same `develop-sector` objective |

Each need is a fact about the sector **now**; none is authored, none is stored. Audit 2026-09-19 — **"now" is the
phase's world, not the pre-step input.** `world-events-host` builds its story input from the ledger *before*
`TurnEngine.Step`, but a sector can change hands, fade or finish a development project during the same turn's
Movement, Growth and Pressure phases. So `SectorNeeds.For` and the ownership test run **inside the `Events` phase** on
the world `RunEvents` receives (post-`Pressure`); the input carries only the eligible petition storylets per need
kind. A petition therefore never fires on a sector lost this turn, or about a need this turn already met. The need kind reaches the storylet as
a host-supplied predicate input (`sector.need = <kind>`, a leaf filed on `narrative-predicates`) and as the `{supply}`
binding (the need's display id), so one petition template covers every sector with that need (Kreminski's resource
binding).

**Clan requests** use the same machinery with a clan's `INeedVector`: the ask is the slot kind (or element) with the
**strictly highest** need above neutral (`INeedVector.ForSlotKind`, `ForElement`, `INeedVector.cs:15-22`). With
`UniformNeeds` every value is neutral, so **no clan request fires** — correct behaviour, not a special case, and the
request starts firing the day world-map/trade-network give needs numbers. A clan request's objective is
`hold-sector-kind` for that slot kind or a `story-fact` on the clan's market (trade-network's exchange, map `:321`);
this module does not build the exchange.

### 3. Firing

Petitions ride `world-events-host`'s phase (`spec-world-events-host.md` §3) as a second candidate class:

- **Candidate**: a sector the player faction owns, with at least one need, and a petition storylet eligible for it.
  Held sectors are always visible, so fog is satisfied by ownership.
- **Fire**: `firing.world.petition` (`50/5`, `spec-narrative-vocabulary.md` §4) with pity counted per sector on the
  world-turn clock; at most one petition per sector per turn and — a pacing bound, structural — at most
  `SelectionBounds.PetitionsPerTurn = 1` across the empire, so petitions read as a resident's voice, not a to-do list.
  (The const joins `SelectionBounds` in this module's change, with a comment naming the reason.)
- **Who asks**: the resident cast at a host slot of that sector (`spec-cast-resolver.md` §1) when one exists; else the
  role `wanderer` is cast from the save's present characters; a clan request's speaker is the clan's elder character
  when clans are cast (`spec-cast-resolver.md` §1 last paragraph).
- **Report and answer**: `story.offered` / `event.choose` / `story.answered` exactly as world storylets; host kind
  `world.petition`, so the playback row reads "a petition" rather than an incident.

### 4. Preflight rules added with this module

| Rule id | Refuses |
|---|---|
| `petition.no-need-condition` | a `world.petition` storylet whose eligibility names no `sector.need` leaf (a petition must be about a need) |
| `petition.pays-loam` | any `offer:loam` choice (loam is only moved, never paid) |
| `petition.no-resolution-path` | a petition with no `quest.offer` choice and no `offer:{stock}` choice (the player could only refuse) |

### 5. Surfaces (filed asks on world-stage)

| Surface | Ask |
|---|---|
| `world-inspector` | a "Petition" block on a held sector with an open petition offer: the asker, the need, and the storylet card action (`storylet-card`, wave 6) |
| `world-notify` | one **non-blocking** rail item per new petition, category `petition`; it flushes at End Turn like every other non-blocking item (`gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts:16-25`), while the offer itself stays open until it lapses (`world.offerLifetimeTurns`) |
| `world-playback` | the `story.offered` row renders "a petition from {asker} at {place}" when the host kind is `world.petition` |

Player-routed push beyond the rail is notification-ssot's (map `:187`).

### 6. Budget and Θ

`WorldHostBudget` for the petitioning sector (`spec-world-events-host.md` §6); `HostContentTheta.ForSector` for its Θ.
A petition's `offer:souls` choice is a soul **sink** priced through `OfferPricing.Souls` (`spec-choice-resolution.md`
§5). Meeting a need rewards through the offered quest's window roll, taken out of the world's claim loot lines
(Owner ruling 2026-09-20; `spec-outcome-routing.md` §3), never added.

## Data shapes

- No table, no new stock. Needs are computed; petitions are storylets; quests and relations are ledger facts.
- Registry: `sector.need` members `loam-fading, hazard-standing, undeveloped` — a closed runtime vocabulary declared in
  `SectorNeedKinds` (C#) and mirrored into `conditions.v1.json` (new) through narrative-seed's `storylet-vocab` so seeds can
  name them (filed).
- Tuning: none new (`firing.world.petition` exists in `spec-narrative-vocabulary.md` §4).

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| need values (clan) | `int` per-mille | `INeedVector`'s own type (`INeedVector.cs:18,21`) |
| development median | `int` | `DevelopmentLevel` is `int` (`WorldState.cs:164`) |
| stock readings | `long` | `LoamStock` and siblings are `long` (`WorldState.cs:173-187`) |

## SOLID notes

- **S:** `SectorNeeds` reads state; the engine selects; `world-events-host` fires and settles.
- **O:** a new need kind is a vocabulary member and one reader arm; clans plug in by giving `INeedVector` numbers.
- **D:** depends on `INeedVector` and `LoamForecast`, never on a clan's authored data.
- No per-clan script, no second firing pass, no second command.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Hosts/SectorNeeds.cs','src/FusionRpg.Core/Narrative/Hosts/WorldStoryPhase.cs','tests/FusionRpg.Core.Tests/Narrative/Hosts/PetitionTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Hosts|FullyQualifiedName~World.Loam"
```

## Structure

```
src/FusionRpg.Core/Narrative/Hosts/SectorNeeds.cs          (new: closed need kinds, pure readers)
src/FusionRpg.Core/Narrative/Hosts/WorldStoryPhase.cs      (edited: petition candidates)
gk-core/src/FusionRpg.Core/Narrative/Vocabulary/SelectionBounds.cs (edited: PetitionsPerTurn)
src/FusionRpg.Core/Narrative/Storylets/EventDeckPreflight.cs (edited: §4 rules)
tests/FusionRpg.Core.Tests/Narrative/Hosts/PetitionTests.cs      (new)
tests/FusionRpg.Core.Tests/Narrative/Hosts/SectorNeedsTests.cs   (new)
```

## Testing strategy

Game closed; fixture worlds.

- **Needs are readings:** a fixture sector with a releasing component reads `loam-fading`; after a `sustain` that saves
  it, the need is gone. A sector with a `Hazard` slot reads `hazard-standing`; after `develop.completed` clears it, gone.
- **Held only:** a need on an unheld sector never produces a petition candidate.
- **Same-turn change (Audit 2026-09-19):** a fixture sector held at turn start and lost in this turn's `Pressure`
  produces no petition; a `hazard-standing` need cleared by this turn's `develop.completed` produces none.
- **Flat needs, no clan request:** with `UniformNeeds` no clan request fires on any seed; with a fixture need vector
  whose `Market` need is highest, a clan request fires binding `Market`.
- **Pacing:** at most one petition fires per turn across the empire; the pity count is per sector.
- **Preflight:** each §4 rule has a red fixture.
- **Quest from need:** answering a `loam-fading` petition's quest choice offers a quest whose objective targets that
  sector, completing when the sector is still held after N turns (end to end through `world-events-host`'s settle).
- **No payment in loam:** no plan produced by a petition contains a loam debit.
- **No population:** fixtures only.

## Success criteria

1. Held sectors produce petitions from computed needs through the one engine. 2. Clan requests are computed from
`INeedVector` and fire only when needs are real. 3. No petition asks for loam as payment; no new stock, and no faucet: the quest reward roll is taken out of the
world's claim loot lines (Owner ruling 2026-09-20).
4. Surfaces are filed on world-stage, not built here.

## Boundaries

- **Always:** compute needs from state; fire through `world-events-host`; answer with `event.choose`.
- **Ask first:** a new need kind that reads a stock this program does not own; a blocking rail item.
- **Never:** author a request per clan; build the clan exchange (trade-network's); give needs numbers here
  (world-map/trade-network's); ask for loam as payment.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `SectorNeeds.For` | `world-events-host` (petition candidates), `narrative-predicates` (`sector.need` leaf, filed) |
| petition offers (host kind `world.petition`) | world-stage `world-inspector`, `world-notify`, `world-playback` (filed asks) |

## Contradictions found (report; not fixed here)

1. **Clan requests are unreachable until needs are real.** Map row 19 (`:224`) lists clan requests as this module's; the
   input they are computed from is flat (`INeedVector.cs:31`) and clans have no policy (`FactionPolicies.cs:13-18`). The
   map already records this as a dependency (`:186`); stated here so no session reads an empty clan-request test as a
   defect.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: world map (reader of loam, slots, development), world AI needs (reader), economy (no faucet: the quest reward is taken out of the claim loot lines — Owner ruling 2026-09-20), world
    stage surfaces (filed asks), quests.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map rows 18-19, :186; ideal §6.6, §6.10; world-graph-ideal §8.2 heading; DESIGN-GATE §1 World map,
    Economy, UI rows; empire-resource-ssot §4; code: INeedVector, FactionPolicies, LoamForecast, SlotTypeCatalog,
    WorldState sector fields, GrowthPhases, notifyRailStore.
[x] Every claim cites file:line.
[x] No population pinned; need kinds are a declared closed vocabulary.
[x] No cache.
[x] Actor numbers: none.
[x] No parallel path: petitions are storylets in the same phase and pass.
[ ] Registry row: none new.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (World map, Economy, UI rows), §2 (1, 2, 9, 12, 15), §3, §5;
`economy-principles.md` P1, P2, P5 (loam never converted); `empire-resource-ssot.md` §4 rule 4; round-3/round-4 rulings.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | HIGH | **"Nothing a petition does is a new faucet" was false.** The quest reward is an extra roll of the sector's table on top of its claim roll | **Fixed in text** (§1). **Resolved — Owner ruling 2026-09-20:** the reward is taken out of the claim loot lines (§1, §6) |
| 2 | MEDIUM | Needs and ownership were read from the pre-step story input, so a petition could fire on a sector lost, faded or developed earlier in the same turn | **Fixed** (§2): evaluated in the `Events` phase on the post-`Pressure` world; test |
| 3 | LOW | `LoamForecast.WillRelease` cited at `:76`; it is declared at `:72` | **Fixed** |

Checked and holding: petitions are storylets in the one engine and one phase; clan requests computed from
`INeedVector` (flat today, correctly silent); no loam payment (`petition.pays-loam`); surfaces filed on world-stage;
dormant worlds fire nothing (the story phase runs only in a full step, `spec-world-events-host.md` §4, round 4).

**Registry row proposed** (shared file, not written): `ns-petition-no-loam-payment` → `EventDeckPreflightTests`
(`petition.pays-loam`), mirroring `empire-resource-ssot.md` §4 rule 4 for narrative content.

## Cross-lane alignment (2026-09-20)

Owner ruling 2026-09-20 (rewards come out of the host budget): the petition's budget line is the world's claim loot
lines (`world-sector`); its quest reward takes one, never adds one (`spec-outcome-routing.md` §3). The P14 key stays
the quest's own (`quest:{questSubject}`). Audit finding 1's deferred economy decision is closed.

- Alignment 2026-09-20: `world.petition` is a seed-side host row (`narrative-seed/spec-storylet-vocab.md` §3.1,
  admits `story`, `bargain`; ~~climate-neutral~~), so the petition shape of §1 (`pattern.persuade-leave-offer`) is
  plannable. Owner ruling 2026-09-20 (round 5): R19 — `world.petition` carries the held sector's climate ~~derived from
  its sector type (`narrative-seed/spec-storylet-vocab.md` §3.9)~~ (Owner ruling 2026-09-20 (round 6), R20: the held sector's own
  `WorldSector.Climate`, `gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`); the phase passes it into selection as
  `spec-world-events-host.md` §3 "Climate" does.
- Owner ruling 2026-09-20 (round 5): R17 — the claim loot lines of §1 and §6 are minted by `world-claim-loot`, which
  lands before this module.

# Spec: world-events-host

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `world-events-host`, row 18 of the [npc-story-events map](../npc-story-events-map.md) (`:223`), wave 4.
Depends on `outcome-routing`, `host-content-theta`, `cast-resolver` and — Owner ruling 2026-09-20 (round 5), R17 —
`world-claim-loot` (the world's budget line); Owner ruling 2026-09-20 (round 6), R21 — `world-anomaly-sites` (so the
`world.anomaly` host exists on a real map, `spec-world-anomaly-sites.md`). **Reviewed with world-map-program**, which
owns the turn engine, its phase order and `RulesetVersion` (map ownership table, `:317-318`). Draft decision row
**NS8** (`npc-story-events-map.md:405`). Gate **G4** (`:299`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Give the world map's turn its incidents, without a second turn loop:

1. **Fire** storylets per sector holding a host slot (`Shrine`, `Anomaly`, `Tear`, `Vault`, `Market`, `Wildland`), in
   the `Events` phase, **fog-correct**, with a quiet share of turns;
2. report them with a **typed event vocabulary** added to `TurnReportKinds`, each kind with a playback translation
   row filed on world-stage's `world-playback`;
3. let the player answer with the world command **`event.choose`**, admitted through `WorldCommandAdmission.Admit`
   and resolved at End Turn — deterministic and replayable like every order;
4. give world-graph's roaming **warlords** names, as characters bound by the anti-Nemesis rules.

Success looks like (G4): with the game closed, a fixture world fires a storylet at a visible `Market` sector in the
`Events` phase; an `event.choose` filed next turn resolves at End Turn and its outcome lands in the story ledger;
world goldens are byte-identical when no world storylet is eligible; a replay of a turn with content reproduces the
same report and state hash.

## Locked anchors

- **The `Events` phase rolls the calendar only today**: *"Calendar boundaries are rolled and reported; their effects
  belong to later modules."* (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:352-365`). It runs after `Pressure` and
  before `Snapshot`/`Observe` (`TurnEngine.cs:190-207`).
- **Phase order and `RulesetVersion` are world-map-program's** (`TurnEngine.cs:124`; map `:185`, `:317`). The version
  history states the bump rule: a bump when *"the same command log produces"* a different outcome; a brand-new command
  kind that no existing log contains needs none (`TurnEngine.cs:96-124`).
- **Commands**: `WorldCommandKinds` is the contract *"between the store, the wire, and the engine"*
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:3-7`, list at `:122-126`); payloads are typed fields, not a JSON blob
  (`:130-137`); admission is *"the cheap gate at submit time"*, legality is re-checked at reveal
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:3-17`).
- **The report is the log** (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:33-36`); entries are fog-scoped by
  `SectorId` and `Audience` (`:12-31`); five kinds today (`:3-10`).
- **Post-Step passes in the commit transaction** are the shipped precedent for Data-side work a turn triggers: the relic
  spend, the cargo pass and retrieval missions run *"in this same tx … before the log insert (outcome entries land in
  the stored report)"* (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601-627`).
- **Fights** go through `BattleRequest` (`gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:39-83`) and the `IBattleResolver`
  the turn holds (`TurnEngine.cs:157-163`).
- **R13 rules 1–6** bind warlords (map principle 17, `:127-130`; ideal §6.12, `npc-story-events-ideal.md`).
- **Surfaces are world-stage's**: playback, inspector, notify rail (map `:319`; `docs/architecture/world-stage-map.md:76-82`).

## Design

### 1. Where each half runs

The turn engine is pure over `(WorldState, commands, seed)`; the story ledger lives in `FusionRpg.Data`. So the host
splits in three, and only the middle runs inside `TurnEngine.Step`:

| Half | Runs | Does |
|---|---|---|
| **Input** | Data, inside `CommitWorldTurn`'s lock, before `Step` | builds `WorldStoryInput` from the ledger: per candidate sector the eligible storylets (already filtered by predicates, cast, cooldowns and tier by `storylet-selection`), the pity count, and every **open offer** with its precomputed choice views (`ChoiceResolver.Present`, `spec-choice-resolution.md` §5) |
| **Phase** | Core, in the `Events` phase, through a seam the engine calls | resolves admitted `event.choose` orders (roll + fight), then fires new offers; writes typed report entries |
| **Settle** | Data, post-Step, same transaction, before the log insert (the cargo precedent) | turns story report entries into ledger facts, executes outcome plans (`OutcomeExecutor`), captures and settles quests, notifies |

```csharp
namespace FusionRpg.Core.World.Turn;

/// The seam TurnEngine.Step takes, like IBattleResolver: a parameter, never a container registration.
/// Null (the default) is today's behaviour exactly.
public interface IWorldStoryHost
{
    void RunEvents(WorldState world, IReadOnlyList<WorldCommand> revealed, TurnReport report,
                   int turn, ulong seed, IBattleResolver battles);
}
```

`TurnEngine.Step` gains an optional `IWorldStoryHost? story = null` parameter; `Events(...)` gains the revealed
commands and the resolver and calls `story?.RunEvents(...)` **after** the calendar roll. The implementation,
`WorldStoryPhase` (new, `Core/Narrative/Hosts/`), holds the `WorldStoryInput` it was constructed with. This is the
only edit inside `TurnEngine.cs`, and it is world-map-program's to review.

### 2. Replay: the input is persisted

A replay re-steps a turn from its command log (`RpgStore.WorldTurns.cs:766-773`). The story phase reads an input the
command log does not contain, so the input is part of the turn's durable record: `rpg_world_turn_log` gains
`story_input_json` (canonical JSON, nullable), written in the same insert as `report_json`. Replay passes it back to
`WorldStoryPhase`; a turn with `NULL` replays with `story = null`, which is every turn committed before this module.
The column is a world-map-program schema change reviewed with it (Contradictions 1). The input is never trimmed with
the report hot tail (`ReportHotTail`, `RpgStore.WorldTurns.cs:476`), because a replay without it diverges.

### 3. Firing (the `Events` phase, Core)

For each **candidate sector** in `WorldStoryInput`, in ordinal sector-id order:

1. **Candidate** = a sector holding at least one host slot kind whose storylet pool is non-empty, and that the player
   can see: the player faction owns it, or its intel saw it last turn (`IntelSnapshot.LastSeenTurn == turn − 1`, the
   `Watched` rung carried into this turn — `IntelLadder.StateOf`, `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:167-174`).
   A sector the player cannot see never fires: an offer is itself information.
2. **Fire roll**: `p = min(1000, base + n × step)` per-mille (`firing.world.{slot}` tuning,
   `spec-narrative-vocabulary.md` §4; `n` = turns since this sector last fired, from the input). The `min` is a
   probability bound, a bounded ratio, and says so in a comment. Roll `WorldSeed.DeriveRollSeed((long)seed,
   "narrative:world:fire", sectorId)` (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24-30`), reinterpreted as
   `ulong` **before** `% 1000` (Audit 2026-09-19: `DeriveRollSeed` returns `unchecked((long)NextULong())`, so half its
   values are negative, and C#'s `%` on a negative `long` yields a negative remainder that is always "under" the fire
   threshold — a silent fire-rate bias).
3. **Pick**: the input already carries the tiered, weighted candidates; the phase takes the top tier present and
   draws through `WeightedChoice.Pick` on `"narrative:world:pick"`, target `sectorId` — the same draw
   `storylet-selection` performs for every host, handed a world stream.
4. **At most one offer per sector per turn**, and **one spine beat per turn across the world**
   (`SelectionBounds.SpineBeatsPerPulse`, `spec-narrative-vocabulary.md` §4): a structural pacing bound.
5. **Report**: `story.offered`, `Subject = offerRef` (`offer:{hostKind}:{sectorId}:{slotIndex}:{turn}`),
   `Detail = storyletId@revision`, `SectorId = sectorId`, `Audience = playerFactionId`.

The quiet share (ideal §7, *"~750 quiet"*) is a reading of the fire curve, not a separate key.

**Climate (Owner ruling 2026-09-20 (round 5): R19; Owner ruling 2026-09-20 (round 6): R20).** ~~When the Input half asks `storylet-selection` for a candidate
sector's tiers, it passes `SelectionRequest.Climate = SectorClimateCatalog.For(sector.TypeId)` — the site climate
**derived from the sector's type** through narrative-seed's closed registry `sector-climates.v1.json` …~~ Owner ruling 2026-09-20 (round 6):
**R20 — the sector's own climate.** When the Input half asks `storylet-selection` for a candidate sector's tiers, it
passes `SelectionRequest.Climate = sector.Climate?.ToString()` — `WorldSector.Climate`
(`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`), the same per-sector era climate the world already reads for wild
spawns (`gk-core/src/FusionRpg.Core/World/Loam/WildSpawnRoller.cs:77`), raised species
(`gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:136`) and ley-lane cost (`gk-core/src/FusionRpg.Core/World/Ai/MarchGraph.cs:44-45`);
`null` (the homeworld) is climate-blind. One source of truth: no narrative registry maps sectors or sector types to a
climate. The value is read from the committed world the input is built from, so it is deterministic and replayable
like the rest of the input (§2). The weight is the one `EventDraw.WeightMilliFor` match/none/off rule every host uses
(`spec-storylet-selection.md` §5). Petitions pass their held sector's own climate the same way.

### 4. `event.choose` — a world command

| Piece | Change |
|---|---|
| `WorldCommandKinds.EventChoose = "event.choose"` | appended to `All` (`WorldCommand.cs:122-126`) |
| `WorldCommand.OfferRef` (`string?`), `WorldCommand.ChoiceSlot` (`int?`) | two typed payload fields, the file's own rule |
| Admission (`WorldCommandAdmission.Admit`) | `SectorId` required and known; `OfferRef` non-empty, at most `MaxCommandIdLength` × 2 characters; `ChoiceSlot` in `0..3` (`SelectionBounds.MaxChoices − 1`); no `EntityId` required. Refusal ids `offer.missing`, `offer.too-long`, `choice.slot-out-of-range` |
| Legality at reveal (the phase) | the offer is open in the input and addressed to the commander, and the chosen slot was eligible in its precomputed `ChoiceView`; otherwise the order is dropped with `story.offer-closed` / `story.choice-ineligible` into the report — one stale order never aborts a turn (`WorldCommandAdmission.cs:7-10`) |

**Resolution at End Turn** (the phase, before firing new offers): for each legal `event.choose` in revealed order —
roll the choice with the precomputed odds through `ChoiceResolver.ResolveFromViews` (`spec-choice-resolution.md` §7:
one resolver arithmetic, never a second roll here) on a stream rooted in `WorldSeed.DeriveRollSeed((long)seed, "narrative:world:choice", offerRef)`;
a `fight` becomes a `BattleRequest { Kind = BattleKinds.Guard, LocationId = sectorId, SlotIndex, AttackerEntityId }`
(`BattleSeam.cs:15`, `:39-65`) resolved by the turn's `IBattleResolver`; report `story.answered` with
`Detail = "slot:{n}:{ordinal}"` (and the battle id when a fight ran). Nothing else in the phase touches `WorldState`:
facts, quests, loot and relations are the Settle half's. **Audit 2026-09-19 — the one exception:** a consequence that
changes hashed world state is applied here, because the Settle half runs outside the hash — today only
`counter-doctrine`'s `doctrine.setback` and study step (`spec-counter-doctrine.md` §2, §5), both on the antagonist's
`WorldFaction` record. Any further in-phase consequence is a reviewed addition with world-map-program.

**Dormant worlds** (Owner ruling 2026-09-19 (round 4)). The story phase runs only inside a full `TurnEngine.Step`.
A hibernating or idle world is advanced by world-continuity's `coarse-step`, which calls no `IWorldStoryHost`: its
offers are **dormant** — kept, not fired, not lapsed — and `world.offerLifetimeTurns`, like every narrative world
clock, counts full-step turns only. A fallen world's open offers close as lapsed with no negative fact and its facts
stay as frozen read-only history. world-continuity's `world-event-budget` module (its map row 12: *"hibernating events
resolve inside `CoarseStep` from the same deck"*) disagrees with "not drawn"; that is reported at map level, not
resolved here.

**Lapse.** An offer not answered within `world.offerLifetimeTurns` turns (tuning, starting 2: the turn it appears and
the next, so a player who ends a turn without reading it still gets one planning turn) is reported `story.lapsed`
and closes as if `leave` were chosen — no penalty, no negative fact.

### 5. Typed report kinds

`TurnReportKinds` (`TurnReport.cs:3-10`) gains three members, each a reviewed vocabulary change:

| Kind | Subject | Detail (closed grammar) | Playback row (filed on `world-playback`) |
|---|---|---|---|
| `story.offered` | offer ref | `{storyletId}@{revision}` | "Something is happening at {place}" + open the storylet card |
| `story.answered` | offer ref | `slot:{n}:{ordinal}` or `slot:{n}:{ordinal}:battle:{battleId}` | the chosen option's result text (`narrative-text`) |
| `story.lapsed` | offer ref | `lapsed` | "The moment passed at {place}" |

Player text never comes from `Detail`: the playback row resolves the storylet's keyed text through `narrative-text`
by offer ref. `world-stage-map.md:82` holds the one translation table; every new kind lands there with a golden in the
same change, so no raw prefix reaches the player (map `:319`).

### 6. Settle (Data, post-Step, same transaction)

`NarrativeWorldPass.Run(db, tx, worldId, turn, result.Report, input)` (new), placed beside `CargoResolveUnlocked`
(`RpgStore.WorldTurns.cs:621`) and before the log insert:

- `story.offered` → `storylet.seen` fact (world scope; source `turn:{worldId}:{turn}:{entryIndex}`,
  `spec-story-ledger.md` §3) carrying the offer (slot key, revision, cast, pin key — the attribute addition filed by
  `spec-choice-resolution.md` Contradictions 2).
- `story.answered` → `choice.picked` + `OutcomeRouter.Plan` → `OutcomeExecutor` in this transaction, with
  `WorldHostBudget` (below). A plan whose fight lost runs its `onLoss` steps only (`spec-outcome-routing.md` §4).
- `QuestLifecycle.Capture` for the committed report, then `QuestLifecycle.Settle` for world-scope quests
  (`spec-quest-sources.md` §3.3, §5).
- `NarrativeNotify.AfterCommit` after the transaction commits (`spec-quest-log-contract.md` §4).

Every write dedupes on the turn-entry source ref, so a crashed commit that retries (the barrier refuses a second
commit of the same turn, `RpgStore.WorldTurns.cs:480-492`) can never double-apply.

**Budget.** `WorldHostBudget : IHostBudget` — loot from the host sector's own `world-sector` source
(`WorldSectorLootSource`, `gk-core/src/FusionRpg.Core/Items/Drops/WorldSectorLootSource.cs:32`); souls **0**; spendable stocks
`[souls]` (`spec-outcome-routing.md` §3). Owner ruling 2026-09-20: the **budget line** is the claim loot lines the
committed End Turn already makes in this world (`claim.loot:` report entries, `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:128-133`).
A world storylet's `loot` outcome and a world quest's reward are `reward.owed` facts that the Settle half pays by
**taking** an unused claim line of the turn — minted under that line's correlation with the outcome's window — oldest
`seq` first; the rest wait for a later full-step turn. The Settle pass runs before the claim-loot mint, so no roll
is ever added. ~~(filed on world-map-program, whose mint does not exist yet)~~ Owner ruling 2026-09-20 (round 5):
R17 — the mint is this program's prerequisite module `world-claim-loot` (`spec-world-claim-loot.md`), which lands
before this one: it turns `ClaimResolver`'s `claim.loot:` lines on and mints the unused ones after this pass. The
Settle half lists lines through its `UnusedClaimLootLinesUnlocked` and takes one through `MintClaimLootLineUnlocked`
with the payout's window (§6 of that spec) — the claim's own roll path, never a second roller.

**Θ.** `HostContentTheta.ForSector(power, sector, ParentWorldTermsSource.For(world))` (`spec-host-content-theta.md`
§2-§3).

### 7. Warlords as characters

World-graph's roaming powers are `WorldEntityKind.Warlord` entities (`gk-core/src/FusionRpg.Core/World/WorldState.cs:61-68`).
When a warlord entity is created, the world cast step (`spec-cast-resolver.md` §1) casts a `warlord`-role character
onto it: home `world-entity:{entityId}` (a home kind added to `character-registry`'s closed list, filed), world
scope. A warlord character:

- **never grows from an encounter** (rule 1) — `character-registry`'s guard (`spec-character-registry.md` §5); its
  entity's growth is world-map's world rule (rule 6), untouched here. Audit 2026-09-19: naming a warlord makes rule 6
  bind **world-map's** future warlord-growth rules too — a named warlord that gained members, level or lairs *because it
  beat the player's legion* would be the Nemesis shape even though no narrative code wrote it. No warlord growth code
  exists today (`WorldEntityKind.Warlord` is an enum member and a display name only, `WorldState.cs:67`,
  `EntityNaming.cs:35`), so this is a filed constraint on world-map-program's warlord-growth design, not a defect;
- **never remembers the player** (rule 3) — no relation fact is ever written about it; its lines are chosen by
  context and its **faction's** band only (`narrative-text`);
- **is not ranked** (rule 2) — no hierarchy type; a warlord's defeat writes nothing about the warlord, only a
  world-scope `flag.set` a later storylet may read at faction level.

### 8. Goldens and `RulesetVersion`

- **Seam off or input empty** (no eligible storylet, no open offer): `RunEvents` writes nothing and the phase is
  today's. World goldens must be byte-identical — proven by running the world golden suite with the seam attached and
  an empty fixture corpus.
- **Content on**: the same command log now yields story entries and possibly guard fights, which is the version
  history's own bump condition (`TurnEngine.cs:100-114`). This module therefore **proposes** one `RulesetVersion`
  bump in the change that attaches the seam in `CommitWorldTurn`, and any golden that moves with content on is
  re-blessed in that same change under world-map-program review (G4). Whether the bump lands is world-map-program's
  call; the spec does not assume it.

## Data shapes

- `rpg_world_turn_log.story_input_json TEXT NULL` (world-map-owned table; §2).
- `WorldStoryInput` canonical JSON: `{ candidates: [{ sectorId, slotIndex, hostKind, pity, tiers: [{ tier, options:
  [{ storyletId, revision, weightMilli, castJson }] }] }], openOffers: [{ offerRef, sectorId, slotIndex, views:
  [ChoiceView], outcomes: [...] }] }`.
- Tuning **declared in `narrative.v1.json` at wave 0 (plan §4 D4; current version `v2`)**: `world.offerLifetimeTurns` (turns, `long`) — read here, not added in this module's build change.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| fire chance, weights | `long` per-mille, `checked` | `base + n × step` grows with `n` (`spec-narrative-vocabulary.md` Numeric types) |
| roll seeds | `long` from `DeriveRollSeed`; the engine's `ulong` seed cast `unchecked` as `WorldSeed` itself does (`WorldSeed.cs:29`) | reinterpretation, not arithmetic |
| turn | `int` | `TurnEngine`'s own type; the ledger stores it widened to `long` |
| `ChoiceSlot` | `int?` | 0..3 |

## SOLID notes

- **S:** the turn engine owns the loop; the story phase decides only what the world's storylets do this turn; Data
  owns persistence.
- **O:** the engine gains one optional seam, exactly as it took `IBattleResolver`; no phase is added or reordered.
- **L:** `story = null` is today's `Step`, byte for byte.
- **D:** the engine depends on `IWorldStoryHost`, never on narrative types.
- One storylet engine (selection is `storylet-selection`'s); no second turn loop, report, command path or push path.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs','gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs','gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs','src/FusionRpg.Core/Narrative/Hosts/WorldStoryPhase.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','tests/FusionRpg.Core.Tests/Narrative/Hosts/WorldStoryPhaseTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World|FullyQualifiedName~Narrative.Hosts"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn|FullyQualifiedName~NarrativeWorld"
```

The change crosses Core, Data and the world goldens, so the build task runs the full suite once at its end (AGENTS.md
verification boundary, point 2).

## Structure

```
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs                (edited: optional IWorldStoryHost; Events takes revealed + resolver)
src/FusionRpg.Core/World/Turn/IWorldStoryHost.cs           (new)
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs              (edited: EventChoose, OfferRef, ChoiceSlot)
gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs     (edited: event.choose arm)
gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs                (edited: three story kinds)
src/FusionRpg.Core/Narrative/Hosts/WorldStoryPhase.cs      (new: resolve orders, fire offers)
src/FusionRpg.Core/Narrative/Hosts/WorldStoryInput.cs      (new: canonical input)
src/FusionRpg.Core/Narrative/Hosts/WorldHostBudget.cs      (new)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs           (edited: build input, story_input_json, NarrativeWorldPass call, replay)
src/FusionRpg.Server/Narrative/NarrativeWorldPass.cs       (new)
tests/FusionRpg.Core.Tests/Narrative/Hosts/WorldStoryPhaseTests.cs       (new)
tests/FusionRpg.Data.Tests/Narrative/NarrativeWorldCommitTests.cs        (new; in-memory store)
```

`NarrativeWorldPass` sits in Server because it needs the corpus and the router; it is invoked through a delegate the
commit takes, the way `CommitWorldTurn` already takes `policies` (`RpgStore.WorldTurns.cs:493-495`), so Data never
references Server.

## Testing strategy

Game closed; fixture world, corpus and ledger; stores in memory.

- **Seam off is today:** every existing world test and golden passes with `story = null`, and with the seam attached
  over an empty input.
- **Fog:** a fixture storylet eligible at a sector the player neither owns nor saw last turn never fires; the same
  sector fires once owned.
- **Unsigned fire roll:** over a fixed seed list including seeds whose `DeriveRollSeed` is negative, the observed fire
  share tracks `p` (a relation) and no roll is negative.
- **Dormant (round 4):** a fixture world that hibernates keeps its open offers unfired and unlapsed through a coarse
  catch-up, and lapses them only after `world.offerLifetimeTurns` further full-step turns. The report entry's `Audience` is the player faction; a projection for another faction omits it.
- **Fire curve:** over a fixed seed list, fire frequency rises with `n` and a fire resets `n` (relation, not a pinned
  rate); `p` never exceeds 1000.
- **One per sector, one spine beat per turn.**
- **Admission:** each refusal id fires for its malformed order; a well-formed order for a closed offer is **admitted**
  and then dropped at reveal with `story.offer-closed` (admission never judges legality at reveal).
- **Resolution:** an `event.choose` resolves with the precomputed odds on its named stream; the same command log and
  input replay to the same report and state hash (replay test through the store's replay path).
- **Order independence:** two players' orders (or an order and the fire pass) produce the same result whatever the
  submission order — reveal orders by commander then command id (`TurnEngine.cs:201-212`).
- **Fight:** a `fight` choice produces a `Guard` `BattleRequest` to a spy resolver; a resolver refusal reports the
  answer without applying the fight-conditional steps.
- **Settle dedupe:** re-running `NarrativeWorldPass` for a committed turn adds no fact, loot or quest.
- **Lapse:** an unanswered offer lapses after the configured turns with no negative fact.
- **Warlord guards:** a warlord character's specimen is unchanged by any story outcome; no relation fact about it is
  ever written.
- **No population:** fixtures only.

## Success criteria

1. World storylets fire in the `Events` phase, fog-correct, through one optional seam. 2. `event.choose` is admitted
like any order and resolved at End Turn, deterministic on replay. 3. Three typed report kinds exist, each with a filed
playback row. 4. Goldens are byte-identical with no eligible content; any golden that moves with content on is
re-blessed with world-map-program. 5. Warlords are characters under the six anti-Nemesis rules. (G4 world half.)

## Boundaries

- **Always:** a parameter seam; persist the input for replay; fog-correct entries; dedupe every settle write.
- **Ask first (world-map-program):** the `Events` signature, the `story_input_json` column, the `RulesetVersion` bump,
  any golden re-bless.
- **Never:** a second turn loop or phase; mutate `WorldState` from Data outside the reviewed post-Step pattern; fire in
  a sector the player cannot see; grow, rank or give memory to a warlord.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `IWorldStoryHost` + `WorldStoryPhase` | `TurnEngine.Step`, the store's commit and replay |
| `event.choose` + `OfferRef`/`ChoiceSlot` | world-stage `world-inspector` (the answer action, filed), `storylet-card` |
| `story.offered/answered/lapsed` | world-stage `world-playback` (translation rows, filed), `notify` rail |
| `GET /api/narrative/{playerId}/offers?worldId=` → open offers with `ChoiceView`s | `storylet-card` (FE) |
| the Settle pass hook | `petition-host`, `counter-doctrine` (same phase, same pass) |

## Contradictions found (report; not fixed here)

1. **"A seam the turn engine calls" versus a pure engine.** Map row 18 (`:223`) puts world storylets inside the
   `Events` phase; the engine is pure over state, commands and seed, and cannot read the story ledger. This spec keeps
   the choice and fire rolls in-engine (deterministic, replayable) over a persisted input, and puts every ledger write
   in a post-Step pass — the shipped cargo precedent. The persisted input needs a new `rpg_world_turn_log` column;
   that is world-map-program's schema and is filed there, not assumed.
2. **Guard fights resolve to a no-op today.** `TurnEngine.Step`'s default resolver is `DistrictAssaultResolver`, and
   every battle kind it cannot simulate *"resolves to a refused/no-op outcome"* (`TurnEngine.cs:149-156`). A world
   storylet `fight` is therefore a real `BattleRequest` that currently refuses; it becomes a real fight when
   world-map-program's resolver simulates guard fights. This is a wiring gap owned by world-map, not a design wall.
3. **Petitions and doctrine share this pass.** Map rows 19 and 24 list `petition-host` and `counter-doctrine` as
   separate modules; both run in the same `Events` phase and post-Step pass defined here, as extensions, not as
   second passes.

## Open questions

None for the owner. Every item above that needs a decision is world-map-program's review, named in Boundaries.

## Design-gate checklist

```
[x] Subsystems: world map turn engine (seam, reviewed), world commands, turn report, fog, battle seam, economy (host
    budget), characters (warlords), story ledger, world-stage surfaces (filed asks).
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map (full); ideal §6.2, §6.6, §6.12; DESIGN-GATE §1 World map, Battle, UI rows, §2, §5;
    world-stage-map.md module table; sibling specs; code: TurnEngine (Step, Events, versions), WorldCommand,
    WorldCommandAdmission, TurnReport, BattleSeam, FactionIntel, WorldState, WorldSeed, RpgStore.WorldTurns
    (commit, post-Step passes, hot tail, replay), WorldSectorLootSource.
[x] decisions.md: NS8 drafted in the map, appended by this module's build change jointly with world-map-program.
[x] Every claim cites file:line.
[x] Goldens: stability is a test to run (seam off, empty input), not a claim; the bump is proposed, not assumed.
[x] No population pinned.
[x] No cache; the input is a per-turn value persisted for replay.
[x] Order independence: reveal order is canonical; tested with swapped submission order.
[x] Actor numbers: none; fights go to the battle resolver.
[x] No parallel path: one turn loop, one report, one command path.
[ ] Registry row: none new; the R13 guards are character-registry's.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (World map: commands through `WorldCommandAdmission`, resolved
at End Turn, deterministic and replayable; Battle; Economy; Standalone; UI rows), §2 (1, 2, 9, 12, 13, 15, 16), §3,
§5; `economy-principles.md` P1, P13, P14; R13's six rules; round-3 and round-4 rulings; `world-continuity-map.md`
modules 6, 7, 12.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | MEDIUM | **Negative modulo.** `DeriveRollSeed` returns a signed reinterpretation of a `ulong`; `mod 1000` on it yields negative values half the time, all below any threshold — a deterministic but wrong fire rate | **Fixed** (§3 step 2): reinterpret as `ulong` before `%`; test |
| 2 | MEDIUM | **Two roll implementations.** The phase rolled `event.choose` with its own arithmetic beside `ChoiceResolver.Resolve` — the "displayed odds are the rolled odds" guarantee held for one path only | **Fixed** (§4): the phase calls `ChoiceResolver.ResolveFromViews` |
| 3 | MEDIUM | "Nothing else in the phase touches `WorldState`" contradicted `counter-doctrine`, which writes hashed faction state in this phase | **Fixed** (§4): the one exception named, further ones reviewed |
| 4 | MEDIUM | Round-4: dormant/fallen worlds — offers, lapse clock and firing were unstated; a coarse catch-up would lapse every open offer at once | **Fixed** (§4 "Dormant worlds"), test |
| 5 | MEDIUM | World loot through `WorldHostBudget` is an on-top faucet (see `spec-outcome-routing.md` audit #1) | **Resolved — Owner ruling 2026-09-20:** world payouts take existing claim loot lines (§6 Budget, `spec-outcome-routing.md` §3) |
| 6 | LOW | R13 rule 6 binds world-map's future warlord growth once warlords are named | **Filed constraint** (§7) |
| 7 | LOW | `TurnEngine.cs` line citations drifted (`RulesetVersion` is `:124`, phase order `:190-207`, `Events` `:352-365`) | **Fixed** |

R13 rule-by-rule for warlords: 1 — character-registry guard + filed world-map constraint; 2 — no hierarchy type;
3 — no relation fact about a warlord, faction band only; 4 — no base from traits; 5 — local; 6 — filed constraint.

**Registry row proposed** (shared file, not written): `ns-world-story-seam-null` → world golden suite run with the seam
attached over an empty input (byte-identical). **Boundary ask:** `gk-core/src/FusionRpg.Core/Narrative/Hosts/**` →
`FusionRpg.Core.Tests` `Narrative.Hosts`; `src/FusionRpg.Server/Narrative/NarrativeWorldPass.cs` (new) →
`FusionRpg.Data.Tests` `NarrativeWorld`; the `TurnEngine.cs` edit keeps its existing world-golden mapping.

## Cross-lane alignment (2026-09-20)

Owner ruling 2026-09-20 (rewards come out of the host budget): the world host's budget line is the End Turn's claim
loot lines; storylet loot and world-quest rewards take one each, oldest owed first, and never add a roll
(`spec-outcome-routing.md` §3). The Settle dedupe (every write keyed on its turn-entry source ref, §6, P14) is unchanged; the owed payout's own
key and the taken line's correlation make a replayed Settle pay nothing. Audit finding 5 is closed.

- Alignment 2026-09-20: the six `world.*` slot host kinds and `world.petition` are now rows of the seed-side
  `host-kinds.v1.json` (`narrative-seed/spec-storylet-vocab.md` §3.1), with the `admits` lists this host's
  `KindFits` reads (`spec-storylet-reseam.md` §2: the host asks the file, never a private table); ~~all are
  climate-neutral, so `SelectionRequest.Climate` is `null` on world hosts.~~ Owner ruling 2026-09-20 (round 5): R19 —
  world hosts are no longer climate-neutral; ~~the site climate is derived from the sector type~~ (Owner ruling 2026-09-20 (round 6), R20: the site
  climate is the sector's own `WorldSector.Climate`) (§3 "Climate").
- Owner ruling 2026-09-20 (round 5): R17 — the world budget line is minted by the prerequisite module
  `world-claim-loot` (§6 Budget; `spec-world-claim-loot.md`).

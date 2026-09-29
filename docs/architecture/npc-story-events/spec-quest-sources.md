# Spec: quest-sources

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `quest-sources`, row 14 of the [npc-story-events map](../npc-story-events-map.md) (`:219`), wave 3. Depends
on `story-ledger` (quest facts). Consumed by `outcome-routing` (`quest.offer`), `quest-log-contract`, the wave 4
hosts (which feed it facts) and, as evidence, achievement-title's evaluator. Implements ideal §6.5
(`npc-story-events-ideal.md`) and §11 item 5 (`:678`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

One quest engine for every place. The Delve's engine — `QuestCatalog`, `QuestOffer`, `QuestProgress`,
`QuestReward` — stays the engine; this module generalizes its one fact source (a `DelveReport`) into **fact sources
per place**: the Delve report, the committed world turn report, an expedition resolution, persisted battle reports
of every mode, and the story ledger itself. Objectives are **mode-agnostic**: no objective can be completed only on
the lawn. Save- and world-scoped quests live as story-ledger facts; delve-scoped quests keep the Delve's per-run
record. Expiry counts on the offering host's clock; abandoning is free; a reward is one roll **taken out of** the
host's existing budget line with the quest's window (Owner ruling 2026-09-20: never an extra roll), deduped on the
quest's durable id; completion is achievement evidence.

Success looks like: a world quest offered by a storylet completes from committed turn reports with the game
closed; a "defeat creatures" objective counts an expedition battle and a world battle alike; the same facts give
the same verdict in any evaluation order; abandoning writes one fact and costs nothing else; no objective template
exists whose only source is the lawn.

## Locked anchors

- **One quest engine, fact sources per place** (ideal §6.5, `npc-story-events-ideal.md`; map row 14,
  `:219`; map principle 11, `:108-110`).
- **Evaluation is pure and total**: *"recomputes from scratch every call, holds no counter... same (quest, report) ⇒
  same verdict"* (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestProgress.cs:9-11`); today it switches on nine Delve templates
  over a `DelveReport` (`:30-47`).
- **Standalone-first objective rule** (map principle 3, `:80-82`; ideal §0 item 3, `:40-42`): *"kill 30 on the lawn
  is not a legal objective"*. Lawn facts are `PvzActivityKinds` (`gk-core/src/FusionRpg.Core/Activity/PvzActivityKinds.cs:6-13`).
- **Rewards from the host's budget** (ideal §11 item 1, `:674`; map principle 8, `:97-100`), through the existing loot
  path: the Delve quest precedent brings *"only its window"* to a table the host already rolls
  (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestReward.cs:7-19`), correlated by `LootCorrelation.Derive`
  (`gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs:135-161`), whose source kinds already include `world-sector` and
  `expedition-tier` (`gk-core/src/FusionRpg.Core/Items/Drops/DropTableValidator.cs:58-59`).
- **Host clocks, never the calendar** (map principle 4, `:83-85`); **free abandon** (ideal §11 item 5, `:678`).
- **Achievements are achievement-title's engine**; quest completion is evidence only (map ownership table, `:322`).
  The evaluator takes durable `AchievementEvidence` (`gk-core/src/FusionRpg.Core/Achievements/AchievementRegistry.cs:176-186`)
  and is not hosted yet (`gk-core/src/FusionRpg.Server/Program.cs:403-410`).

## Design

### 1. What exists, read against the code

| Piece | Today | Production caller |
|---|---|---|
| `QuestCatalog` (anchors: template, target, count band, reward band, scope ∈ `delve/domain/roster`, predicate) | `gk-core/src/FusionRpg.Core/Delve/Quests/QuestRow.cs:23-30`; scope check `QuestCatalog.cs:155-157` | domain importer (party-dungeon) |
| `QuestOffer.Draw` | equal-weight draw on `dungeon:quest:{n}` (`QuestOffer.cs:107-140`) | preflight only (`QuestPreflight.cs:313`) |
| `QuestProgress.Evaluate` | nine templates over `DelveReport` (`QuestProgress.cs:30-47`) | **none** |
| `WriteQuestOffer` / `WriteQuestVerdicts` / reward banking at `CloseDelve` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:517`, `:550`, `:650` | **tests only** for the offer (map `:183`) |

Owner ruling 2026-09-19 (round 3): the Delve's offer at `CreateDelve` and its tracker endpoint moved from
party-dungeon's D4.14 to this program's `delve-live-start` (`spec-delve-live-start.md` §4); the verdict write at
`CloseDelve` stays party-dungeon's. This module still **does not** wire either: it makes the Delve one source among
several and ensures a delve-scoped quest can also appear in the quest log.

### 2. Two families of quest, one engine

| Family | Offered by | Record | Evaluated from |
|---|---|---|---|
| **Delve quest** (scope `delve`/`domain`/`roster`, today's) | `QuestOffer.Draw` at `CreateDelve` (party-dungeon) | `rpg_delves.quests_json` (`RpgStore.Delve.cs:107`) | `DelveReportSource` = today's `QuestProgress.Evaluate`, unchanged |
| **Narrative quest** (scope `save`/`world`, new) | a `quest.offer` outcome (`outcome-routing`) | story-ledger facts (§4) | the fact sources of §3 |

Both share `QuestRow`, the template registry mechanism and `QuestReward`'s window shape. A narrative quest's
anchor is a `QuestRow` whose `Scope` is `save` or `world` and whose `TemplateId` is a **narrative objective template**
(§3); `QuestCatalog.Load` accepts the two new scopes when the caller passes them (it reads scopes as a parameter,
`QuestCatalog.cs:87`, `:155`), so no second catalog exists. Owner ruling 2026-09-19 (round 3): the anchor and the
objective registry are narrative-seed's `quest-vocab` (`narrative-seed/spec-quest-vocab.md` §2–§3), which chose
**widen, not beside**; its §1 lists the three runtime changes this module makes to `QuestCatalog` for it.
Alignment 2026-09-20: the exact seed-field → `QuestRow` mapping (envelope unwrapped; `id` → `QuestId`, `templateId` →
`TemplateId`, `"none"` → `null` on `targetRef`/`countBand`, `eligibility: null` → `Predicate`, and the appended
`Expiry`, `Name`, `Flavor`, `Revision`, `Status`, `Provenance`, `Tokens` members) is owned by
`narrative-seed/spec-quest-vocab.md` §3.1; this module's loader implements that table and does not restate it.

### 3. Fact sources and mode-agnostic objectives

```csharp
namespace FusionRpg.Core.Narrative.Quests;

/// One place's durable record, read-only. A source never mutates anything and never reads live state.
public interface IQuestFactSource
{
    string SourceKind { get; }                 // closed: see the table below
    /// Durable facts of this source for the player, strictly after the quest's offer point, in the source's own order.
    IEnumerable<QuestFact> Facts(long playerId, QuestWindow window);
}

public sealed record QuestWindow(StoryScope Scope, string WorldId, long OfferedAtSeq, long? OfferedAtTurn);

public sealed record QuestFact(string SourceKind, string DurableId, string FactKind,
    IReadOnlyDictionary<string, string> Tags, long Count);
```

**Sources** (closed; each reads a record some other program already commits — never a hook in its code):

| `SourceKind` | Reads | Durable id |
|---|---|---|
| `battle` | persisted `BattleReport` actor results (`BattleActorResult(Key, Side, SpeciesId, TypeId, …, Kills, Survived, …)`, `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:596-599`) from the stores that keep them — today `rpg_web_match_log` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:726`), which holds expedition and web-match battles | the match key |
| `world-turn` | `rpg_world_turn_log.report_json` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:41-50`) for the quest's world, turns after the offer, entries the player's audience may see | `turn:{worldId}:{turn}:{entryIndex}` |
| `expedition` | collected expeditions (state `Collected`/`Recalled`) and their tick outcomes (`ExpeditionTickOutcome`, `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:17-19`) | `expedition:{expeditionId}` |
| `delve` | closed delves (final state, `RpgStore.Delve.cs:81`, `CloseDelve` `:762`) and their `DelveReport` | `delve:{delveId}` |
| `story` | story-ledger facts (`met`, `helped`, `flag.set`, `chapter.reached`, …) | the fact's `seq` |
| `pvz` | lawn activity facts (`PvzActivityKinds`) — **enrichment only** (§3.1) | the activity fact id |

**Narrative objective templates** (closed vocabulary, `data/seed/narrative/_registry/quest-objectives.v1.json` (new)
(new), each row naming the sources that can fill it):

| Template | Counts | Sources | Target kind |
|---|---|---|---|
| `defeat-creatures` | enemy actors with `Survived = false` matching the target tag (side, element or species) | `battle`, `pvz` | creature tag |
| `win-battles` | battles won by the player's side | `battle`, `world-turn` (battle entries) | none or battle kind |
| `hold-sector-kind` | at the end of a committed turn, the player owns a sector holding the target slot kind | `world-turn` | slot kind |
| `hold-sector` | the player owns the target sector at the end of `need` consecutive committed turns after the offer | `world-turn` | sector id (bound at offer) |
| `develop-sector` | a `develop.completed` report entry for the target sector (`gk-core/src/FusionRpg.Core/World/Growth/GrowthPhases.cs:132`) | `world-turn` | sector id (bound at offer) |
| `complete-expeditions` | expeditions collected (not recalled early) at or above a tier | `expedition` | tier id |
| `extract-delves` | delves closed `Extracted` | `delve` | none or domain id |
| `story-fact` | a story-ledger fact of the target kind about the target subject exists | `story` | fact kind + subject |

The count for a counted template comes from the quest's `CountBand` through the dungeon registry's count bands (the
Delve's own vocabulary, `lone · few · several · many`, `QuestCatalog.cs:45-47`) — no new count table.

#### 3.1 The standalone rule, made structural

A template is **legal** only if at least one of its sources is standalone-playable (every source except `pvz`).
`pvz` may **add** to a count a standalone source can also fill (the lawn enriches); it may never be a template's
only source (the lawn never gates). `QuestObjectiveRegistryTests` fails on a template whose source list is `[pvz]`,
and the registry loader refuses it with `quest.objective-lawn-only`. This is the guard for map success criterion
"no objective template reads a lawn-only fact" (`npc-story-events-map.md:376-377`).

#### 3.2 Evaluation

`NarrativeQuestProgress.Evaluate(QuestRow quest, int need, IEnumerable<QuestFact> facts)` is `QuestProgress.Evaluate`'s
shape for the new templates: pure, total, recomputed from scratch, no stored counter. Facts are de-duplicated by
`(SourceKind, DurableId)` before counting, so the same battle read through two paths counts once. Summation is
order-independent by construction; `hold-sector-kind` reads the **latest** committed turn in the window, which is
defined by turn number, not by read order.

#### 3.3 Retention: capture matching facts at commit

Some source records are not kept forever: world turn report bodies older than the hot tail are dropped
(`ReportHotTail = 50`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:476`, trimmed at `:703`). A quest with no
expiry can outlive that window. So at each host commit, `QuestLifecycle.Capture` (§5) reads the **just-committed**
source record and, for every open quest it matches, appends one `quest.progressed` fact (subject the quest, attrs
`{sourceKind, durableId, count, tags}`, dedupe `progress:{questSubject}:{sourceKind}:{durableId}`). Evaluation then
reads those facts through the `story` source, so a verdict never depends on another program's retention. This is
not a stored counter: each fact is one durable source record's contribution, re-summed on every evaluation, and a
re-capture is a no-op. `quest.progressed` is a new `StoryFactKind` member, added as a reviewed change
(`spec-narrative-vocabulary.md` §3 lets `quest-sources` add members).

### 4. Narrative quest lifecycle as facts

All in the story ledger (`spec-story-ledger.md` §2) using the vocabulary's quest kinds (`quest.offered`,
`quest.completed`, `quest.failed`, `quest.abandoned`, `quest.expired`, `spec-narrative-vocabulary.md` §3). Subject:
`quest:{questId}#{offerSeq}` (a quest id may be offered again later; the offer's `seq` makes each instance unique).

| Fact | Written by | Attrs |
|---|---|---|
| `quest.offered` | `outcome-routing` for a `quest.offer` consequence (source: the storylet answer) | `{questId, revision, need, hostKind, clockKind, offeredAtClock, expiresAtClock?, rewardHostRef}` |
| `quest.completed` | `QuestLifecycle.Settle` (§5) when the verdict is done | `{have, need}` |
| `quest.expired` | `QuestLifecycle.Settle` when the host clock passes `expiresAtClock` first | — |
| `quest.abandoned` | the abandon route | — |
| `quest.failed` | a template whose failure is observable (none of §3's eight has one in v1); and, Owner ruling 2026-09-19 (round 3, confirmed round 4), every open **world**-scoped quest of a world whose outcome becomes `fallen` (world-continuity `world-fall`), written in the same fall pass as `spec-character-registry.md` §4 — "retire" means frozen, never deleted | `{cause: world-fallen}` when written by the fall |

A quest is **open** while it has `quest.offered` and none of the four closing facts. Offering *is* accepting:
the player chose the `quest.offer` choice in a storylet, so there is no separate accept step (the Delve precedent:
the offer persists at `CreateDelve` and is evaluated at close with no accept step, `RpgStore.Delve.cs:509-517`,
`:546-550`).

**Expiry on the host's clock.** `expiresAtClock = offeredAtClock + narrative.quest.expiry.{clockKind}` for the
offering host's clock kind (`HostClockKind`, `spec-narrative-vocabulary.md` §3: world turns, expedition collects,
sanctum returns). A quest anchor may declare `expiry: none` (spine and arc quests), because an expiry is a pacing
choice, not a ceiling. No quest reads real time.

**World state and quests** (Owner ruling 2026-09-19 (round 4)). World-scoped quest state is never deleted:

| The quest's world | Its open quests |
|---|---|
| `active` | live: captured and settled at each End Turn commit |
| `hibernating` / `idle` (dormant) | **paused**: no capture, no settle, no expiry. The `world.turn` clock a world quest expires on counts **full-step committed turns only** — Audit 2026-09-19: world-continuity's `coarse-step` advances a dormant world by `n` turns on catch-up (`world-continuity-map.md` module 6), and those catch-up turns never count toward a quest's expiry or a `hold-sector` streak |
| `outcome = fallen` | **closed as failed-by-fall**: one `quest.failed` fact with `{cause: world-fallen}` (below), no penalty beyond the lost reward; the history stays readable for `world-reclaim` |

**Abandon is free.** `quest.abandoned` closes the quest; nothing else is written — no relation fact, no cost, no
cooldown penalty. Losing the reward is the whole consequence (ideal §11 item 5).

### 5. Settlement

`QuestLifecycle.Capture(playerId, sourceRecord)` (§3.3) then
`QuestLifecycle.Settle(playerId, scope, worldId, hostClockNow)` run at each host's commit point — End Turn commit
for world quests, expedition collect for expedition-offered quests, sanctum entry for save quests — and for each
open quest in that scope evaluates §3.2 then appends at most one closing fact, deduped by
`quest-settle:{questSubject}`. Completion is decided **before** expiry within one settlement: a quest whose last
needed fact arrives on the turn it expires completes (ties go to the player; stated so no order is implied by
code layout).

Delve-scoped quests keep `WriteQuestVerdicts` at `CloseDelve` (party-dungeon). When party-dungeon writes a verdict,
the Server mirrors it as `quest.completed`/`quest.expired` with source `delve:{delveId}:quest:{questId}` so the quest
log reads one lifecycle for every quest (a mirror, never a second verdict).

### 6. Rewards — the host's own loot source, a window, one dedupe key

A completed narrative quest pays **one roll taken out of** an existing budget line named by `rewardHostRef`, with the
anchor's `RewardBand` as a rarity window — `QuestReward.Request`'s shape (`QuestReward.cs:41-70`) generalized from the
Delve's `cache` table to the host's source. Owner ruling 2026-09-20: the roll is never added; it takes one roll the
host already makes, by `spec-outcome-routing.md` §3's rule (minted under that roll's correlation; `reward.owed` until a
roll is free):

| Offering host | Budget line the roll is taken from (Owner ruling 2026-09-20) | P14 key (the `reward.owed` subject) |
|---|---|---|
| world (`world.*`) | a claim loot line (`world-sector`) of the settling End Turn in the quest's world (Owner ruling 2026-09-20 (round 5): minted by `world-claim-loot`, `spec-world-claim-loot.md` §6) | `quest:{questSubject}` |
| expedition | one `expedition-tier` roll of the settling collect, else the save's next collect | `quest:{questSubject}` |
| sanctum (save quests) | one `expedition-tier` roll of the save's next collect; while the save has never collected, the reward stays owed (Audit 2026-09-19's "no roll, never a guessed tier" holds: nothing is paid until a real roll exists) | `quest:{questSubject}` |
| delve | `dungeon-quest` (today's), unchanged | `{delveId}:quest:{questId}` |

(Alignment 2026-09-20: the table above replaces a source-id table whose ids were per-quest correlations; the key
column is now the owed fact's subject, and the correlation is the taken roll's own.)

Owner ruling 2026-09-20 — **a quest reward is taken out of the host's payout, never added to it.** The Audit
2026-09-19 paragraph that stood here called the reward an on-top "bounded faucet" and deferred the economy call; the
ruling closes it. Settlement appends `reward.owed` (subject `quest:{questSubject}`, deduped); the host's next commit
that has a free roll of its budget line mints it under that roll's correlation and appends `reward.paid`
(`spec-outcome-routing.md` §3). The owed fact's key and the taken roll's correlation are both durable, so a replayed
settlement cannot pay twice. **No souls, no new stock, no new source kind, no added roll** — total income is what
the hosts already pay. The roll itself is `outcome-routing`'s job through the loot pipeline; this module returns the
`QuestRewardRequest`.

### 7. Achievement evidence

For each `quest.completed` fact, `QuestAchievementEvidence.From(StoryFact)` (pure) builds an `AchievementEvidence`
with `FactId = seq`, `Count` = the player's completed-quest count in scope, `WorldId` for world quests and
`T = "quest.completed:{questId}"` — the shapes the registry's `counter-reach` and `event-seen` triggers read
(`AchievementRegistry.cs:20-27`). Enqueueing is achievement-title's (its evaluator is not hosted; map `:184`); the
durable fact is the evidence, so a later-hosted evaluator backfills by `MaxFactId` without this module changing.

## Data shapes

- `data/seed/narrative/_registry/quest-objectives.v1.json` (new): `{ templateId: { targetKind, targetRef, counted,
  sources: [..] } }`. Owner ruling 2026-09-19 (round 3): authored by narrative-seed's `quest-vocab`
  (`narrative-seed/spec-quest-vocab.md` §2); this module reads it.
- Narrative quest anchors: `QuestRow` JSON with `scope: save | world`, under `data/seed/narrative/quests/` (new)
  when generated, or the authored path with `provenance: authored` (ideal §11 item 10, `:683`).
- Tuning **declared in `narrative.v1.json` at wave 0 (plan §4 D4; current version `v2`)**, not added in this
  module's build change (every key required,
  `spec-narrative-vocabulary.md` §5):

| Key | Unit | Starting value and reason |
|---|---|---|
| `quest.expiry.world.turn` | turns, `long` | 20: about three of the ideal's ~7-turn threat cycles (ideal §7, Threat row) — long enough to plan a march |
| `quest.expiry.expedition.collect` | collects, `long` | 5: a few returns, matching the per-storylet expedition cooldown scale (`spec-narrative-vocabulary.md` §4) |
| `quest.expiry.sanctum.return` | returns, `long` | 5, same reasoning |
| `quest.openLimitPerScope` | count | **not a key**: there is no open-quest limit. Storylets pace offers (cooldowns); a limit would be a ceiling |

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `have`, `need`, fact counts | `long`, summed `checked` | counts over an unbounded play life; `QuestVerdict` keeps `int` for the Delve path, and the narrative verdict narrows `checked` only at the Delve mirror |
| clocks, `expiresAtClock` | `long` | world turns are unbounded (R3) |
| `OfferedAtSeq` | `long` | ledger `seq` |

## SOLID notes

- **S:** one engine (templates + evaluation + reward window); sources only read records; settlement only writes
  closing facts.
- **O:** a new place adds an `IQuestFactSource`; a new objective is a registry row plus one evaluator arm.
- **L:** the Delve evaluation is unchanged behind `DelveReportSource`; its verdicts mirror into the same lifecycle.
- **D:** evaluation depends on `IQuestFactSource`, never on a store; the Server binds sources to stores.
- No second quest catalog, no second reward path, no counter engine (achievements stay achievement-title's).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Quests/NarrativeQuestProgress.cs','src/FusionRpg.Server/Narrative/QuestLifecycle.cs','tests/FusionRpg.Core.Tests/Narrative/Quests/NarrativeQuestProgressTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Quests|FullyQualifiedName~Delve.Quests"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~QuestLifecycle"
python scripts\audit-magic-numbers.py --domain narrative
```

## Structure

```
src/FusionRpg.Core/Narrative/Quests/IQuestFactSource.cs          (new: interface, QuestFact, QuestWindow)
src/FusionRpg.Core/Narrative/Quests/NarrativeQuestProgress.cs    (new: six templates, pure)
src/FusionRpg.Core/Narrative/Quests/QuestObjectiveRegistry.cs    (new: loader + lawn-only refusal)
src/FusionRpg.Core/Narrative/Quests/QuestRewardSource.cs         (new: host -> source kind/id, QuestReward window reuse)
src/FusionRpg.Core/Narrative/Quests/QuestAchievementEvidence.cs  (new)
gk-core/src/FusionRpg.Core/Delve/Quests/QuestProgress.cs                 (unchanged; wrapped by DelveReportSource)
src/FusionRpg.Server/Narrative/QuestSources/*.cs                 (new: Battle, WorldTurn, Expedition, Delve, Story, Pvz sources over RpgStore reads)
src/FusionRpg.Server/Narrative/QuestLifecycle.cs                 (new: Settle, Abandon)
data/seed/narrative/_registry/quest-objectives.v1.json           (new)
tests/FusionRpg.Core.Tests/Narrative/Quests/NarrativeQuestProgressTests.cs   (new)
tests/FusionRpg.Core.Tests/Narrative/Quests/QuestObjectiveRegistryTests.cs   (new)
tests/FusionRpg.Server.Tests/Narrative/QuestLifecycleTests.cs                (new; in-memory store)
```

## Testing strategy

All with the game closed; stores in memory (`DataTestStore.Create()`, as `spec-story-ledger.md` Testing).

- **Mode-agnostic count:** a `defeat-creatures` quest over a fixture expedition battle report and a fixture world
  battle report counts both; the same objective filled by fixture `pvz` facts alone also completes only because a
  standalone source *could* have filled it — and the registry test proves every template has a non-`pvz` source.
- **Lawn-only refused:** a registry row `{sources: [pvz]}` fails load with `quest.objective-lawn-only`.
- **Pure and total:** evaluating the same facts twice, and in reversed order, gives the same verdict; a duplicate
  fact (same source and durable id) counts once.
- **Window:** facts before `OfferedAtSeq`/`OfferedAtTurn` never count.
- **Retention:** a no-expiry world quest keeps its `have` after the fixture trims report bodies past the hot tail
  (the count comes from `quest.progressed` facts); capturing the same turn twice adds nothing.
- **Expiry on host clock:** a world quest settles `expired` at `offeredAt + expiry` turns and not before; advancing
  wall time with no turn changes nothing (the settlement takes no time input).
- **Dormant pauses, fall fails (round 4):** a world quest in a fixture world that hibernates, catches up `n` coarse
  turns and reactivates has the same `Remaining` as before it slept; a fixture world that falls closes every open
  world quest with one `quest.failed {cause: world-fallen}` and writes no other cost.
- **Completion beats expiry on the same settlement** (both orders of arrival tested).
- **Free abandon:** abandon writes exactly one fact; no relation fact, no soul or material change, no cooldown write.
- **Reward dedupe:** settling a completed quest twice produces one `reward.owed` fact and at most one minted roll; the
  source kind is in `DropTableValidator.KnownSourceKinds`.
- **Out of the budget (Owner ruling 2026-09-20):** a completed world quest in a fixture turn with no claim line stays
  owed and mints nothing; the next turn with a line pays it and that line's claim mint pays nothing.
- **Delve parity:** existing `gk-core/tests/FusionRpg.Core.Tests/Delve/Quests/` pass unchanged; a mirrored Delve verdict
  produces one `quest.completed` fact.
- **Evidence mapping:** a `quest.completed` fact maps to evidence with `FactId = seq` and a `T` naming the quest.
- **No population:** fixtures only; no test counts the committed quest corpus.

## Success criteria

1. One quest engine; the Delve evaluator is one source among six (`battle`, `world-turn`, `expedition`, `delve`,
`story`, `pvz`). 2. No objective is completable only on the lawn,
enforced by the registry loader and a test. 3. Narrative quests are ledger facts; expiry on host clocks; abandon is
free. 4. Rewards are one window-roll taken out of the host's existing budget line, never added, deduped by durable ids
(Owner ruling 2026-09-20). 5. Completion is
achievement evidence without a counter engine here. (G3's quest half.)

## Boundaries

- **Always:** read durable records only; recompute verdicts; dedupe facts and rewards by durable ids.
- **Ask first:** a souls reward for a quest (a new faucet on the soul economy); a new loot source kind; an open-quest
  limit.
- **Never:** a lawn-only objective; a real-time timer; a stored progress counter; wiring the Delve's offer at
  `CreateDelve` (`delve-live-start`'s, Owner ruling 2026-09-19 (round 3); formerly party-dungeon's D4.14); enqueueing
  into the achievement evaluator from here.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `QuestLifecycle.Offer(playerId, questRow, host, sourceRef)` | `outcome-routing` (`quest.offer`) |
| `QuestLifecycle.Settle(...)` | `world-events-host` (End Turn commit), `expedition-lead-host` (collect), `sanctum-hub-host` (entry) |
| `QuestLifecycle.Abandon(playerId, questSubject)` | the quest-log route (`quest-log-contract`) |
| `NarrativeQuestProgress.Evaluate` → verdict (have/need/done) | `quest-log-contract` |
| `QuestRewardSource.Request(...)` → `QuestRewardRequest` | `outcome-routing` (rolls it) |
| `QuestAchievementEvidence.From` | achievement-title (`achievement-evaluator`) |

## Contradictions found (report; not fixed here)

1. **No seed contract for narrative quests.** Map row 14 (`:219`) and ideal §6.5 assume world and expedition quests
   exist as content; narrative-seed's four seed schemas are storylet, character, arc and spine chapter
   (`narrative-seed-map.md:209`, module `narrative-contract`) — no quest anchor, and the objective registry above has
   no owner there. Filed on narrative-seed: add a narrative quest anchor (the `QuestRow` shape with `save`/`world`
   scopes) and the `quest-objectives` registry to `narrative-contract` / `storylet-vocab`. Until then quests are
   authored under the authored path. Reconciled 2026-09-19: `narrative-seed-map.md` §4 now carries a proposed
   model-free module `quest-vocab` (Wave 2) for both artifacts, pending the owner's approval of that map amendment.
   **Resolved — Owner ruling 2026-09-19 (round 3):** `quest-vocab` is approved (map row 23, Wave 2) and specced at
   `narrative-seed/spec-quest-vocab.md`; the authored path remains legal but is no longer the only source.
2. **Scope vocabulary.** `QuestCatalog` refuses any scope outside `delve/domain/roster`
   (`QuestCatalog.cs:155-157`, message text). The scope list is a parameter, so accepting `save`/`world` needs no
   code change in the catalog — only the caller's list and that refusal message, which names the three scopes
   literally. **Corrected — Owner ruling 2026-09-19 (round 3):** `spec-quest-vocab.md` Contradictions 1 found two
   more hard-coded rules — the target-ref kinds (`QuestCatalog.cs:120`) and the count-less literal (`:57-61`) —
   so widening needs the three changes its §1 lists, all made here; still one catalog.

## Open questions

None for the owner. Expiry starting values are decided by principle above.

## Design-gate checklist

```
[x] Subsystems: quests (Delve engine, reader), economy (rewards taken out of host budget lines — Owner ruling 2026-09-20), achievements (evidence only),
    world turn log, expeditions, battle reports, lawn activity (enrichment only), story ledger.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map (full); ideal §0, §6.5, §6.9, §11 items 1 and 5; DESIGN-GATE §1 Economy and Standalone rows;
    empire-resource-ssot.md §3-§4; economy-principles.md P1; sibling specs story-ledger, narrative-vocabulary;
    code: QuestProgress, QuestRow, QuestCatalog, QuestOffer, QuestReward, QuestDto, RpgStore.Delve quest block,
    LootPipeline correlation, DropTableValidator, AchievementRegistry, AchievementEvaluator, Program.cs, BattleModels,
    RpgStore.WorldTurns DDL, ExpeditionResolver, PvzActivityKinds.
[x] decisions.md Standalone-first row (map :80-82) enforced structurally (§3.1).
[x] Every claim cites file:line.
[x] No population pinned; the objective template list is a declared closed vocabulary.
[x] No cache; verdicts recompute.
[x] Order independence stated and tested (fact order, completion vs expiry).
[x] Actor numbers: none.
[x] No parallel path: one catalog, one evaluator shape, one reward path.
[x] Registry row: the lawn-only refusal guards map success criterion "no objective template reads a lawn-only
    fact"; row `ns-quest-no-lawn-only-objective` → QuestObjectiveRegistryTests in gk-core/scripts/enforcement-registry.v1.json.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (Economy, Standalone, World map rows), §2 (1, 2, 9, 12, 13, 15),
§3, §5; `economy-principles.md` P1, P13, P14; `validation-ssot.md`; the-loops.md three clocks; ideal §6.5, §11 items 1
and 5; `narrative-seed/spec-quest-vocab.md` (one quest engine — widen `QuestCatalog`); round-3 and round-4 rulings.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | HIGH | Round-4 ruling: world quests in dormant and fallen worlds were unstated beyond the fall's `quest.failed` | **Fixed** (§4 table): dormant pauses, fallen fails-by-fall, nothing deleted |
| 2 | HIGH | **Coarse catch-up would expire quests.** world-continuity's `coarse-step` advances a dormant world `n` turns at once; counted on the plain `world.turn` clock, a paused quest would expire the moment the player returned — the opposite of "pause" | **Fixed** (§4): expiry and `hold-sector` streaks count full-step committed turns only; test added |
| 3 | HIGH | **Quest rewards are on top of the host's payout**, while the Objective and anchors said "the host's own existing loot source" as if drawn from a budget (ideal §11 item 1). The P1 sink was named; the budget claim was not true for world, expedition or sanctum hosts | **Resolved — Owner ruling 2026-09-20:** rewards are taken out of the host's budget line (§6, `spec-outcome-routing.md` §3) |
| 4 | MEDIUM | Sanctum reward source "highest collected tier" is undefined for a save with no collected expedition | **Fixed** (§6): no roll, quest still completes |
| 5 | LOW | "none of §3's six" / "one source among six" miscounted: §3 lists eight templates and six sources | **Fixed** |
| 6 | LOW | Ideal line citations drifted | **Fixed**: cited by section |

Checked and holding: one quest engine (`QuestCatalog` widened per `spec-quest-vocab.md` §1, no second catalog);
mode-agnostic objectives with the structural lawn-only refusal (standalone-first); verdicts recomputed, no stored
counter; host clocks only; free abandon; dedupe by durable ids (P14); no population pinned.

**Registry row** `ns-quest-no-lawn-only-objective` (already proposed in the checklist) stands. **Boundary ask:**
`src/FusionRpg.Core/Narrative/Quests/**` → `FusionRpg.Core.Tests` `Narrative.Quests`; `src/FusionRpg.Server/Narrative/QuestSources/**`
and `QuestLifecycle.cs` (new) → `FusionRpg.Server.Tests` `QuestLifecycle`.

## Cross-lane alignment (2026-09-20)

- Alignment 2026-09-20: the anchor → `QuestRow` field mapping is cited from `narrative-seed/spec-quest-vocab.md` §3.1
  (the seed owns its shape; this module loads it).
- Owner ruling 2026-09-20 (rewards come out of the host budget): §6 now takes one existing roll of the offering host's
  budget line instead of adding one; the on-top faucet paragraph and the deferred economy decision (audit #3) are
  closed. P14 dedupe keys are kept (the owed fact's subject; the taken roll's own correlation).

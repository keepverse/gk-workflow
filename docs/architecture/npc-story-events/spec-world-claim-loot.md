# Spec: world-claim-loot

Status: **DRAFT for owner review, 2026-09-20. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Owner ruling 2026-09-20 (round 5): **R17 — world claim loot is pulled into npc-story-events.** Module
`world-claim-loot`, row 30 of the [npc-story-events map](../npc-story-events-map.md), wave 1. A **prerequisite** of
`world-events-host` (row 18) and `petition-host` (row 19): R14 (`npc-story-events-ideal.md` §10) says a narrative
reward comes out of the host's existing budget, the world host's budget line is the claim loot a committed End Turn
already makes (`spec-outcome-routing.md` §3), and today nothing mints that loot. **Reviewed with world-map-program**,
which owns the turn engine, `CommitWorldTurn` and `RulesetVersion`, and with the item program, which owns the loot
pipeline (no rule of either changes here). Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

**Transfer (text only; no world-map file is edited by this spec).** Part A of world-map-runtime's
`sector-loot-wiring` — *"`LootPipeline.Resolve(request, view, ...)` exactly as party-dungeon's own
`DelveLoot.RollRoom` does it"* after a claim (`docs/architecture/world-map-runtime/spec-sector-loot-wiring.md`,
§Design Part A) — moves to this module. Its Part B (one drop table per sector type) is shipped
(`gk-data/packs/fusion/data/seed/loot/tables-sector-types.v1.json`, one `drop.world.sector-clear.{type}` table per non-home type) and
stays world-map's. The world-map side records the transfer in its own change.

## Objective

When the player's legion claims a sector, mint that claim's loot **once**, through the **existing** loot pipeline,
deterministically, inside the End Turn commit — so the world has a real budget line that storylet and quest rewards
can then take a roll from, never add one to.

Success looks like: with the game closed, a fixture world where the player claims a band-3 `rich` sector commits a turn
whose report carries `claim.loot:drop.world.sector-clear.rich`, and the same transaction writes one `item_drop_log`
row and its items for that claim; re-committing or replaying the turn mints nothing more; a claim on band-0 ground
mints nothing; an AI faction's claim mints nothing; the state hash is the one the turn had before this module.

## Locked anchors

- **The claim seam exists and is inert.** `ClaimResolver.Run` resolves a `LootSourceRow` through
  `WorldSectorLootSource.TryResolve` and writes a `claim.loot:{tableId}` report line **only when `powerTuning` is
  supplied**, and never mints (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:17-27`, `:124-135`). The claim
  itself is the `claim.held:{sectorId}` entry (`:122`), in the `Snapshot` phase (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:206`, `:419`).
- **Nothing passes `powerTuning` in production.** `CommitWorldTurn` calls `TurnEngine.Step(world, commands,
  header.Seed, battles)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601`) and the replay path calls it the same
  way (`:773`); `Step`'s `powerTuning` defaults to null (`TurnEngine.cs:168-170`). So the world's budget line is empty
  twice over: no `claim.loot:` line is written, and nothing reads one.
- **One loot pipeline.** `LootPipeline.Resolve` is the twelve-step roller: correlation derived server-side, idempotency
  gate on `(player_id, correlation_id)`, seed sealed from the source seed, item level from content level, drop table,
  volume, draws, mint at step 9 through `Instantiator.TryInstantiate` (`gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs:170-238`).
  The mint delegate is `LootMintAt.Mint` (`gk-core/src/FusionRpg.Core/Items/Drops/LootMintAt.cs:65-90`), composed on the store's
  transaction by `MintGrantUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Mint.cs:42`). Persistence is one transaction:
  `PersistLootUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs:596`), ownership `AcquireItemUnlocked`
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:308`), backed by `UNIQUE(player_id, correlation_id)` (`RpgStore.Loot.cs:126`).
- **The composition precedent** is the Delve's quest-reward banking inside `CloseDelve`'s transaction:
  `ApplyQuestRewardBankingUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:650`) builds the request, closes
  `MintGrantUnlocked` over Θ, calls the Core roller, acquires each minted instance and persists the manifest, all on
  one `(db, tx)`, reading the recorded manifest through `RecordedLootManifestUnlocked` (`:718`).
- **Post-Step passes in the commit transaction** are the shipped place for Data-side work a turn triggers: the relic
  spend, the cargo pass and retrieval missions run after `Step`, in the same transaction, before the log insert
  (`RpgStore.WorldTurns.cs:609-628`).
- **Content level of a sector** is the owner-decided `world-sector` row, `mapLevel(M) = Wm · DangerBand(M)`
  (`PowerIndexComposer.MapLevel`, `gk-core/src/FusionRpg.Core/Power/PowerIndexComposer.cs:97`), which
  `WorldSectorLootSource` already uses, refusing band 0 by name (`drop.sector-band-safe`,
  `gk-core/src/FusionRpg.Core/Items/Drops/WorldSectorLootSource.cs:65-91`).
- **Rolls**: `WorldSeed.DeriveRollSeed(worldSeed, streamName, targetId)` (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24-30`)
  with a named stream (map principle 12).
- **Report text is not hashed**: `TurnEngine.Step` returns `StateHasher.Hash(next)` over state only
  (`TurnEngine.cs:209`; the same point is recorded at `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:74`).
- **Economy**: *"Every faucet added must name the sink that absorbs it, in the same change"*
  (`economy-principles.md` P1); every mutation carries a dedupe key from a durable fact id (P14);
  `empire-resource-ssot.md` §4 rule 2.

## Design

### 1. Where it runs

The mint is Data-side work triggered by a committed turn, so it is a **post-Step pass in `CommitWorldTurn`'s
transaction** — the cargo precedent — never a phase inside the pure engine (the engine cannot touch the store, and
`ClaimResolver`'s own comment says why: minting needs DB-backed idempotency, `ClaimResolver.cs:22-27`).

1. **Turn the seam on.** `CommitWorldTurn` and the replay path pass `PowerTuningHub.Tuning`
   (`gk-core/src/FusionRpg.Core/Power/PowerTuningHub.cs:15`) as `Step`'s `powerTuning`, so `ClaimResolver` writes its
   `claim.loot:` lines. `mythicClaimBonusRatePerMillion` stays null (no production caller passes it): nothing mints a
   `claim.mythic:` line, and turning the bonus on is not part of any ruling. ~~Its roll is seeded from the turn number
   alone … Filed on world-map-program; not turned on here.~~ Owner ruling 2026-09-20 (round 6): **R22** — this module fixes that seed
   (§7), so the bonus is deterministic per world the day it is turned on.
2. **`ClaimLootPass.RunUnlocked(db, tx, worldId, header, result.Report, result.World, thetaActorFor)`** (new, Data),
   placed after the cargo pass and after `world-events-host`'s `NarrativeWorldPass` once that lands, and before the
   log insert. Order is the R14 rule: **the narrative settle pass takes lines first**, then this pass mints every line
   still unused (`spec-outcome-routing.md` §3 "Pairing order").

Record then drain: the claim is a fact the turn already recorded; the mint reacts to it in the same commit. Nothing
reads PvZ, and nothing here runs mid-match.

### 2. Which lines mint

For each `TurnReportKinds.Event` entry whose `Detail` starts with `claim.loot:`, in report entry order:

- **The durable claim fact** is the `claim.held:{sectorId}` entry with the same `Subject` (the claim command id) and
  `SectorId` in the same committed turn (`ClaimResolver.cs:122`, `:132-133`). A line without its `claim.held` entry
  is refused (`claim-loot.no-claim-fact`) and logged; it cannot occur from shipped code.
- **Only the player's claims mint.** The command's commander must be a faction of kind `WorldFactionKind.Player`
  (`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:10`, `WorldFaction.Kind` at `gk-core/src/FusionRpg.Core/World/WorldState.cs:73`);
  the loot belongs to the world's player (`header.PlayerId`). An AI claim writes its line and mints nothing — the AI
  has no inventory.
- **Once per sector per world.** The source id is **`{worldId}:{sectorId}`**, so the correlation is
  `loot:sector:{worldId}:{sectorId}` (`LootCorrelation.Derive("world-sector", …)`, `LootPipeline.cs:139`). Two
  reasons, both principled: (a) sector ids are template ids reused by every world built from a template
  (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:90-153`), so the shipped bare-sector key would make the second
  world's claim replay the first world's manifest and mint nothing; (b) a reclaim of ground the player lost is the
  same ground with its guards already cleared (a claim needs every guard `Cleared`, `ClaimResolver.cs:88-93`), so
  paying again would make a lose-and-retake cycle a free faucet (`economy-principles.md` P10, the greedy play must not
  be the safe play). The first `claim.held` of a sector by the player in a world is the claim fact that pays; a later
  claim's line exists but its correlation already holds a manifest, so it is **used** and mints nothing. Siege loot
  keeps its own turn-qualified shape (`gk-core/src/FusionRpg.Core/World/Turn/SiegeLoot.cs:26-29`): a won district assault is
  a new fight each time; a reclaim of cleared ground is not.

The pass re-resolves the source with the world-qualified id:
`WorldSectorLootSource.TryResolve($"{worldId}:{sectorId}", sector.DangerBand, sector.TypeId, power, out source)` — the
function takes the id as a string and never parses it (`WorldSectorLootSource.cs:65-89`), so no item-program code
changes. The table id must equal the line's `claim.loot:` suffix; a mismatch is refused
(`claim-loot.table-mismatch`), because both come from the same `TableIdFor(sector.TypeId)`.

### 3. The roll — the existing pipeline, never a second roller

```text
sourceSeed = unchecked((ulong) WorldSeed.DeriveRollSeed((long) header.Seed, "loot:world-claim", "{worldId}:{sectorId}"))
request    = LootRequest(playerId, "world-sector", "{worldId}:{sectorId}", sourceSeed,
                         thetaActor: thetaActorFor(playerId), catalogRevision, dropTableRevision)
view'      = view with { Sources = { [source.Key] = source },
                         Mint = grant => MintGrantUnlocked(db, tx, grant, source.ContentLevel, …) }
LootPipeline.Resolve(request, view', drops, pity, out manifest)
foreach minted grant: AcquireItemUnlocked(db, tx, { OriginKind = "world-claim", OriginRef = source.SourceId })
PersistLootUnlocked(db, tx, playerId, manifest, "world-sector", source.SourceId, …)
pity = manifest.PityOut        # chained across lines in the same turn, as ApplyQuestRewardBankingUnlocked does
```

- **Deterministic.** The source seed is `WorldSeed.DeriveRollSeed` on a named stream (`loot:world-claim`) and the
  sector's world-qualified id; the pipeline seals the loot seed from it and the correlation (`LootPipeline.cs:238`).
  No `System.Random`, no clock. The same world seed, command log and tables reproduce the same manifest.
- **Magnitudes read `P(Θ_content)`.** Content level is `source.ContentLevel` = `mapLevel(DangerBand)`
  (`WorldSectorLootSource.cs:81`), the owner-decided world-sector row; the mint closes over it, as `DelveLoot`
  closes over the room Θ (`gk-core/src/FusionRpg.Core/Delve/Loot/DelveLoot.cs:100`). This equals
  `HostContentTheta.ForSector` (`spec-host-content-theta.md` §3) whenever the world's parent terms are absent — every
  world today — and the two are pinned together by the shipped `Map_level_agrees_with_the_content_axis_it_mirrors`
  (`PowerIndexComposer.cs:90-93`). Whether claim loot should later read the full four-axis `Θ_content` is
  `ssot-power-scale.md`'s call, not this module's; no private `f(level)` is written here.
- **Volume reads `Θ_actor`.** Step 5a's `ThetaActor` comes from a delegate `CommitWorldTurn` takes, the way it already
  takes `policies` (`RpgStore.WorldTurns.cs:493-495`): the server passes its `IPowerIndexProvider.ActorIndex` for the
  player (`gk-core/src/FusionRpg.Core/Power/IPowerIndexProvider.cs:15`), so Data never references Server. A null delegate
  (tests, tools) is `Θ_actor = 0`, the pipeline's documented floor, never a guessed value.
- **Refusals are not errors.** A pipeline refusal (a disabled table, an item-level band that excludes the roll) is
  logged with its rule id and leaves the line **unused**; the turn commits. Band 0 never gets here: `ClaimResolver`
  writes no line on safe ground (`ClaimResolver.cs:134-135`).

### 4. Idempotency and replay

- **Commit retry.** The turn barrier refuses a second commit of the same turn (`RpgStore.WorldTurns.cs:514-515`,
  `expectedTurn`), and a retried mint of the same correlation returns the recorded manifest and mints nothing (the
  pipeline's step 1, `LootPipeline.cs:217-225`, and the `UNIQUE` index under it).
- **Replay** re-steps from the command log (`RpgStore.WorldTurns.cs:769-777`) and **never mints**: it is a read path.
  It passes the same `PowerTuningHub.Tuning` so a re-derived report carries the same `claim.loot:` lines the stored
  one did. The mint's own record is the `item_drop_log` row, which the report hot-tail trim never touches.
- **State hash.** Turning the seam on adds report lines only; `StateHasher.Hash` covers state, not the report
  (`TurnEngine.cs:209`). World goldens that compare the state hash stay byte-identical; a golden that stores report
  text and includes a player claim on danger ≥ 1 gains the line. This spec **proposes no `RulesetVersion` bump**
  (the version rule is about what a command log produces as state, `TurnEngine.cs:96-124`); whether one lands, and
  any report golden re-bless, is world-map-program's call in this module's build change.

### 5. Economy — the faucet names its sinks

This module adds a faucet: item drops from claims. Each claim pays **once per sector per world** (§2), so the faucet
is bounded by the ground a world has, not by turns held — it is not territorial income, so P2's upkeep rule is not
triggered (loam upkeep already prices holding ground, `empire-resource-ssot.md` §3 `loam` row). Its yield is the
per-type tables' existing calibration (`gk-data/packs/fusion/data/seed/loot/tables-sector-types.v1.json`; the 1.50-yield history at
`WorldSectorLootSource.cs:39-43`). **Sinks named in this change** (P1), each an existing path:

| What a claim drops | Sink | Evidence |
|---|---|---|
| Equipment | salvage into materials (`TrySalvageItem`), whose materials are spent by crafting and fusion | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Workbench.cs:310`; `empire-resource-ssot.md` §3 rows `essence.{element}`, `shard.{rung}`, `substrate`, `catalyst` |
| Materials | crafting body, direction, rarity ceiling; fusion; catalyst enhance/reroll | `empire-resource-ssot.md` §3, same rows |
| Relics | wonder build cost | `empire-resource-ssot.md` §3 `relic` row |

No new stock, no new source kind (`world-sector` is already in `DropTableValidator.KnownSourceKinds`,
`WorldSectorLootSource.cs:36-37`), no soul award. **R14 then reshapes, never adds:** a world storylet payout or world
quest reward takes one of these lines instead of the claim (§6), so narrative content changes what a claim pays, not
how much the world pays. P1's instrumentation is the existing `item_drop_log` inflow record
(`gk-core/data/tuning/item-drop-volume.v1.json`'s trim note).

### 6. How story rewards take a line (R14)

This module exposes the one mint the narrative pass uses, so a narrative payout and a claim mint are the **same
roll path**:

```csharp
namespace FusionRpg.Data.Sqlite;   // internal to the store, called by NarrativeWorldPass through the commit's delegate
internal ClaimLootLine[] UnusedClaimLootLinesUnlocked(db, tx, worldId, turn, report, world);   // §2's list, minus used
internal LootManifest? MintClaimLootLineUnlocked(db, tx, ClaimLootLine line, QuestRewardWindow? window, int thetaActor);
```

`window == null` is the claim's own roll (§3). `window != null` is a narrative payout taking the line: the same
source, seed and correlation, with the payout's `dropBand`/`rewardBand` window composed on the table the way
`DelveLoot.RollQuestReward` composes a quest window (`RarityShift.ApplyWindow`, `DelveLoot.cs:156-160`). Because the
correlation is the claim's, the claim pass that runs after it finds a recorded manifest and mints nothing: **one
line, one roll, whichever consumer takes it**. `spec-outcome-routing.md` §3 (the `reward.owed` / `reward.paid` queue,
pairing order) and `spec-world-events-host.md` §6 read these two members; nothing else in narrative code mints world
loot.

### 7. The mythic claim bonus seed — Owner ruling 2026-09-20 (round 6): R22

**Today.** `ClaimResolver.Run` rolls the independent mythic bonus as
`RateAuthoring.Hit(mythicEntry, unchecked((ulong)turn), "claim.mythic." + sector.SectorId)`
(`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:139-145`; `RateAuthoring.Hit` derives a stream from the seed and
the stream name, `gk-core/src/FusionRpg.Core/Items/Drops/RateAuthoring.cs:21-25`). The seed is the **turn number**: every world
that claims the same template sector id on the same turn rolls the same hit, and the world seed plays no part.

**Fix (this module owns the edit; `ClaimResolver.cs` is a world-map file, reviewed with world-map-program).** The roll
seed becomes

```text
rollSeed = unchecked((ulong) WorldSeed.DeriveRollSeed((long) seed, "claim.mythic", sector.SectorId))
RateAuthoring.Hit(mythicEntry, rollSeed, "claim.mythic." + sector.SectorId)     # stream name unchanged
```

where `seed` is the turn's world seed that `TurnEngine.Step` already receives (`TurnEngine.cs:168-170`, passed as
`header.Seed` at commit, `RpgStore.WorldTurns.cs:601`) and threads to the other phases; `Snapshot` passes it on to
`ClaimResolver.Run` (one parameter added on each, `TurnEngine.cs:411-419`). Named stream `claim.mythic`, target the
sector id: the result is fixed per world and sector, independent of the turn, matching §2's "a sector pays once per
world" rule. `WorldSeed.DeriveRollSeed` is the one hash (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24-30`).

**What changes in stored or golden values — to be measured in the build task, not assumed.** Expected: nothing,
because every production caller passes `mythicClaimBonusRatePerMillion = null` (commit and replay,
`RpgStore.WorldTurns.cs:601`, `:773`), so the roll never runs in a committed world and no stored report holds a
`claim.mythic:` line. The plan proves it with three checks run before and after the edit:

1. the world golden suite (`dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World"`) —
   state hashes and stored reports byte-identical;
2. the existing mechanism test `A_boss_lair_claim_can_roll_an_independent_mythic_bonus_reproducibly`
   (`gk-core/tests/FusionRpg.Core.Tests/World/ClaimTests.cs:167-186`) — it asserts same-seed reproducibility only, so it must
   stay green; if its hit/miss flips, that is expected and it asserts no outcome;
3. a scan of a real server data directory's `rpg_world_turn_log.report_json` for `claim.mythic:` — expected zero
   rows; any row found is reported with its world id before the edit lands.

**New tests:** replay determinism (commit a fixture turn with the rate set, replay it, same `claim.mythic:` lines);
turn independence (the same world seed and sector claimed on turn 3 or turn 9 rolls the same hit); world independence
(over a fixed list of world seeds, the hit pattern for one sector id is not constant — a relation, never a pinned
rate).

## Data shapes

- No table, no column. Loot lands in `item_drop_log`, `item_generation` and `rpg_item` through their existing writers.
- `rpg_item.origin_kind` value `world-claim` (a new value of an existing free-text column, beside `quest-reward`).
- No tuning key: tables and volume are the item program's; the stream name is a structural constant with a comment.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| source seed | `ulong` from `DeriveRollSeed`'s `long`, reinterpreted `unchecked` | reinterpretation, not arithmetic (`WorldSeed.cs:29`) |
| content level, Θ_actor | `int` | `LootSourceRow.ContentLevel` and `LootRequest.ThetaActor` are `int`; a level is an index (`PowerIndexComposer.cs:90-93`) |
| counts in a manifest | `long` | `LootGrant.Count` (`LootPipeline.cs:31-35`) |

## SOLID notes

- **S:** `ClaimResolver` decides that a claim happened and which table; this pass mints; the pipeline rolls.
- **O:** the pass is one more post-Step step beside cargo; no phase, no engine change beyond passing a parameter the
  engine already takes.
- **L:** with no player claim on danger ≥ 1, a turn commits exactly as today.
- **D:** Data depends on the Core roller and a `Θ_actor` delegate, never on Server.
- One roller (`LootPipeline`), one mint (`LootMintAt` → `Instantiator.TryInstantiate`), one persistence path. The
  narrative pass reuses §6's mint; it never builds a second.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','src/FusionRpg.Data/Sqlite/RpgStore.ClaimLoot.cs','tests/FusionRpg.Data.Tests/World/ClaimLootPassTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ClaimLoot|FullyQualifiedName~WorldTurn"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Turn|FullyQualifiedName~WorldSectorLootSource"
python gk-core/scripts/guard-dal.py
```

The change crosses Data and the world goldens, so the build task runs the full suite once at its end (AGENTS.md
verification boundary, point 2).

## Structure

```
src/FusionRpg.Data/Sqlite/RpgStore.ClaimLoot.cs            (new: ClaimLootPass, UnusedClaimLootLinesUnlocked, MintClaimLootLineUnlocked)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs           (edited: pass PowerTuningHub.Tuning to Step at commit and replay; call the pass; Θ_actor delegate)
gk-core/src/FusionRpg.Server/WorldEndpoints.cs                     (edited: pass the Θ_actor delegate to CommitWorldTurn)
gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs         (edited, R22: mythic roll seed from WorldSeed.DeriveRollSeed)
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs                (edited, R22: Snapshot passes the world seed to ClaimResolver)
gk-core/tests/FusionRpg.Core.Tests/World/ClaimTests.cs             (edited, R22: replay, turn- and world-independence tests)
tests/FusionRpg.Data.Tests/World/ClaimLootPassTests.cs     (new; in-memory store)
```

## Testing strategy

Game closed; fixture worlds; stores in memory (`docs/contributing/testing-standard.md`).

- **Mints once:** a player claim of a band-3 sector writes one `claim.loot:` line and one `item_drop_log` row with
  correlation `loot:sector:{worldId}:{sectorId}`; its items are owned by the player with origin `world-claim`.
- **Deterministic:** two stores committing the same world seed and command log produce identical manifests.
- **Idempotent:** re-running the pass for a committed turn mints nothing; a replay of the turn mints nothing and
  re-derives the same `claim.loot:` line.
- **Once per sector per world:** lose and retake the sector — the second claim's line exists and mints nothing. Two
  worlds from the same template each mint their own claim of the same sector id.
- **Safe ground and AI:** a band-0 claim writes no line and mints nothing; a `Zomboss`-kind faction's claim writes its
  line and mints nothing.
- **Take-first order (R14):** with a fixture narrative pass that takes one of two lines with a window, the claim pass
  mints only the other, and the item-roll count equals the line count.
- **Hash unchanged:** the world golden suite's state hashes are byte-identical with the seam on; a turn without a
  player claim on danger ≥ 1 stores a byte-identical report.
- **No population:** fixtures only; no manifest size or item count is asserted, only one-row-per-claim and the
  correlation shape (contract).

## Success criteria

1. Every player claim on danger ≥ 1 mints through the one loot pipeline, once per sector per world. 2. The roll is
reproducible from the world seed; commit retries and replays mint nothing. 3. The faucet's sinks are named (§5) and no
stock, source kind or roller is added. 4. The narrative pass can take a line (§6) and total rolls equal claim lines.
5. State hashes unchanged.

## Boundaries

- **Always:** mint post-Step in the commit transaction; derive the correlation from the durable claim fact; read tables
  and volume from the item program's files.
- **Ask first (world-map-program):** passing `powerTuning` into `Step` at commit and replay; the pass's place in
  `CommitWorldTurn`; the `RulesetVersion` question and any report golden re-bless; the `ClaimResolver` seed edit (§7,
  R22); turning on the mythic claim bonus.
- **Ask first (item program):** a change to a `world-sector` table or to the pipeline.
- **Never:** a second roller or mint path; mint inside `TurnEngine`; mint on replay; pay a reclaim; pay an AI faction.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `UnusedClaimLootLinesUnlocked` / `MintClaimLootLineUnlocked` | `world-events-host` (`NarrativeWorldPass`), `petition-host` and world quests through `outcome-routing` §3 |
| `claim.loot:` lines on every committed player claim | `outcome-routing` §3's world budget line; world-stage's reveal surface (filed: `spec-sector-loot-wiring.md` Boundaries asks before building one) |

## Contradictions found (report; not fixed here)

1. **The shipped `world-sector` key collides across worlds.** `WorldSectorLootSource`'s doc says the sector's own id
   must be the key so two sectors never share a loot event (`WorldSectorLootSource.cs:19-26`), but template sector ids
   repeat in every world built from a template (`WorldTemplateCatalog.cs:90-153`). This module passes a
   world-qualified id (§2) without changing the item file; the doc comment's premise ("a sector id is generated per
   world") is filed on the item program.
2. ~~**The mythic claim bonus seed is the turn number** (`ClaimResolver.cs:142`), not `WorldSeed`; filed on
   world-map-program and left off (§1).~~ Owner ruling 2026-09-20 (round 6): resolved by R22 in this module (§7).

## Open questions

None for the owner. Reviews named in Boundaries are world-map-program's and the item program's.

## Design-gate checklist

```
[x] Subsystems: world map turn commit (post-Step pass, reviewed), items (loot pipeline, mint, persistence — reused),
    power (content level), economy (faucet and sinks), narrative budget line (consumer).
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map (full), ideal §6.9, §10 R14, §11 item 1; spec-outcome-routing §3, spec-world-events-host
    §6, spec-sector-loot-wiring (full); empire-resource-ssot §2-§4; economy-principles P1, P2, P14; code:
    ClaimResolver, WorldSectorLootSource, LootPipeline, LootMintAt, SiegeLoot, BattleReporting, TurnEngine (Step,
    Events, Snapshot, Observe), RpgStore.WorldTurns (commit, replay), RpgStore.Delve (quest banking), RpgStore.Mint,
    RpgStore.Loot, RpgStore.Items, WorldSeed, PowerIndexComposer, PowerTuningHub, WorldTemplateCatalog.
[x] Every claim cites file:line.
[x] Goldens: state hash unchanged is a test; the bump and report re-bless are world-map's call, not assumed.
[x] No population pinned.
[x] No cache.
[x] Order: narrative-take before claim-mint is fixed and tested; reveal order is the report's.
[x] Actor numbers: none; Θ_actor is read for volume only.
[x] No parallel path: one roller, one mint, one persistence path.
[ ] Registry row: proposed `ns-world-claim-loot-once` (ClaimLootPassTests) — shared file, not written.
```

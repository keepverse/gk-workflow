# Spec: `relation-facts`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** **Reconciled
2026-09-19** with `exchange` ask E-A7 (one logged step-input record, §3) and `trade-ai` ask T-A7 (the band
through `IWorldView`). Every `file:line` below was opened in this session. Module id `relation-facts`, row 7 of the
[counterparties map](../counterparties-map.md) (wave 2; depends on `diplomacy-facts` and on
`npc-story-events`' `story-ledger` and `relation-ledger`). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) principle 11 (one relation ladder), §7.7 (the
events that move relations), §14b (*"disposition facts that trade reads are world-hashed state, or logged
inputs to the step"*); [npc-story-events-ideal.md](../../npc-story-events-ideal.md) §6.4 (one ladder,
derived from facts, moved by facts, never by time — read, not edited). **Owner decisions 2026-09-19:** the
relation band enters the step as a **per-turn logged input**; `relation-facts` **owns the projection point**
for facts, and `trade-stories`' `trade-fact-source` registers into it. Session record:
`tasks/sessions/trade-network-idea-20260919.json`.

## Objective

Be the bridge between the world engine and the one four-band relation ladder, in both directions:

1. **Out:** after each committed turn, project the turn's diplomatic and trade events into the story
   ledger as relation facts, through **one** commit-time projection point that other fact sources
   register into.
2. **In:** before each turn's step, read the band per faction pair from the ladder and **log it with the
   turn**, so the step reads a replayable input and never the live ledger (P13).

It never stores a relation number and never derives a band itself; `relation-ledger` derives, this
module carries.

Success looks like: breaking a treaty early costs the breaker with its partner and, less, with everyone
who held a treaty with it; steady trade warms a relationship slowly; deleting story-ledger rows after a
turn does not change that turn's replay; a turn with nothing diplomatic in it writes no relation fact.

## Scope and non-goals

**In scope:** the commit-time projection seam and its first projector; the faction relation fact kinds
this program needs (as asks on the vocabulary owner); the per-pair cap on `trade.fulfilled`; the band
snapshot table, its write, its replay read, and its hand-off to `Step` and to the AI fill.

**Non-goals:** the band arithmetic, base bands and per-kind shifts (`npc-story-events`
`relation-ledger`, `narrative-vocabulary`); which bands gate which treaties (`exchange`
`treaty-vocabulary`, `trade-access`); the trade story facts themselves (`trade-stories`
`trade-fact-source`, which registers into the seam); fog rules for story audiences (the registering
projector's).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The four-band registry | `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json` |
| The turn commit resolves Data-side work after `Step`, in the same transaction, after the graph diff and before the log insert | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601-622` |
| The stored hash is recomputed after post-step passes, so the log describes the committed state | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:632-661` |
| The AI fill runs before the barrier, inside the same transaction, and builds each faction's `BelievedWorldView` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:218-245`, `:527` |
| Replay rebuilds from the template and steps each turn's stored commands, refusing on a version mismatch | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:759-776` |
| `Step` already takes optional inputs beyond world, commands and seed | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:157-159` |

### Designed by the sibling program (drafts, read this session, not edited)

| Finding | Evidence |
|---|---|
| The story ledger is one append-only table keyed by save, with a world scope, dedupe on a durable `source_ref`, and `…Unlocked` appends for use inside another transaction | `docs/architecture/npc-story-events/spec-story-ledger.md` §2, §3, §6 |
| A band is derived from relation facts about a **subject** (a character or a faction), summed as whole signed steps and clamped once; no time input | `docs/architecture/npc-story-events/spec-relation-ledger.md` §2 |
| Relation facts are five kinds — `met, helped, refused, betrayed, spared` | `docs/architecture/npc-story-events/spec-narrative-vocabulary.md` §3 |
| Base bands by faction kind are draft tuning: `Clan: wary`, `Rival: hostile`, `Zomboss: hostile`, `Wild: wary` | `docs/architecture/npc-story-events/spec-narrative-vocabulary.md` §4 |
| The read for this program: `RelationReader.FactionBand(playerId, worldId, factionId)` — player-centred | `docs/architecture/npc-story-events/spec-relation-ledger.md` §Interface |

### Real gap

The ledgers are unbuilt (`npc-story-events-map.md` modules 4 and 5). Nothing projects world events into
them; no band reaches the step; no faction relation kind exists for war, treaties or trade; there is no
pair subject for two AI factions.

## Design

### 1. The projection point (owned here)

One commit-time seam for every fact source that turns a committed world turn into story facts:

```csharp
namespace FusionRpg.Core.World.Facts;                 // (new) pure contracts

public sealed record CommittedTurn(
    long PlayerId, string WorldId, int Turn,
    WorldState Before, WorldState After,              // pre-step and post-commit worlds
    IReadOnlyList<TurnReportEntry> Report,            // the stored report, cargo and retrieval entries included
    IReadOnlyList<StockDelta> Deltas);                // trade-foundation stock-deltas (settlements included)

public interface ICommitFactProjector
{
    string ProjectorId { get; }                                   // kebab-case, unique, ordinal order
    IReadOnlyList<StoryFactAppend> Project(CommittedTurn turn);   // pure
}
```

- `CommitFactProjection` (Data) runs every registered projector in `ProjectorId` order **inside the
  commit transaction, after the turn-log insert**, and appends all drafts through the story ledger's
  `AppendStoryFactsUnlocked`. Story facts are not world state, so the pass is hash-neutral.
- `relation-facts` registers the first projector, `relation`. `trade-stories` `trade-fact-source`
  registers `trade-story` into the **same** seam (owner decision): one projection point, not two writers
  of one ledger.
- A projector reads committed records only; it never hooks another module's code (the precedent
  `trade-stories-map.md` §6.2 already states).

### 2. The relation facts this program emits

| Event (source record) | Fact kind (asked of the vocabulary) | Subject pair | Notes |
|---|---|---|---|
| a `war.declared` diplomacy fact appended this turn | `war.declared` | (declarer, target) | |
| a `treaty.broken` diplomacy fact | `treaty.broken` | (breaker, partner) | Includes the one `diplomatic-stance` writes when war is declared inside an active treaty's minimum term (round 6 Q-A, `spec-diplomacy-facts.md` §7a) — this module reads the fact and needs no rule of its own for that case |
| the same, for every faction that held an active treaty with the breaker at the start of the turn | `treaty.break-witnessed` | (breaker, observer) | "less" than the partner's drop, by its own whole-step shift |
| a `treaty.imposed` diplomacy fact | `treaty.imposed` | (imposer, imposed-upon) | |
| settled trade fills between two factions this turn (`exchange` settlement deltas) | `trade.fulfilled` | (buyer, seller) | **at most `relation.tradeFulfilledCapPerPairPerTurn` per pair per turn**, whatever the fill count |
| a capture of a clan sector (`conquest-consequences`' report entry) | `clan.conquered` | (conqueror, every surviving clan) | moves every clan's band with the conqueror toward `hostile` |

- These are faction relation kinds for the one ladder. They are not in the vocabulary today (five
  relation kinds, `spec-narrative-vocabulary.md` §3); adding them — with one `shiftByFactKind` entry each
  — is the vocabulary owner's reviewed change (**ask A7**). The shifts are theirs to tune; this module
  never holds a shift.
- **Whole steps are too coarse for trade.** The ladder sums whole band steps (`spec-relation-ledger.md`
  §2), so one `trade.fulfilled` fact with any non-zero shift moves a full band — the ideal wants *"a small
  positive relation fact"* (§7.7). **Ask A8:** sum per-mille steps and divide once after the sum
  (`net = Σ shiftMilli / 1000`, still order-independent and still one clamp). Until A8 lands,
  `trade.fulfilled`'s shift is tuned to 0: the facts are recorded, and they start to count the day the
  arithmetic can weigh them — a tuning publish, not a code change.
- **Facts only.** No fact is written because turns passed. A turn with no qualifying record writes none.
- **Pairs.** A fact about the player and faction X uses the ledger's existing subject (`faction:X`). A fact
  between two AI factions needs a pair subject the ledger does not have yet (**ask A1**). Until A1 lands,
  AI↔AI events are not projected, and AI↔AI bands read their base band (§4).
- **Dedupe keys** use the story ledger's grammar (`{kind}|{scope}|{world_id}|{subject}|{source_ref}`,
  `spec-story-ledger.md` §3) with these `source_ref`s: `diplomacy:<worldId>:<turn>:<factSeq>` for a
  diplomacy-sourced fact (plus `:<observerId>` for a witness); `settle:<worldId>:<turn>:<pairKey>:<i>` with
  `i < cap` for trade; `conquest:<worldId>:<turn>:<sectorId>:<clanId>`. Re-committing a turn appends
  nothing.

### 3. The band snapshot — a per-turn logged input (owner decision), in the one step-input record

**One channel for logged step inputs** (answers `exchange` ask E-A7, 2026-09-19). The band snapshot is the
first per-turn logged input to `Step`; `exchange` `settlement-payment`'s player soul budget is the second
(`exchange/spec-settlement-payment.md` §1). Two tables, two write sites and two replay reads would be a
parallel path, so this module owns **one** record and each producer registers a section in it:

```sql
CREATE TABLE IF NOT EXISTS rpg_world_step_inputs (        -- (new; owned by this module)
  world_id TEXT NOT NULL, turn INTEGER NOT NULL,
  input_kind TEXT NOT NULL,                               -- closed: 'band' (this module), 'soul-budget' (exchange),
                                                          --         'goods-cover' (empire-goods-sinks)
  input_key TEXT NOT NULL,                                -- band: '<factionA>|<factionB>' (ordinal lower, higher)
  value TEXT NOT NULL,                                    -- band: a disposition registry id; soul-budget: exchange's
  PRIMARY KEY (world_id, turn, input_kind, input_key)
);
```

- `input_kind` is a closed vocabulary this module owns; a producer adds its kind in its own change (a
  reviewed widening). `Step` receives one `StepInputs` value with one typed section per kind, built by one
  Data read; replay passes the same record. A producer never writes another's kind.
- Below, "the snapshot" means the `band` rows of this record.

- **Written** in `CommitWorldTurn` when the barrier fires, **before `Step`**: for every pair of
  non-wild factions, read the band **as of the end of turn N − 1** (ask **A2**: a Data-side read, usable
  inside the commit transaction, that counts only facts whose source turn is ≤ N − 1). A row is written
  only when the band differs from that pair's latest stored row — sparse, like every trade canonical form.
- **Read** by `BandSnapshot.For(worldId, turn, a, b)` = the latest row with `turn ≤ N`; absent → the base
  band (§4). Passed to `TurnEngine.Step` as a new optional input and threaded to `exchange`'s
  `trade-access` and `treaty-lifecycle`, the only readers inside the step.
- **Replay** (`RpgStore.WorldTurns.cs:771-776`) passes each turn's snapshot from the table; it never reads
  the story ledger. Snapshot rows, like commands, are never trimmed: they are part of the replay unit.
- **The AI** reads the same values: the fill passes the A2 read into `BelievedWorldView` as
  `IWorldView.BandWith(factionId)`. Because A2 counts facts only up to turn N − 1, a fill that runs on an
  earlier commit call of the same turn reads exactly what the step will read.
- A legacy world (no `counterparties.stance`) writes no snapshot and passes none; the record carries
  whatever other kinds that world's stamp enables (`soul-budget` is `exchange`'s to gate).

**Round 6 C1 — the gate is wave 2's flag, `counterparties.stance`.** This module and `diplomatic-stance`
are `counterparties` wave 2 (row 16 of [../landing-order.md](../landing-order.md) §2) and share that wave's
single `RulesetVersion` bump. They used to gate on `counterparties.diplomacy`, which wave 1's
`diplomacy-facts` registers — a flag spanning two waves, so a world stamped at wave 1 would have started
writing band snapshots and projecting relation facts mid-life when wave 2 merged (the audit's C1).

### 4. Base bands and the Q1 default

A pair with no relation facts reads `DispositionLadder.Step(base, 0)`. For the player and faction X, the
base is the ledger's `baseBandByFactionKind[X.Kind]`. For two AI factions (until A1 gives the ledger a pair
subject), the base is the **colder** of the two kinds' bases — the side that trusts less decides, so a
missing fact never opens access. Owner decision Q1 puts rival empires and clans at `wary`; the draft
tuning has `Rival: hostile` (**ask A6**). The dominant enemy empire's `hostile` matches Q1's permanent war.

## Tunables

| Key | File | Unit | Starting value |
|---|---|---|---|
| `relation.tradeFulfilledCapPerPairPerTurn` | `data/tuning/diplomacy.v{n}.json` | facts per pair per turn | 1 — a structural pacing limit (a per-turn rate) and commented so where it is enforced; its value is tunable |

The approved map also listed `relation.treatyBrokenObserverShareMilli` and `truceTurns` here. The first
is replaced by the `treaty.break-witnessed` kind with its own whole-step shift (the ladder cannot take a
fraction of a step until A8), and the second is read only by `exchange` `treaty-lifecycle` (a truce blocks
re-signing), so it belongs to that module's keys. The map is corrected.

## Numeric types

No magnitudes. Turn numbers are `int`; the cap and its counters are `int` per pair per turn.

## Acceptance (contract)

1. **Replay never reads the ledger:** deleting every story-ledger row after a turn leaves that turn's
   replay hash unchanged (the snapshot table carries the input).
2. **Idempotent:** re-committing a turn appends no story fact and writes no snapshot row.
3. **Cap:** for any number of fills between a pair in one turn, at most `cap` `trade.fulfilled` facts are
   appended; the cap is read from tuning.
4. **Facts only:** a turn with no qualifying record appends no relation fact; ten empty turns change no
   band.
5. **Witnesses:** a `treaty.broken` produces one `treaty.broken` fact for the partner and one
   `treaty.break-witnessed` fact per faction holding an active treaty with the breaker at turn start, and
   none for anyone else.
6. **One seam:** the relation projector and a test projector registered together append in
   `ProjectorId` order in one transaction; a failure in either rolls back the whole commit.
7. **Hash-neutral:** projecting facts moves no world hash.
8. **Same band, both readers:** for every pair, `IWorldView.BandWith` during the fill equals
   `BandSnapshot.For` in that turn's step.
9. **Sparse:** a snapshot row is written only when a pair's band changes.

No test pins how many facts, pairs or turns a scenario produces.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Facts/RelationFactProjectorTests.cs` (new): event → fact mapping,
  cap, witnesses, dedupe keys, no-event turns.
- `gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs` (extend): projection inside the commit, rollback,
  idempotent re-commit, snapshot write/read, sparse rows, replay after ledger deletion. In memory.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs','tests/FusionRpg.Core.Tests/World/Facts/RelationFactProjectorTests.cs','gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurnCommit|FullyQualifiedName~StoryLedger"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Facts"
python gk-core/scripts/guard-dal.py ; python gk-core/scripts/guard-test-substrate.py
```

Crosses Core and Data and depends on a sibling program's store: the full suite once at module end.

## Hard edges

- **Blocked on a sibling program.** `story-ledger` and `relation-ledger` must exist; A2 must exist before
  the snapshot is written; A7 before any relation fact is appended. The seam (§1) and the snapshot table
  can land first with an empty projector list and a base-band-only snapshot.
- **`Step` signature.** A new optional input; every existing caller keeps compiling, and replay must pass
  the stored snapshot or it would diverge on trade-stamped worlds.

## Dependencies

| Consumes | From |
|---|---|
| `AppendStoryFactsUnlocked`, dedupe grammar | `npc-story-events` `story-ledger` |
| `RelationLedger.Derive`, `DispositionLadder`; A1, A2, A6, A7, A8 | `npc-story-events` `relation-ledger`, `narrative-vocabulary` |
| Diplomacy facts appended this turn | `diplomacy-facts` |
| Settlement delta **kinds**, by registration (audit M1, edge 3) | `trade-foundation` `stock-deltas` — `exchange` `settlement-payment` registers its kinds there in its own wave (row 18). This module reads the kinds it finds and names no exchange module, so the edge no longer points up the build order and the cycle with `spec-settlement-payment.md` is gone. It lands at row 16 with no settlement kinds registered yet and emits no `trade.fulfilled` until there are — which is correct: nothing has settled |
| Clan-capture report entries | `conquest-consequences` |

| Exposes | To |
|---|---|
| `ICommitFactProjector`, `CommitFactProjection` | `trade-stories` `trade-fact-source` (owner decision) |
| `BandSnapshot.For` (step input) | `exchange` `trade-access`, `treaty-lifecycle` |
| `rpg_world_step_inputs` + `StepInputs` (the one logged-step-input record; kinds register) | `exchange` `settlement-payment` (kind `soul-budget`, E-A7); `empire-goods-sinks` (kind `goods-cover`, added by the 2026-09-20 audit — it had drafted a table of its own) |
| `IWorldView.BandWith(factionId)` (the logged band, belief side) | `trade-ai` (T-A7) |
| `IWorldView.BandWith` | `trade-ai` (`deal-valuation`, `ai-treaty-policy`) |

## Contradictions found

1. **Two projectors for one ledger** (map C5): resolved by the owner — this module owns the projection
   point and `trade-fact-source` registers into it (§1).
2. **Relation fact vocabulary.** The ideal's §7.7 events (`war.declared`, `treaty.broken`,
   `trade.fulfilled`, `treaty.imposed`) and the map's `clan.conquered` are not relation kinds in the
   ladder's draft vocabulary (five kinds). Filed as A7 on `narrative-vocabulary`.
3. **Whole-step arithmetic versus "a small positive fact".** Filed as A8; interim shift 0.
4. **Player-centred reads.** `RelationReader.FactionBand(playerId, worldId, factionId)` has no pair form;
   the ideal scores AI-to-AI proposals with the same function (§7.7). Filed as A1 (already on the map).
5. **Rival base band.** Draft tuning `Rival: hostile` versus Q1 `wary`. Filed as A6.
6. **Observer share and truce keys** in the map's tunables: replaced and moved (§Tunables). Corrected in
   the map.

## Open questions

None for the owner. A1, A2, A6, A7 and A8 are asks on `npc-story-events`; each has a stated interim.

## Design-gate checklist

```
[x] Subsystems: world turn commit (Data), turn engine inputs, replay, world AI view, the story ledger
    and relation ladder (a sibling program, consumed).
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus npc-story-events-ideal §6.4 and §6.7,
    spec-story-ledger, spec-relation-ledger, spec-narrative-vocabulary §3-§4, trade-stories-map §6.2 and
    §10.
[x] decisions.md: no lock on relations beyond the Treaties row (:149).
[x] Every factual claim cites file:line; sibling drafts cited by section.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: CommitWorldTurn order (fill, barrier, Step, diff, cargo, re-hash, log),
    replay loop, Step's optional inputs, the registry file.
[x] Surrounding sections read (ideal §6.4 whole; §14b P13 row).
[x] Replay independence is an acceptance test, not a claim.
[x] No §2 invariant contradicted; SQL stays in FusionRpg.Data.
[x] Corrections propagated to the map: tunables, A6-A8, C5 resolution.
[x] No population pinned.
[x] Cache: the snapshot is a logged input, not a cache; it has no invalidation triggers because it is
    written once per turn and never re-read as current state.
[x] Ordering: projectors run in a fixed id order; facts within a projector are order-independent sets
    (dedupe keys carry no ordering).
[x] No actor magnitude (a band grants access, not stats).
[x] No SOLID-violating path: one projection point, one ladder, no stored band.
[ ] Registry row: none proposed.
```

## Audit 2026-09-20

Fixed here: the one step-input record's closed `input_kind` list gains `goods-cover`, so `empire-goods-sinks`
registers into it instead of keeping a second logged-input table (map C17, round-5 X14). Checked and clean:
replay never reads the live ledger (the snapshot is a logged input, not a cache); dedupe keys carry an ordinal
`i < cap` for `trade.fulfilled`, so the cap can exceed 1 without key collisions; facts only, never by the passage
of time; the per-pair cap is a structural per-turn rate commented as such; AI↔AI bands fall back to the colder
base band until ask A1 lands. **Verification boundary:** the `core-world-trade-counterparties` owner boundary
named in `spec-empire-goods-sinks.md` *Audit 2026-09-20* covers `World/Facts/**`; the Data half keeps its owner;
Data tests in memory; the full suite once at module end.

# Spec: story-ledger

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `story-ledger`, row 4 of the [npc-story-events map](../npc-story-events-map.md) (`:210`), wave 1. Depends on
`narrative-vocabulary` (`StoryFactKind`, `StoryScope`, `HostClockKind`). Reads `storylet-contract`'s canonical form
for pins. Consumed by `relation-ledger`, `character-registry`, `narrative-predicates`, `storylet-selection`,
`scene-script-loader` and every wave 3–5 module. Draft decision row **NS3** (`npc-story-events-map.md:401`).
Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

One append-only store of narrative facts with a **save** scope and a **world** scope (ideal §6.7), recording
`(storyletId, revision)` so an in-progress arc resolves against the revision it started on, and absorbing the two
existing precedents — the Delve's persisted event-seen scopes and the onboarding story rows — **behind one store**,
with no third parallel store and no change to story-scene's frozen `rift-prologue` / version `1` contract.

Success looks like: every narrative fact of every place is one row in `rpg_story_fact`; `RecordEventSeen` and
`LoadPersistedEventSeen` keep their signatures and their tests but write and read the ledger; the Rift prologue's
API and row behave exactly as today; a pinned storylet revision is recovered byte-identically after the corpus
moves on.

## Locked anchors

- Two scopes (ideal §6.7): save lives across worlds like souls and roster; world lives as long as its world
  exists. Map locked assumption 9. Owner ruling 2026-09-19 (round 3): a world no longer "dies with the world like
  loam" — under world-continuity it hibernates, and world-scoped state persists through hibernation (§5). Owner
  ruling 2026-09-19 (round 4): world-scoped state is never deleted; `active` is live, `hibernating`/`idle` dormant,
  `fallen` frozen (§5).
- "The ledger generalizes them; it does not add a third parallel store beside them" (ideal §6.7, `:468-469`).
- Revision pinning (ideal §11 item 3, `:676`); ids never reused (`narrative-seed-ideal.md:637`).
- SQL lives only in `FusionRpg.Data` (DESIGN-GATE §2.6); `guard-dal.py`.
- Relations move on facts, never on time (map locked assumption 10, `:159`): the ledger is the only input a
  relation band reads.

## Design

### 1. The two precedents, read against the code

| Precedent | Table and shape | Semantics | What happens to it |
|---|---|---|---|
| Delve event-seen (`per-domain`, `once-per-player`) | `rpg_delve_event_seen(player_id, scope, scope_key, event_id, delve_id)`, PK `(player_id, scope, scope_key, event_id)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:132-140`); first write wins, `ON CONFLICT DO NOTHING` (`:448-452`) | append-only, deduped facts | **Absorbed.** Rows migrate into `rpg_story_fact` as `storylet.seen`; `RecordEventSeen` (`:440`) and `LoadPersistedEventSeen` (`:463`) keep their signatures and become wrappers; the table is dropped after the copy |
| Delve per-delve seen | `rpg_delve_rooms.event_id`, read back by `LoadPerDelveEventSeen` (`RpgStore.Delve.cs:409-415`) | the room's own draw record | **Stays.** It is the room's state, not a narrative fact, and it ends with the delve by design |
| Onboarding story rows | `rpg_onboarding_story(player_id, story_id, version, state, outcome, acknowledged_utc, revision)`, PK `(player_id, story_id, version)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:493-504`); `unseen → acknowledged` with an outcome and a row revision (`RpgStore.Onboarding.cs:141-175`); acknowledgement refuses any id but `rift-prologue` / `1` (`:144-147`) | a mutable lifecycle row, not append-only | **Frozen projection.** Kept exactly for `rift-prologue` / `1` because the web and `/onboarding` route read it (`gk-core/src/FusionRpg.Server/OnboardingEndpoints.cs:34-45`). Every acknowledgement also appends a `scene.acknowledged` fact in the same transaction. Every **other** scene lives in the ledger only |

`RecordEventSeen` and `MarkRoom` have no production caller (`npc-story-events-map.md:180`), so in every real
database `rpg_delve_event_seen` is empty today; the migration copies whatever exists (`delve-live-rooms` — Owner ruling 2026-09-19 (round 3), formerly party-dungeon's D3.9 — may land
first and create rows) and then drops the table in one transaction.

### 2. Tables (owned by `FusionRpg.Data`)

```sql
CREATE TABLE IF NOT EXISTS rpg_story_fact (
  seq               INTEGER PRIMARY KEY AUTOINCREMENT,  -- append order; the only order any read uses
  player_id         INTEGER NOT NULL,                   -- the save
  scope             TEXT    NOT NULL,                   -- 'save' | 'world'
  world_id          TEXT    NOT NULL DEFAULT '',        -- '' for save scope; rpg_worlds.world_id for world scope
  kind              TEXT    NOT NULL,                   -- StoryFactKind wire id (narrative-vocabulary §3)
  subject_kind      TEXT    NOT NULL,                   -- character | faction | storylet | flag | chapter | arc | quest | scene | sector | delve | siege | none
  subject_id        TEXT    NOT NULL DEFAULT '',
  storylet_id       TEXT,                               -- set when a storylet caused the fact
  storylet_revision INTEGER,                            -- the revision it was resolved at
  host_kind         TEXT,                               -- HostKindCatalog id, when a host caused it
  host_clock        INTEGER,                            -- the host clock value at write (turn, room seq, collect seq, return seq)
  source_ref        TEXT    NOT NULL,                   -- durable id of the causing record (§3)
  dedupe_key        TEXT    NOT NULL,                   -- §3
  attrs_json        TEXT    NOT NULL DEFAULT '{}',      -- kind-specific attributes, closed per kind
  created_utc       TEXT    NOT NULL,                   -- audit only; no read decides anything on it
  UNIQUE (player_id, dedupe_key)
);
CREATE INDEX IF NOT EXISTS ix_rpg_story_fact_subject
  ON rpg_story_fact(player_id, scope, world_id, subject_kind, subject_id, seq);
CREATE INDEX IF NOT EXISTS ix_rpg_story_fact_kind
  ON rpg_story_fact(player_id, scope, world_id, kind, seq);

CREATE TABLE IF NOT EXISTS rpg_story_pin (
  player_id      INTEGER NOT NULL,
  scope          TEXT    NOT NULL,
  world_id       TEXT    NOT NULL DEFAULT '',
  pin_key        TEXT    NOT NULL,       -- the arc instance ('arc.<id>#<started seq>')
  storylet_id    TEXT    NOT NULL,
  revision       INTEGER NOT NULL,
  content_sha256 TEXT    NOT NULL,
  content_json   TEXT    NOT NULL,       -- StoryletCanonical.Serialize output (spec-storylet-contract.md §4)
  PRIMARY KEY (player_id, scope, world_id, pin_key, storylet_id)
);
```

- **Append-only.** No `UPDATE` or `DELETE` statement touches `rpg_story_fact`; a guard test scans
  `RpgStore.StoryLedger.cs` for either verb against it. A correction is a new fact.
- **`created_utc` is audit.** Every read orders by `seq`; no derivation reads the wall clock (map principle 12).
- **`attrs_json` is closed per kind:** `storylet.seen` carries `{repeatScope, scopeKey, delveId}`; `choice.picked`
  `{slot, choiceKind, outcomeOrdinal}`; `scene.acknowledged` `{revision, outcome}`; relation facts `{band?}` is
  **not** allowed (a band is derived, never stored). A writer validates its own kind's attribute set.

### 3. Dedupe keys and source refs

The dedupe key is `{kind}|{scope}|{world_id}|{subject_kind}:{subject_id}|{source_ref}`, so a replayed write (a
retried route, a turn resolved twice, a re-imported record) is a no-op, the `AwardSouls` dedupe discipline
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:215`). `source_ref` names the durable record that caused the fact:

| Cause | `source_ref` |
|---|---|
| a Delve room draw (migrated event-seen) | `seen:{repeatScope}:{scopeKey}`, with `delveId` in `attrs` only — this keeps today's "first write wins per `(scope, scope_key, event_id)`, never overwritten" (`RpgStore.Delve.cs:417-439`), because the delve that first saw the event is an attribute, not part of the identity |
| a storylet answer | `answer:{hostKind}:{slotKey}:{hostClock}` |
| a world turn report entry | `turn:{worldId}:{turn}:{entryIndex}` |
| an expedition collect | `expedition:{expeditionId}` |
| a scene acknowledgement | `scene:{sceneId}:{revision}` |
| a world-continuity coarse record (dormant world; Owner ruling 2026-09-19 (round 4)) | `coarse:{worldId}:{coarseSeq}:{entryIndex}` — the only source a `Dormant` world accepts (§5) |

### 4. Pins

When an arc starts (`arc.started` fact), the caller (`storylet-selection`) writes one `rpg_story_pin` row per arc
link with the link's canonical JSON at the current revision. A later link is resolved from its pin, never from the
live catalog, through `StoryletCanonical.Parse` — the same loader and preflight as a live row
(`spec-storylet-contract.md` §4). A pin whose `content_sha256` does not match its `content_json` is a load
refusal. New draws always use the current revision. A tombstoned storylet stays resolvable through its pin.

### 5. Scope and world lifetime

- A world-scoped read is always keyed by `(player_id, world_id)`; no API reads world facts across worlds.
- Save-scoped facts ignore `world_id` (`''`).
- **World lifetime — Owner ruling 2026-09-19 (round 3).** The approved `world-continuity` program replaces "a world
  ends" with two axes on `rpg_worlds` — attention `active | hibernating | idle` and outcome
  `contested | won | fallen` (`world-continuity-map.md` locked assumption 1, module `world-state-vocabulary`).
  World-scoped facts live as long as their world exists. **Owner ruling 2026-09-19 (round 4)** replaces the round-3
  table below it: world-scoped story state is **never deleted** — world-continuity keeps a fallen world revisitable as
  hostile ground and the reserved `world-reclaim` module reads its history (`world-continuity-map.md:117`, `:127`,
  `:274-275`). There is **no "abandoned" state** and no ask on `world-state-vocabulary` for one. The lifecycle is the
  derived `WorldNarrativePhase` (`spec-narrative-vocabulary.md` §3), keyed to world-continuity's states:

  | World-continuity state | `WorldNarrativePhase` | World-scoped facts |
  |---|---|---|
  | attention `active` (outcome `contested` or `won`) | `Live` | read and appended by that world's hosts |
  | attention `hibernating` or `idle` | `Dormant` | kept intact and readable (quest log, history); **not drawn** by any host of this program; **no writes** except the facts world-continuity's `CoarseStep` emits (including `world-event-budget`'s hibernating events) |
  | outcome `fallen` (module `world-fall`) | `Frozen` | **read-only history**; no writer at all; `world-reclaim` may later revive the world, and the facts are there for it |

  "Retire" in this program's specs means **frozen**, never deleted and never rewritten. The ledger is append-only (§2)
  and nothing in this program appends a "retirement" fact at world fall: a frozen world's characters, relations, arcs
  and open quests are read as they stood, marked frozen by the phase (`character-registry` §4, `relation-ledger` §2;
  `quest-sources` owes the same reading for open world quests — outside this audit's fence). Today no code writes any
  state but `'active'` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:32`; the only `UPDATE rpg_worlds` advances the
  turn, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:687-689`), so until `world-state-vocabulary` and
  `world-fall` land every world is `Live`.

  **The write gate (one place).** `AppendStoryFact(s)` reads the world's attention and outcome in the same
  transaction for a `world`-scope append and refuses: any append to a `Frozen` world (`story.world-frozen`), and any
  append to a `Dormant` world whose `source_ref` is not a `CoarseStep` record (`coarse:{worldId}:{coarseSeq}:…`,
  `story.world-dormant`). Save-scope appends are never gated. The phase is derived on each append, never cached, so
  there is no trigger set to keep (DESIGN-GATE §2.16 does not apply).

  *Superseded round-3 table (kept for the trail): live while active/hibernating/idle; "retired" at `fallen` or
  "abandoned", with a retirement pass that retired specimens, appended `character.departed` and closed quests
  `quest.failed`.*

### 6. C# surface

```csharp
namespace FusionRpg.Core.Narrative.Ledger;          // Core: types only, no store

public sealed record StoryFact(
    long Seq, long PlayerId, StoryScope Scope, string WorldId, StoryFactKind Kind,
    string SubjectKind, string SubjectId, string? StoryletId, long? StoryletRevision,
    string? HostKind, long? HostClock, string SourceRef, IReadOnlyDictionary<string, string> Attrs);

public sealed record StoryFactAppend(
    StoryScope Scope, string WorldId, StoryFactKind Kind, string SubjectKind, string SubjectId,
    string? StoryletId, long? StoryletRevision, string? HostKind, long? HostClock,
    string SourceRef, IReadOnlyDictionary<string, string> Attrs);

public sealed record StoryFactQuery(
    StoryScope Scope, string WorldId, StoryFactKind? Kind = null,
    string? SubjectKind = null, string? SubjectId = null, long AfterSeq = 0);
```

```csharp
// FusionRpg.Data — RpgStore.StoryLedger.cs (new)
public (bool Appended, long Seq) AppendStoryFact(long playerId, StoryFactAppend fact);     // dedupe → (false, existing seq)
public IReadOnlyList<(bool Appended, long Seq)> AppendStoryFacts(long playerId, IReadOnlyList<StoryFactAppend> facts); // one transaction
public IReadOnlyList<StoryFact> ListStoryFacts(long playerId, StoryFactQuery query);        // ordered by seq
public bool HasStoryFact(long playerId, StoryFactQuery query);
public void WriteStoryPins(long playerId, StoryScope scope, string worldId, string pinKey, IReadOnlyList<StoryPin> pins);
public StoryPin? GetStoryPin(long playerId, StoryScope scope, string worldId, string pinKey, string storyletId);
// Unlocked variants (…Unlocked(SqliteConnection db, …)) so another store method can append inside its own
// transaction — the MintCreatureUnlocked precedent (gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Creatures.cs:29-31).
```

`RecordEventSeen(playerId, scope, scopeKey, eventId, delveId)` becomes one `AppendStoryFactUnlocked` of kind
`storylet.seen`, scope `save`, subject `storylet:{eventId}`, attrs `{repeatScope: scope, scopeKey, delveId}`.
`LoadPersistedEventSeen(playerId, domainId)` reads `storylet.seen` facts and splits them exactly as today.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `seq` | `long` | an append counter over a save's whole life; SQLite `INTEGER` is 64-bit |
| `host_clock` | `long` | world turns are unbounded (R3: the story never ends) |
| `storylet_revision`, pin `revision` | `long` | matches `EventRow.Revision` (`spec-storylet-contract.md` Numeric types) |
| `player_id` | `long` | the existing `players.id` column type |

## SOLID notes

- **S:** one store for narrative facts. The Delve's persisted event-seen table is absorbed, not duplicated;
  the onboarding table remains only as the frozen projection its approved contract requires, and it writes its
  fact into the ledger so no narrative consumer ever reads it.
- **O:** a new fact kind is a `StoryFactKind` member plus its attribute set; no new table per feature.
- **L:** `RecordEventSeen`/`LoadPersistedEventSeen` keep their exact contract (first write wins, never reset).
- **D:** consumers read `StoryFact` records; no module outside `FusionRpg.Data` sees a table.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs','tests/FusionRpg.Data.Tests/Narrative/StoryLedgerStoreTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~StoryLedger|FullyQualifiedName~EventSeenStore|FullyQualifiedName~Onboarding"
python gk-core/scripts/guard-dal.py ; python gk-core/scripts/guard-test-substrate.py
```

## Structure

```
src/FusionRpg.Core/Narrative/Ledger/StoryFact.cs                    (new)
src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs                   (new: schema, append, query, pins, migration)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs                         (edited: RecordEventSeen/LoadPersistedEventSeen wrap the ledger; table DDL removed)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs                    (edited: ack appends scene.acknowledged in-transaction)
tests/FusionRpg.Data.Tests/Narrative/StoryLedgerStoreTests.cs       (new)
tests/FusionRpg.Data.Tests/Narrative/StoryLedgerMigrationTests.cs   (new)
```

## Testing strategy

All store tests run **in memory** through `DataTestStore.Create()` (`gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs:37-47`);
the migration test uses `DataTestStore.CreateWithPreInitHot` (`:72`) to seed the old table before `Init`.

- **Append and dedupe:** the same append twice returns `(false, firstSeq)`; one row exists.
- **Append-only guard:** no `UPDATE`/`DELETE` against `rpg_story_fact` in the Data source (text scan).
- **Order:** reads return `seq` order regardless of insertion order of independent facts; two facts appended in
  either order produce the same set (order-independent for set-valued reads).
- **Scope isolation:** a world fact for world A is invisible to a query for world B; a save fact is visible from
  any world; a query never returns another player's facts.
- **World lifecycle (Owner ruling 2026-09-19 (round 4)), one test per edge, order-independent:** a world fact
  written while A is `active` reads back unchanged after a fixture moves A to `hibernating`, to `idle`, back to
  `active`, and to outcome `fallen`; no row is ever deleted or rewritten. While A is `hibernating` or `idle`, a
  host-sourced append refuses `story.world-dormant` and a `coarse:`-sourced append succeeds; while A is `fallen`,
  every world-scope append refuses `story.world-frozen`; save-scope appends succeed in every state. Both orders of
  "append then hibernate" and "hibernate then append" are specified.
- **Event-seen parity:** the existing `gk-core/tests/FusionRpg.Data.Tests/Delve/EventSeenStoreTests.cs` passes unchanged
  against the wrapper — first write wins, a second delve does not add a row, `LoadPersistedEventSeen` splits
  `per-domain` by domain and `once-per-player` by `''`.
- **Migration:** pre-seeded `rpg_delve_event_seen` rows reappear as `storylet.seen` facts with equal read results;
  the old table no longer exists; running `Init` twice is idempotent.
- **Frozen Rift contract:** every existing onboarding test passes; acknowledging `rift-prologue` / `1` also yields
  exactly one `scene.acknowledged` fact; a re-acknowledgement adds none; `rpg_onboarding_story` rows are
  byte-identical to the pre-change behaviour.
- **Pins:** write, read back, hash matches; a tampered `content_json` is refused; a tombstoned storylet resolves
  through its pin.
- **No population:** tests assert on the facts they write, never on a count of facts in a seeded corpus.

## Success criteria

1. One narrative fact store; `rpg_delve_event_seen` is gone and its callers are unchanged. 2. The Rift contract
is unchanged and mirrors into the ledger. 3. Every append is deduped by a durable source ref. 4. Pins round-trip
byte-identically. 5. `guard-dal` and `guard-test-substrate` green.

## Boundaries

- **Always:** append-only; dedupe by durable source; order by `seq`; world reads keyed by world id.
- **Ask first:** migrating `rpg_onboarding_story` itself (it is story-scene's frozen contract).
- **Never (Owner ruling 2026-09-19 (round 4)):** delete or rewrite a world's facts at any world-continuity state;
  write a "retirement" fact at world fall; add an "abandoned" state.
- **Never:** store a derived band, number or fate; read the wall clock for a decision; a second narrative table
  for one feature; SQL outside `FusionRpg.Data`.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `AppendStoryFact(s)[Unlocked]`, `ListStoryFacts`, `HasStoryFact` | every module that writes or reads narrative state |
| `WriteStoryPins`, `GetStoryPin` | `storylet-selection` (arc start), `choice-resolution` (later links) |
| `RecordEventSeen`, `LoadPersistedEventSeen` (unchanged signatures) | `delve-live-rooms`' room-entry route (Owner ruling 2026-09-19 (round 3): formerly party-dungeon's D3.9) |
| `scene.acknowledged` facts | `scene-script-loader`, `sanctum-hub-host`, `spine-progress` |

## Contradictions found (report; not fixed here)

1. **"Generalizes the onboarding story rows."** The map (`:210`) and NS3 (`:401`) say the ledger generalizes them.
   The row is a mutable lifecycle with its own revision (`RpgStore.Onboarding.cs:141-175`), not an append-only
   fact, and its contract is frozen. This spec generalizes it by mirroring every acknowledgement into the ledger and
   routing every new scene to the ledger only, rather than migrating the table. NS3's draft text still holds.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: data/SQL, Delve persistence, onboarding story rows (frozen), narrative state.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 4 and NS3; ideal §6.7, §11 item 3; RpgStore.Delve.cs event-seen block;
    RpgStore.Onboarding.cs and its DDL in RpgStore.cs; OnboardingEndpoints.cs; rpg_worlds DDL and its writers.
[x] Every claim cites file:line.
[x] No constraint assumed: the empty-table claim rests on the map's verified no-caller finding.
[x] No cache introduced. No population pinned. No actor number.
[x] No parallel store: one table replaces one; the frozen projection is the only survivor and says why.
[ ] Registry row: the append-only text-scan test is local to Data.Tests; no enforcement-registry row proposed.
    (Audit 2026-09-19: rows proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | Round-4 owner ruling: §5 kept an "abandoned" state with an ask filed on `world-state-vocabulary`, and a "retirement pass" at world fall that retired specimens, appended `character.departed` and closed quests — rewriting history world-continuity keeps for `world-reclaim` | **Fixed:** `Live / Dormant / Frozen` from `WorldNarrativePhase`; no abandoned state; nothing appended or deleted at fall |
| 2 | high | No single place enforced "no writes to a dormant or frozen world" — each host would have re-derived it (a SOLID S/D gap and an untestable rule) | **Fixed:** the append path is the one gate, with `story.world-dormant` / `story.world-frozen` refusals and a per-edge test |
| 3 | low | Map citations one line early (`:209`, `:400`) | **Fixed** |
| 4 | low | Citations sampled against code this audit: `RpgStore.Delve.cs:132-140` (DDL), `RpgStore.Onboarding.cs:144-147` (the rift-only refusal), `RpgStore.World.cs:32`, `RpgStore.WorldTurns.cs:687-689`, `DataTestStore.cs:37-47`, `:72` — all hold | no change |

Checked and clean: SQL only in `FusionRpg.Data` (guard-dal in Commands), store tests in memory
(`DataTestStore.Create`, testing-standard), append-only with a text-scan test, `long` counters, no cache, no
population pin, one store absorbing one (no third parallel store).

**Propagation owed (outside this fence):** `spec-quest-sources.md` §4 still closes open world quests `quest.failed`
at world fall; under round 4 they are frozen, not failed.

**Proposed enforcement-registry rows:** `ns3-story-ledger-append-only` — no `UPDATE`/`DELETE` against
`rpg_story_fact`; guard `tests/FusionRpg.Data.Tests/Narrative/StoryLedgerStoreTests.cs` (text scan).
`ns3-story-sql-in-data` — story-ledger SQL only in `FusionRpg.Data`; guard `gk-core/scripts/guard-dal.py` (existing).
`ns-world-scope-never-deleted` — world-scoped narrative state is frozen, never deleted (round 4); guard: the
append-only scan plus the lifecycle test above. **Verification-boundary ask:** map
`src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs` and `tests/FusionRpg.Data.Tests/Narrative/**` to a focused
`data-narrative` boundary (today they fall to the Data fallback).

# Spec: storylet-reseam

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `storylet-reseam`, row 2 of the [npc-story-events map](../npc-story-events-map.md) (`:208`), wave 1. Depends
on nothing (`:263`: it can land before or after party-dungeon's open event-deck tasks). Consumed by
`storylet-contract` and, through it, every host. Gate **G1** (`:297`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Move the Delve's event engine out of `gk-core/src/FusionRpg.Core/Delve/Events/` into a place-neutral namespace,
`src/FusionRpg.Core/Narrative/Storylets/` (new), behind an `IStoryletHost` seam, **with no behaviour change**.
The Delve keeps its exact behaviour through a Delve host adapter. After this module there is one storylet engine
and the Delve is its first host (NS1, `npc-story-events-map.md:399`).

Success looks like: every event-deck test passes with its assertions and expected values unchanged; the
battle, expedition and world goldens are byte-identical; `grep -r "namespace FusionRpg.Core.Delve.Events" src/`
finds only the Delve host adapter; a guard fails any second `*Deck`/`*Draw` selection type outside the engine
namespace and the adapter.

## Locked anchors

- **One engine, many hosts** (ideal §6.2; map principle 11, `:108-110`). "A place owns its loop, never the
  mechanism" (ideal §6.2 last bullet).
- **Pure move** (map row 2, `:208`): proven by the existing tests and goldens, not by review alone.
- The engine has no production caller today (`npc-story-events-map.md:180`), so moving it cannot change a live
  path; the risk is only to tests and to the concurrent party-dungeon tasks D3.3/D3.5/D3.9, which carry the
  moved code along whichever lands second (`:263`).

## Design

### 1. What is the engine and what is the Delve

Read against the code, the folder holds two different things. The engine is place-neutral apart from four
couplings; the rest is the Delve applying an outcome to its own party.

| File (today, `gk-core/src/FusionRpg.Core/Delve/Events/`) | Goes to | Why |
|---|---|---|
| `EventRow.cs` (records at `:12,17-18,28-37`) | engine | the storylet shape; no Delve type |
| `EventCatalog.cs` (`EventRules` `:8-51`, `Load` `:90-199`) | engine | vocabularies are parameters (`:90-99`); only `Consequences` is local (`:204`) |
| `EventSeedFile.cs` | engine | a JSON reader with no Delve type |
| `EventDeckPreflight.cs` | engine | pure over a catalog; `CheckNoRoomKindIsBoss` takes a caller-resolved ordinal (`:92`) |
| `EventChoices.cs` | engine | the verb set (`:11-13`) |
| `EventDraw.cs` | engine, minus one line | `PickEvent` names its stream with `DelveStreams.Event(row, col)` (`EventDraw.cs:54`) |
| `OutcomeResolver.cs` | engine, minus one line | `PickOutcome` names its stream with `DelveStreams.Event(row, col)` (`OutcomeResolver.cs:114`) |
| `EventEffectContainerBuild.cs` | engine | builds a container from `EventEffectRef`s |
| `EventDeck.cs` | split | `Build`/`PoolFor` and the draw-plus-instantiate core are engine; `Resolve` takes `DelveRoomFact`, `DifficultyRungTuning`, `RoomTheta`, `UnknownPityState`, `DomainAnchor` (`EventDeck.cs:218-233`) and `Answer` takes `DelveMemberState` and `DelveUiPresentSink` (`:339-348`) |
| `EventFilters.cs` | split | the four set filters are engine; `RoomKindToEventKind` (`:16-24`) and `UnknownRoomKind` (`:28`) are Delve |
| `UnknownPity.cs`, `AmbushDraw.cs`, `EventFacts.cs`, `EventOutcomeDispatch.cs`, `DelveResourceDelta.cs`, `DelveUiPresentSink.cs`, `RoomEventPoolSeedFile.cs`, `SupplyOverrideTagSeedFile.cs` | Delve host adapter | Delve room mechanics, party facts and the application of an outcome to Delve party state |

A grep of `DelveStreams`, `DelveMemberState`, `DelveRoomFact`, `DifficultyRungTuning` and `DomainAnchor` inside the
folder finds them only in `EventDeck.cs` (10), `EventOutcomeDispatch.cs` (12), `UnknownPity.cs` (12),
`EventFacts.cs` (3), `AmbushDraw.cs` (2), `EventDraw.cs` (2), `OutcomeResolver.cs` (2) and
`SupplyOverrideTagSeedFile.cs` (1) — which is the table above.

### 2. The seam

```csharp
namespace FusionRpg.Core.Narrative.Storylets;

/// <summary>A place that shows storylets. It decides WHEN to ask; the engine decides WHICH and WHAT.</summary>
public interface IStoryletHost
{
    string HostKind { get; }                     // a HostKindCatalog id (narrative-vocabulary §2)
    HostClockKind Clock { get; }                 // the host's own clock (map principle 4)
    string StreamRoot(string slotKey);           // every engine stream is StreamRoot(slot) + ":pick" / ":outcome" / ":effects"
    bool KindFits(string slotKind, string storyletKind);   // today EventFilters.KindFits for the Delve
}

/// <summary>Everything one draw needs, host-neutral. The Delve adapter builds it from its room.</summary>
public sealed record StoryletDrawContext(
    string SlotKey, string SlotKind, FactReader Facts, EventSeenSets Seen, ulong Seed,
    int SeverityTier, int ThetaContent, string? Climate,
    long ClimateMatchMilli, long ClimateNoneMilli, long ClimateOffMilli,
    IReadOnlyList<string> DropBandOrder, IReadOnlyDictionary<string, int> DropBandWeightTable,
    long CatalogRevision);
```

- **Streams stay byte-identical.** The engine names a stream `host.StreamRoot(slotKey) + ":pick"`. The Delve
  adapter's `StreamRoot` returns `DelveStreams.Event(row, col)` (`gk-core/src/FusionRpg.Core/Delve/Roll/DelveStreams.cs:25`,
  `"dungeon:event:{row}:{col}"`), so every derived seed and every draw is unchanged
  (`SeededRng.DeriveStream`, `gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26`).
- **The engine keeps `EventSeenSets`** (`EventDeck.cs:24-35`) as its seen-state input. Widening the scopes to the
  story ledger is `storylet-selection`'s job, not this move's.
- **Answer splits.** The engine's `StoryletAnswer.Resolve(resolution, choice)` returns
  `(Applied, Instance?)` with the existing `leave` rule (`EventDeck.cs:355-356`) and verb validation
  (`:358-366`). Applying the instance to a party is the host's: `DelveStoryletHost.Answer(...)` keeps
  `EventDeck.Answer`'s exact parameter list and calls `EventOutcomeDispatch.Dispatch` as today (`:368-371`).
- **The old entry points survive on the adapter with their exact signatures.** `DelveStoryletHost.Resolve(...)`
  has `EventDeck.Resolve`'s parameter list (`EventDeck.cs:218-233`), runs `UnknownPity` first exactly as
  `:245-272` does, builds a `StoryletDrawContext` and calls the engine. `DelveStoryletHost.PickEvent(pool, row,
  col, ...)` and `.PickOutcome(outcomes, ..., row, col, seed)` wrap the engine's stream-root overloads.

### 3. Type names do not change

`EventRow`, `EventCatalog`, `EventDeck` and their siblings keep their names; only the namespace moves. A rename
to `Storylet*` would turn a pure move into a diff that touches every consumer for no behaviour, and
`storylet-contract` widens the same types in the next module. The map and the ideal call them storylets; the
code keeps its shipped names.

### 4. External referrers updated in the same change

`grep -rl "FusionRpg.Core.Delve.Events" src/ tests/` outside the folder finds six files:
`gk-core/src/FusionRpg.Core/Delve/Domains/DomainEventPreflightBridge.cs`,
`gk-core/src/FusionRpg.Core/Delve/Quests/QuestArchetypeEventBridge.cs`,
`gk-core/tests/FusionRpg.Core.Tests/Delve/Domains/DomainEventPreflightBridgeTests.cs`,
`gk-core/tests/FusionRpg.Core.Tests/Delve/Domains/DomainQuestPreflightBridgeTests.cs`,
`gk-core/tests/FusionRpg.Core.Tests/Delve/Quests/QuestArchetypeEventBridgeTests.cs` and
`gk-core/tests/FusionRpg.Data.Tests/Delve/Domains/DomainRealPipelineTests.cs`. Each gains a `using` for the engine
namespace; no call changes except where it called a Delve-only overload now on `DelveStoryletHost`.

### 5. What "the tests pass unchanged" means

The map says the existing event-deck tests pass **unchanged** (`:208`, G1 `:297`). The eighteen test files under
`gk-core/tests/FusionRpg.Core.Tests/Delve/Events/` reference types by namespace, so a namespace move must touch their
`using` lines, and tests of `EventDeck.Resolve`/`Answer` must call `DelveStoryletHost.Resolve`/`Answer`. This spec
defines "unchanged" as: **no assertion, expected value, fixture, seed or golden hash changes**; the only edits
are `using` lines, the file's folder, and the type qualifier of the two moved entry points. The build task's
evidence is `git diff -U0 -- tests/` filtered to the lines that are neither a `using` nor that qualifier: it
must be empty. Recorded under Contradictions 1.

### 6. Guard

A guard test, `StoryletEngineSingleSourceTests` (new, `gk-core/tests/FusionRpg.Guard.Tests/`), scans `gk-core/src/FusionRpg.Core/`
for any type whose name ends in `Deck` or `Draw` **and that references a storylet type** (`EventRow`,
`EventCatalog`, `StoryletChoice`) and fails unless it lives in `FusionRpg.Core.Narrative.Storylets` or is on a short
allowlist naming the Delve host adapter's `AmbushDraw` (a Delve rest mechanic built on the engine's draw,
`AmbushDraw.cs:22-30`). The allowlist is closed and each entry carries its reason. Audit 2026-09-19: the name-only
scan this section first specified would fail on landing — `DropTableDraw` (`gk-core/src/FusionRpg.Core/Items/Drops/DropTableModel.cs`),
`RarityDraw` (`gk-core/src/FusionRpg.Core/Items/Drops/LootPity.cs`), `BudgetDraw` and `ResolvedDraw`
(`gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs`, `Resolver.cs`) are loot and atom draws, not storylet selection.
The storylet-type reference is what makes a type a second engine; a name alone is not. This is the
NS1 guard the map's §5 checklist promises (`npc-story-events-map.md:485-487`); its
`gk-core/scripts/enforcement-registry.v1.json` row is added in the same change (invariant id `ns1-one-storylet-engine`,
guard `StoryletEngineSingleSourceTests`).

## Data shapes

No data changes: no seed field, no SQL, no tuning key. The C# surface is §2.

## Numeric types

Unchanged from the moved code: weights `int` narrowed `checked` from `long` per-mille (`EventDraw.cs`,
`WeightMilliFor` and `PickEvent`), `ulong` seeds, `long` roll seeds reinterpreted `unchecked` as today.

## SOLID notes

- **S:** the engine decides which storylet and what it pays; the host decides when and how an outcome lands on
  its own state. Today both live in one folder; after this module they live in two.
- **O:** a new host implements `IStoryletHost`; nothing in the engine changes.
- **L:** the Delve adapter's `Resolve`/`Answer` honour the old contract exactly (same inputs, same outputs, same
  refusals).
- **D:** the engine depends on `IStoryletHost`, never on `DelveStreams` or a Delve type. A reflection test asserts
  that no type in `FusionRpg.Core.Narrative.Storylets` references a type in `FusionRpg.Core.Delve.*`.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Storylets/EventDeck.cs','src/FusionRpg.Core/Delve/StoryletHost/DelveStoryletHost.cs','gk-core/tests/FusionRpg.Core.Tests/Delve/Events/EventDeckTests.cs') -DeletedPaths @('gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Delve.Events|FullyQualifiedName~Narrative.Storylets|FullyQualifiedName~Delve.Domains|FullyQualifiedName~Delve.Quests"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Battle|FullyQualifiedName~Expedition|FullyQualifiedName~World"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Delve"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~StoryletEngineSingleSource"
```

The change crosses Core, Data tests and Guard tests, so the build task also runs the full suite once at its end
(AGENTS.md verification boundary, point 2).

## Structure

```
src/FusionRpg.Core/Narrative/Storylets/                    (new; moved from Delve/Events/)
  EventRow.cs · EventCatalog.cs · EventSeedFile.cs · EventDeckPreflight.cs · EventChoices.cs
  EventDraw.cs · OutcomeResolver.cs · EventEffectContainerBuild.cs · EventFilters.cs (set filters only)
  EventDeck.cs (Build, PoolFor, engine Resolve over StoryletDrawContext) · StoryletAnswer.cs (new)
  IStoryletHost.cs (new) · StoryletDrawContext.cs (new)
src/FusionRpg.Core/Delve/StoryletHost/                     (new; the Delve host adapter)
  DelveStoryletHost.cs (new)   IStoryletHost + the old Resolve/Answer/PickEvent/PickOutcome signatures
  UnknownPity.cs · AmbushDraw.cs · EventFacts.cs · EventOutcomeDispatch.cs · DelveResourceDelta.cs
  DelveUiPresentSink.cs · RoomEventPoolSeedFile.cs · SupplyOverrideTagSeedFile.cs   (moved)
gk-core/src/FusionRpg.Core/Delve/Events/                            (deleted)
gk-core/tests/FusionRpg.Core.Tests/Delve/Events/*                   (using lines and two qualifiers only)
tests/FusionRpg.Guard.Tests/StoryletEngineSingleSourceTests.cs   (new)
gk-core/scripts/enforcement-registry.v1.json                         (edited: ns1-one-storylet-engine row)
```

## Testing strategy

- **Assertions unchanged:** every existing test under `gk-core/tests/FusionRpg.Core.Tests/Delve/Events/` and the three
  bridge test files pass; the test diff contains only `using` lines and the two qualifier changes (§5).
- **Stream identity:** a new test resolves the same room through `DelveStoryletHost.Resolve` before and after
  (a recorded `EventResolution` from the pre-move code, committed as a fixture) and asserts byte equality over
  `EventId`, `DrawnOutcomeOrdinal`, `Instance` and `NextPity`, for 64 seeds across all six event-capable room
  kinds and an `unknown` room.
- **Goldens untouched:** battle, expedition and world golden suites run in the same command; no hash moves.
- **Dependency direction:** reflection test — no engine type references `FusionRpg.Core.Delve.*`.
- **Guard:** a probe type named `ZzProbeDeck` that references `EventRow` outside the engine fails
  `StoryletEngineSingleSourceTests` (created in-memory as source text, never written to `src/`, following the guard
  suite's scan shape); a probe `ZzProbeDraw` with no storylet reference passes, and the four shipped loot/atom
  `*Draw` types pass (Audit 2026-09-19).

## Success criteria

1. Every event-deck, bridge and Data Delve test green with no assertion changed. 2. Stream-identity fixture
equal for all 64 seeds. 3. Battle, expedition and world goldens byte-identical. 4. `Delve/Events/` no longer
exists; the engine has no Delve dependency. 5. The NS1 guard and its enforcement-registry row land together.

## Boundaries

- **Always:** move, never rewrite; keep stream names; keep type names; land the guard with the move.
- **Ask first:** any change to a refusal message, a stream name, or a public signature beyond §2.
- **Never:** change behaviour; delete a test; leave a copy of an engine type under `Delve/`; add a
  second deck for any place.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `IStoryletHost`, `StoryletDrawContext`, engine `EventDeck.Resolve(host, deck, ctx)`, `StoryletAnswer.Resolve` | `storylet-contract`, `storylet-selection`, every wave 4 host |
| `DelveStoryletHost` (old signatures) | `delve-live-rooms`' routes (Owner ruling 2026-09-19 (round 3): formerly party-dungeon's D3.9; they call this instead of `EventDeck.Resolve`) |

## Contradictions found (report; not fixed here)

1. **"Tests pass unchanged" cannot be literal.** `npc-story-events-map.md:208` and G1 (`:297`) say the event-deck
   tests pass unchanged; a namespace move must edit their `using` lines. §5 defines the evidence as "no assertion
   or expected value changes". The map's wording should say so.
2. **Party-dungeon's open tasks name the old paths.** `party-dungeon/spec-event-deck.md` §Structure
   (`:330-346`) places the engine under `gk-core/src/FusionRpg.Core/Delve/Events/`. After this module that section is
   stale; the propagation belongs in party-dungeon's spec update that also lands NS7
   (`npc-story-events-map.md:414-418`).

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: Delve event engine, battle RNG streams (unchanged), guards.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 2 and G1; ideal §6.2; spec-event-deck.md §Structure and §10; every file in
    Delve/Events/ opened or grepped for its Delve couplings.
[x] decisions.md: NS1 drafted in the map, appended by this module's build change.
[x] Every claim cites file:line.
[x] No constraint assumed: golden stability is a test to run, not a claim.
[x] No cache introduced. No population pinned. No actor number touched.
[x] No parallel path: the move removes the only place a second engine could grow.
[x] Registry row: ns1-one-storylet-engine, guard StoryletEngineSingleSourceTests.
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | The NS1 guard as specified (any `*Deck`/`*Draw` type outside the engine) is red on landing: `DropTableDraw`, `RarityDraw`, `BudgetDraw`, `ResolvedDraw` exist in `gk-core/src/FusionRpg.Core` today (verified by grep). A guard that fails on shipped, unrelated code gets allow-listed into meaninglessness | **Fixed:** the scan keys on a storylet-type reference, with a negative probe test |
| 2 | low | Map citations one line early after a map insert (`:207`, `:260-261`, `:296`, `:398`, `:413-418`, `:484-486`) | **Fixed** |
| 3 | low | Verified this session: the folder's 18 files and the six external referrers (`grep` over `src/`, `tests/`) match §1 and §4 | no change |

Checked and clean: SOLID (one engine, dependency direction test), full suite once at the end is correctly justified
(cross-module, AGENTS.md point 2), no SQL, no tunable, no cache, no population pin.

**Proposed enforcement-registry row:** `ns1-one-storylet-engine` — "no second storylet engine"; guard
`tests/FusionRpg.Guard.Tests/StoryletEngineSingleSourceTests.cs` (storylet-type-referencing `*Deck`/`*Draw` outside
`FusionRpg.Core.Narrative.Storylets`, closed allowlist). **Verification-boundary ask:** `core-narrative` (see
`spec-narrative-vocabulary.md`) must also select `gk-core/tests/FusionRpg.Core.Tests/Delve/Events/**` and the Guard test while
the move is in flight.

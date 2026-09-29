# Spec: quest-log-contract

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `quest-log-contract`, row 16 of the [npc-story-events map](../npc-story-events-map.md) (`:221`), wave 3.
Depends on `quest-sources` (open quests and verdicts), `character-registry` (the cast met) and `story-ledger` (the
story so far). Consumed by the FE module `quest-log-layer` (wave 6, after its `/idea-ui` gate). **No UI.** Session
record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

The server read model and wire DTO for the quest log — the player-facing *"quest log you can open as a layer"* the
loop page names as a catalog gap (`docs/guide/the-loops.md:142`; ideal §3.3, `npc-story-events-ideal.md`):

1. **Open quests** across scopes — save, the active world, and the active delve's quests — each with
   `have / need`, its giver and its expiry on the host's clock;
2. **The cast you have met** — every character with a `met` fact, their relation band and fate;
3. **The story so far** — spine chapters reached, and history fragments found out of order and shown sorted.

Plus one command: **abandon** a quest (free).

Success looks like: one `GET` returns all three sections with the game closed; the DTO carries text keys, token
values and small numbers only — no `Θ`, rung id, `PartyIndex`, engine type name or raw fact kind; every FE refresh
edge is named and tested.

## Locked anchors

- **A quest log is a layer, never a route** (map principle 15, `:121-123`; ideal §6.5, `:444-445`; DESIGN-GATE §1 UI
  row, GG-1). This module ships only the read model; `quest-log-layer` designs the layer through `/idea-ui`.
- **No engine vocabulary on a player surface** (DESIGN-GATE §1 UI row: *"engine vocabulary (`typeId`, `Intent`,
  `UniqueActor`) on a player surface"* is a failure), and the Delve's own quest DTO rule: *"no `Θ`, rung id or
  `PartyIndex`"* (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestDto.cs:3-8`).
- **Names are tokens** (map principle 16, `:124-126`): the DTO carries tokens and keys; `narrative-text` renders them.
- **Relations are derived bands** (`spec-relation-ledger.md` §2); **fate is derived** (`spec-character-registry.md` §3).
- **History fragments are found out of order and sorted** (ideal §6.10, `:517-519`; Caves of Qud, `:238`).
- **Edge-refreshed caches enumerate every trigger** (DESIGN-GATE §2.16).

## Design

### 1. Routes

Minimal-API group beside the onboarding routes' shape (`gk-core/src/FusionRpg.Server/OnboardingEndpoints.cs:25-50`:
`PlayerExists` → 404, a DTO body, `409` on a conflict):

| Route | Does |
|---|---|
| `GET /api/narrative/{playerId}/quest-log?worldId={id}` | the whole read model (§2). `worldId` optional: omitted → the player's active world, if any |
| `POST /api/narrative/{playerId}/quests/{questKey}/abandon` | `QuestLifecycle.Abandon` (`spec-quest-sources.md` §4); `404` unknown, `409` already closed, `200` with the updated quest entry |

`questKey` is an opaque, URL-safe token the read model issues for each narrative quest (the ledger subject
`quest:{questId}#{offerSeq}`, base64url-encoded); the client never builds one. Delve quests are not abandonable here —
they end with their delve (party-dungeon's rule) — and their entries carry `CanAbandon = false`.

### 2. DTO

```csharp
namespace FusionRpg.Contracts.Narrative;

public sealed record QuestLogDto(
    IReadOnlyList<QuestEntryDto> OpenQuests,
    IReadOnlyList<QuestEntryDto> RecentlyClosed,      // closed within questLog.recentClosed.{clock} host ticks (§2)
    IReadOnlyList<CastEntryDto> CastMet,
    StorySoFarDto Story,
    long Revision);                                   // max ledger seq read; lets the client skip a no-op refetch

public sealed record QuestEntryDto(
    string QuestKey, string Scope,                    // "save" | "world" | "delve" (display grouping, not an engine id)
    NarrativeTextDto Name, NarrativeTextDto Flavor,   // Alignment 2026-09-20: the one wire text shape (spec-narrative-text.md §2)
    long Have, long Need, bool Done,
    string State,                                     // "open" | "paused" | "completed" | "expired" | "abandoned" | "failed"
    GiverDto? Giver,                                  // who offered it (a character token), null for a delve quest
    ExpiryDto? Expiry,                                // null: no expiry
    bool CanAbandon);

public sealed record ExpiryDto(string Clock, long Remaining);   // Clock: "turns" | "returns" | "expeditions" — a display unit; frozen while "paused"
public sealed record GiverDto(string CharacterToken);           // "{c_<id>}" or a lead token
public sealed record CastEntryDto(string CharacterToken, string EpithetToken, string Role, string Band, string Fate, string Home);
public sealed record StorySoFarDto(IReadOnlyList<ChapterDto> Chapters, IReadOnlyList<FragmentDto> Fragments);
public sealed record ChapterDto(int Ordinal, NarrativeTextDto Title, bool Reached);
public sealed record FragmentDto(int SortKey, NarrativeTextDto Text, bool Found);
// Alignment 2026-09-20: TextRefDto(Key, Tokens: string -> string) is withdrawn. Every story text on this read model
// is narrative-text's NarrativeTextDto { key, tokens: placeholder -> TokenRefDto } (FusionRpg.Contracts), bound by
// StoryTextBinder; one wire text shape in the program (SOLID S).
```

- **`Role`, `Band`, `Fate`, `Home`** are closed display ids from registries (`NarrativeRoleCatalog`, the disposition
  registry, `CharacterFate`, a home kind) — catalog ids the FE maps through lingui, the same way every other surface
  shows catalog ids (DESIGN-GATE §1 UI row: *"Player names … load from `gk-core/data/tuning/*-catalog.v{n}.json`"*).
- **`State`** (Audit 2026-09-19): `failed` is the closing state `quest-sources` writes when a world falls
  (`{cause: world-fallen}`) — the draft's four states omitted it. `paused` (Owner ruling 2026-09-19 (round 4)) is an
  open world quest whose world is hibernating or idle: shown and still abandonable, its `Remaining` frozen
  because its expiry clock counts full-step turns only (`spec-quest-sources.md` §4). A fallen world's quests appear
  under `RecentlyClosed` as `failed`, then in the frozen history; nothing is deleted.
- **Enemy entries in `CastMet`** (R13 rules 2 and 3) carry the same six display ids as anyone else and nothing more:
  no encounter count, no "times defeated", no ordering by threat — a list of names met, never a roster of rivals.
- **`Band`** for a joined character is `"joined"` (the relation became loyalty, `spec-relation-ledger.md` §3); the
  quest log does not show loyalty numbers.
- **No numbers but counts.** `Have`, `Need`, `Remaining`, `Ordinal`, `SortKey` are small counts; there is no
  magnitude, no `Θ`, no price, no seed. A reflection test fails on any DTO property named `Theta*`, `*Seed`,
  `PartyIndex`, `Rung*`, `InstanceId` or `*Id` other than `QuestKey`.
- **Chapters:** every reached chapter, plus the **next** unreached one with `Reached = false`; later chapters are
  omitted so the spine does not spoil itself. **Fragments:** only found ones are sent, sorted by `SortKey`
  (`Found` is always true on the wire; the field exists so a later design can show a found/total count without a
  DTO change).
- **`RecentlyClosed` window:** `questLog.recentClosed.{clockKind}` host ticks per scope, **declared in
  `narrative.v1.json` at wave 0 (plan §4 D4; current version `v2`)** rather than added in this module's build change
  (starting value 3 on every clock: long enough to see an outcome
  on the next visit, short enough that the list stays a log of *recent* events).

### 3. Assembly

`QuestLogReadModel.Build(playerId, worldId)` (Server, new) — one read transaction:

| Section | Reads |
|---|---|
| open narrative quests | `quest.offered` without a closing fact (`spec-quest-sources.md` §4); `have/need` from `NarrativeQuestProgress.Evaluate` over the sources; expiry `Remaining = expiresAtClock − currentClock` of the offering host |
| open delve quests | the active delve's `ReadQuestOffer` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:535`), `have/need` from the stored verdict or `QuestProgress.Evaluate` over the in-progress report (empty until the offer is written at `CreateDelve`, map `:183` — Owner ruling 2026-09-19 (round 3): that write is this program's `delve-live-start`, `spec-delve-live-start.md` §4) |
| recently closed | closing facts within the recent window |
| cast met | characters (`ListCharacters`, `spec-character-registry.md` §4) with a `met` fact about them, their derived band (`RelationReader`, `spec-relation-ledger.md` §4) and derived fate. **Enemy-role characters** never carry a `met` fact (`character-registry` refuses relation facts about them, `spec-character-registry.md` §5); they appear once a `storylet.seen` fact's cast names them, with the band of **their faction** (`RelationReader.FactionBand`), never a personal one (R13 rule 3) |
| story so far | `chapter.reached` facts (spine chapters, `spine-progress`) and fragment facts (`flag.set` subjects `flag:fragment.{fragmentId}`, written by `spine-progress`) joined to the spine chapter and fragment catalogs for keys and sort keys |

Text keys come from the quest anchor (its keyed `name` and `flavor`, `narrative-seed/spec-quest-vocab.md` §3 —
Owner ruling 2026-09-19 (round 3): the narrative quest anchor is `quest-vocab`'s), character seed and spine chapter
seeds at the revision the fact recorded
(`storylet_revision`, `seed_revision`), so an entry never changes wording under the player because the corpus moved.

### 4. Refresh edges (DESIGN-GATE §2.16)

The FE will hold this read model in its query cache. It is **edge-refreshed**: the Server pushes one hub event,
`NarrativeUpdated { playerId, revision }`, on the web group — the pattern every other domain uses (`CreaturesUpdated`,
`SoulsUpdated`, `DelveUpdated` in `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:214-216` and elsewhere). The full
trigger set — every one has a test:

| # | Trigger | Why it moves the read model |
|---|---|---|
| 1 | a `quest.offered` fact | a new open quest (**key-set edge**) |
| 2 | any closing quest fact (`completed`, `expired`, `abandoned`, `failed`) | an entry leaves the open set (**key-set edge**) |
| 3 | a fact that a narrative quest's source counts (a committed world turn, an expedition collect, a battle log row, a delve close) | `have` moves — fired once per host commit, not per fact |
| 4 | a Delve quest offer or verdict write (`WriteQuestOffer`, `WriteQuestVerdicts`, `RpgStore.Delve.cs:517`, `:550`) | the delve section changes |
| 5 | a `met` fact | the cast set grows (**key-set edge**) |
| 6 | a relation fact, an unlock flag, `character.joined/departed/fell` | a band or fate changes; join/depart is a key-set edge for "band vs joined" |
| 7 | `chapter.reached`, a fragment flag | the story section changes |
| 8 | the active world changes (a new world created, the player moves to another world) | the world scope switches entirely |
| 9 | the active player changes (client-side) | a different read model; the client re-keys its query by `playerId` |
| 10 | SignalR reconnect | the client refetches unconditionally (the shipped reconnect gap, DESIGN-GATE §2.16, `gk-fusion/src/FusionRpg.Injector/RpgClient.cs:143-147`) |
| 11 | a host clock advances with **no** quest-source fact (Audit 2026-09-19) — a `sanctum.returned` fact, an expedition collect with no counted fact, a delve room entry | `Remaining` and the `RecentlyClosed` window are measured on host clocks, so they move even when no quest progressed; trigger 3 fires only for counted facts |
| 12 | a world's attention or outcome state changes (Owner ruling 2026-09-19 (round 4): `active` ↔ `hibernating`/`idle`, `outcome → fallen`) | quests flip between `open` and `paused` (**key-set edge** of the paused set), or close as `failed`; raised from world-continuity's state-change commit through `NarrativeNotify.AfterCommit` (filed on `world-state-vocabulary` / `world-fall`) |

The Server raises triggers 1–8, 11 and 12 from **one** place: `NarrativeNotify.AfterCommit(playerId)`, called by
`OutcomeExecutor`, `QuestLifecycle.Settle`/`Abandon`, the world turn commit, the expedition collect and the delve
close — after their transactions commit, best-effort, as the expedition collect already does
(`ExpeditionEndpoints.cs:214-216`). A missed push costs a stale view until the next event or refetch, never wrong
data, because the read model has no server cache: it is rebuilt on every `GET`.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `Have`, `Need`, `Remaining` | `long` | from `quest-sources`' `long` counts and clocks |
| `Revision` | `long` | a ledger `seq` |
| `Ordinal`, `SortKey` | `int` | small catalog positions (chapters are finite per R3; fragments per chapter) |

## SOLID notes

- **S:** one read model assembles; each section's owner computes its values.
- **O:** a new quest family or story section is one more assembler arm and DTO list.
- **I:** the FE reads one DTO; it never queries ledgers directly.
- **D:** the read model depends on the owners' read APIs, never on tables.
- No second quest state, no stored log, no second push path (the hub event uses the existing hub).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Server/Narrative/QuestLogReadModel.cs','src/FusionRpg.Server/Narrative/NarrativeEndpoints.cs','src/FusionRpg.Contracts/Narrative/QuestLogDto.cs','tests/FusionRpg.Server.Tests/Narrative/QuestLogReadModelTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~QuestLog|FullyQualifiedName~NarrativeNotify"
```

## Structure

```
src/FusionRpg.Contracts/Narrative/QuestLogDto.cs          (new)
src/FusionRpg.Server/Narrative/QuestLogReadModel.cs       (new)
src/FusionRpg.Server/Narrative/NarrativeEndpoints.cs      (new: GET quest-log, POST abandon)
src/FusionRpg.Server/Narrative/NarrativeNotify.cs         (new: AfterCommit -> NarrativeUpdated)
tests/FusionRpg.Server.Tests/Narrative/QuestLogReadModelTests.cs   (new; in-memory store)
tests/FusionRpg.Server.Tests/Narrative/NarrativeNotifyTests.cs     (new: one test per trigger in §4)
```

## Testing strategy

Game closed; in-memory store; fixture corpus.

- **Sections:** a fixture save with one open world quest, one delve quest, one met character and one reached chapter
  returns each in its section with the right `have/need` and `Remaining`.
- **World isolation:** a quest in world A is absent when `worldId = B`; a save quest appears in both.
- **No engine vocabulary:** the reflection test in §2; a serialized fixture DTO contains no `Θ`, seed, instance id or
  raw fact-kind string (a text scan of the JSON against the `StoryFactKind` wire ids).
- **Revision stability:** moving the fixture corpus to a new revision after a quest was offered leaves that quest's
  `Name` key unchanged.
- **Spoilers:** only the next unreached chapter is listed; unfound fragments are not sent; found fragments come
  sorted by `SortKey` whatever order they were found in (found in reverse and in shuffled order give the same list).
- **Abandon:** abandoning an open narrative quest returns `200` and moves it to `RecentlyClosed`; again → `409`; a
  delve quest → `CanAbandon = false` and the route refuses.
- **Refresh edges:** one test per §4 trigger asserts `NarrativeUpdated` is raised after the commit (spy hub), including
  the key-set edges 1, 2, 5, 6 and 12, the world switch 8 and the clock-only advance 11.
- **Paused and failed (round 4):** a quest in a hibernating fixture world reads `paused` with an unchanged
  `Remaining`; the same quest after the world falls reads `failed` in `RecentlyClosed`.
- **Enemy band:** an enemy-role character met shows the faction band even when personal relation facts would be
  refused anyway (the value comes from the faction subject).
- **No population:** fixtures only.

## Success criteria

1. One route returns open quests, cast met and story so far with the game closed. 2. The DTO carries no engine
vocabulary or magnitude. 3. Abandon is one free command. 4. Every refresh edge, including every key-set edge, raises
`NarrativeUpdated` and is tested. 5. No UI is built here.

## Boundaries

- **Always:** rebuild on read; tokens and keys, never display strings; one notify call site per commit path.
- **Ask first:** showing a relation as a number; listing unreached chapters beyond the next.
- **Never:** a route-level page; a server-side cache of the log; exposing `Θ`, seeds or instance ids; abandoning a
  delve quest here.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `GET /api/narrative/{playerId}/quest-log` → `QuestLogDto` | `quest-log-layer` (FE) |
| `POST …/quests/{questKey}/abandon` | `quest-log-layer` |
| `NarrativeUpdated` hub event | FE query invalidation; `storylet-card` may reuse it |
| `NarrativeNotify.AfterCommit` | `outcome-routing`, `quest-sources`, every host's commit path |

## Contradictions found (report; not fixed here)

None.

## Open questions

None for the owner. What the layer looks like is `/idea-ui`'s, not this contract's.

## Design-gate checklist

```
[x] Subsystems: UI contract (no UI), quests, characters, relations, spine, SignalR push.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map rows 16 and 27, principle 15; ideal §3.3, §6.5, §6.10; DESIGN-GATE §1 UI row, §2.16;
    sibling specs quest-sources, story-ledger, relation-ledger, character-registry; code: QuestDto,
    RpgStore.Delve quest block, OnboardingEndpoints, ExpeditionEndpoints push block, hub event names.
[x] Every claim cites file:line.
[x] No population pinned.
[x] Cache: the FE query cache is edge-refreshed; all twelve triggers listed (11 and 12 added by the 2026-09-19 audit),
    key-set edges named, each tested.
[x] Order: fragment sort is order-independent and tested.
[x] Actor numbers: none; no magnitude reaches the DTO.
[x] No parallel path: one read model, the existing hub.
[ ] Registry row: the DTO vocabulary reflection test is local; no enforcement-registry row proposed.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (UI row, GG-1; Standalone row), §2 (9, 16 — full trigger set
including key-set edges), §3, §5; `QuestDto.cs` wire rule; R13 rules 2-3; round-3 and round-4 rulings.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | MEDIUM | **§2.16 trigger set incomplete.** `Remaining` and the recent-closed window move on host clocks alone (a Sanctum return, a collect with nothing counted), but trigger 3 fired only for counted facts — the classic "values move without the listed trigger" gap | **Fixed**: trigger 11, with its test |
| 2 | MEDIUM | Round-4: a world's attention/outcome change pauses or fails its quests; no trigger covered it and the DTO could not say `paused` | **Fixed**: trigger 12 (a key-set edge), `State = paused`, test |
| 3 | MEDIUM | `State` omitted `failed`, which `quest-sources` writes on a world fall — the DTO could not represent a real closing fact | **Fixed** |
| 4 | LOW | R13: `CastMet` enemy entries could grow per-enemy history fields later | **Fixed**: stated no encounter count / threat ordering |

Checked and holding: layer not route (GG-1); no engine vocabulary (reflection test); rebuild on read, no server cache;
tokens not display strings; abandon free.

**Registry row proposed** (shared file, not written): `ns-quest-log-dto-vocabulary` → the `QuestLogDto` reflection test
(no `Theta*`, `*Seed`, `PartyIndex`, `Rung*`, `InstanceId`). **Boundary ask:** `src/FusionRpg.Contracts/Narrative/**`
and `src/FusionRpg.Server/Narrative/QuestLogReadModel.cs` (new), `NarrativeNotify.cs` (new) → `FusionRpg.Server.Tests` filter
`QuestLog|NarrativeNotify`.

## Cross-lane alignment (2026-09-20)

Alignment 2026-09-20: `TextRefDto` (a key plus a `string → string` token map) was a second wire text shape beside
`narrative-text`'s `NarrativeTextDto` (`spec-narrative-text.md` §2, its audit finding 4; `npc-story-events-map.md`
deferred list). §2 now uses `NarrativeTextDto` for `Name`, `Flavor`, `ChapterDto.Title` and `FragmentDto.Text`, and
`TextRefDto` no longer exists. The DTO reflection test's `*Id` rule applies to this read model's own records; the
`Id` member of `TokenRefDto` is narrative-text's token reference, not an engine id, and is exempt by type. Quest
anchors carry no amount (`narrative-seed/spec-quest-vocab.md` §3), so no quest-log text binds a `magnitude` token.

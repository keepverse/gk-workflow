# Spec: spine-progress

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `spine-progress`, row 22 of the [npc-story-events map](../npc-story-events-map.md) (`:227`), wave 4. Depends
on `story-ledger`, `storylet-selection` and `scene-script-loader`. Reads narrative-seed's spine chapter seeds
(`spine-pipeline`, `docs/architecture/narrative-seed/spec-spine-pipeline.md`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Run the spine — the chase for the Rotwright and the pieces of his broken time machine — as **data**:

1. **Chapter eligibility** from save-scoped facts: a time-machine **piece recovered per world won** (R3);
2. **Spine beats at the top tier**, at most one per pulse, pre-empting everything else;
3. **`chapter.reached`** facts when a chapter's scenes are acknowledged;
4. **After the last chapter, arcs and texture continue** — no ceiling;
5. **History fragments** placed in vaults, shrines and delve caches as storylets, found out of order and sorted in the
   quest log.

Success looks like: with the game closed, a fixture save with one piece recovered makes chapter 2 due; its scene is
queued at the next Sanctum return ahead of any other conversation; acknowledging it writes one `chapter.reached`; with
every fixture chapter reached, the hub and every host keep offering arcs and texture; fragments found in any order
list sorted.

## Locked anchors

- **R1** spine fully generated; **R3** finite chapters keyed to time-machine pieces, one per world won, then arcs and
  texture continue — *"not a progression ceiling"* (`npc-story-events-ideal.md` §10 R1, R3; map locked assumption 3,
  `:142-143`).
- **Spine beats pre-empt, at most one per pulse** (ideal §6.2 selection item 1, `:347-348`;
  `SelectionBounds.SpineBeatsPerPulse = 1`, `spec-narrative-vocabulary.md` §4).
- **Spine chapter seeds carry their eligibility facts**: each chapter work item carries *"the chapter slot and its
  time-machine piece, the world facts that make it eligible (as the frame names them — the runtime reads them), the
  scene count"* (`docs/architecture/narrative-seed/spec-spine-pipeline.md:28-31`); after the last chapter arcs and
  texture continue (`:34`).
- **Scenes as data, played by `StorySceneHost`** (`scene-script-loader`; `SceneBeat` is linear today,
  `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:32`).
- **History as artifacts** (ideal §6.10, `:517-519`; Caves of Qud, `:238`).
- **Save scope for the spine** (ideal §6.7, `:465`: *"Spine chapters reached, companions, leads' memory of you"*).
- **No world-end transition exists today**: `rpg_worlds.state` only ever holds `'active'`
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:32`; `spec-story-ledger.md` §5).

## Design

### 1. The spine catalog

`SpineCatalog.Load(dir)` (new, Core) reads spine chapter seeds from narrative-seed's corpus
(`data/seed/narrative/spine/` (new)) through the same envelope, revision, tombstone and provenance rules as every seed
(`spec-storylet-contract.md` §1, §4). Alignment 2026-09-20: it reads exactly the seed's fields
(`narrative-seed/spec-narrative-contract.md` §8) — `id`, `chapterId`, `pieceId`, `after`, `title`, `synopsis` and
`scenes[] {sceneId, teaches, beats[]}` — and **derives** what the seed does not carry, because the seed holds no
number and no tree: `Ordinal` is the chapter's position on the `after` chain (the chapter with `after: none` is 1);
`PieceOrdinal` is the same position (the k-th piece recovered opens the k-th chapter, §2); eligibility is the runtime
rule of §2, built here, not a seed field (the earlier `ordinal`, `pieceOrdinal` and `eligibility` seed fields do not
exist on the seed side). The catalog validates: one chain with no gap or cycle, one chapter per `pieceId`, every scene
id resolvable. It never counts chapters in a test (the frame's size is narrative-seed's reading).

**Early chapters teach the first loops (Owner ruling 2026-09-20: story is also the tutorial).** The chain order is
authored in the frame (`narrative-seed/spec-arc-shapes.md` §5), whose rule is that the first chapter teaching each
`teaches` value follows the registry's teaching order (`narrative-seed/spec-storylet-vocab.md` §3.8). This module
plays chapters 1..7 in chain order and adds no ordering of its own; a teaching scene is acknowledged like any scene
(a skip counts, and appends `mechanic.first-seen`, `spec-storylet-selection.md` §4), and no chapter waits on a
first-session checkpoint — those are `docs/architecture/standalone/spec-first-session-progression.md`'s, and the spine
supplies the scenes that teach around them.

### 2. Pieces and chapter eligibility

A **piece** is recovered once per world won:

```text
on world won (world W):  append flag.set  subject flag:spine.piece.{k}  (save scope)
                         where k = 1 + number of spine.piece flags already set
                         source ref: world-won:{worldId}
```

Chapter `c` is **due** when its eligibility holds over save facts — typically `spine.piece.{c.pieceOrdinal}` set — its
predecessor `c − 1` has `chapter.reached`, and `c` itself has not. The source ref makes the piece append idempotent
per world, so re-reading the same win cannot grant a second piece. Audit 2026-09-19: `k` is read and the flag appended
in **one** store transaction (the ledger's write path, `spec-story-ledger.md` §6), so two wins settled back to back can
never both compute the same `k`.

**What "world won" reads.** No code ends a world today (§Locked anchors). The win record is world-map-program's to
define with its world-end transition; this module reads it through one seam,
`IWorldOutcomeSource.WonWorlds(playerId)` (new), whose production implementation lands with that transition (filed
on world-map-program, together with `character-registry`'s retirement call, `spec-character-registry.md` §4).
Owner ruling 2026-09-19 (round 3): worlds no longer end; the approved world-continuity program's `world-victory`
module writes the durable, idempotent world-won fact (`rpg_world_won_facts`,
`world-continuity/spec-world-victory.md` §3) when a world's outcome becomes `won`, and the world keeps running. The
seam's production implementation reads that table; the fall call is a separate edge, filed on `world-fall`
(`spec-character-registry.md` §4), and never fires on a win or on hibernation. Owner ruling 2026-09-19 (round 4):
nothing is deleted — a piece recovered from a world that later **falls** stays recovered (it is save-scoped history),
and "retire" elsewhere means frozen read-only, never removed; there is no "abandoned" world state. Until
then only a chapter whose frame eligibility names no piece (an opening chapter, for example one gated on the Rift
prologue's `scene.acknowledged`, `spec-story-ledger.md` §1) is reachable, which is honest: the spine cannot advance
past a world that cannot be won.

### 3. Spine beats at the top tier

`SpineBeats.DueFor(playerId, hostKind)` returns the next unacknowledged scene of the earliest due chapter. It feeds
`storylet-selection`'s **spine tier**, which pre-empts priority storylets and the pool, **at most one per pulse**:

| Host | Where a spine beat plays |
|---|---|
| `sanctum.hub` | always: Hourbloom's conversation slot for this return (`spec-sanctum-hub-host.md` §3) |
| `world.*` | only when the chapter's frame marks a scene as world-hosted (for example the Rotwright's voice on a doctrine, `counter-doctrine`): fired as a `story.offered` entry that opens the scene on answer |
| every other host | never: a spine beat is not texture |

A due spine scene is exposed as a `scene.due.{sceneId}` flag (`spec-outcome-routing.md` §5), so the scene-trigger
ledger is the one path to `StorySceneHost`.

### 4. Reaching a chapter

When the **last** scene of chapter `c` is acknowledged (`scene.acknowledged`, including a skip — the player chose not
to watch; the story still moved), append `chapter.reached` (save scope, subject `chapter:{chapterId}`, source
`chapter:{chapterId}:{lastSceneRevision}`). The next chapter's eligibility then reads it. A chapter reached is never
un-reached.

### 5. After the last chapter

When no chapter is due and every catalog chapter is reached, `SpineBeats.DueFor` returns nothing and the spine tier is
empty; selection falls through to priority storylets and the pool, exactly as on any pulse without a due beat. There is
no "end state", no flag that stops other content, and no code path that treats the last chapter specially (R3).

### 6. History fragments

A **fragment** is a storylet whose seed field `fragment` names a row of the spine frame's `fragments[]`
(Alignment 2026-09-20: `narrative-seed/spec-narrative-contract.md` §5, `spec-arc-shapes.md` §5 — there is no
`fragment` storylet kind and no seed `sortKey`), hosted on `world.vault`, `world.shrine`, `delve.shrine` and
`delve.curio` (a cache), with:

- a `story.flag` outcome on its `interact` choice setting `flag:fragment.{fragmentId}` (save scope);
- its place in the machine's history **derived** at load: `SortKey` = the fragment's position on the frame's
  `fragments[].after` chain (the seed carries no number);
- eligibility on the frame row's `afterChapter` being reached — a runtime-built gate on its `chapter.reached` fact,
  ANDed with the storylet's own `eligibility`, so a fragment never explains a chapter the player has not seen.

The quest log sorts found fragments by `sortKey` (`spec-quest-log-contract.md` §2-§3). Fragments are texture: pool
tier, ordinary cooldowns, no reward beyond the flag (a `loot` outcome would need the host's budget like any storylet).

## Data shapes

- `data/seed/narrative/spine/` (narrative-seed's corpus; read here).
- Facts: `flag:spine.piece.{k}`, `chapter.reached`, `flag:fragment.{id}` — all existing fact kinds.
- No table, no tuning key: pacing is the structural `SpineBeatsPerPulse`.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| chapter and piece ordinals | `int` | a finite, planned list (R3) |
| `sortKey` | `int` | a position in a finite history |
| piece count read | `long` | a fact count, widened like every ledger count |

## SOLID notes

- **S:** the catalog loads; eligibility reads facts; selection pre-empts; the scene player plays.
- **O:** a new chapter is seed data; a new beat host is one row in §3's table.
- **D:** depends on `IWorldOutcomeSource` for wins, never on world internals.
- No second scene player, no stored "current chapter" (derived from facts), no ceiling.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Spine/SpineCatalog.cs','src/FusionRpg.Core/Narrative/Spine/SpineBeats.cs','tests/FusionRpg.Core.Tests/Narrative/Spine/SpineProgressTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Spine"
```

## Structure

```
src/FusionRpg.Core/Narrative/Spine/SpineCatalog.cs          (new)
src/FusionRpg.Core/Narrative/Spine/SpineBeats.cs            (new: due chapter, next scene, piece rule)
src/FusionRpg.Core/Narrative/Spine/IWorldOutcomeSource.cs   (new seam; production impl with world-map's world end)
src/FusionRpg.Server/Narrative/SpineProgress.cs             (new: piece append on win, chapter.reached on last ack)
tests/FusionRpg.Core.Tests/Narrative/Spine/SpineProgressTests.cs   (new)
tests/FusionRpg.Server.Tests/Narrative/SpineProgressStoreTests.cs  (new; in-memory store)
```

## Testing strategy

Game closed; fixture spine of three chapters; in-memory store.

- **Piece per world won:** a fixture win appends one piece; re-reading the same win appends none; two wins → two
  pieces with ordinals 1 and 2, whichever world is read first (order-independent count; ordinals follow append order,
  which the test states).
- **Fall keeps the piece (round 4):** a fixture world won and later fallen keeps its piece and every chapter it made
  due.
- **Due chapter:** with piece 1 and chapter 1 reached, chapter 2 is due; without chapter 1 reached it is not.
- **Top tier, one per pulse:** a due spine scene pre-empts a priority storylet at the hub; two due scenes never play
  on one pulse.
- **Reached on last ack:** acknowledging (or skipping) the chapter's last scene writes one `chapter.reached`.
- **No ceiling:** with every fixture chapter reached, a fixture pool storylet is still offered at every host.
- **Fragments:** a fragment ineligible before its chapter is reached becomes eligible after; three fragments found in
  reverse order list in `sortKey` order.
- **Catalog contract:** a broken or cyclic `after` chain and two chapters on one `pieceId` are load refusals; ordinals
  are derived from the chain, never read from the seed (Alignment 2026-09-20); the test never counts the committed
  spine.
- **Teaching scenes (Owner ruling 2026-09-20):** acknowledging, or skipping, a fixture scene with `teaches: talk-verbs`
  appends one `mechanic.first-seen` for `talk-verbs`; a second acknowledgement appends none.

## Success criteria

1. Chapters become due from save facts, one piece per world won. 2. Spine beats pre-empt at most once per pulse.
3. `chapter.reached` is written when a chapter's scenes are acknowledged. 4. After the last chapter every host keeps
its content. 5. Fragments are found out of order and listed sorted.

## Boundaries

- **Always:** derive the current chapter from facts; one beat per pulse; the scene-trigger path.
- **Ask first:** a spine beat on a host other than the hub and world; any chapter that gates other content.
- **Never:** edit a generated chapter (narrative-seed regenerates); store a current-chapter number; define what winning
  a world means (world-map-program's).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `SpineBeats.DueFor` | `storylet-selection` (spine tier), `sanctum-hub-host` |
| `chapter.reached`, `spine.piece.*`, `fragment.*` facts | `quest-log-contract`, `narrative-predicates`, `narrative-readings` |
| `IWorldOutcomeSource` | world-continuity `world-victory` (implementation over `rpg_world_won_facts`, filed; Owner ruling 2026-09-19 (round 3)) |

## Contradictions found (report; not fixed here)

1. **"One piece per world won" has no source.** R3 keys the spine to worlds won (`npc-story-events-ideal.md` §10 R3); no
   code ends or wins a world (`RpgStore.World.cs:32`). The spine past chapter 1 is unreachable until world-map-program
   lands a world-end transition with a win record. A wiring gap owned by world-map-program, not a design wall; this
   module ships the seam and its tests. Owner ruling 2026-09-19 (round 3): the owner is now world-continuity's
   `world-victory` (a world-won fact, no world end).
2. **`fragment` is not a storylet kind.** The storylet kind vocabulary is today's event kinds (`spec-storylet-contract.md`
   §1); fragments need a kind (or a tag) narrative-seed's `storylet-vocab` must add. Filed.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: spine (runtime), story-scene (consumer), world map (world-won source, filed), quest log (reader).
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 22; ideal §6.1, §6.2, §6.7, §6.10, §10 R1/R3; narrative-seed spec-spine-pipeline
    (frame, eligibility facts, R3); sibling specs story-ledger, narrative-vocabulary, outcome-routing,
    sanctum-hub-host, quest-log-contract; code: sceneScript.ts SceneBeat, rpg_worlds DDL.
[x] Every claim cites file:line.
[x] No population pinned (chapter counts are never asserted).
[x] No cache; the current chapter is derived.
[x] Order: fragment order and win read order tested.
[x] Actor numbers: none.
[x] No parallel path: one scene player, one selection tier list.
[ ] Registry row: none new.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (Standalone, Caps rows — "not a progression ceiling"), §2 (9,
11, 15), §3, §5; ideal §10 R1/R3; `narrative-seed/spec-spine-pipeline.md`; `world-continuity-map.md` modules 5 and 7;
round-3/round-4 rulings.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | MEDIUM | Round-4: what a later **fall** does to a piece recovered from that world was unstated, and "retirement" wording implied removal | **Fixed** (§2, test): the piece stays; retire = frozen |
| 2 | LOW | Piece ordinal `k = 1 + count` was a read-then-append with no stated transaction; two wins settled together could collide | **Fixed** (§2): one transaction |
| 3 | LOW | Ideal line citations drifted | **Fixed**: cited by section |

Checked and holding: finite chapters then endless, no end state or ceiling (R3); spine generated, never hand-edited
(R1); no stored current chapter; one scene player; the chapter count is never asserted (validation-ssot).

**Registry row:** none new. **Boundary ask:** `src/FusionRpg.Core/Narrative/Spine/**` → `FusionRpg.Core.Tests` filter
`Narrative.Spine`.

## Cross-lane alignment (2026-09-20)

- Alignment 2026-09-20: §1 read `ordinal`, `pieceOrdinal` and an `eligibility` tree off the spine chapter seed; the
  seed carries `chapterId`, `pieceId` and `after` and no number or tree (`narrative-seed/spec-narrative-contract.md`
  §8). The catalog now derives ordinals from the `after` chain and builds eligibility from §2's rule.
- Owner ruling 2026-09-20 (story is also the tutorial): the spine's chain order teaches the first loops first (the
  frame's rule, `narrative-seed/spec-arc-shapes.md` §5); a teaching scene's acknowledgement appends
  `mechanic.first-seen`. Tutorial scenes stay skippable and never gate play.
- Open (not decided here): §6's fragment storylet reads `fragmentId`, `sortKey` and a `fragment` storylet kind that
  the seed contract does not define (and `sortKey` would be a number in a seed). The propagation to narrative-seed is
  still owed.

- Alignment 2026-09-20 (closes the open item above): fragments are storylets with a seed `fragment` field pointing at
  the frame's `fragments[]` rows (`narrative-seed/spec-arc-shapes.md` §5, `spec-narrative-contract.md` §5); `SortKey`
  and the chapter gate are derived here, not read from the seed.

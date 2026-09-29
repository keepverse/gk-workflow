# Spec: scene-script-loader

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `scene-script-loader`, row 12 of the [npc-story-events map](../npc-story-events-map.md) (`:218`), wave 2.
Depends on `narrative-text` (rendering) and `story-ledger` (eligibility and acknowledgement). Reads spine chapters
and hub conversations that narrative-seed's `spine-pipeline` emits as data (`narrative-seed-map.md:221`). Plays every
scene through story-scene's `StorySceneHost`. Consumed by `outcome-routing` (`scene.play`), `sanctum-hub-host`,
`spine-progress` and `counter-doctrine` (the antagonist's voice). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Load scene scripts as **data** — spine chapters and hub conversations — instead of TypeScript literals, and play them
through the one scene player:

1. a JSON scene contract and a loader that validates it with the same rules as today's typed scripts;
2. speakers from the **cast** (leads and characters), not only the closed `ActorId` union, which widens as a reviewed
   story-scene change (R2 adds the antagonist);
3. eligibility from the **story ledger**, reaching the web through the existing `isSceneEligible` seam, which only
   narrows;
4. a scene acknowledgement that appends to the ledger, leaving the frozen `rift-prologue` / version `1` path alone.

Success looks like: a fixture spine scene loads from JSON, plays in `StorySceneHost` with its tokens rendered, and its
acknowledgement is one `scene.acknowledged` fact; the Rift prologue plays and acknowledges exactly as today.

## Locked anchors

- **One scene player**: `StorySceneHost` (map principle 15, `:121-123`; ownership split `:316`: *"Build a second scene
  player"* is forbidden).
- **Today's script is a typed TS literal**: `SceneBeat`/`SceneScript` (`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:31-50`),
  `SceneId = "rift-prologue"` (`:29`), `ActorId = "penny" | "dave"` (`:19`), validated by `assertSceneScript`
  (`:71-92`) against `maxBeatsPerScene` from `gk-core/data/tuning/story-scene-ui.v1.json` (`sceneScript.ts:60-62`).
- **The trigger seam narrows only**: `isSceneEligible` requires a ledger row, the server's `eligible`, no open layer,
  and an optional `when` that is ANDed (`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.ts:58-74`).
- **The frozen contract**: acknowledgement accepts only `rift-prologue` / `1`
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs:144-147`); the host hard-wires that acknowledgement
  (`gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx:81`, `:133-139`) and the Rift chrome (`:106-107`).
- **R1** (the spine is generated), **R2** (the antagonist speaks; story-scene's v1 deferral is lifted,
  `docs/architecture/story-scene-map.md:177`), **S3** (typed TS module, `story-scene-map.md:305`) stays for the
  hand-authored Rift prologue (`narrative-seed-map.md:466-468`).

## Design

### 1. The scene seed (read; authored by narrative-seed)

Audit 2026-09-19: this section first invented a per-scene seed under `data/seed/narrative/scenes/` with its own
`eligibility` tree, `cast` roles and `{lead: …}` speaker objects. No narrative-seed kind emits that. The seed this
loader reads is the **spine chapter** (`narrative-seed/spec-narrative-contract.md` §8), one per file in the standard
envelope under `data/seed/narrative/spine/` and `data/seed/narrative/authored/spine/`:

```jsonc
{
  "id": "spine-chapter.<body>", "revision": 2, "status": "live", "provenance": "generated",
  "chapterId": "<frame id>", "pieceId": "<time-machine piece>", "after": "<previous chapter or none>",
  "title": { "key": "ns.spine-chapter.<body>.title.<h8>", "text": "..." },
  "scenes": [
    { "sceneId": "scene.<chapter slug>.<scene slot>",         // stable, never reused; never "rift-prologue"
      "teaches": "none",                                         // Owner ruling 2026-09-20: a teaches value or "none"
      "beats": [
        { "speaker": "lead_antagonist",
          "line": { "key": "ns.spine-chapter.<body>.scenes.0.beats.0.line.<h8>",
                    "text": "{lead_antagonist_start} laughs. <em>You are too late, {lead_summoner_bare}.</em>" } },
        { "speaker": "none", "line": { "...": "..." } } ] } ]      // "none" = narration
}
```

- `speaker` is a cast token from `token-grammar` — a lead token (`lead_summoner`, `lead_companion`,
  `lead_antagonist`), a character token `c_<slug>`, or `none` for narration — the same "absent means narration" rule
  as today (`sceneScript.ts:33-34`). The loader maps it to the web speaker union (§4).
- **Eligibility is not a seed field.** A chapter's scenes become due from save-scoped facts `spine-progress` reads
  (`pieceId`, `after`, `chapter.reached`); any other scene is made due by a `story.flag` a `scene.play` outcome writes
  (`flag:scene.<sceneId>`). The runtime compiles that as a `StoryFlagSet` leaf; no seed carries a tree.
- `cueId` and `variant` are not seed fields; a data scene plays with no cue (`StoryCueId`, `sceneScript.ts:22-26`,
  stays the Rift's) until story-scene reviews a cue field.
- ~~There is no `teaching` field: teaching lines are first-session pedagogy owned by the Rift prologue.~~ **Owner
  ruling 2026-09-20 (story is also the tutorial):** each seed scene carries `teaches` — a
  `narrative-seed/spec-storylet-vocab.md` §3.8 value or `none` (`spec-narrative-contract.md` §8). The loader maps it to
  story-scene's existing `SceneBeat.teaching` field (`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:40`,
  *"One optional teaching sentence. Absent ⇒ no teaching line rendered"*) on the scene's **last** beat, whose text is
  that value's authored, keyed `teachingLine` from the registry; every other beat has no `teaching`. The model never
  writes a teaching sentence. The Rift prologue keeps its own hand-authored teaching lines (S3), and the first-session
  checkpoints stay `docs/architecture/standalone/spec-first-session-progression.md`'s — a data scene teaches a loop,
  it never grants or waits on a checkpoint. Teaching beats keep `StorySceneHost`'s unconditional skip; a skipped
  teaching scene still counts as taught (`spec-storylet-selection.md` §4).
- **Hub conversations — resolved (Alignment 2026-09-20).** narrative-seed now expresses them without a new kind
  (`narrative-seed/spec-storylet-vocab.md` §3.1, `spec-character-vocab.md` §5–§6): a conversation with choices is a
  `sanctum.hub` storylet (loaded by `storylet-contract`, not here), and a homecoming reaction is a character seed's
  `lines[]` entry, which this loader serves as a **line scene** (§2).

### 2. Server: loader, eligibility, routes

- **Line scenes (Alignment 2026-09-20).** `SceneScriptCatalog.LineScene(characterId, context, band)` builds a one-beat
  scene from a character seed's `lines[]` entry (`narrative-seed/spec-narrative-contract.md` §6): speaker the
  character's token, line the entry's keyed `text`, no `teaching`. Its id is `line.<character id body>.<context>.<band>`
  (never `rift-prologue`), its revision the character seed's `revision`. It is eligible only while
  `sanctum-hub-host`'s queue for the current return holds it, and its acknowledgement is **per return**: source
  `scene:{sceneId}:{revision}:return:{returnSeq}`, so the same line can play again at a later return
  (`spec-sanctum-hub-host.md` §3–§4).
- `SceneScriptCatalog.Load(dir)` (new, Core) parses spine-chapter seeds, validates each scene with the **same** rules
  as `assertSceneScript` — at least one beat, at most `scene.maxBeatsPerScene` from `story-scene-ui.v1.json` (read by
  C# from the same file), a non-empty line per beat — plus: every text passes `TokenGrammar.Validate`
  (`spec-narrative-text.md` §3); every speaker is a lead token, a `c_<slug>` that maps to a corpus character, or
  `none`; `sceneId` ≠ `rift-prologue`; a reused tombstone id is refused.
- **Eligibility** is a runtime-built `StoryFlagSet` leaf on `flag:scene.<sceneId>` (or `spine-progress`'s chapter
  rule), compiled through `PredicateCompiler` with the narrative context (`spec-narrative-predicates.md` §3) and
  evaluated against a save-level frame, **and** no `scene.acknowledged` fact for `(sceneId, revision)`. `outcome-routing` makes a scene due by writing the flag its eligibility requires
  (`scene.play` → `story.flag`), so a scene needs no fact kind of its own beyond `scene.acknowledged`.
- Routes (new, `src/FusionRpg.Server/StoryEndpoints.cs`):

| Route | Returns / does |
|---|---|
| `GET /api/story/{playerId}/scenes` | `StorySceneRowDto[] { storyId, version, state, eligible }` — the exact `StoryLedgerEntry` shape `isSceneEligible` reads (`sceneTrigger.ts:20-25`: `storyId`, `version`, `state`, `eligible`) — one row per data scene whose eligibility compiles for this save |
| `GET /api/story/{playerId}/scenes/{sceneId}` | `StorySceneScriptDto { sceneId, revision, beats[] { speaker, variant, line: NarrativeTextDto, teaching: NarrativeTextDto?, cueId } }`, with the cast resolved and every line bound by `StoryTextBinder`; `teaching` is set on the last beat of a scene whose `teaches` is not `none` (Owner ruling 2026-09-20) |
| `POST /api/story/{playerId}/scenes/{sceneId}/ack` `{ revision, outcome }` | appends `scene.acknowledged` (source `scene:{sceneId}:{revision}`); a repeat with the same outcome is `ok`; a different outcome is `409 story.scene-conflict` — the onboarding semantics (`RpgStore.Onboarding.cs:166-170`) |

`rift-prologue` never appears in these routes; it stays on `/onboarding/{playerId}/stories/{storyId}/ack`
(`gk-core/src/FusionRpg.Server/OnboardingEndpoints.cs:34-45`).

### 3. Web: loading into the one player

`web/fusion-rpg-web/src/features/narrative/scenes/` (new):

- `useStoryScenes(playerId)` — React Query over the rows route; `useStorySceneScript(playerId, sceneId)` over the
  script route.
- `toSceneScript(dto)` — builds story-scene's `SceneScript` from the DTO and runs `assertSceneScript` on it, so the web
  applies the same structural checks as the server.
- The Sanctum trigger (`gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx:89-94` calls `isSceneEligible` for the
  Rift) calls `isSceneEligible` for each data scene row with a `SceneTriggerSpec { sceneId, version }` built from the
  row; `when` may only narrow (`sceneTrigger.ts:58-74`). With two eligible scenes the caller's order decides
  (`sceneTrigger.ts:10-11` — no queue here); the spine's own ordering is `spine-progress`'s.

### 4. The reviewed story-scene widening (coordinated, not done here alone)

Each item is a change to a story-scene-owned file, reviewed under story-scene, landing in this module's build change:

| Change | Today | After |
|---|---|---|
| `SceneId` | the literal `"rift-prologue"` (`sceneScript.ts:29`) | `string`; `RIFT_PROLOGUE_SCRIPT` keeps its literal id |
| speaker | `speakerId?: ActorId` (`sceneScript.ts:34`) | `speakerId?: ActorId \| CastSpeaker`, where `CastSpeaker = { kind: "character"; characterId: string }` resolves name and initial through `narrative-text`; the seed's lead tokens map to `ActorId` members (Audit 2026-09-19) |
| `ActorId` | `"penny" \| "dave"` (`sceneScript.ts:19`; `ACTOR_IDS`, `actorCast.ts:87`) | gains the antagonist lead (R2). The **id spelling** of all three leads is identity-rename's (`tasks/identity-rename-plan.md`); this module adds the member under whatever id that plan fixes |
| beat text | resolved through positional ids `scene.<sceneId>.beat<n>.line` (`messages.ts`, `beatMessageId`) | the host takes an optional `renderBeat(beat)`; the default keeps today's ids; data scenes pass `useNarrativeText` |
| acknowledgement | `useAcknowledgeOnboardingStory(playerId)` hard-wired (`StorySceneHost.tsx:81`) | an optional `acknowledge` prop; the default stays the onboarding hook |
| chrome | the Rift title and subtitle hard-wired (`StorySceneHost.tsx:106-107`) | optional chrome props; the default stays the Rift chrome |

Every default reproduces today's behaviour, so the Rift prologue's tests pass unchanged. The story-scene map's
out-of-scope row *"Dr. Zomboss as a v1 actor"* (`story-scene-map.md:177`) gains a pointer to R2 in the same change
(propagation owed by the map, `npc-story-events-map.md:420-422`; the "Dr. Zomboss" wording is identity-rename's).

### 5. The scene-rows cache and its triggers (DESIGN-GATE §2.16)

The web holds the scene rows in the React Query cache under a new `queryKeys.storyScenes(playerId)` (the onboarding
precedent keys by player, `gk-web/web/fusion-rpg-web/src/lib/bus/onboarding.ts:41-42`). Its key set — which scenes are
eligible — moves whenever the ledger gains a fact a scene's eligibility reads. The full trigger set, each with a test:

1. **profile load or switch** — the key includes `playerId`;
2. **a scene acknowledgement succeeds** — the ack mutation invalidates the key (`onboarding.ts:55`, `:65` precedent);
3. **the player returns to the Sanctum after an outing** (a delve closes, an expedition is collected, a world turn is
   committed) — the state-entry edge where new scenes become due; the server events for those three are mapped to this
   key in `keysForEventKind` (`gk-web/web/fusion-rpg-web/src/lib/bus/invalidate.ts:4-15`), and the Sanctum stage also
   invalidates on mount;
4. **a SignalR reconnect** — the hub provider's resync invalidates it with the other player-scoped keys;
5. **a storylet choice whose outcome is `scene.play`** — the answer route's success invalidates it (wave 3 wires the
   route; this module ships the key and the test hook).

The script query (`useStorySceneScript`) is keyed by `(playerId, sceneId, revision)` and immutable per key, so it
needs no trigger beyond its key.

## Data shapes

- Seed: spine-chapter seeds under `data/seed/narrative/spine/` and `authored/spine/` (§1; Audit 2026-09-19: was an
  invented `scenes/` tree).
- Wire: `StorySceneRowDto`, `StorySceneScriptDto` (`src/FusionRpg.Contracts/StorySceneDtos.cs`, new) using
  `NarrativeTextDto` (`spec-narrative-text.md` §2).
- Ledger: `scene.acknowledged` facts with `attrs {revision, outcome}` (`spec-story-ledger.md` §2).
- No table.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| scene `revision` / row `version` | `long` in C#; `number` on the wire | a regeneration counter; far below 2^53 |
| beat count | `int` | bounded by `maxBeatsPerScene` |

## SOLID notes

- **S:** one scene player; this module supplies data and an ack adapter, never a second host.
- **O:** story-scene is extended through optional props whose defaults keep today's behaviour.
- **L:** a data scene is a `SceneScript`, validated by the same `assertSceneScript`.
- **D:** the host depends on an `acknowledge` abstraction, not on the onboarding hook.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Scenes/SceneScriptCatalog.cs','src/FusionRpg.Server/StoryEndpoints.cs','tests/FusionRpg.Core.Tests/Narrative/Scenes/SceneScriptCatalogTests.cs','tests/FusionRpg.Server.Tests/Narrative/StorySceneRoutesTests.cs') -Session <session-id>
cd gk-web/web/fusion-rpg-web
npx vitest run src/features/narrative/scenes src/features/story-scene src/ui/story-scene
npm run extract ; npm run build ; npm run check:bundle
```

Web paths have no verification boundary (`scripts/verify-change.ps1:95`); the npm commands are their verification.
The change crosses Core, Server and web, so the build task ends with one full-suite run (AGENTS.md verification
boundary, point 2).

## Structure

```
src/FusionRpg.Core/Narrative/Scenes/SceneScriptCatalog.cs          (new)
src/FusionRpg.Contracts/StorySceneDtos.cs                          (new)
src/FusionRpg.Server/StoryEndpoints.cs                             (new)
web/fusion-rpg-web/src/features/narrative/scenes/useStoryScenes.ts (new)
web/fusion-rpg-web/src/features/narrative/scenes/toSceneScript.ts  (new)
gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts         (edited: SceneId, speaker widening)
gk-web/web/fusion-rpg-web/src/features/story-scene/actorCast.ts           (edited: antagonist lead, cast speakers)
gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx           (edited: optional acknowledge, chrome, renderBeat)
gk-web/web/fusion-rpg-web/src/lib/bus/keys.ts · invalidate.ts             (edited: storyScenes key and its triggers)
gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx             (edited: data scene rows through isSceneEligible)
docs/architecture/story-scene-map.md                               (edited: R2 pointer on the out-of-scope row)
tests/FusionRpg.Core.Tests/Narrative/Scenes/SceneScriptCatalogTests.cs   (new)
tests/FusionRpg.Server.Tests/Narrative/StorySceneRoutesTests.cs          (new)
```

## Testing strategy

- **Loader parity (C#):** zero beats, over-cap beats (cap read from the tuning file, never a literal) and an empty line
  reject with the same wording class as `assertSceneScript`; an undeclared role speaker, an unknown character, a bad
  token and `sceneId = rift-prologue` reject.
- **Eligibility (C#):** a scene requiring a flag is ineligible before the flag and eligible after; after an
  acknowledgement at its revision it is ineligible; a new revision is eligible again (the version-pinning behaviour
  `sceneTrigger.ts:40-45` describes for the Rift).
- **Ack (Server, in-memory store):** first ack appends one fact; the same ack again is `ok` with no new fact; a
  different outcome is `409`; the Rift ack route is unchanged.
- **Round trip (web):** a fixture script DTO becomes a `SceneScript` that passes `assertSceneScript`; the host plays it
  with rendered tokens and calls the injected `acknowledge`.
- **Rift unchanged (web):** every existing story-scene and Sanctum test passes with the host's defaults.
- **Narrowing only:** a data scene the server marks `eligible: false` never plays, whatever `when` returns.
- **Cache triggers:** one test per trigger in §5 — profile switch, ack success, each outing-return event kind,
  reconnect, and the `scene.play` hook — each asserts the rows query refetches.
- **No population:** tests use fixture scenes, never the committed corpus.

## Success criteria

1. Data scenes load, validate and play through `StorySceneHost`. 2. Speakers come from the cast; the antagonist speaks
(R2). 3. Eligibility comes from the ledger and only narrows on the web. 4. The Rift prologue is untouched. 5. Every
cache trigger in §5 has a passing test.

## Boundaries

- **Always:** one scene player; defaults that keep today's behaviour; eligibility from the server.
- **Ask first:** changing the `rift-prologue` / `1` contract; a scene queue or scheduler in the web (story-scene N3,
  `sceneTrigger.ts:4-11`).
- **Never:** a second scene player; a scene mid-match on the lawn (map principle 1); literal names in a scene; branching
  beats (ideal §6.11).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `SceneScriptCatalog`, the three `/api/story/{playerId}/scenes` routes | `sanctum-hub-host`, `spine-progress`, `counter-doctrine` |
| scene due-ness through a `story.flag` the scene's eligibility requires | `outcome-routing` (`scene.play`) |
| `queryKeys.storyScenes` and its triggers | every web surface that ends an outing |

## Contradictions found (report; not fixed here)

1. **S3 versus data scripts.** story-scene decision S3 chose a typed TS module (`story-scene-map.md:305`). Generated
   scenes load as data here; the Rift prologue keeps S3. `narrative-seed-map.md:466-468` drafts the `decisions.md` row
   that records the split; it lands with this module's build change.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: story-scene (host, trigger, cast), narrative ledger, i18n, web cache, Sanctum stage.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: story-scene-map (S3, S4, out-of-scope rows); spec-scene-script.md; sceneScript.ts, sceneTrigger.ts,
    actorCast.ts, messages.ts, StorySceneHost.tsx, SanctumStage.tsx trigger; onboarding ack store and route;
    story-scene-ui.v1.json; lib/bus onboarding.ts and invalidate.ts.
[x] Every claim cites file:line.
[x] Cache: the scene-rows cache's full trigger set, including the outing-return key-set edge, each tested.
[x] No population pinned. No actor number.
[x] No parallel path: one scene player, extended by defaulted props.
[ ] Registry row: none proposed. (Audit 2026-09-19: row proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | The loader read a seed shape no seed kind produces (`data/seed/narrative/scenes/`, per-scene `eligibility` trees, `cast` roles, `{lead: …}` speakers, `cond` nodes); the spine chapter (`spec-narrative-contract.md` §8) nests `scenes[]` with token speakers and no eligibility | **Fixed:** §1–§2 read the spine-chapter seed; eligibility is runtime-built from flags and spine facts |
| 2 | medium | Hub conversations (consumed by `sanctum-hub-host`) have no seed kind in `narrative-contract` | **Deferred:** propagation owed to narrative-seed (a hub scene kind or character-line contexts); spine scenes only until then |
| 3 | low | Map citations one line early (`:217`, `:315`, `:419-421`) | **Fixed** |

Checked and clean: one scene player (`StorySceneHost`, defaulted props), the frozen `rift-prologue`/`1` contract
untouched, `isSceneEligible` only narrows, the scene-rows cache lists its full trigger set with the outing-return
key-set edge and a test each (§2.16), no scene mid-match, no population pin.

**Proposed enforcement-registry row:** `ns-one-scene-player` — no second scene player; guard: a web test that
`StorySceneHost` is the only component rendering `SceneScript` beats (`src/features/narrative/scenes` imports it,
never re-implements it).

## Cross-lane alignment (2026-09-20)

- Owner ruling 2026-09-20 (story is also the tutorial): the seed scene's `teaches` value maps to story-scene's existing
  `SceneBeat.teaching` (verified at `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:40`, inside the
  `SceneBeat` type at `:32`) on the last beat, from the registry's authored teaching sentence; the wire DTO gains
  `teaching`. Skippable as every scene; never gates play.
- Alignment 2026-09-20: the hub-conversation gap in §1 is closed by narrative-seed's `sanctum.hub` host row and
  `return-*` line contexts; this loader adds line scenes, acknowledged per return.

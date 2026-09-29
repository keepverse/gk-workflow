# Spec: `arc-shapes`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `arc-shapes` · **Map row:** 7 · **Wave:** 1 (after `storylet-vocab` and `character-vocab`)
**Depends on:** `storylet-vocab`, `character-vocab` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.

---

## Objective

Author the two structures that keep generated story coherent without a model deciding them:

1. **The arc-shape registry** — each shape fixes its link count, each link's host kind and storylet kind,
   the roles that persist across links, and the flags each link sets and reads. The model later writes an
   arc's name, premise and every link **inside** a shape, in one work order, so a link can never point past
   its arc (`narrative-seed-ideal.md` §6.4). The committed corpus shows why: two of four story `chainRef`s
   point at events that do not exist (map §3.4).
2. **The spine frame** — one chapter slot per time-machine piece, with each chapter's scenes, beat counts
   and cast (rulings R1, R3). The spine is fully generated (R1); what keeps it coherent is this frame, which
   the planner owns and the model never changes.

A rival shape is a fixed, authored chain that obeys R13 rules 1–3: the rival never levels, ranks up or
remembers encounters (`npc-story-events-ideal.md` §6.12).

**Done means:** both files exist and load; every link's host and kind are legal under `storylet-vocab`;
flags close; persistent roles close; the rival shape passes the R13 checks; the spine frame's structure
tests pass with its seven chapter slots (Audit 2026-09-19: the owner answered the open question — seven
pieces — so the frame no longer ships empty).

---

## Design

### 1. Why shapes are authored, not generated

Choice-based prior art is consistent: floating storylets alone *"tend to collapse"* without a large volume
of content, branch-and-bottleneck needs heavy state, and a gauntlet is the easiest to author
(`narrative-seed-ideal.md` §5.3). Here texture is floating storylets, arcs are branch-and-bottleneck and
the spine is a gauntlet. Hidden Door ships arcs of three to four templates (`narrative-seed-ideal.md` §5.1).
The dungeon's six hand-authored layout templates are the in-repo precedent for a small authored shape
registry (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/layouts.py:35-42`).

### 2. `gk-data/packs/fusion/data/seed/narrative/_registry/arc-shapes.v1.json` (new)

```json
{
  "schemaVersion": 1,
  "registryVersion": 1,
  "shapes": {
    "<shapeId>": {
      "description": "...", "negative": "...",
      "antagonistRules": false,
      "roles": [ { "roleId": "captive", "kind": "required", "allegiance": "independent",
                   "requires": ["source:named", "source:wild", "characterRole:captive"] } ],
      "links": [
        { "linkId": "<shapeId>.<name>", "host": "delve.wild", "storyletKind": "story",
          "requiredChoiceKinds": ["fight"], "rolesUsed": ["captive"],
          "flagsSet": [ { "flag": "<shapeId>.<name>", "kind": "progress" } ],
          "flagsRead": [ "<shapeId>.<name>" ] }
      ]
    }
  }
}
```

| Field | Meaning | Negative clause |
|---|---|---|
| `roles[]` | the arc's persistent cast, cast once when the arc starts and reused by every later link | not per-link roles; a link-local role belongs to that link's storylet, not the shape |
| `roles[].kind`, `requires` | `storylet-vocab`'s role kinds and requirement families; `requires` is an array of `<family>:<value>` strings (Audit 2026-09-19: was an object, which disagreed with the storylet contract and the runtime's string array — `spec-storylet-vocab.md` §3.6). Two values of one family are alternatives; different families all apply | not a score; scoring is the runtime's casting |
| `roles[].allegiance` | the role's side under `character-vocab` | not a disposition band |
| `links[].host` | a `storylet-vocab` host kind | not a room id; the runtime picks the room |
| `links[].storyletKind` | a storylet kind the host admits | not a free choice; must be in the host's `admits` |
| `links[].requiredChoiceKinds` | choice kinds the link's pattern must contain | not the full pattern; the planner picks a fitting pattern |
| `flagsSet[].kind` | `progress` (the link happened) or `outcome` (which result the player got) | not a counter and not a number |
| `flagsRead` | flags a link needs set before it is eligible or that its text may vary on | never a flag set by the same or a later link |

**Link count** is bounded by `arc.linkCount.{min,max}` in `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json`
(3 and 5, from the ideal's "3–5 linked storylets", `narrative-seed-ideal.md` §6.1), never a constant.

**Flag ids** match `^[a-z][a-z-]*\.[a-z][a-z-]*$` — the shape id, a dot, a name. They carry no digit
because the runtime's story ledger stores them as facts and a text condition may name them.

### 3. The v1 shapes

Every link uses a Delve host, because the Delve is the only place with defined hosts
(`storylet-vocab` §3.1; map §9).

| Shape | Links (host · kind) | Persistent roles | Flags | Description | Negative clause |
|---|---|---|---|---|---|
| `rescue` | rumor (`delve.wild` · story) → search (`delve.curio` · curio) → confrontation (`delve.wild` · story, needs `fight`) → aftermath (`delve.shrine` · shrine) | `captive` (required, independent, characterRole captive) | progress: `rescue.heard`, `rescue.found`; outcome: `rescue.freed` | someone is held; the party hears, finds, frees and settles it | not an escort mission; the captive is not a party member until a `recruit` outcome |
| `debt` | bargain (`delve.merchant` · bargain, needs `offer`) → collection (`delve.unknown` · story) → repay-or-betray (`delve.merchant` · bargain) | `creditor` (required, independent, characterRole trader) | progress: `debt.owed`, `debt.called`; outcome: `debt.settled` | a deal made now is collected later | not a loan with an amount; the cost is priced by the runtime |
| `rival` | taunt (`delve.wild` · story) → race (`delve.trap` · trap) → duel (`delve.wild` · story, needs `fight`) | `rival` (required, **antagonist**, source named) | progress only: `rival.met`, `rival.raced` | a fixed three-beat rivalry | not a nemesis: the rival never grows, ranks or remembers encounters (R13) |
| `lost-piece` | fragment (`delve.curio` · curio) → trail (`delve.unknown` · story) → vault (`delve.shrine` · shrine) → revelation (`delve.shrine` · shrine) | none | progress: `lost-piece.found`, `lost-piece.traced`, `lost-piece.opened` | a fragment of the time machine's history, found out of order | not a spine chapter; it is texture that points at the spine |

**Deferred, named:** the failure-branch shape (`exile → gather → return`, for a lost sector) needs world
hosts, which do not exist yet (map §9; `narrative-seed-ideal.md` §11 item 7). It is added as a row when
`storylet-vocab` gains those host kinds.

### 4. Structural rules (each a test)

1. Link count within the budget bounds; link ids unique within the shape and prefixed by the shape id.
2. Every `host` is a `storylet-vocab` host kind and every `storyletKind` is in that host's `admits`.
3. Every `requiredChoiceKinds` set is satisfied by at least one `storylet-vocab` pattern that fits the
   link's kind — so the planner can always allocate one.
4. **Flag closure:** every flag in a link's `flagsRead` is set by an **earlier** link of the same shape.
5. **Role closure:** every `rolesUsed` entry is declared in the shape's `roles`; every declared role is
   used by at least one link; `requires` values resolve in `storylet-vocab` and `character-vocab`.
6. **R13, for a shape with `antagonistRules: true`:**
   - it declares **only `progress` flags** — no link's text or eligibility can vary on how the player
     fared against the antagonist in an earlier link (rule 3, no personal memory);
   - it declares **at most one** antagonist role — no ranked cast (rule 2, no hierarchy);
   - no link may carry a `recruit` consequence targeting the antagonist role, and the shape declares no
     field that changes a character (rule 1, no growth) — the second half is checked by
     `narrative-contract`'s schema test, which has no such field to offer.
   Any shape with an `antagonist` role must set `antagonistRules: true`.

### 5. `gk-data/packs/fusion/data/seed/narrative/_registry/spine-frame.v1.json` (new)

```json
{
  "schemaVersion": 1,
  "registryVersion": 1,
  "afterLast": "arcs-and-texture",
  "fragments": [ { "fragmentId": "fragment.<slug>", "afterChapter": "chapter.<slug>", "after": "none | fragment.<slug>",
                   "description": "...", "negative": "..." } ],
  "chapters": [
    {
      "chapterId": "chapter.<slug>",
      "pieceId": "piece.<slug>",
      "after": "none | chapter.<slug>",
      "description": "...", "negative": "...",
      "cast": ["lead_summoner", "lead_companion", "lead_antagonist"],
      "scenes": [ { "sceneSlot": "<slug>", "beats": 4, "speakers": ["lead_companion", "lead_antagonist", "none"],
                    "teaches": "none" } ]
    }
  ]
}
```

| Field | Meaning | Negative clause |
|---|---|---|
| `pieceId` | the time-machine piece whose recovery opens the chapter (one piece per world won, R3) | not a world id; which world yields which piece is the runtime's `spine-progress` |
| `after` | the chapter this one follows; exactly one chapter has `none` | not a numeric index — order is a chain, never a number |
| `cast` | lead tokens and arc-style role ids the chapter may use | not a speaker list; a cast member may be mentioned without speaking |
| `scenes[].beats` | the scene's beat count, a structural count | not a pacing tunable; bounded by the scene player's own cap |
| `scenes[].speakers` | who may speak in the scene; `none` means narration | not an order of turns |
| `afterLast` | what continues after the final chapter — fixed to arcs and texture (R3) | not a progression ceiling |
| `fragments[]` | Alignment 2026-09-20: the machine's history fragments `npc-story-events/spec-spine-progress.md` §6 lists — `fragmentId` (a structural id, letters and hyphens), `afterChapter` (the chapter that must be reached first) and `after` (the previous fragment in the history, `none` for the first) | not a number: the history order is the `after` chain, never a sort key; not lore — the words are the fragment storylet's |
| `scenes[].teaches` | Owner ruling 2026-09-20 (story is also the tutorial): the `storylet-vocab` §3.8 value this scene teaches, or `none`; copied PLANNED into the spine chapter seed (`narrative-contract` §8) | not a tutorial gate: a teaching scene stays skippable and never blocks play; not a first-session checkpoint (those are `docs/architecture/standalone/spec-first-session-progression.md`'s) |

Rules, each a test: chapter ids and piece ids unique; `after` forms one chain with no cycle and no gap;
every scene's `beats` is at least one and at most `scene.maxBeatsPerScene` read from
`gk-core/data/tuning/story-scene-ui.v1.json` (the scene player's own authored-content bound, currently 6 — read,
never copied); every speaker is in the chapter's cast; **the union of all speakers contains
`lead_antagonist`** once the frame has chapters (R2, the antagonist speaks); `afterLast` is the fixed
value. A test reads the tuning file so a published `story-scene-ui.v{n+1}` moves the bound for free.

**Teaching order (Owner ruling 2026-09-20).** Every scene's `teaches` is a §3.8 value whose `carriers` include `spine`,
or `none`; no value is taught by two scenes; and along the `after` chain the first scene teaching each value appears in
the registry's teaching order (a value earlier in `teaches.v1.json` is never first taught in a later chapter than a
value after it). So chapters 1..7 teach the early loops first — expedition dispatch and the talk verbs before the world
command and the counter-doctrine — while the first-session checkpoints stay that spec's. Values the frame does not
teach are left to storylets (`storylet-selection` §4 priority).

**Seven chapter slots** (owner answer to the open question below, 2026-09-19; Audit 2026-09-19: this
paragraph still said the file ships empty). The frame ships seven chapter rows chained by `after`. Their
`chapterId` and `pieceId` slugs are structural ids that carry no lore (letters and hyphens only); the
pieces' names and every chapter's words are generated by `spine-pipeline` and pass the `ip-censor` release
gate. Each row's scenes, beat counts, speakers and cast are authored structure, written in the build change
under the rules above and reviewed like any registry; until a row has at least one scene the planner
computes no spine cell for it, so nothing in Waves 1–4 waits on that authoring.

### 6. The reader

`adapters/narrative/arc_shapes.py` (new): loads both files fresh, joins `storylet-vocab` and
`character-vocab`, and exposes `shape(id)`, `links_in_order(id)` and `spine_chain()` for the planner and
`narrative-metrics`' arc-integrity metric.

### 7. `decisions.md` row (drafted; appended in the build change — map §11 item 4, with `narrative-contract`)

> **The spine is a generated seed kind with a planned frame** (owner rulings R1–R3, 2026-09-19). The
> chapter list, each chapter's piece, scenes, beat counts and cast are an authored frame
> (`gk-data/packs/fusion/data/seed/narrative/_registry/spine-frame.v1.json`); the model writes the scenes inside it; generated
> scenes load as data through the runtime programs' loader, while the hand-authored Rift prologue keeps
> story-scene decision S3.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_narrative_arc_shapes.py -q
```

## Project structure

```text
gk-data/packs/fusion/data/seed/narrative/_registry/arc-shapes.v1.json     (new) four shapes
gk-data/packs/fusion/data/seed/narrative/_registry/spine-frame.v1.json    (new) contract + seven chapter slots (Audit 2026-09-19)
gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json             block `arc.linkCount`
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/arc_shapes.py   (new)
gk-forge/tools/seedsmith/tests/test_narrative_arc_shapes.py           (new)
```

## Code style

As `storylet-vocab`. The R13 checks live in one function per rule so a failure names the rule number.

## Testing strategy

| Test | Asserts |
|---|---|
| `every_shape_has_description_and_negative` | both non-empty |
| `link_count_within_budget_bounds` | bounds read from a fixture budget in unit tests and the real file in one load test |
| `hosts_and_kinds_are_legal` | rule 2 |
| `required_choice_kinds_are_allocatable` | rule 3 against the real pattern registry |
| `flags_read_are_set_earlier` | rule 4; a crafted shape reading a later flag fails |
| `roles_close` | rule 5 both directions |
| `rival_has_only_progress_flags` | R13 rule 3; a crafted antagonist shape with an `outcome` flag fails |
| `antagonist_shape_has_one_antagonist_role` | R13 rule 2 |
| `antagonist_role_requires_antagonist_rules` | a shape with an antagonist role and `antagonistRules: false` fails |
| `spine_chain_is_single_and_acyclic` | fixture frames: a cycle, a gap and two roots each fail |
| `scene_beats_within_tuning_cap` | cap read from `story-scene-ui.v1.json` |
| `antagonist_speaks_when_chapters_exist` | fixture frame without `lead_antagonist` among speakers fails (R2) |
| `frame_teaching_order` | every scene `teaches` is a spine-carried §3.8 value or `none`; no value twice; first teachings follow the registry's order along the `after` chain (Owner ruling 2026-09-20) |
| `frame_has_seven_chapter_slots` | the committed frame has exactly seven chapter rows in one `after` chain — a declaration pinned with its reason (the owner's seven-piece answer, 2026-09-19), not a population |
| `chapter_row_without_scenes_plans_nothing` | a fixture row with an empty `scenes` list loads and yields no spine cell |
| `shape_ids_pinned` | the four v1 shape ids pinned as a declaration; a new shape is a reviewed change |

No test counts arcs or chapters in a corpus.

## Boundaries

- **Always:** Delve hosts only in v1; progress-only flags for antagonist shapes; bounds from budget and
  tuning files.
- **Ask first:** a new shape; a shape using hosts that do not exist yet.
- **Never:** a numeric chapter index; a flag that lets an enemy remember the player; a chapter list chosen
  by a model.

## Success criteria

- [ ] Both files exist and load; every rule in §4 and §5 has a passing test and a failing fixture.
- [ ] The rival shape passes all three R13 checks.
- [ ] Link and beat bounds come from the budget and the story-scene tuning file.
- [ ] The spine frame holds seven chapter slots in one chain (owner answer, 2026-09-19); rows without scenes
      plan no spine cell.

## Open questions

> **Answered by the owner 2026-09-19: seven pieces.** The spine frame has **seven chapter slots**, one per
> time-machine piece. The pieces' names and each chapter's content are generated like the rest of the spine
> (ruling R1, fully generated) and pass the `ip-censor` release gate; the count is fixed structure, not a
> tunable. The question below is kept for the trail.

1. **How many time-machine pieces — and so how many spine chapters — does the main story have, and what
   are they?** R3 fixes one chapter per piece and "finite, then endless", but no document or code names
   the pieces or their count (searched `docs/` and `src/` this session; the only mention is the premise in
   `docs/guide/the-game.md` line 29). This is lore, not a derivable number. Until it is answered the frame
   ships empty and only `spine-pipeline` (Wave 5) waits on it. Recommended default: the owner names the
   pieces for the first worlds only; chapters are keyed by id and chained by `after`, so appending later
   chapters never invalidates earlier ones.

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | medium | The owner answered the open question (seven pieces) but the Objective, §5, tests and success criteria still shipped an empty frame (DESIGN-GATE §3 rule 6, propagation) | fixed (seven slots; slot without scenes plans nothing) |
| 2 | medium | `roles[].requires` was an object, disagreeing with the storylet contract and the runtime | fixed |
| 3 | low | Each of the seven chapters' scenes, beats and cast is authored structure with no named author or task | deferred — a plan task for `tasks/narrative-seed-todo.md` |
| 4 | low | `maxBeatsPerScene` read from `gk-core/data/tuning/story-scene-ui.v1.json` (value 6 today) — correctly read, never copied | verified |

## Cross-lane alignment (2026-09-20)

Owner ruling 2026-09-20 (story is also the tutorial): the spine frame's scenes carry `teaches`, and the frame's chain
order follows the `teaches` registry's teaching order, so early chapters teach the first loops. The runtime maps a
scene's `teaches` to story-scene's `SceneBeat.teaching` (`npc-story-events/spec-scene-script-loader.md` §1); tutorial
beats stay skippable and never gate play.

- Alignment 2026-09-20: the frame gains `fragments[]` (§5), the seed-side source of the history fragments
  `npc-story-events/spec-spine-progress.md` §6 reads. Rules, each a test: fragment ids unique; `after` forms one chain
  with no cycle; every `afterChapter` is a chapter of this frame. The planner allocates one storylet work item per
  fragment row (`narrative-contract` §5 `fragment`).

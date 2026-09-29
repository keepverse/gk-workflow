# Spec: `spine-pipeline`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `spine-pipeline` · **Map row:** 21 · **Wave:** 5 (last)
**Depends on:** `arc-pipeline`, `character-pipeline`, `names-registry` · **Model calls:** yes
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §6.1 (the spine), §6.5b, §6.8, §11 item 3
**Sibling rulings:** R1 (spine fully generated), R2 (the Rotwright speaks), R3 (finite chapters keyed to time-machine pieces), R8–R11 (names are tokens), R13
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Generate the main story: one **spine chapter** per chapter slot of the planned spine frame, each a
sequence of scenes emitted as **data** with keyed, tokenised text, in which the three leads speak — the
Rotwright included (R2). The spine is a seed like any other: regenerated, never hand-edited, reviewed
(R1). What keeps it coherent is structure the planner owns — the chapter list (one per time-machine piece,
R3), each chapter's scenes, beats, speakers and cast; the model writes the words inside that frame
(ideal §6.1).

Because it is lead-tier text, each chapter is generated as **two complete candidates**, and the reviewer's
pick is recorded as a verdict, never an edit (ideal §11 item 3). Texture content gets one draft; the spine
is where the second candidate pays.

## Design

### 1. The frame (planned, never generated)

From `arc-shapes`' spine frame, through `narrative-planner` §5, each chapter work item carries as PLANNED
`const`: the chapter slot and its time-machine piece (`pieceId`; the runtime's `spine-progress` decides when a
recovered piece opens the chapter — Audit 2026-09-19: this sentence named "world facts that make it
eligible", a field the frame does not have, `spec-arc-shapes.md` §5), the scene count, and for each scene its
beat count and the speaker slot of every beat (a lead token, a planned character token, or narration). The
frame has seven chapter slots (owner answer, 2026-09-19); a slot with no authored scenes yet plans no work. Speakers are tokens
(`{lead_summoner}`, `{lead_companion}`, `{lead_antagonist}`, `{c_<characterId>}`), never display names.

After the last chapter, arcs and texture continue; a finite spine is not a progression ceiling (R3).

### 2. Calls per candidate

For each of `spine.candidates` candidates (`a`, `b`), in order:

1. **Chapter call** — `title` and `synopsis` (AUTHORED, keyed), shown the frame, the lore packet (cast
   tokens with descriptions and feature tags, glosses for the chapter's places, the counter-doctrine context
   the frame supplies) and the previous chapter's **accepted** synopsis, if any (one chapter back — bounded
   state, `seedsmith/spec-workflow-runtime.md` §2.2).
2. **Scene calls** — one per scene, writing the text of every beat of that scene in order, each beat's
   speaker fixed as `const`. The call sees the chapter's title and synopsis from the same candidate and the
   previous scene's last beat, so a candidate is one coherent draft, never a splice of two. Owner ruling 2026-09-20
   (story is also the tutorial): the scene's `teaches` value from the frame (`arc-shapes` §5) is PLANNED `const`, shown
   with its description and negative clause so the scene's story sets up the lesson; the teaching sentence itself is
   the registry's authored `teachingLine` (`storylet-vocab` §3.8), never written by the model, and the runtime shows it
   on the scene's last beat.

Every text field runs `narrative-validators`' text battery (script, echo, collision, token closure, digit,
length, literal name, unknown entity, out-of-world, round-trip render), plus two spine rules:

| Defect | Rule |
|---|---|
| `speaker-closure` | each beat's text belongs to its planned speaker; the reply cannot add, drop or reorder beats |
| `enemy-memory` | the Rotwright's lines react to the player's **strategy** and the world, never to a personal past encounter with him (R13 rule 3; `npc-story-events-ideal.md` §6.12 "The voice") |

Semantic markup is limited to the closed tag set of `token-grammar` (a reviewed widening of the item seed
contract's "markup forbidden" rule to semantic tags only, never HTML or styling; map §11 item 3). At most
two repairs per call, then that candidate is `unresolved`; the other candidate proceeds. Both calls are
`narrative-contract` §9's `spine-chapter` and `spine-scene` schemas (Audit 2026-09-19: the contract lacked
`synopsis` and the chapter call); each carries the root `blocked` escape, and a blocked reply ends that
candidate `blocked`, never retried.

### 3. Pick, then commit

A spine chapter reaches the corpus only after a human pick:

1. A run writes both candidates as **pending** rows in the run ledger — never into the corpus.
2. `review-render` renders both candidates side by side (spine chapters are a census, never sampled).
3. The reviewer records `pick` with candidate `a` or `b`, or `reject` with a reason, in the verdict queue.
4. `narrative spine commit` emits the picked candidate through `narrative-emit` (canonical JSON, provenance
   naming the candidate and the verdict row, `revision` bumped on change). The unpicked candidate stays in
   the run ledger, never deleted and never merged.
5. A `reject` of both regenerates the chapter with the reason named in the chapter brief.

No text is edited by hand at any step, so R1 holds: the shipped chapter is exactly a generated candidate.

### 4. Scenes as data

Today's authored scenes are TypeScript literals — the prologue is the `RIFT_PROLOGUE_SCRIPT` constant
(`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts:105`), typed by `SceneBeat` at line 32 — and lingui accepts only compile-time literal messages
(`gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts:13-19`). The spine therefore ships as **data**:
each beat carries its speaker token, its text key and its keyed ICU message. Loading that data and turning
keys into literal `msg` descriptors is the runtime's — `npc-story-events`' `scene-script-loader` and
`narrative-text` (the lingui codegen bridge, ideal §6.8), played by story-scene's `StorySceneHost` (map §7).
This module builds no loader, no player and no second translation path; its output shape is
`narrative-contract`'s spine chapter schema.

Draft `decisions.md` row, appended in the change that lands this module (map §11 item 4):

> **The spine is a generated seed kind; generated scenes are data** (narrative-seed, 2026-09-19; owner
> ruling R1). Spine chapters are regenerated, never hand-edited, and shipped as the reviewer's pick of two
> generated candidates. Generated scenes load as data through the runtime programs' scene loader; the
> hand-authored Rift prologue keeps story-scene decision S3 (a typed TypeScript script module).

### 5. Transport and provenance

Model through the config layer only (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:47`, `.env` keys at
lines 69–77); no literal (R6). Constrained decoding with the beat structure pinned; reasoning off;
`narrative preflight` first. Graph per chapter in
`tools/seedsmith/seedsmith/workflow/graphs/narrative_spine.py` (new); checkpointed; TRANSIENT replays,
QUALITY regenerates with the defect named. Provenance: prompt versions, `packetHash`, the frame version,
candidate id, verdict row, attempts.

### 6. Call budget

`docs/research/ai-native-generation/README.md` §9 (no vote: prose only), via the call-shape table
(`narrative-planner` §7). `s` = the chapter's planned scene count; `c = spine.candidates`:

```text
base per chapter  = c x (1 chapter call + s scene calls)   = 2 + 2s   at c = 2
worst per chapter = c x 3 x (1 + s)                         = 6 + 6s   at c = 2
```

The number of chapters is the spine frame's slot count, a reading printed by the dry run.

### 7. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `spine`.

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `spine.candidates` | candidates per chapter | 2 | Ghostwriter's writer-picks-one-of-two, for lead-tier text only (ideal §11 item 3) |
| `spine.temperaturePermille` | ‰ | 600 | two candidates only help if they differ |

**Structural (commented):** two repairs; one chapter and one scene of continuity context; commit only after
a pick.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_spine_pipeline.py -q
cd tools\seedsmith; python -m seedsmith narrative spine run --dry-run                # DEFAULT: every prompt for both candidates, call count, no call
cd tools\seedsmith; python -m seedsmith narrative spine run --write --chapter <slot>
cd tools\seedsmith; python -m seedsmith narrative review render --batch <runId> --kind spine
cd tools\seedsmith; python -m seedsmith narrative spine commit --run <runId>         # emits picked candidates only
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/pipelines/spine.py            (new) chapter and scene nodes, pending rows, commit
tools/seedsmith/seedsmith/adapters/narrative/pipelines/prompts/spine.py    (new) prompts, PROMPT_VERSIONs, schemas with pinned beats
tools/seedsmith/seedsmith/workflow/graphs/narrative_spine.py               (new) graph wiring only
tools/seedsmith/tests/test_narrative_spine_pipeline.py                     (new)
```

## Code style

```python
def commit_chapter(chapter_id: str, run: "RunLedger", verdicts: "VerdictQueue") -> "EmitResult | NotPicked":
    """Emits exactly the picked candidate's rows through narrative-emit. NotPicked when no pick
    verdict exists. Never merges candidates, never edits text."""
```

## Testing strategy

Scripted transport fake that raises when exhausted or called unexpectedly.

| Test | Asserts |
|---|---|
| `dry_run_makes_no_call` | every chapter and scene prompt for both candidates renders with a transport that raises |
| `beats_and_speakers_are_const` | the scene schema pins beat count and speakers; a reply cannot add or reorder beats |
| `speakers_are_tokens` | no rendered prompt or emitted beat contains a lead's display string |
| `candidates_are_not_spliced` | candidate b's scene calls see candidate b's chapter call only |
| `nothing_commits_without_a_pick` | `spine commit` with no verdict emits nothing and reports `NotPicked` |
| `pick_emits_exactly_one_candidate` | after `pick a`, the corpus holds candidate a byte for byte; b stays in the ledger |
| `antagonist_personal_memory_rejected` | a Rotwright line recalling a past personal encounter fails `enemy-memory`; a line about the player's strategy passes |
| `markup_outside_closed_tags_rejected` | an HTML or styling tag fails token closure; a closed semantic tag passes |
| `unresolved_candidate_does_not_block_the_other` | candidate a failing its repairs leaves candidate b proceeding |
| `call_bounds` | a scripted chapter with s=3 makes 8 calls clean and 24 at worst |
| `chapter_schema_is_the_contracts` | the chapter call writes exactly `title` and `synopsis`, the scene call exactly the beats' lines (Audit 2026-09-19) |
| `slot_without_scenes_plans_nothing` | a frame slot with no scenes yields no chapter work item and no call |
| `no_model_literal` | model from `load_config`; the guard test passes |

No test asserts the number of chapters or any generated text.

## Success criteria

1. Every committed spine chapter is exactly one generated candidate chosen by a recorded pick, inside a
   frame the planner fixed.
2. The Rotwright speaks, as a token, and never remembers the player personally.
3. Scene text is keyed, tokenised data ready for the runtime loader; no TypeScript is generated here.
4. The `decisions.md` row in §4 is appended in the change that lands this module.
5. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** stay inside the planned frame; generate two complete candidates; commit only a picked one;
  emit scenes as data with keys and tokens.
- **Ask first:** a third candidate; changing the spine frame's shape (that is `arc-shapes`); letting the
  chapter list grow at runtime (R3 fixes it to time-machine pieces).
- **Never:** hand-edit or merge a candidate (R1); name a lead by display string; build a scene loader,
  player or translation path here; let the antagonist remember a personal encounter.

## Open questions

None.

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | medium | `synopsis` and the chapter call were absent from the contract | fixed (contract §8–§9) |
| 2 | low | "World facts that make it eligible" is not a frame field | fixed (`pieceId` via runtime `spine-progress`) |
| 3 | low | `blocked` unstated; seven slots not reflected | fixed |

## Cross-lane alignment (2026-09-20)

Owner ruling 2026-09-20 (story is also the tutorial): each spine scene work item carries its frame `teaches` value as
PLANNED `const` (§2); the model writes the story around it, never the teaching sentence. The emitted chapter's
`scenes[].teaches` follows `narrative-contract` §8.

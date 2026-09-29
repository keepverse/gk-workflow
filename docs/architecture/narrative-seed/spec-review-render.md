# Spec: `review-render`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `review-render` · **Map row:** 14 · **Wave:** 3
**Depends on:** `narrative-contract`, `names-registry` (the choice type it prints is passed in by the caller from `narrative-validators`' classifier, same wave; Audit 2026-09-19) · **Model calls:** none
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §6.5 (open-loop quality), §11 items 2 and 3
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

**A reviewer reads what a player reads.** A storylet containing `{role_captive}` and `{reward}` reads as a
form, not a scene (ideal §11 item 2), so a reviewer shown the raw seed judges the template instead of the
text. This module renders a stratified sample of narrative seeds with **two to three sample casts** and
every placeholder filled, prints each storylet's **computed choice type** and each option's **outcome
profile**, and records the reviewer's verdict against the sample. It never edits a seed.

It is the open-loop half of the program's quality story: voice, tone, lore fit and "is this choice
interesting" have no machine answer (seedsmith P3), so they go to a person. A verdict that finds a new,
mechanically checkable defect becomes a new validator or metric, which is the loop that makes review effort
fall over time (`seedsmith/spec-pipeline.md` §6).

## Design

### 1. Sampling — reuse, never a second sampler

Samples come from `stratified_sample` (`gk-forge/tools/seedsmith/seedsmith/sampling/__init__.py:38`), seeded from
`metric id + corpus revision` (`corpus_revision`, `gk-forge/tools/seedsmith/seedsmith/sampling/__init__.py:20`), so a
reviewer can re-read exactly last week's sample and diff their own judgement. Every non-empty stratum gets
at least one sample. Strata:

| Seed kind | Stratum |
|---|---|
| storylet | planner cell (host × kind × climate) |
| character | voice register × side — the register is the axis Ghostwriter found acceptance varies on (ideal §5.1) |
| arc | arc shape |
| spine chapter | census: every chapter is rendered, never sampled (a small, high-risk population — the passive-tree review's tier-1 census rule, `gk-forge/tools/seedsmith/seedsmith/adapters/trees/review/sample.py`) |

Generated rows are already marked for review by the open-loop helpers (`NEEDS_REVIEW_FIELD`,
`gk-forge/tools/seedsmith/seedsmith/pipeline/open_loop.py:40`); this module reads that marker to find the batch.

### 2. Sample casts

A **cast** assigns a display value to every token a seed declares. Each sampled seed is rendered once per
cast, `review.castsPerSample` casts (starting 3; the map allows two to three).

| Token family | Filled with | Source |
|---|---|---|
| `{lead_summoner}`, `{lead_companion}`, `{lead_antagonist}` | the live display string | the names registry (`gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`, new) |
| `{c_<characterId>}`, `{c_<characterId>_epithet}` | that character's generated name and epithet | the committed character seed |
| `{role_<roleId>}` | a different committed character per cast whose role and tags satisfy the role's `requires[]`; when none exists, a labelled stand-in `[a <role> — no cast yet]` | the character corpus, picked in the seeded order `blake2b(seedId | roleId | castIndex)` |
| `{place}` | a host display name from the host-kind registry, varied per cast | `storylet-vocab` |
| `{supply}` | a supply tag display name from the `use` choice's `param` | `storylet-vocab` choice kinds (`use` → `supplyTag`). Audit 2026-09-19: the supply is the choice's argument, not its condition |
| `{reward}`, `{cost}` | a **band label**, never a number: `[reward: <dropBand> <consequence>]`, `[cost: <stock> at room power]` | the outcome's own `dropBand` and consequence |

**Why rewards render as labels.** This tool never resolves a magnitude: principle 2 forbids any generation
step from picking a number, and a reviewer shown `gain 42 souls` would review a number the runtime never
promised. The label tells the reviewer the size class and the kind of payoff, which is what the text must
be consistent with.

Casts are chosen so that at least two casts differ in every grammatical feature tag the registry carries
(`article`, `gender`, `number`) where the corpus offers such characters, so an agreement error in an ICU
`select` shows up in the render. Rendering uses `token-grammar`'s parser and renderer, the same one
`narrative-validators` uses for the round-trip check; this module builds no second renderer.

### 3. What one rendered storylet shows

```text
storylet.curio-fire-004   cell: delve-curio × curio × fire   choice type: dilemma-upside   rev 2
cast 1 of 3 ─────────────────────────────────────────────────────────────────────────────
  The Charred Reliquary
  Ashvine Mother kneels by a cracked brazier. "Feed it, and it will answer," she says.
  [1] Feed the brazier               interact   good(loot, occasional) · bad(none)
  [2] Offer a Sunleaf                use:herbs  good(loot, seldom)             requires: herbs
  [3] Walk on                        leave      nothing
  results:
    [1 good] The flames part around a sealed box. [reward: occasional loot]
    [1 bad]  The brazier spits. Everyone steps back singed.
    ...
cast 2 of 3 ─────  (same seed, second cast)
validators: mechanically valid (tier 2)   lore packet: 6 allowed entities   prompt: storylet-text/3
```

For a character: name, epithet, bio, its anchors and lexicon, then one line per required (context, band)
pair, rendered in each cast. For an arc: premise, then each link as above in order, with the flags each
link sets and reads. For a spine chapter: every scene beat in order with its speaker, and, where two
lead-tier candidates exist, both side by side.

The render is text for the terminal and a self-contained HTML page for longer sittings; both come from one
render model, so they cannot disagree.

### 4. Verdicts — recorded, never an edit

A verdict row, one per reviewed item, is appended to `data/seed/narrative/_review/<batch>.json` (new). The
shape follows the passive-tree review's committed verdict queue
(`gk-forge/tools/seedsmith/seedsmith/adapters/trees/review/verdict_queue.py`), so no second, incompatible schema
exists:

| Field | Vocabulary | Is not |
|---|---|---|
| `seedId`, `revision` | the reviewed seed and the revision rendered | not a new id; a verdict never renames |
| `verdict` | `accept · reject · pick` (closed) | not a score; there is no rating scale |
| `reasonTag` | closed: `voice · tone · lore · choice-interest · grammar · name-quality · other` | not free prose; the free text goes in `reason` |
| `reason` | reviewer text; required when `verdict` is `reject` | never copied into a seed |
| `candidate` | for lead-tier seeds with two candidates, which one was picked (`a · b`), else `none` | not an edit; the pick selects a generated candidate |
| `by`, `utc` | reviewer, timestamp | provenance, not content |

**A rejection never edits the seed.** It feeds three places: `narrative-metrics`'
`Narrative/RegisterAcceptance` reading; a regeneration work order for that seed (the generator's brief
gains the reviewer's reason as a named constraint, and the seed's `revision` bumps through `narrative-emit`);
and, where the defect is mechanically checkable, a new validator or metric. A `pick` on a lead-tier seed
records which generated candidate ships; the other candidate is kept in the run ledger, never deleted and
never merged (R1 keeps the spine generated).

The verdict file is authored (a person's record), not generated output, so it is outside the generated-seed
rule; it is still append-only, and a changed verdict is a new row, never a rewrite.

### 5. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `review`.

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `review.castsPerSample` | casts | 3 | the map's two to three; three lets two casts differ in a feature tag while a third checks a stand-in role |
| `review.samplePerBatch.<kind>` | seeds | storylet 24, character 12, arc all, spine all | sized to one reviewer sitting (ideal §6.7: review is the bottleneck); first values are starting shapes |

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_review_render.py -q
cd tools\seedsmith; python -m seedsmith narrative review render --batch <runId> [--kind storylet] [--html out.html]
cd tools\seedsmith; python -m seedsmith narrative review verdict --batch <runId> --seed <seedId> --verdict reject --reason-tag voice --reason "..."
cd tools\seedsmith; python -m seedsmith narrative review status --batch <runId>     # rendered, reviewed, pending per stratum
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/review/__init__.py    (new)
tools/seedsmith/seedsmith/adapters/narrative/review/sample.py      (new) strata over sampling.stratified_sample
tools/seedsmith/seedsmith/adapters/narrative/review/casts.py       (new) §2 cast builder
tools/seedsmith/seedsmith/adapters/narrative/review/render.py      (new) one render model, text and HTML views
tools/seedsmith/seedsmith/adapters/narrative/review/verdicts.py    (new) append-only verdict rows
data/seed/narrative/_review/<batch>.json                            (new) verdict queue per batch
tools/seedsmith/tests/test_narrative_review_render.py              (new)
```

## Code style

```python
def render_sample(seed: "Mapping[str, Any]", casts: "Sequence[Cast]", *, choice_type: "ChoiceType | None") -> RenderModel:
    """Pure: the same seed, casts and registry produce the same bytes. No number is ever formatted
    into the output; reward and cost slots render as band labels."""
```

## Testing strategy

Fixture corpus and fixture names registry; the model transport stubbed to raise.

| Test | Asserts |
|---|---|
| `render_is_deterministic` | two renders of the same batch are byte-identical |
| `sample_reuses_stratified_sample` | the sample equals `stratified_sample` over the §1 strata with the same seed key; every non-empty stratum appears |
| `spine_is_a_census` | every spine chapter in the batch is rendered |
| `no_digit_in_any_render` | a rendered storylet with `{reward}` and `{cost}` contains no decimal digit outside ids and the revision header |
| `casts_differ_in_a_feature_tag` | with a fixture corpus offering both, two casts differ in `gender` or `number` |
| `unfilled_role_renders_a_labelled_stand_in` | a role with no matching character renders the stand-in label, never an empty string |
| `storylet_shows_choice_type_and_profiles` | the header carries the classifier's type; each option lists its (ordinal, consequence) profile |
| `lead_tier_shows_both_candidates` | a two-candidate spine chapter renders both side by side |
| `verdict_is_append_only` | recording a second verdict for a seed appends; the first row is unchanged |
| `reject_requires_a_reason` | a `reject` without `reason` is refused |
| `verdict_never_touches_the_seed` | after any verdict, every seed file's hash is unchanged |
| `verdict_vocabularies_are_pinned` | `verdict` has three members and `reasonTag` seven (declarations; a new tag is a reviewed change) |

## Success criteria

1. A reviewer can render any batch and read every sampled seed as a player would, in two to three casts.
2. Rendered text never contains a number the runtime would resolve.
3. Verdicts land in the committed queue, append-only, and never change a seed file.
4. `Narrative/RegisterAcceptance` reads its rates from these verdicts.
5. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** reuse `stratified_sample`; render through the one grammar renderer; show the choice type and
  outcome profiles; record verdicts append-only.
- **Ask first:** a verdict scale beyond `accept · reject · pick`; a new `reasonTag`; letting a model
  pre-screen samples (a model judge never passes or fails one item — ideal §5.2b).
- **Never:** edit a seed from a verdict; render a resolved magnitude; build a second sampler or renderer;
  treat a verdict count as a pass.

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
| 1 | low | `{supply}` was filled from the condition; it is the `use` choice's `param` | fixed |
| 2 | low | The choice-type input came from `narrative-validators` without saying so | fixed (header) |
| 3 | low | Verdicts append-only, never edit a seed, reuse `stratified_sample` (`sampling/__init__.py:38`) | verified |

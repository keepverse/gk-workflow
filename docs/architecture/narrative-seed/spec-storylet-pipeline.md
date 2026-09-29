# Spec: `storylet-pipeline`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `storylet-pipeline` · **Map row:** 18 · **Wave:** 5
**Depends on:** `narrative-planner`, `narrative-validators`, `narrative-emit`, `lore-packet`, `model-config-resolve` · **Model calls:** yes
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §6.2 (the storylet contract), §6.6 (pipelines and vote set), §6.7 (call cost)
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Generate one storylet per planned work item in **two narrow calls**: a **structure** call that fills the
planned choice slots with roles, per-slot conditions and outcomes (three samples, voted per slot on
`ordinal` and `consequence`), then a **text** call that writes the name, situation, choice labels and
outcome results with the resolved structure shown as `const`. Structural validators gate the structure
before any prose is written; text validators gate the prose with at most two named repairs.

Structure and text are separate calls because structure is a handful of enum picks where position bias
matters and voting is cheap, while text is prose where voting means nothing (ideal §6.6; "one judgement
per call", `docs/research/ai-native-generation/README.md` §3). They are one module because they share one
planner cell and one emit and cannot ship apart (map §4).

This is the **one storylet generator for every place** (map §2 principle 15). The Delve's events are
regenerated through it (`delve-event-regen`); no second storylet generator exists beside it.

## Design

### 1. The structure call

**Shown to the model:** the lore packet (`lore-packet`), the planned `const` values (id, host, kind,
climate, arc link if any, the choice slots with each slot's choice kind and outcome count), and the closed
vocabularies inlined from the registries — never cited by filename (briefkit's rule,
`gk-forge/tools/seedsmith/seedsmith/briefkit/__init__.py:1-6`).

**Written by the model** (every field VALIDATED against a closed vocabulary; the schema pins PLANNED
fields as `const`):

| Field | Vocabulary | Voted |
|---|---|---|
| `roles[]` — `{roleId, kind, requires[]}` | role kinds and requirement tags from `storylet-vocab`; `roleId` from the token grammar's role id form | no — taken from the carrier sample (§2) |
| per slot `condition` | the condition vocabulary (`storylet-vocab`); `none` legal and required on unconditioned kinds | no — carrier |
| per slot, per outcome `ordinal` | `good · mixed · bad · nothing` (`gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json:52-55`) | **yes** |
| per slot, per outcome `consequence` | the consequence kinds and, for `relation.shift`, the relation fact kind (`storylet-vocab` §3.5). Owner ruling 2026-09-19 (round 3): the call writes `consequence.kind` and `consequence.param`; the voted value is the `(kind, param)` pair; `consequence.ref` is filled deterministically after the vote and never appears in the call (`spec-narrative-contract.md` §5, §9). Audit 2026-09-19: the per-item `kind` enum offers only kinds whose `ref` this item can fill (no `story.flag`, `quest.offer` or `scene.play` without the planned flag, quest or scene); a position the planner pinned to a `story.flag` (arc links, `spec-arc-pipeline.md` §3) is `const` in all three samples and leaves the vote | **yes** |
| per outcome `effects[]` | zero to two `{family, powerBand}` — an atom family and a power band, never a number (Audit 2026-09-19: named `effect` here, `effects[]` in the contract) | no — carrier |
| per outcome `dropBand` | the five `dropBand` members | no — carrier |

**Why the vote set is `ordinal` and `consequence`.** They decide fairness and mechanics: an ordinal read
wrong inverts a choice (a `bad` shipped as `good`), and a consequence read wrong hands the runtime a
different mechanic. Both are the fields the structural validators judge. `dropBand` and `powerBand` shift a
size inside a band ladder the runtime resolves through `P(Θ)`, and the dominance and choice-type rules do
not read them; they stay single-sample from the carrier, permuted like every enum. A near-zero disagreement
rate on a voted field is the signal to drop it from the vote set; a high one is the signal to rewrite its
description (`Narrative/VoteDisagreement`).

**Positional voting needs fixed positions.** The planner fixes the slot count and each slot's outcome
count from the choice pattern, so `slot[i].outcome[j].ordinal` is the same question in all three samples —
the fix for the dungeon adapter's outcome count pinned at 2
(`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:236`, reason at lines 227–235). `leave` has one
outcome whose ordinal is `nothing`, fixed by the pattern.

**Permutation.** Every enum in the per-call schema is reordered with `order_for(storyletId, fieldPath,
sampleIndex)` (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26`) — the walk the dungeon
adapter already does (`_permute_schema_enums`, `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:67`).
`sampleIndex` is inside the seed, so three samples see three different orders
(`docs/research/ai-native-generation/README.md` §2).

### 2. Resolving three samples into one structure

1. **Vote** every `(slot, outcome, field)` position in the vote set with `resolve_vote`
   (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26`): 3-0 `high`, 2-1 `split` with the
   minority recorded, 1-1-1 `unresolved`.
2. **Any `unresolved` position makes the storylet `unresolved`.** It is recorded with the position and the
   three values and is not retried: a genuine three-way split is an ambiguity signal, and re-drawing it
   spends calls to hide the signal. The coverage metric shows the gap; the fix is a description or brief
   change, which stales the item for the next run.
3. **Carrier sample.** The non-voted fields come from the lowest-index sample whose voted values equal the
   resolved values at **every** position. No field is spliced from two samples, because a consequence and
   its effect family chosen by different samples need not agree. When no sample matches every resolved
   position, the draw fails with the named defect `no coherent sample` and counts as a structure QUALITY
   retry.
4. **Fill `ref`.** `consequence.ref` is computed from the resolved structure and the plan by
   `narrative-contract` §5's derivation rule (Audit 2026-09-19: the step between the vote and the gate was
   unstated, and the contract used to call `ref` PLANNED although it depends on the model-written roles).
5. **Structural gate.** The resolved structure runs `narrative-validators`' structural battery
   (choice count, one `leave`, no lose-lose, no dominated choice, choice type, conditional value,
   `enemy-consequence`, `consequence-ref-unfillable`). A defect triggers a new three-sample draw with the
   defects named in the brief — at most **two** structure retries, then `unresolved`.

**`blocked`.** Every call schema carries the root `blocked` escape (`spec-narrative-contract.md` §9). A sample
that sets it ends the work item `blocked` with its reason — a terminal ledger row, never a retry and never a
vote input (Audit 2026-09-19).

### 3. The text call

**Shown to the model:** the lore packet, the resolved structure as `const` (roles, conditions, outcome
ordinals and consequences, never a band's size), and the token grammar with each token's description and
negative clause.

**Written by the model** (AUTHORED, keyed): `name`, `situation`, per-choice `label`, per-outcome `result`.
Text keys are assigned by `narrative-contract`'s key rule, never by the model.

**Validated by** `narrative-validators`' text battery (script, echo, collision, token closure, digit,
length, literal name, unknown entity, out-of-world, round-trip render) plus `role-undeclared`, with
`context["allowedEntities"]` filled from the item's lore packet; `names-good-option` is recorded as a soft
signal for review, never repaired (Audit 2026-09-19, `spec-narrative-validators.md` §2). `name_collision` receives every committed storylet name except this seed's own
(`takenNames`, `gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py:69`). A defect triggers a repair
naming the field, the value and the fix — at most **two** repairs, then `unresolved`.

The text call is single-sample: it has no enum to vote on, and prose votes mean nothing (ideal §6.6).

### 4. Transport, retries, runtime

- **Model** resolved only through seedsmith's config layer — `.env` `SEEDSMITH_LLM_MODEL` over
  `seedsmith.toml` over the default (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:47`, `.env` keys at
  lines 69–77); no literal (R6). Constrained decoding on; reasoning off
  (`seedsmith/spec-quality-gates.md` §2.6); `narrative preflight` proves decoding is enforced with one real
  call before the run (README §4).
- **Two retry intents** (`seedsmith/spec-workflow-runtime.md` §2.4): TRANSIENT failures replay from the
  checkpoint with no new generation; QUALITY failures are new generations with the defect named. The bound
  of two is the structural constant of `spec-workflow-runtime.md` §2.3, commented, never a tunable.
- **Workflow.** One graph per storylet, wired in `tools/seedsmith/seedsmith/workflow/graphs/narrative_storylet.py`
  (new) — the only module that imports LangGraph for this pipeline (`spec-workflow-runtime.md` §2.1). Node
  bodies are plain functions in the adapter. Fan-out over the work order uses the existing runner's bounded
  concurrency (`MAX_WORKERS`, `gk-forge/tools/seedsmith/seedsmith/workflow/runner.py:31`).
- **Validate before accept** (`seedsmith/spec-pipeline.md` §3.5): drafts are written to a scratch location;
  only a seed that passed both gates reaches `narrative-emit`, which writes canonical JSON, provenance and
  the run ledger. A non-stale seed is skipped, not regenerated.
- **CoVe stays unbuilt** (`seedsmith/spec-quality-gates.md` §2.3). No tier-3 check runs here.

### 5. Provenance this pipeline hands to emit

`promptVersions` (`storylet-structure/<n>`, `storylet-text/<n>`), `packetHash`, the plan item id, the
resolved model id from the config (never a literal), per-position vote `confidence` and `minorityValues`,
the carrier sample index, attempts per call, and the computed choice type. `narrative-emit` owns the
canonical shape, staleness and the `revision` bump.

### 6. Call budget

`docs/research/ai-native-generation/README.md` §9, as declared once in the call-shape table
(`narrative-planner` §7):

```text
base per storylet  = 2 pipelines + 1 voted call x (3 - 1)       = 4
worst per storylet = 3 structure draws x 3 samples + 3 text calls = 12
batch              = S x 4 base, + heal allowance, <= S x 12 worst
```

Illustration, not an assertion: the ideal's first batch of 84 storylets is 336 base calls. `narrative
storylets run --dry-run` prints the real figure for the real plan.

### 7. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `storylet`.

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `storylet.temperaturePermille.structure` | ‰ | 300 | enough spread that three samples are three opinions |
| `storylet.temperaturePermille.text` | ‰ | 500 | prose variety; below the level where code-switching rises (ideal §5.4) |

**Structural (commented):** three samples; two repairs; the vote set.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_storylet_pipeline.py -q
cd tools\seedsmith; python -m seedsmith narrative storylets run --dry-run             # DEFAULT: render both prompts per item, print calls, call nothing
cd tools\seedsmith; python -m seedsmith narrative preflight
cd tools\seedsmith; python -m seedsmith narrative storylets run --write --limit 12     # a small batch first (phased rollout)
cd tools\seedsmith; python -m seedsmith narrative storylets run --resume <runId>       # TRANSIENT replay from checkpoint
cd tools\seedsmith; python -m seedsmith narrative storylets status --run <runId>
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/pipelines/__init__.py        (new)
tools/seedsmith/seedsmith/adapters/narrative/pipelines/storylet.py        (new) node bodies: brief, structure draw, resolve, gate, text, repair
tools/seedsmith/seedsmith/adapters/narrative/pipelines/prompts/storylet.py (new) system prompts, PROMPT_VERSIONs, schema builders
tools/seedsmith/seedsmith/workflow/graphs/narrative_storylet.py           (new) graph wiring only
tools/seedsmith/tests/test_narrative_storylet_pipeline.py                 (new)
```

## Code style

```python
def resolve_structure(samples: "Sequence[dict]", plan: "StoryletPlan") -> "ResolvedStructure | Unresolved":
    """Vote ordinal and consequence per (slot, outcome); any 1-1-1 -> Unresolved naming the position.
    Carrier = lowest-index sample equal to the resolved values at every position; none -> the named
    defect 'no coherent sample'. Never splices fields from two samples."""
```

Match `workflow/graphs/commander_effect.py`: nodes named for what they do, validators registered rather
than inlined.

## Testing strategy

Every test stubs the transport with a scripted fake that raises when exhausted or unexpected
(`FakeCall`, `gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py:49`).

| Test | Asserts |
|---|---|
| `dry_run_makes_no_call` | both prompts render per item with a transport that raises |
| `three_samples_see_three_orders` | the three structure schemas list each enum in different orders, reproducible from the id |
| `planned_fields_are_const` | host, kind, climate, slot kinds and outcome counts are `const` in every structure schema |
| `vote_3_0_2_1_1_1` | high, split with minority recorded, and `unresolved` naming the position |
| `unresolved_is_not_retried` | a 1-1-1 position ends the item after exactly three structure calls |
| `carrier_is_lowest_matching_sample` | non-voted fields come from the lowest-index sample matching every voted position |
| `no_coherent_sample_is_a_quality_retry` | resolved values matched by no single sample trigger a new draw naming the defect |
| `structural_defect_redraws_with_defect_named` | an obvious-choice structure triggers a new draw whose brief names `choice-type: obvious` |
| `text_sees_structure_as_const` | the text schema pins every structure field; a text reply cannot change an ordinal |
| `literal_name_repairs_with_token` | a reply naming the antagonist literally is re-prompted with the `{lead_antagonist}` fix; a clean reply is accepted |
| `two_repairs_then_unresolved` | three failing text replies end the item `unresolved` after three text calls |
| `worst_case_is_twelve_calls` | a scripted all-fail run makes exactly 12 calls for one storylet |
| `transient_replay_makes_no_new_generation` | a timeout then resume re-uses finished nodes' answers |
| `rerun_is_byte_identical` | a second run over unchanged inputs writes no new bytes (via `narrative-emit`'s hash test) |
| `ref_is_filled_after_the_vote` | a resolved `relation.shift` gets the role the contract's rule names; the model's schema never contains `ref` |
| `unfillable_kinds_are_not_offered` | a texture item's structure schema has no `story.flag`, `quest.offer` or `scene.play` in its `kind` enum |
| `pinned_flag_position_leaves_the_vote` | an arc-link position pinned to `story.flag` is `const` in all three samples and absent from the vote record |
| `blocked_sample_ends_the_item` | a sample with `blocked` set ends the item `blocked` after that call; no further call is made |
| `no_model_literal` | the model id comes from `load_config`; the guard test passes |

No test asserts how many storylets a run produced or any generated text.

## Success criteria

1. A storylet reaches the corpus only after its resolved structure passes the structural gate and its text
   passes the text gate.
2. The vote set is exactly `ordinal` and `consequence`; a 1-1-1 split never resolves to a value.
3. No storylet mixes non-voted fields from two samples.
4. One storylet costs 4 calls in the base case and never more than 12.
5. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** plan first; permute every enum from id, field and sample index; gate structure before text;
  name defects in every retry; hand only accepted seeds to emit.
- **Ask first:** adding a field to the vote set (it moves the call budget); a third call per storylet;
  raising the repair bound.
- **Never:** let the model choose a host, kind, climate or choice kind; splice two samples; resolve a 1-1-1
  split to a value; write a number into any field; build a second storylet generator; call a model at game
  runtime.

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
| 1 | high | No `blocked` handling (shared with the contract finding) | fixed |
| 2 | medium | No step filled `consequence.ref` between the vote and the gate | fixed (§2 step 4) |
| 3 | medium | Arc-link flag positions were both planned and voted | fixed (pinned positions leave the vote) |
| 4 | low | `effect` naming; `names-good-option` now soft | fixed |
| 5 | low | Permutation from `(id, field, sample)`, 1-1-1 → `unresolved`, two retry intents, LangGraph only in `workflow/graphs/`, CoVe unbuilt, transport stubbed | verified |

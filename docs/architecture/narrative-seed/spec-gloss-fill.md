# Spec: `gloss-fill`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `gloss-fill` · **Map row:** 17 · **Wave:** 0 (Owner ruling 2026-09-19 (round 4): moved from Wave 5, because `dungeon-generator-repair`'s legacy regeneration reads its output)
**Depends on:** `gloss-registry`, `model-config-resolve`, `script-check` · **Model calls:** yes — one bounded pass
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §5.4 (language leakage), §11 item 1; `seedsmith/spec-pipeline.md` §5.1
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Fill the motif gloss registry: one target-language gloss per motif, produced once by a translation
pipeline, script-checked, reviewed by sample, and committed through `gloss-registry`'s contract. Every
later narrative brief — and the repaired dungeon generator — reads glosses instead of raw motifs, which
removes the cause of the committed leak (53 of 54 Delve events carry Han characters because the brief asked
for Chinese motifs verbatim — map §3.4).

A gloss is **identity text** (a translation of a flavour word), so a model may write it (seedsmith P1). It
carries no number and decides nothing mechanical.

It runs in Wave 0, before `dungeon-generator-repair`'s legacy regeneration, because that run and every
later brief read its output (map §6; Owner ruling 2026-09-19 (round 4) — it used to run first in Wave 5). It
is split from `gloss-registry` so the only model-spending step in front of the dungeon repair is bounded and
replaceable (map §4, "Why these boundaries").

## Design

### 1. Input and output

- **Input:** the motif list, `gk-data/packs/fusion/data/seed/creatures/_registry/motifs.v1.json` — a flat list under `motifs`,
  Chinese throughout today (ideal §11 item 1; the count is a reading, never asserted). Each motif is looked
  up in the existing gloss registry first; only motifs without an accepted gloss are sent.
- **Output:** rows in `gk-data/packs/fusion/data/seed/narrative/_registry/motif-glosses.en.v1.json` (new, owned by
  `gloss-registry`), in its row shape `{gloss, sense, model, promptVersion}`
  ([spec-gloss-registry.md](spec-gloss-registry.md) §2). `model` is the resolved `config.model`, never a
  default (`model-config-resolve`). This module adds no field and owns no file layout; the loader and the
  lookup that **refuses** an unglossed motif (`GlossMissing`) are `gloss-registry`'s.

### 2. The pipeline — the proven translation loop, reused

`seedsmith/spec-pipeline.md` §5.1 names the shape: the verify-and-self-heal translation loop ported from
the owner's lore-weave translation script, generalized in this repo as `call_with_self_heal`
(`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:504`). Per chunk of `gloss.chunkSize` motifs:

1. **Call** with a JSON Schema per chunk: an object whose keys are exactly the chunk's motif keys, each value
   an object `{gloss, sense}` — `gloss` a short target-language noun phrase with `maxLength` from the budget,
   `sense` a closed enum of `concrete · abstract · action · quality · none` — plus the root `blocked` reason
   the core audit requires (`seedsmith/spec-pipeline.md` §3.7; a blocked chunk writes nothing and its motifs
   stay unglossed). `additionalProperties: false`, every key required
   (`docs/research/ai-native-generation/README.md` §3); every field has a description with a negative
   clause. Constrained decoding enforces the shape; reasoning is off (`seedsmith/spec-quality-gates.md` §2.6).
   **Permutation and vote (Audit 2026-09-19).** The `sense` enum is reordered per motif with
   `order_for(motif, "sense", 0)` (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26`), so
   position bias cannot skew the review strata. The vote set is **empty**, named and justified: `sense` only
   stratifies the review sample and decides nothing downstream, so a three-sample vote would triple the pass
   for no protected decision.
2. **Verify** (hard defects block, soft ones are recorded):

   | Defect | Hard/soft | Check |
   |---|---|---|
   | missing or extra key | hard | shape backstop behind constrained decoding |
   | empty gloss | hard | `non_empty` |
   | foreign script in `gloss` | hard | `script_policy` ([spec-script-check.md](spec-script-check.md) §4) with policy `latin` on `gloss` and `none` on `sense` |
   | digit in `gloss` | hard | `gloss-registry`'s row rule (its loader's digit refusal, run on the draft) — Audit 2026-09-19: this row named `narrative-validators`' `no_digit`, a Wave-3 module this one does not depend on |
   | gloss longer than `gloss.maxWords` words | hard | word count |
   | gloss equal to the romanised motif | soft | an untranslated transliteration reads as a name; recorded for review |
   | two motifs in the chunk with the same gloss | soft | recorded; distinct motifs may share an English word, so this is a review signal, not a rejection |

3. **Heal** by re-prompting with the named defects per key (`spec-pipeline.md` §3.6), **at most two
   repairs** — the structural retry bound (`seedsmith/spec-workflow-runtime.md` §2.3), passed explicitly as
   `max_heal`. The transport default is three (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:51`); the
   narrative program uses the contract's two, and the explicit argument carries a comment saying why.
4. **Never fall back to the source.** `call_with_self_heal`'s default `default_for` supplies the original
   item's value on exhausted heals. For a gloss that would write the raw Chinese motif into the gloss
   registry — the exact leak this program exists to stop. This module passes a `default_for` that returns
   **no gloss**: the motif stays unglossed, is listed as `unresolved` in the run report, and the registry
   lookup keeps refusing it.

**Model.** Resolved through seedsmith's config layer only — `.env` `SEEDSMITH_LLM_MODEL` over
`seedsmith.toml` over the `LlmCallerConfig` default (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:47`,
`.env` keys at lines 69–77, `load_config` at line 124). No model literal in this module or its CLI
(owner ruling R6; `model-config-resolve`'s guard test fails on one).

**Few-shot and temperature.** The system prompt carries `gloss.exemplarCount` authored target-language
exemplar pairs from `gk-data/packs/fusion/data/seed/narrative/_exemplars/gloss.en.v1.json` (new) — hand-authored, as the
`_exemplars/` rule allows, and never generated — and the call uses the low temperature in the budget:
target-language few-shot examples and low temperature are the measured mitigations for code-switching
(ideal §5.4, Marchisio et al.).

### 3. Retries — two intents

- **TRANSIENT** (endpoint down, timeout, 5xx): replay the chunk from its checkpoint, no new generation
  (`docs/research/ai-native-generation/README.md` §5). The run ledger (`RunLedger`,
  `gk-forge/tools/seedsmith/seedsmith/pipeline/run_ledger.py:25`) records finished chunks, so a resumed run never
  re-calls a finished chunk.
- **QUALITY** (a hard verify defect): the named-defect heal above, bounded at two.

### 4. Review — by sample, before commit

Glosses are open-loop in one respect: "is this the right sense of the word" has no machine answer. After a
run, `gloss.reviewSample` rows are drawn with seedsmith's core `stratified_sample`
(`gk-forge/tools/seedsmith/seedsmith/sampling/__init__.py:38`), stratified by `sense` and seeded from the run id, and
the reviewer records `accept · reject` verdicts in the run file (append-only). Audit 2026-09-19: this used
`review-render`'s machinery, a Wave-3 module this one does not depend on and cannot wait for in Wave 0.
**Commit rule:** accepted rows and the unsampled rows of the run are committed through `gloss-registry`
once every rejected row has been regenerated and its replacement accepted — the sample reads eight of sixty,
not sixty (`seedsmith/spec-pipeline.md` §6), and a rejection's reason becomes a new mechanical check wherever
one can be written. A rejected gloss is regenerated with the reviewer's reason named in the brief; it is
never hand-typed into the registry, because the registry's rows carry generator provenance and are generated
output (the no-hand-edit rule, map §2 principle 8).

**Translation is a leak path too** (`ip-censor` ideal "Narrative generation" row 7): a gloss can surface a
third-party mark the source language hid. The gloss registry is a `player-prose` surface in the release
scan's scope (`docs/architecture/ip-censor/spec-registry.md` "Narrative surface" table); this module adds
no IP check of its own (IC-3).

### 5. Call budget

`docs/research/ai-native-generation/README.md` §9, with no vote (a translation has no enum to bias):

```text
calls  = ceil(M / chunkSize)                       base, M = motifs without an accepted gloss
worst  = 3 × ceil(M / chunkSize)                   one call + two repairs per chunk
```

Illustration, not an assertion: with the committed list's 1,586 motifs (a reading, ideal §11 item 1) and a
chunk of 20, the base pass is 80 calls and the worst case 240 — minutes on the local model. The dry run
prints the real figure from the real list.

### 6. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `gloss`. `gloss-registry` creates the
file with `gloss.maxWords` (its loader enforces it); this module adds the other rows.

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `gloss.chunkSize` | motifs per call | 20 | small enough that a heal names few keys; the lore-weave script's chunked shape |
| `gloss.maxWords` | words | 4 | a gloss is flavour for a brief, not a definition (row owned by `gloss-registry`; the verify step reads the same row) |
| `gloss.exemplarCount` | pairs | 8 | few-shot beyond a handful changes little (ideal §5.6) |
| `gloss.temperaturePermille` | ‰ | 200 | low temperature reduces code-switching (ideal §5.4) |
| `gloss.reviewSample` | rows per batch | 60 | one reviewer sitting |

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_narrative_gloss_fill.py -q
cd tools\seedsmith; python -m seedsmith narrative gloss fill --dry-run          # DEFAULT: render every chunk prompt, print calls, call nothing
cd tools\seedsmith; python -m seedsmith narrative preflight                     # one real call proves constrained decoding is on (README §4); built here, reused by every narrative pipeline
cd tools\seedsmith; python -m seedsmith narrative gloss fill --write            # run, checkpointed; writes pending rows, never the registry
cd tools\seedsmith; python -m seedsmith narrative gloss fill --resume <runId>   # TRANSIENT replay
cd tools\seedsmith; python -m seedsmith narrative gloss commit --run <runId>     # after review: accepted rows into the gloss registry
```

## Project structure

```text
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/__init__.py     (new)
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/prompt.py       (new) system prompt, per-chunk schema
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/fill.py         (new) chunking, verify, heal, no-source fallback
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/commit.py       (new) accepted rows through gloss-registry's writer
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/preflight.py          (new) the one-real-call constrained-decoding probe every narrative pipeline runs first
gk-data/packs/fusion/data/seed/narrative/_exemplars/gloss.en.v1.json                     (new) authored few-shot pairs
data/seed/narrative/_runs/gloss-<runId>.json                        (new) pending rows and the run report (unresolved, soft defects)
gk-forge/tools/seedsmith/tests/test_narrative_gloss_fill.py                 (new)
```

The run file is bookkeeping, not corpus content, so it sits under `_runs/` as the item adapter's run files do.

## Code style

```python
def verify_chunk(items: dict, out: dict) -> "tuple[dict, dict]":
    """(hard, soft) per motif key — the split `call_with_self_heal` expects. Hard: shape, empty,
    script, digit, length. Soft: transliteration, duplicate gloss."""


def no_gloss(key: str, original: str) -> None:
    """default_for: an exhausted heal leaves the motif unglossed. Never returns `original` — that
    would write the raw motif into the registry, which is the leak this module exists to stop."""
```

## Testing strategy

The transport is stubbed; any unexpected call raises (`MockModelServer`,
`gk-forge/tools/seedsmith/tests/test_llm_caller.py:69`, or the `FakeCall` shape).

| Test | Asserts |
|---|---|
| `dry_run_makes_no_call` | the dry run renders every chunk prompt with a transport that raises |
| `already_glossed_motifs_are_not_sent` | a fixture with half the motifs glossed sends only the other half |
| `foreign_script_gloss_heals_with_defect_named` | a first reply with a Han character is re-prompted naming the key and the script; a clean second reply is accepted |
| `two_repairs_then_unresolved` | three bad replies leave the motif unresolved and make exactly three calls |
| `exhausted_heal_never_writes_the_source` | after exhaustion, the pending rows contain no raw motif and the lookup still refuses it |
| `transient_replay_makes_no_new_call` | a timeout mid-run, then resume: finished chunks are not re-called |
| `no_model_literal` | the module and its CLI resolve the model through `load_config`; `model-config-resolve`'s guard passes |
| `rejected_gloss_regenerates_with_reason` | a review rejection produces a new call whose brief names the reason; the rejected row is not edited |
| `commit_writes_only_accepted_rows` | `commit` writes accepted and unsampled rows through `gloss-registry`'s writer and nothing else, and refuses while a rejected row has no accepted replacement |
| `commit_is_byte_identical_on_rerun` | committing the same run twice leaves the registry file's hash unchanged (README §6) |
| `sense_options_are_permuted_per_motif` | two motifs see `sense` in the orders `order_for` gives; the order is reproducible from the motif |
| `blocked_chunk_writes_nothing` | a reply with `blocked` set leaves its motifs unglossed and listed in the report; no heal call follows |
| `review_sample_is_seeded_and_stratified` | the same run id yields the same sample; every non-empty `sense` stratum is represented |
| `digit_or_long_gloss_is_hard` | a gloss with a digit, or over `gloss.maxWords`, is a hard defect |

No test asserts how many motifs exist, how many were glossed, or any gloss text.

## Success criteria

1. Every motif either has an accepted, script-clean gloss in the registry or is listed as unresolved; none
   has its raw form stored as a gloss.
2. The pass is bounded: at most three calls per chunk, and the dry run prints the figure before any spend.
3. A resumed run never re-calls a finished chunk.
4. Accepted rows enter the registry only after a recorded review sample.
5. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** resolve the model through the config layer; verify before accept; name defects in heals;
  leave an exhausted motif unglossed; review a sample before commit.
- **Ask first:** a second gloss locale (it doubles the pass and the review); raising the repair bound; a
  hosted model tier.
- **Never:** fall back to the source motif; hand-type a gloss into the registry; add an IP check here
  (IC-3); carry a model literal.

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
| 1 | medium | Owner ruling round 4: must run in Wave 0 before the legacy regeneration | fixed (header, objective, map) |
| 2 | medium | Undeclared dependencies on `narrative-validators` (digit check) and `review-render` (sampling), both later waves | fixed (gloss-registry row rule; core `stratified_sample`) |
| 3 | medium | `sense` enum was not permuted and the vote set was unstated (README §10) | fixed (`order_for`; empty vote set, justified) |
| 4 | medium | No rule for unsampled rows when the review sample holds a rejection | fixed (commit rule) |
| 5 | medium | Chunk schema lacked `blocked` and `maxLength` | fixed |
| 6 | low | No byte-identical commit test (README §6) | fixed |

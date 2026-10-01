# Spec: `model-config-resolve`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `model-config-resolve` · **Map row:** 1 · **Wave:** 0
**Depends on:** none · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.
**Ruling this module implements:** R6 (`narrative-seed-ideal.md` §10) — *"No hard-coded model. The model
is set in the environment; the default is Gemma 26B."*

---

## Objective

Every model call seedsmith makes resolves its model through the one config layer — `.env`
`SEEDSMITH_LLM_MODEL` over `seedsmith.toml` over the `LlmCallerConfig` default — and every provenance
field that records a model records the model the call actually used. No adapter, no helper and no CLI
flag carries its own model id. A test fails on any model literal outside
`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py`.

This is repair work with value today: the narrative pipelines (Wave 5) are built against this layer from
day one, and every existing generator stops silently ignoring the operator's `.env`.

**Done means:** the guard test is green over the whole package, the three bypass classes below are gone,
and the guard is registered as an enforced invariant.

---

## Design

### 1. The layer already exists and is correct

| Piece | Evidence |
|---|---|
| `LlmCallerConfig` with the default model | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:39`, model default at `:47` |
| `DEFAULT_CONFIG` — the built-in bottom layer | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:63` |
| `.env` key table (`SEEDSMITH_LLM_MODEL` and six more) | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:69-77` |
| `load_config` — toml, then `.env` on top | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:124` |
| `resolve_live_transport` — a CLI value wins only when non-empty; `unrecorded` falls through | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:167`, the fall-through at `:188-190` |
| The committed example of the per-machine file | `gk-forge/tools/seedsmith/.env.example` |

The item generators already use it the right way: `--model` defaults to `""` and resolves through
`resolve_live_transport` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/affixfamgen/run.py:143`, `:181`). This
module makes that the only shape.

### 2. Three bypass classes (inventory measured 2026-09-19 — a reading, not a contract)

The counts below are readings taken this session. The guard test (§4) is the contract; it finds every
member of each class, so no list here is pinned.

**A. Executable model literals — 11 in 7 files** (matches `narrative-seed-map.md` §3.5 item 1):

| File | Lines |
|---|---|
| `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_action_descriptions.py` | `:141` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_action_pipeline.py` | `:78`, `:180` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_family_actions.py` | `:66`, `:166` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_general_actions.py` | `:70`, `:175` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_signature_actions.py` | `:84`, `:220` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_commander_effects.py` | `:71` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/effects/affix/generate_affixes.py` | `:378` |

The hits at `gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:158`,
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/family/consolidate.py:36` and
`gk-forge/tools/seedsmith/seedsmith/workflow/graphs/item_set.py:134` are comments and docstrings, not code.

**B. Provenance-stamp defaults that name a model the call may not have used.** A `model: str = "..."`
parameter on an emitter stamps that string into `_meta.model` whenever a caller omits it:

| File | Default |
|---|---|
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/affixfamgen/emit.py:124` | `"claude-sonnet-5"` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/emit.py:152` | `"claude-sonnet-5"` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/run.py:287` | `"seedsmith-basetypegen"` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/droptablegen/run.py:216` | `"seedsmith-droptablegen"` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/gemgen/run.py:254` | `"gemgen/1"` |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/emit.py:221` | `"seedsmith-recipegen"` |

The map names the first two; the last four were found by this spec's reading and are the same defect:
a provenance field holding a value nobody resolved.

**C. The built-in default used as a live value.** `DEFAULT_CONFIG` as a parameter default, or its
fields as a CLI default, skips `.env` and `seedsmith.toml` entirely whenever the caller omits the
argument. Examples: `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_families.py:73-74` (CLI
`--endpoint`/`--model` defaults), `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:109`, `:211`,
`:256`, `:389`, `:500`, `:608`, `gk-forge/tools/seedsmith/seedsmith/workflow/nodes/generate.py:20`, and the
transport's own `call_model` (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:298`) and
`call_with_self_heal` (`:510`). This class is also new relative to the map; it is the same R6 defect in a
form a string grep cannot see.

### 3. The fix — one shape everywhere

1. **The transport resolves late.** `call_model` and `call_with_self_heal` take
   `config: LlmCallerConfig | None = None`; `None` means `load_config()` at call time. `DEFAULT_CONFIG`
   stays, referenced only inside `llm_caller.py` as the bottom layer (`:146`).
2. **Adapters pass through, never construct.** Every adapter function that forwards to the transport
   takes `config: LlmCallerConfig | None = None` and passes it on unchanged. No adapter builds
   `LlmCallerConfig(model=<literal>)`. A function that today takes `model: str = "<literal>"` takes
   `config: LlmCallerConfig | None = None` instead; the model id it needs for provenance is
   `config.model` after resolution.
3. **CLI flags default to empty.** `--model` and `--endpoint` default to `""` and are merged through
   `resolve_live_transport`. `generate_families.py` moves to that shape.
4. **Provenance records what ran.** Every emitter's `model` parameter becomes a required keyword with
   no default. The caller passes, closed vocabulary:

   | Value | When | Negative clause |
   |---|---|---|
   | the resolved `config.model` | a model call produced the row | not the value a CLI flag *would* have sent, and not `LlmCallerConfig`'s default unless that is what resolved |
   | `unrecorded` | the row came from a replayed answer file whose model was not recorded (the report CLI's existing sentinel, `gk-forge/tools/seedsmith/seedsmith/report/cli.py:2835`) | not a model id; never sent to a transport |
   | `none` | a deterministic generator made the row with no model call | not "unknown"; it asserts that no model was involved |

   Rows already committed keep their stamp; the rule governs rows written after this module lands. The
   generated-seed guard keys on the presence of `_meta.model` (`gk-core/scripts/guard-generated-seed.py:117-124`),
   so `none` keeps a deterministic tree protected exactly as before.

### 4. The guard — `test_no_model_literal.py` (new)

A static test over every `.py` file under `gk-forge/tools/seedsmith/seedsmith/`, excluding
`pipeline/llm_caller.py`. It parses each file with `ast` (so comments are invisible and docstrings are
skipped by position) and reports `file:line` for each of five shapes:

| Shape | Detection |
|---|---|
| **S1** string constant naming a model | a code string constant whose lowercased text contains a vendor stem from a closed list declared in the test (`gemma`, `claude`, `gpt-`, `qwen`, `llama`, `mistral`, `deepseek`, `kimi`, `gemini`, `phi-`) **at a token boundary** — the start of the string or right after `/`, `-`, `_`, `:` or a space (Audit 2026-09-19: a bare substring match fires on unrelated words such as `graphi-` or a prose string mentioning an animal, and a guard that over-fires gets allow-listed into uselessness). The list is a declaration: a new vendor is a reviewed one-line addition, and the structural shapes S2–S5 catch the defect without it |
| **S2** a parameter named `model` or `model_id` with a string default | any string default; a Python `None` default is allowed |
| **S3** `add_argument("--model", default=X)` | `X` other than `""` or `"unrecorded"`, including an attribute such as `DEFAULT_CONFIG.model` |
| **S4** any reference to the name `DEFAULT_CONFIG` | outside `llm_caller.py` |
| **S5** `LlmCallerConfig(model=<constant>)` | a keyword `model` bound to a string constant |

Each shape has a positive and a negative fixture, parsed from an inline source string, so the guard is
proven to fire and proven not to over-fire (a docstring naming Gemma passes; a comment passes).

**Registered invariant.** The build change adds a row to `gk-core/scripts/enforcement-registry.v1.json`
`invariants`: id `seedsmith-no-model-literal`, source `narrative-seed-map.md §2 principle 13 (R6)`, guard
`gk-forge/tools/seedsmith/tests/test_no_model_literal.py`. The map's §13 checklist names this row as owed.

### 5. What this module does not do

It adds no config key, changes no resolution order, touches no committed seed file, and changes no model.
It does not edit `.env.example`, whose model line is configuration, not code. It does not add a
verification boundary for `gk-forge/tools/seedsmith/**` — that mapping is `test-verification-boundary`'s
`python-test-lane` (map §7).

### 6. `decisions.md` row (drafted; appended in the build change)

> **No hard-coded model in seedsmith** (owner ruling R6, 2026-09-19). Every seedsmith model call resolves
> its model through `.env` `SEEDSMITH_LLM_MODEL` → `seedsmith.toml` → `LlmCallerConfig`'s default; no
> adapter, helper or CLI flag carries a model id, and provenance records the model that ran (or the
> sentinels `unrecorded` / `none`). Enforced by `gk-forge/tools/seedsmith/tests/test_no_model_literal.py`.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_no_model_literal.py -q
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_llm_caller.py -q
# Every touched adapter's own suite, e.g.
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_affix_families_gen.py -q
```

`verify-change.py` cannot select `gk-forge/tools/seedsmith/**` yet (`gk-core/scripts/verify-change.py:771`); seedsmith's
pytest is the verification and runs in CI (`.github/workflows/ci.yml:284`).

## Project structure

```text
gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py                 call_model / call_with_self_heal resolve late
gk-forge/tools/seedsmith/seedsmith/adapters/actions/*.py                  class A literals removed (5 files)
gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_commander_effects.py   class A
gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_families.py            class C CLI defaults
gk-forge/tools/seedsmith/seedsmith/adapters/effects/affix/generate_affixes.py         class A
gk-forge/tools/seedsmith/seedsmith/adapters/items/{affixfamgen,basetypegen,recipegen}/emit.py   class B
gk-forge/tools/seedsmith/seedsmith/adapters/items/{basetypegen,droptablegen,gemgen}/run.py      class B
every function with a `config: LlmCallerConfig = DEFAULT_CONFIG` default      class C (the guard lists them)
gk-forge/tools/seedsmith/tests/test_no_model_literal.py                   (new) the guard
gk-core/scripts/enforcement-registry.v1.json                             one invariant row (build change)
```

## Code style

Match `llm_caller.py`: frozen dataclasses, no hidden constants, docstrings that name the defect class
they prevent. The guard's vendor-stem tuple carries a comment saying it is a declaration and why the
structural shapes, not the list, are the real check.

## Testing strategy

| Test | Asserts |
|---|---|
| `package_has_no_model_literal` | the five shapes find nothing in `gk-forge/tools/seedsmith/seedsmith/**` outside `llm_caller.py` |
| `s1_fires_on_code_string_and_skips_docstring_and_comment` | positive and negative fixture pair |
| `s1_matches_stems_on_token_boundaries_only` | `"google/gemma-4"` and `"claude-sonnet"` fire; `"autographi-x"` and `"dollama"` (stem inside a word) do not (Audit 2026-09-19) |
| `s2_fires_on_model_param_string_default` | `def f(model: str = "x")` fires; `model: Optional[str] = None` does not |
| `s3_fires_on_cli_default_literal_and_on_default_config_attribute` | both fire; `default=""` and `default="unrecorded"` do not |
| `s4_fires_on_default_config_outside_the_transport` | fixture outside `llm_caller.py` fires |
| `s5_fires_on_config_built_from_a_literal` | `LlmCallerConfig(model="x")` fires |
| `call_model_resolves_env_when_config_omitted` | with a fixture `.env` (hermetic path) setting `SEEDSMITH_LLM_MODEL`, a stub transport receives that model |
| `provenance_model_is_the_resolved_model` | an emitter called after a stubbed run stamps `config.model`; calling it without `model` raises `TypeError` |
| `provenance_sentinels_are_closed` | only a resolved id, `unrecorded` or `none` is accepted by the stamping helper |
| `offline` | every test stubs the transport so a real call raises |

No test pins how many call sites were fixed: the inventory in §2 is a reading.

## Boundaries

- **Always:** resolve through `load_config` / `resolve_live_transport`; pass `config` through; stamp the
  resolved model or a closed sentinel.
- **Ask first:** adding a config key or changing the resolution order; adding a vendor stem that is not a
  model family.
- **Never:** a model id in adapter or CLI code; `DEFAULT_CONFIG` outside `llm_caller.py`; editing a
  committed seed's `_meta.model` by hand; a fallback model.

## Success criteria

- [ ] `test_no_model_literal.py` is green over the package, and each of its five shapes is proven by a
      failing fixture.
- [ ] With `SEEDSMITH_LLM_MODEL` set in a hermetic `.env`, a stubbed call from any adapter entry point
      receives that model.
- [ ] Every emitter's `model` argument is required; rows written after this change carry the resolved
      model, `unrecorded` or `none`.
- [ ] The invariant row `seedsmith-no-model-literal` is in `gk-core/scripts/enforcement-registry.v1.json`.
- [ ] The full seedsmith suite is green with the transport stubbed to raise.

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
| 1 | low | S1's vendor-stem substring match over-fires on unrelated words, which would push the guard toward allow-lists | fixed (token-boundary match + negative fixture) |
| 2 | low | Citations sampled: `llm_caller.py:39/:47/:63/:69-77/:124/:146/:167/:188/:298/:510`, `report/cli.py:2835`, `affixfamgen/run.py:143/:181`, class A/B/C lines — all resolve | verified |
| 3 | low | Registry row `seedsmith-no-model-literal` is proposed for the build change, not added here (fence) | deferred — proposed row |

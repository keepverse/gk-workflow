# Spec: `world-namer`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `world-namer` · **Map row:** 11 ·
**Wave:** 3 (the first module that spends tokens)
**Depends on:** `call-budget-dry-run`, `corpus-metrics` · **Model calls:** **yes**. One proof call per
run, one naming call per planned entry, and at most two repairs per entry.
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build and **no model run**
authorized until this spec is approved and the first batch size is agreed (§10).

---

## 1. Objective

This is the one model stage for every world family. Input: a planned entry whose enums the planner has
already drawn. Output: identity text only (`name`, `flavor`, `reason`), validated, frozen on accept, and
recorded with provenance that makes a rerun byte-identical. Structures use it first
(`trade-structure-rows`), and legion seeds use it unchanged (`legion-seed-rows`). The map allows one
namer, not one per family (map §4, "One naming stage").

**Done means:**
- Every accepted entry passed every validator.
- Every rejected entry carries its named defect.
- Every exhausted entry is `unresolved` and never emitted.
- Constrained decoding was proven by a real call before the run.
- A second run over unchanged inputs makes zero calls and rewrites nothing.

## 2. Scope and non-goals

**In scope.**
- The naming contract and its schema.
- The validators.
- The retry split.
- Freeze, provenance and `stale_ids`.
- The accepted-entry store the corpus writer merges.
- The proof call.

**Not in scope.**
- Choosing any enum, band, role, slot or count. The planner does that (`call-budget-dry-run`).
- Rolling anything. Nothing here is a per-player object. Structures and legion equipment never roll.
- Any number. The model writes none, and a digit anywhere in its output is a defect.
- The `flavor` schema widening. It moved to `world-exemplars` (§3).
- Legion-specific validation, which is `legion-seed-contract`'s schema.

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | The local transport with constrained decoding (`schema=`) | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:298` (`call_model`) |
| Built | Self-heal: a re-prompt naming the defect, bounded by `max_heal` | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:504-530` |
| Built | A hostile-prompt constrained-decoding proof | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_anchor.py:159-183` |
| Built | Permutation and vote helpers, with 1-1-1 → `unresolved` | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26`; `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26`, `:67` |
| Built | Validators `non_empty`, `field_echo`, `name_collision`, `language_consistency` | `gk-forge/tools/seedsmith/seedsmith/workflow/validators/__init__.py:11`; `gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py:38` |
| Built | The workflow runner's TRANSIENT (resume, no new call) and QUALITY (new call, defect named) split | `gk-forge/tools/seedsmith/seedsmith/workflow/runner.py`; ai-native README §5 |
| Built | Late model resolution, `resolve_live_transport` | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:167` |
| Wiring gap | No emit path: `generate_anchor.py` votes fields and records provenance, and nothing writes an accepted row | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_anchor.py:186-221` |
| Wiring gap | The structure pipeline binds `config: LlmCallerConfig = LlmCallerConfig()` at definition time, the "class C" shape `narrative-seed` `model-config-resolve` retires. So map §3.1's *"resolves its model through the config layer"* is only half true: no literal model is passed, but nothing is resolved late either | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_anchor.py:98`, `:132`; `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:47`; `docs/architecture/narrative-seed/spec-model-config-resolve.md:173` |
| Wiring gap | `LlmCallerConfig.max_heal` defaults to 3, and the AI-native rule bounds repairs at two | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:51` |
| Wiring gap | On exhausted heals, `call_with_self_heal` falls back to `default_for`, which defaults to the original value. For naming, the fallback must be `unresolved` | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:504-530` (docstring) |
| Real gap | The naming contract, the digit rule, the accepted-entry store, freeze on accept, the namer's `stale_ids` | — |

**Two corrections to the map (§5.11).**
1. The map rejects a draft whose name is in *"the avoid-list"*. `ip-censor` ruling IC-3 withdrew exactly
   that: *"it does not block generation — 'block generation will cost more than help'"*
   (`docs/architecture/ip-censor-ideal.md:440`). The map's own §5.7 says the same thing. The avoid-list
   is therefore **advisory in the brief** (the tone section), and `ip-censor`'s release scan is the gate.
   Dedup against `world-name-index` still rejects, because that is a corpus-integrity check, not an IP
   check.
2. The `flavor` schema widening moved to `world-exemplars` (`spec-world-exemplars.md` §3).

## 4. The generation rules, as they bind this module

1. **The model writes identity, deterministic code writes magnitude** (seedsmith P1). The output schema
   has three string fields and nothing else. A digit is a defect.
2. **The planner runs first** (decision 33). The namer refuses an entry that is not in the committed
   plan's `plannedEntries`, or whose plan fails `check_plan`.
3. **Permutation and voting.** The planner fixes every enum, so the namer offers the model **no enum to
   select**. Permutation has nothing to act on, and the vote set is empty (`call-budget-dry-run` §4).
   The `generate_anchor.py` voting path stays in the codebase for any future field a model genuinely
   chooses. When one exists, it is permuted seeded from `(entity_id, field, sample_index)`, voted three
   times, and a 1-1-1 result resolves `unresolved`. The namer does not call that path.
4. **Constrained decoding is proven by one real call before the run.** `prove_constrained_decoding`,
   retargeted to the naming schema, sends a hostile prompt (asking for prose, a code fence and an extra
   key). If the reply is not a bare object with exactly the three schema keys, the run aborts before any
   naming call. The proof's raw reply is recorded in the run ledger.
5. **Schema shape for enforceability.** Every string has `maxLength` (llama.cpp's grammar converter does
   not enforce `pattern`; `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:52-59`), and there is
   `additionalProperties: false` with every field required. The digit rule is a validator, not a
   pattern, for the same reason.
6. **TRANSIENT and QUALITY retries are separate paths.** A timeout, a 5xx or a user pause resumes from
   checkpoint with **no new call**. A validator rejection makes a new call with the defect named. Repairs
   are bounded at **two** (`maxRepairs` from tuning), then `unresolved`.
7. **Tests never call a model.** The transport stub raises, and the offline guard is active.
8. **Freeze on accept.** An accepted entry is never regenerated unless `stale_ids()` names it.

## 5. Design

### 5.1 The naming schema

```json
{ "type": "object", "additionalProperties": false, "required": ["name", "flavor", "reason"],
  "properties": {
    "name":   { "type": "string", "maxLength": <tuning generation.nameMaxChars>,
                "description": "What players call this thing. NOT its role word alone, NOT a person's name, NOT a number or a grade." },
    "flavor": { "type": "string", "maxLength": <tuning generation.flavorMaxChars>,
                "description": "One or two sentences on how it looks and is used. NOT its numbers, NOT a restatement of its role." },
    "reason": { "type": "string", "maxLength": <tuning generation.reasonMaxChars>,
                "description": "Why this name fits the drawn role, slot and element. NOT a justification of power." } } }
```

The length bounds are tunables, published through `--add-key` in `structure-seed`'s `generation` block.
The legion family publishes its own. `numeric_audit` passes this schema: no numeric type and no numeric
enum.

### 5.2 Validators, in order, each returning named defects

| Validator | Rejects | Source |
|---|---|---|
| `non_empty` | an empty or whitespace-only field | existing |
| `no_digit` (new, `workflow/validators`) | any `0-9` character in any field | P1, the digit rule |
| `field_echo` | a name that is only the drawn role or slot word | existing |
| `name_taken` (new) | `NameIndex.is_taken(normalize_name(name), except_id=None)`, or a collision with another entry accepted **in the same run** | `world-name-index` |
| `script_policy` if `narrative-seed` `script-check` has landed, else `language_consistency` | a name or flavour in the wrong script or language | `docs/architecture/narrative-seed/spec-script-check.md:135-139`; `gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py:38` |
| length | above the tuning bound (belt and braces behind `maxLength`) | tuning |

The avoid-list is **not** a validator (§3 correction 1).

### 5.3 The run

For each planned entry in `planKey` order:
1. Skip it if accepted and not stale.
2. Otherwise build the prompt with `call-budget-dry-run`'s prompt builder, the same function the dry run
   uses.
3. Call `call_with_self_heal` with `max_heal = tuning generation.maxRepairs`, `default_for` = a sentinel
   that marks the entry `unresolved`, and `schema = §5.1`.
4. Record every attempt in the run ledger.

The model resolves late: `config: LlmCallerConfig | None = None`, resolved through
`resolve_live_transport` / `load_config`. That is the shape `model-config-resolve` makes universal. The
resolved model id is stamped in provenance.

### 5.4 The accepted-entry store and the one writer

Accepted entries go to `data/seed/structures/_generation/accepted.v1.json`, a generated file with
canonical JSON, keyed by `planKey`, holding the drawn enums, the three texts and provenance. **The
namer never writes the corpus tree.** `generate_corpus.write_corpus()` merges its hand-authored source
rows with the accepted store's rows (`_provenance.source: "GENERATED"`) and remains the tree's only
writer (`structure-bands` §5.1). A generated row's `id` is the kebab form of its **first** accepted
`name`, **minted once and frozen in the accepted store under its `planKey`** (corrected by the 2026-09-20
audit). The first draft re-derived the id from the name, so a later `stale_ids()` regeneration that
changed the name would have changed the id — and a saved world that built the structure stores its id
(`rpg_world_slots.structure_id`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:153`), so the save would then hold an
unknown id and refuse to load. An id is identity the game persists; a name is text a regeneration may
improve. So a restaled entry keeps its frozen `id` and only its `name`/`flavor`/`reason` change; the
`name_taken` check still runs on the new name. A collision between a newly minted id and an existing id
is a `name_taken` defect before acceptance, so it cannot happen at write time.

### 5.5 Provenance and staleness

Per accepted entry:
- `planKey`
- `planEntryHash` (the canonical hash of the drawn enums)
- `promptHash` (the rendered prompt)
- `promptVersion`
- `exemplarVersion`
- `toneRegistryVersion`
- `model` (resolved)
- `repairsUsed`
- `validatorVerdicts`
- `acceptedAtRun` (the run id, not a clock string, which keeps rerun bytes stable)

`stale_ids()` returns the entries whose recorded `planEntryHash`, `promptVersion`, `exemplarVersion` or
`toneRegistryVersion` differs from current. **A model change alone does not stale an entry**: accepted
output is frozen, the Infinite Craft rule (`empire-seed-ideal.md` §5.4). Regenerating after a model
change is a deliberate `--restale model` flag, never a default.

### 5.6 Where it lives

The naming stage is family-neutral: `tools/seedsmith/seedsmith/pipeline/world_namer.py`. It takes a
`NamingFamily` (the schema bounds, the prompt builder, the accepted-store path, the planned-entry source)
supplied by each adapter. Structures supply theirs in `adapters/structures/naming.py`. Legion supplies
its own later with no change to the stage.

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m pytest tools/seedsmith/tests/test_world_namer.py gk-forge/tools/seedsmith/tests/test_offline_guarantee.py -q
python -m seedsmith structures plan --dry-run --out $env:TEMP\structures-dry-run   # always first
python -m seedsmith structures name --prove-only                                     # one real call
python -m seedsmith structures name --limit <first-batch>                            # owner-approved size
python -m seedsmith.adapters.structures.generate_corpus                             # the one writer
python -m seedsmith structures name --limit <first-batch>                            # rerun: zero calls
```

Before any real call, run the `seedsmith-preflight` skill (`.claude/skills/seedsmith-preflight/`), per
the repository's standing rule for seedsmith runs.

## 7. Acceptance (contract level)

1. A draft with a digit, an empty field, an echo of its role word, a taken name, or a length above its
   bound is rejected with the defect named. It is repaired at most `maxRepairs` times and then
   `unresolved`, never emitted and never given a fallback value.
2. A TRANSIENT error mid-run resumes without a new call for completed entries. A stub transport counts
   calls, and the count after resume equals the count of never-attempted entries.
3. The proof call runs before any naming call. A stub that returns prose makes the run abort with zero
   naming calls.
4. A rerun over unchanged inputs makes **zero** calls and leaves the accepted store and the corpus tree
   byte-identical (hash test).
5. Changing an entry's drawn enums, or bumping `promptVersion`, stales exactly the affected entries.
   Changing the resolved model stales none.
6. The accepted store and every emitted row carry the resolved model id, never a default constant
   (checked against a stub resolver returning a known id).
7. The whole suite passes with the transport stubbed to raise.
8. No test asserts a generated name, flavour or reason. Tests assert presence, bounds, uniqueness,
   script, and the absence of digits.
9. The avoid-list never causes a rejection. A fixture term in the avoid-list appears in the rendered
   prompt, and a draft containing it is accepted if it passes every other validator.
10. (Audit 2026-09-20) **Ids are frozen:** regenerating a stale entry with a different name keeps its `id`
    byte-identical in the accepted store and the emitted row; a fixture save referencing that id still
    loads its structure.

## 8. Test plan and verification boundary

`test_world_namer.py` covers criteria 1-9 with a scripted stub transport that returns canned drafts per
attempt and counts calls. The structures `NamingFamily` has its own tests next to it. There is no real
call in any test.

**Verification boundary: a gap.** `gk-forge/tools/seedsmith/**` and `data/seed/structures/_generation/**` are
unmapped (`gk-core/scripts/verify-change.py:771`). The owner of the fix is `test-verification-boundary`
`python-test-lane`. The pytest command in §6 is the boundary.

## 9. Hard edges

- **Model spend.** The proof and naming calls run on the local model configured through seedsmith's
  config layer. The first batch is small and reviewed before any larger run. That is the owner's
  standing phased-rollout rule for generators.
- **The accepted store is generated output.** It is never hand-edited, and a bad accepted entry is fixed
  by changing inputs (enums, prompt version) and regenerating that entry.
- **`call_with_self_heal`'s fallback** must be overridden (`default_for` → `unresolved`). A test proves
  that no original or blank value is ever emitted.

## 10. Dependencies

- Upstream: `call-budget-dry-run` (planned entries, the prompt builder), `corpus-metrics` (the pre-run
  closed-loop gate), `world-name-index`, `world-exemplars`.
- Cross-map (soft): `narrative-seed` `script-check` (`script_policy`; `language_consistency` until then),
  `narrative-seed` `model-config-resolve` (late resolution; `resolve_live_transport` until then),
  `ip-censor` `avoid-list` (advisory text in the brief).
- Downstream: `trade-structure-rows`, `legion-seed-rows`.

## 11. Open questions

- **The first batch size.** It is a plan-time decision the owner confirms before tokens are spent (the
  phased-rollout rule). Recommendation: the whole first structure deficit if it is at most five entries,
  otherwise five. This is the only thing in this spec that waits on the owner.

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: seedsmith pipeline (transport, self-heal, validators), structures adapter, accepted store.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares its paths.
[x] Read this session: ai-native README (all), seedsmith-map P1-P5, seedsmith-design skill Step 3,
    generate_anchor.py and llm_caller.py (cited ranges), ip-censor IC-3 in its section,
    narrative-seed spec-model-config-resolve and spec-script-check (headers and structure).
[x] decisions.md: no lock on naming beyond the Keepverse split (paths only).
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: max_heal default, default_for fallback, config binding at definition time.
[x] Read surrounding sections (IC-3's row, llm_caller's max_tokens incident note).
[~] Tested: no real call made (none authorized). The proof call is the run's first act.
[x] No §2 invariant contradicted.
[x] Corrections propagated: avoid-list advisory and flavor ownership, recorded in the map and sibling specs.
[x] No population pin; no generated-text assertion.
[x] No cache; resume order-independence is criterion 2; no actor magnitude.
[x] SOLID: one namer for every family; one prompt builder shared with the dry run.
[ ] New rule registry row: none (the digit rule is a validator inside the stage).
```

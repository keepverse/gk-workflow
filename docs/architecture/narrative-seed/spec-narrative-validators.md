# Spec: `narrative-validators`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `narrative-validators` · **Map row:** 12 · **Wave:** 3
**Depends on:** `narrative-contract`, `names-registry`, `script-check` · **Model calls:** none
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §6.2 (structural validators), §6.5 and §6.5b (text rules)
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Give every narrative seed a battery of **deterministic, closed-loop** checks that decide whether a draft
is structurally legal and mechanically clean before it is written. Each check is a pure function of
`(draft, context)` that returns defect strings naming the field and the offending value, so the same
strings drive the bounded repair prompt in the pipelines (`storylet-pipeline`, `character-pipeline`,
`arc-pipeline`, `spine-pipeline`, `gloss-fill`).

Two families:

- **Structural** (storylets): choice count, exactly one `leave`, no lose-lose, no dominated choice, a
  computed **choice type** (relaxed and dilemma-with-upside pass; obvious, all-bad dilemma and unchoice
  fail), and conditional choices worth at least as much as the best unconditional one.
- **Text** (every text field of every seed kind): script check, `field_echo`, `subject_name_echo`, name
  collision, token and placeholder closure, no digits, a length bound per field, no literal name from the
  names registry or the species catalog, no entity absent from the lore packet, an out-of-world word list
  matched on word boundaries, a round-trip render against two name sets, and the counter-doctrine line
  rule for enemy-side characters (R13).

**What "pass" means.** A pass is reported as *mechanically valid*, never *good*
(`seedsmith/spec-quality-gates.md` §2.4). Voice, tone, lore fit and "is this choice interesting" are
open-loop and belong to `review-render` and `narrative-metrics`, never to this module.

## Design

### 1. Where the checks live

The repo already has a tier-2 validator library: pure functions in
`gk-forge/tools/seedsmith/seedsmith/workflow/validators/`, each returning defect strings, tier-labelled in the
`TIER` table (`gk-forge/tools/seedsmith/seedsmith/workflow/validators/registry.py:20-27`) and run by
`run_validators` (`gk-forge/tools/seedsmith/seedsmith/workflow/validators/registry.py:49`). This module extends it;
it builds no second validator runner.

| Check group | Location | Why there |
|---|---|---|
| Feature-agnostic prose checks: no digit, length bound, word list on word boundaries | `tools/seedsmith/seedsmith/workflow/validators/prose.py` (new) | No narrative knowledge; any adapter can use them (seedsmith P5 keeps the core feature-agnostic) |
| Narrative checks: structure, choice type, token closure, literal names, lore-packet entities, round-trip render, R13 line rule | `tools/seedsmith/seedsmith/adapters/narrative/validators/` (new) | They read narrative registries and contracts, so they belong to the adapter |
| Reused unchanged | `field_echo` (`gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py:15`), `subject_name_echo` (`:48`), `name_collision` (`:69`), `SemanticDedup` (`gk-forge/tools/seedsmith/seedsmith/metrics/dedup.py:122`) | Already built for this defect class |
| The script check | `script_policy` in `gk-forge/tools/seedsmith/seedsmith/workflow/validators/scripts.py` (new, owned by `script-check`) | Built in wave 0 ([spec-script-check.md](spec-script-check.md) §4); it replaces the U+4E00–9FFF regex at `gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py:33` as the script test |

`name_collision` has no row in `TIER` today (`gk-forge/tools/seedsmith/seedsmith/workflow/validators/registry.py:20-27` lists six validators, not it). This
module adds its row alongside the new validators' rows, so every validator a narrative run calls carries
its tier label.

### 2. Structural checks (storylets)

Inputs: the resolved structure of one storylet as `narrative-contract` defines it — the planned choice
slots, each slot's choice kind, condition and `outcomes[]` of `{ordinal, consequence, effects, dropBand}`.
The ordinal vocabulary is the existing closed list `good · mixed · bad · nothing`
(`gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json:52-55`); consequence kinds come from `storylet-vocab`.

Each rule below rejects with a named defect:

| Defect id | Rule | Reason |
|---|---|---|
| `choice-count` | 2 to 4 choices | ideal §6.2; FTL's measured distribution |
| `leave-count` | exactly one `leave` | the escape hatch in every storylet (npc-story-events NS7) |
| `lose-lose` | at least one always-eligible choice **other than `leave`** has an outcome whose ordinal is not `bad` | Total War's lose-lose complaints (ideal §6.2). Audit 2026-09-19: without the `leave` exclusion the rule could never fire — every storylet's `leave` resolves `nothing`, which is not `bad` |
| `dominated-choice` | see §2.2 | a dominant option is a non-choice |
| `choice-type` | the computed type (§2.1) is `obvious`, `all-bad` or `unchoice` | Mawhorter's choice poetics, ideal §5.3 |
| `conditional-value` | every conditional choice (`use`, `bring`, `offer`) has a best ordinal at least equal to the best ordinal of the best unconditional choice | FTL: the blue option pays for bringing the right thing |
| `names-good-option` | **soft** (recorded, never a rejection or a repair): `situation` contains a choice's `label` text verbatim next to an evaluative ordinal word (`good`, `bad`) on word boundaries | the dungeon contract's *"flavour never names the good option"* (`docs/architecture/party-dungeon/spec-dungeon-seed-contract.md` line 83). Audit 2026-09-19: the rule used to reject any ordinal or consequence display word, but `good`, `bad`, `nothing` and `mixed` are ordinary English ("there is nothing here"), so it would have spent repairs on false positives and cannot prove its own fix (P3). It now feeds `review-render`'s queue only |
| `enemy-consequence` | no `recruit` targets, and no `relation.shift` is about, a role whose allegiance is `antagonist` or whose `requires` names an antagonist `characterRole` | R13 rules 1 and 3 (`storylet-vocab` §3.5 negative clauses; `character-vocab` §6 rule 3). Audit 2026-09-19: both registries named this validator as the enforcer, and it did not exist |
| `consequence-ref-unfillable` | every `relation.shift` and `recruit` outcome has a `ref` by `narrative-contract` §5's derivation rule | a consequence with no target cannot be routed by the runtime |
| `role-undeclared` | every `{role_<id>}` token in any text field names a role declared in `roles[]` | no dangling reference in prose |

**Ordinal order.** Comparison uses the closed order `bad < nothing < mixed < good`, declared once as a
module constant with a comment. It is a structural ranking of a closed vocabulary, not a tunable: changing
it changes what "better" means, not how the game feels.

#### 2.1 The choice-type classifier

Computed over the **open set**: every always-eligible choice (unconditioned kinds plus `leave`).
Conditional choices are excluded on purpose: when the player meets a condition, the conditional option is
*meant* to be the best (FTL's blue option), so including it would flag every well-built `bring` storylet
as obvious. The `conditional-value` rule covers conditional choices instead.

For each choice `o`: `meets(o)` = some outcome is `good` or `mixed`; `fails(o)` = some outcome is `bad` or
`mixed`; `safe(o)` = `meets(o)` and not `fails(o)`. A choice's **profile** is the sorted multiset of its
`(ordinal, consequence)` pairs.

```text
open     = always-eligible choices, leave included
if distinct profiles in open < 2              -> unchoice          (reject)
meeting  = { o in open : meets(o) }
safe     = { o in open : safe(o) }
if meeting is empty                           -> all-bad           (reject)
if |meeting| == 1 and safe == meeting         -> obvious           (reject)
if safe is empty                              -> dilemma-upside    (pass)
otherwise                                     -> relaxed           (pass)
```

`ChoiceType` is a closed enum of five members — `relaxed`, `dilemma-upside`, `obvious`, `all-bad`,
`unchoice`. Its member count is a **declaration** and is pinned by test, because a sixth type is a
reviewed change to what the gate accepts. The computed type is also exposed to `review-render` (it prints
it next to each sample) and to `narrative-metrics` (choice-type distribution is a reading).

Worked cases, each a named test: `[interact(good, bad), leave(nothing)]` → `dilemma-upside`;
`[interact(good), leave(nothing)]` → `obvious`; `[interact(bad), leave(nothing)]` → `all-bad`;
`[interact(nothing), leave(nothing)]` → `unchoice`; `[interact(good, bad), persuade(good), leave(nothing)]`
with different consequence kinds → `relaxed`.

#### 2.2 Dominance

Choice `A` is dominated by choice `B` when all of these hold:

1. `A` and `B` pay in the same set of consequence kinds (different kinds serve different goals and are
   not comparable — Mawhorter's multi-goal reading);
2. `best(A) ≤ best(B)` and `worst(A) ≤ worst(B)` in the ordinal order above;
3. `B`'s condition is no stricter than `A`'s (unconditioned is weakest; two conditions of the same kind
   compare by equality only — no condition ordering is invented);
4. `B` costs no more than `A` (only `offer:{stock}` carries a cost, so an `offer` is never "no more costly"
   than a non-offer).

`leave` is exempt as the dominated party: it is the required escape hatch and routinely resolves
`nothing`. The exemption is a comment in code, not a silent skip. Two choices with identical profiles
dominate each other and are reported once, naming both.

### 3. Text checks (every seed kind)

Every text field a contract marks AUTHORED is checked. Field lists come from `narrative-contract`'s
ownership tables, never from a list here, so a new text field is checked the day it is declared.

| Defect id | Check | Source of truth |
|---|---|---|
| `script` | every string leaf passes `script_policy` under its declared policy — `latin` for every English prose field, `none` for ids, keys and enum values; an undeclared string leaf is itself a defect | `script-check` ([spec-script-check.md](spec-script-check.md) §3–§4); the per-field policy map is declared with each schema in `narrative-contract`. `script_policy` accepts digits by design; the `digit` row below owns that rule |
| `field-echo`, `subject-name-echo`, `name-collision` | reused unchanged | `field_echo.py:15`, `:48`, `:69` |
| `token-closure` | every `{…}` token parses under the closed grammar, is declared for **this** seed (a `{c_<id>}` names a character in `context["allowedEntities"]`; a `{role_<id>}` names a declared role; a runtime slot is one the seed kind allows), every declared token the contract requires is used, and no stray brace or unclosed markup tag exists | `token-grammar` |
| `digit` | no character with Unicode general category `Nd` in the **literal text** of any text field (`token-grammar`'s `literal_text`); spelled-out magnitudes are the audit's concern, not this check's | principle 2: magnitudes reach text only through runtime slots. Audit 2026-09-19: the check read the whole field, so a declared token such as `{c_ember_mother_001}` — minted ids carry digits — would have failed; `narrative-contract` §11 already scopes it to literal text |
| `length` | the field's rendered length (tokens replaced by the longest display string in the names registry) is within its bound | the budget's `text.lengthBounds` block (§5) |
| `literal-name` | no field contains, case-insensitively and on word boundaries, the display string of any names-registry row or any species catalog name | `names-registry`; species names from `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` (`displayName`) plus the English species name table once `creature-seed` publishes one (§7 of the map) |
| `unknown-entity` | no capitalised proper-noun run outside a token matches a name the lore packet does not allow — implemented as: every proper noun a field introduces must be a token; a bare capitalised multi-word run that is not sentence-initial is a defect | `context["allowedEntities"]`, which the calling pipeline fills from the item's lore packet. Audit 2026-09-19: this module (Wave 3) does not depend on `lore-packet` (Wave 4); the list is a runtime input, and tests pass fixture lists |
| `out-of-world` | no word from the out-of-world list appears, matched on word boundaries | `data/seed/narrative/_registry/out-of-world.v1.json` (new) |
| `round-trip` | the field renders under name set A and name set B; both renders succeed, and the two outputs differ exactly at the token spans | `token-grammar`'s parser and renderer; the two name sets in §4 |
| `enemy-memory` | an enemy-side character has no line whose context is keyed to its own past encounters with the player | `character-vocab`'s R13 restriction rows |

**The repair message names the fix, not only the fault.** For `literal-name` the message is the ideal's
own: *"use the token `{lead_antagonist}`, not a name"* — the token is looked up from the registry row
that matched.

**Word-boundary matching is mandatory** for `literal-name` and `out-of-world`. AI Dungeon's keyword filter
flagged *"cockpits, breastplates and 4-year-old laptops"* because it matched substrings (ideal §5.1). A
test pins that a list word inside a longer word does not match.

**The out-of-world list is lore drift, not IP.** It holds words that break the setting (modern devices,
real-world institutions and the like). It never holds third-party marks, company names or real-person
names: those are `ip-censor`'s registry, scanned at release (IC-3), and a private IP list here is a
boundary violation (map §7). The registry's own description carries that negative clause, and a test
fails if any entry also appears in the `ip-censor` registry file when that file exists.

### 4. The two name sets for the round-trip render

Set A is the live names registry (`gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`, new, owned by
`names-registry`). Set B is a **deterministic scramble** built in memory from set A: every display string
is replaced by a synthetic string of the same feature tags (`article`, `gender`, `number`) that shares no
word with any set-A string (for example `Qa Vessor 1f3a`-style tokens derived from a hash of the token
id, with digits stripped). Building B in code rather than committing a second file means no one can
accidentally ship it, and it can never collide with a real name.

The check passes when both renders succeed and the diff between them touches only token spans. A literal
name baked into prose shows up as a span that did not change; a token the renderer cannot resolve shows up
as a failed render.

### 5. Tunables

All numbers this module reads live in the narrative generation budget file,
`gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new). `gloss-registry` creates the file in wave 0 with its
`gloss` block ([spec-gloss-registry.md](spec-gloss-registry.md) §3); this module adds its own block, and
`narrative-planner` adds the coverage rows. A change publishes
`budget.v{n+1}.json`; no number is a code constant.

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `text.lengthBounds.<kind>.<field>.{min,max}` | characters after token substitution | name 3–40; epithet 3–40; storylet `situation` 60–420; choice `label` 3–60; outcome `result` 20–240; character `bio` 60–420; line 3–160; arc `premise` 60–420; spine beat 3–240 | Sized to one card or one speech bubble; first values are starting shapes revised from `narrative-metrics` readings |

**Structural, not tunable (each commented in code):** the ordinal order; the five `ChoiceType` members;
the 2–4 choice count and one `leave` (contract rules owned by the storylet contract, repeated here as
checks); "two name sets".

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_validators_structure.py tools/seedsmith/tests/test_narrative_validators_text.py tools/seedsmith/tests/test_prose_validators.py -q
# Run the battery over the committed corpus (model-free; prints defects per seed, exit 1 on any)
cd tools\seedsmith; python -m seedsmith narrative validate --corpus ..\..\data\seed\narrative
# Classify one storylet and print its choice type and per-choice profile
cd tools\seedsmith; python -m seedsmith narrative validate --storylet <storyletId> --explain
```

The `narrative` command group is added to `gk-forge/tools/seedsmith/seedsmith/report/cli.py` by the adapter shell
(`narrative-contract`); this module adds the `validate` verb.

## Project structure

```text
tools/seedsmith/seedsmith/workflow/validators/prose.py                  (new) no_digit, length_bound, word_list_hits
gk-forge/tools/seedsmith/seedsmith/workflow/validators/registry.py               TIER rows for the new validators and name_collision
tools/seedsmith/seedsmith/adapters/narrative/validators/__init__.py     (new) battery per seed kind
tools/seedsmith/seedsmith/adapters/narrative/validators/structure.py    (new) §2 rules
tools/seedsmith/seedsmith/adapters/narrative/validators/choice_type.py  (new) §2.1 classifier, ChoiceType enum
tools/seedsmith/seedsmith/adapters/narrative/validators/text.py         (new) §3 narrative text checks
tools/seedsmith/seedsmith/adapters/narrative/validators/name_sets.py    (new) §4 scrambled set B
data/seed/narrative/_registry/out-of-world.v1.json                      (new) authored word list, description + negative clause
gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json                                (new, created by gloss-registry) text.lengthBounds block added
tools/seedsmith/tests/test_prose_validators.py                          (new)
tools/seedsmith/tests/test_narrative_validators_structure.py            (new)
tools/seedsmith/tests/test_narrative_validators_text.py                 (new)
```

## Code style

```python
def choice_type(choices: "Sequence[ChoiceSlot]") -> ChoiceType:
    """Mawhorter's classification over the open set (always-eligible choices, leave included).
    Conditional choices are excluded on purpose: meeting a condition is meant to make that option
    best; `conditional_value` checks them instead."""


def dominated_choice(draft: "Mapping[str, Any]", context: "Mapping[str, Any]") -> "list[str]":
    """Each defect names both choice slots, their kinds and their (best, worst) ordinals."""
```

One pure function per rule, `(draft, context) -> list[str]`, the signature every existing validator uses.
Defect strings name the field, the slot and the offending value.

## Testing strategy

`pytest`, fixtures only — never the committed corpus, so tests keep testing after the corpus is repaired
(`seedsmith/spec-metrics.md` §6). Every narrative test module stubs the model transport with a callable
that raises, the `FakeCall` shape of `gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py:49`, so any
accidental model call fails the suite.

| Test | Asserts |
|---|---|
| `choice_type_members_are_pinned` | `ChoiceType` has exactly five members (a declaration; the reason is in the test docstring) |
| `choice_type_worked_cases` | the five worked cases in §2.1 yield their stated types |
| `conditional_choices_do_not_make_a_storylet_obvious` | `[interact(good,bad), leave, bring(good)]` is `dilemma-upside` and passes `conditional-value` |
| `conditional_worse_than_unconditional_is_rejected` | a `use` whose best is `mixed` beside an `interact` whose best is `good` fails `conditional-value` |
| `leave_is_never_the_dominated_party` | `leave(nothing)` beside `interact(good,bad)` yields no dominance defect |
| `same_profile_twice_is_one_defect_naming_both` | two identical profiles report once, both slots named |
| `different_consequence_kinds_are_not_comparable` | `interact(good; loot)` vs `persuade(good; relation.shift)` is not dominance |
| `choice_count_and_leave_count` | 1 and 5 choices fail; zero and two `leave` fail |
| `lose_lose_rejected` | every non-`leave` always-eligible outcome `bad` fails beside a `leave(nothing)`; one non-`bad` outcome passes |
| `digit_inside_a_token_is_not_prose` | `"{c_ember_mother_001} nods"` passes `digit`; `"gain 5 souls"` fails |
| `names_good_option_is_soft` | a situation quoting a label beside `good` is recorded as a soft defect and triggers no repair |
| `enemy_consequence_rejected` | `recruit` or `relation.shift` targeting an antagonist-allegiance role fails, naming slot, outcome and role |
| `consequence_ref_unfillable_rejected` | a `relation.shift` whose storylet declares no qualifying role fails |
| `allowed_entities_come_from_context` | with a fixture `allowedEntities`, a `{c_x}` outside it fails; no lore-packet import exists in this module |
| `digit_in_any_text_field_rejected` | `"gain 50 souls"` fails; `"gain {reward}"` passes; a non-ASCII decimal digit fails |
| `literal_name_rejected_on_word_boundary` | `"the Rotwright laughs"` fails with the repair naming `{lead_antagonist}`; a list name inside a longer word does not match |
| `out_of_world_word_boundary` | a list word matches alone; the same letters inside a longer word do not (the AI Dungeon case) |
| `out_of_world_list_holds_no_ip_mark` | with a fixture `ip-censor` registry, an overlapping entry fails the registry check |
| `token_closure` | an undeclared `{c_x}`, an unknown slot, a stray `{`, an unclosed `<em>` each fail; a declared, used set passes |
| `round_trip_detects_a_baked_name` | a field containing a registry display string fails because that span is identical under both sets |
| `round_trip_set_b_shares_no_word_with_set_a` | the scrambled set is disjoint from the live set and keeps each row's feature tags |
| `enemy_side_line_keyed_to_own_encounters_rejected` | an enemy-side character with a line context flagged by `character-vocab` as personal memory fails `enemy-memory` |
| `defect_strings_name_field_and_value` | every validator's defect names its field and the offending value (the repair prompt depends on it) |
| `every_validator_has_a_tier_row` | every function the narrative battery runs has a `TIER` entry, including `name_collision` |
| `pass_is_reported_as_mechanically_valid` | the battery's summary uses `ValidatorResult.summary()` wording, never "good" |

No test asserts a count of seeds, defects in the committed corpus, or any generated text.

## Success criteria

1. Every rule in §2 and §3 exists as a pure function with a failing and a passing fixture.
2. The choice-type classifier is total over any legal structure and its five members are pinned.
3. `literal-name` and `out-of-world` match on word boundaries, proven by the AI Dungeon-shaped fixture.
4. The round-trip render rejects a baked-in name and accepts a fully tokenised field.
5. Every narrative validator carries a tier-2 label; no summary calls a pass "good".
6. The suite passes with the model transport stubbed to raise.
7. `gk-core/scripts/enforcement-registry.v1.json` gains a row for the no-literal-name validator (map §13 checklist);
   the row is added in this module's change.

## Boundaries

- **Always:** pure functions of `(draft, context)`; defect strings that name field and value; word-boundary
  matching for every word list; field lists read from the contract; tunable bounds from the budget file.
- **Ask first:** a sixth `ChoiceType`; changing the ordinal order; adding a check that needs a model (it
  would be tier 3 — `seedsmith/spec-quality-gates.md` §2.3 keeps CoVe unbuilt); relaxing the `leave`
  exemption.
- **Never:** check third-party IP marks here (IC-3 makes the scan a release gate); keep a private IP word
  list; call a model; report a tier-2 pass as quality; read or assert the size of the committed corpus;
  edit a generated seed to make a check pass.

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
| 1 | high | `lose-lose` could never fire: every storylet's `leave` resolves `nothing`, which is not `bad` | fixed (excludes `leave`) |
| 2 | medium | `digit` read the whole field, so minted token slugs with digits would fail | fixed (literal text only) |
| 3 | medium | R13 recruit/relation rule was named as enforced here by two registries but did not exist | fixed (`enemy-consequence`) |
| 4 | medium | `names-good-option` matched common English words; false positives spend repairs and the fix is not machine-verifiable (P3) | fixed (soft, review signal) |
| 5 | medium | Wave-3 module depended on Wave-4 `lore-packet` for the allowed-entity list | fixed (`context["allowedEntities"]`) |
| 6 | low | `effect` vs contract `effects` | fixed |

# Spec: `script-check`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `script-check` · **Map row:** 2 · **Wave:** 0
**Depends on:** none · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.

---

## Objective

Give seedsmith one deterministic check that sees the defect that actually shipped: foreign-script
fragments inside target-language prose. Replace the single-range test in the shared language validator
with a character classifier that covers every CJK form, kana, Hangul, fullwidth forms, CJK punctuation
and Cyrillic, and add a validator that enforces a **declared target-script policy per field**.

Why this matters: 53 of the 54 committed Delve events carry Han characters in `name` or `flavor`
(`narrative-seed-map.md` §3.4), and the shipped check could not have caught all of them even if it had
run — its range is U+4E00–9FFF only (`gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py:33`).
Language identification cannot see this defect either: fastText calls "English with two Chinese words"
English (`narrative-seed-ideal.md` §5.4). A per-character script check can.

**Done means:** the classifier and the policy validator exist as pure functions with positive and
negative tests per script class; `language_consistency` uses the classifier with its existing behaviour
preserved; both carry tier labels. Wiring the check into a generator's retry loop is the consumer's job
(`dungeon-generator-repair` for the Delve events, `narrative-validators` for narrative seeds).

---

## Design

### 1. What exists (verified 2026-09-19)

| Fact | Evidence |
|---|---|
| The only script test is one regex range, U+4E00–9FFF | `gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py:33` |
| `language_consistency` rejects a value **mixing** CJK and 3+-letter Latin words, in either direction; an all-CJK value passes on purpose | `gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py:38-61`; the all-CJK pass is pinned by `gk-forge/tools/seedsmith/tests/workflow/validators/test_language.py:59-65` |
| Its consumers | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/commander_effect.py:21`, `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py:251`, `gk-forge/tools/seedsmith/seedsmith/metrics/content_completeness.py:129` |
| The dungeon adapter never imports it | its retry loop calls the motif checks only, `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334` |
| Validators are tier-labelled | `gk-forge/tools/seedsmith/seedsmith/workflow/validators/registry.py:20` |
| A second copy of the narrow range lives in the motif deriver | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/motifs.py:52` — out of scope here (it segments Chinese source text, it does not police output) |

**Gaps the one range misses** (each has a test fixture below): CJK Extension A (U+3400), Extension B
and beyond (U+20000), compatibility ideographs (U+F900), CJK punctuation such as the ideographic comma
(U+3001), fullwidth Latin and digits (U+FF21, U+FF11), hiragana (U+3042), katakana (U+30A2), halfwidth
katakana (U+FF71), the prolonged sound mark (U+30FC), Hangul syllables (U+AC00) and Cyrillic (U+0430).

### 2. The classifier — standard library only

Python's `re` has no Unicode script property, and seedsmith pins every dependency exactly
(`gk-forge/tools/seedsmith/pyproject.toml:11-22`); the third-party `regex` package is not installed. The Unicode
character database that ships with Python (`unicodedata`) gives each assigned code point a general
category and a name, and the names of letters encode their script. The classifier uses both.

`script_of(ch) -> ScriptClass`, a closed enum. The validator normalises every string to NFC before
classifying (Audit 2026-09-19: without it a decomposed `é` — `e` plus U+0301, category `Mn` — lands in
`other` and English text with an accented loanword is refused). Rules apply in order; the first match wins:

| Class | Rule | Examples |
|---|---|---|
| `fullwidth` | name starts `FULLWIDTH ` or `HALFWIDTH ` and the code point is not katakana | U+FF21, U+FF11, U+FF0C |
| `kana` | name starts `HIRAGANA`, `KATAKANA` or `HALFWIDTH KATAKANA` | U+3042, U+30A2, U+FF71, U+30FC |
| `han` | name starts `CJK UNIFIED IDEOGRAPH` or `CJK COMPATIBILITY IDEOGRAPH` | U+4E00, U+3400, U+20000, U+F900 |
| `hangul` | name starts `HANGUL` | U+AC00, U+1100 |
| `cjk-punctuation` | code point in U+3000–303F, or name starts `IDEOGRAPHIC` | U+3001, U+3002, U+300C |
| `cyrillic` | name starts `CYRILLIC` | U+0430 |
| `latin` | category `L*` and name starts `LATIN` | `a`, `é` (U+00E9) |
| `digit` | ASCII `0`–`9` | `7` |
| `common` | whitespace, ASCII punctuation, and the General Punctuation block U+2000–206F (dashes, curly quotes, ellipsis) | `'`, U+2014, U+2019 |
| `other-letter` | any other category `L*` | Greek, Arabic |
| `other` | everything else, including unassigned code points and symbols | emoji |

**Honesty about the mechanism.** This is a name-prefix classifier over the Unicode character database,
not the Unicode `Script` property itself. For the classes above the two agree; the tests pin one
representative code point per class so a Python upgrade that renames a character fails loudly instead of
silently reclassifying it.

### 3. Target-script policy — declared per field

A closed enum, one value per field path:

| Policy | Accepts | Rejects | Negative clause |
|---|---|---|---|
| `latin` | `latin`, `digit`, `common` | every other class | not a language check: English and French both pass; it polices script only |
| `han` | `han`, `cjk-punctuation`, `fullwidth` punctuation, `digit`, `common`; Latin words shorter than three letters | `kana`, `hangul`, `cyrillic`, `other-letter`, and a Latin word of three or more letters (the mixing rule already in `language_consistency`) | not a Chinese-quality check; it exists so a Chinese-target corpus (creature commander effects) can adopt the same mechanism |
| `none` | anything | nothing | for fields that carry no prose (ids, enum values, keys); a prose field declared `none` is a contract defect the adapter's own schema audit rejects |

Digits are not this module's concern: `digit` is accepted by `latin` and `han`, and the no-digit rule for
narrative prose belongs to `narrative-validators` (map row 12). Keeping them apart means one defect gets
one message.

**Field paths.** A policy map keys dotted paths with `[]` for array items — `name`, `flavor`,
`choices[].label`, `choices[].outcomes[].result`. The validator walks dicts and lists and matches each
string leaf's path against the map.

### 4. The two validators

```python
def script_policy(draft: Mapping[str, Any], context: Mapping[str, Any]) -> list[str]:
    """Reject any string leaf whose characters fall outside its field's declared policy
    (context["scriptPolicy"]: Mapping[str, Policy]). A string leaf with no declared policy is itself
    a defect — an undeclared field is how a new prose field would slip past the check."""

def language_consistency(draft, context) -> list[str]:   # existing name and signature, unchanged
    """Now detects 'the CJK side' with the classifier (han, kana, hangul, cjk-punctuation, fullwidth
    letters) instead of the one range. Behaviour otherwise identical, so its existing tests stay green."""
```

Defect strings name the field path, the offending characters (the first few, as code points and
glyphs), and their class — for example
`field 'flavor' contains han characters '火力' (U+706B U+529B); this field's policy is latin — write it
entirely in the target language`. The number of characters quoted is a display bound, not a tunable; its
constant carries a comment saying so. The string is what a repair prompt reads (`spec-quality-gates.md`
§5), so it names the fix, not only the fault.

Both validators are **tier 2, deterministic**: `script_policy` joins `TIER`
(`gk-forge/tools/seedsmith/seedsmith/workflow/validators/registry.py:20`) and is exported from the package
`__init__`. A pass is "mechanically valid", never "good" (`spec-quality-gates.md` §2.4).

### 5. What this module does not do

It does not call either validator from any generator (the consumers own their wiring), does not run
language identification, does not touch the motif deriver's own regex, and does not edit any committed
seed.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/workflow/validators/test_scripts.py -q
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/workflow/validators/test_language.py -q
```

## Project structure

```text
gk-forge/tools/seedsmith/seedsmith/workflow/validators/scripts.py        (new) ScriptClass, script_of, Policy, script_policy
gk-forge/tools/seedsmith/seedsmith/workflow/validators/language.py       language_consistency uses the classifier
gk-forge/tools/seedsmith/seedsmith/workflow/validators/registry.py        TIER row for script_policy
gk-forge/tools/seedsmith/seedsmith/workflow/validators/__init__.py       export script_policy
gk-forge/tools/seedsmith/tests/workflow/validators/test_scripts.py       (new)
```

`scripts.py` imports nothing from LangGraph, a model or an adapter, like every module in this package
(`seedsmith/spec-workflow-runtime.md` §2.1).

## Code style

One pure function per validator, `(draft, context) -> list[str]`, matching
`gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py:15`. `ScriptClass` and `Policy` are `Enum`s;
the rule table in §2 is data in one tuple, read in order, so adding a class is one row plus one fixture.

## Testing strategy

| Test | Asserts |
|---|---|
| `each_class_has_a_pinned_representative` | one code point per class in §2 classifies as named (U+3400, U+20000, U+F900, U+3001, U+FF21, U+FF11, U+3042, U+30A2, U+FF71, U+30FC, U+AC00, U+0430, U+00E9, U+2014) |
| `latin_policy_rejects_each_foreign_class` | one fixture per rejected class; each defect names the field and the class |
| `latin_policy_accepts_plain_english_with_curly_quotes_and_dashes` | over-refusal is its own defect |
| `decomposed_accent_is_normalised` | `"cafe\u0301"` passes under `latin` after NFC |
| `real_dungeon_defect_is_caught_under_latin_policy` | the committed text already used by `test_language.py` (`火力`, `分配`) is rejected |
| `han_policy_accepts_all_chinese_and_rejects_hangul` | the Chinese-target case stays legal |
| `undeclared_string_leaf_is_a_defect` | a draft with a string field missing from `scriptPolicy` fails, naming the path |
| `array_paths_match` | `choices[].label` covers every choice's label |
| `none_policy_skips_the_field` | an id with digits and hyphens passes under `none` |
| `language_consistency_existing_tests_unchanged` | `test_language.py` passes untouched |
| `language_consistency_now_sees_kana_and_ext_a` | an English sentence with a kana or Extension-A fragment is rejected (was a miss) |
| `script_policy_is_tier_two` | `TIER["script_policy"] is Tier.DETERMINISTIC` |
| `ScriptClass_and_Policy_are_closed` | member lists pinned — a declaration: a new class or policy is a reviewed change with a fixture |

## Boundaries

- **Always:** classify per character; name field, characters and class in every defect; declare a
  policy for every string field a consumer checks.
- **Ask first:** adding a third-party Unicode dependency; adding a policy value.
- **Never:** language identification as a gate; a silent default policy for an undeclared field;
  wiring the check into a generator from this module.

## Success criteria

- [ ] Every class in §2 is proven by a pinned code point.
- [ ] Under `latin`, the committed dungeon defect text is rejected and plain English with typographic
      punctuation is accepted.
- [ ] `language_consistency` keeps its existing tests green and now rejects kana, Hangul and Extension-A
      mixing.
- [ ] `script_policy` is tier 2 and exported; no generator is changed by this module.
- [ ] The seedsmith suite is green with the transport stubbed to raise.

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
| 1 | low | No NFC normalisation: a decomposed accent is category `Mn` and would be refused under `latin` | fixed (§2 + test) |
| 2 | low | Tier-2 labelling, no generator wiring from this module, closed enums pinned as declarations — conform | verified |
| 3 | low | Citations sampled: `language.py:33`, `test_language.py:59-65`, `gk-forge/tools/seedsmith/seedsmith/workflow/validators/registry.py:20`, `motifs.py:52`, `field_echo.py:15` — resolve | verified |

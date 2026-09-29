# Spec: `token-grammar`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `token-grammar` · **Map row:** 8 · **Wave:** 1
**Depends on:** none · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.
**Rulings this module implements:** R8–R11 — story text uses the game's own names, as parameters
(`npc-story-events-ideal.md` §10); names are tokens, never words (map §2 principle 14).

---

## Objective

Define the closed grammar every piece of generated story text is written in: **entity tokens** for the
three leads, named characters and cast roles; **runtime slots** the game fills; a closed set of **semantic
markup** tags; and the **feature arguments** (gender, number, article) that let a message agree with
whatever name the registry holds. Each token carries a description and a negative clause for the brief.

A story string then has three parts and only one of them is words (`narrative-seed-ideal.md` §6.5b):
literal text, tokens resolved from the names registry and the runtime cast, and markup rendered by the
presentation layer. The model never sees a real name, so it cannot leak one, and renaming a lead is one
registry edit.

This module also owns the two pure functions every other module uses on text: **`parse`** (split a string
into literal, token and markup segments, refusing anything outside the grammar) and **`expand`** (turn the
model's short token forms into full ICU MessageFormat, the form lingui renders).

**Done means:** `tokens.v1.json` exists; `parse` and `expand` are pure, total over the grammar and refuse
everything else; every token family has a description and a negative clause; the expansion of every form
is proven by tests.

---

## Design

### 1. Why ICU, and why nothing new

Lingui, the repo's one translation library, renders ICU messages with named placeholders and `select`
(`narrative-seed-ideal.md` §6.5b, prior art). Its macro accepts only compile-time literals
(`gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts:13-19`), which is why seed strings reach it
through a runtime-owned codegen bridge (`npc-story-events-map.md` row 11). This grammar produces strings
that bridge can copy verbatim: plain ICU, no custom syntax.

### 2. `gk-data/packs/fusion/data/seed/narrative/_registry/tokens.v1.json` (new)

```json
{
  "schemaVersion": 1,
  "registryVersion": 1,
  "entityFamilies": { "<family>": { "pattern": "<regex>", "description": "...", "negative": "..." } },
  "leads":         { "<token>": { "description": "...", "negative": "..." } },
  "forms":         { "<suffix>": { "description": "...", "negative": "..." } },
  "pronouns":      { "<suffix>": { "description": "...", "negative": "..." } },
  "slots":         { "<name>":  { "description": "...", "negative": "..." } },
  "features":      { "gender": ["male", "female", "neuter", "none"],
                     "number": ["singular", "plural", "none"],
                     "article": ["definite", "none"] },
  "markup":        { "<tag>":  { "shape": "paired | empty", "description": "...", "negative": "..." } }
}
```

### 3. Entity tokens

| Family | Form | Description (short, for the brief) | Negative clause |
|---|---|---|---|
| lead | `{lead_summoner}` | the player's own summoner, the one the story follows | write the token; it is not a name, and you never invent one for it |
| lead | `{lead_companion}` | the time-travelling companion at the summoner's side | not a creature from the roster; never name it |
| lead | `{lead_antagonist}` | the villain of the chase, whose broken time engine scattered the pieces | write the token itself; it is not a name, and you never invent one for it |
| character | `{c_<slug>}` | a named creature declared for this seed | only a character the seed declares; never a species name, never an invented person |
| character epithet | `{c_<slug>_epithet}` | that character's title-like epithet | not a second name; use it for variety, not to introduce someone new |
| role | `{role_<roleId>}` | whoever the game casts into a role this storylet declares | not a specific creature; you do not know who fills it |

`<slug>` is **derived**, never written by a model: the character id's body with `.` and `-` replaced by
`_`, matching `^[a-z][a-z0-9_]*$` (the id grammar guarantees the leading letter — `spec-narrative-contract.md`
§3, Audit 2026-09-19). The map's and the runtime's `{c_<characterId>}` notation means this slug; the runtime
resolves a slug back to its character id through `slug_for`'s inverse over the corpus, never by string
surgery. ICU argument names cannot contain `.` or `-`, which is why ids are not
used directly. Two ids that would produce the same slug are refused by `slug_for`, and so is a slug or
role id ending in a reserved suffix (`_epithet`, `_start`, `_bare`, `_subj`, `_obj`, `_poss`, `_article`,
`_gender`, `_number`), so a token always parses one way. `<roleId>` matches `^[a-z][a-z_]*$` and is local
to the storylet that declares it (`storylet-vocab` §3.6).

**Forms** (suffix on any lead or character token; a role token takes the running form only):

| Form | Suffix | Meaning | Negative clause |
|---|---|---|---|
| running | none | the name as it reads mid-sentence, with its article if it has one ("the Rotwright") | not for the start of a sentence |
| start | `_start` | the same, capitalised for the start of a sentence ("The Rotwright") | not for mid-sentence use |
| bare | `_bare` | the name without its article, for address ("You are too late, Rotwright.") | not a nickname; it is the same name without "the" |

**Pronouns** (suffix on a lead or character token): `_subj` (he / she / it), `_obj` (him / her / it),
`_poss` (his / her / its). Negative clause: *a pronoun token stands for this entity only; it is not a
pronoun you choose — the game picks it from the entity's registry tags, so a rename cannot make it wrong.*

### 4. Runtime slots

| Slot | Description | Negative clause |
|---|---|---|
| `{place}` | where this happens, filled by the game | never write a place name |
| `{supply}` | the supply a `use` choice spends | never name an item |
| `{reward}` | what the player gains | never write an amount; the game fills it |
| `{cost}` | what the player pays | never write an amount; the game fills it |

A slot is filled with a complete noun phrase by the runtime; it takes no form or pronoun suffix. The
rendered value may contain digits — magnitudes belong to the runtime (map §2 principle 2) — but seed text
never does.

### 5. Feature arguments and `expand`

For every lead or character token `T`, the runtime supplies four ICU arguments: `T` (the display string),
`T_article`, `T_gender`, `T_number` (the registry row's tags, `names-registry`). The model never writes
`select`; it writes the short forms above, and `expand` rewrites them deterministically:

| Short form | Expanded ICU |
|---|---|
| `{T}` | `{T_article, select, definite {the {T}} other {{T}}}` |
| `{T_start}` | `{T_article, select, definite {The {T}} other {{T}}}` |
| `{T_bare}` | `{T}` |
| `{T_subj}` | `{T_gender, select, male {he} female {she} neuter {it} other {<running form of T>}}` |
| `{T_obj}` | `{T_gender, select, male {him} female {her} neuter {it} other {<running form of T>}}` |
| `{T_poss}` | `{T_gender, select, male {his} female {her} neuter {its} other {<running form of T>'s}}` |

So the message selects on closed registry tags and the registry never stores an article-bearing string —
the ideal's rule (`narrative-seed-ideal.md` §6.5b: *"a title-style name needs its article handled by the
message, not the registry"*). A gender of `none` falls back to repeating the name, which is always
grammatical. A sentence-initial pronoun is written with `_start` on the token instead (`{T_start}`), so no
capitalised pronoun is needed in v1.

`article` admits `definite` and `none` only. An indefinite article would need a vowel-sound tag to choose
"a" or "an"; no named entity needs one, so it is a later reviewed widening. `number` is carried for
translations; in English v1 every entity row is `singular` (`names-registry` enforces it), so pronoun
expansion never meets a plural.

`expand` also escapes apostrophes per ICU rules where one would otherwise start a quoted span, so English
contractions survive. It is idempotent on already-expanded text (a second call changes nothing).

### 6. Semantic markup

| Tag | Shape | Meaning | Negative clause |
|---|---|---|---|
| `<em>…</em>` | paired | stress on the enclosed words | not bold or colour; the presentation layer owns style |
| `<whisper>…</whisper>` | paired | spoken quietly | not a secret the player cannot read |
| `<shout>…</shout>` | paired | spoken loudly | not capital letters |
| `<pause/>` | empty | a beat of silence in speech | not a line break; never at the start or end of a string |

A reviewed widening of `docs/architecture/item/seed-contract.md` §6's *"markup forbidden"* rule to
semantic tags only, never HTML or styling (map §11 item 3). Mapping the tags to lingui's rich-text form is
the codegen bridge's job, not this module's. Rules: tags do not nest inside the same tag; tokens may sit
inside a paired tag; no tag sits inside a token; `<` and `>` appear nowhere else.

### 7. `parse` — the closure every validator uses

`parse(text) -> tuple[Segment, ...]` where a segment is `Literal(text)`, `Token(family, name, form)` or
`Markup(tag, open | close | empty)`. It refuses, naming the position and the offending span: an unknown
family or slot; a malformed slug; a form or pronoun suffix on a role or slot; an unbalanced brace; a
literal `{` or `}`; an unknown or unbalanced tag; a stray `<` or `>`; any `select`, `plural` or `#` in a
short-form string (the model writes short forms only).

Helpers built on it: `tokens_used(text) -> frozenset[str]` (for the contract's declared-token closure),
`literal_text(text) -> str` (the literal segments joined — the only part the no-digit and
no-literal-name rules inspect, so digits inside a token's slug are not prose), and
`render_for_brief(declared_tokens) -> str` (each declared token with its description and negative clause,
written into the brief literally per briefkit's rule, `gk-forge/tools/seedsmith/seedsmith/briefkit/__init__.py:1-6`).

### 8. `decisions.md` row (drafted; appended in the build change — map §11 item 3)

> **Structured story text** (owner rulings R8–R11, 2026-09-19). Generated story text names entities only
> through closed ICU tokens (`{lead_*}`, `{c_<slug>}`, `{c_<slug>_epithet}`, `{role_<id>}`) and fills
> runtime values through closed slots (`{place}`, `{supply}`, `{reward}`, `{cost}`); agreement uses ICU
> `select` on closed registry tags (`article`, `gender`, `number`); a closed set of semantic tags (`em`,
> `whisper`, `shout`, `pause`) widens `item/seed-contract.md` §6's markup ban to meaning-only tags, never
> HTML or styling. Grammar: `gk-data/packs/fusion/data/seed/narrative/_registry/tokens.v1.json`.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_narrative_token_grammar.py -q
```

## Project structure

```text
gk-data/packs/fusion/data/seed/narrative/_registry/tokens.v1.json                   (new)
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/token_grammar.py  (new) load_grammar, parse, expand, tokens_used, literal_text, slug_for, render_for_brief
gk-forge/tools/seedsmith/tests/test_narrative_token_grammar.py          (new)
```

## Code style

`parse` is a small hand-written scanner over the closed grammar, not a general ICU parser: the input
language is ours and closed, and a scanner that refuses everything else is the check. Segments are frozen
dataclasses. No regex over whole messages for structure; regexes only for slug and role-id shapes.

## Testing strategy

| Test | Asserts |
|---|---|
| `every_token_family_form_slot_and_tag_has_description_and_negative` | the registry |
| `parse_accepts_every_form` | one fixture per family × form × pronoun, and every slot and tag |
| `parse_refuses_outside_the_grammar` | unknown family, bad slug, suffix on a role, suffix on a slot, stray brace, unknown tag, unbalanced tag, `select` in short form — each a named refusal |
| `expand_matches_the_table` | each row of §5 exactly, for a lead and a character |
| `expand_is_idempotent` | `expand(expand(x)) == expand(x)` |
| `expanded_arguments_are_closed` | the ICU argument names in any expansion are exactly `T`, `T_article`, `T_gender`, `T_number` |
| `apostrophes_survive_expansion` | "It's {lead_companion_poss} turn" round-trips to a message whose literal text keeps the apostrophe |
| `literal_text_excludes_tokens` | a character slug with a digit contributes nothing to `literal_text` |
| `slug_for_is_deterministic_and_refuses_collisions` | two ids mapping to one slug raise; a slug ending in a reserved suffix raises |
| `features_are_closed` | the three enums pinned — declarations; a new value is a reviewed change |
| `render_for_brief_inlines_descriptions` | declared tokens appear with both clauses; undeclared ones do not appear |

## Boundaries

- **Always:** short forms from the model, ICU from `expand`; refuse anything outside the grammar;
  descriptions with negative clauses.
- **Ask first:** a new family, slot, form, feature value or markup tag.
- **Never:** a real name anywhere in this module or its fixtures; model-written `select`; HTML or styling
  tags.

## Success criteria

- [ ] `tokens.v1.json` exists and every entry has both clauses.
- [ ] `parse` accepts the whole grammar and refuses every out-of-grammar fixture with a named reason.
- [ ] `expand` produces the table's ICU exactly, idempotently, with a closed argument set.
- [ ] `literal_text` is the only text the prose rules inspect.

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
| 1 | low | The slug regex needs a leading letter that the id grammar did not guarantee | fixed (contract §3 id body begins with a letter) |
| 2 | low | Map and runtime write `{c_<characterId>}`; the grammar writes `{c_<slug>}` | fixed (notation and inverse lookup stated) |
| 3 | low | Every family, form, slot and tag has a description and negative clause; `expand` is pure and closed; no population asserted | verified |

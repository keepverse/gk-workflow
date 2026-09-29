# Spec: `names-registry`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `names-registry` · **Map row:** 9 · **Wave:** 1 (after `token-grammar`)
**Depends on:** `token-grammar` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.
**Rulings this module implements:** R8 (our own names, as parameters), R10–R11 (the leads are **the
Garden Keeper**, **Hourbloom** and **the Rotwright**), recorded in `npc-story-events-ideal.md` §10.

---

## Objective

Publish the one file that maps story tokens to display strings in a locale, with closed grammatical
feature tags, and the one loader every consumer uses to read names. Its first rows are the three leads.
Renaming a lead is one row edit and a registry version bump; no seed changes, because no seed ever
contains a name.

This is the file other programs consume directly (map §4 "Why these boundaries"): `identity-rename` points
the shipped surfaces at it, `ip-censor` scans it before a release, the runtime's `narrative-text` renders
from it (`npc-story-events-map.md` row 11), and `narrative-validators` reads it to refuse any literal name
in generated text.

**Done means:** `names.en.v1.json` exists with the three lead rows; the loader validates it against the
token grammar and returns one name set that also includes character names from character seeds once they
exist; the rules below are tested.

---

## Design

### 1. The file — `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` (new)

```json
{
  "schemaVersion": 1,
  "registryVersion": 1,
  "locale": "en",
  "names": {
    "lead_summoner":   { "display": "Garden Keeper", "article": "definite", "gender": "male",   "number": "singular", "ruling": "R11" },
    "lead_companion":  { "display": "Hourbloom",     "article": "none",     "gender": "neuter", "number": "singular", "ruling": "R11" },
    "lead_antagonist": { "display": "Rotwright",     "article": "definite", "gender": "male",   "number": "singular", "ruling": "R11" }
  }
}
```

The tags follow the ideal's worked example (`narrative-seed-ideal.md` §6.5b): the Garden Keeper male,
Hourbloom neuter, the Rotwright male; "the Garden Keeper" and "the Rotwright" are titles, so their rows
carry `article: definite` and a bare `display`. `token-grammar`'s `expand` adds or capitalises the article
from the tag; the registry never stores an article-bearing string.

| Field | Meaning | Negative clause |
|---|---|---|
| key | a token from `token-grammar` — in this file, a lead token | not a display string, not an id |
| `display` | the name as the player reads it, without any article | not a translation key, never containing a brace, digit or markup |
| `article` | `definite · none` — whether the name reads with "the" | not a capitalisation flag; `_start` handles capitals |
| `gender` | `male · female · neuter · none` — what pronouns agree with | not a statement about the creature's biology; it is grammar only |
| `number` | `singular · plural · none` — verb and pronoun agreement | English v1 rows are `singular`; `plural` is reserved for group tokens |
| `ruling` | the owner ruling that fixed this row, or `none` | not a version |

**Authored, not generated.** The file lives under `_registry/`, is hand-written, and changes by review.
R10 had lead names generated; R11 superseded it for the three leads with the owner's own choice. A web
search found no conflicting character for "Hourbloom" or "Rotwright", which is **not trademark clearance**
(`npc-story-events-ideal.md` §10 R11); clearance before a commercial release is outside this program.

### 2. Character names — the second source, read not copied

Named characters' display strings are part of their character seeds (`narrative-contract`: `name` and
`epithet` as keyed text, and a `grammar` object with the same three tags). They are **generated** output,
so they are never copied into this authored file (map §2 principle 8). The loader unions both sources:

```python
@dataclass(frozen=True)
class NameRow:
    token: str                 # lead_summoner, c_<slug>, c_<slug>_epithet
    display: str
    article: Article
    gender: Gender
    number: Number
    source: Literal["registry", "character-seed"]

def load_names(locale: str = "en", *, corpus_root: Path | None = None) -> NameSet: ...
```

A character seed contributes `c_<slug>` (its `name`) and `c_<slug>_epithet` (its `epithet`, with the
character's gender and number and the epithet's own article tag). The slug comes from
`token-grammar`'s `slug_for`. Until `character-pipeline` has run there are no character seeds and the set
holds the three leads; a missing corpus directory is an empty source, not an error. Tombstoned characters
contribute nothing.

### 3. Rules the loader enforces (refusal names token and value)

1. Every key parses as a token of a family `token-grammar` allows in that source: lead tokens only in the
   file, character and epithet tokens only from character seeds.
2. Exactly the three lead tokens are present in every locale file (a declaration, pinned with its reason:
   the grammar's lead family is closed).
3. `display` is non-empty, has no digit, no brace, no `<` or `>`, and only Latin-script characters
   (`script-check`'s `latin` policy once that module lands; a strict letters-space-hyphen-apostrophe rule
   until then), and does not begin with an article word — the article is a tag.
4. `article`, `gender`, `number` are in the closed enums from `tokens.v1.json`; in English v1, `number`
   is `singular` on every row, because `expand`'s pronoun forms assume it.
5. **Uniqueness across the union:** no two rows share a display string after case-folding and collision
   normalisation (`docs/architecture/item/seed-contract.md` §5 — lowercase, strip punctuation, drop
   connectives, sort tokens). A character that normalises onto a lead is refused.
6. **Locale parity:** when a second locale file exists, its token set equals the English file's.

### 4. What consumers get

| Consumer | Uses |
|---|---|
| `narrative-validators` | `NameSet.displays()` for the no-literal-name rule, and a second, synthetic `NameSet` it builds itself for the round-trip render |
| `lore-packet` | each declared token's tags, never its display string |
| `review-render` | the live `NameSet` to render samples as a player reads them |
| `identity-rename` | the file path and the lead rows; it points shipped surfaces here and never edits them from this program |
| `ip-censor` | the file as a `player-name` surface in the release scan (`docs/architecture/ip-censor-ideal.md` "Narrative generation" rows 1 and 5) |
| runtime `narrative-text` | the file and the character seeds, the same union |

**A rename touches no seed.** No seed brief contains a display string (lore-packet sends tokens and tags
only), so changing `display` changes no brief hash and stales no seed. A test proves it (§Testing).
Changing a tag can change how existing text renders — that is the point of tags — and is a reviewed edit.

### 5. `decisions.md` row (drafted with `npc-story-events` NS5; appended in the build change)

> **Narrative names are tokens** (owner rulings R8–R11, 2026-09-19). Story text names entities by token,
> never by display string. `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` maps each lead token to a
> display string with closed `article`, `gender` and `number` tags — the Garden Keeper, Hourbloom, the
> Rotwright — and character seeds supply named characters the same way. Renaming a lead is one row edit.

This is the seed-side half of `npc-story-events-map.md` NS5; the two programs append one row, not two.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_narrative_names_registry.py -q
```

## Project structure

```text
gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json               (new) the three lead rows
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/names.py        (new) NameRow, NameSet, load_names
gk-forge/tools/seedsmith/tests/test_narrative_names_registry.py       (new)
```

## Code style

As the other narrative registry readers. `NameSet` is immutable; lookups by token raise a named
`KeyError` subclass rather than returning `None`.

## Testing strategy

Fixtures use invented names (for example `Examplar Vane`), never a real mark: `gk-forge/tools/seedsmith/**` is a
generator-prompt surface in the IP release scan (`docs/architecture/ip-censor/spec-avoid-list.md`).

| Test | Asserts |
|---|---|
| `lead_rows_are_exactly_the_three_leads` | declaration, reason: the grammar's lead family is closed (R11) |
| `lead_display_strings_follow_R11` | `Garden Keeper` with `definite`, `Hourbloom` with `none`, `Rotwright` with `definite` — pinned as the owner's ruling, not as generated text |
| `display_has_no_article_digit_brace_or_markup` | one refusal fixture each |
| `tags_are_closed` | unknown tag value refused |
| `english_rows_are_singular` | a `plural` row is refused in `en` v1 |
| `union_includes_character_seeds` | a fixture corpus with one character seed yields `c_<slug>` and `c_<slug>_epithet` rows |
| `normalised_collision_is_refused` | a character named `Rotwright` or `The Rot Wright` collides with the lead |
| `tombstoned_character_contributes_nothing` | fixture tombstone row |
| `missing_corpus_is_an_empty_source` | leads only |
| `second_locale_must_match_token_set` | a fixture `names.fr.v1.json` missing a lead is refused |
| `rename_changes_no_brief_hash` | with a fixture brief builder that uses tokens, changing a lead's `display` leaves every brief hash unchanged |

No test counts character rows.

## Boundaries

- **Always:** display strings without articles; tags from the grammar; union, never copy, character names.
- **Ask first:** changing a lead row (an owner ruling); adding a locale; a `plural` entity row.
- **Never:** a generated name in the authored file; an IP check here (IC-3 puts it at release); editing a
  shipped surface (identity-rename's).

## Success criteria

- [ ] The file holds exactly the three R11 rows and loads.
- [ ] The loader unions character seeds, enforces uniqueness across both sources and refuses every
      malformed fixture.
- [ ] Renaming a lead is one row edit and changes no seed and no brief hash.
- [ ] The file is listed in the IP release scan's scope by `ip-censor` (their change; this module only
      publishes the path).

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
| 1 | low | Cross-source uniqueness refuses the whole load when a generated character collides; generation-time `name_collision` must catch it first, which `character-pipeline` does | no change — the loader is a backstop |
| 2 | low | `lead_display_strings_follow_R11` pins authored text — allowed: an owner ruling (a declaration), not generated text | verified |

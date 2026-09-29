# narrative-seed NS26 — names registry (lead rows, character-seed union, R11 displays)

Spec: docs/architecture/narrative-seed/spec-names-registry.md · Row: tasks/narrative-seed-todo.md:623

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `lead_rows_are_exactly_the_three_leads` | `pytest test_narrative_names_registry.py -q -s` | pass — printed `committed registry rows=3 authored=3 locale=en registryVersion=1`; the grammar's `leads` is the same closed set | `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` |
| `lead_display_strings_follow_R11` | same | pass — Garden Keeper/definite/male, Hourbloom/none/neuter, Rotwright/definite/male | same |
| `display_has_no_article_digit_brace_or_markup` | same | pass — 7 refusal fixtures: `display_article`, `display_digit`, `display_brace`, `display_markup`, `display_script`, `display_missing`, `display_whitespace` | `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/names.py` |
| `tags_are_closed` | same | pass — 3 fixtures (`article: indefinite`, `gender: other`, `number: dual`) → `unknown_tag`, because the loader reads the grammar's own feature lists | same |
| `english_rows_are_singular` | same | pass — a `plural` row in `en` → `plural_in_english` | same |
| `union_includes_character_seeds` | same | pass — one fixture seed yields `c_marrow_fern` (none/female) and `c_marrow_fern_epithet` (definite), `source=character-seed` | same |
| `normalised_collision_is_refused` | same | pass — `Vane Examplar` and `Examplar Vane` both normalise to `examplar vane` → `normalised_collision` naming both tokens | same |
| `tombstoned_character_contributes_nothing` | same | pass — a tombstone seed leaves the three leads | same |
| `missing_corpus_is_an_empty_source` | same | pass — no `characters/` dir → leads only, no error | same |
| `second_locale_must_match_token_set` | same | pass — a fixture `names.fr.v1.json` missing a lead → `locale_parity` | same |
| `rename_changes_no_brief_hash` | same | pass — after renaming `lead_summoner`'s display the brief's `content_hash` is byte-identical, and no brief text carries a display string | `gk-forge/tools/seedsmith/seedsmith/briefkit/render.py` |
| `feature_enums_match_the_grammar` (drift check) | same | pass — `Article`/`Gender`/`Number` values equal `tokens.v1.json`'s closed lists | `token_grammar.py` |
| Path-owned verification | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <5 changed paths> -AllowUnscoped` | pass — all focused; doc-citation audit 0 findings; pytest (6 narrative files) green; `guard.doc-boundary` and `guard.verification-boundaries` green | `gk-core/scripts/verification-boundaries.v1.json` |
| Boundary registry: the names reader's test | `python gk-core/scripts/guard-verification-boundaries.py` | pass — `VERIFICATION BOUNDARY GUARD OK` after adding `test_narrative_names_registry.py` to `seed-narrative-registry` | same |

The authored `names.en.v1.json` was adopted unchanged from `identity-rename` T1 (`c6f51a159`), which landed it at
the path and in the shape this spec fixes; the loader reads it, never rewrites it.
`-AllowUnscoped` because `tasks/sessions/narrative-seed-2.json` does not exist (see NS25's fragment).

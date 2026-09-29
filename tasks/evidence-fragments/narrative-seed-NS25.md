# narrative-seed NS25 — story text token grammar (`parse`, `expand`)

Spec: docs/architecture/narrative-seed/spec-token-grammar.md · Row: tasks/narrative-seed-todo.md:613

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `tokens.v1.json` exists, every family/form/pronoun/slot/tag carries a description and a negative clause | `pytest test_narrative_token_grammar.py -q -s` | pass — printed `registryVersion=1 families=3 leads=3 forms=3 pronouns=3 slots=4 tags=4 rows-with-clauses=20` | `gk-data/packs/fusion/data/seed/narrative/_registry/tokens.v1.json` |
| `parse_accepts_every_form` — family × form × pronoun, every slot, every tag | same | pass — 37 passed total; the mixed sentence parses to `Literal Token Literal Markup Token Literal Token Literal Token Markup Markup` | `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/token_grammar.py` |
| `parse_refuses_outside_the_grammar`, each a named refusal | same | pass — 24 parametrized cases: `unknown_family`, `malformed_slug`, `malformed_role`, `reserved_suffix`, `suffix_on_role`, `suffix_on_slot`, `suffix_on_lead`, `epithet_takes_no_form`, `unbalanced_brace`, `stray_brace`, `empty_token`, `icu_in_short_form`, `unknown_tag`, `unbalanced_tag`, `nested_tag`, `stray_angle` | same |
| `expand_matches_the_table` — each row of §5, for a lead and a character | same | pass — e.g. `{lead_summoner}` → `{lead_summoner_article, select, definite {the {lead_summoner}} other {{lead_summoner}}}` (balanced); `_bare` → `{T}`; epithet and slot pass through | same |
| `expand_is_idempotent` | same | pass on a message carrying all six forms; the bare-only boundary is proven in the test and the module docstring (§5's `_bare` → `{T}` is textually the running short form) | same |
| `expanded_arguments_are_closed` | same | pass — an ICU-aware extractor reads only argument references, never a select branch body; every argument ∈ `{T, T_article, T_gender, T_number}` | same |
| `apostrophes_survive_expansion` | same | pass — `It's ` survives; a would-be ICU quoted span (`'#`) is doubled to `''#'` | same |
| `literal_text_excludes_tokens`; `tokens_used` | same | pass — `A {c_examplar_vane} speaks` → `A  speaks`; `{c_vane2}` contributes nothing; a digit in literal words is kept | same |
| `slug_for_is_deterministic_and_refuses_collisions` | same | pass — `character.examplar-vane` → `examplar_vane` twice; `vane-2` vs `vane.2` → `slug_collision`; all 9 reserved suffixes refused; `2vane` → `malformed_slug` | same |
| `features_are_closed` | same | pass — registry enums equal `GENDER/NUMBER/ARTICLE`; a widened `gender` fixture is refused | same |
| `render_for_brief_inlines_descriptions`; fixtures contain no real name | same | pass — declared tokens carry both clauses, `{reward}` does not appear; no fixture carries a `names.en.v1.json` display string | same |
| Path-owned verification | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <5 changed paths> -AllowUnscoped` | pass — all 5 paths focused (no unmapped path); doc-citation audit 0 findings; pytest 108 passed; `guard.doc-boundary` 4 passed; `guard.verification-boundaries` 57 passed | `gk-core/scripts/verification-boundaries.v1.json` |
| Boundary registry: the registry's own test file | `python gk-core/scripts/guard-verification-boundaries.py` | pass — `VERIFICATION BOUNDARY GUARD OK` after adding `test_narrative_token_grammar.py` to `seed-narrative-registry` | `gk-core/scripts/verification-boundaries.v1.json` |

`-AllowUnscoped` is used because `tasks/sessions/narrative-seed-2.json` does not exist and `tasks/sessions/**`
is outside this lane's allowed paths, so `-Session narrative-seed-2` fails with "session record not found".

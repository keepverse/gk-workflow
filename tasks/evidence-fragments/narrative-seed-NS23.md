# narrative-seed NS23 — counter-doctrine row (the row's last open half)

Spec: docs/architecture/narrative-seed/spec-character-vocab.md §8 · Row: tasks/narrative-seed-todo.md:577

The registries, the reader and the eleven tests landed in `472c44ae6`; the row stayed open only because its
*Files* line names `docs/architecture/decisions.md`, which was outside the predecessor lane's allowed paths.
This lane holds that path, so the drafted row (map §11 item 6) is the whole of the remaining work.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The R13 counter-doctrine row is in `decisions.md`, cross-referenced to `npc-story-events-ideal.md` §6.12 and naming the registry that enforces it | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths docs/architecture/decisions.md -AllowUnscoped` | pass — doc-citation audit 0 findings; the row is the table's last | `docs/architecture/decisions.md` |
| `antagonist_pairs_have_no_personal_history`, `joins_is_never_an_antagonist_pair` and the rest of the row's acceptance lines still green | `pytest gk-forge/tools/seedsmith/tests/test_narrative_character_vocab.py -q -s` | pass — `13 passed`, with the printed IC-3 note (`ip-censor`'s `load_avoid_terms` helper is absent in this tree — the mark check is skipped) | `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/character_vocab.py` |
| `all_defects()` over the committed registries | same | pass — 0 defects (the predecessor's reading, unchanged by a doc-only change) | `gk-data/packs/fusion/data/seed/narrative/_registry/line-pairs.v1.json` |

No code changed, so the registries' own readings are the ones already recorded in `472c44ae6`'s ledger line.
`-AllowUnscoped` because `tasks/sessions/narrative-seed-2.json` does not exist (see NS25's fragment).

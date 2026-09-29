# narrative-seed NS15 — the `narrative gloss fill|commit` and `narrative preflight` host

Spec: docs/architecture/narrative-seed/spec-gloss-fill.md §4–§5 · Row: tasks/narrative-seed-todo.md:409

The three drivers landed in `82b622ffd` and stayed open on one thing: nothing in the pipeline could reach
them (`report/cli.py` had no `narrative` subcommand tree). This commit is that host, and it is what NS16/NS17
now run through.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `gloss fill` exists (`--dry-run` default, `--write`, `--limit`, `--regenerate`) and reaches `fill_glosses` | `pytest gk-forge/tools/seedsmith/tests/test_narrative_gloss_commit.py -q` | pass — `13 passed` (6 new `NarrativeCliTests`, all through `main([...])`), whole file in 0.29s | `gk-forge/tools/seedsmith/seedsmith/report/cli.py` |
| `--dry-run` counts chunks and calls and spends nothing | same | pass — `dryRun: true`, `calls: 0`, `chunks: 2` with `--limit 2`, and no run file written; `call_model` patched to raise | same |
| `--write` draws with the RESOLVED config and writes only a scratch run | same | pass — 1 call, run file carries `model: test-resolved-model` / `promptVersion: gloss/1`, the whole one chunk unresolved, and the registry bytes unchanged | `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/fill.py` |
| `narrative preflight` makes exactly ONE call | same | pass — `{motif, gloss, sense, calls: 1}`, one stub call | `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/preflight.py` |
| `preflight` fails loudly on a dead endpoint | same | pass — exit 3, `refused:`, the exception class named | same |
| `gloss commit` writes accepted rows; an unreplaced rejection refuses | same | pass — `--reject <motif>=too literal` → exit 3 `no accepted replacement`, registry bytes unchanged; the run's verdict history then carries the accept and the second commit writes both rows with `model`/`promptVersion` stamped | `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/commit.py` |
| A missing run id is a refusal, not an empty run | same | pass — exit 3, `no run file` | `fill.py` |
| `promptVersion` is a declaration, with the prompt text it versions | (read) `gloss/prompt.py` | pass — `GLOSS_PROMPT_VERSION = "gloss/1"` added beside the brief it versions | `prompt.py` |
| The row's own Verify (`SS test_narrative_gloss_fill.py`) and the narrative boundary | `pytest test_narrative_gloss_fill.py test_narrative_gloss_commit.py test_narrative_token_grammar.py test_narrative_names_registry.py test_narrative_storylet_vocab.py test_narrative_character_vocab.py test_briefkit_gloss.py -q` | pass — `136 passed` | same |
| The one shared consumer of the edited CLI | `pytest gk-forge/tools/seedsmith/tests/test_cli.py -q` | pass — `23 passed, 1 failed`, the failure being the pre-existing `atom.fx-overlay-damage` GAP this lane already recorded | `gk-forge/tools/seedsmith/seedsmith/report/cli.py` |
| ruff on the touched files | `ruff check fill.py prompt.py test_narrative_gloss_commit.py` | pass — clean (cli.py keeps its 6 pre-existing findings, proved identical at HEAD during NS13) | same |
| Boundary guard | `python gk-core/scripts/guard-verification-boundaries.py` | pass — `VERIFICATION BOUNDARY GUARD OK` | — |

**`verify-change.ps1` for this change set is `not_run`.** `report/cli.py` maps to `seedsmith-fallback` (module
level = the whole 4585-test suite, ~14 minutes) and that stage was killed by an infrastructure error **twice**,
at 71% and at 97%, with no summary line either time. The focused boundaries it would have run are the two rows
above (136 and 23+1 passed), and the whole-suite stage's 16 failures are the pre-existing set established in
`a5c849802` on the same tree and proved independent of the CLI edit by reverting `cli.py` to HEAD
(`11 failed, 1 passed`). Re-running a third time would be the broad retry the verification boundary exists to
prevent, so the gap is named here instead of glossed.

**Defect I introduced and fixed in this change (recorded because it is a trap for the next test author).**
`gloss/fill.py` imports `call_model` at MODULE level, so patching `seedsmith.pipeline.llm_caller.call_model`
does not reach it — the first version of `NarrativeCliTests` therefore made one REAL call to the local endpoint
during `--write`. The fix patches both bindings (`gloss/fill.call_model` and the transport's, the latter for
`preflight.py`'s in-call import); the suite now runs in 0.29s with zero calls.

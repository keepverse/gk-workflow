# narrative-seed NS13 — the `dungeon events regen` production host

Spec: docs/architecture/narrative-seed/spec-dungeon-generator-repair.md §8 · Row: tasks/narrative-seed-todo.md:338

The plan/draw/review/commit driver landed in `8f12bd519`+`297541913` and stayed open on one thing: nothing in
the pipeline could reach it (`report/cli.py` had no `dungeon` subcommand tree). This commit is that host.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The verb exists with `--dry-run` (default) / `--write` / `--review` / `--commit` / `--ids`, and reaches the driver | `pytest gk-forge/tools/seedsmith/tests/test_dungeon_commit.py -q` | pass — `24 passed`; 3 new `DungeonRegenCliTests` all enter through `main([...])` | `gk-forge/tools/seedsmith/seedsmith/report/cli.py` |
| `--dry-run` spends nothing and prints both bounds | same | pass — `4 base call(s)`, `16 worst call(s)`; `call_model` patched to raise | same |
| `--write` draws with the RESOLVED config and writes only a scratch run | same | pass — `drew 3 event(s), 1 unresolved`; every committed event's bytes unchanged | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/regen.py` |
| `--review` prints the seeded sample; `--accept`/`--reject` record verdicts | same | pass — strata `["bargain", "story"]`; `accepted == ["event.bargain-creature.a-001"]` | same |
| `--commit` writes ONLY accepted events | same | pass — `committed == ["_index.json", "event.bargain-creature.a-001.json"]`, `_provenance.modelId == test-resolved-model`; rejected and unresolved events byte-identical | same |
| A commit with no accepted event refuses instead of rewriting the index | same | pass — exit 3, `no accepted event`, corpus bytes unchanged | same |
| `load_run`/`latest_run_id` make review and commit read the run a `--write` wrote | same | pass — a missing run id refuses with exit 3 and `no run file` | `regen.py` |
| `SS test_dungeon_commit.py` + `SS test_dungeon_idempotency.py` (the row's Verify) | `pytest <both> -q` | pass — `41 passed` | same |
| The `seedsmith-dungeon` boundary now selects the driver's own test | `pytest <the boundary's 20 files> -q` | pass — `348 passed`; `guard-verification-boundaries.py` → `VERIFICATION BOUNDARY GUARD OK` | `gk-core/scripts/verification-boundaries.v1.json` |
| Path-owned verification | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <3 changed paths> -AllowUnscoped` | **exit 1** — `regen.py`→`seedsmith-dungeon` (focused) and the test→`seedsmith-tests`, but `report/cli.py` maps to `seedsmith-fallback` (module) = the whole suite: `16 failed, 4585 passed`. Diagnosis below | same |
| ruff on the touched files | `ruff check regen.py cli.py test_dungeon_commit.py` | pass for `regen.py`/the test; `cli.py` reports the same 6 findings at HEAD (`git show HEAD:… \| ruff --stdin-filename`) — none in the new code | same |

**The 16 failures are pre-existing and independent of this change, proven not asserted.** 5 are on the script's
own KNOWN RED list (`SR-25`, `test_actions_description_completeness`). For the other 11 the controlled experiment
is: `git show HEAD:…/report/cli.py > …/report/cli.py` (my change absent, nothing else touched) then re-run exactly
those 11 → `11 failed, 1 passed`, the same set. Their causes, read: `data/seed/actions/_candidates/general/round-1.json`
is absent (5 `test_general_propose`), `gk-data/packs/fusion/data/seed/actions/**` still names the unknown atom family `atom.fx-overlay-damage`
(`test_cli`, `test_corpus_loader`, `test_actions_description_completeness`), a pinned dump hash moved (`test_preflight`),
a corpus metric asserts `0 > 0` (`test_usage_stats`), and `test_workflow_runtime` fails on
`ModuleNotFoundError: No module named 'langgraph.checkpoint.sqlite'` — the optional `workflow` extra is not installed
in this interpreter. None touches `regen.py`, the new `dungeon` tree or the dungeon boundary (348 passed).
**Out-of-fence finding:** the owning programs' todos are outside this lane's allowed paths, so the manager must route
the 11 "UNEXPECTED FAILURE" labels; recorded as a ledger `finding` with the causes above.

`--accept`/`--reject` are part of the verb though the row's flag list does not name them: `--commit` reads only
verdicts, so without a way to record one the commit stage could never write anything and the driver would still
have no production caller. `-AllowUnscoped` because `tasks/sessions/narrative-seed-2.json` does not exist.

# Lane brief — `ipc-3c` (fix the avoid-list registry wiring test failure)

## Why this lane exists

`ipc-3b` landed the T16 generator change (avoid_list helper + fixture tests,
tree-brief avoid line, `--node` selector) but its own new pytest fails 1/63.
This lane inherits its tree (`--base opencode/ipc-3b`) and fixes exactly
that. No new scope.

⛔ Read `docs/DESIGN-GATE.md` §1 first. No-shell protocol is binding (your
bash refuses): file work only, quote orchestrator-run commands tagged
`UNPROVED-BY-LANE`, never claim a run.

## The defect (manager-measured, exact)

`tests/adapters/trees/test_nodegen_cli.py::TreesGenerateDryRunTests::test_the_cli_still_reports_a_genuine_nameKeyRefused_cleanly_if_one_ever_reaches_it`
fails: it expects `nameKeyRefused` in the CLI output but gets a clean run
(40/40 resolved). stderr shows the cause:
`seedsmith: --write needs the ip-censor avoid-list — <tmp>/ip-censor/_registry/marks.v1.json: cannot be read (No such file or directory)`.
The avoid-list registry path the CLI reads is not wired/seeded in the test
(or helper) environment. Fix in-fence: wire the registry path or plant the
registry in-test — whichever the code's own convention says (read first).

## Goal

Make the full new-test set green without weakening the test (no deleting the
planted-violation assertion, no `knownRed`, no blunting). Re-report.

## Allowed paths

- `gk-forge/tools/seedsmith/seedsmith/briefkit/avoid_list.py`
- `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/**`
- `gk-forge/tools/seedsmith/seedsmith/report/cli.py`
- `tools/seedsmith/tests/adapters/trees/test_nodegen_*.py`
- `gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py`
- `gk-forge/tools/seedsmith/tests/fixtures/avoid_list/**`
- `tasks/ip-censor-todo.md`
- `tasks/evidence-fragments/ip-censor-T16.md`

## Off limits

`gk-data/packs/fusion/data/seed/passive-tree/nodes/**` (regen runs orchestrator-side),
`gk-core/scripts/enforcement-registry.v1.json`, everything else. The T16 tree-brief
and selector code are landed — do not touch them. Commit nothing, push
nothing, create no branches — leave the tree dirty.

## Definition of done

1. The named failing test passes for the reason it was written (planted
   violation reported cleanly), not by weakening.
2. Nothing outside Allowed paths changed vs `opencode/ipc-3b`.

## Verification (orchestrator-run; quote verbatim, tag UNPROVED-BY-LANE)

- `python -m pytest tests/adapters/trees/test_nodegen_brief.py tests/adapters/trees/test_nodegen_cli.py tests/adapters/trees/test_nodegen_run.py tests/test_briefkit_avoid_list.py -q` from `gk-forge/tools/seedsmith` — 63/63.

## Report

`<<<REPORT {...} REPORT>>>`, every claim already a change in this worktree.

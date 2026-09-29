# Lane `tvb60` — test-verification-boundary: the open rows after `tvb58` drained

**Session:** `test-verification-boundary-3` · **Program:** `test-verification-boundary` · **Mode:** worktree
**Fence:** `tests/**`, `scripts/**`, `tools/**`, `gk-core/src/FusionRpg.Core/**` (the split's own writes only), `docs/architecture/test-verification-boundary*`, `docs/contributing/**`, `tasks/test-verification-boundary-*`, `gk-data/packs/fusion/data/seed/atoms/generated/**`
**Protected, granted to this lane:** `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `gk-core/scripts/verification-boundaries.v1.json`, `scripts/test-fast.ps1`, `scripts/run-guards.ps1`

## Why this lane exists

Its predecessor `tvb58` finished its own TVB5.8 manifest and then drained: its session reached
**4.99 MB / 1360 lines** and the runner fell into a `report_missing` loop of 1-turn segments
(measured: 0 tool calls in 10 minutes). It was retired and its last uncommitted docs were salvaged
by the manager (`4d68751e1`). The program's rows are still open: **43 open task blocks** at the
2026-09-23 reading of `.claude/cmdc-agents/scripts/convergence-census.py` — that script is the t1
contract's instrument; run it to see the rows yourself rather than trusting this number.

## First action

`git merge --no-ff features/mega-merge`, then read `tasks/test-verification-boundary-todo.md` and
work its open rows **in the todo's own order**:

- **Wave 5** — TVB5.7 (shared set + manifest project 1, with its wiring), then TVB5.8.k — *one
  increment per remaining manifest project, in manifest order* — then TVB5.9 (split close: the full
  default profile once, the `Csc` reading, the doc sentence).
- **Wave 6** — TVB6.2 (K1: per-area Core production owners from the production map), TVB6.3 (K2:
  re-key the existing focused `core.*` boundaries).
- Then the findings sections in the same order (the TVB5.7-session block, the `ep-autoassign`
  defect block, the TVB5.8.3 block).

The `split --apply` gate is the point of the tool: file moves plus journal, then `dotnet build` and
`dotnet test` for BOTH the new project and the residual `FusionRpg.Core.Tests`, reverting on
failure. **Do not shrink it, do not bypass it, do not add a flag to skip it.** It is slow because it
proves a move did not lose a test. While it runs, do work that needs no CPU: draft the `ci.yml`,
`release.yml`, `test-fast.ps1` and registry edits the same commit needs, and write the fixed parts
of the evidence fragment.

## Rules

- One logical change per commit: code + evidence + the ledger line
  (`tasks/test-verification-boundary-ledger.jsonl`), **in the same commit**.
- Tick the row in the same commit and assert the row id is still present after the tick.
- A row you end still open must name **exactly** what blocks it — never "needs investigation".
- Findings outside your fence get a row in the OWNING program's todo in the same commit, with
  `file:line` and the cause you read — never a lone note in your report.
- Never hand-edit generated JSON: regenerate (`dotnet run --project gk-forge/tools/FamilyExpandGen`) and
  commit the regenerated diff with the reason.
- Foreground commands only; never end a turn waiting on your own background job.
- **Every segment ends with the report block.** Without it the runner restarts the segment labelled
  `report_missing` and burns context for nothing.
- The provider sometimes returns `429 GoUsageLimitError`: if you get one, end the segment with your
  report instead of retrying.

## Verification

- `python gk-core/scripts/guard-verification-boundaries.py`
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~CoreTestProjectPolicy"`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`

Run them in the FOREGROUND. On `user-mapped section open`, run `dotnet build-server shutdown` and retry.

## Evidence contract

The **printed reading**, never an exit code: a test line with its counts, a guard's printed verdict,
a measured number with the command that produced it. Write the fragment under
`tasks/evidence-fragments/`.

## Boundaries

Do not widen the fence. Do not touch another session's files. Never commit conflict markers.
`gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `gk-core/data/tuning/**` and `gk-core/tests/fixtures/**` are enforced roots: a
new file under one needs its boundary row in `gk-core/scripts/verification-boundaries.v1.json` in the same
commit, or the integration guard goes red while your local `verify-change` stays green (TVB-F24).

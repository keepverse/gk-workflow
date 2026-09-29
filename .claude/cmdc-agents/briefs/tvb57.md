# Task: test-verification-boundary TVB5.7, then the TVB5.8.k increments

Program: `tasks/test-verification-boundary-plan.md` / `tasks/test-verification-boundary-todo.md`.
Your rows start at line 322. Read them and their spec sections before writing anything.

TVB5.1 through TVB5.6 are merged into `features/mega-merge`, including the `SplitPlanner` fix for
generated csproj/props not being valid MSBuild. Start from HEAD.

## TVB5.7 — first real increment of the Core.Tests split

> **TVB5.7 — First increment: shared set + manifest project 1, with its wiring** · deps: TVB5.4, TVB5.6

The `split --apply` verb built in TVB5.4 runs its own safety gate: file moves plus journal, then
`dotnet build` and `dotnet test` for BOTH the new project and the residual `FusionRpg.Core.Tests`,
reverting automatically on any failure. **That gate is the point of the tool. Do not shrink it, do
not bypass it, do not add a flag to skip it.** It is slow because it is proving a move did not lose
a test.

The gate takes a long time. While it runs, do the work that needs no CPU:
- draft the `ci.yml`, `release.yml`, `test-fast.ps1` and registry edits the same commit needs;
- read TVB5.8's spec rows;
- write the fixed parts of the evidence fragment.

Then process the gate result: confirm `git diff -M --stat` shows **pure renames**, apply the wiring
edits by hand, write evidence, and commit — all in one commit.

## TVB5.8.k — one increment per remaining manifest project, in manifest order

Same shape as TVB5.7, one commit each. Do not batch several projects into one commit: the whole
value of the increment is that a single project's move is separately revertable.

## Known open item in your program, if you reach it

Six `VerificationBoundaryWorkflowTests` fail with `verification-boundary script timed out` in
`ExternalProcess.Run` — not assertions. Measured: `verify-change.ps1 -PlanOnly` took **415 seconds
for two paths** with 22 `dotnet.exe` hosts running, and returned a correct plan. A scoped planner
that takes minutes defeats scoping, so **the fix is the latency** — likely per-path repo scanning or
a repeated git call that should be hoisted — **not** raising the timeout. If you do raise a timeout,
say in a comment why that number, and never turn it into an asserted reading.

Also unmapped and owned by your program: `gk-core/scripts/verification-boundaries.v1.json` has no
`gk-web/web/fusion-rpg-web` entries, and `gk-forge/tools/seedsmith/tests/**` is unmapped. An unmapped production
path is a verification-boundary defect — repair the mapping.

## Rules

- One logical change per commit: code + evidence + ledger line.
- `gk-core/scripts/verification-boundaries.v1.json` is edited additively by several lanes. If it conflicts,
  resolve by structural union by id and run `gk-core/scripts/guard-verification-boundaries.py` BEFORE
  committing. Never commit a file with conflict markers — check `git show ":<file>"` first.

## Verification

- `python gk-core/scripts/guard-verification-boundaries.py`
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~CoreTestProjectPolicy"`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`

Run them in the FOREGROUND. Never end a turn waiting on your own background job.
On `user-mapped section open`, run `dotnet build-server shutdown` and retry.

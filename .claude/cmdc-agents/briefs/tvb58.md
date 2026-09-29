# Task: test-verification-boundary TVB5.7 (redo with a wider fence), then TVB5.8.k and TVB5.9

Program: `tasks/test-verification-boundary-plan.md` / `tasks/test-verification-boundary-todo.md`.
Your rows start at line 322 and run to the program's closing checkpoint. Read the rows AND their spec
sections before writing anything.

**First action:** merge the integration branch into your own branch — `git merge --no-ff features/mega-merge` (HEAD `3f4d6411`). It moved six commits (docs, scripts, `.claude/cmdc-agents/rules.md`) since your predecessor started. Resolve conflicts in favour of the integration branch unless the conflict is inside your own work.

**You inherit the `cmdc/tvb57` branch** (your base). It already carries four commits you should read
first, because they are your own predecessor's work and its blockers:
- `1fa3cef0` — repaired 3 of the 4 pre-existing `FusionRpg.Core.Tests` reds (stale pins left by
  `39fbed34` / `12175b3d` / `e79c0fde8`) plus the `RealStatusAnchor` mirror in `FamilyExpansionTests`.
- `c9e1c902` — every manifest entry gets `coreInternals=true` (proved by the split gate's own build).
- `9ef1e91e`, `7e9f6398` — findings routed, session record written.

## What changed since that lane stopped (orchestrator rulings)

1. **`.github/workflows/ci.yml` and `.github/workflows/release.yml` are yours now.** The pipeline guard
   that refused them is lifted for this lane by an explicit `--allow-protected` grant. Wire the new
   project's `dotnet test` + exit-check pair into **both**, in the same commit as the move.
2. **The split's own writes are inside your fence now:** `gk-core/src/FusionRpg.Core/InternalsVisibleTo.CoreTests.cs`
   and `FusionRpg.slnx` may be written by `split --apply`.
3. **The last residual red is yours:** `gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json` drifts
   because `e1d9103e` changed the source tag and the tree was not regenerated. Run
   `dotnet run --project gk-forge/tools/FamilyExpandGen` and commit the regenerated file **with** the reason.
   Never hand-edit the emitted JSON — regenerate it.
4. `gk-core/scripts/verification-boundaries.v1.json` and `scripts/test-fast.ps1` are claimed by two other ACTIVE
   sessions (`tvb-wave5`, `keepverse-split`). Edit them only additively if TVB5.7 needs it; run
   `gk-core/scripts/guard-verification-boundaries.py` before you commit, and never commit conflict markers.
   If a conflict with another session's claim cannot be resolved additively, take the minimum needed for
   TVB5.7 and record the rest as a routed finding instead of forcing it.

## TVB5.7 — first real increment of the Core.Tests split

> **TVB5.7 — First increment: shared set + manifest project 1, with its wiring** · deps: TVB5.4, TVB5.6

The `split --apply` verb built in TVB5.4 runs its own safety gate: file moves plus journal, then
`dotnet build` and `dotnet test` for BOTH the new project and the residual `FusionRpg.Core.Tests`,
reverting automatically on any failure. **That gate is the point of the tool. Do not shrink it, do not
bypass it, do not add a flag to skip it.** It is slow because it is proving a move did not lose a test.

The gate takes a long time. While it runs, do the work that needs no CPU: draft the `ci.yml`,
`release.yml`, `test-fast.ps1` and registry edits the same commit needs; read TVB5.8's spec rows; write
the fixed parts of the evidence fragment.

Then process the gate result: confirm `git diff -M --stat` shows **pure renames**, apply the wiring edits,
write evidence, and commit — all in one commit.

## TVB5.8.k — one increment per remaining manifest project, in manifest order

Same shape as TVB5.7, one commit each. **Do not batch several projects into one commit**: the whole value
of the increment is that a single project's move is separately revertable.

## TVB5.9 — split close

Full default profile once, the `Csc` reading recorded, and the doc sentence. A docs-only commit is
legitimate here because the deliverable IS the closing record.

## Known open item in your program, if you reach it

Six `VerificationBoundaryWorkflowTests` fail with `verification-boundary script timed out` in
`ExternalProcess.Run` — not assertions. Measured: `verify-change.ps1 -PlanOnly` took **415 seconds for
two paths** with 22 `dotnet.exe` hosts running, and returned a correct plan. A scoped planner that takes
minutes defeats scoping, so **the fix is the latency** — likely per-path repo scanning or a repeated git
call that should be hoisted — **not** raising the timeout. If you do raise a timeout, say in a comment why
that number, and never turn it into an asserted reading.

Also unmapped and owned by your program: `gk-core/scripts/verification-boundaries.v1.json` has no
`gk-web/web/fusion-rpg-web` entries, and `gk-forge/tools/seedsmith/tests/**` is unmapped. An unmapped production path is a
verification-boundary defect — repair the mapping.

## Rules

- One logical change per commit: code + evidence + ledger line.
- Findings outside your fence get a row in the OWNING program's todo in the same commit, with `file:line`
  and the cause you read — never a lone note in your report.
- Foreground commands only; never end a turn waiting on your own background job.

## Verification

- `python gk-core/scripts/guard-verification-boundaries.py`
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~CoreTestProjectPolicy"`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`

Run them in the FOREGROUND. On `user-mapped section open`, run `dotnet build-server shutdown` and retry.

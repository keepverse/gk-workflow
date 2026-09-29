# Lane `bp-1` — build-preset: the callable gates and the appliers

**Session:** `build-preset-bp1` · **Program:** `build-preset` · **Mode:** worktree
**Todo:** `tasks/build-preset-todo.md` · **Plan:** `tasks/build-preset-plan.md` · **Map/specs:** this program's own `docs/architecture/**` pages (the todo's rows cite them — read the cited section before writing anything)
**Fence:** `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Contracts/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`, `tests/**`, `scripts/**`, `gk-core/data/tuning/**`, `docs/architecture/**`, `tasks/build-preset-*`
**Protected, granted to this lane:** `gk-core/scripts/verification-boundaries.v1.json`, `scripts/run-guards.ps1`

## Why this lane exists

At the 2026-09-23 reading of `.claude/cmdc-agents/scripts/convergence-census.py` (the t1 contract's own
instrument — run it yourself rather than trusting this number) `build-preset` carries **13 open task blocks**
and only 1 residue row, which makes it the largest clean, untended program in the convergence set. Its rows are
implementation, not measurement: an aptitude **build preset** is a named set of pieces a player assembles, and
this program is what lets one be activated, previewed and applied through one audited path.

## Work — the todo's own order

- **Wave A — the callable gates.** `BP1.4` `AptitudePresetActivation.Activate`: lift the activate route (budget,
  materialize, check, store) out of wherever it currently lives into the one callable path. `BP1.5`
  `AptitudePresetActivation.Preview`: the **read half** — no write, and the same quote per scope as the write.
  A preview that can write is the defect this pair exists to prevent; prove it cannot.
- **Wave B — appliers and the orchestrator.** `BP2.3` `IBuildPresetPieceApplier` and its records, with
  `PatronApplier` and `SkillsApplier` registered. `BP2.4` `FieldApplier`: an **exact-set diff**, capacity
  measured *after* the diff, wardens outside the diff, and the old path retired — not left beside the new one.

Read each row's spec section first. Take the rows in `deps:` order and do not skip ahead of an unmet dep.

## Rules

- One logical change per commit: code + its test + the evidence fragment **in the same commit**.
- **One audited path per operation.** If a route, a service and a store method can each do the same job, two of
  them are the defect — retire the others in the same commit that lands the new one.
- Tick the row in the same commit and assert the row id is still present after the tick.
- A row you end still open must name **exactly** what blocks it — never "needs investigation".
- Findings outside your fence get a row in the OWNING program's todo in the same commit, with `file:line` and
  the cause you read.
- `gk-core/data/tuning/**` is authored but never edited in place: publish `v{n+1}` through `gk-core/tools/tuning/publish.py`.
  `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**` and `gk-core/tests/fixtures/**` are enforced roots: a new file under one needs its
  boundary row in `gk-core/scripts/verification-boundaries.v1.json` in the same commit (TVB-F24).
- Foreground commands only; never end a turn waiting on your own background job.
- **Every segment ends with the report block** — without it the runner restarts you labelled `report_missing`
  and burns its context for nothing. On a `429 GoUsageLimitError`, end the segment with your report instead of
  retrying in a loop.

## Verification

- `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <the files you changed> -Session build-preset-bp1`
- `python gk-core/scripts/guard-verification-boundaries.py`
- `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` if the change touches the Hub compose path
- `dotnet test` on the project that owns the changed code — the focused project, never the whole suite

On `user-mapped section open`, run `dotnet build-server shutdown` and retry.

## Evidence contract

The **printed reading**, never an exit code: a test line with its counts, a guard's printed verdict, the
preview's own output proving it wrote nothing (compare the store before/after). Fragments go under
`tasks/evidence-fragments/`.

## Boundaries

Do not widen the fence. Do not touch another session's files. Never commit conflict markers. SQL lives only in
`FusionRpg.Data`; combat writes go through `EntityStatWriter`/Funnel; a level-derived number goes through the
power ladder. Merge `features/mega-merge` freely — the integration head moves several times an hour.

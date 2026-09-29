# Lane `ipc-3` — ip-censor: the gate wiring, the avoid-list, and IC-4.1/IC-4.2

**Session:** `ip-censor-3` · **Program:** `ip-censor` · **Mode:** worktree
**Todo:** `tasks/ip-censor-todo.md` · **Plan:** `tasks/ip-censor-plan.md` · **Map:** `docs/architecture/ip-censor-map.md`
**Specs:** `docs/architecture/ip-censor/**` (`spec-wiring`, `spec-avoid-list`, `spec-report`, `spec-registry`, `spec-scan`, `spec-source`, `spec-suggest`, `spec-census`, `spec-curate`)
**Fence:** `gk-core/tools/ip-censor/**`, `gk-forge/tools/seedsmith/**`, `scripts/**`, `.github/workflows/release.yml`, `docs/architecture/ip-censor*/**`, `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `tests/**`, `tasks/ip-censor-*`
**Protected, granted to this lane:** `.github/workflows/release.yml`, `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/scripts/enforcement-registry.v1.json`, `scripts/run-guards.ps1`

## Why this lane exists

At the 2026-09-23 reading of `.claude/cmdc-agents/scripts/convergence-census.py` (the t1 contract's own
instrument — run it yourself rather than trusting this number) `ip-censor` carries **11 open task blocks**.
Its two named dependencies are already met — **T4** (shipped registry files, surface classifier, remediation
derivation) and **T10** (`report` composition root, CLI, plan and report writers) are both ticked — so the
rows below are unblocked work, not a queue behind something else.

Two kinds of rows live in this todo, and only the first is work:

- **checkpoint** rows (`Checkpoint 1..6`, `Final checkpoint`) — these are *gates*, not tasks. Your census's
  own definition excludes them; do not work them as if they were units, and when a checkpoint's conditions
  are genuinely met, tick it **with the reading that says so**.
- **task** rows (`T12` onward) — the work.

## Work — the todo's own order

- **T12 — release gate step, checklist line, exit-check guard, enforcement row** (deps: T10). The gate must
  fail *loudly on the real tree* and be wired into `release.yml` before `Publish player pack`, with the
  checklist line and the enforcement-registry row in the same commit. Prove it by running the step's own
  command on the current tree (it should exit non-zero and say what it found) — a gate that cannot fail is
  not a gate.
- **T14 — `seedsmith.briefkit.avoid_list`** (deps: T4), then **T15** (the uniques brief adopts the avoid line
  and drops its franchise citation), then **T16** (the tree brief adopts the avoid line, gains the `--node`
  selector, and the Overwatch node is regenerated for IC-4.1). T15/T16 depend on T14 — take them in that
  order. Regenerations commit the regenerated diff **with** the reason; never hand-edit emitted JSON.
- **T18 / T19 / T19b — IC-4.2 `Jackson*`** (deps: T17, T3): the authored rename map plus its validation and
  seedsmith reader (T18), applying it in the creature adapters and regenerating the derived trees (T19), and
  re-keying the species ids (T19b — gate G1 was answered **yes** on 2026-09-19; record that answer in the
  ledger with the row).
- **T21 / T22 / T23 — registry content and release readiness.** T21 needs the downloaded USPTO export and
  T22 an identity-rename hand-off note: if either input is genuinely absent, **end the segment naming exactly
  what is missing** rather than working around it. T23 is the closing reading (release-gate output, residue
  list, full suite) and its evidence is the printed readings.
- The routed finding row (**TVB-F22**) is a pointer to `test-verification-boundary`'s own row — do not
  duplicate it; if you close the underlying gap, say so there instead.

## Rules

- One logical change per commit: code + its test + the evidence fragment + the ledger line
  (`tasks/ip-censor-ledger.jsonl`) **in the same commit**.
- Tick the row in the same commit and assert the row id is still present after the tick.
- A row you end still open must name **exactly** what blocks it — never "needs investigation".
- Findings outside your fence get a row in the OWNING program's todo in the same commit, with `file:line` and
  the cause you read.
- `gk-data/packs/fusion/data/seed/**` and `gk-data/packs/fusion/data/generated/**` are enforced roots: a new file under one needs its boundary row in
  `gk-core/scripts/verification-boundaries.v1.json` **in the same commit** (TVB-F24 — a local `verify-change` stays
  green while the integration guard goes red without it). T12's registry rows and T19's regenerations are
  exactly that case.
- Never hand-edit generated JSON; regenerate and commit the diff with the reason.
- Foreground commands only. **Every segment ends with the report block** — without it the runner restarts the
  segment labelled `report_missing` and burns its context for nothing. On `429 GoUsageLimitError`, end the
  segment with your report rather than retrying in a loop.

## Verification

- `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <files you changed> -Session ip-censor-3`
- `python gk-core/scripts/guard-verification-boundaries.py`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` when a guard or a workflow changes
- `$SS gk-forge/tools/seedsmith/tests -q` (the touched areas, named test files — not the whole tree) — the seedsmith
  skill's own runbook; `test_actions_description_completeness` fails pre-existing on a clean HEAD, so confirm
  any failure already exists before blaming your change.

On `user-mapped section open`, run `dotnet build-server shutdown` and retry.

## Evidence contract

The **printed reading**, never an exit code: the release gate's own output with what it found, the
seedsmith check's findings line, the regenerated tree's count, a test line with its counts. Fragments go
under `tasks/evidence-fragments/`.

## Boundaries

Do not widen the fence. Do not touch another session's files. Never commit conflict markers. Merge
`features/mega-merge` freely — the integration head moves several times an hour, and a registry conflict is
resolved with `.claude/cmdc-agents/scripts/union-registry-sides.py` (it unions the merge sides from git and
reports differences; never hand-edit a conflicted registry).

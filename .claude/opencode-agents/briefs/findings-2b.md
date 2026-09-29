# Lane brief — `findings-2b` (opencode continuation of `cmdc/findings-2`, L3b slice 2)

## Why this lane exists

`cmdc/findings-2` (pi, deepseek-v4.1-flash, 21 segments) died on a runner crash
(`FileNotFoundError`, state `failed`) while its pi session was out of quota. It
left exactly **one unmerged commit** plus a named next slice. This lane adopts
both and continues. It does NOT re-do landed work.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names, in this
session, then verify against code. A comment is not evidence; open the file.

## Goal

Adopt the orphaned ledger commit, then land keepverse KS3.1/L3b slice 2: the
twelve two-root files in `gk-core/tests/FusionRpg.Core.Tests`.

## Handover facts (already verified — do not re-derive, do confirm at adopt time)

- Predecessor branch `cmdc/findings-2` tip `5433b4738` = ledger-only commit
  `docs(keepverse): KS3.1/L3b slice 1's ledger line` (1 insertion in
  `tasks/keepverse-split-ledger.jsonl`). Its code commit `4dac40de7` (nine
  CORE-only `FusionRpg.Core.Tests` files route RepoRoot through
  `CoreRoot.Path`, marker walk deleted) is **already merged** — do not touch it.
- Slice-1 gate: `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` →
  `Passed! - Failed: 0, Passed: 9705, Skipped: 0, Total: 9705` (4 m 13 s).
- Population measurement (a reading, never a guard constant): 235
  `tests/**/*.cs` files name the injector directory at all; 172 mention it
  exactly once (pure signal, done in slice 1); **63 subject files remain**.
- Cheapest next slice (predecessor's own recommendation): the **twelve
  two-root files** in `FusionRpg.Core.Tests` that need content AND core roots —
  per-path edits, and that project's suite is ~4 minutes.
- `verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.Core.Tests/**')` selects
  `core-tests-fallback`, whose project `core` is the **65-project group**, so a
  one-file edit is asked to run the whole Core suite. That is documented
  transitional behaviour
  (`docs/architecture/test-verification-boundary/spec-core-split-wiring.md:55`,
  filed as TVB6.5's reading) — it is the TVB program's in-flight re-key, not
  yours to change. Gate each slice with the **project suite**, and record why
  in the ledger line, exactly as slice 1 did.
- Background (not this slice): the lane's original brief rows KS-F2 (guard
  against hand-rolled repo-root walks in `tests/**`) and CS-F2
  (`tasks/keepverse-split-todo.md`) are still open. If slice 2 closes cleanly
  and budget remains, say so in the REPORT and stop — the manager routes
  follow-ups, you do not widen scope.

## Allowed paths

- `tests/**`
- `scripts/**`
- `src/**`
- `docs/architecture/**`
- `tasks/keepverse-split-todo.md`
- `tasks/keepverse-split-ledger.jsonl`
- `tasks/content-stack-todo.md`
- `tasks/content-stack-ledger.jsonl`
- `tasks/reports/**`

## Off limits

Pipeline files, CI, guards, hooks, generated data (`gk-data/packs/fusion/data/seed/items/**`,
`gk-data/packs/fusion/data/seed/actions/**`, `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/atoms/generated/**`),
other lanes' paths. Never widen a guard, never add a `knownRed`, never pin a
population count in a test. Adopt the ledger line with `git cherry-pick -n`
or an equivalent single-line re-apply — never `git add -A`, never push,
never create branches (leave the tree dirty; the orchestrator harvests).

## Definition of done

1. `tasks/keepverse-split-ledger.jsonl` carries slice 1's adopted ledger line
   (content equal to `5433b4738`'s line) plus slice 2's own ledger line.
2. The twelve two-root `FusionRpg.Core.Tests` files route their roots through
   `CoreRoot.Path` (and the content root where needed); no `..\..\..` marker
   walk remains in them.
3. `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --verbosity minimal`
   prints `Failed: 0` on the changed tree.
4. `tasks/keepverse-split-todo.md` L3b row advanced with the evidence fragment
   (exact command text + printed numbers).

## Verification

- `git log --oneline -3` and `git show 5433b4738 -- tasks/keepverse-split-ledger.jsonl` — confirm what you adopt before touching the tree.
- `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --verbosity minimal` — must print `Failed: 0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — read the printed counts, not the exit code.

## Report

End your last message with the `<<<REPORT {...} REPORT>>>` block
(status/summary/changed_files/commits/verification/unproved), and every claim
in it must already be a change in this worktree.

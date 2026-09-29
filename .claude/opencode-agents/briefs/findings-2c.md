# Lane brief — `findings-2c` (fix the slice-2 build break, then re-report)

## Why this lane exists

`findings-2b` staged the full L3b slice 2 (12 two-root files + ledger/todo
lines) but left a structural slip that breaks compilation of the whole
`FusionRpg.Core.Tests` project. This lane inherits its tree
(`--base opencode/findings-2b`) and fixes exactly that. No new scope.

⛔ Read `docs/DESIGN-GATE.md` §1 first. No-shell protocol is binding (your
bash refuses): file work only, quote orchestrator-run commands tagged
`UNPROVED-BY-LANE`, never claim a run.

## The defect (manager-measured, exact)

`gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureAdmissionTests.cs` lines
112–118: after your `RepoRoot()` edit the method closes correctly at line
115, but lines 117–118 are orphaned remnants — a stray
`throw new DirectoryNotFoundException("repo root");` plus an extra closing
brace. Errors: CS1519 (invalid token 'throw'), CS1001, CS1022.

## Goal

Delete the orphan lines so `RepoRoot()` is one clean method, confirm the
method still matches slice-2 two-root intent for this file (content vs core
root — read the file's usages, do not guess), re-report. Nothing else changes.

## Allowed paths

- `gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureAdmissionTests.cs`
- `tasks/keepverse-split-todo.md`
- `tasks/keepverse-split-ledger.jsonl`

## Off limits

Everything else — the other 11 slice-2 files are landed, do not touch them.
Keepverse/content-stack files outside the two named. Commit nothing, push
nothing, create no branches — leave the tree dirty.

## Definition of done

1. `CreatureAdmissionTests.cs` has exactly one `RepoRoot()` method, no orphan
   lines, root choice justified by the file's usages (one line in the REPORT).
2. Slice-2 content otherwise byte-untouched (only the fix diff vs
   `opencode/findings-2b`).

## Verification (orchestrator-run; quote verbatim, tag UNPROVED-BY-LANE)

- `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --verbosity minimal` — must print `Failed: 0`.

## Report

`<<<REPORT {...} REPORT>>>`, every claim already a change in this worktree.

# Evidence — rpg-simulator UAR-F1 (the unlock chooser's own filter: re-measured, already landed)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Row UAR-F1, routed here by lane `rscf2` out of the RS-CF2 fix. The row's own
"what remains" had two halves; **both are in the tree**, landed by the ADG-F5 lane, and this increment
re-measures rather than assumes.

| Criterion | Command / read | Result | Artifact |
|---|---|---|---|
| The predicate lives in the chooser itself, not in the caller's catalog | read: `ActionUnlockGrantService.TryRollOnce` | `if (ActionValidator.GrantRefusal(a) is { } refusal) { skipped.Add(...); continue; }` — the roll cannot offer what the write path refuses | `gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:107` |
| The choice of home is argued, not accidental | read: the doc block above it | headed *"**ADG-F5 — the offered set must be grantable, and the filter lives here**"*, and it rejects both alternatives by name (`ActionEligibility.Candidates` is scope-only; the store's catalog delegate would make the DAL restate action-layer law) | same |
| The three fixtures set `Grantable = true` | read: the test file's helpers | `Row(...)` sets it with the reason (*"what the imported corpus rows carry"*), plus `BasicRow` / `UnGrantableRow` and four tests pinning the behaviour | `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs:22-35` |
| It passes | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~ActionUnlockGrantServiceTests"` | `Passed: 11, Failed: 0, Total: 11` (38 ms) | — |
| Which commits did it | `git log --oneline -- gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs` | `9ef4988ec fix(ADG-F5): the unlock roll never offers an action it cannot grant` (both halves) and `3a3d0d2da fix(ADG-F5): a refused option is skipped with a reason and reported, never thrown` | — |

**Boundary note, stated rather than compensated for.** The row's own verify line resolves the two files to
`core-fallback` plus `core-area-actions-owners` — about 69 test projects, i.e. the broad set that the
verification-boundary rules assign to CI. The focused class above is the reading this lane takes; running the
whole core fallback to restate it would be the wrong tool, not extra caution.

**What is left of the row, and it is not a deliverable:** its routing note (there is no
`tasks/unique-actor-runtime-todo.md`, so the row was recorded here) stands as a note for the manager. Nothing
in the unique-actor surface is left open by this row.

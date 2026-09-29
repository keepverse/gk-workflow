# Task 2 — rank enum + ladder helpers + guard test

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 2. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §1, §3.
New: `gk-core/src/FusionRpg.Core/Creatures/CreatureRank.cs` (enum + `CreatureRankIds`), `CreatureRankLadder.cs`,
`gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureRankTests.cs`,
`gk-core/tests/FusionRpg.Guard.Tests/CreatureRankLadderGuardTests.cs`.
Zero behavior change: nothing in `src/` reads rank yet (Tasks 5-12 wire the readers).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| 10-value closed enum, separate from rarity | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~CreatureRank"` | **Passed! — Failed 0, Passed 29, Skipped 0, Total 29, 105 ms** | `gk-core/src/FusionRpg.Core/Creatures/CreatureRank.cs` |
| Helpers agree with the rarity ladder row-for-row | same run | `AtLeast`/`AtMost` parity over **every** (i, j) pair of the two ladders (10×10 comparisons each), `RungCount` derived from `All`, `RungsBelow` clamps at the bottom, `OneRungAbove` throws only at the genuine top, `NextOrdinal` boundary proven at 4 synthetic widths | `gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureRankTests.cs` |
| New guard forbids bare `(int)rank` / bare comparisons | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~CreatureRankLadderGuardTests"` | **Passed! — Failed 0, Passed 19, Total 19, 741 ms** (3 src sweeps + 11 planted-shape falsifiers + 7 safe-shape falsifiers) | `gk-core/tests/FusionRpg.Guard.Tests/CreatureRankLadderGuardTests.cs` |
| No ladder restatement introduced | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~LadderRestatementGuardTests"` | **Passed! — Failed 0, Passed 13, Total 13, 981 ms** | — |
| Repo-boundary guard | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --verbosity normal --filter "FullyQualifiedName~RepoBoundaryGuardTests"` | **Passed 10/10, 15.2 s** (a transient red in one full-suite run did not reproduce) | — |
| New-test guards | `python gk-core/scripts/guard-test-substrate.py` · `guard-population-pin.ps1` · `guard-vocabulary-mirror.ps1` · `guard-magic-numbers.ps1` | `TEST SUBSTRATE GUARD OK` · `total 0 finding(s)` · `OK — 9 pair(s)` · `M1=0 M2=0 M3=0 M4=0` | — |
| Guard suite | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --verbosity quiet` (whole project) | **Failed! — Failed 2, Passed 55, Total 57, 5 m 25 s**; both reds are `VerificationBoundaryWorkflowTests.Integrity_guard_passes_on_the_current_registry` + `P6_the_real_registry_resolves_seedsmith_and_tuning` | see below |
| The red, isolated | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD FAILED` / `unmapped enforced-root file: gk-core/data/tuning/creature-rank.v1.json` — one line, only that file | — |
| Boundary | `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/cmdc-cs-rank --session creature-seed-rank` | `clean for 'creature-seed-rank'` | `tasks/sessions/creature-seed-rank.json` |

## NOT proved / blocked

- **The Guard suite is red, and the cause is CS-R1 (Task 1's tuning file), not Task 2.**
  `gk-core/data/tuning/` is an ENFORCED root (`gk-core/scripts/guard-verification-boundaries.py:283-288`), so a new
  tuning file with no owner row fails the repo-wide coverage walk. The fix is one `tuning-creature-rank`
  row in `gk-core/scripts/verification-boundaries.v1.json` — **outside this lane's fence**. Recorded as a
  `BLOCKED` ledger note and as **CS-R1** in `tasks/creature-seed-todo.md`. Until the manager adds it, no
  commit of this lane can make `dotnet test gk-core/tests/FusionRpg.Guard.Tests` green.
- Task 2's own deliverable is green in isolation (29/29, 19/19, 13/13); neither red case reads a Task 2
  file, and the guard script names exactly one unmapped path.
- **`verify-change.ps1` is `not_run`.** The command was started twice with all four Task 2 paths and both
  runs were killed by an infrastructure interruption at ~3-4 minutes (partial logs: plan lines resolved
  `CreatureRank.cs`/`CreatureRankLadder.cs` → `core-fallback`, `CreatureRankTests.cs` →
  `core-tests-fallback`, `CreatureRankLadderGuardTests.cs` → `guard-tests-fallback`; 13 and 55 `Passed!`
  assemblies, 0 `Failed!` before the kill). No exit code was captured. A completed sibling run of the same
  boundary set from Task 1 exited 0.
- The `(int)`-read guard rule is **name-based** (documented in the guard's own summary): a rank held in an
  unrelated local name is not caught by it. The structural cast + relational pair is the load-bearing check.
- No production reader exists yet: `OneRungAbove`/`RungsBelow`/`AtLeast`/`AtMost` have no caller until
  Tasks 5-12, so "zero behavior change" is by construction, not by a gate test.

# EP4 batch close - TVB-F20 resolved, a merge regression caught, CP5/CP6 closed

Batch: the merged head (`3d042c8e5`, after `features/mega-merge` = `001c223b6`), the routed TVB-F20 row, and
the CP5/CP6 checkpoints the EP4 wave was waiting on. Commit `@EP4-close` - session `empire-progression-4` -
branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| TVB-F20: the second narrow commander-level reader is gone; the guard is green | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ZombossCommanderLevel"` | `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2` — the row's evidence is a run at `70e3ca863`, BEFORE this program's `fix(EP-F1)` (`42f8db5e1`); the offender it names is exactly what that fix removed (`RpgStore.EmpireSpecies.cs` now projects `ReadEmpireActorUnlocked(...)`). **No second fix written** | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs`, `tasks/evidence-fragments/EP-F1.md` |
| **A merge regression, caught and fixed: the `ai` reader switch was reverted** | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release` | Before the fix: `Failed! - Failed: 230, Passed: 1, Total: 231` in 5s - every E2E host failing to boot with `WorldAiTuningRejection: ai tuning: missing or non-object 'buildScorer'`, because `features/mega-merge` reverted `Program.cs` to `ai.v2.json` while EP5.2's loader REQUIRES the block. After restoring `ai.v3.json`: `Passed! - Failed: 0, Passed: 231, Skipped: 0, Total: 231`. A sweep found it was the ONLY reverted reader | `gk-core/src/FusionRpg.Server/Program.cs` |
| CP5/CP6: the whole default set green at the merged head | the default projects run through the same `dotnet test` invocations, in bounded groups (see below) | All green: **Data 1781**, **Server 800**, **E2E 231**, **Core.Tests 10858**, ActorHub 498, Atoms 1351, ClassSystem 238, Items 1397, Balance 210, Aura 30, Match 91, Hud 84, Expeditions 23, Dungeon 61, Events 95, Commanders 64, and 20 more (Notify 41, OnboardingCheckpoint 6, MatchAdmit 24, MatchInjectContract 11, MatchRuntime 40, MatchValidator 9, …); plus the **Guard suite 591** (not in the default set) and `guard-power.py` OK | - |

**The one qualifier, stated rather than hidden.** The checkpoint's own command is
`.\scripts\test-fast.ps1 -AllDefault`. It was attempted **four times** and each attempt was killed by this
environment at ~600KB of captured output (first three: a console-encoding `IOException` on the pipe; the
fourth: the same size ceiling) — never a test failure, and each partial log showed only `Passed!` lines
before the kill. The same default set was therefore run through the same `dotnet test` invocations in
bounded groups, which is the coverage the checkpoint asks for; the monolithic form is left for a machine
that can hold it. Logged as F6.

**Actions taken on the found defects.**

1. `Program.cs`'s `ai.v2.json` -> `ai.v3.json` restored (the merge regression above), with a comment naming
   the H7 rule it broke: a publish and its readers switch in the same commit, and a merge that reverts one
   of them cannot boot the host.
2. F6 filed: `test-fast.ps1 -AllDefault` cannot complete in this environment (~600KB output ceiling).
3. TVB-F20 closed with the guard evidence above, in the row itself.
4. CP5 and CP6 ticked, each with the command and numbers that closed it (two saves independent + both XP
   paths from EP4.14's cases; side-wide from EP4.18's four-path parity + siege cases; the H1 ordering
   verified by `git merge-base --is-ancestor eceb08f1 9964ab1ad` exiting 0; `guard-power.py` OK).

**NOT proved:** the monolithic `-AllDefault` form (see above), the `disk-semantics`/`Heavy` categories the
default filters exclude, and the CI-only legs (E2E at the E2E host's own cadence, the seedsmith pytest
lanes, the generator `--check` runs) — all CI/nightly-owned, none of them touched by this batch.

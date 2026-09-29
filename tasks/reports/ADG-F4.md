# ADG-F4 — an E2E test that failed in the suite and passed alone

Lane `adg-f4`, session `action-dist-gaps-f4`, worktree `.claude/worktrees/cmdc-adg-f4` (branch `cmdc/adg-f4`).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the suite failure, reproduced | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` | `Failed: 1, Passed: 230, Total: 231` (2 m 49 s); `System.InvalidOperationException : action unlock grant refused: BasicCollision` — the stack's own line is `UnlockTuningActivationTests.cs:88` in the pre-fix file (the award now sits at `:123`) | this file |
| the same test alone | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~A_real_level_up_grants_a_real_action_row"` | `Passed! - Failed: 0, Passed: 1` (12 s); repeated 5×, 5 passed | this file |
| the shared state, named | `--filter "FullyQualifiedName~ActionBudgetReportTests\|FullyQualifiedName~UnlockTuningActivationTests"` | `Failed: 1` with the same message — the two classes together are sufficient, either alone passes | this file |
| the candidate set, measured | the same pair + a temporary probe (deleted before commit) | boot alone: catalog 1 row, 1 candidate. After `ActionBudgetReportTests`: catalog 19 rows, **5** candidates — `act.attack` (Basic/General) + `action.general.0003/0004/0005` + the test's own row | this file |
| E2E project green twice in a row | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` ×2 | `Passed! - Failed: 0, Passed: 231, Total: 231` (1 m 51 s, 1 m 55 s) | this file |
| the default profile's E2E gate | `pwsh -NoProfile -File scripts/test-fast.ps1 -Project gk-core/tests/FusionRpg.E2E.Tests` | `Failed: 0, Passed: 231, Total: 231` (filter `Category!=DiskSemantics&Category!=Heavy`) | this file |
| the scoped boundary | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths gk-core/tests/FusionRpg.E2E.Tests/UnlockTuningActivationTests.cs -Session action-dist-gaps-f4` | `DAL GUARD OK`, `TEST SUBSTRATE GUARD OK`, `e2e-action-unlock` → `Passed: 231` | this file |
| `-AllDefault` | `pwsh -NoProfile -File scripts/test-fast.ps1 -AllDefault` | guard OK + `FusionRpg.Data.Tests 1784 passed` — **twice**, both cut off by a segment interruption before `Server.Tests` | this file |
| the rest of `-AllDefault`, identical profile | `pwsh -NoProfile -Command "./scripts/test-fast.ps1 -Project <49 projects>"` (3 chunks) | `Server.Tests` 803; 47 Core projects 15455; every project `Failed: 0` | this file |

**Root cause (the shared state, by `file:line`).** `ActionUnlockGrantService.TryRollOnce`
(`gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:107-153`) draws the offered action from the
**whole catalog of the store it awards XP on**, filtered only by already-held ids.
`ActionBudgetReportTests.SeedThroughTheRealImportPath` (`gk-core/tests/FusionRpg.E2E.Tests/ActionBudgetReportTests.cs:135-157`,
called at `:50-52`) imports the real action corpus into the **shared** `RpgApiFactory.DataDir`, adding
`act.attack` — `Kind = Basic`, `Scope = General` (`gk-data/packs/fusion/data/seed/actions/authored-basics.json`).
`ActionValidator.ValidateGrant` (`gk-core/src/FusionRpg.Core/Actions/ActionValidator.cs:87`) refuses every basic by
construction, so when the multi-level award's roll walks the candidate list it reaches that row, the grant
throws, and the XP award's transaction rolls the level-up back. Deterministic in the suite (every accepted
candidate is held, so the basic is never consumed), deterministic pass alone (one candidate).

**Fix.** `UnlockTuningActivationTests` keeps the host boot (it configures the process-wide rung/tuning
holders) but the level-up test now runs on its own `DataTestStore.Create()` in-memory store, so the only
candidate is the action under test; the always-hit control tuning is restored in `finally` instead of
leaking into the rest of the collection. Assertion, specimen, XP award and grant write are unchanged — no
`Skip`, no parallelism change, no weakened assert.

**NOT proved.** (1) A single uninterrupted `-AllDefault` run: the exact command was started twice and both
times the segment was cut off after `Data.Tests`; the remaining projects were run through the same script,
filter and `-c Release --blame-hang` flags via `-Project`. (2) The production fix itself — `ADG-F5` is filed,
not patched (outside this lane's fence). (3) That `act.attack` is the only non-grantable row a live catalog
offers; only that a Basic row is reachable and throws. (4) The E2E project under the `full` profile (no
filter).

**Correction (ADG-F5, 2026-09-22).** The two `file:line` citations above were re-anchored to the post-fix
file when ADG-F5 changed the method they point into: `ActionUnlockGrantService.TryRollOnce` now spans
`:107-153` (it was `:62-93`) and the basic refusal in `ActionValidator` is now made through
`GrantRefusal` at `:87` (it was inline at `:83`). The measurements here are unchanged — they were taken
against the pre-fix file, which is what the row describes.

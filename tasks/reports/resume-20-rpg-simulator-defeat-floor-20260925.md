# Resume 20 — RS-F27 real defeat-award floor

- **Session:** `opencode-resume-20-rpg-sim-defeat-floor-20260925`
- **Date:** 2026-09-25
- **Base commit SHA:** `6d77888cca860805e5a11e617e201847e01c16b7`
- **Policy:** an empty progression ledger remains legal for `victory` and `stalemate`; when a sampled real run reads `defeat`, the normal progression-ledger route must contain a row whose wire fields are exactly `kind=player` and `reason=defeat`.

## Reproduced current shape

Before changing the test, the required command was run against the merged RS-F27 test:

```powershell
$env:FUSIONRPG_RSF27_SAMPLES = '20'; dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --nologo --no-restore --filter "FullyQualifiedName~RS_F27_measures_progression_ledger_non_vacuity_across_real_runs" --logger "console;verbosity=detailed"
```

The fresh worktree initially had no restored NuGet assets file; under the installed .NET 10.0.303 SDK, the first three `--no-restore` invocations exited `0` without discovering a test and were discarded as false no-ops. One foreground restore was run:

```powershell
dotnet restore gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --nologo
```

After restore, the exact required command executed the real test: `Passed: 1, Failed: 0` over 20 fresh-host samples. The observed outcomes were `defeat=20`, and every real ledger contained `player:defeat`; samples 4 and 20 also contained `player:kill`. The pre-change test nevertheless asserted only `ledgerLength > 0`. That reproduced the policy gap as a **false-green guard shape**, not as a product failure: a non-empty but unrelated ledger row would have satisfied the old floor.

## Smallest policy change

`gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs` now reads the returned ledger items and computes `hasPlayerDefeatAward` from the two wire fields:

```text
kind == "player" && reason == "defeat"
```

Only when the sampled run list contains a real `defeat` does the test assert that exact row. There is still no unconditional non-empty assertion, so `victory` and `stalemate` may legally return an empty ledger. No outcome was selected or forced, no ledger row was manually inserted, and neither the scenario fixture nor the accepted resume-13 report changed.

The assertion matches the production policy rather than duplicating it in test prose: `RpgXpAwardMap.FromActivity` returns a player award with reason `defeat` for a normalized defeat and no award for other match results (`gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs:57-61`); the real activity application keeps player awards in web mode (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:72-82`); and the checked route reads persisted ledger rows through `ListRpgXpLedger` (`gk-core/src/FusionRpg.Server/Program.cs:1673-1676`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:669-744`). This stays a wire-contract assertion, not a pinned corpus or outcome-population count (`docs/architecture/validation-ssot.md:59-89`).

## Post-change measurement

Exact command and sample count:

```powershell
$env:FUSIONRPG_RSF27_SAMPLES = '20'; dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --nologo --no-restore --filter "FullyQualifiedName~RS_F27_measures_progression_ledger_non_vacuity_across_real_runs" --logger "console;verbosity=detailed"
```

`FUSIONRPG_RSF27_SAMPLES=20` produced 20 settled real in-process-host samples. Result: `Passed: 1, Failed: 0, Total: 1`.

Observed outcome distribution:

| outcome | samples |
|---|---:|
| `victory` | 0 |
| `defeat` | 20 |
| `stalemate` | 0 |

Observed ledger distribution:

| read-back rows | samples |
|---|---:|
| `[player:defeat]` | 19 |
| `[player:defeat,player:kill]` | 1 |
| no `player:defeat` row | 0 |

Ledger lengths, in sample order:

```text
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1
```

Every sample read its outcome from `GET /api/runs?playerId=2` and its ledger from `GET /api/rpg/progression/2/ledger`. All 20 therefore passed the conditional exact `player` / `defeat` row assertion.

## Changed files

- `gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs` — replaces the weak non-empty defeat floor with the exact `player` / `defeat` ledger-row assertion.
- `tasks/reports/resume-20-rpg-simulator-defeat-floor-20260925.md` — this report.

No other tracked path changed. `tasks/reports/resume-13-rpg-simulator-rsf27-20260925.md` remains untouched.

## Commit SHA

- **Starting/base SHA:** `6d77888cca860805e5a11e617e201847e01c16b7`.
- **Implementation commit SHA:** not created in this lane. The binding lane instructions explicitly require “Commit nothing” and say the orchestrator harvests and commits the dirty tree. Claiming a commit SHA here would therefore be false; the orchestrator must create the one logical commit from the two explicit paths above.

## What this does not prove

- It does not prove the legal-empty `victory` or `stalemate` branch at runtime: this 20-sample run produced only `defeat`.
- It does not add deterministic outcome selection or fill the missing outcome vocabulary.
- It does not prove the award amount, XP curve, idempotency across replays, or every battle mode; it proves the persisted row's `player` / `defeat` identity on this real in-process route.
- It does not replace real-process simulator, live-game, or aggregate-suite evidence. The required focused command is the local acceptance proof for this test-only follow-up.
- It does not fabricate the two unreached outcomes or manually insert any ledger row.

## Verification

```powershell
$env:FUSIONRPG_RSF27_SAMPLES = '20'; dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --nologo --no-restore --filter "FullyQualifiedName~RS_F27_measures_progression_ledger_non_vacuity_across_real_runs" --logger "console;verbosity=detailed"
```

Result: exit `0`; `Passed: 1, Failed: 0, Total: 1`; 20/20 samples contained the exact `player:defeat` row.

```powershell
git diff --check
```

Result: exit `0`.

<<<REPORT {"status":"done","summary":"Tightened RS-F27 so a sampled real defeat requires a persisted progression-ledger row with kind=player and reason=defeat while victory/stalemate remain legal-empty. A 20-sample real fresh-host run passed 1/1; all 20 outcomes were defeat, 19 ledgers were [player:defeat], one was [player:defeat,player:kill], and none lacked player:defeat. The worktree is intentionally left uncommitted for orchestrator harvest under the binding lane rule.","changed_files":["gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs","tasks/reports/resume-20-rpg-simulator-defeat-floor-20260925.md"],"verification":[{"command":"$env:FUSIONRPG_RSF27_SAMPLES = '20'; dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --nologo --no-restore --filter \"FullyQualifiedName~RS_F27_measures_progression_ledger_non_vacuity_across_real_runs\" --logger \"console;verbosity=detailed\"","result":"exit 0; Passed 1, Failed 0, Total 1; 20 real samples, all defeat, all with exact player:defeat row"},{"command":"git diff --check","result":"exit 0"}],"open_issues":["victory and stalemate were not sampled, so their legal-empty branch remains unexercised by this run","deterministic outcome selection remains outside this test-only follow-up","commit SHA is pending because the binding lane instruction requires an uncommitted dirty tree for orchestrator harvest"]} REPORT>>>

# TVB-F26 — a stripped PATH printed phantom guard reds, and the runner now names the gap

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the phantom reds, reproduced | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` (PATH = a bash shell's own + `dotnet`; no `python`, no `C:\Windows\System32\WindowsPowerShell\v1.0`) | `guards failed: doc-citations, magic-numbers, narrative, overflow, population-pin, vocabulary-mirror` — **6 red of 25** | this fragment |
| the same tier, one interpreter set away | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` (PATH + `python` + `C:\Windows\System32\WindowsPowerShell\v1.0`) | `guards failed: doc-citations` — **1 red of 25**, the pre-existing `RS-F18`; every other row `exit 0` | this fragment |
| `narrative` is a phantom, not a red | `python gk-core/scripts/guard-narrative.py -RunTraitFilter` (complete PATH) | `FusionRpg.Core.Tests -> Guard=narrative selected 30 test(s), 0 failed`; `FusionRpg.Guard.Tests -> selected 5 test(s), 0 failed`; `NARRATIVE GUARD OK - 3 row(s) guarded by 'narrative', 3 mapped` | this fragment |
| the warning prints, and is **not** a hard stop | `env PATH=/nonexistent pwsh -NoProfile -File scripts/run-guards.ps1 -Only dal` | `WARNING (environment, not a guard verdict): PATH has no 'dotnet', 'python', 'powershell'.` then `DAL GUARD OK` / `GUARDS OK - 1 guard(s) run, 0 red` | this fragment |
| a phantom red now says so in the failure line | `env PATH=/nonexistent pwsh -NoProfile -File scripts/run-guards.ps1 -Only magic-numbers` | `guards failed: magic-numbers (PATH lacks dotnet, python, powershell: a red guard that shells out to one is an environment fault, not a verdict)` | this fragment |
| silent when PATH is complete | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` (complete PATH) | no `WARNING` line printed at all | this fragment |
| regression on the runner's own contract | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~GuardRunner"` | `Passed! - Failed: 0, Passed: 8, Skipped: 0, Total: 8 - FusionRpg.Guard.Tests.dll (net8.0)`, 9 s | this fragment |
| the owed regression test | edit `gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs` (the project that drives the real runner) | **refused by the pipeline guard**: `protected pipeline file (guards, verify, ledger script, hooks, CI)` | TVB-F26 |

Five of the six reds are the same guard class: a guard shells out to an interpreter **by name**, so its
absence arrives as that guard's own exit 1. The runner cannot know which interpreter a guard needs (that
is the guard's own business), so the fix names the gap instead of pre-resolving one — and deliberately
does not stop the batch, because a source-only guard is still a genuine verdict under the same PATH.

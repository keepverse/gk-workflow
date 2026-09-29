# TVB2.1 — Shared lib `scripts/lib/VerificationBoundaries.ps1` + last-segment wildcard + specificity

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Test-PatternMatch`, `Get-PatternSpecificity`, `Resolve-Owner`, accepted `schemaVersion` live in the lib; both scripts dot-source it; duplicated `Matches` deleted | inspect `scripts/verify-change.ps1`, `gk-core/scripts/guard-verification-boundaries.py` | both dot-source `lib/VerificationBoundaries.ps1`; no local `Matches` function remains in either | new lib + both scripts |
| Starts from `schemaVersion` 2 (SE0.7's) | inspect lib | `$Script:AcceptedVerificationSchemaVersion = 2` | `scripts/lib/VerificationBoundaries.ps1` |
| T4 (wildcard beats `/**`) | `T4_a_wildcard_pattern_beats_a_broader_double_star_owner` | passed | `VerificationBoundaryWorkflowTests.cs` |
| T5 (exact beats wildcard, no AMBIGUOUS) | `T5_an_exact_pattern_beats_a_matching_wildcard_pattern_no_ambiguity` | passed | same |
| T6 (`*` in a non-final segment rejected) | 4 grammar cases + a real planted-registry guard rejection | all passed | same |
| Real registry still passes; depth reading unchanged | `python gk-core/scripts/guard-verification-boundaries.py --report` | `VERIFICATION BOUNDARY GUARD OK`, same depth numbers as before the refactor | console |
| Full `VerificationBoundaryWorkflowTests` class green | `dotnet test ... --filter VerificationBoundaryWorkflowTests` | 23/23 (21 clean in the batch run, 2 confirmed via isolated re-run — see notes) | console |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,scripts/verify-change.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs,gk-core/scripts/verification-boundaries.v1.json --session summoner-convergence-lane-d2-20260919` | 23/23 passed | plan resolved `guard-verification-boundary-tests` (focused) |

**Contention note (per coordinator instruction — foreground, re-run in isolation before judging):**
two pre-existing tests (`Planner_refuses_an_unmapped_path...`, `Planner_can_select_a_registered_deleted_path...`)
hit the 120s `ExternalProcess.Run` timeout during the full-class batch run (30+ concurrent
`dotnet.exe`/`powershell.exe` processes from other sessions at the time). Timed the exact underlying
command directly (`powershell -File scripts/verify-change.ps1 ...`, no test-harness timeout): 16.3s.
Re-ran both tests in isolation: both passed (17s, 1m39s) — confirmed contention, not a regression from
this refactor.

**New registry entry:** `scripts/lib/VerificationBoundaries.ps1` had no owner (a new file); added to
the existing `guard-verification-boundary-tests` boundary's `paths` alongside the two scripts it
serves.

# TVB2.2 — Derived `level` (C3) + stale exact path (C8) + the three G3 label fixes

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Guard derives `level` from `kind` + selector, fails a mismatch | `Get-DerivedLevel` in the lib, wired into the guard's per-boundary loop | new | `scripts/lib/VerificationBoundaries.ps1`, `gk-core/scripts/guard-verification-boundaries.py` |
| Three G3 label fixes (no selection change, label only) | inspect registry | `battle-effect-math` module->focused; `session-and-program-records` focused->module; `effect-catalog-drift` focused->seam | `gk-core/scripts/verification-boundaries.v1.json` |
| An exact pattern naming no file fails `stale exact path: <boundary>: <pattern>` | `Test-ExactPattern` + `Test-Path` check in the guard | new | same two files |
| T3 (level disagrees with selector) | `T3_a_level_that_disagrees_with_its_own_selector_is_rejected` | passed | `VerificationBoundaryWorkflowTests.cs` |
| T13 (exact path deleted -> stale) | `T13_an_exact_path_that_stops_existing_fails_as_stale` | passed (green before delete, red with the exact message after) | same |
| Real registry passes C3 and C8 | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` — confirms the spec's own claim ("the tree is clean against C8 today") and that every OTHER boundary's level already agreed with its derivation | console |
| T9 (real registry) still passes | `Integrity_guard_passes_on_the_current_registry` | passed (part of the 25/25 full-class run) | console |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths gk-core/scripts/guard-verification-boundaries.py,scripts/lib/VerificationBoundaries.ps1,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session summoner-convergence-lane-d2-20260919` | 25/25 passed | plan resolved `guard-verification-boundary-tests` |

Full `VerificationBoundaryWorkflowTests` class run twice this task (once mid-work, once for the scoped
verify) — 25/25 both times, no contention flake this round.

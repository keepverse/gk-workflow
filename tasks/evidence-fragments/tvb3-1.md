# TVB3.1 — Object projects, closed `runner` vocabulary, D2 pairing rules + schemaVersion 4

| Criterion | Result |
|---|---|
| `projects` values: string / array / object with `runner` in {dotnet, pytest, script} (closed, 3) | added to guard's project-shape validation; `nose` rejected (P5) |
| `testFiles` only on pytest; `verificationId` never on pytest/script; `selfSelect` only under the project's test dir | D2 pairing checks added per boundary |
| Every `testFiles` pattern matches >= 1 real `test_*.py` under `<root>/<tests>` | added (P3) |
| `schemaVersion` -> 4 (lib constant, real registry, all 10 planted registries) | done |
| Lib additions | `Get-ProjectRunner`, `Get-PytestProjectDirs`; `Get-ProjectMembers` returns `@()` for an object (was about to stringify the whole object into a garbage path); `Get-DerivedLevel` treats `testFiles`/`selfSelect` as selectors too |
| P3 (testFiles pattern matches nothing) | passed |
| P4a (verificationId on pytest) | passed |
| P4b (testFiles on dotnet) | passed |
| P5 (runner "nose") | passed |
| Real registry unaffected (no object-shaped project exists yet - those land in TVB3.3's D4 boundaries) | `guard-verification-boundaries.py` -> OK |
| Full class | 40/40 (one run clean at 10m; a second scoped-verify run hit 4 spurious 120s timeouts under heavier concurrent load — all 5 theory/fact cases re-run in isolation immediately after: 32-39s each, all passed, confirming contention per the standing rule) |

Scoped verify: `.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session summoner-convergence-lane-d2-20260919`.

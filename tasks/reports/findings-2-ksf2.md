# KS-F2 — a hand-rolled repo-root walk in a test is now refused, with a planted violation

Lane `findings-2`, row `tasks/keepverse-split-todo.md` KS-F2 (`= CS-F1-b` in `tasks/creature-seed-todo.md`).
Delivered: `scripts/guard-test-content-root.ps1` + its registry/boundary wiring +
`gk-core/tests/FusionRpg.Guard.Tests/TestContentRootGuardTests.cs`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The guard passes on the real tree | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-test-content-root.ps1` | exit 0; `scanned 1596 tests/**/*.cs file(s); 47 declare [CallerFilePath]; 60 anchored walk(s) resolved`; `TEST CONTENT-ROOT GUARD OK` | `scripts/guard-test-content-root.ps1` |
| Same verdict on the other host the runner may pick | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/guard-test-content-root.ps1` | exit 0, identical reading (Windows PowerShell 5.1) | — |
| Planted violation fails, real tree passes | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "VerificationId=guard.test-content-root" --verbosity minimal` | `Passed! - Failed: 0, Passed: 6` — escape (CS-F1 shape), miss, a correct depth-3 walk, a `fixtures` walk, a runtime walk-up loop, and the local-wiring case | `gk-core/tests/FusionRpg.Guard.Tests/TestContentRootGuardTests.cs` |
| The guard bites on the CS-F1 shape | the escape case above (probe tree, `-Root`) | exit 1; `gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs:8: walk-escapes-root - 3 ".." from depth 2 resolves 1 level(s) ABOVE the repository root` | same |
| The guard bites on the quiet half | the miss case above (probe tree, `-Root`) | exit 1; `walk-misses-root - "repo" resolves 1 level(s) BELOW the repository root, then names "data"` | same |
| Nothing else in the guard project moved | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --verbosity minimal` | `Passed! - Failed: 0, Passed: 599, Skipped: 0, Total: 599` (5 m 40 s) | — |
| Wired the way the other guards are | `python gk-core/scripts/guard-verification-boundaries.py --skip-coverage-walk` | exit 0, `VERIFICATION BOUNDARY GUARD OK` | `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/scripts/enforcement-registry.v1.json` |
| The tier reads 22 guards, 0 red | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | `test-content-root ci gating 0`; `GUARDS OK - 22 guard(s) run, 0 red` (21 before this row) | — |
| The population, re-measured (never pinned) | `python -c` over `git ls-files tests` `*.cs`: walk literal `"\.\."(\s*,\s*"\.\.")+`, root name `"(data\|content\|docs\|tasks)"` | `58` walk-literal files, `30` naming a Keepverse root, `47` declaring `[CallerFilePath]` — findings-1's erratum figure, reproduced | this file |

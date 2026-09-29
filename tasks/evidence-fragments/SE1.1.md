# SE1.1 — Wire the five green guards

Re-run on the branch-tip working tree carrying only this task's two files
(`git status --short` = `gk-core/scripts/enforcement-registry.v1.json` + the meta-test).

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `debug-scope` re-run | `python gk-core/scripts/guard-debug-scope.py` | exit 0 — `DEBUG SCOPE GUARD OK -- 103 route(s), 0 banner mismatches` | gk-core/scripts/guard-debug-scope.py |
| `magic-numbers` re-run | `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` | exit 0 — `M1=0 M2=0 M3=0 M4=0`, `MAGIC-NUMBER GUARD OK — no M1/M2 findings` | scripts/guard-magic-numbers.ps1 |
| `overflow` re-run | `pwsh -NoProfile -File scripts/guard-overflow.ps1` | exit 0 — `A2=0 A3=0 A4=0 A5=0 A6=0`, `OVERFLOW GUARD OK — no critical findings` | scripts/guard-overflow.ps1 |
| `power` re-run | `python gk-core/scripts/guard-power.py` | exit 0 — `POWER GUARD OK — one ladder, pin holds, no private f(level)` | gk-core/scripts/guard-power.py |
| `stat-pairs` re-run | `pwsh -NoProfile -File scripts/guard-stat-pairs.ps1` | exit 0 — `STAT-PAIRS GUARD OK — every Contest paired, every pair symmetric` | scripts/guard-stat-pairs.ps1 |
| the five rows flip `ci`/`backlog` → `ci`/`gating` | read `gk-core/scripts/enforcement-registry.v1.json` | five rows now `"tier": "ci", "status": "gating", "backlogModule": null` | gk-core/scripts/enforcement-registry.v1.json |
| `local` reasons name the game install (R4 extension, with falsifier) | `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj -c Release --verbosity minimal --filter "FullyQualifiedName~EnforcementRegistry"` | `Passed!  - Failed: 0, Passed: 18, Skipped: 0, Total: 18` (17 + the new `R4_falsifier_a_local_reason_that_names_no_game_install_is_refused`); both real `local` rows name `-GameDir` / `FUSIONRPG_ML_GAMEDIR` / "game install" | gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs |
| the five actually run under the runner | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | exit 0 — `GUARDS OK - 13 guard(s) run, 0 red`; each of the five prints `ci gating 0` in the summary table | scripts/run-guards.ps1 |
| five falsifier runs, each making its gate red | 5 scratch-root/fixture runs (commands + violations in the commit body) | 5/5 exit 1 — `debug-scope` banner mismatch, `M1=1`, `A4=1`, `G1` literal curve field, `P1 Contest class with no counterpart` | — |
| (scope note) `session-boundary` stays `ci`/`backlog` | `python scripts/session-boundary-check.py` has no CI execution path; `run-guards -Tier ci` never reaches it and `R4` admits only the game-install reason | full run contradicts nothing; recorded as a manager erratum ask in the ledger | gk-core/scripts/enforcement-registry.v1.json |

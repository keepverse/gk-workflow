# SE0.2 — EnforcementRegistryGuardTests R1–R8, with a falsifier each

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| R1–R8 green on the real tree | `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj -c Release --verbosity minimal --filter "FullyQualifiedName~EnforcementRegistry"` | `Passed!  - Failed: 0, Passed: 17, Skipped: 0, Total: 17, Duration: 89 ms` | gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs |
| eight falsifiers fail on in-memory broken registries | same run — the eight `R*_falsifier_*` facts | green; each builds a broken registry via `EnforcementRegistry.FromJson` (never written to disk) and asserts the same rule reports it | EnforcementRegistryGuardTests.cs |
| R5 in transitional form (checks `ci.yml` when no runner exists) | same run — `R5_a_gating_ci_guard_is_actually_run` | green; branches on whether `scripts/run-guards.ps1` exists, comparing with separator normalisation | EnforcementRegistryGuardTests.cs |
| one shared `EnforcementMap.ModuleIds` parser that fails loudly if the module table is missing | same run — `ModuleIds_fails_loudly_when_the_map_carries_no_module_table` | green; a temp map with no `## Modules` heading throws `InvalidOperationException` naming it (throwing delete in `finally`) | gk-core/tests/FusionRpg.Guard.Tests/EnforcementMap.cs |

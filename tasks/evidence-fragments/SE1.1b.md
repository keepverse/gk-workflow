# SE1.1b — merge reconciliation: `SR-23` struck with the git-gate retirement

The `features/mega-merge` merge (`0c2b23c1`) brought `6b9f6d21`, which deleted
`scripts/commit-tool/` and the `commit-policy` guard but left `SR-23` — whose `where`
cell pointed at the deleted `scripts/commit-tool/policy.json` — unstruck, so the
register's own file-existence fact went red on the merged tree.

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| the merge keeps the retirement (no `commit-policy` row) and this lane's five `gating` rows | read `gk-core/scripts/enforcement-registry.v1.json` | `commit-policy` absent; `debug-scope`/`magic-numbers`/`overflow`/`power`/`stat-pairs` = `ci`/`gating`; `pr-commit-attribution` = `guards: []` + `unguardableReason` naming the 2026-09-19 retirement | gk-core/scripts/enforcement-registry.v1.json |
| the conflict keeps both incoming features | read `gk-core/src/FusionRpg.Core/Creatures/Generation/ConcreteSpeciesSerializer.cs:41-51` | the CS13 `speciesKind` mark (only when non-default) **and** TVB-EOL1's `.ToLf() + "\n"` both present; no conflict marker | gk-core/src/FusionRpg.Core/Creatures/Generation/ConcreteSpeciesSerializer.cs |
| `SR-23` is struck with the SHA, never deleted | read `docs/architecture/stub-register.md:71` | `~~SR-23~~` + CLOSED 2026-09-19 with `6b9f6d21` and the reason; the row still carries all six fields | docs/architecture/stub-register.md |
| the register's schema/closure facts are green again | `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj -c Release --verbosity minimal --filter "FullyQualifiedName~StubRegister"` | `Passed!  - Failed: 0, Passed: 7, Skipped: 0, Total: 7` | gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs |
| the enforcement registry's R1–R8 still green after the merge | `dotnet test … --filter "FullyQualifiedName~EnforcementRegistry"` | `Passed!  - Failed: 0, Passed: 18, Skipped: 0, Total: 18` | gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs |
| the disk/catalog guard set still agrees | `ls scripts/guard-*.ps1` vs the catalog's `script` column | 17 on disk; every one catalogued, and the catalog's 18 rows each point at an existing file (`guard-commit-policy.ps1` is gone from both) | — |

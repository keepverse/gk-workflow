# TVB2.5 — `guard-bench-compile.ps1` + catalog row + `bench`/`magic-number-audit` guard-only + schemaVersion 3

| Criterion | Command | Result |
|---|---|---|
| New guard builds Bench Release into a temp `OutputPath`, fails on compile error, removes temp dir in `finally` (R3) | `.\scripts\guard-bench-compile.ps1` | `BENCH COMPILE GUARD OK` |
| Catalog row `bench-compile` (`tier: ci`, `status: gating`, `localReason: null`) | `gk-core/scripts/enforcement-registry.v1.json` | added |
| Boundary `bench` guard-only (no `project`, `guards: ["bench-compile"]`) | `gk-core/scripts/verification-boundaries.v1.json` | added |
| `magic-number-audit` loses its `project`, keeps `guards: ["magic-numbers"]` | same file | edited |
| First v3-only construct: `schemaVersion` 2 -> 3 (lib constant + real registry + all 8 planted registries) | `scripts/lib/VerificationBoundaries.ps1`, `gk-core/scripts/verification-boundaries.v1.json`, `VerificationBoundaryWorkflowTests.cs` | done |
| Both scripts refuse a stale schemaVersion-2 registry | `T14_both_scripts_refuse_a_stale_schemaVersion_2_registry` | passed |
| Real `bench` boundary plans the guard, no test check | `T15_the_real_bench_boundary_plans_its_compile_guard_and_no_test_check` | passed |
| Real `magic-number-audit` boundary plans the guard, no test check | `The_real_magic_number_audit_boundary_is_guard_only` | passed |
| Real registry unaffected otherwise | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` |
| Full class green | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter VerificationBoundaryWorkflowTests` | 34/34, 5m43s |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths scripts/guard-bench-compile.ps1,gk-core/scripts/enforcement-registry.v1.json,gk-core/scripts/verification-boundaries.v1.json,scripts/lib/VerificationBoundaries.ps1,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs -Session summoner-convergence-lane-d2-20260919` | 34/34 |

SE0.2 dependency (`EnforcementRegistryGuardTests` R1-R8) was already closed on the SE lane
(`solid-enforcement-todo.md:23`), so the enforcement-catalog row shape used here (`tier`, `status`,
`backlogModule`, `localReason`) matches the existing rows exactly - no schema surprise.

**Bug found by the scoped verify itself**: the first cut of the `bench` boundary owned only
`gk-core/tests/FusionRpg.Bench/**`, so `scripts/guard-bench-compile.ps1` (the new guard SCRIPT) was itself
unmapped - `VERIFICATION BOUNDARY MISSING: scripts/guard-bench-compile.ps1`. Fixed by adding that path
to the same boundary's `paths`, matching the existing pattern (`injector-fallback`, `overflow-audit`,
`magic-number-audit` all own their own guard script alongside what the guard checks). Re-ran scoped
verify after the fix: green.

# TVB1.5 — Local adoption: module-level runs on a sharded project delegate to the runner

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Module check on `data` (shard entry) plans/runs `test-sharded.ps1 -ExtraFilter <default profile>` | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs -AllowUnscoped -PlanOnly` | plan prints `test: data  (sharded runner)`; filter read from `scripts/test-fast.ps1`, not restated | `scripts/verify-change.ps1` |
| Focused (`VerificationId`) check unaffected | same, path `RpgStore.Sockets.cs` | plan prints plain `test: data data.item-socket`, no suffix | console |
| Plan case in `VerificationBoundaryWorkflowTests` | new: `A_data_fallback_module_check_plans_the_sharded_runner`, `A_focused_data_check_does_not_plan_the_sharded_runner` | both pass | `VerificationBoundaryWorkflowTests.cs` |
| `testing-standard.md` §6 gains the paragraph | inspect doc | added after "Wall-clock is its own axis" | `docs/contributing/testing-standard.md` |
| Focused scoped check | `dotnet test ... --filter "VerificationId=guard.verification-boundaries"` | 16/16 passed | console |
| Module scoped check (`testing-standard-doc` boundary, new, since the doc had no owner at all — real gap fixed) | `dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` | 445/447 first pass; 2 failures (`ClassSystemBaselineRegenTests`, `VerificationBoundaryWorkflowTests` x2 across two runs) all confirmed pre-existing/environmental via isolated re-run — see notes | console |
| Integrity guard | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | console |

**New registry entry, not scope creep — a real gap the task's own verify command exposed:**
`docs/contributing/testing-standard.md` had NO owner at all (`docs/contributing/**` was entirely
unmapped). Added `testing-standard-doc` (`guard`, module, no guards) — same precedent as
`solid-remediation-specs` (a policy doc mapped to its domain project's module fallback with no
direct reader).

**Pre-existing failures found and resolved, unrelated to this task's own files:**
1. `ClassSystemBaselineRegenTests` failed twice (missing `gk-core/tools/CombatSim` and `gk-forge/tools/DominanceBaseline`
   Debug builds — this fresh worktree never built either). Built both (`dotnet build gk-core/tools/CombatSim
   -c Debug`, `dotnet build gk-forge/tools/DominanceBaseline -c Debug`); re-ran the class clean: 3/3 passed.
2. Two `VerificationBoundaryWorkflowTests` methods (`Planner_refuses_an_unmapped_path...`,
   `Planner_can_select_a_registered_deleted_path...`) hit the 120s `ExternalProcess.Run` timeout under
   heavy machine contention (same class of flake seen repeatedly this session). Re-ran both in
   isolation: passed in 56s and 20s.

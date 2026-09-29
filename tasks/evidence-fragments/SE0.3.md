# SE0.3 — Map the new files and add the DESIGN-GATE line

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `verify-change` resolves both new files | `.\scripts\verify-change.ps1 -Paths gk-core/scripts/enforcement-registry.v1.json,gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs,gk-core/tests/FusionRpg.Guard.Tests/EnforcementMap.cs -Session summoner-convergence-lane-d-20260919 -PlanOnly -Format json` | exit 0; each path → `enforcement-registry (focused)` with `VerificationId guard.enforcement-registry` | gk-core/scripts/verification-boundaries.v1.json |
| `DESIGN-GATE.md` §5 has the new rule | read `docs/DESIGN-GATE.md:242-243` | "A new rule has a registry row: a guard, or an `unguardableReason`" present in the §5 checklist block | docs/DESIGN-GATE.md |
| the registry integrity guard still accepts the file | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | — |
| `docs/DESIGN-GATE.md` deliberately stays unmapped | not mapped — `VerificationBoundaryWorkflowTests.Planner_refuses_an_unmapped_path_instead_of_selecting_a_broad_suite` names it as the canonical unmapped path | no boundary added for it | — |

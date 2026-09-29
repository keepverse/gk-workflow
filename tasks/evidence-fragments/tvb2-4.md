# TVB2.4 — Guard-only boundaries (C5, script half)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `project` optional iff `guards` non-empty; planner emits no test check for such a path | `verify-change.ps1`'s check-building loop `continue`s past the test check when `$entry.project` is empty | new | `scripts/verify-change.ps1` |
| A boundary with neither `project` nor `guards` fails the guard | `guard-verification-boundaries.py`'s per-boundary loop | `"boundary needs a project or at least one guard: <id>"` | `gk-core/scripts/guard-verification-boundaries.py` |
| T7 (guard-only boundary plans the guard, no test check) | `T7_a_guard_only_boundary_plans_the_guard_and_no_test_check` | passed — plan shows `guard: fake-guard`, no `test:` line | `VerificationBoundaryWorkflowTests.cs` |
| T8 (neither project nor guards -> rejected) | `T8_a_boundary_with_neither_project_nor_guards_is_rejected` | passed | same |
| Real registry unaffected (no guard-only boundary exists yet — `bench` lands at TVB2.5) | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | console |
| Full class green | `dotnet test ... --filter VerificationBoundaryWorkflowTests` | 31/31 | console |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths scripts/verify-change.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session summoner-convergence-lane-d2-20260919` | 31/31 passed | plan resolved `guard-verification-boundary-tests` |

**No change to `gk-core/scripts/verification-boundaries.v1.json`** — machinery only, additive/minimal per the
coordinator's note about lane D's concurrent SE work on that file. The real `bench` guard-only
boundary lands in TVB2.5.

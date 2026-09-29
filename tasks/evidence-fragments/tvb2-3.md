# TVB2.3 — Project groups (C7)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A `projects` value may be an array of `.csproj` — module runs every member, focused runs only trait-holding members | new `Get-ProjectMembers`/`Test-ProjectHasTrait` (lib) wired into both scripts; `verify-change.ps1`'s checks gain a `targets` field resolved once, printed and executed from the same value | new | `scripts/lib/VerificationBoundaries.ps1`, `scripts/verify-change.ps1` |
| Guard: members exist, flat (no group in a group), `.csproj` only, group-level `verificationId` matches ≥1 member | project-validation loop + trait-check loop rewritten for array values | new | `gk-core/scripts/guard-verification-boundaries.py` |
| T10 (focused on group -> only the trait-holding member) | `T10_a_focused_boundary_on_a_group_plans_only_the_member_holding_the_trait` | passed — plan names `FakeB.csproj`, not `FakeA.csproj` | `VerificationBoundaryWorkflowTests.cs` |
| T11 (module on group -> every member) | `T11_a_module_boundary_on_a_group_plans_every_member` | passed — plan names both `FakeA.csproj` and `FakeB.csproj` | same |
| T12 (nested group / non-.csproj member) | `T12_a_malformed_group_member_is_rejected` (2 cases: nested array, pytest-shaped object) | both passed | same |
| Real registry unaffected (no groups exist yet) | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | console |
| Full class green | `dotnet test ... --filter VerificationBoundaryWorkflowTests` | 29/29 | console |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,scripts/verify-change.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session summoner-convergence-lane-d2-20260919` | 29/29 passed | plan resolved `guard-verification-boundary-tests` |

**No change to `gk-core/scripts/verification-boundaries.v1.json`** — this task adds the MACHINERY only; no
group exists in the real registry yet (`core` becomes one at TVB5.6, once the split needs it). Kept
deliberately minimal per the coordinator's note that lane D's SE work also edits that file.

T10/T11's fixture required real copies of `verify-change.ps1`, `guard-verification-boundaries.py`
and the lib under a synthetic `-Root` (that script resolves its own tooling from `-Root`, not from
this test file's location) — proving the shipped files work against an external tree, not a
re-implementation.

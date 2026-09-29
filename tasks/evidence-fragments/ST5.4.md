# ST5.4 — the `action-base` row of the version-agreement guard

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `TuningVersionAgreement("action-base")` passes with `Program.cs` and `RpgHost.cs` on one version | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningVersionAgreement"` | **7/7 pass**, the row included. Both readers the acceptance names name the same version, v2: `gk-core/src/FusionRpg.Server/Program.cs:263` and `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:237`, and nothing else in `src/` or `gk-forge/tools/seedsmith/seedsmith/` names `action-base` at all. | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |
| …and fails on a planted mismatch | same command | **Passes.** `The_action_base_row_fails_on_a_planted_mismatch` points the SAME assertion at a fixture that starts at one version, adds a second reader on `action-base.v1.json` next to `v2`, and requires it to go red — `Assert.ThrowsAny<XunitException>` with the message naming the domain and `1, 2`. Without this, a green row would prove nothing about the tree it reads. | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |
| The theory is the parameterised one the contract names | code read | `[Theory] TuningVersionAgreement(domain)` over `MemberData(nameof(AgreedDomains))`, which holds `action-base` in this commit. ST5.2 appends `action-rungs` to the same list when every reader moves to v4 — it cannot be added earlier: `action-rungs` currently disagrees (v1 in `Program.cs:256`, `RpgHost.cs:227`, `pool.py:31,85`; v3 in the two generators). | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |
| Boundary | `dotnet test gk-core/tests/FusionRpg.Guard.Tests` (module) | **390 passed / 3 failed**, the three documented pre-existing reds (two `VerificationBoundaryWorkflowTests` boundary rows, `StubRegisterTests.Every_row_points_at_a_file_that_exists`). No new red. | tasks/summoner-convergence-ledger.jsonl |

## Shape note

The assertion was factored into `AssertAgrees(roots, domain)` so the real-tree row and the
planted-mismatch proof exercise the identical code — the row is not a bespoke string comparison that
could drift from the thing the probe tests, and the probe does not re-implement the scan.

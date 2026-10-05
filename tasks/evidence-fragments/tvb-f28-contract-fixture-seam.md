# TVB-F28 — a `gk-core/src/FusionRpg.Contracts/**` change now selects the E2E contract-fixture check

**Shape (d), a `seam`.** The row named three shapes and ruled the additive ones out; all three missed
that `verify-change.ps1`'s `VERIFICATION BOUNDARY AMBIGUOUS` throw (`:115`) is reached only for **`owner`**
boundaries (`:112` filters `kind -eq 'owner'`) — the seam loop (`:119-121`) appends with no ambiguity
check, so a seam on the owner's own paths is additive by construction and `level` derives to `seam`
(`scripts/lib/VerificationBoundaries.ps1:231`). Landed: `[Trait("VerificationId", "e2e.contract-fixture")]`
at `gk-core/tests/FusionRpg.E2E.Tests/ContractFixtureTests.cs:18`, and boundary `contracts-fixture-seam` appended
last in `gk-core/scripts/verification-boundaries.v1.json:6251-6261` — a pure append (6098 -> 6109 lines, no
existing line shifts, so no registry citation moves).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| a Contracts DTO path plans the E2E check *and* keeps the `core` run | `pwsh -NoProfile -File scripts/verify-change.ps1 -PlanOnly -AllowUnscoped -Paths gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs` | `-> contracts-fallback (module)` + `-> contracts-fixture-seam (seam)`; `test: core [68 csproj]` + `test: e2e e2e.contract-fixture` | — |
| every Contracts path picks it up, incl. the narrower owners | same, `-Paths gk-core/src/FusionRpg.Contracts/NotificationDtos.cs src/FusionRpg.Contracts/Narrative/StoryBeatDtos.cs` | both plan `contracts-fixture-seam (seam)` beside `notify-contracts` / `contracts-narrative` | — |
| the trait selects exactly the catching tests | `dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj -c Release --filter "VerificationId=e2e.contract-fixture"` | `Failed: 2, Passed: 0, Skipped: 0, Total: 2` — both `ContractFixtureTests` | — |
| the two failures predate the trait | same project before the edit: `--filter "FullyQualifiedName~ContractFixtureTests"` | `Failed: 2, Passed: 0, Skipped: 0, Total: 2` — `commander-list.json:6` `"Crazy Dave"` vs live `"Garden Keeper"`; `unique-actor.json` has no `empireId` | — |
| registry still validates | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | — |
| changed paths verify | `pwsh -NoProfile -File scripts/verify-change.ps1 -Session tvb58 -Paths gk-core/tests/FusionRpg.E2E.Tests/ContractFixtureTests.cs gk-core/scripts/verification-boundaries.v1.json` | `guard: test-substrate` OK; `test: guard guard.verification-boundaries` `Failed: 0, Passed: 57` (9m22s); `test: e2e` `Failed: 3, Passed: 273, Skipped: 0, Total: 276` (2m47s) — the same three pre-existing fixtures | — |
| Guard suite | `dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release --filter "FullyQualifiedName~VerificationBoundary\|FullyQualifiedName~CoreTestProjectPolicy"` | `Failed: 1, Passed: 62, Skipped: 0, Total: 63` (12m50s); the one is `T15_the_real_bench_boundary_plans_its_compile_guard_and_no_test_check` (`verification-boundary script timed out`, 2 m), green alone in 1 m 15 s | — |
| ci tier | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | `GUARDS OK - 25 guard(s) run, 0 red` | — |

**Row stays open — blocker named exactly.** The seam's focused check is red until
`gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json:6` (`ip-censor`) and `.../unique-actor.json`
(`summoner-convergence`, SE4.31) are re-blessed: TVB-F25's two fixtures, already routed. CI is red on
these already (`ci.yml:333` runs the E2E project with an exit check), so the seam moves an integration red
to a local one; it does not create one.

**Scope of the proof, stated rather than implied.** The seam's *selection* is proven by the two plan
readings and the trait's own `--filter` run above; its *execution through `verify-change`* on a Contracts
path was not run, because that plan also names the 68-project `core` group and the only session records
covering `gk-core/src/FusionRpg.Contracts/**` are other programs' (this lane's `test-verification-boundary-3`
record does not exist, so `-Session` cannot be satisfied for a Contracts path; `-AllowUnscoped` is
`-PlanOnly`-shaped). `verify-change.ps1:112-121` builds the same focused `test` check for a seam as for an
owner, and the `--filter` run is that check's command.

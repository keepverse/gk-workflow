# SP1.6 — `AptitudeAllocation.ShareWithinScope` (a pure addition)

Spec: `species-layer-projector` / `species-layer-delivery` step 6.1 prerequisite. Pure addition beside
`AptitudeAllocation`'s existing `Share`/`TotalForScope` — no existing reader touched.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ShareWithinScope(scope, aptitudeId)` divides by that scope's own total | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudeAllocation" --nologo` | pass — `ShareWithinScope_dividesByThatScopesOwnTotal_neverTheGrandTotal`, `ShareWithinScope_splitsCorrectlyWhenOneScopeFundsTwoAptitudes` | `AptitudeAllocation.cs` |
| An empty scope gives 0 | same | pass — `ShareWithinScope_emptyScopeReadsZero_neverOneTwelfth` | — |
| For a single-scope allocation it equals `Share` | same | pass — `ShareWithinScope_equalsShare_forASingleScopeAllocation` | — |
| No existing reader changes | same | pass — full file green (23/23), including the pre-existing `ScopesSumBeforeShare`/`ExactAtOneBillion`/`OverflowThrowsNeverClamps` facts unchanged; `ShareWithinScope_neverChangesShareOrTotalForScope` asserts `Share`/`TotalForScope` read the same as before beside the new method | `AptitudeAllocationTests.cs` |

# SP3.4 — `ProjectEmpire` + `Resolve`: exact parity with `AptitudeResolver` for a species-only allocation

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `EffectiveKMilli` and `sharePowMilli` rounding are single shared functions both resolvers call | code edit | done | `AptitudeResolver.EffectiveKMilli` → `internal`; `AptitudeReadFunctions.SharePowMilli` extracted (new public function, `Magnitude` calls it) |
| `ProjectedLayerRow`/`LayerValue` (`Fixed`, `LadderMicro`) exist | code | done | `gk-core/src/FusionRpg.Core/Creatures/Layers/ProjectedLayerRow.cs` (new) |
| `SpeciesLayerProjector.Revision = 1` carries its structural comment | code | done | `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesLayerProjector.cs` (new) |
| Parity over a grid (single share, mixed shares, empty) and Θ values, incl. one where the old kMicro path overflowed | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector\|FullyQualifiedName~AptitudeResolver"` | **27/27 passed** | `gk-core/tests/FusionRpg.Core.Tests/Creatures/Layers/SpeciesLayerProjectorTests.cs` (new) |
| An empty allocation projects zero rows | same run, `EmptyAllocation_projectsZeroRows_neverZeroValuedRows` | pass | same file |
| Core builds clean | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj` | 0 errors | build log |

## What shipped

- `AptitudeResolver.EffectiveKMilli`: `private static` → `internal static`, with a doc comment naming
  the reason (spec rule 1: "internal-visible, not copied"). No behavior change — still called the
  same way from `AptitudeResolver.Resolve` itself.
- `AptitudeReadFunctions.SharePowMilli(share, shareExponentMilli)`: new public function, the
  `share^gamma` → per-mille rounding step extracted verbatim out of `Magnitude`. `Magnitude` now
  calls it instead of inlining the same three lines — one implementation, not two. (Validation order
  changed slightly: `Magnitude` no longer calls `ValidateShare` directly before its `kMilli` check —
  `SharePowMilli` validates share and the exponent internally. All 62
  `AptitudeReadFunctions|AptitudeResolver|LadderScale` tests still pass, confirming no test depends on
  the old single-bad-input-at-a-time exception ordering.)
- `gk-core/src/FusionRpg.Core/Creatures/Layers/ProjectedLayerRow.cs` (new): `LayerValue.Fixed`/`LadderMicro`,
  `ProjectedLayerRow(Channel, Op, Value, SourceId)`.
- `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesLayerProjector.cs` (new): `Revision = 1` (structural,
  bumped only when the projection's arithmetic changes), `ProjectEmpire` (2b: one row per funded
  aptitude edge in a species-only allocation, calling `AptitudeResolver.EffectiveKMilli` and
  `AptitudeReadFunctions.SharePowMilli`/`.Contest` — no re-typed math) and `Resolve` (turns projected
  rows into `DerivedModifier`s at a reader's own `P(Θ)`). `ProjectBase`/`ProjectPlayerMod`/`ToContainer`
  are NOT in this task — SP3.5/SP3.7 add them to the same file.

## The parity proof

`SpeciesLayerProjectorTests.cs`'s `AssertParity` helper runs the SAME allocation and Θ through both
`AptitudeResolver.Resolve` and `SpeciesLayerProjector.Resolve(ProjectEmpire(...), ...)`, and asserts
every resolved channel/op/value matches to 9 decimal places (only the SourceId differs, asserted
`NotEqual` and `species-empire:`-prefixed). Covered: single share (Might only), mixed shares (Might +
Fortitude, exercising the mitigation-scale-dial branch of `EffectiveKMilli` since `combat.defense` is
a mitigation family), theta=1/1000/near-ladder-ceiling, a Contest edge (Θ-free, proven not to move
across widely different Θ) and a Magnitude edge (proven to grow with Θ), an oversized coefficient that
throws `OverflowException` rather than wrapping, an unfunded aptitude contributing nothing, and null-
argument guards. Every allocation in the grid holds points in `AllocationScope.CreatureType` alone —
`AptitudeAllocation.ShareWithinScope`'s own doc comment: "For an allocation that holds points in
exactly one scope, this equals `Share` by construction" — which is exactly what makes the parity claim
true rather than coincidental.

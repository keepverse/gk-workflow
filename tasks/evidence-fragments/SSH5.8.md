# SSH5.8 — circuits in the one evaluator; `SocketCircuitSize = 4`; the two parser rules

## What changed

- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs` — `SocketLimits.SocketCircuitSize = 4`
  (structural, not tunable: it decides whether a recipe is readable, and a Strain consumes exactly one
  circuit). `Parse` now throws when `strainSplice.ingredientCount != SocketCircuitSize`, and the
  resonance-threshold bound moved from `structuralCeiling` to `SocketCircuitSize` (so a `v2` ceiling of
  8 cannot admit a threshold no single circuit can hold).
- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs` — `CombinationResult` gains `int Circuit = 0`.
- `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs` — the fill is grouped by
  `socketIndex / SocketCircuitSize` and the ONE ordered pass runs per circuit (extracted to
  `EvaluateCircuit`, never a second evaluator): at most one Strain/Splice identity per circuit, then
  Pure, Ring, Eclipse, Diversity over that circuit's own inserts. No cross-circuit recipe or resonance.
  A host with ≤ 4 sockets is one circuit, so v1 behaviour is unchanged.
- Tests: the four circuit tests in `CombinationEvaluatorTests.cs`; the two parser-rule tests in
  `SocketGeometryTests.cs`; `Affinity_never_scales_an_inserts_magnitude`'s reflection set now names
  `Circuit` (the result shape changed by design).

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| four circuit tests pass | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationEvaluator\|FullyQualifiedName~SocketGeometry\|FullyQualifiedName~ComboMatcher"` | 71 passed, 0 failed |
| v1 still loads, behaviour unchanged (one circuit) | same run | green |
| the two parser rules throw | same run | `A_resonance_threshold_above_one_circuit_is_refused_at_load`, `An_ingredient_count_that_is_not_the_circuit_size_is_refused_at_load` |
| downstream consumers unaffected under v1 | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemCardStore\|FullyQualifiedName~ItemSocketStore"`; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints\|FullyQualifiedName~ItemCardEndpoints"` | 34 passed; 37 passed |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

# SSH4.1 — R12: delete the C# per-actor combination cap

## What changed

- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs` — `SocketCombinationCap` (the `Apply`/
  `Suppressed` pair and `ActorCombination`) deleted; nothing in `src/` called it.
- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs` — `MaxCombosPerActor` property, its constructor
  parameter, and the `Positive(root, "maxCombosPerActor")` read removed. An unknown key is ignored,
  so v1 (key present) still loads.
- Tests: the two cap tests deleted from `CombinationEvaluatorTests.cs`; the cap test deleted from
  `SocketGeometryTests.cs`; only the cap lines removed from `StrainSpliceGridTests.cs`. The C# mirror
  of `SOCKETS_OWNED_KEYS` (`StrainSpliceGridTests.cs:236`) keeps `maxCombosPerActor`, as does the
  Python list — SSH4.2 owns the Python field/summary removal.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| cap class + tuning field + key read gone | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry\|FullyQualifiedName~CombinationEvaluator\|FullyQualifiedName~StrainSpliceGrid"` | 73 passed, 0 failed |
| `socket_tuning_parses_without_max_combos_per_actor` | same run | v1 parses; a fixture with the key and its Note removed parses |
| no `SocketCombinationCap` / `MaxCombosPerActor` survives | `grep -rn "SocketCombinationCap\|MaxCombosPerActor" src/ tests/` | no matches |

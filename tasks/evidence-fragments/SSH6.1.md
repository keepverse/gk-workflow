# SSH6.1 — circuit-aware geometry reading on both ports, with a parity test

## What changed

- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketGeometry.cs` — `GeometricCombinationCeiling(tuning, roles)`
  = `Σ floor(ceiling(r) / SocketLimits.SocketCircuitSize)` (a six-socket role is ONE circuit plus a
  remainder, so it counts once), and `ReachableCombinationCeiling(tuning, recipes)` = the same sum
  over the roles at least one recipe admits (an unpinned recipe admits every role). Readings only —
  never compared to a cap.
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py` — `CIRCUIT_SIZE = 4` (the Python mirror
  of the C# const), `geometric_combo_ceiling()` now the circuit sum over the offered roles, and
  `reachable_combo_ceiling(admitted_roles)`.
- `tests/FusionRpg.Core.Tests/Items/SocketGeometryTests.cs` — `Geometric_ceiling_counts_complete_circuits_not_roles`.
- `gk-forge/tools/seedsmith/tests/test_combogen.py` — `python_and_csharp_readings_agree_on_the_shipped_tuning`
  (reads the C# `SocketCircuitSize` from its source, asserts `CIRCUIT_SIZE` matches, then recomputes
  both readings over the shipped v2 file).

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| circuit count, not role count (8→2, 6→1, 4→1, 2→0) | `dotnet test tests.FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry"` | 32 passed, 0 failed |
| geometry parity on the shipped file | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q` | 26 passed, 0 failed |
| neither compared to a cap | same runs | the reading is returned and printed; no caller compares it |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH (25 citations re-anchored for the tuning.py shifts) |

## NOT proved / still open

- `reachableCeiling` is exercised with fixture recipes; the real catalog's `enabled` predicate is
  `recipe-import`'s accepted set (SSH3.3) — this row reads a recipe list, not the DB.
- The report that prints the reading is SSH6.4; the run summary's `geometricCombosPerActor` key still
  uses `len(host_roles)` (out of this row's file set — SSH6.4/SSH6.8 own the report surface).

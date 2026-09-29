# SSH6.5 — `no_combination_count_cap_exists`: the R12 source scan

**DONE 2026-09-22 (lane `ssh29`).** `gk-core/tests/FusionRpg.Guard.Tests/ComboCountCapGuardTests.cs` (new) carries
the scan. The path was recorded as pipeline-protected by an earlier lane; the write was NOT hook-blocked,
so the row closes here instead of riding `tvb58`.

| Criterion | Command | Result |
|---|---|---|
| the scan finds no live identifier | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ComboCountCap"` | **2 passed / 0** |
| identifiers | (in the guard) | `MaxCombosPerActor`, `maxCombosPerActor`, `max_combos_per_actor`, `SocketCombinationCap` over `src/`, `tools/`, `tests/` (`*.cs` + `*.py`, `bin`/`obj`/dot-dirs skipped, comment lines skipped) |
| the allowlist cannot grow into a licence | (in the guard) | a listed file with ZERO hits FAILS the scan ("remove them from the allowlist"), so each entry is re-proved every run |
| nothing under `src/` names it | (the scan would flag it) | zero `src/` hits — no production reader survives |

Allowlist (each entry is a negative assertion that must name what it excludes):
`ComboCountCapGuardTests.cs` itself · `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`
(`SOCKETS_OWNED_KEYS`) · `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs` (its C# mirror
— the earlier note wrote `gk-core/tests/FusionRpg.Core.Tests/...`, which does not exist) ·
`gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketGeometryTests.cs` (the R12 absence test) ·
`gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` (its Python twin). Four of five files, not the two the
acceptance names — the erratum SSH6.5 requested, now discharged by writing it.

## Not proved / open

- The v1 data file needs no entry: it is data, outside the scan roots, and the tuning's own
  `SOCKETS_OWNED_KEYS` is what keeps a future reader from loading the key.

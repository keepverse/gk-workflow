# SP2.1 — `LadderScale.Micro`; the aptitude magnitude read uses it, byte-identical

Spec: `ladder-scale-parity` (module 2, map C6). Built directly from the spec's own code sample.

`AptitudeReadFunctions.Magnitude` now computes `kMicro = checked(kMilli * sharePowMilli)` (a plain
`checked long` multiply — both factors are bounded per-mille quantities, never near `long`'s ceiling)
and returns `LadderScale.Micro(kMicro, pTheta)` — the same two-step arithmetic the previous
single-expression `decimal` computation performed, now shared with `AtomCompiler`'s projected-atom
path (SP2.2) instead of duplicated inline.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `LadderScale.Micro(kMicro, pTheta)` widens to `decimal`, rounds once away from zero, throws on negative input or past `long`; no wrap, no clamp | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LadderScale" --nologo` | pass 15/15 | `LadderScale.cs` |
| Over a grid including the edge where `kMicro × pTheta > long.MaxValue` but the quotient fits, `AptitudeReadFunctions.Magnitude` equals `LadderScale.Micro(kMilli * sharePowMilli, pTheta)`; the aptitude path is unchanged | same run | pass — `Magnitude_equals_LadderScale_over_the_grid_including_the_overflow_edge` (5 rows, including `kMilli=long.MaxValue/1_000_000` which pushes the raw product past `long.MaxValue` while the true quotient still fits); `Both_overflow_at_the_same_point` proves the two entry points throw at the same true boundary | `LadderScaleTests.cs` |
| No regression: the pre-existing `AptitudeReadFunctionsTests.cs` | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudeReadFunctions" --nologo` | pass 31/31, unchanged | — |
| `audit-overflow.py` shows no new finding | `python gk-core/scripts/audit-overflow.py --targets A3`; `python gk-core/scripts/audit-overflow.py \| grep -i "LadderScale\|AptitudeReadFunctions"` | pass — exit 0, zero findings in either touched file | — |
| Build | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --nologo` | Build succeeded, 0 errors | — |

# TVB1.3 — Measure 2 vs 4 shards; record `_meta.measured`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| 2-shard total wall (build+test, stopwatch) | `.\scripts\test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj` | 98.49s (build 1.7s + test ~96-98s) | `_meta.measured` |
| 4-shard total wall, same box, back-to-back | trial manifest `a`(Items/Delve)+`b`(Actions)+`c`(CorpseCache/PassiveTree/CargoCommands)+`rest` | 86.45s (build 5.6s + test ~80.1-80.2s) | `_meta.measured` |
| Manifest keeps the faster count | edited `gk-core/scripts/test-shards.v1.json` to the 4-shard shape | 4 kept (~12% faster) | `gk-core/scripts/test-shards.v1.json` |
| No test asserts shard count/walls/tests-per-shard | inspect `TestShardManifestTests.cs` | unchanged — loops over whatever the manifest holds | same file |
| H-T1–H-T4, H-T6 still green against the new shape | `dotnet test tests\FusionRpg.Guard.Tests -c Release --no-build --filter "FullyQualifiedName~TestShardManifestTests"` | 11/11 passed | console |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths gk-core/scripts/test-shards.v1.json -Session summoner-convergence-lane-d2-20260919` | 11/11 passed | plan resolved `test-shards-guard` (focused) |

**Machine-load caveat (readings, never asserted):** both runs had 26-30 concurrent `dotnet.exe`
processes from other sessions (not idle). The two measurements were taken sequentially, same
`--no-build` assembly, seconds apart, so they are directly comparable to each other even though
neither is an absolute/idle-box number.

# TVB1.2 — `scripts/test-sharded.ps1` runner + H-T6 + completeness proof

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Runner: build once, per-shard process, per-shard results dir, overlap+empty-shard checks, throwing-delete `finally` | inspect `scripts/test-sharded.ps1` | matches H2 | new file |
| H-T1–H-T4, H-T6 green (planted TRX, no `dotnet test`) | `dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~TestShardManifestTests"` | 11/11 passed | `TestShardManifestTests.cs` |
| Real sharded run, `data` project | `.\scripts\test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj` | shard a: 429 tests exit 0; shard rest: 1169 tests exit 1 (one pre-existing failure, see note) | console |
| **Completeness proof (sets, not counts)** | union(a,rest) vs one unsharded run, same TRX-id scheme | union=1598, unsharded=1598, 0 only-in-union, 0 only-in-unsharded, pairwise intersection(a,rest)=0 | `COMPLETENESS PROOF: PASS` |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths scripts/test-sharded.ps1,gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs -Session summoner-convergence-lane-d2-20260919` | 11/11 passed | plan resolved `test-shards-guard` (focused) |

**Pre-existing failure, not caused here:** both the sharded (`rest`) and unsharded runs fail exactly
one test, `CreatureSpeciesImportCliTests.A_real_import_against_the_real_committed_tree_succeeds_and_writes_a_real_store`
— `gk-data/packs/fusion/data/generated/creatures` has 11 species stale against their generator, unrelated to sharding
(same failure, same message, in both sharded and unsharded runs; confirmed pre-existing, out of TVB
scope — generated data is never hand-edited, and this is another program's content).

**Bug found and fixed en route:** a default parameter value `$Root = (Resolve-Path (Join-Path
$PSScriptRoot ".."))...` throws "empty string" here whenever a MANDATORY parameter precedes it in the
same `param()` block (confirmed via isolated repro on this machine's PowerShell) — `$PSScriptRoot` is
not yet populated at default-value-evaluation time in that case. Fixed by resolving `$Root` in the
script body instead of as a param default (script docstring explains why).

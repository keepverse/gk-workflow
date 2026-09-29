# TVB1.1 — Shard manifest + `TestShardManifestTests` H-T1–H-T4

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Manifest shape (2 shards, one remainder, `data` project) | inspect `gk-core/scripts/test-shards.v1.json` | matches spec H1 example verbatim | `gk-core/scripts/test-shards.v1.json` |
| H-T1–H-T4 green | `dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~TestShardManifestTests"` | 8/8 passed | `TestShardManifestTests.cs` |
| Owner boundary added, `guard.test-shards` VerificationId | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | `gk-core/scripts/verification-boundaries.v1.json` |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths gk-core/scripts/test-shards.v1.json,gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session summoner-convergence-lane-d2-20260919` | 8/8 then 14/14 passed | plan resolved both to `guard` project |

Note: a first attempt at the scoped verify timed out inside `VerificationBoundaryWorkflowTests.Planner_selects_only_the_socket_group_for_source_and_its_test` (unrelated pre-existing test, machine had 21 concurrent `dotnet.exe` processes from other sessions). Isolated re-run of that one test passed in 24s; the full scoped verify re-run passed clean.

# TVB-F25 — the E2E host's missing `LeadNamesHub` configure

Found by TVB5.9's `test-fast.ps1 -AllDefault`: the E2E project failed in its class-fixture constructor,
which the row for TVB5.9 would otherwise have reported only as "the profile is red".

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the throw | `dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` (before) | `Failed: 237, Passed: 37, Skipped: 0, Total: 274, Duration: 2 s` — `Class fixture type 'FusionRpg.E2E.Tests.RpgApiFactory' threw in its constructor` / `LeadNamesHub.Configure(...) has not run` | this fragment |
| the call site | stack read | `RpgApiFactory.cs:117` → `RpgStore.cs:4201` → `:4218` → `LeadNames.cs:319` | — |
| after the fix | same command | `Failed: 2, Passed: 272, Skipped: 0, Total: 274, Duration: 2 m 40 s` | this fragment |
| the 2 survivors | same run | `ContractFixtureTests.Commander_list_fixture_matches_live_dto` (fixture `"Crazy Dave"`, live `"Garden Keeper"`); `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening` (fixture `b41ce3ef4c7c…`, live `0f685a162409…`) | — |
| both survivor files | `gk-web/web/fusion-rpg-web/**` | outside this lane's fence and unmapped (TVB-F1) — filed as TVB-F25 | TVB-F25 |
| `verify-change` on the changed file | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs') -Session tvb58` | `e2e-tests-fallback (module)`; `Failed: 3, Passed: 271, Total: 274` — the 2 fixture reds plus `CatalogAndStressE2ETests.Fps120_second_9600_events`, which PASSED in the direct run above and failed only here (a load-sensitive wall-clock test, observed not diagnosed) | this fragment |

The fix is one `LeadNamesHub.Configure(...)` call in
`gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs`, mirroring the Core/Data bootstraps and the
call the same file already makes for the two SE4.12 registries, for the same reason it records there.
The two survivors are **web** fixtures; no lane of this program can re-bless them, so TVB5.9's
"`-AllDefault` green once" acceptance is blocked on TVB-F25's routing, not on further work here.

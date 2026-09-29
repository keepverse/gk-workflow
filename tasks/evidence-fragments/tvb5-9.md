# TVB5.9 — split close: the `Csc` reading, the Core group, and the one acceptance that cannot pass

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Csc`, one tucked-in subsystem | `dotnet build gk-core/tests/FusionRpg.Core.Lawn.Tests -c Release -t:Rebuild -clp:PerformanceSummary` | `2,448 ms  Csc  3 calls`, `Time Elapsed 00:00:03.92` | `docs/architecture/test-verification-boundary-ideal.md` |
| `Csc`, the residual | `dotnet build gk-core/tests/FusionRpg.Core.Tests -c Release -t:Rebuild -clp:PerformanceSummary` | `8,680 ms  Csc  14 calls`, `Time Elapsed 00:00:09.27` | same |
| ratio | the two readings | ~3.5× `Csc`, ~2.4× wall — the 2026-09-22 ratio, on a residual that has given up more files since | — |
| Core group green | `scripts/test-fast.ps1 -Project <every member of the core group>` (68 csprojs, default profile) | `Default test profile OK` in each of 4 chunks; **68 project runs, 0 failures, 15,836 tests** (residual alone `Passed: 9600`) | this fragment |
| the four legs, fresh at `487400ce5` | `scripts/test-fast.ps1 -Project <leg>` per leg | **Data `Passed: 1766, Failed: 0` (11m46s, EXIT=0)**; **Server `Passed: 826, Failed: 0` (2m44s, EXIT=0)**; **E2E `Failed: 2, Passed: 272` (2m36s)**; Core group `Default test profile OK` | this fragment |
| the E2E leg alone, re-read at `a6e84755a` | `scripts/test-fast.ps1 -Project gk-core/tests/FusionRpg.E2E.Tests` | **`Failed: 3, Passed: 271, Skipped: 0, Total: 274`** (2m14s): the two web goldens (fixture `"Crazy Dave"` vs live `"Garden Keeper"`; fixture `b41ce3ef…` vs live `0f685a16…`) plus `RS-CF3`'s `RpgSimInProcHostTests.Two_consecutive_runs…` (`ok=True` then `ok=False` on the same input) | this fragment |
| §6 names the group | `docs/contributing/testing-standard.md` | already there at `:139-145` (`core` group, the residual plus every moved project, TVB-F17 noted) | — |
| `-AllDefault` green once | `scripts/test-fast.ps1 -AllDefault` | **not achievable from this tip** — every leg is green except `gk-core/tests/FusionRpg.E2E.Tests`, which is red for exactly TVB-F25's two stale web fixtures (`ContractFixtureTests.Commander_list_fixture_matches_live_dto`, `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening`) | TVB-F25 |

Two long calls were cut by the harness mid-run, so the Core group was measured in four chunks; each chunk's
own summary line is the reading, and the chunk boundaries are a harness artefact, not a test boundary. The
three non-Core legs were then re-measured one command each at `487400ce5`, after every change this lane made
to them (the Data bootstrap, the E2E bootstrap), so the table above is current rather than inherited.
The `-AllDefault` acceptance is blocked on **TVB-F25**: `gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json:6`
(`"Crazy Dave"` vs the live `"Garden Keeper"`) and
`gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json:4` (`b41ce3ef4c7c…` vs the live
`0f685a162409…`). Neither path is in this program's fence and, per TVB-F1, neither has an owner boundary,
so no lane here can re-bless them; re-checked on 2026-09-23, the main checkout (`features/mega-merge` @
`8958d88d6`) still carries both stale goldens, so the re-bless is owed and nowhere done. A second,
occasional reason is recorded on the row: the profile is
load-fragile (`RpgSimInProcHostTests.Two_consecutive_runs_on_fresh_hosts…` failed in one of two consecutive
full E2E runs and passes alone), which is `RS-CF3` in `tasks/rpg-simulator-todo.md`.

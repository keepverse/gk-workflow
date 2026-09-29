# Evidence — rpg-simulator RS-CF3 (the E2E project's determinism, two causes fixed)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Row RS-CF3, whose "first job" was: capture the message for the two single-red runs
whose message was not captured, and say whether each is a real state defect or the contended machine.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| (b) item 1 — `FoundationE2ETests.Mid_match_switch_keeps_open_run_player` is a REAL race, now fixed | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~FoundationE2ETests"` | `Passed: 16, Failed: 0, Total: 16` (37 s) | `gk-core/tests/FusionRpg.E2E.Tests/FoundationE2ETests.cs` |
| (b) item 2 — the corpus's only RNG-dependent PRESENCE assertion is gone | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` | `Passed: 48, Failed: 0, Total: 48` (2 m 38 s) | `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` |
| The corpus rule is now the one the repo's own validation standard asks for | same run, and the full project run below | `expect.souls.ledger.reasons` is `allNonEmpty`, not `memberOf` — the membership list was measured failing with `kill` in it | same |
| The process-host lane survives its own mid-run reboot under load | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSimProcessHostTests" --logger "console;verbosity=detailed"` | `Total tests: 3, Passed: 3` (55.7 s); `process host: ok=True readings=7 digest=daa9df408054f32e…` and the same digest in-process; whole-reading comparison `MOVED at 94 pointer(s)` | `gk-core/tools/RpgSim/ProcessHost.cs` |
| The guard still reads the corpus the same way | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-sim-fabrication.ps1` | `scenarios=1 steps=36 reads=7 test.* steps=1 \| /api/sim handlers=60 (take RpgStore: 0) \| /api/test handlers=12 (take RpgStore: 11, allowlisted: 11)` — `SIM FABRICATION GUARD OK` | — |
| The whole project, as a reading (heavy load: 14 m 8 s) | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --no-build --nologo` | `Failed: 3, Passed: 285, Total: 288` — the three reds are RS-F21's two fixture drifts plus one **contention** budget (`CatalogAndStressE2ETests`), and the corpus tests are green | — |

**Cause of (b) item 1, read not guessed.** `FoundationE2ETests.cs:122` asserts
`run.GetProperty("plantsPlanted") == 1`, and a run's counters are applied by the `EventIngest` **drain**
(`RpgStore.cs:3394` — `UPDATE runs SET plants_planted = plants_planted + 1`), not by the route that accepted
the plant. That test's two **direct** `/api/runs` reads (`:117`, `:127`) therefore raced the drain — every
other test in the file reads through `Snapshot()`, which flushes (`SimEndpoints.cs:147`), which is exactly why
only this one flaked. Fixed by saying the settle out loud: a `Settle()` helper calling the runner's own
`SimSettler.WaitAsync(_http)`, whose contract already says a timeout is a FAILURE and never a silent pass.

**Cause of (b) item 2, and the honest limit.** Its message was never captured (the run used `--verbosity
quiet`), so the identification is by mechanism, not by log line: the corpus's only RNG-dependent *presence*
assertion was `expect.souls.ledger.expedition`, measured flaking **1 run in 2** on the merged tree, and it is
gone. The residual risk is named in the row rather than hidden: a different cause of that one red cannot be
excluded from the record, only from the present tree.

**The second attempt at that rule, and why the third is the right one.** `allNonEmpty` replaced a
`memberOf ["seed","summon","expedition","discovery","victory","defeat"]` list that I had added earlier the
same day. That list was measured failing in the full project run — `$.items[*].reason is
["expedition","defeat","kill","discovery"×10,"summon","seed"]` — because the battle's own **kill earn**
(`RpgStore.Souls.cs:139`, the activity-fact path) is a legitimate row this run produces. The lesson is the
repo's own: the reason set is `SoulEarnPolicy.Reasons`' ~24-member closed vocabulary, so a corpus enumerating
the members it expects is asserting a **population** (`validation-ssot.md`) and will keep going stale. The
rule the corpus can hold still is "every row names a reason", alongside the attribution, non-zero-delta and
seed-presence rules it already had.

**The boot budget, raised with its measurement.** `ProcessHostOptions.ReadyTimeout` is now 180 s (was 90 s):
the process-host comparison's mid-run **reboot** (the corpus's `clock.set` step) hit
`No connection could be made because the target machine actively refused it` after exactly 1 m 30 s in the
14-minute loaded run, while the server's own log showed a boot making progress. It is a bound on a boot, not a
perf assertion: a genuinely stuck boot still fails, and it still reports the server's log.

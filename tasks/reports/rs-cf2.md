# RS-CF2 — the `POST /api/unique/actors/{instanceId}/xp` 500, captured and fixed

Lane `rscf2` (worktree `cmdc/rscf2`, branch base `5709cffca3b2`), 2026-09-22. Row:
[`tasks/rpg-simulator-todo.md`](../rpg-simulator-todo.md) `RS-CF2`; owning row routed as `UAR-F1`; the
residual flakiness this lane measured is routed as `RS-CF3`.

## The captured failure

```
specimen b4ff12aa1488445db005f6b56b02e359: xp answered 500
System.InvalidOperationException: action unlock grant refused: BasicCollision
   at FusionRpg.Data.RpgStore.<>c__DisplayClass1293_0.<TryRollActionUnlocks>b__4(String _, String actionId)
     in gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:line 2148
   at FusionRpg.Core.Actions.Unlock.ActionUnlockGrantService.TryRollOnce(String instanceId, String speciesKey, UInt64 specimenWorldSeed, UnlockTuning tuning)
     in gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:line 93
   at FusionRpg.Data.RpgStore.TryRollActionUnlocks(...) in gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:line 2153
   at FusionRpg.Data.RpgStore.AwardUniqueActorXp(...) in gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:line 2019
   at FusionRpg.Server.UniqueActorService.AwardXp(...) in gk-core/src/FusionRpg.Server/UniqueActorService.cs:line 89
   at FusionRpg.Server.UniqueActorEndpoints.<>c.<MapUniqueActors>b__0_9(...) in gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:line 120
   at Microsoft.AspNetCore.Diagnostics.DeveloperExceptionPageMiddlewareImpl.Invoke(HttpContext context)
```

The 500 body is the Development-environment developer-exception page, which is why the whole throw path
is visible without adding `ProblemDetails` to the route.

## Cause

The unlock roll drew from `ActionEligibility.Candidates(catalog, speciesKey, familyOf)` minus
`state.Held`. **Eligibility answers "who may hold this action" (general / family / species) — never "may
this be granted"** — so the pool carried `act.attack` (`kind = basic`), which
`ActionValidator.ValidateGrant` refuses by construction (`ActionRejectionReason.BasicCollision`). The
grant delegate then threw inside the XP award's own transaction.

It fired only sometimes because **two seeded coin flips** gate it: the candidate is drawn by
`WeightedChoice.Pick(…, Fnv1a64(instanceId), "unlock:{instanceId}:0")` off a fresh `Guid` instance id per
specimen, and `UnlockState.TryAccept` accepts 50% at `earnCount = 0` (shipped `p1Milli = 500`).

| Reading | Command | Result | Artifact |
|---|---|---|---|
| the throw, at the throw site | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo -v n --filter "FullyQualifiedName~UniqueActorXpUnlockProbeTests"` (probe against the shared host, `--no-build`, 2026-09-22) | 40 one-level awards on a live pool: **7 × 500** (17.5%), body = the stack above; pool = `{act.attack, action.general.0003/0004/0005}` | this file |
| the pool is what makes it reachable | same probe, phase 1 (host exactly as boot left it, no sibling import): `actionIds=0`, `drawableCandidates=0` | **0 × 500 in 20 awards** — an empty pool is a legal no-op | this file |
| the regression test, BEFORE the fix | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo -v n --filter "FullyQualifiedName~UniqueActorXpUnlockRollTests"` (the one-line predicate reverted in place for this reading, then restored) | **FAIL** — `specimen b4ff12aa…: xp answered 500` + `BasicCollision` | this file |
| the regression test, AFTER the fix | the same command | **PASS** — `Passed: 1` (15 s) | this file |
| the fix's own boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/ActionValidator.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs','gk-core/tests/FusionRpg.E2E.Tests/UniqueActorXpUnlockRollTests.cs') -Session rscf2"` | **pass** — 55 Core projects green (`FusionRpg.Core.Tests` 10070/10070), Data shards 1759 tests green, E2E `Failed: 0, Passed: 235`; `DAL GUARD OK`, `TEST SUBSTRATE GUARD OK` | `scripts/verify-change.ps1` |
| determinism | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --no-build --nologo -v n` × 8, looped | **8 consecutive green: 235/235** each — wall 115 / 126 / 120 / 148 / 143 / 153 / 150 / 437 s | logs held by the lane; numbers below |
| the boundary map | `python scripts/session-boundary-check.py --repo-root <worktree> --session rscf2` | `clean for 'rscf2'` | `tasks/sessions/rscf2.json` |

## The fix

`ActionValidator.ValidateGrantable(ActionRow)` — the row-level half of `ValidateGrant`, extracted so the
chooser and the writer read ONE predicate — and `RpgStore.TryRollActionUnlocks`'s `catalog:` delegate,
which now offers the roll only rows that predicate accepts. Production, at the layer that decides what is
drawable; no retry, no skip, no widened validator, and the route's 404/400/409 mapping is untouched.

## Determinism, and what the machine did to it

Thirteen full-project runs with the fix in the tree, `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet`:

| # | result | wall |
|---|---|---|
| e2e-run-1 | `Failed: 1, Passed: 234` — `RpgScenarioSlice0E2ETests.First_session_forward_…` (message not captured: quiet run) | 2 m 21 s |
| e2e-run-2,3,4 | `Failed: 0, Passed: 235` | 2 m 6 s / 2 m 4 s / 2 m 38 s |
| final-1,2 | `Failed: 0, Passed: 235` | 2 m 2 s / 6 m 27 s |
| final-3 | `Failed: 2, Passed: 233` — `CatalogAndStressE2ETests` × 2 (`Mixed_fight_5000_hits_and_500_bullets`, `Fps120_second_9600_events`) | 4 m 59 s |
| final-4 | `Failed: 0, Passed: 235` | 14 m 39 s |
| streak-1 | `Failed: 3, Passed: 232` — the same two plus `Enqueue_2000_returns_fast_then_persists` | 548 s |
| streak-2…7 | `Failed: 0, Passed: 235` | 110–134 s |
| streak-8 | `Failed: 3, Passed: 232` — 2 stress + `FoundationE2ETests.Mid_match_switch_keeps_open_run_player` (`Expected: 1, Actual: 0`, 72 ms) | 716 s |

The red runs are the **contended** ones: `Get-CimInstance Win32_Processor` read `LoadPercentage 100` with
67–80 `dotnet` and 5–6 `testhost` processes (other lanes' suites) while they ran, and the stress failures
are wall-clock budgets (`mixed persist ms 5986`, `120fps persist ms 8044`, `enqueue ms 222`) — the brief's
"that is contention, re-run when quiet" case. Re-running when quiet produced the eight consecutive green
runs above. The two non-budget reds are filed as `RS-CF3` with the message captured only for one of them.

## NOT proved

- **The 500 is gone for every host.** Only the production wiring was narrowed; a different host that wires
  `ActionUnlockGrantService` with its own unfiltered catalog can still reproduce the throw. That is
  `UAR-F1`/`ADG-F5`, still open.
- **The 8-run streak is machine-independent.** Eight consecutive green runs were measured on this machine;
  five of the thirteen runs in the same window went red under 100 % CPU contention (all of them in
  `CatalogAndStressE2ETests` budgets plus the two names now in `RS-CF3`).
- **`RpgScenarioSlice0E2ETests`' and `FoundationE2ETests`' reds have a captured message.** Neither does:
  one ran with `--verbosity quiet`, the other is a single contended observation. `RS-CF3` names the missing
  evidence as its first job.
- **The E2E host's boot import makes the pool live on its own.** It does not: boot alone leaves
  `rpg_action` empty in this host, and the pool only became drawable through the real import path with atoms
  present. Whether a live server's boot reaches that state was not measured here (a production reading, not
  a test one).

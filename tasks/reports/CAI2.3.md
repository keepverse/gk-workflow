# CAI2.3 — `action-schedule-twin`: what the identity half left, measured

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row's title says *"the analytic model follows the core
policy"* and its status said *"IDENTITY HALF LANDED; the row stays open on the parity test, the projection and
the dominance run"*. Re-read against the code, **the parity test has landed** (it is what found CAI2.6), the
**dominance run is measurable and did not move**, and what remains is two rulings — one of which is stated
with a wrong cause. Evidence lives here rather than in `tasks/evidence-fragments/` because that directory is
not in this lane's allowed paths.

## What is measurable now, and was run

| Criterion | Command | Result |
|---|---|---|
| The dominance run — "recorded as evidence it did not move" | `dotnet run --project gk-forge/tools/DominanceBaseline -- --theta 100` | **Reproduces the recorded baseline exactly on the comparable parts:** `dominanceMatrix.names` equal, `dominanceMatrix.wins` equal, `dominantCorners == ["Might"]` equal, `theta == 100`. The stored `docs/research/class-system/_baseline-dominance.json` carries three extra keys (`chains`, `coverage`, `_meta`) from a richer invocation (`chains` needs `--models` pointed at the live tuning file) and a shorter `model` label — the matrix and corners are the overlay, and they are identical. The baseline's own `coverage.tuningSync` dates the matrix to **2026-08-27 (Checkpoint 8)**, so this reproduces a two-year-old reading byte-for-byte |
| The four guard suites green and unchanged | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~DominanceBaselineTests\|FullyQualifiedName~TerminationGuardTests\|FullyQualifiedName~GearedCornerTests\|FullyQualifiedName~ResidualFitLoopTests"` | **32 passed / 0 failed** |
| The parity test and the tier collapse | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~ActionScheduleMatchesCorePolicyTests"` | **3 passed / 0 failed** — the reserve-floor parity case, the overkill divergence witness, and the smart/performance collapse |
| Golden: unmoved | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | **5 passed / 0 failed** |

## Erratum ask 1 — who owns the profile→`ActionEconomy.Options` projection, and what is the mapping?

One line: *does the projection from a `CombatAiProfile` into `Predictor.ActionEconomy.Options` belong to this
row (which claims it), or to `profile-schema` / module 14 (which `spec-action-schedule-twin.md:421-423`
assigns it to) — and if it belongs to anyone, what maps a profile's action FILTERS and reserve floor onto an
`ActionOption`'s `CostShareOfOutputMilli`?*

It is not mechanical, and that is why the ownership question is load-bearing: a `CombatAiProfile` carries
action **filters** (`AiActionFilter`: tags, families, rung bounds) and a **reserve floor** — **no cost and no
damage multiplier** — while `ActionOption.CostShareOfOutputMilli` is a share of the action's own *nominal
output* and the live ledger prices an absolute amount scaled by rung and `Θ`
(`ActionSchedule.cs:76-79`). Every call site hand-builds the list today
(`gk-core/tools/ProvePredictor/Program.cs:115-119`, `PredictorTests.cs:15-18`). Not attempted here: inventing the
mapping would be designing a balance rule in a commit that has no ruling for it.

## Erratum ask 2 — the overkill parity acceptance cannot pass as written

The row's acceptance says `ActionScheduleMatchesCorePolicyTests` *"proves the twin's chosen action id per round
equals the real core policy's, for the reserve-floor case and the overkill case"*. Measured, the overkill case
is a **divergence**, not equality: smart tier, kill margin 50, target below it from round 2 → twin
`[skill, skill, pass, pass]`, seam `[skill, skill, idle, idle]`. That is the same defect class CAI2.6 holds a
ruling for (`ActionStage.cs:126` refuses every action and idles; `ActionSchedule.cs:163`'s `SkipOverkill`
takes the free option). So the line needs either a restated acceptance — *"the parity test agrees on the
reserve-floor case and pins the overkill divergence as a witness"*, which is what actually shipped — or the
CAI2.6 ruling, applied to both guards at once.

## The row's stated blocker for the overkill proof has the wrong cause

The row says the overkill predicate through `Predictor` *"needs a mix-observing seam — the chosen action per
round — before it can be proven through the predictor"*. Read this session, **that seam already exists**:
`ActionSchedule.Walk` returns `IReadOnlyList<RoundOutcome>` and `RoundOutcome` is
`(string ActionId, double DamageMultiplier)` (`ActionSchedule.cs:71`) — the chosen action id per round, which
is exactly what the shipped parity and divergence tests assert on.

What is actually missing is narrower and is a **spec-versus-code gap**: `Predictor.MixedStrike` calls
`ActionSchedule.Walk(options, pools, baseDamage, maxRounds, policy)` — **without** `fightEndsThisRound`
(`Predictor.cs:260`), so `SkipOverkill` can never fire through the predictor (`Choose` requires
`fightEndsThisRound is not null`, `ActionSchedule.cs:163`), even though `spec-action-schedule-twin.md` §2 says
*"`Predictor.MixedStrike` supplies it from the cumulative mean it already computes — one closure, built once
per `MixedStrike` call"*. That sentence is also not implementable in one pass as written: the predicate is
consulted **during** the walk while the cumulative mean is computed **after** it, so the implementable shape
is the two-pass estimate-then-guarded-walk the row records as attempted-and-reverted. And the reverted
attempt's *proof* problem stands too: `MixedSwing` (carrying `EffectiveBase` and `Atoms`) is a private record
(`Predictor.cs:59`) that never reaches `DuelPrediction`, so the mix is not observable through the predictor's
public surface — `DuelPrediction.NetAttrition` is a derived rate, which is why "two all-free mixes produced
1000 vs 6250".

**Not landed here, and why:** it needs the erratum above (the acceptance it would serve is the one that cannot
pass), and it is a design change to a shipped pure function. Named precisely so whoever holds the ruling has
the exact site: `Predictor.cs:260` plus one optional observer on `MixedStrike`'s output.

## Still out of fence

`gk-forge/tools/DominanceBaseline/**` is not in this lane's allowed paths, but the tool is **runnable read-only**
(no `--out` prints to stdout and writes nothing), so the run above needed no fence. `gk-core/tools/CombatSim/**` and
`gk-core/tools/ProvePredictor/**` are likewise outside the fence; neither is touched.

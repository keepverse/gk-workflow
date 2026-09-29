# `CAI2.4` — the router's sink was never supplied in production

Lane `cai3` (session `combat-ai-3`), 2026-09-23. The fourth arm landed earlier in this lane; this is the
correction and the wire it implied.

## The correction

The previous report claimed CAI2.4's acceptance line — *"All four policies behind the router record
through the same sink"* — was **satisfied**. It was satisfied **at the router** and **unreached in the
pipeline**, and that is the stronger statement:

```
grep -rn "sink:" src/ --include=*.cs     ->  no matches
```

Three production `IntentRouter.Compose` call sites exist — `BasicAttack.cs:175`, `TimelineDispatch.cs:81`,
`DelveBattleSession.cs:188` — and **none passed a sink**, so every arm the router wraps recorded nothing in
any shipped battle. That is the *"a mechanism that no production host reaches is not done"* shape.

## What landed

`BasicAttack.cs` and `TimelineDispatch.cs` now pass:

```csharp
sink: trace is null ? null : new FusionRpg.Core.Actions.Ai.BattleTraceDecisionSink(trace)
```

**Gated on the trace being ACTIVE**, deliberately: `AiDecisionRecordingSource` allocates one wrapper per arm
inside `Compose`, and CAI1.14's zero-allocation acceptance line is about the **sink-null** path — so a battle
with no trace must stay allocation-free, and a traced one may pay for observability.

**`DelveBattleSession.cs:188` is deliberately NOT wired.** Its `Trace` is a `DecisionTrace`
(`DelveBattleSession.cs:59`) — the delve's own type, not a `BattleTrace` — so `BattleTraceDecisionSink` does
not fit. Giving that path a sink means either a delve-side sink or a shared interface, which is a design
decision rather than a wire, and it is named here rather than silently skipped.

## Proven through a real battle

`DecisionInspectorTests.A_real_battle_reaches_the_routers_sink` runs
`BattleEngine.Resolve(BattleGoldenTests.CloseSetup(), 2002, trace)` and asserts the trace carries a
**router-level** line. The router knows no round and no candidate detail, so its line is `0 <actor> ` with an
**empty** top-three and no `#1=` slot — which is what distinguishes it from a policy-level record. This is
the "proven by a test that enters through the real host" standard, not a source scan.

| Criterion | Command | Result |
|---|---|---|
| The wire is live in a real battle | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionInspectorTests" --nologo --verbosity quiet` | **9 passed / 0 failed** |
| The wire test is load-bearing (planted violation) | same command with `sink: null` | **1 failed** — exactly `A_real_battle_reaches_the_routers_sink`; reverted green |
| The whole Core project | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **9719 passed / 0 failed** |
| No golden moved | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --nologo --verbosity quiet` | **210 passed / 0 failed** — the trace list is digest-excluded, so an observer moves no digest |
| The lawn/match surface | `dotnet test gk-core/tests/FusionRpg.Core.Match.Tests --nologo --verbosity quiet` | **182 passed / 0 failed** |
| The delve/Server surface | `dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --verbosity quiet` | **858 passed / 0 failed** |
| The program's guards | `guard-actor-hub`, `guard-dal`, `guard-single-writer`, `guard-funnel-delta`, `guard-battle-responsibility`, `guard-secondary-no-unity` | all **exit 0** |
| Doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | all **0 HIGH** |

## NOT proved

- **No live probe.** The wire is proven through `BattleEngine.Resolve` in-process, which is the real host for
  this path; a traced battle in the running game was not taken.
- **The delve path's sink was not designed**, only named as the remaining site and the reason it is not a
  drop-in.
- **The trace's line COUNT grows when a trace is active** — one line per arm consulted, so up to two or three
  per decision where a policy-level record was one. No test asserts a count (all green), but a reader of a
  traced battle should expect more `AiDecision` lines than before, and that is the observable cost of the
  wire rather than a hidden one.

## The second wire site, pinned the only way it can be

`TimelineDispatch`'s reselect path passes the same trace-gated sink, and **no test can enter it**:
`Reselect` is a LOCAL FUNCTION inside the dispatch method. Removing its sink would have left every test
green while a reselect silently stopped recording — the "one wire remains" shape this repo treats as
not-done — so the call site is pinned by scanning the source, the pattern `StanceSeamTests` already uses:

`DecisionInspectorTests.The_reselect_path_passes_the_same_sink` asserts that `TimelineDispatch.cs` contains
**exactly one** code line carrying `sink:` (comments stripped, line numbers deliberately unpinned) and that
it names `state.Trace` and `BattleTraceDecisionSink`.

**Planted violation:** the sink line deleted (with the preceding argument's trailing comma adjusted so the
call still compiles) → **1 failed**, exactly that test, and the other nine passed. Reverted green.

Together the pair is honest about its coverage: the real-battle test proves the COMMIT site end to end, and
this one pins the RESELECT site at the source level because nothing can call it directly.

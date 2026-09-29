# CAI4.8 — the frame slot, default-off: half landed

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row's entry condition (`lawn-perf-budget.v1.json`,
lawn `LW1.1`) and its tuning keys (`combat-ai.v2.json`'s lawn section, landed with `CAI-F1`) both exist as
of this segment, so the slot was built. What remains is ONE named dependency rather than a list.

| Criterion | Command | Result |
|---|---|---|
| `LawnCombatAiFeature` has the `LawnBasicAttackFeature` shape exactly and ships default-off | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnCombatAiFeatureFlagTests"` | **7 passed / 0 failed** — the default const is false; no toggle means off; a stale backing field does not leak; an explicit toggle is the only way it reads true with no env var; `=0` beats an on-toggle, `=1` needs no toggle; an unrecognised value defers to the toggle then the module default |
| The slot runs the due set and reaches the decision seam | `dotnet test ... --filter "FullyQualifiedName~LawnDecisionHostTests"` | **7 passed / 0 failed** — three first-of-swing records make the actor due; the seam is called once; a committed cast locks it; the token is released in the `finally` either way |
| A throwing policy is caught at the tick boundary and the next frame still ticks | same run | **7 / 0** — the first decision throws, `FailureCount` is 1, the token comes back, and the NEXT tick calls the seam again |
| The switch turning off mid-match drops every state and releases every token | same run | **7 / 0** — `TrackedCount` 0, `TokensInUse` 0, `TryTriggerState` false |
| Death releases the token and drops the state; a reused address starts clean | same run | **7 / 0** — after `Remove` the state is gone, and a fresh swing re-registers with no lock and does not inherit the 3 accumulated swings |
| `lawn.ai.decide` reports its own section | same run (the section is entered on every enabled tick) | `PerfProbe.Measure(PerfSection.LawnAiDecide)` wraps the slot's body — its own section, outside `KernelDriveHost`'s budget |
| The host supplies `AiActorClassOf` | same run | **7 / 0** — `ClassOf` answers `General` for an unresolvable actor (the live lookup needs the game assembly), never `Unique` by accident |
| `AiDecisionRecord.Trigger` is populated here | same run | **7 / 0** — `TryTriggerState` returns the recorded swings/timer/lock/token, and `false` for an unknown actor rather than a synthesised state |
| The lawn section parses through its own loader, against the shipped document | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombatAiTuningRevisionTests"` | **5 passed / 0 failed** — 7/50/10/`"lawn.ai.offset"` read through `CombatAiLawnTuning.Parse`, and an absent lawn section (v1) is REFUSED rather than defaulted |
| The injector still compiles | `guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD OK` |
| The project, and the guards | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests`; the seven guards | **104 passed / 3 failed** — the three are the pre-existing `LawnBasicAttackFeatureFlagTests` (`CAI-find-1`); guard-dal/single-writer/funnel-delta/actor-hub/secondary-no-unity/test-substrate/debug-scope all exit 0 |

## The one blocker, and why the decision is a seam

`LawnDecisionHost.Decide` is a delegate the composition root supplies. That is not a shortcut: the decision
chain is **view → policy → cast**, and its inputs are module 16's held sets (which need an `ActionCatalog`
the injector has no feed for — `grep` finds no `ActionCompiler`/`ActionRow` reference in
`gk-fusion/src/FusionRpg.Injector/` at all) and the ledger's held-action rows. Wiring those inside this file would
make it a SECOND composition root, which is the defect `guard-actor-hub` exists to catch. So the slot owns
what it can own — the due set, the budget, the token, the state, the class, the perf section — and the
decision arrives as a seam, exactly as `LawnBattleView` takes its seven.

**A found ordering defect, fixed rather than worked around:** `InjectorLoop.Tick` drains commands BEFORE
this slot runs, so a swing recorded in frame 1 would be dropped for an actor the slot had not yet seen
(registration happened only from the census). `RecordSwing` therefore registers on demand; `Register` is
idempotent and seeds the actor's own offset, so a repeat is a no-op.

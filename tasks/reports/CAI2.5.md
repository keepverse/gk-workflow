# CAI2.5 — `decision-inspector` B: the injector half (the lawn ring, default off)

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The Core half (`AiDecisionRing` + its 8 tests) landed in
lane `combat-ai-2`; this is the injector half the row's Files list names — the switch, the lawn adapter and
the additive registry cleanup. Evidence lives here rather than in `tasks/evidence-fragments/` because that
directory is not in this lane's allowed paths.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Ring bounded, last-per-actor survives eviction, copy-on-read, unknown actor → nothing | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests/FusionRpg.Injector.Tests.csproj --filter "FullyQualifiedName~AiInspectFeatureFlagTests"` | **14 passed / 0 failed** — the ring's own cases landed with CAI2.5's Core half; this run re-proves the sink's reads return what was stored and an unknown actor returns `null` | `gk-core/src/FusionRpg.Core/Actions/Ai/AiDecisionRing.cs` |
| Death removes the index entry; a reused ptr finds no stale entry; order-independent; recorded entries not rewritten | same run | **14 passed / 0 failed** — `Remove_withdraws_the_actors_index_entry_still_drops_its_pools_and_leaves_ring_history` asserts the index is gone while the ring still holds the record (history is not rewritten by reuse) | `gk-fusion/src/FusionRpg.Injector/Effects/InjectorEntityRegistry.cs` (`Remove`) |
| `AiInspectFeature.Enabled` false with no env var and no toggle; `=0` wins over a toggle; `=1` turns it on; a never-toggled `CheatState` supplies no default | same run | **14 passed / 0 failed** — 9 of them are the switch: `DefaultEnabled_constant_is_false_by_owner_decision`, `Enabled_defaults_off_with_no_explicit_toggle_ever_set`, `Enabled_ignores_a_stale_true_backing_field_when_never_explicitly_set`, `Env_forced_off_wins_over_an_explicit_on_toggle`, `Env_forced_on_wins_over_an_explicit_off_toggle_and_needs_no_toggle_at_all`, `An_unrecognised_env_value_defers_to_the_toggle_then_to_the_module_default` | `gk-fusion/src/FusionRpg.Injector/Effects/AiInspectFeature.cs` |
| The ring's cleanup in `InjectorEntityRegistry.Remove`/`Clear` is **additive** | same run | **14 passed / 0 failed** — the `Remove` case asserts the PRE-EXISTING per-actor drop (`ResourcePools.TryGet`) still happens in the same call, so the new line was appended rather than substituted; `Clear_empties_the_ring_and_its_index` covers the match-end edge | `InjectorEntityRegistry.cs` (`Remove`, `Clear`) |
| The injector host still compiles (a skip-stub is not a build) | `pwsh -NoProfile -File scripts/guard-injector-compile.ps1` (with `FUSIONRPG_ML_GAMEDIR=H:/Games/PVZ-Fusion-3.9_MelonLoader`, `FUSIONRPG_GAME_PROFILE=pvzrh-3.9`) | `INJECTOR COMPILE GUARD OK — MelonLoader host compiled to %TEMP%\fusionrpg-injector-compile\` | — |
| The program's guards | `guard-single-writer.ps1`, `guard-funnel-delta.ps1`, `guard-actor-hub.ps1`, `guard-secondary-no-unity.ps1`, `guard-debug-scope.py` | all **exit 0** (`SINGLE-WRITER GUARD OK`, `FUNNEL DELTA GUARD OK`, `ACTOR-HUB GUARD OK`, `SECONDARY NO-UNITY GUARD OK`, `DEBUG SCOPE GUARD OK -- 107 route(s), 0 banner mismatches`) | — |
| Whole injector test project, for the record | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests/FusionRpg.Injector.Tests.csproj` (with `FUSIONRPG_GAME_DIR=H:/Games/PVZ-Fusion-3.9_BepInEx_Full_Tools`) | **67 passed / 3 failed** — all three are the pre-existing stale `LawnBasicAttackFeatureFlagTests` below; every one of this task's 14 is green | — |

## Residual — why the row stays OPEN

**Updated 2026-09-23 (lane `cai2`, session `combat-ai-2b`): the READ ROUTE landed.** `debug.combat.snapshot`
now carries `aiDecisionCount` and `aiDecisions`, projected to primitives — enums by NAME, the candidate list
by COUNT, and the top-three through `CandidateScorer.FormatTopThree`, the one formatter, so no second
formatting path exists. It is read-only and on-demand: reading never scores, never records and never
synthesises an entry (the spec's §6 Game Injector Debug rules), and it reuses the audit-visible injector
dump rather than adding a route, so `guard-debug-scope.py` reports **107 routes, 0 banner mismatches**.
An empty list in that dump is the SWITCH (D4: hidden by default), not a defect.

| Criterion | Command | Result |
|---|---|---|
| The read route is wired and the dump builds | `dotnet build gk-fusion/tests/FusionRpg.Injector.Tests` ; `guard-injector-compile.ps1` | `Build succeeded`; `INJECTOR COMPILE GUARD OK` (not a skip) |
| It added no route and did not break the scope classification | `python gk-core/scripts/guard-debug-scope.py` | `DEBUG SCOPE GUARD OK -- 107 route(s), 0 banner mismatches` |
| The project | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests` | **77 passed / 3 failed** — the three are the pre-existing stale `LawnBasicAttackFeatureFlagTests` (`CAI-find-1`) |
| The program's guards | `guard-dal`, `guard-single-writer`, `guard-funnel-delta`, `guard-actor-hub`, `guard-secondary-no-unity`, `guard-test-substrate` | all **exit 0** |

**The one thing still missing, and it is another row's:** the **decision FEED**. No lawn host calls
`LawnAiDecisionObservability.Sink.Record` yet — the lawn decision host is `CAI4.8`'s, exactly as this row's
own text says (*"`Trigger` population on the lawn is CAI4.7's"*), and `CAI4.8` is itself blocked on the lawn
plan's `lawn-perf-budget.v1.json` (`LW1.1`, measured absent). So the box stays unticked against that NAMED
dependency ROW rather than against "one wire remains".

## The earlier residual, for history

The ring now has a **production edge** (every plant/zombie death and every match reset reaches it through
`InjectorEntityRegistry`), and the switch is the gate its recording sink applies. What does not exist yet
is the **decision feed**: no lawn host calls `LawnAiDecisionObservability.Sink.Record` — the lawn decision
host is `CAI4.8`'s (`LawnDecisionHost` / the frame slot), exactly as this row's own text says *"`Trigger`
population on the lawn is CAI4.7's"*. The debug **read route** is owed too: the class exposes
`Recent()`/`LastFor()` (tested), but no `debug.*` command or endpoint reads them, and the row's Files list
names neither. Per the binding rule ("if the wire truly belongs to another task, say so and keep THIS task
open"), the box stays unticked.

## Stated deviation from the spec's suggested edge

`spec-decision-inspector.md` §4 suggests copying the `MatchHost.Runtime.MembershipChanged` consumer. That
event's `Cleared` transition is raised by `UniqueBindings.ClearInstance` — a **unique-binding** lifecycle
edge, not a general death edge — so it never fires for the general creatures the inspector exists to
explain. `InjectorEntityRegistry.Remove` is the lawn's real per-actor death edge and already covers both
sides (`GameHooks`' plant-death postfix; `NoteZombieDead`, which re-removes on every death-animation frame
because a resync can re-`Add` a dying zombie), and `Clear` is the match-end edge. `Add` is deliberately NOT
an edge: `Resync` clears the registry and re-`Add`s every live actor every `ResyncFrames`, so treating it as
one would wipe a long-lived actor's last decision every ~4 seconds.

## Finding filed in the same commit — `CAI-find-1`

`gk-fusion/tests/FusionRpg.Injector.Tests/LawnBasicAttackFeatureFlagTests.cs:49,63,106` assert
`LawnBasicAttackFeature.DefaultEnabled` is **false**, while `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackFeature.cs:56`
has been **true** since `9f9853138` (2026-09-16, *"the basic-attack feature is default ON again, on its own
metric"*) — that commit flipped the constant and did not update the three assertions, and
`FusionRpg.Injector.Tests` is not in `ci.yml`, so nothing caught it. Filed as a row in
`tasks/combat-ai-todo.md` naming **lawn-combat-wire** as the owning program (its todo is outside this lane's
fence). Not fixed here: the constant is another program's owner decision.

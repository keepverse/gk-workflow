# `CAI4.8` — the frame slot had no start edge, so it could not run

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Found while looking for in-fence work; fixed because the
missing wire is one line and the consequence was total.

## The defect, measured

`LawnDecisionHost.BeginMatch` had **no production caller**.

```
grep -rn "BeginMatch" src/ --include=*.cs
  .../MatchCommanderSnapshotHolder.cs:19      (definition)
  .../MatchHost.cs:217,235,238                (three holders called at board.start)
  .../LawnDecisionHost.cs:85                  (definition — and NO caller anywhere)
  .../tests/FusionRpg.Injector.Tests/LawnDecisionHostTests.cs   (tests only)
```

`LawnDecisionHost.Tick` is called every frame (`InjectorLoop.cs:105`), but with
`_trigger`/`_budget`/`_pool` still `null` it returned at its own guard:

```csharp
if (_trigger is null || _budget is null || _pool is null) return;
```

So the slot never computed a due set, never offered a budget entry, never leased a token — while its
**death and board-end drops already ran** (`InjectorEntityRegistry.cs:175`, `:199`). The lifecycle was
asymmetric: the host dropped state it never created. The row's own claim (*"the slot schedules and counts,
and casts nothing until that feed lands"*) was therefore not true before this commit.

## What landed

| File | Change |
|---|---|
| `gk-fusion/src/FusionRpg.Injector/Effects/LawnDecisionHost.cs` | `Configure(CombatAiLawnTuning)` + a `BeginMatch(ulong matchSeed)` overload that uses it (report-once, no-op when unconfigured — it runs on the frame path) + `ResetForTest()` |
| `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` | hoists the combat-ai JSON it already read and parses the `lawn` block from the SAME document (one read, two sections), inside a try/catch |
| `gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs` | `board.start` calls `LawnDecisionHost.BeginMatch(MatchSeed.For(_runtime.MatchKey))` |
| `gk-fusion/tests/FusionRpg.Injector.Tests/LawnDecisionHostTests.cs` | 2 new cases + the test-isolation reset |

The seed is `MatchSeed.For(matchKey)` — the same pure function the Server uses when replaying
(`RpgHub.cs:144`), not a second derivation.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The configured board edge builds the slot and a decision fires | `FUSIONRPG_GAME_DIR=H:/Games/PVZ-Fusion-3.9_BepInEx_Full_Tools dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnDecisionHostTests" --nologo --verbosity quiet` | **9 passed / 0 failed** | `LawnDecisionHostTests.cs` |
| The new case is load-bearing (planted violation) | same command with an unconditional `return;` before `BeginMatch(tuning, matchSeed)` | **1 failed** — exactly `The_board_edge_builds_the_slot_from_the_configured_tuning`; reverted green | — |
| The whole injector project | `FUSIONRPG_GAME_DIR=... dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --nologo --verbosity quiet` | **106 passed / 3 failed** — the three are the pre-existing `CAI-find-1` staleness (was 104/3 before this commit) | — |
| The injector host still compiles (a skip-stub is not a build) | `FUSIONRPG_ML_GAMEDIR=H:/Games/PVZ-Fusion-3.9_MelonLoader FUSIONRPG_GAME_PROFILE=pvzrh-3.9 pwsh -NoProfile -File scripts/guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD OK` | — |
| Reachability, by grep rather than assertion | `grep -rn "LawnDecisionHost.BeginMatch\|LawnDecisionHost.Configure" src/ --include=*.cs` | exactly one production call site each: `MatchHost.cs:250`, `RpgHost.cs:107` | — |
| The program's guards | `guard-dal`, `guard-single-writer`, `guard-funnel-delta`, `guard-actor-hub`, `guard-test-substrate`, `guard-debug-scope`, `guard-secondary-no-unity` | all **exit 0** | — |

## A test-isolation hole the planted check exposed

`Clear()` deliberately empties the three structures **without nulling them** (board.end semantics), so a
case that only called `Clear()` could still see the *previous* case's `_trigger` — which is why the first
planted violation (a `return` in the new overload) killed **nothing**: a stale trigger registered the actor
on demand and the decision fired anyway. `ResetForTest()` now nulls them, and the same plant then killed
exactly the right case. Production is unaffected: `Clear()` keeps its empties-not-nulls behaviour and the
next `board.start` rebuilds.

## NOT proved

- **No live probe.** The board.start call cannot be entered from a test process (it needs the game), so its
  reachability is proven by grep, the technique `CAI4.7` used for its own single call site. A live probe
  would need the lawn feature enabled and a match.
- **The per-frame cost of a built-but-off slot was not measured.** With the feature default-off, `Tick`
  now runs three `Clear()` calls on empty structures each frame instead of returning immediately. That is
  the price of "off is a release" being real rather than vacuous; it was reasoned, not measured.
- **The remaining half of `CAI4.8` is untouched:** the DECISION step is still a seam, because module 16's
  held sets need an `ActionCatalog` the injector has no feed for (`CAI4.3`'s payload decision).

## The edge is now defended, not just reported

The start edge was proven reachable by a grep in this report — and **a report cannot fail**. `MatchHost` needs
a live game, so no test can enter its `board.start` block, and removing the call would have left every test
green. Two source-scan cases now pin both halves, the pattern `StanceSeamTests` uses for a call site no test
can reach:

| Case | Asserts |
|---|---|
| `LawnDecisionHostTests.The_board_start_edge_is_wired_in_MatchHost` | exactly one CODE line of `MatchHost.cs` mentions `LawnDecisionHost.BeginMatch(`, and the file's joined code mentions `MatchSeed.For(` — asserted over the body rather than one line, because the call and its seed legitimately sit on two |
| `LawnDecisionHostTests.The_tuning_is_configured_in_RpgHost` | the same, for `LawnDecisionHost.Configure(` and `CombatAiLawnTuning.Parse(` in `RpgHost.cs` |

Comments are stripped and line numbers deliberately unpinned, so a housekeeping move cannot fake either.

**Planted violation:** both calls replaced by a compiling no-op (`_ = _runtime.MatchKey;` and
`_ = combatAiJson;`) → **2 failed**, exactly those two cases, and the other nine passed. Reverted green, and
the files are byte-identical to their committed state.

**Reading:** `gk-fusion/tests/FusionRpg.Injector.Tests` **119 passed / 0 failed** (was 117).

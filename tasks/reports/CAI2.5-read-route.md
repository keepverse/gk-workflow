# `CAI2.5` — the read route's tests (the half a live probe reads, previously unpinned)

Lane `cai3` (session `combat-ai-3`), 2026-09-23. The row's injector half and its read route landed in lane
`cai2`; this closes the coverage gap on the route itself, which nothing asserted.

## What was missing

`DebugCombatActions.AiDecisionDump()` was `private static` and no test referenced `aiDecisionCount` or
`aiDecisions`. So the projection a live probe reads — enums by NAME, candidates by COUNT, the top-three
through the ONE formatter — was pinned by nothing, and the `AI-INSPECT` gate's meaning ("an empty list is
the switch, not a defect") was asserted only in a comment.

## What landed

`AiDecisionDump()` is now `public` for the same reason `LawnDecisionDump()` is: the dump builder reads live
entities and then emits through `DebugRuntime`, so it has no other test seam. Five cases in
`gk-fusion/tests/FusionRpg.Injector.Tests/AiDecisionDumpTests.cs`:

| Case | Pins |
|---|---|
| `Every_recorded_decision_is_projected_with_enums_by_name_and_the_one_formatter` | every field of one record, with `tier` as `"Smart"` (never a nested struct's `ToString`), `candidates` as a COUNT, and `topThree` compared against a direct `CandidateScorer.FormatTopThree` call — so a second formatting path cannot appear without failing |
| `With_the_switch_off_recording_writes_nothing_and_the_dump_stays_empty` | the `AI-INSPECT` gate lives in the SINK, not the call site: the host holds the sink unconditionally, and an empty `aiDecisions` therefore means "hidden by default" |
| `An_empty_ring_projects_nothing_rather_than_a_synthesised_row` | a reading never synthesises |
| `Reading_twice_changes_nothing` | the dump is an observation, never a step |
| `The_snapshot_builder_carries_the_ai_decisions_block` | the WIRING, by source scan — the projection tests would pass while the snapshot carried nothing, which is the "one wire remains" shape this repo treats as not-done |

| Criterion | Command | Result |
|---|---|---|
| The five cases | `FUSIONRPG_GAME_DIR=H:/Games/PVZ-Fusion-3.9_BepInEx_Full_Tools dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~AiDecisionDumpTests" --nologo --verbosity quiet` | **5 passed / 0 failed** |
| Each is load-bearing (three planted violations, one per contract) | same command with (a) `["tier"] = record.Tier?.ToString() ?? ""` → `["tier"] = record.Tier`, (b) the `["aiDecisions"] = AiDecisionDump()` line deleted, (c) the sink's `if (!AiInspectFeature.Enabled) return;` removed | **3 failed** — exactly the projection, the wiring and the gate cases; reverted green |
| The whole injector project | `FUSIONRPG_GAME_DIR=... dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --nologo --verbosity quiet` | **114 passed / 3 failed** — the three are the pre-existing `CAI-find-1` staleness (was 109/3) |
| The injector host still compiles | `FUSIONRPG_ML_GAMEDIR=... FUSIONRPG_GAME_PROFILE=pvzrh-3.9 pwsh -NoProfile -File scripts/guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD OK` |
| The route count and scope banners are unmoved | `python gk-core/scripts/guard-debug-scope.py` | `107 route(s), 0 banner mismatches` |
| The program's guards | `guard-single-writer`, `guard-funnel-delta`, `guard-actor-hub`, `guard-dal`, `guard-test-substrate`, `guard-secondary-no-unity` | all **exit 0** |

## NOT proved

- **No live probe**, so the projection is asserted against the ring in-process, never read from a running
  game.
- **The wiring case scans source, not the emitted payload** — a stated limitation, because the snapshot
  builder cannot be entered from a test. The pattern is `StanceSeamTests`'s.
- **The ring's own eviction and copy-on-read behaviour is not re-tested here** — `AiDecisionRingTests` owns
  it; this file only asserts what the dump exposes.

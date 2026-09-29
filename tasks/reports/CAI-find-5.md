# `CAI-find-5` — three more wires CAI4.8's row claims and does not have

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Found by scanning, not by reading the row: every
`public static` member of the combat-ai injector and Core files was listed, then each name grepped for
outside its own file. `BeginMatch` — the wire that made the slot inert — was found that way in the previous
increment and fixed; this is the tail of the same scan.

## What the scan measured

| Wire | Row's claim | Measured |
|---|---|---|
| `LawnDecisionHost.BeginMatch` | the board.start edge | **no caller** — fixed in `0ff34693b` |
| `LawnDecisionHost.RecordSwing` | "the swing feed" | **no caller**: `grep -rn "RecordSwing" src/` finds `LawnDecisionTrigger.cs:143`, `LawnDecisionHost.cs:190` and `LawnDecisionHost.cs:199` only |
| `LawnDecisionHost.ClassOf` | "`ClassOf` resolving a live `UniqueBinding` to `Unique`" | **no caller** (`:299`) |
| `LawnDecisionHost.TryTriggerState` | "`TryTriggerState` as the source of `AiDecisionRecord.Trigger`" | **no caller** (`:320`) |
| `DecisionCount` / `CastCount` / `FailureCount` / `TrackedCount` / `TokensInUse` | "a read of the live counts in `debug.combat.snapshot`" | **no reader** — the row's read was wired for `LawnOrderHost`, not for this host. **Landed in this commit** |

The scan is reproducible: list `public static` members in `src/FusionRpg.Injector/Effects/Lawn*.cs`,
`gk-core/src/FusionRpg.Core/Match/Ai/*.cs` and `gk-core/src/FusionRpg.Core/Actions/Ai/**`, then grep each name across
`src/` excluding its declaring file. A name with zero occurrences elsewhere is a candidate — not proof
(an interface implementation or a delegate reference can hide one), which is why each hit here was then
read in place.

## The swing feed, and why it is NOT wired here

`LawnDecisionTrigger`'s two triggers are OR'd: the swing count (`N`) and the timer (`T`). With no feed,
the timer half still makes actors due every `TicksPerDecision` (50 lawn ticks), so the slot is not dead —
but the feature's primary trigger is inert, and the spec's own §"The swing feed comes from the drained
record" describes a wire that does not exist.

The feed's third argument is the cast discriminator, and the only correct source is
`EffectEventDto.CastOrigin` — `CAI4.6`'s Contracts field, measured absent from `src/` and outside every
combat-ai lane's fence. The two alternatives are both worse:

- **Derive it from `ev.Trigger == EffectActions.OnActivate`.** The constant exists
  (`EffectDtos.cs:45`), but this is read-time *inference* of a fact the producer already knows — the exact
  thing `AiDecisionOrigin`'s own acceptance forbids ("the inspector never infers an origin from
  `Candidates[0]`").
- **Pass `false` unconditionally.** Correct today, because nothing on the lawn emits a cast event yet —
  and silently wrong the day `CAI4.6` lands, with no failure anywhere. That is the drift shape this repo
  refuses, so the wire waits on the field rather than guessing.

`spec-lawn-cast-trigger.md`'s Project-structure table called `EffectRuntime.cs` *"changed — Feed the swing
counter from the drained record (`:360-386`)"*. Measured, `EffectRuntime.OnDrained` never calls it; that
row now says **NOT changed** and names this row.

## What landed

`debug.combat.snapshot` gains a `lawnDecision` block, projected by
`DebugCombatActions.LawnDecisionDump()` — public so a test can assert the projection, because the dump
builder itself has no test seam (it reads live entities and then emits through `DebugRuntime`). This is the
`CAI2.5` precedent applied to module 19: an instrument nobody can read is not an instrument.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every reading is projected, and a second read is identical (the dump is an observation, never a step) | `FUSIONRPG_GAME_DIR=H:/Games/PVZ-Fusion-3.9_BepInEx_Full_Tools dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnDecisionDumpTests" --nologo --verbosity quiet` | **3 passed / 0 failed** | `gk-fusion/tests/FusionRpg.Injector.Tests/LawnDecisionDumpTests.cs` |
| The projection is load-bearing (planted violation) | same command with `["casts"] = LawnDecisionHost.CastCount` → `["casts"] = 0` | **1 failed** — `Every_slot_reading_is_projected_and_a_second_read_is_identical` | — |
| The WIRING is load-bearing (planted violation) | same command with the `["lawnDecision"] = LawnDecisionDump()` line deleted | **1 failed** — `The_snapshot_builder_carries_the_lawn_decision_block` | — |
| The default state reads zero and still builds | same command, `With_the_feature_off_every_reading_is_zero_and_the_dump_still_builds` | **passed** | — |
| The whole injector project | `FUSIONRPG_GAME_DIR=... dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --nologo --verbosity quiet` | **109 passed / 3 failed** — the three are the pre-existing `CAI-find-1` staleness (was 106/3 before this commit) | — |
| The injector host still compiles | `FUSIONRPG_ML_GAMEDIR=H:/Games/PVZ-Fusion-3.9_MelonLoader FUSIONRPG_GAME_PROFILE=pvzrh-3.9 pwsh -NoProfile -File scripts/guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD OK` | — |
| The route count and scope banners are unmoved | `python gk-core/scripts/guard-debug-scope.py` | `107 route(s), 0 banner mismatches` | — |
| The program's guards | `guard-single-writer`, `guard-funnel-delta`, `guard-actor-hub`, `guard-dal`, `guard-test-substrate`, `guard-secondary-no-unity` | all **exit 0** | — |

**The wiring test scans source rather than running the builder**, and that is a stated limitation, not a
convenience: the snapshot builder reads live entities and emits through `DebugRuntime`, so no test can
enter it. The pattern is `StanceSeamTests`'s ("exactly one code occurrence, and it is the seam's own"),
which this repo already accepts for a call site no test can reach. It asserts the wiring line exists and
calls the right helper — it does NOT prove the emitted payload (a live probe would).

## NOT proved

- **No live probe**, so the `lawnDecision` block has never been read from a running game.
- **(2) and (3) are untouched.** `ClassOf` and `TryTriggerState` land with `CAI4.3`'s composition root;
  their acceptance is `CAI2.4`'s own.
- **The timer-half fallback was reasoned from `LawnDecisionTrigger`'s OR'd triggers, not measured live.**
  That is why the swing feed's absence is "the primary trigger is inert" rather than "the slot is dead".

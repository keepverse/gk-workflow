# CAI3.1 — `stance-wiring`: one seam, two dead keys removed (SEAM HALF)

Lane `combat-ai-2`, reopened on the manager's instruction after re-reading its blocker: its deps
(CAI1.8, CAI1.10) are `done`, and the seam half is fully in-fence. The row's criterion is ANSWERED —
**no held action is a stance action today** — and the answer splits three ways, per the spec: Outcome 1
("`StanceRuntime`: **wire the seam, defer the runtime**. Keep the class"), Outcome 2
("`ai.stanceDefault`: **delete**"), Outcome 3 ("`ai.autoResolveHandicapMilli`: **delete**"). This commit is
**Outcome 1 only**.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `BattleRunState` exposes exactly one `IStanceCheck`, default `NoStanceHeld.Instance`, and every policy construction reads it | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs','gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/StanceSeamTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14949 passed, 4 failed** (the four pre-existing corpus facts). The seam is `BattleRunState.cs:194`; the three former hardcoded sites (`BattleRunState.cs` siege construction, `BasicAttack.cs` stub fallback, `TimelineDispatch.cs` reselect fallback) now read `state.Stance` | `System.Stance` + the three call sites |
| `Every_policy_construction_reads_the_run_states_one_stance_seam` (the anti-drift scan) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StanceSeamTests"` | **1 passed, 0 failed** — exactly ONE code occurrence of `NoStanceHeld.Instance` in `gk-core/src/FusionRpg.Core/Battle/**` (comment lines stripped), it is in `BattleRunState.cs`, and it is on the seam's own declaration. A second literal anywhere in `Battle/**` fails the test | `gk-core/tests/FusionRpg.Core.Tests/Actions/StanceSeamTests.cs` |
| Golden: byte-identical, `RulesetVersion` stays 5, and the three named suites unchanged | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|~ExpeditionResolver\|~Siege\|~Stance\|~DefenceAction\|~AuraRuntime\|~Trait\|Category=BalanceGuard"` | **660 passed, 0 failed** — every battle golden, expedition, siege, `DefenceActionStanceTests`, `DefenceActionStanceSlotTests` and `AuraRuntimeTests` unmoved, i.e. outcome 1 was implemented as the SEAM and not as a live `StanceRuntime` | — |
| `StanceRuntime.cs`, `PoiseLedger.cs`, `Riposte.cs` unmodified | `git diff --name-only 0f77d670..HEAD -- gk-core/src/FusionRpg.Core` | none of the three appears | — |
| Overflow + guards | `python gk-core/scripts/audit-overflow.py --targets A3`; `guard-doc-citations.ps1 -Strict` | audit-overflow **exit 0**; doc-citations **0 HIGH** (the six `BattleRunState.cs` aggression citations shifted +15 with the seam and were re-pointed) | — |

## NOT done — the row's two behavioural tests, and the whole tuning half

1. **`A_run_state_with_no_stance_assigned_refuses_nothing` and
   `A_supplied_stance_check_reaches_gate_zero_through_the_run_state` are not written, and they cannot be
   as the row specifies.** They must construct a `BattleRunState`, which is a **private nested class**
   inside `BattleEngine` (`BattleRunState.cs:32` is the `public static partial class BattleEngine`
   wrapper; the run state at `:40` has no modifier, and a nested type without one is private).
   `InternalsVisibleTo` does not reach a private nested type, and no test anywhere constructs one. The
   file records at its own lines 20-31 that the nesting was chosen *precisely so no visibility change
   would be needed* — so making it internal is a deliberate reversal of a recorded position, i.e. an owner
   decision. Writing a second stance fake instead would assert nothing about the seam, which is why I did
   not.
2. **Outcomes 2 and 3 (the two dead-key deletions) are a denied path.** `AiTuning` still declares
   `StanceDefault`/`AutoResolveHandicapMilli` (`Battle/Siege/SiegeAi.cs:65`) and `SiegeTuning.Parse` still
   reads them (`Battle/Board/SiegeTuning.cs:342-348`), so deleting the keys requires narrowing the record
   — and `AiTuning(...)` is constructed positionally in
   `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs:530` and
   `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs:470`, neither in this lane's allowed paths.
   Removing the members breaks those projects' compile and this lane cannot fix them. `siege.v3.json` via
   one `--remove-key ×2` publish is therefore also deferred — H7 forbids landing the file without its
   readers.

**Reported for the manager:** the row is blocked on (1) an accessibility decision for `BattleRunState`,
and (2) a lane holding `gk-core/tests/FusionRpg.Data.Tests/**` + `gk-core/tests/FusionRpg.E2E.Tests/**` (or a decision to
tolerate the two bootstraps' compile break inside this lane). Everything else the row asks for in outcome
1 is landed and green.

## Fourth slice — the dead keys may be present or absent (the parser half, in-fence)

CAI3.1's acceptance requires that `SiegeTuning.Parse` "reads exactly those and rejects **neither** an older
file that still carries the two removed keys **nor** a newer one that does not". The publish itself is
H7-blocked (`gk-core/src/FusionRpg.Server/Program.cs:237` names `combat-ai.v1.json` and `:231` `siege.v2.json` by
hand), but the PARSER half is entirely in-fence — and without it the publish could not land safely anyway.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Both file shapes parse to the SAME `Ai` record | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeTuningContractTests"` | **4 passed, 0 failed** — `A_file_with_the_two_dead_keys_and_one_without_parse_to_the_same_record` mutates the SHIPPED `gk-core/data/tuning/siege.v2.json` (strips the two keys) and asserts the `Ai` records are equal | `Battle/Board/SiegeTuning.cs`, `tests/.../Battle/Board/SiegeTuningContractTests.cs` (new) |
| Absent is legal; malformed is still loud | same run | passes — `A_malformed_dead_key_is_still_rejected` (names `Bogus`) and `A_non_integer_handicap_is_still_rejected`. The new `OptInt`/`OptStr` return null only for an ABSENT key and still throw on a present-but-wrong one, so a typo in a key nobody reads cannot be silently replaced by the default | — |
| The two GEOMETRY keys stay required | same run | passes — `The_two_geometry_keys_are_still_required` (removing `threatRadiusCells` throws). That is the line between "a file may drop a key nothing reads" and "a file may not drop a key the scorer needs" | — |
| Siege behaviour unchanged | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Siege\|~BattleGolden"` | **338 passed, 0 failed** | — |
| Guards + overflow | `guard-magic-numbers.ps1`; `python gk-core/scripts/audit-overflow.py --targets A3` | magic-numbers **0 findings, GUARD OK** (the two documented defaults, `DeadKeyStanceDefault`/`DeadKeyAutoResolveHandicapMilli`, are named structural constants with their reason in place); audit-overflow exit 0 | — |
| Boundary, every selected project's numbers | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs','gk-core/tests/FusionRpg.Core.Tests/Battle/Board/SiegeTuningContractTests.cs') -Session combat-ai-20260920"` | **15108 passed / 0 failed** across five: Core.Tests 13213, Atoms 1351, ActorHub 498, ActorSurface 31, AchievementTitlesTuning 15 | — |

**A stated, deliberate choice.** Absence parses to the values `siege.v2.json` ships today (`Guard` / `1000`),
so an absent key and a present-with-default key are indistinguishable — which is what makes the eventual
deletion a FILE change rather than a behaviour change. Those two defaults are named constants with the
reason beside them (nothing reads either field; the ten scoring values moved to `combat-ai.v1.json` in
CAI1.8), so a future reader can see they are structural rather than a balance dial. **Still owed:** the
publish (`siege.v3.json` via one `--remove-key ×2`) and the `AiTuning` narrowing to two members — both gated
on `gk-core/src/FusionRpg.Server/Program.cs` and the two out-of-fence `ContractTuningTestBootstrap` constructions.

---

## Lane `combat-ai-3`, 2026-09-21 — the visibility blocker dissolves; the seam gets its writer

The row was blocked on "an accessibility decision: the two behavioural tests need a live `BattleRunState`,
a private nested class whose own lines 20-31 record that the nesting exists *to avoid* a visibility change".
Re-reading the seam before accepting that produced a smaller answer.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The seam had a reader and **no writer** | `grep -rn "\.Stance = \|Stance =" --include=*.cs gk-core/src/FusionRpg.Core/` (filtered to `BattleRunState`) | **zero** assignments to `BattleRunState.Stance` anywhere in the repo — every other hit is a World/Loam/Movement stance. So gate 0 was inert **by construction**, not by content, and the two tests were un-writable for that reason rather than a visibility one | — |
| How the stance can reach gate 0 at all | `BasicAttack.cs:175-179` | `IntentRouter.Compose(policy: state.DefaultAiIntentSource ?? NoneIntentSource.Instance, fallback: new StubIntentSource(view, state.Cooldowns, state.Stance, state.CostLedger), steeredSourceFor: intentSource is null ? null : _ => intentSource, …)`. A test-supplied `intentSource` becomes the **steered** source and BYPASSES the stub — so supplying a source cannot exercise the stance; the run state must carry it | — |
| Gate 0 is unexempted | `UsabilityEvaluator` class doc | *"six gates, cheapest first, short-circuiting: stance → bound → cooldown → afford → range → condition"* — a refusing stance refuses **every** action, including the basic attack, on both sides | — |
| The in-fence fix, no visibility change | `BattleEngine.Resolve` + `BattleRunState` ctor | trailing optional `IStanceCheck? stance = null` on `Resolve`, forwarded to the ctor's new trailing parameter; the ctor does `if (stance is not null) Stance = stance;` — keeping the property's initializer as the class's **one** `NoStanceHeld.Instance` literal, which `StanceSeamTests` pins | `BattleEngine.cs:225-236,269`, `BattleRunState.cs:308-326` |
| `FixedStance` reused, not duplicated | new file + edit | promoted out of `ActionUsabilityEvaluatorTests`'s private nesting to `gk-core/tests/FusionRpg.Core.Tests/Actions/FixedStance.cs` (same `namespace`, one class), so both files compile against the one fake — the row says *"reuse the existing `FixedStance` fake, do not write a second one"* | `Actions/FixedStance.cs` (new) |
| The two behavioural tests | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StanceSeam\|FullyQualifiedName~ActionUsabilityEvaluator"` | **16 passed / 0 failed** (14 before, +2). `A_run_state_with_no_stance_assigned_refuses_nothing` → `BattleOutcome.Victory` on `BattleGoldenTests.StompSetup()`; `A_supplied_stance_check_reaches_gate_zero_through_the_run_state` → `BattleOutcome.Stalemate` at the same seed and fixture, and `Assert.NotEqual` between the two | `tests/…/Actions/StanceSeamTests.cs` |
| The fixture is reused too | same run | `BattleGoldenTests.StompSetup()` (`internal static`) is used as-is — no second battle fixture authored | — |
| **H1: goldens byte-identical** | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | **14 passed / 0 failed** — the four hash constants unmoved, which is what a trailing-optional parameter must produce | — |
| Nothing else moved | landed-slice filter (`Stance\|Delve\|Lawn\|Container\|EffectiveRung`); `FusionRpg.Core.Balance.Tests` | **5175 / 0** (5173 + the 2 new) and **210 / 0** | — |
| Audits and guards | `python gk-core/scripts/audit-overflow.py`; `guard-actor-hub.ps1`; `guard-single-writer.ps1`; `guard-battle-responsibility.py` | `A2=0 A3=0 A4=0 A5=0 A6=0`, 0 findings; all three guards exit 0 | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs','gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/FixedStance.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUsabilityEvaluatorTests.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/StanceSeamTests.cs') -Session combat-ai-3"` | `battle-effect-math (focused)` + `core` (12 projects) + `core.battle-effect-math` + `battle-responsibility`/`funnel-delta` → **15158 passed / 0 failed**, exit 0 | — |

### What this does and does not change about the row

- **Blocker (1) is gone.** No `internal`, no fixture-only hook, and the nesting's own recorded rationale is
  undisturbed. The new parameter is also the seam's *production* injection point: the first real supplier is
  `StanceRuntime`, which waits on `ActionRow` gaining a "which action releases this stance" field (the
  `action` program's A8) — the row's own Outcome 1 deferral, unchanged.
- **Blocker (2) stands**, and the row is still open on it: `AiTuning` cannot be narrowed from this lane
  because `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs:530` and
  `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs:470` construct it with **named** arguments
  (`StanceDefault:`, `AutoResolveHandicapMilli:`) and are out of fence. `siege.v3.json` still cannot land
  without its readers (H7). `SiegeKeyMigrationTests.Siege_v2_still_carries_the_two_dead_keys` therefore stays
  — it is superseded *by the narrowing*, and deleting it now would assert a decision nobody made.

### Not proved

- **`UsabilityReason.StanceHeld` is not observed from the battle.** This test proves the *seam's value
  arrives* (the refusal changes a deterministic battle in the one way a stance explanation predicts); the
  reason a refusal produces is pinned one gate level down, in
  `ActionUsabilityEvaluatorTests.Gate0_stance_refuses_first`. That division is stated in the test's own doc
  comment rather than implied.
- **No production caller passes the new parameter yet.** That is the row's own Outcome-1 deferral (the
  runtime waits on A8), not an omission here; `Resolve` already carries `intentSource`, `unlockStateFor`,
  `equipEffectIdsFor`, `runnerControls`-style injections for the same reason.
- **The `Stance` property remains publicly settable on a type no one outside `BattleEngine` can name**, so
  the writer is only reachable through `Resolve`. If a future lane wants per-actor stances, that is a
  different design and not this row's.

### Follow-up measurement — the whole solution, because the change touches a public parameter list

`BattleEngine.Resolve` is called from `Data`, `Server`, `E2E.Tests`, `Server.Tests` and the tools, so
"the Core tests are green" is not by itself proof that the new trailing parameter breaks nobody. Both
directions were measured:

| Check | Command | Result |
|---|---|---|
| Solution build | `dotnet build FusionRpg.slnx -c Release` | exit 1 with **888 errors — every single one in a `FusionRpg.Injector*` project** (`grep -E "error " \| grep -v "FusionRpg.Injector"` is **empty**), and **0** errors in any Core/Server/Data/E2E file or in the five files this task changed |
| …and the errors are environmental | error codes | `CS0246` ×1552 (`Bullet`, `HarmonyPatchAttribute` — game/interop types), `CS0103` ×216, `CS1061` ×6, `CS0400` ×2. None can be produced by adding an optional parameter |
| The non-Injector half DID build | grep of the same log | `FusionRpg.Contracts`, `FusionRpg.CheatCore`, `FusionRpg.Data`, **`FusionRpg.Server`**, **`FusionRpg.E2E.Tests`**, **`FusionRpg.Server.Tests`** all produced their Release assemblies — i.e. every `Resolve` caller outside the Injector compiles |
| The Injector's red is the documented env gap, not the change | `$env:FUSIONRPG_ML_GAMEDIR="H:\Games\PVZ-Fusion-3.9_MelonLoader"; $env:FUSIONRPG_GAME_PROFILE="pvzrh-3.9"; dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj -c Release` | **`Build succeeded. 0 Error(s)`** (23 warnings) — with the two vars the brief names, the project the solution build failed on compiles clean |
| The Injector cannot be affected by this change anyway | `grep -rn "BattleEngine.Resolve" gk-fusion/src/FusionRpg.Injector*` | no hit — the Injector does not call `Resolve`; every hit is Core, Data, Server or the tools |

Stated plainly: the solution-level `dotnet build` is **red on this machine for a documented environment
reason** (the Injector needs the game interop and both env vars), it is **not** red because of this change,
and the strongest available check — that every project which *calls* `Resolve` compiles — passed.

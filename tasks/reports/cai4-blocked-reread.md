# The 19 blocked rows, re-read — every one is still blocked, and here is the dependency

Lane `cai4` (session `combat-ai-4`), 2026-09-22, on the orchestrator's instruction: *"re-read its blocker:
if the dependency is now done in the ledger, reopen it and implement it now; if it is still genuinely
external (owner, live probe, another lane), leave it blocked and say which dependency."*

**Method.** (1) Every blocked row's declared `deps:` was read against the ledger's `done` set
(33 entries). (2) Every blocked row's `Files:` list was extracted mechanically and each path tested
against this lane's fence. (3) The path was then checked against the *active* session records to see who
holds it. The result:

- **7 of the 19 have a ledger dependency that IS now `done`** (`CAI2.2`←CAI2.1, `CAI2.3`←CAI1.8+1.9,
  `CAI2.5`←CAI2.4, `CAI3.1`←CAI1.8+1.10, `CAI3.2`←CAI1.1, `CAI3.4`←CAI1.9+1.10, `CAI4.5`←CAI4.4), and an
  eighth (`CAI4.3`←CAI4.2) has its dependency's **Core half landed this session while the row itself stays
  blocked** — **and every one of those rows' remaining work is still outside this lane's fence.** The fence, not the ledger, is what blocks them, which is why none could be reopened: a
  reopened row would have to be implemented, and the runner rejects any changed file outside the fence.
- **None of the 19 has a single remaining path inside the fence.** The only in-fence paths any of them
  names are ones this lane already landed (CAI4.2/4.6/4.7/4.9's test files), a tuning publish H7 forbids
  from here, or an owner-only probe's report document.

## The table

| Row | Declared dep, and its ledger state | What is actually owed, and where |
|---|---|---|
| `CAI2.2` | CAI2.1 — **done** | `Server/CombatAiProfileFiles.cs`, `Server/WebMatchService.cs`, `Server/DelveBattleSessionManager.cs`, `gk-core/tests/FusionRpg.Server.Tests/**`. It also sits behind CAI2.1's **Data** third (the nullable `combat_ai_profile` column, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs`), which CAI2.1 filed as owed. **External: the Server/Data lanes** (`species-gear-chain`, `strain-splice-host-20260921` and `ep-3` all claim `gk-core/src/FusionRpg.Server/**` / `gk-core/src/FusionRpg.Data/**`). |
| `CAI2.3` | CAI1.8, CAI1.9 — **both done** | The profile→`Predictor.ActionEconomy.Options` projection (its home is `gk-core/src/FusionRpg.Core/Balance/**` or `gk-core/tools/CombatSim/**`) and `dotnet run --project gk-forge/tools/DominanceBaseline`. **External: an OWNER ERRATUM** — the row claims the projection, `spec-action-schedule-twin.md:421-423` assigns it to module 2/14, and no document specifies the mapping — **plus `tools/**`**. Its in-fence half (the parity test) is landed and green (3/3). |
| `CAI2.5` | CAI2.4 — **done** | `Injector/Effects/{AiInspectFeature,LawnAiDecisionObservability}.cs` + the additive `InjectorEntityRegistry` cleanup. Core ring landed earlier. **External: this lane's fence — `gk-fusion/src/FusionRpg.Injector/**` is claimed by NO active session, so this is a cheap fence widening for the manager.** |
| `CAI3.1` | CAI1.8, CAI1.10 — **both done** | Narrowing `AiTuning` breaks `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs:530` and `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs:470`; `gk-core/data/tuning/siege.v3.json` (not a `combat-ai*` file, so not in this fence) cannot land without its reader `Server/Program.cs:231`. **External: those two test projects + the Server reader.** Its two behavioural tests already landed. |
| `CAI3.2` | CAI1.1 — **done** | `Data/Sqlite/RpgStore.Loadouts.cs`, `Server/WebMatchService.cs`, `Server/SpecimenLoadoutEndpoints.cs`, `gk-core/tests/FusionRpg.Data.Tests/**`. **External: the Data/Server lanes.** |
| `CAI3.3` | CAI3.2 — **blocked** | `Core/World/Turn/DistrictAssaultResolver.cs` + `Data/Sqlite/RpgStore.WorldTurns.cs`. **External: dep + `Core/World/**` + `Data/**`.** Its in-fence composite landed. |
| `CAI3.4` | CAI1.9, CAI1.10 — **both done** | The two owed tests need a live `BattleRunState` (a private nested class; making it `internal` is a recorded-position reversal) and its `RoleOf` caller is CAI3.5's Server lane. **External: an OWNER DECISION + `gk-core/tests/FusionRpg.Core.Tests/**` + the Server lane.** |
| `CAI3.5` | CAI3.4, CAI2.2 — **both blocked** | `Server/{RpgHub,DelveAutomatedPolicy,DelveBattleSessionManager,DelveBattleSession}.cs`, `Core/Delve/Battle/DelveBattle.cs`, `Core/Battle/BattleRunState.cs`, `gk-core/tests/FusionRpg.Server.Tests/**`, and the **protected** `tests/FusionRpg.Guard.Tests/NoCatchInLiveBattleCallStackTests.cs`. **External: deps + the Server lane + a protected-path grant.** (`gk-core/data/tuning/combat-ai.v2.json` is in fence but H7-blocked: its readers are outside.) |
| `CAI3.6` | CAI2.2, CAI2.3 — **both blocked** | `Battle/BattleModels.cs`, `Battle/BattleRunState.cs`, `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs` (the one re-bless), `docs/architecture/decisions.md`. **External: deps + the Battle/Balance lanes + decisions.md.** (`docs/research/combat-ai/predicted-delta-rulesetversion-6.md` is in fence, but writing predicted-delta evidence for a change that cannot land would fabricate it.) |
| `CAI4.1` | CAI1.1, BCU0.1 — **both done** | `Injector/Effects/LawnActorViewHost.cs`. Three Core files landed earlier. **External: this lane's fence — `gk-fusion/src/FusionRpg.Injector/**` is claimed by NO active session, so this is a cheap fence widening for the manager.** |
| `CAI4.2` | CAI1.1, BCU0.1 — **both done** | **Its own Files list is complete** (this lane landed the store + its 11 tests; all five acceptance lines run). The module's production caller is CAI4.3's registry + Cold push. **External: CAI4.3, itself blocked on `gk-fusion/src/FusionRpg.Injector/**` + `gk-core/src/FusionRpg.Server/**`.** |
| `CAI4.3` | CAI4.2 — **Core half landed** | `Injector/Effects/LawnHeldActionRegistry.cs`, `Server/RpgHub.cs`, `Injector/CheatCommandRunner.cs`, `Injector/Effects/InjectorEntityRegistry.cs`. **External: this lane's fence on `gk-fusion/src/FusionRpg.Injector/**` (unheld by any active session) + `gk-core/src/FusionRpg.Server/**` (held).** |
| `CAI4.5` | CAI4.4 — **done** | `Injector/Effects/LawnBasicAttackCostCharger.cs` + the new `Injector/Effects/LawnCostRowSource.cs` (its test file is in fence but tests a mechanism with no host). **External: this lane's fence — `gk-fusion/src/FusionRpg.Injector/**` is claimed by NO active session, so this is a cheap fence widening for the manager.** |
| `CAI4.6` | CAI4.5 — **blocked** | This lane landed the pure half (`LawnCastPlan`, spec rows 1–2). Owed: `Contracts/EffectDtos.cs`'s `CastOrigin` field + its two charge/counter refusals, `Fire`'s depth guard, and the fire site `Injector/Effects/LawnCastActivation.cs`. **External: dep + `gk-core/src/FusionRpg.Contracts/**` + this lane's fence on `gk-fusion/src/FusionRpg.Injector/**` (no active session holds it).** |
| `CAI4.7` | CAI4.1, CAI4.6, `lawn-perf-budget.v1` — **2 blocked, 1 absent** | This lane landed all three pure classes (spec rows 1–10, 12). Owed: `Core/Diagnostics/PerfProbe.cs`'s `LawnAiDecide`/`SectionCount`/`"lawn.ai.decide"`, and `data/tuning/combat-ai.v3.json`'s lawn section — **in fence, but H7-blocked** because both readers name `combat-ai.v1.json` by hand (`Server/Program.cs:248`, `Injector/Host/RpgHost.cs:89`). **External: deps + `gk-core/src/FusionRpg.Core/Diagnostics/**` + the two reader paths + the lawn plan's `LW1.1`.** |
| `CAI4.8` | CAI4.7 — **blocked** | `Injector/Effects/{LawnCombatAiFeature,LawnDecisionHost}.cs`, `Injector/Host/InjectorLoop.cs`, `Injector/Effects/EffectRuntime.cs`, `Injector/Effects/InjectorEntityRegistry.cs`. **External: dep + this lane's fence on `gk-fusion/src/FusionRpg.Injector/**` (no active session holds it).** |
| `CAI4.9` | CAI1.10, CAI4.8 — **1 done, 1 blocked** | This lane landed the queue + the refusal classifier (spec rows 1, 2, 6–13, 15). Owed: the two additive `SubjectId`/`ScopeId` fields on `Core/Actions/DirectOrder.cs`, `Actions/IntentRouter.cs`'s forced-intent hook (CAI1.10 reserved it for this module), `Server/LawnOrderEndpoints.cs`, the Injector verb/host, the two `web/**` files, and `data/tuning/combat-ai.v*.json`'s two order keys (in fence, H7-blocked). **External: dep + `gk-core/src/FusionRpg.Core/Actions/**` + `gk-core/src/FusionRpg.Server/**` + this lane's fence on `gk-fusion/src/FusionRpg.Injector/**` + `web/**`.** |
| `CAI5.1` | CAI4.9, lawn `LW2.4` — **both open/blocked** | An **owner-only live probe** (300-zombie A/B, real endpoints, read back through the normal path) writing `docs/research/combat-ai/ab-300-zombies.md`. The document is in fence; the measurement is not something a lane can produce without a live run. **External: an owner-only live probe + the lawn plan's `lawn-combat-baseline`.** |
| `CAI5.2` | CAI5.1 — **blocked** | `docs/research/combat-ai/default-on-recommendation.md` — a recommendation *over* CAI5.1's measurement. **External: dep (owner-only probe).** |
| `CAI5.3` | CAI5.2 + `LW1.4`–`LW1.6`, `LW5.1` — **all unmet** | `Injector/Effects/LawnCombatAiFeature.cs`'s const default + two measured-unmet preconditions. **External: dep + this lane's fence on `gk-fusion/src/FusionRpg.Injector/**` + the lawn plan's two preconditions.** |
| `CAI-perf-1` *(not in the 19, included for completeness)* | — | Remedy (a) needs `gk-core/src/FusionRpg.Core/Diagnostics/**`; remedy (b) is an erratum. **External: the Diagnostics path or an owner ruling.** Measured today: `PerfProbe.cs` still ends at `LawnMoveDrain = 24`, `SectionCount = 25`. |

## What this lane did instead of reopening them

One in-fence item genuinely remained, with no external blocker: the two citation sweeps
`CAI-cite-1` left as its remaining queue. It was filed as **`CAI-cite-3`** and closed in the same session —
both combat-ai doc scopes now audit at `D1 0, D2 0, D3 0, D4 0`, with 7 re-anchors, 3
not-yet-existing notes and 9 pre-fix notes, and 18 heuristic suspects read and judged artifacts. See
`tasks/reports/CAI-cite-3.md`.

**No blocked row was reopened, because reopening means implementing and none of the 19 has an in-fence
path left.** If the manager wants any of them worked from this lane, the fence needs widening — the four
groupings the routing section already sizes are `gk-fusion/src/FusionRpg.Injector/**` (clears 8 rows),
`gk-core/src/FusionRpg.Core/Match/**` (already held; cleared 4), `gk-core/src/FusionRpg.Server/**` (4 rows) and
`gk-core/src/FusionRpg.Data/**` (3 rows).

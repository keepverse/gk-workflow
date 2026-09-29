# Evidence — rpg-simulator RS3 (the clock seam: `clock-seam`)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Row RS3, owner rulings B1 (a) / B2 (b) / B3 (a); the mechanism is **shape B**
(spec §0.1, RS-F13). One section per increment, each landed as its own commit.

## Increment 1 — `ServerClock` (new) + the `FusionRpg.Core` sites

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The seam exists as one configured read, and `net6.0`-safe | `dotnet test gk-core/tests/FusionRpg.Core.EffectClock.Tests -c Release --nologo --filter "FullyQualifiedName~ServerClockTests"` | `Passed: 4, Failed: 0, Total: 4` (92 ms) — `Core -> bin/Release/net6.0/FusionRpg.Core.dll` | `gk-core/src/FusionRpg.Core/Time/ServerClock.cs` |
| A net8.0 `TimeProvider` is an **input**, never a stored type (shape B's load-bearing claim) | same run, `A_net8_TimeProvider_is_adapted_into_the_seam_at_the_composition_root` | `ServerClock.Configure(provider.GetUtcNow)` → `UtcNow == Fixed`; no `ServerClock.Current` exists | `gk-core/tests/FusionRpg.Core.EffectClock.Tests/Time/ServerClockTests.cs` |
| Both accessors keep the round-trip form each type emitted before | same run, `The_two_accessors_keep_the_round_trip_form_each_type_emitted_before` | `UtcNowDateTime.ToString("o")` ends `Z`; `UtcNow.ToString("o")` ends `+00:00` — the measured reason for two accessors | same |
| The 2 real Core sites are migrated; the purity exemption is not | `python scripts/_rs3-migrate-clock.py gk-core/src/FusionRpg.Core --apply` | `APPLIED gk-core/src/FusionRpg.Core: 2 file(s)` — `SimEngine.cs`, `Diagnostics/PerfProbe.cs`; `EffectModels.cs:81` (`SystemEffectClock`) untouched | those files |
| A seam change no longer plans the whole-core fallback | `verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Time/ServerClock.cs -AllowUnscoped -PlanOnly` | `gk-core/src/FusionRpg.Core/Time/ServerClock.cs -> core-server-clock (focused)` | `gk-core/scripts/verification-boundaries.v1.json` (`core-server-clock`) |

**Two measurements, reported not smoothed.**

- The ambient-read scan counts **214** occurrences in `src/` (Data 142 · Server 41 · Injector 19 · Core 8 ·
  Launcher 3 · CheatCore 1), where spec §5's table totals **213** and writes Launcher as `2 (+1
  DateTime.Now)`. The Launcher code carries 3. The difference is a measurement, not a defect.
- Of Core's 8 occurrences only **2 are code**: `SimEngine.cs:833` and `Diagnostics/PerfProbe.cs:256`. The
  other 6 are prose (`AdvancedEffectClock.cs:7,16,41`, `EffectBag.cs:229,245`) plus `EffectModels.cs:81`,
  the purity scan's one named exemption. So increment 1's "8 sites" is 2 real migrations.

**NOT proved / deviations.**

- **RS-F12's `BannedSymbols` edit was refused** — `gk-core/tests/FusionRpg.Guard.Tests/**` is a
  pipeline-protected path. The same rule ships as rule 2 of `gk-core/scripts/guard-clock-seam.py` (no `ServerClock`
  under `gk-core/src/FusionRpg.Core/{World,Battle,Effects}`). The C# line remains owed to the `guard`-program owner.
- **`-Session sim-t3-2` is unusable** (`tasks/sessions/sim-t3-2.json` does not exist; `tasks/sessions/**` is
  outside the fence) — `-AllowUnscoped`, as lane `sim-t3-1` recorded.

## Increment 2 — the `FusionRpg.Server` sites + the composition root

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| 33 real Server sites migrated; the 6 deadline/freshness reads of spec §7 stay raw | `python scripts/_rs3-migrate-clock.py gk-core/src/FusionRpg.Server --apply` | `APPLIED gk-core/src/FusionRpg.Server: 12 file(s)`; a re-scan leaves only `DebugEndpoints.cs` 696/1077/1078/1763/1791/1792 and `WebMatchService.cs:451` | 12 Server files |
| The host builds | `dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj -c Release --nologo` | `Build succeeded. 6 Warning(s) 0 Error(s)` | — |
| The composition root configures the seam exactly once, from the environment | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --nologo` | `Passed: 819, Failed: 0, Total: 819` (7 m 37 s) | `gk-core/src/FusionRpg.Server/Program.cs` |
| SQL still lives only in `FusionRpg.Data` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-dal.ps1` | `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data`, exit 0 | — |

**What the composition root does** (`Program.cs`, immediately before `builder.Build()`): reads
`FUSIONRPG_CLOCK_OFFSET` once, **throws** on a malformed value rather than ignoring it, and calls
`ServerClock.Configure(timeProvider.GetUtcNow, offset)` — the net8.0 `TimeProvider` adapted into shape B's
stored delegate. The offset is never accepted from a route (spec §2).

**Still owed:** the `/health` clock declaration — `HealthDto` and `RpgStore.ToHealth` are outside this
lane's paths (RS-F11).

## Increment 3 — the `FusionRpg.Data` sites

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| 140 real Data sites migrated; the heartbeat pair stays raw | `python scripts/_rs3-migrate-clock.py gk-core/src/FusionRpg.Data --apply` | `APPLIED gk-core/src/FusionRpg.Data: 48 file(s)`; a re-scan leaves exactly `RpgStore.cs:1208` (the 5 s freshness read) and `:1216` (the write it compares against) | 48 Data files |
| The store builds | `dotnet build gk-core/src/FusionRpg.Data/FusionRpg.Data.csproj -c Release --nologo` | `Build succeeded. 0 Error(s)` | — |
| The store's own suite | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --nologo` | `Failed: 1, Passed: 1856, Total: 1857` (10 m 20 s) | — |
| The single red is a documented pre-existing race, not this migration | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --nologo --filter "FullyQualifiedName~EmpireLevelTests.A_pass_that_throws_leaves_no_empire_row"` | `Passed: 1, Failed: 0, Total: 1` (248 ms) — and `tasks/empire-progression-todo.md:1272` (finding **F2**) already records `EmpireLevelTests` mutating the process-wide `ProgressionTuningHub` from its constructor | `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs` (untouched by this change) |

**Why the heartbeat pair stays raw.** `RpgStore.InjectorConnected` is a 5-second freshness window over the
injector's heartbeat, and `LiveInjector` is the property `SimService.Guard()` reads for its D1 (b) refusal
("a live injector is connected"). Shifting the clock forward makes a genuinely live injector look stale, so
the refusal silently stops firing and a scenario could run against a player's install; shifting it backward
makes a dead injector look alive. Both halves of the comparison therefore stay on the machine clock — the
read (spec §7's trap) and the write it is compared against, because a shifted write against a raw read (or
the reverse) breaks the window just as surely.

## Increment 4 — Injector + Launcher + CheatCore

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| 7 Injector files touched (11 of 17 code reads migrated); the probe-timeout pair, the overlay wait and the effect-clock seed stay raw | `python scripts/_rs3-migrate-clock.py gk-fusion/src/FusionRpg.Injector --apply` | `APPLIED gk-fusion/src/FusionRpg.Injector: 7 file(s)`; a re-scan leaves `CheatState.cs:736/760`, `CheatCommandRunner.cs:689`, `OverlayViewHost.cs:327/328`, `EffectRuntime.cs:42` | those files |
| The effect-clock seed was **reverted** after it broke a protected guard test | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~PlayerSpeciesMaterialiseCallerGuardTests"` | `Passed: 5, Failed: 0, Total: 5` (393 ms). The guard asserts the literal `new(DateTimeOffset.UtcNow)` at `PlayerSpeciesMaterialiseCallerGuardTests.cs:148`; spec §7 says increment 4 *may* source it, never that it must, so the site is allowlisted with that reason instead | `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs` |
| CheatCore keeps its Contracts-only graph **and** loses its ambient read | `dotnet build gk-core/src/FusionRpg.CheatCore -c Release --nologo` | `Build succeeded. 0 Error(s)`; `CheatDocumentCodec.FromEntries` now requires `updatedAt`, supplied by `RpgStore.cs:2589` | `gk-core/src/FusionRpg.CheatCore/CheatDocumentCodec.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` |
| The pinned dependency graph is untouched | `python gk-core/scripts/guard-repo-boundary.py` | `REPO BOUNDARY GUARD OK — the five standalone assemblies keep their pinned graph`, exit 0 | — |
| Secondary plugins stay Unity-free | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-secondary-no-unity.ps1` | `SECONDARY NO-UNITY GUARD OK — plugins Grant/Withdraw only`, exit 0 | — |
| The Launcher builds and its suite passes | `dotnet build gk-fusion/src/FusionRpg.Launcher -c Release --nologo`; `dotnet test gk-fusion/tests/FusionRpg.Launcher.Tests -c Release --nologo` | `0 Error(s)`; `Passed: 165, Failed: 0, Total: 165` | — |
| CheatCore's suite passes with the signature change | `dotnet test gk-core/tests/FusionRpg.CheatCore.Tests -c Release --nologo` | `Passed: 41, Failed: 0, Total: 41` (71 ms) | — |
| Data still builds after the `FromEntries` call-site change | `dotnet build gk-core/src/FusionRpg.Data -c Release --nologo` | `Build succeeded. 0 Error(s)` | — |

**The Injector build could not run — stated, not implied.**

| Attempt | Command | Result |
|---|---|---|
| The shim project | `dotnet build gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj -c Release --nologo` | `error : Ambiguous project name 'FusionRpg.Injector'` — **pre-existing**: the csproj is a compatibility shim (`EnableDefaultCompileItems=false`, no `Compile` items) and `FusionRpg.Injector.BepInEx.csproj` sets `AssemblyName=FusionRpg.Injector` |
| The real host | `dotnet build gk-fusion/src/FusionRpg.Injector.BepInEx/FusionRpg.Injector.BepInEx.csproj -c Release --nologo` | exit 1, **1810 errors**, all `MSB3245: Could not resolve this reference` for `0Harmony` / `BepInEx.*` / `Il2Cpp*` / `UnityEngine*` — no game install on this machine |
| The designed skip path | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD SKIPPED — no MelonLoader game dir (set FUSIONRPG_ML_GAMEDIR); injector NOT compiled`, exit 0 — the guard is `tier: local` for exactly this reason |

So the Injector's 11 migrated sites are **type-preserving and unverified**. Every replacement keeps the
type the site already used (`DateTime.UtcNow` → `ServerClock.UtcNowDateTime`; `DateTimeOffset.UtcNow` →
`ServerClock.UtcNow`), each touched file gained `using FusionRpg.Core.Time;`, and both Injector hosts
(`FusionRpg.Injector.BepInEx`, `FusionRpg.Injector.MelonLoader`) already `ProjectReference`
`FusionRpg.Core`. `guard-injector-compile.ps1` must be run on the owner's machine (or in CI with a game
dir) before this increment is called proven.

**The Launcher's one site is an exclusion with a reason** (RS-F14): `FusionRpg.Launcher.csproj` carries no
`ProjectReference` at all, so the seam is unreachable, and the read is a local UI log stamp rather than a
duration, deadline or persisted row.

## Increment 5 — the clock guard (landed) and the `ForceExpeditionDue` retirement (NOT landed)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The guard exists and is green on the finished tree | `python gk-core/scripts/guard-clock-seam.py` | `clock seam guard: source files=1478 ambient reads=21 (clock type=2, allowlisted=19, entries=19) \| simulation-tree ServerClock references=0` — `CLOCK SEAM GUARD OK`, exit 0 | `gk-core/scripts/guard-clock-seam.py` |
| It **bites** on planted violations (rule 1 and rule 2) | `python gk-core/scripts/guard-clock-seam.py -SrcDir /tmp/clockplant` (a temp dir holding a planted `DateTimeOffset.UtcNow` and a `ServerClock` reference under `FusionRpg.Core/Effects/`) | exit 1, 20 violations — the two planted ones named (`Planted.cs:2` ambient read; `PlantedSeam.cs:2` simulation-tree `ServerClock`) plus the expected stale-allowlist noise of a fixture dir | same |
| Wired the way every other guard is | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci -Only clock-seam` | `clock-seam ci gating 0` — `GUARDS OK - 1 guard(s) run, 0 red` | `gk-core/scripts/enforcement-registry.v1.json` (`clock-seam`, invariant `pr-clock-seam`) |
| Registry + runner contracts hold with two new guards | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~EnforcementRegistryGuardTests\|FullyQualifiedName~GuardRunnerTests\|FullyQualifiedName~SimFabricationGuardTests"` | `Passed: 30, Failed: 0, Total: 30` | — |
| The new guard resolves a verification owner | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | `gk-core/scripts/verification-boundaries.v1.json` (`clock-seam-guard`) |

**The retirement did NOT land, and the reason is measured (spec §6a, filed as RS-F16).** A single static clock
offset cannot make an expedition due: `DispatchExpedition` writes `due = ServerClock.UtcNow +
tier.DurationMinutes` and `ExpeditionService.CollectAsync` refuses while `now < due`, both reading the SAME
seam, so the gap is always the tier's 30-minute minimum. A mid-run clock movement is unreachable — the runner
reaches its host over HTTP only, and a route that sets the clock is deliberately not specified (spec §2, owner
ruling D3 (b)). Deleting the rewind would break three test files that have no replacement
(`ExpeditionStoreTests.cs:141`, `ExpeditionE2ETests.cs:70,125`, `ContractE2ETests.cs:173`); the two HTTP ones
would need a process-global `ServerClock.Configure` mutation from a test, the same hazard class as the
documented `ProgressionTuningHub` flake (`empire-progression` F2). So the corpus keeps its documented SIM
rewind, and **RS3 is not closed** — its retirement acceptance is unmet and this lane did not tick it.

## Post-merge verification (2026-09-23) — `features/mega-merge` merged, then re-measured

The lane merged `features/mega-merge` (179 commits, clean, no conflicts) after the integration head was
repaired, and re-ran the sweeps on the merged tree.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The merge is clean | `git merge features/mega-merge --no-edit` | exit 0, no conflicts, no uncommitted files | merge commit |
| The migration's two Core sites are covered by their own projects | `dotnet test tests/<p> -c Release --nologo` for `FusionRpg.Core.SimEngineMatchOverlayTests.Tests`, `...SimEngineMatchIsolationTests.Tests`, `...SimEngineShieldTests.Tests`, `...StatMathAndSimTests.Tests`, `...Diagnostics.Tests`, `...EffectClock.Tests` | `8/8`, `1/1`, `6/6`, `14/14`, `29/29`, `10/10` — 68 passed, 0 failed | — |
| The full CI guard tier, read as counts | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | **25 guards, 23 green, 2 red.** Both new guards green (`clock-seam 0`, `sim-fabrication 0`). The two reds are **not this lane's**: `doc-citations` (two HIGH D3 findings in a **loam** document, RS-F18) and `narrative` (a contention flake — **green standalone**, RS-F19) | — |
| The `narrative` red is a flake, not a rule | `python gk-core/scripts/guard-narrative.py` | exit **0** | — |

**Why `doc-citations` is not this lane's:** the audit's HIGH list names only
`docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md:76` (bare `fill.py` basenames, ambiguous
since the merge added a second `fill.py`); `D1 file does not exist` is 720 with **0 HIGH**. Filed as RS-F18.

**Why `narrative` is not this lane's:** 5 Guard.Tests failures inside the sweep, exit 0 standalone. Filed as
RS-F19; same class as RS-F8.

## Post-merge repair + RS-F7 (2026-09-23, lane `sim-t3-2`)

Merging `features/mega-merge` left `gk-core/tests/FusionRpg.E2E.Tests` uncompilable and its in-process host
unconfigured. All three breaks are in files neither lane owned; this lane fixed them inside its own fence so
the branch could be verified at all, and filed them as **RS-F20** with their owners.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The E2E project compiles again (`DangerBand` + `Encounter` arity, mirrored from `expeditions.v2.json`) | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` | build succeeded (was `error CS7036` ×2), then `Passed: 46, Failed: 0, Total: 46` | `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs` |
| The E2E host is configured again (`LeadNamesHub`) | same run | `RpgApiFactory` no longer throws `LeadNamesHub.Configure(...) has not run`; every `RpgApiFactory`-based test runs | same |
| The corpus's soul-ledger assertion is no longer a presence test on an RNG-dependent row | same run, twice | `Passed: 46/46` (2 m 16 s) then `Passed: 46/46` (2 m 14 s) — the measured reading was `$.items[*].reason is ["expedition","defeat","discovery"×10,"summon","seed"]` | `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` |
| **RS-F7** closed against its acceptance's second branch | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-sim-fabrication.ps1`; and the corpus run above | guard green (`scenarios=1 steps=36 reads=7 test.* steps=2`); the contract now states the ledger is not digest-eligible | `gk-core/tools/RpgSim/readback-verdict.md` §3, `gk-core/tools/RpgSim/ReadingDigest.cs` |

**The flake, measured before it was fixed.** `expect.souls.ledger.expedition` asserted the *presence* of a
row whose write is conditional on the server-minted event-souls roll (`RpgStore.Expeditions.cs:311` writes it
only when `EventSouls > 0`), so ~1 run in 14 had no such row: `expect.souls.ledger.expedition: $.items[*].reason
does not contain "expedition"`, on one of two consecutive runs inside a single test. The assertion is now a
**closed vocabulary** — `seed | summon | expedition | discovery | victory | defeat`, each reason named to the
cause this run has — which is how the corpus already handles every other RNG-dependent value. Same family as
**RS-F4**; the presence proof is not recoverable until a scenario can own the seed.

**RS-F7.** The XP ledger's one-letter timestamp `t` cannot be named in `ReadingDigest.Baseline` without risking
a silent blank elsewhere, so the contract now says so out loud: the ledger is **not digest-eligible**, and a
scenario that wants to digest it must declare the exclusion itself with its own reason. `ReadingDigest`'s own
doc comment carries the same line beside the list it constrains. The payload-shape half (a self-describing
`createdUtc`) stays with the progression surface that owns the payload.

**Also corrected while here:** `ReadingDigest.Baseline`'s `*Utc` reason still said "the clock seam is RS3 and
gated"; it now names the landed seam and the fact that the shipped corpus declares `clock.mode: ambient`.

## The full E2E project after the repair (2026-09-23)

`verify-change.ps1`'s plan for this segment's paths resolves `gk-core/tests/FusionRpg.E2E.Tests/**` to `test: e2e`
(the whole project), so the whole project was run rather than the `RpgSim` filter alone.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The repaired bootstrap serves every E2E class, not just `RpgSim` | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --no-build --nologo` | `Failed: 2, Passed: 284, Total: 286` (3 m 55 s) | `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs` |
| The two reds are another program's fixture drift, filed not re-blessed | same run | `ContractFixtureTests.Commander_list_fixture_matches_live_dto` (`"Garden Keeper"` vs live `"Crazy Dave"`); `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening` (`stateHash 0f685a16…` vs `b41ce3ef…`) — both from the merged identity-rename lane (`e965f65e2`, `29cf63d6d`); neither fixture file was regenerated | **RS-F21** |

**Why the world-turn hash is not the clock migration's:** it is `Core/World` state
(`gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:89` → `StateHasher.Hash`), and the world-simulation purity
scan bans every wall-clock symbol in that tree — a hash that moved with the clock could never have been
stable, which is exactly why the tree is scanned. Moving either fixture to make the test pass is the defect,
not the fix.

## Increment 5a — a declared `offset` is honest for both hosts (RS-F16 ruled)

Owner ruling `f49cd83b4`: candidate (1) first, then candidate (2). 5a is candidate (1) — the offset is
plumbed at BOOT; 5b (the mid-run input) is still owed.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A scenario may declare `clock.mode: offset` + `offsetSeconds`; `explicit` and a stray offset on `ambient` are still refused | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` | `Passed: 48, Failed: 0, Total: 48` (2 m 20 s) — includes `A_declared_offset_is_accepted_and_an_undeclared_one_is_refused` | `gk-core/tools/RpgSim/ScenarioFormat.cs`, `gk-core/tools/RpgSim/ScenarioValidator.cs`, `gk-core/tests/FusionRpg.E2E.Tests/RpgSimFormatContractTests.cs` |
| The in-process host applies it at boot | same run, `RpgSimClockOffsetTests.The_in_process_host_applies_the_declared_offset` | `ok=True clock='offset 3600s — …' readings=7 digest=daa9df408054f32e…`; `dispatchedUtc` and `dueUtc` 55–65 min ahead of the machine clock | `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs` |
| The real process applies it too, by the same variable | same run, `RpgSimClockOffsetTests.The_real_process_host_applies_the_declared_offset` | `process host: pid=… ok=True clock='offset 3600s — …' readings=7 digest=daa9df408054f32e…`; the same two stamps measured on the real row | `gk-core/tools/RpgSim/ProcessHost.cs` |
| The store test moves to its own `utcNow` input (the ruling's explicit step) | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --nologo --filter "FullyQualifiedName~ExpeditionStoreTests"` | `Passed: 8, Failed: 0, Total: 8` (1 s) — `A_dispatch_stamped_in_the_past_is_due_without_rewriting_the_row` replaces `Force_due_rewinds_the_timer` | `gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs` |
| The tool builds, and the CLI refuses an offset it cannot apply | `dotnet build gk-core/tools/RpgSim/RpgSim.csproj -c Release --nologo` | `Build succeeded. 0 Error(s)`; `--base-url` + an offset scenario exits 2 with the reason named, and `--host process` forwards `ClockOffsetSeconds` | `gk-core/tools/RpgSim/RpgSimCli.cs` |
| The corpus is untouched and still honest about its bypass | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-sim-fabrication.ps1` | `scenarios=1 steps=36 reads=7 test.* steps=2` — `SIM FABRICATION GUARD OK` | `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` (unchanged) |
| The test substrate stays clean (a new file-backed store beside the assembly, never `%TEMP%`) | `python gk-core/scripts/guard-test-substrate.py` | `TEST SUBSTRATE GUARD OK — no new swallowed deletes, temp-backed or untagged file-backed stores, or shipped-corpus copies / corpus writes into temp, in tests/` | `gk-core/tests/FusionRpg.E2E.Tests/RpgSimClockOffsetTests.cs` |

**What 5a does NOT prove, stated in the test itself.** It proves the declaration reaches the host and changes
what the host believes the time is. It does not make an expedition due inside one run: a single static offset
moves the dispatch and the due check together. That is 5b, and until it lands `ForceExpeditionDue`'s `UPDATE`,
the corpus's `test.expedition-due` step and its RS4 allowlist entry all stay — with the scenario's own note
still saying what the bypass is.

## Increment 5b — the mid-run clock input, and the bypass retired

Owner ruling `f49cd83b4`, candidate (2).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A scenario declares a mid-run movement and BOTH hosts apply it | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` | `Passed: 48, Failed: 0, Total: 48` (5 m 32 s) — the corpus runs its `clock.set` step on the in-process host and on a real process that **reboots mid-run** | `gk-core/tools/RpgSim/IClockControl.cs`, `gk-core/tools/RpgSim/ScenarioRunner.cs` |
| `ForceExpeditionDue`'s `UPDATE` is retired, with no store bypass replacing it | `grep -rn "ForceExpeditionDue" src/` | only the removal note in `RpgStore.Expeditions.cs:204`; the method is deleted, and `/api/test/expedition-due` is gone (`MapExpeditionTest` is an empty mapper recording the removal) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs`, `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs` |
| The corpus step is re-pointed at the seam, and the vocabulary no longer knows the old op | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-sim-fabrication.ps1` | `scenarios=1 steps=36 reads=7 test.* steps=1 \| /api/sim handlers=60 (take RpgStore: 0) \| /api/test handlers=12 (take RpgStore: 11, allowlisted: 11)` — was `test.* steps=2` and `13/12/12`; no stale allowlist entry remains | `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`, `gk-core/tools/RpgSim/ScenarioVocabulary.cs`, `scripts/guard-sim-fabrication.ps1` |
| The guard's own bite proof still holds after the retirement | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~SimFabricationGuardTests"` | `Passed: 4, Failed: 0, Total: 4` | — |
| The three tests that used the rewind move the clock instead | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --no-build --nologo` | `Failed: 2, Passed: 286, Total: 288` (4 m 37 s) — the two reds are the pre-existing RS-F21 fixture drift, unchanged | `gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs`, `gk-core/tests/FusionRpg.E2E.Tests/ContractE2ETests.cs` |
| The store test that used the rewind is already gone (5a) | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --nologo --filter "FullyQualifiedName~ExpeditionStoreTests"` | `Passed: 8, Failed: 0, Total: 8` | `gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs` |
| The route's removal breaks nothing in the server's own suite | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --nologo` | `Passed: 830, Failed: 0, Total: 830` (11 m 57 s) | — |

**The mechanism, in one line each.**

- `IClockControl` — the host owns the clock, so the runner hands it the value instead of reaching it over
  HTTP; with no control the run is **refused by name** (D3 (b): the untestability is the finding).
- `clock.set` — a sixth step shape: an absolute offset from the machine clock, required, and it may name no
  route. The validator refuses both a missing amount and a route.
- in-process — `RpgApiFactory.ClockControl` applies it to the seam in place.
- real process — `ProcessHostClockControl` **owns the host's whole lifecycle**: it starts the first process
  itself (always `DeleteDataDirOnDispose: false`, because the directory is the world a reboot must find) and
  a movement stops it and reboots it on the **same data dir and same port**, so the caller's `HttpClient`
  stays valid. A failed reboot leaves no half-alive host, and `DisposeAsync` still removes the directory.
- start of run — `ScenarioRunner` resets the host to the scenario's declared boot offset before the first
  step, so `--double-run` cannot inherit the previous run's movement.

**One allowlist entry deliberately stays, and says why.** `test.expedition.due` remains in the RS4 guard's
*op* allowlist: `gk-core/tests/FusionRpg.Guard.Tests/SimFabricationGuardTests.cs:76` plants a scenario using that op
to exercise the **notes** rule, and the guard only reaches that rule when the op is allowlisted — and that
test file is a pipeline-protected path this lane may not edit. The op is out of the closed vocabulary, so the
same planted scenario is refused as not-in-the-closed-table as well; the reason is written beside the entry.

## The guard caught a newly landed ambient read (2026-09-23)

After the merge, `run-guards.ps1 -Tier ci` turned `clock-seam` **red** — on a file this lane never touched:
`gk-fusion/src/FusionRpg.Injector/Effects/LawnExhaustionLifecycle.cs:87`, a new Injector file from the merged
`lawn-playable` lane, passing `DateTimeOffset.UtcNow` into `ExhaustionPolicy.Sync`.

That is the guard doing exactly what it was built for: a rule that only ever sees the tree it was written
against would have missed the first new read to land after it.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The guard fails on a read that landed after it was written | `python gk-core/scripts/guard-clock-seam.py` | exit 1, naming `LawnExhaustionLifecycle.cs:87` | `gk-core/scripts/guard-clock-seam.py` |
| The site is a STAMP, so it migrates rather than being allowlisted | read: `ExhaustionPolicy.Sync(..., DateTimeOffset now)` passes `now` to `StatusRuntime.Apply` with `BaseDuration: 0` (`gk-core/src/FusionRpg.Core/Actions/Cost/ExhaustionPolicy.cs:120-135`) — the status persists until `ClearGrant` and never expires, so no deadline comparison is involved | `ServerClock.UtcNow`, plus `using FusionRpg.Core.Time;` | `gk-fusion/src/FusionRpg.Injector/Effects/LawnExhaustionLifecycle.cs` |
| Green again, with the same reading as before | `python gk-core/scripts/guard-clock-seam.py` | `source files=1502 ambient reads=21 (clock type=2, allowlisted=19, entries=19) \| simulation-tree ServerClock references=0` — `CLOCK SEAM GUARD OK` | — |
| The Injector build still cannot run here | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD SKIPPED — no MelonLoader game dir` | — |

# The clock seam — `clock-seam` (rpg-simulator RS3)

**Module id:** `clock-seam` (capability map [rpg-simulator-map.md](rpg-simulator-map.md), the clock row).
**Program:** `rpg-simulator`. Plan: `tasks/rpg-simulator-plan.md` (Wave 5). Todo: `tasks/rpg-simulator-todo.md` (RS3).
**Owner rulings this spec implements:** **B1 (a)** full `TimeProvider` migration · **B2 (b)** the clock is
**product surface**, not a test-only seam · **B3 (a)** retire `ForceExpeditionDue`.
**Binding row:** [decisions.md](decisions.md) — *"The server can be told what time it is — product surface,
not a test seam"*.
**Consumes it:** `world-continuity`'s `hibernation-clock` ([world-continuity-map.md](world-continuity-map.md) §2,
module table row 2) and `idle-world` (row 9).
**Machine:** `gk-core/src/FusionRpg.Core/Time/ServerClock.cs` (new).
**Tests:** to be written with the machine.

> **Where this document lives, and why.** The map promises
> `docs/architecture/rpg-simulator/spec-clock-seam.md`. The delivery lane's fence is
> `docs/architecture/rpg-simulator*`, which is a *file prefix*, not that directory, so this spec is a
> sibling of the program's other documents (`rpg-simulator-idea.md`, `rpg-simulator-map.md`,
> `rpg-simulator-shape-idea.md`) and the map's clock row points here. The same class of erratum as
> **RS-F5** in `tasks/rpg-simulator-todo.md`; the map row was repointed in the same commit as this file.

---

## 0. Erratum found while implementing: `TimeProvider` does not exist in this Core (2026-09-23)

**Measured, not assumed.** `FusionRpg.Core` and `FusionRpg.Contracts` target **`net6.0`**
(`gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:3`, `gk-core/src/FusionRpg.Contracts/FusionRpg.Contracts.csproj:3`);
`FusionRpg.Data` and `FusionRpg.Server` target **`net8.0`**. `System.TimeProvider` ships in **.NET 8**, so
it does not exist in the two assemblies 142 of the 213 sites and every `FusionRpg.Injector` consumer
compile against. Core stays `net6.0` because the Injector is a Unity/BepInEx `net6.0` host and references
it.

**Consequence for owner ruling B1 (a) (*full `TimeProvider` migration*).** The ruling's *intent* — every
ambient clock read becomes one injectable read — is unaffected and is what the rest of this document
specifies. Its *mechanism*, `System.TimeProvider` as the seam's stored type, cannot be executed in Core as
written. Two shapes can, and the choice is a ruling, not a lane's call:

| Shape | What it is | Cost |
|---|---|---|
| **A — multi-target Core (`net6.0;net8.0`)** and store a `TimeProvider` behind `#if NET8_0_OR_GREATER`, with a `Func<DateTimeOffset>` fallback on `net6.0` | Closest to B1's wording; net8.0 consumers (Data, Server, and any net8.0 test) get the real `TimeProvider`, including `FakeTimeProvider` | One type with two compiled shapes, and a `net6.0` build that must stay green for the Injector — two code paths a future edit can drift between |
| **B — one `net6.0`-safe seam: `ServerClock.UtcNow` backed by a `Func<DateTimeOffset>` configured once, plus a `TimeProvider` *overload* on `net8.0`** | One shape everywhere, no `#if`; `TimeProvider` is accepted as an *input* (`Configure(TimeProvider)`), never stored | B1's wording reads as "the stored type is `TimeProvider`"; this shape says the stored type is a delegate and `TimeProvider` is an adapter. That is a real difference and must not be smoothed over |

**Until that is ruled, increments 1 and 2 do not start.** The seam's *product shape* — one configured
read, one reported declaration, one offset, the exclusions — is independent of the answer and is settled by
this document. Filed as **RS-F13** in `tasks/rpg-simulator-todo.md`.

### 0.1 The ruling the increments ran under — **shape B** (2026-09-23, lane `sim-t3-2`)

The delivery lane `sim-t3-2` was granted the whole migration surface and instructed to implement the
conservative shape (**B**) unless the owner ruled **A** first. No shape-A ruling arrived, so **shape B is
what landed**, and it is recorded here so a later reader sees why the mechanism differs from B1 (a)'s letter
while its intent holds.

What shape B is, concretely, in the code that shipped:

- `FusionRpg.Core.Time.ServerClock` stores **one `Func<DateTimeOffset>`**, configured once
  (`Configure(Func<DateTimeOffset>, long offsetSeconds = 0)`), with `Reset()` for host teardown and tests.
- **A `TimeProvider` is an input, never a stored type**: a net8.0 composition root adapts its own read
  (`ServerClock.Configure(timeProvider.GetUtcNow)`). There is therefore **no `ServerClock.Current`**
  property — a `net6.0` assembly cannot name `TimeProvider` at all — and a net8.0 site that needs a
  `TimeProvider` for `Task.Delay`/`ITimer` keeps its own DI-provided one. Those are delay *mechanisms*,
  and §7 already rules the wait loops that use them unsimulatable.
- **Two accessors, one read** (a measured addition to §3's shape). `ServerClock.UtcNow` returns
  `DateTimeOffset`; `ServerClock.UtcNowDateTime` returns the same configured read as a UTC `DateTime`.
  The second exists because **165 of the 213 sites emitted `DateTime.UtcNow.ToString("o")`**, whose
  round-trip form ends in `Z`, while a `DateTimeOffset` round-trip ends in `+00:00`. Swapping the type at
  those sites would have changed an emitted string — a behaviour change dressed as a migration. Both
  accessors derive from the one configured delegate, so the value stays single-sourced.
- **RS-F12's hole is closed from the guard side, not the purity-scan side.**
  `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs` bans clock/RNG symbols by name, and adding
  `ServerClock` to `BannedSymbols` is the fix RS-F12 names — but `gk-core/tests/FusionRpg.Guard.Tests/**` is a
  pipeline-protected path and refused the write from this lane. The same rule therefore ships as rule 2 of
  `gk-core/scripts/guard-clock-seam.py` (unbuilt as of this commit — RS-F10 owes it; a CI-gating guard, a path this lane's grant covers): **no `ServerClock`
  reference may appear under `gk-core/src/FusionRpg.Core/{World,Battle,Effects}`**, which is exactly the hole
  RS-F12 describes. The C# `BannedSymbols` addition remains owed and is recorded as a finding.

**The second erratum this spec carries (also measured):** the world-simulation purity scan
(`gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs`) bans `DateTime(Offset).UtcNow`,
`Stopwatch`, `Environment.TickCount` and `System.Random` in `gk-core/src/FusionRpg.Core/{World,Battle,Effects}` by
**symbol**, with exactly one named exemption (`SystemEffectClock`). A new seam name is *invisible* to that
scan, so putting `ServerClock` in Core without teaching the scan the name would let a `Core/Effects` wall
clock read slip through the gate that exists to catch it. The scan's `BannedSymbols` must gain
`ServerClock` in the same change as the type. Filed as **RS-F12** (`gk-core/tests/FusionRpg.Guard.Tests/**` is
outside this lane's paths).

---

## 1. The one sentence the whole seam obeys

> **The server's wall clock is an INPUT, not an ambient fact.**

Every rule below is that sentence made mechanical. One value is read from one place; nothing else in
`src/` reads the machine clock; and the value is reported, so a pasted artifact says what time the server
thought it was.

## 2. Why this is product surface (and what that obliges)

Owner ruling **B2 (b)** overturned the lane recommendation: the seam is **product**, not a test capability.
The ruling's two product behaviours are the justification, and both are wall-clock reads a *player* can
already reach:

1. **A player can move their machine clock.** Nothing stops it, so the server must treat "now" as input and
   compute every duration-derived decision from one value. Today 213 call sites each read the ambient clock
   independently, so a moved clock is seen by *some* subsystems and not others inside one request — the
   incoherent middle that a single seam removes.
2. **Hibernating worlds catch up lazily** on read (`world-continuity-map.md:62-69`). The catch-up is
   performed at read time, so "now" is a product input to a product read, not a test hook.

What "product surface" obliges, concretely — and this is the part that would be lost if the seam were a
SIM flag:

| Obligation | Shape |
|---|---|
| **Named** | One type with a name a reader can find: `FusionRpg.Core.Time.ServerClock`. Not a bool, not a hidden static on a store. |
| **Documented as product** | This document, the runbook's clock row, and the `/health` field below. |
| **Reachable without a SIM build** | Configured at the composition root and reported by `/health` on every build. It is **not** behind `SimFlags.Enabled`; a release build compiles and runs it. |
| **Declared in a verdict** | Every scenario verdict prints the clock declaration (`gk-core/tools/RpgSim/readback-verdict.md` §1, `clock`). A run that does not say what time the server thought it was cannot be compared to another run. |
| **The refusal it protects still works** | See §7's trap: the sim's own "a live injector is connected" refusal reads a *freshness window*, so a simulated clock must not silently disable it. |

**The product configuration surface** (this spec's decision, taken from B2 (b), and the one thing here that
wants the owner's eye): one signed offset, applied to the machine clock.

| Name | Meaning | Default |
|---|---|---|
| `FUSIONRPG_CLOCK_OFFSET` | A signed offset in seconds added to the machine clock (e.g. `-3600`, `86400`). Read once at the composition root, reported by `/health`, and **never** accepted from a route. | `0` (the machine clock) |

A route that sets the clock is deliberately **not** specified. Owner ruling **D3 (b)** stands: an
unreachable condition is a finding, not a licence for a new route — and a clock-setting route would be a
player-reachable way to make every deadline in the game lie.

## 3. The shape

- **The stored type is one `Func<DateTimeOffset>`** (shape B, §0.1). The ruling asked for
  `System.TimeProvider`; the BCL type is the net8.0 **input** form, adapted at the composition root. The
  shape of the seam is what matters and is unchanged: **one configured read**, `ServerClock.UtcNow`, and no
  site reading the ambient clock directly. The seam is the *configuration and the discipline*, not a bespoke
  interface.
- **One configured read**, `ServerClock.UtcNow` / `ServerClock.UtcNowDateTime` (one delegate, two typed
  accessors — §0.1), configured exactly once from the composition root
  (`gk-core/src/FusionRpg.Server/Program.cs`). A net8.0 host hands it a `TimeProvider` by adapting that provider's
  own read; there is no stored `TimeProvider` and no `ServerClock.Current` (`net6.0` cannot name the type).
- **Why a configured-once provider rather than per-call injection.** `FusionRpg.Data` holds 142 of the 213
  sites (measured, §5) and cannot depend on the Server's DI container; per-call injection would be a
  213-signature change that still could not reach a store-internal helper. The precedent is `SimFlags`
  (env-configured, read at the composition root) — the difference is that this seam is product surface, so
  it is named and reported rather than hidden. This is the one place a static is the *cheaper* design, and
  it is chosen with the cost named rather than stumbled into.
- **What MAY read it:** stamps (`*Utc`/`*At` columns and event envelopes), durations and windows
  (expedition `due_utc`, idle credited window, heartbeat freshness), accrual (background yield's 500-hour
  cure), and any due-date comparison.
- **What MUST NOT read it:** the deadline and wait loops in §7, and any decision whose *purpose* is to
  observe the real world (freshness of a live process, elapsed wall time of a benchmark).

## 4. The boundary with `hibernation-clock` — the agreement this spec owes

`world-continuity`'s `hibernation-clock` is **not** a wall clock, and this seam must not be mistaken for one.
The boundary, stated so neither module can drift into the other:

| Question | Answer | Owner |
|---|---|---|
| How many hibernation turns are pending? | `pending = saveTurnCounter − sleptAtTurn`, capped by `catch_up_cap` | `hibernation-clock` (turn counter, **never** a wall-clock difference) |
| How much of a hibernating world's catch-up is credited on read? | A budget read from the same counter and `catch_up_cap` (a structural bound, commented, with its `ssot-power-scale.md` §11 row) | `hibernation-clock` |
| What is "now" for an idle world's pro-rated window, an expedition's due time, or a 500-hour yield accrual? | `ServerClock.UtcNow` | **this seam** |
| May a simulated clock change `pending`? | **No.** Pending turns are a subtraction of two stored counters; the clock is not an input to it. | this seam's rule |

**Ask to `world-continuity` — ANSWERED 2026-09-23 (lane `sim-t3-2`), from their spec and my guard rather than
from a reply, because the module is not built.** The honest answer splits in two:

1. **Pending turns — confirmed, and there is no wall-clock read to confirm because the module is a declared
   gap.** `docs/architecture/world-continuity/spec-hibernation-clock.md` §3 defines
   `Pending(saveEndTurns, clockMark, catchUpCapTurns)` as a **pure** function, and its §6 says so outright:
   *"`Pending` is pure and reads no clock; the Core file sits under the world determinism guard's scan root."*
   Its own summary table puts **"save counter, clock mark, pending"** under **Real gap** and
   `catch_up_cap` / `turn_period_seconds` under **Wiring gap — never read**;
   `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:28-29` declares those two columns and nothing reads them
   (`grep -rn "GetPendingTurns\|clock_mark\|end_turns" src/ --include=*.cs` returns nothing). So the first half
   of the ask becomes a **constraint re-armed for when it lands**: pending stays a subtraction of two stored
   counters, and the clock is never an input to it. Filed as **RS-F26** for that module's owner.
2. **Duration pro-rating — already forced through the seam.** The idle window, the yield accrual and freshness
   belong to `idle-world` / `background-yield` (the module's own §2 puts *"idle worlds' wall clock"* out of
   scope), and those are specs whose code has not landed either. **Whatever duration pro-rating exists in
   `src/` today already goes through `ServerClock`** — that is this migration's contract, and
   `gk-core/scripts/guard-clock-seam.py` fails CI on any new ambient read, so the seam cannot be bypassed when they
   land. The answer is therefore a *mechanism*, not a promise.

**Consequence for the plan:** the `idle-world` and `background-yield` increments were recorded as waiting on
this answer. They are not waiting any more — they are waiting on their own code, with the seam's constraint
enforced by the guard rather than by this agreement.

## 5. The measured surface (this lane's own count, 2026-09-23)

Binary-safe scan of `src/**/*.cs` (the file that defeated `grep` is
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs`, which holds raw NUL bytes):

| Module | `DateTime.UtcNow` | `DateTimeOffset.UtcNow` | total |
|---|---|---|---|
| `FusionRpg.Data` | 111 | 31 | **142** |
| `FusionRpg.Server` | 36 | 5 | **41** |
| `FusionRpg.Injector` | 13 | 6 | **19** |
| `FusionRpg.Core` | 2 | 6 | **8** |
| `FusionRpg.Launcher` | 2 (`+1 DateTime.Now`) | 0 | **2** |
| `FusionRpg.CheatCore` | 1 | 0 | **1** |
| **total** | **165** | **48** | **213** |

`TimeProvider` appears **0** times in `src/`. The `decisions.md` row carries lane `sim-idea-b`'s count of
**203 call sites** (Data 142 · Server 38 · Injector 17 · Core 3 · Launcher 2 · CheatCore 1). The two counts
disagree by 10 and the disagreement is a *measurement*, not a defect: this table counts **occurrences**
including ones inside comments and format strings, while the row counts **call sites**. Per module the two
agree on Data exactly (142) and differ elsewhere by a handful. The migration is complete when a guard over
`src/` reports zero ambient reads outside `ServerClock` — a contract, never a pinned number.

## 6. Migration order, and the bypass retirement

Each increment is its own commit with its own verification (`verify-change.py -Paths <files>`), because a
203-site sweep that lands as one commit cannot be reviewed or bisected.

| # | Increment | Files | State |
|---|---|---|---|
| 0 | **This spec** | `docs/architecture/rpg-simulator-spec-clock-seam.md`, the map's clock row | **this commit** |
| 0b | **The §0 erratum ruled** (shape A or B) | `tasks/rpg-simulator-todo.md` (RS-F13), `docs/architecture/rpg-simulator-spec-clock-seam.md` §0.1 | **done — shape B** (2026-09-23, lane `sim-t3-2`). RS-F12's `BannedSymbols` half is refused (guard tests are a protected path) and ships instead as rule 2 of `gk-core/scripts/guard-clock-seam.py` (unbuilt as of this commit) |
| 1 | `ServerClock` (new) + the `FusionRpg.Core` sites (2 real; 6 of the 8 occurrences are prose) | `gk-core/src/FusionRpg.Core/Time/ServerClock.cs` (new), `SimEngine.cs`, `Diagnostics/PerfProbe.cs`, `gk-core/tests/FusionRpg.Core.EffectClock.Tests/Time/ServerClockTests.cs` (new) | **done** — 2026-09-23, lane `sim-t3-2`; `ServerClockTests` 4/4 |
| 2 | `FusionRpg.Server` sites (33 real; the 6 deadline/freshness sites of §7 stay raw), including the composition-root `Configure` | 12 Server files | **done** — 2026-09-23, lane `sim-t3-2`. `Program.cs` reads `FUSIONRPG_CLOCK_OFFSET` once and adapts `TimeProvider.System` into the seam. The `/health` clock field is still owed: `HealthDto` + `RpgStore.ToHealth` are outside the lane's paths (RS-F11) |
| 3 | `FusionRpg.Data` sites (140 real; the heartbeat window's read+write pair stays raw) | 48 Data files | **done** — 2026-09-23, lane `sim-t3-2`; `FusionRpg.Data.Tests` 1856/1857, the one red a documented pre-existing global-hub race (`empire-progression` F2), green in isolation |
| 4 | `FusionRpg.Injector` (11 real of 17 code reads) + `FusionRpg.Launcher` (0 migrated; 1 excluded) + `FusionRpg.CheatCore` (its 1 read retired, not migrated) | 9 files | **done** — 2026-09-23, lane `sim-t3-2`. CheatCore's one read is gone without a new reference (the stamp is passed in from `RpgStore`, because `guard-repo-boundary` B1 pins CheatCore to Contracts alone); the Launcher's local UI log stamp is an exclusion with a reason (§7, RS-F14); `EffectRuntime.cs`'s clock seed is an exclusion too (§7 — increment 4 tried sourcing it and **reverted**, because a guard test asserts that exact literal); the Injector build is **not run** locally (no game interop — the `injector-compile` guard SKIPs, as designed) |
| 5 | Retire `ForceExpeditionDue`'s `UPDATE` and re-point the corpus's `test.expedition-due` step at the seam | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs`, `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs`, `gk-core/tools/RpgSim/ScenarioVocabulary.cs`, `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` | **done** — 5a and 5b landed 2026-09-23, lane `sim-t3-2` (§6b). The store method and the route are **deleted**, the op is out of the vocabulary, and the corpus makes the expedition due with a `clock.set` declaration the host applies (in place in-process, by rebooting the real process). No store bypass replaced it |

**Retirement shape (owner ruling B3 (a)).** `ForceExpeditionDue`'s `UPDATE` rewrites `due_utc` in the
database — a store bypass that rewrites time, which the `decisions.md` row forbids going forward. The seam
replaces it without a bypass: an expedition is due when `ServerClock.UtcNow >= due_utc`, so a declared clock
offset makes it due *without writing anything*. The scenario's step stays a route (the scenario format
forbids computing a time), so the route becomes a thin product-shaped statement of the clock declaration —
and if no such route is honest, the step is removed from the corpus and the finding recorded (D3 (b)).

### 6a. ERRATUM, measured while implementing increment 5 (2026-09-23, lane `sim-t3-2`)

**A declared clock offset cannot make an expedition due.** This paragraph's premise above is wrong, and the
measurement is short:

- `DispatchExpedition` writes `due = now.AddMinutes(tier.DurationMinutes)` from the same seam read
  (`RpgStore.Expeditions.cs:82-84`), and `ExpeditionService.CollectAsync` refuses while `now < due`
  (`ExpeditionEndpoints.cs:90-92`). Both read `ServerClock.UtcNow`, so a **single, static** offset moves both
  sides together and the gap is always the tier's duration. The shortest tier is **30 minutes**
  (`gk-core/data/tuning/expeditions.v1.json`), so nothing the seam can be *configured to* makes an expedition due
  inside one run.
- **A mid-run clock movement is the only mechanism**, and it is unreachable today: `ScenarioRunner` reaches
  its host over **HTTP only** (`gk-core/tools/RpgSim/ScenarioRunner.cs` — one `HttpClient`, both hosts), a route that
  sets the clock is deliberately **not specified** (this spec's §2; owner ruling D3 (b)), and the server's
  offset is read once at the composition root from the environment.
- **Three existing test files depend on the rewind** and have no replacement: `ExpeditionStoreTests.cs:141`,
  `ExpeditionE2ETests.cs:70,125` (dispatch → force-due → collect → real battles → rewards),
  `ContractE2ETests.cs:173`. The store test could use the store's own `utcNow` parameter, but the two HTTP
  E2E tests need the clock to move *during* the test, and their only alternative today is a process-global
  `ServerClock.Configure` mutation from a test — the same hazard class as the documented
  `ProgressionTuningHub` flake (`tasks/empire-progression-todo.md:1272`, finding F2), which this lane will
  not multiply without a ruling.

**Filed as RS-F16** (`tasks/rpg-simulator-todo.md`), with the two candidate fixes named there:
| Candidate | What it is | Cost |
|---|---|---|
| **boot-time clock plumbing** | the in-process host factory and the process host accept the scenario's declared offset (`ServerClock.Configure` / `FUSIONRPG_CLOCK_OFFSET`); store tests use the store's `utcNow` parameter | small, and it makes `clock.mode: offset` honest for both hosts — but it does **not** make the corpus's collect half reachable |
| **a mid-run clock input** | the runner stops and reboots the process host on the same data dir with a new offset, and the in-process host applies it in place; a scenario step declares the movement | larger, and it is the only shape that reaches a due expedition honestly |

### 6b. RS-F16 RULED, and increment 5a landed (2026-09-23, lane `sim-t3-2`)

The owner ruled **candidate (1) first, then candidate (2)** (`f49cd83b4`), so increment 5 lands in two
steps, each its own commit.

**5a — landed.** A scenario may declare `clock.mode: offset` with `offsetSeconds`, and BOTH approved hosts
apply it **at boot** through the one seam:

| Piece | What changed |
|---|---|
| `ScenarioClock` | gains `offsetSeconds`; the validator accepts `offset` (requires the field), refuses `explicit` by name, and refuses an `offsetSeconds` on an `ambient` run |
| in-process host | `RpgApiFactory(clockOffsetSeconds)` sets `FUSIONRPG_CLOCK_OFFSET` before the host builds, configures the seam directly (its `SeedSpeciesRoster` builds a store before `Program.cs` runs), and gives the process clock back on dispose |
| real process | `ProcessHostOptions.ClockOffsetSeconds` → `FUSIONRPG_CLOCK_OFFSET` on the child; the variable is **removed**, never zeroed, when there is no offset, because the child inherits this process's environment |
| CLI | `--host process` passes the declared offset; `--base-url` **refuses** an offset scenario by name — a host this tool did not boot cannot be told the clock |
| store test | `ExpeditionStoreTests.Force_due_rewinds_the_timer` becomes `A_dispatch_stamped_in_the_past_is_due_without_rewriting_the_row`, which uses the store's own `utcNow` input — the ruling's explicit step, and one of the three dependencies on the bypass removed |

**Measured** (`gk-core/tests/FusionRpg.E2E.Tests/RpgSimClockOffsetTests.cs`, the corpus with its clock block
rewritten to `offset 3600s`): both hosts run it `ok=True` with `clock='offset 3600s — …'` in the verdict, the
declared digest unchanged (`daa9df408054f32e…`), and the offset **visible on a real row** — `dispatchedUtc`
and `dueUtc` are 55–65 minutes ahead of the machine clock. The tier duration is deliberately NOT asserted
there: the corpus still carries the rewind, so `due − dispatched` is the bypass's shape, not the tier's.

**5b — LANDED.** The mid-run input, which is what actually retires the bypass:

| Piece | What changed |
|---|---|
| `IClockControl` | the host owns the clock, so the runner never reaches it over HTTP: it hands the value to the control the embedding host supplied, and **refuses the run by name** when there is none (D3 (b) — the untestability is the finding, never a silent no-op) |
| `clock.set` step | a sixth step shape: an ABSOLUTE offset from the machine clock, required, and it may name no route. The validator refuses a missing amount and a route; the runner applies it through the control |
| in-process control | `RpgApiFactory.ClockControl` applies the offset to the seam in place — no process to reboot |
| real-process control | `ProcessHostClockControl` **owns the host's whole lifecycle**: it starts the first process itself (always `DeleteDataDirOnDispose: false`), and a movement stops the process and reboots it on the **same data dir and same port** with a new `FUSIONRPG_CLOCK_OFFSET`, so the caller's `HttpClient` stays valid. `DisposeAsync` is the one place that removes the directory |
| start-of-run reset | `ScenarioRunner.RunAsync` sets the host to the scenario's declared BOOT offset before the first step, so `--double-run` (or any second run on the same host) does not inherit the first run's movement |
| retirement | `RpgStore.ForceExpeditionDue` is **deleted**, `/api/test/expedition-due` is gone (`MapExpeditionTest` is an empty mapper with the removal recorded in place), `test.expedition.due` is out of the closed vocabulary, and the corpus's step is a `clock.set` |
| the three dependent tests | `ExpeditionE2ETests` (×2) and `ContractE2ETests` move the clock through `RpgApiFactory.WithClockAheadAsync`, which gives the process clock back in a `finally` — the same declaration a scenario's `clock.set` makes |

**Measured:** `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~RpgSim"` →
`Passed: 48, Failed: 0, Total: 48` (5 m 32 s), which now includes the corpus running its `clock.set` step on
the in-process host AND on a real process **that reboots mid-run**, the two offset tests, and the format
contract. The guard's own reading moves with the retirement: `test.* steps=1` (was 2) and
`/api/test handlers=12 (take RpgStore: 11, allowlisted: 11)` (was 13/12/12) — the route and its allowlist
entry are gone together, with no stale entry left.

**One entry deliberately stays, and says why.** `test.expedition.due` remains in the RS4 guard's *op*
allowlist, because `gk-core/tests/FusionRpg.Guard.Tests/SimFabricationGuardTests.cs:76` plants a scenario using that
op to exercise the **notes** rule, and the guard only reaches that rule when the op is allowlisted — and that
test file is a pipeline-protected path this lane may not edit. The op is out of the vocabulary, so the same
planted scenario is refused as not-in-the-closed-table too; the reason is written beside the entry.

**The CLI:** `--host process` forwards the declared boot offset and owns the rebootable control; `--base-url`
refuses a boot offset by name, and a `clock.set` step against a host the tool did not boot is refused by the
runner with the reason in the verdict.

## 7. The exclusions — the deadline and wait loops that MUST NOT be simulated

Nine sites measured; each carries its reason. A simulated clock here does not test the feature, it falsifies
the measurement. Those inside this lane's fence are listed first.

| Site | Why it must not be simulated |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1206-1210` — `InjectorConnected` / `LiveInjector`, a 5-second heartbeat freshness window | **The trap, and a safety one.** Shift the clock forward and a *live* injector looks stale, so `LiveInjector` goes false and the sim runner's own refusal ("a live injector is connected", owner ruling D1 (b), `SimService.Guard()`) stops firing — a scenario could then run against a player's install. Shift it backward and a dead injector looks alive. A simulated clock must never reach this comparison. |
| `gk-core/src/FusionRpg.Server/DebugEndpoints.cs:1076-1077` — snapshot deadline loop | Waits for a real board snapshot from a real injector. The deadline is a bound on a *live process*; a simulated clock makes the loop exit instantly (never tested) or spin for ever. |
| `gk-core/src/FusionRpg.Server/DebugEndpoints.cs:1790-1791` — deadline loop | Same class: a bound on a live process, not a game duration. |
| `gk-core/src/FusionRpg.Server/WebMatchService.cs:451` — `t0` elapsed marker | Measures how long the real match resolution took. Simulating it turns a perf reading into a number the sim chose. |
| `gk-fusion/src/FusionRpg.Injector/Hud/OverlayViewHost.cs:327-328` — UI wait deadline | A bound on a frame-driven wait inside the game. Shifting it changes what the player sees, and the loop's `done()` predicate is real engine state. |
| `gk-fusion/src/FusionRpg.Injector/CheatState.cs:760` — probe-timeout window | A freshness window over a live probe. Same class as the `RpgStore` trap. |
| `gk-fusion/src/FusionRpg.Launcher/Services/HealthMonitor.cs:58-59` — server-start deadline | A bound on a process that is starting. A simulated clock either skips the wait or waits for ever. |
| `gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs:46` — `UtcNow => _now` | **Already injectable**, and correctly so: this is the effect runtime's own monotonic-ish clock fed by its host. It is the precedent for the seam, not a site to migrate; it may be *sourced* from `ServerClock` at the injector's composition root (increment 4). |
| `gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs:475` — elapsed from `_clock.UtcNow` | Same: an elapsed measurement inside the effect runtime, already injected. Migrating it would replace one injected clock with another and change nothing. |
| `gk-fusion/src/FusionRpg.Launcher/MainWindow.xaml.cs:399` — `var stamp = DateTime.Now.ToString("HH:mm:ss")`, the UI log's local time | **Measured addition (2026-09-23, lane `sim-t3-2`).** `FusionRpg.Launcher` references **no** FusionRpg project at all (its csproj carries no `ProjectReference`), so the seam is not reachable from it; `guard-repo-boundary`'s pinned graph does not name the Launcher either. The read is a **local UI log stamp** — not a duration, a deadline, or a persisted row — so routing it through the seam needs a Launcher → Core dependency decision first. Filed as **RS-F14**. |
| `gk-core/src/FusionRpg.CheatCore/CheatDocumentCodec.cs:18` — the `UpdatedAt` fallback | **Not an exclusion — retired.** `guard-repo-boundary` B1 pins `FusionRpg.CheatCore` to `FusionRpg.Contracts` alone, so CheatCore cannot read the seam. `FromEntries` now **requires** its `updatedAt` argument and the only production caller (`RpgStore.cs:2589`, which does have the seam) supplies `updatedAt ?? ServerClock.UtcNowDateTime.ToString("o")`. CheatCore therefore has zero ambient reads, with no new dependency. |
| `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs:42` — the effect runtime's clock seed | **Allowlisted, not migrated.** SPEC 7 already calls this site *already injectable, and correctly so*: it is the effect runtime's own clock, fed by its host. Increment 4 first sourced it from the seam (`new(ServerClock.UtcNow)`) and **reverted** in the same session, because `PlayerSpeciesMaterialiseCallerGuardTests` (`gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs:148`) asserts the literal `new(DateTimeOffset.UtcNow)` as the proof that the wall clock is still the SOURCE and that no round trip was added to the injector's hot path. That guard test is a pipeline-protected path, so re-pointing it is not a delivery lane's to do — and §7 says increment 4 *may* source it, never that it must. |

A site whose clock read is a **stamp** (an ISO string written to a row or an envelope) is *not* excluded —
that is the 143-site mechanical class and it is the bulk of the migration.

## 8. The guard, and this lane's fence

RS3's acceptance asks for "a guard that fails ambient `DateTime.UtcNow` in `src/` outside the one clock
type". The house home for that is `gk-core/scripts/guard-clock-seam.py` (new) plus a `clock-seam` row in
`gk-core/scripts/enforcement-registry.v1.json`.

**Landed 2026-09-23 (lane `sim-t3-2`).** `gk-core/scripts/guard-clock-seam.py` is wired the way every other
guard is: its own enforcement-registry row (`clock-seam`, `tier: ci`, `status: gating`), its own invariant
row (`pr-clock-seam`), and a `clock-seam-guard` verification boundary. It has **two rules**: rule 1 refuses
every ambient read in `src/**/*.cs` outside the one clock type and the 19 allowlisted exclusions (each with
its reason; a **stale** entry is itself a violation), and rule 2 refuses a `ServerClock` reference under
`gk-core/src/FusionRpg.Core/{World,Battle,Effects}` — the hole RS-F12 names, closed here because
`gk-core/tests/FusionRpg.Guard.Tests/**` is a pipeline-protected path.

The guard's own reading on the finished tree: **1478 source files, 21 ambient reads — 2 inside
`ServerClock.cs` and 19 allowlisted, 19 entries; 0 simulation-tree `ServerClock` references.** That is the
migration's completion contract (§5: "a contract, never a pinned number") read out loud: what is left is the
one clock type and the exclusions, each of which says why.

**Bite proof (a rule never seen to fail is not known to work), run against a planted fixture dir:**
`python gk-core/scripts/guard-clock-seam.py -SrcDir /tmp/clockplant` → exit 1,
flagging a planted ambient read in the throwaway fixture and a planted `ServerClock` reference under a
`FusionRpg.Core/Effects/` path (rule 2). (The fixture files are temp throwaways, never tracked.)

**Owed:** a C# bite test in `gk-core/tests/FusionRpg.Guard.Tests/**` is the house pattern, and that tree refused the
write from this lane (the same block that left RS-F12's `BannedSymbols` line owed) — so the planted-run proof
above is the evidence, and the test is filed with RS-F12's remainder.

**Not landed from this lane:** the orchestrator's pipeline guard refuses a new `scripts/guard-*.ps1`, and a
registry row without its script fails `EnforcementRegistryGuardTests.R1`. The guard therefore owed a fence
that may write under `scripts/guard-*.ps1` — **which this lane carries**; the historical note is kept so a
reader sees why the row was blocked before. The design is: scan `src/**/*.cs` for
`DateTime(Offset)?.UtcNow|DateTime.Now` outside the one clock type and outside the exclusions above (each
exclusion carrying its reason in the guard, the `guard-sim-fabrication` allowlist pattern).

## 9. NOT covered here

- **A route that sets the clock** — deliberately not specified (§2).
- **The seam's *stored* type** — §0's erratum; one of shape A or shape B, pending an owner ruling.
- **The purity scan learning the new name** — RS-F12; `gk-core/tests/FusionRpg.Guard.Tests/**` is outside this
  lane's paths, and the type must not land without it.
- **The 9 exclusions' code changes** — they are exclusions, not migrations; increment 4 may *source* the two
  already-injectable ones from `ServerClock` at their composition root.
- **`hibernation-clock`'s own turn-counter work** — `world-continuity`'s, per §4.
- **The Data / Injector / Launcher / CheatCore increments and the `ForceExpeditionDue` retirement** — the
  fence, not the design (§6).
- **A verdict that digests a timestamp.** Until the seam lands, the corpus declares `clock.mode: ambient` and
  every `*Utc`/`*At` field is excluded from the digest by name (`gk-core/tools/RpgSim/readback-verdict.md` §3). Once
  the seam lands, a scenario may declare `offset`/`explicit` and digest a timestamp for the first time.

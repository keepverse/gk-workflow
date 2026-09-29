# RPG feature simulator — the shape

**Status: idea / pre-spec. Reasoning trail, not a contract.** This document proposes nothing that
exists yet, and no code may be written against it before a spec does. It is the `sim-idea-b` half of
the 2026-09-22 owner directive (*"our work on this program dont use pvz much but a lot of rpg feature
and we lack of simulator"*); its sibling `sim-idea-a` surveys **what exists and what the simulator
must cover** — this one answers **what shape it should take**. Where the two overlap, this document
defers.

**Method.** `.agents/skills/idea-refine/SKILL.md`, three phases, labelled below.

**Which loops this extends.** None of the ten loops in [`docs/guide/the-loops.md`](../guide/the-loops.md).
This is **developer infrastructure for the RPG layer** — the same class as
[`data-test-substrate-ideal.md`](data-test-substrate-ideal.md) §"Which loop this extends" and
[`test-verification-boundary-ideal.md`](test-verification-boundary-ideal.md). It adds no loop, stock,
class, clock, or fiction.

Read first, per [`DESIGN-GATE.md`](../DESIGN-GATE.md) §1: the rows for **Standalone / web RPG**
(`:63`), **Proving a feature works live** (`:64`), **Match / actor lifecycle** (`:54`), and §2's
invariants — in particular **9 (standalone-first, `:101`)** and **1–2 (two async systems,
record-then-drain)**. The single most load-bearing invariant for this document is that the RPG works
**from past events, never current game state** (§2.1): that is what makes a synthesized event stream an
*input* rather than a fabrication, and §3.4 below turns on it.

---

# 1. Phase 1 — Understand & Expand

## 1.1 The problem, restated

**How might we let an RPG feature be driven through N player-days of real server behaviour — several
systems in sequence — and have the result be a reproducible artifact, without a running lawn game, a
human clicking, or waiting for wall-clock time?**

Today the honest answer to *"does this RPG feature work end to end"* is one of two things: a unit test
of the domain function, or the live game. Everything between them is a per-program invention, and the
inventions disagree with each other about what "end to end" means.

## 1.2 Who this is for

- **Primary: the agent and the owner doing verification.** `sim-idea-a` owns the inventory; this
  document assumes its finding — that most of the RPG surface has no way to be exercised across
  several systems at once.
- **Not the player.** A simulator is not a feature. Nothing here changes what a player sees. The one
  place this brushes a product capability is the clock (§2.3), and that is called out as a decision
  rather than a side effect.
- **Success, stated so it can fail:** a feature family is exercised by a **scenario file** that a
  reviewer can read, producing a **verdict** read back through the same query path the web frontend
  uses, plus a **digest** that is identical on a second run and on a second machine — and *not*
  requiring the game, the owner, or a stopwatch.

## 1.3 What already exists — this is a three-quarters-built simulator

The most important finding of this lane. The pieces exist; they are not joined.

### The input side — a fake injector already speaks the real protocol

| Thing | Where | What it already is |
|---|---|---|
| Sim mode flag | `gk-core/src/FusionRpg.Server/SimFlags.cs:7` reading `RpgConstants.SimEnvVar` (`gk-core/src/FusionRpg.Contracts/Dtos.cs:257`, `"FUSIONRPG_SIM"`) | One env var switches server behaviour |
| Sim service + engine | `gk-core/src/FusionRpg.Server/SimService.cs:9`, `gk-core/src/FusionRpg.Core/SimEngine.cs:9` | A server-side board simulation with **no Unity**; publishes synthesized `EventEnvelope`s into the real ingest (`SimService.Publish`, `SimService.cs:76` → `EventIngest`) |
| The sim API | `gk-core/src/FusionRpg.Server/SimEndpoints.cs:13` (`/api/sim`), **54 routes** | The complete lawn-side event vocabulary: `board/start`, `match/win`, `wave`, `plant/spawn`, `plant/damage`, `plant/die`, `zombie/*`, `card/*`, `sun/*`, `mower/*`, shield, travel, prize … |
| The test API | `gk-core/src/FusionRpg.Server/SimEndpoints.cs:129` (`/api/test`) | `reset` (`:136`), `snapshot` (`:144`), `probe` (`:166`), three `seed-*-demo` fixture writers (`:184`, `:218`, `:240`) |
| Effect sim API | `gk-core/src/FusionRpg.Server/SimEffectEndpoints.cs:12` (`/api/sim/effect`), 6 routes | Grant / withdraw / fire / scenario / snapshot against `SimEffectHost` |
| Gate | `gk-core/src/FusionRpg.Server/Program.cs:2050` gates `/api/sim` + `/api/test` on `SimFlags.Enabled`; `:2053` maps `/api/sim/effect` **unconditionally** | Two different exposures — see §3.4 |
| Sim heartbeat | `gk-core/src/FusionRpg.Server/SimHeartbeatHost.cs:24` (2 s `PeriodicTimer`) | A sim-mode server can already run as a long-lived process |
| Reset contract | `gk-core/src/FusionRpg.Server/SimService.cs:57` (`FullResetAsync`) | Flush → stop hello → reset engine → reset store |

### The determinism side — four independent idioms, none of them joined up

| Thing | Where | The idiom |
|---|---|---|
| Pure battle resolve | `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs:15` | *"No I/O, no clock, no ambient state: same setup + seed + platform ⇒ byte-identical report"*; per-system RNG streams at `:22` |
| Pure expedition resolve | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:41` | `(tier, squad, seed, elapsedTicks)` → outcomes; every tick derives its own stream so recall pro-rates exactly |
| Offline effect kit | `gk-core/src/FusionRpg.Core/Effects/FoundationHarness.cs:11` | `FakeEffectClock` + `SeededEffectRandom` + `RecordingEffectSink`; *"never opens PVZ"* |
| Declarative scenario files | `gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:80`; envelope + step DTO at `:10-60`; the **18-case closed op switch** at `:178-327`; 49 fixtures under `gk-core/tests/fixtures/effects/scenarios/` | JSON op-lists with `expectPlan` / golden asserts, over a **closed** op vocabulary — and, critically, **`advanceMs`/`advance` (`:229`) moves a harness-owned `FakeEffectClock`**: the repo has already proven a scenario-driven fake clock, at bag scope |
| Battle-local clock | `gk-core/src/FusionRpg.Core/Battle/Timeline/SimulationClock.cs:84` | Integer ticks, *"it cannot read the wall clock"* — but it is per-battle |
| Digest hash | `gk-core/tools/SquadHarness/DeterminismHash.cs:19` | SHA-256 over canonical JSON, provenance blanked (`Artifacts.cs`'s `at` field) |
| Balance tooling | `gk-core/tools/CombatSim/README.md:6-8` | **"The one rule"**: *"This tool contains no combat math"* — drive the real entry point or don't cover it |

### The host side — three ways to run the server, already in use

| Shape | Where | Measured reach |
|---|---|---|
| In-process full boot (`TestServer`) | `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:9` (`WebApplicationFactory<Program>`); roster seeded from the real corpus at `:34` | **47** E2E files use it |
| Real Kestrel on a free loopback port + real `HttpClient` | `gk-core/tests/FusionRpg.Server.Tests/Actions/SpecimenLoadoutEndpointsTests.cs:41-47` (`DataTestStore` + `WebApplication.CreateBuilder` + `UseUrls` + `StartAsync`) | **67** files under `gk-core/tests/FusionRpg.Server.Tests/**` use `UseUrls` |
| Real Kestrel + real SignalR transport | `gk-core/tests/FusionRpg.Server.Tests/ActorSheetHotLiveStateTests.cs:235` (`HubConnectionBuilder.WithUrl($"{_baseUrl}/hub/rpg")`) | In use |
| Real child process, real stdout | `gk-core/tests/FusionRpg.Server.Tests/RealRunCollectorTests.cs:16-30`; drain helper `gk-core/tests/FusionRpg.Core.Tests.Shared/TestSupport/ExternalProcess.cs:20` | In use (shells out a `.ps1`) |
| In-memory store | `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs:17`; source-linked into Server/E2E tests (`gk-core/tests/FusionRpg.Server.Tests/FusionRpg.Server.Tests.csproj:31`) | **311** test files reference it |

**So the missing piece is not capability — it is a driver and a contract.** The pieces above are
each owned by a different program (effects, balance, server tests, E2E) and each answers a different
question. Nothing today can say *"replay this scenario against this server and tell me whether the
outcome was the same as last time."*

## 1.4 The design space — five shapes, honestly priced

Divergent step. Five shapes, not three, because "the simulator" is really two orthogonal decisions —
**which host** and **who writes the script** — plus the two ends where the script's data comes from.

---

### Shape A — In-process host (extend `RpgApiFactory`)

A `WebApplicationFactory<Program>` boot in the test process; the driver is a test.

| | |
|---|---|
| **Coverage** | The whole **managed** server: DI, routing, `EventIngest`, hosted services, hub messages over `TestServer.CreateHandler()` (`gk-core/tests/FusionRpg.E2E.Tests/CatalogAndStressE2ETests.cs:262-268`), SQL against a temp data dir. Real domain, real persistence, real endpoint contract. |
| **Determinism** | **Good within the client, weak around it.** The client is in-process and sequential, but `NotificationBootCatchUp`, `EventIngest`, `CompactionWorker` and `UniqueActorDeployWatchdog` are `AddHostedService` background loops (`gk-core/src/FusionRpg.Server/Program.cs:532-535`) that tick on their own. "The run reached a stable state" has to be defined by polling, not by construction. |
| **Cost** | Lowest of the five. The harness exists; a scenario runner added to it is a test-project change, not a new binary. |
| **Makes impossible** | Real transport (`.github`-confirmed: `TestServer` has no WebSockets — dotnet/aspnetcore#11888, #31911, #42657). Real process lifetime: no crash, no kill -9, no restart-and-resume. A real `FUSIONRPG_DATA` lifecycle. And because it is a test, **a long run cannot live in the default suite** — anything over a few seconds is a tax on all 60 CI test projects (`grep -oE ... .github/workflows/ci.yml \| sort -u \| wc -l` → 60; note `AGENTS.md`'s "13 C# test projects" is stale against that). |

### Shape B — Headless server mode (a real `FusionRpg.Server.exe` in sim mode, driven over HTTP/SignalR)

| | |
|---|---|
| **Coverage** | Everything in A **plus** real Kestrel binding, real HTTP and WebSocket transports, real `FUSIONRPG_DATA` directory lifecycle, real process start/stop/restart, and — the reason this option exists — **long-running loops**. It is the only shape that can exercise `SimHeartbeatHost`, the compaction worker, the turn-notification pump, and a restart in the middle of a scenario. |
| **Determinism** | **Weaker by default, and this is the shape's real cost.** It inherits the same background hosted services as A, *plus* two new ambient sources: the wall clock (**203** `UtcNow` code call sites in `src/`, §2.3, with **no** repo-wide clock abstraction — the only `IEffectClock` at `gk-core/src/FusionRpg.Core/Effects/EffectModels.cs:74` is bag-local) and OS scheduling. Determinism here is **bought**, not found — see §2.3. |
| **Cost** | Medium-high. Every part is already proven in the tree (`UseUrls` + real port: 67 Server.Tests files; real `HubConnection`: `ActorSheetHotLiveStateTests.cs:235`; real child process: `RealRunCollectorTests.cs:16`), so the cost is the **driver** plus the clock work, not the host. |
| **Makes impossible** | Debugging at breakpoint speed. A cross-process run is a log, not a stack trace — A stays the inner loop for that reason, and this document recommends running both against the *same* scenario file. |

### Shape C — Scripted client / scenario layer

Not a host — the **driver** A and B both need. The question is what "a player plays for N days"
is written in.

| | |
|---|---|
| **Coverage** | Orthogonal and unbounded: whatever the op vocabulary can name. The ceiling is not the file format, it is whether a feature has a **seam** (endpoint / domain call) at all. A scenario cannot exercise a thing no code can reach. |
| **Determinism** | **This is where determinism is actually bought.** Four requirements, and the format only supplies the fourth: (i) a seed, (ii) a declared clock, (iii) a single sequential writer so op order is total, (iv) a canonical digest over the outcome. |
| **Cost** | Medium. The runner is a small new tool; the *authoring* is per-feature and continuous. |
| **Language** | **Settled by comparison, not by preference.** The existing `EffectScenarioRunner` already *is* a flat JSON op-list with a seed in the header, a closed vocabulary and golden asserts — `{id, seed, matchKey, plugins[], board[], steps[{op, …}]}` (`gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:10-60`), 18 ops (`:178-327`), 49 fixtures. So the honest recommendation is **extend that format, do not author a second one**: same envelope, same `op`-dispatch idiom, a superset of ops. The delta is exactly two families — `sim.*` / `api.*` (HTTP against the real server, which the existing runner has no concept of, because it drives `SimEffectHost` in-process) and `read.*` (a digest-bearing read). The alternative, a C# DSL like `gk-core/tools/SquadHarness`, is rejected for the corpus for the reason the existing format already embodies: the artifact must be reviewable by reading it, not by reading a program. **C# remains the right home for the generator/searcher that writes JSON** — the split `gk-core/tools/CombatSim` already uses (`scenarios/` + `Program.cs` verbs). |
| **Makes impossible** | A JSON op-list cannot express "retry until the RNG produces the interesting branch" or "sweep this channel across 400 values". That is what the C# side is for; do not try to put it in the format. |

### Shape D — Fake game / injector shim

What a stand-in for the PVZ side must emit for the RPG domain to advance: the `EventEnvelope` kinds a
real injector emits — `injector.hello`, `board.start` / `board.end`, `plant.spawn` / `plant.damage` /
`plant.die`, `zombie.*`, `wave.huge`, `match.result`, `sun.gain`, `card.*`. **This already exists as
54 routes** (`SimEndpoints.cs:13`).

| | |
|---|---|
| **Coverage** | Every RPG path that is driven by lawn events — which, by DESIGN-GATE §2.1–2.3, is most of the combat and progression surface. It contributes nothing for paths that are already gameless (summon, fusion, items, world turns, delves), because those do not need a shim at all. |
| **Determinism** | Good. A shim should be a pure function of the scenario step: same step + same seed ⇒ same envelopes. Its problem is not determinism, it is **scope discipline** (§3.4). |
| **Cost** | Already paid. 54 routes are built. The incremental cost is a **fabrication guard**, not more routes. |
| **Makes impossible** | Anything whose *real* input distribution matters — drop rates, wave composition, what a real lawn actually emits. A shim reads the author's belief about the game, not the game. That is exactly what Shape E is for, and the honest way to say it is: **D proves the RPG's response to an event; it never proves the event is realistic.** |

### Shape E — Record / replay

Capture a real session once; replay it as a regression fixture. The repo already does the deterministic
half: RNG-draw traces at `gk-core/tests/fixtures/action-traces/*.trace.txt` and event-sequence traces at
`gk-core/tests/fixtures/battle-traces/`, consumed by `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionAdoptionFixtures.cs:23`
and `gk-core/tests/FusionRpg.Core.Tests/Battle/Adoption/EventSequenceParityTests.cs:28`.

| | |
|---|---|
| **Coverage** | Whatever was played. **Value is highest exactly where the shim is weakest**: real event *distributions* — real wave sizes, real kill timing, real damage magnitudes. Nothing else can supply those. |
| **Determinism** | Best in class, and for free — a recording is a constant. That is also its trap: a recording that is *wrong* is deterministically wrong forever. |
| **Cost** | Cheap to record, **expensive to keep**. It needs a scrubber (a replay fixture is live traffic — tokens, hostnames, real player rows; see keploy.io/record-replay-testing and the "Replay Fixtures Are Still Live Traffic" write-up), a re-record procedure, and a decision about what a diff means. |
| **Makes impossible / risks** | (a) A recording pins a **reading**, not a contract — the repo's own validation rule (`DESIGN-GATE.md` §3.7, `docs/architecture/validation-ssot.md`) forbids a guardrail asserting a population reading. A recorded lawn's *shape* is a population. (b) If the emitter changes and the reader still passes, the trace is silently stale. (c) **The golden-master trap**: recorded from a debug-seeded session, it can launder a fabricated precondition (§3.4) into a permanent, authoritative-looking fixture. (d) `action-traces` are **draw-level** — every entry names an RNG draw (`draw initiative 273`). Any RNG refactor moves all of them, so they price a refactor, not a behaviour. |

---

# 2. Phase 2 — Evaluate & Converge

## 2.1 Stress test

| Shape | Painkiller or vitamin? | Hardest part | Would anyone switch to it? |
|---|---|---|---|
| **A** in-process | **Painkiller** — it already exists and 47 E2E files lean on it | Defining "settled" around background hosted services | Already the default. Nobody needs to switch; they need it to *stop being the only thing* |
| **B** headless | **Painkiller for the gap A cannot fill** (long loops, restart, real transport) | The clock (§2.3) | Only if the scenario file is shared with A — otherwise it is a second, differently-shaped harness |
| **C** scenario layer | **The actual deliverable.** A/B/D are hosts and feeds; C is the thing a reviewer reads | The op vocabulary is a *new closed vocabulary*, and this repo has a documented habit of inventing a parallel one (`DESIGN-GATE.md` §1 — the atom row: *"Inventing a third is the failure this row was widened to prevent"*) | Yes, if a scenario can reproduce an existing E2E test's content. That is the acceptance test in §7.2 |
| **D** shim | **Already bought, already paid for** | Not building more of it; building the guard that keeps it an input | Nothing to switch to — it is the only way to emit lawn events without the lawn |
| **E** record/replay | **Vitamin, with a real use** (real distributions) and a real bill (custody, staleness, laundering) | Deciding what a diff means | No — it should be a *feed into* C, never a parallel suite |

## 2.2 Clustering

Three coherent directions survive:

- **Direction 1 — "Make E2E a framework."** Grow `RpgApiFactory` into a scenario runner. Cheapest, lands
  in a day, and answers maybe 60% of the need. It cannot answer the long-loop, restart, or real-transport
  questions, and it makes every scenario a test (so every scenario competes with the CI budget).
- **Direction 2 — "One driver, both hosts, one scenario format."** A new tool that runs the *same*
  scenario file against either the in-process host (fast, default) or a real sim-mode server process
  (slow, weekly/release lane), with the shim as its feed and a digest as its verdict. Reuses all five
  existing pieces, invents only the driver and the format.
- **Direction 3 — "Deterministic simulation testing proper."** Rewrite the server for a single-threaded
  discrete-event simulator (FoundationDB / TigerBeetle / Antithesis shape), controlling time,
  scheduling, network and randomness. It is the strongest known answer and it is **not** available at
  this repo's current shape: the production code was not written for it, and retrofitting it is a
  multi-quarter program with a fleet of intermediate states (see §2.2 and the FoundationDB row in §8).

**Recommendation: Direction 2**, with Direction 3 explicitly named as the ceiling this path is walking
toward rather than a thing to do now, and Direction 1 as the inner loop that falls out of it for free.

## 2.3 The constraint that decides the shape — time is ambient

The blocker is not the host and not the format. It is this:

- `DateTime.UtcNow` / `DateTimeOffset.UtcNow` appears on **211 lines in `src/`** — **8 of them doc
  comments, 203 real code call sites** — measured by a binary-safe scan (see the note below; `grep`
  undercounts this file set by 15 and the first draft of this document published 197). By assembly:
  **`FusionRpg.Data` 142 · `FusionRpg.Server` 38 · `FusionRpg.Injector` 17 · `FusionRpg.Core` 3 ·
  `FusionRpg.Launcher` 2 · `FusionRpg.CheatCore` 1.** Two thirds is **one assembly** — the store's row
  timestamps.
- **The values are classified, not just counted** (first match wins, so the five rows partition 203):

  | Class | Sites | Share | What it means for a clock seam |
  |---|---|---|---|
  | ISO timestamp emission (`ToString("o"/"O")`) | 143 | 70% | **Mechanical.** A persisted column or wire payload; no control flow changes. The bulk of the work, and the easy bulk |
  | **Already injectable** (`utcNow ?? DateTimeOffset.UtcNow`) | 25 | 12% | **The seam already exists** — `Contracts`, `Expeditions`, `AllocationRespec`, `SpeciesRespec`, `World`, `WorldTurns`, `CommanderRole`, `PassiveTree`, `UniqueActors`. The ambient clock is only the *default* |
  | Other (heartbeat stamp, boot stamp, filename stamp, elapsed-seconds) | 24 | 12% | Mixed; needs a decision each |
  | **Deadline / wait-loop — MUST NOT be simulated** | 9 | 4% | Faking these tests nothing, and one of them is a **trap** (below) |
  | `DateOnly.FromDateTime(UtcNow)` (date-shaped domain read) | 2 | 1% | Genuinely date-shaped: an offset *changes the answer*, which is the point — but it must be declared |

- **The trap in the "must not simulate" class, named:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1207`
  is `LastHeartbeatUtc is { } t && DateTimeOffset.UtcNow - t < TimeSpan.FromSeconds(5)` — the
  **`InjectorConnected` freshness window**. Shift the clock and a perfectly healthy sim server reports
  itself **disconnected**. The offset seam must therefore exclude this window (and
  `gk-core/src/FusionRpg.Server/DebugEndpoints.cs:1073-1074`, `:1599-1600`, the launcher/injector waits) and say
  why, or the first sim run will look like an injector bug.
- There is **no repo-wide clock abstraction**: `TimeProvider` appears **0 times** in `src/`, and the only
  clock-named interface is `IEffectClock` (`gk-core/src/FusionRpg.Core/Effects/EffectModels.cs:74`), which is
  bag-local (`SystemEffectClock` `:79`, `FakeEffectClock` `:84`, `AdvancedEffectClock` in
  `gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs:33`).
- The one existing clock discipline at server scope is **per-battle** (`SimulationClock`,
  `gk-core/src/FusionRpg.Core/Battle/Timeline/SimulationClock.cs:84`): integer ticks, *"it cannot read the wall
  clock"* — but it governs a battle, not the server.
- **The repo has already proven a scenario-driven fake clock — at bag scope.** `EffectScenarioRunner`'s
  `advanceMs`/`advance` op (`gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:229`) calls
  `host.AdvanceMs(...)` into the harness's own `FakeEffectClock`. So the design question is **not "invent
  a clock abstraction" but "widen the one seam that already exists from bag-local to server-scope"** —
  which is a materially smaller and more honest claim than §2.3's opening suggested.
- Where a pure resolver already takes elapsed time as a parameter
  (`ExpeditionResolver.Resolve`, `:41`), the *caller* supplies it from wall time
  (`gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:98`).
- The current workaround is a **database-level rewind**: `POST /api/test/expedition-due`
  (`gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:346-353`) rewrites the stored due time to
  `UtcNow.AddSeconds(-1)`, described in its own comment as *"SIM-only timer rewind"*.

> **Evidence note — why "binary-safe" is load-bearing here, and a defect this lane found.**
> `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs` contains **two raw NUL bytes (U+0000) inside C#
> string literals** — line `:1576`, `while (r.Read()) taken.Add($"{r.GetString(0)}⟨NUL⟩{r.GetString(1)}");`,
> and line `:1586`, `if (!taken.Add($"{instanceId}⟨NUL⟩{roleId}")) continue;` — where the `\0` **escape**
> was presumably intended. A NUL used as a composite-key separator is a fine choice; writing it as a
> literal byte is not. The file still compiles (a NUL is a legal character in a C# string literal, and CI
> is green), but **`grep` classifies the whole file as binary** and prints `Binary file … matches`
> instead of its matching lines. Consequence: **any `grep`-based reconnaissance or audit silently loses
> this file's contents** — including the first draft of this document, which published **197** where the
> real figure is **211** (15 `UtcNow` sites live in that one file). PowerShell guards are **not** affected
> (`gk-core/scripts/guard-dal.py:43` reads via `Get-Content` + regex) and neither are the Python audits
> (`gk-core/scripts/audit-overflow.py:195`, `gk-core/scripts/audit-magic-numbers.py:265` use `io.open`), so this is an
> **agent-evidence** defect, not a runtime or guard defect. Fix: write the escape, not the byte.
> Reported to the manager rather than fixed here — the file is outside this lane's fence.

So the design space has a fork the brief does not name, and it must be named:

| Option | What it buys | What it costs | Why it is honest |
|---|---|---|---|
| **(a) Full `TimeProvider` migration** | Real determinism. `FakeTimeProvider.Advance` (learn.microsoft.com/dotnet/core/extensions/timeprovider-testing) moves time without waiting. **`RpgStore` taking one `TimeProvider` alone covers 142 of the 203 code sites**, and 25 already take the instant as a parameter | A 203-site sweep, heaviest in `FusionRpg.Data` — but **70% of it is mechanical timestamp emission** and **12% is widening a seam that already exists**; plus a guard (`DateTime.UtcNow` banned in `src/` outside one clock type) | It is checkable, and the abstraction is built into .NET 8 already — `TimeProvider` is simply *unused* today |
| **(b) A single offset seam** (one `RpgClock` read at boot from e.g. `FUSIONRPG_TIME_OFFSET_SECONDS`) | The simulator can state which instant it is simulating, and jump forward without touching stored rows | Same sweep, simpler type; and a *partial* sweep is worse than none — half the timestamps shift and half do not, silently. The 9 deadline/wait sites are the **exclusion list**, and each needs a written reason | Yes, if the sweep is total, the exclusion list is explicit, and both are guarded |
| **(c) Per-feature DB rewind** (today's precedent) | No source change at all | Every feature needs its own rewind verb, and the **event log records a fictional time** — so a scenario's own history becomes untrustworthy | Only as a bridge, and only with the fiction stated in the run header |

**Recommendation: (b) as the named prerequisite of the second slice, (a) as the destination, (c) only
where it already is.** But — and this is the sequencing decision — **the first slice should avoid the
clock entirely** by picking a feature family driven by *events*, not by *elapsed time* (§7). That is
how a shape gets proven without first paying for the hardest part.

## 2.4 Hidden assumptions (what we are betting, and what would kill this)

1. **That a scenario file is readable enough to be reviewed.** Bet: JSON op-lists stay under ~100 lines
   for a real flow. Killed by: a flow that needs loops, retries, or data-dependent branching — which is
   *most* interesting flows. Mitigation: keep the C# generator as the escape hatch (Direction 2 already
   allows it) and treat "this scenario needs a loop" as a signal to split it, not to grow the format.
2. **That "the same query path the FE uses" is well-defined for every feature.** Bet: every feature has
   an FE-facing read. Killed by: features whose only read is a hub push. Mitigation: the verdict reads
   the hub message *and* the persisted row, and says which one it used.
3. **That the digests are stable across machines.** Bet: the outcome contains no platform-dependent
   value (float formatting, dictionary order, timestamps). Killed by: any `DateTime` in the outcome —
   which, per §2.3, is currently on 203 code call sites. Mitigation: hash the *canonical subset* the scenario
   declares, exactly as `Artifacts.cs` does by excluding its own `at` field
   (`gk-core/tools/SquadHarness/Artifacts.cs:31`).
4. **That the shim stays an input.** Bet: no new `/api/sim/*` route ever writes the result under test.
   Killed by: convenience, at the first feature whose condition is hard to reach by events. Mitigation:
   §3.4's guard.
5. **That this does not become a second test suite.** Bet: scenarios and tests stay distinct roles —
   scenarios prove *sequences*, tests prove *contracts*. Killed by: the first time a scenario is easier
   to write than a test, after which the suite has two homes for the same assertion.

---

# 3. Phase 3 — Sharpen & Ship

## 3.1 Recommended architecture

```
                    ┌───────────────────────────────────────────────┐
                    │  gk-core/tools/RpgSim  (NEW — the only new binary)    │
                    │  - reads scenario.json, owns the seed         │
                    │  - declares the clock (offset | explicit now) │
                    │  - drives ONE client, sequential ops          │
                    │  - computes the canonical digest              │
                    └───────────────┬───────────────────────────────┘
                                    │  same scenario file, two hosts
             ┌──────────────────────┴───────────────────────┐
             ▼                                              ▼
  A: in-process (fast, default)               B: real process (slow lane)
  WebApplicationFactory<Program>              FusionRpg.Server.exe
  tmp FUSIONRPG_DATA                          FUSIONRPG_SIM=1
  (tests/FusionRpg.E2E.Tests/RpgApiFactory)   FUSIONRPG_DATA=<tmp>
                                              FUSIONRPG_TIME_OFFSET_SECONDS=<n>   ← slice 2
                                              ephemeral 127.0.0.1 port
             │                                              │
             └──────────────────────┬───────────────────────┘
                                    ▼
                       REAL SERVER  (unmodified domain path)
             ┌─────────────────────────────────────────────────────┐
             │  /api/sim/*   54 input routes  ←  the shim (FEED)    │
             │      └─ SimService.Publish → EventIngest            │
             │  EventIngest → domain → RpgStore (SQLite)           │
             │  /api/*  the ordinary FE routes  ←  the READ-BACK    │
             │  /hub/rpg (SignalR)              ←  the READ-BACK    │
             └─────────────────────────────────────────────────────┘
                                    ▼
                    verdict JSON   { ok, steps[], readings[] , digest }
                                    │
                    ┌───────────────┴────────────────┐
                    ▼                                ▼
        CI default lane (fast A-runs)      weekly / release lane (B-runs)
```

**What runs:** one new tool (`gk-core/tools/RpgSim`), zero new server code for slice 1. The server in sim mode
already exists; the shim already exists; both hosts already exist.

**Who drives it:** the tool, as a **single sequential writer**. No concurrency in a scenario — this is
not a load test (Metaplay's BotClient) and pretending otherwise would destroy the ordering guarantee
that makes a digest meaningful.

**Where state lives:** in the server, in its own `FUSIONRPG_DATA`, exactly as in production. The driver
holds no domain state — only its position in the scenario and the readings it has collected. That is
the whole reason the digest is trustworthy: the driver cannot be the thing being tested.

**How a scenario is written:** a JSON op-list, in a **new closed vocabulary** — and this is the part
that needs a spec, because the repo has already paid twice for inventing a parallel vocabulary
(`DESIGN-GATE.md` §1, the atom and action rows). Proposal: name ops after the *endpoint they call*,
not after the effect they cause (`sim.boardStart`, `api.items.equip`, `read.almanac`) so the vocabulary
is derived from an existing closed set (the route table) rather than authored fresh. Ops:
- `sim.*` — a call to an existing `/api/sim/*` route (the shim, the input side)
- `api.*` — a call to an existing FE-facing route (real domain path)
- `read.*` — a read whose payload enters the digest (must name the FE-facing path, per §3.4)
- `expect.*` — an assertion on a reading
- `digest` — mark this reading as digest-bearing

**How determinism is proven:** four things, each checkable:
1. **Seed** in the scenario; every synthesized payload derives from it. The server-side RNG paths already
   take seeds (`BattleEngine.Resolve(setup, seed, …)`, `ExpeditionResolver.Resolve(…, seed, …)`).
2. **Clock** declared in the run header (offset, or an explicit start instant) and *printed*, so a
   pasted verdict is self-describing — the discipline `gk-core/tools/CombatSim` already uses when it prints the
   constants it used.
3. **Total order** — one client, sequential ops, no background waiter.
4. **Digest** — SHA-256 over canonical JSON of the declared readings, provenance blanked, using
   `gk-core/tools/SquadHarness/DeterminismHash.cs:19`'s idiom verbatim. **The exclusion list is the load-bearing
   part, and there is a shipped recipe for it:** `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:163`
   blanks `EnvironmentStamp`, `ContentHash`, `Warnings` and per-event `KillerActorKey`, with a comment
   stating why each is excluded — *"folding any of these in makes the goldens move for a reason that is
   not a determinism break."* A digest that moves for a non-determinism reason is worse than no digest,
   so the simulator's exclusion list must be written down with a reason per field. **The falsifier is a
   same-run re-run**: the driver runs the scenario twice and fails if the two digests differ. A
   determinism claim asserted once is a claim; this one is executed every time.
5. **Both assertion styles, not one.** The existing runner asserts a *specific artifact* against a stored
   `golden` file; a digest asserts only that *nothing moved*. They answer different questions and the
   repo already carries both (`expectPlan` + `golden` in the effect fixtures; hashed goldens in
   `BattleGoldenTests`). A scenario should be able to do both — which is also the answer to Open
   Question 8.

## 3.2 Why this shape and not the others — the short version

- The **shim (D)** is the feed, and it is already built. Reusing 54 routes is the entire argument
  against building a second fake-injector.
- The **in-process host (A)** is the fast lane; the **real process (B)** is the slow lane; **the same
  scenario file must run on both**, or the two lanes become two harnesses (the failure mode Direction 1
  has).
- The **scenario layer (C)** is the deliverable — it is the only piece a reviewer reads.
- **Record/replay (E)** is a *feed*, not a suite: it licenses the shim's shape ("these are the kinds and
  sizes of events a real lawn emits") without becoming a golden.
- The **clock** is a prerequisite, not a slice-1 task, and it belongs to the owner (§6 Q2/Q3) because
  option (a)/(b) is a `src/`-wide sweep with a product-adjacent capability attached.

## 3.3 The CI story

**Today.** `.github/workflows/ci.yml` runs **60** distinct `dotnet test` projects (`:135-292`), each
with its own exit check and a 10-minute `--blame-hang-timeout`; `FusionRpg.E2E.Tests` is one of them
(`:291`), and it is the in-process full boot. `FusionRpg.SquadHarness.Tests` is another. **There is no
long-running lane, and there is no job that runs a real server process.** The balance guard is its own
step (`:106`) precisely because a swallowed failure is a real past incident.

**What can run in CI today, unmodified:** every Shape-A scenario (it is an E2E test by another name),
and every `/api/sim/effect` scenario (`EffectScenarioRunner`, already in the default suite as
`FusionRpg.Core.EffectScenarioRunnerTests.Tests`, present in `ci.yml`).

**What needs a separate lane:** every Shape-B run (a real process costs seconds to boot, and a scenario
containing any wait is minutes), every scenario large enough to be worth a digest, and every sweep.
`gk-core/tools/CombatSim` is referenced by four of the 60 test projects — `FusionRpg.Core.Balance.Tests`,
`FusionRpg.Core.ClassSystem.Tests`, `FusionRpg.Core.Tests`, `FusionRpg.Guard.Tests` — but only its
*library*: a full sweep is a `dotnet run` a human or a schedule issues, never something the suite does.
That is the correct relationship, and the simulator should copy it: **the driver is a tool; only its
pure parts are referenced by tests.**

**Proposed shape for that lane:** a second job in `ci.yml`, `needs: test`, triggered on a label or a
schedule, running `dotnet run --project gk-core/tools/RpgSim -- --scenario …`. It must **not** claim the
`live-slot` game pool — the whole point is that a simulator needs no game install
(`docs/contributing/live-probe-standard.md` §1's "gameless" spirit; `AGENTS.md` "Three live slots").
It must **refuse to run** unless the target server reports `simEnabled: true` on `GET /health` — the
field already exists on the wire (`HealthDto.SimEnabled`, `gk-core/src/FusionRpg.Contracts/Dtos.cs:48`, set from
`SimFlags.Enabled` at `gk-core/src/FusionRpg.Server/Program.cs:1253`). That refusal is the single safety
property that keeps this tool from ever touching the owner's install.

**Smallest first slice that would prove the shape** — §7.

## 3.4 The boundary that must not be crossed

`docs/contributing/live-probe-standard.md:43` — **"A debug API may trigger a real operation. It must
never fabricate the state that operation is supposed to produce."** §1 splits the world into **Game
Injector Debug** (may fabricate engine state; proves only that Unity reflects it) and **RPG Server
Debug** (may fabricate nothing; must run the real path on a real record).

### Where a simulator sits

**A simulator is neither scope. It is a producer of inputs plus a reader of outcomes.**

The reason this is not a loophole is DESIGN-GATE §2.1–2.3: the RPG is built to work **from past events,
never current game state**, and to be driven by **recorded events drained later**. A synthesized event
stream is therefore *the protocol's own input format*, not a shortcut around the domain. The injector is
a client that emits envelopes; the shim is a client that emits the same kinds. Emitting them is the
architecture working as designed — `SimService.Publish` (`gk-core/src/FusionRpg.Server/SimService.cs:76`) hands
envelopes to the same `EventIngest` a real injector's envelopes go to, and the domain then derives
whatever it derives, on its own.

The rule the simulator must obey is therefore a **sharper** version of live-probe-standard §2, in one
sentence:

> **The simulator may synthesize the input. It may never write, or read, the conclusion.**

### Option-by-option

| Option | Violates live-probe-standard §2? | Why |
|---|---|---|
| **A** in-process host | **No** | It is the real server; only the transport is simulated |
| **B** headless server | **No** | It **is** the real server, in a mode it already ships |
| **C** scenario layer | **Depends entirely on the op vocabulary** | An op that calls a real endpoint: fine. An op that *sets* a stat, an XP total or an inventory: a violation by construction — and the danger of a format is that the violation becomes one comfortable line rather than a new route |
| **D** shim | **The only option that can violate it**, and only if it writes results instead of emitting events | Today it mostly does not. The exceptions are named below |
| **E** record/replay | **No fabrication** — a different risk | It can *launder* a fabricated precondition into a permanent, authoritative-looking fixture (§2.4 assumption 5) |

### The shim's three real exposure points in the tree today

Read out of the code, not inferred:

1. **`POST /api/test/reset` → `SimService.FullResetAsync` → `RpgStore.Reset()`**
   (`gk-core/src/FusionRpg.Server/SimEndpoints.cs:136` → `SimService.cs:57-63`). This **writes** — it wipes the
   database. It is a legitimate *fixture* (setup, not result) but it is emphatically not input-only, and
   a scenario that treats "reset succeeded" as evidence has done nothing.
2. **The three `seed-*-demo` writers** — `/seed-pvz-stats-demo` (`SimEndpoints.cs:184` →
   `store.SeedPvzStatsDemo`, `:197`), `/seed-pvz-activity-demo` (`:218` → `:231`),
   `/seed-rpg-progression-demo` (`:240` → `:253`). These write rows **directly**, bypassing the flow
   that would normally produce them. They are the clearest existing instance of what §3.4 forbids as
   *evidence*: a verdict read after seeding a progression row is a verdict about nothing.
3. **`/api/sim/effect/*` is mapped unconditionally** (`gk-core/src/FusionRpg.Server/Program.cs:2053`) while
   `/api/sim/*` and `/api/test/*` are gated on `FUSIONRPG_SIM` (`:2050`). So on a **live, non-sim**
   server the effect-sim routes are reachable. They are input-only (grant/withdraw/fire feed
   `SimEffectHost`) so this is not a fabrication hole — but it is an exposure the simulator's safety
   story must account for, and it is worth an owner ruling rather than an agent's silence.

### The three read-back rules a verdict must satisfy

Straight from `live-probe-standard.md` §3, applied to a scenario:

- **Not `/api/test/snapshot`.** That route (`SimEndpoints.cs:144`) returns raw store tables — the
  standard's §3.3 names exactly this as the anti-pattern (*"a debug-only accessor built to make the test
  convenient"*). It is useful while developing a scenario; it must not be what the digest is computed
  from.
- **The same query path the FE uses**, or the hub message the FE receives — and the verdict must say
  which.
- **A response body is not proof** (§3 opening). The reading is a value read back from persisted state
  or from the normal read endpoint, not the write call's own echo.

### What a guard could hold (proposal, not a build)

A proposed `guard-sim-fabrication.py` (**does not exist yet** — named here as the candidate, in the
shape of the existing `scripts/guard-*.ps1` family), asserting that
every `/api/sim/*` handler in `gk-core/src/FusionRpg.Server/SimEndpoints.cs` reaches `RpgStore` **only** through
`SimService` (read for stats, publish for events) — with the reset and the three `seed-*-demo` routes on
an explicit allowlist carrying a written reason. That makes §3.4 mechanical rather than a review
discipline, which is the same move `gk-core/scripts/guard-debug-scope.py` already made for the debug scopes
(named in `DESIGN-GATE.md` §1, "Proving a feature works live").

---

# 4. MVP scope

**In:**
- `gk-core/tools/RpgSim` — a console tool: `--scenario <file> --host inproc|process --data-dir <tmp>`, emitting
  its verdict as JSON (`ok`, `steps[]`, `readings[]`, `digest`) to a run output file, plus a digest.
- The scenario JSON schema, with the op vocabulary named after existing routes (§3.1).
- **Reuse** of `/api/sim/*` as the only feed. No new server routes.
- The digest, with the same-run double-run falsifier.
- Two hosts, one file: the in-process `RpgApiFactory` path and the real-process path.
- The `simEnabled` refusal.

**Out (deliberately):**
- The clock migration (§2.3) — a separate decision with a `src/`-wide sweep.
- Any scenario generator, shrinker, or model (§2.2 Direction 3, and the Hypothesis row in §8).
- Recording. `gk-core/tests/fixtures/` is untouched by this shape.
- A CI lane. Slice 1 runs locally and in whatever lane the owner names.

# 5. Not doing, and why

1. **A single-threaded discrete-event simulator of the whole server** (Direction 3). It is the correct
   end state for a system that already knows how to test this way, and the wrong first move for one
   whose production code was not written for it. Named as the ceiling; revisit after the clock is owned.
2. **Growing `/api/sim/*` further.** 54 routes is already a second protocol surface to maintain. New
   coverage should come from *events* the shim can already emit, and any genuinely new input shape
   should be argued as a protocol addition, not a test convenience.
3. **Goldens over recorded sessions.** §1.4 Shape E risk (c) and DESIGN-GATE §3.7. A scenario's verdict is a digest
   over *declared* readings, not a byte diff of a captured world.
4. **A load-test / bot-farm.** Different question (Metaplay's BotClient territory), different
   harness — and concurrency destroys the digest.
5. **A web UI for runs.** The verdict is a JSON file and a CI line. A dashboard is a later, separate
   argument.

---

# 6. Open Questions — for the owner

Each answerable in one line. Numbered so an answer can be given as *"Q3: (b)"*.

1. **Does this program exist?** Is `rpg-simulator` a named program with a capability map and a plan
   (`docs/architecture/rpg-simulator-map.md`, `tasks/rpg-simulator-plan.md`), or is this idea input to a
   different program? Nothing in `tasks/` or `docs/architecture/` carries the name today.
2. **Which clock option?** §2.3: (a) full `TimeProvider` migration, (b) a single offset seam, (c) keep
   the per-feature DB rewind. (b) is my recommendation; (a) is the destination; (c) is today.
3. **Is "the server can be told what time it is" a *test* capability or a *product* one?** Hibernating
   worlds are specified to catch up lazily on the world-turn clock (`docs/guide/the-loops.md`), and a
   player can move their machine clock — so this may be a product decision wearing test clothing. If it
   is product, it needs a `decisions.md` row before a spec.
4. **May a scenario file live in the repo as a fixture?** Under `gk-core/tests/fixtures/` (where
   `effects/scenarios/` and `action-traces/` live) or under `docs/` as a research artifact, or a new
   `data/sim/scenarios/`? This decides whether a scenario is a *test input* or a *document*.
5. **Which feature family is slice 1?** §7 proposes the lawn-event → progression chain, sourced from
   the existing `FoundationE2ETests.cs` flow. Any better candidate — summon/fusion, item equip, a world
   turn — is equally acceptable and should be picked by *coverage per unit of scenario*, not by which is
   easiest to script.
6. **Real process or in-process for slice 1?** My recommendation is **both, one file** — but if only one
   is funded, in-process is the honest first cut and the real process is the one that must follow,
   because it is the only shape that answers the long-loop question the brief exists for.
7. **Does the first slice get a CI lane, or run locally only?** A local-only first slice proves the
   shape but not that it survives; a CI lane costs a job on every push.
8. **Is the digest the verdict, or the readings?** A digest says "unchanged", not "correct". Do you want
   the scenario to carry explicit `expect.*` assertions (verbose, but fails loudly and specifically) or a
   digest-only contract (terse, but a change reads as "different" with no diagnosis)? **The repo's own
   answer is "both"** — a stored `golden` for the artifact and a hash for determinism (§3.1 item 5) —
   but the split still needs your ruling for slice 1, because it decides how much each scenario file
   carries.
9. **Should `gk-core/tools/RpgSim` be one tool or a verb on an existing one?** `gk-core/tools/SquadHarness` and
   `gk-core/tools/CombatSim` are both standalone console tools with tests; a fourth tool is consistent, a shared
   one is fewer things to maintain across the 60 CI projects.
10. **What is the stop rule for the shim?** If a feature's condition genuinely cannot be reached by
    events, does that license a new `/api/sim/*` route, or does it mean the feature is untestable without
    the game and should be reported as a gap? (My read: the latter, and the gap is the finding.)
11. **`/api/sim/effect/*` is unauthenticated and ungated while `/api/sim/*` is gated**
    (`gk-core/src/FusionRpg.Server/Program.cs:2050` vs `:2053`). Intentional, or drift?
12. **Who owns the `AGENTS.md` drift?** `AGENTS.md` says CI runs *"13 C# test projects"*; `ci.yml` names
    **60** distinct test projects. That is a documentation defect in a file outside this lane's fence
    (`docs/architecture/**`, `tasks/**`), so it is reported here and in this lane's notes rather than
    fixed. Which program's todo should carry the row?

---

# 7. Slice 1 — the smallest thing that would prove the shape

**Deliverable:** one scenario file + the driver, run against one real server process, twice, with equal
digests and a read-back through an FE-facing endpoint.

**Content source:** the flow already asserted by `gk-core/tests/FusionRpg.E2E.Tests/FoundationE2ETests.cs` and
`gk-core/tests/FusionRpg.E2E.Tests/SummonE2ETests.cs` — an existing, green, in-process flow. Turning a passing
test into a scenario is the cheapest possible expressiveness test, and disagreement between them is
immediately meaningful.

**Acceptance — every line falsifiable:**
1. The driver refuses to run when the target's `GET /health` does not report `simEnabled: true`.
2. One scenario file drives the whole flow: at least two `sim.*` input ops, at least one `api.*` real
   endpoint, and at least one `read.*` whose value enters the digest.
3. The digest is identical across two consecutive runs in the same invocation, on a fresh
   `FUSIONRPG_DATA` each time.
4. Every digest-bearing reading comes from an FE-facing route or a hub message, **never**
   `/api/test/snapshot` — assertable by making the driver record the source path of each reading in the
   verdict.
5. The same scenario file runs against the in-process host and the real-process host.
6. The verdict is a JSON file a human can read, carrying the seed, the clock declaration, the readings
   with their sources, and the digest.

**Explicitly not in slice 1:** any elapsed-time wait, any restart, any sweep, any CI lane.

---

# 8. Prior art — outward

Cited for what to borrow and what to refuse. Access: web, 2026-09-22.

| Source | The claim | Borrow / refuse |
|---|---|---|
| FoundationDB — *Simulation and Testing* (apple.github.io/foundationdb/testing.html) and *Diving into FoundationDB's Simulation Framework* (pierrezemb.fr/posts/diving-into-foundationdb-simulation/) | A whole cluster runs in **one single-threaded discrete-event process**, with simulated network and disk; a seed drives every randomized decision, so a failure replays exactly | **Borrow:** single-writer + seeded + total-order is the target property, and it is what the digest encodes. **Refuse for now:** it required the production code to be written for the simulator (Flow actors); retrofitting is Direction 3 |
| TigerBeetle — *Safety* (docs.tigerbeetle.com/concepts/safety/) and *Protocol-Aware DST* (tigerbeetle.com/blog/2026-08-20-protocol-aware-dst/) | Real code under simulated faults at ~1000×; determinism keyed on **seed + git commit** | **Borrow:** the run header must carry the commit as well as the seed, or a reproducibility claim does not survive a code change |
| Antithesis — *So you think you want to write a deterministic hypervisor?* (antithesis.com/blog/deterministic_hypervisor/) and *Autonomous Testing of etcd's Robustness* (etcd.io/blog/2025/autonomus_testing_with_antithesis/) | A deterministic hypervisor controls **scheduling, clocks and network**, making a whole deployment one replayable experiment | **Borrow:** clocks are a *controlled resource*, first-class. This is the outside confirmation of §2.3's finding that the clock is the load-bearing gap, not an implementation detail |
| .NET — *What is the TimeProvider class* (learn.microsoft.com/dotnet/standard/datetime/timeprovider-overview) and *Testing with FakeTimeProvider* (learn.microsoft.com/dotnet/core/extensions/timeprovider-testing) | `TimeProvider` is the built-in clock abstraction; `FakeTimeProvider.Advance` moves time without waiting | **Borrow:** the type already exists; the cost is the sweep and the guard, not the design. Note this repo has no clock abstraction outside `IEffectClock` |
| Microsoft — *Integration tests in ASP.NET Core* (learn.microsoft.com/aspnet/core/test/integration-tests) and *WebApplicationFactory* API | The in-process factory/`TestServer` is the standard functional-e2e host | **Borrow:** it is the fast lane. **Refuse as the only host** — see the next row |
| dotnet/aspnetcore #11888, #31911, #42657; dotnetcurry, *Integration Testing of Real-time communication* | `TestServer` does not support WebSockets; the client needs `CreateHandler()`; real Kestrel is the workaround | **Confirms Shape A's coverage gap mechanically.** The repo's E2E usage (`_factory.Server.CreateHandler()`) is the adapted form, not a real transport — which is exactly why a real-process lane is a different lane |
| Hypothesis — *Stateful testing* (hypothesis.readthedocs.io/en/hypothesis-python/4.57.1/stateful.html); PropEr — *Testing of generic servers* (proper-testing.github.io/tutorials/PropEr_testing_of_generic_servers.html); *Modeling REST APIs as state machines* (python-testing-debugging.com) | Generate *sequences* of operations against the real system **and a model**; shrink a failure to a minimal sequence | **Borrow later:** it is the direction a scenario corpus grows into. **Refuse in slice 1:** a generator needs a model, and building the model is the actual work — hand-authored scenarios are how the model gets discovered |
| Verify (github.com/VerifyTests/Verify); ApprovalTests.Net (helpmetest.com/blog/approvaltest-dotnet-guide/) | Snapshot: serialize the result, compare to a stored file, fail on divergence; scrub volatile fields | **Borrow:** the approval-file workflow and the scrubber — the same move `DeterminismHash` already makes by blanking provenance. **Refuse:** an approval file that captures a population reading is what DESIGN-GATE §3.7 forbids |
| Keploy — *Record and Replay Testing* (keploy.io/record-replay-testing); *Replay Fixtures Are Still Live Traffic* (dev.to/devrs_886) ; nventive/HttpRecorder ; NSHipster *Replay* | Recording real traffic and replaying it is the canonical way to get realism; and a replay fixture **is** live traffic, carrying tokens and internal hostnames | **Borrow:** capture is the only source of real distributions, and it should feed the shim's shape. **Refuse:** recordings as repo fixtures without a scrubber, and recordings as goldens |
| Metaplay — *BotClient Testing* (docs.metaplay.dev/feature-cookbooks/automated-testing/botclient-testing) | Headless bots driving the real server for load, functional testing **and game-economy simulation** | **Borrow:** "clients against the real server" is the industry-standard shape for exactly this problem — it is Direction 2. **Refuse:** the concurrency (beyond slice 1; it destroys the digest) |
| Idle/offline-progress clock-trust material — bugnet.io *How to Fix Wrong Offline Progress in an Idle Game*; r/GameDevelopment *Offline Progress: Time Cheating in Idle Games* | Offline progress is computed from *trusted* elapsed time and must be validated against clock manipulation | **Borrow:** confirms the clock belongs to the server and is a product-adjacent surface — supporting Q3 |

# 9. NOT proved

This lane is design work. Nothing below was run, and none of it may be quoted as if it were.

**The only three commands this lane executed** were `python scripts/audit-doc-citations.py --scope
<this doc> --strict` (0 HIGH), `powershell -NoProfile -Command ".\scripts\guard-doc-citations.ps1"`
(25207 citations, 0 HIGH), and `powershell -NoProfile -Command
"python scripts/session-boundary-check.py --session rpg-sim-idea-b"` (clean). Everything else below is
read-only: no build, no test, no server, no scenario, no probe.

- **Nothing was executed.** No build, no test, no server was started, no scenario was run. Every claim
  here is a *read* of the tree with `file:line`, or a web source with a URL.
- **No digest was computed and no determinism was measured.** §2.3's four-part determinism story is a
  *design*, not a result. In particular, whether a canonical JSON of real readings is actually stable
  across machines is **untested** — the 203 wall-clock call sites are a concrete reason to expect it is
  not, until the clock question is answered.
- **The clock options are now costed by classification, but still not by a trial sweep.** 203 code call
  sites measured binary-safe, partitioned 143 / 25 / 24 / 9 / 2 (§2.3). What remains unknown is the
  *effort per class*: whether the 143 timestamp emissions collapse into one injected parameter or need
  per-call-site thought, and whether the 25 already-injectable sites can be flipped to a non-optional
  parameter without touching their callers. No site was edited, so no sweep was timed.
- **The op vocabulary is now compared, and the comparison changed the recommendation.** Read against
  `EffectScenarioRunner`'s 18-op switch (`gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:178-327`),
  the proposal is **an extension of that format, not a sibling of it** — same envelope
  (`:10-60`), same `op`-dispatch, a superset of ops. What remains **unproven** is whether the extension
  is actually expressible: the existing `EffectScenarioStepDto` carries op-specific optional fields on
  one flat step type (`:34-60`), and whether `sim.*`/`api.*`/`read.*` fit that shape or force a
  discriminated-union redesign has **not** been tried. Also unproven: whether the two runners should
  share a step DTO at all, or share only the envelope and the fixture directory.
- **The trade-off table in §2.1 is a judgement, not a measurement.** No shape was prototyped.
- **The proposed `guard-sim-fabrication.py` was not written, and does not exist.** The proposal was not
  prototyped and may not be mechanisable: the
  current routes reach `RpgStore` through `SimService`, but whether every handler can be classified
  without reading method bodies is unverified.
- **`sim-idea-a`'s inventory was not read.** This document defers to it by lane name only; if it
  concludes a feature family is un-scriptable, that conclusion overrides §7's example.
- **The numbers I did reproduce are:** 60 distinct test projects named in `ci.yml`; 211 `UtcNow` matching
  lines in `src/` (203 code call sites, partitioned 143 / 25 / 24 / 9 / 2); 54 routes under `/api/sim`
  and 6 under `/api/sim/effect`; 47 E2E files using `RpgApiFactory`; 67 `gk-core/tests/FusionRpg.Server.Tests/**`
  files using `UseUrls`; 311 test files referencing `DataTestStore`; 49 effect scenario fixtures. Every
  other figure is a file count from a single `grep -rl`, reproduced once — and **the `UtcNow` count is
  the one that had to be re-derived binary-safe**, because `grep` loses
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs` (§2.3's evidence note).
- **No live probe was run**, and none of the existing live-probe conventions (install locks, slots,
  killing rules) were exercised.

---

# 10. DESIGN-GATE §5 pre-proposal checklist

```
[ ] I identified the subsystem(s) this touches.
    ✔ The test/verification substrate (developer infrastructure), not a product subsystem. Named as
      such up front (header), and it adds no loop.
[x] I established and recorded this session's boundary.
    ✔ Lane sim-idea-b, worktree `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/cmdc-sim-idea-b`
      on branch `cmdc/sim-idea-b`; record at `tasks/sessions/rpg-sim-idea-b.json`, `status: active`.
      Fence `docs/architecture/**` + `tasks/**` — read-only everywhere else. No product code, no tests,
      no scripts were touched.
    ⚠ LATE, and named: the record was created and committed **after** the document's first commit,
      not before it. `docs/contributing/session-boundary.md` §4 wants it before the first edit. Nothing
      crossed (the lane is a worktree and the whole change is two new files), but the ordering was
      wrong. Verified clean afterwards:
      `powershell -NoProfile -Command "python scripts/session-boundary-check.py --session rpg-sim-idea-b"`
      → `[session-boundary] clean for 'rpg-sim-idea-b'`, exit 0.
[x] I read every doc in the §1 row(s) for those subsystems, this session.
    ✔ DESIGN-GATE (whole file), guide/the-game.md, guide/the-loops.md, contributing/live-probe-standard.md,
      architecture/effect-testing.md, architecture/data-test-substrate-ideal.md (head), and the code
      cited throughout. Read in this session, in this worktree.
[x] I checked decisions.md for a lock covering this.
    ✔ No decisions.md row names a simulator. The near rows (Standalone-first; Product vision;
      ActorHub sole Hot compose) were read via DESIGN-GATE §1's table and are not contradicted.
[x] Every factual claim cites file:line.
    ✔ Every claim about the tree does, or is marked as a judgement (§2.1, §2.4 of this doc). Outward claims
      cite URLs.
[x] `python scripts/audit-doc-citations.py --scope <the doc I touched>` reports no HIGH finding.
    ✔ RUN: `python scripts/audit-doc-citations.py --scope docs/architecture/rpg-simulator-shape-idea.md --strict`
      → 1 document, 71 resolvable citations, D1/D2/D3/D4 all 0, 0 HIGH, exit 0. Four initial HIGH findings
      (a not-yet-existing guard script named twice, an output filename, a bare `Program.cs` basename)
      were **fixed**, not exempted.
[x] I verified claims against CODE, not comments.
    ✔ Where a comment and the code disagreed the code is what is written up; e.g. the
      "SIM-only timer rewind" comment (ExpeditionEndpoints.cs:346) is reported alongside the store call
      it actually makes (:352).
[x] I read the surrounding section of every rule I quoted.
    ✔ live-probe-standard §1/§2/§3 read in full; DESIGN-GATE §1/§2/§3/§5 read in full.
[x] I tested (not assumed) any constraint I am reporting.
    ✗ NOT APPLICABLE-then-honest: nothing was run (see §9). No constraint is *reported* as tested.
[x] Nothing contradicts a §2 invariant, or I named the contradiction explicitly.
    ✔ DESIGN-GATE §2.1 (two async systems / past events) is what makes the shim an input — used, not
      contradicted. DESIGN-GATE §2.9 (standalone-first) is why a real-process host is required rather
      than optional. DESIGN-GATE §2.16 (edge-refreshed caches) is NOT addressed and is a named gap for
      the spec that follows: a scenario that binds a specimen after allocating (the 2026-09-13
      incident's shape) is exactly the case a scenario corpus should cover — and the scenario format
      must be able to express order.
[x] Corrections are propagated to prose, Structure, Testing, Boundaries, map, and tasks.
    ✗ Partial by design: `docs/README.md` is OUTSIDE this lane's fence, so the map row is owed and
      cannot be added here. Q12 asks who owns the AGENTS.md drift.
[x] No assertion pins a derived-population count, an item total, or a per-cycle outcome.
    ✔ The only literals are toolchain/route counts (60 test projects, 54 routes) used as readings with
      their reproducing command; none is proposed as a guard.
[x] If this introduces or touches an event-refreshed cache (§2.16): EVERY trigger listed and tested.
    ✗ Not applicable to this document, and explicitly flagged above as a gap the spec must close.
[x] No acceptance criterion silently fixes an ordering that can vary in real play.
    ✗ The §7 acceptance deliberately FIXES an ordering (single sequential writer) — and says so. That is
      a property of the harness, not of the game; real-play order variation is not covered by slice 1
      and is named in §9.
[x] Produces/consumes an actor combat/derived magnitude: contributes via ActorHub or consumes Hub output.
    ✔ N/A — the simulator is a client of the server and composes no magnitude. It must not become a
      second fold, and the shape gives it nowhere to put one.
[x] Does not invent or extend a SOLID-violating parallel path (§2.15).
    ✔ The recommendation is explicitly *anti*-parallel: reuse the existing 54 sim routes, both existing
      hosts, and the existing digest idiom. The one new vocabulary (op names) is proposed as *derived
      from* the route table, not authored fresh — with §2.4 assumption 1's mitigation for the port.
[x] A new rule has a registry row: a guard, or an `unguardableReason`.
    ✗ OWED: §3.4's read-back rule and §3.4's input-only rule are new rules with no registry row. The
      proposed `guard-sim-fabrication.py` is the candidate; until it exists the rules are
      `unguardableReason`-class and must be registered in `gk-core/scripts/enforcement-registry.v1.json` when
      the spec lands. Cannot be done from this lane.
```

Two boxes are honestly unticked and one is unticked incompletely; all three are named above rather
than smoothed over.

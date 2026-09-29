# Capability map: `rpg-simulator` — the RPG feature simulator

**Status:** proposed 2026-09-22. **The shape is owner-cleared** — all twenty questions in
[`tasks/rpg-simulator-decisions.md`](../../tasks/rpg-simulator-decisions.md) carry an `ANSWER:` line
(owner, 2026-09-22), five of them overrides of the lanes' recommendations. This map is the index that
turns those answers into module ids; the plan is
[`tasks/rpg-simulator-plan.md`](../../tasks/rpg-simulator-plan.md) and the task list is
[`tasks/rpg-simulator-todo.md`](../../tasks/rpg-simulator-todo.md).

**Inputs it implements.** [`rpg-simulator-idea.md`](rpg-simulator-idea.md) (lane `sim-idea-a`: what
exists, what must be covered, five divergent options) and
[`rpg-simulator-shape-idea.md`](rpg-simulator-shape-idea.md) (lane `sim-idea-b`: the shape, the clock
measurement, the boundary against the never-fabricate rule). Where the two disagree, the decisions
sheet wins; where this map and a decision disagree, the decision wins and this file is wrong.
**Clock lock:** [`decisions.md`](decisions.md) row *"The server can be told what time it is — product
surface, not a test seam"* — written from decision B2, and it gates the `clock-seam` module.

**Module specs:** the plan's original shape was `docs/architecture/rpg-simulator/spec-<module-id>.md`, one
per id below, written per wave in dependency order and verified against code before it is placed. **That tree
is not where the contracts ended up, and the Spec column below now names each module's REAL document** (RS-F5,
repointed 2026-09-23): a contract that a machine enforces lives beside that machine (`gk-core/tools/RpgSim/*.md`, the
`gk-core/tools/CombatSim/README.md` precedent), a contract that IS a mechanism lives in the file that implements it
(`ProcessHost.cs`, `guard-sim-fabrication.py`), and a module that was never needed says so. Two modules have
full specs as siblings of this map — `rpg-simulator-spec-clock-seam.md` (10) and
`rpg-simulator-spec-seed-seam.md` (11) — because a *seam* is product surface that no single machine owns.
**No module is built until its contract exists and its gate's prerequisites land.**

---

## What this program is

A **forward-play instrument for the RPG layer**: a scenario — a readable list of steps that name real
routes — is driven against the **real server** (the in-process `WebApplicationFactory<Program>` by
default, a real `FusionRpg.Server.exe` in the slow lane), and every verdict is a **read-back through
the same GET route the web FE calls**. It exists so an agent or CI can play days of a save in seconds
with the PvZ game closed, and see the defects that only a *sequence* reveals: reachability (a route
nothing can reach) and cross-family ordering.

The program adds **no loop, no stock, no class, no clock of its own and no player-facing surface**
(`docs/guide/the-loops.md:170` — a feature owes the loops page a loop; an instrument owes it
nothing). It is developer infrastructure, the same class as
[`data-test-substrate-ideal.md`](data-test-substrate-ideal.md) and
[`test-verification-boundary-ideal.md`](test-verification-boundary-ideal.md).

**The one sentence the whole program obeys** (shape-idea §3.4, sharpened from
`docs/contributing/live-probe-standard.md:41`):

> **The simulator may synthesize the input. It may never write, or read, the conclusion.**

## What it is not

- **Not a change to PvZ, and not an injector tool.** Zero injector work, permanently, in this program
  (decision E3 (a): "no game, HTTP only"). The injector's half is neither CI-covered nor cheaply
  probeable (`gk-fusion/tests/FusionRpg.Injector.Tests` needs interop refs and is not in `ci.yml`), which is a
  second reason the line is drawn at the process boundary.
- **Not a fake injector.** Decision D/E3 refuses the shim as a *substitute* for the injector: it is
  the wrong side of the never-fabricate boundary, and heartbeating as an injector makes
  `SimService.Guard()` return 409 (`gk-core/src/FusionRpg.Server/SimService.cs:25-30`), i.e. it switches off
  the surface the simulator needs. `/api/sim/*` stays a **feed** (the same `EventIngest` a real
  injector's envelopes reach), never a result.
- **Not a balance tool.** `gk-core/tools/CombatSim` and `gk-core/tools/SquadHarness` own balance, sweeps and
  determinism hashes. A simulator that also optimizes is two tools fighting over one report.
- **Not a UI, not a browser.** Decision C4 (a): HTTP-only state. The Playwright surface already
  covers what a player sees.
- **Not a second implementation.** The runner contains no domain math — `gk-core/tools/CombatSim`'s one rule
  (`gk-core/tools/CombatSim/README.md:8`) applied one layer up. A number the API does not return is a route
  or a service call, never a copied formula.
- **Not a new debug surface.** No new `/api/sim/*`, no `/api/debug/*`, no second MCP toolset. The
  `/api/test/*` group stays the seeding surface it already is.
- **Not a licence to delete the live path.** A green scenario never replaces a live probe for an
  injector claim (`docs/contributing/live-probe-standard.md:25-37`).

## Verified current state (2026-09-22, read in this worktree — do not re-specify)

| Capability | Where | What it does — and does not do |
|---|---|---|
| The real-server in-process host | `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:9`; env set at `:16-18`; species roster seeded in the ctor | Boots the **real** `Program` (public, `gk-core/src/FusionRpg.Server/Program.cs:2129`): real DI, catalogs, boot seeding, HTTP, SignalR, SQLite. One instance per collection, serialized: `gk-core/tests/FusionRpg.E2E.Tests/FoundationE2ETests.cs:308` (`E2ECollection : ICollectionFixture<RpgApiFactory>`). It does not play forward — each test resets and pokes |
| The sim feed (`/api/sim`, 54 routes) | `gk-core/src/FusionRpg.Server/SimEndpoints.cs:13`; gated at `gk-core/src/FusionRpg.Server/Program.cs:2050-2051`; flag `gk-core/src/FusionRpg.Server/SimFlags.cs:7-8` | The lawn-side event vocabulary. Every handler reaches the store through `SimService` (`gk-core/src/FusionRpg.Server/SimService.cs:68`), which publishes into the real `EventIngest` |
| The test group (`/api/test`) | `gk-core/src/FusionRpg.Server/SimEndpoints.cs:129`; reset `:136`; snapshot `:144`; four `seed-*-demo` writers `:184`, `:218`, `:240` and `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:29` | Fixtures and debug reads. **The writers write rows directly** — the clearest existing instance of what the honesty guard must allowlist |
| The effect-sim group | `gk-core/src/FusionRpg.Server/SimEffectEndpoints.cs:12`; mapped **unconditionally** at `gk-core/src/FusionRpg.Server/Program.cs:2053` | Input-only (grant/withdraw/fire feed `SimEffectHost`), but reachable on a non-sim server. Owner ruling F1: **drift, gate it** — filed as `DM-F2` in `tasks/debug-mcp-todo.md`, another program's row |
| The honest-scope guard | `gk-core/src/FusionRpg.Server/SimService.cs:25-30` (409 `live injector connected`); liveness `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1207-1210` (`Source == SourceInjector` ∧ heartbeat < 5 s) | The property the simulator inherits (decision D1 (b)): it hard-refuses while a live injector is connected |
| The only time control | `POST /api/test/expedition-due` `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:346-353` → `RpgStore.ForceExpeditionDue` `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202-215` | A SIM-only `UPDATE rpg_expeditions SET due_utc=…`. Owner ruling B3: **retire it** in favour of the clock seam |
| The sanctioned store substrate | `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs:37` (`Create()`, in-memory); source-linked into E2E by `<Compile Include>` (`gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj:27`) | A test-project helper with a compile link — decision F3 gives it a shared, non-test home |
| The declarative scenario precedent | `gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:80-81`; 49 fixtures under `gk-core/tests/fixtures/effects/scenarios/` | A JSON op-list with a seed in the header, a **closed** op switch and golden asserts. The format the new corpus extends (see §"Decisions this map makes" 1) |
| The no-math rule | `gk-core/tools/CombatSim/README.md:8` | "This tool contains no combat math" — every number comes back out of `gk-core/src/FusionRpg.Core` |
| Seed discipline + digest | required `--seed` `gk-core/tools/SquadHarness/Program.cs:35-39`; SHA-256 over canonical JSON `gk-core/tools/SquadHarness/DeterminismHash.cs:19-25` | A seed nobody chose is refused; the digest blanks provenance rather than hashing it |
| The digest exclusion recipe | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:163-172` | Four fields blanked, **a written reason per field** — the pattern the verdict's exclusion list must copy |
| Pure resolvers (determinism already bought) | `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs:15` (no I/O, no clock); `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:41` (`(tier, squad, seed, elapsedTicks)`); per-battle clock `gk-core/src/FusionRpg.Core/Battle/Timeline/SimulationClock.cs:84` | Server-scope time is the gap; battle-scope time is solved |
| The battle producer + the fabrication fallback | `gk-core/src/FusionRpg.Server/WebMatchService.cs:527` (`BuildSquad` returns `InstanceIds`); `:573` empty-roster fallback; `:713` `Synthetic` | A scenario that means to exercise the roster must assert the roster was used, or it inherits the synthetic squad silently |
| The four slice-0 families, all E2E-covered today | player create `gk-core/src/FusionRpg.Server/Program.cs:1260`; souls read `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:11-27`; summon `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:83`; roster `:45`; expedition dispatch/collect `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:282`, `:297`; progression summary/ledger `gk-core/src/FusionRpg.Server/Program.cs:1422`, `:1430`; runs `:1542` | Individual coverage only — `gk-core/tests/FusionRpg.E2E.Tests/SoulsE2ETests.cs`, `SummonE2ETests.cs`, `ExpeditionE2ETests.cs`, `RpgProgressionE2ETests.cs`. **Nothing owns the sequence** |
| Health carries sim-ness | `gk-core/src/FusionRpg.Contracts/Dtos.cs:48` (`simEnabled`), set from `SimFlags.Enabled` at `gk-core/src/FusionRpg.Server/Program.cs:1253` | The field the runner refuses on when it targets a real process |
| Real-process precedents | `scripts/smoke-player-pack.ps1:44-53` (a published exe as its own process); `gk-core/tests/FusionRpg.Server.Tests/Actions/SpecimenLoadoutEndpointsTests.cs:41-47` (real Kestrel on a loopback port) | The slow lane's host shape is already proven in the tree; the driver is not |

## Decisions this map makes (technical, resolved here)

1. **The scenario format is an extension of the effect-scenario envelope, not a sibling of it.**
   Same header (`{id, seed, …}`), same `op`-dispatch idiom, a superset of ops named after the route
   they call (`sim.*`, `api.*`, `read.*`, `expect.*`, `digest`). The repo has paid twice for inventing
   a parallel vocabulary (`docs/DESIGN-GATE.md` §1, the atom and action rows), and the shape lane's
   comparison (`rpg-simulator-shape-idea.md` §3.1) is the argument. **Whether the two runners share a
   step DTO or only the envelope and the fixture directory is a spec-level question** — the shape lane
   could not try it (`rpg-simulator-shape-idea.md` §9).
2. **Scenarios live under `gk-core/tests/fixtures/rpg-scenarios/**`** (decision C1 (a)), beside the
   `effects/scenarios/` precedent. They are test inputs, not content: `gk-data/packs/fusion/data/seed/**` is
   generator-owned and a scenario is authored.
3. **The verdict carries both an assertion and a digest** (decision C2 (a)): `expect.*` assertions
   fail loudly and specifically, a golden artifact pins the readings, and a SHA-256 digest over the
   declared readings catches drift. The **exclusion list is load-bearing** and carries a written
   reason per field, the `BattleGoldenTests.cs:163-172` pattern. The falsifier is a **same-run
   re-run**: the driver runs the scenario twice and fails if the two digests differ.
4. **One scenario file, two hosts** (decision E2 (a)): the in-process host is the default fast lane,
   the real process is the slow lane. Two hosts is not two harnesses — the file is the contract.
5. **The runner is a tool, not a test project** (decision A1 (a)), and only its **pure** parts are
   referenced by tests — `gk-core/tools/CombatSim`'s relationship to its four referencing test projects is
   the precedent.
6. **The honesty rule is mechanical, not a review discipline** (decision D4 (b)): a guard, not a
   checklist line. It has two halves — the *scenario* half (every digest-bearing read names an
   FE-facing route or a hub message, never `/api/test/snapshot`) and the *shim* half (every
   `/api/sim/*` handler reaches `RpgStore` only through `SimService`, with the reset route and the
   **four** `seed-*-demo` writers on an explicit allowlist with a written reason). The shim half is
   the shape lane's proposed `guard-sim-fabrication.py` (which does not exist yet —
   `rpg-simulator-shape-idea.md` §3.4 names it as the candidate); it owes a row in
   `gk-core/scripts/enforcement-registry.v1.json`.
7. **`DataTestStore` gets a shared, non-test home** (decision F3 (a)) — but only when a `tools/`
   consumer actually needs it. The slice-0 scenario is an E2E test and the E2E csproj's existing
   `<Compile Include>` link already works (`gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj:27`);
   the module exists for `scenario-runner`'s in-process host, and it is **jointly owned** with
   `data-test-substrate`, whose module `test-store-helper` says "Test-only"
   (`docs/architecture/data-test-substrate-map.md:82`) — a line this decision supersedes.
8. **The clock is product surface and is a separate, gated module** (decisions B1/B2/B3). Its product
   shape is co-owned with the module that consumes it, `world-continuity`'s `hibernation-clock`
   (`docs/architecture/world-continuity-map.md:118`), and its mechanism is a `src/`-wide sweep. No
   clock code is written before its spec names the product shape.
9. **Slice 0 is local-only** (decision C3 (c)); the CI lane is its own module, gated on the shape
   holding. A real-process run costs seconds to boot and a scenario with a wait costs minutes — it
   belongs in a slow lane, not in the default 60-project suite.

## Assumptions — corrected 2026-09-23 (lane `sim-t3-2`)

The section used to be headed *"correct these now"* and nobody did, so three of the five had been answered by
the program's own work and were still written as open bets. Each is now marked with what answered it.

1. **The four-family chain runs end to end today — RESOLVED, it does.** RS1's scenario executes the chain
   (`gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs`), the corpus is run in-process and on a real
   process by `RpgSimInProcHostTests`/`RpgSimProcessHostTests`, and the golden pins it
   (`gk-core/tests/fixtures/rpg-scenarios/golden/first-session-forward.verdict.json`). The declared digest is identical
   across fresh hosts and across both hosts (`daa9df408054f32e…`).
2. **The `gk-core/tools/RpgSim` content root is solvable — RESOLVED as the fallback this assumption itself predicted.**
   RS-F6 decided it: the CLI is a **real-process front end only** (`--host process` / `--base-url`), and the
   in-process host is a run parameter of the EMBEDDING host (`RpgApiFactory`), which is exactly "`scenario-runner`
   hosts from the E2E project's assembly and the CLI is a thin front end". The module's shape changed; the
   program's did not, and `gk-core/tools/RpgSim/RpgSim.csproj` still carries no reference at all.
3. **A canonical JSON of real readings can be stable across machines — RESOLVED, and the fear was wrong.**
   The digest is identical on two fresh in-process hosts and on a real process, and the golden holds it. The
   clock is **declared** now (RS3 landed: one seam, `FusionRpg.Core.Time.ServerClock`, plus a scenario-declared
   offset), and the exclusion list is written with a reason per field, which is what made the stability
   measurable instead of hoped for.
4. **`DataTestStore`'s non-test home — STILL OPEN, and its premise is retired.** No `tools/` consumer exists
   (`gk-core/tools/RpgSim` stayed store-free and RS-F6 kept the CLI a process front end), so the row is either closed as
   superseded or re-scoped to a future consumer — a manager ruling (**RS6**), with the 314-file/five-project
   fence as the second, independent blocker.
5. **`/api/sim/effect/*` is gated by `DM-F2` — RESOLVED, it is gated.** `MapSimEffect()` now sits INSIDE
   `if (SimFlags.Enabled)` (`gk-core/src/FusionRpg.Server/Program.cs:2240-2248`, with the owner ruling cited in the
   comment), and `DM-F2` is ticked in `tasks/debug-mcp-todo.md`.

## External dependencies — other programs' modules this program consumes or asks for

| Dependency / ask | Owner map / row | What this program needs | Gate |
|---|---|---|---|
| Gate `/api/sim/effect/*` behind `SimFlags.Enabled` | `tasks/debug-mcp-todo.md` row **`DM-F2`** (owner ruling F1) | A non-sim server exposes no sim-shaped route at all | **LANDED 2026-09-23** — `MapSimEffect()` is inside `if (SimFlags.Enabled)` (`gk-core/src/FusionRpg.Server/Program.cs:2240-2248`) and `DM-F2` is ticked |
| A shared, non-test home for `DataTestStore` | `docs/architecture/data-test-substrate-map.md:82` (module `test-store-helper`) | The helper reachable from `gk-core/tools/RpgSim` without a `<Compile Include>` link | **OPEN, premise retired** — no `tools/` consumer exists (RS6; a manager ruling decides close-or-re-scope) |
| The clock's **product** shape | `docs/architecture/world-continuity-map.md:118` (module `hibernation-clock`) + the `decisions.md` row | Agreement on what "the server can be told what time it is" means to a player, before the sweep | **LANDED 2026-09-23** — the decisions row, `rpg-simulator-spec-clock-seam.md`, and both increments (the seam is product surface, reported by the verdict, with a scenario-declared offset) |
| A sanctioned item-acquisition route (SSH4.9-P2's ask) | `tasks/strain-splice-host-todo.md:979-991`; owner ruling D2 (b): **the item program owns it** | The simulator only *proves* it; it never becomes the route | not a gate — it is the first defect the corpus will expose |
| `docs/README.md` map row | repo-wide doc index (outside this lane's fence) | A row pointing at this map and the plan | owed, cannot be added from here |

## Modules

Stable kebab-case ids, chosen once. Every module is provable with the game closed and with no PvZ
install. "Model?" is whether the module itself calls a model — none does. **The ten ids below are this
program's whole vocabulary.** Two other kebab ids appear in this map and in the plan —
`hibernation-clock` (`world-continuity`) and `test-store-helper` (`data-test-substrate`) — and they are
**cross-program module ids named as external dependencies, never ids this program builds**.

| # | Module id | Responsibility | Depends on | Spec | Wave |
|---|---|---|---|---|---|
| 1 | `first-session-scenario` | **Slice 0, no product code** (RS1): one E2E scenario test in `gk-core/tests/FusionRpg.E2E.Tests` that plays the four-family chain through real routes — create player → earn souls through the **real earn path** (a sim match into `EventIngest`, *not* `/api/test/seed-souls-demo`) → summon → read the roster back → dispatch an expedition → make it due → collect → read progression summary, the XP ledger and the run list. Its job is to prove the shape at zero risk and to be the reference behaviour the JSON format is authored from. Asserts the squad it fought with came from the roster it just built (`WebMatchService.cs:527`'s `InstanceIds`), i.e. refuses the `Synthetic` fallback (`:573`) | — | the shape IS the test and the corpus: `gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs` + `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` | **1** |
| 2 | `scenario-format` | The JSON scenario contract: the envelope (id, seed, declared clock, host), the **closed** op vocabulary named after the route it calls (`sim.*` / `api.*` / `read.*` / `expect.*` / `digest`), the rule that a `read.*` names an FE-facing route or a hub message, and the decision on whether the effect-scenario step DTO is extended or shared. Authoring rules for the corpus under `gk-core/tests/fixtures/rpg-scenarios/**` | — | `gk-core/tools/RpgSim/scenario-format.md` (beside the machine that enforces it) | **2** |
| 3 | `readback-verdict` | The verdict contract: every reading records **its source path**; the canonical-JSON digest with the **exclusion list written down with a reason per field**; the golden artifact (C2 (a)); the `expect.*` assertion style; the same-run double-run falsifier; the verdict JSON a human reads (seed, clock declaration, readings + sources, digest) | `scenario-format` | `gk-core/tools/RpgSim/readback-verdict.md` (beside the machine that emits it) | **2** |
| 4 | `scenario-runner` | **`gk-core/tools/RpgSim`** (RS2): reads a scenario, owns the seed, drives **one sequential client** (single writer — no concurrency), emits the verdict JSON, and **refuses to run unless the target reports `simEnabled: true`** (`gk-core/src/FusionRpg.Contracts/Dtos.cs:48`). Contains no domain math. Only its pure parts are referenced by tests. **It is a real-process front end only (RS-F6, decided 2026-09-23):** `--host process` or `--base-url`, never `--host inproc` — the in-process host is a run parameter of the EMBEDDING host (`RpgApiFactory` boots the real `Program` and supplies the `HttpClient`), and a tool that referenced the app assembly plus `Microsoft.AspNetCore.Mvc.Testing` would carry the whole server to run what the embedding host already runs, for no acceptance line the program has | `scenario-format`, `readback-verdict` | `gk-core/tools/RpgSim/README.md` + the CLI's own usage block (`gk-core/tools/RpgSim/RpgSimCli.cs`) | **2** |
| 5 | `inproc-host` | The **default fast lane**: `WebApplicationFactory<Program>` in-process with its own `FUSIONRPG_DATA`, reusing `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:9`'s proven boot. Owns the "settled" discipline around the background hosted services that tick on their own (`NotificationBootCatchUp`, `EventIngest`, compaction) — "the run reached a stable state" is defined by polling, not assumed | `scenario-runner` | `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs` + `RpgSimInProcHostTests.cs` | **2** |
| 6 | `shared-store-home` | Move `DataTestStore` off "lives in a test project, consumed by a `<Compile Include>` link" (decision F3 (a)) so a `tools/` consumer reaches it cleanly, **without a `src/` change** and without breaking the 311 test files that reference it. **Jointly owned with `data-test-substrate`** | — | **NOT WRITTEN, and the module's premise is retired:** `gk-core/tools/RpgSim` stayed store-free (RS2.4), so no `tools/` consumer ever needed the substrate moved — RS-F6 is the surviving question | **2 (premise retired)** |
| 7 | `process-host` | The **slow lane**: boot a real `FusionRpg.Server.exe` as its own process with `FUSIONRPG_SIM=1`, its own `FUSIONRPG_DATA`, an ephemeral loopback port, real HTTP and SignalR transport, clean start/stop/restart, and the `simEnabled` refusal. The only shape that answers the long-loop and restart questions (E2 (a)) | `scenario-runner` | `gk-core/tools/RpgSim/ProcessHost.cs` + `gk-core/tests/FusionRpg.E2E.Tests/RpgSimProcessHostTests.cs` | **3** |
| 8 | `honesty-guard` | The **automated** honesty check (decision D4 (b)), two halves: (a) scenario files — every digest-bearing read names an FE-facing route or a hub message, never `/api/test/snapshot`, and every `sim.*`/`api.*` op names a route that exists; (b) the shim — every `/api/sim/*` handler reaches `RpgStore` only through `SimService`, with the reset route and the **four** `seed-*-demo` writers allowlisted with a written reason. Green on the shipped corpus, red on a planted violation. Owes a row in `gk-core/scripts/enforcement-registry.v1.json` | `scenario-format`, `scenario-runner` | `gk-core/scripts/guard-sim-fabrication.py` (its allowlists and written reasons ARE the contract) + its registry row | **3** |
| 9 | `sim-ci-lane` | The CI decision (C3 (c)): slice 0 is **local-only**; once the shape holds, the fast in-process scenarios join CI (they are E2E tests by another name) and the real-process scenarios get the slow lane (a scheduled or labelled job that runs `dotnet run --project gk-core/tools/RpgSim`, **never** claiming a live game slot). The runner stays a tool; only its pure parts are referenced by the suite | `first-session-scenario`, `scenario-runner`, `inproc-host` | `rpg-simulator-spec-sim-ci-lane.md` (written 2026-09-23; the promised `docs/architecture/rpg-simulator/` tree is outside the file-prefix fence, so it is a sibling of this map — RS-F5) | **4** |
| 10 | `clock-seam` | **RS3, gated.** The full `TimeProvider` migration of the ambient wall-clock call sites, the retirement of `ForceExpeditionDue`'s SQL rewrite (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202-215`), the clock declaration printed in the verdict, and a guard banning ambient `DateTime.UtcNow` in `src/` outside the one clock type. The **9 deadline/wait-loop sites must not be simulated** and each carries a written reason — one is a trap: shifting the clock makes a healthy server report itself disconnected (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1207-1210`) | the `decisions.md` row (present) + a spec that names the seam's **product** shape; external `hibernation-clock` | `rpg-simulator-spec-clock-seam.md` (written 2026-09-23; the promised `docs/architecture/rpg-simulator/spec-clock-seam.md` tree is outside the delivery lane's file-prefix fence, so the spec is a sibling of this map — RS-F5) | **5 (gated)** |
| 11 | `seed-seam` | **RS-F4.** A run's RNG seed becomes an INPUT the idempotency key already carries: the **four** `Guid.NewGuid()` mints (`CreatureEndpoints.cs:95` summon, `ExpeditionEndpoints.cs:38` dispatch, `FusionEndpoints.cs:39` fusion, `WebMatchService.cs:122` web-match) derive from `(playerId, route stream, correlationId)` through the EXISTING chain (`WorldSeed.DeriveRollSeed`) instead of ambient randomness, so the corpus's declared digest can cover roster and battle values. Refused shapes with reasons: a `seed` body field, a `/api/sim/*` route (D3 (b)), a server-global seed config (wrong scope), a per-save secret (it would defeat the fresh-host reproducibility the sim needs) | `readback-verdict` (the digest it unblocks); the creature / expedition / fusion route families own the call sites | `rpg-simulator-spec-seed-seam.md` (written 2026-09-23) | **5 (waits on the predictability ruling, §6)** |

**Dependency direction, no cycles.** `scenario-format` → `readback-verdict` → `scenario-runner` →
{`inproc-host`, `process-host`}; `scenario-runner` → `honesty-guard`; `shared-store-home` feeds
`inproc-host` only; `first-session-scenario` depends on nothing and is the reference behaviour
`scenario-format` is authored from; `sim-ci-lane` comes after the shape holds; `clock-seam` and `seed-seam`
are last and both wait on a ruling. `honesty-guard` never depends on a host; `seed-seam` feeds
`readback-verdict`'s digest rather than depending on it.

## Build order

```
Wave 0  (this lane)  the index: map + plan + todo re-keyed
Wave 1  first-session-scenario                       ── CHECKPOINT S1
Wave 2  scenario-format → readback-verdict → scenario-runner → inproc-host
        shared-store-home ∥                            ── CHECKPOINT S2
Wave 3  process-host ∥ honesty-guard                  ── CHECKPOINT S3
Wave 4  sim-ci-lane                                   ── CHECKPOINT S4
Wave 5  clock-seam (gated)                            ── CHECKPOINT S5
```

**Why this order.** Slice 0 first, because it proves the shape with zero new surface and with the
substrate that already exists — if the chain does not run, nothing above it is worth building
(decision A2 (a), E1 (a)). The format is authored *from* the green chain rather than ahead of it, so
the op vocabulary is derived from what a real flow needs. The verdict contract comes before the
runner, because a runner without a verdict is a script. The in-process host precedes the real process
because it is the inner loop; the real process is the only shape that answers the long-loop question
and must follow (E2 (a)). The honesty guard lands with the first corpus it can check. CI is last of
the ungated work, because C3 (c) explicitly buys the shape before it buys the gate. The clock is last
and gated, because it is the largest sweep in the program and the only module with a product
consequence.

## Gates

| Gate | Proves | After |
|---|---|---|
| **S1 — the chain runs** | The four-family scenario is green locally through real routes; souls are earned through the real earn path, not a `seed-*-demo` writer; the squad is asserted roster-derived (`WebMatchService.cs:527` `InstanceIds`), so the `Synthetic` fallback (`:573`) cannot pass silently | wave 1 |
| **S2 — one file, two verdicts** | The same scenario file runs on the in-process host; the verdict carries seed, clock declaration and per-reading source paths; the digest is identical across two consecutive runs on a fresh `FUSIONRPG_DATA`; no digest-bearing reading comes from `/api/test/snapshot` | wave 2 |
| **S3 — the same file, the real process** | The same scenario runs against a real `FusionRpg.Server.exe` with `simEnabled: true`, and the runner refuses a target that does not report it; the real-process digest matches the in-process one where the scenario declares it must; a restart mid-scenario is survivable | wave 3 |
| **S4 — honesty is mechanical** | The guard is green on the shipped corpus, red on a planted fabricated read-back and on a planted direct-store `/api/sim/*` handler; the four `seed-*-demo` writers are allowlisted **by name**; the registry row exists | wave 3 |
| **S5 — the gate** | The fast scenarios run in CI with their exit check; the real-process lane is scheduled/labelled and claims no live game slot | wave 4 |
| **S6 — time is honest** | The clock seam is product surface per the `decisions.md` row; the migration is complete over the measured surface; `ForceExpeditionDue` is retired and no new store bypass exists; the 9 must-not-simulate sites are named with reasons and the freshness window is excluded; ambient `DateTime.UtcNow` in `src/` outside the clock type fails the guard | wave 5 |

## What this program does not touch

The injector and anything under `pvz.*`; `BattleEngine`'s round order or resolver math; the
`EffectBag`/Funnel/Writer paths; `ActorHub` or any combat compose; drop tables, the armoury or any
balance number; `SummonRoller`'s pity rules; the world turn phases; the web FE. The only `src/`
change this program plans is `clock-seam`, and it is gated.

## Open items carried into the specs

- `scenario-format`: does the effect-scenario step DTO extend, or do the two runners share only the
  envelope and the fixture directory? (Unproven by both idea lanes.)
- `readback-verdict`: the exclusion list's exact fields and a reason per field — written before the
  digest is trusted.
- `inproc-host`: the "settled" definition around the background hosted services.
- `process-host`: whether the restart-and-resume case is in this module or a follow-up.
- `sim-ci-lane`: new gate vs. part of the E2E project, decided when the shape holds (C3 (c)).
- `clock-seam`: the product shape, agreed with `world-continuity`'s `hibernation-clock`, and the
  9-site exclusion list with a reason each.

## NOT proved (this lane ran no code)

- **Nothing was built, tested, booted or probed.** This lane's fence is `docs/architecture/**` +
  `tasks/**`. Every claim above is a **read** of the tree with `file:line`, or a claim inherited from
  an idea lane and marked as such.
- **The four-family chain was not executed.** Each route is cited and each family has E2E coverage
  individually (`gk-core/tests/FusionRpg.E2E.Tests/SoulsE2ETests.cs`, `SummonE2ETests.cs`,
  `ExpeditionE2ETests.cs`, `RpgProgressionE2ETests.cs`), but the sequence was not run. The claim is
  "every step is cited and covered individually", not "the chain runs".
- **The clock surface is measured, by the guard rather than by a grep.** The figures this map repeated (203
  sites, 143 mechanical, 25 already injectable, 9 must-not-simulate) were **lane `sim-idea-b`'s binary-safe
  measurement**, carried by the `decisions.md` row — and RS3 has since migrated the surface and left a guard that
  reports what is left: `gk-core/scripts/guard-clock-seam.py` reads **1502 source files, 21 ambient reads (2 inside
  `ServerClock.cs`, 19 allowlisted with a reason each), 0 simulation-tree `ServerClock` references**, and a stale
  allowlist entry is itself a violation. `TimeProvider` now appears in `src/` — in `Program.cs`'s composition
  root, which adapts it into the seam (`rpg-simulator-spec-clock-seam.md` §0.1, shape B). The old `grep`-based
  count (200 lines, undercounting because `RpgStore.UniqueActors.cs` holds raw NUL bytes and `grep` calls it
  binary) is no longer how this program measures the surface.
- **The four `seed-*-demo` writers are four, not three.** The shape lane counted three
  (`rpg-simulator-shape-idea.md` §3.4) and named `gk-core/src/FusionRpg.Server/SimEndpoints.cs:184`, `:218`,
  `:240`; the fourth is `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:29` (`/seed-souls-demo`), verified in
  this worktree. The guard's allowlist must carry all four.
- **No `docs/architecture/rpg-simulator/spec-*.md` tree exists, and RS-F5 repointed every row (2026-09-23).**
  The Spec column now names each module's real document: `gk-core/tools/RpgSim/scenario-format.md`,
  `gk-core/tools/RpgSim/readback-verdict.md`, `gk-core/tools/RpgSim/README.md`, `RpgApiFactory.cs`,
  `gk-core/tools/RpgSim/ProcessHost.cs`, `gk-core/scripts/guard-sim-fabrication.py`, plus the three seam/lane specs that are
  siblings of this map (`rpg-simulator-spec-clock-seam.md`, `rpg-simulator-spec-seed-seam.md`,
  `rpg-simulator-spec-sim-ci-lane.md`). **One row says NOT WRITTEN on purpose:** `shared-store-home` (its
  premise was retired — `gk-core/tools/RpgSim` stayed store-free).
- **The `gk-core/tools/RpgSim` content root is answered (assumption 2), and `DataTestStore`'s home is not.** The content
  root question was settled by RS-F6 in favour of the fallback this map predicted — the CLI is a real-process
  front end and the E2E project hosts in-process — so there is nothing left to attempt there. The helper's home
  remains RS6's, with its premise retired and a manager ruling owed.
- **`docs/README.md` has no row for this program** and this lane's fence cannot add one.
- **Counts quoted from the idea docs** are the idea lanes' readings except where this map says it
  re-counted: **54 `/api/sim` routes** (re-derived here by counting `sim.Map*` in
  `gk-core/src/FusionRpg.Server/SimEndpoints.cs`), **4 `seed-*-demo` writers** (the shape lane said 3),
  **49 effect fixtures** (`ls gk-core/tests/fixtures/effects/scenarios/ | wc -l`) and **`TimeProvider` = 0 in
  `src/`**. The **60 CI test projects** figure is the idea lanes' `grep` over `.github/workflows/ci.yml`
  and was **not** re-derived here.

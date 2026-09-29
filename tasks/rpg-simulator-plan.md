# Plan: `rpg-simulator` — the RPG feature simulator

**Status:** drafted 2026-09-22 from the **owner-cleared** decision sheet
([`rpg-simulator-decisions.md`](rpg-simulator-decisions.md), all twenty questions answered) and the
capability map [`docs/architecture/rpg-simulator-map.md`](../docs/architecture/rpg-simulator-map.md).
Task list: [`rpg-simulator-todo.md`](rpg-simulator-todo.md). **The map is the index**: every module id
below exists in the map's module table, and this plan adds none. Where this plan and a cleared
decision disagree, the decision wins and this file is wrong.

Inputs it sequences: [`rpg-simulator-idea.md`](../docs/architecture/rpg-simulator-idea.md) (lane
`sim-idea-a`), [`rpg-simulator-shape-idea.md`](../docs/architecture/rpg-simulator-shape-idea.md)
(lane `sim-idea-b`), and the [`decisions.md`](../docs/architecture/decisions.md) row *"The server can
be told what time it is — product surface, not a test seam"*.

---

## 1. What is already true (checked in this worktree, 2026-09-22)

The map's §"Verified current state" table is the evidence base; this section states only what *gates*
the plan, so nobody re-checks it from scratch.

| Premise | State | Evidence |
|---|---|---|
| All twenty owner questions are answered, five as overrides | **Done** | `tasks/rpg-simulator-decisions.md` carries an `ANSWER:` line per question (B1/B2/B3/F1/F2 are the overrides) |
| The clock's `decisions.md` row exists, so `clock-seam` has its gate | **Done** | `docs/architecture/decisions.md:174` |
| The real-server in-process host exists and is CI-covered | **Done** | `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:9`; one instance per collection, serialized (`gk-core/tests/FusionRpg.E2E.Tests/FoundationE2ETests.cs:308`) |
| The sim feed exists and is gated on `FUSIONRPG_SIM` | **Done** | `gk-core/src/FusionRpg.Server/Program.cs:2050-2051`; flag `gk-core/src/FusionRpg.Server/SimFlags.cs:7-8` |
| The honest-scope refusal exists and is the property the simulator inherits | **Done** | `gk-core/src/FusionRpg.Server/SimService.cs:25-30`; liveness `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1207-1210` |
| Every slice-0 route exists and each family has E2E coverage **individually** | **Done** | player create `gk-core/src/FusionRpg.Server/Program.cs:1260`; souls `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:11-27`; summon `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:83`; roster `:45`; dispatch/collect `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:282`, `:297`; progression `gk-core/src/FusionRpg.Server/Program.cs:1422`, `:1430`; runs `:1542` |
| A declarative scenario format already ships, with a closed op switch | **Done** | `gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:80-81`; 49 fixtures under `gk-core/tests/fixtures/effects/scenarios/` |
| The digest idiom and its exclusion recipe already ship | **Done** | `gk-core/tools/SquadHarness/DeterminismHash.cs:19-25`; `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:163-172` |
| The real-process host shape is proven in the tree | **Done** | `scripts/smoke-player-pack.ps1:44-53`; `gk-core/tests/FusionRpg.Server.Tests/Actions/SpecimenLoadoutEndpointsTests.cs:41-47` |
| `simEnabled` is on the wire, so the runner can refuse a non-sim target | **Done** | `gk-core/src/FusionRpg.Contracts/Dtos.cs:48`, set at `gk-core/src/FusionRpg.Server/Program.cs:1253` |

**And what was not true when this plan was drafted — corrected 2026-09-23 (lane `sim-t3-2`).** The paragraph
below is kept because a plan that silently rewrites its own starting point is worse than one that shows the
distance: each item now carries what answered it.

- ~~No `gk-core/tools/RpgSim`~~ — **it exists** (`gk-core/tools/RpgSim/**`, and it references nothing: the CLI is a real-process
  front end, RS-F6).
- ~~no scenario format or corpus~~ — **both exist**: `gk-core/tools/RpgSim/scenario-format.md`,
  `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`, and the format's own contract test validates every
  file under that tree.
- ~~no verdict/digest contract~~ — **it exists** (`gk-core/tools/RpgSim/readback-verdict.md`), with the golden artifact
  landed (`gk-core/tests/fixtures/rpg-scenarios/golden/first-session-forward.verdict.json`).
- ~~no honesty guard~~ — **it exists** (`scripts/guard-sim-fabrication.ps1`, wired through the enforcement
  registry, green on the corpus and red on three planted violations).
- ~~`ForceExpeditionDue`'s store rewrite is still shipped~~ — **retired**: the store method and its route are
  deleted and the corpus makes an expedition due with a `clock.set` declaration (RS3 increments 5a/5b).
- **`DataTestStore` still lives in a test project — STILL TRUE.** `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs`
  with a `<Compile Include>` link as its only cross-project seam; RS6 owns the move, its premise is retired (no
  `tools/` consumer exists), and a manager ruling decides close-or-re-scope.
- ~~`DM-F2` (`/api/sim/effect/*` ungated) is open~~ — **landed**: `MapSimEffect()` sits inside
  `if (SimFlags.Enabled)` (`gk-core/src/FusionRpg.Server/Program.cs:2240-2248`) and `DM-F2` is ticked.
- **`docs/README.md` has no row for this program — STILL TRUE**, and outside this program's fence.

## 2. The cleared decisions, as binding constraints

Each row says what the owner answered and which module or gate is bound by it. **No row re-opens a
cleared question.**

| Decision | Answer | Binds |
|---|---|---|
| **A1** | `gk-core/tools/RpgSim` CLI, with slice 0 living in the E2E project first | `scenario-runner` (wave 2); `first-session-scenario` (wave 1) |
| **A2** | Slice 0 is one E2E scenario file, no product code | `first-session-scenario` — it must add no production surface |
| **A3** | `rpg-simulator` is a named program with a map + plan | this lane (RS5) |
| **B1** | **Full `TimeProvider` migration** (override) | `clock-seam`; S6 |
| **B2** | The clock is **product** surface (override); a `decisions.md` row before a spec | `clock-seam` is gated on the row (present) **and** on a spec naming the product shape |
| **B3** | **Retire `ForceExpeditionDue`'s SQL rewrite** (override) | `clock-seam`'s S6 acceptance: no store bypass survives |
| **C1** | Scenarios live under `gk-core/tests/fixtures/rpg-scenarios/**` | `scenario-format`; RS2.1 |
| **C2** | Golden artifact **and** a hash for determinism | `readback-verdict`; S2 |
| **C3** | Slice 0 is **local-only**, CI once the shape holds | `sim-ci-lane` is wave 4, not wave 1 |
| **C4** | HTTP-only | no module owns a browser surface; `honesty-guard`'s read-back rule names routes and hub messages only |
| **D1** | Hard-refuse while a live injector is connected, like `SimService.Guard()` | `scenario-runner` refuses; `inproc-host`/`process-host` inherit the 409 |
| **D2** | The item program owns a sanctioned acquisition route; the simulator proves it | external ask, not this program's build |
| **D3** | Untestability **is** the finding | no new `/api/sim/*` route licenses a missing condition; `honesty-guard` refuses one |
| **D4** | An **automated** guard reviews scenario honesty | `honesty-guard`; S4 |
| **E1** | Slice 0 is the four-family chain (economy, roster, expeditions, progression) | `first-session-scenario` |
| **E2** | Both hosts, one scenario file | `inproc-host` + `process-host`; S3 |
| **E3** | No injector shim in wave 1; "no game, HTTP only" | the whole program's boundary |
| **F1** | `/api/sim/effect/*` ungated is **drift — gate it** (override) | external row `DM-F2`, another program |
| **F2** | Fix the stale `AGENTS.md` count (already done) | closed; `AGENTS.md` no longer carries the number |
| **F3** | Give `DataTestStore` a shared, non-test home | `shared-store-home` (wave 2), jointly owned with `data-test-substrate` |

## 3. Dependency graph

```
Wave 0   (this lane)  map + plan + todo re-keyed
Wave 1   first-session-scenario ─────────────────────────────────────┐
                                                                     │
Wave 2   scenario-format → readback-verdict → scenario-runner → inproc-host
         shared-store-home ∥ (feeds inproc-host when the in-memory substrate is used)
                                                                     │
Wave 3   scenario-runner → { process-host ∥ honesty-guard } ──────────┤
                                                                     │
Wave 4   sim-ci-lane (after the shape holds — C3 (c)) ────────────────┤
                                                                     │
Wave 5   clock-seam (gated: decisions.md row + a spec naming the product shape)
```

Arrows point one way; there are no cycles. `honesty-guard` depends on the format and the runner's op
dispatch, never on a host. `first-session-scenario` depends on nothing — it is the reference behaviour
`scenario-format` is authored from, which is what the cleared row means by "depends on RS1 only for the
scenario format it must read".

## 4. Waves and tasks

Every row carries its module id from the map. Verification uses the path-owned boundary
(`scripts/verify-change.ps1 -Paths … -Session <id>`), never a full unfiltered suite. **New paths
(`gk-core/tools/RpgSim/**`, `gk-core/tests/fixtures/rpg-scenarios/**`) are unmapped today** — the map's read of
`gk-core/tests/fixtures/**` matches the test-verification-boundary program's G8 finding. Adding the boundary
entries is part of the row that first writes those paths, and an unmapped path is a
verification-boundary defect to repair, never a reason to run the full suite.

### Wave 0 — the index (this lane, RS5)

- **RS5 — the program's map + plan, module ids, and the CI decision** · S · *approved A3 (a)* · module:
  none (this row *is* the index).
  - Acceptance: `docs/architecture/rpg-simulator-map.md` names every module id, its one-line purpose
    and its spec path; `tasks/rpg-simulator-plan.md` sequences only ids the map names; every row in
    `tasks/rpg-simulator-todo.md` carries its module id; the CI decision (C3 (c), slice 0 local-only)
    is stated in both.
  - Acceptance: `python scripts/audit-doc-citations.py --scope <each doc> --strict` reports 0 HIGH.
  - Verify: `.\scripts\verify-change.ps1 -Paths docs/architecture/rpg-simulator-map.md,tasks/rpg-simulator-plan.md,tasks/rpg-simulator-todo.md -Session rpg-simulator-map`

### Wave 1 — slice 0: the shape, with no product code (RS1)

- **RS1 — one E2E scenario file, the four-family chain** · S · *approved E1 (a) / A2 (a) / C3 (c)* ·
  module: `first-session-scenario`.
  - Acceptance: one new test file under `gk-core/tests/FusionRpg.E2E.Tests/` plays create player → earn souls
    through the **real earn path** (a sim match into `EventIngest`, as `SoulsE2ETests` does — **not**
    `/api/test/seed-souls-demo`, which writes the balance row directly) → summon → read the roster
    back → dispatch an expedition → make it due → collect → read the progression summary, the XP
    ledger and the run list. Every step is a real route; no product code is added.
  - Acceptance (the fabrication line): the test asserts the squad the battle resolved with came from
    the roster it just built — the `InstanceIds` `BuildSquad` returns
    (`gk-core/src/FusionRpg.Server/WebMatchService.cs:527`) — so the empty-roster `Synthetic` fallback
    (`:573`, `:713`) cannot pass silently.
  - Acceptance: it is green **locally** and is **not** added to a new CI gate (C3 (c)).
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tests/FusionRpg.E2E.Tests/<scenario file>.cs -Session <id>`
  - Note: the row is *the reference behaviour* the JSON format is authored from. If the chain does not
    run, that is the finding the program exists to produce (the shape lane's §7 argument) — report it
    as a reachability defect with `file:line`, do not route around it.

**Checkpoint S1** — the four-family chain is green locally, every step a real route, and the
roster-derived squad is asserted (not inferred). The map's gate S1.

### Wave 2 — the contract, the runner, the fast host (RS2.1–RS2.4, RS6)

- **RS2.1 — the scenario contract** · M · *approved C1 (a)* · module: `scenario-format`.
  - Acceptance: the envelope (id, seed, declared clock, host) and the **closed** op vocabulary
    (`sim.*` / `api.*` / `read.*` / `expect.*` / `digest`) are specified; ops are named after the
    route they call, so the vocabulary is derived from the route table rather than authored fresh; a
    `read.*` must name an FE-facing route or a hub message; the decision on extending the
    effect-scenario step DTO (`gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:80-81`) versus
    sharing only the envelope is made **with the expressibility test that the shape lane could not
    run** (`rpg-simulator-shape-idea.md` §9).
  - Acceptance: `gk-core/tests/fixtures/rpg-scenarios/**` is named as the corpus home; its verification
    boundary is added in the same change.
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/RpgSim/scenario-format.md,gk-core/tests/fixtures/rpg-scenarios/**,gk-core/scripts/verification-boundaries.v1.json -Session <id>`
    — **repointed 2026-09-23 (lane `sim-t3-2`)**: this line used to name
    `docs/architecture/rpg-simulator/spec-scenario-format.md`, a path in the promised tree that does not exist
    (RS-F5). The contract is `gk-core/tools/RpgSim/scenario-format.md`, beside the machine that enforces it.

- **RS2.2 — the verdict and digest contract** · M · *approved C2 (a)* · module: `readback-verdict`.
  - Acceptance: every reading records its **source path**; a digest-bearing read may not come from
    `/api/test/snapshot` (`gk-core/src/FusionRpg.Server/SimEndpoints.cs:144`); the canonical-JSON digest's
    **exclusion list is written down with a reason per field**, the
    `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:163-172` pattern; the golden artifact and
    the same-run **double-run falsifier** are specified.
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/RpgSim/readback-verdict.md -Session <id>`
    — **repointed 2026-09-23 (lane `sim-t3-2`)**: it named
    `docs/architecture/rpg-simulator/spec-readback-verdict.md` (RS-F5); the contract is
    `gk-core/tools/RpgSim/readback-verdict.md`, beside the machine that emits it.

- **RS2.3 — `gk-core/tools/RpgSim`, the runner** · M · *approved A1 (a)* · module: `scenario-runner`.
  - Acceptance: the tool reads a scenario, owns the seed, drives **one sequential client** (no
    concurrency — the digest depends on total order), writes the verdict JSON (seed, clock
    declaration, readings + sources, digest), and **refuses unless the target reports
    `simEnabled: true`** (`gk-core/src/FusionRpg.Contracts/Dtos.cs:48`). It contains **no domain math**.
  - Acceptance: `gk-core/tools/RpgSim/**` and `gk-core/tests/fixtures/rpg-scenarios/**` gain verification boundaries;
    the tool's pure parts are what a test project may reference (the `gk-core/tools/CombatSim` relationship).
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/RpgSim/**,gk-core/tests/fixtures/rpg-scenarios/**,gk-core/scripts/verification-boundaries.v1.json -Session <id>`

- **RS2.4 — the default in-process host** · S · *approved E2 (a)* · module: `inproc-host`.
  - Acceptance: the same scenario file runs in-process on `WebApplicationFactory<Program>` with its
    own `FUSIONRPG_DATA`, reusing `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:9`; "settled" is
    **defined by polling** around the background hosted services, not assumed; the digest is
    identical across two consecutive runs on a fresh data dir.
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/RpgSim/**,gk-core/tests/fixtures/rpg-scenarios/** -Session <id>`

- **RS6 — `DataTestStore` gets a shared, non-test home** · S · *approved F3 (a)* · module:
  `shared-store-home`. **Jointly owned with `data-test-substrate`**, whose spec calls the helper
  "Test-only" (`docs/architecture/data-test-substrate-map.md:82`) — a line this decision supersedes.
  - Acceptance: a `tools/` consumer reaches the helper without a `<Compile Include>` link, with **no
    `src/` change**, and every existing consumer keeps compiling (the helper is referenced by test
    files across Data/Server/E2E).
  - Acceptance: the `data-test-substrate` map's "Test-only" line is corrected, or the erratum is filed
    as a row on that program and named here.
  - Verify: `.\scripts\verify-change.ps1 -Paths <the moved helper>,gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj,gk-core/tests/FusionRpg.Server.Tests/FusionRpg.Server.Tests.csproj,gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj -Session <id>`

**Checkpoint S2** — one scenario file, one host, a readable verdict, a stable digest, and the substrate
reachable from a tool. The map's gate S2.

### Wave 3 — the slow lane and the honesty guard (RS2.5, RS4)

- **RS2.5 — the real-process slow lane** · M · *approved E2 (a)* · module: `process-host`.
  - Acceptance: a real `FusionRpg.Server.exe` boots as its own process with `FUSIONRPG_SIM=1`, its own
    `FUSIONRPG_DATA`, an ephemeral loopback port, real HTTP and SignalR transport; the runner refuses a
    target that does not report `simEnabled: true`; the process is stopped and its data dir removed on
    every exit path (a failed delete is a failure, not a swallowed catch).
  - Acceptance: the same scenario file is used — the in-process and real-process digests agree where
    the scenario declares they must, and the disagreement is **reported**, never smoothed.
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/RpgSim/**,gk-core/tests/fixtures/rpg-scenarios/** -Session <id>`

- **RS4 — the honesty guard** · S · *approved D4 (b)* · module: `honesty-guard`.
  - Acceptance, scenario half: every `read.*`/`digest`-bearing op in the shipped corpus names an
    FE-facing route or a hub message, never `/api/test/snapshot`; every `sim.*`/`api.*` op names a
    route that exists. Green on the corpus, **red on a planted fabricated read-back**.
  - Acceptance, shim half: every `/api/sim/*` handler reaches `RpgStore` only through `SimService`,
    with the reset route (`gk-core/src/FusionRpg.Server/SimEndpoints.cs:136`) and the **four** `seed-*-demo`
    writers (`:184`, `:218`, `:240`, `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:29`) on an explicit
    allowlist carrying a written reason. Red on a planted direct-store handler.
  - Acceptance: the guard owes a row in `gk-core/scripts/enforcement-registry.v1.json`, with its `tier` and
    `status` set there rather than here.
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/guard-sim-fabrication.ps1,gk-core/scripts/enforcement-registry.v1.json,gk-core/tests/fixtures/rpg-scenarios/** -Session <id>`

**Checkpoint S3** — the same file on both hosts, and honesty is mechanical. The map's gates S3 and S4.

### Wave 4 — the gate (RS7)

- **RS7 — the CI lane** · S · *approved C3 (c)* · module: `sim-ci-lane`.
  - Acceptance: the fast in-process scenarios run in CI **with their exit check** (they are E2E tests
    by another name, so the E2E project is the default home); the real-process scenarios get a
    scheduled or labelled lane that runs the tool and **claims no live game slot** — a simulator needs
    no game install. The runner stays a tool; only its pure parts are referenced by the suite.
  - Acceptance: the first CI run of the new step is green; the `CiWiringGuardTests` completeness rule
    holds (every `tests/**/*.Tests.csproj` in `ci.yml` or a named exemption).
  - Verify: `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml,<any new test project or registry entry> -Session <id>`

**Checkpoint S4** — the shape survives a push. The map's gate S5.

### Wave 5 — the clock (RS3), gated

- **RS3 — full `TimeProvider` migration, then retire `ForceExpeditionDue`** · L · *approved B1 (a),
  B3 (a); B2 (b) makes it product surface* · module: `clock-seam`.
  - **Gates before any code:** (i) the `decisions.md` row — present (`docs/architecture/decisions.md:174`);
    (ii) the seam's spec names its **product shape** and that shape is agreed with the
    module that consumes it, `world-continuity`'s `hibernation-clock`
    (`docs/architecture/world-continuity-map.md:118`). Until both hold, this row is **blocked on an
    external agreement**, not on its own work. **Both gates met, and the spec's path repointed 2026-09-23
    (lane `sim-t3-2`)**: the spec is `docs/architecture/rpg-simulator-spec-clock-seam.md` (a sibling of the map,
    not the promised `docs/architecture/rpg-simulator/` tree — RS-F5), and its §4 carries the agreement with
    `hibernation-clock`, answered.
  - Acceptance: the migration covers the surface the `decisions.md` row measured (203 sites — 143
    mechanical ISO emissions, 25 already injectable, 24 other, 2 date-shaped); the **9 deadline/wait
    sites are excluded and each carries a written reason**, and the freshness window is named
    explicitly — `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1207-1210` is a trap: shift the clock and a
    healthy server reports itself disconnected.
  - Acceptance: `ForceExpeditionDue`'s `UPDATE` is retired
    (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202-215`) and no store bypass replaces it; the
    verdict prints the clock declaration; a guard fails ambient `DateTime.UtcNow` in `src/` outside the
    one clock type.
  - Acceptance: the migration is a sweep of `src/`, so this row's verification is the one place a
    **broad** suite is legitimate — it crosses `FusionRpg.Data`, `FusionRpg.Server`, `FusionRpg.Core`,
    `FusionRpg.Injector`, `FusionRpg.Launcher` and `FusionRpg.CheatCore` together, which is the
    repo's own criterion 2 for a full run (`AGENTS.md`, "When the whole suite is actually the right
    call").
  - Verify: `.\scripts\verify-change.ps1 -Paths <every migrated file> -Session <id>` for each
    increment; `.\scripts\test-fast.ps1 -AllDefault` at the row's close, and the injector build
    (`FusionRpg.Injector` needs interop refs and is not in CI).

**Checkpoint S5** — time is honest, the bypass is gone, and the exclusions are written. The map's
gate S6.

## 5. Gates

| Gate | After | Passes when |
|---|---|---|
| **S0 — the index** | wave 0 | The map names every module id and spec path; the plan references no id the map lacks; every todo row carries its id; the citation audit is 0 HIGH |
| **S1 — the chain runs** | wave 1 | The four-family scenario is green locally, souls earned through the real earn path, the squad asserted roster-derived |
| **S2 — one file, one host, a verdict** | wave 2 | The verdict carries seed + clock + per-reading sources; the digest is stable across two same-invocation runs; no read comes from `/api/test/snapshot` |
| **S3 — two hosts, one file** | wave 3 | The same scenario runs against a real process that reports `simEnabled: true`, and the runner refuses one that does not |
| **S4 — honesty is mechanical** | wave 3 | The guard is green on the corpus, red on both planted violations; the four `seed-*-demo` writers are allowlisted by name; the registry row exists |
| **S5 — the gate** | wave 4 | The fast scenarios run in CI with an exit check; the real-process lane claims no live slot |
| **S6 — time is honest** | wave 5 | The seam is product surface per the `decisions.md` row; the migration is complete; `ForceExpeditionDue` is retired; the 9 exclusions carry reasons; ambient `DateTime.UtcNow` fails the guard |

## 6. External asks (not this program's work)

| Ask | Owner | Why it gates us |
|---|---|---|
| Gate `/api/sim/effect/*` behind `SimFlags.Enabled` | `tasks/debug-mcp-todo.md:364` (**`DM-F2`**), owner ruling F1 | Until it lands, the `simEnabled` refusal is the only thing keeping a sim route off a player's install |
| The clock's product shape | `world-continuity`'s `hibernation-clock` (`docs/architecture/world-continuity-map.md:118`) | RS3 cannot be specified before the product shape is agreed (B2 (b)) |
| A shared, non-test home for `DataTestStore` | `data-test-substrate` module `test-store-helper` (`docs/architecture/data-test-substrate-map.md:82`) | Jointly owned; the "Test-only" line is superseded by F3 (a) |
| A sanctioned item-acquisition route | the item program (owner ruling D2 (b)) | Not a gate — it is the first defect the corpus is built to expose |
| A `docs/README.md` row for this program | repo-wide doc index | Owed; outside this lane's fence |

## 7. What could invalidate this plan

1. **Slice 0 does not run.** Then the shape is unproven and every later wave is speculative — and the
   failure is a reachability finding worth more than the plan.
2. **The `gk-core/tools/RpgSim` content root proves unworkable.** The runner then hosts from the E2E
   assembly and the CLI is a front end; the module boundaries survive, the packaging changes.
3. **The clock's product shape is refused or reshaped by `world-continuity`.** `clock-seam` shrinks to
   the mechanical half or waits; nothing above it depends on it.
4. **`DM-F2` is ruled intentional.** Then `process-host` carries a named residual exposure instead of
   a gate, and the runner's refusal must be stronger.
5. **The format cannot extend the effect-scenario step DTO** (shape-idea §9). Then `scenario-format`
   owns a new DTO, and the "no second vocabulary" decision is kept by naming ops after routes, not by
   reusing the type.

## 8. NOT proved

- **Nothing was run.** This plan's fence is `docs/architecture/**` + `tasks/**`: no build, no test, no
  server, no scenario. Every claim about code is a read with `file:line` (the map's table) or is
  inherited from an idea lane and marked as such.
- **The four-family chain was not executed** — its routes are cited and individually E2E-covered, but
  the sequence is assumption 1 above.
- **The clock surface is not re-measured here.** The 203/143/25/24/9/2 figures are lane `sim-idea-b`'s
  binary-safe measurement carried by the `decisions.md` row. A plain
  `grep -rn "DateTime.UtcNow" src/ --include=*.cs | wc -l` in this worktree returned **200 lines**,
  which undercounts: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs` holds raw NUL bytes and
  `grep` calls the file binary. `TimeProvider` appears **0** times in `src/`.
- **The `seed-*-demo` writer count is four, not three** — the shape lane named three
  (`rpg-simulator-shape-idea.md` §3.4); the fourth is `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:29`,
  verified here. The guard's allowlist must carry all four.
- **The `gk-core/tools/RpgSim` content root was answered (RS-F6), and the `DataTestStore` non-test home was not
  attempted** — the first was settled in favour of the fallback this plan's own risk 2 predicted (the CLI is a
  real-process front end; the E2E project hosts in-process), the second is RS6 with its premise retired.
- **The module specs exist, beside their machines.** Three are siblings of the map
  (`rpg-simulator-spec-clock-seam.md`, `rpg-simulator-spec-seed-seam.md`, `rpg-simulator-spec-sim-ci-lane.md`)
  and the rest are the documents the map's Spec column names; the promised
  `docs/architecture/rpg-simulator/spec-*.md` tree was repointed away (RS-F5, closed).
- **Row sizes are estimates**, not measurements: `M`/`L` reflect the number of unknown call sites and
  hosts, and the first increment of any row may revise its neighbours.

---

## 9. Wave-2 addendum (lane `sim-runner`, 2026-09-23) — errata and rulings asked

Wave 1 and Wave 2 (except RS6) are delivered. Five things this plan says differently than the tree now
does. **None of them re-opens a cleared decision**; each is a delta between the plan's promise and the
lane's fence or the code's measured behaviour.

1. **The module specs are written beside their machine, not in `docs/architecture/rpg-simulator/`.**
   This plan promises `docs/architecture/rpg-simulator/spec-<module-id>.md` for all ten modules. A
   delivery lane's fence does not include `docs/architecture/**`, so the RS2.1 and RS2.2 contracts live at
   `gk-core/tools/RpgSim/scenario-format.md` and `gk-core/tools/RpgSim/readback-verdict.md`, each with a header saying why
   (`gk-core/tools/CombatSim/README.md` is the precedent). **Ruling asked:** repoint the map's spec paths at the
   tool, or move the two documents into the promised tree — filed as **RS-F5**. **RESOLVED 2026-09-23 (lane
   `sim-t3-2`): the map is repointed** — every module row's Spec column now names its real document, the header
   states the rule instead of promising a tree, and the three seams/lane specs are siblings of the map; one row
   (`shared-store-home`) says NOT WRITTEN on purpose because its premise is retired.
2. **The op vocabulary gained a `test.*` surface.** §4's RS2.1 row and the map's decision 1 name four call
   prefixes (`sim`/`api`/`read`/`expect`) plus `digest`. The shipped slice-0 chain calls two
   `/api/test/*` routes (`POST /api/test/seed-souls-demo`, `POST /api/test/expedition-due`), which are
   neither the `/api/sim/*` feed nor player-facing; folding them into `sim.*` would lose the
   fixture-surface distinction the RS4 guard needs. Recorded in `scenario-format.md` §3.
3. **`host` is a run parameter, not an envelope field.** RS2.1's acceptance lists `host` in the envelope;
   owner ruling E2 (a) is *one file, two hosts*, and an envelope that named its host would be two files.
   The verdict records which host ran. Recorded in `scenario-format.md` §2.
4. **RS6's premise is retired, and its paths are outside every delivery lane's fence.** The row exists so a
   `tools/` consumer can reach `DataTestStore`. The shipped runner takes an `HttpClient` and opens no
   store, so there is no such consumer today; and the move would need the helper's project plus five
   consumer csprojs (314 referencing test files), none of which this lane may edit. **Ruling asked:** see
   the RS6 row for the two options.
5. **`gk-core/tools/RpgSim/**` has no verification boundary.** `tools/**` is not an enforced root, so
   `guard-verification-boundaries.py` stays green while `verify-change.ps1` refuses every path in the new
   tool (`VERIFICATION BOUNDARY MISSING`, `scripts/verify-change.ps1:114`). Filed as **RS-F3** with the
   house pattern to follow (`gk-forge/tools/AtomImporter/**` + its test project).

**New rows this wave opened, all in `tasks/rpg-simulator-todo.md`:** RS-F3 (the tool's boundary),
RS-F4 (two server-minted RNG seeds make the post-summon half non-deterministic — measured), RS-F5 (the
spec paths), RS-F6 (no CLI `--host inproc`), RS-F7 (the XP ledger's one-letter timestamp field).

**Measured, not assumed (RS2.4):** two fresh in-process hosts, one scenario file — the declared digest is
identical (`daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e`), while the falsifier over
every reading moves 71–110 named pointers. That gap *is* RS-F4, and it is why the corpus asserts closed
vocabularies and attribution over the outcome-dependent readings instead of digesting them.

---

## 10. Wave-3/5 addendum (lane `sim-t3-1`, 2026-09-23) — what landed, and two fences

1. **RS2.5 landed** (commit `e5676ca22`): `gk-core/tools/RpgSim/ProcessHost.cs` boots a real
   `FusionRpg.Server.exe` (own `FUSIONRPG_DATA`, free loopback port, `FUSIONRPG_SIM=1`, real HTTP and
   SignalR) and stops it again with its data dir removed on every exit path; the CLI gained
   `--host process`. The same scenario file on a fresh in-process host and a fresh real process gives
   the **same declared digest** (`daa9df408054f32e…`) while the whole-reading falsifier moves 109 named
   pointers — RS-F4, reported. **RS-F3 landed with it** (`rpgsim-tool` in
   `gk-core/scripts/verification-boundaries.v1.json`), because RS2.5's own verification could not run without it.
2. **RS4 is blocked by a denied path.** Its deliverable is `scripts/guard-sim-fabrication.ps1`; the
   orchestrator's pipeline guard refuses a new `scripts/guard-*.ps1`, and the enforcement registry
   cannot carry a row for a script that does not exist. The design and the measured surface (55
   `/api/sim` handlers, 0 touching `RpgStore`; 12 `/api/test` direct-store handlers) are preserved in
   the todo row and the ledger. Filed as **RS-F10** (the guard fence).
3. **RS3's gate (ii) is met**: `docs/architecture/rpg-simulator-spec-clock-seam.md` names the seam's
   product shape (one injected `TimeProvider`, one signed offset reported by `/health`, never a route),
   the boundary with `world-continuity`'s `hibernation-clock`, the 9 exclusions with reasons, and this
   lane's own binary-safe count (**213 occurrences**, vs the row's 203 call sites). The map's clock row
   is repointed at it.
4. **RS3 is two-thirds fenced.** 164 of the 213 sites (`FusionRpg.Data` 142, `Injector` 19, `Launcher` 2,
   `CheatCore` 1) and the `ForceExpeditionDue` retirement itself
   (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202-215`) are outside this lane's paths. Filed as
   **RS-F9**; this lane can land the Core and Server increments only.

**New rows this wave opened:** RS-F8 (the Guard boundary test's 2-minute timeout under contention),
RS-F9 (RS3's fence), RS-F10 (the guard scripts' fence).
5. **RS3's mechanism hit a build fact (2026-09-23).** `FusionRpg.Core` and `FusionRpg.Contracts` are
   `net6.0`; `FusionRpg.Data`/`FusionRpg.Server` are `net8.0`. `System.TimeProvider` is .NET 8+, so owner
   ruling B1 (a)'s *mechanism* cannot be the seam's stored type in the assembly 142 of the 213 sites
   compile against (Core must stay `net6.0` for the Unity Injector). The spec's §0 records two executable
   shapes and asks for the ruling; **RS3's increments 1 and 2 do not start until it lands** — filed as
   **RS-F13**. A second measured erratum: the purity scan bans clock symbols *by name*, so `ServerClock`
   must not land in Core before `BannedSymbols` gains it (**RS-F12**), or a `Core/Effects` wall-clock read
   slips past the gate built to catch it. The `/health` clock declaration is fenced by
   `HealthDto`/`ToHealth` (**RS-F11**).

---

## 11. Wave-5 addendum (lane `sim-t3-2`, 2026-09-23) — RS3 closed, and the digest's scope said out loud

1. **RS3 landed and is closed**, in six commits: `ServerClock` in shape B (one configured
   `Func<DateTimeOffset>`, `TimeProvider` as a net8.0 *input*), the Core / Server / Data / Injector /
   Launcher / CheatCore sites migrated (the guard's own reading: `1502 source files, 21 ambient reads — 2
   inside the clock type, 19 allowlisted — 0 simulation-tree ServerClock references`), a declared
   `clock.mode: offset` honest for both hosts at boot (5a), and the mid-run `clock.set` input that retired
   `ForceExpeditionDue`'s `UPDATE` and its route (5b). Two verification gaps are named on the row rather
   than smoothed: the close gate `test-fast.ps1 -AllDefault` was killed by an infrastructure error (no
   reading), and the Injector build needs a game dir (`guard-injector-compile.ps1` SKIPs by design).
2. **RS4 landed**: `scripts/guard-sim-fabrication.ps1`, wired through the enforcement registry, green on
   the corpus and red on three planted violations.
3. **The digest's scope is intentional, and this is the statement RS-F4's acceptance branch (b) asks for.**
   The corpus's declared digest covers **host-stable readings only** — a terminal state, a tier, a row id,
   the run engine, closed vocabularies, attribution, the fabrication line — and it deliberately does NOT
   cover the roster's rolled species/rarity/element or the battle outcomes, because those are downstream of
   **four** server-minted RNG seeds (`CreatureEndpoints.cs:95`, `ExpeditionEndpoints.cs:38`,
   `FusionEndpoints.cs:39`, `WebMatchService.cs:122`). **The reason is measured, not assumed:** on two fresh
   in-process hosts with one scenario file the declared digest is identical
   (`daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e`) while the falsifier over every
   reading moves 71–110 named pointers. That residue is not a defect in the runner and not a gap to paper
   over with a wider exclusion list — it is **RS-F4**, and the fix is a *seed seam* specified in
   `docs/architecture/rpg-simulator-spec-seed-seam.md` (map module row 11): derive each seed from
   `(playerId, route stream, correlationId)` through the existing `WorldSeed.DeriveRollSeed` chain, which
   the sim's own scenario-controlled correlation id already drives. **The implementation waits on a ruling**
   about the one product consequence the spec names (§5/§6): the derivation is public, so a client could
   compute a chosen key's roll offline — capability-equivalent to today's unlimited retry, but cheaper.
   Until that ruling, this paragraph is the program's stated scope, and the digest is honest rather than
   incomplete-by-accident.
4. **A correction to RS-F4's row, measured:** it names *two* minting sites. There are *four*; the fusion and
   web-match sites were found by scanning for the mint idiom rather than trusting the count.

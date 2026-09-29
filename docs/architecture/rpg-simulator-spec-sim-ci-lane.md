# The CI lane — `sim-ci-lane` (rpg-simulator RS7)

**Module id:** `sim-ci-lane` (capability map [rpg-simulator-map.md](rpg-simulator-map.md), module row 9).
**Program:** `rpg-simulator`. Plan: `tasks/rpg-simulator-plan.md` (Wave 4). Todo: `tasks/rpg-simulator-todo.md` (RS7).
**Owner ruling this implements:** **C3 (c)** — slice 0 is local-only *until the shape holds*; then CI.
**Depends on:** `first-session-scenario`, `scenario-runner`, `inproc-host`, `process-host` (all landed).
**Machine:** `.github/workflows/ci.yml` — the only artifact this module owns, and it is **outside every delivery
lane's fence**; this spec is the contract that fence is waiting for.
**Tests:** the lane's own gate is `CiWiringGuardTests` (completeness) plus the scenarios themselves.

> **Where this document lives, and why.** The map promised `docs/architecture/rpg-simulator/spec-sim-ci-lane.md`.
> The delivery lane's fence is `docs/architecture/rpg-simulator*`, a *file prefix*, so this spec is a sibling of
> the program's other documents and the map's row points here — the same class of erratum as RS-F5, already
> recorded for the clock and seed seams.

---

## 0. The measured starting point (2026-09-23, lane `sim-t3-2`)

**The fast lane is already wired, and one clause of RS7's acceptance is not.** Both halves matter, because the
row's summary ("the CI lane is unbuilt") would send a lane to build what exists:

| What | Measured |
|---|---|
| The fast in-process scenarios run in CI **with their exit check** | `.github/workflows/ci.yml:333` — `dotnet test gk-core/tests/FusionRpg.E2E.Tests/… -c Release` followed by `if ($LASTEXITCODE -ne 0) { throw "FusionRpg.E2E.Tests failed" }`. The in-process scenarios are tests in that project (`RpgScenarioSlice0E2ETests`, `RpgSimInProcHostTests`, `RpgSimGoldenTests`). |
| The real-process scenarios run there too, unfiltered | the same step passes **no `--filter`**, and `ci.yml:352-368` *asserts* that CI stays the unfiltered full profile (only the BalanceGuard step is filtered) — so the `DiskSemantics`-tagged `RpgSimProcessHostTests` run in CI. |
| The runner stays a tool | `gk-core/tools/RpgSim/RpgSim.csproj` carries **no `ProjectReference` and no `PackageReference`**; the E2E project references IT (the correct direction). |
| The wiring is guarded for test projects | `gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs` asserts both that Server/E2E are named in ci.yml and that **every** `tests/**/*.Tests.csproj` appears there. |
| **The literal gap** | no CI step invokes the **CLI** (`dotnet run --project gk-core/tools/RpgSim -- --host process …`). With no new step, "the first CI run of the new step is green" has nothing to run. |

## 1. The one sentence the module obeys

> **The scenarios run in CI through the project that can host them, and any lane that runs the CLI claims no
> game slot.**

## 2. The two lanes, concretely

**Fast lane — the E2E project, and it is already the lane.** `gk-core/tests/FusionRpg.E2E.Tests` runs unfiltered in CI
with its own exit check. The contract is therefore *negative*: the step stays unfiltered (the assertion at
`ci.yml:352-368` is the guard), and a new scenario test lands in that project rather than in a new lane. Nothing
about a scenario needs its own workflow step, because a scenario IS an E2E test by another name (owner ruling
C3 (c)'s own words).

**Slow lane — the real process, and this is the clause in question.** Today it is the same unfiltered step:
`RpgSimProcessHostTests` boots a real `FusionRpg.Server.exe` through `ProcessHost`, on its own data directory and
a free loopback port, and tears it down. That satisfies the *intent* ("the real-process scenarios get a lane …
that claims no live game slot") and not the *letter* ("…running the tool"). The two shapes, and the ask:

| Shape | What it is | Cost |
|---|---|---|
| **(a) the E2E step IS the lane** | the contract names `ci.yml:333`'s unfiltered step as the slow lane, on the ground that the CLI's `--host process` path is the same `ProcessHost` code the test drives (RS-F6 decided the CLI is a real-process front end, so the test and the CLI are two callers of one machine) | **nothing to build**; RS7 closes against its own measurement, and the row's "first CI run of the new step" clause is retired as moot |
| **(b) the CLI runs in its own labelled step** | a step (or a scheduled workflow) runs `dotnet run --project gk-core/tools/RpgSim -- --host process --data-dir <fresh> --server-exe <path> --golden gk-core/tests/fixtures/rpg-scenarios/golden/<id>.verdict.json`, so CI also exercises the CLI's flags and the golden comparison | a `ci.yml` edit (**outside this lane's fence**) **plus** a wiring assertion of its own, because `CiWiringGuardTests` only walks `tests/**/*.Tests.csproj` — nothing fails today if a tool step is deleted, and adding that assertion lands in the protected `gk-core/tests/FusionRpg.Guard.Tests/**` tree |

**This spec does not choose.** The choice is the manager's erratum (RS7's row carries it), and the measurement
above is what makes it cheap: (a) needs no work, (b) needs two edits in two fenced trees.

## 3. What "claims no live game slot" means, mechanically

The phrase is about the **game**, not about concurrency:

- the lane boots a **headless server process** (`FUSIONRPG_SIM=1`, its own `FUSIONRPG_DATA`, a free loopback
  port) and never launches the game, the injector or a browser;
- it therefore never touches `FUSIONRPG_GAME_POOL` or the source game install, and the three-slot live-probe
  protocol (`docs/contributing/live-probe-standard.md` §9) does not apply to it — that protocol exists because a
  *live probe* needs the game's window, and this lane runs the game closed;
- a fresh data directory is sufficient since **CS-F3** (the server self-heals the shipped species tree on its
  first boot, `gk-core/src/FusionRpg.Server/Program.cs:683`), so the lane needs **no provisioning step** — the fact that
  made shape (b) cheap.

## 4. What the wiring must keep true

1. **The E2E project's step stays unfiltered** — `ci.yml:352-368` already asserts it, and a filter would silently
   drop the `DiskSemantics` real-process tests.
2. **Every scenario in the corpus is executed by some CI step.** Today that is the E2E project (the corpus file is
   read by `RpgScenarioSlice0E2ETests` and `RpgSimGoldenTests`); a new corpus file with no test is unwired, and
   the honesty guard does not check that (`gk-core/scripts/guard-sim-fabrication.py` checks what a scenario *asserts*,
   not whether anything runs it).
3. **The runner stays a tool** — only its pure parts are referenced by the suite.
4. **A tool step, if shape (b) is chosen, gets its own assertion.** `CiWiringGuardTests` covers test projects
   only; without a new assertion a `dotnet run --project gk-core/tools/RpgSim` line could vanish unnoticed.

## 5. NOT covered here

- **The workflow file itself.** `.github/workflows/**` is outside this program's delivery fences; this spec is
  the contract it waits for, and RS7's row records the erratum ask.
- **The game and the injector.** Wave 1 is "no game, HTTP only" (owner ruling E3 (a)); a lane that needed the
  game would be a live probe, which this module is not.
- **The browser.** Owner ruling C4 (a): HTTP-only.
- **The golden's refresh in CI.** The lane compares; refreshing is a human act with a commit message
  (`readback-verdict.md` §5), never a CI behaviour.

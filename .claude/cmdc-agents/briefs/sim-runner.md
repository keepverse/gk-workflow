# Lane `sim-runner` — RS2: the scenario contract and `gk-core/tools/RpgSim`

**Session:** `rpg-sim-runner` · **Program:** `rpg-simulator` · **Mode:** worktree
**Fence:** `gk-core/tools/RpgSim/**`, `gk-core/tests/fixtures/rpg-scenarios/**`, `gk-core/tests/FusionRpg.E2E.Tests/**`,
`tasks/rpg-simulator-todo.md`, `tasks/rpg-simulator-plan.md`, `tasks/reports/**`

## Read first

- `tasks/rpg-simulator-plan.md` — **Wave 2** (`RS2.1`–`RS2.4`, `RS6`) and the gates; the plan is the sequencing authority
- `docs/architecture/rpg-simulator-map.md` — the module ids your work belongs to (`scenario-runner`, `scenario-format`)
- `tasks/rpg-simulator-decisions.md` — the owner **cleared** all 20 questions; its `ANSWER:` lines are binding
- `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` + `gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs` — RS1, already delivered: the scenario format in use and the runner that reads it

## Work, in plan order

1. **RS2.1 — the scenario contract.** Formalize the format slice 0 already uses (its runner refuses a step whose
   declared route is not the one it calls — keep that property). It must express: steps (`op` + args), the
   declared route each step names, the read-back each verdict uses, and any expectation the scenario carries.
2. **RS2.2–RS2.4 and RS6** in the plan's order — the runner (`gk-core/tools/RpgSim`), driving **the same scenario file
   against two hosts**: in-process `WebApplicationFactory<Program>` as the default, a real
   `FusionRpg.Server.exe` as the slow lane (approved `A1 (a)` / `E2 (a)`).
3. Land each numbered item as **its own commit** with its evidence, and tick its row with the numbers printed.

## The rules that make this a simulator and not a mock

- A scenario may **sequence and read**; it may **not compute**.
- Every verdict is a **read-back** through the same GET route the web FE calls — never a response body, never a
  debug-only accessor (`docs/contributing/live-probe-standard.md` §3).
- ⛔ Never fabricate: a debug surface may *trigger* a real operation, never invent its result.
- Scenarios live under `gk-core/tests/fixtures/rpg-scenarios/**` (approved `C1 (a)`); CI wiring is **not** in this wave
  (approved `C3 (c)` was local-only for slice 0 — if you believe the runner should join CI, say so as a question,
  do not wire it).

## Verification

- `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet`
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session rpg-sim-runner`

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- findings routed to the owning todo in the same commit, **with the id asserted present**
- do not re-open a cleared decision: if one looks wrong, say so in one sentence with evidence and leave the answer

## Boundaries

- Do not edit generated data; do not hand-edit `gk-core/data/tuning/**` (publish `v{n+1}`); do not widen a guard.
- Your session record's `worktree` path must be **ABSOLUTE**.

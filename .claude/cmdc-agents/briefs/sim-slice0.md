# Lane `sim-slice0` — RS1: the slice-0 scenario that proves the simulator's shape

**Session:** `rpg-simulator-slice0` · **Program:** `rpg-simulator` · **Mode:** worktree
**Fence:** `gk-core/tests/FusionRpg.E2E.Tests/**`, `gk-core/tests/fixtures/rpg-scenarios/**`, `tasks/**`

## What this is, and why it is the first thing built

The owner approved **E1 (a) / A2 (a) / C3 (c)** on 2026-09-22 (`tasks/rpg-simulator-decisions.md`): slice 0 is
**one new E2E scenario file, no product code, local-only** — the smallest thing that proves the shape, with zero
new surface and zero risk. Read that sheet and `docs/architecture/rpg-simulator-idea.md` §5.3 (the slice's own
spec) before writing anything.

## The scenario, exactly

*Scenario `first-session-forward`*, every step a **real route**, in order:

1. create a player
2. award souls through the real `/api/souls` path
3. summon a creature through the real summon route
4. read the roster back
5. dispatch a real expedition
6. make it due
7. collect it
8. read back `/api/rpg/progression/{id}/summary`, the soul ledger, and the run list

It crosses four families (economy, roster, expeditions, progression) using only routes that already have E2E
coverage — so if it fails, the failure is the **shape**, not a missing route.

## The rules that make it a simulator and not a mock

- **The runner may sequence and read; it may not compute.** `gk-core/tools/CombatSim`'s one rule, one layer up.
- **Every verdict is a read-back** through the same GET route the web FE calls — never a response body, never a
  debug-only accessor (`docs/contributing/live-probe-standard.md` §3).
- **The fabrication assertion is the point:** assert that the squad it fought with came from the roster it just
  built. That is the line between "ran the real path" and "made it look like it did".
- Scenario data lives under `gk-core/tests/fixtures/rpg-scenarios/**` (approved C1 (a)).
- **Local-only for now** (approved C3 (c)): do not wire it into `ci.yml`.

## A known bypass you may hit, and must name rather than hide

`ForceExpeditionDue` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202`) is a SIM-only `UPDATE` — a store
bypass. Step 6 may need it while it exists. If you use it: say so in the commit and in the evidence, and note
that the owner's ruling **B3 → A** retires it in favour of the product clock seam (row `RS3`, gated by
`docs/architecture/decisions.md`). Do not invent a second bypass.

## Evidence contract

- the test green, with the **numbers printed** (passed/failed/total), run locally
- the file(s) committed, and the exact command used
- an explicit **NOT-proved** list (e.g. "this does not prove the real-process host; that is RS2's slow lane")
- findings routed to the owning todo with the id asserted present

## Boundaries

- ⛔ No product code. If a route you need does not exist, **that is a finding** — report it, do not add it.
- Do not edit another lane's files. `tasks/**` is shared: name your artifacts uniquely.
- Your session record's `worktree` path must be **ABSOLUTE** (a relative one makes `verify-change.ps1` exit 1 on
  DRIFT in your own record — measured on lane `isg-gen-fix`).

## Verification

- `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet`
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session rpg-simulator-slice0`

# Lane `sim-map` — the `rpg-simulator` capability map and plan

**Session:** `rpg-simulator-map` · **Program:** `rpg-simulator` · **Mode:** worktree
**Fence:** `docs/architecture/**`, `tasks/**` — **docs only. No product code, no test edits, no scripts.**

## Your inputs (read these first, in this order)

1. `tasks/rpg-simulator-decisions.md` — **the owner CLEARED all 20 questions on 2026-09-22.** Its `ANSWER:`
   lines are binding. Five were overrides of the lanes' recommendations: **B1 → full `TimeProvider` migration**,
   **B2 → the clock is PRODUCT surface**, **B3 → retire `ForceExpeditionDue`'s SQL rewrite**, **F1 → the ungated
   `/api/sim/effect/*` is drift**, **F2 → fix the stale `AGENTS.md` count** (already done).
2. `docs/architecture/decisions.md` — the row *"The server can be told what time it is — product surface, not a
   test seam"* (written from B2). It carries the measured migration surface: 203 call sites, 143 mechanical ISO
   emissions, 25 already injectable, **9 deadline/wait loops that must not be simulated**.
3. `docs/architecture/rpg-simulator-idea.md` (lane `sim-idea-a`) and
   `docs/architecture/rpg-simulator-shape-idea.md` (lane `sim-idea-b`) — the two merged idea docs.
4. `tasks/rpg-simulator-todo.md` — rows `RS1`–`RS5`, which your plan must sequence.

## Deliverable

1. **`docs/architecture/rpg-simulator-map.md`** — the capability map, following the conventions of an existing
   map in this repo (read `docs/architecture/party-dungeon-map.md` or `docs/architecture/test-verification-boundary-map.md`
   and match their shape). Modules get **stable kebab-case ids chosen once**; each module gets a one-line purpose
   and the spec file that will describe it. The map is the index — no plan or task may reference a module id that
   is not in it.
2. **`tasks/rpg-simulator-plan.md`** — the sequenced plan over those ids, honoring the cleared decisions:
   in-process real-server host as the default with a real-process slow lane (A1/E2), the scenario layer as the
   interface with read-back verdicts (C2), scenarios under `gk-core/tests/fixtures/rpg-scenarios/**` (C1), slice 0
   local-only (C3), HTTP-only (C4), a hard refusal while a live injector is connected (D1), the honesty guard
   (D4), `DataTestStore` given a shared non-test home (F3), and **the clock work (RS3) gated by the
   `decisions.md` row and by a spec that names the seam's product shape**.
3. Update `tasks/rpg-simulator-todo.md` so its rows reference the module ids.

## Evidence contract

- every claim about existing code carries `file:line`
- an explicit **NOT-proved** list
- the artifacts committed, and your report ends with the report block

## Boundaries

- ⛔ Docs only. If something needs code, name the row and the owner — do not write it.
- Do not re-open a cleared question. If a decision looks wrong, say so in one sentence with evidence and leave
  the answer as the owner gave it.
- Your session record's `worktree` path must be **ABSOLUTE** (a relative one makes `verify-change.ps1` exit 1 on
  DRIFT in your own record — measured on lane `isg-gen-fix`).

## Verification

- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session rpg-simulator-map`

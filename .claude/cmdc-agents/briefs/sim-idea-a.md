# Lane `sim-idea-a` — an RPG-feature simulator: what exists, what it must cover, and a first-cut idea

**Session:** `rpg-sim-idea-a` · **Program:** `rpg-simulator` (new) · **Mode:** worktree
**Fence:** `docs/architecture/**`, `tasks/**` — **read-only everywhere else. This is an IDEA task: no product
code, no test edits, no script edits.**

## Why this exists (owner's framing, 2026-09-22)

> *"our work on this program dont use pvz much but a lot of rpg feature and we lack of simulator"*

Most of this repo's work is **RPG-domain** — progression, items, sockets/words, aptitudes, delves, empire,
passives, notifications — and almost all of it is currently exercised either by unit tests or by the **live
path**, which needs the real game (PVZ + MelonLoader + injector + a server). That makes a whole class of
end-to-end RPG behaviour expensive to test and impossible to test in CI. The owner wants an **idea** for a
simulator, not an implementation.

## Read this FIRST, and use it as the method

`.agents/skills/idea-refine/SKILL.md` — the owner asked for this explicitly (*"tell them much use idea skill"*).
Follow its process (understand → diverge → converge), and say in the doc which step each section is.

## What already exists — survey it, do not re-derive it from scratch

Name each of these by `file:line` and say what it does and does not cover:

- `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs` — an **in-process** boot of the real `Program` (`WebApplicationFactory<Program>`). The closest thing to a simulator that exists today.
- `SimFlags` and the `/api/test/*` helpers, plus `app.MapSimAndProbes()` in `gk-core/src/FusionRpg.Server/Program.cs` — what they can seed, and what they refuse when a real injector is connected.
- `DataTestStore.Create()` (the sanctioned in-memory store helper) and `SeedImportRunner.RunSelfHealing` (the real boot seeding path).
- `gk-core/tools/CombatSim` and `gk-core/tools/SquadHarness` (+ `gk-core/tests/FusionRpg.SquadHarness.Tests`) — what they simulate today and how they are driven.
- The **live path** (game → injector → server) and exactly which RPG behaviours today require it.

## Deliverable

One idea document at `docs/architecture/rpg-simulator-idea.md` (add `-a` if the sibling lane's file exists),
containing:

1. **The problem, restated in one paragraph**, with the specific RPG feature families it must serve.
2. **A feature inventory**: for each RPG family (progression/level-ups, items + instances + sockets/words,
   aptitudes, delves, empire, passives, notifications, …), where its logic lives (`file:line`) and what a
   simulator would have to drive to exercise it end to end.
3. **Divergent options** (at least four, honestly different): e.g. extend the in-process E2E factory; a headless
   "sim host" server mode; a scripted-client harness against a real server; a fake injector/game shim; a
   scenario/DSL layer. For each: what it covers, what it cannot, and its cost.
4. **Convergence**: your recommended shape, and the smallest first slice that would prove it.
5. **Risks and anti-goals** — especially: anything that would let a simulator *fabricate* a result instead of
   running the real domain path (`docs/contributing/live-probe-standard.md` §1 and the "never fabricate" rule
   are binding here), and how the idea avoids becoming a second, drifting implementation of the server.
6. **Open Questions** — a numbered list, each one a decision only the owner can make, phrased so it can be
   answered in one line. This is an explicit deliverable, not an afterthought.

## Evidence contract

- every factual claim carries `file:line`
- an explicit **NOT-proved** list (what you did not verify)
- the doc committed, and your report ends with the report block

## Boundaries

- ⛔ No product code, no tests, no scripts — if the idea needs a change somewhere, describe it, do not make it.
- Do not edit another lane's files; `tasks/**` is shared, so name your own artifacts uniquely.
- Your session record's `worktree` path must be **ABSOLUTE** (a relative one makes `verify-change.ps1` exit 1 on
  DRIFT in your own record — measured on lane `isg-gen-fix`).

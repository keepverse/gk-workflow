# Lane `sim-idea-b` — the SHAPE of an RPG-feature simulator: design space, prior art, recommended architecture

**Session:** `rpg-sim-idea-b` · **Program:** `rpg-simulator` (new) · **Mode:** worktree
**Fence:** `docs/architecture/**`, `tasks/**` — **read-only everywhere else. This is an IDEA task: no product
code, no test edits, no script edits.**

## Why this exists (owner's framing, 2026-09-22)

> *"our work on this program dont use pvz much but a lot of rpg feature and we lack of simulator"*

A sibling lane (`sim-idea-a`) is surveying **what exists and what the simulator must cover**. Your job is the
complementary half: **what shape it should take** — the design space, prior art, and a recommended architecture
with its trade-offs. Do not duplicate the feature inventory; reference it and go deeper on the design.

## Read this FIRST, and use it as the method

`.agents/skills/idea-refine/SKILL.md` — the owner asked for this explicitly (*"tell them much use idea skill"*).
Follow its process (understand → diverge → converge) and label which step each section is.

## Design space to explore honestly (at least these, and say what each costs)

- **In-process host** (extend `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs`, a `WebApplicationFactory<Program>`):
  fastest, but lives inside the test host — what can it not do?
- **Headless server mode** (a real server process with a sim flag, driven over HTTP/SignalR like the game would
  be): closest to the live path, and the only shape that can exercise persistence, hubs and long-running loops.
- **Scripted-client / scenario layer**: a way to express "a player plays for N in-game days" deterministically —
  what language, what determinism guarantees (seeded RNG, a controllable clock), and how scenarios are stored.
- **Fake game / injector shim**: what a stand-in for the PVZ side must emit for the RPG domain to advance, and
  where that crosses into fabricating state.
- **Record/replay**: capturing a real session once and replaying it as a regression fixture — value and risk.

For each: coverage, determinism, cost, and what it makes impossible.

## Prior art — look both inward and outward

- **Inward:** `gk-core/tools/CombatSim`, `gk-core/tools/SquadHarness` (+ `gk-core/tests/FusionRpg.SquadHarness.Tests`), the
  `SimFlags` / `/api/test/*` surface (`gk-core/src/FusionRpg.Server/Program.cs`), `DataTestStore`, and any headless
  entry point already used by CI. Name each by `file:line` and say what a simulator can borrow from it.
- **Outward:** how comparable projects test a game's *server/domain* without the client (headless backends,
  deterministic simulation, property-based and model-based testing, golden-run suites). Cite what you read.

## Deliverable

One idea document at `docs/architecture/rpg-simulator-shape-idea.md`, containing:

1. **The design space** (above), each option with coverage/determinism/cost/impossibilities.
2. **A recommended architecture**, drawn as a small text diagram: what runs, who drives it, where state lives,
   how a scenario is written, how a run is proven deterministic.
3. **The CI story**: what of this can run in CI today, what needs a separate lane, and the smallest first slice
   that would prove the shape (one feature family, end to end).
4. **The boundary that must not be crossed**: this repo's rule is that a debug API may *trigger* a real
   operation but never *fabricate* its result (`docs/contributing/live-probe-standard.md` §1). Say exactly where
   a simulator sits relative to that rule, and which of your options would violate it.
5. **Open Questions** — a numbered list, each answerable in one line, addressed to the owner. Explicit
   deliverable, not an afterthought.

## Evidence contract

- every factual claim carries `file:line` (or a URL for outward prior art)
- an explicit **NOT-proved** list
- the doc committed, and your report ends with the report block

## Boundaries

- ⛔ No product code, no tests, no scripts — describe changes, never make them.
- `tasks/**` is shared: name your own artifacts uniquely. Do not touch the sibling lane's files.
- Your session record's `worktree` path must be **ABSOLUTE** (a relative one makes `verify-change.ps1` exit 1 on
  DRIFT in your own record — measured on lane `isg-gen-fix`).

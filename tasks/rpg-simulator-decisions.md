# RPG simulator — decision sheet (CLEARED by the owner 2026-09-22)

All recommendations approved except five overrides: **B1 → A, B2 → B, B3 → A, F1 → B, F2 → update stale.**

From `docs/architecture/rpg-simulator-idea.md` (lane `sim-idea-a`) and
`docs/architecture/rpg-simulator-shape-idea.md` (lane `sim-idea-b`), both merged.
Answer inline after `ANSWER:` — one line each. ⭐ marks the lane's own recommendation; where the two lanes
converged independently it says **CONVERGED**.

## What the two lanes agree on already (so these are not questions)

Both arrived independently at the same core: **the host is the real server** (`WebApplicationFactory<Program>`
in-process as the default, a real `FusionRpg.Server.exe` as the slow lane), **the unit is a scenario** that may
sequence and read real routes but never compute, **every verdict is a read-back through the same GET route the
web FE calls**, and **the fake-injector shim is refused** in wave 1 (it is the wrong side of the
never-fabricate boundary, and it would switch off the sim surface it needs — `SimService.cs:26`).

---

## A. Where it lives and what it is

**A1. The runner's home** — *(a)* `gk-core/tools/RpgSim` CLI, the `CombatSim`/`SquadHarness` precedent, agent-runnable
⭐ **CONVERGED** · *(b)* a fixture inside `gk-core/tests/FusionRpg.E2E.Tests` (no new project, CI-native) ·
*(c)* a verb on an existing tool (`SquadHarness`/`CombatSim`)
ANSWER: (a) `gk-core/tools/RpgSim` CLI -- with slice 0 living in the E2E project first (see A2)

**A2. May slice 0 be a test file with no product code?** — *(a)* yes: lane `sim-idea-a`'s slice 0 is exactly one
new E2E scenario file, zero new surface ⭐ · *(b)* no: build the tool first
ANSWER: (a) yes -- slice 0 is one E2E scenario file, no product code

**A3. Is `rpg-simulator` a named program?** — *(a)* yes, with a map + plan (`docs/architecture/rpg-simulator-map.md`,
`tasks/rpg-simulator-plan.md`); a todo already exists ⭐ · *(b)* no, this idea feeds another program
ANSWER: (a) yes -- named program, map + plan

## B. Time — the constraint that decides the shape

Lane `sim-idea-b` measured it: `DateTime.UtcNow` on **203 real call sites** in `src/` (Data 142 · Server 38 ·
Injector 17 · Core 3 · Launcher 2 · CheatCore 1), classified as **143 mechanical ISO emissions**, **25 already
injectable** (`utcNow ?? UtcNow`), **24 other**, **9 deadline/wait loops that must NOT be simulated**, 2
date-shaped reads.

**B1. Which clock option?** — *(a)* full `TimeProvider` migration of all 203 · *(b)* a **single offset seam**
behind `SimFlags` ⭐ · *(c)* keep today's per-feature DB rewind (`ForceExpeditionDue`'s `UPDATE`)
ANSWER: (a) FULL `TimeProvider` migration -- owner OVERRIDE of the lane recommendation

**B2. Is "the server can be told what time it is" a test capability or a product one?** — *(a)* test-only, seam
behind `SimFlags` · *(b)* **product** (hibernating worlds catch up lazily; a player can move their machine clock)
— if product it needs a `decisions.md` row **before** a spec
ANSWER: (b) PRODUCT -- needs a `decisions.md` row before any spec -- owner OVERRIDE

**B3. Approve retiring `ForceExpeditionDue`'s SQL rewrite** (`RpgStore.Expeditions.cs:202`) in favour of the seam?
— *(a)* yes · *(b)* no, keep the bypass and document it as SIM-only
ANSWER: (a) yes -- retire `ForceExpeditionDue` SQL rewrite -- owner OVERRIDE

## C. Scenarios and their verdicts

**C1. Where do scenario files live?** — *(a)* `gk-core/tests/fixtures/rpg-scenarios/**` (the `effects/scenarios/`
precedent) ⭐ · *(b)* `gk-data/packs/fusion/data/seed/**` (content, generator-owned) · *(c)* a new `data/sim/scenarios/` ·
*(d)* `tools/**` · *(e)* `docs/` as a research artifact
ANSWER: (a) `gk-core/tests/fixtures/rpg-scenarios/**`

**C2. Golden files or assertion-only?** — *(a)* golden artifact **and** a hash for determinism (what the repo
already does for effect plans) ⭐ **CONVERGED** · *(b)* assertion-only (cheaper, weaker) · *(c)* digest-only
ANSWER: (a) golden artifact + hash

**C3. Does the scenario suite join CI?** — *(a)* yes, as a test project (a new gate) · *(b)* nightly ·
*(c)* local-only for slice 0, CI once the shape holds ⭐
ANSWER: (c) local-only for slice 0, CI once the shape holds

**C4. Is the browser in scope?** — *(a)* HTTP-only (state) ⭐ · *(b)* also the Playwright surface (what the
player sees)
ANSWER: (a) HTTP-only

## D. The never-fabricate boundary

**D1. May a scenario run while a live injector is connected?** — *(a)* yes, read-only, never `/api/test/*` ·
*(b)* hard-refuse, exactly as `SimService.Guard()` does ⭐
ANSWER: (b) hard-refuse, like `SimService.Guard()`

**D2. Is a sanctioned item-acquisition route in scope here?** (SSH4.9-P2's ask) — *(a)* yes, this program builds
it · *(b)* no: the item program owns it and the simulator only proves it ⭐
ANSWER: (b) the item program owns it; the simulator proves it

**D3. If a condition genuinely cannot be reached by events, what then?** — *(a)* that licenses a new `/api/sim/*`
route · *(b)* the untestability **is** the finding; report it ⭐
ANSWER: (b) the untestability is the finding

**D4. Who reviews a scenario's honesty ("the subject was created by a real route")?** — *(a)* a checklist item
on the scenario file itself · *(b)* an automated guard ⭐
ANSWER: (b) automated guard

## E. Slice 1 — what proves it

**E1. Which feature family first?** — *(a)* lane `sim-idea-a`'s slice 0: player → souls → summon → roster read →
expedition dispatch/due/collect → progression + ledger + run reads (four families, every route already has E2E
coverage) ⭐ · *(b)* lane `sim-idea-b`'s lawn-event → progression chain (from `FoundationE2ETests.cs`) ·
*(c)* summon/fusion · *(d)* item equip · *(e)* a world turn
ANSWER: (a) the four-family slice 0 chain

**E2. Real process or in-process for slice 1?** — *(a)* both, one scenario file, two hosts ⭐ · *(b)* in-process
only · *(c)* real process only (the only shape that answers the long-loop question)
ANSWER: (a) both hosts, one scenario file

**E3. Does wave 1 model the injector's contract at all?** — *(a)* no: "no game, HTTP only" is the whole first
program ⭐ **CONVERGED** · *(b)* yes, include the shim
ANSWER: (a) no -- no game, HTTP only

## F. Housekeeping the lanes found (already routed, confirm the owner)

**F1. `/api/sim/effect/*` is registered unconditionally** (`Program.cs:2052`) while the rest of the sim surface
is behind `SimFlags.Enabled` (`:2050`) — *(a)* intentional, document it · *(b)* drift, gate it. Filed as
**`DM-F2`** in `tasks/debug-mcp-todo.md`.
ANSWER: (b) drift -- gate it -- owner OVERRIDE

**F2. `AGENTS.md` says CI runs 13 C# test projects; `ci.yml` names 60.** Filed as **`TVB-F22`** in
`tasks/test-verification-boundary-todo.md` (the program that owns CI wiring), with the fix being to state the
invariant rather than a number that rots.
ANSWER: update stale -- done in this commit (AGENTS.md now points at `ci.yml` as the list) -- owner OVERRIDE

**F3. `DataTestStore` lives in a test project and is consumed by a `<Compile Include>` link** — *(a)* give it a
shared, non-test home so a `tools/` consumer can use it ⭐ · *(b)* the compile link is acceptable
ANSWER: (a) give `DataTestStore` a shared, non-test home

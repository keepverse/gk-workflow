# Lane brief — `sim-t3-2` (RS4 with its guard path granted, then RS3's increments)

## Why this lane exists

`sim-t3-1` landed **RS2.5** (the real-process host — the same scenario file against both approved hosts, declared
digest identical, 109 moved pointers reported), closed **RS-F3**, and wrote the RS3 clock-seam spec. Two things then
stopped it, and this lane carries the grants that unblock them:

1. **RS4 was refused by a path fence, not by the work**: its deliverable is `scripts/guard-sim-fabrication.ps1`, and
   the orchestrator's pipeline guard refuses a new `scripts/guard-*.ps1`. `EnforcementRegistryGuardTests.R1` also
   forbids a registry row without the guard file, so *nothing* of the row could land.
2. **RS3's increments 3–5 are outside that lane's fence** (`gk-core/src/FusionRpg.Data/**` — 142 sites incl.
   `ForceExpeditionDue` at `RpgStore.Expeditions.cs:202-215` — plus Injector 19, Launcher 2, CheatCore 1).

⛔ **Read the design gate first** (`docs/DESIGN-GATE.md` §1), then these three in full:
`docs/architecture/rpg-simulator-spec-clock-seam.md` (the shape this lane implements), `tasks/rpg-simulator-todo.md`
(the rows), `tasks/rpg-simulator-decisions.md` (the owner rulings).

## Row 1 — RS4: the scenario-honesty guard

*"A scenario may not assert on state it created through anything but a real route."* Build
`scripts/guard-sim-fabrication.ps1`, wire it the way every other guard is wired (its tier in
`scripts/run-guards.ps1`, its row in `gk-core/scripts/enforcement-registry.v1.json`), and prove it **bites on a planted
violation** — a scenario written to cheat must fail the guard, the real scenarios must pass. A rule never seen to
fail is not known to work. The design and the measured surface are already preserved in the todo and ledger from the
previous lane: use them, do not re-derive them.

## Row 2 — RS3's increments, under the measured erratum

**The erratum is measured, not assumed:** `FusionRpg.Core` and `FusionRpg.Contracts` target **`net6.0`**
(`gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:3`), while `System.TimeProvider` ships in **.NET 8**. Owner ruling
**B1 (a)** — *full `TimeProvider` migration* — therefore cannot be executed in Core **as a mechanism**, though its
**intent is unaffected and binding**: every ambient clock read becomes one injectable read.

**Ruling for this lane (the conservative shape, per `AGENTS.md`'s default-to-action clause): implement shape B** —
one `net6.0`-safe seam over a configured `Func<DateTimeOffset>`, with `TimeProvider` as a `net8.0` input — unless the
owner rules shape A (multi-target Core `net6.0;net8.0` with `TimeProvider` behind `#if`) first. Record the erratum
against the ruling in the same commit as the first increment, so a later reader sees why the mechanism differs from
the decision's letter while its intent holds.

Then land the increments in the order the spec sets, one coherent group of sites per commit — **a 213-site migration
that lands as one commit cannot be reviewed or bisected**. The 9 sites the decisions row says must NOT be simulated
are named in that row: keep them named in your report, never silently skipped.

## Fence and grants this lane carries

- `gk-core/tools/RpgSim/**`, `gk-core/tests/FusionRpg.E2E.Tests/**`, `gk-core/tests/fixtures/rpg-scenarios/**`
- `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`, `gk-fusion/src/FusionRpg.Injector/**`,
  `gk-fusion/src/FusionRpg.Launcher/**`, `gk-core/src/FusionRpg.CheatCore/**` — the clock migration's own surface
- **`scripts/guard-*.ps1` (including NEW guard scripts), `gk-core/scripts/enforcement-registry.v1.json`,
  `scripts/run-guards.ps1`** — via `--allow-protected`; this is the grant that unblocks RS4 and RS-F10
- `docs/architecture/rpg-simulator*`, `docs/architecture/decisions.md`, `tasks/rpg-simulator-*`, `scripts/**`

If a row still needs a path outside that list, **stop and name it** (the previous lane already filed RS-F9/F11/F12
for exactly that) — do not reach across.

## Hard rules

1. **One ActorHub compose**; combat writes via `EntityStatWriter`/Funnel (`guard-actor-hub`, `guard-single-writer`, `guard-funnel-delta`).
2. **Never widen a guard, never add a `knownRed`, never re-add a baseline exemption.**
3. **Test substrate**: tests run **in memory** (`guard-test-substrate.py`).
4. **No magic numbers on the balance surface** — publish `v{n+1}` via `gk-core/tools/tuning/publish.py`.
5. **A row you close needs its evidence in the same commit**, the row id asserted present after the tick.

## Verification

- `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` — read the printed counts.
- The same scenario against **both** hosts (`gk-core/tools/RpgSim --host inproc` and `--host process`) — the digest comparison is the proof.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session sim-t3-2`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — read the printed counts, not the exit code.

## Report

End every segment with the `<<<REPORT {...} REPORT` block; every claim in it must already be a commit in this worktree.

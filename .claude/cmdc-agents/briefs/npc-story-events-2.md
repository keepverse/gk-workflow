# Lane brief — `npc-story-events-2` (continued, with the guard path granted)

## Why this lane exists

`npc-story-events-1` worked the largest open program in the repo and got **blocked three times on the same
protected path**: it could not create `gk-core/scripts/guard-narrative.py`, because the pipeline guard refuses writes to
`scripts/guard-*.ps1` and `gk-core/scripts/enforcement-registry.v1.json`. Its NR1.4 **code half is written, green and
committed** (`78bebd0f7`, `fef45f2ce`: the tuning file with plan D4's full union published, plus `narrative.v1.json`,
its loader and the hub). It also landed NR1.6 (plan D4 propagated into the eight specs) and NR2.1 (the stream-identity
fixture, recorded before the engine move).

**This lane carries the grant that unblocks it.** Everything else is unchanged — read
[`npc-story-events-1.md`](npc-story-events-1.md) for the program context, the hard rules and the verification
commands.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names **in this session**, then verify against code.
`tasks/npc-story-events-todo.md` is the authority — it is the **largest open program in the repo** (105 open task
blocks). Work it in dependency order.

## First row: NR1.4 — finish it

Its code half is committed; what remains is the guard and its wiring:

- `gk-core/scripts/guard-narrative.py` (new — the path three refusals blocked)
- its registry entry in `gk-core/scripts/enforcement-registry.v1.json` and its tier in `scripts/run-guards.ps1`
- the `guard.narrative` verification boundary (`gk-core/scripts/verification-boundaries.v1.json` + the
  `[Trait("VerificationId", …)]` test the boundary guard demands), per the plan's `level: focused` decision

A guard must have a case that proves it **bites on a planted violation** — a rule never seen to fail is not known to
work. Never widen a guard, never add a `knownRed`, never re-add a baseline exemption.

## Then: continue in dependency order

Take the next open blocks in the todo's own order (NR2.x onward), one row per commit, evidence in the same commit,
the row id asserted present after the tick. A row that ends the segment still open must end with a **named
dependency** or a **sharpened question** — never "needs investigation". Findings about other programs get a row in
*that* program's todo, with the id asserted present.

## Grants this lane carries (the reason it exists)

- `scripts/guard-*.ps1` — **including new guard scripts**, via `--allow-protected`
- `gk-core/scripts/enforcement-registry.v1.json`, `scripts/run-guards.ps1`, `gk-core/scripts/verification-boundaries.v1.json`
- `src/**`, `tools/**`, `tests/**`, `gk-data/packs/fusion/data/seed/**`, `docs/architecture/npc-story-events/**`,
  `docs/architecture/decisions.md`, `tasks/npc-story-events-*.md`, `tasks/npc-story-events-ledger.jsonl`,
  `data/tuning/narrative*.json`

## Hard rules

1. **Generated seed data is never hand-edited** — fix the generator and regenerate; a corpus count is a reading, not a constant.
2. **No magic numbers on the balance surface** — publish `v{n+1}` through `gk-core/tools/tuning/publish.py`, never edit in place.
3. **Test substrate**: tests run **in memory**; `gk-core/scripts/guard-test-substrate.py` enforces it (a `tests/**` file constructing a file-backed store carries `[Trait("Category","DiskSemantics")]`).
4. **One ActorHub compose** — contribute via `IActorStatSubsystem` / registered atom readers.

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session npc-story-events-2`
- `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet` (and `gk-core/tests/FusionRpg.Server.Tests` when a server path is touched).
- `python gk-core/scripts/guard-verification-boundaries.py` after a boundary edit.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — read the printed counts, not the exit code.

## Report

End every segment with the `<<<REPORT {...} REPORT` block (status/summary/closed/open/blocked/next); every claim in
it must already be a commit in this worktree.

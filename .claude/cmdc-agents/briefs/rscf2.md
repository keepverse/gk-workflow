# Lane `rscf2` — an intermittent 500 on the unique-actor XP route makes the E2E suite non-deterministic

**Session:** `rscf2` · **Program:** `unique-actor` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Core/**`,
`gk-core/tests/FusionRpg.E2E.Tests/**`, `tasks/rpg-simulator-todo.md`, `tasks/reports/**`

## The defect — measured, and it is a flake, not noise

Row **`RS-CF2`** in `tasks/rpg-simulator-todo.md` (line ~29) carries the reading:

- `POST /api/unique/actors/{instanceId}/xp` (`gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:113`) **intermittently
  answers 500**.
- The E2E test that catches it — `UniqueEquipmentE2ETests.Award_xp_levels_and_refuses_retired`,
  `gk-core/tests/FusionRpg.E2E.Tests/UniqueEquipmentE2ETests.cs:126` (`xp.EnsureSuccessStatusCode()`) — catches it only
  sometimes: with lane `sim-slice0`'s new test **excluded**, 4 runs gave `1 failed / 230 passed` once and
  `231/231` three times; with it **included**, 8 runs gave the same single failure twice and `232/232` six times.
- The symptom captured so far: `System.Net.Http.HttpRequestException : Response status code does not indicate
  success: 500 (Internal Server Error)`.

So it reproduces **without** the new test — pre-existing, not caused by it. The assembly's only collection is
`e2e` with `DisableParallelization = true`, so it is not a parallel-collection race.

## Why it matters more than a normal red

`test-fast.ps1 -AllDefault` green is one half of CC8's done-criteria. A test that fails ~25% of the time makes
that gate unusable: it will be "re-run until green", which is how a real regression gets waved through later.

## Deliverable

1. **Reproduce it deterministically enough to see it**: run the E2E project repeatedly and **capture the
   server-side exception** behind the 500 (the in-process host's logs, or the response body if the endpoint
   returns one). Do not stop at "it failed once" — you need the throw site.
2. **The cause, named by `file:line`**, with the mechanism that makes it *intermittent* (an ordering, a shared
   static, a clock, a retry, a cache, a race, a leaked row from a sibling test — say which, and why it only fires
   sometimes).
3. **The fix at the responsible layer.** ⛔ Not by retrying the request in the test, not by skipping or
   quarantining it, not by widening a validator, not by marking it known-red. If the cause is test isolation,
   fix the isolation; if it is production state, fix production — and say which it was.
4. **Proof of determinism**: the E2E project green on **at least 8 consecutive runs**, with the numbers printed
   for each (or a single command that loops and prints them).
5. **Route the row**: `RS-CF2` currently sits in `tasks/rpg-simulator-todo.md` as a carried finding. Update it
   (ticked with evidence, or left open with what remains) **and** put the owning row in the owning program's todo
   — the unique-actor runtime surface — with the id asserted present in the file.

## Verification

- `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet`
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session rscf2`

## Evidence contract

- the captured 500 (status line + the server-side throw site)
- exact command text and the numbers printed for every run you cite
- the committed artifact (SHA)
- an explicit **NOT-proved** list
- the routed row id, verified present

## Boundaries

- The machine may be busy: if a run reports **mass** failures within seconds, that is contention — re-run when
  quiet rather than recording it (measured once: 178 "failures" in 6 s versus 3 failed / 580 passed in 14 min).
- Do not edit generated data or `gk-core/data/tuning/**` in place. Do not touch another lane's files.
- Your session record's `worktree` path must be **ABSOLUTE**.

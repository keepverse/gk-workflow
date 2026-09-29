# Evidence — rpg-simulator row-close sweep on the head that accepted this lane (RS-F17, RS-F18, RS-F19; RS-F21 re-measured)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`), after merging `features/mega-merge` to `61d67f4cf` — the commit that **accepted this
lane's five commits**. The three rows closed here were filed by this lane as *another program's* reds; each was
re-measured before closing, and each is fixed by its owner.

| Row | Command | Result | Artifact |
|---|---|---|---|
| **RS-F17** (`population-pin` red from ADG-F5's test) | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-population-pin.ps1` | exit **0**, `P1 (0 finding(s))` — the `Assert.Equal(500, grantedIds.Count)` the row named is gone | fixed by `c0637f93a fix(population-pin): the ADG-F5 sweep asserts its own bound, not a second copy of 500` |
| **RS-F18** (`doc-citations` HIGH in a LOAM document) | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | exit **0** with **no HIGH at all** (`D1 714 (0 HIGH)`, `D3 58 (2 HIGH)` → 0) | fixed by `7464bf590 docs(citations): qualify two bare fill.py basenames …` |
| **RS-F19** (`narrative` flakes in-sweep, green standalone) | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | `narrative ci gating 0 17.20` inside a tier that reads **25 guards, 0 red** | the sweep is the row's own acceptance |
| The whole tier, as one reading | same command | **`GUARDS OK - 25 guard(s) run, 0 red`** — `clock-seam`, `sim-fabrication`, `doc-citations`, `population-pin`, `narrative` and `test-content-root` all green | — |
| **RS-F21** re-measured (still open, still fenced) | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~ContractFixtureTests\|FullyQualifiedName~WorldTurnFixtureTests"` | `Failed: 3, Passed: 0, Total: 3` — a **third** fixture drifted since this lane's first measurement (`unique-actor.json`, which matched exactly then) | the row now carries all three re-bless diffs and the commands that produced them |

**Why RS-F21 is still open, in one line:** all three fixtures live under `web/**`, which is not in this lane's
allowed paths, so the blessed edits were reverted again (tree clean) and the C# reds stay red on purpose. The
row now carries the complete evidence for whoever holds that fence: one rename line, one added line
(`"empireId": "dave"`), six `stateHash` lines, plus the Playwright literal that must move with the first.

**What this sweep is not:** it is not proof that a contention flake is gone. RS-F19's acceptance is the sweep,
and the sweep passed; a second green sweep would strengthen it, and the honest limit is recorded in the row.

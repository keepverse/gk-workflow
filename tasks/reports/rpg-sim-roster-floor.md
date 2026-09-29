# Evidence — the corpus's roster floor (a count that was knowable, and the pointer mechanism it rides on)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). The corpus's `expect.roster.held` asserted only `notEmpty` on `$.items`, so a summon
route that delivered **one** of the ten specimens it was asked for would have passed. The count IS knowable, so
the assertion is now a floor — and the pointer mechanism it rides on is pinned by tests instead of assumed.

| Criterion | Command / read | Result |
|---|---|---|
| The count is deterministic, read from the code | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Summons.cs:34`; `gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs:67-77`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Summons.cs:102-117` | `count` may only be **1 or 10**; the roller loops exactly `count` times adding one result each; the mint loop mints one specimen per result — so `count: 10` yields ten specimens for a fresh player |
| The assertion is a floor now, with the mechanism named in its own `why` | read: `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`, `expect.roster.held` | `path: $.items[9].actor.instanceId`, `check: notEmpty` — an index at 9 is an existence proof for ten elements, because a pointer that selects nothing returns null and `notEmpty` refuses null |
| The mechanism is pinned by tests, not assumed | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSimFormatContractTests"` | `Passed: 21, Failed: 0, Total: 21` (was 20) — the pointer grammar test now covers an **out-of-range index** (`$.items[9]` → null, and `$.items[9].actor.instanceId` → null) and a **clamping slice** (`$.items[1:9]` → one element), and a new test proves `notEmpty` over a null selection **fails** while the same check on an element that exists passes |
| The corpus still runs green with the floor | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --no-build --nologo --filter "…RpgSimFormatContractTests|…RpgSimGoldenTests|…RpgScenarioSlice0E2ETests"` | `Passed: 24, Failed: 0, Total: 24` (28 s) — the corpus executes with the new assertion, and the golden still matches (no reading set, digest or exclusion change) |
| The whole set | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` | `Passed: 50, Failed: 0, Total: 50` (13 m 50 s — a heavily loaded machine) |
| Guards | `guard-sim-fabrication.ps1`; `guard-test-substrate.py`; `guard-doc-citations.ps1 -Strict`; `run-guards.ps1 -Tier ci` | `SIM FABRICATION GUARD OK` (`… \| golden verdicts skipped=1`); `TEST SUBSTRATE GUARD OK`; doc-citations exit **0**, `D1 683 (0 HIGH)`; the tier `GUARDS OK - 25 guard(s) run, 0 red` |

**Why `[9]` and not a length check.** The assertion vocabulary is closed and has no `length`/`count` check on an
array of objects (`atLeast` is a numeric comparison; the roster payload is `{ playerId, items }` with no total
field — `gk-core/src/FusionRpg.Contracts/CreatureDtos.cs:31-35`). So the available honest form of "at least ten" is an
index at 9 plus a non-emptiness test — and it is only honest if the pointer really returns null past the end,
which the two new test cases pin (`JsonPointer.cs:76-79` adds nothing when `k >= items.Count`; `:107` returns
null).

**What this is an instance of.** `validation-ssot.md`: assert the contract, not a population — but here the
*count is an input* (the scenario asked for ten), not a population reading, so a floor is legitimate where a
pinned number would not be. The distinction is the reason the `why` names the code that makes ten certain.

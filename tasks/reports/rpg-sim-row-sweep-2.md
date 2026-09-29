# Evidence — row sweep on the head that accepted the last increment (RS-F23 closed; RS-F27 filed)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`), after merging to `d9535311e`. Each row was re-measured before being touched; the point
of the sweep is that a row's summary is not evidence of what is wired (the RS-F9 lesson).

| Row | Command / read | Result |
|---|---|---|
| **RS-F23** (a pytest project with no CI step at its own root) | `grep -n -B4 -A6 "working-directory: \." .github/workflows/ci.yml` | **the fix landed**: `d19154eb8 fix(tvb): the register re-verified at the merged head -- two rows close, the tools-audit-tests CI step lands` added a step at `working-directory: .` running `python -m pytest gk-core/tests/tools -q -p no:cacheprovider` with its own exit check (`ci.yml:464-470`) — exactly what this lane's pre-read recommended |
| …and the guard agrees | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~CiPytestWiringTests\|FullyQualifiedName~PlayerSpeciesMaterialiseCallerGuardTests"` | `Failed: 1, Passed: 6, Total: 7` — **`CiPytestWiringTests` is green**; the one red is **RS-F24**'s pick-refusal pin. So RS-F23's acceptance is met and the Guard suite's remaining red is RS-F24 alone |
| **RS-F24** (a tenth pick-refusal code, pin not moved) | `grep -c "source-below-rank-floor" gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs` | **still 0** — the pin has not moved, and the test is the one red above. Its two-line fix and the justification (the widening is a distinct rank floor) are already in the row |
| **RS-F11** (`/health` clock field) | `grep -c "Clock" gk-core/src/FusionRpg.Contracts/Dtos.cs` | **still 0** — the fenced half has not landed |
| **RS-F21** (three drifted `web/**` fixtures) | `git log --oneline -1 -- gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json` | unchanged (`f2f67caa9`), so the row's three measured re-bless diffs are still current |
| **RS-F27** (new) | read: `gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs:47-65` | `match.ended` returns an award **only for a defeat** (`:58-59`) and `Array.Empty<Award>()` otherwise, so a victory or a stalemate credits nothing from that fact — the corpus's four ledger assertions are all vacuously true on an empty row set, and whether that set can be empty is now a filed question with the mechanism argument and the measurement that would settle it |

| Criterion | Command | Result |
|---|---|---|
| No citation broken by the edits | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | exit **0**; `D1 683 (0 HIGH)`, `D2 7 (0 HIGH)` |
| Nothing else regressed | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | exit **0** — `GUARDS OK - 25 guard(s) run, 0 red` |

**Why RS-F27 is filed rather than fixed.** The tempting fix is a `notEmpty` on the ledger, and it is the wrong
one to apply blind: this lane already removed exactly that shape from the soul ledger after measuring it flaking
**1 run in 2** (`expect.souls.ledger.expedition`), because the row's presence rode a server-minted roll. The
progression ledger's rows ride the battle outcome instead, and `RpgXpAwardMap` shows a victory crediting nothing
from `match.ended` — so the honest sequence is measure the emptiness, then guard or document. Filing it keeps the
question alive without guessing at an answer that a future run would falsify.

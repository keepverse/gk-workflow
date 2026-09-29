# TVB-F16 — the two CI-tier guard reds on this program's files are clear

Routed in from `test-verification-boundary` on 2026-09-21. Both findings it named were this program's own
files and were cleared by `CAI-guard-2` (`5fd0feba`, lane `combat-ai-2`); this is the closure, re-measured
on the take-over lane rather than assumed from that row's own text.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| M1 — `CoreIntentPolicy.cs:76-77`'s two bare `64`s | `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` | exit 0, `M1=0  M2=0  M3=0  M4=0`, `total 0 finding(s), 0 high`, `MAGIC-NUMBER GUARD OK`. The literals are now the named `const int DecisionScratchCapacity = 64;` (`Actions/Ai/CoreIntentPolicy.cs:84`) read by both scratch lists at `:86-87` — the guard's own structural-const justification, the same shape as `CostLedger.StackCostRows` | `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs:84` |
| P1 — `DecisionAllocationTests.cs:400`'s bare `32` | `pwsh -NoProfile -File scripts/guard-population-pin.ps1` | exit 0, `total 0 finding(s)`, `clean`. The assertion now reads `Assert.Equal(cap, result.Count)` (`:405`) where `cap` is `new ScoringWeights(…).MaxCandidatesScored` (`:401`), and the comment states the criterion the guardrail standard requires — it pins the work bound's contract, not a population reading | `gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs:401,405` |
| The CI tier's own report | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | exit 1 with `guards failed: doc-citations` **only**. The 21-guard table shows `magic-numbers ci gating 0` and `population-pin ci gating 0`; 20 of 21 guards exit 0 and the one red is the notify-rail file move in **other programs'** docs (`docs/architecture/combat-ai/**` reports 0 findings) | this file's row above (`tasks/combat-ai-todo.md` §`TVB-F16`) |
| Nothing was widened to get here | `git show --stat 5fd0feba` | the fix is two source/test files of this program's own; **no** guard, allowlist, `knownRed` entry or registry was touched | `5fd0feba` |
| The behaviour the two fixes must not move | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Ai"` | **4615 passed, 0 failed** | — |

## Not proved

- **`doc-citations` is still red and is not this program's.** 19 D1 + 2 D2 + 2 D3 + 1 D4, every D1 in
  notification-ssot / npc-story-events / trade-network / world-stage docs. The previous lane's ledger note
  (`mk1-ab32a4869fce768d`) records them as already filed in their owning todos (`NS5.11`, `DOC-NS5.2`,
  `DOC-NS5.7`, one npc-story-events row); **this lane did not re-verify that those rows still exist**, so
  treat the attribution as inherited. This row's own acceptance names `magic-numbers` and `population-pin`
  only, so it closes against its wording — the tier's overall exit 1 is reported rather than smoothed over.
- **`CAI-guard-1`'s red is a different guard** (`gk-core/tests/FusionRpg.Guard.Tests`, a protected path) and is not
  covered here. `run-guards.ps1 -Tier ci` does not run the Guard test project, which is why the tier table
  is clean for it and a `dotnet test gk-core/tests/FusionRpg.Guard.Tests` run would not be.
- **No Guard.Tests run is quoted.** `CAI-guard-1`'s re-pin rides lane `tvb58`; running that suite here would
  produce a red this lane cannot fix and is not asked to.

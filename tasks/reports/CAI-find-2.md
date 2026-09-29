# `CAI-find-2` — a negative AI weight is refused at parse

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Found by lane `cai2` while re-anchoring the citations
`CAI3.1`'s deletion moved; fixed here because module 2's loader is in every combat-ai lane's fence.

## The defect, re-read from the code (not the finding)

`CombatAiTuningLoader.ParseScoring` read all seven weights through `Int(el, …)` with no sign check, while
its neighbours in the same method refused a non-positive structural bound (`maxCandidatesScored <= 0`,
`aggressionRange <= 0`). The refusal the spec cited was a property of the OLD `SiegeTuning` reader, and
CAI1.8 moved the ten keys without carrying it.

Two distinct consequences, which is why the fix covers all seven rather than the one the spec row names:

- **Four terms have no downstream clamp** — hit-chance, objective, cannot-counter, round. A negative value
  there *inverts* its own score term instead of being rejected.
- **Three are clamped** by `AiPersonalityApply.ClampNonNegative` (risk, low-HP, kill). The clamp is the
  policy's and bounds the RESULT; it would have *hidden* a malformed authored weight rather than reported
  it. Both halves are true at once, which is why "the policy clamps it" is not a reason to skip the parse.

Zero is deliberately still legal: it disables a term, which is a real authoring choice, and the spec's own
clamp is a statement about the result, not the input.

## What landed

`CombatAiTuningLoader.NonNegativeWeight(profileId, el, key)` — reads one weight, throws
`CombatAiTuningRejection` naming `profiles.<id>.scoring.<key>` when it is negative. `ParseScoring` calls it
for all seven, so the failure is the same whole-row rejection the two structural checks already use.

The spec row (`spec-ai-tiers-personality.md:200`) is corrected in the same commit, because the fix moved
the `file:line` it cited and re-asserted a claim (`the loader already refuses a negative weight`) that was
false when `cai2` measured it and is true again now.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| All seven negative weights are refused, each naming its key | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombatAiTuningTests\|FullyQualifiedName~SiegeKeyMigrationTests" --nologo --verbosity quiet` | **33 passed / 0 failed** (8 new cases: 7 per-weight theory rows + 1 zero-boundary fact) | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CombatAiTuningTests.cs` |
| The refusal is load-bearing (planted violation) | same command with `if (value < 0)` → `if (value < int.MinValue)` | **7 failed**, exactly the seven per-weight cases; reverted green | — |
| Zero stays legal (the boundary the refusal must not cross) | same command, `A_zero_weight_is_admitted` | **passed** | — |
| No shipped file authors a negative weight, so no publish is owed | `grep -n "weight" gk-core/data/tuning/combat-ai.v1.json gk-core/data/tuning/combat-ai.v2.json` | all seven positive in both files (70/50/15/10/10/1/120) | — |
| The spec row it corrects | `grep -n "CombatAiTuningLoader.cs:" docs/architecture/combat-ai/spec-ai-tiers-personality.md` | `:198-206` — the new `NonNegativeWeight` address | `spec-ai-tiers-personality.md:200` |

## NOT proved

- **The behaviour change's blast radius on real content is unmeasured beyond the two shipped tuning
  files.** Every profile in `gk-core/data/tuning/combat-ai.v1.json` and `v2.json` is positive, so no shipped
  parse changes; a hand-authored negative weight outside `gk-core/data/tuning/` was not searched for, because a
  profile only reaches this parser through those files (`CombatAiProfilePolicy.Configure`).
- **No golden run.** The change is a parse-time refusal on malformed input; `BattleGolden` was not run for
  it, because no shipped document can reach the new throw. `verify-change` selects the boundary.

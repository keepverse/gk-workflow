# CAI2.6 — the reserve floor's rule: the shipped seam and the ideal disagree (FOUND by CAI2.3's parity test)

Lane `combat-ai-2`. The row is blocked on a ruling; this fragment is the evidence it was opened from, plus
the two cases added to the SEAM's own suite so the ruled rule has a concrete assertion to change.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The divergence is measured, not argued | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionScheduleMatchesCorePolicyTests"` | **2 passed, 0 failed** — `The_reserve_floor_rule_differs_between_the_twin_and_the_shipped_seam` asserts both sequences: twin `[act.skill, act.pass, act.pass, act.pass]`, seam `[act.skill, act.skill, null, null]` at max 1000 / floor 900 / costs 80,40 from a full pool | `tests/.../Balance/ActionScheduleMatchesCorePolicyTests.cs` |
| The seam's own suite now pins its ACTUAL rule, not just the floor's existence | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionStageTests"` | **16 passed, 0 failed** — two new cases: `The_floor_refuses_at_exactly_the_balance_and_would_admit_one_point_above_it` (balance == floor refuses; balance == floor+1 admits, pinning the `<=`) and `A_zero_cost_action_is_refused_at_or_below_the_floor_too_so_the_actor_idles` | `tests/.../Actions/Ai/ActionStageTests.cs` |
| Golden: nothing moved (no behaviour changed — this is test-only) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | **5 passed, 0 failed** | — |
| Boundary, every selected project's numbers | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/ActionStageTests.cs') -Session combat-ai-20260920"` | **15104 passed / 0 failed** across the five projects it selected: Core.Tests 13209, Atoms.Tests 1351, ActorHub.Tests 498, ActorSurface.Tests 31, AchievementTitlesTuningTests 15 | — |
| Guards | `guard-actor-hub.ps1`; `guard-battle-responsibility.py` | both exit 0 | — |

## Why two cases in the seam's suite matter

The seam's existing case (`Reserve_floor_refuses_through_gate_3_and_never_starves_a_basic_attack`) proves the
floor EXISTS and that `ActionKind.Basic` is exempt. It does not pin the boundary or the cost-blindness — and
those are exactly the two facts the divergence rests on:

1. **`ReserveFloorAffordability.cs:106` compares `current <= floor`**, before any cost is considered. A
   post-payment rule (`current - cost >= floor`, the ideal's own words and what the twin implements) would
   admit any action cheaper than the slack at that same balance.
2. **The comparison is cost-blind**, so at or below the floor a zero-cost non-Basic action is refused too:
   the policy returns `ActionIntent.None` and the actor idles instead of taking a free option. The twin never
   floors its free fallback — deliberately, since a floor that could starve the walk is a hang.

Both are now green against the shipped code, which means the ruling has a target: whichever semantics is
chosen, `The_floor_refuses_at_exactly_the_balance_...` is the test that flips, and the row's acceptance says a
golden move from this cause is its own one-cause commit — never folded into CAI3.6's re-bless.

**A note for the next reader on the merge layout.** This turn's merge split several suites out of
`FusionRpg.Core.Tests` (Atoms, ActorHub, ActorSurface, AchievementTitlesTuning, and a shared TestSupport
project), so `FusionRpg.Core.Tests` alone now reports ~13209 where earlier fragments quote ~15100. The
boundary total is unchanged: 15104 passed / 0 failed across the projects the path boundary selects.

## Cross-reference slice — the rule is now stated in both code sites AND the spec

The row's own acceptance asks for the rule to be "stated ONCE — in the code comment and the spec together,
because the whole defect is that two files state the same word differently". The ruling has not happened, so
what is landed here is the missing cross-reference on all three sides, stated factually rather than
pre-emptively: each site now says what IT does, names the other reading, and points at CAI2.6.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The seam says what it does and names the twin's different reading | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionStageTests"` | **16 passed, 0 failed** (comment-only change; the behaviour tests still pass) | `Actions/Ai/ReserveFloorAffordability.cs` class doc |
| The twin says what it does and names the seam's different reading | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionSchedule\|~ActionStageTests"` | **33 passed, 0 failed** | `Balance/Analytic/ActionSchedule.cs` (`Choose`'s floor comment) |
| The spec records the divergence as an open question with both consequences | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | **0 HIGH** on D1/D2/D3/D4 (23 documents, 1165 citations) | `spec-action-schedule-twin.md` → "Open questions" 0 |
| Golden: byte-identical (comments only, plus the spec) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | **5 passed, 0 failed** | — |
| Guards | `guard-magic-numbers.ps1`; `guard-doc-citations.ps1 -Strict` | magic-numbers **0 findings, GUARD OK**; doc-citations unchanged at 20 HIGH with **0 in this program's docs** | — |
| Boundary, every selected project's numbers | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/ReserveFloorAffordability.cs','gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs','docs/architecture/combat-ai/spec-action-schedule-twin.md') -Session combat-ai-20260920"` | **15108 passed / 0 failed** across SIX projects: Core.Tests 13209, Atoms.Tests 1351, ActorHub.Tests 498, ActorSurface.Tests 31, AchievementTitlesTuningTests 15, **Guard.Tests 4** — the Guard suite is green now, so the tvb58 reds (CAI-guard-1's pin and the pipe-drain family) have been fixed by their owner | — |

**Why this is not the fix, and does not pretend to be.** Each site states its own rule truthfully and names the
other's, so a reader of any one file now knows a second reading exists and where the ruling lives. Nothing was
changed in either implementation, so no golden can move and the ruling still decides which side changes.

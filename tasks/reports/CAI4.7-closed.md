# CAI4.7 — CLOSED: both owed acceptance lines landed

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row's Core half (the three pure classes, 33 tests)
landed in lane `cai4`; its two owed acceptance lines were the section and the tuning file, and both landed
in this lane. Re-verified this segment with printed readings rather than ticked on the strength of the
rows that recorded them.

| Acceptance line | Command | Result |
|---|---|---|
| Line 6: `PerfSection.LawnAiDecide = 26`, `SectionCount = 27`, `"lawn.ai.decide"` | `grep -n "LawnAiDecide\|SectionCount =" gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs`; `dotnet test gk-core/tests/FusionRpg.Core.Diagnostics.Tests --filter "FullyQualifiedName~PerfProbeTests"` | `AiDecide = 25`, `LawnAiDecide = 26`, `const int SectionCount = 27`; **8 passed / 0 failed**, including the three-way pin whose planted `SectionCount = 25` kills it |
| Line 7: the lawn section holds exactly the four BALANCE keys | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombatAiTuningRevisionTests"` | **5 passed / 0 failed** — 7 / 50 / 10 / `"lawn.ai.offset"` read back through the SHIPPED parser from `CombatAiTuningFiles.Current`, the four structural values asserted ABSENT, and an absent lawn section refused |
| The pure classes' own contracts (the trigger's N/edge/lock/carry, the budget's FIFO, the pool's leases) | `dotnet test gk-core/tests/FusionRpg.Core.Match.Tests --filter "FullyQualifiedName~LawnDecisionTriggerTests\|FullyQualifiedName~LawnDecisionBudgetTests\|FullyQualifiedName~LawnCastTokenPoolTests"` | **33 passed / 0 failed** — in their NEW home, because `CAI-tests-1` (this lane) moved them from `tests/FusionRpg.Core.Balance.Tests/CombatAi/` |

## Two recorded differences from what the row predicted

1. **The revision is `v2`, not `v3`.** The row and its spec both said `combat-ai.v3.json`, assuming CAI3.5's
   four `delve/*` rows would be v2. Those aborted — `AiRole` declares no `Enemy`, so `delve/enemy` cannot
   parse — so the next publish was v2 and the lawn section is in it. The substance the row asked for (a
   `v{n+1}` carrying the lawn section, published through `publish.py`, with its readers moved in the same
   commit) is what landed, and `CAI-F1` closed the H7 problem for good by making the revision a constant.
2. **The test path in the row is stale by one move**, and by this lane's own `CAI-tests-1`: the 33 tests now
   live in `gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/`, which has its own focused `core-match` boundary.

## What is NOT this row's

Its injector half is `CAI4.8`'s and is four-sixths landed: the switch, the frame slot, the registry drops,
and the `lawn.ai.decide` section with its declared share. What remains there is the decision half, blocked
on the injector's missing action-catalog feed (`CAI4.3`), not on anything this row names.

# CAI-loop-2 — the loop through the REAL lawn view

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

`CAI-loop-1` proved the four wave-4 halves compose, but it fed the policy a hand-rolled `IBattleView`.
The production lawn view is **`LawnBattleView` (CAI4.1)**, and it is the one thing between the board and
every decision. Two claims only the real view can carry are checked here, through the **real profiled
policy** rather than in the view's own suite:

1. **Side comes only from the oracle.** The board is built so the two readings are *disjoint*: a raw
   `zombie` col-1 unit the oracle calls an ALLY, and a raw `plant` col-3 unit the oracle calls an ENEMY
   (with a second raw zombie keeping its raw reading, so this is a contradiction on two units, not a
   blanket flip). The policy must target the oracle-enemy and never the oracle-ally.
2. **One derived resolve per actor per frame**, however many times the policy asks — measured as
   (reads the policy demanded) vs (resolves the cache performed), so a disabled memo cannot pass.

Tests: `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnDecisionLoopViewTests.cs` — 4.

| Criterion | Command | Result |
|---|---|---|
| The displayed loop, through the real view | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnDecisionLoopView"` | **4 passed / 0 failed** |
| Row Verify line | `verify-change.ps1 -Paths @('tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnDecisionLoopViewTests.cs') -Session combat-ai-4` → part of a 3-path run | exit 0; **41 distinct test projects, 0 with any failure** (summed 15728 passed / 0 failed) |
| Guards | `guard-actor-hub.ps1`; `audit-overflow.py --targets A3` | OK; exit 0, no finding |

## Mutations, each killing its named test

| Planted | Killed |
|---|---|
| `LawnBattleView.SideOf` replaced with the raw census side — **CAI4.1's own named mutation**, now proven against the real policy rather than only in the view's suite | 1 red |
| `LawnDerivedCache.Get`'s memo disabled | 1 red — **only after the measurement was fixed**: my first version counted *distinct* resolved actors, so a disabled memo still passed. It now counts resolve CALLS and asserts the demand exceeds the supply |

Both planted in files **outside this lane's fence** (`gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/**`), run, then
reverted — `git diff --stat` on that directory is empty afterwards, so the files are byte-identical.

Two corrections found by the tests failing honestly, both worth recording because they were *my* errors,
not the product's: `SideOf` returns the **relative** side (an oracle-ally reads 0 = my side, not the raw
code), and the argmax does **not** pick by distance between equal-scoring enemies, so the second claim's
assertion is "the target is an oracle-enemy" rather than "the nearest one wins".

## What this is NOT

Still not the production host: `LawnActorViewHost` (CAI4.1's adapter) and `LawnDecisionHost` (CAI4.8) are
what will build these seams in a live frame. This proves the real view and the real policy agree; it does
not prove a lawn creature decides in a match.

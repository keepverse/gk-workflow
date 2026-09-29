# CAI4.1 — CLOSED: all nine acceptance lines, with the production caller named

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row was reopened and advanced across several
segments (Core slice, then the injector host). Its own recorded reason for staying open was *"without it no
production host reaches the view"* — and CAI4.8's tick wiring answered exactly that, so the row closes.

| Acceptance line | Command | Result |
|---|---|---|
| (1) the three files under `Actions/Ai/Lawn/`; `ILawnBoardViewTests` green and **unmodified** | `dotnet test gk-core/tests/FusionRpg.Core.Match.Tests --filter "FullyQualifiedName~ILawnBoardViewTests"` | **6 passed / 0 failed** |
| (2) side only from the oracle; (3) `_resolve` once per (actor, frame); (5) `GarrisonedStructureKeyOf`/`ObjectivePositionOf` null, `PositionOf` non-null, `HpMilli` 0/1000; (6) the twelve-member set; (7) no fog; (8) the constant revision seam; (9) `StubIntentSource` unmodified driving a real `ActionIntent` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnBattleViewTests\|FullyQualifiedName~LawnDerivedCacheTests\|FullyQualifiedName~LawnRelationChainTests"` | **18 passed / 0 failed** |
| (9)'s "unmodified" clause | `git log -1 -- gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs` | **f46efadaf, 2026-08-28** — this program never touched it |
| (4) with no decision edge the census delegate is never invoked; a repeat `ViewFor` allocates nothing | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnActorViewHostTests"` | **10 passed / 0 failed** |
| The production caller | `grep -rn "LawnActorViewHost.ViewFor" src/` before, then the wiring | before: nothing outside the file; after: `InjectorLoop` → `LawnDecisionHost.Tick` → `ViewFor` |

## The one stated deviation, which is NOT an acceptance line

`statusMaskOf` reads **0**. The spec's table names `EffectRuntime.Status` as the source, and measured there
is no per-ptr status-mask producer in the injector: `SimEffectHost.StatusMaskOf` is an instance property of
Core's sim host that nobody sets, `StatusRuntime` exposes status *instances* rather than a mask, and a grep
for `statusBit`/`StatusBit` in `gk-fusion/src/FusionRpg.Injector/` returns nothing — the mask needs the compiler's
status-id interning, which the injector never supplies. Inventing one would fork that mapping, so the
absence is stated in the class doc and `FactsOf.StatusMask` under-reports until a producer lands. None of
the nine acceptance lines names the mask, which is why this is a recorded deviation rather than an open
line.

## What the close does NOT claim

The view is reached and every member is answered; what is still not production-fed is the DECISION that
would read it — the `LawnDecisionHost.Decide` seam, blocked on the injector's missing action-catalog feed
(`CAI4.3`). That is CAI4.8's line and is named there, not here.

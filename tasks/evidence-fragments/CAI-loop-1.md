# CAI-loop-1 — the four wave-4 Core halves run together

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

`tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnDecisionLoopTests.cs` — 4 tests that compose
`lawn-held-actions` (CAI4.2), `lawn-cast-activation` (CAI4.6), `lawn-cast-trigger` (CAI4.7) and
`commander-direct-orders` (CAI4.9) **where they actually meet**. Each half had its own green suite;
none had ever run against another. These are the seams a bundle of separately-green halves can still get
wrong.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| The composed loop | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnDecisionLoop"` | **4 passed / 0 failed** |
| Row Verify line | `verify-change.ps1 -Paths @('tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnDecisionLoopTests.cs') -Session combat-ai-4` | exit 0, **287 passed / 0 failed** (`core-balance`) |
| Guards | `guard-actor-hub.ps1`; `audit-overflow.py --targets A3` | OK; exit 0, no finding |

### Edge 1 — the decision (`CoreIntentPolicy` × module 16)

The **real profiled policy** (`CoreIntentPolicy.Create(…, AiPlace.Lawn, AiRole.Default)`, resolving
`lawn/default` → `*/default` through the hub the test bootstrap's module initializer configured) over a
view whose `HeldActionsOf` is module 16's store: the chosen action is **one the store holds** and the
target is the nearest enemy.

And for a species the store never pushed, the same policy declares `None` — with **another species
holding a kit**, so "empty" cannot be satisfied by the store simply being empty. That distinction is what
the planted violation below proves the test is sensitive to.

### Edge 2 — the cast (edge → budget → token → real ledger at the real rung)

`LawnDecisionTrigger` reaches its edge on the N-th first-of-swing record → `LawnDecisionBudget` serves the
actor inside its per-frame cap → `LawnCastTokenPool` leases → `LawnCastPlan` pays and builds the event.
The ledger's rows are built from each action's **own `CompiledAction.Costs`** (the same one-line
projection battle uses, `BattleRunState.cs:662`) and `rungOf` is the **real `EffectiveRungResolver`** with
the lawn's floor of 1 — so the number paid is authored data, not a test literal. Asserted: charged exactly
once; the cooldown arms at the envelope's own tick count; the event carries
`OnActivate` / `HitCount 1` / the post-decision target; a pool one unit short refuses with
`ShortfallResourceId` and charges nothing; and **a rung-5 action costs strictly more than a rung-1 one**,
which is what proves the resolution reaches the payment rather than stopping at the ledger's door.

### Edge 3 — the order (admission rules × queue × the real router)

Every §2 fact resolved the way the host will resolve it (same scope; a bound subject whose ptr is the one
the order names and which is live; an action the store holds), then the queue, then the **real
`IntentRouter`**'s own step 1: live at `IssuedTick + lifetime - 1`, expired at `+ lifetime`. A retryable
gate refusal leaves the order live and a terminal one removes it; one failing admission fact keeps an
order out of the queue entirely.

## Mutations, each killing its named test

| Planted | Killed |
|---|---|
| `LawnCastPlan`'s cooldown start removed | 1 red — the cast-edge test (the cooldown assertion) |
| `LawnOrderQueue.Expire` made a no-op | 1 red — the order-edge test (the lifetime assertion) |
| `LawnHeldActionSets.HeldFor` made to hand out another species' kit | 1 red — **only after the no-kit test was strengthened** to give a *different* species a kit; against an empty store the mutation was inert, which is exactly the weakness that fix removed |
| The test's own `RungOf` forced flat to rung 1 | 1 red — the rung-sensitivity assertion |

All four reverted; 4/4 green after each revert.

## What this is NOT

It is **not** the production host. `LawnDecisionHost` (CAI4.8) is what will run this loop, and its feature
switch, tick entry, registry drops and `PerfSection` remain owed. A green test here says the halves fit.
It is **not** evidence that a lawn creature casts in a live match, and none of the four rows' "no
production host" status changes because of it.

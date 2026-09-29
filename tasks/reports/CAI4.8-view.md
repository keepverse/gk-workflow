# CAI4.8 — the view wired into the tick (and CAI4.1's caller line answered)

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row's own ordering is *due set → view → policy →
cast*, and the view was the one step the host could own without the catalog-blocked inputs: for each due
actor it builds the view for that actor's OWN side and hands it to the decision seam.

| Criterion | Command | Result |
|---|---|---|
| The view has a production caller | `grep -rn "LawnActorViewHost.ViewFor" src/` before, then the wiring | before: **nothing outside the file itself**; after: `InjectorLoop` → `LawnDecisionHost.Tick` → `ViewFor` |
| The view handed over is scoped to the actor's own side | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnDecisionHostTests"` | **7 passed / 0 failed** — the seam receives a non-null view and `view.SideOf(actorKey)` is `MySideCode` |
| The injector still compiles, and the guards | `guard-injector-compile`; the seven guards | `INJECTOR COMPILE GUARD OK`; all seven **exit 0** |

## Why the perspective is the actor's own side

`LawnBattleView` is perspective-scoped and `SideOf` is relative, so "the decider that owns this actor" is
the view built for that actor's own board side. The HOST reads the raw side to route (`PerspectiveOf`),
which is not what the view is forbidden to do: the view must not read the raw side to answer a RELATION
(that is the ownership oracle's job), while the host's question is a routing one. An actor the census does
not hold falls to the player's perspective rather than being dropped.

## What still blocks the row, unchanged

The decision step is still a seam because its inputs are module 16's held sets (the `ActionCatalog` feed,
`CAI4.3`'s unowned blocker) and the ledger's held-action rows.

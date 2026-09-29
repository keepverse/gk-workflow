# CAI4.9 owed item (3) — the Server order endpoint

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row's acceptance carries this line verbatim:

> `LawnOrderEndpointTests`: the route sends **exactly one** `CommandDto` through `InjectorCommandSender`
> and returns **without awaiting anything else**.

`gk-core/src/FusionRpg.Server/LawnOrderEndpoints.cs` is that route (`POST /api/lawn/order`), registered in
`Program.cs` beside the other host routes. It rides the ONE server&#8594;injector seam every other host
command uses, so the order reaches the lawn's `LawnOrderQueue` in process and the launcher host relays one
pipe verb — no second transport.

| Criterion | Command | Result |
|---|---|---|
| Exactly ONE command per click | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~LawnOrderEndpointTests"` | **6 passed / 0 failed** — `The_route_sends_exactly_one_command_and_returns` asserts `Assert.Single(_inbox.Drain())` and every carried field. A second command would SUPERSEDE the first in the injector's queue, so one is a correctness property, not a style |
| An incomplete body is refused with nothing relayed | same run | **6 / 0** — the `[Theory]` covers a null/blank `matchKey`, `actorKey` and `actionId`: 400 and `Assert.Empty(_inbox.Drain())` |
| Two clicks are two orders (the route is not idempotent) | same run | **6 / 0** — the injector's queue is where "a second order replaces the first" lives |
| The boundary's own check and guards | `dotnet test gk-core/tests/FusionRpg.Server.Tests`; `guard-debug-scope.py`; `guard-dal.ps1` | **823 passed / 2 failed** — both failures are `RealRunCollectorTests` on a bare `powershell` spawn (`CAI-find-3`), unrelated to this change; `DEBUG SCOPE GUARD OK -- 107 route(s), 0 banner mismatches`; `DAL GUARD OK` |

## Two deliberate choices

**The route relays and returns; it does not adjudicate.** `StaleRun`, `SubjectMoved`, `SubjectGone`,
`NotHeld` and `QueueFull` belong to the injector, which holds the live ptr bindings, the run identity and
module 16's held sets — none of which exist on this side. So the honest answer here is "accepted for
relay", and the acceptance's own wording says exactly that.

**The request body is declared Server-side, not in `FusionRpg.Contracts`.** The two fields the FE does not
own (the durable `SubjectId`/`ScopeId`) are the injector's and the run's to resolve; a Contracts DTO would
invite the FE to supply them, which is the debug-scope rule turned into a type. The route carries the
`// Game Injector Debug` banner because it relays to the Injector and proves only what the injector does
with the order — never that a cast resolved.

## Still owed on the row

The **Injector verb/host/registry** half, which shares CAI4.3's blocker (the injector has no
`ActionCatalog` and no feed for one, and `grep` finds no `ActionCompiler`/`ActionRow` reference in
`gk-fusion/src/FusionRpg.Injector/` at all), and the two `web/**` files, which are outside this lane's fence.

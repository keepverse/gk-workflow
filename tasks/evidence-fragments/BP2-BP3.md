# BP2/BP3 — the real production caller of `RpgStore.Bind`

`AuraBindingPlan` (Core, pure) + `AuraBindingProducer` (Server, Data I/O) reconcile a player's durable
`aura`-sourced bindings to `AuraRuntime.ActiveAuraIds` on `/enable`/`/disable`, reusing the existing
`UniqueActorService.PushAtomUnionAsync` for G1's push (no `RpgHub.cs` edit — see BP1's re-verification).

| Check | Command | Result |
|---|---|---|
| Pure reconcile (7 cases: add, idempotent, disable, eviction-in-one-reconcile, equipped-not-enabled, duplicate self-heal, deterministic order) | `dotnet test tests\FusionRpg.Core.Tests --filter FullyQualifiedName~AuraBindingPlan` | 7/7 |
| Producer through the real endpoint (write, resolve, idempotence, withdraw, source-scoped withdraw, falsifier) | `dotnet test tests\FusionRpg.Server.Tests --filter FullyQualifiedName~AuraBindingProducer` | 6/6 |
| Full Core suite | `dotnet test tests\FusionRpg.Core.Tests` | 14525/14525 |
| Full Server suite | `dotnet test tests\FusionRpg.Server.Tests` | 656/656 |
| Full Data suite | `dotnet test tests\FusionRpg.Data.Tests` | 1646/1648 — 2 pre-existing, unrelated failures (`CreatureSpeciesImportCliTests`: "11 species stale against gk-data/packs/fusion/data/generated/creatures... run CreatureSpeciesGen and commit first" — species-anchor drift, nothing this session touched; out of scope, not fixed) |
| `guard-dal.ps1` | `.\scripts\guard-dal.ps1` | OK — no SQL outside `FusionRpg.Data` |
| Boundary guards | single-writer / secondary-no-unity / funnel-delta / actor-hub | all 4 OK |

**Found and fixed while wiring (not invented):** two other test hosts map `AuraRuntimeEndpoints`
(`AuraRuntimeEndpointsTests.cs`, `CommanderListEndpointsTests.cs`) and did not register
`UniqueActorService`/`InjectorCommandInbox`, so minimal-API's parameter-source inference threw at
startup ("uniqueActors | UNKNOWN"). Fixed by registering both, matching the existing
`UniqueActorAtomRepushTests.cs` pattern — `IHubContext<RpgHub>` needs only `AddSignalR()`; `RpgHub`
itself is never constructed unless a client actually connects.

**Falsifier required by the spec, run:** `A_broken_producer_would_be_caught_the_falsifier_the_spec_requires`
proves `ResolveBindings` returns nothing before `/enable` and something after — the aura genuinely does
not reach a resolved actor without this producer's write, not merely "the fixture already had rows."

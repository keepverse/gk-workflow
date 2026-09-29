# CAI4.5 — the Core half of the lawn ledger's two row sources

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row as written cannot be satisfied: it puts the row
source at `Injector/Effects/LawnCostRowSource.cs` and its TEST at
`gk-core/tests/FusionRpg.Core.Tests/Actions/LawnCostAuthorityTests.cs`, and a Core test project cannot reference the
injector. Measured, the build belongs in Core — `ActionCostRow` is Core (`ActionRow.cs:141`) and
`CompiledActionCost` is Core (`CompiledAction.cs:8`) — so `gk-core/src/FusionRpg.Core/Actions/LawnCostRows.cs`
landed there and the injector's file becomes the thin caller.

| Criterion | Command | Result |
|---|---|---|
| "Adding held-action keys leaves the basic-attack id's rows identical", proven not argued | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnCostAuthorityTests"` | **5 passed / 0 failed** — `Union_never_rewrites_an_existing_keys_rows` asserts `Assert.Same(basic[BasicId], union[BasicId])`: the SAME list instance, which is as strong as "unchanged" gets |
| One row per compiled cost, in the authored order | same run | **5 / 0** — `A_held_action_gets_one_row_per_compiled_cost_in_the_authored_order` (qi/OnCommit then poise/PerTick, each row naming its own action id) |
| An empty held set leaves the basic rows untouched | same run | **5 / 0** — `An_empty_held_set_returns_the_basic_rows_untouched` |
| A held action reusing a basic id does not take the key over | same run | **5 / 0** — the union never rewrites what it did not create, so the basic-attack row source keeps authority over its own id |
| Null arguments refused rather than a partial map returned | same run | **5 / 0** |
| Golden and the program's guard | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"`; `guard-actor-hub.ps1` | **5 / 0**; guard **exit 0** |

## Why the injector half did not land, named

`LawnBasicAttackCostCharger.cs`'s union needs the HELD SETS to build rows from — module 16's, i.e.
`LawnHeldActionRegistry`, which needs an `ActionCatalog` the injector has no feed for. That is CAI4.3's
blocker, stated there with its own evidence (`ActionCatalogHost` has zero users in `src/`; the only builder
is `RpgStore.BuildActionCatalog`, Data-side). The acceptance's *charged-amount* half is proven at the
union's keying for the same reason: there is no production composition to charge through yet, and inventing
one for a test would be a second cost authority — precisely what this module forbids.

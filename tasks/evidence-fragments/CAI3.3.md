# CAI3.3 — `siege-loadout-wiring` B: real loadouts enter a district assault (COMPOSITE SLICE)

Lane `combat-ai-2`, resumed after the checkpoint-4 merge. The row's Files list is three production files
(`World/Turn/DistrictAssaultResolver.cs`, `Data/Sqlite/RpgStore.WorldTurns.cs`) plus one **in-fence** Core
file, `Actions/IContainerEffectResolver.cs` — and that file carries a complete, self-contained deliverable
the spec sketches in full, so it is landed here.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `CompositeContainerEffectResolver` — first non-empty wins, ordinal, allocation-free | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeLoadoutWiringTests"` | **7 passed, 0 failed** | `Actions/IContainerEffectResolver.cs` (appended) |
| The first non-empty answer wins and later resolvers are NEVER asked | same run | passes — `The_first_non_empty_answer_wins_and_later_resolvers_are_never_asked` asserts the winner's ids AND that the second resolver's call count is 0, so the short-circuit is proven rather than assumed | — |
| An empty answer falls through — the reason the composite exists | same run | passes — the store bundle knows nothing about the four fixed construction containers (`ConstructionActions.cs:70-77`), so an empty answer must reach the second source | — |
| Empty, never null | same run | passes — `Nothing_answering_returns_empty_rather_than_null`, because `BindContainers` turns empty into its own LOUD rejection and null would move that failure downstream | — |
| Deterministic: the order is the constructor's order | same run | passes — swapping the two sources swaps the winner, which is what makes "siege composes `[store, construction]`" a statement about behaviour | — |
| Allocation-free per call, in bytes | same run | passes — `A_warm_composite_allocates_zero_bytes_per_call` measures `GC.GetAllocatedBytesForCurrentThread` after three warm passes and a collect: **0 bytes**, matching the spec's own "no LINQ, no closure" | — |
| An empty composite is legal and answers empty | same run | passes | — |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|~ContainerEffect\|~Siege\|Category=BalanceGuard"` | **363 passed, 0 failed** — no battle, siege or construction number moved, and the composite has no caller yet | — |
| Boundary, with real paths and the numbers | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/IContainerEffectResolver.cs','gk-core/tests/FusionRpg.Core.Tests/World/Turn/SiegeLoadoutWiringTests.cs') -Session combat-ai-20260920"` | **15100 passed / 0 failed** — the project is CLEAN now that checkpoint 4 fixed the four corpus facts, so this is a genuinely green boundary rather than a green-with-caveats one | — |
| Guards | `guard-actor-hub.ps1`; `guard-battle-responsibility.py`; `guard-doc-citations.ps1 -Strict` | first two exit 0; doc-citations remains the attributed repo-wide notify-rail red (21 HIGH, none in this program's docs) | — |

## NOT done — the row's two denied production files, and its caller

1. **`World/Turn/DistrictAssaultResolver.cs`** — the assault path that would COMPOSE the resolver
   (`[store bundle, ConstructionActions.ContainerResolver]`) and pass it to
   `BattleEngine.Resolve` — is under `gk-core/src/FusionRpg.Core/World/**`, outside this lane's allowed paths.
   So the composite is landed and tested but **no production host reaches it yet**: the row stays blocked
   on that file, exactly as CAI4.1 is blocked on its injector host and CAI2.5 on its injector wiring.
2. **`Data/Sqlite/RpgStore.WorldTurns.cs`** — the store-side container bundle the composite's first
   source would be — same fence.
3. The row's own test path was used (`gk-core/tests/FusionRpg.Core.Tests/World/Turn/SiegeLoadoutWiringTests.cs`),
   so the next lane adds the assault-composition cases to the file that already exists rather than
   creating a second one.

**A finding for the record, no row needed.** `gk-core/src/FusionRpg.Server/Program.cs:237` reads
`gk-core/data/tuning/combat-ai.v1.json` **by name**, the same pattern as the `siege.v2.json` line at `:231`. That
is why CAI3.5's and CAI3.6's tuning publishes face the H7 constraint: a `combat-ai.v2.json` cannot switch
its reader without that line moving in the same commit, and that file is outside this lane.

# Evidence — party-dungeon D3.5 (lane `pd-d3`, 2026-09-22)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| "an outcome golden per severity" (the verify line's one missing half) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~OutcomeResolverTests"` | `Passed: 58, Failed: 0` (34 prior + 24 new `[InlineData]` rows) | `gk-core/tests/FusionRpg.Core.Tests/Delve/Events/OutcomeResolverTests.cs` |
| "a `supplyOverride` red/green pair" (already shipped) | same run | pass (unchanged) | same file |
| Acceptance: severity shifts `dropBand` indices; weights then `TryInstantiate` at Θ; a dispatch plan; `consequence` closed vocabulary; `supplyOverride` reads `HoldsStock` | read against code + `EventDeckGoldensTests`/`EventDeckTests` | pass | `OutcomeResolver.cs`, `EventCatalog.cs`, `EventDeck.cs` |
| No regression across the module | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Delve"` | `Passed: 1739, Failed: 0` | — |
| DAL boundary | `pwsh -NoProfile -File scripts/guard-dal.ps1` | `DAL GUARD OK` | — |
| No new magic number / overflow | `python gk-core/scripts/audit-magic-numbers.py --domain dungeon` · `python gk-core/scripts/audit-overflow.py` | 0 findings · 0 critical | — |

**NOT proved**

- The new golden is a TABLE PIN of `ShiftDropBand`, not a resolution-level golden: it pins the
  band-index shift for all four ordinals × four severity tiers, which is exactly what the verify line
  names ("an outcome golden per severity"). The resolution-level goldens (24, hashed over
  `EventResolution`) are D3.3's, in `EventDeckGoldensTests`.
- The row's one unbuilt clause — the live call site threading a real pack-sourced
  `holdsOverrideStock` into `EventDeck.Resolve` — is **not** proved and is **not this row's**: the
  owner's transfer ruling at the top of `tasks/party-dungeon-todo.md` moves it to `npc-story-events`'
  `delve-live-rooms` ("the live call site of the draw with a real pack-sourced `holdsOverrideStock`
  fact → `delve-live-rooms`"). The resolver LOGIC is real and tested; the wire is another program's.
- `supplyOverride` reading `HoldsStock` end-to-end from a real pack is likewise unproved: all 54 real
  events carry `supplyOverride: "none"` and all 31 real supplies carry an empty `overrideTags` array, so
  the path is exercised by fixtures only (the row's own 2026-09-08 finding, re-confirmed).

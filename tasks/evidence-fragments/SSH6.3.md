# SSH6.3 — derived levers per failing cell: `bore` / `imbue` / `forge-gem` souls (R20)

Landed in `gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricing.cs` (+ 4 tests): `ComboPricingLever`,
`ComboPricing.Derive`, and a `Lever` on every `ComboPriceLeg` so a leg knows which coefficient can move
it. Every failing cell gets the levers ON ITS OWN ROUTE, the cheapest one by name, and its required
coefficient; the report gets one derived coefficient per lever; a cell no lever can move is listed by id.

The derivation is arithmetic, not a search: the cell needs a floor of
`ceil(power · elevate · 1000 / (ΔPower · maxRatio))` souls, its lever's legs carry `T` of the floor and the
rest cannot move, so the factor is `ceil((need − (floor − T)) · 1000 / T)`, rounded UP. A lever whose souls
leg is not `rung`-linear is refused by name — deriving one would be a guess.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| a gem-only cell names `forge-gem` as its lever | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboPricing"` | **11 passed / 0 failed**. On the shipped tuning the floor is `fused`'s (no bore, no imbue), so `LeversOf` is exactly `[ForgeGem]`; a cheap-rung floor carrying four bores names `[Bore, ForgeGem]` |
| the derived `forge-gem` coefficient makes a gem-only cell pass, one below still fails | (above) | `The_derived_forge_gem_coefficient_makes_a_gem_only_cell_pass`: today's coefficient is asserted at **30**; the derived one passes the cell, `derived − 1` does not |
| the derived coefficient makes EVERY cell pass | (above) | `The_derived_coefficient_makes_every_cell_pass`: two failing cells → derivation → the whole catalog re-priced with the derived triple via `MaterialTuning.Mutated` + `MaterialRecipeCatalog.Load` → `after.Passes`; the dearest cell's requirement is what sets `forge-gem` |
| a cell no leg can move is listed by id | (above) | `A_cell_no_lever_can_move_is_listed_by_id`: a leg priced by the upcycle chain carries `Lever: null`, so the derivation reports the id and no invented lever (hand-built report — unreachable through `Measure` today, which is the reading, not a gap) |
| overflow audit clean for the new file | `python gk-core/scripts/audit-overflow.py` | exit **0**, `A2=0 A3=0 A4=0 A5=0 A6=1` (the A6 is the pre-existing `Actions/Ai/CoreIntentPolicy.cs:313`); **0 findings name `ComboPricing.cs`** |
| scoped verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricing.cs','tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs') -Session strain-splice-host-20260921"` | exit **0** — `FusionRpg.Core.Tests` **15086 passed / 0 failed** |

## Not proved / open

- The three derived coefficients are computed **per lever against the other legs at their current
  values**, so the triple is SUFFICIENT, never under-stated — but it is not claimed to be the jointly
  minimal triple (a joint solve is not what the report's publish path needs; `socket-pricing` publishes
  the maxima). Stated in `ComboPricingDerivation`'s own doc comment.
- Applying the derived numbers is a `materials.v{n+1}` publish: SSH8.5 owns it (`publish.py materials
  operations.<verb>.souls.coefficient=<derived>`), and SSH6.4 owns printing them.
- The upcycle-chain leg carries no lever today because the chain never wins at today's numbers; if a
  reprice makes it win, the derivation correctly refuses to move it rather than guessing.

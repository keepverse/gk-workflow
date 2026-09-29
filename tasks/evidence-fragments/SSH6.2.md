# SSH6.2 — `ComboPricing`: power, price floor, rarity reference, and the bound

New: `gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricing.cs` (the measurement) and
`tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs` (7 tests, on the REAL tuning / ladder /
materials catalog; only the atom price and the ladder's own spread are fixtures).

Every term is an existing one — no second curve: power is `ActorPowerCache.Compose` over the atoms
`ComboContainerBuild.TryBuild` mints; price is `MaterialRecipeCatalog.Resolve` read for its souls leg
(the one unit of price; the other legs are readings); the rarity route is
`RarityPowerCeilings.PriceReferenceSlate` above minus below, over `elevate`'s souls; geometry is
`SocketLimits.SocketCircuitSize` and the tuning's own `rarityGrant` windows.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| power from `ActorPowerCache.Compose` over `ComboContainerBuild` atoms | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboPricing"` | **7 passed / 0 failed**; `A_combination_cheaper_than_the_rarity_route_fails_the_report_by_cell` rebuilds the cell's power through `TryBuild` + `Compose` and asserts equality |
| `priceFloorSouls` over the admitting rungs with the best-rolled chassis | (above) | `Price_floor_takes_the_cheapest_admitting_rung_and_best_rolled_chassis`: on the shipped table the floor is `fused` (window 2..4) with **no bore at all** — a MIN-roll reader would bore 2 there and take `chaff`'s 4; on the first three rungs the floor is `chaff` (4 bores, 200 souls) rather than `grafted`'s 2 at 300. The legs sum to the floor exactly |
| reference from `PriceReferenceSlate` / `elevate`; prices from `MaterialRecipeCatalog.Resolve` | (above) | `A_rarity_step_...`: the chosen step's `DeltaPower` equals `PriceReferenceSlate(to) − PriceReferenceSlate(from)` and `ElevateSouls` is the resolver's own souls leg (60 at rung 0) |
| `the_comparison_is_cross_multiplied` | (above) | the ratio 1000 vs reference 999/1000 case FAILS, and the test states the truncated form that would have passed it |
| `a_rarity_step_that_buys_nothing_is_excluded_by_name` | (above) | the shipped ladder's own single no-op step (`firstseed → sunwoven`, ΔP 0 — same affix count and same reference tier) is reported with both rung ids in its reason |
| all steps excluded → refused | (above) | `All_rarity_steps_excluded_is_refused_by_name`: `ChosenStep` and `Measure` both refuse, naming the condition |
| the top rung gives no step | (above) | `The_top_rung_gives_no_step`: 9 steps for 10 rungs; the top rung is never a `FromRungId` |
| a zero floor is refused by name | (above) | `A_zero_floor_is_refused_by_name`: `RequirePositiveFloor` refuses directly, and the wiring refuses a cell whose plan + bore-free rung leave nothing to pay |
| `a_combination_cheaper_than_the_rarity_route_fails_the_report_by_cell` | (above) | one report, two cells: `FailingCells` is exactly the 100_000_000-power cell (ratio 263_157_894 vs reference 1_100_000), the second cell passes against the same reference |
| `python gk-core/scripts/audit-overflow.py` clean for the new file | `python gk-core/scripts/audit-overflow.py` | exit **0** — A2/A3/A4/A5 clean, the one A6 finding is the pre-existing `Actions/Ai/CoreIntentPolicy.cs:313`; **0 findings name `ComboPricing.cs`** |
| scoped verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricing.cs','tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs') -Session strain-splice-host-20260921"` | exit **0** — `core-fallback` + `core-tests-fallback` → `FusionRpg.Core.Tests` **15082 passed / 0 failed** (15075 + the 7 new) |

## Readings worth carrying forward

- Floor for the fixture cell at tier 1 with plan `[1,1,2,2]`: **380 souls** (4 gems 30/30/60/60 + bore leg),
  and the reference step is **66_000 power per 60 souls** of `elevate`.
- The upcycle chain (`gem(t) = min(forge-gem(t), sockets.upcycleInputPerOutput · gem(t−1) + upcycle(t))`)
  never wins against today's numbers (3×30·(t−1) + 20 > 30·t for every t ≥ 2) — implemented as the spec's
  term, and a reprice is what would move it.

## NOT proved / open

- **One tier only.** `ComboPricing` prices whatever tier its request names; the ladder that would give it
  more than rung 1 is `tier-ladder` (SSH7.1/SSH7.2). Nothing here invents a rung.
- **No report verb, no provenance, no published bound**: SSH6.3 (per-cell levers), SSH6.4
  (`items combo-budget --report`), SSH6.6/SSH6.7 (`comboPricing` parse + the boot check) and SSH6.8
  (`sockets` v3 + the `Category=BalanceGuard` test) are untouched by this row.
- The fixture atoms are `stat.modify` on `maxHp` (the shape `PriceReferenceSlate`'s own reference affix
  uses), so a fixture cell's absolute power is a fixture fact, not a shipped reading.

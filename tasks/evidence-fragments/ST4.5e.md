# ST4.5e — `Unpriced` is visible per action, and the pooled-channel gap is bounded

**Status: done.** Manager ruling on the ST4.5a diagnosis, item (3): *"Pooled-channel atoms (3 of the
zeros): make 'Unpriced' visible in the calibration report per action (never folded in as 0), and
determine whether they can be priced from data that already exists; if yes, price them through the same
one helper; if not, record the gap with its bound (what those 3 would need to be to change
recommendedReferencePower) and name the follow-up."*

## Half 1 — the report names what its price left out

| File | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Effects/Atoms/Power/ActorPowerCache.cs` | `ComposeWithFindings` returns the composition **plus the ids of the atoms it could not price**; `Compose` delegates to it and discards the list |
| `gk-core/src/FusionRpg.Core/Actions/Rungs/PricedAction.cs` | `UnpricedAtomIds` — `null` means "not reported", empty means "asked and found none" |
| `gk-core/src/FusionRpg.Core/Actions/Rungs/BudgetCalibration.cs` | `BudgetCalibrationResult.UnpricedActions` (+ the `UnpricedAction` record) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActionCatalog.cs` | `PriceContainerWithFindings`; `ListActionPricing` carries the findings, `PriceContainer` keeps reading the number |
| `gk-core/src/FusionRpg.Server/DebugEndpoints.cs` | `unpricedActions` on the endpoint |

**One implementation, so no price moved.** `Compose` is `ComposeWithFindings(...).Power` — the finding is
additive, never a correction, and never a filter: the action is still priced and still counted (contract
3), so a `0` in a rung's distribution can now be told apart from "these atoms could not be priced".
All three of `ComposeWithFindings`' skips are named: an unknown kind, an unpriceable atom on the `Price`
path, and a channel whose coefficient row is missing (the one the report could not previously see at all).

Tests: `ComposeFindingsTests` (3 — the pooled atom is named and the price equals the reporting
composition's), `BudgetCalibrationTests` (2 — the action is named and still priced; a reader that
reported nothing produces no entries), `ActionPricingTests` (1 — the REAL pooled-channel container path
through `UpsertAtom`/`ListActionPricing`), and the E2E endpoint reconciliation (the wire's list equals
the store's own).

## Half 2 — can they be priced from data that already exists? **No, and it does not matter for the scalar**

**The data exists; the path does not.** `gk-data/packs/fusion/data/seed/channel-pools/pools.v1.json` is authored and
`AtomSeedFile.Collect` already parses it into `SeedContent.ChannelPools` — but `RpgStore` has **no
`channel_pool` table, no `UpsertChannelPool` and no reader** (`SeedContentCoverageTests.cs:37-48`
records exactly that), and `ActorPowerCache.Compose` has no pool parameter at all. Pricing them
properly therefore needs: a store surface for pools + a pool parameter on the composition + **the same
at A-G1's check** (`ContentValidation.Budget` calls the same `Compose`), or the check and the report
would price differently — the one thing contract 1 forbids. That is E30 channel-pool's own remaining
work, not an addendum to a report module. **Follow-up: E30's channel-pool store surface**, then this
report can be re-taken with its three atoms priced.

**The bound.** `recommendedReferencePower` is `max over actions of ceil(realized × 1000 / (poolRolls ×
qPowerMilli))`, and on this corpus it is **1512**, set at rung 4 (`gk-core/data/tuning/action-rungs.v3.json`:
rung 4 is `poolRolls 1 × qPowerMilli 2315` = 2315; rung 7 is `2 × 5359` = 10718). So a pooled action
would have to price at

- **≥ 3501** on rung 4 (general.0005) — `realized > 1512 × 2315 / 1000 = 3500.28`; or
- **≥ 16206** on rung 7 (fruit.001, hypno.002) — `realized > 1512 × 10718 / 1000 = 16205.6`

to move the scalar. If they were priced, the published derivation says they would imply roughly **13**
(rung 4: one `stat.derived` pooled atom of mean magnitude 32, at the only `stat.derived` coefficient row
— 1000‰, referenceScale 1) and **19 / 9** (rung 7: mean magnitudes ~107 and ~214 over a divisor of
10718). Those are two orders of magnitude short of 3501.

**So the pooled-channel gap cannot change `recommendedReferencePower`.** What it understates is the
per-rung low tail: rung 4's `min` reads 0 instead of ~13, and rung 7 carries 8 zeros instead of 6 (its
`p50` stays 0 either way). The scalar ST5.2 will publish is not affected by this gap — which is worth
knowing before anyone treats the three zeros as a reason to distrust it.

## Verification

| Command | Result |
|---|---|
| `dotnet test tests\FusionRpg.Core.Tests -c Release -v q` | **14207/14208** — only the named CRLF worktree artifact |
| `dotnet test tests\FusionRpg.Server.Tests -c Release -v q` | **552/552** |
| `dotnet test tests\FusionRpg.Data.Tests -c Release -v q --filter "FullyQualifiedName~Power\|~Content\|~Action\|~Item"` | **471/471** |
| `dotnet test tests\FusionRpg.E2E.Tests -c Release -v q` | **226/226** |
| focused: `~ComposeFindings\|~BudgetCalibration` / `~ActionPricingTests` / `~ActionBudgetReport` | **19/19**, **5/5**, **1/1** |

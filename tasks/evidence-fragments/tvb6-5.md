# TVB6.5 — the reading, re-measured at this head (K3 landed)

Seven-path change inside `gk-core/src/FusionRpg.Core/Stats/` and `gk-core/src/FusionRpg.Core/Effects/**`, planned at
`d9f87811b` with `verify-change.ps1 -AllowUnscoped -PlanOnly`:

| Path | Plan |
|---|---|
| `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs` | `battle-effect-math` (focused) |
| `gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs` | **`core-advanced-effect-clock` (focused)** — was `core-fallback` before TVB6.4's K3 |
| `gk-core/src/FusionRpg.Core/Effects/CombatHitEmitPolicy.cs` | `core-fallback` (module) |
| `gk-core/src/FusionRpg.Core/Effects/DamageFx.cs` | `core-fallback` (module) |
| `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs` | `core-fallback` (module) |
| guards | `battle-responsibility`, `funnel-delta` |
| test check | `test: core` (whole group) |

Command: `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths
'gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs','gk-core/src/FusionRpg.Core/Effects/EffectBag.cs',
'gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs','gk-core/src/FusionRpg.Core/Effects/CombatHitEmitPolicy.cs',
'gk-core/src/FusionRpg.Core/Effects/DamageFx.cs' -AllowUnscoped -PlanOnly"`

**Reading against the before-pair** (recorded in `tvb6-5`'s own row and `tvb6-2.md`): one of the five
production paths narrowed (`AdvancedEffectClock.cs`), the other four still plan the module fallback. The
five paths that remain `core-fallback` are exactly K1's target, so they narrow when **TVB6.2** lands -
which is gated by **TVB-F18** (the production map binds nothing; the reference set is proven correct, so
the fault is inside `BuildCompilation`).

## K3 completeness, same run

`guard-verification-boundaries.py --report` now lists **seven orphans and none of them `core.*`**:
`data.action-pricing`, `data.ai-empire-specimen`, `data.allocation-respec`,
`data.effective-unique-allocation`, `data.item-upgrade`, `guard.unique-allocation-reader`,
`server.lawn-quick-start`. All six former `core.*` orphans select a boundary now, so K3's core half is
complete; the ideal's "Core half done" line stays unwritten until K1 (TVB6.2) lands, because that
sentence covers the whole Core half.

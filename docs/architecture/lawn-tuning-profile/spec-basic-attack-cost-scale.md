# Spec: `basic-attack-cost-scale` (lawn-tuning-profile module 7)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) ·
**Depends on:** `lawn-resource-scale` · **Unblocks:** `lawn-scale-live-proof` · **Fixes:** defect M4
**Status:** spec, 2026-09-16. Not built.

## Objective

Price a swing against the pool it spends from.

The basic attack costs a **flat 25 stamina**
(`gk-core/data/tuning/action-corpus-cost-templates.v2.json` → `kinds.basic.baseAmountAtRung1 = 25`, marked
`UNMEASURED` in that file's own `_meta`), while the pool and its regen both scale with `P(Θ)`. So the
price of acting falls to nothing as a character grows: against the clean-player pool of 53 a swing is
half the bar; against 1,706 it is 1.5%.

`spec-lawn-combat-calibration.md`'s own boundary already requires an anchored cost. This module is that
requirement, landed.

## The shape

```
cost(Θ, rung) = anchor(Θ) × q(rung)
```

- `anchor(Θ)` is a **fraction of the actor's own pool at that Θ**, not an absolute — that is what makes
  the price hold its meaning across the ladder.
- `q(rung)` keeps the existing rung ordering (`basic` cheapest, `support`/`status` dearest). The shipped
  relative ordering of `action-corpus-cost-templates` is preserved; only its absolute anchoring changes.
- The flat value stays reachable: a mode whose profile names no anchor keeps today's behaviour exactly,
  so battle, delve and siege are untouched.

## Tunables

`data/tuning/mode-profiles.v{n}.json`, lawn row (the cost-templates file keeps the rung ordering):

| Key | Meaning | v1 |
|---|---|---|
| `modes.lawn.cost.basic.poolFractionAtRefTheta` | `anchor(Θ)` as a fraction of pool | `UNMEASURED` |
| `modes.lawn.cost.refTheta` | the rung the fraction is anchored at | shares `base-relative-read`'s |
| `modes.battle.cost.*` | absent — battle keeps the flat template | unchanged |

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionCost|BasicAttackCost"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~Golden"
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
```

## Project structure

| What | Where |
|---|---|
| Cost resolution | the kind-aware cost path that reads `action-corpus-cost-templates` |
| Anchor | the mode profile row |
| Tests | `tests/FusionRpg.Core.Tests/Actions/BasicAttackCostScaleTests.cs` |

## Testing strategy

- ✅ **Cost is a stable fraction of pool across Θ** for a fixed allocation — the defining property.
- ✅ Rung ordering survives whatever the anchor is.
- ✅ A mode with no anchor resolves to exactly the flat template value (battle's identity).
- ✅ Cost is never zero and never exceeds the pool — both structural bounds, commented as such.
- ❌ Never assert 25, or any shipped fraction. Readings.

## Boundaries

- **Always:** keep the existing template's relative ordering; leave battle on the flat path.
- **Ask first:** nothing.
- **Never:** make the cost depend on the victim (that is a combat formula, not a price); add a second
  cost resolver beside the kind-aware one.

## Numeric types

Cost is carried as `long` per-mille of pool and divided by 1000 last, `checked`. The fraction is
`double`.

## ActorHub gate

Consumes Hub's `resource.max.*` output to anchor against; contributes nothing.

## Success criteria

1. A swing costs a stated fraction of the actor's pool at every Θ and every allocation.
2. Battle/delve/siege costs and goldens byte-identical.
3. With `lawn-resource-scale`, a fully-invested lawn actor exhausts — observed by
   `lawn-scale-live-proof`.

## Open questions

None.

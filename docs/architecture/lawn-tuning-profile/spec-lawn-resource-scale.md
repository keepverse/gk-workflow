# Spec: `lawn-resource-scale` (lawn-tuning-profile module 6)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) ·
**Depends on:** `mode-profile`, `regen-unit-trace` · **Unblocks:** `basic-attack-cost-scale`,
`lawn-scale-live-proof` · **Fixes:** defect M2
**Status:** spec, 2026-09-16. Not built.

## Objective

Make exhaustion a **mechanic at every build**, instead of the all-or-nothing gate it is today.

Measured live (`_lawn-combat-proof4-exhaustion-clean-player.json` and the L-N2 traces):

| Actor | stamina max | regen | exhaustion |
|---|---|---|---|
| Clean player, zero allocation | 53 | 0.2 / tick | **591 events over 551 hits** — exhausts every 30–45 hits |
| Same actor, **three** aptitude points | 1,706 | 29.2 / tick | **0 events** — never empties |
| Player 1 (1,440 points allocated) | 1,009 | 17.2 / tick | 0 events |

Three points is the difference between a rhythm and a resource that does not exist. The cause is unit,
not taste: the baseline pool is `BaseHp(Θ) × shareOf/1000` — about 0.5 × `P(Θ)` — while each aptitude
edge adds 8–26 × `P(Θ)` on top of it. The pool is a rounding error next to its own modifiers.

## Depends on the unit answer

`regen-unit-trace` must land first. Sizing a pool against a rate whose unit is unsettled is exactly how
this defect happened: the runtime reads `resource.regen.*` as units per 100 ms tick while the POC that
fitted the coefficients accrued per round (~200 ticks). A pool sized before that is settled is sized
against a number that may be 200× off.

## The shape

The lawn row carries **family scales**, not per-channel overrides:

```
lawn.families["resource.max"].scale       — applied to the aptitude contribution, not the baseline
lawn.families["resource.regen"].scale
```

Sizing rule, stated so the numbers are derivable rather than taste:

1. **A zero-allocation actor exhausts** — it does today (591 events), and that must survive.
2. **A fully-invested actor still exhausts**, in a longer rhythm — **owner ruling 2026-09-16**:
   stamina means something at every build, and investment buys a longer rhythm, never immunity. The
   target is a *ratio* between the two, not an absolute: the pool at full investment is a stated
   multiple of the pool at zero, and the multiple is the tunable. (The rejected alternative — investment
   removes exhaustion — would have made today's measured `ExhaustionEvents 0` the intended end state.)
3. **Regen refills a bounded fraction of the pool per second at every build**, so recovery time is
   roughly build-independent while capacity is not — burst scales, sustain does not vanish.

## Tunables

`data/tuning/mode-profiles.v{n}.json`, lawn row:

| Key | Meaning | v1 |
|---|---|---|
| `modes.lawn.families.resource.max.scale` | aptitude contribution scale for pools | `UNMEASURED` |
| `modes.lawn.families.resource.regen.scale` | same for rates | `UNMEASURED` |
| `modes.lawn.exhaustion.fullInvestmentPoolMultiple` | rule 2's ratio | `UNMEASURED` |
| `modes.lawn.exhaustion.refillFractionPerSecond` | rule 3's bound | `UNMEASURED` |

Battle's row is unchanged, so `battle-resources.v{n}.json` and every battle golden stay as they are.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Resource|Exhaust|Stamina"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~Golden"
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
python gk-core/tools/tuning/publish.py mode-profiles <dotted.key>=<value>
```

## Project structure

| What | Where |
|---|---|
| Scale application | `ResourceBaselineSubsystem` / `AptitudeSubsystem` read the profile row |
| Numbers | `data/tuning/mode-profiles.v{n}.json` |
| Tests | `tests/FusionRpg.Core.Tests/Stats/LawnResourceScaleTests.cs` |
| Live evidence | `lawn-scale-live-proof`'s run files |

## Testing strategy

- ✅ **The ordering property**: for any allocation, `poolMax(allocated) ≥ poolMax(zero)` and the ratio is
  bounded by the tunable — a contract over the whole allocation space, not one sampled build.
- ✅ **Exhaustion is reachable at full investment** in the closed-form sense: cost per swing × swings per
  refill window > pool. Asserted symbolically against the shipped tunables, so a future retune that
  breaks it fails a test instead of shipping.
- ✅ Battle's numbers are byte-identical (its row is the identity).
- ✅ No pool is capped: the no-ceilings rule holds — a scale, never a clamp.
- ❌ Never assert 53, 1,706, or any live figure. Readings.

## Boundaries

- **Always:** publish `v{n+1}`; keep every starting value marked `UNMEASURED`; scale the aptitude
  contribution, not the baseline formula (the baseline is `BattleModels`' and shared).
- **Ask first:** nothing.
- **Never:** clamp a pool to make exhaustion happen (a clamp turns "your build stopped mattering" into a
  bug with no symptom); change `TicksPerSecond`; touch battle's row.

## Numeric types

Pools and rates are `long` at the reader boundary (`ResourceChannelReader`, `checked`), rates carried as
per-mille per tick with the single `/1000` at `ResourcePoolState`. Scales are `double` ratios.

## ActorHub gate

Consumes and contributes through the existing resource subsystems. No new composer.

## Success criteria

1. A zero-allocation lawn actor still exhausts, in the same order of cadence it does today.
2. A fully-invested lawn actor **also** exhausts, in a longer rhythm — the thing that is impossible
   today.
3. Battle goldens byte-identical.
4. The two properties above are asserted in test, and then **observed live** by
   `lawn-scale-live-proof` — which is where `lawn-combat-wire` proof 5 / L-N2 finally becomes runnable.

## Open questions

None. Every starting number is `UNMEASURED` by design and sized by the live proof.

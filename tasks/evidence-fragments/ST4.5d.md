# ST4.5d — a trigger with no frequency row is refused by name, never priced at zero

**Status: done.** Manager ruling on the ST4.5a diagnosis, item (2): *"GetPowerTables and the pricing
path must never price a triggered atom at 0 because a frequency is missing: a missing frequency for a
trigger that content uses is a loud refusal/finding naming the trigger, with a planted-violation test."*

## What changed

| File | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Effects/Atoms/Power/CostFunction.cs` | `PriceForChannel` refuses by name when the atom's trigger has no rate, instead of returning a zero vector under a `Priced` verdict |
| `gk-core/src/FusionRpg.Core/Effects/Atoms/Power/CoefficientTable.cs` | `FrequencyOf`'s doc corrected — it claimed an unlisted trigger's zero "the ICD factor handles", which is false: `Conditionality` multiplies by `DivRound(perMinute × 1000, 60)`, so the whole factor is zero and the ICD multiplier cannot rescue it |
| `tests/FusionRpg.Core.Tests/Atoms/CostFunctionTriggerFrequencyTests.cs` | 4 tests: the planted violation, the same atom arriving at a real price once the row exists, the triggerless short-circuit, and a total rate of zero treated as no row |
| `tests/FusionRpg.Core.Tests/Atoms/PowerVectorTests.cs` | `A_zero_frequency_trigger_does_not_divide_by_zero` — its intent (no throw, ICD neutral at zero frequency) is unchanged and still asserted; what moved is the surface, from "prices 0" to "refused by name" |
| `gk-core/tests/FusionRpg.Data.Tests/Power/PowerTableSeedTests.cs` | the closure guardrail: every trigger the real authored corpus uses has a row in the shipped seed |

**The power does not move.** The refusal returns `PowerVector.Zero` and `Compose`'s `Price` path did
`if (priced.Ok) total += priced.Power` — so the atom contributed zero before and contributes zero now.
What changes is that it can no longer do so *silently*: it lands in `BackfillAtomPower`'s `Unpriced`
list, in `ContentValidation.Drift`'s blocking "stored power exists but the atom no longer prices"
finding, and (ST4.5e) in the calibration report's per-action unpriced ids. That is why no golden moved.

## Measured before changing: no shipped atom is newly refused

`CostFunction.PriceForChannel` refuses on a rate of zero, so if real content authored a trigger the seed
does not carry, the refusal would fire on shipped content. Read-only against the owner's published DB:

```powershell
@'
import sqlite3
c = sqlite3.connect("file:.../dist/FusionRpg.Server/data/rpg-hot.sqlite?mode=ro", uri=True)
for r in c.execute("select trigger_id, count(*) from effect_atom group by trigger_id"):
    print(r)
'@ | python -
```

```
(None, 327)  ('OnDamageDealt', 86)  ('OnSpawn', 2)  ('OnDeath', 1)  ('OnTimer', 1)
```

The whole 417-atom catalog uses four triggers, and the seed carries all four (plus `OnDamageTaken`,
which nothing uses yet). So the refusal is **inert on shipped content and live for the next mistake** —
which is what the closure test pins, so it cannot silently start firing on the corpus.

## Verification

| Command | Result |
|---|---|
| `dotnet test tests\FusionRpg.Core.Tests -c Release --verbosity minimal` | **14200/14201** — only the named CRLF worktree artifact |
| `dotnet test tests\FusionRpg.Data.Tests -c Release --verbosity minimal --filter "FullyQualifiedName~Power\|FullyQualifiedName~Content\|FullyQualifiedName~Action\|FullyQualifiedName~Item"` | **470/470** |
| `dotnet test tests\FusionRpg.E2E.Tests -c Release --verbosity minimal` | **226/226** |
| focused: `--filter "FullyQualifiedName~CostFunctionTriggerFrequency"` | **4/4** |
| focused: `--filter "FullyQualifiedName~PowerTableSeed"` | **5/5** |

`Server.Tests` is unchanged from ST4.5c's run (534/552, all 18 from the one named
`ActionBaseTuningHub` cause): this change alters no number, so it cannot alter that boundary.

## One consequence found and recorded, not fixed (out of the ruling's scope)

`ActorPowerCache.Compose`'s **string-channel** path never calls `CostFunction.Price` at all — it
accumulates the raw magnitude and prices the channel total, so a triggered atom with a concrete
`channel` string is priced as if UNCONDITIONAL (over-stated, not zeroed). That is a different defect
from the one this ruling names and it is a price movement, so it is recorded here rather than changed:
fixing it would move the power of every triggered `stat.modify` atom in the game and is a manager call,
not an unattended edit.

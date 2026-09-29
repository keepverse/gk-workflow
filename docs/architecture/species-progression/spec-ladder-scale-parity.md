# spec — `ladder-scale-parity`

**Module 2 of `species-progression`** ([map](../species-progression-map.md)). Depends on nothing.
Status: spec, 2026-09-18, strengthened the same day (negative-`kMicro` reading taken). No build authorized
until the map is reviewed.

## Objective

One function computes `k · P(Θ)` for a per-million coefficient. Today two do, with different arithmetic
(map **C6**):

| Site | Arithmetic | Consequence |
|---|---|---|
| `AptitudeReadFunctions.Magnitude` (`AptitudeReadFunctions.cs:48-68`) | `kMilli × sharePowMilli × pTheta` in `decimal`, `/ 1_000_000`, **round away from zero**, throws `OverflowException` past `long` | the live aptitude read, every lawn and battle actor |
| `AtomCompiler` `powerLadder` + `kMicro` (`AtomCompiler.cs:618-621`) | `checked(kMicro * pTheta / 1_000_000)` in `long` — **truncates**, and the multiply overflows before the divide can bring it back into range | tree-binder atoms today; **every projected 2b atom** once `species-layer-projector` lands |

`species-layer-projector` projects a 2b allocation into atoms whose coefficient is exactly
`kMilli × sharePowMilli` (an integer product of the two per-mille factors). With one shared scale
function, a projected atom resolved at `Θ` equals the live resolve at `Θ` **by construction** — which is
what makes the ideal's *"the math does not change; where it runs does"* true rather than approximately
true. Without it, the parity test in module 3 cannot be exact and the projected path overflows earlier
than the live one.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LadderScale|FullyQualifiedName~AptitudeReadFunctions|FullyQualifiedName~PowerLadderMagnitude"
dotnet test gk-forge/tests/FusionRpg.TreeBinder.Tests
dotnet run --project gk-forge/tools/TreeBinder -- --seed gk-data/packs/fusion/data/seed/passive-tree --out gk-data/packs/fusion/data/generated/passive-tree --check
python gk-core/scripts/audit-overflow.py --targets A3
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project Structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Power/LadderScale.cs` | **(new)** `LadderScale.Micro(long kMicro, long pTheta) → long` |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeReadFunctions.cs` | `Magnitude` computes `kMicro = checked(kMilli * sharePowMilli)` and returns `LadderScale.Micro(kMicro, pTheta)` |
| `gk-core/src/FusionRpg.Core/Effects/Atoms/AtomCompiler.cs` | the `kMicro` branch (`:618-621`) calls `LadderScale.Micro` |
| `gk-core/tests/FusionRpg.Core.Power.Tests/Power/LadderScaleTests.cs` | **(new)** |

## Code Style

```csharp
namespace FusionRpg.Core.Power;

/// <summary>The one k · P(Θ) product for a per-million coefficient. decimal is the widening type
/// because kMicro × pTheta overflows long long before the true quotient does; rounding happens once,
/// last, away from zero — the rule AptitudeReadFunctions.Magnitude already shipped.</summary>
public static class LadderScale
{
    public static long Micro(long kMicro, long pTheta)
    {
        if (kMicro < 0) throw new ArgumentOutOfRangeException(nameof(kMicro), kMicro, "kMicro must not be negative");
        if (pTheta < 0) throw new ArgumentOutOfRangeException(nameof(pTheta), pTheta, "pTheta must not be negative");
        var rounded = Math.Round((decimal)kMicro * pTheta / 1_000_000m, MidpointRounding.AwayFromZero);
        if (rounded > long.MaxValue)
            throw new OverflowException($"ladder magnitude overflow: kMicro={kMicro} pTheta={pTheta}");
        return (long)rounded;
    }
}
```

Negative coefficients: the aptitude path already refuses them (`AptitudeReadFunctions.cs:51`). **Read
2026-09-18 (strengthen pass), a reading, not a pinned count:** every `kMicro` in the committed
`gk-data/packs/fusion/data/generated/passive-tree/**` corpus is non-negative, so the non-negative precondition above holds for
today's atom side and a negative `kMicro` **throws** rather than rounding. The build re-reads the corpus
before landing (`grep -rhoE '"kMicro"\s*:\s*-?[0-9]+' gk-data/packs/fusion/data/generated/passive-tree`); if a malus node has
appeared since, the precondition widens to a sign-symmetric rounding in the same change, never a clamp.

## Testing Strategy

- **Exactness:** for a grid of `(kMilli, share, γ, Θ)` including the edge where `kMicro × pTheta` exceeds
  `long.MaxValue` while the quotient does not, `AptitudeReadFunctions.Magnitude(...)` equals
  `LadderScale.Micro(kMilli * sharePowMilli, pTheta)` — the refactor is behaviour-preserving for the
  aptitude path (it already rounded in `decimal`).
- **Overflow is a throw, never a wrap or a clamp**, at the first `pTheta` whose true quotient exceeds
  `long`.
- **The behaviour change is on the atom side only**, and it is measured before it is described:
  run `FusionRpg.TreeBinder.Tests`, the tree-resolve Core tests and `BattleGoldenTests`, and record
  which values move (truncation → rounding moves a value by at most 1 unit; the widened multiply removes
  spurious overflows). If a golden moves, report the list and stop — that is the Ask-first below, not a
  re-bless.
- `audit-overflow.py` shows no new finding in the three touched files.

## Numeric

`long` result, `decimal` intermediate, single rounding step, `checked`/explicit throw on range — the
CLAUDE.md range rules (widen before multiply; overflow throws). `P(Θ)` is the one ladder's
(`PowerLadder.Value`); nothing here is a new curve.

**Filed, not fixed:** the `kMilli` branch (`AtomCompiler.cs:624`) narrows to `int` —
`checked((int)((long)kMilli * pTheta / 1000))`. Under the repo's caps rule a narrowing cast on a
magnitude is a ceiling, and per-mille `int` leaves its range at `Θ = 3,213`. Its own comment keeps it
*"exactly as shipped"* for authored atoms. This module does not widen it (authored `kMilli` content and
its refusal semantics are the atom program's), and records it for `audit-overflow.py`'s register.

## Tunables

None. Rounding mode and widening type are structural (correctness of one product), not balance.

## Seedsmith / generator

No generator involved. `gk-forge/tools/TreeBinder` emits `kMicro` coefficients; their committed values do not
change, only the compile-time product.

## ActorHub gate

No contribution. Both callers already feed Hub through registered subsystems (`rpg.aptitude`,
`atom.derived`); this changes arithmetic inside them.

## Boundaries

- **Always:** prove the aptitude path byte-identical; list every atom-side value that moves.
- **Ask first:** any golden that moves; changing the `kMilli` `int` branch.
- **Order:** this module lands before `species-layer-projector` (it is module 3's exactness premise) and
  is independent of the program's one re-bless (`species-layer-delivery` step 6.1). Its own atom-side
  movement is at most one unit of rounding per value and is **not** a re-bless: if it moves a golden, it
  stops at the Ask-first above rather than folding into 6.1.
- **Never:** keep a second copy of the product anywhere in `src/` (a grep for `/ 1_000_000` over
  `kMicro` is part of review).

## Success Criteria

- [ ] `LadderScale.Micro` is the only `kMicro × P(Θ)` product in `src/`.
- [ ] The aptitude magnitude read is unchanged for every tested input.
- [ ] The atom-side movement is measured and listed (or shown empty).
- [ ] No spurious overflow below the true `long` range.

## Open Questions

None.

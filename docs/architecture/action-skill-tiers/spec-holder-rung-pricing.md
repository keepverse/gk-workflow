# Spec: holder-rung-pricing (ST2)

**Status: proposed 2026-09-18.** Module **ST2** of [action-skill-tiers-map.md](../action-skill-tiers-map.md).
No dependencies. Not approved; no build authorized.

## Objective

**One holder, one rung reading, bounded by the action's window.** Two defects in the same path:

### Defect A — the holder's rung ignores the window's ceiling

The ideal's windows say *who may hold which rung* (general 1–4, family 1–7, signature 1–10 as shipped).
Its own wiring-gap list names the missing piece: `UnlockLadder.EffectiveRung` is *"still 2-arg, no
`scopeMax`"* (ideal, Wiring gap). The code:

- `UnlockLadder.cs:71-77` — `EffectiveRung(earnCount, tuning) = min(earnCount, rungCap)`. No window.
- `BattleRunState.cs:636-649` — `EffectiveRungOf` returns that value for a held action, the authored
  `Rung` otherwise.

So a general action (authored window `[1,4]`) held by a holder with `earnCount = 9` is priced at rung 9.
The window bounds structure (the authored `Rung` is the window ceiling, `ActionCorpusComposer.cs:57-58`,
read by `StructureBudgetGuard.cs:41`) but **not** cost or `qPower`. The ideal states the opposite
(map C-1); the code is what is true.

The ideal also names the shape to copy: the item program's **collapsing envelope**,
`maxTier = min(band.Max, ceiling(ilvl))` (`DropEnvelope.cs:46` via `IlvlTierLadder.Envelope`),
*"applied to rung windows for actions"*. For a holder that is
`effectiveRung = min(earnCount, rungCap, window.Ceiling)`.

### Defect B — cost is scaled by a rung twice

- `ActionCompiler.cs:61` — every compiled cost is pre-scaled by the **authored** rung's `CostMulti`.
- `BattleRunState.cs:602` — that pre-scaled amount becomes the ledger's cost row.
- `CostLedger.cs:148-155` — the ledger scales it **again** by `rungOf(actor, action)`: the holder's
  effective rung, or the authored rung when the holder has none.

`spec-cost-scaling-holder-rung.md` §Objective is explicit that cost must follow the **holder's** rung.
Instead it follows `authored × holder`. At the shipped table the fallback path (every non-held action,
which is every action in production today — see below) pays `costMulti²`: rung 4 `2628‰ → 6906‰`,
rung 7 `6907‰ → 47706‰`, rung 10 `18151‰ → 329458‰` (`action-rungs.v1.json`). The existing A23
tests did not see it because their fixture action is authored at rung 1, where `costMulti = 1000`
(`ActionCostsCooldownsAdoptionTests.cs:30,47,134`).

### Production reach, stated honestly

`BattleEngine.Resolve`'s `unlockStateFor` has **no production caller** — only
`ActionCostsCooldownsAdoptionTests.cs:308,313` pass it. So in production **defect B is live** (every
costed action with authored rung > 1 goes through the fallback and is double-scaled) and **defect A is
inert** (no holder reaches `EffectiveRung` in a real battle). This module fixes the function; wiring
holders into production battles belongs to the action program (A26–A32), not here.

## Contract

1. **`UnlockLadder.EffectiveRung(long earnCount, UnlockTuning tuning, RungBand? window)`** returns
   `min(earnCount, rungCap, window.Ceiling)` when `window` is present, `min(earnCount, rungCap)` when it
   is `null`. The existing two-argument form delegates with `null`, so every current caller is
   unchanged. Still **one function, one input curve** — the window is a bound on it, not a second curve.
2. **A `null` window means no bound.** Actions authored before A-E1 carry no `RungBand`
   (`ActionRow.cs:108`); bounding them by their authored rung would change A23's shipped behaviour
   (a holder earning past rung 1 pays more, `ActionCostsCooldownsAdoptionTests`). They stay unbounded.
3. **No floor.** A-U1 dropped the floor (`spec-rung-semantics.md` §3.2) and R7 (2026-09-18) confirmed
   every window starts at 1 (*"a floor of 5 is a hidden tax on a first unlock"*). The window's `Floor` is
   not read here.
4. **The window reaches the battle.** `CompiledAction` gains `RungBand? RungBand` (default `null`),
   copied from `ActionRow.RungBand` by `ActionCompiler`. `BattleRunState.EffectiveRungOf` — made the
   **one instance resolver** shared by `CostLedger` and the hit by `action-enrich`'s `action-base`
   (`spec-action-base.md` §Which rung) — passes the band of the row the actor holds. Whichever of the
   two modules lands first creates that instance method; the second adds only its own line to it (the
   band here, the held-row fallback there). No new vocabulary, no `tier` field (ruling 1) — the band
   already exists on the row.
5. **Cost is scaled at exactly one place: `CostLedger`.** `ActionCompiler` stops pre-scaling
   (`ActionCompiler.cs:59-61`); `CompiledActionCost` carries the authored amount (field renamed from
   `ScaledAmount` to `Amount` so the name stops lying). Its production reader is `BattleRunState.cs:602`;
   one test reads it too and asserts the **pre-scaled** amount (`ActionCatalogTests.cs:374-375`,
   `10 * 2000milli`) — a stale test once this contract lands, rewritten to assert the authored amount and
   moved nowhere else. The ledger applies the rung once, with `rungOf`'s reading, as A23 intended. This
   module is the **sole owner** of the pre-scale line; `action-enrich` does not touch `ActionCompiler`.
6. **`StructureBudgetGuard` is untouched.** It reads the authored rung and that is correct
   (`spec-rung-semantics.md` §3.1, §4).

## Why this is not a second curve

`DESIGN-GATE.md` §1 Actions row: *"rung is progression, never an action property, so a per-action power
difference is a second curve."* The bound here is not per action. The window is **per scope** — three
tunable values (ST3) — and the planner refuses a brief whose band differs from its scope's window
(`distribution_planner/derive.py:402-412`). The curve is still `min(earnCount, …)`; a scope ceiling is
the same kind of structural bound as `rungCap`, which `ssot-power-scale.md:888` already records as a
soft, tunable content window. Magnitude keeps growing through `P(Θ)`; only the rung multiplier stops at
the window.

## Interaction with action-enrich

`action-enrich` reads `qPowerMilli` as the action's damage base at the holder's **effective** rung,
through the same `BattleRunState.EffectiveRungOf` the ledger uses (resolved 2026-09-18, map §7). So this
module's window bound reaches the damage base with no further code, and cost and base can never read two
different rungs. This module does not change `qPowerMilli`'s values or meaning.

## Tunables

None new. Reads `rungCap` (`gk-core/data/tuning/action-unlock.v1.json:15`) and the rung rows' `costMulti`
(`data/tuning/action-rungs.v{n}.json`). The window ceilings are ST3's tunables, carried on each action
row by the generator.

## Numeric types

Rungs and window bounds are structural `int` indices in `1..cap`. `earnCount` stays `long` and the
`min` is taken before the narrowing `(int)` cast, as today (`UnlockLadder.cs:76`) — the result is bounded
by `rungCap`, so the cast cannot lose range. Cost arithmetic is unchanged (`CurveTable.ApplyMilli`),
now applied once instead of twice, which only lowers the magnitudes it produces.

## Seedsmith / generator

**No generator change.** Holder pricing is battle runtime. The window each action carries is the
`rungBand` index pair the planner already emits (`distribution_planner/derive.py:770`); ST3 owns where
those values come from.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~RungSemantics|FullyQualifiedName~UnlockLadder|FullyQualifiedName~CostLedger|FullyQualifiedName~ActionCostsCooldownsAdoption"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
python scripts\audit-overflow.py --targets A3
```

## Project structure

```
gk-core/src/FusionRpg.Core/Actions/Unlock/UnlockLadder.cs     (window-bounded EffectiveRung)
gk-core/src/FusionRpg.Core/Actions/CompiledAction.cs          (RungBand on CompiledAction; CompiledActionCost.Amount)
gk-core/src/FusionRpg.Core/Actions/ActionCompiler.cs          (copy the band; stop pre-scaling cost)
gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs           (pass the band; feed the unscaled amount)
gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs              (:112 comment names the renamed field)
gk-core/tests/FusionRpg.Core.Tests/Actions/ActionCatalogTests.cs  (:360-376 asserts the authored amount)
gk-core/tests/FusionRpg.Core.Tests/Actions/…                  (see Testing strategy)
```

## Code style

```csharp
/// <summary>ST2: min(earnCount, rungCap, window.Ceiling). The window is the scope's rung window the
/// action was authored for (A-E1) -- a bound on the one curve, never a second curve. A null window
/// (an action authored before A-E1) is unbounded, byte-identical to A23.</summary>
public static EffectiveRung EffectiveRung(long earnCount, UnlockTuning tuning, RungBand? window)
{
    // ... argument checks as today ...
    var ceiling = window is { } w ? Math.Min(tuning.RungCap, w.Ceiling) : tuning.RungCap;
    return new EffectiveRung((int)Math.Min(earnCount, ceiling));
}
```

## Testing strategy

| # | Test | Proves |
|---|---|---|
| 1 | Window `[1,4]`, `earnCount` above 4 → effective rung 4; below 4 → `earnCount` | Contract 1 |
| 2 | `null` window → `min(earnCount, rungCap)`, identical to the two-argument form for a spread of inputs | Contract 1, 2 |
| 3 | The window's `Floor` never raises the result (`earnCount = 1`, window `[3,10]` → 1) | Contract 3 |
| 4 | A held corpus action priced through a real `BattleEngine.Resolve` pays at `min(earnCount, ceiling)` | Contract 4 |
| 5 | A non-held action with authored rung `r` pays `base × costMulti(r)` once — **planted violation:** reinstating the compile-time pre-scale fails this test | Contract 5 |
| 6 | Existing `ActionCostsCooldownsAdoptionTests` stay green unchanged (authored rung 1, `null` band) | Contract 2 |
| 7 | `RungSemanticsTests`' guard-reads-authored test stays green unchanged | Contract 6 |
| 8 | `ActionCatalogTests` compile test asserts `Costs[0].Amount` equals the authored `ValueSpec`, not `× costMulti` | Contract 5 (stale test corrected to the contract) |

No test pins a `costMulti` value from the tuning file; expected costs are computed from the loaded row.

**Goldens.** Any battle golden that commits a costed action with authored rung > 1 **will move** (its
cost falls from `costMulti²` to `costMulti`); run `BattleGoldenTests` after the code change to find out
whether one does, and say so either way. A move is a defect fix: re-bless in a **separate commit** stating
the reason (tunables T7), after the code change is green on every non-golden test. This is **first** in the
cross-program re-bless order ST2 → ST1 → `action-enrich` `action-base` (map §7).

## Boundaries

- **Always:** keep `EffectiveRung` the one derivation; keep `CostLedger` the one scaling point.
- **Ask first:** giving `null`-band actions a bound (a behaviour change for A23's shipped actions); making cooldown follow the holder rung (timing
  reads the authored `cdMulti` at catalog build, `RpgStore.ActionCatalog.cs:126`, and the ideal does not
  ask for a change).
- **Never:** change what `StructureBudgetGuard` reads; add a third rung reading; wire `unlockStateFor`
  into production battles here (action program's); read the window's floor.

## Success criteria

1. A held action's effective rung never exceeds its window ceiling.
2. A cost is scaled by one rung reading, once.
3. Actions without a band behave exactly as today.
4. `StructureBudgetGuard` and its tests are unchanged.

## Self-audit (debate pass)

- *"Isn't defect B the action program's?"* It sits in A23's code, but no spec owns it — A23's spec
  describes the intended single scaling and its tests cannot see the double one. It is the same question
  this program exists for (which rung prices a holder), and fixing A without B would make the window
  bound invisible under a squared multiplier. SOLID S: one scaling point. Kept here, reported to the
  action program as a cross-program note in the map.
- *"Should the bound live in `BattleRunState` instead of `UnlockLadder`?"* No. `UnlockLadder.EffectiveRung`
  is the registered derivation (`ssot-power-scale.md` §10 row 19). A second place computing a bounded
  rung would be two derivations of one number.
- *"Is capping a general action's rung at 4 a hard progression ceiling?"* The ceiling is a published
  tunable (ST3), the same class as `rungCap`; magnitude keeps growing through `P(Θ)`. It is a window,
  not a wall — the ideal's own words.

## Open questions

None.

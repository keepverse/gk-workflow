# Spec: `action-base` — the hit's base comes from the action

**Program:** [`action-enrich`](../action-enrich-map.md). **Ideal:** [action-enrich-ideal.md](../action-enrich-ideal.md).
**Delivers:** the battle half of the spec `solid-enforcement` SE5.1 names (SE5.1 is marked done on these
specs' writing, `tasks/solid-enforcement-todo.md:313`).

## Objective

Today every attack-category action, rung 1 or rung 10, lands the same hit: `BaseOverlayDamage =
attacker.LiveAtk(state.Ledger)` (`BasicAttack.cs:369`), the actor's `atk`. The owner ruled `atk` redundant:
the design has power and defense, and the move owns its strength. After this module:

```
BaseOverlayDamage = basePowerMilli(action, effectiveRung) × P(Θ_attacker) / 1000
```

and everything downstream is unchanged — `EffectivenessMultiplier`, the hybrid element split with
per-element `combat.power.*` and the element matrix (`OverlayCombatCalculator.cs:99-178`), defense, crit,
and the action's `OnDamageDealt` effect chain.

**Acceptance:**
1. Every attack resolves a `long` base through one function, `ActionBaseDerivation.BasePowerMilli`: the
   basic attack from `gk-core/data/tuning/action-base.v1.json` (new), a skill or innate from `qPowerMilli` of the
   rung row at its holder's `effectiveRung`.
2. No base is authored per action row and none is stored on `CompiledAction`: the skill base is resolved
   at hit time through the **same** rung resolver the cost ledger uses (`BattleRunState.EffectiveRungOf`).
3. `BasicAttack.cs:369` reads the action's base × `P(Θ)`; no production damage path calls `LiveAtk(`.
4. Battle goldens are re-blessed **once for this module**, in its own commit, with the reason in the
   commit and the golden file's note, in the order the map's §Golden re-bless order fixes.

## Design

### Derivation — one function, no stored field

| `ActionKind` | Base (per-mille of `PowerMath.One`) |
|---|---|
| `Skill` / `Innate` | `RungRow(effectiveRung).QPowerMilli` (`RungRow.cs:25`) from the **loaded** rung table (`RungPolicy.Table`; `action-rungs.v1.json` today, the one ST5 version afterwards — `qPowerMilli` is identical in v1, v2 and every later version `action-skill-tiers` publishes) |
| `Basic` (`act.attack`, rung 0, `BasicAttackFactory.cs:41-42`) | `ActionBaseTuning.BasicAttackBasePowerMilli` from `action-base.v1.json` (new) |

```csharp
public static class ActionBaseDerivation
{
    /// The move's base. Basic reads tuning; a skill/innate reads its holder's effective rung row.
    /// A skill whose effective rung has no row throws naming the action -- never a basic fallback.
    public static long BasePowerMilli(ActionKind kind, string actionId, int effectiveRung,
        RungTable rungTable, ActionBaseTuning tuning) => kind switch
    {
        ActionKind.Basic => tuning.BasicAttackBasePowerMilli,
        _ => rungTable.TryGet(effectiveRung, out var row)
            ? row.QPowerMilli
            : throw new InvalidOperationException($"action '{actionId}': effective rung {effectiveRung} has no rung row"),
    };
}
```

**Why no `CompiledAction.BasePowerMilli` (corrected 2026-09-18, strengthen pass).** The first draft
stored a base for the basic attack and derived it "where `ActionCompiler` reads the rung row for
`CostMulti`" (`ActionCompiler.cs:61`). That line is `action-skill-tiers` ST2's seam (it removes the
compile-time cost pre-scale there), and a skill's base is resolved per hit anyway, so a stored field
would serve only the basic attack — and adding a field to `BasicAttackFactory.Create` moves its
field-level golden (`BasicAttackFactoryGoldenTests`) for nothing. This module therefore touches neither
`ActionCompiler` nor `BasicAttackFactory` nor `CompiledAction`. One owner per seam.

### Which rung — the resolver is made reachable at the hit site

`spec-rung-semantics.md` §3.1: the **authored** `Rung` fixes structure; the holder's **`effectiveRung`**
fixes *magnitude and cost*. The base is a magnitude, so it reads `effectiveRung` through the resolver
the cost ledger already uses.

**Code today:** `EffectiveRungOf` is a `static` private helper of `BattleRunState`
(`BattleRunState.cs:636-649`) and is reachable only as the `rungOf` closure captured inside
`CostLedger` (`BattleRunState.cs:611-612`, stored privately at `CostLedger.cs:47`). `unlockStateFor` and
`unlockTuning` are constructor parameters, not fields (`BattleRunState.cs:263`). So `ApplyBasicAttack`
(`BasicAttack.cs:327`, which holds `state`) **cannot** reach it. The change:

1. `BattleRunState` stores `unlockStateFor`/`unlockTuning` in two private readonly fields and exposes
   **one** instance method, `public int EffectiveRungOf(string actorKey, string actionId)`, whose body is
   the existing static helper.
2. The `CostLedger` construction passes that method group as `rungOf` — the ledger and the hit site call
   the **same** delegate. There is no second resolver, and `action-skill-tiers` ST2's window bound
   (which lands inside `UnlockLadder.EffectiveRung`, called from this method) reaches both at once.

**The fallback is A23's rule** (its source moves to the held row, below). A holder with no matching `UnlockState` entry — every intrinsic or
innate action, and every battle whose caller passes no `unlockStateFor` (all production battles today:
`BattleEngine.Resolve`'s `unlockStateFor` has no production caller, see the map's §Cross-program) — reads
the **authored** `Rung`, which is the scope window's ceiling (`ActionRow.cs:118`). Consequence stated
plainly: until holders are wired into production battles, a skill's base is its window ceiling's
`qPowerMilli`, and its cost scales by the same row. Base and cost stay paired because they share one
resolver.

### The read

```csharp
// BasicAttack.cs:369 — the one production read-site this module changes.
var held = state.HeldActionOf(attacker.Setup.Key, envelope.ActionId)   // from HeldActionsOf, never the catalog
    ?? throw new InvalidOperationException($"'{attacker.Setup.Key}' swung '{envelope.ActionId}', which it does not hold");
var basePowerMilli = ActionBaseDerivation.BasePowerMilli(
    held.Kind, held.ActionId,
    state.EffectiveRungOf(attacker.Setup.Key, envelope.ActionId),
    RungPolicy.Table, ActionBaseTuningHub.Tuning);
var theta = checked((int)attacker.Derived.Get(DerivedStatChannels.ProgressionPower));
// ... BaseOverlayDamage = ActionBaseMath.BasePerHit(basePowerMilli, BattleRuleset.PowerValue(theta)),
```

- **The action is the one the actor holds, not a catalog lookup.** The basic attack is hand-built and in
  no catalog (the comment at `BasicAttack.cs:333-336`); a catalog-less battle falls every equipped id
  back to it (`BattleRunState.cs:548-553`); siege `AdditionalHeldActions` are compiled rows that are not
  in any catalog (`BattleRunState.cs:586-587`, `ConstructionActions.cs:87-106`); a garrison lends a
  structure's actions (`HeldActionsOf`, `BattleRunState.cs:838-850`). `HeldActionsOf` covers all four, so
  the hit reads `Kind` from the row the actor actually swung (`BasicAttackCompiled` carries
  `ActionKind.Basic`, `BasicAttackFactory.cs:41`). `HeldActionOf(actorKey, actionId)` is a thin lookup
  over `HeldActionsOf`, not a second list. The category read at `BasicAttack.cs:337` keeps its own
  documented golden-preserving catalog fallback; this module does not change it.
- **The resolver's fallback reads the held row too.** `EffectiveRungOf`'s non-held fallback is
  `actionCatalog?.Get(actionId)?.Rung ?? 0` (`BattleRunState.cs:648`), which gives rung 0 for a held row
  that is not in the catalog (siege, lent). The instance method reads the fallback from the same held row
  (`held.Rung`) — byte-identical for every catalog action, since those held rows *are* the catalog's —
  so the derivation never sees a skill at rung 0. A skill that still resolves to a rung with no row
  throws, naming it.
- **`Θ` for magnitude is Hub output, not a setup field.** The draft named `Setup.ThetaActor ?? Setup.Index`
  and `BattleModels.cs:185-195`; that doc comment describes the **contest** side. The magnitude `Θ`
  battle already uses is the Hub channel `progression.power`: `BattleHubCompose.Compose` feeds
  `setup.ThetaActor ?? setup.Level` into the Hub through `FixedPowerIndexProvider`
  (`BattleHubCompose.cs:56-58`), `RpgProgressionSubsystem` writes it verbatim
  (`RpgProgressionSubsystem.cs:44-48`), and `CostLedger` already reads it that way (`CostLedger.cs:153`).
  Reading it from `attacker.Derived` keeps "one ActorHub compose / one read". The value is an integer carried as `double`; the narrowing
  is `checked` (numeric rule 4).
- **`P(Θ)`** through `PowerLadder.Value(int)` (`PowerLadder.cs:58`), cached exactly as
  `BattleRuleset.BaseHp` caches its ladder (`BattleModels.cs:337-338`). A `PowerValue(int)` sibling of
  `BaseHp` is the one addition; it is the same ladder (ssot-power-scale §10 row 20), not a new curve.

```csharp
public static class ActionBaseMath
{
    /// Magnitude, not a ratio: long, checked, divided by 1000 once, last (CLAUDE.md numeric rules 1-3).
    /// Both operands are already long, so the multiply is widened by construction.
    public static long BasePerHit(long basePowerMilli, long pTheta) =>
        checked(basePowerMilli * pTheta) / PowerMath.One;
}
```

### What leaves

- `LiveAtk` (`BattleEngine.cs:101`) stops feeding damage; its one damage caller is `BasicAttack.cs:369`.
  Deleting `BattleActorSetup.Atk` (`BattleModels.cs:43`), `LiveAtk` and the `atk` channel is
  `solid-enforcement` SE1.7's, not this module's. `BattleHubCompose.cs:83,89` keeps passing `setup.Atk`
  into the Hub baseline until SE1.7.
- A `stat.modify` on `atk` (the ledger path `LiveAtk` composed) no longer changes damage. If shipped
  content grants an `atk` modifier, the build task lists it by id and hands it to `solid-enforcement`
  SE1.6 (`retire-atk` R5, the owner of regenerating generated content — `tasks/solid-enforcement-todo.md:116`),
  never an edit to generated JSON and never a second routing fix here.

### Power-ladder registration

`qPowerMilli` becomes a direct damage multiplier on `P(Θ)`. `ssot-power-scale.md` §10 lists the unlock
ratchet that picks the rung (row 19) and the ladder itself (row 20) but has **no row for the rung table's
`qPower(r)` quality ladder** (§10.2 rows 7-37, read 2026-09-18). The build owes one §10.2 row, written
with the power program's review (the file is theirs): *"Action rung quality ladder `qPower(r) =
1.75^((r-1)/2)`, 10 rows, bounded at the rung cap (×12.4) — relative, level-free, multiplies `P(Θ)` exactly
once at the hit; the rung it reads is row 19's `effectiveRung`"*, same shape and reasoning as row 7.
This is also the answer to `DESIGN-GATE.md` §1 Actions row (*"a per-action power difference is a
second curve"*): the difference is read at the **holder's** rung through the one resolver, from an
already-shipped table, not authored per action.

## Seedsmith / generator

**No seedsmith stage changes, by construction.** An action seed names its rung window through
`rungBand` (a table index, `RungBand.Collapse()` → ceiling, `ActionRow.cs:118`), and the base derives
from the holder's `effectiveRung` of that action at hit time. The seed gains no field, so P1 (*the model
writes identity; deterministic code writes magnitude*) holds without touching `audit_schema`.

| Stage | Change | Why |
|---|---|---|
| `distribution_planner` (assigns `rungBand`) | none | its output already bounds the base |
| `general/family/signature` propose (A-P1..3) | none | no number enters a prompt or a seed |
| `validate_heal` | none | a seed whose rung has no `RungRow` is already rejected at load |
| `innate_picker` | none | innates derive from their rung like any skill |
| `authored-basics.json` (hand-authored, not generated) | none | the basic attack's base lives in `action-base.v1.json`, not in the seed |

**Regeneration is not required.** If a later pass wants a per-action base beyond the rung, the change
goes into the generator and its tuning, then a regenerate — never an edit to generated JSON.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionBase"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGoldenTests"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionCostsCooldownsAdoption"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~ActionBaseNoAtkRead"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
python scripts\audit-overflow.py --targets A3
python scripts\audit-magic-numbers.py --summary
python gk-core/scripts/guard-actor-hub.py
```

## Project structure

```
gk-core/data/tuning/action-base.v1.json                              (new, authored once) basicAttack.basePowerMilli + _meta
gk-core/src/FusionRpg.Core/Actions/ActionBaseTuning.cs               (new) record + loader + ActionBaseTuningHub (LawnAttritionTuningHub shape)
gk-core/src/FusionRpg.Core/Actions/ActionBaseDerivation.cs           (new)
gk-core/src/FusionRpg.Core/Actions/ActionBaseMath.cs                 (new)
gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs                  EffectiveRungOf becomes the one instance resolver; CostLedger receives it
gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs                     :369 read
gk-core/src/FusionRpg.Core/Battle/BattleModels.cs                    BattleRuleset.PowerValue(int) beside BaseHp (same cached ladder)
gk-core/src/FusionRpg.Server/Program.cs                              ActionBaseTuningHub.Configure at startup
tests/FusionRpg.Core.Tests/ContractTuningTestBootstrap.cs    configure the hub from the real file for Core tests
gk-core/tests/FusionRpg.Core.Tests/Actions/ActionBaseTests.cs        (new)
gk-core/tests/FusionRpg.Guard.Tests/…ActionBaseNoAtkReadTests.cs     (new)
```

`gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` configures the same hub; that line is `lawn-action-base`'s.

## Code style

Match `LawnAttritionTuningHub` (`LawnAttritionTuning.cs:29`; configured once at host startup, throws
when unconfigured, no built-in default) and `ActionTimingDerivation` (pure, tuning in, value out,
overflow comment on the multiply).

## Testing strategy

| Case | Expect |
|---|---|
| Skill held at effective rung `r` | base `== RungRow(r).QPowerMilli` for every row of the loaded table — read from the table, never a literal; a held unlock whose `effectiveRung` differs from its authored `Rung` uses the effective one |
| Non-held skill (no `unlockStateFor`) | base `==` the authored rung's `QPowerMilli` — the A23 fallback, same row the cost ledger reads for the same action in the same battle |
| One resolver | a test double counting calls proves `CostLedger` and the hit site both call `BattleRunState.EffectiveRungOf`; **planted violation:** a hit site computing its own rung fails it |
| Basic attack | base `==` the tuning value, read from the loaded file |
| Envelope the actor does not hold | throws naming the actor and action — never the basic base |
| Held row absent from the catalog (siege `AdditionalHeldActions`, a lent garrison action) | the resolver's fallback reads the held row's `Rung`; for every catalog action the result is byte-identical to today's `actionCatalog.Get(id).Rung` |
| Two same-category actions, effective rungs 1 and 9, one attacker, one defender | the rung-9 hit's `BaseOverlayDamage` is strictly larger; the ratio equals `qPower(9)/qPower(1)` read from the table |
| `Θ` source | `BaseOverlayDamage` follows `attacker.Derived`'s `progression.power`: two setups differing only in `ThetaActor` give bases in the ratio `P(Θ₁)/P(Θ₂)` |
| Hybrid attacker (two element components) | the per-element split and matrix still apply to the new base — same `ElementPayload` path, asserted through `OverlayCombatCalculator`, not re-derived |
| Effect chain | an `OnDamageDealt` rider on the action still fires on a landed hit (`BasicAttack.cs:380-406`) |
| Large `Θ` | `BasePerHit` at a `Θ` whose `P(Θ)` × base exceeds `int` stays exact in `long`; an overflow of `long` throws |
| Unconfigured tuning hub | throws, naming the file |
| Guard (source scan) | no file under `gk-core/src/FusionRpg.Core/**` calls `LiveAtk(` except its own definition (`BattleEngine.cs:101`); allowlist exactly that one line, retired by SE1.7 |
| Goldens | re-blessed once for this module; the re-bless commit names this module and the reason |

Tests assert contracts and table joins. None pins a tuning value or a damage number.

## Tunables

| Key | File | Unit |
|---|---|---|
| `basicAttack.basePowerMilli` | `gk-core/data/tuning/action-base.v1.json` (new) | per-mille of `PowerMath.One` |
| `qPowerMilli` per rung | `data/tuning/action-rungs.v{n}.json`, the version `RungPolicy.Table` loads (existing, unchanged) | per-mille |

`action-base.v1.json` is authored once as a new domain's first version (as every domain's v1 is); every
later change is `gk-core/tools/tuning/publish.py action-base …` → `v{n+1}`. It ships **stated untuned** in its
`_meta`, naming the event that tunes it (the A20 synthetic-loadout sweep once the action program's
holder wiring lands — map §Cross-program). Its first value is chosen so the basic attack's base is
close to the median `Setup.Atk` of the battle goldens' own actors, so goldens move by the re-bless and
not by a balance swing; the build task records how that value was measured.

> **Erratum (2026-09-19, orchestrator ruling).** The first draft of the measurement above divided the
> median golden `atk` by `P(20)` (`power-scale` `curve.pinValue`). **A calibration ratio must be taken
> at the same Θ as the value it came from**, and the median `Setup.Atk` (30) is a Θ≈5 value: the base is
> `30 / (P(5)/1000) = 30/0.215 = 139.5 → 140`, not `30 / (P(20)/1000) = 44`. Dividing a Θ≈5 atk by
> `P(20)` mixes two ladder points, which is the internal inconsistency behind the first shipped number.
> One scalar still holds across the band because the `atk` channel and the HP ladder are both
> projections of the same power curve (`BaseAtk(20)/P(20) = 135.3`, `BaseAtk(1)/P(1) = 141.5`). The
> shipped `gk-core/data/tuning/action-base.v2.json` (`AE1.4`) carries `140`; it stays **untuned** and the A20
> sweep after `T74` retunes it.

## Boundaries

- **Always:** one derivation function; one rung resolver shared with `CostLedger`; `Θ` from Hub output;
  `long` magnitude math; tuning changes through `gk-core/tools/tuning/publish.py`.
- **Ask first:** changing `qPowerMilli`'s meaning or values (shared with `action-skill-tiers`).
- **Never:** keep `LiveAtk` feeding damage beside the new base; a per-mode base table; a model-chosen
  number; editing generated seed JSON; putting the base into the ActorHub fold (it is the move's, not
  the actor's); a second rung resolver; touching `ActionCompiler.cs:61` (ST2's seam).

## Success criteria

The four acceptance items above, `verify-change.ps1` green for the changed paths, `guard-actor-hub.py`
green, overflow and magic-number audits at 0, the §10.2 row written.

## Open questions

None. The lawn half is [`spec-lawn-action-base.md`](spec-lawn-action-base.md).

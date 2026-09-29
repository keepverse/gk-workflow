# `CAI2.3` — the profile→`ActionOption` projection: a candidate answer, derived from the code

Lane `cai3` (session `combat-ai-3`), 2026-09-23. `CAI2.3`'s ERRATUM 1 asks who owns the projection from a
`CombatAiProfile` into `Predictor.ActionEconomy.Options` and what the mapping is. This is not a decision
taken — it is the derivation offered so the owner's erratum becomes a yes/no instead of an open design.

## The derivation

`ActionSchedule.ActionOption` is `(Id, Priority, DamageMultiplier, CostResourceId,
CostShareOfOutputMilli, ReserveFloorMilli, MinTargets)` (`ActionSchedule.cs:63-67`). Filling it from a real
profile takes **three** inputs, and the profile is only one of them:

| Field | Source | Evidence |
|---|---|---|
| `Id` | module 16's compiled held list | `CompiledAction.ActionId` |
| `Priority` | the same list's index | `LawnHeldActionSets` sorts once by `ActionTagPreference.Compare` (`LawnHeldActionSets.cs:195`); `BattleRunState` uses the SAME comparison (`BattleRunState.cs:681`), so the two compile paths cannot disagree |
| `CostResourceId` | the action's own cost row | `CompiledAction.Costs` |
| `CostShareOfOutputMilli` | **the ledger**, at the actor's `EffectiveRungOf` | `CostOf(a, base) = NominalOutput(a, base) * (CostShareOfOutputMilli / 1000)` (`ActionSchedule.cs:79`), so the share is `1000 * cost / nominalOutput`; the cost read has a precedent — `ReserveFloorAffordability.ActionCostOf`, "a read the composer supplies from the same authority" (`ReserveFloorAffordability.cs:44,65`) |
| `DamageMultiplier` | **the base derivation**, at the same rung | `ActionBaseDerivation`; the ideal's §6.1 step 2 names it for the kill/value terms (`combat-ai-ideal.md:312`) |
| `ReserveFloorMilli` | **the profile** | `AiReserveFloor(ResourceId, FloorMilliOfMax)` → the option's per-resource floor |
| `MinTargets` | **the profile** | `AiWasteGuards.MinTargetsForArea` (`CombatAiProfile.cs:79` projects the guard block positionally) |

And the profile's `AiActionFilter(Tags, Families, RungAtLeast, RungAtMost)` (`CombatAiProfile.cs:48-51`) is
what SELECTS which held actions become options at all.

**So the profile contributes selection plus two bounds, and nothing else.** Measured: it carries no cost
and no multiplier — which is precisely the fact ERRATUM 1 turns on, and why "the mapping is not mechanical"
was true of the profile *alone* and false of the composition.

## What that implies for ownership

The projection is a composition of a real loadout, the profile and the ledger — the shape `BattleRunState`'s
compile loop and the composition root already own. That points to **module 14's re-fit (`CAI3.6`)**, not to
this analytic twin, whose own contract is "the model follows the core policy" and which must not become a
second place a loadout is priced.

- **If the owner rules that way**, `CAI2.3`'s acceptance line 7 should be struck and the projection moves
  into `CAI3.6`'s one-cause commit.
- **If the owner rules the other way**, the seven-field table above is the mapping to implement, and it is
  mechanical given the three inputs.

## Verified

| Criterion | Command | Result |
|---|---|---|
| `ActionOption`'s exact members and the share formula | `grep -n "record ActionOption" -A 14 gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs` | `(Id, Priority, DamageMultiplier, CostResourceId, CostShareOfOutputMilli, ReserveFloorMilli, MinTargets)`; `CostOf` = nominal output × share/1000 |
| The cost read precedent exists | `grep -rn "ActionCostOf" src/ --include=*.cs` | `ReserveFloorAffordability.cs:44,65,74,86` — a delegate the composer supplies |
| The base derivation exists | `grep -rln "ActionBaseDerivation" src/ --include=*.cs` | `Actions/ActionBaseDerivation.cs`, `CoreIntentPolicy.cs`, `BasicAttack.cs` |
| The preference order is shared, not re-invented | `grep -rn "ActionTagPreference.Compare" src/ --include=*.cs` | `BattleRunState.cs:681` and `LawnHeldActionSets.cs:195` — the same comparison in both compile paths |
| The profile's filter/bounds are as stated | `grep -n "record AiActionFilter" -A 6 gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfile.cs` | `(Tags, Families, RungAtLeast, RungAtMost)` |

## NOT proved

- **No code changed**, so no build or test was run for this note.
- **The mapping was not implemented or executed.** It is derived from reading the types on both sides; a
  first implementation is where a wrong assumption would surface (e.g. whether `CostLedger` exposes a
  per-resource read for an arbitrary action id, which was not checked — `ActionCostOf`'s own doc says the
  composer supplies it, and no composer does yet).
- **`DamageMultiplier`'s exact derivation was not read in `ActionBaseDerivation`.** The ideal names it for
  the kill/value terms; whether its output is already a multiplier against `baseDamage` (which is what
  `ActionOption` wants) or an absolute damage figure is the one field a first implementation must check.

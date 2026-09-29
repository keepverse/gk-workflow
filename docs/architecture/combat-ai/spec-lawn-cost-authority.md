# Spec: `lawn-cost-authority` (combat-ai module 17)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `lawn-held-actions` (module 16) · **Unblocks:** `lawn-cast-activation` (module 18) ·
**Status:** **part built** (CAI4.4, 2026-09-20; `CAI4.5`'s Core half 2026-09-23, lane `cai2`). The one rung derivation landed — `Actions/Unlock/EffectiveRungResolver.cs`, with `BattleRunState.EffectiveRungOf` reduced to a delegation and exactly one code call site repo-wide. `CAI4.5`'s **Core half** also landed — `Actions/LawnCostRows.cs`, the union of basic-attack and held-action rows, with its tests in this spec's own path — while the lawn LEDGER's injector caller is still owed, blocked on the same `ActionCatalog` feed as `CAI4.3` (that file is marked in the Project-structure table below).

## Objective

**The lawn's cost ledger knows one action and one rung, and both are hardcoded.**

```csharp
// gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackCostCharger.cs:97-106
var costs = LawnBasicAttackCostRow.Build(template);
var ledger = new CostLedger(
    costsByActionId: costs,
    poolsFor: ptr => InjectorEntityRegistry.ResourcePools.GetOrCreate(ptr, DerivedFor(ptr), NowTick()),
    derivedFor: DerivedFor,
    rungOf: (_, _) => 1,
    nowTick: NowTick);
```

`costsByActionId` holds **only** the basic-attack rows (`:97`), and `rungOf` is `(_, _) => 1` (`:105`).
Battle's equivalent ledger is built from every held action's real rows
(`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:601-610`) and prices through the holder's rung
(`:614-619`, `rungOf: EffectiveRungOf`). The audit buckets this as a wiring gap and names the
consequence: *"Otherwise the lawn prices every skill at rung 1, a second cost behaviour"*
(`../research/combat-ai/AUDIT.md:55`). The ideal restates it (`../combat-ai-ideal.md:136`).

**The cost is real, not cosmetic.** `CostLedger.ScaleCost` multiplies by the rung's `costMulti`
(`gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs:148-156`), and `action-rungs.v4.json` rung 1 is
`costMulti: 1000` — the inert row. A rung-7 skill cast on the lawn would therefore be charged as if it
were rung 1, while the same skill in a battle pays the real multiplier. One action, two prices,
decided by which place you are standing in. That is a mode owning a mechanism
(`battle-engine-ssot.md:64`), and it is the thing this module closes.

A second, smaller defect is closed at the same time and for the same reason: today's
`derivedFor: DerivedFor` (`:63,101`) is `InjectorStatusBridge.ResolveDerived` with no cache, reached
once per gate-3 check — *"exactly the 'uncached resolve' the perf audit blames"*
(`../combat-ai-ideal.md:161`).

**This module does not change basic-attack charging.** That is the hard boundary, and §"The shape"
states exactly how it is kept — including one live throw hazard that a naive fix would introduce.

## Tech stack

`FusionRpg.Core` (the shared rung-fallback resolver, extracted, Unity-free) and
`FusionRpg.Injector` (the lawn ledger's construction). No new dependency; `CostLedger`,
`UnlockLadder` and `RungPolicy` are all existing shipped types and none of them changes shape.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~EffectiveRung|FullyQualifiedName~UnlockLadder|FullyQualifiedName~CostLedger|FullyQualifiedName~LawnCostAuthority"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session backlog-clean-up-20260920
python gk-core/scripts/guard-actor-hub.py ; python gk-fusion/scripts/guard-single-writer.py
python scripts\audit-overflow.py --targets A3
```

No tuning publish: no new tunables (see below).

## Project structure

| File | New / changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Core/Actions/Unlock/EffectiveRungResolver.cs` | **new — landed (CAI4.4)** | The rung fallback chain, extracted so one derivation serves battle and the lawn |
| `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` | changed | `EffectiveRungOf` (`:668-685`) delegates to the extracted resolver; byte-identical |
| `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackCostCharger.cs` | changed | The ledger takes union rows, a real `rungOf`, and a cached `derivedFor` (`:97-106`) |
| `gk-core/src/FusionRpg.Core/Actions/LawnCostRows.cs` | **new — landed (CAI4.5, the Core half)** | The union itself: a pre-existing key's row list passes through BY REFERENCE, so "the basic attack's rows are unchanged" is a property of the function, not of a caller's copy. The row's own Files list put this in the Injector while putting its test in this Core project, which cannot reference the injector — resolved by building it here |
| `src/FusionRpg.Injector/Effects/LawnCostRowSource.cs` | **new; does not exist yet** | Builds the held-action rows from module 16's sets, in `BattleRunState.cs:601-610`'s shape |
| `gk-core/tests/FusionRpg.Core.Tests/Actions/EffectiveRungResolverTests.cs` | **new — landed (CAI4.4)** | Parity with today's battle behaviour, plus the lawn floor |
| `gk-core/tests/FusionRpg.Core.Tests/Actions/LawnCostAuthorityTests.cs` | **new — landed (CAI4.5, the Core half)** | Union rows, basic-attack invariance (5 cases) |

## The shape

### 1. One ledger, two row sources — never a second ledger

`costsByActionId` becomes the **union** of:

- the basic-attack rows exactly as today, from `LawnBasicAttackCostRow.Build(template)` reading
  `action-corpus-cost-templates.v2.json` (`LawnBasicAttackCostCharger.cs:78-97`); and
- one `ActionCostRow(actionId, resourceId, amount, when)` per `CompiledActionCost` on every action in
  module 16's held sets — **the same construction `BattleRunState.cs:601-610` performs**, copied as a
  shape, not as a second authority.

`CostLedger.RowsFor` is keyed by `actionId` and filtered by timing
(`gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs:67-77`), so adding keys **cannot** change the rows any
existing key returns. That is the mechanical guarantee behind "basic-attack charging unchanged", and it
is a property of the data structure rather than a promise.

One `CostLedger` on the lawn, as there is one in a battle. `guard-actor-hub.py` and the
`LawnBasicAttackCostCharger` class doc's own claim — *"the SAME `CostLedger`/`LawnBasicAttackCostGate`
types battle uses… Never a second cost authority"* (`:13-16`) — stay true, and become true of held
actions too, which today they are not.

### 2. `rungOf` becomes the real resolver, extracted once

Battle's resolver is an instance method with a documented fallback chain
(`BattleRunState.cs:668-685`):

```csharp
// BattleRunState.cs:671-684, as shipped
var state = unlockStateFor?.Invoke(actorKey);
if (state is not null && unlockTuning is not null)
    foreach (var held in state.Held)
        if (held.UnlockId == actionId)
        {
            var band = HeldActionOf(actorKey, actionId)?.RungBand;
            return UnlockLadder.EffectiveRung(held.EarnCountAtAcceptance, unlockTuning, band).Value;
        }
return HeldActionOf(actorKey, actionId)?.Rung ?? actionCatalog?.Get(actionId)?.Rung ?? 0;
```

**Copying this into the injector would be a second derivation of one number — a SOLID S defect, and
exactly the shape `holder-rung-pricing`'s own self-audit refuses** (*"A second place computing a bounded
rung would be two derivations of one number"*,
`../action-skill-tiers/spec-holder-rung-pricing.md:196-198`). So the chain is **extracted** to
`EffectiveRungResolver` in `Core/Actions/Unlock/`, taking its four inputs as parameters:

```csharp
public static int Resolve(
    string actorKey, string actionId,
    Func<string, string, CompiledAction?> heldActionOf,
    Func<string, UnlockState>? unlockStateFor, UnlockTuning? unlockTuning,
    ActionCatalog? actionCatalog, int floorWhenUnknown);
```

`BattleRunState.EffectiveRungOf` becomes a one-line delegation passing
`floorWhenUnknown: 0` — its shipped value (`:684`'s `?? 0`) — so battle is **byte-identical**.
`UnlockLadder.EffectiveRung` is untouched: it remains the registered derivation
(`ssot-power-scale.md` §10 row 19, per `../action-skill-tiers/spec-holder-rung-pricing.md:196-198`).
Only the *fallback chain around it* moves, and it moves into one place rather than two.

Code beats docs here, and it is worth stating: `holder-rung-pricing` (ST2) reads **"proposed
2026-09-18… no build authorized"** (`../action-skill-tiers/spec-holder-rung-pricing.md:3`), but its
contract 4 — the `RungBand` reaching `EffectiveRung` through one instance resolver — is **already in the
shipped code** at `BattleRunState.cs:708-709`, and `BattleRunState.cs:702` names ST2 by number. So
the lawn can call the shipped chain today; this module does not wait on ST2's approval and does not
re-decide anything ST2 owns.

### 3. ⚠️ The floor, and the live throw it prevents

`CostLedger.ScaleCost` **throws** when the rung has no row:

```csharp
// gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs:150-151
if (!RungPolicy.Table.TryResolve(rung, out var multipliers))
    throw new ArgumentOutOfRangeException(nameof(rung), rung, "no rung row for this action's rung");
```

`gk-core/data/tuning/action-rungs.v4.json` has `cap: 10` and rows `1..10`. **There is no row 0.**

The basic attack is deliberately **not** in module 16's held registry
(that module's own boundary), and the lawn supplies no `ActionCatalog`. So a naive `rungOf` that simply
called the battle chain would return `0` for the basic-attack id — and `TryPay` on the very next lawn
swing would throw, which `ShouldApplyRider` catches and turns into a fail-closed charge failure
(`LawnBasicAttackCostCharger.cs:153-157`), silently disabling the elemental rider for every actor.

**The lawn therefore passes `floorWhenUnknown: 1`**, with the reason in the code:

```csharp
// An action this lawn ledger has no held row and no catalog entry for prices at rung 1 --
// RungPolicy's own inert row (costMulti 1000). This is BYTE-IDENTICAL to the shipped
// `rungOf: (_, _) => 1` for the basic attack (LawnBasicAttackCostCharger.cs:105) and for every
// id the held registry does not know. Rung 0 has no row in action-rungs (cap 10, rows 1..10),
// so returning 0 here would make CostLedger.ScaleCost throw on every lawn swing.
```

A held action **does** have a row, so it prices at its authored `Rung` today, and at the holder's rung
the moment an unlock-state producer exists. The floor only catches the unknown case.

### 4. What the holder rung actually costs today — stated, not implied

`unlockStateFor` **has no production caller anywhere**, battle included: only
`ActionCostsCooldownsAdoptionTests` passes it
(`../action-skill-tiers/spec-holder-rung-pricing.md:46-49`). So on the lawn, from day one:

| Case | Price |
|---|---|
| A held action with an authored rung | its authored `Rung` — the same price battle charges today |
| A held action once an unlock-state producer exists | `min(earnCount, rungCap, window.Ceiling)` through `UnlockLadder.EffectiveRung`, with no further change here |
| The basic attack, and any unknown id | rung 1 — byte-identical to today |

The lawn ledger takes `Func<string, UnlockState>?` and it is `null` until a producer exists. **That is a
wiring gap, and the word is used on purpose**: the path is built end to end and one delegate is
unsupplied. Wiring holders into production belongs to the action program (A26–A32,
`../action-skill-tiers/spec-holder-rung-pricing.md:48-50`), not here.

### 5. `derivedFor` reads module 15's memo, and there is still only one reader

`CostLedger` takes exactly one `derivedFor` (`CostLedger.cs:54,61`), so the lawn cannot have a cached
one for decisions and an uncached one for swings. It gets **one delegate that is both**:

```csharp
// module 15's type, at gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnDerivedCache.cs (new; does not exist
// yet) -- NOT under Match/Ai/, for the folder-invariant reason spec-lawn-actor-view.md §Project
// structure states. Memo hit, else InjectorStatusBridge.ResolveDerived.
derivedFor: LawnDerivedCache.Resolve,
```

On a frame with no decision edge the memo is empty and every call is a pass-through — **byte-identical
to today's `DerivedFor`** (`LawnBasicAttackCostCharger.cs:63`). On a decision frame the memo is warm and
the N gate-3 checks of one decision share one resolve. One reader, one compose, consuming
`ActorHub.ResolveDerived`'s output (`gk-fusion/src/FusionRpg.Injector/Effects/InjectorStatusBridge.cs:18-24`) and
never folding it.

**`CostLedger.RowsFor`'s per-call `new List<ActionCostRow>` (`CostLedger.cs:72`) is not fixed here.**
It is module 7 `decision-perf`'s named task (`../combat-ai-map.md:47`), it affects every mode, and
fixing it in two places would fix it twice.

## Tunables

**None new.** The module reads three files that already exist, through the readers that already read
them:

| Value | File | Read by |
|---|---|---|
| basic-attack cost template | `gk-core/data/tuning/action-corpus-cost-templates.v2.json` | `LawnBasicAttackCostCharger.cs:79-82` (unchanged) |
| `costMulti` per rung | `data/tuning/action-rungs.v{n}.json` | `RungPolicy.Table` via `CostLedger.ScaleCost` (`:150-154`) |
| `rungCap` | `gk-core/data/tuning/action-unlock.v1.json` | `UnlockLadder.EffectiveRung` |

Two structural constants, each commented:

- `floorWhenUnknown = 1` on the lawn — the byte-identity guarantee above, not a balance number.
- `floorWhenUnknown = 0` in battle — the shipped value, preserved verbatim.

## Numeric types

Unchanged, and that is the point. A cost base is an `int` (`CompiledActionCost.Amount`), scaled through
`CurveTable.ApplyMilli` twice (rung, then the Θ seam) and returned as `long`
(`CostLedger.cs:148-156`). Rungs are structural `int` indices in `1..rungCap`
(`../action-skill-tiers/spec-holder-rung-pricing.md:105-108`). This module introduces no new magnitude
and no new multiply, so `audit-overflow.py --targets A3` should report no new finding — run it and say
so either way.

## Code style

- Build the ledger **once**, lazily, loud-once-on-failure, never retried — the shape
  `TryGetGate` already has (`LawnBasicAttackCostCharger.cs:71-120`), including its explicit refusal of a
  silently-vacuous gate (`:86-95`).
- Fail **closed**: a charge that could not run is not a free rider (`:156`).
- One derivation per number; a second place computing it is the defect, not the optimisation.
- Comment every structural constant with why it is structural (`tunables-ssot.md` §1).

## Testing strategy

Core, in memory.

| # | Test | Asserts the contract |
|---|---|---|
| 1 | `EffectiveRungResolver.Resolve` with `floorWhenUnknown: 0` matches today's `BattleRunState.EffectiveRungOf` over a spread of (held / not-held / catalog / no-catalog, with and without unlock state) | The extraction is byte-identical for battle |
| 2 | A held action with authored rung `r` and no unlock state prices at `r` | §4 row 1 |
| 3 | The same action with an unlock state holding `earnCount` prices at `min(earnCount, rungCap, band.Ceiling)` | The holder rung, once a producer exists |
| 4 | An id with no held row, no catalog and `floorWhenUnknown: 1` returns **1**, and `CostLedger.TryPay` for it does not throw | The floor and the throw it prevents |
| 5 | **Planted violation:** setting the lawn floor to 0 makes test 4 throw `ArgumentOutOfRangeException` | The hazard is real, and the guard is load-bearing |
| 6 | **Planted violation:** reinstating `rungOf: (_, _) => 1` makes test 2 fail for `r > 1` | The defect cannot silently return |
| 7 | Adding held-action keys to `costsByActionId` leaves the basic-attack id's rows and charged amount identical | Basic-attack charging unchanged, proven not argued |
| 8 | A held action's shortfall refuses that action and charges nothing; the next basic-attack swing still charges | Validate-all-then-consume (`CostLedger.cs:22-26`) across the union |
| 9 | `derivedFor` is invoked once per (actor, frame) across one decision's N gate checks; with an empty memo it is invoked per call exactly as today | The cache is an addition, not a behaviour change |

**Never asserted:** a `costMulti` value from the tuning file, how many actions carry costs, or any
authored action name — expected costs are computed from the loaded row, the rule
`../action-skill-tiers/spec-holder-rung-pricing.md:165` already states.

**Goldens.** No battle golden should move: the extraction is a delegation with the same inputs and the
same `floorWhenUnknown: 0`. `../action-skill-tiers/spec-holder-rung-pricing.md:167-171` warns that
*changing* the scaling moves goldens — this module changes no scaling, only where the fallback chain
lives. That is a claim to **test, not assume**: run
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` after the extraction
and state the result either way. If one moves, it is a defect in the extraction, not a re-bless.

## Boundaries

- **Always:** one `CostLedger` on the lawn; one rung derivation shared with battle; the union keyed by
  action id; the lawn floor at rung 1 with its comment; fail closed.
- **Ask first:** giving the lawn a real `unlockStateFor` producer (that is the action program's
  A26–A32 wiring and it changes live prices); making cooldown follow the holder rung — timing reads the
  authored `cdMulti` at catalog build and no spec asks for a change
  (`../action-skill-tiers/spec-holder-rung-pricing.md:176-179`).
- **Never:** copy `EffectiveRungOf` into the injector; add a second lawn ledger or a private price fold;
  change `ActionCompiler`'s pre-scale (that is ST2's sole ownership,
  `../action-skill-tiers/spec-holder-rung-pricing.md:76-77`); change what `StructureBudgetGuard` reads;
  fix `RowsFor`'s allocation here; change the basic attack's timing or its once-per-swing gate.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** Responsibility 6, *resource resolve and consume* — whose SSOT the
   register already names as `LawnActorResourcePools`, `ResourcePoolState`, `CostLedger`
   (`battle-engine-ssot.md:134`). No addition to the closed register.
2. **Decide or resolve (§3c)?** **Resolve.** Pricing is the engine's: §3c's own table puts *"which
   action to use"* on the AI side and *"cost, cooldown, effect, outcome"* on the engine's
   (`battle-engine-ssot.md:193`). The AI only asks affordability through `IAffordabilityCheck`.
3. **Mechanism or loop?** **Mechanism** — and the defect being closed is precisely a mode owning one
   (`battle-engine-ssot.md:68`: *"A mode may own its loop. A mode may never own a mechanism."*).
4. **Which existing implementation does it extend?** `CostLedger` (`CostLedger.cs:42`) and
   `UnlockLadder.EffectiveRung`, called rather than copied. The extraction moves battle's own fallback
   chain into a shared function that battle then calls — the opposite of `SiegeExpectedDamage`, the
   named anti-example (`battle-engine-ssot.md:266`).
5. **Does every mode get it?** Yes, after this module. Before it, the lawn was the one mode pricing
   differently — which is the §5 Q5 answer the page says to *"expect to be refused"*, and it is.
6. **Is it deterministic and seeded?** `nowTick` is `KernelDriveHost.NowTicks / 100`
   (`LawnBasicAttackCostCharger.cs:61,106`) — simulated, pause-respecting engine time, never the wall
   clock (`:30-36`). The only randomness is a spread cost's `AtomRng`, supplied by the caller
   (`CostLedger.cs:106,121`); `Check` is explicitly roll-free so it may be polled
   (`CostLedger.cs:79-81`).

## Success criteria

1. A held lawn action with authored rung `r > 1` is charged at `costMulti(r)`, not `costMulti(1)`.
2. Exactly one rung derivation exists in the repo; the lawn calls it and does not have its own.
3. The basic attack's charged amount, its once-per-swing gate and its observer hooks are unchanged,
   proven by test 7 rather than asserted in prose.
4. No lawn swing can make `CostLedger.ScaleCost` throw (test 4 + planted violation 5).
5. `derivedFor` resolves at most once per (actor, frame) during a decision, and behaves exactly as
   today on a frame with no decision.
6. No battle golden moves; the suite is run and the result stated.
7. `audit-overflow.py --targets A3` reports no new finding.

## Open questions

1. **Should the lawn's unknown-id floor be 1, or should unknown ids be refused outright?**
   Options: (a) floor at 1, byte-identical to today (recommended); (b) refuse an id with no held row,
   which would make the basic attack — deliberately absent from the registry — unchargeable and break
   the shipped rider. **Recommended default: (a)**, and (b) is only reachable if the basic attack is
   later given a held row, which module 16 explicitly rules out.
   **ANSWERED 2026-09-22 (lane `cai4`):** **option (a) taken, and it is pinned.** `EffectiveRungResolver.Resolve` carries
   `floorWhenUnknown` as a parameter (`CAI4.4`), and its suite pins the planted violation directly:
   floor **0** throws `ArgumentOutOfRangeException` for an uncatalogued id while floor **1** pays and
   `CostLedger.TryPay` does not throw. The lawn's own call site passing `1` is owed with `CAI4.5`
   (`gk-fusion/src/FusionRpg.Injector/**`).
2. **Cross-module note (module 7, `decision-perf`):** `CostLedger.RowsFor` allocates a `List` on every
   `Check` (`CostLedger.cs:105`), which is gate 3 of every decision in every mode
   (`../research/combat-ai/AUDIT.md:32`). It is deliberately not fixed here. The lawn's decision budget
   (module 19) is sized with that allocation still present, so module 7 landing later can only make the
   budget more comfortable, never less.
   **ANSWERED 2026-09-22 (lane `cai4`):** **module 7 landed.** `CAI1.14` precomputed the rows per `(actionId, timing)` at ledger
   construction - `rows.Count == 0` returns before any allocation - and `DecisionAllocationTests`
   measures a whole round at **zero bytes**. The budget this spec was sized against is now strictly
   more comfortable, which is what the note predicted.
3. **Cross-module doc-hygiene defect, owed to `action-skill-tiers`, not open here.** ST2's status line
   (`../action-skill-tiers/spec-holder-rung-pricing.md:3`) still reads *"proposed, 2026-09-18 … no
   build authorized"*, while its contract 4 — the `RungBand` reaching `UnlockLadder.EffectiveRung`
   through one instance resolver — is **visibly shipped** at `BattleRunState.cs:708-709`, which
   `BattleRunState.cs:702` names by ST2's own number. A reader who follows **this** spec's
   citation chain outward therefore hits a spec saying "not built" one hop from code that is built,
   and the natural conclusion — *"lawn-cost-authority depends on unapproved work"* — is false.

   **This is not a change to this spec, and it is not this spec's file to edit.** The owed edit is one
   line, by the `action-skill-tiers` program: change that status line to say contract 4 shipped (and
   when), keeping the rest of ST2's proposed scope as proposed. It is recorded here so the next change
   that touches `spec-holder-rung-pricing.md` carries it, per DESIGN-GATE's propagation rule — a
   correction that lands in one document and not its sibling has not landed.

   **What this module depends on, stated so the ordering is unambiguous:** the **code** at
   `BattleRunState.cs:708-709`, not ST2's approval. The extraction moves that shipped chain into
   `EffectiveRungResolver` and has battle call it; nothing here waits on, or pre-empts, any ST2
   decision (§2's Boundaries keep `ActionCompiler`'s pre-scale ST2's sole ownership).

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: resources/actor pools, actions & action costs, lawn.
[x] Session boundary: backlog-clean-up-20260920 (tasks/sessions/backlog-clean-up-20260920.json).
[x] I read every doc in the §1 row(s) this session: resource/actor-pool and action rows via
    spec-holder-rung-pricing.md (in full), battle-engine-ssot.md, overlay-control-loops.md,
    combat-ai-ideal.md, combat-ai-map.md, AUDIT.md, S4-lawn.md.
[x] I checked decisions.md: the "Action selection (battle adoption)" row (:44) and the "Battle engine
    is the SSOT" row (:53) both cover this; neither locks a lawn-local cost path, and :53 names a mode
    owning a mechanism as the defect class this closes.
[x] Every factual claim cites file:line, and every cited file was opened this session --
    including gk-core/data/tuning/action-rungs.v4.json, whose cap (10) and row set (1..10) were read, not
    assumed, because the floor argument depends on there being no row 0.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses.
[x] I verified claims against CODE, not comments: the rungOf literal, RowsFor's keying, ScaleCost's
    throw, BattleRunState's ledger construction and its fallback chain were each read.
[x] I read the surrounding section of every rule I quoted (battle-engine-ssot §2, §3c, §5 in full;
    holder-rung-pricing in full).
[~] I tested (not assumed) any constraint I am reporting. **Gap named honestly:** no suite was run in
    this spec session. The two constraints that matter -- "no golden moves" and "no new overflow
    finding" -- are written as commands to run with the result stated either way, not as results.
[x] Nothing contradicts a §2 invariant. Hot rules 1 and 3 hold: a failed charge is a fail-closed skip
    that is already caught (LawnBasicAttackCostCharger.cs:153-157), and nothing awaits.
[x] Corrections propagated: Open question 3 records the ST2 status-line drift rather than quietly
    relying on it.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. No test pins a costMulti value; expected costs are computed from the loaded row.
[x] Event-refreshed cache (§2.16): the only cache introduced is module 15's derived memo, whose
    invalidators that spec lists in full (frame edge, board-snapshot invalidation, actor-liveness
    revision) including its key-set edges (spawn, death). This module adds no cache of its own and
    copies no trigger set.
[x] No acceptance criterion fixes an ordering that can vary: test 8 asserts the basic attack still
    charges after a held-action shortfall, which is true in either order of arrival.
[x] Consumes Hub output only, via InjectorStatusBridge.ResolveDerived -> ActorHub.ResolveDerived
    (InjectorStatusBridge.cs:23). No second composer, no private fold. BattleStatComposer is not cited
    as precedent.
[x] Does not invent or extend a SOLID-violating parallel path: it REMOVES one (the lawn's private
    rungOf) by extracting a single shared derivation, and explicitly refuses to copy the chain.
[~] A new rule has a registry row. **Gap named honestly:** the rule "exactly one EffectiveRung fallback
    chain exists" would be guarded naturally by extending gk-core/scripts/guard-actor-hub.py's
    single-derivation family or by a new scan. Which one is a plan decision, unresolved here.
```

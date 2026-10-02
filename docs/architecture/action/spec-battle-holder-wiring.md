# spec-battle-holder-wiring — held unlocks reach real battles

**Status:** active · **Program:** `summoner-convergence` lane A (T74, id **A33**) · **Source:** `action-map.md` §17 A33 row
**Deps:** A26/T62 (`unlock-tuning-activation`) — without grants every `UnlockState` is empty and this is inert, though still correct.
**Read first:** [DESIGN-GATE.md](../../DESIGN-GATE.md) rows *Actions, skills, targeting, action costs* and *Anything that changes what happens in a BATTLE* · [battle-engine-ssot.md](../battle-engine-ssot.md) · [action-ideal.md](../action-ideal.md) §3.1/§3.5.

---

## 1. The defect

The engine can already price a held action at its holder's real rung; nothing in production asks it to.

| Piece | State |
|---|---|
| `BattleEngine.Resolve(..., Func<string, UnlockState>? unlockStateFor = null, UnlockTuning? unlockTuning = null, ...)` | built — `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs:229`, threaded to `BattleRunState` at `:270` |
| `BattleRunState.EffectiveRungOf(actorKey, actionId)` | built — public instance method at `:640`; `CostLedger` receives it as a method group at `:618` |
| `RpgStore.GetUnlockState(OwnerScope)` | built — `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActionUnlocks.cs:47` |
| `UnlockTuningPolicy.Tuning` | built, configured by the real host since A26/T62 |
| **A production caller passing the pair** | **absent.** `WebMatchService.cs:144/:211/:387`, `DelveBattle.cs:29`, `DistrictAssaultResolver.cs:174`, `SyntheticLoadoutHarness.cs:86` all omit it; only two Core tests supply one (`ActionCostsCooldownsAdoptionTests.cs:308,:313`) |

With no delegate, `EffectiveRungOf` takes its A23 fallback (`BattleRunState.cs:668-690`) and every held action reads its **authored** rung — the catalog's own value, which is not the holder's progression at all.

**Why that is a defect and not a default.** `action-ideal.md:283` fixes `rung(n) = min(earnCount, cap)`, and `:365` states the rule this breaks: *"One ladder, many readers, no private `f(source)`."* Rung **is** progression — it is the holder's earn history, not a property of the action row (`action-map.md` §1's own wording: *"rung is progression, never an action property"*). A battle that prices costs off the authored row is therefore reading a per-action constant where the design says the holder's ladder belongs, and two specimens holding the same `action_id` at different earn counts pay the same price. A26/T62 made level-ups grant real second actions; T74 is what makes those grants *mean* something once granted.

---

## 2. Design — the store-owning caller supplies the pair, Core declares the need

One rule: **whoever holds the store supplies the delegate; Core never learns about a store.**

That is not a new pattern — it is `DistrictAssaultResolver.HubInputsFor`'s own already-shipped inversion, documented in that file as *"Core declares the need and the Data layer injects the implementation at its own call site, which is dependency inversion rather than a layering exception"* (`DistrictAssaultResolver.cs:60-68`). T74 applies the same seam a second time, so nothing here invents a third mechanism.

### 2a. Data — one key→owner mapping, once

`RpgStore` gains the mapping so no caller re-derives it:

- `UnlockStateFor(BattleSetup setup)` — returns `Func<string, UnlockState>` over the setup's **squad** keys, resolving `BattleActorSetup.SpecimenId` → `new OwnerScope(OwnerKind.UniqueActor, specimenId)` → `GetUnlockState(...)`. A key that is not a squad actor, or a squad actor with no `SpecimenId` (a wave enemy, a structure, a non-player force), returns `UnlockState.Empty()`.
- `UnlockStateOf(string? instanceId)` — the single-owner form, for a Core seam that hands over one `InstanceId` at a time (`DistrictAssaultResolver`'s `HubInputsFor` shape).

`OwnerScope(OwnerKind.UniqueActor, instanceId)` is the owner the grant path already writes (`RpgStore.UniqueActors.cs:1610`, `TryRollActionUnlocks(db, instanceId, …)` at `:941`), so the read and the write agree by construction rather than by convention.

**No `ORDER BY`, no caching, no second table.** `GetUnlockState` is already the round-trip; this is a key-mapping helper over it.

### 2b. Server — the three web-match call sites

`WebMatchService`'s three `Resolve` calls (`:144` the stored replay, `:211` the second replay path, `:387` the fresh resolve every real match takes) each pass:

```csharp
unlockStateFor: _store.UnlockStateFor(setup),
unlockTuning: UnlockTuningPolicy.Tuning,
```

`UnlockTuningPolicy.Tuning` is `null` until a host configures it; `EffectiveRungOf` already treats a null tuning as "fall back to the authored rung", so a project that never configures it stays byte-identical.

### 2c. Core — the two resolvers take the delegate as a parameter

`DelveBattle.Run` and `DistrictAssaultResolver` are Core-only and statics-constructible; they may not read a store (`guard-dal.py`).

- `DelveBattle.Run` gains `Func<string, UnlockState>? unlockStateFor = null` and `UnlockTuning? unlockTuning = null`, passed straight through to `BattleEngine.Resolve`. Its one real caller, `DelveBattleSession.cs:179`, supplies them from the store it already holds.
- `DistrictAssaultResolver` gains `UnlockStateFor`/`UnlockTuning` **init properties**, matching `HubInputsFor` exactly — the Data layer injects them at the construction site beside it. The setup builder already resolves each member's `InstanceId` (`DistrictAssaultResolver.cs:415`), so the delegate is invoked per member there.
- `SyntheticLoadoutHarness`'s `LoadoutComparator.RunVariant` gains the same two optional parameters. It is a comparison harness, so its default (`null` on both) is the harness's documented behaviour: every run prices at the authored rung unless a caller asks otherwise.

### 2d. Battle-engine §5 — what this feature owes the engine

| # | Question | Answer |
|---|---|---|
| 1 | Which responsibility? | **8, the action system** — specifically action *cost*, already resolved by `CostLedger` + `EffectiveRungOf`. No new register entry |
| 2 | DECIDE or RESOLVE? | **RESOLVE.** Which rung a held action is at is a deterministic fact of the holder's persisted state, not a policy choice |
| 3 | Mechanism or loop? | **Mechanism.** One resolver (`EffectiveRungOf`), every mode. This spec adds no second rung read to any mode |
| 4 | Which existing implementation does it extend? | `BattleRunState.EffectiveRungOf` — the shipped one. Nothing is copied, and no mode gets its own rung math |
| 5 | Does every mode get it? | **Yes, by construction.** The seam is on `BattleEngine.Resolve`, so every mode that resolves through the engine can supply it; the callers that do are enumerated in §2b/§2c and every remaining one carries a comment saying why it does not |
| 6 | Deterministic and seeded? | **Deterministic.** The delegate reads a persisted row; the same `UnlockState` yields the same rung, so replay is unaffected. No clock, no ambient state, no RNG |

---

## 3. Acceptance

1. In a real-host battle (`RpgApiFactory`), a specimen holding a granted action above rung 1 pays cost at its **effective** rung, not the authored-rung fallback. **The test fails on pre-T74 code** — proven, not assumed.
2. An actor with no `UnlockState` row still reads the authored rung, byte-identical to today (the A23 fallback).
3. Every production `BattleEngine.Resolve` call site in §2b/§2c passes the pair, **or** carries a one-line comment saying why that battle has no holders.
4. Golden impact is **recorded**: goldens call `Resolve` directly with no delegate, so they are expected not to move. A moved golden is re-blessed in its own commit naming A33, never sharing a commit with a parent-H1 re-bless.

## 4. Non-scope, named

- **Not a cap.** The rung window (`min(earnCount, cap, window.Ceiling)`) is `action-skill-tiers` `ST2.4`'s; T74 supplies the seam it lands in and does not implement it.
- **Not a second cache.** No per-match memoization of `UnlockState`; `GetUnlockState` is the read, and a cache here would be a §2.16 edge-refreshed cache with its own trigger set to enumerate. Out of scope, deliberately.
- **Not the base.** After `action-enrich`'s `action-base`, a hit's *base* also reads the effective rung at `BasicAttack.cs:384`; that path is already written and needs no change here.

## 5. Verify

```
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BattleHolderWiring"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionCostsCooldownsAdoption|FullyQualifiedName~BattleGolden"
python gk-core/scripts/guard-dal.py
.\scripts\verify-change.py -Paths <files> -Session <session>
```

## 6. Structure

| File | Change |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActionUnlocks.cs` | `UnlockStateFor(BattleSetup)` + `UnlockStateForInstance(string?)` |
| `gk-core/src/FusionRpg.Server/WebMatchService.cs` | three `Resolve` call sites pass the pair |
| `gk-core/src/FusionRpg.Core/Delve/Battle/DelveBattle.cs` | two optional parameters, threaded |
| `gk-core/src/FusionRpg.Server/DelveBattleSession.cs` | supplies the pair to `DelveBattle.Run` |
| `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs` | `UnlockStateFor`/`UnlockTuning` init properties (the `HubInputsFor` idiom) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` | injects the siege provider beside `HubInputsFor` |
| `gk-core/src/FusionRpg.Core/Battle/SyntheticLoadoutHarness.cs` | two optional parameters |
| `tests/FusionRpg.Server.Tests/Actions/BattleHolderWiringTests.cs` | new — the real-host proof |

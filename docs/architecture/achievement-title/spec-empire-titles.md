# Spec: empire-titles

Module `empire-titles` (map: `docs/architecture/achievement-title-map.md`,
depends on `achievement-registry`, `reward-bundles`). Reading gate as registry
+ bundles + economy SSOT (loam throttle, upkeep, conduit), power scale §10/§11,
tunables, validation.

## Objective

Hall inventory + 3-slot multi-equip of empire titles feeding empire-scoped
magnitudes (yields, upkeep shares, conduit rates) through the economy path.
Users: empire/world-stage players. Success: loadout choices move the economy
measurably without double-scaling or ceilings. Every yield-raising title
carries a holding-scaled upkeep term (`upkeepShareMilli`) validated in the
Production/Pressure step — yield-only titles reject at load (economy P2:
territorial income needs territorial upkeep; loam stays the throttle).

## Tech Stack

C# net8 Server/Data (Hall, equip bindings) + economy steps
(Production/Pressure); FE Hall composition later via `/idea-ui`.

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj
Test: dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireTitle"
Guards: python gk-core/scripts/guard-dal.py
Verify: powershell -File scripts/verify-change.ps1 -Paths <changed> -Session <id>
```

## Project Structure

```
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireTitles.cs → Hall + bindings (NEW)
src/FusionRpg.Server/Empire/TitlesEconomy.cs       → single call site inside the
                                                     Production and/or Pressure step
                                                     (named at implement time; the P(Θ)-once
                                                     site) — never a second turn engine (NEW)
gk-core/tests/FusionRpg.Data.Tests/**/EmpireTitle*         → stacking/scale tests (NEW)
```

## Code Style

```csharp
// P(Theta) applied exactly once, at the Production/Pressure call site above.
// Loam flows are Theta-invariant (shares only); banked Tier-2 yields may read P(Theta).
// Per-mille shares divide last; checked.
var magnitude = ContentScale.Theta(theta) * shareMilli / 1000; // banked yields only
```

## Testing Strategy

xUnit: stacking (additive in-family, one-per-group cross-variant per explicit
`family`/`group`/`variant` membership columns owned by the title registry —
dual-family rows and unknown groups reject at load with per-row isolation);
3-slot capacity enforced as structural limit with T2 comment (capacity bounds
the Hall layout + binding-table shape — a correctness property, not a feel
dial); soft caps as configurable diminishing curves in tuning (never
`Min`/clamp); scale-once test on both legs (loam shares Θ-invariant, banked
yields `P(Θ)`); envelope/reconciliation tests, never row counts. Numbers
owned here: `equipShareMilli`, `stackRule`, soft caps, `seasonTurnWindows`
(relative turns — calendar seasons stay out of world scope).

## Tunables & Catalogs

`achievement-titles.v{n}.json`: `equipShareMilli` per family, `upkeepShareMilli`
per yield-raising title (required, holding-scaled), `stackRule`,
soft caps, `seasonTurnWindows` (relative turns). Display in catalog file. `hallSlots: 3`
structural (T2 comment: capacity bounds Hall layout + binding-table shape —
correctness, not feel), not a balance dial.

## Numeric Types

`long`, widen-before-multiply, per-mille divide-last, `checked` throw.
Conduit/yield rates reference existing §10 rows only — no new curve.

## ActorHub Gate

N/A — empire magnitudes are not actor numbers and never enter ActorHub. (Any
actor-facing side effect routes via actor-titles module.)

## Boundaries

- Always: economy steps own the math; loam stays the throttle; ledger dedupe.
- Ask first: new empire magnitude (needs §10 row review); the
  Production/Pressure insertion itself — provider-owned integration applied
  by the economy program from this spec's intent (never edited here).
- Never: ActorHub input for empire scope (composer abuse); hard ceilings;
  bankable grants from non-banking contexts; `const` balance numbers.

## Success Criteria

- [ ] 3-slot equip enforced; stacking/soft-caps behave per tuning.
- [ ] Scale-applied-once proven; harness measures net flow oscillating ~zero.
- [ ] Per-world feats re-earnable; no dead permanent unlocks of holdings.

## Open Questions

None (N=3 locked in ideal).

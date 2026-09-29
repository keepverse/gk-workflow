# Spec: reward-bundles

Module `reward-bundles` (map: `docs/architecture/achievement-title-map.md`,
depends on `achievement-registry`). Reading gate as registry + effect-atom
(container-schema, definitions units, atom-catalog pool rule), power scale,
economy P1/P2/P6, scoped-inventory SSOT, Funnel/single-writer guards.

## Objective

Turn unlocks into grants: fixed-core deterministic sets + weighted-pool draws
through the one existing roll path, fanned out to existing ownership roots.
Consumers: specimen FSM, item store, title registry. Success: seeded draws are
byte-identical on same inputs; pools never promise undrawable rows; every
faucet names its sink in the definition.

## Tech Stack

C# net8 Core (draw call site) + net8 Data/Server (grant fan-out); bundles are
modeled as `effect_container` rows with two new `container_kind` values
(`empire-title`, `actor-title`) via the Ask-first vocab path — no separate
bundle tables. Draws go through the one existing path (`TryInstantiate(container, lookupAtom, lookupAffix, rollSeed,
thetaContent, tuning, origin, catalogRevision)` / `InstanceProducer` compose,
owned by effect-pipeline module 4); this module is client-only. Bare-`Draw`
bundle paths are forbidden. Title mint stays blocked until the reviewed
vocab widening lands (convention + registry +
DESIGN-GATE atom row + `ParseKind` default-to-throw, all in the same change).

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj
Test: dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~RewardBundle"
Guards: python gk-fusion/scripts/guard-funnel-delta.py; python gk-fusion/scripts/guard-single-writer.py
Verify: powershell -File scripts/verify-change.ps1 -Paths <changed> -Session <id>
```

## Project Structure

```
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Achievements.cs  → bundle rows live in effect_container (registry spec)
data/seed/achievements/bundles/**                  → authored bundles (NEW)
gk-core/tests/FusionRpg.Core.Tests/**/RewardBundle*        → determinism tests (NEW)
```

No `BundleDraw.cs`, no `RpgStore.Bundles.cs` — a second roller/store is a
SOLID fork. Host injects loaded tuning/seed; Core reads no files.

## Code Style

```csharp
// No second roller: fixed core verbatim + pool via the existing instantiate path,
// which also owns the single ContentScale.Milli application (P(Theta)-once site).
TryInstantiate(container, lookupAtom, lookupAffix, rollSeed, thetaContent, tuning,
    out var instance, origin, catalogRevision); // fan-out never rescales
```

## Testing Strategy

xUnit: byte-identity is `(containerId, container.revision,
affixCatalogRevision, PowerTuning version, rollSeed, content Θ, origin,
stream-name set, world_id, turn)` over `InstanceRow.ContentFingerprint` (tuning
version alone must change the fingerprint); undrawable promise rejects at
load via the existing `ContainerValidator` naming the group (no second
validator; whole-row rejection for bundles); ownership-root tests: specimen
mint enters the FSM at `Roster` only (gated on UniqueActor program — bundles
never mint to `ActiveBound`/live `ptr`), item mint hits the single `rpg_item`
root with scope overlay + capacity (empire uncapped / unique-actor 15-role;
bundle-minted gear on real death follows corpse-cache moves-never-copy, never
the armoury), title mint blocked until the registry ships. PowerVector stays
scale-free. Title buffs on derived channels inherit sim-Partial
(Replace/Flag) until `Priority` ships — no silent Full claim.

## Tunables & Catalogs

Reads `achievement-titles.v{n}.json` (`poolWeightsMilli` per-mille, tier windows, odds
tiers); display tiers in catalog file. Every bundle's faucet names its sink
in the definition (P1); competing sinks shown (P6); territorial rewards
throttled by loam (P2).

## Numeric Types

Weights/thresholds `long`, per-mille divide-last, `checked` throw. Magnitudes
read `P(Θ)` exactly once at the single owned site; PowerVector never scaled.

## ActorHub Gate

Consume-only here (draw + fan-out); stat-affecting contents contribute
downstream via registered Hub subsystems (empire/actor title specs), never a
private fold in this module.

## Boundaries

- Always: grants via Funnel→FA* / Intent-after-Admit / CapPolicy; ledger
  dedupe keys; SQL only in Data.
- Ask first: new ownership root (expected answer: no — use existing roots).
- Never: second roller; direct Unity writes; `TakeDamage`/absolute-HP writes;
  wall-clock draws on world scope; population-count goldens.

## Success Criteria

- [ ] Deterministic draws byte-identical on same inputs.
- [ ] Undrawable pool promises reject at load naming the group.
- [ ] Mints land in correct roots/entry states with capacity checks.

## Open Questions

None.

# Spec: actor-titles

Module `actor-titles` (map: `docs/architecture/achievement-title-map.md`,
depends on `achievement-registry`, `reward-bundles`). Reading gate as registry
+ bundles + unique-actor runtime, ActorHub SSOT + GG-49, status/catalog notes.

## Objective

Specimens earn titles and equip them instead of physical items: bindings,
structural slot grammar beside the 15-role gear grammar, worn-display rule,
withdraw semantics. Users: roster/commander players. Success: titles reach
combat only through the one Hub gate with full attribution; sheet/HUD/
telemetry agree on what is worn vs what computes.

## Tech Stack

C# net6 Core (Hub contribution) + net8 Data/Server (bindings); equip menu FE
later via `/idea-ui`.

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj
Test: dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActorTitle"
Guards: python gk-core/scripts/guard-actor-hub.py
Verify: powershell -File scripts/verify-change.ps1 -Paths <changed> -Session <id>
```

## Project Structure

```
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActorTitles.cs    → equip/withdraw/worn over effect_binding (NEW)
gk-core/src/FusionRpg.Core/Achievements/TitleWornSelector.cs → slots + worn pick + six-resource rule (NEW)
gk-core/tests/FusionRpg.Data.Tests/**/ActorTitle*            → equip tests (NEW)
gk-core/tests/FusionRpg.Server.Tests/**/TitleHubReach*       → reach via existing projection (NEW)
```

## Code Style

```csharp
// Titles ride the existing equip path: grant binds to the player owner
// (inventory), equip binds to the actor owner with a title-{1,2,3} slot.
// DerivedFromStore resolves actor bindings only — each title composes once.
// (Overturned: no ActorTitleSubsystem — a second fold would be the
// BattleStatComposer defect class. See ActorHub Gate below.)
```

## Testing Strategy

xUnit + guard-actor-hub: title buffs visible only via Hub snapshot/
AppliedCombat with FULL `(source, op, value)` expansion + fiction labels; no
`*Composer*` added; worn selection owned by one deterministic selector
(bindings reader, highest-tier wins + explicit tiebreak) consumed by sheet,
HUD, and telemetry with a three-way agreement fixture (selector proven here;
sheet/HUD consumption is T7); title slots live in a
separate title-slot domain (the 15-role gear enum is never widened — no gear
migration needed); resource-touching
title families rejected unless all six resource ids present (ownership check);
worn rule: highest tier wins, tiebreak lowest `containerId`, Ordinal
(TitleWornSelector — the contract sheet/HUD/telemetry share); units stated per channel
family (ledger ids `long`/checked; resolver-points channels ÷100.0 — not ÷1000).

## Tunables & Catalogs

Shares/caps in `achievement-titles.v{n}.json`; names/readings/hudToken in
catalog file. Worn-selection rule is data, not branching.

## Numeric Types

`long`, per-mille divide-last, `checked`. Contests read `Θ`, magnitudes
`P(Θ)` — stated per magnitude; no new curve.

## ActorHub Gate

**Consume the existing equip path — overturned 2026-09-15 during T5 build.**
The spec as written demanded a new `ActorTitleSubsystem : IActorStatSubsystem`;
code evidence overturned it: title bindings (owner `unique-actor:`, slot
`title-{1,2,3}`, `stat.derived` atoms) already resolve through
`EquippedBoundAtoms.DerivedFromStore` → `EquipAtomSource` →
`AtomDerivedSubsystem` with role-tagged `equip:title-{slot}:{instance}`
SourceIds, and `FictionLabel` renders them with no new arm. A second subsystem
would be the BattleStatComposer defect class (parallel fold) — SOLID binding
says extend the gate, and the gate already extends here. Proven by
`TitleHubReachTests` (reach + no-double-count via the player-inventory/actor-
equip split). No new Order band, no registry-table row owed.

## Boundaries

- Always: Hub contribute-or-consume-only; bindings withdrawable; binder
  rewrites durable keys at Bound (`instance:` never Hot).
- Ask first: slot-count changes; new title family touching resources (must
  cover all six per owner rule); gear-validator acceptance — provider-owned
  by the UniqueActor program from this spec's slot-domain contract (title
  slots stay a separate domain here; this spec never edits gear files).
- Never: private ChannelMods combat writer; live `ptr` grants bypassing FSM;
  engine vocab on player surfaces (GG-23, FE later).

## Success Criteria

- [ ] Equip/withdraw flows through bindings; Hub output is the only read.
- [ ] guard-actor-hub green; attribution expands per contribution.
- [ ] Worn-vs-computing agreement test green.

## Open Questions

None (one-worn + stacking locked in ideal).

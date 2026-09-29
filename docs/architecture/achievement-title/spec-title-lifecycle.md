# Spec: title-lifecycle

Module `title-lifecycle` (map: `docs/architecture/achievement-title-map.md`,
depends on `empire-titles`, `actor-titles`). Reading gate as parent specs +
economy P13/P14, status timeless precedent, live-probe scope discipline.

## Objective

Own time and permanence: relative turn-window expiry with destinations,
slot-free honor binds keyed to durable grading facts, hidden curses with
priced ritual removal. Success: expiry/withdraw/re-earn are distinguishable
in the ledger; replay never double-withdraws; curses are fair and liftable.

## Tech Stack

C# net8 Server/Data; virtual-turn evaluation inside the turn step; telemetry
on every transition.

## Commands

```
Build: dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj
Test: dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~TitleLifecycle"
Guards: python gk-core/scripts/guard-dal.py
Verify: powershell -File scripts/verify-change.ps1 -Paths <changed> -Session <id>
```

## Project Structure

```
src/FusionRpg.Server/Titles/TitleLifecycle.cs    → expiry/honor/curse transitions (NEW)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Titles.cs     → lifecycle ledger (NEW)
gk-core/tests/FusionRpg.Data.Tests/**/TitleLifecycle*    → idempotence tests (NEW)
```

## Code Style

```csharp
// Relative windows anchored at equip (equippables) or grant (honors/curses).
// equipKey = equip-command factId; re-equip writes a new row, expiry reads the latest only.
ledger.ExpireTitle(scope, titleId, equipKey, turn);   // withdraw + telemetry
ledger.LiftCurse(scope, titleId, ritualKey, turn);    // atomic priced sink first
// Keys: grant=(scope,titleId,rev,factId); equip=(scope,titleId,equipFactId);
//   expire=(scope,titleId,equipFactId,expiryTurn). Re-earns are new rows on new
//   world-turn facts (world_id folded into scopeKey), never dedupe hits.
```

## Testing Strategy

xUnit: grant/equip/expire/re-earn sequences distinguishable via `kind` column
(grant/expire/re-grant) — replay hits dedupe, new world-turn facts re-earn;
save/load mid-window converges from hashed state
(`remaining = equipTurn + validTurns − currentTurn`, in-step); scope→clock
table enforced at load (empire = world virtual turns; actor lawn/battle
windows bind a named battle-tick counter or are rejected; expedition =
wall-clock with platform stamp only); destinations: expiry → Hall, Hall-full
→ oldest-unexpired-returns-first else re-equip rejected with cause, Retired
actor → binding tombstoned (curse follows tombstone, no refund — stated);
withdraw commits first, telemetry retries on the expire key, never rollbacks;
v1 curse taxonomy closed (enumerated Cold fact kinds); ritual is one atomic
sink (`title.ritual.souls` + `title.ritual.essence`, essence matched,
`omni` fallback) — insufficient funds = curse stays, no partial/escrow,
repeat-while-cursed climbs the rung, never concurrent curses; hidden-curse
probe creates a real transgression through the real service path and asserts
closed `visibility` vocab + teaser (never hidden counts); world-scoped
bundles with loam sinks reject at load (optional pools included);
`world_id` (+turn) in bundle seeds. Binding tables stay provider-owned —
lifecycle returns intents the providers apply.

## Tunables & Catalogs

`validTurns` (relative turns, integer), `titleRitualPrice.{souls, essence}`
per element (`omni` fallback), destinations in the catalog/registry file,
`wornRule: highestTier` closed enum, sink reasons `title.ritual.souls` /
`title.ritual.essence` + named telemetry events (integer math; any double
feeding hash/persistence records the platform stamp).

## Numeric Types

Turns/counters `long`, `checked`. No wall-clock on world scope.

## ActorHub Gate

Consume-only (lifecycle moves bindings; magnitude effects stay in the two
title modules' gates).

## Boundaries

- Always: virtual turns, in-step evaluation; withdraw + telemetry, never
  silent; dedupe keys per transition kind.
- Ask first: new transgression fact taxonomy entries.
- Never: Hot transgression detection; absolute turn-range windows; silent
  snaps; fabricated debug preconditions as proof.

## Success Criteria

- [ ] Expiry returns to stated destination; re-earn ≠ double-grant on replay.
- [ ] Honors persist slot-free on durable facts; curses lift only via ritual.
- [ ] All edge cases above green.

## Open Questions

None (windows relative, ritual shape, hidden+vague locked in ideal).

# Spec: `item-loadout-apply`

**Program:** [`build-preset`](../build-preset-map.md) · **Wave A** · depends on: nothing.
**Owner of the contract:** the item program, [`spec-armoury.md`](../item/spec-armoury.md) §"Loadouts —
claimed here, applied through module 4" (`docs/architecture/item/spec-armoury.md:103-121`). This module
builds that contract; it does not redesign it. If the item program lands it first, this module closes
as consumed and `piece-appliers` calls theirs.
**Status:** spec, not reviewed, no build authorized.

## Objective

A build preset's gear piece points at a saved **item loadout**. The loadout library already exists and
has never been reachable:

| Built | Where | Production callers |
|---|---|---|
| `rpg_item_loadout`, `rpg_item_loadout_entry` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:131-147` | — |
| `SaveLoadout`, `GetLoadoutEntries`, `GetLoadoutEntriesValidated`, `ListLoadouts` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:431,459,489,576` | **none** (tests only) |
| `LoadoutReport.Plan`: conflicts named by cell, `Stripped`, `Refused` | `gk-core/src/FusionRpg.Core/Items/LoadoutReport.cs:40-101` | **none** |
| `FindAssignmentHolders` across specimen and commander tables | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:541-574` | the equip route only |

What is missing is exactly what the armoury spec deferred: the routes (`docs/architecture/item/spec-armoury.md:220`)
and the **apply**, which writes assignments and so waits on module 4. Module 4's executor now ships
(`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:63`), so the apply can be built.

**Also missing, and not in the armoury spec: a delete.** The store has no `DeleteLoadout`. The route row
names `DELETE`, so this module adds it (below).

## Design

### Routes (`gk-core/src/FusionRpg.Server/ItemLoadoutEndpoints.cs`, new)

| Method | Route | Serves |
|---|---|---|
| GET | `/api/items/loadouts?playerId=` | `ListLoadouts` + per-loadout validated entries |
| PUT | `/api/items/loadouts/{loadoutId}` | `SaveLoadout` (create or replace; `revision` increments) |
| DELETE | `/api/items/loadouts/{loadoutId}?playerId=` | `DeleteLoadout` (new store method, owner-checked, one transaction over both tables) |
| POST | `/api/items/loadouts/{loadoutId}/preview` | `{ targetId }` → `LoadoutPlan` for that target, no write |
| POST | `/api/items/loadouts/{loadoutId}/apply` | `{ targetId, force }` → per-role outcome |

`targetId` uses the equip route's own target grammar: a specimen `instance_id`, or the commander's
stable id, resolved by the same `TryResolveTarget` (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:300-325`).
No second target parser.

### Apply

1. Read `GetLoadoutEntriesValidated(loadoutId, playerKey)`.
2. `FindAssignmentHolders` for the instance-pinned refs, then `LoadoutReport.Plan(entries, targetId, heldBy, force)`.
3. `Refused` → 409 with the conflict list naming cells. **Nothing is written.**
4. Otherwise, for each `Present` entry in stored order, call the flow that owns its kind:

| Loadout `ref_kind` | Owning flow | Call |
|---|---|---|
| `item` (one rolled copy) | module 4 equip executor | `ItemEquipService.Equip(playerId, targetId, refId, role)` (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:110`) |
| `stock` (a catalog relic) | the relic wire | `UniqueActorService.PutEquipment(targetId, slot, refId)` (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:54`), where `slot` comes from `LegacyEquipSlots.TryToLegacy(role, out slot)` (`gk-core/src/FusionRpg.Core/Items/LegacyEquipSlots.cs:68`), the inverse of the map the relic wire itself applies (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:1515-1530`) |

   With `force`, each stripped cell is first emptied through its owning flow's unequip
   (`ItemEquipService.Unequip`, `:209`, or `UniqueActorService.ClearEquipment`, `:82`), and the response
   lists what was stripped. **Never a silent strip** (`docs/architecture/item/spec-armoury.md:112-114`).
   The relic wire takes a legacy slot word, not a role, and only for a specimen in `Roster` phase
   (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:57-60`). So a `stock` entry whose role has no legacy slot,
   or whose target is the commander, is a **named refusal in the plan** (`loadout.stock-role-unmapped`,
   `loadout.stock-target-commander`), found by preview before anything is written, never a skipped row.
5. `Missing` entries are reported and skipped; they are never dropped from the response.
6. One lawn runtime sync after the last write, through the same `SyncLawnRuntimeAsync` the equip route
   uses (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:460`), not one per role.

**The ref-kind spelling (map X4).** A loadout pins a copy as `"item"`; an assignment pins the same copy as
`"rolled"` (`gk-core/src/FusionRpg.Core/Items/EquipProjector.cs:16-27`). One function maps them:

```csharp
// gk-core/src/FusionRpg.Core/Items/LoadoutReport.cs
public static string AssignmentRefKindFor(string loadoutRefKind) => loadoutRefKind switch   // (new)
{
    InstanceRefKind => EquipRefKinds.Rolled,
    EquipRefKinds.Stock => EquipRefKinds.Stock,
    _ => throw new ArgumentOutOfRangeException(nameof(loadoutRefKind), loadoutRefKind, "unknown loadout ref kind"),
};
```

**Convergence.** Each flow is idempotent on `(target, role)` (the equip executor's own note,
`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:35-41`), so re-running an interrupted apply lands the same
rows. The response lists per-role outcomes, so a partial apply is visible.

**Not a price.** Equip costs nothing by design (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:35-36`), so
apply costs nothing.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LoadoutReport"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Armoury"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemLoadout"
python gk-core/scripts/guard-dal.py
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Server/ItemLoadoutEndpoints.cs` (new) | five routes |
| `gk-core/src/FusionRpg.Server/Gates/ItemLoadoutApplyService.cs` (new) | the apply above; used by the route and by `piece-appliers` |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs` | `DeleteLoadout(playerId, loadoutId)` (new), owner-checked |
| `gk-core/src/FusionRpg.Core/Items/LoadoutReport.cs` | `AssignmentRefKindFor` (new) |
| `gk-core/src/FusionRpg.Server/Program.cs` | map + register |
| `gk-core/tests/FusionRpg.Server.Tests/ItemLoadoutEndpointsTests.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/Items/ArmouryTests.cs` | cases below |

## Code style

The apply loop reads as a dispatch over the owning flow, never an inline write:

```csharp
foreach (var e in plan.Entries.Where(e => e.State == LoadoutEntryState.Present))
{
    var outcome = LoadoutReport.AssignmentRefKindFor(e.RefKind) switch
    {
        EquipRefKinds.Rolled => _equip.Equip(playerId, targetId, e.RefId, e.Role),
        EquipRefKinds.Stock  => FromRelic(_unique.PutEquipment(targetId, LegacySlotFor(e.Role), e.RefId)),
        _ => throw new UnreachableException(),
    };
    results.Add(new RoleOutcome(e.Role, outcome.Ok, outcome.Reason));
}
```

## Testing strategy

1. **Contract names from the armoury spec**, now driven over HTTP:
   `a_loadout_entry_whose_item_was_salvaged_returns_missing` and
   `applying_a_loadout_whose_item_is_held_elsewhere_refuses_with_LoadoutConflict`
   (`docs/architecture/item/spec-armoury.md:274-275`), plus a new `force_reports_what_it_stripped`
   for that row's second clause.
2. **Refused writes nothing.** Assignment rows are unchanged after a refused apply.
3. **Each kind reaches its own flow.** A rolled entry produces a `rolled` assignment row; a stock entry
   produces the relic wire's row **and** its `mods_json` / atom bindings (what makes the relic wire the
   owner). Neither flow ever writes the other's kind.
4. **Commander target.** A loadout applies to the commander's stable id and lands in the player-scope
   table, exactly as a direct equip would.
5. **Idempotent.** Applying twice leaves the same rows and reports every role `Ok` the second time.
6. **Delete.** Owner mismatch refuses; delete removes both tables' rows in one transaction.

## Boundaries

- **Always:** route every write through its owning flow; report `Missing` and stripped cells by name.
- **Ask first:** any change to the armoury's conflict semantics (default refuse, force reports).
- **Never:** write `rpg_item_assignment` directly from this module; strip silently; drop a `Missing`
  entry from a response.

## Tunables, ActorHub, integer widths

- **Tunables:** none. The library has no soft max in the armoury spec, and none is added here.
- **ActorHub:** not applicable. Equipment reaches Hub as layer 3 through the existing projection
  (`MaterializeRolledEquipRuntime`), unchanged.
- **Integer widths:** none; no magnitudes.

## Seedsmith / generator

**None.** Player-owned runtime rows. `gk-data/packs/fusion/data/seed/items/**` is untouched.

## Success criteria

- [ ] Five routes live; list, save, delete, preview, apply.
- [ ] Apply refuses on conflict with cells named; `force` reports what it stripped.
- [ ] Each entry is written by the flow that owns its ref kind.
- [ ] The armoury spec's two loadout test names and the new force test pass.

## Open questions

None. The contract is the armoury spec's.

## Self-audit — the debate

- **"This belongs to the item program."** It does, and the armoury spec says so. It is specced here
  because build-preset cannot ship without it and nobody has scheduled it. The spec copies the armoury
  contract rather than extending it, and closes as consumed if the item program builds it first.
- **"Use `ItemEquipService` for stock entries too."** It refuses a relic cell by name on purpose
  (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:43-50`); the relic wire also rebuilds `mods_json` and
  bindings. Routing by kind is the only way both derived states stay right.

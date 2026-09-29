# Spec: `commander-roster`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave C** · depends on: external
`solid-enforcement` [`commander-identity`](../solid-enforcement/spec-commander-identity.md) and
[`save-identity`](../solid-enforcement/spec-save-identity.md) (`EmpireRef`; its consumer row for this
module, X11), neither **re-specified here**. Waiting for `save-identity` means the table below is born
keyed by empire and never migrated (map S8). **Rulings honoured:** *"a commander literally a unique demon, it only carry
more role"*; R-C2 (*"no special for commander, it basically a unique unit"*); map decision P3.
**Status:** spec, not reviewed, no build authorized.

## Objective

Let a unique creature **hold the commander role**, and let the player's roster of commanders be data
that grows when they grant the role, with no code change per commander.

`commander-identity` makes this possible and stops there, by design. Its own words: *"`empire-progression`
then makes a unique creature a commander by adding a directory row, or a directory source backed by
`rpg_unique_actor`. That extends the directory. It never edits it."* This module is that source.

What stands in the way today, after `commander-identity` lands:

| Gap | Where |
|---|---|
| No state anywhere means "this specimen holds the commander role" | stated by the code itself, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:177-185` |
| The player's commander list is a hard-coded one-element array | `gk-core/src/FusionRpg.Core/Commanders/PlayerEmpireCommanders.cs:9-10` (replaced by the directory's data rows in `commander-identity`, still one row) |
| The directory resolves a commander but cannot **list** a player's roster | `ICommanderDirectory` in `spec-commander-identity.md` has `TryResolve`, `EmpireOf`, `DisplayName`, `AllocationScopeKey`, `DefaultFor`, and no enumeration |

## Design

### The role is a binding (map P3)

```
rpg_commander_role (new)
  save_id      INTEGER NOT NULL      -- SaveId (R17: today's player id)
  empire_id    TEXT    NOT NULL      -- EmpireId value, "dave" for a player's own creature
  instance_id  TEXT    NOT NULL      -- rpg_unique_actors.instance_id
  granted_utc  TEXT    NOT NULL
  PRIMARY KEY (save_id, empire_id, instance_id)
```

- **Additive and removable.** Grant inserts, revoke deletes. The creature is unchanged either way: same
  `rpg_unique_actors` row, same level, gear, allocation and phase. The creature is the noun; commander
  is an adjective (the ideal's rule).
- **No `RpgActorKinds` member** for commanders, no new phase, no second level. Today the vocabulary is
  `player/plant/zombie/species/specimen` (`gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:25`);
  `empire-level` adds `empire`, an empire's own level, which is not a commander kind and does not change
  this rule.
- **No roster size limit.** A roster is a population; a count limit would be a ceiling. If a cap is ever
  wanted it is a soft, tunable one, and nobody has asked for one.
- Refusals on grant, each named: `commander.role.retired` (the specimen is `Retired`),
  `commander.role.notOwner`, `commander.role.unknown`. A creature in any other phase may be granted the
  role; *where* it can then lead is the place's rule, owned by `lawn-commander-seat` and
  `legion-commander`.

### The directory source

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


`commander-identity` ships a data-backed directory holding the authored rows (`commander:dave`,
`commander:zomboss`). This module adds a second **source** the directory composes, never a second
directory:

| Directory method | For a role-holding creature |
|---|---|
| `TryResolve(stableId)` | `commander:unique:{instanceId}` resolves when a role row exists. The `commander:` prefix is kept, so it still cannot collide with a faction id or a battle key (`gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs:28-31`) |
| `EmpireOf` | the binding's `empire_id` |
| `DisplayName` | the creature's nickname if set, else its species' display name (`rpg_creature_profiles.nickname`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:619`) |
| `AllocationScopeKey` | **the empire's default commander's key** (`player:{id}` for Dave's empire). Decided by R4: both apply |
| `DefaultFor(empire)` | unchanged. The authored row stays each empire's fallback |

### `AllocationScopeKey` — both apply (R4)

Today the player's `Commander` allocation is merged into every member of the player's side
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:573-576`, and the lawn commander cache). The owner
ruled R4 ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)): *"Yes, both apply. The leading creature adds only its aura."* So when a creature
leads, the empire's commander allocation keeps lifting the side exactly as it does today, and the
creature commander contributes its aura and nothing else side-wide. Swapping commanders never changes
the army's aptitudes. This source's `AllocationScopeKey` therefore always returns the empire's default
commander's key; it stays in one place because one place is where the directory answers it, not because
the answer is still open.

### Listing — a separate interface (I in SOLID)

```csharp
namespace FusionRpg.Core.Commanders;

/// An empire's commanders: the authored default(s) for that empire, then every creature holding the
/// role, ordinal by stable id. Enumeration only; resolution stays on ICommanderDirectory.
public interface ICommanderRoster                                        // (new)
{
    IReadOnlyList<CommanderRef> ForEmpire(EmpireRef empire);             // save-identity X11
}
```

It is its own interface rather than a sixth method on `ICommanderDirectory`, because most directory
consumers (allocation, kill attribution) never list, and should not depend on a method they do not use.
`GET /api/commanders/{playerId}` (`gk-core/src/FusionRpg.Server/CommanderEndpoints.cs:45`) projects `ForEmpire(HumanEmpireOf(save))` from it (the route's `playerId` is the `SaveId`, ruling R17), so
the Commanders layer (`commander-surface`) shows the roster with no FE change beyond more rows.

### Routes

| Route | Effect |
|---|---|
| `POST /api/commanders/role` (new) `{ playerId, instanceId, grant }` | grant or revoke; broadcasts the commander list refresh the layer already listens for |

Revoking the role of the **default** lawn commander resets the default to the empire's authored
default, in the same transaction, so the default never points at a non-commander. A revoke never
touches a frozen match snapshot: a run already started keeps its leader (commander-surface's
`match-snapshot` rule, mid-run changes affect the next run).

### Delve, unchanged

A role-holding creature joins a delve party like any unique (R-C2). This module adds a test that party
admission ignores the role, and nothing else.

## Seedsmith / generator

**None.** The authored default rows are `commander-identity`'s registry
(`gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json`, (new) there, authored, never generated).
Creature commanders are player data, not seed content.

## Tunables

None. There is no commander stat, curve or limit (R-C2; the ideal's Tunables: *"no commander-specific
magnitude at all"*).

## ActorHub gate

**Consumes Hub only, and contributes nothing new.** A commander creature composes exactly like any
unique, through `UniqueActorHubCompose` and the battle Hub seams. The side lift keeps its existing seam
and key (above). The aura is `aura-skill`'s contribution path. No commander-shaped branch enters the stat
path.

## Integer widths and the power ladder

No magnitudes. `granted_utc` is ISO text like every other stamp.

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CommanderRole"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CommanderDirectory|FullyQualifiedName~CommanderRoster"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~CommanderEndpoints"
python gk-core/scripts/guard-open-identity.py
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderRole.cs` (new) | table, grant, revoke, list |
| `gk-core/src/FusionRpg.Core/Commanders/ICommanderRoster.cs` (new) | the listing interface |
| `gk-core/src/FusionRpg.Core/Commanders/UniqueCommanderSource.cs` (new) | the directory source |
| `gk-core/src/FusionRpg.Server/CommanderEndpoints.cs` | `POST /role`; list from `ICommanderRoster` |
| `gk-core/tests/FusionRpg.Data.Tests/CommanderRoleTests.cs` (new) | below |

## Code style

```csharp
public bool TryResolve(string stableId, out CommanderRef commander)
{
    commander = default;
    if (!stableId.StartsWith(UniquePrefix, StringComparison.Ordinal)) return false;   // "commander:unique:"
    var instanceId = stableId[UniquePrefix.Length..];
    if (!_roles.HasRole(instanceId)) return false;
    commander = new CommanderRef(stableId);
    return true;
}
```

No `switch` over `CommanderRef` or `EmpireId` (`commander-identity`'s I2).

## Testing strategy

1. **Open/Closed, again.** Granting the role to a creature makes it resolvable, listable and selectable
   as the default lawn commander with **no production edit**, extending `commander-identity`'s
   third-commander test from an in-memory row to a real role row.
2. **Additive.** Grant then revoke leaves the creature's row, allocation, gear and phase byte-identical.
3. **Refusals** are named for retired, not-owned and unknown.
4. **Default follows revoke.** Revoking the default commander's role resets the default in the same
   transaction; a started match's snapshot is unchanged.
5. **No re-keying.** A creature commander's `EmpireOf` is its binding's empire, and a species allocation
   for that empire resolves identically before and after the grant. This is the conflation
   `commander-identity` exists to prevent, tested from this side.
6. **Delve ignores the role.** A role-holder is admitted to a party exactly as before.

## Boundaries

- **Always:** role as a binding; one directory; listing through `ICommanderRoster`.
- **Ask first:** the new table (schema); a roster limit.
- **Never:** give a creature commander its own side-wide allocation key; R4 ruled that its aura is its
  only side-wide contribution.
- **Never:** an `RpgActorKinds` member for commanders; a commander stat path; a `switch` on commander
  identity.

## Success criteria

- [ ] A creature can be granted and revoked the role; the roster lists it.
- [ ] It can be the default lawn commander.
- [ ] `guard-open-identity` green; Open/Closed test green.

## Open questions

None.

## Rulings applied 2026-09-18

- **R4** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)), was map question 2: when a creature leads, the player's commander allocation still
  applies side-wide and the leading creature adds only its aura. Recorded as decided; this spec already
  built that answer, so no behaviour changed.

## Self-audit — the debate

- **"Why not store the role on `rpg_unique_actors`?"** A column there makes the role part of the
  creature's row and every read of the creature pays for it; a binding table makes it additive,
  removable, and listable by one index, which is what "roles are additive and removable" asks for.
- **"Zomboss's creatures could hold the role too."** The table carries `empire_id`, so they can. Who
  grants an AI empire a commander is the AI's business; this module does not invent that behaviour.

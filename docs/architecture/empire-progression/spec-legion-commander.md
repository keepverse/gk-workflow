# Spec: `legion-commander`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave C** · depends on:
[`commander-roster`](spec-commander-roster.md); external `species-progression`
[`layer-source-selector`](../species-progression/spec-layer-source-selector.md), the single owner of the
`HubInputsFor` seam at `RpgStore.WorldTurns.cs:559-593` (a **hard** dependency: this module is the first
writer of `InstanceId`, so it must not land before the seam stops handing a unique the species
fallback). **Rulings honoured:** *"it can play commander role in the
legion (the inspire of heroes of might and magic)"*; R-C1 (a specimen lives in exactly one parent; a
legion in a sector is a parent); R-C2 (a commander is a unique unit with one extra feature, its aura);
the owner's correction that a commander **fights** in siege and world assault. **Status:** spec, not
reviewed, no build authorized.

## Objective

Let a creature commander **lead a legion** and **fight with it** in sieges and world assaults, as its own
specimen.

Most of the path already exists. Read in code:

| Piece | State | Where |
|---|---|---|
| A legion member row can carry a real specimen | column exists, **every writer omits it** | `gk-core/src/FusionRpg.Core/World/WorldState.cs:277-278`; writers per `deployment-hierarchy-ideal.md` §"The tree" |
| A siege composes an `InstanceId` member through Hub, from its real allocation | **built** (solid-remediation D4) | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:409-415`, provider `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:559-592` |
| A member's role | `{ Fighter, Bearer }` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:269-273` |
| A world command that binds a real specimen, re-validated at resolution | **built**, the precedent to copy | `bind-warden`: `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:51`, `gk-core/src/FusionRpg.Core/World/Movement/WardenResolver.cs:14-50` |
| The siege seam gives an `InstanceId` member the **empire species fallback** | **defect** (map X5) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:581-590` vs `decisions.md` "Creature progression source" |

So this module adds a role member, a writer, a parent rule, and fixes the one seam it is about to
depend on.

## Design

### `WorldEntityMemberRole.Commander`

`{ Fighter, Bearer }` gains `Commander`. That enum **is** a closed vocabulary the code owns, so adding a
member is a reviewed declaration change, which is the correct use of an enum, the contrast with
`CommanderId` the ideal draws. Persistence already writes the role by name
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:387`, `m.Role.ToString()`), and the reader must accept the
new name.

A `Commander` member fights (R-C2 and the owner's correction). It is not a `Bearer`, so it carries no
cargo, and it counts toward the legion's fighting strength like any `Fighter`.

**One `Commander` member per legion**, a structural limit: a legion has one leader, the HoMM3 hero shape
the owner named. It is enforced at resolution with a named drop, and the code comment says it is
structural, not a tunable.

### Attach and detach — two world commands, modelled on `bind-warden`

| Kind | Target | Resolves |
|---|---|---|
| `attach-commander` (new) | a legion entity + an `instanceId` | adds a `Commander` member with the specimen's `InstanceId`, `SpeciesId`, `Level` and full `Hp`, `Wounds = 0` |
| `detach-commander` (new) | a legion entity | removes the `Commander` member; the specimen's parent returns to home |

Checks split by where the fact lives, the way `bind-warden` already splits them:

| Check | Layer | Drop reason |
|---|---|---|
| the specimen holds the commander role for this faction's empire | Data, at command admission | `commander.role.missing` |
| the specimen is in phase `Roster` and not already in another legion | Data, at admission | `commander.not-at-base` |
| the legion exists, is this faction's, and is **stationed**, not on a lane | Core, at resolution (re-validated, like `WardenResolver.cs:32-38`) | `legion.gone`, `legion.not-yours`, `legion.marching` |
| the legion has no `Commander` member already | Core, at resolution | `legion.has-commander` |

Resolution phase: `Snapshot`, beside `bind-warden` and `raise`, for the same reason (ownership settles
last in the turn).

### The parent rule (R-C1)

Attaching changes the specimen's **parent** from home to the legion; its phase stays `Roster` (not
deployed). Every child admission then asks one question, `ParentOf(instanceId)` (new, Data, reads the
world graph): `Home`, or `Legion(entityId, stationed)`.

| Child | From home | From a stationed legion | From a marching legion |
|---|---|---|---|
| lawn Bound, lawn commander seat, delve slot, expedition seat | ✅ | ✅ | ❌ `not-at-base` |
| siege combatant | — | ✅ as a member of that legion | — |

This is the deployment tree exactly as `deployment-hierarchy-ideal.md` §"The tree" draws it, and it is
*"to enter the lawn run, the commander must on any base"* made mechanical. One query, used by every
admission path, so the rule cannot drift between them.

**The reverse direction, found in the self-audit.** A commander attached to a stationed legion may be
seated for a lawn run (`lawn-commander-seat`), which moves it to `ActiveBound`. If the player then ends a
world turn in which that legion fights, the siege would field the same specimen a second time. So
`BuildAnimateSetups`' provider skips a `Commander` member whose specimen is not in phase `Roster`, and
the turn report names it (`commander.away`). The legion fights without its leader that turn; the
specimen stays in one place.

### Fighting — reuse the built seam, fix it first (map X5)

> **Reconciled 2026-09-18 (orchestrator review): the fix has ONE owner, and it is not this module.**
> The same defect is `species-progression` map C1, closed by
> [`spec-layer-source-selector.md`](../species-progression/spec-layer-source-selector.md) — one Core rule deciding which
> layer and which empire an actor reads, with the red-then-green regression at `RpgStore.WorldTurns.cs:590`. Two programs
> each patching the same seam is the parallel-fix shape SOLID forbids. **This module depends on `layer-source-selector`
> and consumes it**; the snippet below shows the intended outcome, not a second implementation. The acceptance item
> "no `CreatureType` points" stays here as a consumer-side assertion.

A `Commander` member has an `InstanceId`, so `BuildAnimateSetups` already routes it through
`HubInputsFor` and composes it as its specimen. One correction must land first, because this module is the
first to put a player's unique into a legion. **It is `layer-source-selector`'s change, not this
module's**; the lines below show the outcome this module asserts from the consumer side:

```csharp
// RpgStore.WorldTurns.cs:590 today
Aptitude = commander + species + specimen,
// after layer-source-selector: a unique never receives the empire species fallback
// (decisions.md, Creature progression source). The exact shape of the commander and specimen terms
// (ruling R16: each resolves only its own points) is species-progression's `species-layer-delivery`;
// this module asserts only "no CreatureType points" and never edits the provider's layer selection.
Aptitude = commander + specimen,
```

**Read the provider closely, because the defect is sharper than it looks.** `HubInputsFor` returns
`null` for a member with no `InstanceId` (`RpgStore.WorldTurns.cs:561`), so general troops never get Hub
inputs at all: they fight on the flat level-derived stats at `DistrictAssaultResolver.cs:395-396`. The
species term (solid-remediation T4.4's S2, *"battle received no species allocation at all"*) therefore
reaches **only** `InstanceId` members, which are exactly the population the ownership row forbids it
to. Since no writer sets `InstanceId` today, it has never fired in production; this module is the first
thing that would make it fire. Removing it changes nothing for general troops, which stay as they are.
That general troops receive no species allocation in a siege is a separate, pre-existing gap for
`species-progression` (it is where S2 was meant to land), recorded in the map and not widened here.

The specimen term reads `default-build`'s resolver when that module has landed, so an unbuilt commander
fights with its species' default distribution rather than nothing.

The `commander` term (the player's pool, `RpgStore.WorldTurns.cs:573-576`) is unchanged, by ruling: R4
([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)) — *"Yes, both apply. The leading creature adds only its aura."* The legion's creature commander
lifts the side through its aura (owned by `aura-skill`) and fights as its own specimen; it never
replaces the player's pool.

### Casualty — no commander special

A commander member reduced to zero in a siege is handled as a unique. `deployment-hierarchy`'s
`injury-tiers` defines how a unique is wounded or killed. Until it ships, a fallen commander member is
detached and set `Recovering`, the non-lethal default the delve already uses for a downed unique
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:445`). The ideal left *"whether a commander can
be lost"* undecided; R-C2 answers it: a commander can be lost exactly as any unique can.

### What this module does not add

- **XP for the fight.** Siege and world assault award no specimen XP to any unique today; only
  expeditions consume the battle report's per-specimen XP (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:318`).
  That is a gap for every unique, filed as a cross-program ask in the map, not a commander feature.
- **The aura's reach.** Siege and world assault at 100% of the lawn value (R-C5) is `aura-skill`'s table.

## Seedsmith / generator

**None.** World commands and runtime composition. No world template seeds a commander.

## Tunables

None. The one-per-legion limit is structural (see above).

## ActorHub gate

**Consumes Hub through the existing siege seam.** The member composes through `HubInputsFor` →
`BattleHubCompose`, the one battle compose. This module **removes** a term that violated the ownership
row; it adds no contribution and no subsystem.

## Integer widths and the power ladder

`Hp`, `Wounds` and `Level` keep their existing member types. The member's magnitudes come from its
specimen through `P(Θ)` via Hub. Nothing new.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~DistrictAssault|FullyQualifiedName~CommanderAttach|FullyQualifiedName~WorldCommandAdmission"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn|FullyQualifiedName~ParentOf"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~DistrictAssault"
# crosses Core, Data and Server: full suite once at module end
.\scripts\test-fast.ps1 -AllDefault
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/World/WorldState.cs` | `WorldEntityMemberRole.Commander` |
| `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs` | two kinds |
| `gk-core/src/FusionRpg.Core/World/Movement/CommanderAttachResolver.cs` (new) | resolution checks, modelled on `WardenResolver` |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` | admission checks and the `commander.away` skip in `BuildAnimateSetups`' member loop. **Not** the species-term fix, which `layer-source-selector` owns; this module does not edit `HubInputsFor`'s layer selection |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderParent.cs` (new) | `ParentOf` |
| every child admission path (lawn deploy, seat, delve, expedition) | consults `ParentOf` |
| `gk-core/tests/FusionRpg.Core.Tests/World/Turn/CommanderAttachResolverTests.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs` | below |

## Code style

```csharp
if (next.Entities.Single(e => e.EntityId == legionId).Members.Any(m => m.Role == WorldEntityMemberRole.Commander))
{
    Drop(report, phase, command, "legion.has-commander");   // structural: one leader per legion
    continue;
}
```

## Testing strategy

1. **Attach writes the specimen.** A resolved `attach-commander` yields one `Commander` member carrying
   the specimen's `InstanceId`, species and level; the world round-trips it through persistence.
2. **Every drop reason**, each in its own test, including re-validation of a legion lost the same turn.
3. **Fights as itself.** In a siege, the commander member's setup carries `HubInputs` built from its
   `UniqueCreature` (or default) allocation, and **no `CreatureType` points** (X5, tested from the
   resolver's output).
4. **General members unchanged.** A siege with no `InstanceId` members produces byte-identical setups
   and a byte-identical report to before the fix (they never had Hub inputs).
5. **Parent rule.** From a marching legion every child refuses `not-at-base`; from a stationed legion
   each child admits. Order-independent against attach and seat in the same turn.
6. **Casualty.** A commander member at zero is detached and `Recovering` until `injury-tiers` lands.
6b. **Away leader.** A commander member whose specimen is seated on the lawn (or otherwise not `Roster`)
   is skipped in a siege with `commander.away` in the report, and the rest of the legion fights.
7. **Goldens.** Only a fixture that already builds an `InstanceId` member can move, by the species
   term; each move is listed and explained. No production save can move, because no writer set
   `InstanceId` before this module.

## Boundaries

- **Always:** re-validate at resolution; one `ParentOf`; consume `layer-source-selector`'s answer for unique
  members (and assert it carries no species term) rather than re-deriving it.
- **Ask first:** attaching non-commander uniques (that is `deployment-hierarchy`'s later item).
- **Never:** a commander-specific stat path; a second siege compose; leaving the species term on a
  unique member; replacing the `commander` term with the creature commander's allocation (R4).

## Success criteria

- [ ] A creature commander can be attached to and detached from a stationed legion.
- [ ] It fights in a siege as its own specimen, with no species fallback.
- [ ] Every child admission reads `ParentOf`.
- [ ] Full suite green at module end; every moved golden explained.

## Open questions

None.

## Rulings applied 2026-09-18

- **R4** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)), was map question 2: both apply. The `commander` term stays the player's pool; the
  creature commander adds only its aura. Recorded as decided; no behaviour in this spec changed.

## Self-audit — the debate

- **"Fixing X5 is solid-remediation's job."** Superseded by the reconciliation above: `species-progression`
  `layer-source-selector` owns it, and this module takes it as a hard dependency. The original argument
  follows for the trail — it assumed no open program had it, which stopped being true when that map was
  written. This module is the first to route a player's unique through that seam, which is exactly why it
  must wait for the fix rather than ship the violation into a new feature.
- **"Phase `Roster` for a specimen away in a legion reads oddly."** `Roster` means "at a parent, not
  deployed" in the deployment tree, and a legion is a parent. A new phase would force every admission
  path and the FE to learn it; one `ParentOf` query carries the same fact.

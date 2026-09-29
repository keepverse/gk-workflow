# Spec: `role-aware-placement`

**Status: written against shipped code 2026-09-19.** Module id `role-aware-placement`, row 3 of the
[legion-build map](../legion-build-map.md) (wave 1; depends on `member-stack`, external `empire-progression`
`legion-commander`). Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.1 (roles gate placement
and eligibility — *"loop, not mechanism"*).

## Objective

A battle places only the members whose role fights. `Fighter` and `Commander` take cells; `Bearer` never
does, and shares its legion's fate instead. Today the district assault fields every living row, so a
bearer — a porter the supply model exists to separate from fighters (`LegionSupply.cs:11-12`) — fights.

Success looks like: one predicate decides who is placed for every battle kind; a world with no bearers
resolves byte-identically; a bearer's fate is a stated rule with a test.

## Scope and non-goals

- **In:** one `Fights(role)` predicate; its use in `BuildAnimateSetups`; the bearer-fate rule in
  `BuildSideOutcome`; the empty-side handling for a bearer-only legion.
- **Out:** *what a hit does* (the engine's); the `Commander` value and its `attach-commander` command
  (`empire-progression` `legion-commander`, map X3); producing bearers in play (`raise-choice`).

This is a **loop** decision in the `battle-engine-ssot.md` §2 sense — who is placed on the board — never
a mechanism. §5 of that page: responsibility — none (placement input); decides or resolves — neither, it
selects the setup list; every mode — the world is the only mode with roles.

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | Roles `{Fighter, Bearer}`, `Fighter` default | `gk-core/src/FusionRpg.Core/World/WorldState.cs:267-275` |
| Built | Supply separates bearers from fighters: capacity from bearers, burn from everyone | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:11-25` |
| Wiring gap | `BuildAnimateSetups` has no role filter: every row with effective HP > 0 is fielded | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:415-462` (skip rule at `:421-422`) |
| Wiring gap | `BuildSideOutcome` carries a never-fielded row forward unchanged, and counts it as a survivor for `Destroyed` | `DistrictAssaultResolver.cs:515-521,539` |
| Real gap | Bearers exist only in template literals | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:196`; producing them is `raise-choice`'s |
| Owned elsewhere | `WorldEntityMemberRole.Commander` and attach/detach; *"a Commander member fights"* | `docs/architecture/empire-progression/spec-legion-commander.md:34-40` |

## Design

### 1. One predicate

```csharp
// beside WorldEntityMemberRole, WorldState.cs
public static class WorldEntityMemberRoles
{
    // Which roles take a battle cell. Closed: a new role states its answer here in the same change.
    public static bool Fights(WorldEntityMemberRole role) => role switch
    {
        WorldEntityMemberRole.Fighter => true,
        WorldEntityMemberRole.Bearer => false,
        // WorldEntityMemberRole.Commander => true,   // armed when legion-commander lands (§3)
        _ => throw new ArgumentOutOfRangeException(nameof(role)),   // a new role must answer
    };
}
```

`BuildAnimateSetups` skips a row when `!Fights(member.Role)`, before the effective-HP test. Every later
battle kind (`field-battle-kinds`) builds its setups through the same method, so the predicate has one
call site.

### 2. Bearer fate — a stated rule

Bearers are never placed, so the battle says nothing about them. Their fate follows their side:

| Side result | Bearers |
|---|---|
| At least one fighting member survives, not routed | carried forward unchanged |
| At least one fighting member survives, routed | carried forward unchanged, and move with the rout |
| **No fighting member survives** | **lost with the side** — the legion is destroyed; a legion with no fighters left cannot protect its porters |

`BuildSideOutcome`'s `Destroyed` becomes "no **fighting** survivor". A row that was fighting-eligible but
entered at zero effective HP keeps today's carry-forward (it was never fielded for a different reason).

### 3. The `Commander` arm

`legion-commander` adds `Commander` to the enum (`spec-legion-commander.md:36-40`). Until it lands, the
switch has no `Commander` arm and the enum has no such member, so nothing can reach it. The spec that adds
the member adds the arm (`Commander => true`, *"a Commander member fights"*) in the same change — the
throwing default makes forgetting it a test failure, not a silent non-fighter. A
`CrossProgramLandedFlags` entry (`gk-core/src/FusionRpg.Core/Actions/CrossProgramLandedFlags.cs`) is **not**
needed: the enum member itself is the landed signal, and the predicate cannot compile a reference to a
member that does not exist.

### 4. Empty sides

- **Attacker with no fighting member:** `attackerSetups.Count == 0` already refuses the battle with a
  winnerless outcome (`DistrictAssaultResolver.cs:155-157`). Unchanged: a bearer-only legion cannot attack.
- **Defender with no fighting member:** the existing unopposed path (`:200-205`,
  `SiegeObjective.Evaluate` on an empty defender list) resolves it; by §2 the defending bearers are lost.

## Tunables and numeric types

None.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~DistrictAssault|FullyQualifiedName~SiegeEngagement"
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                    MODIFIED  WorldEntityMemberRoles.Fights
gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs  MODIFIED  filter + bearer fate
gk-core/tests/FusionRpg.Core.Tests/World/...                      EXTEND    cases below
```

## Testing strategy

- A bearer is never placed (its key is absent from the setup list and the report).
- Each row of the §2 table has its own test.
- A bearer-only attacker is refused winnerless; a bearer-only defender loses its bearers and the attacker
  takes the objective.
- **Byte identity:** every district-assault and siege golden with no bearer present is unchanged.
- The predicate throws for an unmapped role (a test adds a fake value via `(WorldEntityMemberRole)99`).
- `Fights` has exactly one production call site (a source-scan test over `gk-core/src/FusionRpg.Core/World/**`).

## Boundaries

- **Always:** decide placement through `Fights`; keep the predicate total.
- **Ask first:** capturing bearers instead of losing them (a loot rule — `scoped-inventory-hierarchy`
  `cargo-fate` owns what happens to a destroyed legion's cargo).
- **Never:** a second placement filter in any battle kind; a role check inside `BattleEngine`.

## Success criteria

1. Only fighting roles are placed, in every battle kind, through one predicate.
2. The bearer-fate table is implemented and each row tested.
3. No golden without bearers moves.

## Interface exposed to dependents

`WorldEntityMemberRoles.Fights` — consumed by `stack-combatant`, `legion-owner-scope` (5c contributions go
to fighting members only), `field-battle-kinds`, `fleet` (`crew`, `trade-route-order`: a caravan's
bearers carry, its fighters defend).

## Hard edges

A template world with a bearer in a siege (`WorldTemplateCatalog.cs:196`) moves: that bearer no longer
fights. Re-blessed with the reason in the commit. **Round 6 C1:** the world bump is **wave 1's single bump**,
shared with the other wave-1 modules and taken at landing rather than minted here
([landing-order.md](../trade-network/landing-order.md)); it is needed because the same command log now
resolves that fight differently. No migration; no schema change.

## Dependencies

`member-stack` (rows are stacks when this lands; the filter is per row either way); external
`empire-progression` `legion-commander` for the `Commander` arm only.

## Design-gate checklist

```
[x] Subsystems: world battle placement (loop); battle engine untouched.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: see spec-member-stack.md's list; plus battle-engine-ssot.md §2/§3c/§5 for the
    loop/mechanism split, spec-legion-commander.md Design. Not read: world-map row documents.
[x] decisions.md checked: Battle engine is the SSOT (loop may be mode-specific).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: BuildAnimateSetups, BuildSideOutcome, the refusal and unopposed paths.
[x] Read the surrounding section of every rule quoted.
[~] "No-bearer goldens unchanged" is an acceptance test, not yet run.
[x] No §2 invariant contradicted: placement is loop; the engine owns every mechanism.
[x] Corrections propagated (map §10).
[x] No population count pinned.
[x] No event-refreshed cache.
[x] No ordering assumption.
[x] No actor magnitude.
[x] No parallel path: one predicate.
[ ] Enforcement-registry row owed: "placement only through Fights" — the single-call-site scan test is the
    guard; the registry row is written by the implementing change.
```

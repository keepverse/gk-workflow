# Spec: `raise-choice`

**Status: written against shipped code 2026-09-19.** Module id `raise-choice`, row 7 of the
[legion-build map](../legion-build-map.md) (wave 2; depends on `member-stack`). Ideal:
[legion-build-ideal.md](../legion-build-ideal.md) §6.1 (*"Recruitment choice — raise picks a species from
the sector's pool instead of a fixed one"*). Interacts with owner decision **Q2**. **Round 4 (2026-09-19),
binding:** owner decision **Q6** in [decisions-round-4.md](../trade-network/decisions-round-4.md) — *"the
recruitment pool is the raising faction's own side plus the sector's species pool"* — closes this spec's
former "Left open" item (§2 below). Units that can only be raised in particular sectors through a recruit,
train or hire building are a **future unit-system program**, not this module (round 4 §U).

## Objective

`raise` today founds exactly one level-1 `Fighter` of a species the player never chooses: the first
zombie-side species, by id, whose element is the sector's climate. This module lets a `raise` name **which
species** from the sector's pool, **how many units**, and **which role** — which is also how the `Bearer`
role first appears in real play.

Success looks like: a raise with none of the new fields behaves byte-identically to today; a legal raise
founds exactly the stack it names and spends exactly its price; an illegal one is dropped with a named
reason; replay derives the same entity and member ids.

## Scope and non-goals

- **In:** three optional payload fields; the pool rule; per-unit pricing; three drop reasons; the gate on
  counts above one.
- **Out:** adding units to an **existing** legion (no reinforce command exists; a later module); raising
  uniques (they `attach`, `legion-commander`); which empire a raised general reads (Q2 — the owning
  legion's, `general-member-hub`); sector-specific units raised, trained or hired through a building (round 4
  §U: a future unit-system program, recorded so it is not lost).

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | `raise` resolves in `Snapshot`; every legality check is resolution-time; admission only checks a sector was named | `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:8-19`; `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:82-87` |
| Built | One raise per sector per turn; spends `RaiseCostPoints` from `RecruitStock` | `RaiseResolver.cs:24-33,84-90` |
| Built | Entity id derived from cause: `e-{faction}-legion-{turn}-{sector}` | `RaiseResolver.cs:93-96` |
| Built | One `Fighter`, level 1, `Hp = RaiseMemberHp` | `RaiseResolver.cs:124-142` |
| Built | Species = first zombie-side species of the climate element, by id | `RaiseResolver.cs:157-170` |
| Built | Tunables `raiseCostPoints`, `raiseMemberHp` (`growth` section) | `gk-core/src/FusionRpg.Core/World/WorldTuning.cs:148-149`; `gk-core/src/FusionRpg.Core/World/Growth/RecruitPolicy.cs:38,45` |
| Built | Commands persist as `payload_json`, so a payload field is additive storage | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:21-28` |
| Built | Wire: request DTO and the `/commands` mapping | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:518`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:122-138` |
| Real gap | No species, count or role parameter | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:140-220` |

## Design

### 1. Payload

`WorldCommand` gains three optional fields, used only by `raise`:

| Field | Type | Meaning when absent |
|---|---|---|
| `RaiseSpeciesId` | `string?` | today's pick (first of the pool) |
| `RaiseCount` | `long?` | 1 |
| `RaiseRole` | `string?` (`WorldEntityMemberRole` by name) | `Fighter` |

Named `Raise*` so they cannot be mistaken for `InstanceId`/`SpeciesId` of another kind — the
`ward`/`bind-warden` collision the command file already records (`WorldCommand.cs:43-49`) is the reason.

### 2. The pool — one function (owner Q6)

```csharp
// RaiseResolver.cs
public static IReadOnlyList<string> PoolFor(WorldSector sector, WorldFactionKind raiser)
    // ordered by (side, SpeciesId), ordinal; duplicates removed
```

The pool is the union of two sets, both filtered by `ElementPrimary` equal to the sector's climate (`Dark`
for a climate-less sector), because it is still **the sector's** pool — Q6 widens the side, not the
geography:

1. **The sector's species pool** — exactly today's rule: zombie-side species of the climate
   (`RaiseResolver.cs:157-170`).
2. **The raising faction's own side** — species whose `Side` is `SideOf(raiser)`.

`SideOf` is a closed table beside `FactionKindCatalog` (a fixed set, not content:
`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:20-30`), decided from what each kind is:

| Faction kind | Own side | Why |
|---|---|---|
| `Player` | `plant` | Dave (`FactionKindCatalog.cs:9`) |
| `Rival` | `plant` | *"A rival summoner — the mirror, running the same rules"* (`:14`) |
| `Zomboss` | `zombie` | the enemy empire's own roster |
| `Clan`, `Wild` | none | neutral; their pool is the sector pool only |

Pinned as a closed vocabulary (a sixth faction kind states its side in the same change). For `Zomboss` the two
sets coincide, so its raises are unchanged. **The default is unchanged by construction:** with no
`RaiseSpeciesId`, the species is the first entry of set 1 (`?? "normalzombie"`), exactly today's pick — the
own-side species are reachable only by naming them. With Q2 (a legion reads its owning empire's layer 2b), a
player's plant legion reads the player's own plant progression, which the lawn already earns — the
"sits at species baseline" consequence Q2 accepted for zombie legions does not apply to them.

### 3. Resolution (inside `RaiseResolver.Run`, after today's checks)

In order, each a `CommandDropped` with its reason, before any write:

| Check | Reason |
|---|---|
| `RaiseSpeciesId` set and not in `PoolFor(sector, raiser)` | `raise.species-not-in-pool` |
| `RaiseCount` < 1 | `raise.bad-count` |
| `RaiseCount` > 1 while `StackCombatantLanded` is `false` | `raise.stack-unavailable` |
| `RaiseRole` not `Fighter` or `Bearer` (a `Commander` is attached, never raised) | `raise.bad-role` |
| `RecruitStock` < `RaiseCostPoints × RaiseCount` (checked) | `raise.cannot-afford` (today's reason) |

Admission gains only shape checks (count parses, role is a known name) so a malformed wire order is
refused at submit, the same split every kind uses.

### 4. What is founded

One legion, one member: `MemberId = "m0"` (`member-stack` §2), `SpeciesId` = the named or default
species, `Level = 1`, `Hp = RaiseMemberHp` (per unit), `Wounds = 0`, `Count = RaiseCount`,
`Role = RaiseRole`. Stock spent: `RaiseCostPoints × RaiseCount`. The entity id is unchanged.

### 5. The `Count > 1` gate

`CrossProgramLandedFlags.StackCombatantLanded` (`gk-core/src/FusionRpg.Core/Actions/CrossProgramLandedFlags.cs`,
the `const bool` discipline at `:10`) starts `false` and is flipped by `stack-combatant` in the commit
that proves stack scaling. Until then a stack could not fight as a stack, so none may be raised.

## Tunables

None new. `raiseCostPoints` becomes the **per-unit** price — the same number, the same file, a stated
change of meaning (a raise of 1 costs what it costs today). `raiseMemberHp` is the per-unit HP. The map's
§6 entry *"raise size pricing per recruit"* is therefore satisfied by the existing key, not a new one.

## Numeric types

`RaiseCount`, the price product and `RecruitStock` arithmetic are `long`, `checked`, widened before
multiplying. No upper bound on count: the stock is the only limit, which is a price, not a cap.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Raise"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldCommandRoundTrip"
cd gk-web/web/fusion-rpg-web; npm test
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs           MODIFIED  three optional fields
gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs  MODIFIED  shape checks on the raise arm
gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs        MODIFIED  PoolFor, checks, founding
gk-core/src/FusionRpg.Core/Actions/CrossProgramLandedFlags.cs   MODIFIED  StackCombatantLanded = false
gk-core/src/FusionRpg.Contracts/WorldDtos.cs + Server/WorldEndpoints.cs  MODIFIED  wire fields
gk-web/web/fusion-rpg-web contract + fixture                   MODIFIED  additive fields
```

## Testing strategy

- **Default identity.** A raise with no new fields produces the same entity, member, stock and report
  line as today; `RaiseThreadingTests` and the E2E sector-development suite pass unchanged.
- **Each drop reason** has its own test, and a dropped raise writes nothing (stock, entities).
- **Legal raise.** Named species from the pool, count 7 (with the flag forced on in the test's own
  configuration seam, or after `stack-combatant` lands), role `Bearer`: exactly one row, `Count = 7`,
  `Role = Bearer`, stock reduced by exactly `7 × RaiseCostPoints`.
- **Pool.** `PoolFor(sector, raiser)` returns the climate-matching zombie-side set plus the raiser's
  own-side set, deduplicated, in ordinal order; for `Zomboss`, `Clan` and `Wild` it equals today's set; the
  default pick is today's (a property test over all six climates, the climate-less case and every faction
  kind). `SideOf` is pinned as a closed table.
- **Round trip.** `WorldCommandRoundTripPropertyTests` covers the three fields.
- **Replay.** A logged raise with the new fields replays to the same ids.

## Boundaries

- **Always:** price per unit through the existing key; decide the pool in `PoolFor` only.
- **Ask first:** a reinforce command; raising above level 1; any sector-specific unit rule (that is the
  future unit-system program, round 4 §U).
- **Never:** a cap on count; a second species-selection rule anywhere else.

## Success criteria

1. Default raises unchanged; named raises exact; illegal raises dropped with named reasons.
2. `Bearer` producible in play.
3. No `Count > 1` before `stack-combatant`.

## Interface exposed to dependents

`PoolFor`, the raise payload — consumed by the FE raise surface (a later UI module), `fleet` (raising
bearers for caravans and crews).

## Hard edges

- **Command payload addition** — contract fixture and `CONTRACT_VERSION` unaffected (additive).
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave** (owner decision C1, 2026-09-20): a world's rules never change mid-life, and the family keeps a single landing order in [landing-order.md](../trade-network/landing-order.md). The bump is taken at landing, never pre-assigned (map *Audit 2026-09-20* R1). This module is **wave 2** and grants a player-facing feature (choosing species
  and stack size when raising), so it rides **wave 2's single bump** rather than claiming none. ~~No world
  `RulesetVersion` bump: the new fields exist only on new commands …~~ — that reasoning still explains why
  **no stored command log carries them, no world is migrated and no golden moves** (the
  `TurnEngine.cs:134-140` command-only precedent).
- **No golden re-bless.**

## Dependencies

`member-stack` (`Count`, `MemberId`); `stack-combatant` flips the gate.

## Closed by round 4

The former "Left open" item — whether the pool includes the raising faction's own side — is decided by the
owner (Q6, 2026-09-19): yes, own side plus the sector pool (§2).

## Design-gate checklist

```
[x] Subsystems: world commands, recruitment, world wire.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: map, ideal, DESIGN-GATE, PRINCIPLES §3-§13, empire-resource-ssot.md §3 recruit
    row. NOT read: world-map row documents, spec-sector-development.md.
[x] decisions.md checked: no lock on raise parameters.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: RaiseResolver (whole), admission arm, WorldTuning keys, payload_json storage.
[x] Read the surrounding section of every rule quoted.
[~] No suite run; default-identity is an acceptance test.
[x] No §2 invariant contradicted; no cap (stock is a price).
[x] Corrections propagated (map §10: pricing reuses the existing key).
[x] No population count pinned; the role set is WorldEntityMemberRole (closed).
[x] No cache.
[x] No ordering assumption beyond today's one-raise-per-sector rule.
[x] No actor magnitude.
[x] No parallel path.
[x] No new rule needing a registry row.
```

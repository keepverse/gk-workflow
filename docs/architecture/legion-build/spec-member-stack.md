# Spec: `member-stack`

**Status: written against shipped code 2026-09-19** — every `file:line` below was opened this session on
branch `features/mega-merge`. Module id `member-stack`, row 1 of the
[legion-build map](../legion-build-map.md) (wave 1; depends on external `trade-network` `trade-foundation`).
Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.1, owner decision **L4** (stack `Count` lands
now). House style: [spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

Today a legion member row is one creature: `Hp`, `Wounds`, `Role`, no count
(`gk-core/src/FusionRpg.Core/World/WorldState.cs:277-286`). A legion at army scale cannot be one row per creature
(`creature-system-map.md` Vocabulary, Axis 1). This module makes a member row a **stack**: a species ×
a living **count**, with a stable **member id** that survives battles and reordering, and moves every
place that counts heads from "rows" to "Σ count".

Success looks like: a world whose every row has `Count = 1` resolves and hashes exactly as today (the new
fields are emitted only when not their default — audit 2026-09-20, §6); a world with a stack of 40 burns,
upkeeps, carries, recovers and is sized by the AI exactly as the same world expanded to 40 one-unit
rows would be.

**Who uses it:** every later module in this program. Standards and legion equipment bind to a member by
`MemberId` (L4: *"before standards bind to member rows"*); `stack-combatant` fights the count;
`raise-choice` produces counts greater than one.

## Scope

- `Count` (living units) and `MemberId` on `WorldEntityMember`, persisted, hashed, on the DTO and the web
  contract.
- The HoMM3 top-unit arithmetic in **one** pure function, used by every world site that turns HP into
  units or units into HP.
- Every headcount site reads `Σ Count`.
- The saved-world migration.

## Non-goals

- **How a stack fights.** Output scaling, overflow down the stack inside a battle and the unit count a
  battle reports are `stack-combatant`'s (Q1, a battle-engine mechanism). This module only translates a
  battle's reported HP back into `Count`/`Wounds` — outcome arithmetic, the same job
  `BuildSideOutcome` does today.
- **Producing a count above one.** `raise-choice` does that, gated behind `stack-combatant` (see Hard
  edges). Nothing this module ships creates a stack of more than one unit.
- Merging and splitting stacks. No command does either; a later module may add one as its own reviewed
  change.

## Locked anchors

- **`Hp` is per-unit HP; `Wounds` is damage on the top unit only; `Count` is living units** (map
  assumption 2). This is the HoMM3 shape the `decisions.md` *Deployment hierarchy SSOT* row already names
  for troop stacks — *"HoMM3 top-unit count arithmetic only, no per-unit wounds, no inventory"*
  (`docs/architecture/decisions.md:46`). A row with `Count = 1` means exactly what every row means today.
- **A member row is never a unique creature list.** Uniques ride along through `InstanceId`
  (`WorldState.cs:279-280`); a row with an `InstanceId` always has `Count = 1`, enforced by
  `WorldValidation` (a unique specimen is one creature).
- **Battle actor keys stay index-based.** `DistrictAssaultResolver` keys an actor `{entityId}:{i}`
  (`gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:425,515`) and uses the index only inside one
  resolve. `MemberId` is the identity **across** turns; the in-battle key does not change, so no battle
  report byte moves because of this module.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Member row: `InstanceId?`, `SpeciesId`, `Level`, `Hp` (`long`), `Wounds` (`int`), `Role` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:277-286` |
| Roles `{Fighter, Bearer}` | `WorldState.cs:271-275` |
| Table keyed `(world_id, entity_id, member_index)`; `role` added through `EnsureColumn` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:121-131,171` |
| Member rows hashed positionally: `member, entityId, i, InstanceId, SpeciesId, Level, Hp, Wounds, Role` | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:64-68` |
| Diff writer deletes/replaces by `member_index` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:393-415` |
| DTO carries `InstanceId, SpeciesId, Level, Hp, Wounds (int), Role` | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:313-324`; mapping `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:1001-1013` |
| Outcome arithmetic: survivors rebuilt as a new list, dead rows dropped, so `member_index` shifts | `DistrictAssaultResolver.cs:507-541` (`newWounds` at `:531-532`) |
| Raise ids derived from cause, not a counter | `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:93-96` |

### Wiring gap (every headcount reads rows, not units)

| Site | Today | After | Evidence |
|---|---|---|---|
| `LegionSupply.BearerCount` | `Members.Count(m => m.Role == Bearer)` | `Σ Count` over bearers | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-17` |
| `LegionSupply.Burn` | `Members.Count × BurnPerMember` | `Σ Count × BurnPerMember`, `checked` | `LegionSupply.cs:24-25` |
| `LoamUpkeep` garrison | `.Sum(e => e.Members.Count)` into an `int garrisonMembers` | `Σ Count`, parameter widened to `long` | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:61-63,90,97,100` |
| AI garrison sum | `.Sum(e => e.Members.Count)` | `Σ Count` | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:191` |
| AI wound ratio | `WoundedMilli` sums per row | pool arithmetic over `Count` | `FrontierRulesPolicy.cs:330-345` |
| Banner element vote | `+1` per row | `+Count` per row, `long` weights, ties still by ring order | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:67-93` |
| Intel strength | `Σ (Hp − Wounds) × Level` per row | `Σ EffectivePool × Level` | `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:15-24` |
| Recovery | heals each row's `Wounds` by 150‰ of `Hp` | heals the **top unit** only, never raises `Count` | `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:158-173` |
| Cargo capacity count | `SELECT COUNT(*)` rows, returned `int` | `SELECT SUM(count)`, `long` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:89-97,102,106` |
| Cargo capacity math | `SlotCapacityFor(int)`, `int` result on the premise *"a legion's realistic member count is small"* | `long` in, `long` out, `checked`; the premise comment removed | `gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs:27-47` |
| Battle entry HP | `effectiveHp = Hp − Wounds` per row | `StackArithmetic.EffectivePool` (identical for `Count = 1`) | `DistrictAssaultResolver.cs:421-422,438` |
| Battle outcome | `newWounds = Hp − HpRemaining` | `StackArithmetic.FromPool` → `(Count, Wounds)`; `Count = 0` drops the row | `DistrictAssaultResolver.cs:531-532` |

Sites that read `Members.Count` as **row presence** and stay as they are: `WildSpawnRoller`
(`gk-core/src/FusionRpg.Core/World/Loam/WildSpawnRoller.cs:54`), the loop bounds at
`DistrictAssaultResolver.cs:418,512` and `WorldCanonical.cs:64`.

### Real gap

- No count, no stable member identity. `member_index` is the key (`RpgStore.World.cs:124,130`) and a
  battle renumbers it.
- `Wounds` is `int` while `Hp` is `long` (`WorldState.cs:283-284`), and `BuildSideOutcome` narrows with
  `checked((int)newWounds)` (`DistrictAssaultResolver.cs:532`). A top-unit wound can be as large as the
  unit's HP, which is a `P(Θ)` magnitude, so the field is the wrong width.

## Design

### 1. The row

```csharp
public sealed record WorldEntityMember
{
    public string MemberId { get; init; } = "";   // stable within the legion; see §2
    public string? InstanceId { get; init; }
    public string SpeciesId { get; init; } = "";
    public int Level { get; init; } = 1;
    public long Hp { get; init; }                  // PER-UNIT HP (unchanged meaning for Count = 1)
    public long Wounds { get; init; }              // damage on the TOP unit only; widened from int
    public long Count { get; init; } = 1;          // living units; 0 never persists (row removed)
    public WorldEntityMemberRole Role { get; init; } = WorldEntityMemberRole.Fighter;
}
```

`WorldValidation` gains three rules: `Count ≥ 1`; `0 ≤ Wounds < Hp`; a row with an `InstanceId` has
`Count = 1`; `MemberId` unique within its entity.

### 2. `MemberId`

`m{n}`, `n` a non-negative integer. Deterministic from its cause, the `RaiseResolver.cs:93-96` idiom:

| Cause | Id |
|---|---|
| Template construction | `m{i}` — the row's index in the template literal |
| `raise` | `m0` — a raise founds a new legion |
| Any later addition to an existing legion (`attach`, a future merge) | `m{max(n)+1}` over the legion's current ids |
| Migration of a saved row | `m{member_index}` — the same answer a fresh world from the same template gives |

A battle, a recovery or a reorder never assigns an id. Dead rows leave gaps; ids are never reused within
a legion, because "the next id" is computed from the maximum, not the count.

### 3. `StackArithmetic` — the one place units and HP convert

`src/FusionRpg.Core/Battle/StackArithmetic.cs` (new; the file does not exist yet). It lives under `Battle/` because
`stack-combatant` makes it the SSOT of register row 21 and the engine calls it too; world code already
references `FusionRpg.Core.Battle` (`DistrictAssaultResolver.cs:3`).

```csharp
public static class StackArithmetic
{
    // (Count − 1) × Hp + (Hp − Wounds). checked: overflow throws, never wraps.
    public static long EffectivePool(long count, long unitHp, long wounds);

    // The inverse: living units and top-unit wounds for a remaining pool.
    // count = ceil(pool / unitHp); wounds = count × unitHp − pool. pool ≤ 0 → (0, 0).
    public static (long Count, long Wounds) FromPool(long pool, long unitHp);

    // Heal the top unit by `amount`, never above unitHp, never raising Count.
    public static long HealTop(long unitHp, long wounds, long amount);
}
```

All three are `checked`, widen before multiplying, and have no divisor except `FromPool`'s ceiling
division by `unitHp` (a unit HP of 0 is a `WorldValidation` rejection, so the divide is total).

### 4. Outcome translation

`BuildSideOutcome` enters each row with `EffectivePool(Count, Hp, Wounds)` (identical to today's
`Hp − Wounds` at `Count = 1`) and turns the reported `HpRemaining` back with `FromPool`. A row with
`Count = 0` is dropped; the survivors keep their `MemberId`. **Until `stack-combatant` lands** a row with
`Count > 1` never reaches a battle (Hard edges), so this module's battle behaviour is exactly today's.

### 5. Headcount sites

Each site in the wiring-gap table reads through two helpers on `WorldEntity` so no site re-derives the
sum:

```csharp
public static long Units(this WorldEntity e) => checked(e.Members.Sum(m => m.Count));
public static long Units(this WorldEntity e, WorldEntityMemberRole role) => /* same, filtered */;
```

`BannerElement` weights each element by `Count` with `long` counts; ties still break by the ring's
declared order (`LaneCost.cs:81-90`), so reordering never changes the banner.

### 6. Persistence, hash, wire

- **Schema.** Two `EnsureColumn`s on `rpg_world_entity_members`: `count INTEGER NOT NULL DEFAULT 1` and
  `member_id TEXT`, then a one-time, idempotent backfill `member_id = 'm' || member_index` where it is
  `NULL`, then `CREATE UNIQUE INDEX IF NOT EXISTS ux_world_member_id ON rpg_world_entity_members(world_id,
  entity_id, member_id)`. `member_index` stays the storage order and primary key.
- **Hash — emitted only when not the default (corrected by the 2026-09-20 audit).** The first draft
  appended `Count` and `MemberId` to every `member` row, moving every world's hash once. That is not
  needed, and it costs every saved world the replay of its whole history (the `RulesetVersion` bump makes
  the store refuse to re-derive every older turn, `RpgStore.WorldTurns.cs:759-760`). Map §10 S1 already
  names the precedent: state is hashed only when present (`WorldCanonical.cs:71-72`). So the `member` row
  (`WorldCanonical.cs:67`) appends `count=<n>` **only when `Count != 1`** and `id=<MemberId>` **only
  when `MemberId != "m{i}"`** (`i` the row's position, the id the migration backfills). Both defaults are
  exactly what every row stored today reads back, so every existing world hashes byte-identically; the
  encoding stays injective because an absent field has one fixed meaning. A battle that removes an
  earlier row makes a survivor's id differ from its new position, and that row then carries `id=` —
  deterministic, and only in worlds where a battle already moved the bytes.
- **Wire.** `WorldEntityMemberDto` gains `MemberId` and `Count`; `Wounds` widens to `long`. Additive for
  the web contract (`gk-web/web/fusion-rpg-web/src/contract/types.ts`, `adapt.ts`, fixtures); `Wounds` was
  already a JSON number.

## Tunables

None new. Every existing number keeps its file: `BurnPerMember`, `CarryPerBearer`,
`GarrisonUpkeepPerMember` (`loam.v{n}.json`), `CargoWeightPerUnit`/`CargoSlotsPerUnit`
(`scoped-inventory.v1.json`), `RecoveryMilli` (a `const` today at `LaneCost.cs:44`, untouched). Per-member
constants become per-**unit** constants by meaning, with no value change.

## Numeric types

`Count`, `Wounds`, pools, `Units()` and every product are `long`, `checked`, widened before multiplying
(`PRINCIPLES.md` §5). A pool is `Count × unit HP`; with unit HP a `P(Θ)` magnitude, it passes `int` long
before it passes `long`, so `int` is wrong at modest counts. `LoamUpkeep`'s `garrisonMembers` and the
cargo slot capacity move from `int` to `long` for the same reason, and the structural-bound comment on
`CargoSlotsPerUnit` (`ScopedInventoryPolicy.cs:27-31`) is removed because stacks remove its premise.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~World|FullyQualifiedName~LegionCargo"
cd gk-web/web/fusion-rpg-web; npm test
python gk-core/scripts/audit-overflow.py --targets A3
python gk-core/scripts/guard-dal.py
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                    MODIFIED  Count, MemberId, Wounds long
gk-core/src/FusionRpg.Core/World/WorldValidation.cs               MODIFIED  four row rules (§1)
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs                MODIFIED  member row appends count/id only when non-default
src/FusionRpg.Core/Battle/StackArithmetic.cs              NEW       §3
src/FusionRpg.Core/World/WorldEntityUnits.cs              NEW       Units() helpers (§5)
gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs             MODIFIED  BearerCount, Burn
gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs               MODIFIED  Σ Count, long parameter
gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs        MODIFIED  :191, WoundedMilli
gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs             MODIFIED  BannerElement weights
gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs            MODIFIED  ForceStrength
gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs          MODIFIED  Recover heals top unit
gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs MODIFIED long capacities
gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs  MODIFIED  entry pool + outcome (outcome only)
gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs          MODIFIED  MemberId per template row
gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs          MODIFIED  MemberId = m0 (no behaviour change)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs               MODIFIED  columns, backfill, index, read/write
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs      MODIFIED  write both columns
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs         MODIFIED  SUM(count), long
gk-core/src/FusionRpg.Contracts/WorldDtos.cs + Server/WorldEndpoints.cs  MODIFIED  DTO fields
gk-web/web/fusion-rpg-web/src/contract/{types,adapt}.ts + fixtures  MODIFIED  additive fields
(TurnEngine.cs is modified only where wave 1's shared RulesetVersion bump lands — round 6 C1; this module
 moves no golden: audit 2026-09-20, Hard edges)
```

## Testing strategy

- **Expansion property.** For generated worlds, expand every stack to `Count` one-unit rows (wounds on the
  top unit's row, full HP on the rest) and assert every headcount function returns the same value on both
  worlds: `BearerCount`, `Burn`, garrison upkeep, the AI garrison sum, `WoundedMilli`, `ForceStrength`,
  cargo capacity, `BannerElement`. Order-independent: shuffle member order on both sides.
- **Arithmetic.** `FromPool(EffectivePool(c, h, w), h) == (c, w)` for all valid inputs; `FromPool` of 0
  and of negatives is `(0, 0)`; overflow throws; `HealTop` never exceeds `unitHp` and never changes
  `Count`.
- **Identity.** `MemberId` survives a battle that kills an earlier row, a recovery and a reorder; a new
  member takes `m{max+1}` even after gaps; migration gives `m{member_index}`, identical to a fresh world
  from the same template.
- **Byte identity.** A `Count = 1` world whose ids are the backfilled `m{i}` resolves every turn golden to
  the same outcomes **and the same canonical bytes** as before — no stripping, no re-bless. A world with a
  `Count = 2` row, and one whose surviving row's id differs from its position, each emit exactly the
  non-default field (two tests).
- **Migration.** Load a pre-module database: columns added, backfill idempotent (run twice), unique
  index holds, world loads and resolves.
- **Validation.** Each of the four new `WorldValidation` rules rejects with its own reason.

## Boundaries

- **Always:** read heads through `Units()`; convert HP and units only through `StackArithmetic`; keep
  `MemberId` deterministic from cause.
- **Ask first:** any stack merge/split command; changing `RecoveryMilli` semantics beyond "top unit".
- **Never:** produce `Count > 1` in this module; key anything durable by `member_index`; per-unit rows or
  per-unit item rows for a stack (`deployment-hierarchy-ideal.md:175`).

## Success criteria

1. Every headcount site in the wiring-gap table reads `Σ Count`, proven by the expansion property.
2. `Count = 1` worlds resolve and hash identically; no golden is re-blessed (audit 2026-09-20).
3. `MemberId` is stable across battle, recovery and reorder, and unique within a legion.
4. Saved worlds migrate idempotently.
5. `audit-overflow.py --targets A3` reports no new `int` magnitude on these paths.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `WorldEntityMember.Count`, `.MemberId` | every module in this program; `fleet` (bearer counts); `crew` |
| `StackArithmetic` | `stack-combatant` (registers it as the SSOT of register row 21) |
| `WorldEntity.Units(role?)` | `legion-cohesion`, `legion-count-cost`, `legion-equipment`, `fleet` |

## Hard edges

- **The Count migration.** Two columns, a deterministic backfill and a unique index, in one
  transaction, idempotent. Saved worlds are migrated under `trade-foundation`'s `world-stamp`
  (`docs/architecture/trade-network/trade-foundation-map.md` §2.4): a world whose stored turn logs were
  hashed under the old `RulesetVersion` refuses to re-derive them, which is the existing behaviour the
  counter exists for (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:108-111`, the version-2 note).
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave** (owner decision C1, 2026-09-20): a world's rules never change mid-life, and the family keeps a single landing order in [landing-order.md](../trade-network/landing-order.md). The bump is taken at landing, never pre-assigned (map *Audit 2026-09-20* R1). This module is **wave 1**, and it grants a player-facing feature (stacks with a
  `Count`), so it does **not** claim "no bump": it rides **wave 1's single bump**, and a world stamped before
  wave 1 never gains stacks mid-life (`trade-foundation/spec-world-stamp.md` §2). What the 2026-09-20 audit
  actually removed was the **golden re-bless**, and that still holds — see the next bullet.
- **Golden re-bless — none (audit 2026-09-20); the bump is the wave's (round 6 C1).** With the new fields emitted only
  when not their default (§6), no stored world's bytes change, and no stored command log can produce
  `Count > 1` (only `raise-choice`'s new optional field can, and no stored log carries it — the
  `TurnEngine.cs:134-140` command-only precedent). The first draft's bump to the next value (13 today,
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`) is superseded by round 6 C1 — the wave's one bump, not
  this module's own — and its re-bless stays withdrawn. **The saved-world
  migration still happens** (columns, backfill, index — first bullet) and still orders after
  `trade-foundation` `world-stamp`, so a migrated world's stamp is recorded before its rows change shape.
- **The gate on `Count > 1`.** No module may produce a count above one until `stack-combatant` lands;
  `raise-choice` enforces it through a `CrossProgramLandedFlags`-style `const bool StackCombatantLanded`
  (`gk-core/src/FusionRpg.Core/Actions/CrossProgramLandedFlags.cs`, its own discipline at `:10`).
- **Cross-doc requirement (not made here).** `deployment-hierarchy-map.md:106` says troop representation
  stays *"`Hp/Wounds` headcount, unchanged"*. Owed wording: *"`Count` living units, per-unit `Hp`,
  top-unit `Wounds` — the HoMM3 shape of the Deployment hierarchy SSOT row; `Count = 1` is today's row."*
  Filed to the `deployment-hierarchy` program.

## Dependencies

- External `trade-network` `trade-foundation` → `world-stamp` (saved-world migration record).
- Nothing in this program.

## Design-gate checklist

```
[x] Subsystems: world map (legions, turn, supply, cargo, intel, AI), world persistence and hash, the
    world DTO and web contract. No actor number produced or consumed.
[ ] Session boundary — NOT recorded. Docs-only spec session scoped by its caller; no tasks/sessions record,
    session-boundary-check.py not run. The implementing session must record one.
[~] Read this session: DESIGN-GATE.md (whole), PRINCIPLES.md §3-§13, legion-build-map.md and
    legion-build-ideal.md (whole), actor-layer-compose-ideal.md (whole), actor-hub-ssot.md §1-§2 and
    §6-§13, battle-engine-ssot.md (whole), creature-system-map.md Vocabulary + amendments,
    effect-atom/definitions.md §0-§6, spec-budget-debit.md, decisions.md rows Deployment hierarchy SSOT
    and Actor layer stack. NOT read: the world-map row's own documents (world-map-program.md,
    world-map-runtime-*), data-architecture.md.
[x] decisions.md checked: Deployment hierarchy SSOT names the HoMM3 top-unit shape for troop stacks.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: WorldState, WorldCanonical, RpgStore.World, RpgStore.LegionCargo,
    ScopedInventoryPolicy, LegionSupply, LoamUpkeep, FrontierRulesPolicy, LaneCost, FactionIntel,
    SupplyGraph, DistrictAssaultResolver, RaiseResolver were each read.
[x] Read the surrounding section of every rule quoted.
[~] Constraints stated, not measured: "Count = 1 resolves identically" and "only the two fields move the
    hash" are acceptance tests the implementer runs; no suite was run for this spec.
[x] No §2 invariant contradicted. No cap: counts are unbounded long; structural checks throw.
[~] Corrections propagated: map §10 records this spec's corrections; the deployment-hierarchy wording is
    listed as owed, not made (another program's document).
[x] No population count pinned. Closed vocabularies pinned: none added here.
[x] No event-refreshed cache introduced (headcounts are computed per read).
[x] Order-independent criteria: the expansion property shuffles member order on both sides.
[x] No actor combat/derived magnitude produced or consumed.
[x] No SOLID-violating parallel path: one StackArithmetic, one Units() helper, no second pricer.
[ ] Enforcement-registry row: owed — "headcounts read Units(), never Members.Count" needs a guard (a
    source scan of World/** for `Members.Count` outside the allowlisted row-presence sites) or an
    unguardableReason. Written by the implementing change.
```

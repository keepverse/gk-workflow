# Spec: `sector-features`

**Status:** written 2026-09-19 (round-4 reconciliation) against `features/mega-merge`. Every `file:line`
below was opened in this session. Module §2.11 of the [trade-foundation map](../trade-foundation-map.md),
added to carry owner principle **B** of [../decisions-round-4.md](../decisions-round-4.md) (*"To unlock a
feature in a sector, we should have the correct building … Tiers are `variants` of one structure row …
A feature with no unlocking building in the sector is not available there."*).
**Round 5 (2026-09-20)**, [../decisions-round-4.md](../decisions-round-4.md) R5-X: **X1** — every feature
gate in every program reads this module (`TierOf` per sector, `FactionTier` per faction); a new
`StructureKind` only where loam or siege rules need one. **X8** — the upgrade verb is `build` on the
building's own slot (§4). **X13** — `sector-yield` reads the Counting House and Storehouse tiers here.
**B1/B2** — a structure row may allow more than one slot kind (Trading Post: Wildland or Market; Rift
Anchor: Wildland with a bonus beside a rift-tear slot); that is the row's and `BuildResolver`'s slot rule,
not a tier rule, and changes nothing in this module (see §4 note).

**Asked for by:** `exchange` (E-A14 and cross-cluster conflict X-1 in [../exchange-map.md](../exchange-map.md):
*"one shared building-tier mechanism … recommended `trade-foundation`"*), `fleet` (A11 in
[../fleet-map.md](../fleet-map.md): a `building-tiers` module in `trade-foundation`). Field names follow
`empire-seed` [../../empire-seed/spec-trade-structure-rows.md](../../empire-seed/spec-trade-structure-rows.md)
§5.4 (`featureUnlock`, tier = variant list position + 2).

## Why this module exists, and why here

Principle B is read by seven features in five programs: storage and banking (`sector-yield`), trade
(`exchange`), caravans (`fleet`), cross-world (`rift-trade`), diplomacy (`counterparties`), legion
equipment (`legion-build`). If each program answered "does this sector have the building, and at what
tier" for itself, the repo would have seven readers of one fact — the dual-engine shape SOLID rule S
forbids. The answer is one query over the structure catalog. It lives in `trade-foundation` because
`legion-build` depends on `trade-foundation` and not on `sector-yield` (umbrella §1 row 10), so the one
place every consumer can read without an upward arrow is here.

## Objective

One closed vocabulary of **sector features**, one field on a structure that says which feature it
unlocks, one per-slot tier, and two reads: *the highest active tier of feature F in sector S* and *the
highest active tier of F over every sector faction X owns in a world* (each 0 when there is none). Every
trade and logistics feature gates on those reads and on nothing else.

## Scope and non-goals

**In scope:** the `SectorFeature` vocabulary; `StructureDef.FeatureUnlock`; the per-tier resolution of a
row's `variants`; the slot's tier; the upgrade rule; `SectorFeatures.TierOf` and `FactionTier`.

**Not in scope:** what any feature does at any tier (each consumer's spec); the rows and their names and
bands (`empire-seed` `trade-structure-rows`, generated, never hand-edited); a unit-raising building (round
4 §U: a future unit program).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| A slot holds one structure id and a construction counter | `gk-core/src/FusionRpg.Core/World/WorldState.cs:96`, `:119`, `:126` |
| `build` refuses an occupied slot | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:69-73` |
| `build` checks one required slot kind per structure | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:82-89` (`structure.RequiredSlotKind`) |
| The structure catalog: `StructureDef`, `Get`, `IsKnown` | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:47`, `:330-333` |
| Only corpus rows with a `magnitudes` block load | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65` |
| A tier chain is a `variants` list on one row, at most four; no row authors one yet | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:48-54` |
| Every shipped anchor carries an empty `anchor.variants` | `gk-data/packs/fusion/data/seed/structures/bank/soul-conduit.json` (`entries[0].anchor.variants`) |
| Conditional canonical rows keep old hashes byte-identical for a new slot field at its default | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:113-115` (`slot-hp`, `slot-depletion`) |

### Wiring gap

`anchor.variants` is parsed by the generator and ignored by Core: no `StructureDef` field reads it
(no match for `variant` under `gk-core/src/FusionRpg.Core/World/StructureSeed/`).

### Real gap

No feature vocabulary, no tier on a slot, no upgrade, no query.

## Design

### 1. The vocabulary (closed, nine members)

`SectorFeature` (wire names; the C# enum member is the PascalCase form, e.g. `cross-world` ↔ `SectorFeature.CrossWorld` — never `cross-world`) — `none`, `storage`, `banking`, `trade`, `caravans`, `cross-world`, `diplomacy`,
`legion-equipment`, `standards` — `empire-seed`'s `featureUnlock` vocabulary exactly (`spec-trade-structure-rows.md`
§5.4), which is round-4 table B plus round 6 L6's eighth building plus `none`. Pinned in a test with the
reason: *a new member is a new building-gated feature and a reviewed change to the round-4 register*. Each
feature records its maximum tier from the table (storage 3, banking 3, trade 4, caravans 2, cross-world 1,
diplomacy 2, legion-equipment 3).

**`standards` is round 6 L6.** *"Does forging a standard need a building — **Yes, its own building kind** —
a Standard Hall, with tier variants gating the standard tier (an eighth kind in the building ladder; tiers
are variants of one row, as for every other building)"*
([../decisions-round-4.md](../decisions-round-4.md) Round 6 L6). The member and its row follow every rule
above: one row with tier variants, `StructureKind.Feature` like the other seven (§Boundaries), gated
through `TierFor`. Its **maximum tier is `legion-build`'s to state** — it equals the number of standard
tiers `legion-standards` defines — so it is an ask to that program, not a number invented here; until that
number lands the row ships with the tiers its variants carry and the maximum is asserted per row, never by
count.

### 2. The field and the tiers

- `StructureDef.FeatureUnlock` (`SectorFeature`, `none` for every row that unlocks nothing), resolved at
  load from the anchor field `featureUnlock` that `empire-seed`'s `band-reader` validates. The name and
  meaning are `empire-seed`'s (§5.4); this module is the field's first reader, so it lands here (the
  "first consumer's change" rule that spec states).
- `StructureDef.Tiers` — tier 1 is the row itself; tier *n* ≥ 2 is `anchor.variants[n − 2]` (the tier is
  the list position, never a field — `empire-seed` §5.4). Each tier carries the variant item's ordinals
  (`costProfile`, `strengthBand`, `footprint`), so its cost, HP and size resolve through the existing bands.
  **What a tier does** (capacity, banking rate, clearing, crew, range) is its consuming mechanism's own
  tuning, keyed by tier — never a band on the variant (`empire-seed` §2: *"What each tier does is the
  consuming mechanism's"*).
- A row whose feature is `none` uses no variant as a tier (a load rejection), and no row has more tiers
  than its feature's maximum.
- One row per feature: the round-4 names (Storehouse → Warehouse → Granary Complex, Counting House →
  Treasury → Vault, …) are the row's and its variants' display names, never separate rows.

### 3. The tier on a slot

`WorldSlot.StructureTier` (`int`, default 1). Canonical form: a conditional `slot-tier` row written only
when the tier is above 1, after `slot-depletion` — so every existing world hashes byte-identically.
Persisted as one additive column on the slot row, in the same change as the field (the rubble lesson,
`RpgStore.World.cs:180-188`).

**What the field means while something is being built (audit 2026-09-20).** `StructureTier` is the
**target** tier of the structure on the slot; `ConstructionTurnsRemaining > 0` means that target is not
active yet. So a first build is `(tier 1, counter > 0)` and an upgrade from *n* to *n + 1* is
`(tier n + 1, counter > 0)` — the one existing counter serves both, and the two cases are told apart by
the tier, not by a second field. The **active** tier is read through one function, and every reader
(`TierOf`, `sector-yield` `warehouse-axis`, `banking-fact`'s rate, every consumer in §5's table) calls it
and never re-derives the rule:

```csharp
public static int ActiveTier(WorldSlot slot) =>                 // 0 = nothing active on this slot
    slot.StructureId is null ? 0
    : slot.ConstructionTurnsRemaining is > 0 ? slot.StructureTier - 1
    : slot.StructureTier;
```

**Clearing or replacing a structure resets the tier.** Every site that sets `StructureId` to null or to
a different structure sets `StructureTier = 1` in the same `with`. Today there are two: a lost sector's
slots are cleared in `Pressure` (`gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:224`), and a district
assault destroys or places a structure (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:165-172`,
`StructureDestroyed` / `StructurePlaced`). Any later demolition path joins the rule. Otherwise a rebuilt
structure would inherit a stale tier and the `slot-tier` row would outlive the building it described.

**Every existing "is this structure active" gate moves to `ActiveTier`.** Today a slot with
`ConstructionTurnsRemaining > 0` is inactive in every reader: loam flat yield and loam storage
(`gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:34`, `:51`; `LoamPhases.cs:92`), item storage
(`gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs:20`), wonder effects
(`gk-core/src/FusionRpg.Core/World/Loam/WonderEmpireEffects.cs:25`), habitability
(`gk-core/src/FusionRpg.Core/World/Loam/Habitability.cs:22-23`) and growth (`gk-core/src/FusionRpg.Core/World/Growth/GrowthPhases.cs:92`).
With the upgrade arm, that reading would switch a building **off** while it is upgraded — the opposite
of §4's *"an upgrade never switches a building off"*. So the change that ships the upgrade arm moves each
of those gates to `ActiveTier(slot) >= 1` in the same commit. For every slot that exists today (tier 1)
the two readings are identical, so no golden moves; they differ only on a slot mid-upgrade.
`LoamPhases.cs:105-111` (the countdown) is not a gate and stays as it is.

### 4. The upgrade

A `build` order naming the structure **already on the slot** raises its tier by one instead of being
refused `build.occupied` (`BuildResolver.cs:69-73`), when the structure has a next tier. It pays the next
tier's cost and runs the next tier's build turns through the existing `ConstructionTurnsRemaining`
counter; during construction the slot keeps working at its current tier (an upgrade never switches a
building off). At the last tier the order is refused `build.max-tier`. One verb, one resolver, no new
command kind. **Round 5 X8 (2026-09-20):** this is the upgrade verb for every building ladder — `build` on
the building's own slot; the `world-map` owner of `BuildResolver` is asked to confirm (a coordination ask,
not an open design question).

*Slot kinds (round 5 B1, B2).* `BuildResolver` compares the slot's kind with one `RequiredSlotKind` per
structure (`BuildResolver.cs:82-89`). A row allowed on several slot kinds (B1's Trading Post on Wildland or
Market, with a Market bonus) needs that field widened to a set — `empire-seed`'s row schema and the
`world-map` resolver's check, coordinated like the upgrade arm. The upgrade arm never re-checks the slot
kind: the building already stands on a slot it was allowed on.

### 5. The query

```csharp
// src/FusionRpg.Core/World/Structures/SectorFeatures.cs (new)
public static int TierOf(WorldSector sector, SectorFeature feature);                        // ground read; 0 = not unlocked
public static int TierFor(WorldSector sector, string factionId, SectorFeature feature);     // the gate read (§5a); 0 = counts for nobody
public static int FactionTier(WorldState world, string factionId, SectorFeature feature);   // max of TierFor over owned sectors
public static int ActiveTier(WorldSlot slot);                                              // §3; 0 = nothing active
public static bool CountsFor(WorldSector sector, WorldSlot slot, string factionId);        // §5a
public static bool Unlocks(StructureDef def, SectorFeature feature);                       // def.FeatureUnlock == feature
```

### 5a. Whose building it is — one faction owns both the sector and the slot (round 6 S1)

A sector and a slot each carry their own owner (`gk-core/src/FusionRpg.Core/World/WorldState.cs:158` for the
sector, `:105` for the slot), and both are nullable — so a slot can be held by a faction that does not
hold the sector around it, and either can be unowned. The owner's ruling:

> **It counts for nobody until one faction owns both.**
> ([../decisions-round-4.md](../decisions-round-4.md) Round 6 S1)

`CountsFor(sector, slot, factionId)` is that rule, and it lives **here**, once:

```
CountsFor = slot.OwnerFactionId == factionId
         && sector.OwnerFactionId == factionId
         && factionId is not null/empty
```

`TierFor(sector, factionId, feature)` is the highest `ActiveTier(slot)` over the sector's slots that
`Unlocks(def, feature)` **and** `CountsFor(sector, slot, factionId)`. `FactionTier` is the max of `TierFor`
over the sectors the faction owns (so it cannot see a contested slot either). Consequences, stated because
each is a real case on the board:

- A captured sector whose slot the loser still holds unlocks **nothing for either side** until the slot
  falls too — no side gets a free feature on the turn a sector flips, and no rule has to pick a winner.
- An unowned (wild) sector's feature building counts for nobody. A clan hub counts for the clan, which is
  what B3's *"the hub's owner also needs a Caravan Yard"* reads.
- **Every feature gate reads `TierFor` or `FactionTier`**, never bare `TierOf`. `TierOf` stays, and stays
  owner-blind, for the ground reads that are not gates: the report, the inspector, the world editor and
  `forecast-facts`' *"build a Counting House here"* answer. A spec that gates on `TierOf` is a defect —
  acceptance covers it.
- The named wrappers (`Hubs.TradeTier`, `DiplomacyGate.TierOf`, the Rift Anchor's Grand-Exchange read,
  `bank-points`, `warehouse-axis`, `depot`, `legion-equipment`) delegate to `TierFor`/`FactionTier` and add
  no second owner rule of their own.

A per-slot consumer that must sum over slots (warehouse capacity sums every storage building's tier
capacity) iterates the slots itself but reads the feature and the tier only through `Unlocks` and
`ActiveTier` — so the one-read rule (acceptance 9) holds without forcing every consumer through a max.

`FactionTier` is the read a faction-level gate uses — trade orders and treaties (`exchange` `Hubs.TradeTier`),
diplomacy (`counterparties` `DiplomacyGate.TierOf`), a Rift Anchor's *"Grand Exchange in the same world"*
(`rift-trade`). Those names may stay as thin, named wrappers; each must delegate here and add no second
building check.

`TierOf` is the highest `ActiveTier(slot)` (§3) among the sector's slots whose structure is known and has
`FeatureUnlock == feature`. An upgrade in progress counts at its current tier; a first build counts 0. Pure over the sector,
computed per call, never cached (the `SupplyGraph` reason, `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:5-11`).
`TierOf` reads no owner and no faction kind: a feature belongs to the ground. **The owner rule is not the
consumer's any more** — round 6 S1 puts it here as `CountsFor`/`TierFor` (§5a), and every gate reads it
there rather than writing its own. Neither read branches on faction *kind*: a clan's Trading Post counts
for the clan exactly as an empire's counts for the empire.

## Tunables

None here. Tier costs, build times and every feature band are `empire-seed`'s band tables.

## Numeric types

`int` tiers (a level, bounded by the feature's maximum, not a magnitude).

**The tier maximum is a content ladder, not a progression ceiling.** Each feature's maximum is the number
of variants its one row carries (round 4 §B; `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:48-54` allows at most four). It bounds **which
building rungs exist**, never how far a mechanism can grow: every consumer that reads a tier also scales
with something unbounded — warehouse capacity with development and the content scale
(`sector-yield` `warehouse-axis`), banking with the number of bank points a faction builds
(`sector-yield` `banking-fact`). A consumer that would stop growing at the top tier is a PS-8 defect in
that consumer, not a reason to cap here. The maximum is a structural constant and its declaration says so
(tunables-ssot T2).

## Acceptance (contract)

1. `SectorFeature` has exactly nine members (`none` + eight, round 6 L6 included) with the maxima above
   (closed vocabulary, pinned with the reason), equal to `empire-seed`'s `featureUnlock` vocabulary (a join
   test).
2. `TierOf` is 0 for a sector with no building of the feature; the highest active tier otherwise; a
   building under first construction contributes 0; one under upgrade contributes its current tier.
2a. **S1:** `TierFor` is 0 when the slot's owner and the sector's owner differ, when either is unowned, or
   when neither is the asked faction; it equals `TierOf` when one faction owns both. A sector flipping
   owner while the slot does not gives **both** sides 0 in the same turn. `FactionTier` never counts a
   contested slot. Every gate in the family is asserted to call `TierFor`/`FactionTier`, not `TierOf` (a
   source scan over the named wrappers).
3. A `build` of the structure on its own slot raises the tier by one, pays the next tier's cost and
   refuses at the maximum with `build.max-tier`; a `build` of a different structure on an occupied slot is
   still `build.occupied`.
4. A world with every slot at tier 1 hashes byte-identically to today; save → load round-trips a tier
   above 1.
5. Every loaded row whose feature is not `none` has at most its feature's maximum tiers; a row whose
   feature is `none` uses no variant as a tier (both asserted per row over the real corpus, never by count).
6. `TierOf` returns the same value for identical sectors whatever faction owns them; `FactionTier` is the
   maximum of `TierOf` over the faction's owned sectors and 0 when it owns none with the feature; capture
   moves it the same turn.
7. `ActiveTier` is 0 for an empty slot and for a first build, `n` for a finished tier-`n` structure, and
   `n` for a structure mid-upgrade to `n + 1`; the upgrade's completion turn raises it to `n + 1` (each case
   its own test).
8. **Reset on clear or replace:** a sector lost in `Pressure` (`LoamPhases.cs:224`) and a structure
   destroyed or placed by a district assault (`BattleApplication.cs:165-172`) each leave the slot at
   `StructureTier == 1`, and the world hashes as if the structure had never been upgraded; building on
   that slot again starts at tier 1. A source scan asserts no `StructureId` assignment in
   `gk-core/src/FusionRpg.Core/World/**` omits the tier reset.
9. **One tier read:** no file under `gk-core/src/FusionRpg.Core` outside `SectorFeatures.cs` reads
   `WorldSlot.StructureTier` or `StructureDef.FeatureUnlock` except `StructureCatalog.cs` (load),
   `WorldCanonical.cs` (hash) and `BuildResolver`'s upgrade arm; consumers call `TierOf`, `FactionTier`,
   `ActiveTier` or `Unlocks` (a source scan; see the registry row below).
10. **An upgrade never switches a building off:** a tier-*n* storage building, loam `Storage`, `Yield`,
    item-storage, wonder or refinery structure mid-upgrade contributes exactly what it contributed at tier
    *n* in every gate listed in §3 (one test per gate); a first build still contributes nothing.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Structures/SectorFeaturesTests.cs` (new): items 1, 2, 5, 6, 7, 9.
- `tests/FusionRpg.Core.Tests/World/BuildResolverTests.cs` (extended): items 3, 8, 10.
- `tests/FusionRpg.Data.Tests/World/SlotTierPersistenceTests.cs` (new, in-memory store): item 4.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'src/FusionRpg.Core/World/Structures/SectorFeatures.cs',
  'gk-core/src/FusionRpg.Core/World/StructureCatalog.cs',
  'gk-core/src/FusionRpg.Core/World/WorldState.cs',
  'gk-core/src/FusionRpg.Core/World/WorldCanonical.cs',
  'gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs',
  'gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs',
  'gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs',
  'gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs') -Session <active-session-id>
```

The gate moves of §3 touch the other listed gate files too (`SectorItemCapacity.cs`,
`WonderEmpireEffects.cs`, `Habitability.cs`, `GrowthPhases.cs`); pass every one. They all fall to
`core-fallback`, which runs the world goldens — the right boundary for acceptance 4 and 10.

## Structure

```
src/FusionRpg.Core/World/Structures/SectorFeatures.cs   (new) — vocabulary + TierOf
gk-core/src/FusionRpg.Core/World/StructureCatalog.cs            MODIFIED — Feature, Tiers
gk-core/src/FusionRpg.Core/World/WorldState.cs                  MODIFIED — WorldSlot.StructureTier
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs              MODIFIED — conditional slot-tier row
gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs      MODIFIED — upgrade arm
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs             MODIFIED — column, write, load
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs    MODIFIED — equality, upsert
gk-data/packs/fusion/data/seed/structures/**                                  regenerated by empire-seed (never hand-edited)
```

## Boundaries and hard edges

- **Always:** gate a trade feature on `TierOf` only; tiers from one row's variants.
- **Ask first:** a feature not in the round-4 table; a tier as a separate row or a separate building.
- **Never:** a per-program "has building" check (or a `StructureKind` used as one); read `StructureDef.Role` to decide a feature (the
  `bank` role is a currency faucet, umbrella X2).
- **Hard edge — cross-program files.** `BuildResolver.cs` is the world-map/structures program's file and
  the variant schema is `empire-seed`'s; both changes are coordinated with those owners, not taken over.
  The same holds for the active-gate moves of §3 (loam, wonder, growth and the siege battle seam's
  `BattleApplication.cs`): a one-expression change each, behaviour-identical at tier 1, made with those
  owners' agreement recorded in the change.
- **Hard edge — goldens.** Tier 1 everywhere is the neutral value; no golden may move (acceptance 4).

## Dependencies and interface

**Depends on:** nothing in this sub-program. External: `empire-seed` `band-reader` and
`trade-structure-rows` (the `feature` key and per-variant bands).

| Exposed | Consumer |
|---|---|
| `SectorFeatures.TierOf(sector, SectorFeature.storage)` | `sector-yield` `warehouse-axis` |
| `… banking` | `sector-yield` `bank-points`, `banking-fact`; `logistics-flow` `auto-banking` (the hold gate) |
| `… trade` (`TierOf` and `FactionTier`) | `exchange` (`exchange-hub` `Hubs.HubTier`/`TradeTier`, `trade-access`, `treaty-lifecycle`); `rift-trade` (Grand Exchange check) — E-A14 |
| `… caravans` | `fleet` (`depot`) — fleet A11 |
| `… cross-world` | `rift-trade` (`crossing-anchor`) |
| `… diplomacy` (`FactionTier`) | `counterparties` (`diplomatic-stance` `DiplomacyGate.TierOf`), `exchange` `treaty-lifecycle` |
| `… legion-equipment` | `legion-build` (`legion-equipment`: the best producible piece tier) |
| the upgrade rule (§4) | every ladder; `empire-seed` `trade-structure-rows` leaves the upgrade verb out of its scope |

**A kind is never a feature gate — and every feature building loads under one neutral kind (round 6 C2).**
No consumer adds a `StructureKind` per building (`Exchange`, `Depot`, `Embassy`, `RiftAnchor` are all
withdrawn, `StructureKind.Exchange` included). A kind says what a structure *does* in the loam/siege
economy; the feature says which trade feature it unlocks, and gates read `FeatureUnlock` through this
module — never a kind.

But a row cannot load at all without a kind: `StructureDef.Kind` is a required enum with no "none" member
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`), a corpus row loads only when it has magnitudes
(`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`), and `IsKnown` answers only for loaded
rows (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:330`) — which `TierOf` requires (§5). The seven
feature rows were being emitted `structureKind: none`, so **none of them could ever be placed, built or
counted**, and every gate here read tier 0 forever (global audit C2). The owner's answer:

> **One neutral `StructureKind.Feature`** for all feature buildings; `StructureKind.Exchange` is
> withdrawn; ruling X1's wording is amended to allow this one neutral kind.
> ([../decisions-round-4.md](../decisions-round-4.md) Round 6 C2)

`Feature` does nothing in the loam or siege economy — its behaviour *is* its `FeatureUnlock`. That is the
`Obstacle` precedent exactly: a member whose documented purpose is *"the row has no OTHER behavior to gate
on `Kind`"* (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`, with `ItemStorage` as the fifth member at
`:43`). **X1's amended wording, quoted wherever this rule is cited:** *a new `StructureKind` is added only
where loam or siege rules need one — plus the one neutral `Feature` kind, which no gate reads.* The
loadable rule becomes **magnitudes present AND kind != none**, and the seven rows (Trading Post included)
are emitted `Feature` by `empire-seed` `trade-structure-rows`. Nothing in this module branches on `Kind`;
adding the member changes no gate here.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: structures and corpus, world state (slots), build command, world store.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check was not re-run (docs only).
[x] Read this session: decisions-round-4 (B); empire-seed spec-trade-structure-rows and spec-structure-bands
    (through the cross-cluster sweep); the planner's variant policy; BuildResolver's occupied refusal.
[x] decisions.md: magic numbers (no literal; bands only).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file.
[x] Verified against code: slot fields, the occupied refusal, the variants list, the Core loader ignoring it.
[x] Surrounding sections read: the planner's variant-policy comment.
[x] Constraints tested, not assumed: none claimed; tier-1 hash identity is acceptance 4.
[x] No §2 invariant contradicted: no cap (tiers are a feature ladder, not a magnitude ceiling).
[x] Corrections propagated: consumers listed; each consumer spec cites this module.
[x] No population pinned; the **nine**-member vocabulary (`none` + eight features, `standards` included
    since round 6 L6 — §1 `:74` and acceptance 1 `:249-251`) is a closed register row set with its reason.
    (Corrected 2026-09-20, reconciliation R-19.2: this line still read "eight-member (`none` + seven
    features)" after L6 added the Standard Hall.)
[x] No event-refreshed cache (computed per call).
[x] Ordering: an upgrade and a capture in the same turn resolve by BuildResolver's existing
    after-claim slot (Snapshot), unchanged.
[x] No actor magnitude.
[x] No SOLID fork: one query for seven features in five programs; one ActiveTier rule for every reader.
[~] Registry row (specified in the audit of 2026-09-20, lands with the module): guard
    `feature-gate-one-read` (script `scripts/guard-feature-gate.ps1`, tier `ci`, gating) that fails when a
    file under `gk-core/src/FusionRpg.Core/**` other than `World/Structures/SectorFeatures.cs`,
    `StructureCatalog.cs`, `WorldCanonical.cs` and `Movement/BuildResolver.cs` reads `.FeatureUnlock` or
    `.StructureTier`, and invariant `tn-feature-gate-one-read` (source: trade-network-map §5 invariant 16)
    naming it. Owner row in `gk-core/scripts/verification-boundaries.v1.json` for the script, its registry and its
    falsifier tests.
```

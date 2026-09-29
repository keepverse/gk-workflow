# Spec: `legion-standards`

**Status: written against shipped code 2026-09-19.** Module id `legion-standards`, row 11 of the
[legion-build map](../legion-build-map.md) (wave 3; depends on `member-stack`, `legion-owner-scope`;
external `trade-network` `sector-yield`, `empire-seed` `band-reader`/`world-exemplars`/`legion-seed-contract`).
Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.1, owner decision **L2** (standards reset on
disband or rout). Naming per map X8: `LegionStandard` / `legion-standard`, never `standard`.

## Objective

A legion may carry **one standard**: forged from a standard seed with goods, carried by a named member row,
lost with that row, and reset — not inherited — when the legion disbands or routs. Its atoms reach every
fighting member through layer 5c. Forging consumes goods through the existing storage path, so building a
legion creates trade demand.

Success looks like: at most one standard per legion; a carrier that fails `carrierRequirement` is refused
with a named reason; carrier loss, rout and disband each remove every standard contribution in the same
commit; validation asserts the seed contract, never how many standards exist.

## Scope and non-goals

- **In:** the standard state on a legion; the `forge-standard` and `assign-standard` commands; the
  carrier-requirement vocabulary (`empire-seed` waits on it, `empire-seed-map.md` §5.13, *Real gap*); the loss and
  reset rules; the 5c contributor; the goods gate and spend.
- **In (round 6 L6):** the **Standard Hall** gate on forging and the tier it allows (§3a). The building row
  itself is `empire-seed` `trade-structure-rows`'; the tier read is `trade-foundation` `sector-features`'.
- **Out:** the seed schema and its numbers (`empire-seed` `legion-seed-contract`, `legion-bands` — standard
  tier ladder in `legion-seed.v1.json`, proposed; the file does not exist yet); where goods come from
  (`sector-yield`); the magnitude scaling (the 5c reader).

## Layer answers

5c · scope: the legion's fighting members · lifetime: while the carrier row lives, until rout or disband ·
carrier: `world-buff.legion-standard-{seedId}-t{tier}` · SourceId `legion:{entityId}:{containerId}`.

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | Stable member identity and 5c binding (after `member-stack`, `legion-owner-scope`) | `spec-member-stack.md` §2; `spec-legion-owner-scope.md` §2–§3 |
| Built | Rout is stored and lasts one turn | `gk-core/src/FusionRpg.Core/World/WorldState.cs:314-320` |
| Built — **not used** (audit 2026-09-20) | The Data-side gate-before-Step, spend-after-Step pattern, right for relics (Data-held); forge goods are hashed located stock, so §3 spends inside `Step` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:544` (gate), `:609-611` (spend on the accepted report line) |
| Specified (not built) | Located stock: `WorldSector.LocatedStock`, changed only through `LocatedStockOps.Add` inside `Step` | `docs/architecture/trade-network/sector-yield/spec-located-stock.md` §2 |
| Built | Name collision to avoid: `ItemRole.Standard` is the commander's item slot | `gk-core/src/FusionRpg.Core/Items/ItemRole.cs:29-31`; `gk-core/src/FusionRpg.Core/Items/BaseTypeSlate.cs:28` |
| Real gap | No standard anywhere | — |

## Design

### 1. State

```csharp
public sealed record LegionStandard(string SeedId, int Tier, string CarrierMemberId, int ForgedOnTurn);
// WorldEntity gains: public LegionStandard? Standard { get; init; }
```

Hashed as a `standard` canonical row only for legions holding one (the `WorldCanonical.cs:71-72`
precedent), so worlds without standards hash unchanged.

### 2. Carrier requirement — a closed vocabulary owned here

**Registry (round 4, owner Q12):** the members live in the one shared legion vocabulary registry, `data/seed/legion/_registry/vocab.v1.json` (`empire-seed/spec-legion-seed-contract.md` §5.2); this C# enum is validated against it at load, so there is one list, never a mirror plus a sync test.

`StandardCarrierRequirement { Any, Fighter, Commander }`, the three values `empire-seed` validates
(`docs/architecture/empire-seed-map.md` §5.13, `legion-standard` row). `Any` = any member row; `Fighter` = a row whose role is
`Fighter`; `Commander` = the legion's `Commander` row (`legion-commander`). Until that role exists, no row
satisfies `Commander` and forging such a standard is refused `standard.no-eligible-carrier` — no flag is
needed, the role's absence is the answer.

### 3. Commands

- `forge-standard { EntityId, StandardSeedId, Tier, CarrierMemberId }`, resolved in Snapshot. Refusals:
  unknown seed (`standard.unknown`); carrier row absent (`standard.no-carrier`); carrier fails the
  requirement (`standard.carrier-ineligible`); legion not standing in an own sector (`standard.not-home`);
  goods short (`standard.goods-short`, decided inside `Step` against the located stock — audit 2026-09-20). A legion
  that already carries a standard **replaces** it (report line names the old seed).
- `assign-standard { EntityId, CarrierMemberId }` moves the standard to another eligible row.

### 3a. Forging needs a Standard Hall (round 6 L6)

**Owner decision L6 (2026-09-20):** *"Does forging a standard need a building — **yes, its own building
kind** — a Standard Hall, with tier variants gating the standard tier (an eighth kind in the building ladder;
tiers are variants of one row, as for every other building)."* This closes the map's own open question
A-LB-Q1 (which offered "no building", "the Workshop chain", or "its own building"): the answer is the third,
its own kind, so the equipment ladder and the standard ladder are built and upgraded separately.

`forge-standard` gains two checks, in this order, **before** the goods read of §3 — the same shape as
`legion-equipment` §7's Workshop chain, deliberately, so there is one pattern for a building gate:

| Check | Reason |
|---|---|
| `SectorFeatures.TierOf(sector, SectorFeature.standard)` is 0 — the sector the legion stands in has no Standard Hall (`trade-foundation/spec-sector-features.md` §5; the row is `empire-seed/spec-trade-structure-rows.md` §5.1, `featureUnlock: standard`) | `standard.no-hall` |
| The requested `Tier` exceeds that tier — a hall of tier *i* forges tiers ≤ *i* (the Workshop rule, `legion-bands` §3 item 3) | `standard.tier-too-high` |

**The gate is read, never re-implemented (round 6 S1).** *"A building whose sector and slot have different
owners counts for nobody until one faction owns both."* That rule lives once, in `sector-features`' `TierOf` /
`FactionTier`; this module calls it and never compares a slot owner with a sector owner itself. `standard.not-home`
(§3) stays: it is about where the *legion* stands, not about who owns the building.

**Interaction with the unpublished tier ladder.** The owner named the hall's three tiers on 2026-09-20 —
**Banner Yard → Standard Hall → Hall of Triumphs** — which fixes this ladder at **three** standard tiers
(`empire-seed/spec-trade-structure-rows.md` §5.1a). The variants' *multipliers* land with the standard tier
multiplier ladder, which publishes nothing until the `ssot-power-scale.md` §10.2 row lands (Hard edges below;
`empire-seed/spec-trade-structure-rows.md` §5.1a). Until then a Standard Hall is tier 1 and this module forges
tier 1 only — which is already what the Hard-edges section says the containers carry.

Goods: the seed's `forgeGoods[]` names **which** goods (VALIDATED against the goods registry by
`empire-seed`); **how many**, per tier, is `legion.v1.json` (proposed; the file does not exist yet)
`standards.forgeQtyPerTier` — a price curve over tier, not a cap. **Where the goods come from, and when
they are spent (corrected by the 2026-09-20 audit):** the first draft checked the scoped-inventory sector
storage overlay (`rpg_world_sector_storage`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SectorStorage.cs:55-66`) in a Data gate before `Step` and spent it after `Step` (the relic pattern). The map places forge
goods in `trade-network` `sector-yield`'s **located stock** (map §3; round 5 X4 puts legion goods in the
hashed sector warehouse, never `rpg_item_stock`), and located stock is hashed world state changed only by
`LocatedStockOps.Add` from inside `Step` (`trade-network/sector-yield/spec-located-stock.md` §2). So the
`forge-standard` resolver, in Snapshot, reads `LocatedStock.Of(good)` of the sector the legion stands in,
refuses `standard.goods-short` with nothing written, and on acceptance takes each good through
`LocatedStockOps.Add` (a negative delta, its `ledger-keys` fact kind) in the same resolver call that sets
`Standard`. No Data-side gate or spend exists for this module.

### 4. Loss and reset — each a rule over hashed state

| Event | Result |
|---|---|
| Carrier row removed (its `Count` reached 0, or it left the legion) | `Standard = null`, `standard.lost` |
| Legion routed this turn (`Routed` set) | `Standard = null` (L2) |
| Legion disbanded or destroyed | gone with the entity |

Applied in Snapshot after battles and before the reconcile, so the 5c withdrawal follows in the same
commit through `legion-owner-scope`.

### 5. Contributor

`LegionBuffSources` gains `standard`: desired = `{ container(SeedId, Tier) }` when `Standard` is set. The
container is projected from the seed's `atomFamilies[]` and the tier band (`legion-bands`) — deterministic,
identical for every player; magnitudes are scaled per member by the 5c reader only.

## Tunables

`legion.v1.json` (proposed; the file does not exist yet) `standards.forgeQtyPerTier` (goods per tier,
`long`). The tier multiplier ladder is `legion-seed.v1.json`'s (proposed; the file does not exist yet),
`empire-seed-map.md` §11 item 6 and §12b (owner Q12).

## Numeric types

Goods quantities `long`, `checked`; tier `int` (an ordinal, not a magnitude).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Standard"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~LegionBuff|FullyQualifiedName~WorldTurn"
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                    MODIFIED  WorldEntity.Standard
src/FusionRpg.Core/World/Legion/LegionStandards.cs        NEW       commands, loss/reset rules, contributor
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs (+Admission) MODIFIED forge-standard, assign-standard
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs                MODIFIED  standard row when present
(no Data-side goods gate or spend — the resolver spends located stock inside Step, §3)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs               MODIFIED  standard_json column
```

## Testing strategy

- Each refusal with its reason, writing nothing.
- One standard per legion; forging again replaces.
- **Loss, one test per row of §4**, each proving the 5c contribution is gone in the same commit.
- Order: a carrier dying in battle and a rout in the same turn yield the same end state either way.
- Goods: the resolver refuses short located stock inside `Step` with nothing written; an accepted forge
  spends exactly `forgeQtyPerTier[tier]` of each named good through `LocatedStockOps.Add`, once, inside the
  step (replay reproduces the spend and the hash; no Data-side write).
- `StandardCarrierRequirement` pinned to three members with its reason (it mirrors `empire-seed`'s
  validator). Seed tests assert the contract on exemplars, never a count of standards.

## Boundaries

- **Always:** name the type `LegionStandard`; bind through 5c; spend on the accepted line only.
- **Ask first:** inheriting a standard across disband (L2 says reset); more than one standard.
- **Never:** a second reader; per-player rolled standard stats.

## Success criteria

1. At most one standard, carried by an eligible row, forged with goods.
1a. (Round 6 L6) Forging in a sector with no Standard Hall drops `standard.no-hall` with nothing written;
   forging above the hall's tier drops `standard.tier-too-high`; both read `SectorFeatures.TierOf` and neither
   re-derives building ownership.
2. Every loss path removes its contribution in the same commit.
3. No world without a standard changes hash.

## Interface exposed to dependents

`StandardCarrierRequirement` (mirrored by `empire-seed`); `LegionStandard` on the legion DTO.

## Hard edges

- **Wave and ruleset bump (round 6 C1).** This module is legion-build **wave 3**, and it grants a
  player-facing feature (standards, forging, and now the Standard Hall gate), so it does **not** claim "no
  bump": it rides **wave 3's single `RulesetVersion` bump**, taken at landing (never pre-assigned) and
  recorded with the wave's one capability flag in [landing-order.md](../trade-network/landing-order.md).
  ~~No `RulesetVersion` bump: state emitted only when present; commands new … Corrects map §4's bump list.~~
  State stays emitted only when present (`WorldCanonical.cs:71-72`), which keeps the *re-bless* small; the
  bump is what stops a world stamped before wave 3 gaining the feature mid-life
  (`trade-foundation/spec-world-stamp.md` §2).
- **A new building kind (round 6 L6)** is owed by `empire-seed` `trade-structure-rows` (the `standard-hall`
  row, `featureUnlock: standard`, the neutral `structureKind: Feature` of round 6 C2) and by
  `trade-foundation` `sector-features` (the ninth `featureUnlock` member and the `SectorFeature.standard`
  read). This module cannot forge until both land; the order is in
  [landing-order.md](../trade-network/landing-order.md).
- **World channels (round 6 D2).** A standard's atoms may contribute to the six `world.*` channels (D2 names
  standards as a source). They contribute as ordinary 5c Hub contributions; the roll-up is `legion-power`'s
  `LegionWorldChannels` (`spec-legion-power.md` §6). This module computes no channel and folds none.
- New closed vocabulary; schema column; `WorldCommandKinds` +2.
- **Power ladder row owed (audit 2026-09-20).** The standard tier multiplier ladder
  (`legion-seed.v1.json` `standards.tierMultiplierMilli`, `empire-seed` `legion-bands` §5.1) multiplies a
  `P(Θ)`-scaled magnitude per tier. That is the shape of `ssot-power-scale.md` §10.2 row 7 (the affix tier
  ladder) and row 38 (the action rung quality ladder, which was given its own row), and §10 is a closed
  inventory: *"a power-shaped number not in this table does not have permission to exist."* The ladder
  therefore owes a §10.2 row (relative, bounded at its last authored tier, PS-4: never multiplied by
  `contentScale` a second time — the 5c reader scales once), requested from the power program. Until the
  row lands, `legion-bands` publishes no value for it and this module's containers carry tier 1 only.

## Dependencies

`member-stack`, `legion-owner-scope`, `role-aware-placement`; external `sector-yield` (goods),
`empire-seed` (`legion-seed-contract`, `legion-bands`, exemplars — the tests run on exemplars until
generation; `trade-structure-rows` for the `standard-hall` row, round 6 L6), `trade-foundation`
`sector-features` (`TierOf(sector, standard)` and the upgrade verb for any tier above the first).

## Design-gate checklist

```
[x] Subsystems: world legions, atom layer (5c), economy (goods sink), seeds (contract consumer).
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: map, ideal, empire-seed-map legion sections. NOT read: empire-resource-ssot.md
    beyond §3, economy-principles.md, sector-yield-map.md.
[x] decisions.md checked: Actor layer stack (5c).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: Routed, relic gate/spend pattern, sector storage schema, ItemRole collision.
[x] Read the surrounding section of every rule quoted.
[~] No suite run.
[x] No §2 invariant contradicted; forging is a sink (goods), no faucet added.
[~] Corrections propagated (map §10).
[x] Pinned: StandardCarrierRequirement (3) closed with reason; no population count.
[x] No cache; loss is a diff over hashed state.
[x] Order-independent loss tested both ways.
[x] Contributes through the 5c reader.
[x] No parallel path.
[x] No new rule beyond legion-owner-scope's registry row.
```

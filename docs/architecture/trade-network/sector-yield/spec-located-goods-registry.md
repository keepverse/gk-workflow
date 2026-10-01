# Spec: `located-goods-registry`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.1 of the
[sector-yield map](../sector-yield-map.md) (approved 2026-09-19). Umbrella invariants:
[../../trade-network-map.md](../../trade-network-map.md) §5. Ideal:
[../../trade-network-ideal.md](../../trade-network-ideal.md) §8.2, §8.6, §14b (*"Located goods had no
registry class"*). House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Give the economy a word for a banked good that is still on the map. Today the registry has six
classes and none of them fits: a **material** is player-held and survives a world, a **world stock**
is map-scoped and never feeds an account path
([empire-resource-ssot.md](../../empire-resource-ssot.md) §2, §4 rule 5). Shape B needs essence,
shards and souls to sit in a sector's warehouse first and reach the wallet only through a banking
fact. Without a class for that, banking would be a world stock feeding an account path, which rule 5
forbids.

This module lands:

1. a seventh registry class, **Located good**, in `empire-resource-ssot.md` §2, and its §3 row;
2. `LocatedGoodCatalog` in Core: the closed map from each located good id to what it becomes when
   banked.

Success: every later sector-yield module, and every trade sub-program after it, names a located good
by one id, and the catalog answers "does this good bank, and into what" with one call.

## Scope and non-goals

**In scope:** the registry class and row; the catalog; its three-member kind vocabulary.

**Not in scope:** any stock (that is `located-stock`); yields (`yield-structures`); banking
(`banking-fact`); prices or valuation (`exchange`); legion-equipment piece ids (they join the catalog
in `legion-equipment-stock`, which adds the `LegionPiece` kind's members). Loam, rubble, ironwork and
recruits are **never** located goods: they are world stocks or an accrual meter already, and they
never bank.

## What already exists

### Built

| Fact | Evidence |
|---|---|
| The issuable material ids are one closed list, built from two catalogs, in class order | `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:61-68` (doc: 27 ids, *"Souls carry no id — they are a ledger balance"*), `:70-80` (built from `CreatureMaterialCatalog` for shards and essence) |
| The materials store refuses an unknown id at the write boundary | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:187-188` |
| Materials are keyed by player only | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:191-193` |
| Souls are a ledger balance with a dedupe key | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:139-147` (`AppendSoulLedgerUnlocked`, `INSERT OR IGNORE`) |
| The registry's classes and rules | [empire-resource-ssot.md](../../empire-resource-ssot.md) §2 (six rows: wallet, material, world stock, accrual meter, battle budget, item), §4 rules 1–5b |

### Wiring gap

None.

### Real gap

| Gap | What this module builds |
|---|---|
| No registry class for a banked good that sits on the map | The **Located good** class and its §3 row |
| No code names which goods may be located or what each becomes | `LocatedGoodCatalog` |

## Design

### 1. The class (registry §2)

| Class | Meaning | Survives a world | Rules that apply |
|---|---|---|---|
| **Located good** | A quantity of a banked good (a material or souls) held in one sector's warehouse as hashed world state, or a legion-equipment piece. Converts **one way** into its banked form on a banking fact; a piece has no banked form | The stock stays with its world like any map-scoped quantity (§4 rule 5); only a banking fact takes it off the map | P1, P2, P3, P4, P5, P6. It never feeds fusion or crafting **while located**; the banking fact is its only path to an account |

The class sits between *material* and *world stock* on purpose: it is the same good as its banked
form (so P4 is its banked form's P4), but it is held and lost like a world stock.

### 2. The row (registry §3)

| Id / family | Class | Held by | Faucets | Sinks | Conversions | Owner | Code |
|---|---|---|---|---|---|---|---|
| **located goods** (`essence.*`, `shard.*`, `substrate.*`, `catalyst.*`, `souls`; later legion pieces) | Located good | Sector warehouse (whoever owns the sector) | Yield structures (`sector-yield`); income with a location (`sector-yield` `income-parity`, round 4 Q11); clan production (`counterparties`); deliveries (`logistics-flow`, a move, not a faucet) | Banking (→ wallet / material / AI treasury); trade (`exchange`); lane loss (`logistics-flow`); capture moves it with the sector | → banked form, one way, on a banking fact; never the reverse | `trade-network` `sector-yield` | `WorldSector` located stock (spec'd, `located-stock`) |

P6 is met by three competing sinks on different horizons: bank now, trade for a missing element, or
hold as a buffer (with capture risk). The row cites this spec and `located-stock`; the Code column
says "spec'd" until `located-stock` ships (registry §3's own rule for unshipped quantities).

### 3. Ids — one id space, not a second one

A located good's id **is** its banked id: `essence.fire` in a warehouse and `essence.fire` in the
wallet are the same string. Souls, which have no material id, use the id `souls`. One id space means
`exchange`'s valuation, `logistics-flow`'s flows and the ledgers all key on the same string, and no
translation table can drift.

### 4. `LocatedGoodCatalog`

```csharp
public enum LocatedGoodKind { Material, Souls, LegionPiece }

public sealed record LocatedGood(string Id, LocatedGoodKind Kind, string? BankedId);

public static class LocatedGoodCatalog
{
    public const string SoulsId = "souls";
    public static IReadOnlyList<LocatedGood> All { get; }      // ordinal id order
    public static bool IsKnown(string id);
    public static LocatedGood Get(string id);                   // unknown id throws
    public static bool Banks(string id) => Get(id).BankedId is not null;
}
```

- `All` is **derived**: one `Material` entry per `MaterialCatalog.All` id (`BankedId` = the same id),
  one `Souls` entry (`BankedId` = `souls`, which `banking-fact` routes to the soul ledger). Nothing is
  typed twice.
- `LegionPiece` entries are added by `legion-equipment-stock` from `legion-build`'s injected piece
  catalog, with `BankedId = null`. Until then the kind has no members.
- `LocatedGoodKind` is a **closed vocabulary** with three members. Its count is pinned in a test
  with the reason: a fourth kind is a new class of good and a reviewed change.
- Lazy, like `MaterialCatalog.All`, for the same static-initialiser reason
  (`gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:66-68`).

## Tunables

None. The catalog is structural: which goods exist is a content decision owned by the material
catalog, not a balance number.

## Numeric types

None. This module holds no quantity.

## Acceptance (contract)

1. Every id in `MaterialCatalog.All` appears in `LocatedGoodCatalog.All` exactly once, as
   `Material`, with `BankedId` equal to its own id (asserted as a join, never as a count).
2. `souls` appears exactly once, as `Souls`.
3. No located id is `loam`, `rubble`, `ironwork` or `recruit`, or any id the registry lists as a world
   stock or accrual meter.
4. The mapping from located id to banked id is total over every banking kind and injective (two
   located ids never bank into one banked id).
5. `Get` on an unknown id throws; `IsKnown` returns false for it.
6. `All` is in ordinal id order.
7. `LocatedGoodKind` has exactly three members (closed vocabulary, pinned with its reason).
8. The registry's §2 table gains the class and §3 gains the row in the same change as the code, and
   the row states P4 (inherited from the banked form) and P6 (three sinks named).

The catalog's size is a reading; no test asserts it.

## Test plan and verification boundary

- **Tests** (`tests/FusionRpg.Core.Tests/World/Goods/LocatedGoodCatalogTests.cs`, new): one test per
  acceptance item 1–7.
- **Verification** (the path-owned command, AGENTS.md "Verification boundary"):

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'src/FusionRpg.Core/World/Goods/LocatedGoodCatalog.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/LocatedGoodCatalogTests.cs',
  'docs/architecture/empire-resource-ssot.md') -Session <active-session-id>
python scripts/audit-doc-citations.py --scope docs/architecture/empire-resource-ssot.md
```

If `verify-change.py` reports the new `World/Goods/` path as unmapped, the mapping is added in the
same change (a missing boundary is the defect; the full suite is not the fallback).

## Structure

```
src/FusionRpg.Core/World/Goods/LocatedGoodCatalog.cs     (new)
tests/FusionRpg.Core.Tests/World/Goods/LocatedGoodCatalogTests.cs   (new)
docs/architecture/empire-resource-ssot.md                 MODIFIED — §2 class, §3 row
```

## Boundaries and hard edges

- **Always:** derive from `MaterialCatalog`; assert joins, not counts; land the registry row with the
  code.
- **Ask first:** a fourth `LocatedGoodKind`; making loam, rubble, ironwork or recruits a located good
  (it would breach `empire-resource-ssot.md` §4 rules 4 and 5).
- **Never:** a second id space for located goods; a hand-typed list of material ids; a banked form for
  a legion piece (see `legion-equipment-stock`).
- **Hard edge — sequencing.** The ideal says the class lands *"before `sector-yield` is specced"*
  (§14b) and the map says *"before any other module is specced"* (§2.1). All ten specs were written in
  one session, so the order is kept at **build** time instead: this module is the first task of the
  plan, and no other sector-yield module merges before the registry row is in.

## Dependencies and interface

**Depends on:** nothing.

| Exposed | Consumer |
|---|---|
| `LocatedGoodCatalog.IsKnown/Get/Banks`, `SoulsId` | `located-stock`, `yield-structures`, `banking-fact`, `legion-equipment-stock`; later `logistics-flow`, `exchange`, `counterparties` `empire-treasury` |
| The registry class | Every quantity that sits in a warehouse |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy/resources registry; materials catalog (read only).
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json covers
    docs/architecture/trade-network/**. session-boundary-check.py --session trade-network-idea-20260919
    exits 1 on the crossing already recorded in that file (other active lanes); this file is new.
[x] Read this session: empire-resource-ssot (whole), economy-principles P1-P14 and §12-§13,
    trade-network-ideal §5, §8, §14b, the umbrella map and the sector-yield map, DESIGN-GATE §1-§5,
    PRINCIPLES §5-§6.
[x] decisions.md: Empire resource registry row (:108) — a new class lands its row in the same change.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: MaterialCatalog's derivation and its comment on souls; the store's unknown-id
    throw; the soul ledger's dedupe insert.
[x] Surrounding sections read: registry §4 rules 1-7 and §5 widening rule.
[x] No constraint claimed that was not tested; no "moves goldens" claim (this module moves none).
[x] No §2 invariant contradicted.
[x] Corrections propagated: the sequencing note is stated here and in the session report.
[x] No population pinned: the catalog is asserted by join; only the closed three-member kind is pinned,
    with its reason.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion (ordinal order is a stated canonical order, not a play ordering).
[x] No actor magnitude.
[x] No SOLID fork: one id space, derived from the one material catalog.
[x] Registry row for a new rule: "a located good banks only through banking-fact" is enforced by
    banking-fact's acceptance; no separate guard.
```

# Spec: `trade-predicates`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 4, wave 2). Every `file:line` below was opened this session. Docs only.

## Objective

Let a storylet's eligibility say trade things — *this warehouse is nearly full*, *fire essence is spiking
at this hub*, *we have market access to this clan*, *we are under embargo* — through the one predicate
grammar, with each new leaf a reviewed addition to the closed `LeafId` enum.

## Locked anchors

- **Closed leaf enum, reviewed additions** (`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46`;
  `effect-atom/definitions.md` §3). Grammar bounds: depth 4, 16 nodes
  ([spec-narrative-predicates.md](../../npc-story-events/spec-narrative-predicates.md) §Grammar bounds).
- **Order of widening:** npc-story-events' `narrative-predicates` appends six leaves first (16 → 22); trade
  appends after them. Existing ordinals never move.
- **Two kinds of leaf, kept apart:** *current-state* leaves read hashed world state now; *event recency*
  reads the story ledger. Trade adds **state leaves only**; recency goes through one generic story-fact
  leaf (Design 2), so the enum never grows a trade-specific event leaf.
- **Access is `exchange`'s; treaties are `counterparties`'** (counterparties map C6, correcting this map's
  original "`AccessIs` from `counterparties`"): `AccessIs` reads `exchange` `trade-access`; `TreatyIs` reads
  `counterparties` `diplomacy-facts`.
- **No second ladder, no second curve.** Price bands come from `exchange` `price-curve`; the relation band
  and "clan request open" use npc's own leaves (`RelationBandAtMost`, petition leaf).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The closed `LeafId` enum (16 members) | `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46` |
| String-plus-threshold leaf precedent (`HoldsStock`) | `PredicateNode.cs:41`; interned per spec-narrative-predicates §Constraints |

### Real gap

No trade state to read (warehouse, price band, access, treaty facts all unbuilt); no story-fact recency
leaf in npc's six.

## Design

### 1. Four state leaves (appended after npc's six)

| `LeafId` | Subject | Argument (compiled) | True when | Reads |
|---|---|---|---|---|
| `WarehouseFillAtLeast` | `Target` (host sector) | `Value` = good slot; `Set[0]` = per-mille (0..1000) | the sector's stock of the good ≥ that share of its warehouse capacity | `sector-yield` `warehouse-axis`, `located-stock` |
| `PriceBandIs` | `Target` (host hub) | `Value` = good slot; `Set[0]` = band ordinal (`crash`, `normal`, `spike`) | the hub's current band for the good is that band | `exchange` `price-curve` |
| `AccessIs` | `Self` | `Value` = counterparty slot; `Set[0]` = access ordinal (`closed`, `passage`, `market`, `preferential`) | derived access from the viewer to the counterparty is at least that level — **`EffectiveLevel`** since round 4, so *"we can trade with this clan"* is false until the viewer holds a Trading Post (the building gate, `trade-access` §2a) | `exchange` `trade-access` |
| `TreatyIs` | `Self` | `Value` = counterparty slot; `Set[0]` = treaty-kind ordinal (incl. `embargo`) | that treaty kind (or embargo) is active between viewer and counterparty | `counterparties` `diplomacy-facts` (+ `diplomatic-stance` for war voiding) |

`WarehouseFillAtLeast`'s per-mille is a **bounded ratio** (commented as such), so it is never a cap on a
magnitude. `LeafId` grows 22 → 26 — a declaration pinned in the leaf-count test with this spec as its
reason, and in `effect-atom/spec-predicate-tree.md`'s leaf table in the same change (definitions.md wins
over specs).

### 2. Event recency — one generic leaf, requested

"A caravan was lost here within 3 turns" needs a story-fact recency leaf. npc's six do not include one
(`StoryFlagSet` tests a flag, not a fact kind in a window). This module files an ask on npc-story-events
`narrative-predicates` for **one generic leaf**, `StoryFactWithin` (`Value` = fact-kind slot, `Set[0]` =
window in host-clock units), usable by every host. Trade adds no event leaf of its own; if the ask is
refused, trade storylets react to trade facts only through the priority tier (consequence storylets keyed
by flags that `outcome-routing` sets).

### 3. Readers

`FactReader` arms in `src/FusionRpg.Core/World/Trade/Stories/TradeFactReaders.cs` (new): allocation-free,
string-free at evaluation (values interned at compile time). Each reads hashed world state or a logged step
input only.

## Contract exposed

Four `LeafId` members and their readers; the `StoryFactWithin` ask. Consumers: storylet eligibility
(`storylet-selection`), `trade-trigger-reachability`, `trade-storylet-supply` (condition vocabulary rows on
narrative-seed).

## Acceptance (contract level)

1. Each leaf compiles through `PredicateCompiler` within depth 4 / 16 nodes; out-of-range `Set[0]` is a
   compile rejection.
2. Each reader is deterministic over hashed state (same state → same verdict) and allocation-free.
3. A guard fails a trade reader that reads unhashed state (the Data-side ledger, the wall clock) inside the
   step.
4. The four trade leaves are pinned **by membership** (`WarehouseFillAtLeast`, `PriceBandIs`, `AccessIs`,
   `TreatyIs` exist in `LeafId`; a declaration with reason). The enum's **total** is not pinned here: it is
   a closed vocabulary shared with npc-story-events and the atom program, so a total pinned in this module
   (the earlier "26 after this module") fails whenever a sibling lands its own leaf first — the atom
   program's own pin owns the total (audit 2026-09-20; `LeafId` holds 16 today,
   `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46`).
5. `AccessIs` equals `exchange`'s `EffectiveLevel` and `TreatyIs` equals `counterparties`' facts for every
   fixture pair, including a clan pair before and after the viewer's first Trading Post (round 4).

## Test plan and verification boundary

Core leaf tests (compile, evaluate, determinism, count) — `core-fallback`; the leaf enum sits in
`gk-core/src/FusionRpg.Core/Effects/Atoms/`, so `seed-atoms-fallback` joins only if generated atom catalogs change.

## Hard edges

- Blocked on npc `narrative-predicates` (ordinal order) and on each reader's provider.
- `definitions.md` §3 and the predicate-tree leaf table move with the enum, or the widening is not done.

## Dependencies

`trade-fact-kinds`; npc-story-events `narrative-predicates`; `sector-yield`, `exchange`, `counterparties`;
atom program predicate grammar (`effect-atom/definitions.md` §3).

## Boundaries

- **Always:** append after npc's leaves; bounded ratios commented.
- **Ask first:** any event leaf; a leaf reading the relation band (npc's).
- **Never:** reorder `LeafId`; a second price curve or access rule in a reader.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: atom predicate grammar (closed enum), storylet eligibility, trade state (read).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: spec-narrative-predicates §Constraints/§1, DESIGN-GATE atom row. NOT read in full:
    effect-atom/definitions.md §3 (bounds quoted from the npc spec, which cites it).
[x] decisions.md: Atom attach points row (:113) — the leaf enum is part of the closed grammar.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: LeafId members and count.
[x] Surrounding sections read.
[x] No untested constraint claimed.
[x] No §2 invariant contradicted (one ladder, one curve; determinism).
[x] Corrections propagated: C6 (AccessIs owner) recorded in the map.
[x] No population pinned: leaf count is a closed-vocabulary declaration.
[x] No cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path.
[ ] Registry row: "no unhashed read in a trade reader inside step" needs a guard row when built.
[x] Round 4 reconciliation (2026-09-19): AccessIs reads EffectiveLevel (the building gate); no new leaf.
```

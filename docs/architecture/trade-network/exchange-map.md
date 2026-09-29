# Capability Map: exchange

**Status: APPROVED 2026-09-19** (owner, with the umbrella and every sibling map; owner decision Q1 recorded
below). Module specs written 2026-09-19 — see *Module specs*. **Reconciled with the round-4 owner
decisions ([decisions-round-4.md](decisions-round-4.md)) on 2026-09-19** — see *Reconciliation
2026-09-19 (round 4)* at the end; where this map's older text disagrees with that section, the section
and the register win.
**Program:** `trade-network` sub-program 6, `exchange` ([trade-network-ideal.md](../trade-network-ideal.md) §11).
**Ideal:** [trade-network-ideal.md](../trade-network-ideal.md) §7.1–§7.3, §7.6, §7.7, §13, §14b.
**Specs land:** `docs/architecture/trade-network/exchange/spec-<module-id>.md` (the umbrella's §6 layout).
**Plan:** `tasks/trade-network-exchange-plan.md` / `tasks/trade-network-exchange-todo.md` (written after approval).
**Siblings:** [counterparties-map.md](counterparties-map.md) (upstream), [trade-ai-map.md](trade-ai-map.md) (downstream).

## What this sub-program is

Where goods change hands between factions: the **trade hub** (a structure with a new `exchange` role),
the **price** each hub quotes, the **order** that walks that price, **settlement** at the end of the
turn with fees and tariffs as sinks, **payment** by barter topped up with souls, the closed list of
**what may trade**, the derived **Access** function and the closed **treaty vocabulary** that decide who
may trade where, and the **shared goods valuation** that the AI, the item program and (through it) the
Delve merchant all read. Moving your own goods is logistics (`logistics-flow`), never exchange (ideal
§7.4, base-defense decision 19).

## Assumptions (correct before approving)

1. **Model-free.** Deterministic C# and tuning only. Hub names and flavour are `empire-seed` content.
2. **Runs inside `step`.** Quote and settlement are sub-passes of the one Logistics phase that
   `logistics-flow` adds after Production (ideal §8.7). This map adds passes to that phase, never a
   phase of its own.
3. **Integer arithmetic for hashed state** (`long`, `checked`, per-mille, divide by 1000 last). Floating
   point is allowed by repo ruling, but every quantity here feeds the state hash, and integer math needs
   no platform stamp.
4. **Value-normalised units** (ideal §14b PS-5): quantities, clearing capacity and order steps read the
   same scaled value as the goods they carry; the **value index is relative** and never multiplied by
   `contentScale` (ssot-power-scale PS-4 standing).
5. **Counterparties first.** Hub demand comes from `need-vector`; treaty and war facts live in
   `diplomacy-facts`; the relation band arrives as `relation-facts`' logged snapshot.
6. Numbers live in `data/tuning/trade.v1.json` (new) and `data/tuning/diplomacy.v1.json` (new).

## What the code says (verified 2026-09-19)

| Fact | Where |
|---|---|
| Structure roles are a closed ten-value tuple; no role clears exchanges | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41` |
| Each role maps to a C# `StructureKind`, or raises | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:64-68` |
| `StructureKind` is a closed C# enum (loam source, storage, yield, refinery, obstacle, item storage) | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:10` |
| Only corpus rows with a `magnitudes` block are playable | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:55-65` |
| The Market slot exists once per template, home sector only, pre-claimed | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74`; `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:147`; `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:47` |
| Orders reveal in `(CommanderId, CommandId)` order | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:215` |
| Command kinds are a closed list; admission rejects unknown kinds | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:121`; `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17` |
| The Delve merchant refuses to price: its base must be an **item** price in souls, derived on the item side | `gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:17`, `:49-58` |
| Every in-game soul price ends in one function, scaled once by content Θ | `gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:40-41`; `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15`, `:31` |
| The catalyst lock: forge and flux have no salvage faucet and *"cannot be accelerated"* | `gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs:46-48`; `docs/architecture/item/ssot-materials-crafting.md` §7.3 |
| Materials are keyed by player only — no location | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:185-195` |
| Souls are a player wallet; no AI faction can hold or receive souls | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:145-149` |
| The registry's souls row has no conversion; three catalysts are registered | `docs/architecture/empire-resource-ssot.md` §3 |

## Modules

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `goods-valuation` | The shared value index per good; the soul-conversion base; the contract the AI, the item program and the Delve merchant consume | `trade-foundation` stamp | 1 |
| 2 | `tradeable-goods` | The closed table of what may trade and how; the catalyst lock amendment; legion equipment as a good; registry rows | `goods-valuation`; `sector-yield` located-material class | 1 |
| 3 | `treaty-vocabulary` | `treaty-kind.v1`: `passage`, `market`, `preferential`, `bloc`, `embargo` — scope, grant, lowest band; **round 4:** the Trade (4) and Diplomacy (2) tier ladders, the deal classes and the tier each needs; the treaty article kinds and deal shape (T-A5) | — | 1 |
| 4 | `price-curve` | Pure price math with its guards: imbalance, band, spread by relation band, the order walk | `goods-valuation` | 1 |
| 5 | `exchange-hub` | The trade hub as a structure: `exchange` role and kind, clearing capacity, Market-slot bonus, upkeep row; **round 4:** the hub is the Trade building ladder (Trading Post → Market → Exchange → Grand Exchange, tier variants of one row) with `HubTier` / `TradeTier` reads | `empire-seed` structure row; `sector-yield` warehouse; shared building-tier read (E-A14) | 2 |
| 6 | `trade-access` | `Access(grantor, requester, turn)` — derived, never stored — from treaty facts, band snapshot, embargo, bloc; **round 4:** capped by the building gate (`EffectiveLevel`, `LevelAt` a hub); clans trade from `wary`, `hostile` blocks | `treaty-vocabulary`, `exchange-hub`; counterparties `diplomacy-facts`, `diplomatic-stance`, `relation-facts` | 2 |
| 7 | `order-book` | The `order-set` command, standing orders, partial fills, cancel; quote at start, settle at end; pro-rata | `price-curve`, `exchange-hub`, `trade-access`; counterparties `need-vector`; `logistics-flow` phase | 3 |
| 8 | `settlement-payment` | Barter at the value index, souls top-up (reserved, then sunk), fees and tariffs as sinks, ledger rows | `order-book`, `tradeable-goods`; `trade-foundation` ledgers | 3 |
| 9 | `treaty-lifecycle` | Treaty, embargo and bloc commands; offers, terms, ending, breaking, imposition; **round 4:** reads `counterparties`' Embassy → Consulate gate (`DiplomacyGate`) at admission, plus the Exchange tier for `preferential` and blocs; treaty deal legs | `trade-access`; counterparties `diplomacy-facts`, `relation-facts`, `diplomatic-stance` §9 | 3 |
| 10 | `exchange-invariants` | The property suite: souls never increase, no world stock banks, closed cycles lose value | all above (scaffold in wave 1, grows) | 1→4 |

**Build order:** (`goods-valuation` → `tradeable-goods` ∥ `price-curve`) ∥ `treaty-vocabulary` ∥
`exchange-invariants` scaffold → (`exchange-hub` ∥ `trade-access`) → (`order-book` → `settlement-payment`)
∥ `treaty-lifecycle` → `exchange-invariants` complete.

**External dependencies (module ids from the sibling maps in this directory where they exist):**
`trade-foundation` `world-stamp`, `ledger-keys`, `material-ledger`, `world-stock-ledger`,
`economy-report`, `synthetic-graph` · `sector-yield` (located goods, warehouse, the located-material
registry class, the `LoamUpkeep` structure term; no map yet) · `logistics-flow` `logistics-phase` (it
reserves the settlement slot A1 after the flow steps L0–L8, `logistics-flow/spec-logistics-phase.md` §1),
`transit-buffer` (filled goods travel), `path-cache` (`passage` joins the route graph) · `trade-surface`
`trade-policy-editor`, `treaty-screen` (consumers) · `trade-stories` `trade-fact-source` (price and
treaty facts) · `fleet` (hub crews) ·
`empire-seed` (the `exchange` structure rows, D-E1) · `legion-build` (legion equipment pieces as a
counted stock) · `counterparties` (this directory) · item program (derives item prices from
`goods-valuation`) · `npc-story-events` `host-content-theta` (a hub's Θ for the soul leg).

---

## Module detail

### 1. `goods-valuation`

**Capability.** One function, `ValueOf(goodId)`, in **value-index units** — a relative worth, not a
currency, held by nobody (ideal §7.2). It is the `base` of every hub price, the unit every AI deal is
scored in, and the unit tariffs and fees are charged in. It also exports **`SoulsBaseFor(valueUnits)`**,
the unscaled soul equivalent used only on the payment side and by the item program. A soul amount is
scaled **exactly once**: for trade the scale is already in the quantity (assumption 4), so trade never
passes it through `SoulSinkPolicy.Price`; the item program, whose bill is priced at the pin, scales it
once through `SoulSinkPolicy.Price` (`gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:40-41`) — EC6. The **item program** derives an item's base price from its material bill valued here, and
the **Delve merchant** reads that item price (`gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:49-58`), so the
merchant consumes this valuation through the item program, not directly (contradiction EC2).

- **Built:** the one soul-price function and content scale (`SoulSinkPolicy.cs:40-41`, `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15`, `:31`).
- **Wiring gap:** the Delve merchant's refusal waits for an item price (`DelvePrices.cs:17`).
- **Real gap:** any goods valuation.
- **Touches:** `src/FusionRpg.Core/World/Trade/Valuation/` (new); `trade.v1.json` (new) `goods.{id}.baseValue`,
  `payment.soulsBasePerValueMilli`.
- **Acceptance (contract):**
  - Every tradeable good has a `baseValue ≥ 1`; a missing good is a load rejection naming it (T5).
  - `ValueOf` reads no `Θ` and no `contentScale` (a source-scan guard in the World tree, PS-4 standing).
  - `SoulsBaseFor` is monotone in value units, returns an **unscaled** `long` and rounds against the
    payer; trade settlement never scales it again (EC6).
  - A `§10.2` row in `ssot-power-scale.md` is landed for the value index (relative, bounded) in the same
    change, or the change is not done.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade), `FusionRpg.Guard.Tests`
  (`guard-power`, world determinism).

### 2. `tradeable-goods`

**Capability.** The **closed** table of what may trade (ideal §7.3), enforced at order admission and at
settlement: `essence.*`, `shard.*`, `substrate.*`, `catalyst.*` and **legion equipment pieces** trade
between factions as located goods; `rubble`/`ironwork` trade **world-to-world barter only**; `souls`
appear **only on the payment side**; `loam` and `recruits` **never**; unique items and creatures are not
goods in v1. It carries the three document-and-registry changes the table requires:

- **Catalyst lock amendment (owner, round 3).** Amend `docs/architecture/item/ssot-materials-crafting.md`
  §7.3 (the *"cannot be accelerated by inventory management"* bottleneck paragraph) and the matching
  comment at `gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs:46-48`: trade becomes a **second, priced**
  catalyst source. Salvage stays at *never* for forge and flux (§5 of that doc is unchanged). The
  `catalyst.*` row in `empire-resource-ssot.md` §3 gains *trade (priced, gated by a hub and Access)* as a
  faucet and a Conversions entry, with crafting as its named sink (P1).
- **Souls → located goods conversion row** on the `souls` row of `empire-resource-ssot.md` §3: lossy
  (spread, fee, walk), rate-capped (clearing capacity), gated (a hub and `Access`). Goods → souls has no
  row and never will.
- **Legion equipment** trades as a located good (`legion-build-ideal.md` §6.7); its registry row is
  `legion-build`'s, and this module lists it as tradeable.

- **Built:** the material catalog ids this table names (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:187`).
- **Wiring gap:** —
- **Real gap:** the table, its guard, the three registry/doc changes.
- **Touches:** `src/FusionRpg.Core/World/Trade/Goods/` (new); the two docs and one comment named above
  (in the change that lands this module, per DESIGN-GATE evidence rule 6).
- **Acceptance (contract):**
  - The trade classes are a **closed vocabulary** (tradeable, world-barter-only, payment-only, never) —
    pinned because the code owns it and a new class is a reviewed change; every good id resolves to
    exactly one class.
  - An order naming a `never` good is refused at admission with a named reason; a `payment-only` good
    can only appear in a payment leg; a `world-barter-only` good can only settle between two world
    stocks.
  - The amended §7.3 paragraph, the comment and both registry rows land in the same commit as the code.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade, Items/Materials); citation audit on the
  amended docs.

### 3. `treaty-vocabulary`

**Capability.** One closed registry, `treaty-kind.v1`, owned here (ideal §7.7):

| Kind | Scope | Grants | Lowest band |
|---|---|---|---|
| `passage` | bilateral | Legions and routes may cross the grantor's sectors | `wary` |
| `market` | bilateral | Orders at the grantor's hubs; its lanes join the route graph (implies `passage`) | `open` |
| `preferential` | bilateral | Lower tariff, most-favoured clause: never above the lowest tariff the grantor charges anyone | `eager` |
| `bloc` | multilateral, **in v1** | No tariffs inside; one shared external tariff and shared embargoes; members give up their own | `eager` with every member |
| `embargo` | one-sided act | Stops the target's orders and passage; voids `market` and `preferential` | any; **automatic at war** |

The registry file names the kinds and their structure; the numbers (lowest band per kind as data, tariff
bands, minimum term, truce turns) live in `diplomacy.v1.json` (new).

- **Built:** the band vocabulary it refers to (`gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`).
- **Real gap:** the registry and its reader.
- **Touches:** a registry file under a `_registry/` path (hand-authored, per the generated-data rule) and
  its C# reader in `src/FusionRpg.Core/World/Diplomacy/` (new).
- **Acceptance (contract):** exactly five kinds and four `Access` levels (`closed`, `passage`, `market`,
  `preferential`) — both pinned as closed vocabularies owned by this code; every kind names a lowest band
  that exists in the disposition registry; an unknown kind in a fact or command is a load or admission
  rejection.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Diplomacy).

### 4. `price-curve`

**Capability.** Pure, integer price math (ideal §7.2 with the §14b guards):

```
d = max(demand, floorUnits)        s = max(stock, floorUnits)          // floor both terms: no divide-by-zero
imbalanceMilli = clamp((d − s) × 1000 / min(d, s), −1000, +1000)       // a bounded ratio, commented as such
price = base × (1_000_000 + bandMilli × imbalanceMilli) / 1_000_000    // widen first, divide once, last
buy   = ceil (price × (1000 + spreadBuyMilli  + bandSpreadMilli[band]) / 1000)   // round buy UP
sell  = floor(price × (1000 − spreadSellMilli − bandSpreadMilli[band]) / 1000)   // round sell DOWN
```

All operands `long`, all products `checked`. `sell ≥ 0` is guaranteed by a load-time check that the
sell-side spread terms stay below 1000‰. An order **walks** the curve every `orderStepUnits`: each step
re-reads `imbalanceMilli` with the stock and demand moved by the volume already filled, so a batch never
trades at one price (the flat-price batch loop, ideal §6). The relation band enters as an extra
spread per band (`spread.byDispositionBand`), never as a second relation axis.

- **Real gap:** all of it.
- **Touches:** `src/FusionRpg.Core/World/Trade/Pricing/` (new) — a Math file, so no bare literal (T3).
- **Acceptance (contract):**
  - `buy ≥ price ≥ sell` for every input; `buy > sell` whenever the spreads are non-zero.
  - Empty stock or empty demand never throws and never divides by zero.
  - A cheap good never prices to zero on the buy side (`buy ≥ 1`).
  - Walking an order of volume V in steps yields a total cost ≥ V × the first-step price for a buy, and
    ≤ for a sell (monotone walk).
  - Integer overflow throws (`checked`), never wraps; `python gk-core/scripts/audit-overflow.py --targets A3`
    reports nothing in this folder.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade/Pricing), property tests with seeded
  generators.

### 5. `exchange-hub`

**Capability.** A trade hub is a **row in the structure corpus** with the new **`exchange` role**
(owner decision D-E1; the rows come from `empire-seed`, which owns the corpus, D-E2), built on a
buildable slot through the existing `BuildResolver` — not a special case of the Market slot. The Market
slot stays the preferred site and gives a bonus (round 5 B1: the one Trading Post row allows `Wildland`
**or** `Market` through a multi-kind `requiredSlotKinds` field — `exchange-hub` §3). A hub's **clearing capacity** — value units exchanged
per turn, value-normalised — rises with its level and is a **per-turn structural rate** (commented as
such, not a progression cap). It pays loam upkeep through the structure term `sector-yield` adds to
`LoamUpkeep`, and it needs crews (`fleet`). Its warehouse is `sector-yield`'s.

- **Built:** the corpus, the loadable-row rule, the build pipeline, the Market slot
  (`StructureCorpus.cs:55-65`; `SlotTypeCatalog.cs:74`).
- **Wiring gap:** the Market slot has no mechanism and is not buildable (ideal §5).
- **Real gap:** ~~a new `StructureKind.Exchange` in `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:10`~~
  (**withdrawn by round 6 C2** — the hub row loads under the one neutral `StructureKind.Feature`, landed by
  `trade-foundation` `sector-features`, and no gate reads a kind); the clearing capacity field; the
  Market-slot bonus; **consignments** (a foreign trader's goods at a
  hub, EC9). The role in the seedsmith tuple is `empire-seed` `exchange-role`'s, not this module's (EC7).
- **Touches:** `StructureCatalog.cs` (the `ClearingValuePerTurn` field only — **no enum member** after round 6
  C2), `WorldSector` (consignments), `trade.v{n}.json` `hub.marketSlotBonusMilli` and `hub.staffingCurve`
  (global audit m14 — one `LabourCurve` evaluator, this module's own points). Capacity reads the hub row's band
  and the sector's content scale — no `clearingByLevel` table (EC5). `SlotTypeCatalog.cs` is **not** touched:
  the C4 display rename is one ask to world-map covering both slots (global audit m15/X-14).
- **Acceptance (contract):** a hub built on any slot its row allows clears orders; a hub on the Market slot
  clears `bonus` more; a sector's clearing capacity is the sum over its active hubs; an under-construction
  hub clears nothing; ~~the role list and the `StructureKind` enum widen together and the loader refuses a
  role with no kind~~ — **round 6 C2:** the load rule is the feature/field pair (`FeatureUnlock == trade`
  **iff** `ClearingValuePerTurn > 0`), and a split-owned building counts for nobody through
  `sector-features` (S1).
- **Verification boundary:** `FusionRpg.Core.Tests` (World structures); seedsmith `pytest` for the role
  tuple (`gk-forge/tools/seedsmith/tests`).

### 6. `trade-access`

**Capability.** `Access(grantor, requester, turn) ∈ {closed, passage, market, preferential}` — a **pure
function**, never stored, rebuilt by replaying the ledger (ideal §7.7). Inputs: the active treaty facts
for the pair (signed, not ended, within term, not voided by war), the pair's logged band snapshot, any
embargo, and bloc membership. Rules: an embargo or war gives `closed`; otherwise the highest granted kind
**whose lowest band the current band still reaches** — so a band drop suspends a treaty's effect without
writing a broken fact; `market` implies `passage`; inside a bloc, members read `preferential` at a zero
internal tariff and the bloc's shared external tariff applies to outsiders. Your own and unheld ground is
always open for passage (ideal §7.6). The **tariff** a requester pays is read here too: the kind's tariff
band, and for `preferential` the most-favoured clause (never above the grantor's lowest tariff to anyone).
Clans grant access by band alone — owner decision Q1 (below), amended by round 4: `market` from `wary`,
only `hostile` blocks, and every trade level above `passage` also needs its building on both sides
(`treaty-vocabulary` §5; spec `trade-access` §2a).

- **Real gap:** all of it.
- **Touches:** `src/FusionRpg.Core/World/Diplomacy/Access` (new); read by `order-book`, by `logistics-flow`
  route planning (passage), and by `trade-ai`.
- **Acceptance (contract):**
  - Pure and deterministic: same facts + snapshot → same level; replaying the command log reproduces
    every turn's `Access` for every pair.
  - War or embargo ⇒ `closed`, in both directions for war.
  - Lowering the band below a treaty's lowest band lowers `Access` the same turn and restoring it restores
    `Access`, with no fact written either way.
  - Most-favoured clause: for every grantor and turn, a `preferential` tariff ≤ the minimum tariff that
    grantor charges any requester.
  - Not cached across turns (derived per step, so DESIGN-GATE §2.16 has no trigger set to enumerate).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Diplomacy), property tests over generated fact
  sequences.

### 7. `order-book`

**Capability.** The standing trade order and its lifecycle (ideal §7.6): `order-set` (a new command kind
admitted through `WorldCommandAdmission`) places, replaces or — at quantity zero — cancels a standing
buy or sell order at a hub the requester can reach at `market` or better. Policy commands set policy;
they move nothing themselves. Each turn, inside the Logistics phase:

1. **Quote at the start of the step** — every hub's curve is read from its start-of-step stock, demand
   (`need-vector` truth side) and the band snapshot.
2. **Aggregate, then walk.** All admitted orders at a hub are summed per good and side; the aggregate
   walks the curve in `orderStepUnits`, bounded by the seller's stock and the hub's clearing capacity.
3. **Pro-rata.** When stock or capacity binds, fills split **pro rata by requested volume** across
   commanders (ideal §14b replaces "lower faction id wins"); each commander pays the volume-weighted
   average of the walk, so splitting one order into many, or a lower `CommandId`, buys nothing.
4. **Settle at the end of the step**, writing in `(CommanderId, CommandId)` order (the reveal order,
   `TurnEngine.cs:215`) for ledger determinism only.
5. **Partial fills are normal**; the remainder stays open until its policy says otherwise; **cancelling**
   stops future fills and never recalls goods in transit.
6. **Risk transfers at the seller's hub.** Filled goods belong to the buyer from that moment and travel by
   `logistics-flow`; if the counterparty is captured mid-route, `cargo-fate` decides (ideal §7.6).

- **Real gap:** all of it.
- **Touches:** `WorldCommandKinds` (`order-set` — reviewed widening), `WorldCommandAdmission`,
  `WorldState` (standing orders are hashed state), `src/FusionRpg.Core/World/Trade/Orders/` (new).
- **Acceptance (contract):**
  - Order-independent: permuting the filing order or the `CommandId`s of a turn's orders leaves every
    fill and every price identical (tested with shuffled command sets).
  - Splitting one order into k orders of equal total volume yields the same fill and the same total cost.
  - Σ fills at a hub per turn ≤ clearing capacity and ≤ seller stock.
  - A sale uses only stock held at step start: goods bought this step cannot be resold this step.
  - An order at a hub whose `Access` fell below `market` is suspended, not deleted, and resumes when
    access returns.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade/Orders, World/Turn); world determinism
  guard.

### 8. `settlement-payment`

**Capability.** How a fill is paid and what it destroys:

- **Barter at the value index** (owner, round 3): the buyer pays in goods valued by `goods-valuation`,
  delivered from its **consignment** at that hub (EC9); the seller receives them in its hub stock. They
  bank later like any stock — settlement never writes an AI treasury (CM3, EC12).
- **Souls top-up — player only, and fully sunk.** Only the player holds souls
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:145-149`), so a soul leg can only flow from the player.
  Souls for a purchase are **reserved before the step** (Data side, in the commit) and **settled with it**
  (ideal §14b); every soul paid is **destroyed** — the `souls → located goods` conversion row
  (`tradeable-goods`). The hub owner receives nothing for the soul-paid part (the spec's waterfall,
  `settlement-payment` §3), and **every** buy — soul-paid or not — is bounded by the owner's stock above
  its need reserve (`order-book` §Design 6), so selling for souls never starves it. The seller receives no
  souls and no minted goods. *(Map text aligned to the spec by the 2026-09-20 audit; it used to say the
  seller's valuation counts the soul leg, which no module computes.)*
- **Fees:** `fee.milli` of each fill's value, destroyed at the hub (a sink).
- **Tariffs:** charged on the value index at settlement by the grantor's `Access` tariff;
  `tariff.sinkMilli` is destroyed, the rest goes to the grantor **in goods**; **any souls part of a tariff
  is sunk in full** (ideal §7.7).
- **Ledger:** one row per settled exchange, per fee and per tariff, deduped on
  `(save_id, empire_id, world_id, turn, factKind, sector, good)` (ideal §14b) through
  `trade-foundation`'s P14 ledgers; each fill writes the counterparties `trade.fulfilled` relation fact
  (capped per pair per turn there).

- **Built:** the soul ledger's dedupe pattern (`RpgStore.Souls.cs:145-149`).
- **Real gap:** reservation, barter settlement, fee/tariff sinks, the ledger rows.
- **Touches:** `src/FusionRpg.Core/World/Trade/Settlement/` (new); `gk-core/src/FusionRpg.Data/Sqlite/` (soul
  reservation in the commit transaction).
- **Acceptance (contract):**
  - A reserved soul amount that the step does not use is released in the same commit; a failed step
    leaves no reservation and no spend.
  - Σ souls leaving the player = Σ souls destroyed; no settlement path writes a positive soul delta.
  - Every non-empty basket loses value **at the hub's own pass-start mid prices** (not at base value,
    where buying a hub's surplus with what it lacks can gain — that is comparative advantage).
  - Every ledger row has a dedupe key; re-committing a turn writes nothing new.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade/Settlement), `FusionRpg.Data.Tests`
  (commit transaction, soul ledger).

### 9. `treaty-lifecycle`

**Capability.** The diplomacy verbs, as world commands resolved at End Turn — deterministic and
replayable like every order: `treaty-propose` (a kind plus articles from `trade-ai`'s fixed article list),
`treaty-respond` (accept, decline, or counter from the same list), `treaty-end`, `embargo-set` /
`embargo-lift`, `bloc-propose` / `bloc-join` / `bloc-leave`. An offer is hashed state with a lifetime of
`offerTtlTurns`; a response lands the next turn a party commits. Ending a treaty before its **minimum
term** writes `treaty.broken` (counterparties `relation-facts` moves the bands, then a truce period);
`war.declared` voids treaties both ways (counterparties `diplomatic-stance`); a peace term may impose
`market` as `treaty.imposed`. The facts land in counterparties `diplomacy-facts`; this module never keeps
a second list of active treaties.

- **Real gap:** all of it. `spec-ai-commander.md:284` (*"no diplomacy"*) is amended for this program
  (counterparties filed ask A5).
- **Touches:** `WorldCommandKinds` (the kinds above — a reviewed widening the ideal's §8.7 list did not
  name, see EC4), `WorldCommandAdmission`, `src/FusionRpg.Core/World/Diplomacy/` (new).
- **Acceptance (contract):**
  - A treaty exists only if both parties' commands are in the log; replay rebuilds it.
  - Ending at or after the minimum term writes `treaty.ended`; before it, `treaty.broken`.
  - A proposal whose kind's lowest band the pair does not reach is refused **at resolution** with the
    band named (admission has no band; it arrives as the logged snapshot, CM1).
  - A bloc member cannot hold a bilateral tariff with a non-member that differs from the bloc's external
    tariff.
  - Every refusal carries a reason that names the rule or article (explainable, ideal §7.7).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Diplomacy, World/Turn).

### 10. `exchange-invariants`

**Capability.** The property suite that makes the ideal's three invariants executable, built as a
scaffold in wave 1 and completed when settlement lands. It generates seeded worlds (via
`trade-foundation`'s synthetic graph builder), random order and treaty sequences, and asserts:

1. **No trade path increases souls** — for every generated sequence, the player's soul balance after the
   turn ≤ before, and no AI faction ever holds souls.
2. **No world stock reaches a banked stock** — no settlement or delivery moves `loam`, `rubble`,
   `ironwork` or `recruit` into a player wallet or material row.
3. **A closed cycle loses value** — for any set of fills within one turn after which **every
   (good, location) balance** of the trader equals its start, the trader's total value index is strictly
   lower. Such a cycle decomposes into per-hub round trips, each losing by spread + fee + walk, which is
   why the definition includes location (EC1).
4. **Buy-then-sell at one hub** in the same quantity always loses value.
5. **Determinism** — same seed and log ⇒ same hash, twice.

Each invariant gets a row in `gk-core/scripts/enforcement-registry.v1.json` (a guard, per DESIGN-GATE §5's last box).

- **Touches:** `tests/FusionRpg.Core.Tests/World/Trade/` (new), the enforcement registry.
- **Acceptance (contract):** the five properties above hold over the generated space; no assertion names
  a count of goods, hubs, orders or turns (those are generator parameters, printed, never asserted).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade), `FusionRpg.Guard.Tests` (registry
  meta-test).

---

## Module specs (written 2026-09-19)

[goods-valuation](exchange/spec-goods-valuation.md) · [tradeable-goods](exchange/spec-tradeable-goods.md) ·
[treaty-vocabulary](exchange/spec-treaty-vocabulary.md) · [price-curve](exchange/spec-price-curve.md) ·
[exchange-hub](exchange/spec-exchange-hub.md) · [trade-access](exchange/spec-trade-access.md) ·
[order-book](exchange/spec-order-book.md) · [settlement-payment](exchange/spec-settlement-payment.md) ·
[treaty-lifecycle](exchange/spec-treaty-lifecycle.md) · [exchange-invariants](exchange/spec-exchange-invariants.md).
Where a spec and the module detail above disagree, the spec wins: it was verified later, against code.

## Filed asks (other programs)

| # | To | Ask |
|---|---|---|
| E-A1 | item program | Derive an item's base price from its material bill valued by `goods-valuation` and `SoulsBaseFor`, scaled once through `SoulSinkPolicy.Price`, so the Delve merchant's refusal (`DelvePrices.cs:17`) can close; `seed-contract.md` §2.1 already lists price as DERIVED |
| E-A2 | `empire-seed` | The `exchange` role and rows (`exchange-role`, `trade-structure-rows`) with ~~`structureKind: "Exchange"`~~ **`structureKind: "Feature"`** (round 6 C2 — one neutral kind for every feature building; `Exchange` withdrawn), ~~rows for at least the Wildland and Market slot kinds~~ (superseded by round 5 B1: **one** Trading Post row whose `requiredSlotKinds` is `[Wildland, Market]`), and the clearing ordinal once `ClearingValuePerTurn` lands |
| E-A3 | `logistics-flow` | Quote and settlement run as this map's passes in the slot `logistics-phase` reserves ~~after arrivals~~ — round 5 X5 quotes the canonical order: row **A1**, after every flow step L0–L8 (so after caravan load/unload L2 and banking L3), before `clan-economy` A2 (`logistics-flow/spec-logistics-phase.md` §1); `path-cache` holds `trade-access`'s per-pair `PassageBit` in its topology key and compares it every L0 (it covers the band-only and faction-collapse edges, DESIGN-GATE §2.16; the `PassageDigest` this row once named was withdrawn by the 2026-09-20 audit) |
| E-A4 | `sector-yield` | The located-material registry class before this sub-program's code; hub warehouses on its capacity axis, with consignments counted in occupancy |
| E-A5 | `logistics-flow` | A trader's consignment at a foreign hub is a lane-flow **source** (default destination: nearest own bank point, over `passage` ground) and a `route-set` **destination** (to deliver payment goods to a hub) |
| E-A6 | `legion-build` | State whether any equipment recipe consumes a world stock; if one does, pieces trade as `world-barter-only` |
| E-A7 | `counterparties` `relation-facts` | The per-turn logged step input it adds for the band snapshot is the one channel; `settlement-payment` adds the player soul budget to the same record |
| E-A8 | `trade-foundation` `stock-deltas` | An owner dimension on a delta, so consignment changes reconcile in the world-stock ledger |
| E-A9 | `trade-stories` / `npc-story-events` | **Superseded by round 4 (2026-09-19).** Was: a band-raising fact must be reachable early because clans granted `market` only from `open`. Clans now grant `market` from `wary` behind a Trading Post, so the ask becomes a reachability case "build a Trading Post, then fill a clan order" in `trade-stories` `trade-trigger-reachability` and `trade-surface` `trade-unlock` (both in this reconciliation's fence, both updated) |
| E-A10 | `counterparties` `need-vector` | Per-**sector** reads `DemandAt(faction, sector, good)` (value-normalised units) and `ReserveAt(faction, sector, good)`: its demand is faction-wide today (`counterparties/spec-need-vector.md` §2) and a hub prices against its own sector |
| E-A11 | `sector-yield` / `logistics-flow` | A per-(sector, good) **hold** in the banking policy. Banking runs before the exchange pass, so a hub at a bank point (the home sector holds the only Market slot) otherwise has no stock to sell. **Decided by round 4 (Q2):** the hold is in `sector-yield`'s banking policy, unlocked by the **Treasury** tier; default *"keep what open sell orders need"*, which `order-book` exposes as `OpenSellNeed` (EC21). Still an ask on `sector-yield` to build |
| E-A12 | `counterparties` `empire-treasury` | Drop *"trade payments"* from the treasury's drains: settlement pays only from consignments and never reads or writes a treasury (EC10, CM3) |
| E-A13 | `counterparties` `diplomacy-facts` | A `TariffMilli?` field on `offer.made`, `treaty.signed`, `treaty.imposed` and the founding `bloc.joined`; until then every treaty charges its kind's default tariff. **Round 4 widening:** the fact record also carries the `Deal` (legs, shape, soul top-up, leg hub) `treaty-lifecycle` §1 defines, so a signed deal replays from its fact |
| E-A14 | `trade-foundation` `sector-features` — **answered during this reconciliation** ([spec](trade-foundation/spec-sector-features.md): `SectorFeature`, `StructureDef.FeatureUnlock`, `WorldSlot.StructureTier`, the upgrade arm of `build`, `TierOf`/`FactionTier`) | **One shared building-tier mechanism** for every round-4 ladder: a built slot records its tier variant; an upgrade is a `build` on an occupied slot of the same row to the next variant (today refused `build.occupied`, `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:71`); the old tier stays active until the upgrade completes; one read ~~`BuildingTier(world, sector, structureKind)` / `FactionTier(world, faction, structureKind)`~~ (superseded: the built read is `SectorFeatures.TierOf(sector, SectorFeature)` / `FactionTier(world, faction, SectorFeature)` — keyed by feature, never by kind; round 5 X1) every consumer uses |
| E-A15 | `empire-seed` (`exchange-role`, `trade-structure-rows`) | The `Exchange` row carries **four tier variants** in ladder order (Trading Post, Market, Exchange, Grand Exchange), each with its clearing band. (The Embassy row with its two variants is `counterparties`' ask A15 — not repeated here; its role in the closed role list is a reviewed widening that ask must name.) |
| E-A16 | `counterparties` `clan-seeding` | Seed each clan's hub as the `Exchange` row at **tier 1** on its `Market` slot, so clan barter exists from turn 0 and the player's Trading Post is the missing half (`exchange-hub` §7). Round 5: legal on `Market` by B1; see E-A20 for the yard |
| E-A17 | `counterparties` `diplomatic-stance` | `IPassageRule.Grants(world, grantor, requester)` cannot see the logged band snapshot that `Level` needs for clan passage; add the snapshot to the seam (`trade-access` §4) |
| E-A18 | `rift-trade` | The Rift Anchor's "Grand Exchange in the same world" check reads `Hubs.TradeTier(world, faction) ≥ 4` (`exchange-hub` §7); no second check |
| E-A19 | `sector-yield` `banking-fact` | **Answered by sector-yield's reconciliation:** its hold reads registered `IBankingHoldSource`s (`spec-banking-fact.md` §3a); `order-book` registers `OpenSellNeed` as one. ~~Open: what "open sell orders" means (OQ-4)~~ — decided by round 5 A4/X15: other traders' open buy orders at this hub |
| E-A20 (**answered concurrently:** `counterparties/spec-clan-seeding.md` rule 2a) | `counterparties` `clan-seeding` | **Round 5 B3:** seed a **tier-1 Caravan Yard** (`caravan-yard` row, X12) in each clan's hub sector beside its tier-1 hub, so caravans can unload there (`exchange-hub` §4; the check is `fleet` `depot` `ForeignSite.Of`). The clan's hub sector needs a free slot the yard row allows (`Wildland`); where a template lacks one, the slot comes with the clan's own template version (world-continuity `world-creation` §5 rule 1) |
| E-A21 (**answered concurrently:** `fleet/spec-depot.md` `ForeignSite.Of`, refusal `depot.no-foreign-yard`; `trade-route-order` reads it) | `fleet` `trade-route-order` / `depot` | **Round 5 B3:** the `Unloading` and `ReturnLoading` legs at a foreign hub need the hub owner's Caravan Yard; `fleet/spec-depot.md`'s FQ1 default *"no"* is superseded. `exchange` keeps no second check |
| E-A22 (**answered concurrently:** `counterparties/spec-diplomatic-stance.md` no longer names `StructureKind.Embassy`) | `counterparties` `diplomatic-stance` §9 | **Round 5 X1/X10/X16:** `DiplomacyGate.TierOf` delegates to `sector-features` `FactionTier(world, faction, SectorFeature.diplomacy)`; drop `StructureKind.Embassy` (the Embassy row stays `Enable`-role with `structureKind: none` until a loam or siege rule needs a kind) |
| E-A23 | world-map / structures program (`BuildResolver`, `WorldValidation`, the siege board) | **Round 5 B1:** accept a slot whose kind is in `StructureDef.RequiredSlotKinds` (the new multi-kind field) instead of equal to the single `RequiredSlotKind` — `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:84`, `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:411`, `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:267`, `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs:363`; specified in `exchange-hub` §3, the field's first consumer |
| E-A24 (**answered:** `trade-foundation/spec-ledger-keys.md` §4 lists `deal-leg`, added 2026-09-20) | `trade-foundation` `ledger-keys` | `settlement-payment` §7 asks for a sixth exchange kind, `deal-leg` (treaty deal legs), which `spec-ledger-keys.md`'s table does not list. Add it beside the five settlement kinds (round 5 X2 fixes the five; `deal-leg` is a treaty leg, not a settlement kind, so X2 does not remove it) |

## Required amendments to other documents (not made by the spec session)

- `docs/architecture/item/ssot-materials-crafting.md` §7.3 and the comment at
  `gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs:46-48` — the catalyst lock: trade becomes a
  second, priced catalyst source; salvage stays at never (`tradeable-goods`, in its implementing commit).
- `docs/architecture/empire-resource-ssot.md` §3 — the `catalyst.*` and `souls` Conversions cells
  (`tradeable-goods`).
- `docs/architecture/trade-network-ideal.md` §7.7 and `docs/architecture/trade-network-map.md` §5
  invariant 3 — the corrected closed-cycle rule (`exchange-invariants`, EC1).
- `docs/architecture/world/spec-ai-commander.md:284` — *"no diplomacy"* (counterparties ask A5).
- `docs/architecture/power/ssot-power-scale.md` §10.2 and `docs/architecture/power/inventory.json` — the
  value-index row (`goods-valuation`).

## Contradictions found

| # | Where | What | Resolution |
|---|---|---|---|
| EC1 | Ideal §7.7, *"any closed trade cycle across any number of hubs in one turn loses value"* | Read as "same goods", false: value moved between places can gain | **Closed = every good returns to every location it started at.** The cycle then decomposes into per-hub round trips; a non-empty closed cycle costs the player souls and cannot settle for an AI (`exchange-invariants` I4) |
| EC2 | Ideal §7.2 vs `DelvePrices.cs:49-58` | The merchant needs an item price in souls; items are not goods | The item program derives item prices from `goods-valuation` (E-A1) |
| EC3 | Ideal §7.3 vs `empire-resource-ssot.md` §3 | Three catalysts are registered; the table names two | `temper` has no salvage lock, so it is tradeable; only forge and flux need the amendment |
| EC4 | Ideal §8.7 command list | No cancel, no diplomacy verbs | Cancel is `order-set` at 0; `treaty-lifecycle` adds eight kinds |
| EC5 | Map tunable `center.clearingByLevel` | A structure has no level (`StructureCatalog.cs:134`); a per-level table is a private `f(level)` | Dropped. Capacity = row band × Market bonus × staffing × the sector's content scale |
| EC6 | Map module 1 (scale the soul leg through `SoulSinkPolicy.Price` with the hub's Θ) vs assumption 4 | Trade quantities already carry the content scale; scaling the soul leg again would square it | Scale once: in the quantity for trade, in `SoulSinkPolicy.Price` for a pin-priced item. The `host-content-theta` dependency is dropped |
| EC7 | Map module 5 touches the role tuple and `ROLE_TO_STRUCTURE_KIND` | Both belong to `empire-seed` (`exchange-role`; `structure-bands` deletes the mapping) | `exchange-hub` adds only the C# enum member and field |
| EC8 | Map and ideal: the Market slot is "not buildable" | The engine never reads `Buildable`; `BuildResolver` gates on slot kind (`BuildResolver.cs:82-89`) | A Market-slot hub is buildable in the engine once a row requires `Market`; the client-facing flag is flipped |
| EC9 | Map module 8: the buyer pays *"from its stock at that hub"* | Nothing represents a third party's goods at another faction's hub | **Consignments** at the hub, on the hub's warehouse axis (`exchange-hub`) |
| EC10 | `counterparties` `empire-treasury` lists *"trade payments"* as a drain | An unlocated treasury paying at hubs is a channel the player lacks | Settlement never touches a treasury (E-A12) |
| EC11 | Map tunable `demandRecoveryPerTurnMilli` | `need-vector` derives demand every step and never stores it | No exchange key; nothing drifts here |
| EC12 | Map module 8: the seller receives goods *"in … an AI's treasury"* | CM3 gives the treasury one writer, `banking-fact` | Goods land in hub stock and bank later |
| EC13 | Map module 8: per-fill loss "for the buyer" | At base value a buyer can gain (buying a hub's surplus with what it lacks) | Loss is asserted at the hub's own pass-start mid prices |
| EC14 | Several maps each say `trade.v1.json` / `diplomacy.v1.json` "(new)" | `publish.py` can only bump an existing file | The first module to land authors v1 with its own keys; every other module publishes `v{n+1}` with `--add-key` |
| EC15 | Map module 9: band check at admission | Admission has no band; it arrives as the logged snapshot (CM1) | Checked at resolution, with the same named reason |
| EC16 | Map module 7: *"quote at the start of the step"* | Would stop goods a caravan unloaded this turn from selling this turn (fleet A6) | Read at the start of the exchange pass; same-pass resale is still impossible |
| EC17 | Map module 4, the walk | Pricing a step at its starting stock lets a large step round-trip at a gain | Each step is priced at the stock it leaves behind (`price-curve` §Design 3) |
| EC18 | Map module 9: an offer record in this module | `diplomacy-facts` stores offers as `offer.made`/`offer.declined` facts, and `diplomatic-stance` writes `treaty.imposed` | `treaty-lifecycle` appends facts only; no offer store, no impose entry point |
| EC19 | Q1 and `treaty-vocabulary` §3: clan `market` from `open` | Round 4 Q1: the band blocks only at `hostile`; clan trade opens with a Trading Post | `market` from `wary`, behind the building gate (`trade-access` §2a); E-A9 superseded |
| EC20 | `treaty-lifecycle` scope: *"the article list's content (`trade-ai` `counter-offer-articles` owns the list"* vs `counter-offer-articles` (TC4: the kinds are `exchange`'s) and `deal-valuation`'s goods and soul legs | Inside this cluster: each module said the other owned the articles, and exchange had no goods legs to settle a valued deal | Kinds, deal shape and refusal codes in `treaty-vocabulary` §6; legs settle in `settlement-payment` §7 (fee, no tariff, short leg ⇒ `treaty.broken` inside the minimum term) |
| EC21 | Round 4 Q2 default *"keep what open sell orders need"* vs `order-book` §2 `order.own-hub` (an owner cannot place an order at its own hub) | Read literally, the owner has no sell orders at its own hub to keep stock for | **Reading adopted:** the hold defaults to what other traders' open buy orders ask the hub to sell (`OpenSellNeed`). Stated as an interpretation; it needs no new command |
| EC22 | `acceptMilli.{band}` ownership: this map and `treaty-lifecycle` said `trade-ai`; `trade-ai-map`, `deal-valuation` and `ai-treaty-policy` said `exchange` | Each side named the other, so nobody owned the key | Owner: `trade-ai` `deal-valuation` (its one reader), stored in `diplomacy.v{n}.json`; the `hostile` value is dropped (no deal is possible at `hostile`) |
| EC23 | `treaty-lifecycle` payload `CounterpartFactionId` vs `counterparties` `diplomatic-stance`'s `TargetFactionId` (its ask A9) | Two counterpart fields on one command shape | `TargetFactionId` only |
| EC24 | `treaty-lifecycle` §8 identified the locked pair by the `Zomboss` faction kind | `diplomatic-stance` exposes `IsLockedWar` as the one rule; round 4 Q4 scopes it to the player | Read `IsLockedWar`; the dominant enemy empire treats with rivals and clans |
| EC25 (**resolved, round 5 C4:** the slots' display names are renamed; building names and ids stay; words in `trade-surface` `trade-lexicon`) | Round 4 tier names vs code | The T2 building is named "Market" while the `Market` **slot** is displayed "Market" (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74`); the T3 building "Exchange" shares its name with the whole ladder's `StructureKind.Exchange` | Wire ids stay (`market` tier, `Market` slot kind); player words decided by round 5 C4 (`trade-lexicon` §4a) |
| EC26 | trade-ai ask T-A6 names `ValueOfSouls` | `goods-valuation` already exports the inverse as `ValueForSouls` | One function, `ValueForSouls`; `deal-valuation` renamed its reference |
| EC27 | `exchange-hub` gated trade on `StructureKind.Exchange` and put a clearing band on each tier variant | `trade-foundation` `sector-features`: gates read `FeatureUnlock` only; what a tier does is the mechanism's tuning keyed by tier, never a variant band | Gates read `SectorFeature.trade`; ~~the kind stays for behaviour with an iff load rule~~ **round 6 C2: no kind at all — the neutral `Feature` loads the row and the iff rule becomes `FeatureUnlock == trade` iff `ClearingValuePerTurn > 0`**; per-tier clearing is `hub.clearingByTierMilli.{t}` (a tier table, not a level curve — EC5 intact) |
| EC28 | `trade-surface` `throttle-forecast` (first reconciliation draft) kept its own cause → building table | `logistics-flow` `forecast-facts` §2 owns the fact → answer table, including `build` [feature] | One table (forecast-facts'); the surface ranks and renders (`build-feature`) |

## Owner decisions (2026-09-19)

| # | Question | Decision |
|---|---|---|
| Q1 | Do clans need a treaty before you can trade with them? | **Current rule (round 5 X10, 2026-09-20 — follows the R5-A rules):** no treaty with a clan; `passage` from `wary`; `market` once the **trader** holds a Trading Post anywhere in that world (B4) at a clan hub that also has its seeded tier-1 hub; the band sets the spread and only `hostile` blocks; caravans unload at the clan hub through its seeded Caravan Yard (B3). *Superseded original text follows:* ~~**No. Clans trade by relation band alone: `passage` from `wary`, `market` from `open`. Preferential terms and blocs still need a treaty. Empires grant nothing without a treaty.** Built by `treaty-vocabulary` (the band-grant table) and `trade-access`. Consequence, filed as E-A9: with the approved default clan band `wary`, the first clan market opens only after a band-raising fact.~~ **Amended by round 4 Q1 (2026-09-19):** clan trade opens by building a **Trading Post**; the band sets the spread and blocks only at `hostile` — so `market` from `wary`; E-A9 superseded |

Round 4 left four questions, OQ-1 to OQ-4 in the reconciliation section; **all four were decided on
2026-09-20** (round 5 B4, C4, C3, A4 — see *Round 5* at the end).

## Tunables (keys owed by the specs; values decided by principle)

`data/tuning/trade.v{n}.json`: `goods.{id}.baseValue`, `payment.soulsPerKiloValue` (was
`payment.soulsBasePerValueMilli`), `price.bandMilli`, `price.floorUnits`, `spread.buyMilli`,
`spread.sellMilli`, `spread.byDispositionBand.{eager,open,wary}Milli` (`hostileMilli` dropped in round 4: `hostile` blocks), `fee.milli`,
`orderStepUnits`, `hub.marketSlotBonusMilli` (was `center.marketSlotBonusMilli`), `hub.clearingByTierMilli.{1..4}` (round 4, EC27), `hub.crewNeededByTier.{1..4}` (round 5 X9: exchange owns the staffing term). Dropped:
`center.clearingByLevel` (EC5), `demandRecoveryPerTurnMilli` (EC11).
`data/tuning/diplomacy.v{n}.json`: `treaty.{kind}.lowestBand`, `access.bandGrant.Clan.{passage,market}`,
`treaty.{market,preferential,bloc}.tariffBandMilli`, `treaty.{kind}.defaultTariffMilli`,
`tariff.marketDefaultMilli`, `tariff.sinkMilli`, `treaty.minimumTermTurns`, `truceTurns`.
`offerTtlTurns` belongs to `diplomacy-facts`; `acceptMilli.{eager,open,wary}` belongs to `trade-ai`
`deal-valuation` (its only reader; stored in `diplomacy.v{n}.json`; EC22). Round 4 adds one tunable, `hub.clearingByTierMilli` (what a trade tier does, EC27); the tier-to-feature
tables are registry rules (`treaty-vocabulary` §5), and `access.bandGrant.Clan.market` moves
from `open` to `wary` as a value, not a new key.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy (registry, P1/P5, conversions, soul sinks), tunables, numeric types, power
    (PS-4/PS-5 standing of the value index), world map (turn engine, commands), structures, items
    (catalyst lock, item price), Delve merchant.
[~] Session boundary: working under trade-network-idea-20260919 (docs/architecture/trade-network/**).
    session-boundary-check.py exits 1 on crossings already recorded in that record; new files only.
[~] Read this session: see counterparties-map.md's checklist (same session, same reading), plus
    item/ssot-materials-crafting.md §3, §5, §7.3 (by section, not whole), DelvePrices.cs,
    SoulSinkPolicy.cs, SalvagePolicy.cs, schema.py role tuple. NOT read: world-map-runtime ideal and
    specs (FE), creatures/spec-soul-economy.md, item-ideal.md (its no-auction-house lock is quoted from
    trade-network-ideal §4, not re-read).
[x] decisions.md:108 (loam never traded; world stocks never feed account paths) respected by
    tradeable-goods. No lock covers treaties or prices.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH finding.
[x] Verified against code: DelvePrices/SoulSinkPolicy/SalvagePolicy bodies, role tuple, StructureKind,
    reveal ordering read directly.
[x] Surrounding sections read for §7.2, §7.3, §7.7, §8.7, §12, §14b and materials-crafting §7.3.
[x] No constraint claimed without a run; stamp-gating is stated as an acceptance criterion.
[x] No §2 invariant contradicted (all in-step, deterministic, RPG layer only).
[x] Corrections: none made outside this file (fence); the catalyst amendment is scheduled into
    tradeable-goods' own change, and contradictions are listed.
[x] No population count pinned. Pinned closed vocabularies: treaty kinds (5), Access levels (4),
    trade classes (4) — each code-owned, each named as such.
[x] Caches: Access is derived per step and never cached across turns.
[x] Orderings: order-book fills are order-independent and tested with shuffled command sets.
[x] Actor magnitudes: none. Legion equipment is traded as a counted good; its stats reach ActorHub
    through legion-build, never here.
[x] No SOLID-violating path: one valuation, one soul-price function, one treaty fact list
    (counterparties), one phase (logistics-flow's).
[~] Registry rows: specified in exchange-invariants §4 (guard-trade-invariants.ps1 + one row per rule);
    they land with that module's code.
[x] Owner approval 2026-09-19 recorded; Q1 decided; module specs written under exchange/.
[x] Round 4 (2026-09-19): decisions-round-4.md read whole; reconciliation below; slot tier, upgrade
    refusal, build legion rule and slot display names verified in code.
```

---

## Reconciliation 2026-09-19 (round 4)

Applies [decisions-round-4.md](decisions-round-4.md) (binding) to this sub-program, fixes the
contradictions found inside the four downstream clusters (`exchange`, `trade-ai`, `trade-surface`,
`trade-stories`), and answers the asks other maps aimed here. Verified against code this session:
a slot holds only a `StructureId` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:119`); a second build on
an occupied slot is refused (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:71`); a `build` needs
a legion standing in the sector (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:110`,
`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:47`); the `Market` slot is displayed "Market"
(`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74`).

### R1. What round 4 changed here

| Decision | Where it landed |
|---|---|
| B — Trade ladder: Trading Post (T1 clan barter) → Market (T2 empire market orders) → Exchange (T3 preferential treaties and blocs) → Grand Exchange (T4 cross-world routes), tier variants of one row | `exchange-hub` §1, §7 (`HubTier`, `TradeTier`); `treaty-vocabulary` §5 (tier and deal-class tables) |
| B — Access = building tier AND treaty/band rules | `trade-access` §2a (`EffectiveLevel`, `LevelAt`); `order-book` §5 (suspension names the building) |
| B/Q1 — clans need no treaty; the band sets the spread; `hostile` blocks | `treaty-vocabulary` §3; `trade-access` §2; `price-curve` tunables (`hostileMilli` dropped) |
| B — Diplomacy needs an Embassy (T1 treaties with an empire); Consulate (T2) for blocs and embargo leverage; clans need no embassy | `treaty-lifecycle` §3a reads `counterparties`' `DiplomacyGate` (~~which owns `StructureKind.Embassy`, its §9~~ — superseded by round 5 X10: no Embassy kind; the gate reads `sector-features`) at admission — offerer only, per counterparties CQ1's default; losing an Embassy voids nothing and `trade-access` never reads it |
| Q2 — the home hub's per-good hold at the Treasury tier | `order-book` §6 (`OpenSellNeed` as the default, EC21); E-A11 decided, E-A19 filed |
| Q4 — never-peace applies to the player only | `treaty-lifecycle` §8 (reads `IsLockedWar`, EC24) |
| P — power roll-up | Not consumed by `exchange` (no force number here); `trade-ai` consumes it |

### R2. Asks aimed at this map, answered

| Ask | From | Answer |
|---|---|---|
| T-A5 (article kinds, deal shape, refusal terms) | `trade-ai-map.md` | `treaty-vocabulary` §6; `treaty-lifecycle` §1, §3a; `settlement-payment` §7 |
| T-A6 (own orders and offers through `IWorldView`; limit price; soul inverse) | `trade-ai-map.md` | `order-book` interface (`OwnTradeOrders`; `LimitMilli` already existed); `treaty-lifecycle` §3b (`OwnOpenOffers`); `goods-valuation` (`ValueForSouls`, EC26) |
| A9 (clan hub on its Market slot; hub closure; war voiding; collapse ⇒ closed; offer kinds; `TargetFactionId`; register `IPassageRule`) | `counterparties-map.md` | `exchange-hub` §7 (seeded tier-1 hub, E-A16); `trade-access` §2 (collapse), §4 (registration, with conflict X-3); `treaty-lifecycle` §1 (`TargetFactionId`, EC23) |
| A13 (reuse `empire-goods-sinks`' verdict shape for the soul reservation) | `counterparties-map.md` | `settlement-payment` §8: per-turn record; unification belongs to counterparties (X-4) |
| A16 (gate empire treaties on the offerer's Embassy, blocs and `embargo.set` on a Consulate, through `DiplomacyGate`; no second building check) | `counterparties-map.md` | `treaty-lifecycle` §3a, exactly as asked |
| C18 / X-C1 (clan `market` from `open` contradicts round 4) | `counterparties-map.md` | Fixed: EC19; `treaty-vocabulary` §3, `trade-access` §2 |
| A14 (rift-trade: expose the trade tier; say T4 unlocks cross-world routes) | `rift-trade-map.md` | `exchange-hub` §7 (`TradeTier`), `treaty-vocabulary` §5 (`cross-world` needs tier 4) |
| A6 (crew labour; fill foreign orders on a caravan's arrival) | `fleet-map.md` | Already answered: `exchange-hub` §2 (`staffingMilli` — round 5 X9: exchange owns the term and `hub.crewNeededByTier`; crew supplies the bearer count), `order-book` §4 (EC16) |
| A7 (an `Access` change bumps the path-cache graph version) | `logistics-flow-map.md` | Answered: `trade-access` §4 `PassageBit`, read into `path-cache`'s key (the digest was withdrawn, audit 2026-09-20); building changes never move it (passage needs no building) |

### R3. Cross-cluster conflicts (files outside this fence — not edited)

| # | Conflict | Recommended resolution |
|---|---|---|
| X-1 (**resolved** — `trade-foundation` `sector-features` now exists and cites this ask) | Round 4 needs **one shared building-tier mechanism** (slot tier, upgrade on an occupied slot, one read) for seven ladders, and the register names no owner. Without one, each consumer (`sector-yield`, `exchange`, `fleet`, `rift-trade`, `counterparties`, `legion-build`) would build its own — a SOLID defect | Owner: **`trade-foundation`, new module `building-tiers`** — the same recommendation `fleet-map.md` (A11, X-F1), `counterparties-map.md` (A14) and `rift-trade-map.md` (X-R4) reached independently. Empire-seed emits the variants; every ladder consumes the read (E-A14) |
| X-2 | The Diplomacy building needs a row and a role in the closed role list; `empire-seed`'s spec lists only `exchange` as a new role | `counterparties` ask A15 carries it; `empire-seed` `exchange-role` should widen the role list once for both (`exchange` and the diplomacy role) in one reviewed change |
| X-3 | `counterparties` `diplomatic-stance` `IPassageRule.Grants(world, grantor, requester)` has no band input, but clan passage depends on the logged band | Add the step's band snapshot to the seam (E-A17) |
| X-4 | `counterparties` has two logged-input shapes (the per-turn band snapshot record, `relation-facts`; the per-command cover table, `empire-goods-sinks`) and asks this map to follow the second | One step-input table keyed `(world, turn, inputKind, key)` inside `counterparties`; `settlement-payment` writes a `soul-budget` row there |
| X-5 | `counterparties` `clan-seeding` places "the structure `exchange`'s hub uses" on the clan's Market slot without a tier | Seed the `Exchange` row at tier 1 (E-A16) |
| X-6 | `rift-trade` must gate the Rift Anchor on a Grand Exchange in the same world | Read `Hubs.TradeTier ≥ 4` (E-A18) |
| X-7 (**resolved, round 5 A4/X15**) | `sector-yield` `spec-banking-fact.md` §3a describes the hold source as *"the quantity its open sell orders at that hub still need"* — but an owner cannot order at its own hub (`order.own-hub`) | This map's reading (EC21): the source returns other traders' open **buy** orders at the hub; sector-yield's sentence should say so, or the owner decides OQ-4 otherwise |

### R4. Closed-vocabulary widenings (each a reviewed change, listed once)

~~`StructureKind` +1 here (`Exchange` — kept for the clearing behaviour and loadability, never read as a
gate; answers `fleet-map.md` X-F1)~~ — **withdrawn by round 6 C2: this map widens no `StructureKind`.** The one
neutral `Feature` member is `trade-foundation` `sector-features`', and `Exchange` is withdrawn (round 5 X10
had already dropped `Embassy`, and `fleet` its `Depot`); `SectorFeature` is
`trade-foundation`'s (this map reads `trade`); structure role list +1 here
(`exchange`, empire-seed's; the diplomacy role is counterparties A15's); `WorldCommandKinds` + `order-set` and the eight treaty kinds; treaty kinds (5), `Access`
levels (4), Trade tiers (4), Diplomacy tiers (2), deal classes (6), article kinds (9), deal shapes (2),
refusal codes (5); `ledger-keys` fact kinds `settle-buy`, `settle-sell`, `fee`, `tariff-grant`,
`tariff-sink`, `soul-pay`, `deal-leg`; `SoulEarnPolicy.Reasons` + `trade`; trade classes (4).

### R5. Gap check

- Every module in §Modules has a spec under `exchange/` (10 of 10).
- Dependencies resolve to named modules (E-A14 became `trade-foundation` `sector-features` during this
  reconciliation).
- Tuning keys: none double-claimed after EC22 (`acceptMilli` → `trade-ai`). `tariff.sinkMilli` is
  `settlement-payment`'s; it also appears in this map's diplomacy key list as a listing, and
  `trade-access` names it as not its own — one owner.

### R6. Owner questions (genuine, round 4 left them open)

**OQ-1 — DECIDED 2026-09-20 (round 5 B4): option (a), the trader's best Trading Post tier anywhere in
that world.** *Original question:* Whose Trading Post counts for a trade at a clan's hub? Round 4 says clan trade opens by
building a Trading Post, but every clan already holds a hub.
- (a) **The requester's highest trade tier anywhere in that world** — one Trading Post opens clan barter
  everywhere you can reach. *Recommended:* it matches "build a Trading Post" as one act, and the goods
  still travel by lane or caravan, so distance is already priced.
- (b) A Trading Post in the sector the goods ship from — more building, a per-sector puzzle.
- (c) Only the hub's tier counts (clans' seeded posts suffice) — contradicts "opens by building a
  Trading Post".

**OQ-2 — DECIDED 2026-09-20 (round 5 C4): option (a), rename the slots' display names; building names
and ids stay.** *Original question:* Player names for the colliding words. The T2 building "Market" and the `Market` slot share a
display name; the T3 building "Exchange" and the whole ladder share one; the Banking T3 "Vault" and the
`Vault` slot (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:72`) collide the same way.
- (a) **Rename the slots' display names** (e.g. "Market Square", "Vault Site"); keep the register's
  building names. *Recommended:* the register named the buildings; a slot name is one catalog field.
- (b) Rename the buildings ("Bazaar", "Strongroom").
- (c) Keep both and disambiguate by context.

**OQ-3 — DECIDED 2026-09-20 (round 5 C3): option (a), a deliberate embargo needs a Consulate; war
embargoes stay automatic.** *Original question:* What does the Consulate's "embargo leverage" unlock?
- (a) **A deliberate `embargo-set` needs a Consulate; lifting and the automatic war embargo need
  nothing.** *Recommended and specced* (`treaty-lifecycle` §3a) — `counterparties` `diplomatic-stance` §9
  adopted the same reading independently, so both clusters already agree; this asks only for the owner's
  confirmation.
- (b) Anyone may embargo, but only a Consulate holder's embargo binds its bloc partners.
- (c) A Consulate embargo also closes `passage` for the target's legions (a stronger embargo).

**OQ-4 — DECIDED 2026-09-20 (round 5 A4): option (a), enough to fill other traders' open buy orders at
this hub.** *Original question:* What does the Treasury hold's default, *"keep what open sell orders need"*, count? The
hub owner cannot place an order at its own hub (`order-book` `order.own-hub`), so the owner has no sell
orders there.
- (a) **Other traders' open buy orders at that hub** — what the hub is being asked to sell.
  *Recommended and specced* (`OpenSellNeed`, EC21): no new command, and the hold follows demand.
- (b) Let the owner post sell listings at its own hub (lift `order.own-hub` for sell orders) and hold what
  they list — more control, a new order shape and a pricing rule for owner listings.
- (c) The owner's own sell orders at **foreign** hubs, holding the goods at home until caravans or lanes
  carry them there — ties the home hold to trade elsewhere.

### R7. Citation audit

`python scripts/audit-doc-citations.py --scope` was run on this map and on every edited spec under
`exchange/` after these edits: no HIGH finding.

## Round 5 (2026-09-20)

Applies [decisions-round-4.md](decisions-round-4.md) *Round 5* (R5-A owner answers, R5-X cross-cluster
rulings; binding) to this sub-program. Re-verified against code this session: a row names one slot kind
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:54`, parsed at `:297`); `BuildResolver` compares it
(`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:84`), and so do load validation
(`gk-core/src/FusionRpg.Core/World/WorldValidation.cs:411`) and the siege board
(`gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:267`, `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs:363`); the
`Market` slot type is displayed "Market" and unset `Buildable` (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74`);
`Buildable` reaches the client at `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:508` (was cited `:500`).

| Ruling | Where it landed |
|---|---|
| **A4** — hold default = other traders' open buy orders at this hub (also X15) | `order-book` §3 (`OpenSellNeed`, the owner's wording); OQ-4, X-7, E-A19 closed |
| **B1** — Trading Post on Wildland **or** Market; Market gives a bonus | `exchange-hub` §3 (`StructureDef.RequiredSlotKinds`, the `BuildResolver`/`WorldValidation`/siege-board change, acceptance 10); E-A2 corrected; E-A23 filed; `empire-seed` `trade-structure-rows` emits the field |
| **B3** — the hub's owner needs a Caravan Yard for caravans to unload | `exchange-hub` §4 (the check is `fleet` `depot` `ForeignSite.Of`, `depot.no-foreign-yard` — one predicate, no exchange duplicate; acceptance 11), §7 (clan hub + yard); E-A20, E-A21 answered by the concurrent fleet and counterparties round-5 edits |
| **B4** — the trader's best Trade tier anywhere in the world counts at a clan hub | `trade-access` §2a; `treaty-vocabulary` §5; OQ-1 closed |
| **C2** — only the offering side needs an Embassy | `treaty-lifecycle` §3a (the default is now the owner's decision) |
| **C3** — a deliberate embargo needs a Consulate; war embargoes stay automatic | `treaty-lifecycle` §3a; OQ-3 closed |
| **C4** — slot display names renamed; building names and ids stay | `exchange-hub` §3 (slot `Name` only), `treaty-vocabulary` §5; EC25 and OQ-2 closed; the words are `trade-surface` `trade-lexicon`'s |
| **X1** — every gate reads `sector-features` | Already true of `HubTier`/`TradeTier`/`trade-access`; `treaty-lifecycle` §3a and `treaty-vocabulary` §5 now say `DiplomacyGate` delegates to `FactionTier(diplomacy)`; E-A14's stale `BuildingTier(structureKind)` struck; E-A22 filed |
| **X2** — exchange's five settlement kinds | `settlement-payment` §5; `empire-treasury`'s `settle` re-points (its program's change); E-A24 files the extra `deal-leg` kind |
| **X9** — exchange owns the staffing term and its key | `exchange-hub` §2 (`staffingMilli` from `Crew.LabourAt`, `hub.crewNeededByTier`, acceptance 12); tunables above |
| **X5** — logistics-flow's step order is canonical | E-A3 now quotes it (A1 after L0–L8); `order-book` §4 already reads it by reference; B3's yard check sits in L2 (caravan unload), before banking L3 and the exchange pass A1 |
| **X10** — Q1 row follows the A-rules; `treaty-lifecycle` drops `StructureKind.Embassy` | Q1 row rewritten (old text struck); `treaty-lifecycle` §3a and dependencies; R1 and R4 rows struck |
| **X16** — Embassy uses the `Enable` role | `treaty-lifecycle` §3a cites it; no role widening beyond `exchange` |

**Not applicable here:** A1–A3, B2, C1, D1, X3, X4, X6–X8, X11–X14 (other clusters' modules; none changes an
`exchange` interface). X4's storage and X7's power roll-up are not read by `exchange`.

**New contradictions found while applying round 5** (outside this fence — reported, not edited):

- ~~`ledger-keys` lists five exchange kinds but `settlement-payment` §7 also writes `deal-leg` (E-A24).~~
  Resolved: `ledger-keys` §4 now lists `deal-leg` (audit 2026-09-20).
- B3's yard needs a free `Wildland` slot in each clan hub sector; `clan-seeding` rule 2a now adds it
  in the clan's own template version (verified in its concurrent edit) — no conflict remains.

Citation audit: `python scripts/audit-doc-citations.py --scope` run on this map and every edited
`exchange/` spec after these edits.

## Audit 2026-09-20

Independent audit of this map and its ten specs against DESIGN-GATE §2/§3/§5, PRINCIPLES,
tunables-ssot, validation-ssot, testing-standard, economy-principles, ssot-power-scale §10–§11, and the
round-4/round-5 register, with every load-bearing claim re-checked in code this session. Baseline
`audit-doc-citations.py --scope` on this map and `exchange/`: 0 HIGH before the edits.

### Findings

| # | Sev | Finding (evidence) | Status |
|---|---|---|---|
| F1 | HIGH | **Clearing capacity overflowed `long` near `Θ` ≈ 190.** `exchange-hub` §2 multiplied a magnitude (`ClearingValuePerTurn × scaleMilli`) by three per-mille factors in one `long` product; with `P(Θ) = 80 + 26.2Θ + 0.2Θ(Θ−1)` against the pin 680 (`gk-core/data/tuning/power-scale.v2.json:9`) that passes `long.MaxValue` inside normal play — a `checked` throw would stop the turn engine | **Fixed:** `BigInteger` intermediate (Core is `net6.0`, `gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:3`, no `Int128`; precedent `gk-core/src/FusionRpg.Core/Actions/Unlock/UnlockLadder.cs:38`), divided once, narrowed checked; `exchange-hub` Acceptance 13 |
| F2 | HIGH | **Ledger dedupe collisions dropped rows.** The soul row is one per (player, hub, turn) but deal top-ups (`settlement-payment` §7) wrote souls at the same hub under the same key; `INSERT OR IGNORE` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:147-150`) keeps only the first, so goods could be delivered for souls never taken. The same shape hit `settle-buy` (several traders, one hub-owner holder) and `fee` (an order and a deal at one hub and good) | **Fixed** in `settlement-payment` §5: one row per key holding the sum (the `world-stock-ledger` rule); criterion 10 |
| F3 | HIGH | **Accept-then-default deal exploit.** Deal legs delivered independently (`settlement-payment` §7, `treaty-lifecycle` §3a): a party that signs a one-off barter and cannot deliver still receives the other side in full, paying only a band drop. Open to player and AI alike | **Fixed:** one fulfilment ratio per deal, every leg delivers the same share; giving legs draw pass-start stock only; criteria in `settlement-payment` (9), `treaty-lifecycle` (11) and an `exchange-invariants` broken fixture |
| F4 | MED | **Magnitude × magnitude products in `long`.** `order-book` §8's pro-rata (`units × request`) and capacity scaling (`request × capacity`) square a content-scaled quantity, overflowing near `Θ` ≈ 1.2 × 10⁵ — the same order as the `int` limit CLAUDE.md's range table rejects | **Fixed:** `BigInteger` intermediate; `order-book` Acceptance 11 |
| F5 | MED | **`PassageDigest` had no consumer.** `logistics-flow` `path-cache` compares a per-pair passage bit in its key by value (`logistics-flow/spec-path-cache.md` §3), and `IPassageRule` already carries the band snapshot (`counterparties/spec-diplomatic-stance.md`, round 5 X14), so `trade-access` §4's digest and its "do not register" hold were both stale | **Fixed:** §4 rewritten around `PassageBit`; E-A3 and R2 A7 updated |
| F6 | MED | **Stale phase-order citation.** `order-book` §4/§6 and this map's dependency line cited `logistics-flow-map.md`'s old arrow list; round 5 X5 makes `logistics-flow/spec-logistics-phase.md` §1 (row A1) the one order | **Fixed** |
| F7 | MED | **Consignments had no canonical order.** A hashed list with three writers must write in one order or the SHA-256 state hash (`gk-core/src/FusionRpg.Core/World/Turn/StateHasher.cs:17-23`) depends on write order | **Fixed:** ordinal `(FactionId, GoodId)` order, one row per pair; `exchange-hub` Acceptance 14 |
| F8 | MED | **Culture-sensitive id ordering.** "sector-id order" / "good-id order" without `StringComparer.Ordinal` lets the host locale change fills | **Fixed** in `order-book` §6; Acceptance 10 |
| F9 | LOW | **Acceptance criteria false by rounding:** `price-curve` 6 (split walk equal in value units), `exchange-hub` 2 ("exactly"), `order-book` 3 (Σ rounded values ≤ capacity) | **Fixed:** each stated in milli or to within the final divide |
| F10 | LOW | `settlement-payment` criterion 3 asserted mid-price loss for deal legs, which are valued at the index, not walked | **Fixed:** scoped to order baskets; a deal's loss is its positive fee |
| F11 | LOW | Acceptance lists numbered out of order (`trade-access`, `order-book`, `treaty-lifecycle`) | **Fixed** |
| F12 | LOW | Franchise names in new prose (vocabulary rule): the flat-price loop, the ratio ladder, seed values, the solver exploit | **Fixed:** generic terms; prior art points at ideal §6/§13 |
| F13 | LOW | E-A24 and the round-5 "new contradiction" said `ledger-keys` lacks `deal-leg`; it lists it (`trade-foundation/spec-ledger-keys.md` §4). Module 8 text said the seller values the soul leg | **Fixed** |

**Checked and sound (no change):** one valuation (`goods-valuation` only; `deal-valuation` multiplies it
by need, never re-derives it); no second event engine or relation ladder; loam and recruits never trade;
P1/P5 (every conversion lossy — spread, fee ≥ 1, walk; souls one-way and sunk); PS-4/PS-5 (value index
level-free, scale in the quantity); P13/P14 (all in `Step`, logged inputs, dedupe keys); the flat-price
batch loop (the walk re-quotes), split and id-order gaming (aggregate + pro rata) and closed cycles (I4)
are guarded; closed vocabularies are pinned with reasons and no population is pinned; store tests run in
memory; each module names its verification boundary.

### Violations this map cannot fix (other owners)

| # | Owner | Violation | Fix |
|---|---|---|---|
| F-X1 | umbrella / ideal authors | `trade-network-map.md` §5 invariant 3 and ideal §7.7 still say "any closed trade cycle … loses value", false as worded (EC1) | Reword to "every good returns to every location it started at" in the change that lands `exchange-invariants` (a listed required amendment) |
| F-X2 (**closed, round 6 Q-A**) | `counterparties` `relation-facts` | Declaring war voids treaties as a derived effect with no `treaty.broken` (`treaty-lifecycle` §5); unless `war.declared` itself costs the observers' bands, war is a free exit from a minimum term | **Answered by the owner (Q-A, option (a)):** war inside a minimum term **also writes `treaty.broken`**, same observer effect. The fact is appended by `treaty-lifecycle` §5 (this cluster's file, done); `relation-facts` needs no new rule — it already moves bands on `treaty.broken` |
| F-X3 | `trade-foundation` `stock-deltas` | Consignments need the owner dimension on a delta (E-A8, still open) for the world-stock ledger to reconcile them | Land E-A8 before `settlement-payment` |

### Owner question — answered (round 6 Q-A)

**Q-A — Does declaring war on a treaty partner inside the minimum term count as breaking the treaty?**
**Answered 2026-09-20: (a), as recommended.** *"It also writes `treaty.broken`, with the same observer effect
as any early exit."* One rule for leaving a promise early whatever the verb, closing the war-as-exit loophole
for player and AI alike (principle 10). Not (b) — war's own band cost left the observers' side free — and not
(c): the rule is the same for every treaty kind, so there is nothing to remember per kind.

Applied in [exchange/spec-treaty-lifecycle.md](exchange/spec-treaty-lifecycle.md) §5 (one `treaty.broken` per
live treaty still inside its minimum term, breaker = declarer, `treaty.ended` for the rest; the void itself
stays derived in `trade-access`, so no second void path) and acceptance 2 (an early `treaty-end` and a war
declaration move the same bands for partner and observers). `trade-ai` `ai-treaty-policy` prices the same fact
on its End branch. No open owner question remains in this cluster.

---

## Round 6 (2026-09-20)

Applies [decisions-round-4.md](decisions-round-4.md) *Round 6* (binding, the owner's answers after the global
standards audit) and the audit items this cluster owed. Where this section disagrees with anything above, it
wins; each change is made in the named spec.

| Ruling / finding | Change in this cluster | Where |
|---|---|---|
| **C2** — one neutral `StructureKind.Feature`; **`StructureKind.Exchange` is withdrawn**; X1's wording amended | `exchange-hub` adds **no** enum member. The hub row loads under `Feature` like every other feature building; the load rule becomes the feature/field pair (`FeatureUnlock == trade` **iff** `ClearingValuePerTurn > 0`); `ClearingValuePerTurn`'s validation is keyed on the feature, not a kind; the capacity sum walks trade-feature structures. The member itself lands with `StructureDef.FeatureUnlock` in `trade-foundation` `sector-features`, ahead of the rows. This map's closed-vocabulary list (R4) no longer widens `StructureKind` at all | [exchange/spec-exchange-hub.md](exchange/spec-exchange-hub.md) Objective, Scope, §1, §2, §6, acceptance 4 and 8, Hard edges; §5 module row; R4; EC27; E-A2 |
| **C1** — one capability flag and one ruleset bump **per wave** | The global audit found `trade.exchange` gating **ten** modules across several waves — a world stamped mid-family would gain rules mid-life. Now: `exchange-hub` (wave 2) registers `trade.exchange` and it grants **only what wave 2 ships**; the wave takes **one** bump, at landing, never pre-assigned; a later exchange wave (for example `treaty-lifecycle`'s treaties and blocs, wave 3) gets **its own** flag row and bump. No spec here claims "no bump", and none mints a number — the order lives in [landing-order.md](landing-order.md) | spec-exchange-hub §5, Hard edges; [exchange/spec-treaty-lifecycle.md](exchange/spec-treaty-lifecycle.md) Hard edges; spec-order-book checklist |
| **C3** — banking waits on the save-identity re-key | Settlement itself is **not** banking work (it writes located stock and consignments only — invariant I2), so the first value-moving trade does **not** wait. What waits, stated where it touches banked materials: the hub owner's goods **banking** on a later turn, the Treasury hold that lets a hub at a bank point sell at all, and `legion-build`'s banked draw — all behind `banking-fact` → `material-ledger` → `solid-enforcement` SE4.12–SE4.38 | [exchange/spec-settlement-payment.md](exchange/spec-settlement-payment.md) §4 (the waits table); [exchange/spec-order-book.md](exchange/spec-order-book.md) §Hub-at-a-bank-point and its interface row |
| **CQ2** — legion equipment and doctrine upkeep may draw banked goods | **Does not touch settlement.** The draw is a sink inside `legion-build`'s own resolvers, through `material-ledger`'s single writer; it never passes through a fill, a consignment or this cluster, so invariant I2 stands unchanged and keeps its source scan | spec-settlement-payment §4 |
| **Q-A** — war inside a treaty's minimum term also writes `treaty.broken` | F-X2 closed: `treaty-lifecycle` §5 appends one `treaty.broken` per live treaty still inside its minimum term (breaker = declarer), `treaty.ended` for the rest, with the same observer effect as any early exit; the **void** stays derived in `trade-access`, so there is no second void path. Acceptance 2 asserts war and an early `treaty-end` move the same bands | spec-treaty-lifecycle §5, acceptance 2; F-X2; *Owner question* |
| **S1** — a feature building counts for nobody until one faction owns both its sector and its slot | Stated once in `exchange-hub` §7 and read by every gate in this cluster (`HubTier`, `TradeTier`, `trade-access`, `DiplomacyGate`, `order-book`'s hub-sector test): the rule lives inside `sector-features`' `TierOf`/`FactionTier`, and no module here compares a slot owner with a sector owner | spec-exchange-hub §7, acceptance 8; spec-treaty-lifecycle §4 |
| **S2** — trade goods cross worlds only by rift-trade route | Unchanged for this cluster and now explicit family-wide: a hub never moves a good between worlds; `rift-trade` owns the only crossing, and `world-continuity`'s advance carries none | `world-continuity/spec-advance-carry.md` §4–§5 (no change owed here) |
| **M8** — one creator per versioned tuning file | `data/tuning/trade.v1.json` is created by **`trade-foundation` `economy-report`**; `exchange-hub` (and every other spec here) publishes `v{n+1}` and no longer writes *"`trade.v1` (new)"* | spec-exchange-hub Tunables |
| **m14** — two labour-to-output shapes | The staffing term is evaluated through the one `LabourCurve` with **this cluster's own points** (`hub.staffingCurve`), whose default reproduces the old linear ramp exactly. Round 5 X9 gives exchange the term and the key, not a second evaluator | spec-exchange-hub §2 |
| **m15** — the C4 slot rename had two routes | One ask to world-map (global audit X-14) covering the `market` and `vault` slot display names; `exchange-hub` no longer edits `SlotTypeCatalog.cs` | spec-exchange-hub §3; §5 module row |
| **m16** — `OpenSellNeed` meant the opposite after round 5 A4 | Renamed `OpenBuyDemandAt` in every place it appears | spec-order-book §2, acceptance 9, interface table, checklist |
| **m10** — the legion piece catalog's producer was named twice | Named once: `LegionPieceDef` is produced by `empire-seed` `legion-bands`; `legion-build` `legion-equipment` owns the slots, recipes and production rule | [exchange/spec-tradeable-goods.md](exchange/spec-tradeable-goods.md) Dependencies |
| **m11** — two diplomacy flags with no stated relation | Stated once, in the module that consumes both: **`trade.diplomacy` ⇒ `counterparties.diplomacy`**, validated by `world-stamp` at registration (a stamp with one and not the other is a load rejection naming both); the reverse does not hold | spec-treaty-lifecycle Hard edges, §4 |
| **M1** — the `goods-valuation` ↔ `tradeable-goods` cycle needed a landing note | One line: `goods-valuation` lands **first** (it prices by good id over the registry and needs no tradeability class), then `tradeable-goods`, whose acceptance asserts the two key sets agree. Same wave, one flag, one bump, so no world sees one without the other | spec-tradeable-goods Dependencies |

### DESIGN-GATE §5 (this round)

`[x]` Read this session: the register's Round 6 (whole), the global audit (C1–C3, M1–M8, the minor table),
this map and every spec edited · `[x]` Verified against code: `StructureCatalog.cs:10-44` (the closed enum),
`:32-38` (the `Obstacle` precedent of a kind that does nothing economic), `:71-78` (one-field-one-axis
validation), `:296` (`Enum.Parse` refusal), `SlotTypeCatalog.cs:74` (the Market slot's display name),
`WorldCommandAdmission.cs:17-40` (admission's checks) · `[x]` citation audit run on every edited file ·
`[ ]` no suite run (documents only) · `[~]` session boundary: the caller's fence (this map, `exchange/**` and
the other named trees; `trade-foundation/**` read-only) · `[x]` corrections propagated (§5 module 5, R4, EC27,
E-A2, F-X2, the owner question) · `[x]` no population pinned · `[x]` no cap added (`hub.staffingCurve` is a
bounded ratio and says so; the clearing capacity stays a per-turn rate) · `[x]` no magic number (every new
value is a named tunable in `trade.v{n}.json`) · `[x]` no SOLID fork (one `LabourCurve` evaluator, one banked
writer, one void path, one settlement module).

# Spec: `exchange-invariants`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 10 of the [exchange map](../exchange-map.md) (scaffold in wave
1, complete in wave 4; approved 2026-09-19). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§3 principles 7–8, §7.3, §7.7; umbrella invariant 3 ([trade-network-map.md](../../trade-network-map.md) §5).
House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Make the exchange's promises executable. A property suite generates seeded worlds, order sets and
treaty sequences and checks five invariants against the **real** `TurnEngine.Step`, and a guard script
runs it with the source scans the other exchange specs define, so every rule has a row in the
enforcement registry. The suite asserts contracts only — never how many goods, hubs, orders, factions
or turns a run had.

## Scope and non-goals

In scope: the generators; the five invariants; the corrected closed-cycle rule; the guard script and
its registry rows.

Not in scope: the unit tests each module owns (they stay in that module's folder); balance reporting
(`trade-foundation` `economy-report` prints net flows and sink shares — this suite asserts only
invariants).

## Design

### 1. Generators

- **Worlds:** `trade-foundation` `synthetic-graph` builds seeded graphs with N empires and M clans
  (counterparties ask A4); this module adds hubs, stocks, consignments and located goods to them —
  hubs at every tier of the Trade ladder and factions with and without an Embassy (round 4), so the
  building gate is inside the generated space, and treaty deal legs (`settlement-payment` §7) are part
  of the generated sequences: I1 and I3 must hold for deals as well as orders.
- **Orders and treaties:** seeded streams from `SeededRng.DeriveStream`
  (`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26`), one stream per concern, so adding a generator never
  moves another's draws.
- **Parameters** (world size, turns, order counts) are generator inputs, printed with each run and
  never asserted (validation-ssot; DESIGN-GATE §3 rule 7).

### 2. The five invariants

| # | Invariant | How it is checked |
|---|---|---|
| **I1** | **No path increases souls.** | For every generated turn: each player's soul balance after commit ≤ before; every trade soul-ledger row has `delta ≤ 0`; no non-player faction has a soul budget or a soul row. |
| **I2** | **No world stock enters a banked stock.** | No settlement or delivery writes a wallet, material or treasury row; no fill pairs a map-bound good with a bankable one; `loam` and `recruit` appear in no fill, consignment or order. Banking itself is `sector-yield`'s and is out of this suite's reach by construction: the source scan proves `World/Trade/` never calls a banking writer. **Round 6 CQ2 does not weaken this:** legion equipment and doctrine upkeep may draw *banked goods* when local stock is short, but that draw is a sink inside `legion-build`'s own resolvers through `material-ledger`'s single writer — it is a banked store paying for a *world* cost, never a world stock *entering* a banked one, and it never passes through a fill, a consignment or any file under `World/Trade/`. The scan is unchanged and stays the guard. **Round 6 C3:** every banked path in the family lands after the save-identity re-key, so this suite's own modules never wait on it. |
| **I3** | **Round-trip loss at a single hub.** | From any generated hub state, buying `q` of a good then selling `q` back — in one pass (both legs from pass-start state) and across turns with nothing else changed (the sell walked from the stock the buy left) — returns strictly less value than it cost, for every `q ≥ 1`, step size and band. Plus the settlement half: every non-empty basket loses at the hub's own pass-start mid prices (`spec-settlement-payment.md` Acceptance 3). |
| **I4** | **A closed cycle loses value — corrected rule.** | See §3. |
| **I5** | **Determinism.** | The same seed and command log give the same `StateHash` twice, and the same hash on replay from the log with the logged step inputs (band snapshot, soul budget). |

### 3. I4 — what "closed" means, and why

The ideal says *"any closed trade cycle across any number of hubs in one turn loses value"* (§7.7) and
the umbrella repeats it (§5 invariant 3). Read as "the trader ends with the same **goods**", it is
false: with independent hub prices, a trader holding stock at hub A and at hub B can sell at A what A
pays well for, buy what A sells cheap, and do the reverse at B, ending with the same goods and more
value. That is value **moved between places** — the purpose of trade, not a loop (the map's EC1).

**The corrected rule: a cycle is closed only if every good returns to every location it started at** —
for every `(good, location)` pair, the trader's balance after the turn's fills equals its balance
before, where a location is a hub sector's consignment or the trader's own stock. Then:

- Goods bought in a pass cannot be sold in the same pass (`spec-order-book.md` §Design 6), so restoring
  a `(good, hub)` balance means buying and selling that good at that hub in the same pass: the cycle
  decomposes into **per-hub round trips**, each of which loses by I3.
- Because goods are restored exactly, the loss must be paid in something that is not a restored good.
  For the player that is **souls**: a non-empty closed cycle costs strictly positive souls. An AI has no
  souls, so for an AI **no non-empty closed cycle can settle at all** — the budget cut and sell trim in
  `settlement-payment` leave at least one `(good, location)` balance changed.

**Checked as:** over generated worlds and order sets, for every trader and turn whose fills restore every
`(good, location)` balance and are non-empty — the trader is a player and its souls strictly decreased.
A generated closed cycle for an AI is a failure with the counterexample printed.

**Required amendment (not made in this session):** ideal §7.7's invariant sentence and the umbrella
map's §5 invariant 3 are reworded to the corrected rule in the change that lands this module (DESIGN-GATE
evidence rule 6). This spec states the requirement; it does not edit either document.

### 4. The guard and its registry rows

- `scripts/guard-trade-invariants.ps1` (new) runs the suite by trait
  (`VerificationId=core.world-trade.invariants`) and the source scans the specs define:
  no `ContentScale`/`SoulSinkPolicy`/`PowerLadder` under `World/Trade/` (`spec-goods-valuation.md`
  Acceptance 4); no wallet, material, treasury or banking writer called from `World/Trade/`
  (`spec-settlement-payment.md` Acceptance 2); no `AccessLevel`-typed field on `WorldState`
  (`spec-trade-access.md` Acceptance 8).
- `gk-core/scripts/enforcement-registry.v1.json`: a `trade-invariants` entry in `guards` and one `invariants` row
  each for I1–I5, the no-scale scan, the no-stored-Access scan and order-independence
  (`spec-order-book.md` Acceptance 1), each naming `trade-invariants` as its guard. The registry's
  meta-test fails on a rule covered by nothing (DESIGN-GATE §5, last box).
- Wired into `gk-core/scripts/run_guards.py` and CI like the existing guards.

### 5. Scaffold, then completion

- **Wave 1 (scaffold):** generators on the synthetic graph; I3's pricing half against `price-curve`;
  I5 on a world with hubs but no orders (proving the new state is hash-silent); the guard script with
  the source scans that already apply.
- **Wave 3:** I1, I2, I3's settlement half, I4 — once `order-book` and `settlement-payment` land.
- **Wave 4:** the full suite over treaties and blocs (`treaty-lifecycle`), and over many-empire worlds.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | The determinism guard over the World tree | `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-48` |
| Built | The enforcement registry: `guards`, `invariants`, a meta-test | `gk-core/scripts/enforcement-registry.v1.json` |
| Built | Named deterministic streams | `gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26` |
| Built | A pure `Step` returning its hash | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:157-199` |
| Real gap | The generators beyond `synthetic-graph`, the suite, the guard, the rows | — |

## Tunables

None. Generator parameters are test inputs, printed.

## Acceptance (contract)

1. I1–I5 hold over the generated space at each wave's scope; each failure prints the seed and a minimal
   counterexample.
2. No assertion names a count of goods, hubs, orders, factions, turns or cases; runs print them.
3. Every rule listed in §4 has a registry row naming `trade-invariants`, and the registry meta-test
   passes.
4. A deliberately broken fixture fails each invariant: a settlement that credits one soul (I1); a fill
   that pairs rubble with essence (I2); a walk priced at the step's starting stock (I3, the exploit
   `spec-price-curve.md` §Design 3 closes); a sell of goods bought in the same pass (I4); a
   `System.Random` in `World/Trade/` (I5, through the existing determinism guard); **a deal whose legs
   settle independently, so a party that delivers nothing still receives its counter-leg** (the
   accept-then-default exploit `settlement-payment` §7 closes — audit 2026-09-20; fails I4's per-hub
   loss for the defaulter's counterpart). Each broken fixture lives in the test project and never in
   `src/`.
5. **Deals inside I4 (audit 2026-09-20).** The closed-cycle check includes deal legs: a cycle mixing an
   order round trip and a deal leg at one hub still costs the player strictly positive souls or leaves a
   `(good, location)` balance changed (deal legs pay a positive fee and draw only pass-start stock).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Invariants/` (new), trait `core.world-trade.invariants`,
  boundary row `core-world-trade-invariants`; the guard script's own test in
  `gk-core/tests/FusionRpg.Guard.Tests/`.
- `verify-change.ps1 -Paths` selects the invariants boundary for any change under `World/Trade/`
  (the boundary row lists `src/FusionRpg.Core/World/Trade/**` as a seam into it).

## Hard edges

- **Contract, not population** (validation-ssot).
- **Real engine.** The suite drives `TurnEngine.Step`; it never re-implements settlement to check it.
- **Broken fixtures stay in tests.**

## Dependencies

- Upstream: every module in this map; `trade-foundation` `synthetic-graph`; `counterparties`
  (`diplomacy-facts`, `relation-facts` for generated bands).
- Downstream: CI; `trade-ai` (its bids must pass the same invariants when it lands).

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy (souls, world stocks), determinism, guards/registry.
[~] Session boundary: trade-network-idea-20260919; new file only; the check's exit 1 is the recorded
    broad-lane crossing.
[x] Read this session: trade-network-ideal §3, §7.3, §7.7; trade-network-map §5; DESIGN-GATE §3 rule 7
    and §5; the other nine exchange specs (written this session).
[x] decisions.md :108 respected.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: the registry's shape (guards dict, invariants rows with guards /
    unguardableReason), the determinism guard's banned list.
[x] Surrounding sections read (ideal §7.7 whole; umbrella §5 whole).
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: EC1's corrected rule stated here and in the map; the ideal and umbrella
    amendments listed as requirements.
[x] No population count pinned.
[x] No event-refreshed cache.
[x] Orderings: order-independence is one of the registered rules.
[x] No actor magnitude.
[x] No SOLID-violating path.
[x] Registry rows: this module is where they land (§4).
[x] Audit 2026-09-20 (independent): added the default-exploit broken fixture and the deal-leg case of I4;
    the umbrella §5 invariant 3 and ideal §7.7 still carry the uncorrected closed-cycle sentence
    (required amendment above, not yet made — reported in exchange-map Audit 2026-09-20).
```

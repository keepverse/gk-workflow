# Trade-network family — the one landing order

**Status:** binding for every spec under `docs/architecture/trade-network/**`,
`docs/architecture/world-continuity/**`, `docs/architecture/legion-build/**` and
`docs/architecture/empire-seed/**`. Written 2026-09-20 to carry round 6 C1 (*"One capability flag and one
ruleset bump per wave … the family keeps a single landing order (see `landing-order.md`)"* —
[decisions-round-4.md](decisions-round-4.md) Round 6) and to answer the global audit's M1–M8
([audit-2026-09-20-global.md](audit-2026-09-20-global.md) §3).

This file is the family's **integration ledger**: the wave order, the capability flag and ruleset bump each
wave carries, the shared-file landing order, one creator per tuning file, the golden re-bless points, and
the cross-program blockers. Where a sub-program map's own build order disagrees with this file, **this file
wins for order and for bump numbering**; the map wins for what each module does.

**Reconciled 2026-09-20.** The first draft of this file left the internal wave splits and flag ids of
`exchange`, `trade-ai`, `trade-surface`, `trade-stories`, `legion-build`, `empire-seed` and
`world-continuity` marked *"owner confirms"*. All seven are now settled, together with twenty other
questions the seven planning fragments raised — §10 records each ruling, what it changed and why. §2 is
therefore the whole family's wave order, and no row says "owner confirms" any more.

---

## 1. The rules this order applies

**R1 — a capability flag never spans waves.** A flag's `IntroducedAtRuleset` must be strictly above every
ruleset any world was stamped with before the flag's row existed, or a world created before the behaviour
gains it mid-life and its hash moves — the D-C breach the stamp exists to prevent
([trade-foundation/spec-world-stamp.md](trade-foundation/spec-world-stamp.md) §2, *"The bump is
mandatory"*). So every behaviour a flag gates ships in the **one wave** that registers it. A later wave of
the same sub-program gets its **own** flag, never a widening of the earlier one.

**R2 — one ruleset bump per wave.** The change that lands a wave bumps
`TurnEngine.RulesetVersion` (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`, **13** today) by one and
uses the new value for every capability row the wave registers. Where a wave's behaviour is several
independently-gated surfaces, its rows **share that one bump** — which the stamp spec already allows
(*"Several capabilities shipped in one change may share one bump"*, `spec-world-stamp.md` §2). A wave never
takes two bumps, and two waves never share one.

**R3 — infrastructure takes neither.** A wave that adds only test-only builders, pure queries, ledger
tables, report text or schema columns — nothing `Step`'s behaviour or the canonical projection reads — takes
**no flag and no bump**, and says so with that reason. This is not the withdrawn *"no bump needed"* claim:
that claim was made for **feature grants** (`sector-yield` `banking-fact`, `logistics-flow`
`logistics-phase`) and is void everywhere in the family. A spec may only claim "no bump" for a wave that
grants no capability.

**R4 — the bump number in this file is an ordinal, not a literal.** The engine constant moves under the
family (every program bumps it), so the table's column reads `N+1`, `N+2`, … where `N` is the constant at
the moment the *first* row of this table lands. A lane that bumps **rebases onto the latest constant and
takes the next integer**; a capability row references the constant, never a literal (M2). The ordinal fixes
the **order** of the bumps, which is what a stamped world's rules depend on.

**Three ordinal series, because three lanes bump independently.** §2 carries the trade-network spine
(`N+1` … `N+25`), the legion-build lane (`L1` … `L10`) and the world-continuity lane (`C1` … `C4`);
`empire-seed` bumps nowhere (R3, see §10 R-15). A series fixes the order **within its lane** and at the
trade rows its waves land after — the legion and continuity waves that anchor in phase 0 are deliberately
unordered against trade rows 1–25, because nothing makes one wait for the other. The absolute integer is
never fixed anywhere: whichever lane lands next **rebases onto the live
`TurnEngine.RulesetVersion` and takes the next integer**, and its capability rows reference that constant.

**R7 — the first flag and the first bump of the whole family belong to row 0d, `trade.sectorFeatures`.**
Row 0a's exemption (*"the registry ships empty"*) does not stretch to cover `sector-features`:
[trade-foundation/spec-sector-features.md](trade-foundation/spec-sector-features.md):152-160 turns a `build`
order naming the structure already on the slot into an **upgrade** instead of a `build.occupied` refusal.
That changes how an existing world's stored order resolves — the mid-life rule change R1 exists to prevent
— so it cannot ship unflagged in an unbumped wave, even though no shipped template places a structure and
so no golden moves today. `sector-features` therefore lands in its own row after the schema and rows it
reads (§10 R-1), registers `trade.sectorFeatures` and takes ordinal **N+1**.

**R5 — feature buildings load under one neutral kind.** Round 6 C2: all feature buildings load as
`StructureKind.Feature`; `StructureKind.Exchange` is withdrawn; ruling X1's wording is amended to allow this
one neutral kind. No gate ever reads a kind — a gate reads `FeatureUnlock` through `sector-features`
([trade-foundation/spec-sector-features.md](trade-foundation/spec-sector-features.md) §1–§5).

**R6 — a feature building counts for nobody until one faction owns both its sector and its slot** (round 6
S1). The rule lives in `sector-features` §5 (`TierFor` / `FactionTier`); every gate reads it there.

---

## 2. Waves in build order, with flag and bump

`—` in the bump column means R3 (no capability, no bump). The **Lands after** column is what makes the
reading order safe: a row with no entry is unordered against the rows around it and may land in parallel.
Nothing in this table says "owner confirms" any more — the reconciliation of 2026-09-20 (§10) closed all
seven open splits, so this table is now the whole family's wave order, flags and bump ordinals.

| # | Wave | Modules | Capability flag(s) | Bump | Lands after |
|---|---|---|---|---|---|
| 0a | `trade-foundation` W0 — **minus `sector-features`** | `synthetic-graph`, `routing-guard`, `step-benchmark`, `ledger-keys`, `stock-deltas`, `world-stamp`, `system-commands`, `economy-report`, `world-stock-ledger` | none — the registry ships **empty**, so `GrantedBy` is empty and no hash moves (`spec-world-stamp.md` §3) | — | — |
| 0b | `empire-seed` W1 — I1–I5, the role widening, the anchor-schema widening, the name index and the metric set | `structures-adapter`, `band-reader`, `structure-bands`, `world-exemplars`, `world-budgets`, `exchange-role`, the schema widening (`featureUnlock`, the closed `variants` item, `requiredSlotKinds` — M5), `world-name-index`, `corpus-metrics` | none — seed content, tuning bands, a load-time reader and pure queries (R3) | — | 0a |
| 0c | `empire-seed` W1b — `trade-structure-rows` | the **eight** feature rows (round 6 L6 added the Standard Hall), emitted `StructureKind.Feature` (R5) | none — authored seed content (R3) | — | 0b |
| **0d** | **`trade-foundation` `sector-features`** | `sector-features` — the feature-tier read, the `TierFor`/`FactionTier` split-owner rule (S1, R6) and the `build`-on-own-slot upgrade arm | **`trade.sectorFeatures`** — the family's first flag (R7) | **N+1** | 0c |
| 0e | `legion-build` W1 | `member-stack`, `caravan-kind-retire`, `role-aware-placement` | `legion.rolePlacement`, registered by `role-aware-placement` — the only wave-0e change that makes an existing world's stored command log resolve a siege differently (`WorldTemplateCatalog.cs:196`). `member-stack` rides the bump and registers nothing; `caravan-kind-retire` adds nothing | **L1** | 0d |
| 0f | `world-continuity` W1 | `world-state-vocabulary`, `seat-outcome`, `continuity-doc-amendment` | none — a schema column, two closed vocabularies, a pure detector and documents; `state` is never hashed and `outcome` stays at its default (R3) | — | 0e |
| 0g | `trade-foundation` `material-ledger` | `material-ledger` | none — a ledger-first verb (R3) | — | 0f; **waits on X-1** (§7) |
| ES2 | `empire-seed` W2 | `call-budget-dry-run`, `decision-45-revision` | none — a planner budget whose dry run calls nothing, and a documents-only ownership revision (R3) | — | 0c |
| ES3 | `empire-seed` W3 | `world-namer` | none — seed content (R3) | — | ES2 |
| ES4 | `empire-seed` W4 | `legion-seed-contract` | none — schemas, a registry and hand-authored exemplars (R3) | — | ES3; `legion-build`'s three **approved specs** (slot list, trigger facts, carrier roles) |
| ES5 | `empire-seed` W5 | `legion-bands` | none — a tuning file and a load-time resolver (R3) | — | ES4 |
| ES6 | `empire-seed` W6 | `legion-seed-rows` | none — generated seed content (R3) | — | ES5; L7's shipped mechanics |
| L2 | `legion-build` W2 | `stack-combatant`, `raise-choice`, `legion-owner-scope`, `standing-orders` | `legion.stacks` (`stack-combatant`, with `raise-choice` as its producer half) and `legion.standingOrders` (`standing-orders`) — two rows, **one** bump (R2). `legion-owner-scope` ships an empty contributor list and adds nothing | **L2** | 0e |
| L3 | `legion-build` W3 | `general-member-hub` | `legion.generalHub` | **L3** | 0e; `species-progression` `layer-source-selector` |
| L4 | `legion-build` W4 | `escort-stance`, `legion-cohesion` (code half), `legion-traditions`, `legion-count-cost` (code half), `legion-power` | `legion.escortStance` and `legion.traditions` — two rows, one bump (R2). The other three land **inert** (empty bands, a flat curve, a roll-up nothing in `Step` reads yet) and add nothing (R3) | **L4** | L2 |
| L5 | `legion-build` W5 | `field-battle-kinds` | `legion.fieldBattles` | **L5** | L4 |
| L8 | `legion-build` W8 | `legion-cohesion` (band publish) | `legion.cohesionBands` — a flag is never registered before the behaviour it gates exists, so the publish that fills the bands is its own landing | **L8** | L4 |
| L9 | `legion-build` W9 | `legion-count-cost` (curve publish) | `legion.countCostCurve` — same reason as L8 | **L9** | L4 |
| WC2 | `world-continuity` W2 | `hibernation-clock` | none — a save-scoped counter column and a ledger tick re-key; no world's `StateHash` moves (R3) | — | 0f |
| WC3 | `world-continuity` W3 | `world-victory`, `coarse-step`, `world-fall` | `continuity.worldOutcome`, registered by `world-victory`; `coarse-step` and `world-fall` ride it | **C1** | WC2 |
| WC4 | `world-continuity` W4 | `world-warden`, `idle-world` | `continuity.warden`, registered by `world-warden`; `idle-world` rides it | **C2** | WC3 |
| 1 | `sector-yield` W1 — stocks, capacity, halt, bank-point query | `located-goods-registry`, `essence-loop-read`, `warehouse-axis`, `located-stock`, `production-halt`, `bank-points` | `trade.sectorYield` (registered by `located-stock`) | **N+2** | 0d |
| L6 | `legion-build` W6 | `legion-standards`, `legion-doctrine` | `legion.standards` and `legion.doctrine` — two rows, one bump (R2); both spend located stock inside `Step` | **L6** | 1, 0c, L2 |
| 2 | `sector-yield` W2 — the structure loam term | `structure-upkeep` | `trade.structureUpkeep` | **N+3** | 0d |
| 3 | `sector-yield` W3 — structures yield goods | `yield-structures` | `trade.yieldStructures` | **N+4** | 1, 2 |
| 4 | `sector-yield` W4 — the `Logistics` **phase slot** (`banking-fact` part 1: the slot, its report phase, the `decisions.md:7` amendment; no good banks yet) | `banking-fact` (slot half) | `trade.bankingPhase` | **N+5** | 0a |
| 5 | `logistics-flow` W1 — the phase steps | `logistics-phase`, `logistics-canonical` | `trade.logistics` (registered by `logistics-phase`) | **N+6** | 4, 1 |
| 6 | `logistics-flow` W2 — lanes | `path-cache`, `lane-flow`, `transit-buffer`, `lane-loss`, `logistics-facts` | `trade.logisticsLanes` | **N+7** | 5 |
| 7 | `logistics-flow` W3 — policy and building | `auto-banking`, `construction-chain`, `lane-verbs` | `trade.logisticsPolicy` | **N+8** | 6 |
| 8 | `sector-yield` W5 — goods **leave the map** (`banking-fact` part 2: the L3 step, the rate, the hold, the fact, the commit-time credit) | `banking-fact` (step half) | `trade.banking` | **N+9** | 7, 0g — **after save identity** (§7) |
| L10 | `legion-build` W10 | `legion-equipment` (banked-draw half), `legion-doctrine` (banked-draw half) | `legion.bankedDraw` — both arms land in one change | **L10** | 8, 0g, L6, L7 |
| 9 | `logistics-flow` W4 — read model and gate | `forecast-facts`, `logistics-bench` | none — *"the forecast writes nothing"* ([spec-forecast-facts.md](logistics-flow/spec-forecast-facts.md) §Ruleset) and the bench is a test (R3) | — | 7 |
| 10 | `sector-yield` W6 — located income | `income-parity` | `trade.incomeParity` | **N+10** | 8 |
| 11 | `sector-yield` W7 — legion equipment as a located good | `legion-equipment-stock` | `trade.legionEquipStock` | **N+11** | 1 |
| L7 | `legion-build` W7 | `legion-equipment` (located-stock half) | `legion.equipment` | **L7** | 1, 11, L3, 0c |
| 12 | `fleet` W1 | `carried-goods`, `depot` | `trade.fleet` (registered by `carried-goods`) | **N+12** | 5, 1, 0e |
| 13 | `fleet` W2 | `crew`, `trade-route-order` | `trade.fleetRoutes` (registered by `trade-route-order`) | **N+13** | 12, L2 (`standing-orders`) |
| 14 | `fleet` W3 | `escort-link`, `interception`, `goods-cargo-fate` | `trade.fleetEscort` (the wave's one flag; `interception` and `goods-cargo-fate` are not escorts but ride it) | **N+14** | 13, L4, L5 |
| 15 | `counterparties` W1 | `need-vector`, `empire-roster`, `diplomacy-facts`, `empire-treasury`, `trade-difficulty-knobs` | `counterparties.needs`, `.roster`, `.diplomacy`, `.treasury` — four rows, **one** bump (R2). `trade-difficulty-knobs` adds none: the profile id is already stamped at creation (CM10) | **N+15** | 1; `empire-treasury`'s **credits** alone wait on row 8 (§7) |
| 16 | `counterparties` W2 | `diplomatic-stance`, `relation-facts`, `clan-seeding` | `counterparties.stance` (stance + relation facts, registered by `diplomatic-stance`), `counterparties.clans` (`clan-seeding`) — two rows, one bump | **N+16** | 15, 0c |
| WC5 | `world-continuity` W5 | `world-creation`, `advance-carry` | `continuity.advance`, registered by `world-creation`; `advance-carry` rides it | **C3** | 16 — the A1 start kit needs `empire-roster`'s v2 templates, and the template goldens are one shared re-bless (§6) |
| WC6 | `world-continuity` W6 | `background-yield`, `world-event-budget`, `world-difficulty-profile` | `continuity.backgroundEconomy`, registered by `background-yield`; the other two ride it (`world-difficulty-profile`'s `default` profile is hash-neutral) | **C4** | WC5, 1 |
| WC7 | `world-continuity` W7 | `away-digest` | none — report entries and notification drafts derived from stored coarse and idle records (R3) | — | WC6 |
| WC8 | `world-continuity` W8 | `multiverse-surface` | none — a read-only FE layer; its unlocks are UI milestones, not stamp capabilities (R3) | — | WC7 |
| 17 | `counterparties` W3 | `clan-economy`, `empire-goods-sinks`, `conquest-consequences` | `counterparties.clanEconomy`, `.sinks`, `.conquest` — three rows, one bump | **N+17** | 16, 8 |
| 18a | `exchange` W1 — value, classes, prices, the treaty registry | `goods-valuation`, `tradeable-goods`, `treaty-vocabulary`, `price-curve`, `exchange-invariants` (scaffold) | none — a value table, a class table, a pure Math file, a hand-authored registry and a test scaffold (R3) | — | 0a, 1, 15 |
| 18b | `exchange` W2 — the hub on the map, and derived access | `exchange-hub`, `trade-access` | `trade.exchange`, registered by `exchange-hub` | **N+18** | 18a, 17 |
| 18c | `exchange` W3 — orders, settlement, treaties | `order-book`, `settlement-payment`, `treaty-lifecycle`, `exchange-invariants` (settlement half) | **`trade.exchangeOrders`** (registered by `order-book`, gating `order-set` admission and settlement writes) **and** `trade.diplomacy` (`treaty-lifecycle`; `trade.diplomacy` ⇒ `counterparties.diplomacy`, m11) — two rows, **one** bump (R2, row 15 is the precedent) | **N+19** | 18b |
| 18d | `exchange` W4 — the invariant suite complete | `exchange-invariants` (complete) | none — tests only (R3) | — | 18c, 16, 17 |
| 19a | `trade-ai` W1 — belief, valuation, the two bounds | `trade-intel`, `ai-spend-limit`, `deal-valuation` | **`trade.intel`**, registered by `trade-intel`, which hashes AI belief inside `Step` and adds two `WorldCanonical` row kinds. `ai-spend-limit` and `deal-valuation` register nothing (R3: policies run outside `Step`) | **N+20** | 18c |
| 19b | `trade-ai` W2 | `counter-offer-articles`, `ai-bidding` | none — policies outside `Step` (R3) | — | 19a |
| 19c | `trade-ai` W3 | `ai-treaty-policy`, `ai-logistics` | none (R3) | — | 19b, 13, L2 (`standing-orders`), L4 (`escort-stance`) |
| 19d | `trade-ai` W4 | `ai-trade-buildings` | none (R3) | — | 19c |
| 19e | `trade-ai` W5 | `interdiction`, `clan-behaviour` | none (R3) | — | 19d, 17 |
| 20 | `rift-trade` W1 | `rift-route`, `crossing-goods`, `crossing-anchor` | `trade.riftTrade` (registered by `rift-route`) | **N+21** | 18b, 13, 0f |
| 21 | `rift-trade` W2 | `crossing-leg`, `crossing-handoff` | `trade.riftCrossing` (registered by `crossing-handoff`) — never a widening of `trade.riftTrade` | **N+22** | 20, WC2 |
| 22 | `rift-trade` W3 | `sleeping-endpoint`, `endpoint-loss`, `rift-facts` | `trade.riftEndpoints`, registered by `sleeping-endpoint` for the wave | **N+23** | 21, WC3, WC4, WC7 |
| 23 | `logistics-flow` W5 — the power switch | `lane-loss` escort-strength switch (round 4 §P) | `trade.laneLossPower` — its own flag, never a widening of `trade.logisticsLanes` | **N+24** | 6, L4 (`legion-power`); **waits on X-2** (§7) |
| 24a | `trade-surface` W1 — vocabulary and the read contract | `trade-lexicon`, `trade-wire` W1 | none — read-only surface; its `TradeCapabilities` are milestone UI unlocks, **not** stamp capabilities (`spec-world-stamp.md` §Exposed) | — | 1, 0d |
| 24b | `trade-surface` W2 — the steady-state turn | `trade-unlock`, `trade-wire` W2+W3, `trade-status`, `throttle-forecast` | none — `trade-unlock`'s milestone set is gated by the **producers'** flags and is empty without them (§10 R-16) | — | 24a, 6, 9 (and 8 for `Banked`) |
| 24c | `trade-surface` W3 — sector surface, map lens, rail rows | `trade-panel`, `flow-lens`, `trade-notify` | none | — | 24b |
| 24d | `trade-surface` W4 — editors and the power-loop payoff | `trade-wire` W4+W5, `trade-policy-editor`, `blocked-demand` | none | — | 24c, 7, 18c, 19a |
| 24e | `trade-surface` W5 — diplomacy and the click budget | `treaty-screen`, `trade-click-budget` | none | — | 24d, 15–18 |
| 25a | `trade-stories` W1 — the fact vocabulary | `trade-fact-kinds` | none — a vocabulary declaration with no writer (R3) | — | 18c |
| 25b | `trade-stories` W2 — projector, hosts, leaves, content asks | `trade-fact-source`, `trade-hosts`, `trade-predicates`, `trade-storylet-supply` | none — the projection is proven hash-neutral, hosts decide only *when* to ask, leaves read hashed state and write none (R3) | — | 25a, 16 |
| 25c | `trade-stories` W3 — pacing, reachability, seasons | `trade-story-pacing`, `trade-trigger-reachability`, `seasonal-demand-shocks` | **`trade.demandShock`**, registered by `seasonal-demand-shocks` — the shock is a term in the demand function `exchange` reads, so it moves prices on a live world (§10 R-7). Pacing and reachability register nothing | **N+25** | 25b, 15, 18b |
| 25d | `trade-stories` W4 — quests and failure branches | `trade-quests`, `trade-failure-branches` | none — template rows and branch semantics over already-declared facts (R3) | — | 25c, 17, 18c |

**Consequences recorded, not hidden.**

- **`banking-fact` lands in two waves (rows 4 and 8), and that is what unblocks logistics.** CM4 makes
  `banking-fact` the creator of the `Logistics` phase slot, and `logistics-flow` extends the same phase — so
  if the whole module waited on `material-ledger` (C3), every logistics wave would wait on the save-identity
  re-key too. The slot has no ledger dependency: it is a phase name, a report phase and the `decisions.md:7`
  amendment. Round 6 C3 defers *"`material-ledger` and the banking work that needs it"*, which the slot is
  not. Splitting the module's landing is a wave split inside one owner, **not** a second owner of the phase —
  CM4 is unchanged.
- `structure-upkeep` (row 2) *can* land alone, which the audit flagged as impossible while its flag was
  unregistered (SY-A1, build-readiness). Under R1/R2 it is its own wave with its own flag and bump, so the
  *"can land first"* claim is now true as written.
- Row 7 lands `auto-banking`'s default destination and its `route-set`/`route-clear`/`bank-hold` commands
  **before** anything banks: goods flow to the nearest bank point and wait there. The hold state and the
  hold-source seam are registered; the first good leaves the map at row 8.
- `trade.incomeParity`'s ordinal (N+10) is after `trade.logistics` (N+6) and after banking (N+9), which
  [sector-yield/spec-income-parity.md](sector-yield/spec-income-parity.md) §5 requires for the first and
  needs for the second (a located reward is credited by banking).
- **`counterparties` W1 as a whole does not wait on banking.** It needs `sector-yield` located goods (row 1).
  Only `empire-treasury`'s **credits** need `banking-fact`'s destination seam (row 8, CM3): the field, the
  canonical row, the seam registration, the sink and the collapse rules all land at row 15, and **every
  treasury reads zero** until row 8, with the economy report printing that zero *with its reason*
  ([counterparties/spec-empire-treasury.md](counterparties/spec-empire-treasury.md) §7 already says so).
  `need-vector`, `empire-roster`, `diplomacy-facts` and `trade-difficulty-knobs` have no X-1 dependency at
  all (§10 R-8).
- `rift-trade` W1 needs `exchange`'s Grand Exchange tier read, so it sits after row 18b — the umbrella's own
  build order item 6.
- Row 23 waits on cross-program ask X-2 (§7).
- **`exchange` takes two bumps, not one, and that is why row 18 is split into four sub-waves.**
  `spec-exchange-hub.md:249` and `spec-order-book.md:53` both gated `order-set` on `trade.exchange`, which
  `exchange-hub` registers in wave 2, while `order-book` lands in wave 3. A world stamped between the two
  waves would have gained `order-set` mid-life — the R1 breach. Wave 3 therefore registers its own flag,
  `trade.exchangeOrders`, and shares wave 3's single bump with `trade.diplomacy` (§10 R-5). Merging 18b and
  18c would also have worked arithmetically and was **not** taken: it would put hub, orders, settlement and
  treaties in one landing.
- **Row 19 is not bump-free.** Nine `trade-ai` modules are policies outside `Step` and register nothing, but
  `trade-intel` hashes belief inside `Step` and appends two `WorldCanonical` row kinds, so 19a registers
  `trade.intel` and takes one bump (§10 R-6).
- **Row 25 takes one flag.** Nine `trade-stories` modules project producers' records and ride the producers'
  flags; `seasonal-demand-shocks` is a demand **term**, so 25c registers `trade.demandShock` (§10 R-7).
- **The legion and world-continuity lanes are in this table now** (rows `0e`, `L2`–`L10` and `0f`, `WC2`–`WC8`).
  Before the reconciliation, `standing-orders`, `escort-stance`, `field-battle-kinds`, `legion-power`,
  `hibernation-clock`, `coarse-step`, `idle-world`, `background-yield`, `world-fall` and `away-digest` had no
  row at all, and five `fleet` tasks plus four `rift-trade` and `trade-ai` tasks were being sequenced against
  modules with no position in the family order (§10 R-13, R-14).

---

## 3. The eight backwards edges (M1) and how this order resolves each

The umbrella's *"Arrows never point back up"* was false in eight places
([audit-2026-09-20-global.md](audit-2026-09-20-global.md) M1). Each is resolved by a **registration seam
owned by the earlier module**, so the wave order above holds with no cycle.

| # | Edge | Resolution | Lands at |
|---|---|---|---|
| 1 | `fleet` `crew` → `exchange` `exchange-hub`, `rift-trade` `crossing-anchor` (their working predicates, to write `crew.idle`) — also a cycle both ways | `crew` owns an `IWorkingSite` predicate **registry**; a site kind registers its own predicate. `crew` ships with the caravan-building predicate only; `exchange-hub` and `crossing-anchor` register theirs in their own waves | `crew` row 13; consumers rows 18 and 20 |
| 2 | `counterparties` `clan-seeding` → `exchange` `exchange-hub` (the trade row's kind and tier-1 variant) | Avoidable and avoided: the row is `empire-seed`'s (`trade-structure-rows`, row 0c) and the tier is `sector-features`'. `clan-seeding` names no exchange module | row 16, after 0c |
| 3 | `counterparties` `relation-facts` → `exchange` `settlement-payment` (settlement deltas) — cycle | `relation-facts` projects from the `stock-deltas` **kinds** that `settlement-payment` registers; it lands with an empty registration set and names no exchange module | row 16; exchange registers at row 18 |
| 4 | `counterparties` `diplomatic-stance` → `exchange` `trade-access` (passage rule) | Relabelled: `trade-access` **registers into** the stance's passage seam (`spec-trade-access.md` already says so). Not a dependency | row 16 |
| 5 | `fleet` `trade-route-order` → `exchange`, `rift-trade` ("later") | `trade-route-order` exposes the standing-order kind; the later programs consume it. No upward edge | row 13 |
| 6 | `world-continuity` `advance-carry` ↔ `rift-trade` `crossing-anchor` (republish call) — cycle | `advance-carry` exposes a **post-move hook**; `crossing-anchor` registers into it. Round 6 S2 also removes the goods half: trade goods cross only by rift route, so an advance republishes anchors and carries no trade goods | hook with `advance-carry`; registration at row 20 |
| 7 | `legion-build` `legion-equipment`, `legion-standards`, **`legion-doctrine`** → `sector-yield` | **Real**, and the umbrella's §1 row 10 (*"1; empire-seed"*) is corrected to name `sector-yield` too. Those legion-build modules land after row 1 (located stock) and after row 11 for the equipment stock itself. **`legion-doctrine` is the third** (added 2026-09-20, §10 R-12): round 6 CQ2 gave a held doctrine a **per-turn goods upkeep** paid from located stock inside `Step` — `perUnit × Σ Count`, a rate proportional to the army — so it depends on row 1 exactly as the other two do | rows 1 and 11; `legion-doctrine` lands in wave L6, after row 1 |
| 8 | `trade-surface` modules → `exchange`, `fleet`, `counterparties`, `trade-ai` | By design (*"grows with 4–7"*). The per-module order is: **a surface module lands in or after the wave whose flag it displays**, and reads only | row 24 |

**Small cycles inside one sub-program**, each resolved by the wave order rather than a seam:
`relation-facts` ↔ `conquest-consequences` (rows 16 then 17 — the later module reads the earlier one's
emitter). The remaining five (`goods-valuation` ↔ `tradeable-goods`, `escort-stance` ↔
`field-battle-kinds`, `trade-wire` ↔ `trade-unlock`, `seasonal-demand-shocks` ↔ `trade-fact-kinds`,
`trade-failure-branches` ↔ `trade-storylet-supply`) are in other sessions' clusters and need the same
one-line landing note there.

---

## 4. Shared files — landing order, and the one-appender rule

Module counts are the audit's lower bounds (M4). The rule that matters is the last column.

| File | Modules that name it | Landing order in this family | Rule |
|---|---|---|---|
| `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` | 18 | `RulesetVersion` moves once per wave, in the row order of §2; the phase slot is created once by `banking-fact` (row 4, CM4) and extended by `logistics-phase` (row 5) | **One wave at a time.** A lane that bumps rebases onto the latest constant and takes the next integer (R4) |
| `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs` | 11 | After the `sector-ironwork` loop (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:123-129`): **1** `world-stamp`'s stamp row, **2** `located-stock` (row 1), **3** `logistics-canonical` (row 5), **4** `carried-goods` (row 12), then any later conditional row in §2 order | **Only one module at a time appends hashed rows.** Each spec states its slot as *"after the last conditional row present at landing"*, never an absolute position, and the wave order above is what makes that unambiguous (M3). **Sparse-row clause (added 2026-09-20, §10 R-11):** the four named modules are not the only appenders. `sector-features`' `slot-tier` row (0d, a **slot** row after `slot-depletion`, outside the sector-row sequence), `banking-fact`'s `sector-bank-hold` (row 8), `diplomacy-facts` and `empire-treasury` (row 15), `crossing-anchor` (row 20), `exchange-hub`'s consignments (18b), `order-book`'s `TradeOrders` (18c), `trade-intel`'s `intel-quote`/`intel-flow` (19a), `trade-unlock`'s milestone set (24b), `world-victory`'s `Outcome` (WC3), `standing-orders`' `order` row, `legion-traditions`' `history`, `legion-standards`' `standard` and `legion-equipment`'s `gear` row all append one, each **after the last conditional row present at landing**. **A sparse row that emits nothing for a world without the wave's flag moves no existing hash and owes no re-bless** — which is why most of them are absent from §6 |
| `gk-core/src/FusionRpg.Core/World/WorldState.cs` | 17 | Field additions follow §2: `Stamp` (0a), located stock (row 1), logistics packets (row 5), carried goods (row 12), diplomacy facts + treasury (row 15) | Additive record fields only; a field that enters the hash enters it through the `WorldCanonical` order above |
| `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs` | 8 | The system-command path lands once (`system-commands`, 0a) with the closed set `release-warden`, `rift-window`, `rift-arrive` (X11); player verbs land with their waves — `set-order`/`clear-order` at L2, `war-declare`/`peace-offer`/`peace-accept` at row 16, `route-set`/`route-clear`/`bank-hold` and `widen`/`ward` at row 7, `order-set` plus the eight treaty, embargo and bloc kinds at 18c, `forge-standard`/`assign-standard` at L6, `depart`/`advance` at WC5, rift route verbs at row 20 | **Each command kind belongs to exactly one wave, and its `WorldCommandAdmission` arm lands in the same change as the kind. A wave may land several kinds.** (Reworded 2026-09-20, §10 R-10: the old *"one kind per wave"* was contradicted by this file's own row 7, which lands five verbs, and by `advance-carry` needing `depart` and `advance` together.) Within a wave, sequence the appends so one task edits the file at a time |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` | 15 | Ledger tables first (0a `world-stock-ledger`, 0f `material-ledger`), then per-wave packed rows in §2 order | Additive columns through `EnsureColumn`; a turn-log write never changes an existing column's meaning |

Also shared, and **not this family's to edit**: `BuildResolver.cs`, `WorldValidation.cs` and
`SlotTypeCatalog.cs` are world-map's. Their changes are asks X-11 and X-14 (§7), and `member-stack`'s
four member-row rules in `WorldValidation.cs` are a **fourth** — filed as an extension of X-11 with a
stated default (§7, §10 R-20). `CreateWorld` is touched by `world-stamp` (0a), `world-state-vocabulary`
(0f) and `world-creation` (WC5) — in that order, which is the §2 order.

`gk-core/scripts/verification-boundaries.v1.json` **is** this family's to edit, in the task that first needs the
path (§7 X-18, §10 R-17). One owner row per path, from one task: a second overlapping row at the same
specificity makes `verify-change.ps1` throw `VERIFICATION BOUNDARY AMBIGUOUS`.

---

## 5. One creator per tuning file

`gk-core/tools/tuning/publish.py` can only bump a file that exists, so the **first** module to need a domain
authors `v1` and every later module publishes `v{n+1}` with its own keys. Rows for other programs are
named here for the family order; their owners confirm in their own change.

| File | Creator (authors `v1` and the loader) | How the others add keys |
|---|---|---|
| `data/tuning/trade.v1.json` | `trade-foundation` `economy-report` (row 0a — the earliest wave with keys: the report's P6 health ceilings) | `warehouse-axis`, `structure-upkeep`, `banking-fact`, the lane and difficulty keys, all as `v{n+1}`. The ~15 specs still writing *"`trade.v1.json` (new)"* mean "the `trade` domain"; only row 0a creates it |
| `data/tuning/diplomacy.v1.json` (the file does not exist yet) | **`counterparties` `diplomacy-facts` (row 15)** — corrected 2026-09-20 (§10 R-3). It needs `diplomacy.offerTtlTurns` at row 15; `exchange`'s `treaty-vocabulary` and `treaty-lifecycle` are both row 18c, and §5's own rule gives `v1` to the **first** module that needs the domain | `relation-facts` (row 16), then every `exchange` module (`treaty-vocabulary`'s `treaty.{kind}.lowestBand` and `access.bandGrant.Clan.*`, `trade-access`'s tariff bands, `treaty-lifecycle`'s minimum term and truce turns) and `trade-ai` `deal-valuation`'s `acceptMilli`, all as `v{n+1}` (exchange EC14 already states the shape) |
| `gk-core/data/tuning/ai.v3.json` | **`trade-ai` `ai-spend-limit` (row 19a)**, which carries the loader switch (`gk-core/src/FusionRpg.Server/Program.cs:234`) — corrected 2026-09-20 (§10 R-4). Its own spec `:188-191` and `trade-ai-map.md:387-390`/`:614` all say so, and `deal-valuation` had already withdrawn its claim; **this file's line was the stale one** | `deal-valuation`, `counter-offer-articles`, `ai-bidding`, `ai-treaty-policy`, `ai-logistics`, `ai-trade-buildings`, `interdiction` publish `v{n+1}` and claim **no** loader switch (M8). Inside wave 19a the landing order is therefore `trade-intel` → `ai-spend-limit` → `deal-valuation` |
| `data/tuning/legion.v1.json` (the file does not exist yet) | `legion-build` `legion-cohesion`, code half (wave L4) — *"created here (shared with modules 11–15)"* | `legion-traditions`, `legion-count-cost`, `field-battle-kinds`, `legion-standards`, `legion-doctrine`, `legion-equipment` and both publish halves (L8, L9) as `v{n+1}` |
| `data/tuning/legion-seed.v1.json` (the file does not exist yet) | `empire-seed` `legion-bands` (wave ES5) — round 4 Q12: seed magnitudes here, mechanics in the `legion` domain file, one shared legion vocabulary registry both read | later seed bands as `v{n+1}`. `publish.py` cannot create a first version of a new domain (`gk-core/tools/tuning/publish.py:60-68`), so ES5 extends the tool rather than hand-writing the file |
| `data/tuning/world-continuity.v1.json` (the file does not exist yet) | `world-continuity` `hibernation-clock` (wave WC2) — `catchUpCapTurns`, the earliest keyed module in that lane | `world-victory`, `coarse-step`, `world-warden`, `idle-world`, `world-creation`, `advance-carry`, `background-yield`, `world-event-budget` and the difficulty-profile knobs m12 moves here, as `v{n+1}`. Same `publish.py` first-version extension as above |
| `data/tuning/world-difficulty-catalog.v1.json` (the file does not exist yet) | `world-continuity` `world-difficulty-profile` (wave WC6) — ids and display names only; the numbers live under `difficulty.profiles.{id}` in the `world-continuity` domain (tunables-ssot T7/T8, A-WC9/m12) | — |
| `data/tuning/trade-catalog.v1.json` (the file does not exist yet) | **`trade-surface` `trade-lexicon` (sub-wave 24a)** — added 2026-09-20 (§10 R-18). It is a **runtime word catalog**, never the `trade.v1.json` number file ([trade-surface/spec-trade-lexicon.md](trade-surface/spec-trade-lexicon.md):60) | each later `trade-surface` sub-wave publishes `v{n+1}` as its family of tokens lands |
| `data/tuning/structure-seed.v{n+1}.json` (the file exists) | `empire-seed` `structure-bands` (wave 0b) publishes the next version and owns the **consumer-added anchor fields** table (field, shape, band table, consumer module, landing order) (M7) | `warehouseBand`, `locatedYields`/`yieldBand`, the clearing ordinal, depot and anchor magnitudes each land as `v{n+1}` **in their consumer's wave**, in §2 order; the corpus regenerates once per publish |

**Files this family publishes into but does not own.** `data/tuning/siege.v{n+1}.json` (the siege domain's —
`construction-chain` publishes the refine rate at row 7), `data/tuning/notification-catalog.v{n+1}.json`
(notification-ssot's — `trade-notify` at 24c) and `data/tuning/narrative.v{n+1}.json`
(npc-story-events' — `trade-story-pacing` at 25c). The last has **no `v1` anywhere yet**, and
`gk-core/tools/tuning/publish.py` can only bump a file that exists, so it is filed as an ask in §7 (§10 R-18).

Every file this family creates needs a verification-boundary owner row in the same change (M6, ask X-18,
which is **our own work** — §7, §10 R-17).

---

## 6. Golden re-bless points

Two facts make this list short, and both are load-bearing.

1. **A capability gate means no existing golden moves.** Every wave in §2 runs only on a stamp that grants
   its flag, and `GrantedBy` is empty for legacy and unstamped worlds, so the canonical projection is
   byte-identical for every world created before the wave (`spec-world-stamp.md` §3: *"no hash moves until
   the first capability ships"*). Specs assert that, and none is re-blessed to pass
   ([sector-yield/spec-banking-fact.md](sector-yield/spec-banking-fact.md) acceptance 1;
   [logistics-flow/spec-logistics-phase.md](logistics-flow/spec-logistics-phase.md) acceptance 1).
2. **A bump does cost one thing, every time.** A trimmed turn report logged under an older ruleset is no
   longer re-derived (`spec-world-stamp.md` §2 and §8). That is a refusal, not a re-bless — 20 times in
   §2, once per bump.

| Re-bless point | Wave | Why it moves |
|---|---|---|
| Fixtures and Data tests that build a world **at the live `RulesetVersion`** and then grant a flag | every flagged row in §2 | The stamp's granted-capability line enters the canonical text for those worlds. Owned by the wave, re-blessed in the wave's own change, never batched with another wave's |
| The template-created world goldens for the A1 start kit | 0b/0c + `world-continuity` `world-creation` | The seat gains a tier-1 Counting House and a tier-1 Storehouse (round 5 A1), which changes the slot rows of every shipped template. **One shared re-bless** with `counterparties` `empire-roster` and `clan-seeding` ([counterparties/spec-empire-roster.md](counterparties/spec-empire-roster.md) §Goldens) |
| The regenerated structure corpus (`gk-data/packs/fusion/data/seed/structures/**`) and its `--check` gate | 0b, 0c and every `structure-seed.v{n+1}` publish in §5 | Generated tree, committed; CI fails on drift. Regenerate in the publishing wave, never by hand (hard rule) |
| `WorldCanonical` append-order goldens | rows 1, 5, 12 | Each appends one conditional row at the slot §4 fixes; the second module to land rebases onto the first |
| The world goldens the warden retirement moves | WC4 | `world-warden` removes a shipped freeze, so the worlds that had one move once, in that wave's own change |
| Every world golden with a battle | L4 | `legion-traditions`: a legion that fights accumulates hashed history, so this is a **large** re-bless — one explained movement, in that commit |
| The siege goldens the cohesion band publish moves, and the loam goldens the count-cost curve publish moves | L8, L9 | A publish that makes an inert term real is behaviour; each re-blesses in its own publishing commit |
| The siege goldens for general world members | L3 | `general-member-hub`, ordered **after** `species-progression`'s own re-bless so no value moves twice |
| The turn goldens wherever a refused field fight becomes a real one | L5 | `field-battle-kinds` wires the join predicate L4 left inert |

**This table is not a closed list of `WorldCanonical` appenders** (clarified 2026-09-20, §10 R-11). Many more
modules append a **sparse** conditional row — §4's sparse-row clause names them — and a sparse row that emits
nothing for a world without the wave's flag **moves no existing hash and owes no re-bless**, which is exactly
why it is not here. This table lists the rows that *do* move hash text.

No other re-bless is owed by this family. A golden movement that is *not* in this table is a defect to
diagnose, not a re-bless (the specs say so individually).

---

## 7. Cross-program blockers — who must land first

| Blocker | Ask | Blocks | Must land before |
|---|---|---|---|
| **Save identity re-key** — `save-identity` SE4.12 → SE4.38 (unchecked, `tasks/solid-enforcement-todo.md:634`) | X-1 | `material-ledger` (row 0g) and therefore the **banking step** (row 8) and everything downstream of banking: `empire-treasury`'s **credits only** (row 15 — narrowed 2026-09-20, §10 R-8: the module lands with the wave and reads zero), `income-parity`'s credit (row 10), `exchange` settlement at bank points, both `legion.bankedDraw` arms (L10). It does **not** block the phase slot (row 4), the lane layer (rows 5–7), row 9, or the rest of row 15 | Row 8. **Round 6 C3 is "wait"** — see the interim behaviour below |
| **Power-ladder rows** — consumer-authored §10 rows for lane throughput, warehouse capacity, clearing capacity and located-good scale | X-4 | Rows 1 (warehouse capacity) and 6 (lane throughput): PS-5 requires faucet and sink read the same scale | Rows 1 and 6 |
| **Power-ladder contest row** — Θ for two rolled-up legion powers | X-2 | **Row 23 (`trade.laneLossPower`) and `world-continuity` `world-warden`'s defence term — those two only** (narrowed 2026-09-20, §10 R-9). Until it lands the warden defence term is **0** and escort strength stays the v1 stance count (round 4 §P). It does **not** block `deal-valuation` (19a) or `ai-trade-buildings` (19d): both read the roll-up **to choose**, never as a contest term, and both state a default (today's stack count), so X-2 gates a quality improvement in row 19, not its landing | Row 23 and WC4's defence term |
| **Multi-slot `BuildResolver`** — accept a slot whose kind is in `RequiredSlotKinds` (B1, E-A23), plus the `build`-on-own-slot upgrade arm (X8) at `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:84` and `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:411` | X-11 | `sector-features` §4's upgrade verb; Trading Post on Wildland **or** Market (B1); Rift Anchor on Wildland (B2); `depot` and `crossing-anchor` placement; `empire-goods-sinks`' cost arm (row 17); `ai-trade-buildings`' upgrade candidates (19d) | Rows 0c, 0d, 1, 12, 20 — world-map lands the two arms first |
| **`WorldValidation.cs` member-row rules** — `member-stack`'s four rules on a stack member row (`spec-member-stack.md` §Structure) touch a file §4 fences as world-map's | X-11 (extension, filed 2026-09-20 — §10 R-20) | `member-stack`'s validation half only | **Default: `member-stack` ships without that edit** if world-map has not landed its arms, with the four rules asserted in the module's own tests and the validation arm following when world-map lands it. Whether §4's fence means only the X-11/X-14 changes or every edit to that file is **not decided here** |
| **Verification boundaries** — `verify-change.ps1` throws *"VERIFICATION BOUNDARY MISSING"* for an unmapped path (`scripts/verify-change.ps1:118`) | X-18 — **not an ask any more: this family's own work** (settled 2026-09-20, §10 R-17) | The proven-unmapped paths: `gk-core/data/tuning/**` (every domain §5 publishes), `gk-data/packs/fusion/data/seed/structures/**`, `data/seed/diplomacy/**`, `data/seed/legion/**`, `gk-forge/tools/seedsmith/**`, `gk-core/tests/FusionRpg.Bench/**`, the whole `gk-web/web/fusion-rpg-web/**` tree, `scripts/guard-*.ps1` (`guard-dal.py` included), and the new `gk-core/src/FusionRpg.Core/World/{Trade,Diplomacy,Facts,Logistics,Logistics/Rift}/**` directories, which resolve only to `core-fallback` | **Each path is added by the first task that touches it**, in that task's own change. `empire-seed-map.md:709`'s prohibition on this family editing `gk-core/scripts/verification-boundaries.v1.json` is **overruled for that file only**; `test-verification-boundary` still owns the tool and the registry's schema. One owner row per path from one task — a second overlapping row at the same specificity throws `VERIFICATION BOUNDARY AMBIGUOUS` |
| **`gk-core/data/tuning/narrative.v1.json` does not exist** — `trade-stories` `trade-story-pacing` (25c) publishes trade rows into it, and `gk-core/tools/tuning/publish.py` can only bump a file that exists | ask to **`npc-story-events`** (filed 2026-09-20, §10 R-18) | 25c's pacing rows | Before 25c. **Default:** if that program has not authored `v1` by then, `trade-story-pacing` lands its rate-limit *rows as a proposal in its spec* and its selection tests against npc's engine, and publishes when the file exists. Nothing under `docs/architecture/npc-story-events/**` or `docs/architecture/narrative-seed/**` is edited by this family |
| **Fusion essence cost scales by level** (`EssenceCount` widens to `long`) | X-5 | `essence-loop-read`, and therefore row 1 as a whole — the spec will not ship one half of the PS-5 loop | Row 1 |
| **`world-transit`** (round 6 W2) and **`world-derived`** (round 6 D2) | named future programs; no spec here implements either | The six `world.*` channels and rift-gate import/export. Specs consume them **behind a stated default** | — |

### Interim behaviour while save identity is unfinished (round 6 C3)

Round 6 C3 decides **wait**: `material-ledger` and the banking work that needs it start after the
save-identity re-key finishes. Until then, and stated in each affected spec:

- Rows 1–7 and 9 land normally, and so do rows 10–17 except the paths named in the X-1 row above (§10 R-8):
  located goods accumulate in sector warehouses, `production-halt` caps
  production at warehouse capacity, structures pay their loam term and yield goods, the `Logistics` phase
  exists with its L3 slot **empty**, and the lane layer moves goods toward the nearest bank point.
- **Nothing leaves the map.** No banking fact is written, no wallet or treasury is credited, and the
  economy report prints a banked total of **zero with that reason** — not a silent zero.
  `bank-points` still answers *which sectors are bank points* (a pure query, row 1), so the
  first-throttle answer — *build a Counting House* — is buildable, visible in `forecast-facts`, and does
  raise the banking tier that row 8 will read.
- The interim is therefore a **full warehouse economy with no outflow**: the player sees production halt
  at capacity and can widen storage and lanes, which is exactly the throttle the ideal wants, minus the
  reward. That is a playable but incomplete state, and no spec may describe the family as shippable
  before row 8 lands.
- Row 8 lands `material-ledger` (row 0g) first, then the banking step, then re-points nothing: the four
  writer sites are written once, against the re-keyed store. Option (b) of the audit's Q3 (land on the
  Tier B `player_id` key and re-point later, editing the writer sites twice) is **not** taken — round 6
  C3 says wait.

---

## 8. What this file does not decide

- Anything `world-transit` or `world-derived` owns (round 6 W2, D2). Every consumer here reads them behind a
  stated default.
- Whether §4's `WorldValidation.cs` fence means only the X-11/X-14 changes or every edit to that file. §7
  files `member-stack`'s member-row rules as an X-11 extension with a default, and leaves the fence to
  world-map (§10 R-20).
- Who authors `gk-core/data/tuning/narrative.v1.json` (a file that does not exist yet anywhere in the repo). That is
  npc-story-events' file and this family may not edit
  that program's documents; §7 files the ask with a default (§10 R-18).
- The multiverse map's drawing (WC8), which `/idea-ui` owns, and every per-row click budget, which
  `spec-trade-click-budget.md` keeps.

**No longer open.** The internal wave splits and flag ids of all seven sub-programs are in §2; the M2
legion bump contradiction is closed (§10 R-13); the creators of `ai.v3.json` and
of `diplomacy.v1.json` (which does not exist yet) are fixed (R-3, R-4); rows 19 and 25 are no longer
bump-free (R-6, R-7); and X-18 is this family's own work (R-17).

## 9. DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine, canonical hash, world store and turn log, structures corpus, tunables,
    power scale, verification boundary.
[x] Read this session: decisions-round-4.md (whole, incl. Round 6), audit-2026-09-20-global.md (whole),
    trade-network-map.md (whole), the six sub-program maps this session owns, spec-world-stamp.md §1-§5
    and its exposed/capability tables, spec-sector-features.md §1-§5 and its Boundaries, the wave tables
    of logistics-flow, fleet, rift-trade and counterparties, sector-yield's build order.
[x] Code verified, not inferred: TurnEngine.cs:125 (RulesetVersion 13), WorldCanonical.cs:123-129 (the
    sector-ironwork loop and the append point), StructureCatalog.cs:38/:43/:51 (the Obstacle precedent and
    the required Kind), WorldState.cs:105/:158 (slot and sector OwnerFactionId, for S1),
    verify-change.ps1:118.
[x] Every factual claim cites file:line or a spec section.
[x] audit-doc-citations.py --scope run on this file, and again after the 2026-09-20 reconciliation
    (§10): 39 resolvable citations, 0 HIGH. The two unresolved D1 findings are files that do not exist
    yet and say so on their own line.
[x] No assertion pins a population count: §2's row count is a landing order, not a test constant.
[x] No new cap, no private power curve, no second composer, no magic number: this file sets no number
    except bump ordinals, which are order, not balance.
[x] No SOLID-violating path: §3's eight resolutions are registration seams owned by the earlier module.
[~] Session boundary: this session was fenced to the six sub-programs it owns plus this new file; the
    rows for other programs are recorded, not edited.
[x] Reconciliation 2026-09-20 (§10): the seven planning fragments read against every spec and map they
    cover; twenty rulings applied here and in the nine documents §10 R-19, R-6, R-7, R-13, R-16 and R-17
    name. Nothing under docs/architecture/npc-story-events/** or narrative-seed/** was touched — the two
    items that needed it are filed as asks in §7.
```

---

## 10. Reconciliation 2026-09-20 (the seven planning fragments)

The family build todo ([../../../tasks/trade-network-todo.md](../../../tasks/trade-network-todo.md), 162
tasks) was assembled from seven planning fragments, one per cluster group. Each fragment read its own specs
and maps against this file and reported where they disagreed. Twenty of those disagreements were decided
here; the table records each ruling, what it changed, and why. **§2 remains the single source of wave
order** — every ruling below either edits §2 or edits a rule §2 applies.

| # | Ruling | What it changed | Why |
|---|---|---|---|
| **R-1** | Phase-0 rows are renumbered: `sector-features` moves out of row 0a into its own **row 0d**, after the widening (0b) and the feature rows (0c). Legion W1 becomes 0e, world-continuity W1 becomes 0f, `material-ledger` becomes 0g | §2 rows 0a–0g; every cross-reference in the todo (`0a.10` → `0d.1`, legion `0d.*` → `0e.*`, continuity `0e.*` → `0f.*`, `0f.1` → `0g.1`) | `sector-features` lands `StructureDef.FeatureUnlock` and `StructureKind.Feature`, but the anchor-schema widening that adds those fields is row 0b (`empire-seed`, audit M5) and the feature rows themselves are 0c. As written, `sector-features` would have landed its C# members against a schema that had neither field |
| **R-1b** | Row 0d takes the family's **first capability flag and first bump**: `trade.sectorFeatures`, ordinal **N+1**. The whole ordinal column shifts by one — `trade.sectorYield` becomes N+2, and so on to `trade.demandShock` at N+25 | §1 R7 (new), §2's bump column end to end | `spec-sector-features.md:152-160` turns `build` on a structure's own slot into an **upgrade** instead of a `build.occupied` refusal. That changes how an existing world's stored order resolves — precisely what R1 exists to prevent — so it cannot ship unflagged in an unbumped wave. No shipped template places a structure, so no golden moves today; that is luck, not a licence |
| **R-2** | Row 0b gains `world-name-index` and `corpus-metrics` | §2 row 0b's module list | `spec-trade-structure-rows.md:5` names `world-name-index` as a dependency and its acceptance 8 asserts name uniqueness *through* that index, while its "done means" needs `corpus-metrics`' `bands_resolve`. Neither was in the row. Both take no flag and no bump, so the cost is ordering only |
| **R-3** | `data/tuning/diplomacy.v1.json` does not exist yet, and its creator is **`counterparties` `diplomacy-facts` (row 15)**, not any exchange module | §5's diplomacy row; exchange tasks 18a.3 (`treaty-vocabulary`) and 18c.3 (`treaty-lifecycle`) now publish `v{n+1}` | §5's own rule is that the **first** module to need a domain authors `v1` and its loader. `diplomacy-facts` needs `diplomacy.offerTtlTurns` at row 15; `treaty-vocabulary` and `treaty-lifecycle` are both row 18c |
| **R-4** | `gk-core/data/tuning/ai.v3.json`'s creator is **`trade-ai` `ai-spend-limit`**, which carries the loader switch — not `deal-valuation` | §5's `ai.v3` row; inside wave 19a the landing order becomes `trade-intel` → `ai-spend-limit` → `deal-valuation` | `spec-ai-spend-limit.md:188-191` and `trade-ai-map.md:387-390`/`:614` both claim the switch, and `deal-valuation` had already withdrawn its claim. `landing-order.md:180` was the stale line, so it is fixed **here** rather than in four other documents |
| **R-5** | `exchange` gets a third flag, **`trade.exchangeOrders`**, at sub-wave 18c, sharing 18c's single bump with `trade.diplomacy`. 18b and 18c are **not** merged | §2 rows 18a–18d; `spec-exchange-hub.md:249` and `spec-order-book.md:53`/`:299` corrected | `spec-exchange-hub.md:249` and `spec-order-book.md:53` gated `order-set` on wave 2's flag while the map puts `order-book` in wave 3. A world stamped between them would gain rules mid-life — the R1 breach. Merging the two waves would have closed it too, and was rejected: it would put hub, orders, settlement and treaties in one landing |
| **R-6** | Row 19 (`trade-ai`) is **not** bump-free: 19a registers `trade.intel` and takes one bump | §2 row 19a (was *"none expected"*); `trade-ai-map.md:606` corrected | `spec-trade-intel.md` hashes AI belief inside `Step` and adds two `WorldCanonical` row kinds (`intel-quote`, `intel-flow`). A world stamped at 18b that then reached 19a would start emitting canonical rows it had not emitted before |
| **R-7** | Row 25 (`trade-stories`) takes one flag, **`trade.demandShock`**, registered by `seasonal-demand-shocks` at 25c | §2 row 25c; `trade-stories-map.md:681` corrected | The shock is a term in the demand function `exchange` reads, so it moves prices on a live world. R1 forbids widening row 15's `counterparties.needs` to cover it. Every other trade-stories sub-wave registers nothing, for the reason the map always gave: a story fact rides its **producer's** flag |
| **R-8** | Row 15's save-identity blocker narrows to `empire-treasury`'s **credits** | §7's X-1 row; §2 row 15; the §7 interim list | The old wording put all of wave 15 behind row 8, which would have held `need-vector`, `empire-roster`, `diplomacy-facts` and the difficulty knobs behind a re-key none of them touches. `spec-empire-treasury.md` §7 already says the module lands and reads zero |
| **R-9** | Ask X-2 blocks **only** row 23 and `world-warden`'s defence term | §7's X-2 row | `deal-valuation` and `ai-trade-buildings` read the roll-up **to choose**, never as a contest term, and both state a default (today's stack count). Listing them made the row read as a hard stop on row 19 |
| **R-10** | §4's `WorldCommand.cs` rule is reworded: **each command kind belongs to exactly one wave, and its `WorldCommandAdmission` arm lands in the same change as the kind. A wave may land several kinds** | §4's `WorldCommand.cs` row | *"One kind per wave"* was contradicted by this file's own row 7 (five verbs) and by `advance-carry`, which needs `depart` and `advance` together. Read literally it would have forced 18c to split into nine landings |
| **R-11** | §4's `WorldCanonical.cs` rule gains a **sparse-row clause**, and §6 says it is not a closed list of appenders | §4's `WorldCanonical.cs` row; §6's closing clause | Many more modules than the four named append a sparse conditional row — `sector-features`' slot tier, `banking-fact`'s sector bank-hold, `diplomacy-facts`, `empire-treasury`, `crossing-anchor`, `trade-unlock`'s milestone set and the rest. They all follow the existing *"after the last conditional row present at landing"* rule, and **a sparse row that emits nothing for a world without the wave's flag moves no existing hash and owes no re-bless** — which is why they were not in §6 and why §6 read misleadingly as closed |
| **R-12** | §3 edge 7 gains a third module: **`legion-doctrine`** | §3 edge 7 | Round 6 CQ2's per-turn doctrine goods upkeep is paid from `sector-yield` located stock inside `Step`, so `legion-doctrine` depends on row 1 exactly as `legion-equipment` and `legion-standards` do. It lands in wave L6, after row 1 |
| **R-13** | Legion-build's flag-and-bump answer is accepted and **audit M2 is closed**. Wave 0e takes one flag (`legion.rolePlacement`, registered by `role-aware-placement`) and one bump; `member-stack` rides it and registers nothing. **Every legion sub-wave is now a row in §2** | §2 rows 0e, L2–L10; §8; `legion-build-map.md` §14 gains the same record | §13 A-LB6 was right about the **module** (`member-stack` grants nothing at landing: `count=`/`id=` are default-suppressed and the only producer of `Count > 1` is a wave later) and §4 was right about the **rule** (a feature-granting module rides its wave's bump). They only looked contradictory because C1's question was being asked per module; it is asked **per wave**. Registering `legion.stacks` at 0e would gate behaviour arriving at L2 — the flag-spans-waves breach R1 forbids. And `role-aware-placement` makes a template bearer at `WorldTemplateCatalog.cs:196` stop fighting, so the wave is not an R3 wave. The rows matter beyond legion-build: three fragments could not sequence against `standing-orders`, `escort-stance`, `field-battle-kinds` or `legion-power`, because those had no place in the family order |
| **R-14** | World-continuity's four flags are accepted: `continuity.worldOutcome` (WC3), `continuity.warden` (WC4), `continuity.advance` (WC5), `continuity.backgroundEconomy` (WC6). Rows 0f, WC2, WC7 and WC8 take neither. **Every continuity sub-wave is now a row in §2** | §2 rows 0f, WC2–WC8 | Same reason as R-13: two fragments could not sequence against `hibernation-clock`, `coarse-step`, `idle-world`, `background-yield`, `world-fall` or `away-digest`, all hard prerequisites of rift-trade rows 21 and 22, and none of them had a row |
| **R-15** | **Every `empire-seed` wave takes no flag and no bump** (R3: seed content, tuning bands, a load-time reader, pure queries, report text, schema columns). Its sub-waves are rows in §2 | §2 rows 0b, 0c, ES2–ES6 | Nothing in the cluster is read by `Step` or by the canonical projection. The flag and bump that make its rows *buildable* belong to row 0d, `sector-features` |
| **R-16** | `trade-surface` registers **no stamp capability anywhere**, and `trade-unlock` must say why its hashed milestone set is safe | §2 rows 24a–24e; `spec-trade-unlock.md` §Design 1 and Hard edges rewritten | `spec-trade-unlock.md:67-74` and `:256` added a hashed milestone set to `WorldState` and called themselves stamp-gated, while row 24 grants no flag to gate on. The resolution: milestones derive from the **producers'** flags, so a world with none has an empty set, **an empty milestone set emits no canonical row**, and the row takes its §4 slot under R-11's sparse-row clause |
| **R-17** | Adding rows to `gk-core/scripts/verification-boundaries.v1.json` is **this family's own work**, in the task that first needs the path. `empire-seed-map.md:709`'s prohibition is overruled for that file only | §4's shared-file note; §7's X-18 row; `empire-seed-map.md` §3's row annotated | `AGENTS.md` is explicit that an unmapped production path is a verification-boundary defect to add or repair, never something to compensate for by widening the suite — and §7 blocked row 0b on exactly these rows, so the prohibition and the blocker could not both stand. The paths the fragments proved unmapped are listed in §7's X-18 row; each is assigned to the first task that touches it, and a second overlapping row later throws `VERIFICATION BOUNDARY AMBIGUOUS` |
| **R-18** | §5 gains two creators, and one becomes an ask: `data/tuning/trade-catalog.v1.json` does not exist yet and is created by `trade-surface` `trade-lexicon` (24a); `gk-core/data/tuning/narrative.v1.json` does not exist anywhere and belongs to `npc-story-events` and is **filed as an ask in §7** | §5's table; §7's new ask row | `spec-trade-lexicon.md:60` creates a new file that appeared in no §5 row. `narrative.v1.json` has no `v1` anywhere, and `gk-core/tools/tuning/publish.py` can only bump a file that exists, so `trade-story-pacing` would have published into nothing. Nothing under `docs/architecture/npc-story-events/**` or `docs/architecture/narrative-seed/**` is edited by this family |
| **R-19** | Six stale lines fixed in their own documents | `logistics-flow-map.md:128` and its counter/fingerprint paragraph (the hashed graph-version counter and T1–T10 are withdrawn; `spec-path-cache.md:241-242` has an unhashed topology key and T1–T12, and `spec-logistics-canonical.md:189-190` asserts no counter is hashed) · `spec-sector-features.md:393-394` (checklist said eight members, body says nine since round 6 L6) · `spec-economy-report.md:99-101`, `spec-warehouse-axis.md:151-154`, `spec-structure-upkeep.md:103-105` (all three read as an open race for `data/tuning/trade.v1.json`; §5 gives it to `economy-report`, row 0a) · `spec-standing-orders.md` Hard edges (*"no bump and no re-bless"*, although `legion-build-map.md` §14 already listed it as rewritten under C1) · `spec-legion-equipment.md` Structure (omitted the `WorldCanonical.cs` edit its default-suppressed `gear` row needs) · `spec-order-book.md:299` (corrected by R-5) | Each is a document that disagreed with a settled decision. Code beats docs and docs beat comments, but a stale line in a binding spec is the next session's wrong turn |
| **R-20** | `spec-member-stack.md`'s `WorldValidation.cs` edit becomes an **ask**, not a decision: an extension of X-11, with the default that `member-stack` ships without it if world-map has not landed its arms | §7's new X-11 extension row; §8 | §4 fences `WorldValidation.cs` as world-map's (*"not this family's to edit"*), and `spec-member-stack.md` §Structure edits it for four member-row rules. Whether the fence means only the X-11/X-14 changes or every edit to that file is world-map's to say, so it is filed rather than decided |

**What this pass cost, for the DESIGN-GATE §4 record.** Seven fragments, read against their own specs and
maps, found one ordering defect that would have shipped C# members against a schema lacking the fields
(R-1), four R1 breaches that would have let a live world gain rules mid-life (R-1b, R-5, R-6, R-7), two
tuning files whose publishers would have published into a file that did not exist (R-3, R-4, R-18), two
blockers scoped wide enough to stall work that was not blocked (R-8, R-9), two rules that contradicted this
file's own rows (R-10, R-11), ten waves with no place in the family order at all (R-13, R-14, R-15), and six
stale lines. None of it needed new design; all of it needed the documents read against each other once.

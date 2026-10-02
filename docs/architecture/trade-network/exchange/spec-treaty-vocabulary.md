# Spec: `treaty-vocabulary`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 3 of the [exchange map](../exchange-map.md) (wave 1; approved
2026-09-19, including owner decision Q1). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§7.4, §7.7. House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

One closed registry, `treaty-kind.v1`, that names every treaty kind, what it grants, and the lowest
relation band at which it may exist — plus the closed list of **`Access` levels** those grants map
onto, the rule for factions that grant access **without** a treaty (clans, owner decision Q1 as amended
by round 4), the **building tiers** each trade and diplomacy feature needs (round 4, principle B), and
the closed **article kinds** and **deal shape** a treaty proposal may carry (trade-ai ask T-A5).
Everything downstream — `trade-access`, `treaty-lifecycle`, `trade-ai`'s counter walk, the treaty
screen — reads this one registry and never keeps a second list.

**Round 4 (2026-09-19, [decisions-round-4.md](../decisions-round-4.md)) is binding here.** Where this
spec's earlier text disagreed, it has been corrected in place: §3 (clans trade from `wary`, only
`hostile` blocks), §5 (new: building tiers), §6 (new: articles and deal shape).

## Scope and non-goals

In scope: the registry file and its C# reader; the `Access` level enum; the treaty-free grant rule for
clans; the diplomacy tuning keys this module owns.

Not in scope: evaluating `Access` for a pair and turn (`trade-access`); proposing, signing, ending
(`treaty-lifecycle`); the facts themselves (`counterparties` `diplomacy-facts`); how bands move
(`npc-story-events` and `counterparties` `relation-facts`); when an AI signs (`trade-ai`).

## Design

### 1. Treaty kinds — five, closed

| Kind | Scope | Grants | Implies | Lowest band (v1 data) |
|---|---|---|---|---|
| `passage` | bilateral | The grantee's legions and flows may cross the grantor's sectors | — | `wary` |
| `market` | bilateral | Orders at the grantor's hubs; the grantor's lanes join the grantee's route graph | `passage` | `open` |
| `preferential` | bilateral | A tariff below the grantor's default, with the most-favoured clause | `market` | `eager` |
| `bloc` | multilateral | No tariff inside; one shared external tariff and shared embargoes | `preferential` between members | `eager` with every member |
| `embargo` | one-sided act | Stops the target's orders and passage at the actor's ground; voids `market` and `preferential` | — | any band; automatic at war |

The registry file holds names, scope and the grant/implies structure. The lowest band per kind is
data in `diplomacy.v{n}.json`, validated at load against the band registry
(`gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`, four bands `eager, open, wary, hostile`).

### 2. `Access` levels — four, closed and ordered

`closed < passage < market < preferential`. A bloc member reads `preferential` toward other members
(at a zero internal tariff); `embargo` and war read `closed`. The order is used by `trade-access`
("highest level whose conditions hold") and by `order-book` ("`market` or better").

### 3. Grants without a treaty — owner decision Q1, amended by round 4 (2026-09-19)

**Clans trade by relation band alone; no treaty and no embassy are needed.** The band sets the spread
(`price-curve`) and **blocks trade only at `hostile`** (round 4, B and Q1). A `Clan`-kind faction
(`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:12-13`) grants:

| Level | From band | Needs a treaty? | Needs a building (§5) |
|---|---|---|---|
| `passage` | `wary` or better | No | No |
| `market` | `wary` or better (was `open` before round 4) | No | Trade tier ≥ 1 (a Trading Post) |
| `preferential` | `eager` (the kind's lowest band) | **Yes** — a `preferential` treaty | Trade tier ≥ 3 |
| `bloc` membership | `eager` with every member | **Yes** — a `bloc` treaty | to found or join: the actor's Trade tier ≥ 3 and Consulate (`DiplomacyGate`) |

Empires (`Rival` kind and the dominant enemy empire) grant **nothing** without a treaty. The table is
data: `access.bandGrant.{factionKind}.{level}` names the band per faction kind and level; only `Clan`
has rows in v1, and a faction kind with no rows grants nothing without a treaty. War and embargo
override band grants exactly as they override treaties.

**Superseded consequence (was ask E-A9).** Before round 4 a clan at the approved starting band `wary`
granted `passage` but not `market`, so the first clan market waited for a band-raising fact. Round 4
opens clan trade at `wary` behind a building instead: **the first clan market opens when the player
builds a Trading Post** (round 4 Q1). E-A9's band-raising storylet is no longer needed; what replaces
it is a reachability case for "build a Trading Post, then fill a clan order" (`trade-stories`
`trade-trigger-reachability`, `trade-surface` `trade-unlock`).

### 4. Reader

`TreatyKindRegistry` in `src/FusionRpg.Core/World/Diplomacy/` (new): loads the registry through the
host (T8), joins it with the diplomacy tuning, and exposes the kinds, the implies closure, the lowest
band per kind and the band-grant table. An unknown kind, an unknown band, a cycle in `implies`, or a
kind with no lowest band is a load rejection naming it.

### 5. Building tiers — round 4, principle B

*"To unlock a feature in a sector, we should have the correct building"* (owner, round 4 §B). Two of
the register's building kinds gate features this program owns. Each is **one structure row whose tiers
are its `variants`** (never separate rows; empire-seed generates the variants); the tier of a built
slot is `trade-foundation` `sector-features` ([spec](../trade-foundation/spec-sector-features.md))' `WorldSlot.StructureTier`, read through `SectorFeatures.TierOf` / `FactionTier` (it
answered this map's ask E-A14), never stored here.

| Ladder (closed, 4 + 2 tiers) | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---|---|---|---|
| **Trade** (`SectorFeature.trade`; hub behaviour `exchange-hub`) | `trading-post` — clan barter | `market` — empire market orders | `exchange` — preferential treaties and blocs | `grand-exchange` — cross-world routes (`rift-trade`) |
| **Diplomacy** (`SectorFeature.diplomacy`, read by `counterparties` `diplomatic-stance` §9 `DiplomacyGate`; checked by `treaty-lifecycle`) | `embassy` — treaties with an empire | `consulate` — blocs and embargo leverage | — | — |

Tiers are integers (1–4, 1–2); the player-facing names are the structure row's and its variants' display
names (`sector-features` §2), and what each tier unlocks is a `trade-surface` `trade-lexicon` reading line.
The T2 building "Market" is not the `Market` **slot**: **round 5 C4 (owner)** renames the slots' display
names and keeps the building names and every id; the new slot words are `trade-surface` `trade-lexicon`'s
(was exchange-map owner question OQ-2).

**Deal classes and the tier each needs (closed, structural — the register's own table, not a balance
number):**

| Deal class | When it applies | Trade tier needed | Diplomacy tier needed |
|---|---|---|---|
| `clan-barter` | an order at a hub where either the hub owner or the trader is a `Clan` | 1 | — (clans need no embassy) |
| `empire-market` | an order at a hub where neither side is a `Clan` | 2 | — (the `market` treaty behind it needed one to sign) |
| `preferential` | `Access` would be `preferential` (treaty or bloc) | 3 | — |
| `cross-world` | a route between two worlds (`rift-trade`) | 4 (in the anchoring world) | — |
| `treaty-with-empire` | offering any treaty kind to a counterpart that is not a `Clan` | — | 1 — **the offerer's** (`DiplomacyGate.TreatiesTier`; counterparties owner question CQ1, default (a)) |
| `bloc` | founding or joining a bloc; a deliberate `embargo-set` | 3 (bloc only) | 2 — **the actor's** (`DiplomacyGate.BlocsEmbargoTier`) |

**Whose buildings count.** A deal class is available at hub sector *s* between requester *R* and hub
owner *G* only if **both** hold the tier: the **hub** — the highest active Trade tier in *s* — and
the **requester** — the highest active Trade tier *R* holds anywhere in that world
(`Hubs.TradeTier`, `exchange-hub`). That is what makes round 4's *"clan trade at world start opens by
building a Trading Post"* true even though every clan is seeded with a hub. The requester-side reading
("anywhere in the world") is **the owner's decision, round 5 B4** (*"the trader's best Trading Post tier
anywhere in that world"*; was exchange-map OQ-1). **Diplomacy tiers** are `DiplomacyGate.TierOf` (the
highest active `diplomacy`-feature tier the faction holds in that world, read through `sector-features`
`FactionTier` — round 5 X1; no structure kind) and gate **acts** only — offering, founding, joining, embargoing — never an
in-force treaty: losing an Embassy does not void or suspend what was signed (`counterparties` `diplomatic-stance` §9 (`DiplomacyGate`)).

The table lives in the registry file (it is a rule, not a feel number) and is pinned: a new class or a
moved tier is a reviewed change.

### 6. Treaty articles and deal shape (answers trade-ai ask T-A5)

The payload a `treaty-propose` / `treaty-respond` may carry is a **command contract**, so it lives
upstream of both the player and the AI (trade-ai contradiction TC4). Closed lists:

| Article kind (9) | One step, as `counter-offer-articles` walks it |
|---|---|
| `goods.ask-more`, `goods.give-less`, `goods.give-remove`, `goods.ask-add` | a goods leg `(GoodId, Qty, From, To)` changed by one `orderStepUnits` step, removed, or added |
| `tariff.step` | the tariff article moved one band step inside `treaty.{kind}.tariffBandMilli` |
| `term.step` | the term moved one step, never below `treaty.minimumTermTurns` |
| `kind.downgrade` | `preferential` → `market` → `passage` |
| `embargo-lift.drop` | an embargo lift removed from the deal |
| `souls.ask-more` | one soul step, only from a party with a soul wallet (the player) |

| Deal shape (2) | Meaning |
|---|---|
| `one-off` | every goods and soul leg settles once, on the turn after signing |
| `per-turn` | every goods leg settles each turn of the term; no soul leg (souls are a one-off top-up only) |

A deal mixing the two shapes is refused at admission as out of vocabulary (the ideal's *"no
lump-sum-for-per-turn deals in v1"* as a type rule). The **walk order** over the article kinds is
`trade-ai` `counter-offer-articles`' (it owns order and direction, not the kinds). How a goods leg
settles is `settlement-payment` §7; how a signed deal's legs are funded and broken is
`treaty-lifecycle` §3a. **Refusal terms** (code, band, shortfall, building, articles tried) travel in
`treaty-respond`'s payload so the step can write the proposer's report line (T-A5); the code list is
`Accepted`, `Band`, `Building`, `Shortfall`, `OutOfVocabulary` — closed.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | The four-band ladder, one registry | `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json` |
| Built | `Clan` and `Rival` faction kinds | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:12-15` |
| Wiring gap | Every faction is hostile to every other; no peace, so no treaty can matter yet | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:12-16` (`counterparties` `diplomatic-stance` closes it) |
| Real gap | The registry, the `Access` enum, the band-grant table, the tier tables, the article and shape lists | — |
| Real gap | No tier on a built slot: a slot holds only a `StructureId` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:119`) and a second `build` on it is refused `build.occupied` (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:71`), so no upgrade exists yet | shared building-tier read, ask E-A14 |

## Tunables

`data/tuning/diplomacy.v{n}.json` (the domain file; first lander authors `v1`, others publish
`v{n+1}` with `--add-key`, the rule in [spec-goods-valuation.md](spec-goods-valuation.md) §Tunables):
`treaty.{kind}.lowestBand` (band name), `access.bandGrant.Clan.{passage,market}` (band names;
v1 values `wary`, `wary` per Q1 as amended by round 4). Tariff numbers are `trade-access`'s keys. The
tier tables (§5) and article/shape lists (§6) are registry rows, not tunables: they are rules, and a
balance pass never moves them.

## Acceptance (contract)

1. Exactly five treaty kinds and four `Access` levels — both pinned as **closed vocabularies owned by
   this code**; each pin's message says a sixth kind or fifth level is a reviewed change.
2. Every kind names a lowest band that exists in the disposition registry; an unknown band or kind is
   a load rejection naming it (T5).
3. `market` implies `passage`; `preferential` implies `market`; the implies relation is acyclic and
   closed (asserted by walking it).
4. For a `Clan` grantor with no treaty facts: band `hostile` → `closed`; `wary`, `open` and `eager` →
   `market` (never `preferential` without a treaty). For an empire grantor with no treaty facts, every
   band → `closed`. Asserted per band from the registry, not by literal count. (The building half of
   the gate is `trade-access`'s acceptance.)
5. The band-grant table is data: republishing it with a different band moves the result, with no code
   change (tested with two fixture tuning documents).
6. The tier ladders (4 trade tiers, 2 diplomacy tiers), the six deal classes, the nine article kinds,
   the two deal shapes and the five refusal codes are pinned as closed vocabularies owned by this code,
   each pin's message naming the rule it guards; every deal class names a tier that exists in its
   ladder.
7. A proposal payload mixing `one-off` and `per-turn` legs, or carrying a soul leg on a `per-turn`
   deal, is an admission refusal naming the rule.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Diplomacy/` (new), trait `core.world-diplomacy.vocabulary`;
  boundary row `core-world-diplomacy` (paths `src/FusionRpg.Core/World/Diplomacy/**` and its tests).
- `verify-change.py -Paths` on the reader, the registry file, the tuning file and the tests.

## Hard edges

- **One relation ladder.** No treaty kind defines a band of its own (ideal principle 11).
- **One treaty list.** Kinds live here; facts live in `counterparties` `diplomacy-facts`; no module
  keeps active treaties anywhere else.
- **Registries are hand-authored** (`**/_registry/**`), never generated.

## Dependencies

- Upstream: the disposition registry (built).
- Downstream: `trade-access`, `treaty-lifecycle`, `trade-ai` `counter-offer-articles`,
  `trade-surface` treaty screen.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `TreatyKind` (5), `AccessLevel` (4, ordered) | every diplomacy and trade module |
| `TreatyKindRegistry.LowestBand(kind)`, `.Implies(kind)`, `.BandGrant(factionKind, band) : AccessLevel` | `trade-access`, `treaty-lifecycle` |
| `TradeTier` (4), `DiplomacyTier` (2), `DealClass` (6), `TreatyKindRegistry.TierNeeded(dealClass)` | `trade-access`, `treaty-lifecycle`, `exchange-hub`, `rift-trade`, `trade-ai`, `trade-surface` |
| `ArticleKind` (9), `DealShape` (2), `RefusalCode` (5) | `treaty-lifecycle`, `settlement-payment`, `trade-ai` `counter-offer-articles`, `deal-valuation`, `trade-surface` `treaty-screen` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world map (factions), relation ladder, tunables.
[~] Session boundary: trade-network-idea-20260919; new file only; the boundary check's exit 1 is the
    recorded broad-lane crossing.
[x] Read this session: trade-network-ideal §7.4, §7.7; counterparties-map (whole); npc-story-events-ideal
    §6.4; disposition registry; decisions.md "Treaties, Diplomacy rail layer" row (:149).
[x] `decisions.md` — 'Treaties, Diplomacy rail layer, flow lens (2026-09-19)' locks the closed treaty vocabulary; this spec implements it.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: ZoneOfControl.IsHostile body, FactionKindCatalog read directly.
[x] Surrounding sections read (§7.7 whole, npc §6.4 whole).
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: Q1 recorded in the map; the wary-start consequence filed as E-A9.
[x] Pinned: 5 kinds, 4 levels — closed vocabularies with reasons. No population count.
[x] No event-refreshed cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No SOLID-violating path: one registry, one ladder.
[x] Registry row: the vocabulary pins are the guard; no new rule outside them.
[x] Round 4 reconciliation (2026-09-19): read decisions-round-4.md whole; Q1 band grant amended
    (market from wary, hostile blocks), building tiers (§5) and articles/shape (§6, T-A5) added;
    verified the slot has no tier (WorldState.cs:119) and upgrade is refused today (BuildResolver.cs:71).
[x] Round 5 (2026-09-20): B4 (requester's best tier anywhere) and C4 (slot display names renamed) are
    decisions, not recommendations; Diplomacy tier read through sector-features (X1), no kind.
```

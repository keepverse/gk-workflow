# Spec: `trade-access`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 6 of the [exchange map](../exchange-map.md) (wave 2; approved
2026-09-19, including owner decision Q1). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§7.6, §7.7. Cross-map decision CM1 ([trade-network-map.md](../../trade-network-map.md) §1a).
House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

One pure function answers "what may `requester` do on `grantor`'s ground this turn?" —
`Access(grantor, requester) ∈ {closed, passage, market, preferential}` — and a second answers "what
tariff does `requester` pay at `grantor`'s hubs?". Both are **derived every step and never stored**:
replaying the command log rebuilds every turn's answer for every pair. `order-book`, `logistics-flow`
(passage for routes) and `trade-ai` read them; nobody keeps a permission list.

**Round 4 (2026-09-19, [decisions-round-4.md](../decisions-round-4.md)):** access is **building tier
AND the treaty/band rules**. Clans need no treaty; the band sets the spread and `hostile` blocks. The
diplomatic level (§2) is unchanged in shape; the building gate is applied on top of it (§2a), so
`passage` — which needs no building — and the passage relation the path cache reads (§4) are untouched
by building changes.

## Scope and non-goals

In scope: the `Access` rules; the tariff rules including the most-favoured clause and the bloc; a
the per-pair passage read `logistics-flow`'s path cache holds in its key (§4).

Not in scope: writing facts (`treaty-lifecycle`, `counterparties` `diplomacy-facts`,
`diplomatic-stance`); moving bands (`counterparties` `relation-facts`, `npc-story-events`); charging a
tariff (`settlement-payment`).

## Design

### 1. Inputs — all hashed state or logged step inputs (P13)

| Input | Owner |
|---|---|
| Diplomacy facts for the pair (treaties, embargoes, bloc membership) | `counterparties` `diplomacy-facts` (hashed `WorldState`) |
| War or peace for the pair | `counterparties` `diplomatic-stance` (derived from the same facts) |
| The pair's relation band | `counterparties` `relation-facts`' **logged band snapshot** (CM1) — never a live ledger read |
| Faction kind of the grantor | `WorldFaction` (hashed) |
| Kinds, lowest bands, band grants, tariff bands, tier tables | `treaty-vocabulary` |
| Collapse of either party | `counterparties` `conquest-consequences` (`Collapse.IsCollapsed`, its ask A9) |
| Hub tier of the sector, trade tier of the requester | `exchange-hub` §7 (`Hubs.HubTier`, `Hubs.TradeTier` — thin wrappers over `trade-foundation` `sector-features`) |
| (not an input) Embassy / Consulate | **Not read here.** The Diplomacy tier gates acts (`treaty-lifecycle` §3a, via `counterparties` `diplomatic-stance` §9 (`DiplomacyGate`)), never an in-force treaty — counterparties states it so this module never re-derives access from a diplomacy building |

### 2. `Access(grantor, requester)` — rules in order

1. `grantor == requester`: not an `Access` question; own ground is logistics, always open. Unheld ground
   (no owner) is open for passage (ideal §7.6).
2. **War** between the pair ⇒ `closed`, both directions. **Collapse** of either party
   (`Collapse.IsCollapsed`) ⇒ `closed`, both directions — derived, no fact (counterparties ask A9).
3. **Embargo** in force by the grantor on the requester, or by any bloc the grantor belongs to ⇒
   `closed` (one direction: the embargo's).
4. Otherwise the highest level among three sources, and `market` implies `passage`:
   - **Treaty:** each active treaty fact for the pair (signed, not ended, not broken, not voided by a
     later `war.declared`) grants its kind's level **only while the current band reaches the kind's
     lowest band.** A band drop suspends the effect the same turn and recovery restores it, **with no
     fact written either way** (map module 6). A lost Embassy suspends nothing: the Embassy gates the
     act of offering (`treaty-lifecycle` §3a), not the treaty once signed (`counterparties` `diplomatic-stance` §9 (`DiplomacyGate`)).
   - **Band grant (owner decision Q1, amended by round 4):** `BandGrant(grantorKind, band)` from
     `treaty-vocabulary` — a `Clan` grants `passage` and `market` from `wary` (only `hostile` blocks);
     empires grant nothing without a treaty.
   - **Bloc:** both in the same bloc, and the band reaches `eager` ⇒ `preferential` (zero internal
     tariff).

This is the **diplomatic level**, `Level(grantor, requester)`. It decides `passage` on its own.

Bilateral kinds grant in both directions from one fact; `embargo` is one-sided. The `Access` level
enum and its order are `treaty-vocabulary`'s.

### 2a. The building gate — round 4

Two derived reads cap the diplomatic level by the buildings `treaty-vocabulary` §5 names:

```
cap(requester, grantor)         = the highest level whose deal class the REQUESTER's TradeTier reaches:
                                    market       needs TradeTier ≥ 1 if either party is a Clan, else ≥ 2
                                    preferential needs TradeTier ≥ 3
                                    passage      needs no building
EffectiveLevel(grantor, requester)      = min(Level(grantor, requester), cap(requester, grantor))
LevelAt(grantor, requester, hubSector)  = min(EffectiveLevel, the same cap computed from HubTier(hubSector))
```

- `order-book` trades only where `LevelAt ≥ market`; the tariff (§3) reads `LevelAt`, so a
  `preferential` treaty charges its preferential tariff only at a hub of tier ≥ 3 and the `market`
  tariff at a lower one — the treaty is not lost, its best terms need an Exchange.
- **Clan trade at world start** (round 4 Q1): every clan holds a seeded tier-1 hub (`exchange-hub` §7),
  so `LevelAt` with a clan becomes `market` the turn the player's first Trading Post completes.
- **Whose tier counts at a clan hub — decided, round 5 B4 (owner, 2026-09-20):** *"the trader's best
  Trading Post tier anywhere in that world"* — `cap(requester, …)` reads `Hubs.TradeTier(world,
  requester)` (`sector-features` `FactionTier`), never a tier in the sector the goods ship from. The
  hub-side term stays, and a clan's seeded tier-1 hub always satisfies it for `clan-barter`, so at a clan
  hub the trader's own best tier is the one that decides. (Was exchange-map owner question OQ-1, option
  (a); now closed.)
- The band still sets the spread (`price-curve`'s `relationSpreadMilli`); the building never moves a
  price.
- Neither read is stored or cached (§4 hard edge). Because `passage` never depends on a building,
  building changes never move the passage relation.

The refusal a surface or an AI shows for a missing building names the deal class and tier
(`access.needs-building:{dealClass}:{tier}`), so *"build a Trading Post"* is an explainable answer, not
a silent `closed`.

### 3. Tariff

`TariffMilli(grantor, requester)` is defined only at `market` or better:

| Case | Tariff |
|---|---|
| Same bloc | 0 |
| Grantor in a bloc, requester outside | The bloc's shared external tariff (the bloc treaty's article). Members give up their own tariffs toward non-members (ideal §7.7) |
| `preferential` treaty (grantor in no bloc) | `min(article tariff, MFN floor)` |
| `market` by treaty | The treaty's article tariff |
| `market` by band grant (clans) | `tariff.marketDefaultMilli` |

- **Most-favoured clause:** `MFN floor(grantor)` = the lowest tariff the grantor charges **any
  non-bloc requester** this turn. A bloc's zero internal tariff is excluded, as a customs union is
  excluded from most-favoured-nation treatment in real trade law; without that exception every
  `preferential` partner would be dragged to zero and a bloc would mean nothing. The floor is computed
  over non-preferential cases first, so there is no circularity.
- A treaty's tariff article is read from its fact; until the fact record carries one (ask E-A13, see
  `spec-treaty-lifecycle.md` §3) the kind's `treaty.{kind}.defaultTariffMilli` applies.
- Articles must lie inside `treaty.{kind}.tariffBandMilli` (`[min, max]`); `treaty-lifecycle` refuses
  one outside it at admission.
- Tariffs are **bounded ratios** of a fill's value (0‰–1000‰), exempt from the caps rule and commented
  as such.

### 4. The passage relation — what the path cache reads

`logistics-flow` `path-cache` must rebuild whenever the set of ground a faction may cross changes (its
trigger T10; DESIGN-GATE §2.16). Passage can change **without any fact**, because a band crossing a
threshold changes `Access`. **Superseded (audit 2026-09-20):** this section specified a `PassageDigest`
hash that `path-cache` would store and compare. `path-cache` did not adopt it: its topology key holds,
per faction pair, a **passage bit** read from this module, and compares the whole key array element by
element every L0 (`logistics-flow/spec-path-cache.md` §3, key part *Relations*; T10 in its §4). A key
compared by value cannot miss a trigger or collide, which a 64-bit digest could, so the digest is
withdrawn and nothing here stores or hashes the relation. What this module owes the cache:

- **`PassageBit(world, bands, grantor, requester) = Level(grantor, requester) ≥ passage`** (own and
  unheld ground are the cache's own rule, §2 rule 1), pure over hashed state and the logged band
  snapshot, so every trigger below reaches the key:

| Trigger | Reaches the key through `PassageBit` |
|---|---|
| Treaty signed, ended, broken, imposed | yes |
| Embargo set or lifted (own or bloc) | yes |
| War declared, peace made | yes |
| Bloc joined or left | yes |
| Band snapshot crossing a lowest band or a band-grant threshold | yes — the case a fact-driven trigger would miss |
| A faction added or removed (collapse) | yes — the pair set changes (a key-set edge) |
| A sector changing owner | no — the cache's own *Owners* key part (T5) |
| A building built, upgraded or razed | no — `passage` needs no building (§2a), so it never moves |

Faction counts per world are small, so the relation is `O(factions²)` per step.

**Registering the passage seam (counterparties ask A9) — conflict resolved.** `counterparties`
`diplomatic-stance` now defines `IPassageRule.Grants(WorldState world, BandSnapshot bands, string
grantor, string requester)` (`counterparties/spec-diplomatic-stance.md` §Design, round 5 X14: the seam
receives the logged band snapshot). This module registers the real rule, `PassageBit`, through it; the
earlier "does not register a band-blind rule" hold is lifted.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | One hostility entry point, today "anyone not you" | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:12-16` |
| Built | Faction kinds, `Clan` included | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18` |
| Built | The band ladder | `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json` |
| Wiring gap | No peace state, so every pair is at war (`counterparties` `diplomatic-stance`) | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16` |
| Real gap | All of `Access`, the tariff rule and the passage read | — |

## Tunables

`data/tuning/diplomacy.v{n}.json`: `treaty.{market,preferential,bloc}.tariffBandMilli` (`[min, max]`),
`tariff.marketDefaultMilli`. (`tariff.sinkMilli` is `settlement-payment`'s.)

## Acceptance (contract)

1. **Pure and replayable:** the same facts, stance, snapshot and kinds give the same level and tariff;
   replaying a generated command log reproduces every turn's `Access` for every pair.
2. War ⇒ `closed` in both directions; an embargo ⇒ `closed` in its direction only.
3. Lowering the band below a treaty's lowest band lowers `Access` the same turn; restoring it restores
   `Access`; no diplomacy fact is written either way (asserted on the fact list).
4. Q1 as amended by round 4: with no treaty, a `Clan` grantor gives `passage` and `market` at `wary`,
   `open` and `eager`, `closed` at `hostile`; an empire grantor gives `closed` at every band.
5. **Most-favoured clause:** for every grantor and turn, every `preferential` tariff ≤ every tariff that
   grantor charges any non-bloc requester — asserted over generated fact sequences.
6. A bloc member charges every non-member exactly the bloc's external tariff and every member 0.
7. `PassageBit` changes for a pair if and only if that pair's diplomatic `Level` crosses `passage` —
   tested for each trigger in §4's table, including a band-only change and a faction collapse (the
   key-set edge); the path cache's own T10 test consumes it.
8. Not cached across turns: no field of `WorldState` stores an `Access` level or a passage relation
   (source scan).
9. **Building gate (round 4):** with a clan at `wary` and no Trading Post anywhere in the requester's
   world, `EffectiveLevel` is `passage`; the turn the requester's first Trading Post completes it is
   `market`. With an empire `market` treaty, `LevelAt` is `market` only at hubs of tier ≥ 2 and when the
   requester's `TradeTier ≥ 2`; a `preferential` treaty reads `preferential` only at tier ≥ 3 on both
   sides and `market` below it. Each drop names `access.needs-building:{dealClass}:{tier}`.
10. **Embassy:** losing every Embassy changes no `Level` for a treaty already signed (the Embassy gates
    acts, not access — `counterparties` `diplomatic-stance` §9 (`DiplomacyGate`)).
11. Collapse ⇒ `closed` both ways, no fact written.
12. Building changes never change `PassageBit` for any pair (tested by building and razing a hub).
13. **Order-independent (audit 2026-09-20):** facts filed in one turn in either order (a treaty and an
    embargo, a bloc join and a war) give the same next-turn `Level` and tariff for every pair (both
    filing orders tested).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Diplomacy/Access/` (new), trait `core.world-diplomacy.access`,
  under boundary row `core-world-diplomacy`. Property tests generate fact sequences with
  `SeededRng.DeriveStream` (`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26`) and print, never assert, how
  many sequences ran.
- `verify-change.py -Paths` on the `Access` files and tests.

## Hard edges

- **Never stored.** An `Access` table in state would be a second source of truth beside the facts.
- **One ladder.** The band comes from the logged snapshot; no relation number is kept here.
- **Order-independent:** facts written in one turn resolve in `treaty-lifecycle` before any `Access`
  read of the next turn, so filing order inside a turn never changes an answer.

## Dependencies

- Upstream: `treaty-vocabulary`; `counterparties` `diplomacy-facts`, `diplomatic-stance`,
  `relation-facts` (band snapshot).
- Downstream: `order-book`, `settlement-payment` (tariff), `treaty-lifecycle` (admission checks),
  `logistics-flow` `path-cache` (`PassageBit`), `trade-ai` `deal-valuation`, `trade-stories` (`AccessIs`
  leaf, counterparties C6).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `TradeAccess.Level(world, bands, grantor, requester) : AccessLevel` (diplomatic; decides passage) | `logistics-flow` (via `IPassageRule`), `trade-ai` |
| `TradeAccess.EffectiveLevel(world, bands, grantor, requester)`, `TradeAccess.LevelAt(world, bands, grantor, requester, hubSectorId)` | `order-book` (`LevelAt`), `trade-ai`, `trade-stories` `AccessIs` (`EffectiveLevel`), `trade-surface` |
| `TradeAccess.TariffMilli(world, bands, grantor, requester, hubSectorId) : long` | `settlement-payment`, `trade-ai` |
| `TradeAccess.PassageBit(world, bands, grantor, requester) : bool`, registered as `IPassageRule` | `logistics-flow` `path-cache` (key part *Relations*) |

**A policy reads the same functions (trade-ai ask T-A9).** Each function takes its inputs through a
small read interface implemented by the world (inside `Step`) and by `BelievedWorldView` (for policies:
own tiers exact, foreign hub tiers believed — `trade-ai` `trade-intel`). One rule, two input sources —
the `SupplyReach` precedent — never a second copy of the gate in `World/Ai/`.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: diplomacy (facts, stance), relation ladder, world movement (passage), caps (tariff ratio).
[~] Session boundary: trade-network-idea-20260919; new file only; the check's exit 1 is the recorded
    broad-lane crossing.
[x] Read this session: trade-network-ideal §7.6-§7.7; counterparties-map (whole); logistics-flow-map
    (phase order, path-cache triggers, A7); trade-network-map §1a (CM1); npc-story-events-ideal §6.4.
[x] decisions.md :149 (closed treaty vocabulary, access derived) implemented, not re-decided.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: IsHostile body and callers' premise; faction kinds.
[x] Surrounding sections read (§7.7 whole).
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: Q1 in the map; the MFN customs-union exception is stated here and in the
    map's module 6 text.
[x] No population count pinned.
[x] Cache (§2.16): the path cache's full trigger set for passage is enumerated above, including the
    key-set edge (faction added/removed) and the band-only edge; each has its own test (Acceptance 7).
[x] Orderings: same-turn filing order cannot change Access (facts land in Snapshot, read next turn).
[x] No actor magnitude.
[x] No SOLID-violating path: one Access function for player, AI and routing.
[~] Registry row: "Access is never stored" (Acceptance 8) gets a guard row with its source scan.
[x] Round 4 reconciliation (2026-09-19): decisions-round-4.md read whole; clan band grant amended,
    the building gate added as §2a on top of an unchanged diplomatic level; counterparties A9 answered
    (collapse ⇒ closed; IPassageRule registration, with its band-snapshot conflict reported).
[x] Round 5 (2026-09-20): B4 decided (requester's TradeTier = FactionTier anywhere in the world);
    OQ-1 closed; no formula change.
[x] Audit 2026-09-20 (independent): PassageDigest withdrawn — path-cache compares a per-pair passage bit
    by value (logistics-flow/spec-path-cache.md §3); IPassageRule now carries the band snapshot
    (counterparties/spec-diplomatic-stance.md), so the rule is registered; acceptance renumbered 1-13
    with an order-independence criterion added.
```

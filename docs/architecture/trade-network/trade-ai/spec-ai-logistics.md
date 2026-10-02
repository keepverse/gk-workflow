# Spec: `ai-logistics`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `ai-logistics`, row 7 of the approved
[trade-ai map](../trade-ai-map.md) (wave 3). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§8.3 (caravans are legions), §8.5 (*"Automate the flow; the player sets policy"*), §8.6, principle 10.
Upstream: `trade-intel`, `deal-valuation`, `ai-bidding`, `ai-spend-limit`; `logistics-flow`
`auto-banking`, `lane-loss`, `logistics-facts`; `fleet` `trade-route-order`, `escort-link`;
`legion-build` `standing-orders`, `escort-stance` ([legion-build-map.md](../../legion-build-map.md) §5.8–§5.9).

## Objective

An AI empire runs its goods the way a player does, through the same commands: auto-banking by default,
`route-set` when goods should go somewhere else, a caravan (a legion on a trade standing order) when a
foreign hub can only be reached overland, and an escort on the caravans carrying the most. It **plans no
paths** — it names destinations, and `logistics-flow` and `fleet` do the routing — and it takes legions
for trade work only when the military ladder has nothing for them to do.

Success looks like: an AI whose route is cut redirects or clears it within one turn of seeing the cut;
no legion is ever given two orders in a turn; and an AI never files a command the player could not file.

## Scope and non-goals

**In:** when to file `route-set`/`route-clear`, when to put an idle legion on a trade standing order,
when to escort, and how the ladder skips legions already on a standing order.

**Not here:** paths, flow, loss, delivery (`logistics-flow`); the trade-route order's behaviour and the
escort mechanics (`fleet`, `legion-build`); what to buy or sell (`ai-bidding` decides; this module moves
the goods there). No routing code: TC7.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The ladder walks own forces in ordinal order, at most one order each, and skips routed legions | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:53-70` |
| `Hold` is the ladder's last rule; it files `stand-fast` | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:70` |
| The one per-legion command builder every AI order comes from | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:568-582` |
| Two orders for one legion in one turn throw in the commit | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:270-272` |
| Stances are a closed list of four today | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:22` |
| A legion's route survival check against supply burn, used by `Sever` | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:474-500` |
| `Sever` already calls `ReconnectionCost` from `World/Ai/`, through `SeveranceScore` | `gk-core/src/FusionRpg.Core/World/Ai/SeveranceScore.cs:23-32` |

### Wiring gap

None in this module's code. Its inputs are all other programs' unbuilt modules.

### Real gap

All of it; and three upstream pieces must exist first: `legion-build` `standing-orders` (a stored order
on the legion, [legion-build-map.md](../../legion-build-map.md) §5.8), `escort-stance` (§5.9), and
`fleet` `trade-route-order`.

## Design

### 1. Routes: file only on a reason

With no policy, goods auto-bank (`logistics-flow` `auto-banking`). The AI files:

| Command | When | Subject |
|---|---|---|
| `route-set sector → hub, good` | `ai-bidding`'s plan sells good *g* at a **foreign** hub *h* (its §2a pairs), and *g* is not yet in the faction's consignment there — the route delivers into that consignment (`exchange` ask E-A5: a consignment is a `route-set` destination) over ground the faction holds `passage` for | the good's source sector |
| `route-set sector → own hub, good` | the faction's own hub at a Treasury bank point holds goods for other traders' buy orders (`bank-hold`, round 4 Q2) and *g* sits in another own sector | same |
| `route-set sector → bank point, good` | the default destination is believed cut (own `lane.cut`/strand facts, read exact as own flows through `trade-intel` `OwnFlows`) and another own bank point is reachable | same |
| `route-clear sector, good` | the reason above no longer holds | same |

Each is a policy-order kind (`ai-spend-limit` `AiPolicyOrderKinds`), id `ai-{turn}-r-{sector}-{good}`,
re-filed only when the destination changes.

### 2. Caravans and escorts come only from idle legions

The ladder runs first. A legion whose ladder result is **`Hold`** — nothing to defend, finish, take,
sever, recover, interdict, explore or expand — is **idle**. Only idle legions are used here, which keeps
the owner's rule order intact (no new rule enters the ladder for trade logistics):

1. **Escort first.** For each own caravan, in descending own flow value, whose lane has believed
   hostile threat (`ThreatMap`, defensive reading) and whose flow value ≥ `trade.escortMinFlowValue`,
   assign the idle legion with the fewest reach turns to it: `legion-build`'s escort command targeting
   the caravan. Ties by entity id.
2. **Then caravans.** For each hub in `ai-bidding`'s plan that the faction can reach only overland
   through foreign ground it holds `passage` or better for, assign an idle legion with bearer capacity:
   `legion-build`'s set-standing-order command with `fleet`'s trade-route order kind. At most
   `trade.caravanShareMilli` of own legions are on trade standing orders at once (a structural share, so
   the empire keeps an army).
3. **Otherwise** the idle legion keeps its `stand-fast`.

**Round 4 (2026-09-19, [decisions-round-4.md](../decisions-round-4.md)):** a caravan standing order is
a feature of the **Caravan Yard** (Caravans tier 1: legions load and unload goods; Convoy Depot, tier 2,
more crew and range) — step 2 files only from a sector whose Caravans tier the order needs, read through
the view (ask T-A9); a `route-set` to a bank point targets only sectors with a **Counting House** (the
bank point, round 4 B). **Round 5:** the AI's seat holds a tier-1 Counting House and Storehouse from turn 0
(A1), so a bank-point route always has at least the seat as a target; a caravan leg to a **foreign** hub
is planned only where the hub owner has a Caravan Yard (B3 — `fleet` `depot` `ForeignSite.Of`, read as
belief through the view, `trade-intel` `BelievedAcceptsCaravans`), because the leg otherwise waits with
`depot.no-foreign-yard`. When a caravan or a bank point the plan wants is blocked by a missing building,
the plan's value is handed to `ai-trade-buildings` as that building's payoff; this module never files
`build`. **Escort choice** (step 1) weighs the idle legion's strength by the power roll-up (`legion-build`
`legion-power`, round 5 X7) over its own
stacks once it lands (round 4 P — *"escort strength … the AI's force estimates where it reads its own
legions"*); until then, fewest reach turns and entity id, as above. `ai-trade-buildings` claims its
at most one `Hold` legion **before** this module (the order in `ai-treaty-policy` §1).

The escort or standing-order command **replaces** that legion's `stand-fast` in the order list, so the
legion still has exactly one order (the invariant at `RpgStore.WorldTurns.cs:270-272`).

### 3. The ladder skips standing-order legions

A legion that holds a standing order is skipped by the ladder's entity walk, the way a routed legion
already is (`FrontierRulesPolicy.cs:57`). Otherwise the ladder's explicit order would override the
standing order every turn (`legion-build`: *"An explicit order for that legion this turn wins over its
standing order"*). The legion is identified from state through `OwnForces` once `standing-orders` puts
the field on the entity (ask T-A2). Releasing a caravan (the good is no longer planned) is a
`clear-standing-order` filed here, after which the ladder sees it again next turn.

### 4. No routing here (TC7)

This module never computes a path or calls `ReconnectionCost`. Destinations are named; `logistics-flow`
`path-cache` routes goods and `fleet`'s planner routes caravans. Code lives under
`src/FusionRpg.Core/World/Ai/Trade/` (the no-`WorldState` scan) and `trade-foundation` `routing-guard`
widens to that folder (T-A4), so a later edit that adds routing fails a guard, not a review.

### 5. Gate

Every command here is filed only when the stamp grants the capability that admits it (TC6).

## Tunables

| Key | File | Unit | Nature |
|---|---|---|---|
| `trade.escortMinFlowValue` | `gk-core/data/tuning/ai.v3.json` (next AI version) | value-index units per turn | a caravan worth escorting |
| `trade.caravanShareMilli` | same | ‰ of own legions | structural share, commented |

## Acceptance (contract)

1. **One order per entity** over a 20-turn trade run (extends
   `gk-core/tests/FusionRpg.Core.Tests/World/Ai/FrontierRulesTests.cs:115`).
2. **Same commands as the player.** Every command kind this module files is in `WorldCommandKinds.All`
   and passes admission.
3. **Cut response.** A route whose default path is cut is redirected or cleared within one turn of the
   cut entering the AI's view.
4. **Idle only.** No legion whose ladder result is anything but `Hold` receives an escort or standing
   order; a legion under threat still defends.
5. **Skip.** A legion on a standing order receives no ladder order.
6. **Share.** At most `trade.caravanShareMilli` of own legions hold trade standing orders at any turn end.
7. **No routing.** A source scan under `World/Ai/Trade/` finds no `ReconnectionCost` and no path search.
8. **Legacy.** On a world without the logistics capability the policy files exactly what it files today.
9. **Order-independent.** An escort assigned before or after its caravan's order is set gives the same
   first escorted turn (both filing orders tested — the key-set edge is the caravan acquiring its order,
   DESIGN-GATE §2.16).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ai/Trade/AiLogisticsTests.cs` (new): 2–6, 9.
- `gk-core/tests/FusionRpg.Core.Tests/World/Ai/FrontierRulesTests.cs` (extend): 1, 5, 8.
- `gk-core/tests/FusionRpg.Guard.Tests/` (the widened routing guard): 7.
- Run `.\scripts\verify-change.py -Paths <changed paths> -Session <id>`; `FrontierRulesPolicy.cs`
  changes, so the full suite once at module end; campaign tests run and reported.

## Hard edges

- **Ordering against `legion-build` and `fleet`.** This module cannot land before `standing-orders`,
  `escort-stance` and `trade-route-order`; each is a hashed-state change owned there.
- **The ladder's skip** changes `FrontierRulesPolicy`'s walk; on a world with no standing orders it is
  a no-op, which criterion 8 proves.

## Dependencies

| Consumes | From |
|---|---|
| own flows, cut and strand facts | `trade-intel` (`OwnFlows`), `logistics-flow` `logistics-facts` |
| the sell plan | `ai-bidding` |
| `route-set`, `route-clear` | `logistics-flow` `auto-banking` |
| stored standing order on the entity; set/clear command; escort command | `legion-build` `standing-orders`, `escort-stance` (T-A2) |
| trade-route order kind, escort behaviour | `fleet` `trade-route-order`, `escort-link` |
| `AiPolicyOrderKinds`, `Trim` | `ai-spend-limit` |

| Exposes | To |
|---|---|
| the idle-legion rule and the standing-order skip | `interdiction` (runs before idle is decided), `clan-behaviour` |

## Boundaries

- **Always:** name destinations, never paths; idle legions only; one order per legion.
- **Ask first:** a trade rule inside the ladder (that is a rule-order change, owner-reserved).
- **Never:** a routing call; a caravan entity kind (`WorldEntityKind.Caravan` is being retired by
  `legion-build` `caravan-kind-retire`); a command the player cannot file.

## Design-gate checklist

```
[x] Subsystems: world map AI (ladder walk), logistics (commands — consumed), legions (standing orders,
    escort — consumed), tunables.
[~] Session boundary: docs-only under trade-network-idea-20260919; check exits 1 on crossings already
    recorded; this file is new.
[~] Read this session: as spec-trade-intel.md's list, plus legion-build-map §5.8-§5.9 and fleet-map
    §4-§5. NOT read: fleet and legion-build module specs (fleet specs for these modules do not exist yet).
[x] decisions.md: no lock covers AI logistics.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: ladder walk and routed skip, Order builder, two-order throw, stance list,
    SurvivesTheRoute, SeveranceScore's ReconnectionCost call.
[x] Surrounding sections read: logistics-flow-map §6-§7, §10; fleet-map §4-§5.
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: TC7 in the map and ask T-A4.
[x] No population pinned.
[x] Event-refreshed cache: none owned; the path cache's triggers are logistics-flow's.
[x] Orderings: escort-before/after-order is stated order-independent and tested both ways.
[x] No actor magnitude.
[x] No SOLID-violating path: same commands as the player; no second route planner.
[ ] Registry row for criterion 7 lands with trade-foundation's widened routing guard (T-A4).
[x] Round 4 reconciliation (2026-09-19): caravans need a Caravan Yard, bank-point routes a Counting
    House; missing buildings feed ai-trade-buildings; escort strength from the power roll-up when it lands.
[x] Round 5 (2026-09-20): A1 (the seat is a bank point from turn 0), B3 (foreign-hub caravan legs only
    where the hub owner has a yard), X7 (roll-up owner).
```

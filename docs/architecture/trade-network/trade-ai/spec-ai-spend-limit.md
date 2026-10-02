# Spec: `ai-spend-limit`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `ai-spend-limit`, row 3 of the approved
[trade-ai map](../trade-ai-map.md) (wave 1). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§7.5 (*"a per-turn AI purchasing limit is a structural limit, stated in a comment"*), §13
(`ai.maxSpendPerTurnMilli`), §14b (*"AI bidding and AI spend limit are its knobs"*). Upstream:
`counterparties` `trade-difficulty-knobs`, `empire-treasury`, `clan-economy`; `trade-foundation`
`world-stamp` (profile id).

## Objective

Two bounds keep a trading AI from doing damage by volume:

1. **What it may commit.** An AI's outstanding trade exposure — open buy orders, per-turn treaty legs it
   pays, tariffs it accepts — stays within a stated share of what it earned last turn. A player cannot
   drain an AI by selling into an unbounded appetite, and an AI with a bug in its wants cannot empty its
   own treasury in one turn.
2. **How many orders it may file.** The store's guard against a runaway policy today counts the wrong
   thing (TC1). It becomes two honest counts: at most one order per own entity plus one, and at most a
   stated number of policy-kind orders.

Both are **structural limits** (per-turn rates, not magnitude ceilings), commented as such, per the caps
rule (`power/ssot-power-scale.md` §11, CLAUDE.md "Caps").

## Scope and non-goals

**In:** the exposure computation, the limit, the trimming rule every trade-ai module calls before
filing, the order bound in the store fill, the closed list of policy-order kinds.

**Not here:** what to buy (`ai-bidding`), what a treaty is worth (`deal-valuation`), the difficulty
profile catalog (`world-continuity`) and its trade rows (`counterparties` `trade-difficulty-knobs`), the
treasury itself (`counterparties` `empire-treasury`). No player-side limit: the player's spend is bounded
by what the player holds, the same rule as everyone's.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The AI fill: every policy faction in ordinal order, on its own view and seed stream, inside the commit transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:218-245` |
| The bound: `orders.Count > world.Entities.Count + 1` throws | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:252-255` |
| One order per entity is enforced separately, by entity id | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:270-272` |
| Every AI order passes the player's admission; a refused one throws | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:277-281` |
| The ladder files `stand-fast` with a **null** entity id for `Hold` and a holding `Recover` | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:568-582` (`:578`) |
| The store passes self-knowledge derived from the command log into the view (`LastOrderedDestinations`) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:237-244`; `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:54-67` |
| A declared per-faction lever is hashed and named in the report (`UpkeepHandicapMilli`) | `gk-core/src/FusionRpg.Core/World/WorldState.cs:79-83` |

### Wiring gap

The order bound exists but does not know policy orders.

### Real gap

The spend limit, the exposure computation, the policy-kind class.

## The contradiction this module corrects (TC1)

The map said the current bound *"would throw on the first AI that files a treaty and a route in one
turn."* Reading `RpgStore.WorldTurns.cs:252` shows otherwise: `world.Entities` is **every faction's**
entities, so a faction's allowance is `(everyone's legions + 1)`, whatever it owns. The bound is loose
by an amount that depends on how many legions the faction's *enemies* field — a limit by accident. And
"entity-less" cannot mark a policy order, because the ladder's `Hold` is already entity-less
(`FrontierRulesPolicy.cs:578`). The bound is therefore counted by **kind**, not by a null field.

## Design

### 1. The order bound (Data, in the fill)

```text
policyKinds  = AiPolicyOrderKinds.All                       // closed Core list, §2
ordinary     = orders.Count(o => !policyKinds.Contains(o.Command.Kind))
policy       = orders.Count(o =>  policyKinds.Contains(o.Command.Kind))
ownEntities  = world.Entities.Count(e => e.OwnerFactionId == faction.FactionId)

if (ordinary > ownEntities + 1) throw …    // structural: one per own entity, plus the faction's stand-fast
policyBound  = PolicyOrdersBase + PolicyOrdersPerOwnSector × ownSectors      // grows with holdings
if (policy > policyBound) throw …                            // structural: bounds a runaway policy loop
if (two policy orders share one command key) throw …         // a duplicate key is a policy bug, never a trim
```

**Why the policy bound scales (audit 2026-09-20).** A flat per-turn count facing an empire whose
legitimate policy orders grow with its holdings (one `order-set` per hub, good and side; one route per
sector and good) is a flat rate against a scaling sink — a hidden ceiling on how much an AI can trade
(ssot-power-scale PS-8). Standing orders are refiled only on a real change (`ai-bidding` §4), so the
normal count is small; the bound exists to catch a loop, and a loop is caught just as well by a bound
that grows with what the faction holds. The duplicate-key check catches the other runaway shape (one key
refiled many times) at any empire size.

It replaces `RpgStore.WorldTurns.cs:252-255` in place, keeps the existing "two orders for one entity"
check (`:270-272`) unchanged, and keeps throwing rather than trimming: a policy that over-files is a bug,
and a silent trim would hide it (the store's own reasoning at `:246-251`). Both comments say
*structural limit, not a progression cap*.

### 2. `AiPolicyOrderKinds` — the closed list of policy-order kinds

`src/FusionRpg.Core/World/Ai/Trade/AiPolicyOrderKinds.cs` (new): the command kinds that name no entity by
design — `route-set`, `route-clear`, `bank-hold` (`logistics-flow` `auto-banking` §2a), `order-set` (`exchange`), the treaty, embargo and
bloc kinds (`exchange` `treaty-lifecycle`), `war-declare`, `peace-offer`, `peace-accept`
(`counterparties` `diplomatic-stance`). Each is added **by the module that adds the kind**, in the same
change; a guard test fails if a kind in `WorldCommandKinds.All` (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:121`)
is entity-less by admission rule yet missing from the list. A closed vocabulary, pinned because the code
owns it.

### 3. The spend limit (Core, policy side)

```text
income(view)   = Σ value of the faction's own banking facts last turn        (empire: empire-treasury)
               + Σ value of its own sector production last turn             (clan: clan-economy)
limit(view)    = aiMaxSpendPerTurnMilli[profile] × income / 1000             // structural per-turn rate
exposure(plan) = Σ open buy orders:  remaining qty × limit price
               + Σ per-turn treaty legs the faction gives, and tariffs it pays, per turn
```

- **Income is self-knowledge from the log.** The store reads the previous turn's stored report for the
  faction's banking/production entries and passes the value into the view, exactly as it passes
  `LastOrderedDestinations` (`RpgStore.WorldTurns.cs:237-244`). Replay never runs a policy, so this input
  can never reach a hash (`gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs:136`).
- **`SpendLimit.Trim(view, plan) → plan`.** Every trade-ai module builds its candidate orders, then calls
  `Trim`. If `exposure > limit`, orders are dropped lowest priority first (priority = the leg's want,
  descending; ties by good id, then hub id) until it fits, and each dropped order is reported in the
  reason of the order that survived: *"bought 3 of 5 wants, spend limit 420 of 420"*.
- **Never beyond holdings.** Exposure also never exceeds the value of goods the faction holds above its
  need reserve, because payment is barter from stock (`exchange` settlement). The limit tightens; it
  never licenses an unpayable order.
- **Zero income, zero buys.** An AI that banked nothing last turn files no buys. It can still sell
  surplus, which is how it earns. Stated, not hidden: a starving empire does not trade its way out on
  credit, because no one has credit (every empire runs the same economy, ideal principle 10).
- The profile id comes from the world stamp through the view (T-A8); the ‰ row is `counterparties`'.
- **This limit binds the AI only, and says so** (umbrella invariant 11: a rule that binds one side is a
  handicap and is named). It is the ideal's own AI purchasing limit (§7.5), a difficulty knob on AI
  appetite; the player's equivalent bound is simply what the player holds. It bounds the exposure an
  AI **files**. It does **not** bound what leaves an AI's hub when other traders buy there: a hub owner
  files nothing at its own hub (`order-book` `order.own-hub`), and that passive flow is bounded by
  `exchange` — clearing capacity and the owner's need reserve on every buy (`order-book` §Design 6).

## Tunables

| Key | File | Unit | Nature |
|---|---|---|---|
| `difficulty.<profileId>.aiMaxSpendPerTurnMilli` | `data/tuning/trade.v1.json` (new; `counterparties`' row) | ‰ of last turn's income | structural per-turn rate, a difficulty knob |
| `trade.policyOrdersBase` | `gk-core/data/tuning/ai.v3.json` (next AI version) | orders | structural runaway bound, constant part |
| `trade.policyOrdersPerOwnSector` | same | orders per owned sector | structural runaway bound, the part that grows with holdings (audit 2026-09-20; replaces the flat `trade.maxPolicyOrdersPerTurn`) |

The loader rejects a missing key, a `policyOrdersBase < 1` and a `policyOrdersPerOwnSector < 1`.

## Acceptance (contract)

1. **Spend.** Over a 20-turn scripted run with trade on, for every AI faction and turn,
   `exposure ≤ limit` after `Trim` (an invariant over the run, not a count of orders).
2. **Order bound.** A policy filing `ownEntities + 1` ordinary orders and `policyBound` policy orders
   commits; one more of either, or two policy orders with one key, throws inside the commit and leaves the
   world untouched
   (the `A_policy_that_throws_leaves_the_world_exactly_where_it_was` shape,
   `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs:213`).
3. **Not enemy-dependent.** Adding enemy legions to a world does not change how many orders a faction
   may file (the TC1 regression).
4. **`Hold` is ordinary.** A faction whose every legion holds files `stand-fast` orders counted as
   ordinary, and commits.
5. **Closed kind list.** Every entity-less command kind is in `AiPolicyOrderKinds`, and every member of
   it exists in `WorldCommandKinds.All`.
6. **Exploit guard — no drain.** A player trading at an AI's hub for many turns never takes that AI's
   stock of any good below its need reserve, and never moves more value out per turn than the hub's
   clearing capacity — asserted per turn over the run against `exchange`'s bounds, which are what govern
   passive hub flow. *(Audit 2026-09-20: this criterion said the flow was bounded by this module's
   limit, which a hub owner never files against, so it tested a mechanism that does not exist.)*
7. **Exploit guard — no credit.** No trimmed plan's exposure exceeds the value of goods held above the
   need reserve.
8. **Profile read.** A missing profile or key rejects the load; the default profile reproduces the
   stated ‰.

## Test plan and verification boundary

- `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs` (extend): criteria 2–4 with fake policies.
- `tests/FusionRpg.Core.Tests/World/Ai/Trade/SpendLimitTests.cs` (new): 1, 6, 7, 8 with a scripted view.
- `gk-core/tests/FusionRpg.Guard.Tests/` (new scan): criterion 5.
- Run `.\scripts\verify-change.py -Paths <changed paths> -Session <id>`. `RpgStore.WorldTurns.cs`
  resolves only to `data-fallback` and `World/Ai/**` to `core-fallback` today; the change touches Core
  and Data together, so per AGENTS.md it runs the full suite **once** at module end, and adds focused
  boundary rows (`data-world-ai-fill`, `core-world-ai-trade`).

## Hard edges

- **A shipped method's guard changes** (`FillAiCommandersUnlocked`). No hash moves — the fill writes
  commands, not state — but every existing AI test runs through it; they are run and reported.
- **AI tuning version switch** (`ai.v2.json` → `ai.v3.json`): the host names the file literally
  (`gk-core/src/FusionRpg.Server/Program.cs:234`), so the publish and the loader switch are one change. **This module
  is the file's one creator (global audit M8, round 6):** its keys are the structural bounds every other
  trade-ai module's filing passes through, so it lands first inside wave 1 and carries the switch; every other
  trade-ai spec publishes `v{n+1}` and claims no switch.
- **AI-only settings live in `ai.v3.json` (round 6, closing audit A-X1 by principle).** A policy-only key must
  not sit in the step-read `trade.v{n}.json`, whose version enters every world stamp: retuning AI appetite
  would refuse replay of every trade world for nothing (TC5, tunables-ssot T7). So
  `difficulty.<profileId>.aiMaxSpendPerTurnMilli` — which only this policy reads — belongs in `ai.v3.json`.
  Its file is `counterparties`' (`trade-difficulty-knobs`), so the move is ask **T-A13**; this module reads one
  home, never two, and duplicates no key while the move lands.
- **Wave and ruleset bump (round 6 C1):** trade-ai **wave 1**. Policies run **outside** `Step` (replay never
  re-runs one, `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs:136`), so this module grants no capability
  flag and takes no bump: it **reads** the flags `world-stamp` grants (T-A8) and files nothing a flag does not
  allow. Its wave is named because the family's landing order is one document
  ([../landing-order.md](../landing-order.md)).

## Dependencies

| Consumes | From |
|---|---|
| `aiMaxSpendPerTurnMilli` per profile | `counterparties` `trade-difficulty-knobs` |
| profile id and capability flags via the view | `trade-foundation` `world-stamp` (T-A8) |
| last turn's banking and production entries | `sector-yield` `banking-fact`, `counterparties` `clan-economy` (T-A7) |
| own open orders via the view | `exchange` `order-book` (T-A6) |
| need reserve | `counterparties` `need-vector` (`needs.reserveTurns`) |

| Exposes | To |
|---|---|
| `SpendLimit.Trim` | `ai-bidding`, `ai-treaty-policy`, `ai-logistics`, `clan-behaviour` |
| `AiPolicyOrderKinds` | the store fill; every sibling that adds an entity-less kind |

## Boundaries

- **Always:** throw on over-filing; trim on over-spending; say which orders were trimmed; comment both
  as structural.
- **Ask first:** any spend limit on the player; credit or deferred payment.
- **Never:** a silent trim of an over-filed order list; a limit that depends on another faction's size.

## Design-gate checklist

```
[x] Subsystems: world map AI (fill, policy), economy (sinks, AI treasury — read), caps (structural
    per-turn limits), tunables, data (the fill's guard).
[~] Session boundary: docs-only under trade-network-idea-20260919; check exits 1 on crossings already
    recorded; this file is new.
[~] Read this session: as spec-trade-intel.md's list, plus ssot-power-scale §11 via CLAUDE.md "Caps".
    NOT read: ssot-power-scale.md in full.
[x] decisions.md: no lock covers the AI order bound; spec-ai-commander §The invariant is the binding text.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: the fill (:218-281), Order() entity null for stand-fast (:578), view seam.
[x] Surrounding sections read: the fill's own comment block on the bound (:246-251).
[x] Constraints tested, not assumed: TC1 was found by reading the bound, and is corrected here.
[x] No §2 invariant contradicted; both limits are structural and commented (invariant 11).
[x] Corrections propagated: TC1 corrected in the map (What the code says, module 3, contradictions).
[x] No population pinned; AiPolicyOrderKinds is a closed code-owned list, pinned for that reason.
[x] No event-refreshed cache: income is read from the stored report each fill.
[x] Orderings: trimming is by want then id, deterministic; no filing-order dependency.
[x] No actor magnitude.
[x] No SOLID-violating path: one limit, one trimming rule for every module.
[ ] Registry rows (closed kind list scan; structural-limit comments) owed with the change.
[x] Audit 2026-09-20 (independent): the flat policy-order bound replaced by one that grows with owned
    sectors plus a duplicate-key check (a flat bound against scaling holdings is a hidden ceiling);
    `bank-hold` added to the policy kinds; criterion 6 re-pointed at exchange's bounds (a hub owner files
    nothing at its own hub); the AI-only nature of the spend limit stated.
```

# Spec: `clan-behaviour`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `clan-behaviour`, row 9 of the approved
[trade-ai map](../trade-ai-map.md) (wave 4). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§7.4 (clans as the main partners; *"a clan's price is its personality"*), §14b (clans consume and pay
upkeep). Upstream: `ai-bidding`, `ai-treaty-policy`, `ai-logistics`, `ai-spend-limit`; `counterparties`
`clan-seeding`, `clan-economy`, `empire-roster`.

## Objective

Neutral clans are the headline v1 counterparty. They need a brain that does three things and refuses a
fourth: **defend their own ground**, **run their hub from their own needs**, **answer treaty offers** —
and **never expand**. The last is the kind's own contract (`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:12-13`,
*"A neutral clan: defends its ground, never expands"*) and the reason clans are counterparties rather than
a third and fourth empire racing the player for sectors (`spec-ai-commander.md` §Who gets which policy
makes the same call for the wild).

Success looks like: a clan never leaves its sectors or claims ground; it sells what it has to spare and
buys what it lacks; two clans with the same data behave the same; and nothing about a clan is authored
per clan.

## Scope and non-goals

**In:** the `clan-keeper` policy id; the rule subset of the one ladder it runs; the diplomacy step
subset; the economic layers it calls; its registration.

**Not here:** where clans are and what they crave (`counterparties` `clan-seeding` — computed from climate
and species through `need-vector`); what they produce and consume (`clan-economy`); clan **requests to the
player** (`npc-story-events` `petition-host`, which reads the same need vector — this module files none);
whether a clan hub needs a treaty (`exchange` Q1, **amended by round 4**: no treaty and no embassy; the
band sets the spread and only `hostile` blocks; the trader needs a Trading Post — this module files only
what `LevelAt` and admission permit).

**Round 4 (2026-09-19):** a clan is seeded with a **tier-1 trade hub** on its `Market` slot (`exchange`
ask E-A16 on `counterparties` `clan-seeding`) and **never builds or upgrades** — building is expansion of
the empire kind, and the clan contract is *defend, never expand* (`FactionKindCatalog.cs:12-13`). So
`ai-trade-buildings` is not in the clan layer list, and a clan's barter reach is its seeded post.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The `Clan` kind and its contract | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:12-13` |
| Only two policies exist; a faction's `PolicyId` must be known | `gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18`; `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:118-120` |
| The ladder is a chain of static rules over one entity walk | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:53-70` |
| `Defend` routes a legion to a threatened own Seat | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:91-123` |
| `stand-fast` is the wild's permanent posture; the log still records "chose to do nothing" | `gk-core/src/FusionRpg.Core/World/Ai/StandFastPolicy.cs:6-17` |
| No template seeds a clan | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:78-83` |

### Wiring gap

None — the kind exists and is never used; `clan-seeding` is what first puts a clan on a map.

### Real gap

The policy.

## Design

### 1. One ladder, a rule subset as data

`FrontierRulesPolicy`'s rules become an **ordered list** the class is constructed with, instead of a
hard-coded `??` chain (`FrontierRulesPolicy.cs:62-70`). The empire list is today's order plus
`Interdict` (owner Q1); the clan list is:

```text
clan-keeper:   Defend(own-ground) ?? Finish(own-ground) ?? Recover ?? Hold
```

- **`Defend(own-ground)`** is `Defend` with one extra condition: the route stays inside sectors the clan
  believes it holds. A threatened seat the clan cannot reach through its own ground is not defended by
  marching through someone else's.
- **`Finish(own-ground)`** clears a guarded slot only on a sector the clan holds.
- No `Abandon`, `Take`, `Sever`, `Interdict`, `Explore` or `Expand` — the rules that move a legion onto
  ground it does not hold or claim it. The contract is enforced by which rules exist in the list, not by
  a weight a tuning change could undo.

One class, two lists: the refactor is behaviour-preserving for `frontier-rules`, proven by its existing
tests and the 20-turn acceptance scenario, which are run and reported.

### 2. Economy and diplomacy — the same layers, clan rows

- **Hub:** `ai-bidding` with the clan's personality row — sells surplus above reserve, buys wants. Its
  wants are its computed personality (`need-vector` over climate and species), so *"the goods it craves"*
  is never authored.
- **Goods movement:** `ai-logistics` restricted to `route-set` between its own sectors. **No caravans and
  no escorts**: a clan never puts a legion on a trade standing order, so it never files a foreign trade
  route (the map's contract).
- **Diplomacy:** `ai-treaty-policy` with the step subset `Answer, Peace, End, Embargo, Propose` — **no
  `War`**. A clan answers and proposes treaties and can make peace; it never declares war. Again a
  structural subset, not a zero weight.
- **Spend:** `ai-spend-limit` with income = its own production last turn (`clan-economy`).

### 3. Registration

`clan-keeper` joins `FactionPolicies` (`FactionPolicies.cs:13-18`) as the same composed class with the
clan rule list, the clan step subset and personality id `clan-keeper`. `counterparties` `clan-seeding`
gives every seeded clan this policy id. The wild keep `stand-fast`.

### 4. Gate and determinism

On a world without the clan and trade capabilities there are no clans, so nothing here runs. Pure over
`(view, seed)`; the seed is unused; ordinal ids everywhere.

## Tunables

`personality.clan-keeper.{tradeAppetite,treatyWillingness}Milli` — `counterparties`' rows in
`data/tuning/trade.v1.json` (new). No key of its own: the contract is structural (rule and step subsets).

## Acceptance (contract)

1. **Never expands.** Over a 20-turn run, no clan files a `move` whose route leaves its own sectors, and
   no `claim`.
2. **Never wars.** No clan files `war-declare`.
3. **Never caravans.** No clan legion receives a standing trade-route order or an escort order.
4. **Defends.** A clan seat under threat above its garrison, reachable through own ground, draws a
   `Defend` move.
5. **Needs, not scripts.** Two clans with the same climate, species and state file byte-identical orders
   (up to their own ids); a source scan finds no clan-id or faction-id literal in the policy.
6. **No surplus, no sell.** A clan whose every good is at or below reserve files no sell order.
7. **Ladder refactor is neutral.** `frontier-rules` produces byte-identical orders before and after the
   rule list refactor on every existing AI test scenario.
8. **Registered.** A world naming `clan-keeper` validates; the existing unknown-id rejection still holds.
9. **Never builds (round 4).** No clan files `build` over a 20-turn run; its seeded tier-1 hub clears
   clan barter with any trader holding a Trading Post, and nothing at `hostile`.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ai/ClanKeeperTests.cs` (new): 1–6, 8 on a synthetic clan fixture
  (`trade-foundation` `synthetic-graph` can seed clans, counterparties ask A4).
- `gk-core/tests/FusionRpg.Core.Tests/World/Ai/FrontierRulesTests.cs` and `WorldAiAcceptanceTests.cs`: 7, run
  and reported.
- Run `.\scripts\verify-change.ps1 -Paths <changed paths> -Session <id>`; `FrontierRulesPolicy.cs`
  changes, so the full suite once at module end.

## Hard edges

- **The ladder refactor** touches the one playing policy. It must be neutral (criterion 7) and lands as
  its own commit before the clan list is added, so a regression bisects to one change.

## Dependencies

| Consumes | From |
|---|---|
| the ladder and its rules | `world-map-program` `ai-commander` (built) |
| `ai-bidding`, `ai-logistics`, `ai-treaty-policy`, `SpendLimit` | this map |
| clan placement, policy id assignment, computed personality | `counterparties` `clan-seeding`, `need-vector` |
| last turn's production (income) | `counterparties` `clan-economy` (T-A7) |

| Exposes | To |
|---|---|
| `clan-keeper` policy id | `counterparties` `clan-seeding`, `empire-roster` |

## Boundaries

- **Always:** the contract by rule subset; needs from the one vector; the same layers as empires.
- **Ask first:** giving clans `Explore` or any rule that leaves their ground; a clan that can declare war.
- **Never:** per-clan scripts or authored cravings; clan petitions filed from here (that is
  `npc-story-events`).

## Design-gate checklist

```
[x] Subsystems: world map AI (ladder, policy catalog), counterparties (clans — consumed), tunables.
[~] Session boundary: docs-only under trade-network-idea-20260919; check exits 1 on crossings already
    recorded; this file is new.
[~] Read this session: as spec-trade-intel.md's list. NOT read: the npc-story-events petition-host spec.
[x] decisions.md: no lock covers clans; the kind's contract is the code comment and the ideal.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: FactionKindCatalog clan contract, FactionPolicies, WorldValidation,
    the ladder chain and Defend, StandFastPolicy, template seeding.
[x] Surrounding sections read: spec-ai-commander §Who gets which policy.
[x] No constraint claimed without a run: the ladder refactor's neutrality is a test to run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: none needed beyond the map.
[x] No population pinned: rule and step subsets are code-owned closed lists.
[x] No event-refreshed cache.
[x] No ordering-dependent criterion.
[x] No actor magnitude.
[x] No SOLID-violating path: one ladder class parameterised by a rule list, not a second policy.
[ ] Registry row for criterion 5 (no per-clan literal) owed with the change.
[x] Round 4 reconciliation (2026-09-19): seeded tier-1 hub, never builds, band blocks only at hostile.
```

# Spec: `legion-doctrine`

**Status: written against shipped code 2026-09-19.** Module id `legion-doctrine`, row 13 of the
[legion-build map](../legion-build-map.md) (wave 3; depends on `legion-owner-scope`; external `empire-seed`
exemplars). Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.1 (*"a signed modifier inside the
existing pricers — never a second pricer"*), prior art: one detachment per army.

## Objective

A legion holds at most one **doctrine**. Its combat half is a set of atoms bound through layer 5c. Its world
half is **one signed term inside the one pricer** that already exists for its `worldTradeoffKind`: march,
burn, sight or cargo. There is never a second pricer.

Success looks like: with no doctrine every pricer returns exactly today's value; a doctrine changes exactly
one pricer by a tuned term; switching withdraws the old atoms the same commit.

## Scope and non-goals

- **In:** doctrine state; `adopt-doctrine`/`drop-doctrine`; the `worldTradeoffKind` vocabulary; one term in
  each of four pricers; the contributor.
- **In (round 6 CQ2):** the doctrine's **goods upkeep** and its banked top-up (§3a) — the *"later reviewed
  addition"* the first draft deferred; the owner reviewed and added it on 2026-09-20.
- **Out:** doctrine seeds (`empire-seed`); magnitude scaling (5c reader); ~~upkeep goods (none in v1 — a later
  reviewed addition if wanted)~~ — superseded by CQ2, §3a. Also out: the four `world.*` channels a doctrine
  term looks like (`world.march.range`, `world.supply.burn`, `world.sight`, `world.carry.capacity`) —
  registering those is `world-derived`'s and rolling them up is `legion-power`'s (§3b).

## What already exists

| Pricer | Today | Evidence |
|---|---|---|
| march | the refill budget per stance, set in Snapshot | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:50-60`; refill at `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:456`; AI read at `gk-core/src/FusionRpg.Core/World/Ai/ReachMap.cs:37` |
| burn | `LegionSupply.Burn` | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:24-25` |
| sight | radius per stance | `gk-core/src/FusionRpg.Core/World/Intel/Visibility.cs:33-38,106-108` |
| cargo | weight/slot capacity per unit | `gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs:39-47`; read at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:102,106` |

Real gap: no doctrine anywhere.

## Design

### 1. State and commands

`WorldEntity.Doctrine` = the adopted doctrine seed id or null; hashed as a row only when set. `adopt-doctrine`
(replaces any current one) and `drop-doctrine`, resolved in Snapshot. No cost to adopt in v1; the
trade-off **is** the price.

### 2. The vocabulary

`WorldTradeoffKind { March, Burn, Sight, Cargo }` — the four values `empire-seed` validates
(`docs/architecture/empire-seed-map.md` §5.13, `legion-doctrine` row), pinned by a membership test with its reason. **Registry (round 4, owner Q12):** the members live in the one shared legion vocabulary registry, `data/seed/legion/_registry/vocab.v1.json` (`empire-seed/spec-legion-seed-contract.md` §5.2); this C# enum is validated against it at load, so there is one list, never a mirror plus a sync test.

### 3. One term per pricer

A single helper reads the term: `DoctrineTerm.For(legion, kind) → long` (per-mille, signed, 0 with no
doctrine or a doctrine of another kind), value from `legion.v1.json` (proposed; the file does not exist yet)
`doctrine.termMilli.{kind}` keyed by doctrine seed id. Each pricer applies it once, divide-last:

| Kind | Where | Form |
|---|---|---|
| march | `BudgetFor` gains the legion; `budget × (1000 + term) / 1000` | `LaneCost.cs:50` (signature), `TurnEngine.cs:456`, `ReachMap.cs:37` |
| burn | `Burn × (1000 + term) / 1000` | `LegionSupply.cs:24-25` |
| sight | radius + `term / 1000` lanes (whole lanes; term authored in thousandths of a lane) | `Visibility.cs:106-108` |
| cargo | capacity `× (1000 + term) / 1000` | `ScopedInventoryPolicy.cs:39-47`, via the Data reader |

A combined factor below zero is a load rejection of the tuning row, never a clamp.

### 3a. Goods upkeep, and the banked top-up (round 6 CQ2)

**Owner decision CQ2 (2026-09-20):** *"Legion equipment and doctrine upkeep may draw on banked goods when
local stock runs short — the same rule for the player and every AI, so no handicap."* It answers
`counterparties-map.md` CQ2 (an AI treasury with a perpetual faucet and only one-off sinks) with option (a),
naming *"doctrine goods upkeep"* as one of the two recurring, army-proportional sinks; `counterparties-map.md`
CX2 asked legion-build's agreement, and this section is it. §1's *"no cost to adopt in v1; the trade-off is
the price"* is unchanged — **adopting** is still free. What CQ2 adds is a **recurring** cost of holding one.

| Rule | Statement |
|---|---|
| Amount | `legion.v1.json` `doctrine.upkeepGoodsPerUnitPerTurn` per doctrine seed id × the legion's `Σ Count` — proportional to army size (P2), a per-turn rate, never a cap, and it keeps scaling with holdings |
| Which good | the doctrine seed's `upkeepGoods[]`, VALIDATED against the goods registry by `empire-seed` (`legion-seed-contract` — which goods, never how many, the same split as `forgeGoods[]`) |
| Where paid | the located stock of the sector the legion stands in, through `LocatedStockOps.Add` inside the phase that already walks legions for supply (`LegionSupply`'s burn step), so it is hashed state changed once, inside `Step` |
| Short locally | the shortfall is drawn from the **owner's banked store** of that good — the player's banked materials or an AI's treasury (round 5 X3) — through the one banked writer, `trade-foundation` `material-ledger`. Never a second writer, never `rpg_item_stock` (X4) |
| Short everywhere | the doctrine **lapses**: `Doctrine = null` with a `doctrine.lapsed` report line and the 5c container withdrawn in the same commit (the §4 switch path). Never a silent debt, never a clamp, never a free turn |
| Symmetry | nothing in the rule reads the owner's faction kind. The same test runs twice, player-owned and AI-owned, with the same result (principle 11 — no handicap) |

**This waits on the save-identity re-key (round 6 C3).** The banked arm writes a banked material store keyed
by the save identity `solid-enforcement` SE4.12–SE4.38 is re-keying, and *"`material-ledger` and the banking
work that needs it start after it finishes"*. **Stated default until then:** upkeep is paid from located stock
only, and a legion standing where its goods are short lapses — the mechanism is whole and honest without the
top-up, which lands in its own later change (the same one as `legion-equipment` §7a), recorded in
[landing-order.md](../trade-network/landing-order.md). No interim second writer.

### 3b. The four pricers and the six `world.*` channels (round 6 D2)

D2 names *"doctrine"* among the sources of the six world channels (`world.carry.capacity`,
`world.march.range`, `world.supply.burn`, `world.sight`, `world.hazard.resist`, `world.upkeep.discount`),
which compose in `ActorHub` and roll up the way `legion-power` does. This module's four terms are the same
four quantities by another name, so the rule is stated once, here, to keep one answer:

- **A doctrine contributes to a world channel as an ordinary Hub contribution** (the 5c container's atoms,
  §4), under its existing SourceId. It never computes a channel and never folds one per legion.
- **The roll-up is `legion-power`'s** `LegionWorldChannels` (`spec-legion-power.md` §6): Σ per unit for carry
  and burn, min for march and hazard, max for sight, and `world.upkeep.discount` applied per unit, divided
  last.
- **§3's four pricer terms stay exactly as written until `world-derived` registers the channels.** They are
  the *stated default* D2 asks for: one signed term inside the one existing pricer. When the channels
  register, each pricer reads the Hub channel at the same call site and `DoctrineTerm.For` becomes one
  contributor to it — not a parallel path kept alive beside it.

### 4. Combat half

`LegionBuffSources` gains `doctrine`: desired = `{ world-buff.legion-doctrine-{seedId} }` projected from the
seed's `combatFamilies[]`. Switching doctrine withdraws the old container in the same commit.

## Tunables

`legion.v1.json` (proposed; the file does not exist yet) `doctrine.termMilli` per doctrine seed id (signed
per-mille); `doctrine.upkeepGoodsPerUnitPerTurn` per doctrine seed id (`long`, goods per unit per turn, round
6 CQ2 — a rate, not a cap); `doctrine.bankedDrawPremiumMilli` (bounded ratio, default 1000‰ = no premium,
shared shape with `legion-equipment`). Combat magnitudes: `legion-seed.v1.json` (proposed; the file does not
exist yet).

## Numeric types

Terms `long` per-mille, products widened and `checked`, divided by 1000 last. Budgets stay in their `int`
per-mille frame after a checked narrowing.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Doctrine|FullyQualifiedName~MovementMath|FullyQualifiedName~Loam|FullyQualifiedName~Intel"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~LegionCargo"
```

## Structure

```
src/FusionRpg.Core/World/Legion/LegionDoctrine.cs     NEW       state rules, DoctrineTerm, contributor
gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs         MODIFIED  BudgetFor term
gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs         MODIFIED  Burn term
gk-core/src/FusionRpg.Core/World/Intel/Visibility.cs          MODIFIED  sight term
gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs  MODIFIED  cargo term
gk-core/src/FusionRpg.Core/World/Turn/{WorldCommand,WorldCommandAdmission,TurnEngine}.cs  MODIFIED  commands
```

## Testing strategy

- **Identity:** no doctrine → each of the four pricers returns today's value for every input (property).
- **Exactly one:** a doctrine of kind *k* changes pricer *k* only; the other three are unchanged.
- **Upkeep (round 6 CQ2):** the per-turn amount is `perUnit × Σ Count`, one divide where a ratio applies; a
  short sector draws the remainder from the owner's banked store through `material-ledger` and nothing else;
  short in both lapses the doctrine and withdraws its 5c container in the same commit; the player-owned and
  AI-owned cases are the same test with the owner swapped.
- **Switch:** old combat container withdrawn, new bound, same commit.
- `WorldTradeoffKind` pinned with reason.
- A tuning row making a factor negative fails load.

## Boundaries

- **Always:** read the term through `DoctrineTerm.For`.
- **Ask first:** a doctrine touching two pricers; adopt costs.
- **Never:** a doctrine-specific pricer; a clamp.

## Success criteria

1. Four pricers each gain exactly one term, zero by default.
2. One doctrine, one pricer, one tuned term.
3. Combat half through 5c.

## Interface exposed to dependents

`WorldTradeoffKind` (mirrored by `empire-seed`); `DoctrineTerm.For` (the FE legion card).

## Hard edges

**Wave and ruleset bump (round 6 C1).** This module is legion-build **wave 3**, and it grants a player-facing
feature (doctrines, their pricer terms and now their goods upkeep), so it does **not** claim "no bump": it
rides **wave 3's single `RulesetVersion` bump**, taken at landing (never pre-assigned) and recorded with the
wave's one capability flag in [landing-order.md](../trade-network/landing-order.md). ~~No `RulesetVersion`
bump: the state exists only when adopted and the commands are new (`TurnEngine.cs:134-140`) … Corrects map
§4's bump list.~~ Hashing stays default-suppressed (a `doctrine` row only when adopted), which keeps the
*re-bless* small; the bump is what stops a world stamped before wave 3 gaining the feature mid-life
(`trade-foundation/spec-world-stamp.md` §2). Signature change of `BudgetFor` touches its three callers.

**Banked upkeep draw (CQ2) waits on the save-identity re-key (C3)** — §3a; until then upkeep is located-stock
only and an unpayable doctrine lapses.

## Dependencies

`legion-owner-scope`; external `empire-seed` exemplars.

## Design-gate checklist

```
[x] Subsystems: world movement, supply, intel, cargo pricers; 5c.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: map, ideal, empire-seed-map legion rows. NOT read: tunables-ssot.md.
[x] decisions.md checked: no lock on pricers.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: each pricer and its callers.
[x] Read the surrounding section of every rule quoted.
[~] No suite run.
[x] No §2 invariant contradicted: no second pricer, no cap.
[~] Corrections propagated (map §10).
[x] Pinned: WorldTradeoffKind (4) closed with reason.
[x] No cache.
[x] No ordering assumption.
[x] Combat half via 5c reader.
[x] No parallel path.
[x] No new rule needing a registry row.
```

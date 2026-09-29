# Spec: `legion-equipment`

**Status: written against shipped code 2026-09-19.** Module id `legion-equipment`, row 14 of the
[legion-build map](../legion-build-map.md) (wave 3; depends on `member-stack`, `general-member-hub`;
external `trade-network` `sector-yield` (located stock; `sector-storage` superseded by round 4), `empire-seed`
legion-equipment seeds). Owner decision **L5** and [legion-build-ideal.md](../legion-build-ideal.md) §6.7:
fixed stats, atom effects only, **no sets, no sockets, no rolls**, weaker than unique items, a counted stock.
**Round 4 (2026-09-19), binding** ([decisions-round-4.md](../trade-network/decisions-round-4.md) §B): legion
equipment is produced only where a sector has the **Workshop → Armory → Foundry** building, and the tier it
has reached is the best piece tier that sector can produce. §7 below adds the production rule this spec and
`sector-yield` each left to the other.

## Objective

General stacks get their own equipment scope. A **legion-equipment piece** is a catalog entry with a fixed
tier and fixed stats, identical for every player; pieces are a counted stock in a sector's storage; fitting
a stack of *N* in a slot consumes *N* pieces where the legion stands; casualties consume the pieces their
units wore. A fitted stack's pieces reach `ActorHub` through `general-member-hub`'s one join, under a SourceId
that can never be confused with a unique item's.

Success looks like: a piece's stats are the same for every player and every read; fitting consumes exactly
the fitted count; no unique-item rule applies to this scope; every contribution names its slot and piece.

## Scope and non-goals

- **In:** the legion slot vocabulary (`empire-seed` waits on it, `docs/architecture/empire-seed-map.md` §5.13, *Real gap*);
  the container kind for pieces; fitted state on a member; fit/unfit; casualty consumption; the reader and
  SourceId; the registry row obligation.
- **In (round 4):** the production rule — which building produces a piece, at which tier, from which inputs
  (§7). `sector-yield`'s `legion-equipment-stock` says *"production recipes and the building that runs them"*
  are `legion-build`'s (`docs/architecture/trade-network/sector-yield/spec-legion-equipment-stock.md:22-25`),
  and this spec's first draft said the reverse; nobody owned it. Claimed here.
- **In (round 6):** the banked top-up when the sector warehouse is short (CQ2, §7a) — the one arm that waits
  on the save-identity re-key (C3); the statement that any `world.*` contribution a piece makes rolls up
  through `legion-power` and never here (D2).
- **Out:** resolving piece stats from seed + bands (`empire-seed` `legion-bands`: *"a legion-equipment
  piece's resolved budget is strictly below a unique item's at the same tier"*, `empire-seed-map.md` §5.14, *Acceptance*);
  the building row itself (`empire-seed` `trade-structure-rows`: the `workshop` row, re-roled to `Refine`, tiers
  Workshop → Armory → Foundry); how a located stock is held, capped and moved (`sector-yield`
  `legion-equipment-stock`, `located-stock`); recipes from world events (later); the tier-upgrade verb and the tier
  read (`trade-foundation` `sector-features`).

## Layer answers

Layer **3 (equipment), stack scope** — a new scope and carrier on an existing layer, not a new layer
(ideal §6.7) · scope: one member row (a stack) · lifetime: while fitted · carrier: a `legion-gear.{pieceId}`
container · SourceId `legion-equip:{slot}:{pieceId}`, distinct from `equip:{role}:{itemRef}`
(`docs/architecture/actor-hub-ssot.md` §8.1).

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | One ownership root **for items**: stock rows keyed `(player_id, container_id)` with `qty` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:102-108`; `decisions.md` *Scoped inventory hierarchy SSOT* (`docs/architecture/decisions.md:47`) |
| Specified (not built) | Legion pieces are a **located good** in the sector warehouse (`LocatedGoodCatalog` kind `LegionPiece`), changed only through `LocatedStockOps.Add`, credited by `LocatedProduction.Credit` | `docs/architecture/trade-network/sector-yield/spec-legion-equipment-stock.md` §Design; `legion-build-ideal.md` §6.7 (*"Pieces are located goods"*) |
| Built | Container prefixes are a closed, validated list | `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerValidator.cs:35`; parse at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs:565-580` |
| Built | `BoundDerivedAtom` carries its SourceId into battle via `BoundAtoms` | `gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/AtomDerivedSubsystem.cs:91-92`; `gk-core/src/FusionRpg.Core/Battle/BattleHubInputs.cs:21` |
| Built — **not applicable here** (audit 2026-09-20) | Gate-before-Step / spend-after-Step for a **Data-held** resource a Core command consumes (relics). Located stock is hashed state, so this module never uses it (§4) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:544,609-611` |
| Constraint | Stacks never get per-unit item rows | `docs/architecture/deployment-hierarchy-ideal.md:175` |
| Real gap | All of it | — |

## Design

### 1. Slot vocabulary — closed, disjoint from `ItemRole`

**Registry (round 4, owner Q12):** the members live in the one shared legion vocabulary registry, `data/seed/legion/_registry/vocab.v1.json` (`empire-seed/spec-legion-seed-contract.md` §5.2); this C# enum is validated against it at load, so there is one list, never a mirror plus a sync test.

`LegionGearSlot { Weapon, Armour, Kit }`. Three slots for a rank-and-file stack; pinned with the reason
("legion gear is cheap and common — three slots, never the unique paperdoll"). A test asserts no name
overlaps `ItemRole` (`gk-core/src/FusionRpg.Core/Items/ItemRole.cs`), and the list never contains `standard`
(map X8).

### 2. The piece carrier

`ContainerKind.LegionGear`, prefix `legion-gear` — a closed vocabulary widening (`ContainerValidator.cs:35`
gains it). A piece's container holds only `stat.derived` atoms with **fixed** values; the validator refuses a
pool, a rarity, a roll range, a socket or a set field on this kind. The rows are projected deterministically
from the seed and `legion-seed.v1.json` (proposed; the file does not exist yet) bands; identical for every
player.

### 3. Fitted state — hashed, on the member

`WorldEntityMember.Gear` — per slot `(PieceId, Qty)`, hashed only when non-empty. `Qty ≤ Count` always.
Gear contributes **only when `Qty == Count`** (the whole stack wears it); an under-fitted stack's gear is
inert until topped up — no partial-stack arithmetic.

### 4. Fit and unfit

`fit-gear { EntityId, MemberId, Slot, PieceId }` fits `Count − Qty` more pieces (all or nothing — a stack short
of pieces in the warehouse is refused `gear.stock-short`, nothing fitted). `unfit-gear` returns `Qty` pieces to
the warehouse where the legion stands. **The stock is `sector-yield`'s located stock, not `rpg_item_stock`**
(round 5 X4, binding: *"legion equipment storage — the hashed sector warehouse (sector-yield located
stock), never `rpg_item_stock`"*; first decided in the round-4 reconciliation: pieces are a located good, so they share the warehouse, trade and flow like every
good; the item ownership root in `decisions.md` *Scoped inventory hierarchy SSOT* governs item instances, and
the warehouse axis is deliberately a third axis beside it, `trade-network-map.md` §4). **The check and the
spend both run inside `Step` (corrected by the 2026-09-20 audit).** The first draft used the relic pattern —
a Data gate before `Step` and a Data spend after it (`RpgStore.WorldTurns.cs:544`, `:609-611`). That
pattern is right for relics, which live in Data-side tables outside the world hash; it is wrong here,
because the located stock is **hashed world state** (`WorldSector.LocatedStock`, canonical row
`sector-goods`) and `LocatedStockOps.Add` *"is called only from phases inside `Step`. Data-side code
constructs the field on load and never mutates it"* (`trade-network/sector-yield/spec-located-stock.md` §2). A
Data-side spend would be a side-channel write to hashed state that replay never reproduces — the defect
`warden-mortality-ideal.md` §The shape rules out. So `fit-gear`/`unfit-gear` resolve in Snapshot: the
resolver reads `LocatedStock.Of(pieceId)` of the sector the legion stands in, refuses short stock with
`gear.stock-short` and writes nothing, and on acceptance moves the pieces through `LocatedStockOps.Add`
(a negative delta on fit, a positive one on unfit, each with its `ledger-keys` fact kind) and updates
`Gear` in the same resolver call. The legion must stand in an own sector (`gear.not-home`). ~~"an own sector with a warehouse"~~ — superseded by round 5 A2: every held
sector has a small **base yard capacity** (one `sector-yield` tunable) and the Storehouse ladder only widens
it, so every own sector has a warehouse; a full one refuses `unfit-gear` through `sector-yield`'s capacity
rule, never through a missing building.

### 5. Casualties consume

When `Count` falls (battle, starvation), `Qty` falls to `min(Qty, Count)` in the same place `member-stack`
applies `FromPool` — the dead units' pieces are gone. A sink that scales with war (ideal default).

### 6. Reader and SourceId

`LegionGearAtomsUnlocked(member)` → for each slot with `Qty == Count`, the piece container's atoms as
`BoundDerivedAtom`s, scaled per member by `ContentScale` exactly like the 5c reader, SourceId
`ContributionSourceIds.LegionEquip(slot, pieceId)` = `legion-equip:{slot}:{pieceId}`, `FictionLabel`
`Legion gear · {slot} ({pieceId})`. Called by `general-member-hub`'s `LegionMemberAtoms`, the one join.

### 7. Production — the Workshop chain (round 4)

`produce-gear { SectorId, PieceId, Qty }`, resolved in the `Production` phase:

| Check (in order, each a named drop before any write) | Reason |
|---|---|
| `SectorFeatures.TierOf(sector, legion-equipment)` is 0 (`trade-foundation/spec-sector-features.md` §5; the building row is `empire-seed` `trade-structure-rows` §5.1) | `gear.no-workshop` |
| The piece's `tierBand` rung needs a higher Workshop-chain tier than `TierOf` returns (`empire-seed` `legion-bands` §3 item 3: rung *i* needs tier ≥ *i*) | `gear.tier-too-high` |
| The recipe goods (`recipeGoods[]` from the seed × `legion.v1.json` `equipment.recipeQtyPerTier`) are short in the sector warehouse (`LocatedStock.Of`, read **inside** the `Production` phase — audit 2026-09-20: the warehouse is hashed state, so there is no Data gate) **and the banked top-up of §7a cannot cover the shortfall** | `gear.inputs-short` |

Accepted: the inputs leave through `LocatedStockOps.Add` and the pieces are credited with
`LocatedProduction.Credit`, so a full warehouse halts production exactly as it halts any yield
(`sector-yield` `production-halt`). A building produces at most `legion.v1.json`
`equipment.batchPerTurnByTier[tier]` pieces per turn — a **per-turn rate**, a structural limit stated as such in
the code comment (umbrella invariant 12), never a lifetime cap.

### 7a. A short warehouse may draw on banked goods (round 6 CQ2)

**Owner decision CQ2 (2026-09-20):** *"Legion equipment and doctrine upkeep may draw on banked goods when
local stock runs short — the same rule for the player and every AI, so no handicap."* It answers
`counterparties-map.md` CQ2 (a mature AI treasury had a perpetual faucet and only one-off sinks) by reusing a
sink this module already owns, rather than inventing an AI-only upkeep. `counterparties-map.md` CX2 asked
legion-build's agreement; this section is it.

**The rule, one rule for every faction.** When an accepted `produce-gear` (and the casualty replacement that
follows a battle, §5) finds the sector warehouse short of a recipe good, the shortfall is drawn from the
**owner's banked store of that good** — the player's banked materials or an AI's treasury, whichever the
owning faction has (`counterparties` `empire-treasury` is the AI side, round 5 X3) — and only then is the
order refused:

1. Take what the sector warehouse holds through `LocatedStockOps.Add` (a negative delta, as today).
2. Draw the remainder from the owner's banked store through the **one** banked writer,
   `trade-foundation` `material-ledger` (its `ledger-keys` fact kind for a legion-goods draw). Never a second
   writer, never `rpg_item_stock` (round 5 X4).
3. If the banked store is also short, nothing is written and the order drops `gear.inputs-short` (§7).

Properties this keeps: **symmetric** (principle 11 — no handicap, and nothing in the rule reads which faction
kind the owner is), **recurring and proportional to army size** (pieces are consumed by casualties, so the
draw scales with war, not with a balance), **never a clamp** (short is a refusal), and **no new faucet** — it
is a sink with a second source, not a source.

**This waits on the save-identity re-key (round 6 C3).** *"Banking waits on the save-identity re-key —
save-identity is being built now; `material-ledger` and the banking work that needs it start after it
finishes."* Step 2 is banking work: it writes a banked material store keyed by the save identity that
`solid-enforcement` SE4.12–SE4.38 is re-keying (`trade-foundation/spec-material-ledger.md`; global audit C3).
So:

- **Stated default until then:** `produce-gear` reads **located stock only** and refuses `gear.inputs-short`
  exactly as §7 says. The module ships whole; the top-up is the one arm that lands later.
- The top-up arm lands in its own change **after** `material-ledger`, and it is the same change that closes
  `counterparties` CQ2's scoped P1 assertion. Landing order in
  [landing-order.md](../trade-network/landing-order.md).
- No interim path: the draw never goes through a second writer "until the ledger is ready". That is the
  defect the single-writer rule exists for.

**Tunable:** none new — the quantity is already `equipment.recipeQtyPerTier`. Whether a banked draw costs a
premium over local stock is a balance question with an honest default of **none** (1000‰), published as
`legion.v1.json` `equipment.bankedDrawPremiumMilli` so a balance pass can change it without a rebuild
(tunables-ssot).

**No recipe consumes a world stock** (answers `exchange-map.md` ask E-A6): `recipeGoods[]` is VALIDATED against
the goods registry, `MaterialCatalog.All` in v1 (`empire-seed/spec-legion-seed-contract.md` §5.1), whose 27
issuable ids are shards, substrates, essences and catalysts
(`gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:60-64`) — no `rubble`, `ironwork`, `loam` or
`recruit`. Pieces therefore trade as ordinary located goods, not `world-barter-only`; a recipe that named a
world stock would be a seed-contract rejection.

## Tunables

Owned here (`legion.v1.json`, proposed; the file does not exist yet — mechanics, owner Q12):
`equipment.recipeQtyPerTier`, `equipment.batchPerTurnByTier`, `equipment.bankedDrawPremiumMilli` (round 6
CQ2, default 1000‰ = no premium; a bounded ratio, divided last). **Not** owned: the budget share and the tier
ladder are `legion-seed.v1.json`'s (proposed; the file does not exist yet — seed magnitudes, Q12).

## Numeric types

`Qty`, stock quantities `long`, `checked`.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LegionGear|FullyQualifiedName~ContainerValidator"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SectorStorage|FullyQualifiedName~WorldTurn"
python gk-core/scripts/guard-actor-hub.py
```

## Structure

```
gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs, ContainerValidator.cs   MODIFIED  LegionGear kind + no-roll rule
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs                           MODIFIED  parse arm
gk-core/src/FusionRpg.Core/World/WorldState.cs                                     MODIFIED  member Gear
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs                                 MODIFIED  default-suppressed `gear` row (added 2026-09-20, R-19.5)
src/FusionRpg.Core/World/Legion/LegionGear.cs                              NEW       slots, fit rules, casualty rule
gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs                  MODIFIED  LegionEquip + label
src/FusionRpg.Data/Sqlite/RpgStore.LegionGear.cs                           NEW       reader only (the stock moves inside Step, §4)
src/FusionRpg.Core/World/Legion/LegionGearProduction.cs                    NEW       produce-gear checks (§7)
```

## Testing strategy

- Two loads, two players: identical piece **definitions** (atoms and pin values). A piece's *contribution*
  is scaled once by the wearer's Θ in the reader (§6), like every content-scaled magnitude — so "identical
  for every read" (map §5.14) means the definition, not the scaled amount (audit 2026-09-20 wording fix).
- (Audit 2026-09-20) Fit, unfit and production change the sector's located stock only inside `Step`: a
  replay of a turn with a `fit-gear` reproduces the stored hash, and a source scan finds no Data-side
  write to `LocatedStock` in this module.
- Validator refuses every roll/set/socket/pool shape on `legion-gear`.
- Fit consumes exactly `Count − Qty`; short stock refuses with nothing written; unfit credits `Qty`.
- Casualties: `Count` 40 → 25 leaves `Qty` 25, pieces gone.
- Production: no Workshop-chain building → `gear.no-workshop`; rung above the building's tier →
  `gear.tier-too-high`; short inputs → `gear.inputs-short` with nothing written; a full warehouse halts
  output; a recipe naming a world stock is refused by the seed contract (fixture).
- Under-fitted stack contributes nothing; fully fitted contributes each slot once, SourceId named.
- Slot vocabulary pinned and disjoint from `ItemRole`.

## Boundaries

- **Always:** one stock root; one join; fixed values.
- **Ask first:** partial-stack gear; wear over time; capture of a routed legion's gear.
- **Never:** per-unit item rows; sets, sockets, rolls, rarity count bands on this scope.

## Success criteria

1. Fixed, player-identical pieces; exact fit/unfit/casualty arithmetic.
2. No unique-item rule applies, asserted.
3. Contributions attributed `legion-equip:`.
4. (Round 6 CQ2) A short warehouse draws the shortfall from the owner's banked store through
   `material-ledger` and nothing else, identically for a player-owned and an AI-owned sector (the same test
   run twice, only the owner changed); both short is a refusal with nothing written.
5. (Round 6 D2) Where a piece contributes to a `world.*` channel (carry, march, burn, sight, hazard,
   upkeep), it does so as an ordinary Hub contribution under its `legion-equip:` SourceId — the roll-up is
   `legion-power`'s `LegionWorldChannels` (§6 there) and this module computes no channel itself.

## Interface exposed to dependents

`LegionGearSlot` (mirrored by `empire-seed`); the reader (called by `general-member-hub`).

## Hard edges

- **Registry row owed (P4, P6)** in `empire-resource-ssot.md` §3 in the implementing change — the
  bottleneck is goods × building time; the two sinks are fitting and trade. Not made by this spec session.
- **Closed vocabularies widened:** `ContainerKind` (+`LegionGear`), and `effect-atom/definitions.md` §1's
  `container_id` grammar, already stale (6 prefixes listed vs 14 accepted at `ContainerValidator.cs:35`),
  must move in the same change. `actor-hub-ssot.md` §8.1 gains the `legion-equip:` row.
- **Wave and ruleset bump (round 6 C1).** This module is legion-build **wave 3**, and it grants a
  player-facing feature (legion equipment, its production and the Workshop gate), so it does **not** claim
  "no bump": it rides **wave 3's single `RulesetVersion` bump**, taken at landing (never pre-assigned) and
  recorded with the wave's one capability flag in
  [landing-order.md](../trade-network/landing-order.md). ~~No `RulesetVersion` bump: gear exists only when
  fitted by a new command.~~ Hashing stays default-suppressed (gear rows only for fitted stacks), which is
  what keeps the *re-bless* small — but a world stamped before wave 3 never gains the feature mid-life, and
  that is what the bump is for (`trade-foundation/spec-world-stamp.md` §2).
- **Banked draw (round 6 CQ2) waits on the save-identity re-key (C3)** — §7a; the top-up arm is a later
  change, and the module ships on located stock only until then.
- **The feature gate is read, never re-implemented (round 6 S1).** A feature building counts for **nobody**
  until one faction owns both its sector and its slot; that rule lives once in `trade-foundation`
  `sector-features` and reaches this module only through `SectorFeatures.TierOf` / `FactionTier` (§7). This
  module never compares a slot owner with a sector owner itself.

## Dependencies

`member-stack`, `general-member-hub`; external `sector-yield` (`located-stock`, `production-halt`,
`legion-equipment-stock`), `empire-seed` (`legion-bands`, `legion-seed-contract`, `trade-structure-rows`); `trade-foundation` `sector-features`
(`SectorFeatures.TierOf`, and the upgrade verb for any tier above Workshop).

## Design-gate checklist

```
[x] Subsystems: equipment layer (stack scope), atom layer (container kind), economy (a new quantity),
    world legions, stats.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: ideal §6.7, empire-seed-map legion rows, definitions.md §0-§6, actor-hub-ssot §8.1.
    NOT read: item program docs (ssot-inventory.md, spec-equip-and-paperdoll.md), empire-resource-ssot §4-§5.
[x] decisions.md checked: Scoped inventory hierarchy SSOT (one ownership root).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: stock table, sector storage, container prefix list, BoundDerivedAtom, gate/spend.
[x] Read the surrounding section of every rule quoted.
[~] No suite run.
[x] No §2 invariant contradicted.
[~] Corrections propagated: registry and grammar rows listed as owed.
[x] Pinned: LegionGearSlot (3) closed with reason.
[x] No cache.
[x] No ordering assumption.
[x] Contributes via ActorHub (AtomDerivedSubsystem) with SourceId legion-equip:...
[x] No parallel path: one stock root, one join.
[ ] Registry row owed: "legion-gear containers carry no roll" — enforced by the validator rule.
[x] Round 5 (2026-09-20): X4 confirmed (hashed sector warehouse, never rpg_item_stock); A2 removes
    the "with a warehouse" condition (base yard capacity in every held sector); X1 gate already
    SectorFeatures.TierOf(legion-equipment).
```

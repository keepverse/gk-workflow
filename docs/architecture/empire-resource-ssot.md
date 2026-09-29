# Empire resource SSOT — every quantity the player or a world holds

**Status: registry, 2026-09-16.** Owner ruling P10 of the doc reconciliation: *"empire have a lot of
resource, not only three"*. This file is the one list of every non-actor quantity in the game — who
holds it, whether it survives a world, where it comes from and where it goes. It replaces the
**count** in [empire-economy-ssot.md](empire-economy-ssot.md) §2 ("three stocks, and only three");
every **rule** that section and [economy-principles.md](economy-principles.md) state still holds.

Actor pools (`hp` `stamina` `hunger` `spirit` `qi` `poise`) are a different scope and live in
[resource-hub-ssot.md](resource-hub-ssot.md). Nothing here is ever an actor pool.

---

## 1. Why this file exists

`empire-economy-ssot.md` ran the P4 test on 2026-08-23 over five buildings, all costing loam, and
concluded three stocks. Every later addition passed its own P4 test in its own program and never came
back to update that count:

| Date | Program | Added | Evidence |
|---|---|---|---|
| 2026-08-22 | items lane I9 | shard, substrate, catalyst material classes | [item/ssot-materials-crafting.md](item/ssot-materials-crafting.md) §3.1 · `Items/Materials/MaterialCatalog.cs` |
| 2026-09-03 | world-map `sector-development` | per-sector recruit accrual | [world/spec-sector-development.md](world/spec-sector-development.md) §1 · `WorldState.cs` `RecruitStock` |
| 2026-09-04 | base-defense | `rubble`, `ironwork` ("from three stocks to five", decision 16) | [base-defense-ideal.md](base-defense-ideal.md) decisions 16–18, 28 · `WorldState.cs` `RubbleStock`/`IronworkStock` |
| 2026-09-13 | empire-development | relics (items) fund wonders | [decisions.md](decisions.md) *Loam relics and wonders SSOT* |

Meanwhile about fifteen ideal and spec documents kept citing *"no fourth stock"* as a design gate. A
fixed count cannot survive a growing empire; a registry with a widening rule can.

## 2. Classes

A quantity belongs to exactly one class. The class decides which economy rules apply.

| Class | Meaning | Survives a world | Rules that apply |
|---|---|---|---|
| **Wallet** | One fungible player balance | Yes | P1, P2, P5, P6 |
| **Material** | A player-held, id-typed stack; ids inside a family are not interchangeable | Yes (banked) | P1, P4, P5, P6 |
| **World stock** | Held per sector, spent per connected component or per sector | No — map-scoped; stays with its world (worlds persist, world-continuity 2026-09-19) and crosses only as cargo (rule 5b) | P1, P2, P3, P4, P5, P6; never feeds fusion or crafting |
| **Accrual meter** | Progress toward one action; spent only by that action | No | P1; exempt from P4/P6 because it buys exactly one thing by design and is never traded |
| **Battle budget** | Seeded from world stock at battle start, spent inside the board, reconciled spend-only | No — dies with the battle | Never pays out more than it was seeded plus board income |
| **Item** | An individual object or item stack (`rpg_item` / `rpg_item_stock`) | Per item rules | Owned by the item SSOTs, not here; listed only where a resource cost consumes one |

## 3. The registry

| Id / family | Class | Held by | Faucets | Sinks | Conversions | Owner | Code |
|---|---|---|---|---|---|---|---|
| **souls** | Wallet | Player | Lawn kills and victories, expeditions; soul conduit yields (designed, `empire-economy-ssot.md` §5) | Summon, contracts/tribute, patron switch, respec, craft fees, discard tax | None | creature program · [spec-soul-economy.md](creatures/spec-soul-economy.md) | `rpg_soul_ledger` |
| **essence.{element}** ×6 | Material | Player | Expeditions, salvage, drops | Fusion (element-matched), crafting direction; compound building costs (designed, `empire-economy-ssot.md` §2) | None | [ssot-materials-crafting.md](item/ssot-materials-crafting.md) | `CreatureMaterialCatalog` · `rpg_creature_materials` |
| **shard.{rung}** ×10 | Material | Player | Salvage, drops, expeditions | Rarity ceiling on crafting and fusion | Recipe-gated only | items I9 | `CreatureMaterialCatalog` (`CreatureRarityLadder`) |
| **substrate.{frame}.{grade}** | Material | Player | Salvage, drops | Crafting body | None | items I9 | `MaterialCatalog` |
| **catalyst.{forge,temper,flux}** | Material | Player | Drops, salvage | Craft/socket · enhance/elevate · reroll | None | items I9 | `MaterialCatalog` · `CostClassMatrix` |
| **loam** | World stock | Sector (spent per component) | Rootbeds, wells and other `LoamSource` structures; wonders' generation-rate effect (spec'd) | Upkeep, construction, marching out of supply, farming the Unmade | **Never traded or converted — only moved** | [empire-economy-ssot.md](empire-economy-ssot.md) · [loam-map.md](loam-map.md) | `WorldSector.LoamStock` |
| **rubble** | World stock | Sector | `material-seam` slots, board income in a siege | Construction (`ConstructRubbleCost`), refining; wonder build cost (spec'd) | → ironwork, lossy and gated (P5) | base-defense `siege-construction` | `WorldSector.RubbleStock` · `SiegeConstruction` |
| **ironwork** | World stock | Sector | Refined from rubble, `shard-vein` slots, board income | Construction (`ConstructIronworkCost`); wonder build cost (spec'd) | ← rubble only | base-defense `siege-construction` | `WorldSector.IronworkStock` |
| **recruit** | Accrual meter | Sector | Weekly pulse on held sectors with a Seat; a cleared lair multiplies it | `raise` (founds a legion) | None | world-map `sector-development` | `WorldSector.RecruitStock` |
| **free empire respec** | Accrual meter | Empire, `(SaveId, EmpireId)`; survives a world | One grant of `freeRespecsPerEmpireLevel` per empire level (`empire-level`) | One species (empire) respec, at the player's choice instead of souls. Never a unique or commander respec (ruling R18) | None; never traded | `empire-progression` · [spec-respec-free-counter.md](empire-progression/spec-respec-free-counter.md) | `rpg_empire_free_respec_ledger` |
| **siege depot** | Battle budget | Side, one battle | Seeded from the sector's loam/rubble/ironwork; board node income | In-battle construction | Reconciled back spend-only | base-defense `siege-economy` | `Battle/Siege/BoardEconomy.cs` `SiegeDepot` |
| **relic** | Item | Player / legion cargo / sector storage | Rolled drops | Wonder build cost | None | empire-development `loam-relics-wonders` | `DropEntryKind.Relic` (spec'd; see its map) |

A row is added by the change that ships the quantity. A spec'd but unshipped quantity may be listed with
its program and "spec'd" in the Code column, never with invented fields.

## 4. Rules — unchanged, restated so the count is not mistaken for the rule

1. **No count ceiling — a gate instead.** A new wallet, material family or world stock must pass
   **P4** (at least one real cost is a bottleneck pair) and **P6** (at least two competing sinks) in the
   change that adds it, and must land a row in §3 in that same change. *"No fourth stock"* in older
   documents means this gate, not the number three.
2. **Every faucet names its sink** in the same change (**P1**). Territorial income needs territorial
   upkeep (**P2**).
3. **Conversions are lossy, rate-capped or gated** (**P5**). The only shipped conversion is
   rubble → ironwork.
4. **Loam is never traded or converted.** A world battle never pays loam; destroying a building never
   refunds it ([empire-economy-ssot.md](empire-economy-ssot.md) §7a, §8).
5. **World stocks never feed fusion, crafting or any account-scoped path.** They are **map-scoped and
   never auto-bank**: they stay with the world that made them, which no longer ends — it develops,
   hibernates, idles or falls ([world-continuity-ideal.md](world-continuity-ideal.md) §6.1–§6.2;
   amends base-defense decision 18's *"die with the map"*). **Wallets and materials bank** across worlds.
5b. **World stocks cross worlds only as cargo.** Rubble and ironwork may leave a world only as legion
   cargo on an advance, through the bounded single-transaction cargo model — a move, never a copy.
   Loam never crosses (rule 4); recruits never cross. (world-continuity `advance-carry`,
   [world-continuity-map.md](world-continuity-map.md).)
6. **Headline rows, not ids, are what P7 counts.** Each surface shows 3–4 headline rows, grouping
   families the way six essences are one row. Player surfaces: souls · essence · materials. World
   surfaces: loam · construction (rubble, ironwork) · recruits.
7. **No stamina gate.** No quantity here gates whether the player may play.

## 5. Widening — a quantity is not finished until its row lands

The same rule the actor-pool and status registries use. A module that adds, splits, retires or
re-scopes a quantity is not done until §3 moves with it, and until any count it states elsewhere is
removed in favour of a link here.

Known upcoming rows, owned by their programs: legion cargo and sector item storage
(`scoped-inventory`), the relic row's final code column (`loam-relics-wonders`), species materials
(`species-gear-chain`).

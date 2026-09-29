# Trade-network family — round-4 owner decisions (2026-09-19)

**Status:** binding owner decisions, recorded 2026-09-19 after the Wave 2 spec pass. They apply to
every spec under `docs/architecture/trade-network/**`, `docs/architecture/world-continuity/**`,
`docs/architecture/legion-build/**` and `docs/architecture/empire-seed/**`. Where a spec disagrees,
this register wins and the spec is corrected.

## B. Buildings unlock features (new cross-cutting principle)

Owner: *"To unlock a feature in a sector, we should have the correct building. This is strategy empire
building, so we should have specific buildings for feature unlock."*

**Rule:** every trade and logistics feature in a sector is unlocked by a specific building kind. Higher
tiers widen the feature. Tiers are **`variants` of one structure row** (seedsmith generates the tier
variants deterministically); a tier is never a separate building and never a separate row. A feature
with no unlocking building in the sector is not available there.

| Feature | Building kind (tiers, low → high) | What each tier unlocks |
|---|---|---|
| Storage | Storehouse → Warehouse → Granary Complex | The warehouse capacity axis; each tier widens it |
| Banking | Counting House → Treasury → Vault | T1 makes the sector a **bank point**; T2+ adds the per-good hold and faster banking |
| Trade | Trading Post → Market → Exchange → Grand Exchange | T1 clan barter; T2 empire market orders; T3 preferential treaties and blocs; T4 cross-world routes |
| Caravans | Caravan Yard → Convoy Depot | T1 legions load and unload goods; T2 more crew, more range |
| Cross-world | Rift Anchor | A cross-world route end; needs a Grand Exchange in the same world |
| Diplomacy | Embassy → Consulate | T1 treaties with an empire; T2 blocs and embargo leverage (clans need no embassy) |
| Legion equipment | Workshop → Armory → Foundry | The tier is the best legion-equipment tier the sector can produce |

Consequences, applied by this round:
- **Bank point** is the Counting House building (replaces the earlier "capability granted by default on
  the Vault slot"). The `bank` structure role keeps its meaning (a currency source).
- **Clan trade at world start** opens by building a Trading Post; the relation band still sets the
  spread and blocks trade only at `hostile`.
- **The first-throttle answer** ("no path to a bank point") is a one-click "build a Counting House".
- **The home hub** keeps stock to sell through the Treasury tier's per-good hold (default: keep what
  open sell orders need).
- Recruit, train and hire buildings are **not** part of this program — see U below.

## Q. Answers to the Wave 2 open questions

| # | Question | Decision |
|---|---|---|
| Q1 | No clan trade at world start | Build a Trading Post (B above). The band sets the spread; only `hostile` blocks |
| Q2 | The home hub has nothing to sell | A per-good hold in the banking policy, unlocked by the Treasury tier |
| Q3 | First throttle has no one-click answer | "Build a Counting House" |
| Q4 | Never-peace scope | The dominant enemy empire never makes peace **with the player only**; it may treat with rivals and clans |
| Q5 | Where the first clan goes | **Both shipped templates** get a clan (plus the rival already decided for `two-hearths` v2) |
| Q6 | Recruitment pool | The raising faction's **own side** plus the sector's species pool |
| Q7 | Essence faucet and sink scale | The fusion essence cost scales by the fused creature's level through the power ladder (needs the creature program's agreement in the building change) |
| Q8 | Realms power axis | Counts **worlds held** (not fallen) |
| Q9 | Warden strength in contests | **Power roll-up** — P below |
| Q10 | System-issued world commands | One shared path, built in **trade-foundation** |
| Q11 | Income parity | Owned by **sector-yield** |
| Q12 | Legion tuning (two proposed tuning files; each does not exist yet) | Seed magnitudes (tiers, the weaker budget share) in empire-seed's `legion-seed.v1.json`; mechanics numbers in legion-build's `legion.v1.json`; **one shared legion vocabulary registry** both read |

## P. Power roll-up (owner's container-power idea)

Owner: *"We already have actor hub — extend actor's derived stats to power point … a formula
calculating power point for each container, like a file system where power point is file size on the
disk."*

- **The leaf is built:** an actor's combat power is ActorHub's Standing vector over the combat-affecting
  channels (`gk-core/src/FusionRpg.Core/Stats/Derived/CombatPowerMembership.cs`, `gk-core/src/FusionRpg.Core/Effects/Atoms/Power/PowerVector.cs`,
  `docs/architecture/combat-power-number-ideal.md`). The combat power label is Offense + Survivability
  + Control.
- **The roll-up is new:** a container's power is the sum of its children, like file sizes. A stack's
  power = unit power × count; a legion's = the sum of its stacks (and attached uniques); an old world's
  defence = the sum of its warden legions.
- **Uses:** warden defence during catch-up steps; escort strength in lane loss (replacing the v1 stance
  count once available); the AI's force estimates where it reads its own legions.
- **One read, never a second composer:** the roll-up sums Hub output only. A contest between two
  rolled-up powers needs one new row in `docs/architecture/power/ssot-power-scale.md` §10, requested from the power program;
  until it lands, the warden defence term is 0 and escort stays the v1 count.

## U. A future unit-system program (not trade)

Owner: *"Some legion units can only be raised in specific sectors — for example a lava sector where we
build a building to recruit, train or hire fire-specific units. That should be its own program, not the
trading system."* Recorded here so it is not lost; `legion-build`'s `raise-choice` stays limited to
Q6.

---

## Round 5 — owner answers and cross-cluster rulings (2026-09-20)

### R5-A. Owner answers to the reconciliation questions

| # | Question | Decision |
|---|---|---|
| A1 | What empires start with | Every empire's seat (player and AI) starts with a **tier-1 Counting House and a tier-1 Storehouse**; everything else is built |
| A2 | A sector with no storage building | Every held sector has a **small base yard capacity** (one tunable); the Storehouse ladder widens it |
| A3 | "Faster banking" | A **per-turn banking rate that grows with the bank tier**, scaled like goods, never a cap |
| A4 | Treasury hold default | Keep enough to fill **other traders' open buy orders at this hub** |
| B1 | Trading Post slot | **Wildland or Market** — a structure row may allow more than one slot kind; a Market slot gives a bonus |
| B2 | Rift Anchor slot | **Wildland**, with a capacity bonus when the sector also has a rift-tear slot |
| B3 | Unloading at a foreign hub | **The hub's owner also needs a Caravan Yard** in that sector (so seeded clan hubs get a yard too) |
| B4 | Whose trade tier counts at a clan hub | **The trader's best Trading Post tier anywhere in that world** |
| C1 | Convoy Depot "more range" | **Provisioning top-up**: a caravan legion tops up loam at its Convoy Depot to a multiple of its bearer capacity |
| C2 | Who needs an Embassy | **Only the side making the offer** |
| C3 | Consulate "embargo leverage" | **A deliberate embargo needs a Consulate**; war embargoes stay automatic |
| C4 | Name collisions (Market, Exchange, Vault) | **Rename the slots' display names**; building names stay; ids unchanged |
| D1 | When a new world counts as held (realms axis) | **From creation** |

### R5-X. Cross-cluster rulings (decided by principle; binding)

| # | Conflict | Ruling |
|---|---|---|
| X1 | Several programs define their own building check | **Every feature gate reads `trade-foundation` `sector-features`** (`TierOf` per sector, per faction). A new `StructureKind` only where loam or siege rules need one |
| X2 | Settlement fact kinds (one vs five) | **Exchange's five kinds** |
| X3 | Who writes the AI treasury | **`counterparties` `empire-treasury`**, registered into `banking-fact`'s hand-off point |
| X4 | Legion equipment storage | **The hashed sector warehouse** (sector-yield located stock), never `rpg_item_stock` |
| X5 | Step order inside the Logistics phase | **logistics-flow's spec order** is canonical; every other spec quotes it |
| X6 | Umbrella map staleness | Income parity → sector-yield; `RulesetVersion` is 13 |
| X7 | Power roll-up owner | **`legion-build` `legion-power`**; lane loss, warden defence and AI estimates cite it |
| X8 | Upgrade verb | **`build` on the building's own slot** (sector-features); world-map is asked to confirm |
| X9 | Hub staffing | Crew supplies a bearer count; **exchange owns** the staffing term and its key |
| X10 | Stale exchange text | The exchange-map Q1 row follows A-rules above; `treaty-lifecycle` drops `StructureKind.Embassy` |
| X11 | System-only command set | **`release-warden`, `rift-window`, `rift-arrive`**; `depart` and `advance` are the player's own orders |
| X12 | Caravan building id | **`caravan-yard` is the row**; `convoy-depot` is its tier-2 variant |
| X13 | Bank point and storage reads in sector-yield | Read the Counting House and Storehouse tiers through `sector-features` |
| X14 | Passage seam and step inputs | The passage seam receives the **logged band snapshot**; counterparties keeps **one step-input table** (band snapshot, soul budget) |
| X15 | Banking hold wording | Follows A4 |
| X16 | Embassy role | **`Enable`** (no new role); the only role widening is `exchange` |

---

## Round 6 — owner decisions after the standards audit (2026-09-20)

| # | Question | Decision |
|---|---|---|
| C1 | Features vs the per-world stamp across build waves | **One capability flag and one ruleset bump per wave.** A world's rules never change mid-life; the family keeps a single landing order (see `landing-order.md`) |
| C2 | Feature buildings cannot load without a `StructureKind` | **One neutral `StructureKind.Feature`** for all feature buildings; `StructureKind.Exchange` is withdrawn; ruling X1's wording is amended to allow this one neutral kind |
| C3 | Banking waits on the save-identity re-key | **Wait.** Save-identity is being built now; `material-ledger` and the banking work that needs it start after it finishes |
| S1 | A building whose sector and slot have different owners | **It counts for nobody until one faction owns both** |
| S2 | Goods aboard a legion that advances | **Trade goods cross only through rift-trade routes.** An advance is a weight-limited transit: see W1 |
| W1 | What the advance carry limit counts | **A weight limit, like a spacecraft's payload.** A carry is Σ(unit count × that unit type's carry capacity), read from the new `world.carry.capacity` derived channel. Both units and goods draw on the same limit |
| W2 | Scope of import/export through the rift gate | **Its own program, `world-transit`** (noted now, idea round later). It owns import/export and the gate's weight limits. Until it exists, `world-continuity`'s advance moves only what the weight limit allows, and goods cross by rift-trade route |
| CQ2 | What drains an AI treasury | **Legion equipment and doctrine upkeep may draw on banked goods** when local stock runs short — the same rule for the player and every AI, so no handicap. **Confirmed 2026-09-20:** holding a doctrine costs goods **every turn**, proportional to the army it covers, and lapses (never blocks) when unpayable — a doctrine is a standing commitment, not a one-time purchase, and P6 wants a second sink competing with equipment |
| Q-A | War inside a treaty's minimum term | **It also writes `treaty.broken`**, with the same observer effect as any early exit |
| L6 | Does forging a standard need a building | **Yes, its own building kind** — a Standard Hall, with tier variants gating the standard tier (an eighth kind in the building ladder; tiers are variants of one row, as for every other building). **Tiers named 2026-09-20: Banner Yard → Standard Hall → Hall of Triumphs**, which fixes the standard tier ladder at three rungs |
| D2 | Derived stats for world-map features | **A family of six world channels plus its own program, `world-derived`** (idea round later): `world.carry.capacity`, `world.march.range`, `world.supply.burn` (lower is better), `world.sight`, `world.hazard.resist`, `world.upkeep.discount`. They compose in `ActorHub` like every other channel and roll up per stack and legion the way `legion-power` does; sources include species, equipment, legion equipment, standards, doctrine and traditions |

**Consequences for this family's specs:**
- Every spec that grants a capability flag names its wave and its ruleset bump; the family's bump order lives in one place (`landing-order.md`).
- `legion-power`, the carry limit, depot crew reads, escort strength and lane-loss resistance read **Hub output** for the world channels — never a private formula.
- `world-transit` and `world-derived` are named future programs. No spec here may implement them; specs consume their reads behind a stated default.

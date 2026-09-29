# Spec: `lane-loss`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `lane-loss`, row 6 of the
[logistics-flow map](../logistics-flow-map.md) (wave 2; depends on `lane-flow`, `transit-buffer`).
Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §8.4 (*loss is a deterministic fraction,
no spawned raiders*), §14b (*clamp to [0, 1000], a bounded ratio; abstract lane loss vanishes*), §8.3
(*an escort is a legion in the `escort` stance*). **Owner decision Q1 (2026-09-19, recorded in the map):**
escort strength in v1 is a **count of legions in the escort stance, weighted by tuning**; it switches to
a **power-difference contest** once `legion-build` provides a Hub-composed power index. House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Make distance, danger and protection cost something every turn, in the one currency the player feels:
goods that do not arrive. Each turn, goods on a lane lose a deterministic fraction set by the lane's
hazard, hostile presence on and around it, the good's own perishability, the lane's wards and posted
escorts. The lost goods vanish. Every loss carries its main cause.

Success looks like: loss is always between none and all of what was carried; it never increases any
stock anywhere; a ward or an escort never makes it worse and a hostile legion never makes it better; and
the same inputs always lose the same amount.

## Locked anchors

- **A bounded ratio, exempt from PS-8.** The rate is clamped to `[0, 1000]` ‰ and the code says so in a
  comment (`docs/architecture/power/ssot-power-scale.md` §11.6's class; ideal §14b).
- **A pure sink.** Lost goods appear in no balance, ledger credit or cache (ideal §14b). Goods on a
  **legion** that loses a battle follow `cargo-fate` — that is `fleet`, not this module.
- **One hostility rule.** Hostile means `ZoneOfControl.IsHostile` and projecting means
  `ZoneOfControl.Projects` (`gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16`, `:22-29`), until
  `counterparties` derives hostility from the logged band snapshot (umbrella §1a CM1). This module calls
  the rule; it never restates it.
- **No actor number in v1.** The only strength figure the world has for a whole force is fog-only by
  contract — *"Never call this to decide a battle"* (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:6-13`).
  Inventing another would be a private power curve (`ssot-power-scale.md` §10's closed inventory). Q1's
  v1 rule reads **presence**, so no curve and no Hub coupling exist until the contest switch.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `HazardMilli` and `WardLevel` on every lane, hashed | `gk-core/src/FusionRpg.Core/World/WorldState.cs:261-262`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:55-56` |
| Hostility and projection rules | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-42` |
| Stances are a closed list in code: `march`, `scout`, `hold`, `dowse` — no `escort` yet | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:10-25` |
| A legion stands at a sector or on a lane, never both | `gk-core/src/FusionRpg.Core/World/WorldState.cs:294-297` |
| The contest function a later strength read would use | `gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8` |

### Wiring gap

`WardLevel` has no logistics reader (its only reader is the siege approach depth,
`gk-core/src/FusionRpg.Core/World/District/DistrictLayout.cs:342-350`).

### Real gap (this module closes it)

The loss rate, its application per lane per packet, the cause set, and the stance-weight table.

## Design

### 1. The rate

For a packet of faction `f` carrying good `g`, on lane `L`, this turn:

```
raw  = L.HazardMilli
     + hostileCount(L, f) × lane.hostilePresenceMilli
     + goods.{g}.transitLossMilli
     − L.WardLevel × lane.protectionPerWard
     − escortMilli(L, f)
rate = clamp(raw, 0, 1000)        // bounded ratio — exempt from PS-8; commented in code
rate = clamp(rate × difficulty.{profile}.laneLossMilli ÷ 1000, 0, 1000)   // the world's difficulty knob
lost = ⌊qty × rate ÷ 1000⌋        // long, checked, divide last
```

- `hostileCount(L, f)` — projecting entities hostile to `f` standing on `L` (`OnLaneId == L`) or at
  either end of it.
- `escortMilli(L, f)` — **owner decision Q1, v1:** the sum over `f`'s legions standing on `L` or at
  either end of `lane.stanceEscortMilli.{stance}` for that legion's stance. v1 publishes a non-zero
  weight for the `escort` stance only (`legion-build` `escort-stance` adds it to
  `MovementPolicy.Stances`, map ask A3); every other stance has a row at 0, so a later balance pass can
  weight `hold` without a code change. Escort strength is therefore a weighted **count** of escort-stance
  legions, not a power read.
- `raw` may be negative (a well-warded, escorted lane) — the floor at 0 means protection can never turn
  loss into a gain.
- `difficulty.{profile}.laneLossMilli` is `counterparties` `trade-difficulty-knobs`' key, read for the
  world's stamped difficulty profile (`trade-foundation` `world-stamp`) through that module's hub. Until it
  lands the factor is exactly 1000 (neutral) — declared, not defaulted: the knob module is the only
  writer of the value, and a world stamped with a profile the hub does not know is a load rejection.

The rate is one pure function, `LaneLoss.Milli(hazardMilli, hostilePresenceMilli, perishMilli, wardLevel,
escortMilli)`, before the difficulty factor — the signature `rift-trade` `crossing-leg` calls for the
crossing leg, so the crossing and the lanes share one loss rule.

`WardLevel` keeps its siege meaning (approach depth for an attacker on that lane) and gains this one;
both point the same way, a warded lane is a defended lane (ideal §8.4). The dual-reader guard is
`lane-verbs`'.

### 2. Which lanes a packet pays on (L6)

A packet pays once for **each lane it occupied during this turn's movement**, in the order it walked
them: the lane it started on, then every lane it entered. `qty` shrinks after each lane before the next
is applied. Each lost quantity is recorded as a `loss` stock delta on the packet's route holder (`r:`,
`spec-transit-buffer.md` §5a), so `stock-deltas`' reconciliation and `world-stock-ledger`'s sums close
with the goods gone — the ledger records the sink; no balance receives it. A `Stranded` packet pays its lane every turn (cause `stranded`). A packet waiting `AtDoor`
pays no lane loss (it pays delivery overflow instead, `transit-buffer` L4). Goods still in a source
warehouse pay nothing.

### 3. The dominant cause — a closed set

Every non-zero loss records one cause:

| Cause | When |
|---|---|
| `stranded` | the packet is `Stranded` |
| `hazard` | otherwise, `HazardMilli` is the largest positive term |
| `hostile-presence` | otherwise, the hostile term is the largest |
| `perishability` | otherwise, the good's transit loss is the largest |

Ties resolve in the table's order. The set's cardinality is a **closed vocabulary** pinned in
`logistics-facts` (a reviewed change adds a cause), never a count of losses.

### 4. The strength switch (round 4 §P — a reviewed change, not built here)

Round 4 decides what replaces the v1 count: **escort strength switches to the power roll-up once the
power row exists** ([../decisions-round-4.md](../decisions-round-4.md) §P). A container's power is the
sum of its children's, like file sizes: a stack's power is unit power × count, a legion's is the sum of
its stacks and attached uniques, and a unit's power is ActorHub's combat-power Standing vector
(`gk-core/src/FusionRpg.Core/Stats/Derived/CombatPowerMembership.cs`; `docs/architecture/combat-power-number-ideal.md`).
When the switch lands, the escort and hostile terms become one contest between the rolled-up power of own
posted escorts and of hostile posted forces. Rules the switch must keep:

- **One read, never a second composer.** The roll-up sums Hub output only (ActorHub rule); this module
  consumes the sum and never folds a stat.
- **The contest needs its §10 row.** A contest between two rolled-up powers is one new row in
  `docs/architecture/power/ssot-power-scale.md` §10, requested from the power program (round 4 §P). Until
  it lands, escort stays the v1 count (§1) — no interim curve.
- **A stamp capability, not a code swap.** Old worlds keep the v1 count rule: the switch ships as its own
  **wave**, `trade.laneLossPower`, with its own `RulesetVersion` bump (round 6 C1; row 23 of
  [../landing-order.md](../landing-order.md) §2), so a stamped world never changes rules mid-life.
- **Same clamp, same sink, same monotonicity.**

### 4a. The world channels this module reads (round 6 D2)

Round 6 D2 creates **six world derived channels** — `world.carry.capacity`, `world.march.range`,
`world.supply.burn` (lower is better), `world.sight`, `world.hazard.resist`, `world.upkeep.discount` —
plus their own program, **`world-derived`** (idea round later). They *"compose in `ActorHub` like every
other channel and roll up per stack and legion the way `legion-power` does"*
([../decisions-round-4.md](../decisions-round-4.md) Round 6 D2).

One of them is this module's: **`world.hazard.resist`**, the escorting force's resistance to the lane's
hazard. The rules, stated now so the later wiring has nothing to decide:

- **Read Hub output, never a private formula.** The term is the rolled-up `world.hazard.resist` of the
  legions posted on the lane, summed the way `legion-power` sums combat power — one read of composed
  channel values, no fold of species, equipment, standard, doctrine or tradition contributions in this
  module. That is the one-ActorHub-compose rule, and a local *"hazard resistance = Σ species trait"* would
  break it.
- **Stated default until `world-derived` ships: the term is 0**, exactly as the round 4 §P escort switch
  defaults to the v1 count. A lane's loss today is `hazard − ward × protectionPerWard − escortMilli`
  (§1) and stays so; when the channel exists the resistance term joins the same subtraction, clamped by the
  same floor, behind the same `trade.laneLossPower` wave as the strength switch (they are one change: both
  replace a count with a Hub read).
- **No spec here implements `world-derived`.** This module names the channel, the default and the wave, and
  nothing more.

**Owner (round 5 X7, 2026-09-20): `legion-build` `legion-power`**
([../../legion-build/spec-legion-power.md](../../legion-build/spec-legion-power.md)). The switch reads
`LegionPower.Of(legion, unitPowerOf)` for each posted escort and hostile legion (that spec §3, which lists
`lane-loss` as a consumer) and never sums stacks itself; the §10 contest row is still the power program's.
The map's earlier cross-program gap ("no module owns the roll-up") is closed.

### 5. Determinism, allocation, numbers

No RNG is consumed. Per turn, one pass over `world.Entities` fills two runtime count arrays
(`[lane × faction]` for hostile and escort weights); the packet pass reads them. No allocation after
warm-up. `qty × rate` is `long`, `checked`; `rate ≤ 1000`, so the product fits while `qty` does.

## Tunables

| Key | Unit | Home |
|---|---|---|
| `lane.protectionPerWard` | ‰ per ward level | `data/tuning/trade.v{n}.json` |
| `lane.hostilePresenceMilli` | ‰ per hostile force | same |
| `lane.stanceEscortMilli.{stance}` | ‰ per posted legion in that stance | same — one row per stance in `MovementPolicy.Stances`; v1: non-zero for `escort` only. **This module owns the key family**; the `escort` row is published in the same change that adds the stance to `MovementPolicy.Stances` (`legion-build` `escort-stance`), because the join test rejects a stance with no row at load. `fleet` `escort-link` reads it and publishes nothing |
| `goods.{id}.transitLossMilli` | ‰ per lane crossed | same — one row per id of the **closed** goods vocabularies: every `MaterialCatalog` id, `souls`, `rubble` and `ironwork` |
| `goods.legion-piece.transitLossMilli` | ‰ per lane crossed | same — **one family row** for every `LegionPiece` good (audit 2026-09-20). Piece ids are seeded content injected from `legion-build`'s catalog, a population that grows; a per-id row would make every new piece seed a tuning republish and fail the load on the day content ships (validation-ssot §1: never couple a contract to a population) |

A stance or good with no row is a **load rejection naming it** (T5), never weight 0. The row sets are
joined against `MovementPolicy.Stances`, the closed goods vocabularies and the `LegionPiece` family at
load — a join, not a count.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.LaneLoss"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/LaneLoss.cs     (new) — rate, per-lane application, cause
data/tuning/trade.v{n+1}.json                       via gk-core/tools/tuning/publish.py (four key families)
tests/FusionRpg.Core.Tests/World/Logistics/LaneLossTests.cs   (new)
```

## Testing strategy

- **Bounds (property sweep):** loss ∈ `[0, qty]` for every input, including raw terms far below 0 and far
  above 1000.
- **Sink:** over seeded runs, Σ(all stocks + all packets) after L6 = before − Σ lost; the lost amount
  appears in no warehouse, packet, positive ledger row or cache (its only ledger trace is the negative
  `loss` delta on the route holder).
- **Monotonicity:** +1 `WardLevel` never increases loss; +1 own escort-stance legion never increases
  loss; +1 hostile projecting force never decreases it.
- **Determinism:** the same inputs lose the same amount across runs; the RNG stream is untouched (the
  next phase's draws are identical with and without losses).
- **Stance table:** a tuning file missing a stance row is rejected at load with the stance named;
  adding a stance to `MovementPolicy.Stances` without a row fails the join test.
- **Cause:** every non-zero loss has exactly one cause from the closed set; ties resolve in order.

Verification boundary: `FusionRpg.Core.Tests` (World/Logistics).

## Acceptance (contract)

1. Loss ∈ `[0, goods]` for every input; the clamp is a commented bounded ratio.
2. Lost goods vanish — no stock anywhere increases because of loss.
3. Wards and own escorts never increase loss; hostile forces never decrease it.
4. Same inputs, same loss, no RNG consumed.
5. A missing stance or good row is a load rejection naming it; adding a legion piece to the injected
   catalog needs no tuning change (the family row covers it).
6. v1 reads no actor number; escort strength is the tuned count of escort-stance legions (Q1).
7. Every lost quantity is a `loss` stock delta on its route holder; `stock-deltas`' reconciliation closes
   every turn.

## Hard edges

- **Ruleset / goldens:** the loss step runs only under **`trade.logisticsLanes`** (round 6 C1:
  `logistics-flow` wave 2, one bump for the wave — landing order row 6). The §4 strength switch is a
  **separate** wave with its own flag `trade.laneLossPower` and its own bump (row 23), because it lands
  only when the power program's contest row exists: a single flag over both would change a stamped world's
  loss rule mid-life. No existing golden moves.
- **Contest switch** is a later reviewed change behind its own stamp capability (§Design 4); nothing in
  this module anticipates it in code.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| Per-lane, per-faction rate and the cause | `logistics-facts`, `forecast-facts`, `lane-verbs` (tests that `ward` reduces loss) |
| `LaneLoss.Milli(hazardMilli, hostilePresenceMilli, perishMilli, wardLevel, escortMilli)` | `rift-trade` `crossing-leg` (the crossing leg's loss) |
| The stance-weight table | `legion-build` `escort-stance` (adds the row), `fleet` `escort-link` (an escort posts protection through this table, fleet map module 5) |

## Boundaries

- **Always:** clamp, floor, vanish; causes from the closed set.
- **Ask first:** any read of an actor or force strength (that is the Q1 switch, a reviewed change).
- **Never:** spawned raiders; RNG; a loss that credits anyone; `ForceStrength` for this purpose.

## Design-gate checklist

```
[x] Subsystems: world lanes, movement stances, tunables; battle/actor numbers explicitly not read.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md, plus FactionIntel's contract. Gap:
    legion-build-map.md read only through the logistics-flow and fleet maps' references.
[x] decisions.md: no lock on lane loss.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: stance list (no escort yet), ZOC rules, ForceStrength's "never decide a
    battle" contract, WardLevel's only reader.
[x] Surrounding sections read: ZoneOfControl in full; ForceStrength's class doc.
[x] Constraints tested, not assumed: none claimed.
[x] §2 invariants: bounded ratio exempt and commented; one ladder respected (no curve in v1).
[x] Corrections propagated: Q1 recorded in the map and applied here and in lane-verbs/fleet refs.
[x] No population pinned; stance and good rows are joined, not counted.
[x] Event-refreshed cache: none.
[x] Orderings: loss applied in walk order, fixed; no filing-order dependence.
[x] Actor magnitudes: none consumed in v1; the switch consumes Hub output only.
[x] No SOLID fork: the one hostility rule, the one contest function for the later switch.
[ ] Registry row: "loss never credits a stock" needs a guard or unguardableReason row when the code
    lands (the property test is the natural guard).
```

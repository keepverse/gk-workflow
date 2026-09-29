# Spec: `legion-power`

**Status: written against shipped code 2026-09-19** (round-4 reconciliation). Module id `legion-power`,
row 17 of the [legion-build map](../legion-build-map.md) (wave 3; depends on `member-stack`,
`role-aware-placement`, `general-member-hub`). Owner decision **P** and **Q9** in
[trade-network/decisions-round-4.md](../trade-network/decisions-round-4.md): *"a container's power is the sum
of its children, like file sizes. A stack's power = unit power × count; a legion's = the sum of its stacks
(and attached uniques) … One read, never a second composer: the roll-up sums Hub output only."* Ideal of the
leaf: [combat-power-number-ideal.md](../combat-power-number-ideal.md) (D2 membership, D3 label).

## Objective

Give every legion one honest strength number, built by **adding up ActorHub output** and nothing else:

```text
unitPower(member)  = combat-power label of the member's Standing  (Offense + Survivability + Control)
stackPower(member) = unitPower(member) × member.Count
legionPower(legion) = Σ stackPower over the legion's fighting members (attached uniques included)
```

Consumers named by the owner (P): a world's **warden defence** (the sum of its warden legions,
`world-continuity` `world-warden`), **escort strength** in lane loss (`logistics-flow` `lane-loss`, replacing
the v1 stance count once available), and the **AI's force estimates where it reads its own legions**.

Success looks like: a stack of one unit reads exactly its Standing label; doubling a stack's count doubles its
power; a legion's power is the same whatever order its members are in; nothing composes a combat number
outside `ActorHub`.

## Scope and non-goals

- **In:** the one Standing projection shared by the sheet and the world (lifted, not copied); the per-member
  Hub read for a world member; the roll-up arithmetic; the Data-side seam that hands the number to Core; the
  request for the contest row; **the roll-up of the six `world.*` derived channels** (round 6 D2, §6).
- **Out:**
  - **Any contest between two rolled-up powers.** How two powers become loss odds needs one new row in
    `docs/architecture/power/ssot-power-scale.md` §10, requested from the power program (P). Until it lands,
    every consumer keeps its fallback: warden defence is 0 (`world-warden` §5), escort stays the v1 count
    (`logistics-flow-map.md` OD1), AI estimates keep their current reads.
  - The consumers' own formulas (`world-warden`, `lane-loss`, the AI).
  - Showing an **enemy** legion's power. The roll-up is true strength; a foreign legion's strength is intel
    and stays fog-bound (`ForceStrength` is fog-only by contract, `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:6-13`).
  - Any tunable. The label is a sum with no weights; the leaf's prices are E9's
    (`gk-data/packs/fusion/data/seed/power/coefficients.v1.json`, `combat-power-number-ideal.md` D4).
  - **Registering the six `world.*` channels** — their ids, units and defaults are the named future program
    `world-derived`'s (round 6 D2). This module states how they roll up and nothing more (§6).

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | The Standing algorithm: membership filter, synthetic `stat.derived` rows, one `ActorPowerCache.Compose` | `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:276-313` (`ProjectStanding`), `:354` (`SyntheticStatDerived`) |
| Built | Combat-affecting membership, one predicate | `gk-core/src/FusionRpg.Core/Stats/Derived/CombatPowerMembership.cs:39-67` |
| Built | The five-axis price vector (`int` fields) | `gk-core/src/FusionRpg.Core/Effects/Atoms/Power/PowerVector.cs:18-62` |
| Built | A Hub resolve that returns the contribution bag with the snapshot, from one modifier list | `gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs:76-87` (`ResolveDerivedWithContributions`) |
| Built | Battle composes a world member through the one Hub path | `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs:52-104` |
| Built | The Data-injected per-member inputs seam | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:71` (`HubInputsFor`); `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:548-600` |
| Wiring gap | `ProjectStanding` is private to the unique-actor sheet, so no world member has a Standing | `UniqueActorHubCompose.cs:276` (`static`, unique `actor` argument) |
| Wiring gap | `BattleHubCompose.Compose` returns only the snapshot; the bag it could return is discarded | `BattleHubCompose.cs:52`, `:92` (`hub.ResolveDerived`) |
| Real gap | No roll-up anywhere; no Hub-composed legion strength (`logistics-flow-map.md` Q1 found the only whole-legion figure is fog-only) | — |

## Design

### 1. One Standing projection — lifted, not copied

`ProjectStanding`'s algorithm moves into Core as `StandingProjection.Of(IReadOnlyList<BoundDerivedAtom>
bound, DerivedContributionBag contributions, PowerTables? tables)`: take the explicitly bound atoms, add every
residual Hub contribution whose SourceId is not already one of them, filter once through
`CombatPowerMembership`, turn each into a synthetic `stat.derived` row, and price them with one
`ActorPowerCache.Compose`. `UniqueActorHubCompose.ProjectStanding` becomes a call to it with the same inputs
it passes today. **Refactor only:** every sheet Standing stays byte-identical (a test compares the vector for
the sheet fixtures before and after). Two copies of the Standing fold would be the dual-compose defect the
Hub rule exists for.

### 2. The per-member read for a world member

A world member composes through the **same** path battle uses: its `BattleHubInputs` from
`general-member-hub`'s provider (2b for a general, the unique branch for a unique, `BoundAtoms` = 5c + legion
gear through `LegionMemberAtoms`), into `BattleHubCompose`. `BattleHubCompose` gains
`ComposeWithContributions(setup)`, which calls `hub.ResolveDerivedWithContributions` instead of
`ResolveDerived` and returns both. `Compose` becomes that call with the bag dropped, so battle output cannot
move. The member's `unitPower` is `StandingProjection.Of(bound, bag).Offense + .Survivability + .Control`
(the D3 label; Utility and Economy are never combat power).

Contributions are **per unit** (`general-member-hub` §5), which is what makes `unit × Count` right.

### 3. The roll-up

```csharp
// src/FusionRpg.Core/World/Legion/LegionPower.cs — pure
public static long StackPower(long unitPower, long count) => checked(unitPower * count);
public static long Of(WorldEntity legion, Func<WorldEntityMember, long> unitPowerOf) =>
    legion.Members.Where(m => WorldEntityMemberRoles.Fights(m.Role))
                  .Aggregate(0L, (sum, m) => checked(sum + StackPower(unitPowerOf(m), m.Count)));
```

- **Who counts:** members whose role fights (`role-aware-placement`'s `Fights`,
  `legion-build/spec-role-aware-placement.md` §1). Bearers take no cell, so they add nothing; an attached
  unique (a `Commander` member, `Count` 1) adds its own Standing — the "attached uniques" of P.
- **Order-independent:** a sum of non-negative `long`s; member order never changes the result.
- **Range:** `PowerVector` fields are `int` (`PowerVector.cs:18-19`); the label sum is widened to `long`
  **before** the multiply by `Count`, and every step is `checked` (CLAUDE.md numeric rules 1–3). No clamp.
- **Containers above a legion** (a world's wardens, a faction's field army) are sums of `Of` — the same
  function, one level up, never a new formula. `world-warden` sums its warden legions this way.

### 4. How the number reaches Core

`legionPower` needs the Hub, so it is computed **Data-side** inside the commit transaction, like
`HubInputsFor`. Core receives it one of two ways, both already precedents here:

1. **A logged input** for anything replayed without the Hub — a coarse record's warden defence
   (`world-continuity` `coarse-step`, `world-warden` §5). Replay reads the logged value and never recomputes it.
2. **A Data-injected delegate** (`Func<WorldEntity, long>? LegionPowerFor`) for a consumer inside `Step`,
   the `HubInputsFor` shape (`DistrictAssaultResolver.cs:71`). A consumer that uses it inside `Step` must also
   log what it read, or its replay depends on live progression; that is the consumer's acceptance, stated in
   its own spec.

Core never reads a store; no cache is kept (computed on request each turn — DESIGN-GATE §2.16 does not apply).

### 5. The contest row — requested, not built

A contest between two rolled-up powers (warden vs. frontier pressure; escort vs. hostile presence) is a new
scale use. By the power SSOT's closed inventory it needs a `ssot-power-scale.md` §10 row before any consumer
turns a power into odds. **Request to the power program:** one pure conversion
`ContestTheta(rolledPower) → Θ units`, so every such contest is a Θ difference through
`CombatProbability.Sigmoid` (`gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8`) — contests read Θ, one ladder.
The shape of the conversion (for example an inverse of the price scale) is the power program's call. This
module ships the roll-up with or without the row; nothing downstream reads it as odds until the row lands.

### 6. The six `world.*` channels roll up through this module (round 6 D2)

**Owner decision D2 (2026-09-20):** world-map features get *"a family of six world channels plus its own
program, `world-derived`"* — `world.carry.capacity`, `world.march.range`, `world.supply.burn` (lower is
better), `world.sight`, `world.hazard.resist`, `world.upkeep.discount` — which *"compose in `ActorHub` like
every other channel and roll up per stack and legion the way `legion-power` does; sources include species,
equipment, legion equipment, standards, doctrine and traditions."*

Two ownership lines, and they do not move:

- **`world-derived` registers the channels** (a named future program; idea round later). It owns the six
  channel ids, their registration in the derived registry, their units and their defaults. **No spec in this
  family implements it**, and nothing here defines a channel.
- **This module owns the roll-up**, because it already owns the one roll-up (round 5 X7) and because a second
  place that folds per-unit derived values into a legion figure is the dual-compose defect. The per-unit value
  always comes from **Hub output** — the same `BattleHubCompose` read as §2, no private `f(level)`, no second
  fold, and never a channel computed from a species row or a piece directly.

**The roll-up, per channel.** A sum is right for a capacity and wrong for a range, so the aggregator is stated
once here and every consumer calls it — this is the whole point of D2 naming `legion-power`:

| Channel | Unit | Roll-up over the legion's members | Why |
|---|---|---|---|
| `world.carry.capacity` | weight units | **Σ (unit value × `Count`)** — the `StackPower` shape | Round 6 W1: *"a carry is Σ(unit count × that unit type's carry capacity)"*; every unit adds payload |
| `world.supply.burn` | loam per turn (**lower is better**) | **Σ (unit value × `Count`)** | A per-unit cost; the existing burn is already per member (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25`) |
| `world.march.range` | movement units | **min over members with `Count > 0`** | A legion moves no faster than its slowest unit; summing range would make a bigger legion faster |
| `world.sight` | tiles | **max over members with `Count > 0`** | A legion sees as far as its best scout |
| `world.hazard.resist` | bounded ratio, per-mille 0..1000 (**bounded — not a magnitude, no cap review**) | **min over members with `Count > 0`** | The weakest unit decides whether the legion survives the hazard; a mean would hide it |
| `world.upkeep.discount` | bounded ratio, per-mille 0..1000 (**bounded**) | **not rolled up** — applied per unit where the per-unit cost is computed, divided by 1000 **last**. If a legion-level figure is ever displayed it is the count-weighted mean, one divide at the end | A discount multiplies a per-unit cost; rolling it up first would apply it twice (PS-4's shape) |

`LegionPower` gains one generic family for this, never six private folds:

```csharp
// src/FusionRpg.Core/World/Legion/LegionWorldChannels.cs — pure, beside LegionPower
public static long SumPerUnit(WorldEntity legion, Func<WorldEntityMember, long> perUnit);  // carry, burn
public static long MinPerUnit(WorldEntity legion, Func<WorldEntityMember, long> perUnit);  // march, hazard
public static long MaxPerUnit(WorldEntity legion, Func<WorldEntityMember, long> perUnit);  // sight
```

Same rules as §3: `long`, `checked`, widened before the `Count` multiply, no clamp, order-independent (min,
max and Σ all are). Who counts differs from combat power by one row: a **bearer carries and burns**, so the
`Sum`/`Min`/`Max` family walks **every** member with `Count > 0`, not only `Fights(m.Role)`. That is why it is
a separate function family rather than a parameter on `Of`.

**Until `world-derived` ships — the stated default.** Every consumer reads the channel through Hub output
behind a **default of today's shipped value**, named in the consumer's own spec, so nothing waits and nothing
guesses:

| Consumer | Reads | Default until `world-derived` registers the channel |
|---|---|---|
| `world-continuity` `advance-carry` | `world.carry.capacity` | the per-unit carry weight in `world-continuity.v{n}.json` (`advance-carry` §2) |
| `fleet` depot crew / bearer reads, `logistics-flow` | `world.carry.capacity` | today's `CargoWeightPerUnit` / `CargoSlotsPerUnit` (`ScopedInventoryPolicy`) |
| the loam burn | `world.supply.burn` | today's per-member burn (`LegionSupply.cs:24-25`) |
| march, sight, hazard, upkeep consumers | the other four | today's shipped movement, fog and upkeep values |

A default is a **read**, not a second source: when the channel registers, the default disappears and the same
consumer call site reads Hub output. No consumer computes a world channel privately, before or after.

## Tunables

None. The label is a sum; prices are E9's; the contest conversion will be the power program's. The six
`world.*` channels carry no tunable here either: their defaults live in the consumer's own tuning file until
`world-derived` registers them (§6).

## Numeric types

`unitPower`, `stackPower`, `legionPower`: `long`, `checked`, widened before the `Count` multiply. `Count` is
`long` (`member-stack`).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LegionPower|FullyQualifiedName~StandingProjection|FullyQualifiedName~BattleHubCompose"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~UniqueActorHubCompose"
python gk-core/scripts/guard-actor-hub.py
python gk-core/scripts/audit-overflow.py --targets A3
```

## Structure

```
src/FusionRpg.Core/Stats/Derived/StandingProjection.cs   NEW       the lifted Standing algorithm (§1)
gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs             MODIFIED  ProjectStanding calls StandingProjection.Of
gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs             MODIFIED  ComposeWithContributions; Compose delegates
src/FusionRpg.Core/World/Legion/LegionPower.cs            NEW       StackPower, Of (§3)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs          MODIFIED  LegionPowerFor delegate, built in the commit
```

No type or file here is named `*Composer*` (the guard's ban, `gk-core/scripts/guard-actor-hub.py:64-69`).

## Testing strategy

- **Leaf identity:** for every sheet fixture, `StandingProjection.Of` equals the pre-change `ProjectStanding`
  vector field for field.
- **Battle unchanged:** `Compose` and `ComposeWithContributions(...).Snapshot` are equal for the battle fixture
  set; battle goldens do not move.
- **Stack:** `Count = 1` → `unitPower`; `Count = n` → `n × unitPower` (property test over counts).
- **Legion:** additive and order-independent (property test over member permutations); a bearer adds 0; a
  legion of only bearers is 0; an attached unique adds its Standing label.
- **Overflow:** a count that would overflow `long` throws, never wraps (`checked`).
- **World channels (§6):** `SumPerUnit` doubles with `Count`; `MinPerUnit`/`MaxPerUnit` ignore `Count` and
  are order-independent; a bearer counts in all three (and adds 0 to combat power, above); an empty legion
  reads the neutral value, never a wrong one; a bounded-ratio channel stays inside 0..1000 and divides last.
- **Replay:** a coarse record carrying a logged power replays with the Hub delegate absent.
- **Guard:** `guard-actor-hub.py` green.

## Boundaries

- **Always:** sum Hub output only; one Standing projection; `long` and `checked`.
- **Ask first:** any weight on the label; reading a foreign legion's true power anywhere a player or an AI
  can see it.
- **Never:** a second fold of combat numbers; a private `f(level)` or a contest formula before the §10 row.

## Success criteria

1. One Standing algorithm, used by the sheet and the world; sheet output byte-identical.
2. `legionPower` = Σ fighting stacks of `unit × Count`, order-independent, range-safe.
3. Consumers get the number as a logged input or an injected delegate; Core reads no store.
4. No consumer turns it into odds until the power program's §10 row exists.
5. (Round 6 D2) The six `world.*` channels roll up **only** through `LegionWorldChannels`' three functions,
   each aggregating Hub output with the aggregator §6's table names; a source scan finds no other fold of a
   `world.*` value into a stack or legion figure, and `world.upkeep.discount` is never rolled up before the
   per-unit cost it scales.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `LegionPower.Of`, `StackPower` | `world-continuity` `world-warden` (warden defence = Σ warden legions), `logistics-flow` `lane-loss` (escort, after OD1's switch), `trade-ai` / `ai-commander` (own force estimates) |
| `LegionWorldChannels.SumPerUnit` / `MinPerUnit` / `MaxPerUnit` (§6) | `world-continuity` `advance-carry` (the carry weight limit, W1), `fleet` (depot crew and bearer reads), `logistics-flow` (lane and escort resistance), the loam burn, every future reader of a `world.*` channel |
| `LegionPowerFor` (Data delegate), the logged value | `coarse-step`, any in-`Step` consumer |
| `StandingProjection.Of` | the unique-actor sheet (`UniqueActorHubCompose`), this module |

## Hard edges

- **Wave and ruleset bump (round 6 C1).** This module is legion-build **wave 3**. It grants no capability
  flag and no player-facing feature, and nothing in `Step` reads it until a consumer lands, so it adds
  nothing to its wave's bump — it never claims a bump of its own either. A wave grants **one** capability
  flag and takes **one** `RulesetVersion` bump, taken at landing (never pre-assigned) and recorded in
  [landing-order.md](../trade-network/landing-order.md); a consumer whose behaviour moves rides the bump of
  **its own** wave, not a separate one.
- **Server refactor** of `ProjectStanding` — sheet contract unchanged, proven by the leaf-identity test.
- **External ask:** the power program's §10 contest row (P). Recorded in the map's round-4 reconciliation.
- **External ask (round 6 D2):** `world-derived` registers the six `world.*` channels; `actor-hub`'s §8.1
  SourceId list already carries `legion:` and `legion-equip:` (map §8). Until the channels register, §6's
  stated defaults hold and no consumer computes one privately.

## Dependencies

`member-stack` (`Count`), `role-aware-placement` (`Fights`), `general-member-hub` (the world member's Hub
inputs). Optional: `legion-owner-scope` and `legion-equipment` — their contributions reach the Standing
automatically through `BoundAtoms`. External: the power program (§5), for consumers only.

## Design-gate checklist

```
[x] Subsystems: stats (ActorHub, Standing, E9 price), world legions, battle compose (read path only).
[~] Session boundary: docs-only reconciliation session; no build session record for this module yet.
[x] Read this session: decisions-round-4.md P/Q9; combat-power-number-ideal.md (built, gaps, D2-D4);
    CombatPowerMembership.cs, PowerVector.cs, ActorPowerCache.cs, UniqueActorHubCompose.ProjectStanding,
    ActorHub.ResolveDerivedWithContributions, BattleHubCompose.cs, spec-general-member-hub.md §3-§5,
    spec-role-aware-placement.md §1, ssot-power-scale.md section list and §10 heading.
[x] decisions.md: ActorHub sole compose (the rule this module is shaped by).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file.
[x] Verified against code: the Standing algorithm's location and privacy; the bag-returning Hub method; the
    int fields of PowerVector; the guard's *Composer* ban.
[x] Read surrounding sections (ProjectStanding's doc comment; BattleHubCompose's class doc).
[ ] Constraint tested: none run; byte-identity of the sheet and of battle are acceptance tests.
[x] No §2 invariant contradicted: one compose, one read; contests wait for the power SSOT row.
[x] Corrections propagated: map row 17 and the round-4 reconciliation; world-warden §5 consumes it.
[x] No population pinned.
[x] No event-refreshed cache.
[x] Order-independence asserted by a property test.
[x] Actor magnitude consumed from Hub output only.
[x] No SOLID fork: the Standing algorithm is lifted, not copied; containers reuse one sum.
[ ] Registry row: "no second Standing fold" is covered by guard-actor-hub's composer ban only for *Composer*
    names; a source-scan row for a second ActorPowerCache.Compose-over-contributions caller is owed when built.
```

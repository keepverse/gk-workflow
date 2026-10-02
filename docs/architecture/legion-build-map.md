# Capability map: legion-build

**Status: APPROVED 2026-09-19** (owner). Module boundaries, dependency direction and build order stand;
owner decisions Q1–Q3 and the standing-order kind request are recorded in §7. Module specs:
`docs/architecture/legion-build/spec-<module-id>.md` (all sixteen written 2026-09-19; the seventeenth,
`legion-power`, in the round-4 reconciliation). Spec-phase corrections to this map are listed in §10; the
round-4 owner decisions are applied in §11, which wins where the text above disagrees.
**Ideal:** [legion-build-ideal.md](legion-build-ideal.md) (owner decisions L1–L5 closed 2026-09-19).
**Umbrella:** sub-program 10 of [trade-network-ideal.md](trade-network-ideal.md) §11.
**Specs land:** `docs/architecture/legion-build/spec-<module-id>.md`. **Plan:** `tasks/legion-build-plan.md` /
`tasks/legion-build-todo.md` (not written yet).

## Assumptions (correct before approving)

1. The ideal's rulings L1–L5 stand as written: layer 5c and `OwnerKind.Legion` are approved; standards and
   traditions reset on disband or rout; a caravan is a legion on an order; stack `Count` lands now; legion
   equipment is a stack-scoped equipment layer with no sets, sockets or rolls.
2. A **stack** keeps today's member row shape: `Hp` is the **per-unit** HP, `Count` is the number of living
   units, and `Wounds` is damage on the **top unit** only (the HoMM3 shape the `decisions.md` *Deployment
   hierarchy SSOT* row already names for troop stacks). A row with `Count = 1` then means exactly what every
   row means today, which is what keeps current worlds and goldens byte-identical until a module chooses to
   move them.
3. Modules that another map already owns are **dependencies**, not modules here (§3). This map claims only
   what no other map claims, and says so with evidence where two maps each point at the other.
4. Model-free first. Nothing here calls a model. Standard, tradition, doctrine and legion-equipment
   **identity** comes from `empire-seed`'s legion family; this program's tests run on authored exemplars
   (`**/_exemplars/**`) until that family is generated.
5. Every magnitude that is an integer and can grow with play is `long`, `checked`, widened before
   multiplying, per-mille divided last (`PRINCIPLES.md` §5). A stack's HP is `Count × unit HP`, which
   passes `int` at modest counts.

## 1. What this program is

Today a legion is a list of member rows and a position (`gk-core/src/FusionRpg.Core/World/WorldState.cs:277-328`),
raising one founds a single level-1 fighter of a species the player does not choose
(`gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:124-170`), and a legion fights through the one battle
engine only as a district assault. This program makes a legion something the player **builds**: stacks with
counts, roles that decide who fights, a standard, earned traditions, one doctrine, cohesion from its
element mix, stack equipment, and standing orders that let it run on its own. A caravan, an escort and a
garrison are orders and stances on that one architecture.

Every number a legion changes on a creature enters `ActorHub` through a registered atom reader with a GG-49
SourceId. Every battle mechanism a legion needs is a battle-engine extension. Nothing reaches PvZ.

## 2. Contradictions found while verifying (code beats docs)

| # | Finding | Evidence | Disposition |
|---|---|---|---|
| X1 | The ideal cites `World/District/DistrictAssaultResolver.cs` and a refusal at `:95-98`. The file is `World/Turn/`, the refusal is `:101-104`, and `BuildAnimateSetups` is `:415-465` | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:101-104,415-465` | Ideal citation drift; this map cites the real lines. Ideal owes a one-line fix |
| X2 | **Nobody owns giving a general world member layer 2b.** `species-layer-delivery` leaves "Battle general member (no `InstanceId`)" **unchanged** and calls it a world-battle change; `legion-commander` calls the same gap "a separate, pre-existing gap for `species-progression`". Each map points at the other | `docs/architecture/species-progression/spec-species-layer-delivery.md:28`; `docs/architecture/empire-progression/spec-legion-commander.md:117-121`; the provider returns `null` for them at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:561` | **Claimed here** by `general-member-hub` |
| X3 | The Commander member role is already specified elsewhere: `WorldEntityMemberRole.Commander`, `attach-commander`/`detach-commander`, "a Commander member fights" | `docs/architecture/empire-progression/spec-legion-commander.md:34-62`; map row `docs/architecture/empire-progression-map.md:66` | **Not a module here.** `role-aware-placement` consumes it |
| X4 | The siege provider merges `commander + species + specimen` for a unique member, so a unique carries 2a **and** 2b, which the *Actor layer stack* row forbids | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:559-592` | Owned by `species-progression` `layer-source-selector` (its C1). `general-member-hub` lands after it |
| X5 | Raising always founds a **zombie-side** species whatever faction raises, and the siege provider picks the empire from the species' **side**. A player-raised general legion would therefore read the enemy empire's (`zomboss`) progression | `RaiseResolver.cs:157-170` (`s.Side == "zombie"`); `RpgStore.WorldTurns.cs:567-568` (`KillAttribution.EmpireOf(... .Side)`) | Owner question **Q2** |
| X6 | The ideal lists stances `march`/`scout`/`hold`; code has four, including `dowse` | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:10-22` | `escort` is the fifth |
| X7 | `deployment-hierarchy-map` module `deploy-carry` says *"keep troop representation as `Hp/Wounds` headcount, unchanged (locked, revisit only on playtest evidence)"*; L4 adds `Count` now | `docs/architecture/deployment-hierarchy-map.md:106` | Reconciled by assumption 2: `Count` with per-unit `Hp` and top-unit `Wounds` is the HoMM3 shape the same program's `decisions.md` row names, and `Count = 1` is byte-identical. `deployment-hierarchy-map` owes a wording amendment; `member-stack` files it |
| X8 | **Name collision.** `ItemRole.Standard` is the commander's own reserved **item** slot, and `BaseTypeSlate` maps `"standard"` to `ClassLadder.Standard` — neither is a legion standard | `gk-core/src/FusionRpg.Core/Items/ItemRole.cs:29-31`; `gk-core/src/FusionRpg.Core/Items/BaseTypeSlate.cs:28` | Legion code uses `LegionStandard` / `legion-standard`; the legion-equipment slot vocabulary never contains `standard` |
| X9 | Legion cargo capacity reads a **row** count and types slot capacity as `int` on the premise *"a legion's realistic member count is small, a structural bound"*. Stacks remove that premise | `gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs:27-47`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:88-97` | `member-stack` moves both to `Σ Count` and `long` |
| X10 | Every headcount reads member **rows**: supply burn and bearer count, garrison upkeep, the AI's force sums, the banner element vote, intel strength, recovery | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25`; `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:61-63`; `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:191,332`; `LaneCost.cs:69-93`; `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:15-24`; `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:158-173` | `member-stack` owns the full list |
| X11 | Stored standing orders are **new hashed state**. The ideal's "replay, hashing and the command log need no new cases" is true for the *emitted* commands only | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:58-68` hashes every entity field | `standing-orders` bumps the world `RulesetVersion` (13 today, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`) |
| X12 | Layer 5c and `OwnerKind.Legion` are owner-approved (L1) but appear in no binding register: the *Actor layer stack* row lists 1a–7, `definitions.md` §6 has no `legion` owner key, `actor-hub-ssot.md` §8.1 has no legion SourceId | `docs/architecture/decisions.md:52`; `docs/architecture/effect-atom/definitions.md` §6; `docs/architecture/actor-hub-ssot.md` §8.1 | `legion-owner-scope` writes all three in the change that adds the enum member |
| X13 | `trade-network` makes `legion-build` depend on `trade-foundation` (the per-world ruleset stamp and migration); the ideal's build order does not mention it | `docs/architecture/trade-network-ideal.md:560` | `member-stack` depends on it for saved-world migration |
| X14 | `spec-legion-commander.md` and `empire-progression-map.md` cite `DistrictAssaultResolver.cs:395-396` / `:409-415`; those lines moved to `:439-440` / `:459` | `DistrictAssaultResolver.cs:439-440,459` | Citation drift in another program; noted, not edited here |
| X15 | `WorldEntityKind.Caravan` is retired in two documents. `trade-network` states it in its transport section but its `fleet` scope does not list it; the legion-build ideal claims it | `trade-network-ideal.md:429` vs `:554`; `legion-build-ideal.md` §6.6 | **Owned here** (`caravan-kind-retire`); `fleet` consumes the result |

## 3. Owned elsewhere — dependencies, not modules

| Capability | Owning map / module | What this program needs from it |
|---|---|---|
| `WorldEntityMemberRole.Commander`, attach/detach, one commander per legion | `empire-progression` `legion-commander` | The role value and the attach command. `role-aware-placement` places the Commander as a fighter |
| Commander aura at 100% in siege and world assault | `aura-skill` (named by `spec-legion-commander.md:129-146`) | Nothing built here; the aura rides its own path |
| Which of 2a/2b an actor carries, and which empire it reads | `species-progression` `layer-source-selector` | The selector's `ProgressionOwner.Species` branch, called for a general world member |
| Layer 2b as a per-`(save, empire, species)` container | `species-progression` `empire-species-container`, `species-layer-delivery` 6.1/6.3 | The container to bind for a general member |
| A non-player empire owning species progression | `empire-progression` `ai-empire-species` | The enemy empire's (`zomboss`) rows, so its legions read something |
| Legion cargo and sector storage | `scoped-inventory-hierarchy` `legion-cargo`, `sector-storage`, `cargo-fate` | Cargo-fate for a destroyed trade legion (legion-equipment stock moved to `sector-yield`'s located stock, §11) |
| Troop casualties, wounds, top-unit arithmetic outside battle | `deployment-hierarchy` (troops exempt from tiers and caches; `decisions.md` row) | Nothing new; `member-stack` implements the arithmetic that row names |
| Located goods, warehouses, the goods registry | `trade-network` `sector-yield` | Forge goods for standards; inputs for legion equipment; **the legion-equipment stock itself** (`legion-equipment-stock`) |
| The Workshop → Armory → Foundry building row | `empire-seed` `trade-structure-rows` (round 4 §B) | Where legion equipment can be produced, and its best producible tier |
| The power contest row | the power program (`ssot-power-scale.md` §10, requested by round 4 P) | Turning a `legion-power` roll-up into loss odds; until it lands, consumers keep their fallbacks |
| Lane loss `escortMilli`, trade standing orders on legions, depots, crews | `trade-network` `logistics-flow`, `fleet` | `fleet` consumes `standing-orders` and `escort-stance` |
| Per-world ruleset stamp and save migration | `trade-network` `trade-foundation` | `member-stack` migrates saved worlds under it |
| Legion seeds (standards, traditions, doctrines, legion equipment) | `empire-seed` legion family (§6.4), infrastructure `band-reader` (I2) and `world-exemplars` (I4) | Seeds and exemplars. **`band-reader` is the one seed-plus-bands reader for every world family — no module here writes a second one** |
| Effect-driven hits in battle using the resolver | `solid-remediation` `battle-effect-math` (D1) | Standard, tradition and doctrine atoms that fire on events only mean something in battle after D1 |

## 4. Modules

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `member-stack` | `Count` and a stable member id on `WorldEntityMember`; every headcount reads `Σ Count`; HoMM3 top-unit wound arithmetic in the world | ext `trade-foundation` | 1 |
| 2 | `caravan-kind-retire` | Delete `WorldEntityKind.Caravan` and its naming and FE arms | — | 1 |
| 3 | `role-aware-placement` | Only fighting roles take a battle cell; bearers stay off the board; a Commander member fights | 1; ext `legion-commander` | 1 |
| 4 | `stack-combatant` | A stack enters `BattleEngine` as one combatant whose HP and output scale with its living count; casualties flow back to `Count` | 1, 3 | 2 |
| 5 | `general-member-hub` | A general world member composes through `ActorHub` with layer 2b of its owning empire (and 1a when delivered), not flat level stats | 1; ext `layer-source-selector`, `empire-species-container`, `ai-empire-species` | 2 |
| 6 | `legion-owner-scope` | `OwnerKind.Legion`, layer 5c, a `world-buff` binder and a registered atom reader with a legion SourceId | 1 | 2 |
| 7 | `raise-choice` | Raise picks species and stack size from the raising faction's own side plus the sector's pool (round 4 Q6), and may raise bearers | 1 | 2 |
| 8 | `standing-orders` | A stored per-legion standing order carrying a **kind** with a per-kind resolver (owner SO / CM5), re-emitted each turn into the one command pipe | — | 2 |
| 9 | `escort-stance` | The `escort` stance: move with and screen a named legion | 8 | 3 |
| 10 | `legion-cohesion` | A 5c atom set read from the legion's count-weighted element spread | 1, 6 | 3 |
| 11 | `legion-standards` | One standard per legion, carried by a named member, lost with it, reset on disband or rout; **forged only at a Standard Hall, whose tier caps the standard tier (round 6 L6)** | 1, 6; ext `sector-yield`, `empire-seed` exemplars and `trade-structure-rows` (the `standard-hall` row), `trade-foundation` `sector-features` | 3 |
| 12 | `legion-traditions` | Per-legion history counters from world facts; rank-tiered 5c atoms; reset on disband or rout | 6; ext `empire-seed` exemplars | 3 |
| 13 | `legion-doctrine` | One doctrine per legion: 5c combat atoms plus one signed term inside the existing march, burn, sight and cargo pricers | 6; ext `empire-seed` exemplars | 3 |
| 14 | `legion-equipment` | Equipment layer 3 at stack scope: counted located-stock pieces, a legion slot vocabulary, fit and unfit, casualties consume pieces; production only at the Workshop chain, whose tier caps the piece tier (round 4 §B) | 1, 5; ext `sector-yield`, `empire-seed` | 3 |
| 15 | `legion-count-cost` | The cost of fielding another legion, priced on a curve inside the existing loam burn | 1 | 3 |
| 16 | `field-battle-kinds` | Sector, lane and guard battles resolve through `BattleEngine` instead of the refused no-op | 3, 4, 5 | 4 |
| 17 | `legion-power` | The power roll-up (round 4 P): stack = unit Standing label × `Count`, legion = Σ fighting stacks, summed from ActorHub output only; one Standing projection shared with the sheet. **Round 6 D2:** also the roll-up of the six `world.*` derived channels (Σ per unit for carry and burn, min for march and hazard, max for sight; `world.upkeep.discount` applied per unit) — the channels themselves are `world-derived`'s | 1, 3, 5 | 3 |

**Dependency direction, no cycles.** Everything above 1 hangs off `member-stack` or the scope module. The
content modules (10–13) all bind through `legion-owner-scope` and never through each other.

**Build order:** `member-stack` ∥ `caravan-kind-retire` → `role-aware-placement` → (`stack-combatant` ∥
`general-member-hub` ∥ `legion-owner-scope` ∥ `raise-choice` ∥ `standing-orders`) → (`escort-stance` ∥
`legion-cohesion` ∥ `legion-standards` ∥ `legion-traditions` ∥ `legion-doctrine` ∥ `legion-equipment` ∥
`legion-count-cost` ∥ `legion-power`) → `field-battle-kinds`.

`trade-network` needs `standing-orders` and `escort-stance` before `fleet` (`trade-network-ideal.md:565`), so
those two are the ones to prioritise inside their waves.

**World `RulesetVersion` ordering — one bump per wave (round 6 C1, superseding this paragraph's old rule).**
Owner decision C1 (2026-09-20): *"One capability flag and one ruleset bump per wave. A world's rules never
change mid-life; the family keeps a single landing order."* So:

- **Each wave takes exactly one bump**, shared by every module landing in it, taken at landing and never
  pre-assigned (R1 below). ~~Each takes its own bump in build order … No two land in one bump.~~ is withdrawn:
  it produced one bump per module and still let a flag's behaviour arrive over several waves, which is the
  breach C1 closed.
- **Every module names its wave, and a module that grants a feature never claims "no bump"** — it rides its
  wave's. The modules that add nothing to their wave's bump are the ones that grant no capability and change
  no hashed behaviour: `caravan-kind-retire` (wave 1), `legion-owner-scope` (wave 2), `legion-power` (wave 3).
  Every other module rides its wave's bump.
- **A re-bless is still per module**, not per wave: whoever moves a golden re-blesses it with the reason in
  its own commit (`legion-traditions`, `role-aware-placement`, `field-battle-kinds`, and the two later tuning
  publishes). A bump does not imply a re-bless, and a re-bless does not imply a second bump.
- **Two landings, two bumps:** `legion-cohesion`'s band publish and `legion-count-cost`'s curve publish each
  change behaviour after their code landed, so each is its own landing with its own capability row and bump —
  never a flag registered before the behaviour it gates exists.
- The family's whole order, bump by bump, lives in one place:
  [trade-network/landing-order.md](trade-network/landing-order.md).

---

## 5. Module detail

### 5.1 `member-stack`

**Capability.** A member row gains `Count` (living units, `long`, default 1) and a stable `MemberId` that
survives casualties and reordering. `Hp` stays the per-unit HP and `Wounds` becomes damage on the top unit,
so a row's effective HP is `(Count − 1) × Hp + (Hp − Wounds)`. Every place that counts heads reads `Σ Count`
instead of the number of rows. Persistence, the canonical hash, the DTO and the FE contract carry both
fields. Nothing else in the program can bind to a member before this lands (L4), because standards and
equipment need a member identity that a battle cannot shuffle.

**State.**
- *Built:* the member row, role and persistence — `WorldState.cs:277-285`; table
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:121-131`, `role` column added through `EnsureColumn` at `:171`.
- *Real gap:* no count. `member_index` is the key (`RpgStore.World.cs:130`) and it is not stable: a battle
  rebuilds the survivor list, dropping dead rows (`DistrictAssaultResolver.cs:508-530`).
- *Wiring gap:* every headcount site in X10 and X9, plus `DistrictAssaultResolver.BuildAnimateSetups`
  (`:415-465`) and `BuildSideOutcome` (`:508`), `WildSpawnRoller`, the graph diff writer
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:408-415`) and the DTO
  (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:1001-1009`).

**Depends on.** External `trade-network` `trade-foundation` for the per-world ruleset stamp that migrates a
saved world.

**Touches.** `WorldState.cs`, `WorldCanonical.cs`, `RpgStore.World.cs`, `RpgStore.WorldGraphDiff.cs`,
`RpgStore.LegionCargo.cs`, `LegionSupply.cs`, `LoamUpkeep.cs`, `FrontierRulesPolicy.cs`, `LaneCost.cs`
(`BannerElement`), `FactionIntel.cs` (`ForceStrength`), `SupplyGraph.cs` (`Recover`),
`ScopedInventoryPolicy.cs`, `DistrictAssaultResolver.cs` (outcome arithmetic only — how a stack *fights* is
`stack-combatant`), `WorldEndpoints.cs`, the web world contract and its fixture.

**Acceptance (contract).**
- A world whose every row has `Count = 1` hashes, persists and resolves byte-identically to today, except for
  the new columns themselves, which is the one explained re-bless.
- Every headcount function returns `Σ Count` over the same member filter it uses today; a property test
  compares each against a world expanded to one row per unit.
- Recovery heals the top unit and never raises `Count`; casualties lower `Count`; `Count = 0` removes the row;
  wound arithmetic never goes negative and never overflows (`checked`).
- `MemberId` is unique within a legion, deterministic from its cause (the `RaiseResolver.cs:93-96` idiom),
  and unchanged by a battle, a recovery or a reorder.
- `BannerElement` weights each element by `Count`, ties still broken by ring order.
- Cargo capacity reads `Σ Count` and slot capacity is `long`, `checked`.

**Verification boundary.** `.\scripts\verify-change.py -Paths <changed> -Session <id>`; focused suites
`TurnEngineTests`, `WorldCanonicalSeamGuardTests`, `WorldStoreTests`, `WorldGraphDiffTests`, `SupplyTests`,
`gk-core/tests/FusionRpg.Core.Tests/World/LegionCargo/**`, `DistrictAssaultResolverTests`; web `npm test` for the
world adapters. `python gk-core/scripts/audit-overflow.py --targets A3` for the new arithmetic.

**Hard edges.** Schema migration (two `EnsureColumn`s, `count` default 1, `member_id` backfilled
deterministically). ~~World `RulesetVersion` to the next integer and a turn-golden re-bless~~ — none: the new fields are hashed only when not their default (§13 *Audit 2026-09-20*, A-LB6). FE contract field addition
(additive, fixture updated). Files the X7 wording amendment on `deployment-hierarchy-map`.

### 5.2 `caravan-kind-retire`

**Capability.** `WorldEntityKind.Caravan` is removed. A caravan is a legion on a trade standing order
(L3), so the kind can only invite a second mode.

**State.** *Built but dead:* declared at `WorldState.cs:66`, named at
`gk-core/src/FusionRpg.Core/World/EntityNaming.cs:34`, never constructed. The FE maps it at
`gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.ts:53`, pinned by `worldEnums.test.ts:53`.

**Depends on.** Nothing. Ownership is this program's (X15).

**Touches.** `WorldState.cs`, `EntityNaming.cs`, `worldEnums.ts` and its test, any i18n row that names it.

**Acceptance.** The enum has no `Caravan`; nothing in `src/` or `web/` names it; saved worlds load, because
the kind is persisted and hashed **by name** (`RpgStore.World.cs:378,632`; `WorldCanonical.cs:157`) and no
saved world ever held a caravan. No golden moves.

**Verification boundary.** `verify-change.py`; `EntityNamingTests`, `WorldStoreTests`, web `npm test`.

**Hard edges.** None. The enum is closed; removing a never-constructed member is the reviewed change.

### 5.3 `role-aware-placement`

**Capability.** A battle places only members whose role fights. `Fighter` and `Commander` take cells;
`Bearer` never does, and survives or falls with its legion's outcome instead. This is loop, not mechanism:
it decides *who is placed*, never *what a hit does*.

**State.**
- *Wiring gap:* `BuildAnimateSetups` has no role filter, so a bearer fights (`DistrictAssaultResolver.cs:415-465`;
  the file never reads `Role`).
- *Real gap:* bearers are never produced outside template literals (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:196`).
  Producing them is `raise-choice`'s.
- *Owned elsewhere:* the `Commander` value and its attach command (X3).

**Depends on.** `member-stack`; external `empire-progression` `legion-commander` for the `Commander` value.
Until that lands, the filter is `Fighter`-only, with the `Commander` arm behind a
`CrossProgramLandedFlags` flag (`gk-core/src/FusionRpg.Core/Actions/CrossProgramLandedFlags.cs`) so neither program
blocks the other.

**Touches.** `DistrictAssaultResolver.cs` (and `field-battle-kinds` reuses the same filter), a single
`FightingRoles` predicate beside `WorldEntityMemberRole`.

**Acceptance.** One predicate decides placement for every battle kind. A legion of only bearers fields
nothing and is handled as an empty side. A bearer's fate follows the side's outcome rule, stated in the spec
and tested. With no bearers present, results are byte-identical to today.

**Verification boundary.** `DistrictAssaultResolverTests`, `DistrictAssaultPhaseTests`, `SiegeEngagementTests`.

**Hard edges.** None while no real world holds a bearer outside templates; a template world with a bearer in
a siege moves, and that is re-blessed with the reason.

### 5.4 `stack-combatant`

**Capability.** A stack of *N* units enters `BattleEngine.Resolve` as **one** combatant: its HP pool is the
stack's effective HP, its output scales with its living count, damage overflows down the stack from the top
unit, and the living count at battle end flows back to `Count`. This is a battle **mechanism** — it changes
what damage and death mean for a combatant — so it is built in the engine and registered in the
responsibility register, never inside a world resolver (`battle-engine-ssot.md` §2, §5).

**State.** *Real gap:* `BattleActorSetup` has no count (`gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:7-202`);
one setup is one body. The world side today builds one setup per member row
(`DistrictAssaultResolver.cs:418-460`).

**Depends on.** `member-stack`, `role-aware-placement`.

**Touches.** `BattleModels.cs`, `BattleEngine.cs`, the death-and-cleanup and damage-apply paths the register
names (§3a #1, §3b #15), `DistrictAssaultResolver.cs` (pass the count, read it back),
`battle-engine-ssot.md` §3 (register amendment).

**Acceptance.** A combatant with count 1 resolves byte-identically to today (every battle, delve, siege and
expedition golden unchanged). Output scales with living count through one engine function, so no mode
re-derives it. Overflow damage kills whole units before wounding the next; the reported count never exceeds
the entering count. Deterministic and replayable from a recorded intent stream.

**Verification boundary.** Battle suites for the touched paths (`BattleEngine*Tests`, the four battle
hashes and the expedition hashes), plus `DistrictAssaultResolverTests`.

**Hard edges.** Amends a closed register (`battle-engine-ssot.md` §3) — a reviewed change. Owner question
**Q1** decides the shape.

### 5.5 `general-member-hub`

**Capability.** A general world member — one with no `InstanceId` — composes through `ActorHub` from the
layers a general actor carries: layer 2b of its **owning empire** for its species (and layer 1a once
`species-layer-delivery` 6.2 delivers it), instead of flat `BattleRuleset.BaseAtk/BaseDefense(level)`. Legion
equipment (module 14) and layer 5c (module 6) reach it through the same `BattleHubInputs.BoundAtoms` field
(`gk-core/src/FusionRpg.Core/Battle/BattleHubInputs.cs:21`), so this module is the one place the world asks "what
does this member bring into battle".

**State.**
- *Built:* the provider seam — `DistrictAssaultResolver.HubInputsFor` (`:71`) injected by the Data layer
  (`RpgStore.WorldTurns.cs:557-592`).
- *Wiring gap:* the provider returns `null` for every member with no `InstanceId` (`RpgStore.WorldTurns.cs:561`),
  so generals fight on `BaseAtk`/`BaseDefense` (`DistrictAssaultResolver.cs:439-440`). No map owns closing it (X2).
- *Wiring gap:* an empire other than the player's (`dave`) resolves `Empty` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:229-243`),
  closed by `ai-empire-species`.

**Depends on.** `member-stack`; external `layer-source-selector` (must land first so the unique branch is
already corrected, X4), `empire-species-container`, `ai-empire-species`.

**Touches.** `RpgStore.WorldTurns.cs` (the provider asks the selector for a general member),
`DistrictAssaultResolver.cs` (stop overriding Hub output with flat stats when inputs exist).

**Acceptance.** For the same `(empire, species, level)`, a general world member and a general lawn actor
resolve the same 2b contributions, by scope and SourceId. A general member never receives a 2a or commander
allocation term. Which empire it reads follows **Q2**. With 2b empty the member resolves exactly as today.
`gk-core/scripts/guard-actor-hub.py` stays green; no new composer.

**Verification boundary.** Data tests around the world-turn commit (`WorldTurnCommitTests`), Core
`DistrictAssaultResolverTests`, the guard.

**Hard edges.** Moves siege goldens for general members — one explained re-bless, ordered after
`species-progression`'s own re-bless so no value moves twice.

### 5.6 `legion-owner-scope`

**Capability.** Layer 5c exists. `OwnerKind.Legion` is a durable owner scope keyed by entity id (unlike
session-scoped `entity:`). A binder attaches `world-buff.*` containers to a legion and withdraws them; a
registered atom reader turns a legion's bound atoms into `BoundDerivedAtom`s
(`gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/AtomDerivedSubsystem.cs:91-92`) for each fighting member, each
carrying a SourceId of the form `legion:{entityId}:{containerId}`. Standards, traditions, doctrine and
cohesion all bind here and nowhere else. Layer 5c is **legion** scope — it is not an empire axis, and it does
not become a fourth answer to the empire-scope question `world-buff`, `world-map-scope` and `empire-title`
already compete for (`actor-layer-compose-ideal.md`, "Layer 5 is in build").

**State.**
- *Built but inert:* `ContainerKind.WorldBuff` and its prefix (`gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:38,203`;
  `ContainerValidator.cs:35`), and a store mapping (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs:575`).
  Nothing binds or reads it.
- *Real gap:* `OwnerKind` has eight members and no `Legion` (`gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs:20-30`).
  `BindGate` refuses world scopes without a world host (`gk-core/src/FusionRpg.Core/Effects/Atoms/BindGate.cs:49-51`);
  `Legion` joins that rule.

**Depends on.** `member-stack` (members to deliver to).

**Touches.** `OwnerScope.cs`, `BindGate.cs`, a legion binder in `FusionRpg.Data`, a registered reader in
`Stats/Derived/Subsystems`, `ContributionSourceIds.cs`, and three binding documents in the same change:
`decisions.md` *Actor layer stack* (5c), `effect-atom/definitions.md` §6 (the `legion` owner key; that table
also still omits `unique-actor`), `actor-hub-ssot.md` §8.1 (the SourceId row).

**Acceptance.** A `world-buff` container bound to `legion:{id}` contributes to every fighting member of that
legion and to no other actor. Withdrawal on disband or rout removes every contribution in the same turn.
Every contribution carries a non-empty SourceId that `FictionLabel` explains. Binding is idempotent and
refuses a non-`world-buff` container. The guard stays green.

**Verification boundary.** `verify-change.py`; atom bind-gate tests, owner-scope parse tests, the reader's
own tests, `gk-core/scripts/guard-actor-hub.py`.

**Hard edges.** Widens a closed vocabulary (`OwnerKind`) and the layer list; three register rows move in the
same commit. A new rule (legion contributions only through this reader) needs a row in
`gk-core/scripts/enforcement-registry.v1.json` or a stated `unguardableReason`.

### 5.7 `raise-choice`

**Capability.** A `raise` names a species from the pool, a stack size and a role. **The pool is the raising
faction's own side plus the sector's species pool** (owner Q6, round 4 — spec §2: both filtered by the
sector's climate; `Clan` and `Wild` have no side of their own); the size spends recruits in proportion; a raise
may found bearers, which is how the Bearer role first appears in play. Units raised, trained or hired only in
particular sectors through a building are a **future unit-system program**, out of scope here (round 4 §U).

**State.**
- *Built:* `raise` spends `RecruitStock` and founds one level-1 `Fighter` (`RaiseResolver.cs:84-142`); admission
  checks only that a sector was named (`:13-17`).
- *Real gap:* no species, size or role parameter; the species is always the first zombie-side species of the
  sector's climate (`:157-170`), whatever faction raises (X5).

**Depends on.** `member-stack`.

**Touches.** `RaiseResolver.cs`, `WorldCommand` payload (a species, a size, a role), admission, the recruit
tuning (`RecruitPolicy`), `empire-resource-ssot.md` §3's `recruit` row if the sink wording changes.

**Acceptance.** An illegal species, size or role is dropped with a named reason; a legal raise founds exactly
the stack asked for and spends exactly its price; no parameter defaults to today's behaviour byte-identically.
Replay derives the same entity and member ids.

**Verification boundary.** `RaiseThreadingTests`, `gk-core/tests/FusionRpg.Core.Tests/World/Growth/**`,
`WorldCommandRoundTripPropertyTests`.

**Hard edges.** Command payload addition (contract fixture). Species pool rule interacts with **Q2**.

### 5.8 `standing-orders`

**Capability.** A legion may hold one standing order: **a kind plus its payload**, each kind with its own
resolver (owner decision SO / umbrella CM5; spec §1–§2 — kinds `repeat`, `escort`, `trade-route`, `crew`);
the `repeat` kind stores a `WorldCommand` of the same shape the AI builds per
legion (`gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:568-582`), stored on the legion. A pure Core
emitter re-issues it each turn into the command list the player and the AI already feed, at the one site
where AI orders are merged (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:246`). A march resumes
mid-lane exactly as it does today (`gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:26-30`). An explicit
order for that legion this turn wins over its standing order. Automation reads the order, never the roster,
so it works with or without a commander.

**State.**
- *Built:* the resume geometry and the one command shape (`MarchResolver.cs:26-30`; `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:140-205`).
- *Real gap:* nothing stores an order; the client must resubmit (`docs/architecture/world-stage/spec-world-commands.md:266-267`;
  `world-stage-ideal.md:246`).

**Depends on.** Nothing in this program. `trade-network` `fleet` depends on it.

**Touches.** `WorldState.cs` (an order field on the entity), `WorldCanonical.cs`, `RpgStore.World.cs`, a new
emitter in `World/Turn`, `RpgStore.WorldTurns.cs`, a set/clear command, the DTO.

**Acceptance.** An emitted command is indistinguishable from the same command submitted by hand: same
admission, same drops, same report lines. Explicit-order precedence is deterministic. A routed legion's
standing order is dropped for its recovery turn exactly as a hand order would be. A standing order that
becomes illegal is dropped with a named reason and stays stored until cleared, or is cleared by a stated rule
— the spec picks one and tests it. Replay is byte-identical.

**Verification boundary.** `WorldCommandStoreTests`, `WorldCommandTurnGuardTests`, `MovementTurnTests`,
`WorldAiCommitTests`, `TurnEngineTests`.

**Hard edges.** New hashed state (X11): world `RulesetVersion` bump and turn-golden re-bless. Schema column.

### 5.9 `escort-stance`

**Capability.** `escort` joins `march`, `scout`, `hold` and `dowse`. A legion in `escort` names another
legion of its faction, moves with it along its path, and is present in any battle that legion is drawn into.
Its strength is what `trade-network`'s lane-loss formula reads as `escortMilli`. Any combat effect of the
stance is an atom through layer 5c, never a branch in the engine.

**State.** *Real gap:* `MovementPolicy.Stances` is the closed list of four (`LaneCost.cs:10-22`); stances are
loop behaviour priced by `BudgetFor` (`:50-60`).

**Depends on.** `standing-orders` (an escort is a standing relation that re-emits each turn).

**Touches.** `LaneCost.cs` (`MovementPolicy`), movement and contact resolution, the command's target field
(`WorldCommand.cs:197` already has `TargetEntityId`), the FE stance list, `world-stage`'s `world-playback`
translation table (a new drop reason set).

**Acceptance.** An escort never outpaces or strands its charge; losing the charge ends the stance with a
named reason; an escort is drawn into its charge's battle by the same kind-agnostic contact rule, never a
special case. A world with no escort resolves byte-identically.

**Verification boundary.** `StanceTests`, `MovementTurnTests`, `ContactAndClearTests`, `CrossingSymmetryTests`.

**Hard edges.** Stance vocabulary widening; world `RulesetVersion` bump.

### 5.10 `legion-cohesion`

**Capability.** A legion's element spread — count-weighted, over its fighting members — selects a cohesion
atom set bound through layer 5c: a mono-element legion gains, three or more elements lose (the Heroes III
alignment shape). Recomputed whenever the roster changes, never stored.

**State.** *Built:* the element vote the banner already takes (`LaneCost.cs:67-93`), made count-weighted by
`member-stack`. *Real gap:* no cohesion read and no container.

**Depends on.** `member-stack`, `legion-owner-scope`.

**Touches.** A cohesion reader beside `BannerElement`, the legion binder, `data/tuning/legion.v1.json` (proposed; the file does not exist yet).

**Acceptance.** Cohesion is a pure function of the fighting roster; reordering members never changes it; its
contribution withdraws the moment the roster no longer qualifies. Magnitudes come from tuning and `P(Θ)`,
never a literal.

**Verification boundary.** Unit tests on the reader; the owner-scope reader tests.

**Hard edges.** New tunable domain file (shared with modules 11–15).

### 5.11 `legion-standards`

**Capability.** A legion carries at most one standard, forged from a standard seed and carried by a named
member (by `MemberId`). Its atoms bind to the legion through layer 5c. The standard is lost when its carrier
dies or leaves, and it is reset — not inherited — when the legion disbands or routs (L2). Forging consumes
goods through the existing cargo and supply paths, so building a legion creates trade demand.

**State.** *Real gap:* no standard exists anywhere. The seed shape is `empire-seed` §6.4 (`name`, `flavor`,
`elementAffinity`, `atomFamilies[]`, `carrierRequirement`, `forgeGoods[]`).

**Depends on.** `member-stack`, `legion-owner-scope`; external `sector-yield` (forge goods), `empire-seed`
`band-reader` and `world-exemplars`.

**Touches.** The legion binder, a forge and assign command, the entity's standard field, the canonical hash,
the tuning file.

**Acceptance.** At most one standard per legion; a carrier that does not meet `carrierRequirement` is refused
with a named reason; carrier death withdraws every standard contribution the same turn; rout and disband
reset it. Validation asserts the seed contract and closed enums, never how many standards exist.

**Verification boundary.** Core world tests for the new command; the owner-scope reader tests.

**Hard edges.** New hashed state; wave 3's single world `RulesetVersion` bump (round 6 C1). Naming per X8.

**Round 6 L6 — forging needs a Standard Hall.** A-LB-Q1 is answered: standards get **their own building
kind**, not the Workshop chain. `forge-standard` reads `SectorFeatures.TierOf(sector, standard)` and drops
`standard.no-hall` at tier 0 or `standard.tier-too-high` above it; the row is `empire-seed`
`trade-structure-rows`' eighth feature building (`standard-hall`, `featureUnlock: standard`, `Refine`), and its
tier variants land with the standard tier ladder. Forging goods stay as specced (located stock, spent inside
`Step`), and CQ2's banked top-up is `legion-equipment`'s and `legion-doctrine`'s, not this module's.

### 5.12 `legion-traditions`

**Capability.** A legion earns traditions from its own history: counters over a **closed** list of world
facts (battles won, climates fought in, lanes held — the `triggerKind` vocabulary empire-seed validates
against). Each tradition has rank tiers whose magnitudes read `P(Θ)` × a tier multiplier from tuning, and
binds through layer 5c. Counters and traditions reset on disband or rout.

**State.** *Real gap:* nothing records a legion's history; the only per-legion memory is `Routed`
(`WorldState.cs:317-322`).

**Depends on.** `legion-owner-scope`; external `empire-seed` exemplars.

**Touches.** A counters field on the entity (hashed), the turn phase that observes the facts, the legion
binder, the tuning file.

**Acceptance.** Each counter advances from exactly one kind of turn fact, once per fact; rank thresholds come
from tuning with a soft curve and no ceiling; reset on rout and disband is total. The `triggerKind` list is a
closed vocabulary pinned by a membership test with its reason stated.

**Verification boundary.** Core world turn tests for the observing phase; reader tests.

**Hard edges.** New hashed state; world `RulesetVersion` bump. A closed vocabulary is declared here and
mirrored by empire-seed's validator.

### 5.13 `legion-doctrine`

**Capability.** A legion holds at most one doctrine. Its combat half is a set of atoms bound through layer 5c.
Its world half is **one signed term inside the pricer that already exists** for its `worldTradeoffKind`:
`march` inside the march budget and lane cost (`LaneCost.cs:50-60,134-140`), `burn` inside
`LegionSupply.Burn` (`LegionSupply.cs:24-25`), `sight` inside the visibility read
(`gk-core/src/FusionRpg.Core/World/Intel/Visibility.cs:38`), `cargo` inside the cargo capacity read
(`ScopedInventoryPolicy.cs:39-47`). There is never a second pricer.

**State.** *Real gap:* no doctrine. All four pricers are built and take no doctrine term today.

**Depends on.** `legion-owner-scope`; external `empire-seed` exemplars.

**Touches.** The four pricers (one term each), the legion binder, an adopt command, the tuning file.

**Acceptance.** With no doctrine every pricer returns exactly today's value. A doctrine changes exactly one
pricer, by a term read from tuning. Switching doctrine withdraws the old combat atoms the same turn.
`worldTradeoffKind` is a closed four-member vocabulary with a membership test.

**Verification boundary.** `MovementMathTests`, `gk-core/tests/FusionRpg.Core.Tests/World/Loam/**`,
`gk-core/tests/FusionRpg.Core.Tests/World/Intel/**`, legion-cargo tests.

**Hard edges.** New hashed state; world `RulesetVersion` bump.

### 5.14 `legion-equipment`

> **Round 4 (§11):** pieces live in `sector-yield`'s **located stock** (the warehouse), not `rpg_item_stock`;
> production happens only at the Workshop → Armory → Foundry building, whose tier caps the piece tier; the
> production rule is this module's ([spec](legion-build/spec-legion-equipment.md) §7). Where the text below
> disagrees, the spec and §11 win.

**Capability.** Equipment layer 3 gains a **stack** scope. A legion-equipment piece is a catalog entry with
fixed tier and stats resolved once from its seed and tuning bands, atom effects only — no sets, no sockets, no
rolls — and a power budget that is a tunable share below 1 of a unique item's at the same tier (L5). Pieces
are a counted stock located in a sector's storage; fitting a stack of *N* in a slot consumes *N* pieces where
the legion stands; casualties consume the pieces their units wore (the ideal's stated default). A fitted
stack's pieces reach `ActorHub` as `BoundDerivedAtom`s through `general-member-hub`, with a SourceId of the
form `legion-equip:{slot}:{pieceId}` — distinct from `equip:{role}:{itemRef}`, so the two scopes can never
be confused on a sheet. Slots come from a closed legion-slot vocabulary separate from `ItemRole`.

**State.** *Real gap:* none of it exists. *Constraints already locked:* ~~every inventory scope uses the one
ownership root `rpg_item`/`rpg_item_stock`~~ (superseded by round 4 R4-2 and **round 5 X4**: pieces are
located stock in the hashed sector warehouse, never `rpg_item_stock`; the item root below governs item
instances only) (`decisions.md` *Scoped inventory hierarchy SSOT*;
`rpg_item_stock` is keyed `(player_id, container_id)` with a `qty`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:102-108`);
stacks never get per-unit item rows (`deployment-hierarchy-ideal.md:175`).

**Depends on.** `member-stack`, `general-member-hub`; external `scoped-inventory-hierarchy` `sector-storage`,
`trade-network` `sector-yield` (production inputs, the `workshop` row — re-roled to `Refine`, tiers Workshop → Armory → Foundry by round 4 (§11) —
today `gk-data/packs/fusion/data/seed/structures/multiply/workshop.json`, regenerated into `refine/` by `empire-seed`
`trade-structure-rows` §5.2), `empire-seed` legion-equipment seeds.

**Touches.** The stock row family (no new ownership table), the legion slot vocabulary, a fit/unfit command,
the casualty path in `member-stack`, `ContributionSourceIds.cs`, `empire-resource-ssot.md` §3 (a new
quantity: P4 bottleneck and P6 two sinks — fitting and trade — in the same change), the tuning file.

**Acceptance.** A piece's stats are identical for every player and every read. Fitting consumes exactly the
fitted count; a stack short of pieces is refused, not partly fitted, or the spec states partial fitting and
tests it. Casualties consume exactly the dead units' pieces. No unique-item rule (sets, affix rolls, sockets,
rarity count bands) applies to this scope, asserted by a test on the resolver. Every contribution names its
slot and piece. The slot vocabulary is closed and disjoint from `ItemRole`.

**Verification boundary.** Data tests on the stock family, Core tests on the piece resolver, the Hub guard.

**Hard edges.** A new registered quantity (empire-resource row owed). A carrier kind for pieces: if it needs a
new `ContainerKind`, that widens a closed vocabulary and moves `definitions.md` §1's grammar — which is already
stale, listing 6 prefixes while `ContainerValidator.cs:35` accepts 14. SourceId grammar row in
`actor-hub-ssot.md` §8.1.

### 5.15 `legion-count-cost`

**Capability.** Fielding another legion costs more on a **curve**, not a steep flat tax and never a cap
(the Total War lesson in the ideal's prior art). The term lives inside the existing legion burn — each
legion's burn is multiplied by a curve of how many legions its faction fields — so there is no new quantity
and no second pricer.

**State.** *Built:* burn per member (`LegionSupply.cs:24-25`), garrison upkeep per head (`LoamUpkeep.cs:61-63`).
*Real gap:* nothing reads how many legions a faction has.

**Depends on.** `member-stack`.

**Touches.** `LegionSupply.cs`, `data/tuning/legion.v1.json` (proposed; the file does not exist yet; curve points in the `[x, multiplierMilli]`
shape `definitions.md` §2 already validates).

**Acceptance.** With the curve at 1000‰ everywhere, burn is exactly today's. The curve is monotone, has no
point past which a legion cannot be fielded, and extends past its last authored point by the last segment's
slope (audit 2026-09-20: a clamped tail is a cap on a scaling sink). It reads legion count, not level, so it is not a power-ladder curve; the spec says so rather than
leaving it implied.

**Verification boundary.** `gk-core/tests/FusionRpg.Core.Tests/World/Loam/**`, `TurnEngineTests`.

**Hard edges.** World `RulesetVersion` bump when the default curve is not flat.

### 5.16 `field-battle-kinds`

**Capability.** `Sector`, `Lane` and `Guard` battles resolve through `BattleEngine.Resolve` on a board, as
the district assault already does, so interception, escort and guard clearing have real outcomes. Placement
uses `role-aware-placement`; stacks use `stack-combatant`; members compose through `general-member-hub`. The
world owns the loop (who fights where, when in the turn); the engine owns every mechanism.

**State.** *Wiring gap by design:* the one resolver refuses every non-district kind and returns a
winnerless outcome (`DistrictAssaultResolver.cs:101-104`), a deliberate feature-absence guarantee from
`placeholder-battle-hub` T20 (`:14-25`). The seam is kind-agnostic (`gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:6-31,280-289`;
`BattleReporting.cs:34-58`).

**Depends on.** `role-aware-placement`, `stack-combatant`, `general-member-hub`.

**Touches.** A board projection for sector, lane and guard fights, the resolver dispatch, `BattleApplication`,
the turn goldens.

**Acceptance.** Every kind resolves through the same engine entry; a district assault is unchanged; a fight
with no living attacker is still refused, not invented; replay is byte-identical.

**Verification boundary.** Large: the world turn suites and the battle suites together. This is one of the
three points where the full suite is right (a change crossing program boundaries).

**Hard edges.** Turn goldens move wherever a refused battle becomes real; wave 4's single world
`RulesetVersion` bump (round 6 C1). Ownership is **Q3**.

---

### 5.17 `legion-power` (m17 of the global audit — this section was owed)

**Capability.** One honest strength number per container, built by **adding up ActorHub output and nothing
else** (round 4 P, round 5 X7): `unitPower` = the combat-power label of the member's Standing (Offense +
Survivability + Control), `stackPower` = `unitPower × Count`, `legionPower` = Σ over the legion's fighting
members (attached uniques included). Containers above a legion — a world's wardens, a faction's field army —
are sums of the same function, one level up, never a new formula.

**Round 6 D2 — the six `world.*` channels roll up here too.** `world.carry.capacity`, `world.march.range`,
`world.supply.burn` (lower is better), `world.sight`, `world.hazard.resist` and `world.upkeep.discount`
compose in `ActorHub` like every other channel; this module owns their roll-up because it owns *the* roll-up.
Σ per unit for carry and burn, **min** for march and hazard, **max** for sight, and `world.upkeep.discount`
applied per unit and divided last — a sum would make a bigger legion faster, which is why the aggregator is
stated per channel (`spec-legion-power.md` §6). The channels' ids, units and defaults belong to the named
future program **`world-derived`**; no spec in this family registers them, and every consumer reads them
behind a stated default until it ships.

**State.** *Wiring gap:* `ProjectStanding` is private to the unique-actor sheet
(`gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:276`) and `BattleHubCompose` discards the contribution bag it
could return (`gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs:52`). *Real gap:* no roll-up anywhere; the only
whole-legion figure is fog-only intel (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:6-13`).

**Depends on.** `member-stack` (`Count`), `role-aware-placement` (`Fights`), `general-member-hub` (the world
member's Hub inputs). Optional: `legion-owner-scope`, `legion-equipment`, `legion-standards`,
`legion-traditions`, `legion-doctrine` — their contributions reach the Standing and the world channels
automatically through `BoundAtoms`, and none of them computes either privately.

**Touches.** `StandingProjection` (lifted into Core, refactor only), `BattleHubCompose`
(`ComposeWithContributions`), `LegionPower` and `LegionWorldChannels` (new, pure), the Data-side delegate in
the commit transaction.

**Acceptance.** Sheet Standing byte-identical; `Count = n` gives `n ×` the unit figure; order-independent; a
bearer adds 0 to combat power but **does** carry and burn; `long` and `checked` throughout, no clamp; no
consumer turns two powers into odds until the power program's `ssot-power-scale.md` §10 contest row lands
(until then warden defence is 0 and escort stays the v1 count); `guard-actor-hub.py` green and no second
Standing fold.

**Verification boundary.** Core tests (LegionPower, StandingProjection, BattleHubCompose) plus
`FusionRpg.Server.Tests` for the sheet identity, and `guard-actor-hub.py`.

**Hard edges.** Wave 3; grants no capability and nothing in `Step` reads it until a consumer lands, so it adds
nothing to wave 3's single bump (round 6 C1). External asks: the power program's §10 contest row (P), and
`world-derived`'s registration of the six channels (D2).

---

## 6. Tunables

**Two files, split by owner decision Q12 (round 4, §11).** `data/tuning/legion.v1.json` (proposed; does not
exist yet; `legion-build`'s, mechanics only): cohesion bands; tradition rank thresholds (soft curve); standard
forge quantities; doctrine world-side terms per `worldTradeoffKind`; the legion-count cost curve;
field-board sizes; equipment recipe quantities and per-turn batches; **round 6 CQ2:**
`doctrine.upkeepGoodsPerUnitPerTurn` per doctrine seed id (a per-turn rate, never a cap) and the banked-draw
premium `equipment.bankedDrawPremiumMilli` / `doctrine.bankedDrawPremiumMilli` (bounded ratios, default
1000‰ = no premium, divided last). `data/tuning/legion-seed.v1.json` (both tuning files are proposed; neither exists yet)
(proposed; does not exist yet; `empire-seed` `legion-bands`, seed magnitudes): the equipment `tierBand`
ladder and the weaker budget share; the standard tier multipliers and tradition rank tier multipliers; the
doctrine combat band; the legion planner budget. **No key is in both.** Raise pricing reuses the existing
`raiseCostPoints` per unit (S7). Both files are published through `gk-core/tools/tuning/publish.py`, extending the
tool if a new domain needs it. Existing files keep their numbers: `loam.v{n}.json` (burn, carry),
`scoped-inventory.v1.json` (cargo per unit), `world.v{n}.json` (movement). No per-species number lives in any
of them.

## 7. Owner decisions — closed 2026-09-19

| # | Question | Decision |
|---|---|---|
| Q1 | How does a stack fight? | **One combatant per stack**, its HP and damage scaled by how many units are alive (the Heroes 3 model), through a **reviewed change to the battle engine's responsibility register** (`battle-engine-ssot.md` §3). Spec: [spec-stack-combatant.md](legion-build/spec-stack-combatant.md) |
| Q2 | Which empire's layer 2b does a general world member read? | **The progression of the empire that owns its legion** (option (a) below). Spec: [spec-general-member-hub.md](legion-build/spec-general-member-hub.md) |
| Q3 | Does this program own routing sector, lane and guard battles into the engine? | **Yes.** `field-battle-kinds` takes over the tracked `world-actor-combat` work. Spec: [spec-field-battle-kinds.md](legion-build/spec-field-battle-kinds.md) |
| SO | Standing-order shape (request from `fleet`, trade-network map CM5 / fleet-map C6, ask A1) | **Accepted.** A standing order carries a **kind**, and each kind has its own resolver. The trade-route order is one kind. Spec: [spec-standing-orders.md](legion-build/spec-standing-orders.md) |

The question texts and recommendations below are kept as the reasoning behind the decisions.

**Q1. How does a stack fight?** (`stack-combatant`)
- (a) **One combatant per stack**, HP pool and output scaled by living count, damage overflowing down the
  stack — the HoMM3 shape, and a new mechanism in the engine's register.
- (b) Expand each stack into one combatant per unit — no new mechanism, but a stack of thousands becomes
  thousands of actors, and any cap on the expansion would be a hidden ceiling.
- **Recommendation: (a).** It is the shape the `decisions.md` *Deployment hierarchy SSOT* row already names for
  troop stacks, it keeps the cost of a battle independent of army size, and `Count = 1` keeps every existing
  golden byte-identical. It amends `battle-engine-ssot.md` §3, which is a reviewed change either way.

**Q2. Which empire's layer 2b does a general world member read?** (`general-member-hub`, `raise-choice`)
The ruling says 2b reads "the empire that owns the species" — on the lawn, side and empire coincide. On the
world map they do not: raising founds zombie-side species for every faction (X5), and zombie species XP
credits the enemy empire (`zomboss`, `empire-progression` R1).
- (a) **The owning faction's empire.** A player's zombie legion reads the player's empire progression of that
  species. Clan, Rival and Wild forces read none until `counterparties` gives them an empire.
- (b) The species' side. A player's zombie legion reads the enemy empire's (`zomboss`) progression.
- **Recommendation: (a)** — the ideal's own fiction is "a legion grows because the empire trained the species".
  The consequence to accept with it: under R1 the player's empire earns no zombie-species XP today, so a
  player's zombie legions sit at the species baseline until the player's own world battles credit them. If
  that is not acceptable, the recruitment pool in `raise-choice` should draw the raising faction's own side
  instead.

**Q3. Does this program own routing sector, lane and guard battles into the engine?** (`field-battle-kinds`)
`actor-hub-and-combat-power-solid-fixing` deleted the stand-in and tracked the real work as
`world-actor-combat`, with no specs and "rename allowed at idea time"
(`docs/architecture/actor-hub-and-combat-power-solid-fixing/spec-placeholder-battle-hub.md:22`).
- **Recommendation: yes** — absorb `world-actor-combat` as `field-battle-kinds`, the last module here, with its
  own spec. This idea round already covers its loop, and legion-build is its only consumer. If the owner
  prefers it separate, module 16 becomes an external dependency and `escort-stance`'s battle clause waits on it.

## 8. Amendments owed by this program (made by the owning module, in the same change)

| Document | Change | Module |
|---|---|---|
| `decisions.md` *Actor layer stack* | Add layer 5c (legion scope, `world-buff` carrier, `legion:` SourceId) | `legion-owner-scope` |
| `effect-atom/definitions.md` §6 | `legion` owner key row | `legion-owner-scope` |
| `actor-hub-ssot.md` §8.1 | `legion:` and `legion-equip:` SourceId rows | 6, 14 |
| `battle-engine-ssot.md` §3 | Stack combatant under damage and death responsibilities | `stack-combatant` |
| `deployment-hierarchy-map.md:106` | "Headcount unchanged" wording reconciled with `Count` (X7) | `member-stack` |
| `empire-resource-ssot.md` §3 | Legion-equipment stock row | `legion-equipment` |
| `DESIGN-GATE.md` atom row / `PRINCIPLES.md` | Only if a vocabulary this program widens is counted there | the widening module |
| `legion-build-ideal.md` | Path and line fixes (X1), stance list (X6) | first spec written |
| `trade-network/landing-order.md` | This program's waves, their capability flags and their single bumps (round 6 C1) | the family's landing-order owner; each module cites it |

## 9. DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches: world map (legions, turn, supply, cargo), stats (ActorHub,
    actor layer stack), battle engine, the atom layer (owner scopes, containers), general vs unique creature,
    economy (a new quantity), tunables.
[ ] Session boundary recorded — NOT done. This session was scoped by its caller to one file and told not to
    edit anything else; no tasks/sessions record was written and session-boundary-check.py was not run.
[~] §1 rows read this session: DESIGN-GATE.md (whole), PRINCIPLES.md §3-§13, legion-build-ideal.md (whole),
    actor-layer-compose-ideal.md (whole), actor-hub-ssot.md (whole), battle-engine-ssot.md (whole),
    creature-system-map.md Vocabulary + amendments, effect-atom/definitions.md (whole),
    deployment-hierarchy-ideal.md (whole), world-action-economy-map.md (house style); plus the
    decisions.md rows for Actor layer stack, Deployment hierarchy SSOT, Scoped inventory hierarchy SSOT and
    World turn phase order; trade-network-ideal §8.3/§11, empire-seed-ideal §6.4/§7, and the
    species-progression, empire-progression, deployment-hierarchy, scoped-inventory-hierarchy and
    solid-remediation maps. NOT read this session: the world-map row's documents (world-map-program.md,
    world-map-runtime-*), stat-system.md, spec-derived-stat-sheet.md, spec-magnitude-and-units.md,
    combat-power-number-ideal.md, battle-timeline-map.md, battle-turn-ideal.md, effect-system/-data/-runtime,
    atom-catalog-ssot.md, economy-principles.md, tunables-ssot.md, ssot-power-scale.md. Each module spec
    must read the rows its module touches before it is written.
[x] I checked decisions.md for a lock covering this (rows above; no lock forbids any module; layer 5c is
    approved but unrecorded — X12).
[x] Every factual claim cites file:line.
[x] `python scripts/audit-doc-citations.py --scope docs/architecture/legion-build-map.md`: 108 resolvable
    citations, 0 HIGH, 0 D1/D2/D3 (two D1 hits on the not-yet-existing legion.v1.json were marked as such).
[x] I verified claims against CODE, not comments (headcount sites, the provider's merge, the refusal, the
    enum persistence by name, the hash row, the cargo int premise were each read in source).
[x] I read the surrounding section of every rule I quoted.
[~] Constraints tested, not assumed: "Caravan removal moves no golden" is argued from persistence and hash
    by name (read, not run); "Count = 1 is byte-identical" is a design requirement each module must prove
    by running its goldens. No suite was run for this map.
[x] Nothing contradicts a §2 invariant. RPG layer only; one ActorHub compose; one battle engine; no cap.
[ ] Corrections propagated — not done by design: this session edits only this file. §8 lists every owed
    amendment and the module that makes it.
[x] No assertion pins a population count; every acceptance above is a contract or a closed vocabulary with
    its reason.
[x] Event-refreshed caches: none introduced by the map. Contributions are recomputed per turn and per
    resolve; `legion-owner-scope`'s spec must still list its withdrawal triggers (carrier death, rout,
    disband, roster change) with one test each.
[x] No acceptance criterion fixes an ordering that can vary: standing-order precedence is stated as a rule,
    and the spec must test both "explicit then standing" and "standing then explicit" submission orders.
[x] Actor magnitudes: every module contributes through ActorHub (registered atom reader, SourceIds
    `legion:` and `legion-equip:`) or consumes Hub output. No composer, no private fold.
[x] No SOLID-violating parallel path: no second pricer (doctrine terms live inside the existing four), no
    second seed reader (empire-seed band-reader), no second battle resolver, no second ownership table.
[ ] New rules need enforcement-registry rows: owed by legion-owner-scope and member-stack; not written here.
```

## 10. Spec-phase corrections (2026-09-19)

Found while writing the sixteen specs against code; each spec carries the evidence.

| # | Correction | Spec |
|---|---|---|
| S1 | **`RulesetVersion` bumps — superseded by round 6 C1 (§4).** ~~State a module adds is hashed only when present … so `standing-orders`, `escort-stance`, `legion-standards` and `legion-doctrine` need **no** bump. Bumps: `member-stack`, `role-aware-placement` …~~ The default-suppressed hashing and command-only precedents still hold, and they are why **no golden moves and no world is migrated** for those modules — but they never justified skipping the *stamp*. Round 6 C1: **one capability flag and one bump per wave**, ridden by every feature-granting module in the wave; only `caravan-kind-retire`, `legion-owner-scope` and `legion-power` add nothing to theirs | §4; each spec's *Wave and ruleset bump*; [trade-network/landing-order.md](trade-network/landing-order.md) |
| S2 | **Two tuning files.** `legion-seed.v1.json` (`empire-seed`) holds standard/tradition tier multipliers and the legion-equipment budget share and bands (`empire-seed-map.md` §11 item 6); `legion.v1.json` holds mechanics only. §6's list mixes both. **Confirmed by owner Q12 (round 4); §6 rewritten** | cohesion, standards, traditions, doctrine, equipment (both tuning files are proposed; neither exists yet) |
| S3 | **§5.5 wording.** A general member composes 2b **on top of** the `BaseAtk`/`BaseDefense` baseline every battle actor carries, not "instead of" it. Two guards return `null` for generals (`DistrictAssaultResolver.cs:459` and `RpgStore.WorldTurns.cs:561`), not one. Trimmed-report re-derivation (`RpgStore.WorldTurns.cs:773`) must refuse composed fights | general-member-hub |
| S4 | **The legion owner key names the world** (`legion:{worldId}/{entityId}`): entity ids repeat across worlds and `effect_binding` has no world column | legion-owner-scope |
| S5 | **Escort reads presence, not strength** in v1 (`logistics-flow-map.md` Q1) | escort-stance |
| S6 | `Wounds` widens to `long`; cargo slot capacity and `LoamUpkeep`'s garrison count widen to `long` | member-stack |
| S7 | Raise pricing reuses `raiseCostPoints` per unit — no new tunable | raise-choice |
| S8 | Standing-order kinds: `repeat`, `escort`, `trade-route`, `crew` (fleet's decision SO names `crew` as a second kind); one writer for order state, callable from `fleet`'s Logistics phase | standing-orders |
| S9 | `role-aware-placement` needs no landed flag: the `Commander` enum member is the signal | role-aware-placement |
| S10 | Stack scaling is register row **21** ("Stack body"), a new row rather than a clause of #1 or #15 | stack-combatant |

## 11. Reconciliation 2026-09-19 (round 4)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) (binding; the register wins
where this map disagrees).

### Decisions applied

| Round-4 item | Change | Where |
|---|---|---|
| §B — legion equipment needs Workshop → Armory → Foundry | `produce-gear` is legal only where `trade-foundation` `sector-features`' `TierOf(sector, legion-equipment)` ≥ 1; its tier is the best producible piece tier (rung *i* needs tier ≥ *i*); recipe quantities and per-turn batches are this program's tunables | [spec-legion-equipment.md](legion-build/spec-legion-equipment.md) §7; `empire-seed/spec-legion-bands.md` §3 item 3 |
| Q6 — the recruitment pool | Own side (closed `SideOf` table: Player and Rival `plant`, Zomboss `zombie`, Clan and Wild none) plus the sector pool, both climate-filtered; the default raise is unchanged | [spec-raise-choice.md](legion-build/spec-raise-choice.md) §2 |
| §U — a future unit-system program | Sector-specific recruit, train and hire buildings are **out of scope**; `raise-choice` stays limited to Q6 | spec-raise-choice header and scope; §5.7 above |
| P / Q9 — the power roll-up | New module 17 `legion-power`: stack = unit Standing label × `Count`, legion = Σ fighting stacks, summed from ActorHub output only; `ProjectStanding`'s algorithm lifted into Core, not copied; no `*Composer*`. Consumers (warden defence, escort, own-force AI estimates) wait on a `ssot-power-scale.md` §10 contest row requested from the power program | [spec-legion-power.md](legion-build/spec-legion-power.md) |
| Q12 — legion tuning and vocabulary | `legion.v1.json` = mechanics; `legion-seed.v1.json` = seed magnitudes (tier ladders, the weaker share); no key in both (§6 rewritten). One shared vocabulary registry, `data/seed/legion/_registry/vocab.v1.json`, which the standards, traditions, doctrine and equipment enums are validated against at load | §6; `empire-seed/spec-legion-seed-contract.md` §5.2; the four specs' vocabulary sections (both tuning files are proposed; neither exists yet) |

### Contradictions fixed

| # | Contradiction | Fix |
|---|---|---|
| R4-1 | Row 8 and §5.8 still said a standing order is *"a stored per-legion `WorldCommand`"*, after owner decision SO (umbrella CM5) and the `standing-orders` spec made it kind-keyed | Row 8 and §5.8 corrected |
| R4-2 | §5.14 and `legion-equipment` stored pieces in `rpg_item_stock` sector storage; `sector-yield` `legion-equipment-stock` stores them as a located good (`legion-build-ideal.md` §6.7) | Located stock wins (ideal, and the warehouse is the third axis the umbrella names); `legion-equipment` §4 corrected |
| R4-3 | Production of pieces was claimed by neither side: `legion-equipment` pointed at `sector-yield`, and `sector-yield/spec-legion-equipment-stock.md:22-25` pointed back | Claimed here (`legion-equipment` §7) |
| R4-4 | `legion-traditions` has no top rank, while the seed's `rankNames[]` was fixed to "the rank count" | Names cover the authored points; later ranks reuse the last name (presentation, not a cap) |
| R4-5 | §6 listed the equipment share and tier bands under `legion.v1.json`, against §10 S2 and `empire-seed-map.md` §11 item 6 | Q12 applied (both tuning files are proposed; neither exists yet) |
| R4-6 | `member-stack` and X11 cited `RulesetVersion` 12 at `TurnEngine.cs:114`; the freeze fix `d6931e43a` made it 13 at `:125` and shifted every later line | Re-pointed; line citations into the files that commit changed were re-mapped in every spec of this program |
| R4-7 | Four specs cited `empire-seed-map.md` by line number, which the round-4 edits to that map moved | Replaced by section references |

### Asks answered (from `trade-network`)

| Ask | Answer | Where |
|---|---|---|
| fleet A1 / CM5 (kind-keyed standing orders) | Done in the spec; the map wording now matches | row 8, §5.8 |
| fleet A3 (escort holds with a loading caravan) | The `escort` resolver's hold contract | `spec-escort-stance.md` §3 |
| fleet A8 (multi-entity battle sides) | `field-battle-kinds` §3 | `spec-field-battle-kinds.md` |
| logistics-flow A3 (`escort` as a stance id) | `escort-stance` adds it to `MovementPolicy.Stances` | `spec-escort-stance.md` |
| logistics-flow OD1 (escort switches to a power contest later) | The later read is `legion-power`'s roll-up, after the power §10 row | `spec-escort-stance.md`; `spec-legion-power.md` §5 |
| logistics-flow A9 (a named owner and module for the roll-up; addressed to the power program) | **`legion-build` `legion-power`** owns the roll-up; the power program owns only the §10 contest row | `spec-legion-power.md` |
| exchange E-A6 (does a recipe consume a world stock?) | **No**: `recipeGoods[]` validates against `MaterialCatalog.All`, which holds no world stock; pieces trade as ordinary located goods | `spec-legion-equipment.md` §7 |
| trade-ai T-A2 (a trade-order legion is identifiable) | `StandingOrder.Kind` on the entity | `spec-standing-orders.md` interface |
| sector-yield `legion-equipment-stock` hard edge (storage root) | Located stock (R4-2) | as above |

### Cross-cluster conflicts (trade-network files — reported, not edited)

| # | Conflict | Recommended resolution |
|---|---|---|
| X-LB1 | `sector-yield/spec-legion-equipment-stock.md` §Scope says recipes and the producing building are `legion-build`'s *"on a `refine`/`multiply` row such as `workshop`"* | Keep the ownership (now claimed here); name the Workshop chain (`featureUnlock = legion-equipment`) as the only producer |
| X-LB2 | `logistics-flow/spec-lane-loss.md` (round-4 paragraph under its escort-strength switch) says *"No module id owns the roll-up yet"*, and its header still expects a power index from `general-member-hub`/`stack-combatant` | The owner is `legion-build` `legion-power` (module 17), which sums what those two compose; the spec should cite it and drop the gap |
| X-LB3 | `fleet-map.md` (its caravan-count note) cites the per-legion cost curve in `legion.v1.json` | Correct under Q12 (a mechanic); no change needed — recorded so no one moves it to the seed file (both tuning files are proposed; neither exists yet) |

### Closed-vocabulary widenings (this program)

`OwnerKind` (+`Legion`), `ContainerKind` (+`LegionGear`), `MovementPolicy.Stances` (+`escort`; +`warden` for
`world-continuity`), `WorldEntityMemberRole` placement predicate (unchanged members), standing-order kinds
(`repeat · escort · trade-route · crew`), the legion registry lists (`legionSlots`, `triggerKinds`,
`carrierRequirements`, `worldTradeoffKinds`), `SideOf` (new closed table, five faction kinds), battle-engine
register row 21 (stack body), `WorldCommandKinds` (+`produce-gear` and the kinds the specs already list).

### Owner questions

None open in this program after round 4. Q6's climate filter on the own-side species is decided by principle
(the pool stays the **sector's** pool; Q6 widens the side, not the geography) and is a one-line change to
`PoolFor` if the owner reads it the other way.

## 12. Round 5 (2026-09-20)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) *Round 5* (R5-A, R5-X;
binding). Re-verified this session: the `workshop` row still sits under `gk-data/packs/fusion/data/seed/structures/multiply/`
and `convoy-depot` under `move/` (the regeneration `empire-seed` specifies has not run); `rpg_item_stock`
is keyed `(player_id, container_id)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:102-108`).

| Ruling | Change | Where |
|---|---|---|
| **X4** — equipment storage is the hashed sector warehouse, never `rpg_item_stock` | §5.14's "constraint already locked" line struck and pointed at X4; `legion-equipment` §4 cites X4 | §5.14; [spec-legion-equipment.md](legion-build/spec-legion-equipment.md) §4 |
| **A2** — every held sector has a small base yard capacity | `fit-gear`/`unfit-gear` need only an own sector (`gear.not-home`), not "a sector with a warehouse" | spec-legion-equipment §4 |
| **X7** — the power roll-up owner is `legion-power` | Already this program's module 17; consumers cite it (trade-ai and world-continuity checked this round) | [spec-legion-power.md](legion-build/spec-legion-power.md) |
| **X1** — every gate reads `sector-features` | Already true: `produce-gear` reads `TierOf(sector, legion-equipment)` | spec-legion-equipment §7 |
| **X12** — `caravan-yard` is the row, `convoy-depot` its tier-2 variant | No legion-build text names the row id; `standing-orders` names a depot **sector** only | — |
| **X5** — logistics-flow's step order is canonical | `standing-orders` and `escort-stance` add no Logistics step (they resolve in Snapshot); no quote to fix | — |

**Not applicable here:** A1, A3, A4, B1–B4, C1–C4, D1, X2, X3, X6 (already 13, R4-6), X8–X11, X13–X16.
No new contradiction; no owner question.

Citation audit: `python scripts/audit-doc-citations.py --scope` run on this map and the edited spec after
these edits.

## 13. Audit 2026-09-20

An independent audit of this map and its seventeen specs against code and the binding documents
(`DESIGN-GATE.md` §2, §3, §5 and its Stats, actor-layer, battle-engine and atom-layer rows; `PRINCIPLES.md`;
`tunables-ssot.md`; `validation-ssot.md`; `contributing/testing-standard.md`; `economy-principles.md`;
`power/ssot-power-scale.md` §10–§11; `actor-hub-ssot.md` §6–§8; `actor-layer-compose-ideal.md` (layer
stack, the five questions, layer 5); `battle-engine-ssot.md` (whole); `effect-atom/definitions.md` §0–§6;
`trade-network/decisions-round-4.md`), all read in this session. Every fix below is in the named spec; where
this section and the text above disagree, this section wins.

### Findings

| # | Severity | Finding (evidence) | Status |
|---|---|---|---|
| A-LB1 | HIGH | DESIGN-GATE §2.16. `legion-owner-scope` ran its reconcile only after `Step` in the turn commit. The key-set edges — a world **created** with legions, a legion **arriving** by advance, a legion destroyed in a hibernating world's **coarse** record, a Data-side crossing — never reconciled, so an arrived legion fought its first battles with no layer 5c | **Fixed** — trigger table T1–T5, one test each, and a source-scan guard that every world-graph writer runs the reconcile (`spec-legion-owner-scope.md` §2); `world-continuity` `world-creation`, `advance-carry`, `coarse-step` carry the call |
| A-LB2 | HIGH | `legion-equipment` checked and spent pieces with a Data gate before `Step` and a Data spend after it (the relic pattern, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:544`, `:609-611`). Round 5 X4 puts pieces in the **hashed** sector warehouse, changed only by `LocatedStockOps.Add` from inside `Step` (`trade-network/sector-yield/spec-located-stock.md` §2). A Data-side spend of hashed state is a side-channel write replay never reproduces | **Fixed** — fit, unfit and production read and move located stock inside `Step`; a replay test and a source scan (`spec-legion-equipment.md` §4, §7) |
| A-LB3 | HIGH | `legion-standards` forged from the scoped-inventory sector storage overlay (`rpg_world_sector_storage`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SectorStorage.cs:55-66`) with the same Data gate/spend, while §3 of this map places forge goods in `sector-yield`'s located stock | **Fixed** — the resolver spends located stock inside `Step` (`spec-legion-standards.md` §3) |
| A-LB4 | HIGH | One power ladder. The standard tier multipliers, the tradition rank multipliers and the tradition rank thresholds are power-shaped scales with no `ssot-power-scale.md` §10 row; §10 is closed. Precedents: row 38 (a per-rank quality multiplier got its own row) and row 33 (a counter-to-rank cost ladder got its own row) | **Gated, row requested** — no value publishes and ranks bind rank 1 only until the rows land (`spec-legion-standards.md`, `spec-legion-traditions.md` Hard edges; `empire-seed/spec-legion-bands.md` Hard edges). The rows are the power program's file |
| A-LB5 | MEDIUM | `legion-count-cost` clamped its curve at the last authored point — a flat tail on an upkeep that must keep scaling with holdings (PS-8's "flat rate facing a scaling sink"; economy-principles P2) | **Fixed** — extends by the last segment's slope, the rule `legion-traditions` already uses; §5.15 above corrected in place |
| A-LB6 | MEDIUM | `member-stack` appended `Count` and `MemberId` to every canonical member row, moving every world's hash and making the store refuse to re-derive every saved world's older turns (`RpgStore.WorldTurns.cs:759-760`). §10 S1 already named the fix: hash a field only when present (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:71-72`) | **Fixed** — `count=` only when `Count != 1`, `id=` only when `MemberId != m{i}`; no re-bless, **no `RulesetVersion` bump** (the migration still runs). §5.1 above and §4's and §10 S1's bump lists are superseded for this module |
| A-LB7 | MEDIUM | `field-battle-kinds` refused a sector or lane fight whose force outgrew its deployment edge (copying `DistrictAssaultResolver.cs:175-178`). A field board has no authored geometry, so refusal made large armies impossible to intercept — a hidden count ceiling that pays the biggest army | **Fixed** — the field board grows to fit; the tuned size is a minimum (`spec-field-battle-kinds.md` §2) |
| A-LB8 | MEDIUM | `standing-orders` walked entities in ordinal order, while `escort-stance` §3 needs every charge's command before its escort's | **Fixed** — per-kind pass rank; the emitter walks `(Pass, EntityId)` (`spec-standing-orders.md` §5) |
| A-LB9 | MEDIUM | `stack-combatant` narrowed `LivingUnits` into the pipeline's `int hitCount` (`gk-core/src/FusionRpg.Core/Combat/DamageApplyPipeline.cs:66`, `gk-core/src/FusionRpg.Core/Combat/Shield/ShieldGate.cs:51`) with a checked cast: with `Count` unbounded by design, a large stack would throw mid-battle — an arithmetic ceiling on army size where a wider type exists | **Fixed** — both parameters widen to `long` (callers widen implicitly; no golden moves) |
| A-LB10 | MEDIUM | `RulesetVersion` numbers were pre-assigned ("13 today, so 14") while `world-continuity` `world-victory` also bumps "to the next integer" — two programs in parallel would mint one number for two rule sets | **Fixed** — rule R1 below (shared with `world-continuity-map.md` *Audit 2026-09-20* R1) |
| A-LB11 | MEDIUM | New tuning and seed files (`legion.v1.json`, `legion-seed.v1.json`, `data/seed/legion/**`) have no verification mapping, so `gk-core/scripts/verify-change.py:771` throws for them; no `legion-build` spec named the gap | **Fixed as an obligation** — rule R3 below |
| A-LB12 | LOW | Closed-vocabulary counts written as transitions ("stances 4 → 5", "`WorldCommandKinds` 18 → 20") while other modules widen the same lists (`warden`, `depart`, `advance`, `produce-gear`, …) | **Fixed** — the pinned test names members; the count is what the list holds at landing |
| A-LB13 | LOW | Design prose named IP characters ("Zomboss's rows", "a non-Dave empire") where the vocabulary rule asks for generic terms; enum ids keep their names | **Fixed** in `spec-general-member-hub.md` and this map (X5, §3, §5.5, Q2) |
| A-LB14 | LOW | `legion-cohesion` listed a Core "loader hook"; Core never reads a file | **Fixed** — a pure parser; the host reads (tunables-ssot §7.2) |

Checked and **clean**: every actor number reaches `ActorHub` through a registered reader with a SourceId
(`legion:`, `legion-equip:`; `aptitude.{Share}` for 2b), and `legion-power` sums Hub output only (no
`*Composer*`); `stack-combatant` and `field-battle-kinds` are a register row and a loop, never a mode
mechanism; the five layer questions are answered for 5c and stack-scope equipment; `long`/`checked`/divide
last throughout; every pinned literal is a closed vocabulary with a reason; standards, traditions and
cohesion withdraw through the one reconcile.

### Program rules added by this audit

- **R1 — `RulesetVersion` is taken at landing, never pre-assigned** (13 today,
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`). The module that lands second rebases onto the landed
  number, takes the next, and re-blesses once more with the reason; each history line names its module.
  ~~The bump list after this audit: `role-aware-placement` … Not `member-stack` (A-LB6).~~ **Superseded by
  round 6 C1** (§4): the bump is the **wave's**, not the module's, so there is no per-module bump list any
  more — every module of a wave rides one bump, and only `caravan-kind-retire`, `legion-owner-scope` and
  `legion-power` add nothing to theirs. The **re-bless** list is unchanged and stays per module:
  `role-aware-placement` (only if a template-bearer golden moves), `general-member-hub`, `legion-traditions`,
  `legion-cohesion` (at the publish that fills its bands), `legion-count-cost` (at the publish that bends its
  curve), `field-battle-kinds`. `member-stack` still moves no golden (A-LB6).
  
- **R2 — store tests run in memory** (`contributing/testing-standard.md` R1).
- **R3 — a new tuning or seed file ships with its verification mapping** in
  `gk-core/scripts/verification-boundaries.v1.json`, in the change that publishes it; `data/seed/legion/**` is
  `test-verification-boundary`'s `python-test-lane` (as `empire-seed-map.md` §8 records).
- **R4 — owed enforcement-registry rows** (`gk-core/scripts/enforcement-registry.v1.json`, each with its module):
  headcounts read `Units()` (`member-stack`); placement only through `Fights` (`role-aware-placement`);
  stack scaling only in `StackBody` (`stack-combatant`); 5c only through the one reader, and every graph
  writer runs the reconcile (`legion-owner-scope`); `History` written only by the observer
  (`legion-traditions`); emitted orders only through the barrier emitter (`standing-orders`); no Data-side
  write to located stock (`legion-equipment`); no second Standing fold (`legion-power`).

### Reported, not fixable in this program's files

| Item | Owner | Fix |
|---|---|---|
| §10.2 rows for the standard tier multipliers, the tradition rank multipliers and the tradition rank thresholds (A-LB4) | the power program (`ssot-power-scale.md`) | Three rows in the row-33 / row-38 shape, PS-4 on the two multipliers |
| `PowerVector`'s fields are `int` (`gk-core/src/FusionRpg.Core/Effects/Atoms/Power/PowerVector.cs:18-19`); `legion-power` widens only after reading them, so a Standing label that outgrows `int` at high `Θ` would fail before the roll-up sees it | the effect-atom program (E9) | Widen the vector's category fields to `long` |
| `effect-atom/definitions.md` §1's `container_id` grammar lists 6 prefixes while `ContainerValidator.cs:35` accepts more; `legion-equipment` adds `legion-gear` | the effect-atom program | Regenerate the grammar row from the validator list in the change that adds `legion-gear` |

### Owner question — answered (round 6 L6)

**A-LB-Q1 — Is forging a standard gated by a building?** ~~Open; recommendation (b), the Workshop chain.~~
**Answered by the owner on 2026-09-20 (round 6 L6): option (c), its own building kind.** *"Yes, its own
building kind — a Standard Hall, with tier variants gating the standard tier (an eighth kind in the building
ladder; tiers are variants of one row, as for every other building)."* The recommendation was **not** taken:
the equipment ladder and the standard ladder are built and upgraded separately, so growing one does not grow
the other. Applied in [spec-legion-standards.md](legion-build/spec-legion-standards.md) §3a (the
`standard.no-hall` / `standard.tier-too-high` gate, read through `SectorFeatures.TierOf`) and in
[empire-seed/spec-trade-structure-rows.md](empire-seed/spec-trade-structure-rows.md) §5.1, §5.1a (the
`standard-hall` row, `featureUnlock: standard`, `Refine`). No open owner question remains in this program.

---

## 14. Round 6 (2026-09-20)

Applies [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) *Round 6* (binding, the
owner's answers after the global standards audit). Where this section disagrees with anything above, this
section wins; every change is made in the named spec, not only here.

| Ruling | Change in this program | Where |
|---|---|---|
| **C1** — one capability flag and one ruleset bump **per wave** | §4's *"each takes its own bump … no two land in one bump"* and §10 S1's *"need **no** bump"* list are both superseded. Every module names its wave; a module that grants a feature rides its wave's single bump and never claims "no bump"; only `caravan-kind-retire` (w1), `legion-owner-scope` (w2) and `legion-power` (w3) add nothing to theirs. Re-blesses stay per module. `legion-cohesion`'s band publish and `legion-count-cost`'s curve publish are their **own** landings with their own bumps — a flag is never registered before the behaviour it gates exists | §4; §13 R1; each spec's *Wave and ruleset bump* section (`member-stack`, `role-aware-placement`, `stack-combatant`, `general-member-hub`, `legion-owner-scope`, `raise-choice`, `standing-orders`, `escort-stance`, `legion-cohesion`, `legion-standards`, `legion-traditions`, `legion-doctrine`, `legion-equipment`, `legion-count-cost`, `field-battle-kinds`, `legion-power`, `caravan-kind-retire`) |
| **C3** — banking waits on the save-identity re-key | Every banked draw this program gains (CQ2) is banking work: it lands **after** `material-ledger`, which waits on `solid-enforcement` SE4.12–SE4.38. Stated default until then: located stock only — `produce-gear` refuses `gear.inputs-short`, and an unpayable doctrine lapses. No interim second writer | [spec-legion-equipment.md](legion-build/spec-legion-equipment.md) §7a; [spec-legion-doctrine.md](legion-build/spec-legion-doctrine.md) §3a |
| **CQ2** — legion equipment and doctrine upkeep may draw banked goods when local stock is short, symmetric for player and AI | `legion-equipment` §7a: a short sector warehouse draws the recipe shortfall from the owner's banked store (player materials or AI treasury, round 5 X3) through `material-ledger` only, then refuses. `legion-doctrine` §3a: doctrine gains a **per-turn goods upkeep** (`perUnit × Σ Count` — recurring and army-proportional, a rate, never a cap), paid from located stock, topped up from banked goods, and **lapsing** with a report line when neither can pay. Nothing reads the owner's faction kind: the same test runs twice with the owner swapped (principle 11). This is legion-build's agreement to `counterparties-map.md` CX2 | spec-legion-equipment §7a, criterion 4, Tunables; spec-legion-doctrine §3a, Tunables, Testing |
| **L6** — forging a standard needs its own building kind (a Standard Hall, tier variants gating the standard tier) | A-LB-Q1 answered — option (c), **not** the recommended Workshop chain. `legion-standards` §3a adds the gate (`standard.no-hall`, `standard.tier-too-high`) read through `SectorFeatures.TierOf(sector, standard)`; the row is `empire-seed`'s eighth feature building, whose three tiers the owner named on 2026-09-20 (Banner Yard → Standard Hall → Hall of Triumphs), fixing the standard tier ladder at three | [spec-legion-standards.md](legion-build/spec-legion-standards.md) §3a, Hard edges, criterion 1a; §5.11; §13 *Owner question* |
| **D2** — six `world.*` channels compose in ActorHub and roll up like `legion-power` | `legion-power` §6 states the roll-up (Σ per unit for carry and burn, min for march and hazard, max for sight, `world.upkeep.discount` per unit and divided last) in one function family `LegionWorldChannels`, walking **every** member with `Count > 0` (a bearer carries and burns). `legion-equipment`, `legion-standards`, `legion-doctrine` and `legion-traditions` may **contribute** as ordinary Hub contributions and compute nothing. `world-derived` is the named future program that registers the channels; consumers read them behind a stated default (today's shipped values) until it ships | [spec-legion-power.md](legion-build/spec-legion-power.md) §6, criterion 5; spec-legion-equipment criterion 5; spec-legion-standards Hard edges; spec-legion-doctrine §3b; spec-legion-traditions Scope; §4 row 17; §5.17 |
| **S1** — a feature building counts for nobody until one faction owns both its sector and its slot | Both building gates in this program (`legion-equipment` §7's Workshop chain, `legion-standards` §3a's Standard Hall) read that rule from `trade-foundation` `sector-features` (`TierOf` / `FactionTier`) and never compare a slot owner with a sector owner themselves | spec-legion-equipment Hard edges; spec-legion-standards §3a |
| **S2 / W1 / W2** — trade goods cross worlds only by rift-trade route; an advance is a weight-limited transit | Nothing in this program moves goods between worlds. What it owes is the **per-unit carry capacity** the limit is computed from, and that is `world.carry.capacity` — a channel this program contributes to and rolls up (D2), never one it defines | spec-legion-power §6; `world-continuity/spec-advance-carry.md` §2 |
| **m17** (global audit) — `legion-power` had no §5 detail section | Added as §5.17 | §5.17 |

### Reconciliation 2026-09-20 — the flag-and-bump answer, and audit M2 closed

`trade-network/landing-order.md` recorded this program's first family row as *"none stated by its specs
(owner confirms; `legion-build-map.md:117` vs `spec-member-stack.md:253` still disagree — M2)"*. The
reconciliation of 2026-09-20 closes M2, and the answer is that **both citations were right about different
things**:

- **§13 A-LB6 was right about the module.** `member-stack` takes **no bump and no re-bless of its own**:
  `count=` is emitted only when `Count != 1` and `id=` only when `MemberId != m{i}`, and the only producer
  of `Count > 1` is gated behind `StackCombatantLanded` in the next wave. At its landing its behaviour is
  arithmetically today's, so it grants nothing. Registering a `legion.stacks` flag beside it would gate
  behaviour arriving a wave later — the flag-spans-waves breach landing-order R1 forbids.
- **§4 (and §14 C1) was right about the rule.** Every feature-granting module **rides its wave's** single
  bump and never claims "no bump".

The two only looked contradictory because the question was being asked per module. **C1's question is asked
per *wave*: does this wave grant a capability?** Asked that way:

- **The first wave (family row 0e) is not an R3 wave.** `role-aware-placement` makes an existing world's
  stored command log resolve a siege differently — a template bearer at `WorldTemplateCatalog.cs:196` stops
  fighting — which is exactly the mid-life rule change R1 exists to stop. So the wave takes **one flag,
  `legion.rolePlacement`, registered by `role-aware-placement`, and one bump**; `member-stack` rides that
  bump and registers nothing, and `caravan-kind-retire` adds nothing.
- **Three waves carry two capability rows each** (`legion.stacks` + `legion.standingOrders`;
  `legion.escortStance` + `legion.traditions`; `legion.standards` + `legion.doctrine`). Landing-order R2
  allows it explicitly — several independently-gated surfaces in one wave **share** that wave's one bump —
  and family row 15's four rows on one bump is the precedent. No wave here takes two bumps and no flag
  spans two waves.

**Every legion wave now has a row in `landing-order.md` §2**, with its flag, its bump ordinal in the legion
lane (`L1`…`L10`) and the family row it lands after — so `standing-orders`, `escort-stance`,
`field-battle-kinds` and `legion-power`, which `fleet`, `trade-ai` and `rift-trade` all read, finally have a
place in the family order. Three planning fragments could not sequence against them before.

### Closed-cycle landing note (global audit M1)

M1 listed `escort-stance` ↔ `field-battle-kinds` as a cycle inside this program (`escort-stance`'s battle
presence clause needs the engine route; `field-battle-kinds` reads `escort-stance` for its join predicate).
**Landing note, one line, so it is not a cycle in practice:** `escort-stance` lands **first** in wave 3 with
its battle-presence clause **inert** (an escorting legion is never joined into a fight, because no sector, lane
or guard fight resolves yet — the refusal at `BattleSeam` stands); `field-battle-kinds` (wave 4) wires the
join predicate in its own change and carries the turn-golden re-bless for it. Neither spec waits on the other
to be written, and no capability flag spans both (C1: two waves, two bumps).

### DESIGN-GATE §5 (this round)

`[x]` Read this session: the register's Round 6 (whole), the global audit (C1–C3, M1–M8, minor table), this
map and every spec edited · `[x]` Verified against code: `TurnEngine.cs:125` (`RulesetVersion` 13),
`:134-140` (command-only precedent), `WorldCanonical.cs:71-72` (default-suppressed hashing),
`LegionSupply.cs:16-25` (per-member burn), `ScopedInventoryPolicy.cs:39-49` (cargo capacity from count),
`PowerVector.cs:18-19` (`int` fields) · `[x]` citation audit run on every edited file · `[ ]` no suite run
(documents only) · `[~]` session boundary: the caller's fence (this map, `legion-build/**` and the other six
named trees) · `[x]` corrections propagated (§4, §5.11, §5.16, §5.17, §10 S1, §13 R1 and the owner question) ·
`[x]` no population pinned · `[x]` no actor magnitude composed outside Hub (D2's roll-up sums Hub output) ·
`[x]` no cap added (the upkeep is a per-turn rate, the banked draw a source, a short pay a refusal) ·
`[x]` no magic number (every new value is a named tunable with a home file).

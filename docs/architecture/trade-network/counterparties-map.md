# Capability Map: counterparties

**Status: APPROVED 2026-09-19** (owner). Owner decisions are recorded in *Owner decisions (2026-09-19)* below; module specs are written.
**Reconciled with the round-4 owner decisions 2026-09-19** ([decisions-round-4.md](decisions-round-4.md)) — see *Reconciliation 2026-09-19 (round 4)* at the end; where this map and that register disagree, the register wins.
**Program:** `trade-network` sub-program 5, `counterparties` ([trade-network-ideal.md](../trade-network-ideal.md) §11).
**Ideal:** [trade-network-ideal.md](../trade-network-ideal.md) §7.4, §7.5, §7.7 (the facts this map records), §14b.
**Specs:** `docs/architecture/trade-network/counterparties/spec-<module-id>.md` (umbrella §6) — [need-vector](counterparties/spec-need-vector.md) · [empire-roster](counterparties/spec-empire-roster.md) · [diplomacy-facts](counterparties/spec-diplomacy-facts.md) · [empire-treasury](counterparties/spec-empire-treasury.md) · [trade-difficulty-knobs](counterparties/spec-trade-difficulty-knobs.md) · [diplomatic-stance](counterparties/spec-diplomatic-stance.md) · [relation-facts](counterparties/spec-relation-facts.md) · [clan-seeding](counterparties/spec-clan-seeding.md) · [clan-economy](counterparties/spec-clan-economy.md) · [empire-goods-sinks](counterparties/spec-empire-goods-sinks.md) · [conquest-consequences](counterparties/spec-conquest-consequences.md).
**Plan:** `tasks/trade-network-counterparties-plan.md` / `tasks/trade-network-counterparties-todo.md` (written after approval).
**Siblings in this directory:** [exchange-map.md](exchange-map.md) (sub-program 6) and [trade-ai-map.md](trade-ai-map.md) (sub-program 7) consume this map's modules.

## What this sub-program is

The people you trade with and fight: **many enemy empires per world**, **neutral clans** that produce and
consume their own goods, the **per-world treasury** each AI empire banks into, the **real need vector**
every AI decision and every hub's demand reads, the **war/peace state** and the **relation facts** that
feed the one four-band ladder, and what **conquest** does to all of them. It owns no price and no treaty
kind (those are `exchange`), and it decides nothing for an AI (that is `trade-ai`).

Player vocabulary on every surface: *enemy empires*, *the dominant enemy empire*, *clans*, *treaty*,
*war*, *peace*. Code identifiers that carry legacy names (`WorldFactionKind.Zomboss`) are untouched,
per `ip-censor-ideal.md` §6.1a; no new identifier or prose here uses them.

## Assumptions (correct before approving)

1. **Model-free.** Every module here is deterministic C# plus tuning. Clan and empire *names* are
   content from `empire-seed` / `narrative`; this map needs none of them to build or test.
2. **One relation ladder.** The band is `npc-story-events`' `relation-ledger` (four bands `eager, open,
   wary, hostile`, `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`). This map writes facts into it and
   reads the band out. It never stores a relation number.
3. **P13 for relation reads.** The step never reads the Data-side story ledger. The band a turn uses is
   a **logged step input**: a per-pair band snapshot taken at commit, stored with the turn's commands,
   replayed from the log (ideal §14b *"disposition facts that trade reads are world-hashed state, or
   logged inputs to the step"* — this map picks the logged-input half, because the ledger lives in Data
   and is owned by another program).
4. **The per-world stamp exists first.** Every behaviour change here rides `trade-foundation`'s
   per-world ruleset stamp (ideal §14 D-C). Worlds stamped before this sub-program replay byte-identically.
5. **Numbers are tunables** in `data/tuning/trade.v1.json` (new) and `data/tuning/diplomacy.v1.json` (new),
   decided by principle at spec time, never owner questions.

## What the code says (verified 2026-09-19)

| Fact | Where |
|---|---|
| `Clan` and `Rival` faction kinds exist; a clan *"defends its ground, never expands"* | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18` |
| Only two policies exist: `stand-fast` and `frontier-rules` | `gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18` |
| No template seeds a clan or a rival; both seed player + dominant enemy empire + wild | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:78-83`, `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:26-30` |
| `INeedVector` reads only a slot kind and an element — there is no per-good axis | `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:15-22` |
| `UniformNeeds` returns 1000 for everything and is the default | `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31-41`, `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:67` |
| `ValueMap.For` already accepts a need vector; its only caller passes none | `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:59-64`, `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:60` |
| `PolicyId` is inside the state hash | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:28-29` |
| The AI fill runs every policy faction in ordinal order, each on its own seed stream | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:218-245` |
| **Every other faction is hostile, always.** Hostility is `factionA != factionB`; there is no peace state | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16` |
| Three sites compare owner ids directly where they mean hostility, outside the one rule: assault target and defender, and the `raise` contest check *(added at spec time)* | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultPhase.cs:66-70`, `:76-78`; `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:75-80` |
| Its six direct callers: contact (lane and sector), the held-against test (itself called by claims, march, supply twice), believed supply, threat, the Finish rule | `gk-core/src/FusionRpg.Core/World/Movement/ContactResolver.cs:94`, `:120`; `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:37`; `gk-core/src/FusionRpg.Core/World/Ai/BelievedSupply.cs:64`; `gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs:71`; `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:235` |
| A faction with no loam source anywhere pays **no upkeep at all** (rule G-C) | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:51-58` |
| Upkeep has no structure term | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:34` |
| Capture is `ClaimResolver`: ownership, slots and warden binding change hands in Snapshot | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:94-118` |
| Souls are a player-keyed wallet; an AI faction has no soul balance | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:145-149` |
| `rpg_worlds.ruleset_version` exists and is always 1 | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:31` |
| A faction handicap is a declared, hashed per-mille lever (`UpkeepHandicapMilli`) | `gk-core/src/FusionRpg.Core/World/WorldState.cs:83` |
| No difficulty profile exists anywhere in the world tree | `grep -rn difficulty gk-core/src/FusionRpg.Core/World` — only comments saying something *is not* a difficulty setting |

## Modules

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `need-vector` | The real `INeedVector`: per-good want derived from stock against demand, one rule on truth and belief | `trade-foundation` stamp; `sector-yield` located goods | 1 |
| 2 | `empire-roster` | Many enemy empires per world: `Rival`-kind factions with personality policy ids, validation, seeding | `trade-foundation` stamp | 1 |
| 3 | `diplomacy-facts` | The hashed, append-only per-pair diplomacy fact list inside `WorldState` (12 kinds, offers included) | `trade-foundation` stamp | 1 |
| 4 | `empire-treasury` | Per-world hashed treasury per AI empire; the AI's banking destination; unlocated (**owned by this program**, owner 2026-09-19) | `sector-yield` `banking-fact` destination seam (A11) | 1 |
| 5 | `trade-difficulty-knobs` | The trade rows of the per-world difficulty profile: loss rates, AI bidding, AI spend limit | `trade-foundation` stamp (profile id) | 1 |
| 6 | `diplomatic-stance` | War/peace per pair derived from facts; `ZoneOfControl.IsHostile` becomes its read | `diplomacy-facts` | 2 |
| 7 | `relation-facts` | Emits `war.declared`, `treaty.broken`, `trade.fulfilled` (capped per pair per turn), `treaty.imposed`, `clan.conquered` into the one ladder; logs the band snapshot the step reads | `diplomacy-facts`; `npc-story-events` `relation-ledger` | 2 |
| 8 | `clan-seeding` | Clans on the map: placement, a hub site, a loam source, personality computed from climate and species | `empire-roster`, `need-vector` | 2 |
| 9 | `clan-economy` | Clan production under the shared rules, clan consumption from its own needs, clan upkeep — no free faucet | `clan-seeding`, `need-vector`; `sector-yield` | 3 |
| 10 | `empire-goods-sinks` | The compound structure goods cost every empire pays from its banked goods, so an AI treasury cannot only grow; symmetry checks on `legion-build`'s located-goods sinks | `empire-treasury`, `need-vector`; `empire-seed` cost bands | 3 |
| 11 | `conquest-consequences` | What capture does: clan hub closed, clan production ends, every clan's relation moves, collapse destroys a treasury — one pass at the end of `Snapshot` | `diplomatic-stance`, `relation-facts`, `clan-economy`, `empire-treasury` | 3 |

**Build order:** (`need-vector` ∥ `empire-roster` ∥ `diplomacy-facts` ∥ `empire-treasury` ∥
`trade-difficulty-knobs`) → (`diplomatic-stance` ∥ `relation-facts` ∥ `clan-seeding`) →
(`clan-economy` ∥ `empire-goods-sinks`) → `conquest-consequences`.

**Dependency direction:** nothing here depends on `exchange` or `trade-ai`. `exchange` reads
`need-vector` (hub demand), `diplomacy-facts` and the logged band (Access), and writes treaty facts through
`diplomacy-facts`' API; `trade-ai` reads everything here through `IWorldView`.

**External dependencies (module ids from the sibling maps in this directory where they exist):**
`trade-foundation` `world-stamp` (per-world stamp incl. difficulty profile id), `ledger-keys`,
`world-stock-ledger`, `economy-report`, `synthetic-graph` · `logistics-flow` `logistics-phase` (the
phase slot; this map's `clan-economy` pass runs after arrivals, `logistics-flow-map.md` *Phase-internal
order*), `auto-banking` (an AI empire's banking facts land in `empire-treasury`), `path-cache` (its
graph-version trigger on a hostility change) · `sector-yield` (located goods, warehouse axis, bank
points, the `LoamUpkeep` structure term; no map yet) · `legion-build` (legion equipment as a counted
stock and its production; no map yet) · `trade-stories` `seasonal-demand-shocks` (a demand term fed into
`need-vector`), `trade-fact-source` (see C5) · `npc-story-events` `relation-ledger` and `story-ledger` ·
`world-map-program` `ai-commander` (the commander loop, `IWorldView`) · `world-continuity` W7 (one
difficulty profile per world; it owns the profile catalog).

---

## Module detail

### 1. `need-vector`

**Capability.** One deterministic function that says how badly a faction wants one more unit of each good,
per-mille against a neutral 1000 — the same shape `INeedVector` already documents. It is derived from the
faction's own located and treasury stock against a **demand** built from its climate, its species, its
planned sinks (compound building costs, legion equipment, clan consumption) and seasons. It is **the
SSOT for demand**: a hub's local demand (`exchange`), every AI valuation (`trade-ai`), `sector-development`
and empire progression all read it (ideal §14b: *"`counterparties` owns it"*). Truth side (inside `step`,
for hub demand) and belief side (AI, outside `step`) call the same rule with different inputs — the
`SupplyReach` precedent — never two copies. Own-faction stock is never fogged (holding ground grants full
sight, `world-map-program.md` line 46).

- **Built:** the interface and its per-mille contract (`gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:15-22`);
  `ValueMap.For` already multiplies yield by it (`gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:137-153`).
- **Wiring gap:** `FrontierRulesPolicy` calls `ValueMap.For(view, defensive, reach)` without needs, so the
  stub is always used (`gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:60`).
- **Real gap:** no per-good axis (`ForGood(goodId)`); no demand derivation; nothing to derive from until
  `sector-yield` lands located stock.
- **Touches:** `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs` (widen with a per-good read — a reviewed
  interface change), `src/FusionRpg.Core/World/Trade/Needs/` (new), `FrontierRulesPolicy.cs:60` (pass it).
- **Acceptance (contract):**
  - Pure: same `(world or view, faction, turn)` gives the same vector, byte for byte; no wall clock, no
    `System.Random` (inherits `WorldDeterminismGuardTests`).
  - Monotone: raising a faction's stock of a good never raises its want of that good; raising its demand
    never lowers it.
  - A faction whose stock equals its demand for a good reads exactly 1000 for it.
  - Truth side and belief side return the same vector for the faction's own stock (own ground is never
    fogged).
  - `ForSlotKind`/`ForElement` stay answerable and agree with `ForGood` over the goods a slot kind and an
    element produce — one source, three reads.
  - Every demand coefficient is a `trade.v1.json` key; a missing key rejects the load (T5).
  - Demand is a sum of registered **demand terms** (climate, species, season, planned sinks, and
    `trade-stories`' `seasonal-demand-shocks`); a new term registers into the one function and never
    writes a price or a second demand table.
  - *Spec-time (2026-09-19):* this module ships climate, species (keyed by **element**, never species id)
    and season; `planned-sinks` is registered later by `empire-goods-sinks` and shocks by `trade-stories`,
    so no arrow points back. Clan consumption reads the vector's demand; it registers no term.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade, World/Ai filters) through
  `verify-change.py -Paths`; `WorldDeterminismGuardTests` in `FusionRpg.Guard.Tests`.

### 2. `empire-roster`

**Capability.** A world holds **many enemy empires**: the dominant enemy empire (the win condition,
kind `zomboss` in code) plus any number of `Rival`-kind empires, each with a **personality policy id**.
Personality is a policy id plus a row of weights (trade appetite, war appetite, treaty willingness), never
a per-empire script. Every empire runs the same goods economy (ideal principle 10). Validation rejects an
unknown policy id, as it already does. Before `world-generator` exists, a synthetic multi-empire fixture
(from `trade-foundation`'s graph builder) exercises every many-empire path; `two-hearths` v2 gains one
rival (owner decision Q2). Round-4 Q5 adds a clan to **both** shipped templates (`clan-seeding`); roster
rule 3 applies to an empire that holds ground at creation, so `first-light`'s landless dominant enemy empire
passes (C15).

- **Built:** the `Rival` kind (`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:14-15`); hashed
  `PolicyId` (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:28-29`); the AI fill already iterates every
  policy faction with an independent stream, so adding one moves no other
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:225-245`).
- **Wiring gap:** no template or fixture seeds a `Rival`; `FactionPolicies` knows two ids only
  (`gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18`).
- **Real gap:** personality weights; the policy ids that carry them (registered by `trade-ai`, catalogued
  here).
- **Touches:** `FactionPolicies.cs` registrations (ids only), `WorldValidation`, template/fixture data,
  `data/tuning/trade.v1.json` (new) `personality` block.
- **Acceptance (contract):**
  - A world with N enemy empires validates for any N ≥ 1; exactly one is the dominant enemy empire.
  - Adding an empire to a world leaves every other faction's AI commands byte-identical (stream
    independence, already true for the fill; asserted for the new kind).
  - An unknown personality policy id is a load rejection, never a silent default.
  - Old-stamp worlds replay byte-identically.
- **Verification boundary:** `FusionRpg.Core.Tests` (World), `FusionRpg.Data.Tests` (world commit fill).

### 3. `diplomacy-facts`

**Capability.** An append-only list of **diplomacy facts per faction pair**, inside `WorldState` so it is
hashed and replayed: `war.declared`, `peace.made`, `treaty.signed`, `treaty.ended`, `treaty.broken`,
`treaty.imposed`, `embargo.set`, `embargo.lifted`, `bloc.joined`, `bloc.left`. Each fact carries
`(turn, kind, grantor, grantee or bloc id, treaty kind id where relevant, minimum term)`. It is written only
by the step (from admitted commands owned by `diplomatic-stance` here and `treaty-lifecycle` in
`exchange`) and read by `Access` (`exchange`), the stance (§6) and the AI through `IWorldView`.
Diplomacy is public: a declaration or treaty is known to every faction, so belief carries it unfogged.
Canonical form is sparse (facts only), per §14b.

- **Built:** hashed faction state and the canonical writer pattern (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:28-29`).
- **Wiring gap:** —
- **Real gap:** the whole fact list; its canonical rows; its `IWorldView` projection.
- **Touches:** `gk-core/src/FusionRpg.Core/World/WorldState.cs` (new list), `WorldCanonical.cs`,
  `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs` (projection), `src/FusionRpg.Core/World/Diplomacy/` (new).
- **Acceptance (contract):**
  - Facts are append-only: no step removes or rewrites a fact; replay of the command log rebuilds the
    list byte for byte.
  - Fact kinds are a **closed vocabulary** (12 — the ten above plus `offer.made` and `offer.declined`,
    added at spec time so peace and treaty offers share one store; pinned because the code owns the list
    and a new kind is a reviewed change); an unknown kind is a load rejection.
  - Facts are appended only in `Snapshot`, after its resolvers, so a fact filed on turn N acts from N + 1.
  - Each fact's pair key is ordered `(ordinal lower, ordinal higher)` for bilateral kinds and
    `(actor, target)` for one-sided kinds, so a pair has one key.
  - A world with an empty list hashes exactly as a pre-module world with the same state (no field written
    when empty).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Diplomacy, hash tests).

### 4. `empire-treasury`

**Capability.** Each AI empire (dominant or rival; not clans, not the wild) holds a **per-world treasury**:
a sparse per-good balance in hashed world state, where goods reaching that empire's bank points land
(the AI's equivalent of banking). It is **unlocated** — ideal principle 9 applied symmetrically
(principle 10): capturing a sector never hands over an empire's treasury. It is world-scoped and never
feeds an account path (it belongs to an AI). Its only drains are `empire-goods-sinks` and collapse (§11) —
`exchange` settlement never reads or writes a treasury (E-A12, C16). Its only faucet is banking at the
empire's **Counting Houses** (round 4 B). It holds **located-material-class goods only** (the class `sector-yield` lands in the
registry, ideal §14b); rubble and ironwork stay in sector stocks.

- **Built:** hashed per-faction rows (`gk-core/src/FusionRpg.Core/World/WorldState.cs:70-94`).
- **Wiring gap:** —
- **Real gap:** the treasury itself; the AI destination it registers into `sector-yield` `banking-fact`'s
  destination seam (A11). `logistics-flow` never touches a treasury (its C7). **Owner decision
  2026-09-19: this program owns the AI-empire treasury** and its registry row.
- **Touches:** `WorldState.cs`, `WorldCanonical.cs`, `src/FusionRpg.Core/World/Trade/Treasury/` (new).
- **Acceptance (contract):**
  - Every balance is a `long`; every add/subtract is `checked`; a negative balance is impossible (a spend
    beyond balance is refused, never clamped).
  - Capture of any sector, including a seat, leaves the treasury unchanged.
  - The player faction has no treasury row (the player banks to the wallet); a clan has none.
  - Sparse canonical form: a zero balance writes no row.
  - Net change over a turn equals banked-in minus sinks minus destroyed, asserted per turn
    (reconciliation, not a population count). *(Said "minus payments" until the 2026-09-20 audit; settlement
    never touches a treasury, C16.)*
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade).

### 5. `trade-difficulty-knobs`

**Capability.** The trade rows of the world's one difficulty profile (world-continuity W7): a lane-loss
multiplier, an AI bidding aggressiveness, and the AI per-turn spend limit that `trade-ai` enforces. The
profile id lives in the per-world stamp (`trade-foundation`); this module owns the three rows and their
loader. **Symmetric by default** — a knob that binds only the player is a handicap and is declared in the
turn report, the `UpkeepHandicapMilli` precedent (`gk-core/src/FusionRpg.Core/World/WorldState.cs:83`). v1 ships
one default profile. Difficulty is policy parameters, not stat bonuses (`spec-ai-commander.md` assumption 3).

- **Built:** the declared-handicap precedent (above).
- **Wiring gap:** —
- **Real gap:** any difficulty profile; these rows.
- **Touches:** `data/tuning/trade.v1.json` (new) `difficulty.<profileId>` block; loader in
  `src/FusionRpg.Core/World/Trade/` (new).
- **Acceptance (contract):** a missing profile or key rejects the load; the default profile reproduces the
  un-knobbed arithmetic exactly (multiplier 1000‰); a non-default knob that applies to one faction only
  writes a handicap line in the turn report.
- **Verification boundary:** `FusionRpg.Core.Tests` (tuning loader).

### 6. `diplomatic-stance`

**Capability.** Per faction pair, **war or peace**, derived from `diplomacy-facts` (never stored): the last
`war.declared` / `peace.made` decides. `ZoneOfControl.IsHostile` stays **the one hostility rule** and
becomes a read of this stance — every one of its callers keeps calling it, so contact, zone of control,
supply and threat change together (one rule, not a second). Owns the commands `war-declare` and
`peace-offer` / `peace-accept` (a peace term may impose `market`, which `exchange` records as
`treaty.imposed`). **Round 4:** the locked pair is the player and the dominant enemy empire **only** (Q4 —
it may make peace and treat with rivals and clans); and diplomacy with an **empire** needs an **Embassy**
(T1: peace offers and treaties; T2 **Consulate**: blocs and embargoes; clans need none) — the
`DiplomacyGate` read (over `trade-foundation` `sector-features`' `diplomacy` feature) is owned here, the treaty-side checks by `exchange`
`treaty-lifecycle` (A16). War **auto-embargoes** both ways and voids treaties — both **derived** by `exchange`
`trade-access` from `war.declared`, never written. Default stance: owner decision Q1 (below). At peace,
borders are closed to legions without a passage right (`IPassageRule`, registered by `exchange`; default
closed), and claims and assaults on the peaceful owner's ground are refused.

- **Built:** the single hostility entry point with six direct call sites, plus three direct owner-id
  comparisons that mean hostility and move to the rule in this module (see *What the code says*).
- **Wiring gap:** —
- **Real gap:** a peace state. **Today every faction is permanently at war with every other**
  (`gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16`), so the ideal's `passage` treaty and
  `war.declared` fact have nothing to change until this lands.
- **Touches:** `ZoneOfControl.cs` (signature gains the world's diplomacy, or a stance lookup; all seven
  callers pass it), `WorldCommandKinds` (`war-declare`, `peace-offer`, `peace-accept`),
  `WorldCommandAdmission`. A behaviour change → gated by the per-world stamp.
- **Acceptance (contract):**
  - For every pair with no facts, the stance equals the stated default; an old-stamp world keeps
    `IsHostile(a, b) == (a != b)` exactly and replays byte-identically.
  - At peace, two factions' legions sharing a sector raise no contact battle and project no zone of
    control on each other; at war, behaviour is today's. Asserted for each of the seven callers.
  - `war.declared` voids every treaty and embargo fact state for that pair in the same turn (derived, not
    deleted) and sets a mutual embargo.
  - Order-independent: a declaration and a peace or treaty for one pair in one turn — **war dominates**
    whatever the filing order; the test covers both filing orders.
  - The AI believes the true stance (diplomacy is public) — belief-side and truth-side agree.
  - A turn that changes any pair's stance bumps `logistics-flow`'s graph version in the same step, so
    `path-cache` never serves a route across ground whose hostility changed (that map's ask A4; the
    edge where the cache's key set moves, DESIGN-GATE §2.16).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Movement, World/Ai, World/Diplomacy); any
  campaign scenario test whose behaviour moves is run and reported, never assumed
  (`spec-ai-commander.md` §Momentum point 4 precedent).

### 7. `relation-facts`

**Capability.** The bridge to the one ladder. After each committed turn it emits relation facts into
`npc-story-events`' story ledger, world scope, keyed by a durable fact id: `war.declared`, `treaty.broken`
(the breaker's band drops with the partner and, less, with every observer that holds a treaty with it;
then a truce period), `trade.fulfilled` (**capped per pair per turn** — a structural pacing limit, commented
as such), `treaty.imposed`, and `clan.conquered` (moves every clan's band toward the conqueror). Before each
turn's step it takes the **band snapshot** per pair from `relation-ledger` and logs it with the turn's
commands, so the step reads a logged input (assumption 3; **owner decision 2026-09-19**). Band shift per
fact kind is `npc-story-events`' tuning; the per-pair cap is `diplomacy.v1.json` (new). Observers get their
own kind, `treaty.break-witnessed`, instead of a per-mille share (the ladder sums whole steps, A8). **This
module owns the commit-time projection point** (owner decision 2026-09-19); `trade-stories`'
`trade-fact-source` registers into it.

- **Built:** the ladder's registry (`gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`); the turn commit
  already resolves Data-side work after `Step` inside one transaction (the cargo precedent,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs:131`).
- **Wiring gap:** —
- **Real gap:** `story-ledger` and `relation-ledger` are unbuilt (`npc-story-events-map.md` modules 4 and
  5); the snapshot row and its replay read.
- **Touches:** `gk-core/src/FusionRpg.Data/Sqlite/` (a snapshot table beside `rpg_world_commands`, fact emission
  in the commit), `src/FusionRpg.Core/World/Diplomacy/` (new, fact mapping).
- **Acceptance (contract):**
  - Replay reads the logged snapshot and never the live ledger: deleting ledger rows after a turn leaves
    that turn's replay hash unchanged.
  - Every emitted fact carries a dedupe key `(save_id, world_id, turn, factKind, pair)` plus an ordinal
    `i < cap` for `trade.fulfilled` (`spec-relation-facts.md` §2 — without it a cap above 1 would collide on
    the key; stated here by the 2026-09-20 audit); re-committing a turn emits nothing new.
  - `trade.fulfilled` emits at most `cap` facts per pair per turn regardless of fill count; the cap is a
    tunable read, and the comment names it structural.
  - No fact is emitted by the passage of time: a turn with no qualifying event emits no relation fact
    (facts-only, ideal §6.4).
  - Facts are keyed by **faction pair**, so AI↔AI bands exist (filed ask A1 below).
- **Verification boundary:** `FusionRpg.Data.Tests` (world commit), `FusionRpg.Core.Tests` (mapping).

### 8. `clan-seeding`

**Capability.** Clans exist on the map: each is a `Clan`-kind faction holding one or a few sectors with a
**hub site** carrying a seeded, working **Trading Post** (the trade building at tier 1 — round 4 B), a
**seat** and a **loam source**, so the shared upkeep and
supply rules charge it (C2; **owner decision 2026-09-19: every clan is seeded with a loam source**; the seat
closes the matching supply exemption by principle 10). Its **personality** — the goods it craves and pays a premium for — is **computed
from climate and species** through `need-vector`, never authored per clan (`world-graph-ideal.md` §8.2,
*"a clan's price is its personality"*). It runs a `clan-keeper` policy (defend, never expand — the kind's
own contract) registered by `trade-ai`. Placement enters the world generator's constraint table
(`world-map-program` wave 4); v1 seeds clans through the per-world stamp's template version and the
synthetic fixture — **both** shipped templates gain one clan at their v2 (round-4 Q5). Clan trade opens when
the **player** builds a Trading Post; the band sets the spread and blocks only at `hostile` (round 4).

- **Built:** the `Clan` kind and its contract (`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:12-13`).
- **Wiring gap:** never seeded; no policy.
- **Real gap:** placement rules, the personality computation, template/generator entries.
- **Touches:** template data (stamped), generator constraint table (filed), `src/FusionRpg.Core/World/Trade/Clans/` (new).
- **Acceptance (contract):** every seeded clan holds ≥1 sector with a hub site carrying a working tier-1
  Trading Post, a seat and a loam source; two clans
  with the same climate and species read the same personality; personality is recomputed from state,
  never stored; a world with zero clans still validates and plays.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade).

### 9. `clan-economy`

**Capability.** A clan's goods come **only** from its own sector production under the rules every faction
uses (`sector-yield`), never from a refill (ideal §10 C4). It **consumes** from its own needs every turn —
a sink proportional to what it holds — and **pays the same loam upkeep**. Its production and consumption
enter the P1 net-flow line of the world economy report (`trade-foundation`). The result: a clan's surplus
is bounded by its production minus its consumption, so it is never a free faucet (ideal §14b).

- **Built:** —
- **Wiring gap:** —
- **Real gap:** everything; it rides `sector-yield`'s production and warehouse.
- **Touches:** `src/FusionRpg.Core/World/Trade/Clans/` (new); a consumption pass in the Logistics phase
  (`logistics-flow` owns the phase, this module owns the pass).
- **Acceptance (contract):**
  - Over any turn, `Δclan stock = production − consumption − sold + bought − upkeep-driven losses`,
    reconciled per clan per good.
  - A clan with no production and no purchases ends every turn with stock ≤ the turn before.
  - The world economy report's P1 net flow includes a clan line; the report is a test in the determinism
    suite (economy-principles §13), asserting the reconciliation, never a count of clans or goods.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade, economy report).

### 10. `empire-goods-sinks`

**Capability.** The world-scoped goods sinks **every empire** pays, so an AI treasury has somewhere to go
and Shape B throttles AI empires the same way it throttles the player (ideal principle 10, §10 C3):
compound structure costs (essence beside loam — designed in `empire-economy-ssot.md` §2, unbuilt),
legion equipment production and fitting (`legion-build-ideal.md` §6.7), and a doctrine's goods upkeep
(`legion-build-ideal.md` §6.5). A sink added here applies to the player's equivalent action too, or it is
declared as a handicap. **Siege preparation is not a v1 sink** — see contradiction C3. *Spec-time correction:* legion equipment
production and doctrine upkeep consume **located** goods where the legion stands (`legion-build-ideal.md`
§6.5, §6.7), so they are `legion-build`'s sinks; this module owns the compound structure cost paid from
banked goods (player wallet, AI treasury) and asserts the symmetry of the located-goods sinks.

- **Built:** —
- **Wiring gap:** compound building cost is designed but no structure cost reads essence
  (`empire-economy-ssot.md` §2).
- **Real gap:** every goods sink on the map.
- **Touches:** structure cost resolution (`BuildResolver`, through `empire-seed`'s `costProfile` bands),
  `legion-build`'s production hook, `src/FusionRpg.Core/World/Trade/Treasury/` (new).
- **Acceptance (contract):** every sink names its faucet (P1) in the same change; each sink applies to
  every empire kind; an AI empire's treasury over a scripted campaign is not monotone increasing
  (economy-principles §13, net flow oscillates); sink share by reason is reported, not asserted as a count.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Trade, economy report).

### 11. `conquest-consequences`

**Capability.** What capture means for counterparties, hooked where capture already happens
(`ClaimResolver` in Snapshot, and the assault path): capturing a **clan** sector closes its hub, ends
clan production there and writes `clan.conquered`; capturing an **empire** sector transfers its warehouse
with the sector (`sector-yield` rule) and never its treasury; an empire that loses its last seat
**collapses** — its treasury is destroyed (a sink, principle 9 applied symmetrically), its treaties end,
routes through its ground follow `cargo-fate`. Goods in transit on a captured counterparty's route follow
`cargo-fate` (ideal §7.6). `world-graph-ideal.md` §8.2 already lists Conquest as a designed clan option.

- **Built:** the capture site (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:94-118`).
- **Wiring gap:** —
- **Real gap:** every consequence above.
- **Touches:** `TurnEngine.Snapshot` (one pass at its end over opening-versus-now ownership, so fade in
  `Pressure` is seen as well as claims; `ClaimResolver.cs` is not edited — spec-time correction),
  `src/FusionRpg.Core/World/Trade/` (new).
- **Acceptance (contract):** capture of a clan sector closes its hub the same turn and its production the
  next; the treasury of a surviving empire is identical before and after losing any sector; a collapsed
  empire's treasury is zero and the destroyed amount is a sink line in the economy report; no consequence
  runs for an old-stamp world.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Movement, World/Trade).

---

## Filed asks (other programs)

| # | To | Ask |
|---|---|---|
| A1 | `npc-story-events` `relation-ledger` | Key faction relation facts by **faction pair**, not only toward the player, so AI↔AI bands exist for AI-to-AI treaties (ideal §7.7 scores AI-to-AI proposals with the same function) |
| A2 | `npc-story-events` `relation-ledger` | A read of the band per pair **as of the end of turn N−1** (facts whose source turn ≤ N−1), Data-side and usable inside the commit transaction, for the logged snapshot and the AI fill |
| A3 | `world-map-program` `world-generator` | Constraint rows: every clan with a hub site, a seat and a loam source; every empire with a seat and a loam source; clan and rival ground off every shortest path between the player's homeworld and the dominant enemy empire's seat; N enemy empires per size tier |
| A4 | `trade-foundation` | The per-world stamp carries the difficulty profile id and the template version; `WorldTemplateCatalog.Build` takes the stamped template version so a legacy world rebuilds its old content; the synthetic graph builder seeds **exactly one** dominant enemy empire plus N rivals and M clans, each meeting `empire-roster` / `clan-seeding` validation; the capability flags join the closed flag registry — **per wave, per round 6 C1** (see the Round 6 section below): wave 1 `counterparties.{needs,roster,diplomacy,treasury}` sharing one bump, wave 2 `counterparties.{stance,clans}` sharing one, wave 3 `counterparties.{clanEconomy,sinks,conquest}` sharing one. The single `counterparties.diplomacy` over waves 1–2 and the single `counterparties.clans` over waves 2–3 are withdrawn |
| A5 | `world-map-program` `ai-commander` | `spec-ai-commander.md:284` (*"no diplomacy"*) is amended for this program (ideal §7.7) |
| A6 | `npc-story-events` `narrative-vocabulary` | `relation.baseBandByFactionKind.Rival` = `wary` (owner decision Q1); the draft has `hostile` |
| A7 | `npc-story-events` `narrative-vocabulary` | Faction relation fact kinds with their `shiftByFactKind` rows: `war.declared`, `treaty.broken`, `treaty.break-witnessed`, `treaty.imposed`, `trade.fulfilled`, `clan.conquered` |
| A8 | `npc-story-events` `relation-ledger` | Sum per-mille steps and divide once after the sum, so a small fact (`trade.fulfilled`) can weigh less than a whole band; until then its shift is tuned to 0 |
| A9 | `exchange` (`exchange-hub`, `trade-access`, `treaty-lifecycle`) | Serve a clan's hub on its `Market` slot; derive hub closure from ownership; derive treaty voiding and a mutual embargo from `war.declared`, and closed access for a collapsed empire (`Collapse.IsCollapsed`); use `diplomacy-facts`' offer kinds and `WorldCommand.TargetFactionId`; register the real `IPassageRule` |
| A10 | `trade-foundation` `ledger-keys` / `stock-deltas` | Widen the fact-kind list with `sink`, `collapse`, `consume`; a holder for an unlocated treasury. **Answered** (`spec-ledger-keys.md` §4a): the holder is `f:<factionId>` with `StockHolderKind.Faction`, not a sentinel sector value (re-worded by the 2026-09-20 audit) |
| A11 | `sector-yield` `banking-fact` | Expose an `IBankingDestination` seam and own only the player's destination; do not write an AI treasury field or its registry row (owner decision: `counterparties` owns the treasury) |
| A12 | `logistics-flow` `logistics-phase` | Place the `clan-economy` consumption pass after `exchange` settlement in the phase-internal order |
| A13 | `exchange` `settlement-payment` | Reuse `empire-goods-sinks`' logged pre-step verdict shape for the souls reservation, rather than a second reservation mechanism. *(Superseded 2026-09-19 by `exchange`'s E-A7: the soul budget is a section of `relation-facts`' one logged step-input record — accepted, `spec-relation-facts.md` §3.)* |
| A14 | `trade-foundation` `sector-features` (§2.11) | **Round 4:** `DiplomacyGate` (the `diplomacy` feature's tier) and `clan-seeding` (a seeded tier-1 `trade`-feature building) need a placed-structure tier and a feature per structure. **Answered** by `trade-foundation/spec-sector-features.md` (`SectorFeatures.TierOf`, `WorldSlot.StructureTier` default 1) |
| A15 | `empire-seed` `trade-structure-rows` | **Round 4:** an **Embassy** row with two tier variants (Embassy T1, Consulate T2), `feature: diplomacy`, and magnitudes through bands; the tier-1 **Trading Post** variant of the trade building must exist before `clan-seeding` can seed it. `spec-trade-structure-rows.md` §5.1 has no diplomacy row — by its own rule a deficit. **Its structure role** (asked by `exchange` E-A15): recommended **`Enable`**, one of the ten existing roles, whose shipped rows are the charters (`gk-data/packs/fusion/data/seed/structures/enable/district-charter.json`, `garrison-charter.json`) — a building that grants a right rather than producing, so no role widening is needed |
| A16 | `exchange` `treaty-lifecycle` |
**Round 4:** gate treaty offers and signings with an **empire** on the offerer's `DiplomacyGate.TierOf ≥ TreatiesTier` (Embassy), and `bloc.joined` / `embargo.set` on `≥ BlocsEmbargoTier` (Consulate); nothing with a clan. Read the gate from `diplomatic-stance` §9; add no second building check. **Answered** (`exchange/spec-treaty-lifecycle.md` §3a, `treaty.no-embassy`) |
| A17 | `trade-ai` (`ai-trade-buildings`, `clan-behaviour`) | **Round 4:** AI empires build their Counting House, Trading Post, Embassy and caravan buildings through the ordinary build path (principle 10 — the treasury only fills after a Counting House, `spec-empire-treasury.md` §3); `clan-keeper` builds nothing, so a clan hub stays a tier-1 Trading Post. **Answered for empires** by `trade-ai/spec-ai-trade-buildings.md` (written this round); the `clan-keeper` half stays open on `clan-behaviour` |

## Contradictions found

| # | Where | What | Recommended resolution |
|---|---|---|---|
| C1 | Ideal §7.7 vs `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16` | The ideal's `war.declared`, `passage` and peace terms presume a peace state; the code has none — every pair is always hostile | `diplomatic-stance` (module 6) makes `IsHostile` a read of a derived stance; stamp-gated. **Specced** |
| C2 | Ideal §14b (*"clans … pay the same upkeep"*) vs `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:51-58` | A faction with no loam source is exempt from all upkeep; a clan seeded without one would pay nothing | **Owner decision 2026-09-19:** every clan is seeded with a loam source. `clan-seeding` also seeds a seat, closing the parallel no-seat supply exemption (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:60-62`) by principle 10 |
| C3 | Ideal §7.4 (AI sinks include *"siege preparation"*) vs ideal §12 (v1 excludes *"warehouse goods seeding a siege depot"*) | One lists it as a sink, the other excludes it | Drop siege preparation from the v1 sink list; `empire-goods-sinks` names compound costs, legion equipment and doctrine upkeep |
| C4 | `npc-story-events-map.md` module 5 (`relation-ledger`) vs ideal §14b P13 | The ledger is a Data-side store; the step may not read it | **Owner decision 2026-09-19:** the band enters the step as a per-turn logged input (module 7). `trade-stories-map.md` raises the same point as its contradiction 4 and leaves it to this map; this is that answer |
| C5 | `trade-stories-map.md` module 2 (`trade-fact-source`) vs module 7 here (`relation-facts`) | Both project committed trade records into the story ledger at commit — two projectors for one ledger | **Owner decision 2026-09-19:** `relation-facts` owns the projection point (`ICommitFactProjector`); `trade-fact-source` registers into it |
| C6 | `trade-stories-map.md` (the `AccessIs` leaf, *"from `counterparties`"*) vs this directory's split | `Access` is owned by `exchange` (`trade-access`), not by this map; this map owns only the facts it reads | `AccessIs` reads `exchange`'s `trade-access`; `TreatyIs` reads this map's `diplomacy-facts` |
| C7 | `sector-yield-map.md` §2.9 (*"An AI empire's fact credits a per-world, hashed treasury on its faction"*, and it adds the treasury row) vs module 4 here | Two maps define the AI treasury (`logistics-flow-map.md` C7 asked for one owner) | **Owner decision 2026-09-19:** this program owns it. `banking-fact` exposes a destination seam; `empire-treasury` registers the AI destination and owns the registry row (A11) |
| C8 | Owner decision Q1 (rivals start at band `wary`) vs `npc-story-events/spec-narrative-vocabulary.md` §4 (`Rival: hostile`) | The base band disagrees | Ask A6 |
| C9 | Ideal §7.7 events and `clan.conquered` vs the ladder's five relation kinds (`spec-narrative-vocabulary.md` §3); *"a small positive relation fact"* vs whole-step arithmetic (`spec-relation-ledger.md` §2) | The ladder cannot yet express these facts or a fraction of a step | Asks A7 and A8; `trade.fulfilled` shift 0 until A8 |
| C10 | `trade-foundation-map.md` §2.1 (*"a player, several `Rival` empires, clans"*) vs `empire-roster`'s one-dominant rule | A synthetic world with no dominant enemy empire fails roster validation | Ask A4 (widened) |
| C11 | This map (*"seven call sites"*) vs the code | Six direct `IsHostile` calls; three more sites compare owner ids directly and bypass the rule (`gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultPhase.cs:66-70`, `:76-78`; `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:75-80`) | Corrected above; `diplomatic-stance` moves all three to the rule and adds a source scan |
| C12 | Module 11 (*"`ClaimResolver.cs` (a call into this module)"*) vs `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:212-224` | A hook in `ClaimResolver` misses ground lost to fade, and collapse can follow either | One pass at the end of `Snapshot` over opening-versus-now ownership; corrected above |
| C13 | Module 10's sink list vs `legion-build-ideal.md` §6.5, §6.7 | Legion equipment and doctrine upkeep consume located goods, not the treasury | They are `legion-build`'s sinks; `empire-goods-sinks` owns the compound structure cost and checks their symmetry; corrected above |
| C14 | `exchange-map.md` `treaty-lifecycle` (*"an offer is hashed state"*) vs peace offers here | Two offer stores would be a parallel path | `diplomacy-facts` carries `offer.made` / `offer.declined` for every offer (A9) |
| C15 | Round-4 Q5 (a clan on `first-light` v2) vs `empire-roster` rule 3 (*"every empire holds at world creation a Seat and a Rootbed"*) | `first-light`'s dominant enemy empire holds no sector at creation (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:83`, `:101-107`), so a roster-stamped `first-light` v2 would be rejected | Rule 3 applies to an empire that holds any sector at creation; a landless empire pays no upkeep because it has no territory (P2), not by exemption (`spec-empire-roster.md` §1) |
| C16 | Module 4 and `spec-empire-treasury.md` (trade receipts a faucet, trade payments a sink) vs `exchange` E-A12 / EC10 | An unlocated treasury paying at hubs is a channel the player lacks | Accepted: settlement never touches a treasury; P6 is met by build vs upgrade costs across the round-4 building ladders |
| C17 | Module 7 (a band snapshot table) vs `exchange` E-A7 (the soul budget is a logged step input too) | Two logged-input channels | One record, `rpg_world_step_inputs`, owned by `relation-facts`, with registered kinds (`band`, `soul-budget`) |
| C19 | An earlier draft of this reconciliation (`StructureKind.Embassy`) vs `trade-foundation/spec-sector-features.md` §1–§2 (`StructureDef.Feature`) | Two classifications of one fact | The Embassy is `Feature == diplomacy`; `DiplomacyGate` reads `SectorFeatures.TierOf` |
| C18 | `exchange-map.md` Q1 (*"Clans trade by relation band alone: `passage` from `wary`, `market` from `open`"*) vs round-4 Q1/B (*"Clan trade … opens by building a Trading Post; the band sets the spread and blocks only at `hostile`"*) | Clan `market` access from `open` would block a `wary` clan the register says is open | Not this map's file — reported as a cross-cluster conflict for `exchange` to reconcile; `clan-seeding` §6 states the round-4 rule |

## Owner decisions (2026-09-19)

| # | Decision |
|---|---|
| Q1 | **The dominant enemy empire starts at war with the player and never makes peace or a treaty, so its capital stays the win condition. Rival empires and clans start at peace, with no treaty, at band `wary`.** (`diplomatic-stance` §1; base bands via A6) |
| Q2 | **Many empires are first proven on `trade-foundation`'s synthetic worlds; then one rival is added to `two-hearths` under the per-world stamp. Scale comes from the world generator.** (`empire-roster` §3) |
| — | **The relation band enters the step as a per-turn logged input** (`relation-facts` §3; C4). |
| — | **`relation-facts` owns the projection point for facts; `trade-stories`' `trade-fact-source` registers into it** (`relation-facts` §1; C5). |
| — | **This program owns the AI-empire treasury** (`empire-treasury`; C7, A11). |
| — | **Every clan is seeded with a loam source, so the `LoamUpkeep` exemption cannot apply to it** (`clan-seeding` §1; C2). |
| Q4 (round 4) | **The dominant enemy empire never makes peace with the player only; it may treat with rivals and clans.** (`diplomatic-stance` §1 rule 3) |
| Q5 (round 4) | **Both shipped templates get a clan, plus the `two-hearths` v2 rival.** (`clan-seeding` §4; `empire-roster` §3) |
| B (round 4) | **Buildings unlock features:** clan trade opens by building a **Trading Post** (the band sets the spread; only `hostile` blocks); diplomacy with empires needs an **Embassy** (T2 **Consulate** for blocs and embargo leverage; clans need none); a bank point is a **Counting House**. (`clan-seeding` §1, §6; `diplomatic-stance` §9; `empire-treasury` §3) |

## Still open (after the specs)

O1 and O2 are **closed by round 4** (2026-09-19): **Q4** — the dominant enemy empire never makes peace with
the player only; it may treat with rivals and clans (the default `diplomatic-stance` already enforced);
**Q5** — both shipped templates get a clan, plus the `two-hearths` v2 rival (`clan-seeding` §4,
`empire-roster` §3). One question was opened by round 4 (CQ1, answered) and one by the 2026-09-20 audit (CQ2,
**open**):

| # | Question | Options | Recommendation (default until answered) |
|---|---|---|---|
| CQ2 *(open — opened by the 2026-09-20 audit)* | **What recurring sink drains an AI empire's treasury once it has built everything its ground allows?** Banking pays every turn; the treasury's only drains are one-off structure goods costs (a new building, a tier upgrade) and collapse. With finite slots and ladders, a mature AI empire's treasury then grows without bound (P1) and has no upkeep term (P2); `empire-goods-sinks`' P1 report assertion fails by construction on a long campaign. The player's banked goods escape this only because the player also spends them on account-scoped sinks an AI lacks | (a) **Recurring world costs paid from banked goods, for everyone:** `legion-build`'s located-goods sinks (legion equipment production, doctrine goods upkeep) may draw on the owner's banked store (player wallet or AI treasury) when located stock is short — one rule, symmetric, recurring and proportional to army size. (b) **A treasury upkeep proportional to balance** (the contract-tribute shape, P2), AI-only and therefore declared as a handicap in the turn report (principle 11). (c) **Accept the growth:** the treasury only lowers the AI's own `want` (need-vector stock), no price reads it, and the P1 treasury assertion stays scoped to "while a goods-cost build remains" | **(a).** It is the only option that is symmetric (principle 11), recurring and proportional to holdings (P2) without a handicap, and it reuses sinks `legion-build` already owns rather than inventing one; it needs `legion-build`'s agreement. (b) is a declared handicap that punishes AI saving for no player-visible reason. (c) leaves a known P1 violation in the design. Default until answered: (c)'s scoped assertion (`spec-empire-goods-sinks.md` §5), so the report never pins a result the design cannot deliver |
| CQ1 *(answered 2026-09-20, R5-A C2: option (a), the offerer only)* | **Who needs the Embassy for peace and treaties with an empire — the offerer, or both sides?** Round 4 says *"T1 treaties with an empire"* without naming a side. | (a) **The offerer only**; accepting needs no building. (b) **Both sides.** (c) Neither for peace (peace ends a war; it is not a treaty); the Embassy gates treaties only | **(a).** (b) lets a faction that never builds an Embassy refuse every peace — a war nobody can end — and makes an AI's build order decide diplomacy; (c) splits one diplomatic act into gated and ungated halves for no player-visible reason. (a) is one check at one admission site per act (`diplomatic-stance` §9, `exchange` A16) and reversible |

### The approved questions, as asked

| # | Question | Recommendation (approved) |
|---|---|---|
| Q1 | **Default stance, and whether the dominant enemy empire can make peace.** Today everything is at war. Rivals and clans need a default, and peace or a `market` treaty with the dominant enemy empire would let a player stall the world's win condition | Dominant enemy empire: at war with the player from world creation, and never offers or accepts peace or a treaty with the player (it may treat with rivals). Rival empires and clans: at peace with everyone, no treaty, band `wary` |
| Q2 | **Where "many empires" first appears.** The shipped maps have 6 and 14 sectors and the generator is wave 4 | Build and prove every many-empire path on `trade-foundation`'s synthetic fixture; add one rival to `two-hearths` under the new stamp so a shipped map exercises it; scale arrives with the generator |

## Tunables (keys owed by the specs; values decided by principle)

`data/tuning/trade.v{n}.json`: `needs.smoothingUnits`, `needs.climateDemandUnits`,
`needs.speciesDemandUnits` (per member, keyed by element — never by species id), `needs.seasonDemandMilli`
(one entry per season), `needs.reserveTurns` (added by `empire-goods-sinks`), `clan.consumptionPerTurnMilli`,
`personality.<policyId>.{tradeAppetite,warAppetite,treatyWillingness}Milli`,
`difficulty.<profileId>.{laneLossMilli,aiBidAggressionMilli,aiMaxSpendPerTurnMilli}`.
`data/tuning/diplomacy.v{n}.json`: `diplomacy.offerTtlTurns`, `relation.tradeFulfilledCapPerPairPerTurn`
(a structural per-turn rate, tunable in value).
*Removed at spec time:* `defaultStance` (the Q1 defaults are a structural table — they decide the win
condition, not the feel), `relation.treatyBrokenObserverShareMilli` (replaced by the
`treaty.break-witnessed` kind with its own whole-step shift), `truceTurns` (read only by `exchange`
`treaty-lifecycle`, so it is that module's key). Each file is created by the first trade module that needs
it; later keys arrive through `gk-core/tools/tuning/publish.py --add-key`.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world map (factions, AI, movement/hostility), economy (registry, P1/P2, sinks),
    tunables, numeric types, power (value-normalised units via exchange), relation ladder.
[~] Session boundary: working under trade-network-idea-20260919 (paths include
    docs/architecture/trade-network/**). session-boundary-check.py exits 1 on the crossings already
    recorded in that record's notes (summoner-convergence lanes' broad globs); these are new files only.
[~] Read this session: DESIGN-GATE, PRINCIPLES, trade-network-ideal (whole), npc-story-events-ideal
    §0, §6.4, §6.12, §7-§12, npc-story-events-map (modules), economy-principles, empire-resource-ssot,
    empire-economy-ssot, tunables-ssot, ssot-power-scale §10-§11 (partial), world-map-program,
    world-map-runtime-map, spec-ai-commander, empire-seed-ideal §6.1/§8/§9, legion-build-ideal
    §6.5-§6.7, world-continuity-ideal §6. NOT read: world-map-runtime-ideal and its two specs (FE map
    rendering; no module here touches the map plane), creatures/spec-soul-economy.md.
[x] decisions.md: the empire resource registry row (loam never traded; world stocks never feed
    account paths) — decisions.md:108. No lock covers diplomacy or clans.
[x] Every factual claim cites file:line (table "What the code says").
[x] audit-doc-citations.py --scope run on this file: 0 HIGH (the LOW rows are proposed files, marked).
[x] Claims verified against code, not comments (IsHostile body, LoamUpkeep G-C body, ClaimResolver
    body, AI fill body read directly).
[x] Read the surrounding section of every quoted rule (§7.4, §7.7, §12, §14b; relation-ledger row).
[x] No constraint reported as "moves goldens" without a run: stamp-gated changes are stated as
    "old-stamp worlds replay byte-identically", an acceptance criterion to test, not a claim.
[~] §2 invariants: none contradicted. Invariant 1/2 (PvZ) untouched; 14 (one ladder) respected.
    C1 is a named behaviour change to world-movement's hostility rule.
[x] Corrections propagated: none made to other docs (fence); contradictions listed for the owner.
[x] No assertion pins a population count. Pinned literals: diplomacy fact kinds (12 — was "10" here until the
    2026-09-20 audit; `offer.made`/`offer.declined` were added at spec time — closed, code-owned),
    disposition bands (4, closed registry).
[x] Event-refreshed cache: none owned here. The band snapshot is a per-turn logged input, not a cache;
    stance is derived per step. The one cache this map touches is logistics-flow's path-cache, and
    diplomatic-stance names the trigger it owes it (a hostility change bumps the graph version).
[x] Orderings: war/treaty same-turn filing is stated order-independent and tested both ways.
[x] Actor magnitudes: none produced or consumed here.
[x] No SOLID-violating parallel path: one hostility rule, one ladder, one need vector, one AI fill.
[ ] Registry rows: new rules (facts-only relations, symmetric knobs, no owner-id inequality as hostility,
    one capture path) are local tests in the specs; enforcement-registry rows are owed at build time.
[x] Spec pass 2026-09-19: eleven specs written under counterparties/; corrections propagated here (call
    sites, fact kinds, treasury seam, sink list, capture hook, tunables); asks A6-A13 and C7-C14 added.
```

---

## Reconciliation 2026-09-19 (round 4)

Against [decisions-round-4.md](decisions-round-4.md) (binding; it wins where this map disagreed). Docs only.

**Round-4 decisions applied**

| Register item | Where it landed |
|---|---|
| Q4 — the dominant enemy empire never makes peace **with the player only**; it may treat with rivals and clans | `diplomatic-stance` §1 rule 3 and acceptance 12; O1 closed (it was already the enforced default) |
| Q5 — both shipped templates get a clan, plus the `two-hearths` v2 rival | `clan-seeding` §4 (`first-light` v2: a spur off `ash-waste`; `two-hearths` v2: a second corridor spur); `empire-roster` §3 and acceptance 5; O2 closed; roster rule 3 corrected for `first-light`'s landless dominant empire (C15) |
| B / Q1 — clan trade opens by building a **Trading Post**; the band sets the spread and blocks only at `hostile` | `clan-seeding` rule 2 (every clan hub seeded with a working tier-1 Trading Post) and §6; `conquest-consequences` (the Trading Post passes to the captor) |
| B — diplomacy with empires needs an **Embassy** (T2 **Consulate**: blocs, embargo leverage; clans need none) | `diplomatic-stance` §9: `DiplomacyGate` over the `diplomacy` feature, `peace-offer` refused `diplomacy.no-embassy` toward an empire; treaty and bloc/embargo checks asked of `exchange` (A16); CQ1 |
| B — a bank point is a **Counting House** | `empire-treasury` §3: an AI empire banks only after building one (A17 to `trade-ai`) |
| B — buildings unlock features generally | A14 (`sector-features`, answered), A15 (Embassy and Trading Post rows), A17 (AI builds through the ordinary path); no `StructureKind` member added (C19) |

**Contradictions fixed in this cluster:** C15 (roster rule vs `first-light`), C16 (treasury trade drains),
C17 (two logged-input channels), C19 (no `StructureKind.Embassy` beside `sector-features`); O1, O2 closed.

**Asks received and answered here**

| Ask | From | Answer |
|---|---|---|
| E-A7 — one channel for logged step inputs | `exchange` | Accepted: `rpg_world_step_inputs`, owned by `relation-facts`, kinds `band` and `soul-budget` (`spec-relation-facts.md` §3) |
| E-A10 — per-sector `DemandAt` / `ReserveAt` | `exchange` | Accepted: over the faction's supply component through `SupplyReach` (`spec-need-vector.md` §5) |
| E-A12 — settlement never touches a treasury | `exchange` | Accepted (C16; `spec-empire-treasury.md` §3, §6) |
| E-A13 — `TariffMilli?` on four fact kinds | `exchange` | Accepted: nullable field on the fact, canonical column and table column; the vocabulary stays at 12 (`spec-diplomacy-facts.md` §1, §4, §5) |
| T-A7 — `WantAt`, reserve, belief estimate, band and own treasury via `IWorldView` | `trade-ai` | `WantAt`, `ReserveAt`, `EstimateFor` (`spec-need-vector.md` §5); `IWorldView.BandWith` (`spec-relation-facts.md` §3); `OwnTreasury` and `BankedLastTurn` (`spec-empire-treasury.md`) |
| logistics-flow A4 — a stance change bumps the graph version | `logistics-flow` | Already in `spec-diplomatic-stance.md` §7 |
| E-A13 widening — the fact carries the treaty `Deal` | `exchange` | Accepted: nullable `Deal` field (exchange's `TreatyDeal` record and canonical text) on `offer.made`, `treaty.signed`, `treaty.imposed` (`spec-diplomacy-facts.md` §1) |
| E-A15 — name the Embassy's structure role | `exchange` | `Enable` recommended in A15 (no role widening) |
| E-A16 — seed each clan hub as the `Exchange` row at tier 1 | `exchange` | Accepted (`spec-clan-seeding.md` rule 2) |
| E-A17 — `IPassageRule` cannot see the band | `exchange` | Accepted: `Grants(world, bands, grantor, requester)` (`spec-diplomatic-stance.md` §3) |

**Cross-cluster conflicts (files this session does not own)**

| # | Conflict | Recommended resolution |
|---|---|---|
| X-C1 | *(Mostly resolved this round.)* `exchange-map.md:249-250` now reads *"`market` from `wary`, only `hostile` blocks"*, but its owner-question row Q1 (`exchange-map.md:476`) still carries the pre-round-4 *"`market` from `open`"* (C18) | `exchange` updates the Q1 row to the amended rule |
| X-C2 | *(Resolved this round.)* `exchange` `treaty-lifecycle` §3a now gates on `DiplomacyGate` (A16) | — |
| X-C7 | `exchange/spec-treaty-lifecycle.md` §3a says *"`StructureKind.Embassy` and `DiplomacyGate` … live in `counterparties` `diplomatic-stance` §9"*; the Embassy is now `Feature == diplomacy` and no `StructureKind` member exists (C19) | Drop the `StructureKind.Embassy` mention; `DiplomacyGate` is unchanged. *(Ruled 2026-09-20, X10.)* |
| X-C3 | `empire-seed/spec-trade-structure-rows.md` §5.1 has no diplomacy row and no Trading Post variant | Add the Embassy row (2 variants) and the trade building's tier variants (A15) |
| X-C4 | `npc-story-events/spec-narrative-vocabulary.md:132` still gives `Rival` the base band `hostile` (A6, unchanged) | Set `Rival` to `wary`; under round 4's "only `hostile` blocks", a `hostile` rival base band would also block trade the register means to allow |
| X-C5 | *(Mostly resolved this round.)* `trade-ai` `ai-trade-buildings` now builds the round-4 ladders for AI empires; nothing yet states that `clan-keeper` builds nothing | `trade-ai` `clan-behaviour` states it, so a clan hub stays a tier-1 Trading Post (A17) |
| X-C6 | `exchange/spec-exchange-hub.md` §1 widens `StructureKind` with `Exchange`, beside `sector-features`' `trade` feature | Gate on `SectorFeatures.TierOf(sector, trade)` only (as `fleet-map.md` X-F1). *(Ruled 2026-09-20, X1.)* |

**Gap check**

- Every module row has a spec (11 of 11).
- Dependencies resolve to real module ids (`trade-foundation`, `sector-yield`, `logistics-flow`, `exchange`,
  `trade-ai`, `trade-stories`, `npc-story-events`, `empire-seed`); `world-map-program` `ai-commander` and
  `world-generator` are program items, not map modules; `trade-foundation` `sector-features` (A14) now exists.
- Tuning keys (`needs.*`, `clan.consumptionPerTurnMilli`, `personality.*`, `difficulty.<profileId>.*` in
  `trade.v{n}`; `diplomacy.offerTtlTurns`, `relation.tradeFulfilledCapPerPairPerTurn` in `diplomacy.v{n}`) —
  `trade-ai` and `exchange` read them and name `counterparties` as owner; none is double-claimed (searched).
  Round 4 adds no key here (`TreatiesTier`/`BlocsEmbargoTier` are structural constants).
- Closed-vocabulary widenings: no `StructureKind` member (C19; `diplomacy` is a `SectorFeature`, owned by
  `sector-features`); admission reason `diplomacy.no-embassy`;
  `rpg_world_step_inputs.input_kind` (`band`, `soul-budget`); `DiplomacyFact` gains a field (`TariffMilli`),
  not a kind — the 12 fact kinds are unchanged.

**Citation audit:** `python scripts/audit-doc-citations.py --scope docs/architecture/trade-network/counterparties`
— see the session report; no HIGH finding.

## Round 5 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 5" (R5-A, R5-X), which wins over any spec.
Citations touched were re-opened on `features/mega-merge`.

| # | Change | Where |
|---|---|---|
| CR1 | **A1 start kit:** every empire seat the empire owns at creation gets a tier-1 Counting House and Storehouse. Placement is `world-continuity` `world-creation` §5a (one placement, in `Rebuild`); this map owes template content — the `first-light` v2 / `two-hearths` v2 versions give each owned empire seat sector (and the rival's spur home) two free `Wildland` slots, because today's seats cannot hold the kit (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:143-149`; `WorldTemplateCatalog.TwoHearths.cs:43-48`, `:198-203`). Clans are not empires and get no kit | `spec-empire-roster.md` §3, §3a; `spec-clan-seeding.md` header |
| CR2 | **B3:** every seeded clan hub also holds a tier-1 Caravan Yard (rule 2a, `Wildland`), so a player's caravan can unload there (`fleet` `depot` `ForeignSite`); the upkeep-at-seed rule counts its term; the generator reserves a `Wildland` slot | `spec-clan-seeding.md` §1, §4, acceptance 6 |
| CR3 | **C2 (CQ1 → a):** only the side making the offer needs an Embassy | `spec-diplomatic-stance.md` §9 |
| CR4 | **C3:** a deliberate embargo (`exchange` `embargo-set`) needs a Consulate; the war embargo is automatic and needs no building | `spec-diplomatic-stance.md` §6, §9 (consistent with `exchange/spec-treaty-lifecycle.md` §3a) |
| CR5 | **X1:** `DiplomacyGate.TierOf` is a named wrapper over `SectorFeatures.FactionTier(…, diplomacy)` | `spec-diplomatic-stance.md` §9 |
| CR6 | **X2 / X3:** `empire-treasury` is the AI treasury's writer, registered into `banking-fact`'s destination seam; it uses no `settle` kind — settlement kinds are `exchange`'s five and never touch a treasury | `spec-empire-treasury.md` §2, header |
| CR7 | **X14:** unchanged, already so — `IPassageRule.Grants(world, bands, …)` receives the logged band snapshot, and `relation-facts` keeps the one step-input table `rpg_world_step_inputs` (kinds `band`, `soul-budget`) | `spec-diplomatic-stance.md` §3; `spec-relation-facts.md` §3 |
| CR8 | **X16:** the Embassy row's role is `Enable` (no new role) — `empire-seed`'s row, consistent with §9 | — |
| CR9 | Citation re-verified: the new-kind no-bump precedent is `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:134-141` (the `Assaults` phase note). *(The round-5 pass re-cited it to `:117-123`, which is the ruleset-6 bump note — corrected by the 2026-09-20 audit.)* | `spec-diplomatic-stance.md` |

**Closed vocabularies:** clan validation gains rule 2a (a rule, not a vocabulary member); `ledger-keys`
fact kinds asked for by this map lose `settle` (`bank`, `sink`, `collapse` remain).

**Still other owners' files:** `world-continuity` places the kit; `exchange` `exchange-hub` gates a foreign
caravan's consignment writes on `fleet` `depot` `ForeignSite` (B3); `empire-seed` authors the `Enable` role on
the `embassy` row (already so in `spec-trade-structure-rows.md` §5.1).

## Audit 2026-09-20

An independent audit of this map and its eleven specs against the checklist stated in
[fleet-map.md](fleet-map.md) *Audit 2026-09-20*, each claim checked in code on `features/mega-merge`. Docs only.

### Findings

| # | Sev | Where | Finding | State |
|---|---|---|---|---|
| CA1 | HIGH | `empire-goods-sinks` §2, Hard edges | The player's goods-cover verdict was a **second** logged step-input table (`rpg_world_goods_cover`) beside `relation-facts`' one record — the parallel channel map C17 and round-5 X14 (*"counterparties keeps one step-input table"*) rule out. Its Hard edges bullet still asked `exchange` to copy it | **Fixed:** a registered `goods-cover` kind in `rpg_world_step_inputs`; `relation-facts`' closed kind list widened |
| CA2 | HIGH | `empire-treasury` §6; `empire-goods-sinks` §5 | The AI treasury has a perpetual faucet and only one-off sinks: P1 inflation and no P2 upkeep term once an empire's ladders are complete; the P1 report assertion fails by construction on a long campaign | **Opened** owner question **CQ2**; the assertion is scoped meanwhile (visible, not silently green) |
| CA3 | MED | `need-vector` §2 | The smoothing term `k` was flat while demand and stock are content-scaled (PS-5), so `want`'s shape drifted with `Θ`; the "loader rejects worst-case demand" safeguard could not exist | Fixed (`k` scaled by the same read; Θ-invariance acceptance; the true narrowing bound stated) |
| CA4 | MED | `diplomatic-stance` §Built, §8; this map CR9 | The no-bump precedent was cited at `TurnEngine.cs:117-123`, which is the ruleset-6 **bump** note — the opposite precedent; the real note is `:134-141` | Fixed |
| CA5 | MED | `empire-roster` acceptance 2 | Still stated the uncorrected rule (every empire needs a seat and a rootbed), contradicting rule 3's landless exception and rejecting `first-light` v2 | Fixed |
| CA6 | MED | `empire-treasury` §2; this map A10 | Asked for an "unlocated sector value" that `trade-foundation` answered differently (`f:` holder, `StockHolderKind.Faction`) | Fixed |
| CA7 | LOW | this map module 4, module 7, §5 checklist | "minus payments" (settlement never touches a treasury); the relation dedupe key lacked the cap ordinal; "10" fact kinds (12) | Fixed |
| CA8 | LOW | `clan-seeding` Hard edges; `conquest-consequences` acceptance 6 | "Rule 5" (rule 6); `LoamPhases.cs:218` (`:219`); the one-capture-path scan did not say it concerns sector owners only | Fixed |
| CA9 | LOW | every spec | Verification boundary: `World/Trade/**`, `World/Diplomacy/**`, `World/Facts/**` map only to `core-fallback` | Named: a `core-world-trade-counterparties` owner boundary lands with the first implementing task |

**Checked and clean:** RPG layer only; one hostility rule (six direct callers verified by grep:
`gk-core/src/FusionRpg.Core/World/Movement/ContactResolver.cs:94`, `:120`; `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:37`;
`gk-core/src/FusionRpg.Core/World/Ai/BelievedSupply.cs:64`; `gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs:71`;
`gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:235`); the relation band is a logged step input, never a live
ledger read (P13); relation facts are facts only, deduped on durable ids (P14); every behaviour change rides the
per-world stamp; loam is never traded; no souls come out of anything here; clans and empires pay the shared loam
upkeep (the G-C and supply exemptions closed at seed by principle 10); the treasury is unlocated and never
negative; collapse is a named sink; no population is pinned; every order-sensitive rule is stated
order-independent with both orders tested; SQL only in `FusionRpg.Data`; no actor magnitude; no IP name in new
prose (code identifiers such as the dominant empire's faction kind are untouched, per `ip-censor-ideal.md` §6.1a).

### Reported to other programs (their files; not edited)

| # | To | Finding | Recommended fix |
|---|---|---|---|
| CX1 | `trade-foundation` `sector-features` | An assault writes **slot** owners without changing the sector owner (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:146-161`); `TierOf` reads no owner and `FactionTier` maxes over owned sectors. A clan's Trading Post, an Embassy or a Counting House whose slot an enemy holds still counts for the sector's owner, and `conquest-consequences` sees no conquest | One owner rule in `sector-features` (fleet-map FX1: a building counts only while one faction owns both its sector and its slot) |
| CX2 | `legion-build` | CQ2 option (a) would let its located-goods sinks draw on the owner's banked store | Agreement needed if the owner picks (a) |
| CX3 | `trade-ai` | `NeedVector.WantAt` gains a `k` argument (scaled per sector) | Pass the hub sector's `k` |
| CX4 | `exchange` | `settlement-payment`'s soul budget and this program's `goods-cover` share `rpg_world_step_inputs`; any new pre-step verdict registers a kind there | Confirmation only |

**Citation audit:** `python scripts/audit-doc-citations.py --scope docs/architecture/trade-network/counterparties`
and `--scope docs/architecture/trade-network/counterparties-map.md`, run after these edits — no HIGH finding.


---

## Round 6 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 6". The family's single landing order is
[landing-order.md](landing-order.md); this sub-program is rows 15, 16 and 17 of its §2.

| # | Decision | What changed in the specs |
|---|---|---|
| **C1** | One capability flag and one ruleset bump per wave | Two of the seven flags spanned waves and are split: `counterparties.diplomacy` gated `diplomacy-facts` (W1) **and** `diplomatic-stance` / `relation-facts` (W2), and `counterparties.clans` gated `clan-seeding` (W2) **and** `clan-economy` (W3) — so a world stamped at the earlier wave would have gained derived war/peace, or a clan economy, mid-life. New: **W1** `counterparties.needs`, `.roster`, `.diplomacy`, `.treasury` (four rows, **one** bump); **W2** `counterparties.stance` (`diplomatic-stance` + `relation-facts`) and `.clans` (`clan-seeding`), one bump; **W3** `counterparties.clanEconomy`, `.sinks`, `.conquest`, one bump. `trade-difficulty-knobs` registers **no** row — the profile id is stamped at creation (CM10), the one case a spec may still say "no bump". `spec-diplomatic-stance.md` §8 also drops its *"this module does not bump `RulesetVersion`"* claim: the `Assaults` new-kind precedent is about a phase no old log can populate, not about skipping a capability's bump |
| **C2** | One neutral `StructureKind.Feature`; `StructureKind.Exchange` withdrawn | `spec-diplomatic-stance.md` §9: *"no `StructureKind` member is added"* stands as *no gate reads a kind* — but the row was shipping `structureKind: none`, which **cannot load** (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`, `:330`), so no Embassy could ever be built and `DiplomacyGate.TierOf` returned 0 forever: no treaty, ever (audit C2). Feature rows load as the neutral `Feature` kind, the `Obstacle` precedent (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`). `spec-clan-seeding.md` gains the same note for a seeded hub's Trading Post |
| **C3** | Banking waits on the save-identity re-key | `spec-empire-treasury.md` §7: this module may land, and **every treasury reads zero** until `banking-fact`'s step half ships (banking is its only faucet, E-A12). Its acceptance proves the arithmetic on injected facts, never on a campaign's banked total, and the report prints zero **with that reason** |
| **S1** | A building counts for nobody until one faction owns both its sector and its slot | `spec-diplomatic-stance.md` §9 reads `TierFor`/`FactionTier`; `spec-clan-seeding.md`'s seeded `trade` tier is read the same way. No spec here writes an owner test of its own; the rule lives in `sector-features` §5a |
| **S2 / W1 / W2** | Trade goods cross worlds only by rift route | No change: nothing here moves a good between worlds. A clan and an AI empire are per-world by construction, and a treasury is per-world (§4) |
| **CQ2** | Legion equipment and doctrine upkeep may draw banked goods when local stock is short, symmetric for player and AI | **This answers the map's own CQ2.** `spec-empire-goods-sinks.md` §5 gains two recurring sink reasons, `legion-equip` and `doctrine-upkeep`, which debit the treasury only for the **shortfall** after local located stock is spent — the recurring drain the audit showed was missing (structure goods costs are finite; banking is not). Symmetry is tested against umbrella invariant 11: the same fixture, the same shortfall, player and AI debit the same quantity for the same reason. The *"only while a goods-cost build is available"* caveat and its "ladder complete" verdict are withdrawn. `spec-empire-treasury.md` §7 records the `sink` kind carrying it — no new fact kind, no new holder prefix. **The legion-build side is an ask** (`legion-equipment`, `legion-doctrine`: which fittings and which upkeep may fall back, in what order, and what happens when the treasury is empty too) |
| **Q-A** | War inside a treaty's minimum term also writes `treaty.broken` | `spec-diplomacy-facts.md` new §7a: a `war-declare` against a partner inside an active treaty's minimum term appends **two** facts in one step, `war.declared` then `treaty.broken`, with the same observer effect as any early exit (`relation-facts`' `treaty.break-witnessed` fires unchanged). The vocabulary stays **pinned at 12** — only the writer column widens, because `diplomatic-stance` now also writes `treaty.broken`. `treaty.ended` is *not* also written (a broken treaty is broken; two facts for one event would move two bands). The append order is fixed and tested. `spec-relation-facts.md` §2 notes it reads the fact and needs no rule of its own |
| **D2** | Six `world.*` channels compose in `ActorHub` | Nothing here reads one. `need-vector` reads stock against demand; the treasury holds quantities. Where an AI's *force* matters it is `legion-build` `legion-power` (X7), which also sums Hub output only |
| **M1 (audit), edges 2–4** | Three edges pointed up or cycled | `spec-clan-seeding.md`: the Trading Post row comes from `empire-seed` and its tier from `sector-features`, so `exchange` `exchange-hub` is no longer named (edge 2). `spec-relation-facts.md`: settlement deltas arrive as **`stock-deltas` kinds `settlement-payment` registers**, so the cycle with `spec-settlement-payment.md` is gone and this module emits no `trade.fulfilled` until kinds exist — correct, since nothing has settled (edge 3). `spec-diplomatic-stance.md`: the passage rule is relabelled a **seam `trade-access` registers into**, default closed (edge 4) |
| **m4 (audit)** | Stale clause | `spec-clan-seeding.md`: the *"`exchange-map.md` Q1 conflicts"* clause is deleted — round 5 X10 resolved it |

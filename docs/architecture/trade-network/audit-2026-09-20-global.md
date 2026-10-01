# Global audit 2026-09-20 — the trade-network family

**Status:** independent global audit, docs only, read-only on every spec and map. Written 2026-09-20 on
`features/mega-merge` (HEAD `fefb6ed3` plus the uncommitted edits the per-cluster auditors were making at
the same time). **Every `path:line` below was re-resolved against the working tree immediately before this
file was written** (a script matched a quoted phrase and recorded its line). Specs under concurrent edit
will drift; each finding quotes the phrase it anchors on so it can be found again.

**Scope:** the umbrella [trade-network-map.md](../trade-network-map.md), the ten sub-program maps under
`trade-network/`, [world-continuity-map.md](../world-continuity-map.md),
[legion-build-map.md](../legion-build-map.md), [empire-seed-map.md](../empire-seed-map.md) (13 maps), the 150
module specs under `trade-network/*/`, `world-continuity/`, `legion-build/` and `empire-seed/`, and the binding
register [decisions-round-4.md](decisions-round-4.md) (rounds 4 and 5).

**Read first, this session:** `CLAUDE.md` (hard rules), `docs/DESIGN-GATE.md` (whole), `docs/PRINCIPLES.md` §5,
the register (whole), the umbrella map (whole), and in full: `spec-world-stamp.md`, `spec-sector-features.md`,
`spec-ledger-keys.md`, `spec-system-commands.md`, `spec-located-goods-registry.md`, `spec-located-stock.md`,
`spec-production-halt.md`, `spec-bank-points.md`, `spec-legion-equipment-stock.md`,
`spec-world-state-vocabulary.md`, `spec-world-difficulty-profile.md`, `spec-trade-structure-rows.md` (§1–§10).
The other specs were read through their dependency, tunables, structure, hard-edge and acceptance sections
(extracted by script) plus targeted reads. Code claims were checked in `src/` (listed per finding).

**Method, mechanical parts.** (1) Module inventory: every `### \`id\`` heading and module-table row in the 13
maps against the 150 spec files. (2) Dependency graph: every spec's upstream section parsed into edges
(540 edges), checked for dangling ids, cycles (DFS) and edges against the umbrella build order
(`trade-network-map.md` §3). (3) Every backticked kebab id in a dependency section that is not a family
module was resolved against the other programs' maps and specs. (4) Every production path named as
modified in a spec's Structure / verification block was inverted into a file → modules table. (5) Tuning
keys in every Tunables section (135 keys) were checked for more than one owner.

---

## 1. Summary

The family is in good shape at module level. All 149 map modules have a spec and `legion-power` (the
150th) is in its map's module table; no dependency names an unknown module; every external module id
resolves to a real spec in another program (the only unspecced ones are `drop-tables`, which has a map row,
and `world-reclaim`, which is declared *reserved*). Tuning-key ownership is disciplined: 17 keys appear in
more than one spec, and every one of them is a cross-reference to a named single owner. Numeric discipline
(`long`, `checked`, bounded ratios labelled) and the contract-not-population rule hold everywhere sampled.
Round 5 X14 (passage seam), X2 (settlement kinds), X5 (step order), X7 (power roll-up owner), X8, X11 and
X12 are reflected in the specs they affect, several of them fixed by the cluster auditors during this audit.

What does not hold is the **family as one build**. Three defects block the first build slice, and each one
lives *between* clusters, which is why no cluster audit could close it:

- **C1.** The per-world stamp freezes a world's rules at creation, but each sub-program uses **one**
  capability flag for behaviour that lands across two to four waves. A world stamped between two waves
  changes rules mid-life, which is the exact D-C breach the stamp exists to prevent.
- **C2.** Six of the seven round-4 feature buildings (Storehouse, Counting House, Caravan Yard, Rift
  Anchor, Embassy, Workshop) can **never load** into the structure catalog as the specs stand: a row
  loads only with a `StructureKind`, the rows are emitted with `structureKind: none`, and ruling X1 forbids
  giving them a kind. The start kit, bank points, warehouses and every feature gate read nothing.
- **C3.** Banking — the first thing that moves value off the map — depends on `material-ledger`, which
  waits on `save-identity` SE4.38, an unchecked task twenty-six tasks deep in another program.

Beyond those: the umbrella's claim that *"arrows never point back up"* is false in eight places (M1);
`TurnEngine.RulesetVersion`, `WorldCanonical.cs`, the structure-seed tuning file and the regenerated
structure corpus are shared serialization points with no family-level ledger (M2, M3, M7); the first-slice
order puts `sector-features` before the empire-seed schema it joins against (M5); and the seedsmith, corpus
and tuning paths the first slice edits have no verification boundary at all (M6).

**Counts:** 3 Critical, 8 Major, 20 Minor. 30 cross-program asks to 22 owners (§5). Of the 33 first-slice
modules, 19 are implementable as written, 9 are implementable with a stated caveat, and 5 are blocked (§6).

---

## 2. Critical

### C1 — One capability flag per sub-program, but its behaviour lands in several waves (D-C breach)

**Rule.** A capability is granted when `stamp.RulesetVersion >= def.IntroducedAtRuleset`
(`trade-network/trade-foundation/spec-world-stamp.md:117`); *"The bump is mandatory"* so that no world stamped
before the behaviour existed gains it mid-life (`spec-world-stamp.md:123`). A stamp is never migrated
forward. The cluster audits of 2026-09-20 have now propagated the mandatory bump into
`spec-banking-fact.md:76` and `spec-logistics-phase.md:37`.

**Defect.** The rule protects a world only if *everything* a flag gates ships in the change that registers
the flag. The specs gate multi-wave behaviour on one flag:

| Flag | Modules that gate on it (evidence) | Waves they land in |
|---|---|---|
| `trade.logistics` | `logistics-phase`, `logistics-canonical`, `lane-flow` (`spec-lane-flow.md:225`), `lane-loss` (`spec-lane-loss.md:215`), `transit-buffer`, `logistics-facts`, `construction-chain` (`spec-construction-chain.md:210`) | 1, 2, 3 (`logistics-flow-map.md:127`, `:129`, `:134`) |
| `trade.sectorYield` | `banking-fact` (registers it, `spec-banking-fact.md:76`), `yield-structures` (`spec-yield-structures.md:82`), `structure-upkeep` (`spec-structure-upkeep.md:78`), `essence-loop-read` (`spec-essence-loop-read.md:94`) | separate changes; `structure-upkeep` *"can land first"* (`spec-structure-upkeep.md:171`) |
| `trade.fleet` | one flag for seven fleet modules (`spec-world-stamp.md:352`; `spec-carried-goods.md:75`) | waves 1–3 |
| `trade.riftTrade`, `trade.exchange` | one flag each for eight and ten modules (`spec-world-stamp.md:354`, `:353`) | several waves |

A world created after wave 1 of `logistics-flow` (stamped at the bumped ruleset, so granted
`trade.logistics`) gets lane loss, transit buffers and the refine step when wave 2 and 3 merge: its rules
and hash change mid-life. Second symptom: `structure-upkeep` landing first would gate on a flag that is not
yet registered, and `Grants` throws on an unknown id (`spec-world-stamp.md:102`).

**Fix.** An owner decision (question 1, §8): either one capability row (and one bump) per landing wave,
or register each sub-program's flag only when its last wave lands (behaviour tested on fixture registries,
as `spec-world-stamp.md` acceptance 4 already does), or accept mid-life changes for worlds created before
the first release. Whichever is chosen, `spec-world-stamp.md` §2 states it and every flag owner quotes it.
Today 12 of the 16 capability rows named in `spec-world-stamp.md:348-355` sit in specs that say nothing about
a bump (every `counterparties` flag, `trade.fleet`, `trade.exchange`, `trade.diplomacy`, `trade.riftTrade`).

### C2 — Six feature buildings can never be loaded or built

**Evidence, code.** `StructureDef.Kind` is a required enum with no "none" member
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`); a corpus row loads only when it has magnitudes
(`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`); `IsKnown` answers only for loaded rows
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:330`); `TierOf` counts only slots *"whose structure is known"*
(`trade-network/trade-foundation/spec-sector-features.md:177`).

**Evidence, specs.** `structure-bands` makes `structureKind: none` mean *"identity-registered, not
catalog-loadable"* (`empire-seed/spec-structure-bands.md:126`). `trade-structure-rows` emits all seven rows
that way and says *"Each loads when its consuming module adds its kind"* (`empire-seed/spec-trade-structure-rows.md:67`,
acceptance 7 at `:274`). Ruling X1 allows *"a new `StructureKind` only where loam or siege rules need one"*
(`decisions-round-4.md:107`), and the consumers comply: `depot` adds no kind (`fleet/spec-depot.md:26`),
`crossing-anchor` adds none (`rift-trade/spec-crossing-anchor.md:112`), `diplomatic-stance` adds none
(`counterparties/spec-diplomatic-stance.md:218`), and the exchange map records that *"the Embassy row stays
`Enable`-role with `structureKind: none`"* (`exchange-map.md:430`). `sector-features` itself says a feature is
*"Not a `StructureKind`"* (`spec-sector-features.md:299`).

**Consequence.** No Storehouse, Counting House, Caravan Yard, Rift Anchor, Embassy or Workshop can ever be
placed, built or counted. The A1 start kit (`world-continuity/spec-world-creation.md:163`) places rows that
never load; `bank-points`, `warehouse-axis`, `depot`, `crossing-anchor`, `DiplomacyGate` and
`legion-equipment` always read tier 0. Only the Trading Post escapes, because `exchange-hub` adds
`StructureKind.Exchange` as *"a seventh member"* (`exchange/spec-exchange-hub.md:49`) — which is itself
outside X1's allowance (its justification is clearing, not loam or siege, `spec-exchange-hub.md:66`).

**Fix.** Owner question 2 (§8). The smallest change that keeps X1's intent (a kind is never a feature
gate) is one neutral member, e.g. `StructureKind.Feature` (*"does nothing in the loam/siege economy; its
behaviour is its `FeatureUnlock`"*, the `Obstacle` precedent at `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:32-38`), and the loadable
rule `magnitudes present AND kind != none` with the seven rows emitted as `Feature` (Trading Post included,
retiring `StructureKind.Exchange`). Then `structure-bands` §5.4, `trade-structure-rows` §2 and acceptance 7,
`exchange-hub` §1, E-A22 and the register's X1 wording change together.

### C3 — Banking sits behind an unscheduled task in another program

`banking-fact` depends on `material-ledger` (`sector-yield/spec-banking-fact.md:311`) and may never credit
materials any other way; `material-ledger` depends on `save-identity` SE4.38
(`trade-foundation/spec-material-ledger.md:211`). SE4.38 is unchecked (`tasks/solid-enforcement-todo.md:634`)
and transitively needs SE4.12 (`tasks/solid-enforcement-todo.md:352`) and every task between. Everything
downstream of banking — `auto-banking`, `exchange` settlement at bank points, the AI treasury, trade-ai's
income read — inherits the wait. The umbrella says the ledger modules are *"sequenced behind
save-identity"*, but no plan says when SE4.12–SE4.38 run. Owner question 3 (§8).

---

## 3. Major

### M1 — Eight dependency edges point up the build order; the umbrella says none do

The umbrella claims *"Arrows never point back up: no sub-program reads a later one"*
(`trade-network-map.md:106`). Parsed from the specs' own dependency sections (umbrella order:
foundation / legion-build / empire-seed / world-continuity → sector-yield → logistics-flow → fleet ∥
counterparties → exchange → trade-ai → rift-trade → trade-stories):

| Edge | Evidence | Kind |
|---|---|---|
| `fleet` `crew` → `exchange` `exchange-hub` and `rift-trade` `crossing-anchor` (their working predicates, to write `crew.idle`) | `fleet/spec-crew.md:205`, `:115` | hard; also **cycles** with `exchange-hub` (`spec-exchange-hub.md:321`) and `crossing-anchor` (`spec-crossing-anchor.md:280`) |
| `counterparties` `clan-seeding` → `exchange` `exchange-hub` (the trade building's kind and tier-1 variant) | `counterparties/spec-clan-seeding.md:218` | hard; the row is empire-seed's and the tier is `sector-features`', so the edge is avoidable |
| `counterparties` `relation-facts` → `exchange` `settlement-payment` (settlement deltas) | `counterparties/spec-relation-facts.md:249`; reverse edge `exchange/spec-settlement-payment.md:268` | cycle |
| `counterparties` `diplomatic-stance` → `exchange` `trade-access` (passage rule) | `counterparties/spec-diplomatic-stance.md:335` | optional; really a seam `trade-access` registers into (`spec-trade-access.md:157`) — relabel |
| `fleet` `trade-route-order` → `exchange`, `rift-trade` | `fleet/spec-trade-route-order.md:315` | "later" |
| `world-continuity` `advance-carry` → `rift-trade` `crossing-anchor` (republish call) | `world-continuity/spec-advance-carry.md:235`; reverse `rift-trade/spec-crossing-anchor.md:285` | cycle |
| `legion-build` `legion-equipment`, `legion-standards` → `sector-yield` | `legion-build/spec-legion-equipment.md:219`; `legion-build-map.md:98` | real; the umbrella row for legion-build lists only `1; empire-seed` (`trade-network-map.md:38`), and `sector-features` relies on that stale row for its placement argument (`spec-sector-features.md:29`) |
| `trade-surface` modules → `exchange`, `fleet`, `counterparties`, `trade-ai` | e.g. `spec-throttle-forecast.md`, `spec-trade-unlock.md` Dependencies | by design (*"grows with 4–7"*) but no per-module order is written |

Minor cycles inside a sub-program, each needing a one-line landing note: `goods-valuation` ↔
`tradeable-goods`; `escort-stance` ↔ `field-battle-kinds`; `trade-wire` ↔ `trade-unlock`;
`seasonal-demand-shocks` ↔ `trade-fact-kinds`; `trade-failure-branches` ↔ `trade-storylet-supply`;
`relation-facts` ↔ `conquest-consequences`.

**Fix.** Invert the hard ones through registration seams owned by the earlier module (a
`IWorkingSite`-style predicate registry in `crew`; `clan-seeding` reads the row and tier through
`sector-features` and names no exchange module; `relation-facts` projects from `stock-deltas` kinds that
`settlement-payment` registers; a post-move hook in `advance-carry` that `crossing-anchor` registers).
Correct the umbrella §1 row 10 and the §2 sentence.

### M2 — `RulesetVersion`, golden re-blesses and migrations have no family ledger

After C1's decision, the global constant becomes a serialization point shared by four programs. Specs that
take a bump today: `world-victory` (`world-continuity/spec-world-victory.md:148`, shared with `world-fall`),
`legion-traditions` (`legion-build/spec-legion-traditions.md:136`), `field-battle-kinds`
(`spec-field-battle-kinds.md:148`), `general-member-hub` (`spec-general-member-hub.md:198`), the filling
publishes of `legion-cohesion` and `legion-count-cost` (`spec-legion-cohesion.md:151`,
`spec-legion-count-cost.md:95`), `banking-fact`, `logistics-phase`, and every capability row under C1.
`income-parity` additionally orders its row *"not below"* `trade.logistics`
(`sector-yield/spec-income-parity.md:120`). The legion-build map's own bump list names modules 1, 8, 9, 11,
12, 13, 15 and 16 (`legion-build-map.md:117`) while the specs now say modules 1, 8, 9, 11 and 13 take no
bump (`spec-member-stack.md:253`) and module 10 does. Each bump stops trimmed turn reports from being
re-derived (`spec-world-stamp.md:123`), and schema changes pile onto the same tables (`rpg_worlds`:
`world-stamp`, `world-state-vocabulary`, `world-victory`; `rpg_world_sectors`: `located-stock`,
`sector-features`; `rpg_world_entities`: `member-stack`, `carried-goods`, `standing-orders`;
`rpg_world_commands`: `system-commands`).

**Fix.** One table in the umbrella map: each bump, its owner module, the capability rows it carries, its
golden re-bless, its schema change, and its order. Merge-time rule: a lane that bumps rebases onto the
latest constant and takes the next integer; capability rows reference the constant, never a literal.

### M3 — Four modules append canonical rows at the same point, in no stated order

*"after the `sector-ironwork` loop"*: `world-stamp` (`spec-world-stamp.md:156`), `located-stock`
(`sector-yield/spec-located-stock.md:93`), `carried-goods` (`fleet/spec-carried-goods.md:177`);
`logistics-canonical` appends *"after the rubble/ironwork rows"* (`spec-logistics-canonical.md:113`). The
canonical text is hashed, so the relative order of these conditional rows is part of every future golden.
Each spec is correct alone and ambiguous together; the second module to land cannot follow its spec
literally. **Fix:** an ordered append table (umbrella or `spec-logistics-canonical.md`) with the rule
"after the last conditional row present at landing", and each spec cites its slot.

### M4 — Hot shared files with no integration order; world-map-owned files edited by the family

Specs that name the file as modified (lower bounds — several specs describe edits in prose the
extraction did not catch): `TurnEngine.cs` 18 modules, `WorldState.cs` 17, `RpgStore.WorldTurns.cs` 15,
`RpgStore.World.cs` 12, `WorldCanonical.cs` 11, `WorldCommand.cs` 8, `WorldDtos.cs` 8,
`WorldEndpoints.cs` 9, `RpgStore.WorldGraphDiff.cs` 7, `WorldCommandAdmission.cs` 6,
`StructureCatalog.cs` 5, `LegionSupply.cs` 5, `FrontierRulesPolicy.cs` 4, `BattleApplication.cs` 4,
`DistrictAssaultResolver.cs` 4. Three of them belong to the world-map program: `BuildResolver.cs` (upgrade
arm, `sector-features` §4; multi-slot, E-A23 at `exchange-map.md:431`), `WorldValidation.cs` and
`SlotTypeCatalog.cs` (C4 rename, claimed twice — see m15). `CreateWorld` is changed by `world-stamp`
(`spec-world-stamp.md:193`), `world-state-vocabulary` (`spec-world-state-vocabulary.md:171`) and
`world-creation` (`spec-world-creation.md:163`) with no stated order. **Fix:** per hot file, the landing
order in the umbrella; the world-map asks filed with the exact lines (§5).

### M5 — `sector-features` is first-slice "independent", but it joins against a wave-2 empire-seed module

The trade-foundation map lists `sector-features` as *"independent, any order"*
(`trade-foundation-map.md:328`). The spec depends on `empire-seed` `band-reader` and `trade-structure-rows`
(`spec-sector-features.md:285`) and its acceptance 1 is a join test against `trade-structure-rows`'
`featureUnlock` vocabulary. `trade-structure-rows` is empire-seed wave 2, after `exchange-role`,
`structure-bands` and `world-name-index`. **Fix:** state the order: empire-seed's schema widening
(`featureUnlock`, the closed `variants` item, `requiredSlotKinds`) lands first — it can be split out of
`trade-structure-rows` as its own step — then `sector-features`, then the rows.

### M6 — The first slice's seedsmith, corpus and tuning paths have no verification boundary

`verify-change.py` throws *"VERIFICATION BOUNDARY MISSING"* for any path with no owner row
(`gk-core/scripts/verify-change.py:771`). No row covers `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/structures/**` or
`data/tuning/structure-seed.*` (`empire-seed-map.md:704`; `empire-seed/spec-trade-structure-rows.md:283`
*"Verification boundary: a gap"*), and `gk-core/data/tuning/**` has no fallback at all
(`trade-foundation/spec-economy-report.md:131`). Every empire-seed first-slice module and every first
publish of `trade.v1`, `legion.v1`, `legion-seed.v1`, `world-continuity.v1` and
`world-difficulty-catalog.v1` hits it. **Fix:** `test-verification-boundary` `python-test-lane` lands before
empire-seed I1; one owner row per new tuning domain lands with its creator (the economy-report pattern).

### M7 — Structure-seed schema, publishes and corpus regeneration are split across programs

Several consumers add an anchor field or band table in empire-seed's generator and `structure-seed.v{n+1}`
in their own change: `warehouseBand` (`sector-yield/spec-warehouse-axis.md:83`), `locatedYields` and
`yieldBand` (`sector-yield/spec-yield-structures.md:61`, *"the generator emits"* at `:200`), the clearing
ordinal (`exchange-map.md:409` row E-A2), plus depot and anchor magnitudes. The rule behind it is
empire-seed's (*"A capacity or clearing ordinal is added to the anchor only when its consuming
`StructureDef` field lands"*, `empire-seed-map.md:548`), while `structure-bands` says the opposite side adds
the field (`spec-structure-bands.md:309`). No empire-seed spec lists any of these fields in its closed field
table, and `locatedYields` (an array of objects) breaks that table's rule *"Every added field is a string
enum or boolean"* (`spec-structure-bands.md:120`). With `structure-bands`, `exchange-role` and
`trade-structure-rows` also publishing `structure-seed` and regenerating the tree, at least six modules in
four programs serialize on one tuning file and one generated corpus. **Fix:** empire-seed owns a
"consumer-added anchor fields" table (field, shape, band table, consumer module, landing order) and the
regeneration order; `structure-bands` widens its field-shape rule for `locatedYields` or the field is
reshaped.

### M8 — Versioned tuning files with more than one creator

- `ai.v3.json`: eight trade-ai specs each put keys in *"`gk-core/data/tuning/ai.v3.json` (next AI version)"*
  (`trade-ai-map.md:34`), and three separately claim the loader switch — `spec-ai-spend-limit.md:187`,
  `spec-deal-valuation.md:214`, `spec-interdiction.md:188`. These modules land in different waves, so only
  the first can publish `v3`; the rest publish `v{n+1}`.
- `data/tuning/trade.v1.json` (proposed; the file does not exist yet): created by *"whichever … lands first"* — `economy-report` (`spec-economy-report.md:99`),
  `warehouse-axis` (`spec-warehouse-axis.md:148`) or `structure-upkeep` (`spec-structure-upkeep.md:98`) —
  while about 15 other specs still write "`trade.v1.json` (new)".

**Fix:** name one creator per file (`economy-report` for `trade`, the first trade-ai module in the trade-ai
plan for `ai.v3`, including the loader switch), and have every other spec write `v{n+1}`.

---

## 4. Minor

| # | Finding | Evidence | Fix |
|---|---|---|---|
| m1 | Ledger-keys says the treasury uses the settlement kinds (*"a treasury credit from a sale is `settle-sell`"*), but settlement never writes a treasury | `trade-foundation/spec-ledger-keys.md:163` vs `counterparties/spec-empire-treasury.md:104` (E-A12) | Drop the parenthesis |
| m2 | `system-commands` still reports re-pointing *"owed"* by world-continuity and rift-trade; both have re-pointed | `trade-foundation/spec-system-commands.md:235` | Delete the paragraph |
| m3 | ES-R4-1 still described as open; round 5 B1 decided it | `empire-seed/spec-exchange-role.md:87`; `decisions-round-4.md:93` | Cite B1 |
| m4 | `clan-seeding` says `exchange-map.md` Q1 still conflicts; X10 fixed it | `counterparties/spec-clan-seeding.md:161` | Delete the clause |
| m5 | `crossing-anchor` lists `world-warden` as a publisher of moves outside a step; `world-warden` says ask A9 does not apply | `rift-trade/spec-crossing-anchor.md:285` vs `world-continuity/spec-world-warden.md:272` | Drop `world-warden` |
| m6 | `convoy-depot` still named as a row (X12: it is `caravan-yard`'s tier-2 variant) | `logistics-flow-map.md:589` (ask A5); `trade-stories-map.md:228` | Re-point to `caravan-yard` |
| m7 | The world-continuity cross-program table still says `sector-yield` and `rift-trade` are *"Ideal only"* | `world-continuity-map.md:95` | Update state |
| m8 | `trade-difficulty-knobs` names its source by an ideal tag, not a module id | `counterparties/spec-trade-difficulty-knobs.md:147` (*"`world-continuity` W7"*) | `world-difficulty-profile` |
| m9 | Start kit: the umbrella and `bank-points` say `clan-seeding` carries it; `clan-seeding` and `world-creation` say clans get none (A1: *empires*) | `trade-network-map.md:284`; `sector-yield/spec-bank-points.md:84` vs `counterparties/spec-clan-seeding.md:15`, `world-continuity/spec-world-creation.md:174`; `decisions-round-4.md:89` | Drop `clan-seeding` from both |
| m10 | The legion piece catalog is called `legion-build`'s, but `LegionPieceDef` is produced by empire-seed `legion-bands` | `sector-yield/spec-legion-equipment-stock.md:52`; `exchange/spec-tradeable-goods.md:142` vs `empire-seed/spec-legion-bands.md:152` | Name the producer once |
| m11 | Two diplomacy flags, `counterparties.diplomacy` and `trade.diplomacy`, with no stated implication between them | `counterparties/spec-diplomacy-facts.md:181`; `exchange/spec-treaty-lifecycle.md:131`; `spec-world-stamp.md:353`, `:355` | State `trade.diplomacy ⇒ counterparties.diplomacy`, or merge |
| m12 | Numeric knobs live in a `*-catalog` file; catalogs carry names and rosters, numbers go in the number file | `world-continuity/spec-world-difficulty-profile.md:47` vs `docs/PRINCIPLES.md:251` | Move knobs to `world-continuity.v{n}.json`, keyed by profile id |
| m13 | `essence-loop-read` cites `power-scale.v2.json`; `v3` is live (values unchanged) | `sector-yield/spec-essence-loop-read.md:43`; `gk-core/data/tuning/power-scale.v3.json` | Cite `power-scale.v{n}` |
| m14 | Two labour-to-output shapes: `exchange-hub`'s linear `min(1000, …)` staffing vs the one `LabourCurve` used by depot and anchor | `exchange/spec-exchange-hub.md:94` vs `rift-trade/spec-crossing-anchor.md:67` | X9 lets exchange own its term; evaluate it through `LabourCurve` (one evaluator, its own points) |
| m15 | The C4 slot rename has two routes: `exchange-hub` edits the `Name` field, `trade-lexicon` files it as an ask to world-map | `exchange/spec-exchange-hub.md:167` vs `trade-surface/spec-trade-lexicon.md:134` | One ask to world-map covering both slots |
| m16 | `OrderBook.OpenSellNeed` now means *other traders' open **buy** orders* (A4) | `exchange/spec-order-book.md:262` | Rename (e.g. `OpenBuyDemandAt`) |
| m17 | `legion-power` has no §5 detail section in its map (only the table row) | `legion-build-map.md:104` | Add §5.17 |
| m18 | The twelve `logistics-flow` specs have no Dependencies section; their edges exist only in the map table | e.g. `logistics-flow/spec-logistics-phase.md` (sections list) | Add one line each |
| m19 | `world-warden` adds the `warden` stance while `escort-stance` pins the stance list; both now use relative widenings — keep it so | `world-continuity/spec-world-warden.md:145`; `legion-build/spec-escort-stance.md:166` | None beyond keeping relative pins |
| m20 | Owner-named building "Grand Exchange" is also a well-known name from another game | `empire-seed/spec-trade-structure-rows.md:110` | Run it through `ip-censor` `avoid-list` like every authored name (advisory) |

**Principle sweep, no finding.** No private composer or second actor fold (`legion-power` sums Hub output;
`world-warden` and `lane-loss` read it). No hard magnitude cap found: every `min(…)` sampled is either a
quantity-available bound or a commented bounded ratio / per-turn rate. No `int` magnitudes; floats appear
only where PRINCIPLES allows (`coarse-step`'s `ln`, recorded). No population-pinned test: every "exactly N"
is a closed vocabulary with its reason. IP names appear only as existing code identifiers (`Zomboss`) and
as design-precedent citations; `treaty-screen` acceptance 7 keeps code ids off the player surface. Magic
numbers: every provisional value in a spec is a named tunable with a home file.

---

## 5. Cross-program asks

One row per ask to a program outside the family. "Blocks" names the family modules that cannot finish
without it.

| # | Owner | Ask | Blocks | Recommended wording |
|---|---|---|---|---|
| X-1 | solid-enforcement `save-identity` | Land SE4.12 → SE4.38 before `sector-yield` banking (C3) | `material-ledger`, `banking-fact`, `general-member-hub` (interim) | "Schedule SE4.12–SE4.38 ahead of trade-network sector-yield wave 2; report the landing date to the trade umbrella." |
| X-2 | power program (`ssot-power-scale.md` §10) | A contest row for two rolled-up legion powers (Θ from `LegionPower.Of`) | `lane-loss` strength switch, `world-warden` defence term, `deal-valuation`, `ai-trade-buildings` | "Add §10 row *rolled-up legion power*: magnitude = Σ unit Standing × Count (owner `legion-build` `legion-power`); contests read Θ via the ladder's inverse; consumers lane-loss, world-warden, trade-ai." |
| X-3 | power program | `realmsAdvanced` = worlds held from creation (Q8, D1), wiring `gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs:49` | `world-victory` §5 | "Redefine `realmsAdvanced` as `CountWorldsHeld(save)` (outcome ≠ fallen, from creation) and wire it from world-continuity." |
| X-4 | power program | Accept the §10 rows consumers author in their own change (lane throughput, warehouse capacity, clearing, located-good scale) | `lane-flow` (`spec-lane-flow.md:165`), `warehouse-axis`, `exchange-hub`, `essence-loop-read` | "Consumer-authored §10 rows are allowed when reviewed by the power owner in the same change." |
| X-5 | creature program | Fusion essence cost scales by the fused creature's level through `P(Θ)`; `EssenceCount` widens to `long` (Q7) | `essence-loop-read` (*"an essence yield cannot ship while the fusion essence cost is flat"*, `spec-essence-loop-read.md:25`) | "Agree to scale `FusionCost.EssenceCount` once at spend by `ContentScale.Milli(Θ_fused)`, `long`, in the essence-loop-read change." |
| X-6 | item program | Item base price from `goods-valuation` (E-A1); amend the catalyst lock `gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs:46-48` when catalysts trade | `goods-valuation` consumers, `tradeable-goods`, Delve merchant refusal | "Derive item base price from its material bill via `goods-valuation` + `SoulsBaseFor`, scaled once by `SoulSinkPolicy.Price`." |
| X-7 | npc-story-events `relation-ledger` | Pair-keyed faction facts; a band read as of end of turn N−1 (A1, A2); per-mille sum then one divide (A8) | `relation-facts` (CM1 snapshot), `ai-treaty-policy` | as filed at `counterparties-map.md:422`, `:423`, `:429` |
| X-8 | npc-story-events `narrative-vocabulary` | `Rival` base band `wary`; the six faction fact kinds with shifts (A6, A7) | `relation-facts`, `diplomatic-stance` | as filed at `counterparties-map.md:427`, `:428` |
| X-9 | npc-story-events (`storylet-selection`, `story-ledger`, `narrative-predicates`, `quest-sources`, `world-events-host`, `outcome-routing`, `counter-doctrine`) | Per-empire budget (CM7, decided OD-5); trade story kinds; `lane`/`legion` subject kinds; `StoryFactWithin`; four quest templates; `Market` host de-dup; ransom offer outcome; shared anti-Nemesis rows (T-A3) | all `trade-stories` modules, `interdiction`, `world-event-budget` | as filed at `trade-stories-map.md:438` §8 and `trade-ai-map.md:342` |
| X-10 | narrative-seed | Host-kind list owns the trade hosts (CM6/OD-3); storylet vocab, token grammar, planner rows | `trade-hosts`, `trade-storylet-supply` | as filed at `trade-stories-map.md:438` §8 |
| X-11 | world-map (`BuildResolver`, `WorldValidation`, siege board) | Upgrade arm: `build` of the structure already on the slot raises its tier (X8); accept a slot whose kind is in `RequiredSlotKinds` (B1, E-A23) | `sector-features`, `exchange-hub`, `clan-seeding`, `trade-structure-rows` | "Confirm the `build`-on-own-slot upgrade arm and the multi-kind slot check at `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:84`, `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:411`, `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:267`." |
| X-12 | world-map `ai-commander` | Amend *"no diplomacy"* and the new-kind boundary for this program (A5, T-A1) | `diplomatic-stance`, every trade-ai module | as filed at `counterparties-map.md:426`, `trade-ai-map.md:340` |
| X-13 | world-map `world-generator` / templates | Constraint rows: clan hubs, empire seats, off-path clans (A3); rift-tear + Wildland placement (A6); guaranteed first throttle; seats with two free Wildland slots for the A1 kit | `clan-seeding`, `empire-roster`, `crossing-anchor`, `trade-unlock`, `world-creation` | as filed at `counterparties-map.md:424`, `rift-trade-map.md:403`, `trade-surface-map.md:512` |
| X-14 | world-map `SlotTypeCatalog` | Display names "Market Square", "Vault Site" (C4), ids unchanged — one ask (m15) | `exchange-hub`, `trade-lexicon` | "Rename the display `Name` of the `market` and `vault` slot types; ids and `SlotKind` unchanged." |
| X-15 | world-map `intel` | Remember a surveyed slot's `StructureTier` (T-A11) | `trade-intel`, `ai-trade-buildings` | as filed at `trade-ai-map.md:349` |
| X-16 | world-stage | Inspector `trade` block, `trade.will-halt` nag, a seventh lens, playback rows, HUD strip, goods `UnitClass` | `trade-panel`, `throttle-forecast`, `flow-lens`, `trade-lexicon`, `trade-status`, `away-digest` | as filed at `trade-surface-map.md:501` §8 |
| X-17 | scoped-inventory | Goods follow `cargo-fate`'s rule (no new tables); `legion-cargo`'s `world_stock` kind for advance | `goods-cargo-fate`, `advance-carry`, `world-warden` | "Confirm `cargo-fate` applies to located goods on a caravan legion unchanged." |
| X-18 | test-verification-boundary | `python-test-lane` rows for `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/structures/**`, `data/tuning/structure-seed.*`; an owner row per new tuning domain; a web boundary | every empire-seed module, every first tuning publish, every trade-surface FE module (M6) | "Map seedsmith, the structure corpus and `gk-core/data/tuning/<domain>.v*.json` before empire-seed I1 lands." |
| X-19 | `decisions.md` | Phase-order row gains `Logistics` (and records `Assaults`); an empire-seed corpus-ownership row (D-E1/D-E2, `empire-seed-map.md:407`); Actor layer stack 5c; the Diplomacy layer (OD-1, `trade-surface-map.md:515`) | `banking-fact` (`spec-banking-fact.md:240`), `decision-45-revision`, `legion-owner-scope`, `treaty-screen` | each lands in its module's change, as the specs say |
| X-20 | effect-atom (`definitions.md`) | §6 `legion` owner key; `ContainerKind` + `LegionGear`; new `LeafId` members for trade predicates | `legion-owner-scope`, `legion-equipment`, `trade-predicates` | as listed at `legion-build-map.md:656` §8 |
| X-21 | actor-hub (`actor-hub-ssot.md` §8.1) | `legion:` and `legion-equip:` SourceIds | `legion-owner-scope`, `legion-equipment`, `legion-power` | as listed at `legion-build-map.md:656` §8 |
| X-22 | battle-engine (`battle-engine-ssot.md` §3) | Stack combatant under the damage and death responsibilities | `stack-combatant`, `field-battle-kinds` | as listed at `legion-build-map.md:656` §8 |
| X-23 | base-defense | Annotate decisions 30/33/45 for D-E2; `production-halt` is decision 22's first caller | `decision-45-revision`, `production-halt` | as listed in `empire-seed-map.md` §5.6 |
| X-24 | species-progression / empire-progression | `layer-source-selector`, `empire-species-container`, `species-layer-delivery` 6.1, `ai-empire-species`; the `Commander` role (`legion-commander`) | `general-member-hub`, `role-aware-placement` (Commander arm only) | as listed at `legion-build-map.md` §3 |
| X-25 | party-dungeon | Record the map door's sector id beside `ParentWorldId` (IP1) | `income-parity` (declared gap) | as filed at `sector-yield/spec-income-parity.md:207` |
| X-26 | drop-tables | Claim and siege loot manifests flow through the income divert when woken (IP2) | `income-parity` | as filed at `sector-yield/spec-income-parity.md:208` |
| X-27 | notification-ssot | Move the world fog rule into Core (`world-notify-source`); notify vocabulary rows | `trade-wire`, `trade-notify`, `trade-fact-source`, `away-digest` | "Expose the fog audience rule as a Core function the trade and continuity producers call." |
| X-28 | ip-censor | `avoid-list` helper; release scan of trade and building names | `world-exemplars`, `world-namer`, `trade-lexicon` (m20) | "Scan owner-named buildings and trade copy in the release gate." |
| X-29 | empire-inventory-surfaces | `route` tab reservation on the legion sheet | `trade-policy-editor` (b) | as filed at `trade-surface-map.md:501` §8 |
| X-30 | IA owner (`design/information-architecture.md`) | §3/§4/§5/§7 amendments for the Diplomacy layer | `treaty-screen` | as filed at `trade-surface-map.md:515` |

---

## 6. Build-readiness — first slice

"Ready" means implementable as written, with testable contract acceptance and a named verification
boundary. The slice is `trade-foundation`, `empire-seed` I1–I5 plus `exchange-role` and the building rows,
`legion-build` wave 1, `world-continuity` `world-state-vocabulary`, and `sector-yield`.

| Module | Verdict | Blockers / caveats |
|---|---|---|
| `synthetic-graph`, `step-benchmark`, `routing-guard` | Ready | — |
| `world-stamp` | Ready | C1 decides how consumers use it; the module itself is sound |
| `ledger-keys` | Ready | m1 (text) |
| `stock-deltas` | Ready | Walk the Located-good class too (named by `located-stock` §Dependencies) |
| `world-stock-ledger` | Ready | — |
| `material-ledger` | **Blocked** | C3 (SE4.38) |
| `economy-report` | Ready | M8: make it the one `trade.v1` creator; its tuning boundary row (M6) |
| `system-commands` | Ready | — |
| `sector-features` | Ready with caveat | Lands after empire-seed's schema widening (M5); BuildResolver edits are world-map's (X-11); real content needs C2 |
| `structures-adapter` (I1), `band-reader` (I2), `world-budgets` (I5), `world-exemplars` (I4) | Ready with caveat | No verification boundary (M6) — the pytest command is the stated boundary |
| `structure-bands` (I3) | Ready with caveat | Carries the `structureKind: none` rule behind C2; field-shape rule vs `locatedYields` (M7); M6 |
| `exchange-role` | Ready | m3 (text) |
| `trade-structure-rows` | **Blocked** | C2 (acceptance 7 locks the rows unloadable); M6 |
| `member-stack`, `caravan-kind-retire`, `role-aware-placement` | Ready | `member-stack` migration orders after `world-stamp` (stated, `spec-member-stack.md:324`); Commander arm waits on `legion-commander` (stated) |
| `world-state-vocabulary` | Ready | Crosses Core, Data and Server (full suite once at the end, stated); `CreateWorld` order with `world-stamp` (M4) |
| `located-goods-registry`, `located-stock`, `production-halt`, `bank-points`, `legion-equipment-stock` | Ready | M3 for `located-stock`'s canonical slot; tests use fixture rows and synthetic piece ids |
| `warehouse-axis` | Ready with caveat | `warehouseBand` ownership (M7); real Storehouse needs C2; M8 (`trade.v1` creator) |
| `structure-upkeep` | Ready with caveat | Cannot "land first" while its flag is unregistered (C1); M8 |
| `income-parity` | Ready with caveat | Its flag must follow `trade.logistics` (C1, M2); IP1/IP2 declared gaps (X-25, X-26) |
| `banking-fact` | **Blocked** | C3; C1 (it registers `trade.sectorYield` that three other modules also gate on) |
| `yield-structures` | **Blocked** | M7 (`locatedYields`/`yieldBand` has no empire-seed owner); C1 |
| `essence-loop-read` | **Blocked** | X-5: the fusion half is the creature program's and the spec will not ship one half alone |

Totals: 19 Ready, 9 Ready with caveat, 5 Blocked (counting each module in a grouped row).

---

## 7. Recommended fix order

1. **Owner rulings** on questions 1–3 (§8). Record them as round 6 in `decisions-round-4.md`.
2. **C2** — land the chosen `StructureKind` answer in `structure-bands` §5.4, `trade-structure-rows` §2 and
   acceptance 7, `exchange-hub` §1, and E-A22, in one docs pass.
3. **C1** — apply the ruling to `spec-world-stamp.md` §2 and to every flag owner (the 16 rows at
   `spec-world-stamp.md:348-355`); `structure-upkeep` stops claiming it can land first.
4. **C3** — schedule SE4.12–SE4.38 in the solid-enforcement plan, or record the chosen alternative.
5. **M6** — verification boundaries for seedsmith, the corpus and every new tuning domain, before any
   empire-seed code.
6. **M2 + M3 + M4 + M7 + M8** — one "integration ledger" section in the umbrella map: ruleset bumps and
   capability rows in order; the `WorldCanonical` append order; landing order per hot file; the
   `structure-seed` publish and regeneration order with the consumer-added anchor fields; one creator per
   versioned tuning file.
7. **M5** — split empire-seed's schema widening out of `trade-structure-rows` and put it before
   `sector-features`.
8. **M1** — the four registration seams, then correct umbrella §1 row 10 and the §2 sentence.
9. File the cross-program asks (§5) that are not already on their owners' maps.
10. Sweep the Minor rows (§4).

---

## 8. Owner questions (genuine — each changes behaviour or another program's schedule)

**Q1 — How does a sub-program ship in waves without changing a stamped world's rules mid-life? (C1)**
- (a) One capability row and one `RulesetVersion` bump per landing wave (e.g. `trade.logistics` rows per
  wave). Faithful to D-C; about 30–40 bumps across the family, each one ending re-derivation of older
  trimmed turn reports.
- (b) Register each sub-program's flag once, in the change that lands its **last** wave; earlier waves run
  only on fixture registries in tests and dev. One bump per sub-program (about 11), D-C holds, but no
  player-facing world sees a sub-program until it is complete.
- (c) Declare stamps binding only from the first public release; until then a flag may gain behaviour
  after registration. Cheapest; every pre-release save may change rules on update.
- **Recommendation: (b).** It keeps D-C exactly, matches the stamp's own *"several capabilities shipped in
  one change may share one bump"*, and the fixture-registry test path already exists (world-stamp
  acceptance 4).

**Q2 — What makes a feature building loadable? (C2)**
- (a) One new neutral member, `StructureKind.Feature` (does nothing in the loam/siege economy; behaviour
  comes from `FeatureUnlock`). All seven feature rows use it, and `StructureKind.Exchange` is withdrawn.
  One reviewed widening, which amends X1's wording.
- (b) Make the kind optional (`none` loads when the row has magnitudes and a non-`none` `featureUnlock`).
  No new member, but a nullable `Kind` touches every `switch` on it.
- (c) Per-building kinds (`Exchange`, `Depot`, `Embassy`, `RiftAnchor`, …), which X1 forbids.
- **Recommendation: (a).** It is the smallest change and follows the `Obstacle` precedent of a kind that
  deliberately does nothing economic. It keeps X1's real intent: no gate ever reads a kind.

**Q3 — Banking waits on save-identity SE4.38. Which path? (C3)**
- (a) Schedule solid-enforcement SE4.12–SE4.38 ahead of sector-yield wave 2.
- (b) Land `material-ledger` on today's Tier B `player_id` key and re-point it when SE4.38 lands. The four
  writer sites are edited twice.
- (c) Ship banking for souls and located goods only; materials bank after SE4.38.
- **Recommendation: (a)** if the solid-enforcement lane can start now; otherwise (c), which keeps the
  ledger rule intact and still lets players meet the first throttle.

---

## 9. DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine, economy/resources, structures corpus, tunables, power scale, data/SQL,
    stats (legion-build via ActorHub), verification boundary.
[~] Session boundary: none recorded by this auditor. The caller fenced this session to two writable files
    (this report and an appended umbrella section); nothing else was edited.
[x] Read this session: CLAUDE.md, DESIGN-GATE.md (whole), PRINCIPLES.md §5, the register (whole), the
    umbrella map (whole), the specs listed in the header in full; the rest through extracted sections.
[x] decisions.md: not re-read in full; the findings cite the family register and the specs' own
    decisions.md rows. No finding proposes a new lock; the asks in X-19 are the specs' own.
[x] Every factual claim cites file:line, re-resolved against the working tree before writing.
[x] audit-doc-citations.py --scope run on this file after writing.
[x] Verified against code: StructureCatalog.cs:51, :330; StructureCorpus.cs:65; verify-change.ps1:118;
    WorldCommand.cs (18 kinds); WorldEntityMemberRole (no Commander yet); power-scale.v3.json.
[x] Surrounding sections read for every rule quoted (world-stamp §2, structure-bands §5.4, X1's row).
[x] Constraints tested, not assumed: loadability traced through code; SE4.38 read in the task file.
[x] No §2 invariant contradicted; C2's recommendation keeps X1's intent and says it amends its wording.
[~] Corrections propagated: this audit edits no spec (read-only by charter); the fixes are listed for the
    cluster owners.
[x] No assertion pins a population count.
[x] No event-refreshed cache introduced.
[x] No ordering-fixed acceptance criterion introduced.
[x] No actor magnitude composed.
[x] No SOLID-violating path proposed; M1 fixes are registration seams.
[ ] Registry rows: none added (docs-only audit).
```

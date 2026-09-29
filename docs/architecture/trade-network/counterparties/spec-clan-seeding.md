# Spec: `clan-seeding`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `clan-seeding`, row 8 of the
[counterparties map](../counterparties-map.md) (wave 2; depends on `empire-roster` and `need-vector`).
Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) D3 (*"v1 worlds seed neutral clans as
counterparties"*), §7.4 (*"Its personality … is computed from climate and species, never authored per
clan"*), §14b (clans *"pay the same upkeep"*). **Owner decision 2026-09-19:** every clan is seeded with a
loam source, so the `LoamUpkeep` exemption cannot apply to it. **Reconciled with the round-4 owner
decisions 2026-09-19** ([../decisions-round-4.md](../decisions-round-4.md)): **Q5** — *"Both shipped
templates get a clan"* (closes this spec's former open question); **B / Q1** — clan trade opens when the
player builds a **Trading Post**; the relation band sets the spread and blocks only at `hostile` (§6).
**Round 5 (2026-09-20)**, R5-A: **B3** — a caravan unloads at a foreign hub only where the hub's owner has
a Caravan Yard in that sector, so every seeded clan hub also gets a **tier-1 Caravan Yard** (rule 2a);
**A1** — the seat start kit (Counting House, Storehouse) is for **empires**; clans are not empires, never
bank (`sector-yield` `banking-fact` §2: no destination accepts `Clan`) and get none — the reading
`world-continuity` `world-creation` §5a states too; **B1** — a Trading Post may stand on `Wildland` or
`Market`, and a `Market` slot gives a bonus, so the clan's hub keeps its `Market` site.
Session record: `tasks/sessions/trade-network-idea-20260919.json`.

## Objective

Put **neutral clans** on the map: small factions that hold a little ground with a hub site and a loam
source, defend it and never expand, and whose personality — what they crave and pay a premium for — is
**computed** from their climate and the species they field, never authored per clan.

Success looks like: an ice-marsh clan wants fire and has ice to spare because of where it lives and who
lives there; two clans with the same climate and species read the same personality; every clan pays loam
upkeep from the first turn; a world with no clans still validates and plays.

## Scope and non-goals

**In scope:** what a seeded clan must hold (the validation rule), including its seeded Trading Post; the
personality read; the placement recipe for synthetic worlds and the two template versions; the garrison a
clan starts with; the generator constraint rows (as an ask); the capability flag.

**Non-goals:** clan production, consumption and upkeep accounting (`clan-economy`); the hub structure
and prices (`exchange` `exchange-hub`, `price-curve`); the clan policy (`trade-ai` `clan-behaviour`
registers `clan-keeper`); clan requests and elders (`npc-story-events`); names and flavour (`empire-seed`
/ `narrative` content).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The `Clan` kind and its contract: *"defends its ground, never expands"* | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:12-13` |
| The `Market` slot kind (the preferred hub site, ideal §7.1) and the `Rootbed` slot (the loam source) | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:18`, `:25-28`, `:49`, `:74`, `:79` |
| A faction with no rootbed anywhere pays no upkeep at all (rule G-C) | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:51-58` |
| Loam production of a sector, and upkeep of a sector, both computable at turn 0 | `gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:23`; `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:40` |
| A garrison by posture: a warband on `hold` projects a zone of control and does not roam | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:219-230`; `docs/architecture/world/spec-ai-commander.md` §Who gets which policy |
| `stand-fast` exists and files one entity-less order per faction | `gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18`; `spec-ai-commander.md` §The invariant |
| A sector's climate is an element | `gk-core/src/FusionRpg.Core/World/WorldState.cs:154` |

### Wiring gap

Never seeded; no clan policy beyond `stand-fast`.

### Real gap

The seeding rule, the personality read, placement.

## Design

### 1. What a seeded clan holds (validation, gated by `counterparties.clans`)

A faction of kind `Clan`:

1. holds at least one sector;
2. holds at least one sector with a **`Market` slot it owns** carrying a **working Trading Post** — the
   trade building (`StructureDef.Feature == SectorFeature.trade`, `trade-foundation` `sector-features`) at
   tier 1, seeded constructed. Round 4 B makes every
   trade feature need its building (*"Trade: Trading Post → … T1 clan barter"*); a clan hub is no exception,
   so the clan's side of barter exists from turn 0 and the player's side opens when the player builds its own
   Trading Post (§6). The kind and hub behaviour are `exchange`'s (ask A9), the row and its tier variants
   `empire-seed`'s; this rule only requires the seeded structure. A clan's hub stays at tier 1 unless its
   policy builds (the `clan-keeper` policy builds nothing — `trade-ai` `clan-behaviour`);
2a. **(round 5 B3)** holds, in that same hub sector, a **working Caravan Yard** — the caravan building
   (`StructureDef.Feature == SectorFeature.caravans`; the `caravan-yard` row, `Wildland`,
   `../../empire-seed/spec-trade-structure-rows.md` §5.1) at tier 1, seeded constructed — so a player's
   caravan can unload at the clan's hub (`fleet` `depot` §2, `ForeignSite`). The clan's own caravans are
   not a reason: `clan-keeper` files no trade route. A clan hub without its yard is rejected naming rule 2a;
3. holds at least one sector with a **`Rootbed` slot** — its loam source, so G-C never exempts a seeded
   clan (owner decision). If a clan later loses every rootbed, G-C applies to it exactly as to any faction;
   that is the shared rule, not a clan exception;
4. holds a **`Seat` slot** in its hub sector. The same shape of exemption exists for supply: a faction
   with no seat has no supply network and its legions are exempt from supply burn entirely
   (`gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:14-17`; `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:60-62`).
   Principle 10 (every faction runs the same economy) closes it the way the owner closed G-C: at seed;
5. has a known `PolicyId`: `stand-fast` until `trade-ai` registers `clan-keeper`;
6. **can pay its way at seed:** at turn 0, the loam its sectors produce per turn is at least the upkeep
   they cost per turn with its seeded garrison **and its seeded Trading Post's and Caravan Yard's structure
   terms** once
   `sector-yield` `structure-upkeep` adds that term (`LoamProduction.For` against `LoamUpkeep.For`). A clan
   seeded into a deficit would fade away through no choice of anyone's, the countdown G-C's own comment
   warns about (`LoamUpkeep.cs:51-54`).

A world with zero clans validates.

### 2. The garrison

Each clan starts with one warband on `hold` in its hub sector — the garrison-by-posture shape the wild pack
already uses (`WorldTemplateCatalog.cs:219-230`). Its members are drawn from species native to the hub's
climate by the same deterministic roller shape the world already uses for rolled warbands, on a named
stream `clan:<factionId>`. Following `decisions.md` *Creature progression source and spawn ownership*,
this spawn declares its progression source: the seeded level set by the placement recipe (template or
generator), never inferred from species.

### 3. Personality is computed, never stored

```csharp
public static class ClanPersonality
{
    public static INeedVector Of(WorldState world, string clanFactionId);   // = NeedVector.For(world, clan, turn)
}
```

It is the `need-vector` truth side for the clan: the climate term (a clan wants every element-typed good
except its own climate's) and the species term (the elements of the species it fields). Nothing about a
clan's personality is written into a seed or a template. `exchange` reads it as hub demand; the storylet
engine reads it for clan requests.

### 4. Placement

- **Synthetic worlds first** (`trade-foundation` `synthetic-graph`, ask A4): M clans, each a hub sector
  plus zero or more neighbours, climates spread across the elements.
- **Templates (round-4 Q5: both).** A clan enters a shipped template only through a new template version
  under the per-world stamp, like the rival in `empire-roster`:
  - **`first-light` v2** gains one clan on a **spur** — one new hub sector (with `Market`, `Seat`,
    `Rootbed` and one `Wildland` slot for the Caravan Yard, rule 2a) joined by one lane to `ash-waste`, the no-base middle
    (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:90-96`, lanes `:168-177`). The win path
    home → ember/frost → ash-waste → black-gate never enters the spur. Climate `Air` or `Light`, which no
    `first-light` sector uses (its climates are earth, dark, fire, ice, `:90-153`), so the clan has
    something to trade (P12).
  - **`two-hearths` v2** gains one clan on a **second spur** off the corridor, distinct from the rival's
    spur (`empire-roster` §3), in a climate neither capital nor the rival uses. The corridor is a single
    chain between the capitals (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:258-268`), so a
    spur keeps the road clear.
  - Both versions land only with the version-aware template build (A4).
- **The generator** (world-map wave 4) gets constraint rows (ask A3): every clan has a hub site, a free
  `Wildland` slot beside it for its Caravan Yard (round 5 B3), a seat and a rootbed; a clan's ground is off every shortest path between the player's homeworld and the dominant enemy
  empire's seat (at peace, borders are closed — `diplomatic-stance` §3 — so a clan on the only road would
  wall off the win condition); clans cover several climates per world.

### 5. The capability flag

`counterparties.clans` joins `world-stamp`'s registry in **`counterparties` wave 2**, sharing that wave's
single `RulesetVersion` bump with `counterparties.stance` (round 6 C1; row 16 of
[../landing-order.md](../landing-order.md) §2). It gates rule set §1 — clans on the map — and **nothing
else**: `clan-economy` is wave 3 and gates on its own flag `counterparties.clanEconomy`
(`spec-clan-economy.md` §2). *(Corrected by round 6 C1: this flag used to gate "every clan pass in
`clan-economy`" too, spanning two waves, so a world stamped at wave 2 would have gained a clan economy
mid-life when wave 3 merged.)*

### 6. How clan trade opens (round 4 B / Q1 — consumed, not owned)

The register: *"Clan trade at world start opens by building a Trading Post; the relation band still sets the
spread and blocks trade only at `hostile`."* This module seeds the clan's side (rule 2). The rest is owned
elsewhere and stated here so the seed is fit for it:

- the **player's** Trading Post (tier 1) is what unlocks clan barter — `exchange`'s gate, not a seed rule;
- the band sets the spread and blocks only at `hostile` — `exchange` `trade-access`/`price-curve` reading
  `relation-facts`' logged band. The clan base band is `wary`
  (`npc-story-events/spec-narrative-vocabulary.md:132`), so a newly met clan trades from the player's first
  Trading Post. *(`exchange-map.md`'s Q1 no longer conflicts: round 5 **X10** ruled that its Q1 row follows
  the A-rules, so this clause is resolved — audit m4.)*
- **no Embassy** is ever needed with a clan (`diplomatic-stance` §9).

## Tunables

None here. Garrison size and level are placement-recipe content (template or generator), not balance
numbers of this module; demand coefficients are `need-vector`'s.

## Numeric types

No magnitudes produced. The seed-time loam check compares `long` values the loam code already returns.

## Acceptance (contract)

1. Every seeded clan satisfies §1 rules 1–6; each rule has a negative test that is rejected with the rule
   named.
2. Two clans with the same climates and the same species read identical personalities; changing one
   clan's garrison species changes its personality and nobody else's.
3. Personality is recomputed from state: no field on `WorldFaction` or `WorldSector` stores it (source
   scan).
4. A clan-stamped world with zero clans validates and plays; a legacy world never runs a clan rule.
5. On every clan-stamped template version (`first-light` v2, `two-hearths` v2), a path from the player's
   homeworld to the dominant enemy empire's seat crosses no clan sector.
6. Every seeded clan's hub `Market` slot carries a constructed trade building at tier 1, and the same hub
   sector a constructed caravan building at tier 1 (round 5 B3); a clan seeded without either is rejected
   naming rule 2 or 2a. No clan sector holds a banking or storage building from seeding (A1 is for
   empires).
7. No test pins the number of clans on a map; synthetic runs print it.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Clans/ClanSeedingTests.cs` (new): the six rules, personality
  determinism, zero-clan world, path rule.
- Synthetic worlds with M clans (`trade-foundation` builder) validate and replay.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/WorldValidation.cs','src/FusionRpg.Core/World/Trade/Clans/ClanPersonality.cs','tests/FusionRpg.Core.Tests/World/Trade/Clans/ClanSeedingTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Trade.Clans|FullyQualifiedName~WorldInvariant"
```

## Hard edges

- **Template versions under replay.** A clan added to a shipped template follows the same rule as the
  rival: version-aware `WorldTemplateCatalog.Build` first (A4), content second.
- **Loam balance at seed.** Rule 6 (corrected from "Rule 5" by the 2026-09-20 audit — the rules were renumbered when rule 2a arrived) ties a seeding recipe to loam tuning; a loam balance publish can make a
  previously valid clan recipe invalid. That is the check doing its job: the recipe is fixed, never the
  check loosened.

## Dependencies

| Consumes | From |
|---|---|
| `NeedVector.For` | `need-vector` |
| Roster validation shape, dominant-empire rule | `empire-roster` |
| Stamp, template version, synthetic builder | `trade-foundation` (A4) |
| Constraint rows | world generator (A3) |
| The Trading Post **row** and its tier-1 variant — read from `empire-seed`, and the tier from `sector-features`; **not from `exchange`** (audit M1, edge 2: naming `exchange-hub` here pointed up the family build order, and the row was never exchange's to give). Round 6 C2: the row loads as the neutral `StructureKind.Feature`, so a seeded clan hub's Trading Post can actually be placed and counted — until C2 it could not load at all | `empire-seed` `trade-structure-rows`; `trade-foundation` `sector-features` |
| The caravan building (`caravan-yard`, round 5 X12) and the foreign-hub unload rule (B3) | `fleet` `depot`; `empire-seed` `trade-structure-rows` |
| The `trade` feature and the placed tier (seeded at 1, the default), read through `TierFor`/`FactionTier` so round 6 **S1** holds — a seeded building on a slot the clan does not hold counts for nobody | `trade-foundation` `sector-features` §5a |
| Wave and flag: `counterparties` **wave 2**, flag `counterparties.clans`, sharing that wave's single `RulesetVersion` bump with `counterparties.stance` (round 6 C1; landing-order row 16). `clan-economy` gates on **wave 3**'s `counterparties.clanEconomy`, not on this flag | `trade-foundation` `world-stamp` |

| Exposes | To |
|---|---|
| Clan validation, `ClanPersonality.Of` | `clan-economy`; `exchange` `exchange-hub` (hub sites and their seeded Trading Posts, A9); `trade-ai` `clan-behaviour`; `npc-story-events` petition host |

## Contradictions found

None new. Map C2 (G-C exemption) is closed by the owner's decision and rule 3.

## Open questions

None. The former question 1 (*which shipped template gains a clan*) is answered by round-4 Q5: **both**
(§4). The clan hub's Trading Post follows from round 4 B by principle.

## Design-gate checklist

```
[x] Subsystems: world model and validation, templates, loam upkeep and production, world AI policy ids.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus decisions.md :113 (spawn progression
    source).
[x] decisions.md: :113 honoured (the garrison declares its progression source).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: FactionKindCatalog, SlotTypeCatalog Market/Rootbed, LoamUpkeep G-C, the wild
    garrison entity, LoamProduction.For.
[x] Surrounding sections read (§7.4, §14b clan row, G-C comment).
[x] No "moves goldens" claim.
[x] No §2 invariant contradicted.
[x] Corrections propagated: owner decision recorded in the map; A9 filed.
[x] No population pinned.
[x] No cache; no ordering; no actor magnitude beyond seeded members (whose stats compose through ActorHub
    like every warband's).
[x] No SOLID-violating path: personality is need-vector, not a second demand table.
[ ] Registry row: none proposed.
```

## Audit 2026-09-20

Fixed here: Hard edges cited the seed-pay rule as rule 5; it is rule 6. Checked and clean: personality is
computed from climate and fielded elements through `need-vector` (never stored, never authored); every clan
pays loam upkeep from turn 0 (rootbed and seat at seed, the G-C and supply exemptions closed by principle 10);
the seeded Trading Post and Caravan Yard are counted in the seed-pay check; the win path crosses no clan
ground; a world with zero clans validates. Reported (another program's file, `trade-foundation`
`sector-features`): an assault can take a clan hub's Trading Post **slot** without the sector
(`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:146-161`); whether the clan's hub still trades is the
slot-versus-sector owner rule that module owns (counterparties-map *Audit 2026-09-20*, CX1).
**Verification boundary:** the `core-world-trade-counterparties` owner boundary (`spec-empire-goods-sinks.md`
*Audit 2026-09-20*) covers `World/Trade/Clans/**`; `WorldValidation.cs` stays on `core-fallback`.


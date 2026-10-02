# Spec: `ledger-keys`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `ledger-keys`, §2.5 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; no dependencies). Umbrella
invariant 6 ([../../trade-network-map.md](../../trade-network-map.md) §5): *"the key grammar and the
closed `factKind` vocabulary are `trade-foundation`'s; no sub-program mints a second one."* Principle
P14 ([../../economy-principles.md](../../economy-principles.md) §P14).

## Objective

Every mutation of a banked or world stock carries a dedupe key from a durable fact id, so replay and
re-commit can never double-count (P14). The soul ledger proves the pattern but its key is free text
chosen per call site. This module is the **one key grammar and the one closed fact-kind vocabulary** for
every trade-era ledger row — world stocks and banked materials alike — in Core, pure, no I/O.

Success looks like: two different facts can never produce one key, a key round-trips to its fact, an
unknown fact kind throws, and every later sub-program widens the vocabulary by one reviewed line instead
of inventing a string.

## Scope and non-goals

In scope: `LedgerFact` (two scopes), its encoder and decoder, `FactKind` (closed), and their tests.

Not in scope: any table or SQL (`world-stock-ledger`, `material-ledger`); emitting facts
(`stock-deltas`); the soul ledger, which keeps its own key.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Soul ledger: `UNIQUE(player_id, reason, dedupe_key)`, `INSERT OR IGNORE`, balance folded only when the row is new | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:684-696`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:138-168` |
| Soul dedupe keys are free text per call site (fusion passes its correlation id as both ref and key) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:530-532` |
| Material spend log keys on `(player_id, correlation_id)` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:57-69` |
| A world turn is a durable, unique fact: one turn-log row per `(world_id, turn)` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:41-51` |
| `SaveId`, `EmpireRef` exist in Core (SE4.11 done) | `tasks/solid-enforcement-todo.md:339-348` |
| World faction ids share the save-empire id space; a closure contract binds the two tables | `docs/architecture/solid-enforcement/spec-save-identity.md:77`, `:96-100` |

### Real gap

No grammar for world facts, and no fact-kind vocabulary anywhere.

## Design

### 1. Two scopes, one fact type (`src/FusionRpg.Core/World/Ledger/`)

```csharp
public enum LedgerScope { World, Account }          // closed, two members

public sealed record LedgerFact
{
    public required LedgerScope Scope { get; init; }
    public required long SaveId { get; init; }        // SaveId value (players.id)
    public string? OwnerId { get; init; }              // world faction id / empire id; null = unowned ground
    public required string FactKind { get; init; }     // FactKinds member
    public required string GoodId { get; init; }       // stock or material id: "loam", "rubble", "essence.fire", …

    // World scope only
    public string? WorldId { get; init; }
    public int? Turn { get; init; }
    public string? Holder { get; init; }               // "s:<sectorId>" | "e:<entityId>" (| "f:" / "r:" once widened, §4a)

    // Account scope only
    public string? SourceKind { get; init; }           // "fusion", "salvage", "expedition", "loot", "recipe", "migration"
    public string? SourceId { get; init; }             // the durable id of that source row
}

public static class LedgerKey
{
    public static string Encode(LedgerFact fact);     // validates, then encodes
    public static LedgerFact Decode(string key);      // exact inverse; malformed input throws
}
```

A **world** fact is `(save, owner, world, turn, factKind, holder, good)` — the umbrella's
`(save_id, empire_id, world_id, turn, factKind, sector, good)` with `sector` widened to **holder**,
because loam is held by legions as well as sectors (`gk-core/src/FusionRpg.Core/World/WorldState.cs:327`) and a
legion's carried loam changes every turn it is out of supply
(`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:124-146`).

An **account** fact is `(save, owner, factKind, sourceKind, sourceId, good)`: banked materials have no
world and no turn; their durable fact is the source row that moved them (a fusion correlation, a
salvage event, an expedition id, a loot correlation, a recipe correlation).

### 2. Encoding — injective by construction

`Encode` writes the scope tag, then every field of that scope **in a fixed order**, each as
`<length>:<value>` joined by `|`, with null written as `-` (a length prefix can never be `-`):

```
w|<save>|<len>:<owner>|<len>:<world>|<turn>|<len>:<factKind>|<len>:<holder>|<len>:<good>
a|<save>|<len>:<owner>|<len>:<factKind>|<len>:<sourceKind>|<len>:<sourceId>|<len>:<good>
```

Length prefixes make the encoding injective without escaping any character, so ids may contain `|` or
`:` and still never collide. Integers use `CultureInfo.InvariantCulture`, the canonical writer's rule
(`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:149-159`). The string is an internal key, never shown to a
player.

`Encode` validates before writing: the scope's required fields are present and the other scope's are
null; `FactKind` is a member of `FactKinds`; `Turn >= 0`; `Holder` starts with a registered holder prefix
(`s:` or `e:` in v1; `f:` and `r:` join with their emitters, §4a). Any failure throws `ArgumentException`.

### 3. The owner column — decided here, not by the owner

The umbrella names the owner `empire_id`, but clans are factions, not save empires
(`spec-save-identity.md:96-100` binds only faction ids that name an empire), and an unowned sector's loam
has no owner at all. So the key carries the **world faction id** (the same id space as `empire_id`,
`spec-save-identity.md:77`), nullable. The ledger tables' closure contract resolves a non-null owner to
`rpg_save_empires` when it names an empire of the world's save and to `rpg_world_factions` otherwise.
Recorded as the map's decision; it changes no behaviour.

### 4. The fact-kind vocabulary — closed, v1

`FactKinds` is a C# registry of `(Id, Scope)` rows. v1 holds exactly the kinds whose emitters exist or
land in this sub-program:

| Id | Scope | Emitted by (today's code) |
|---|---|---|
| `open` | both | opening balance: world creation, first ledger write for a pre-existing world or balance |
| `produce` | world | loam production `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:57-66`; rubble and ironwork `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:90-103` |
| `upkeep` | world | pooled upkeep draw `LoamPhases.cs:160-165` |
| `topup` | world | legion top-up from its component (sector −, legion +) `LegionSupply.cs:98-104` |
| `burn` | world | legion burn out of supply `LegionSupply.cs:124-146` |
| `sustain` | world | legion loam deposited into a sector `gk-core/src/FusionRpg.Core/World/Movement/SustainResolver.cs:71-76` |
| `construct` | world | build cost from carried loam, rubble, ironwork `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:150-158` |
| `develop` | world | sector project cost `gk-core/src/FusionRpg.Core/World/Growth/DevelopResolver.cs:77` |
| `pulse` | world | recruit accrual `gk-core/src/FusionRpg.Core/World/Growth/GrowthPhases.cs:66` |
| `raise` | world | recruit spend `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:108` |
| `lost` | world | a holder's stock leaves the world with it (a legion destroyed or starved, `LegionSupply.cs:134-140`) |
| `grant` | account | material credit (loot, salvage, expedition, workbench) |
| `spend` | account | material debit (fusion, recipe) |
| `rename` | account | a material id rewritten by a migration (`gk-core/src/FusionRpg.Data/Sqlite/Migrations/ShardRungs.cs:60-99`) |

The count is **pinned in its test with the reason**: a closed vocabulary the code owns; a new member is a
reviewed change made by the sub-program that ships its emitter (`bank`, `depart`, `deliver`, `loss`,
`settle-buy`, `carry`, `rift-depart`, `rift-arrive`, … — the full list is §4a). `refine` joins when the
construction chain wires the refine step, which has zero callers today (`SiegeConstruction.cs:33`, `:47`).
`halt` is not a fact kind: a halted production moves no stock. There is no one-kind `settle` (round 5 X2).

### 4a. Widenings requested by other programs (reconciliation 2026-09-19)

Each lands in the change that ships its emitter, as a reviewed change to the pinned vocabulary. Listed
here so no program mints a free-text kind and no two programs mint one kind twice.

| Kind(s) | Scope | Requested by |
|---|---|---|
| `bank` | world | `sector-yield` `banking-fact` |
| `income` | world | `sector-yield` `income-parity` (round 4 Q11) |
| `depart`, `deliver`, `waste`, `return` | world | `logistics-flow` `transit-buffer` (a departure moves stock from a sector to its route's `r:` holder; arrival, delivery overflow and return move it back or out — audit 2026-09-20) |
| `loss`, `refine` | world | `logistics-flow` (`lane-loss`, `construction-chain`) |
| `carry` | world | `fleet` `carried-goods` (used as if it existed — `fleet/spec-carried-goods.md` §Design; no ask filed) |
| `consume` | world | `counterparties` `clan-economy` |
| `sink`, `collapse` | world | `counterparties` `empire-goods-sinks`, `conquest-consequences` (A10) |
| `settle-buy`, `settle-sell`, `fee`, `tariff-grant`, `tariff-sink` | world | `exchange` `settlement-payment` |
| `deal-leg` | world | `exchange` `treaty-lifecycle` (a treaty's goods leg settled through `settlement-payment` §7; exchange ask E-A24, added 2026-09-20) |
| `rift-depart`, `rift-arrive` | world | `rift-trade` `crossing-handoff` (A10) |
| `soul-pay` | — (a soul-ledger dedupe key built with `LedgerKey`, not a `FactKinds` member) | `exchange` `settlement-payment` |

**Resolved 2026-09-20 (round-5 ruling X2):** exchange's five settlement kinds apply, and the treasury uses
them too (a treasury credit from a sale is `settle-sell`). `counterparties/spec-empire-treasury.md` once used
a one-kind `settle`; round 5 re-pointed it. No `settle` member exists.

**Holder widening (counterparties A10).** An AI treasury is held by a **faction**, not a sector or a
legion. The holder grammar gains a third prefix `f:<factionId>` (and `stock-deltas`' `StockHolderKind`
gains `Faction`), added in the change that ships `counterparties` `empire-treasury` — not a sentinel
sector value. `world-continuity` `background-yield`'s coarse records use the same kinds (never `bank`, its
allow-list).

**Holder widening (logistics-flow, audit 2026-09-20).** Goods in transit are held by neither a sector nor
a legion: they sit on a **route** (`logistics-canonical` `TransitPacket`, keyed `(faction, source, good)`).
The holder grammar gains a fourth prefix `r:` whose body is the route key written with the same
length-prefixed encoding as §2 (`r:<len>:<faction><len>:<source><len>:<good>`), so ids containing `:` stay
injective; `StockHolderKind` gains `Route`. Added in the change that ships `transit-buffer`. Without it a
departure would take stock out of a warehouse with no holder to receive it, and `stock-deltas`'
reconciliation and `world-stock-ledger`'s per-holder sums would fail on the first logistics turn.

**Account-scope source for banked materials (audit 2026-09-20).** A banking fact that credits a human
empire's materials is an **account** fact in `material-ledger`: factKind `grant`, `sourceKind`
`world-bank`, `sourceId` = the world `bank` fact's own encoded key. The account key therefore embeds the
world key, and re-committing a turn re-derives both (`sector-yield` `banking-fact` §4).

### 5. Determinism

Pure string functions; no clock, no RNG, no culture dependence. Keys depend only on the fact.

## Tunables

None.

## Acceptance criteria (contract)

1. **Injective:** a property test over generated facts — including ids containing `|`, `:`, `-` and
   digits, empty strings and nulls — never produces one key for two unequal facts.
2. **Round trip:** `Decode(Encode(f)) == f` for every valid fact; `Decode` of a truncated or altered key
   throws.
3. `Encode` throws for an unknown fact kind, a kind used in the wrong scope, a missing required field, a
   field of the other scope, a negative turn, or a holder without a registered prefix (`s:`/`e:` in v1;
   each widening adds its prefix and a test that the other prefixes still round-trip).
4. `FactKinds` membership is pinned with the closed-vocabulary reason; `LedgerScope` has exactly two
   members, pinned with the same reason.
5. Keys are identical across cultures (the test runs `Encode` under two `CultureInfo`s).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ledger/LedgerKeyTests.cs` (new),
  `[Trait("VerificationId", "core.world-ledger-keys")]`.
- `gk-core/scripts/verification-boundaries.v1.json` owner row `core-world-ledger`: paths
  `src/FusionRpg.Core/World/Ledger/**` and `tests/FusionRpg.Core.Tests/World/Ledger/**`, project `core`,
  verificationId `core.world-ledger-keys`, level `focused`.
- Verify: `.\scripts\verify-change.py -Paths <changed files> -Session <id>`.

## Hard edges

None: pure Core, no schema, no hash.

## Boundaries

- **Always:** widen `FactKinds` in the change that ships the emitter.
- **Ask first:** a third scope.
- **Never:** build a ledger key by string concatenation anywhere else; mint a free-text fact kind.

## Dependencies and interface

**Depends on:** nothing (types only; `SaveId` from `save-identity` SE4.11, done).

| Exposed | Consumer |
|---|---|
| `LedgerFact`, `LedgerKey.Encode/Decode` | `world-stock-ledger`, `material-ledger`; later `sector-yield` `banking-fact`, `rift-trade` |
| `FactKinds` | `stock-deltas` (every delta names one), every later sub-program that adds a kind |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy ledgers (design only), save identity (read).
[~] Session boundary: trade-network-idea-20260919 covers this doc; boundary check not re-run.
[x] Read this session: economy-principles P14 and §12-§13; spec-save-identity decision 2 and the
    new-table rule; trade-foundation map §2.5; umbrella invariant 6.
[x] decisions.md: Empire resource registry row (:108) — no quantity is added here.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: every stock mutation site listed in §4 was opened; the soul ledger's key.
[x] Surrounding sections read (LegionSupply.Resolve whole; LoamPhases.Pressure's component loop).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: "sector" widened to "holder" is recorded in the map's corrections section.
[x] Pinned counts are closed vocabularies with a stated reason; no population pinned.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion.
[x] ActorHub: not touched.
[x] No SOLID fork: one grammar for both ledgers; the soul ledger is left alone rather than forked.
[x] No new guarded rule (the grammar's single use is enforced by review and by the ledgers calling it).
```

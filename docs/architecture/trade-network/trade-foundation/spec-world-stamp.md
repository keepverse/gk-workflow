# Spec: `world-stamp`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `world-stamp`, §2.4 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; no dependencies). Ideal:
[../../trade-network-ideal.md](../../trade-network-ideal.md) §14 **D-C** (the program's one irreversible
gate) and §14b ("the per-world stamp covered only the ruleset"). Umbrella map X3, X4.
Owner-decided 2026-09-19, recorded in the map: **old ruleset code retires only when no world in any
state carries that stamp** (hibernating and idle worlds keep their stamps); **the difficulty profile id
lives on this stamp** (`world-continuity-ideal.md` §6.10; `world-continuity-map.md` module 14).

## Objective

A world must say which rules it runs on, so that a phase a later sub-program adds runs only on worlds
that started with it. Today the column meant to say so has never carried a real ruleset
(`rpg_worlds.ruleset_version` defaults to 1 and creation writes the literal 1, while the live
`TurnEngine.RulesetVersion` is 13). This module adds **one per-world stamp** — ruleset version, template
version, the tuning manifest the server loaded, and the difficulty profile id — written when a map world
is created, carried on `WorldState`, and read inside `Step` as **capability flags** from a closed C#
registry. Every world that exists before the change reads back as **legacy**, which grants no
capability, so it plays and hashes exactly as today.

Success looks like: a world created after the change stores the live ruleset and the loaded tuning
manifest; every existing world loads as legacy with an unchanged hash; replay refuses with a named reason
when the tuning or template it would need is not what is loaded; and the first sub-program that adds a
capability flag (`sector-yield` wave 1's `trade.sectorYield`) can gate its behaviour on one call.

## Scope and non-goals

In scope: the `WorldStamp` record and its hashed projection; the capability registry (shipped empty);
the tuning manifest; template versions; persistence columns; the create path; the replay gate; the
`IWorldView` read; the retirement census query.

Not in scope: any capability flag (each ships with the sub-program that owns its behaviour); the
difficulty profile **catalog** and its knobs (`world-continuity` `world-difficulty-profile`); production
world creation (`world-continuity` `world-creation`); running two tuning versions side by side (X4 —
tuning stays process-global).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `rpg_worlds` carries `engine_version` and `ruleset_version`, both `DEFAULT 1`, plus `state`, `mode`, `catch_up_cap`; `kind` added later via `EnsureColumn` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:20-35`, `:204-206` |
| Creation validates first, then writes the literals `1, 1` | `RpgStore.World.cs:219-254` (insert `:242-245`) |
| Delve worlds are inserted with the same literals, `kind='delve'` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:190-192` |
| The only map-world creation in `src/` is the SIM-only test endpoint | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:600-624` |
| Every turn-log row records the live engine and ruleset versions | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:41-51`, `:666-681` (`$rv` at `:675`) |
| Replay: served from the stored report when present; otherwise refuses on an engine/ruleset mismatch (returns `null`, no reason), refuses delve worlds, rebuilds from the **current** template and re-steps | `RpgStore.WorldTurns.cs:738-780` (mismatch `:759-760`, delve `:767`, rebuild `:769`) |
| `RulesetVersion = 13`, `EngineVersion = 1`; a new phase that no existing log can populate needed no bump | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:20`, `:125`, `:133-141` |
| Conditional canonical rows keep old hashes byte-identical when a new field sits at its default (`faction-scope`, `slot-hp`, `slot-depletion`, `sector-rubble`, `sector-ironwork`) — and the `faction-scope` comment records that appending a column instead *"moved WorldWaveOneAcceptanceTests' own golden even at the neutral default"* | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:90-129` |
| The canonical `world` row carries template id, seed and turn, never the world id | `WorldCanonical.cs:24-27` |
| Tuning is loaded once per process from literal file names into static hubs; every tuning file carries a top-level `version` | `gk-core/src/FusionRpg.Server/Program.cs:32-116`; e.g. `gk-core/data/tuning/world.v6.json` (`"version": 6`) |
| The diff writer's equivalence guard reloads the graph, copies four header fields onto it, and asserts the two hashes match | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:56-67` |
| `LoadWorldState` copies the same four header fields onto the loaded graph | `RpgStore.World.cs:437-450` |
| The commit path loads the world through `LoadWorldState` | `RpgStore.WorldTurns.cs:500-501` |
| Templates are built by id with no version | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:39-45` |
| One `IWorldView` implementation | `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:76` |
| The only per-faction knob today is `UpkeepHandicapMilli`; no difficulty profile exists in `src/` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:79-83` |
| Additive schema evolution is the house rule; backup + marker + one transaction is reserved for **key-widening** migrations | `docs/architecture/decisions.md:90` |

### Wiring gap

`ruleset_version` exists and has never been meaningful (`RpgStore.World.cs:31`, `:244`).

### Real gap

No stamp record, no capability registry, no tuning manifest, no template version, no difficulty id, no
replay check on tuning or template.

## Design

### 1. Types (Core, `src/FusionRpg.Core/World/Stamp/`)

```csharp
public sealed record WorldStamp(
    int RulesetVersion,                 // TurnEngine.RulesetVersion at creation; LegacyRuleset for legacy
    int TemplateVersion,                // WorldTemplateCatalog.CurrentVersionOf(templateId) at creation
    TuningManifest Tuning,              // every tuning file the server loaded, sorted by domain
    string DifficultyProfileId)         // world-continuity's catalog id; "default" in v1
{
    public const int LegacyRuleset = 0; // structural sentinel: no real ruleset is 0
    public static readonly WorldStamp Legacy = new(LegacyRuleset, 0, TuningManifest.Empty, DifficultyProfiles.Default);
    public bool IsLegacy => RulesetVersion == LegacyRuleset;
}

public sealed record TuningManifest(IReadOnlyList<TuningEntry> Entries)   // ordinal by Domain, unique
{
    public static readonly TuningManifest Empty = new(Array.Empty<TuningEntry>());
    public string Canonical();          // "domain=version\n" per entry
    public string Digest();             // SHA-256 hex of Canonical(), the StateHasher algorithm
}
public readonly record struct TuningEntry(string Domain, int Version);

public sealed record WorldCapabilityDef(string Id, int IntroducedAtRuleset);

public sealed class WorldCapabilityRegistry
{
    public static readonly WorldCapabilityRegistry Shipped = new(Array.Empty<WorldCapabilityDef>());
    public WorldCapabilityRegistry(IReadOnlyList<WorldCapabilityDef> rows);   // validates: kebab/dotted ids, unique, IntroducedAtRuleset > 0
    public bool Grants(WorldStamp? stamp, string capabilityId);              // unknown id throws
    public IReadOnlyList<string> GrantedBy(WorldStamp? stamp);               // ordinal order
}

public static class DifficultyProfiles
{
    public const string Default = "default";   // the one legal id until world-continuity's catalog lands
}
```

`WorldState` gains `public WorldStamp? Stamp { get; init; }`. **`null` means unstamped**: a template or
test build that has not been through the store. Null and legacy both grant nothing.

### 2. What a capability is, and the retirement rule

A capability is granted by **ruleset**: `Grants(stamp, id)` is true when the stamp is non-null,
non-legacy and `stamp.RulesetVersion >= def.IntroducedAtRuleset`. The sub-program that ships a
behaviour adds one row with the `RulesetVersion` it bumps to, in the same change, and gates its phase on
`WorldCapabilityRegistry.Shipped.Grants(world.Stamp, id)`. The registry is a **closed vocabulary**; its
member count is a reviewed change, pinned in its test with that reason.

**The bump is mandatory, and it is not the gate (audit 2026-09-20).** A capability row **must** carry a
`RulesetVersion` strictly above every ruleset any world was stamped with before that row existed — in
practice, the change that adds the row bumps `TurnEngine.RulesetVersion` by one and uses the new value.
A row registered at the *current* ruleset would grant the capability to every world already stamped at
that ruleset — worlds created before the behaviour existed — and move their hashes mid-life, which is the
exact breach of D-C this module exists to prevent. The bump does **not** gate old worlds (their stamps
do); its one cost is the one every earlier bump paid: a trimmed turn report logged under the old ruleset
is no longer re-derived (§8 `RulesetVersion` refusal; the world itself keeps playing). Several
capabilities shipped in one change may share one bump. Consumer specs that said *"no `RulesetVersion`
bump"* (`sector-yield` `banking-fact` §1, `logistics-flow` `logistics-phase`) are corrected to this rule.

**Retirement (owner, 2026-09-19).** The branch a capability replaces — the behaviour a world without it
keeps — may be deleted only when **no world in any state** (`active`, `hibernating`, `idle`, or any later
state value; delve rows excluded because `Step` never runs on them) carries a stamp below the
capability's `IntroducedAtRuleset`. Legacy stamps count as below every capability. A world never has its
stamp migrated forward, on waking or otherwise. The store exposes the reading this rule needs —
`ListStampCensus()` returning `(stampKind, rulesetVersion, worlds)` over every `kind='map'` row — and
prints it; nothing asserts it. **Consequence, stated:** saves are local files and the game sends no
telemetry (PRINCIPLES §11), so no census of players' saves exists; in practice a pre-capability branch is
kept for the life of the product. That is the cost the owner accepted; the census only proves the local
case.

### 3. What is hashed — the projection `Step` reads

`Step` reads the capability set and (after `world-difficulty-profile` lands) the difficulty profile. It
never reads the template version or the tuning manifest: tuning is process-global (umbrella X4), and the
template only matters for replay. So the canonical writer hashes **what `Step` reads**, and only when it
is not the neutral value:

```
world-stamp \t <granted capability ids, ordinal, comma-joined> \t <difficulty profile id>
```

written after the `sector-ironwork` loop (`WorldCanonical.cs:123-129`), **only when** the stamp is
non-null and (`GrantedBy(stamp)` is non-empty **or** `DifficultyProfileId != DifficultyProfiles.Default`).
Template version and tuning manifest are persisted provenance, compared by the replay gate, not hashed.

This is a deliberate refinement of the map's *"a non-legacy stamp changes the hash"*. Hashing provenance
would move the hash of every store-created world for values no simulation reads — the exact failure the
`faction-scope` row records (`WorldCanonical.cs:90-94`) — and it would break every Data test that
compares a store commit against a pure `Step` of the template (`gk-core/tests/FusionRpg.Data.Tests/CargoCommands/BudgetDebitTests.cs:538`
is one). With the refinement, **no hash moves until the first capability ships**, and that sub-program
owns its re-bless.

### 4. Persistence (`RpgStore.World.cs`, `RpgStore.WorldTurns.cs`)

Additive columns through `EnsureColumn`, beside the existing ones (`RpgStore.World.cs:204-206`):

| Column | Type / default | Meaning |
|---|---|---|
| `stamp_kind` | `TEXT NOT NULL DEFAULT 'legacy'` | closed: `legacy` \| `stamped` |
| `ruleset_version` | existing | the stamp's ruleset when `stamped`; **never read** when `legacy` |
| `template_version` | `INTEGER NOT NULL DEFAULT 0` | 0 when `legacy` |
| `tuning_manifest` | `TEXT` (nullable) | `TuningManifest.Canonical()`; null when `legacy` |
| `difficulty_profile_id` | `TEXT NOT NULL DEFAULT 'default'` | |

and on `rpg_world_turn_log`: `tuning_digest TEXT` (nullable), written by every commit from the loaded
manifest.

**The migration is the column default.** Every pre-existing row — map and delve — reads `legacy` the
moment the column exists, with no row rewritten, so it is atomic, idempotent and reversible by
construction, and the old `ruleset_version = 1` is never read as a ruleset (X3). The approved map asked
for "backs up the database first, runs in one transaction"; that shape is what `decisions.md:90`
reserves for key-widening migrations, which this is not — nothing is rewritten, so there is nothing to
back up. Recorded as a correction in the map.

`LoadWorldState` (`:437-450`) and the equivalence guard (`RpgStore.WorldGraphDiff.cs:58-61`) set
`Stamp` from the header **with** the four fields they already copy; missing it in the guard would trip
its `Debug.Assert` the first time a capability row is hashed.

### 5. The create path

`RpgStore.CreateWorld(playerId, world)` (`:219`), after validation:

- `world.Stamp is null` → stamp it `WorldStampHub.Current(world.TemplateId)`: live
  `TurnEngine.RulesetVersion`, `WorldTemplateCatalog.CurrentVersionOf(templateId)`, the configured
  manifest, `DifficultyProfiles.Default`.
- `world.Stamp.IsLegacy` → refuse `world.stamp-legacy` (legacy is a migration-only value; a new world is
  never legacy).
- otherwise persist the given stamp after checking `0 < RulesetVersion <= TurnEngine.RulesetVersion`, a
  buildable template version and a known difficulty id (refuse `world.stamp-invalid`).

It writes `stamp_kind='stamped'` and the columns above, and returns the stamped world. The delve insert
(`RpgStore.Delve.cs:190-192`) is untouched: delves stay `legacy` and `Step` never runs on them.

`WorldStampHub.Configure(TuningManifest)` is called once at the composition root. An unconfigured hub
throws on `Current` — a missing input is a load rejection, never a default. Test projects configure it
in a `[ModuleInitializer]` bootstrap, the pattern `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs`
already uses.

### 6. The tuning manifest

`Program.cs` reads each tuning file through one helper, `TuningFiles.Read(tuningDir, fileName, manifest)`,
which returns the text and records `(domain, version)` parsed from the `<domain>.v<n>.json` name and
checked against the file's own `version` field (a mismatch throws). After the last load,
`WorldStampHub.Configure(manifest.Build())`. The manifest covers **every** tuning file the process loads,
not a hand-kept list of "files `Step` reads": a missing domain would let replay run silently on the
wrong numbers, while an extra one costs only an honest refusal. That trade is the point of the stamp.

### 7. Template versions

`WorldTemplateCatalog.CurrentVersionOf(templateId)` returns 1 for `first-light` and `two-hearths`
today. `Build(templateId, templateVersion, seed, worldId)` builds that version or throws
`template.version-unknown`; the existing `Build(templateId, seed, worldId)` builds the current version.
A template edit that changes a built world bumps its version and keeps the old version buildable while
any world carries it — the same retirement rule as a capability. `counterparties` adds `two-hearths`
version 2 through this seam (its ask A4, widened).

### 8. The replay gate

`WorldReplayGate.Check(logRow, header, stamp, loadedDigest, templateBuildable) → ReplayRefusal?`, pure,
in Core, with a closed reason enum:

| Reason | When |
|---|---|
| `EngineVersion` | the turn's logged engine version ≠ live (today's check) |
| `RulesetVersion` | the turn's logged ruleset ≠ live (today's check) |
| `TuningManifest` | the turn's `tuning_digest` is non-null and ≠ the loaded manifest's digest |
| `TemplateVersion` | the stamp's template version cannot be built |
| `NotMap` | `kind != 'map'` (today's delve refusal) |

`GetWorldTurnReport` (`RpgStore.WorldTurns.cs:738`) keeps its `TurnReport?` contract and returns `null`
on any refusal, as today; the reason is available through the pure gate and tested there. Replay rebuilds
with `Build(templateId, stamp.TemplateVersion or current-for-legacy, …)` and sets `Stamp` from the
header before the first `Step`. A turn logged before this module has a null digest and keeps today's
behaviour (no tuning check is possible for it).

### 9. The `IWorldView` read

`IWorldView` gains `IReadOnlyList<string> Capabilities` and `string DifficultyProfileId`, public and never
fogged; `BelievedWorldView` answers from `world.Stamp`. A policy then files trade orders only where
admission will take them (trade-ai ask T-A8).

### 10. Numeric types

Versions are `int`; they count reviewed changes, not magnitudes.

## Tunables

None. The difficulty profile's knobs belong to `world-continuity`'s catalog
(`world-difficulty-catalog.v1.json`, proposed there).

## Acceptance criteria (contract)

1. A map world created through `CreateWorld` from an unstamped template stores `stamp_kind='stamped'`,
   `ruleset_version = TurnEngine.RulesetVersion` (read, never a literal), the configured manifest's
   canonical text and the template's current version.
2. After `EnsureColumn` runs on a database holding pre-existing map and delve worlds, every one of them
   loads with `Stamp == WorldStamp.Legacy`; running schema setup twice changes nothing.
3. **A legacy world hashes byte-identically to today**, and so does a stamped world whose stamp grants no
   capability and names the default difficulty. Every existing world golden in Core.Tests and Data.Tests
   stays green unedited.
4. With a fixture registry that grants a test capability at ruleset *N*, `Grants` is false for a null
   stamp, the legacy stamp and a stamp below *N*, and true at or above *N*; the same world under a
   granting stamp writes the `world-stamp` row and under a non-granting stamp does not.
5. `CreateWorld` refuses a legacy-stamped world and an out-of-range stamp, writing nothing.
6. `WorldReplayGate.Check` returns each reason in its table for a constructed case and `null` when
   everything matches; `GetWorldTurnReport` returns `null` for a trimmed turn whose logged digest differs
   from the loaded one.
7. A stamped world round-trips through commit and reload with an equal `Stamp`, and the diff writer's
   equivalence guard passes with a capability-granting stamp.
8. `WorldCapabilityRegistry.Shipped` has zero members at this module's landing, pinned **with the
   reason** (a closed vocabulary; each later sub-program adds its member and edits the pin in the same
   change). `stamp_kind` has exactly two members, pinned with the same reason.
9. `TuningFiles.Read` throws when a file's name and its `version` field disagree.
10. `ListStampCensus()` counts map worlds in every `state` value, and nothing asserts its numbers.
11. **No retroactive grant.** A registry test asserts, for every row, `0 < IntroducedAtRuleset <=
    TurnEngine.RulesetVersion`, and that the newest row's `IntroducedAtRuleset` equals
    `TurnEngine.RulesetVersion` at the commit that adds it (the landing check); a world stamped at ruleset
    *N − 1* is not granted a row introduced at *N*, and one stamped at *N* is (both directions tested).

## Test plan and verification boundary

- Core: `tests/FusionRpg.Core.Tests/World/Stamp/` (new) — registry, manifest, canonical projection,
  replay gate, template versions. `[Trait("VerificationId", "core.world-stamp")]`.
- Data: `tests/FusionRpg.Data.Tests/World/WorldStampStoreTests.cs` (new) — create, legacy default,
  round-trip, equivalence guard, replay refusal; **in memory**.
  `[Trait("VerificationId", "data.world-stamp")]`.
- `gk-core/scripts/verification-boundaries.v1.json`: owner rows `core-world-stamp` (paths
  `src/FusionRpg.Core/World/Stamp/**` and its test folder; project `core`) and `data-world-stamp` (its
  test file; project `data`; guards `dal`, `test-substrate`). The edits to `TurnEngine.cs`,
  `WorldCanonical.cs`, `WorldState.cs`, `RpgStore.World.cs`, `RpgStore.WorldTurns.cs`,
  `RpgStore.WorldGraphDiff.cs` and `Program.cs` stay on their module fallbacks.
- **This module crosses Core, Data and Server** (AGENTS.md verification point 2): run the full suite once
  at module end, after the focused runs.
- Verify: `.\scripts\verify-change.ps1 -Paths <changed files> -Session <id>`; `python gk-core/scripts/guard-dal.py`.

## Hard edges

- **Save format:** additive columns with defaults; no rewrite, no backup owed (`decisions.md:90`).
  Dropping or renaming a stamp column later is a key-widening-class migration.
- **Golden re-bless order:** none owed here (criterion 3). Each **wave** bumps `RulesetVersion` once and
  re-blesses in its own change, in the order of [../landing-order.md](../landing-order.md) §2 and §6 —
  never batched with another wave's. A legacy world's goldens never move on a bump: the bump changes no
  hashed field. The one recurring cost is the one §2 names: a trimmed turn report logged under an older
  ruleset is no longer re-derived, once per bump.
- **Ruleset stamp:** this module introduces it and does not bump `RulesetVersion`: `Step` behaves
  identically for every world (field-only addition, `TurnEngine.cs:133-141` precedent).
- **The irreversible part** of D-C is not this module's column; it is the first stamped world that a
  capability reaches. From then on that world keeps its rules for its life.

## Boundaries

- **Always:** read a capability through the registry; set `Stamp` wherever the header's four fields are
  copied.
- **Ask first:** migrating any world's stamp forward (the owner ruled it out); a second tuning version
  loaded side by side.
- **Never:** read `ruleset_version` on a legacy row; hash provenance; default an unconfigured hub; a
  capability flag outside the registry.

## Dependencies and interface

**Depends on:** nothing. `world-continuity` owns the difficulty catalog and consumes this stamp.

| Exposed | Consumer |
|---|---|
| `WorldStamp`, `WorldState.Stamp`, `WorldCapabilityRegistry` | the capability rows below; `trade-surface`, `trade-ai`, `economy-report` (trade on/off) |
| `WorldTemplateCatalog.CurrentVersionOf` / versioned `Build` | `counterparties` (two-hearths v2), `world-continuity` `world-creation` |
| `IWorldView.Capabilities`, `.DifficultyProfileId` | `trade-ai` (ask T-A8) |
| `WorldReplayGate`, `tuning_digest` | `world-continuity` `coarse-step` (replay interleave) |
| `ListStampCensus()` | the retirement decision for any capability's old branch |

**Capability rows requested — one flag per wave, one bump per wave (round 6 C1).** The owner's ruling is
*"One capability flag and one ruleset bump per wave. A world's rules never change mid-life; the family
keeps a single landing order"* ([../decisions-round-4.md](../decisions-round-4.md) Round 6 C1). Two rules
follow, and this module enforces both:

- **A flag never spans waves.** Every behaviour a flag gates ships in the one wave that registers it. A
  later wave of the same sub-program gets its **own** flag, never a widening of the earlier one. The
  2026-09-19 list below had one flag for behaviour landing in two to four waves — the defect the global
  audit raised as C1 — and is replaced by the per-wave list.
- **A wave takes exactly one bump.** Where a wave registers several independently-gated surfaces, its rows
  share that one bump (§2, *"Several capabilities shipped in one change may share one bump"*). A wave never
  takes two bumps and two waves never share one.

The family's wave order, its flag per wave and its bump ordinal live in **one** place:
[../landing-order.md](../landing-order.md) §2. This table names the owner and the wave; the ordinal is that
file's, because the engine constant moves under the family and a literal here would go stale on the next
lane to land.

| Flag | Owner and wave | Landing-order row |
|---|---|---|
| `trade.sectorYield` | `sector-yield` W1 (`located-stock` registers; `located-goods-registry`, `essence-loop-read`, `warehouse-axis`, `production-halt`, `bank-points` gate on it) | 1 |
| `trade.structureUpkeep` | `sector-yield` W2 (`structure-upkeep`) | 2 |
| `trade.yieldStructures` | `sector-yield` W3 (`yield-structures`) | 3 |
| `trade.bankingPhase` | `sector-yield` W4 (`banking-fact`, the `Logistics` phase slot only) | 4 |
| `trade.logistics` | `logistics-flow` W1 (`logistics-phase`, `logistics-canonical`; ask A1) | 5 |
| `trade.logisticsLanes` | `logistics-flow` W2 (`path-cache`, `lane-flow`, `transit-buffer`, `lane-loss`, `logistics-facts`) | 6 |
| `trade.logisticsPolicy` | `logistics-flow` W3 (`auto-banking`, `construction-chain`, `lane-verbs`) | 7 |
| `trade.banking` | `sector-yield` W5 (`banking-fact`, the L3 step — after `material-ledger`, round 6 C3) | 8 |
| `trade.incomeParity` | `sector-yield` W6 (`income-parity`) | 10; `IntroducedAtRuleset` ≥ `trade.logistics`' |
| `trade.legionEquipStock` | `sector-yield` W7 (`legion-equipment-stock`) | 11 |
| `trade.fleet` | `fleet` W1 (`carried-goods`, `depot`) | 12 |
| `trade.fleetRoutes` | `fleet` W2 (`crew`, `trade-route-order`) | 13 |
| `trade.fleetEscort` | `fleet` W3 (`escort-link`, `interception`, `goods-cargo-fate`) | 14 |
| `counterparties.needs`, `.roster`, `.diplomacy`, `.treasury` | `counterparties` W1 — four rows, **one** bump | 15 |
| `counterparties.stance`, `.clans` | `counterparties` W2 (`diplomatic-stance` + `relation-facts`; `clan-seeding`) | 16 |
| `counterparties.clanEconomy`, `.sinks`, `.conquest` | `counterparties` W3 | 17 |
| `trade.exchange`, `trade.diplomacy` | `exchange` (its own wave split; `trade.diplomacy` ⇒ `counterparties.diplomacy`) | 18 |
| `trade.riftTrade` | `rift-trade` W1 (`rift-route`, `crossing-goods`, `crossing-anchor`; ask A4) | 20 |
| `trade.riftCrossing` | `rift-trade` W2 (`crossing-leg`, `crossing-handoff`) | 21 |
| `trade.riftEndpoints` | `rift-trade` W3 (`sleeping-endpoint`, `endpoint-loss`, `rift-facts`) | 22 |
| `trade.laneLossPower` | `logistics-flow` W5 — the round 4 §P escort-strength switch, after the power program's contest row (ask X-2) | 23 |

Withdrawn by round 6 C1: the single `counterparties.clans` gate over both `clan-seeding` (W2) and
`clan-economy` (W3), and the single `counterparties.diplomacy` gate over both `diplomacy-facts` (W1) and
`diplomatic-stance` / `relation-facts` (W2). Each pair spanned two waves, so each later wave now has its
own flag (`counterparties.clanEconomy`, `counterparties.stance`). Likewise the single `trade.sectorYield`
over four sector-yield waves and the single `trade.logistics` over four logistics waves.

A wave that grants nothing — a test-only builder, a pure query, a ledger table, report text or a schema
column — registers **no row and takes no bump**, and says so with that reason. That is not the withdrawn
*"no `RulesetVersion` bump"* claim, which was made for **feature grants** and is void everywhere in the
family.

`trade-surface`'s `TradeCapabilities(Logistics, Routes, Diplomacy)` (`trade-surface/spec-trade-unlock.md`) are
milestone-derived UI unlocks, not stamp capabilities; the two vocabularies must not share names (reported
to that program).

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world model, turn engine (field read), canonical hash, world store, turn log and replay,
    server composition root (tuning loads), AI view.
[~] Session boundary: trade-network-idea-20260919 covers this doc; boundary check not re-run.
[x] Read this session: trade-foundation map §2.4; umbrella X3/X4; ideal §14 D-C and §14b;
    world-continuity-ideal §6.10; world-continuity-map module 14 and its note 6 (the ask the owner
    answered); decisions.md :7 and :90; spec-save-identity's new-table and migration rules.
    tunables-ssot.md and data-architecture.md not read in full (rules taken from PRINCIPLES §5-§6).
[x] decisions.md: phase order (:7) untouched; key-widening row (:90) decides that this migration is
    additive.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: the create literals, the replay refusal's null contract, the equivalence
    guard's field copy, LoadWorldState's field copy, the single map-world creation path, the tuning
    files' version field.
[x] Surrounding sections read (the faction-scope comment that records the golden move; the Assaults
    no-bump comment; decisions.md:90's full row).
[~] Constraint tested, not assumed: "no golden moves" is acceptance criterion 3 and is to be proven by
    the suite at build time; it was not run in this docs-only session. The reasoning is the
    conditional-row precedent, which the code shows held for five earlier fields.
[x] §2 invariants: nothing contradicted. The refinement of the map's hash wording is named in §3.
[x] Corrections propagated: hash projection, additive migration and the null-return replay contract are
    in the map's corrections section.
[x] No population pinned: the census is printed; the two pinned counts are closed vocabularies with
    their reason.
[x] No event-refreshed cache introduced (the hub is configured once at boot).
[x] No ordering-fixed criterion: stamping on create is one step; the census is order-free.
[x] ActorHub: not touched.
[x] No SOLID fork: one stamp, one registry, one replay gate; the manifest is read by one helper.
[x] No new guarded rule; the capability registry is enforced by its own closed-vocabulary test.
```

# Spec: `save-identity`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 4** · depends on:
[`commander-identity`](spec-commander-identity.md) (it supplies `EmpireId`, which this module never
redefines) and `debt-ledger` (the debt row this module closes is recorded there at build).
**Source:** owner ruling **R3**, [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md), binding.
**Status:** spec, written 2026-09-18, strengthened the same day (adversarial pass, R3 + R17), no build authorized.

## Objective

The owner, 2026-09-18: *"did we count empire as player? If true we need to escalate a new save identity
instead of overlapping the role of player."* The ruling: **a Save owns its empires** (Dave's,
Zomboss's, later AI ones), each keyed `(SaveId, EmpireId)`. The player row stops doubling as an
empire, and Zomboss stops being a player row.

### What the code does today: one row, three roles

| Role | Where the `players` row plays it |
|---|---|
| **The save** | The web calls each row a save slot (`gk-web/web/fusion-rpg-web/src/app/SaveSelect.tsx:45`, `data-testid="save-slot-…"` at `:51`). Its `world_seed` is *"the whole save's own root"* (`gk-core/src/FusionRpg.Contracts/Dtos.cs:138-142`). Every run is stamped with the current row (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:2855-2906`), and `decisions.md` already calls type progression *"per-save"* |
| **The human identity** | `players.name` is the summoner name typed at "Choose a summoner" (`SaveSelect.tsx:45`), and `commander-identity` displays it as the first commander |
| **The empire** | Everything the human's side owns is keyed `player_id`: species and type levels (`rpg_actor_progression`, PK `(player_id, kind, type_id)`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:511-524`), specimens, items, souls, and more (inventory below) |

**Zomboss is a second player row, found by name** and shared by every save:
`EnsureZombossPlayer()` returns the first row named `"Zomboss"`, or creates one
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs:25-29`), and every Zomboss deploy mints its
specimen under that row (`:42-47`).

### The defects that follow, each verified in code

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


| # | Defect | Evidence |
|---|---|---|
| D1 | **One Zomboss for every save.** A deploy in save A and a deploy in save B mint onto the same row, so any progression put there leaks between saves | `RpgStore.ZombossDeploy.cs:25-29` |
| D2 | **Zomboss is a selectable summoner.** `GET /api/players` lists every row unfiltered (`gk-core/src/FusionRpg.Server/Program.cs:949-953`) and the save screen renders every item with a Continue button (`SaveSelect.tsx:25`, `:48-75`). After the first Zomboss deploy, "Zomboss" is a save the player can load | as cited |
| D3 | **Two incompatible answers to "whose row is Zomboss's".** His deploy-side data sits on the global row (D1), while his commander allocation (`zomboss:{playerId}`, `gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs:68-72`) and his species override key (`player:{id}:empire:zomboss:species:{id}`, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocation.cs:28-31`) are keyed under the **human** row | `species-progression-map.md` C5 names the same split |
| D4 | **Ownership by elimination.** The injector tells a Zomboss specimen apart only because its owner id is *not* the human's: *"any registered owner that is NOT this player is, by elimination, Zomboss's own"* (`gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs:304-310`). `KillAttribution` documents the same hazard (`gk-core/src/FusionRpg.Core/Battle/KillAttribution.cs:41-45`). A third empire breaks the rule silently | as cited |
| D5 | **Empire-owned rows have no empire in their key.** `rpg_actor_progression` cannot hold a Zomboss species level beside the human's zombie-type history, because its PK is `(player_id, kind, type_id)` (`RpgStore.cs:523`). That is why a non-Dave empire resolves Empty today (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:229-233`) | as cited |

### What success looks like

- A save is a first-class identity (`SaveId`). Each save lists its empires as data.
- Every empire-owned row is owned by an `EmpireRef(SaveId, EmpireId)`, and code asks for an empire,
  never for "the other player".
- No player row represents Zomboss. Save A's Zomboss and save B's Zomboss are different empires.
- An existing save loads with every number it had, byte for byte, for the human's empire.

## Design

### Decision 1: the `players` row IS the save, and its id IS the `SaveId`

The row already behaves as a save in every place that matters (table above). So the save identity is
**not a new table**. It is a *typed name* for an id that exists, plus the removal of the empire role
from that row.

- **No id rewrite.** About 60 tables carry `player_id` (60 `CREATE TABLE` bodies plus three `EnsureColumn` additions, a reading; inventory below). Their values are already
  save ids. Reusing them means the migration touches only the tables whose **key must widen**.
- **Human identity stays on the save row.** The summoner name and the per-save preference table
  (`rpg_user_settings`) are the only human-identity state in the code. There is no cross-save
  profile, no account, and no consumer that needs one (the server has no auth and is localhost-only,
  `software-architecture.md` §1). Splitting a human-profile table out now would be a 1:1 table with no
  second reader. The ruling does not ask for it, and it is not built.
- **The physical table keeps its name.** Schema evolution here is additive (`data-architecture.md`
  §2, "Schema evolution"). A rename would touch every query for no behaviour change. New and rebuilt
  tables name the column `save_id`. Untouched pre-R3 tables keep `player_id`, and the rule is written
  once: **`player_id` in a table predating this module is the `SaveId`.**

**Rejected: a new `rpg_saves` table mapped 1:1 from `players`.** It adds a join to every save read and
a second place where "which saves exist" is decided (two SSOTs for one fact, the S in SOLID). It also
carries no information the `players` row does not.

### Decision 2: a save owns its empires as data

```sql
-- (new) gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SaveEmpires.cs
CREATE TABLE IF NOT EXISTS rpg_save_empires (
  save_id      INTEGER NOT NULL,   -- players.id
  empire_id    TEXT    NOT NULL,   -- EmpireId.Value (commander-identity); same id space as WorldFaction.FactionId
  controller   TEXT    NOT NULL,   -- closed vocabulary: 'human' | 'ai'
  created_utc  TEXT    NOT NULL,
  PRIMARY KEY (save_id, empire_id)
);
```

- **`controller` is a closed vocabulary** (`EmpireController { Human, Ai }`). Its two members are the
  contract, pinned with that reason.
- **Exactly one `human` empire per save** is a contract, asserted by a test. It is not a count of
  empires, which is a population and never pinned.
- **Which empires a new save gets is authored data**, not code:
  `gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json` (new, hand-authored, never generated) with two
  rows today, `{ "empireId": "dave", "controller": "human" }` and
  `{ "empireId": "zomboss", "controller": "ai" }`. A later AI empire is a new row. No `switch`, no
  literal list in `src/`.
- **Code never assumes the human empire is `"dave"`.** It asks `HumanEmpireOf(save)`. The well-known
  values `EmpireId.Dave` / `EmpireId.Zomboss` from `commander-identity` stay legal where the code
  means *that faction*, for example `EmpireForSide` (`SpeciesAllocation.cs:38-39`).
- **Relation to the world map.** `rpg_world_factions(world_id, faction_id, …)`
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:37-44`) holds a faction's **map state** in one world.
  `rpg_save_empires` holds **which empires exist** in the save. They share an id space, and a closure
  contract binds them: every `faction_id` that names an empire must be an empire of the world's save
  (`rpg_worlds.player_id`, `RpgStore.World.cs:20-35`). One fact per table, no second SSOT.

### Types (new, Core)

```csharp
namespace FusionRpg.Core.Saves;

/// <summary>A save: one playthrough. Its value is `players.id`. Never an empire, never a person.</summary>
public readonly record struct SaveId(long Value);

/// <summary>The owner of every empire-scoped row: an empire *of a save*. Zomboss in save 1 and
/// Zomboss in save 2 are two different owners.</summary>
public readonly record struct EmpireRef(SaveId Save, EmpireId Empire);

/// <summary>Who decides for an empire. Closed on purpose: a third kind of decider is a design change.</summary>
public enum EmpireController { Human, Ai }
```

`SaveId` is `long` because `players.id` is `INTEGER` (SQLite 64-bit, `RpgStore.cs:198-203`). It is an
identity, not a magnitude, so no range audit applies beyond keeping the full `long`.

### The classification — every `player_id`-keyed table, store and surface

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


Measured on `features/mega-merge` at `7ea3691a`, 2026-09-18, by scanning every `CREATE TABLE` under
`gk-core/src/FusionRpg.Data`. The counts are **readings**. Re-measure at build, and never pin them in a test.

**Four classes.** *Save-scoped*: a fact about the playthrough, shared by every empire in it.
*Empire-scoped*: an asset, a progression or a currency that one faction owns, and that a second empire
would own its own copy of. *Human identity*: what belongs to the person at the keyboard. *Via parent*:
keyed by an instance, world or run id and owned through it.

Empire-scoped rows split by **when their key widens**:

- **Tier A (re-keyed by this module):** a non-human empire writes this data today, or a ruled consumer
  (R1, R3) needs it to. The key becomes `(save_id, empire_id, …)`.
- **Tier B (declared, key unchanged):** only the human empire owns such rows today. The **store API
  takes an `EmpireRef` from the first build.** For any empire other than `HumanEmpireOf(save)` it
  throws `EmpireScopeNotWidened(table)`, and never silently writes the human's row. The feature that
  first needs a second empire there widens the key through this module's migration framework. Callers
  do not change, because they already pass the empire (the O in SOLID).

| Class | Tables / stores (`file:line` of the `CREATE TABLE`) | Change |
|---|---|---|
| **Save** | `players` (`RpgStore.cs:198`) — the save itself | `archived_utc` column (new, see migration) |
| **Save** | `settings['current_player_id']` (`RpgStore.cs:204`; read `:3999-4008`) — the current save | none; value is a `SaveId` |
| **Save** | `events`, `runs` (`RpgStore.cs:209`, `:217`; `player_id` added `:363`, `:366`) — the match log. A run keeps the save it started with (`decisions.md` "Mid-match switch") | `SaveOfRunUnlocked`, `SaveOfMatchUnlocked` (new) read `runs.player_id` |
| **Save** | `entities`, `mowers`, `spawn_stats` (`RpgStore.cs:224`, `:264`, `:277`) — capture | none |
| **Save** | `archive_catalog` (`RpgStore.cs:387`) | none (see "Archive" below) |
| **Save** | `pvz_activity_revisions`, `pvz_activity_facts`, `pvz_activity_rollups` (`RpgStore.cs:450`, `:455`, `:471`) — play facts. Progression is *projected* from them per empire | none |
| **Save** | `rpg_onboarding_checkpoint`, `rpg_onboarding_story`, `rpg_first_open` (`RpgStore.cs:479`, `:493`, `:505`) — the save's prologue | none |
| **Save** | `rpg_web_match_log` (`RpgStore.cs:726`) | none |
| **Save** | `rpg_worlds` (`RpgStore.World.cs:20`), and every `rpg_world_*` table via `world_id` | closure contract with `rpg_save_empires` |
| **Save** | `rpg_creature_codex` (`RpgStore.cs:624`) — the human's almanac of this save (seen / discovered) | an AI empire's mint **stops writing it** (see "Zomboss") |
| **Save** | `rpg_achievement_unlock` (`RpgStore.Achievements.cs:30`), `rpg_delve_event_seen` (`RpgStore.Delve.cs:132`) | none |
| **Empire A** | `rpg_actor_progression` (`RpgStore.cs:511`), `rpg_xp_ledger` (`RpgStore.cs:525`) — type, species and commander levels, and their ledger. R1 puts zombie species levels on Zomboss's empire, and `zomboss-commander-clock` puts his commander level there | **rebuilt**: PK `(save_id, empire_id, kind, type_id)`; ledger `UNIQUE (save_id, empire_id, kind, type_id, reason, dedupe_key)` |
| **Empire A** | `rpg_unique_actors` (`RpgStore.cs:548`) — specimens; Zomboss mints them today | `empire_id` column (added, backfilled, never null after migration) |
| **Empire A** | `rpg_aptitude_allocation` (`RpgStore.Aptitudes.cs:39`) — its `scope_key` strings **already** carry save and empire: `player:{save}`, `zomboss:{save}` (`CommanderId.cs:68-72`), `player:{save}[:empire:{token}]:species:{id}` (`SpeciesAllocation.cs:28-31`) | **no data change.** The strings stay (commander-identity's promise). The one encoder takes an `EmpireRef` |
| **Empire** (via parent) | `rpg_unique_lawn_sessions`, `rpg_unique_actor_recovery` (`RpgStore.cs:578`, `:596`), and everything keyed `instance_id` (`rpg_unique_lawn_xp_receipts`, `rpg_unique_actor_pools`, `rpg_unique_equipment`, `rpg_unique_stat_mods`, `rpg_creature_profiles`, `rpg_expedition_members`) | none; the empire is the instance's. The two with a `player_id` column move with their specimen (migration step 5) |
| **Empire** (key implies it) | `rpg_zomboss_state`, `rpg_zomboss_pattern_log` (`RpgStore.ZombossAdaptive.cs:21`, `:29`) — already one row per **save**, and the table itself names the empire | none. Already the R3 shape; the column is documented as `SaveId` |
| **Empire B** | `rpg_player_commander` (`RpgStore.PlayerCommander.cs:17`) — the human empire's default commander. An AI empire's default comes from `ICommanderDirectory.DefaultFor(empire)` and is not stored | store API empire-typed |
| **Empire B** | items: `rpg_item`, `rpg_item_stock`, `rpg_item_rule`, `rpg_item_event`, `rpg_item_loadout`, `rpg_player_item_assignment` (`RpgStore.Items.cs:86`, `:102`, `:110`, `:120`, `:131`, `:165`) | store API empire-typed |
| **Empire B** | charms: `charm_pouch`, `charm_run_hold`, `charm_attunement` (`RpgStore.Charms.cs:68`, `:81`, `:119`) | same |
| **Empire B** | loot: `item_drop_log`, `item_loot_pity`, `item_first_clear` (`RpgStore.Loot.cs:105`, `:137`, `:144`) | same |
| **Empire B** | materials: `rpg_creature_materials` (`RpgStore.cs:764`), `rpg_material_spend_log` (`RpgStore.Materials.cs:60`) | same |
| **Empire B** | souls: `rpg_soul_ledger`, `rpg_soul_balances` (`RpgStore.cs:684`, `:699`) | same |
| **Empire B** | summons and fusion: `rpg_summon_log`, `rpg_summon_pity`, `rpg_fusion_log`, `rpg_fusion_discovery` (`RpgStore.cs:708`, `:720`, `:640`, `:651`); `player_species` (`RpgStore.PlayerSpecies.cs:45`, being retired by `species-mod-ledger`) | same |
| **Empire B** | patron and contracts: `rpg_patron`, `rpg_creature_contracts`, `rpg_contract_state` (`RpgStore.cs:657`, `:663`, `:677`) | same |
| **Empire B** | expeditions and delves: `rpg_expeditions` (`RpgStore.cs:743`), `rpg_delves` (`RpgStore.Delve.cs:97`), `rpg_domain_progress` (`RpgStore.Domains.cs:75`), `rpg_cache_retrieval_mission` (`RpgStore.CacheRetrieval.cs:124`), `rpg_corpse_cache.owner_player_id` (`RpgStore.CacheDecay.cs:45`) | same |
| **Empire B** | build state: `rpg_aptitude_preset`, `rpg_aptitude_preset_active` (`RpgStore.AptitudePresets.cs:58`, `:80`), `rpg_species_respec` (`RpgStore.SpeciesRespec.cs:34`), `rpg_title_lifecycle` (`RpgStore.Titles.cs:18`) | same. `ai-empire-species` already rules that an AI empire gets no respec surface |
| **Empire B** | PvZ player attributes: `pvz_stat_revisions`, `pvz_stat_modifiers`, `pvz_stat_snapshots`, `pvz_stat_contributions` (`RpgStore.cs:410`, `:415`, `:430`, `:436`) — modifiers to the human side's game stats | same |
| **Empire B** (owner key) | owner-scoped rows whose owner string is `player:{id}` (`OwnerKind.Player`, `gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs:20-30`; for example `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActorTitles.cs:39`): `effect_binding`, `rpg_actor_loadout`, `rpg_gate_counter`, `rpg_actor_unlock_state`, and the passive-tree `scope_key` rows | none now; the `player:` owner means *the save's human empire*. Widening it is a new `OwnerKind` member, a reviewed change to a closed vocabulary |
| **Human identity** | `players.name` — the summoner name, shown as the human empire's first commander (`commander-identity`) | none |
| **Human identity** | `rpg_user_settings` (`RpgStore.UserSettings.cs:24`) — preferences, stored per save | none |

**Stores and surfaces outside the database**, same classification:

| Surface | Today | Class | Change |
|---|---|---|---|
| `CheatState.CurrentPlayerId` (`gk-fusion/src/FusionRpg.Injector/CheatState.cs:256`, `:272`) | the id the server hydrated with the power snapshot (`RpgClient.RefreshPowerIndexAsync`, `gk-fusion/src/FusionRpg.Injector/RpgClient.cs:851-860`, which reads `GET /api/players/current`) | save | documented as the current `SaveId`. The injector still never originates it (`software-architecture.md` §2). **Ownership no longer reads it** (see "Injector ownership" below) |
| Specimen owner map, `RegisterSpecimenOwner(ptr, long)` / `TryGetSpecimenOwner` (`CheatState.cs:316`, `:322`), fed from the `pvz.spawn.extra` payload's `playerId` (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:178`; registered at `gk-fusion/src/FusionRpg.Injector/CheatActions.cs:445`, `:514`) | owner player id per board pointer | empire | value becomes the owner's `(EmpireId, EmpireController)`, carried **in the spawn payload** (new fields `empireId`, `controller`). The injector plays one save at a time, so the save is implicit (D4) |
| `SpecimenOwnershipOracle(long myPlayerId, …)` (`gk-core/src/FusionRpg.Core/Battle/SpecimenOwnershipOracle.cs:35`) | ally/enemy by comparing player ids | empire | `Ally` iff the registered owner's controller is `Human` (D4); needs no "my id" |
| `KillCredit(CommanderId Empire, long? PlayerId)` (`KillAttribution.cs:19`) | empire plus the owner row | empire | `PlayerId` becomes `EmpireRef? SpecimenOwner` |
| `ResolveLawnKillCreditPlayerUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:54-70`) | returns the killer specimen's `player_id` | empire | returns its `EmpireRef`; souls stay Tier B |
| REST routes with `{playerId}` in the path | 50 routes in 21 server files (a reading) | save | the path value is the `SaveId`; see Contracts |
| Server reads of `GetCurrentPlayerId()` | 24 server files (a reading) | save | none |

### Zomboss stops being a player row

- **Deleted:** `ZombossPlayerName` and `EnsureZombossPlayer` (`RpgStore.ZombossDeploy.cs:13`, `:25-29`).
  Nothing in `src/` may look up a `players` row by name again (guard I3 below).
- **`MintForZomboss(speciesId, seed)`** becomes **`MintForEmpire(EmpireRef owner, speciesId, seed)`**. The
  mint mapping (`:47-58`) is unchanged. `origin: "zomboss"` stays, because it is provenance.
- **Which save a Zomboss deploy belongs to comes from the match, never from "current".** The
  endpoint already receives `MatchKey` (`gk-core/src/FusionRpg.Server/ZombossDeployEndpoints.cs:15`), and the
  injector already sends it (`gk-fusion/src/FusionRpg.Injector/RpgClient.cs:264-277`). `runs.match_key` is
  unique (`RpgStore.cs:406`). `SaveOfMatchUnlocked(matchKey)` resolves the save. A deploy whose match
  resolves to no run is refused with `409 match_unresolved`, and never credited to a guessed save.
  `MatchKey` becomes required on that request. The refusal happens **before** the mint, so a refused
  deploy leaves no orphan specimen (today the endpoint mints first, `ZombossDeployEndpoints.cs:40`, and
  a failed `DeployAsync` leaves the mint behind). The injector fires the deploy mid-match, after
  `board.start` has created the run (`RpgStore.cs:2855-2906`); a deploy that races ahead of that ingest
  is refused and logged, never retried onto a guess.
- **An AI empire's mint does not touch the codex.** Today `MintCreatureUnlocked` upserts
  `rpg_creature_codex` for the minting row (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Creatures.cs:85`).
  The codex is the human's almanac of the save (classified above). Zomboss "discovering" a species is
  meaningless, and writing it to the save would put species the player has never met into the player's
  almanac.
- **Ownership is read, not inferred** (D4). The injector's owner map stores each specimen's
  `(EmpireId, EmpireController)`, carried in its spawn payload. The oracle asks "is the owner's
  controller human?". The "by elimination" rule in `MatchHost` is deleted (see "Injector ownership").
- **Specimen reads are classified by purpose, not blanket-filtered.** `ListUniqueActors(playerId)`
  reads `WHERE player_id = $pid` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:128-142`). After
  the migration a save's Zomboss specimens share its `save_id`, so each read declares which question it
  asks:

  | Purpose | Reads | Scope after R3 |
  |---|---|---|
  | **An empire's roster** (UI, deploy roster, fusion inputs, patron, expeditions, respec) | `ListUniqueActors`, `UniqueActorEndpoints`, the injector deploy-roster cache | `EmpireRef`; routes default to `HumanEmpireOf(save)`. The human's roster never lists an AI empire's specimen |
  | **The match's runtime** (every side on the board) | atom push owners (`AtomPushService.OwnersForPlayer`, `gk-core/src/FusionRpg.Server/AtomPushService.cs:37-47`, via `UniqueActorService.ObserveEvents`, `gk-core/src/FusionRpg.Server/UniqueActorService.cs:195-207`), the stale-`ActiveBound` boot sweep, kill-credit lookup | **every empire of the save**. Today Zomboss's `ActiveBound` specimens get their trait atoms pushed because the push runs per owning row; filtering this read to the human empire would silently strip them. So it becomes `OwnersForSave(save)`: the human empire's `player:{save}` owner plus the `ActiveBound` specimens of **all** `EmpiresOf(save)` |

  The roster regression (an AI specimen in the human's list) and the runtime regression (an AI
  specimen losing its atoms) each have a named test.

### AI-empire specimens never touch a human-only table

A Zomboss mint and deploy run through code written for the human. Four of those paths touch
Tier B or human-surface state (three write it today, one would after the re-key), and each is decided
here, because a Tier B **throw** on a mint or an
ingest path would break Zomboss's deploy outright:

| Path today | What it writes for Zomboss's specimen | After R3 |
|---|---|---|
| `MintCreatureUnlocked` → `AutoBindNewSpecimenUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Creatures.cs:88`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:85-104`) | a bound `rpg_creature_contracts` row and a `rpg_contract_state` row on the minting row | **skipped for a non-human empire.** Contracts are the summoner's binding slots, loyalty and tribute (Tier B). An AI empire's specimen has no contract |
| `TryBeginUniqueDeploy`'s contract gate (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs`, the `contract.unbound` / `contract.insubordinate` refusals after the phase check) | reads the contract under `row.PlayerId` | applies to **human-empire** specimens only; an AI empire's deploy is gated by its own decision policy (`ZombossDeployPolicy`) |
| `DeployAsync` → `RecordExtraSpawnIntent(begin.Actor.PlayerId, …)` (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:157`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1829-1860`) | an `ExtraSpawnFired` fact and rollup on the minting row | **not recorded for a non-human empire.** Today it lands on the Zomboss row, which no reader sees; recording it on the save would change the human's activity rollup |
| `ResolveLawnKillCreditPlayerUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:54-70`) | nothing today: it filters `side = 'plant'`, and Zomboss mints zombie species | returns the killer's `EmpireRef`. Souls are Tier B: a non-human killer earns **no** kill souls and is logged; the ingest path never throws |

**D6, a live defect this removes (found by reading code, not live-proven).** Every Zomboss mint in
every save auto-binds on the one global row, whose capacity is `baseSlots` 12
(`gk-core/data/tuning/contracts.v1.json:26`; `ContractPolicy.Capacity`,
`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:171`). Nothing releases those contracts: release
happens only on an explicit release or on fusion retire (`RpgStore.Contracts.cs:362`, `:514-519`). So
from the 13th Zomboss mint onward the specimen arrives unbound and `TryBeginUniqueDeploy` refuses it
`contract.unbound`, which the endpoint returns as 409 and the injector only logs
(`gk-fusion/src/FusionRpg.Injector/RpgClient.cs:276-279`). Taking AI specimens out of the contract system fixes it.

### One ownership predicate for specimen-targeted writes

Every store or endpoint that acts on a specimen by `instanceId` checks ownership by comparing the
specimen's `player_id` with the caller's (a reading, 2026-09-18): `RpgStore.Contracts.cs:539`,
`RpgStore.cs:3913` (species XP from a specimen source), `RpgStore.Expeditions.cs:59`,
`RpgStore.Fusion.cs:471`, `:496`, `RpgStore.Patron.cs:33`, `RpgStore.UniqueActors.cs:565`, and
`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:344`. Today a Zomboss specimen fails every one of them,
because it sits on another row. **After the migration it would pass all of them**, since it shares the
save's id: the human could fuse away, bind, patron, equip or send on an expedition a specimen of
Zomboss's, and (`:3913`) Zomboss's deployed specimens would start crediting the human's zombie species
XP.

So all of them call **one** predicate, `OwnsSpecimenUnlocked(db, EmpireRef owner, instanceId)` (new),
which compares `(player_id, empire_id)`. A refusal keeps each site's existing reason code. Guard rule
I4 (below) keeps new sites from comparing `PlayerId` directly.

### The migration — irreversible, so backed up first

`SaveIdentity.Migrate(db, log)` (new) in `gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs`. It
follows the shipped precedent `ShardRungs.Migrate` (`gk-core/src/FusionRpg.Data/Sqlite/Migrations/ShardRungs.cs:6-25`):
one shot, idempotent, run from `Init` on every boot, and a no-op once done.

**Step 0: gate.** If `settings['schema.save-identity']` exists, return. A **fresh** database (no
`players` row before `SeedPlayerIfEmpty`) is created in the new shape by `Init`'s DDL, seeded through
`SeedSaveEmpiresUnlocked`, and gets the marker at seed time with an empty report: the rebuild never runs
on a table that is already widened. As a second check, step 4 reads `PRAGMA table_info` and skips a
table that already has `empire_id`.

**Ordering inside `Init`.** The migration runs after every `CREATE TABLE IF NOT EXISTS` and
`EnsureColumn` of the classified tables and **before** `CloseAbandonedRunsUnlocked` and
`SweepStaleActiveBoundUnlocked` (`RpgStore.cs:174-179`). The sweep returns stale `ActiveBound`
specimens to `Roster` and clears their `match_key` (`SweepStaleActiveBoundUnlocked` → `RecoverToRosterUnlocked`, `RpgStore.UniqueActors.cs:1211-1233`, `:1038-1047`), which is
provenance rule (a)'s input. `Init`'s DDL creates the old shape for an existing database (a no-op, the
table exists) and the new shape only for a fresh one, so no boot ever holds both shapes of one table.

**Step 1: backup (file plan only), before any write.** `VACUUM INTO
'{dataDir}/rpg-hot.sqlite.pre-save-identity.{utcStamp}.bak'` takes a consistent copy even under WAL.
The name is **new on every attempt**: `VACUUM INTO` refuses an existing target, and an older `.bak` may
predate play on a rolled-back build, so it is never reused or overwritten. The precedent is
`LegacyMonoMigrator`'s `.pre-dal.bak` (`gk-core/src/FusionRpg.Data/Sqlite/LegacyMonoMigrator.cs:14`, `:43-44`):
made first and never deleted automatically. **If the backup fails, the migration does not run and the
server refuses to start**, with the reason on the console. A memory store has no file, so it skips this
step (`data-architecture.md` §1, the memory plan). Only `rpg-hot.sqlite` is written: every classified
table lives there, and `rpg-media.sqlite` and `archive/*` are untouched.

**Steps 2–7 run in one transaction.** Any failure rolls the whole thing back, leaves no marker, and
the server refuses to start. The `.bak` is untouched. The server accepts no request and no injector
batch until `Init` returns, so no live ingest interleaves; an injector that buffered events across the
restart replays them afterwards against the unchanged `runs` rows.

2. **Find the legacy Zomboss row** with exactly the rule the code used: the lowest-id row named
   `"Zomboss"` (`ListPlayers` orders by id, `RpgStore.cs:1159-1169`; `EnsureZombossPlayer` takes the
   first match, `RpgStore.ZombossDeploy.cs:27`). None found: skip to step 3.

   **Whether it is also a save is decided by evidence, and a tie goes to "save".** The name collision
   is real: `POST /api/players` accepts any name (`gk-core/src/FusionRpg.Server/Program.cs:954-959`). If a
   player named a save "Zomboss" before Zomboss's first deploy, `EnsureZombossPlayer` found **that**
   save and minted every later Zomboss specimen into it, where they sat in the player's roster, on the
   player's contract slots, usable by the player. So the row is **Zomboss-only** only if every row that
   references it is one the Zomboss path writes:

   | Zomboss path writes (allowed) | Source |
   |---|---|
   | `players`, `pvz_stat_revisions`, `pvz_activity_revisions`, `rpg_onboarding_story` | `CreatePlayer`, `RpgStore.cs:1171-1189` |
   | `rpg_unique_actors` + `rpg_creature_profiles` with `origin = 'zomboss'`, and their instance-keyed children | `MintForZomboss`, `RpgStore.ZombossDeploy.cs:42-58` |
   | `rpg_creature_codex`, `rpg_creature_contracts`, `rpg_contract_state` | `MintCreatureUnlocked`, `RpgStore.Creatures.cs:85-88` |
   | `pvz_activity_facts` / `pvz_activity_rollups` from `ExtraSpawnFired` | `RecordExtraSpawnIntent`, `RpgStore.cs:1829-1860` |
   | `rpg_unique_lawn_sessions`, `rpg_unique_actor_recovery`, lawn XP receipts of those specimens | their deploy and lawn path |

   Any other reference is human evidence and makes the row a save: it is `current_player_id`; it owns
   a `runs` or `rpg_worlds` row; it owns a specimen whose `origin` is not `zomboss`; it owns a row in
   any other classified table (items, souls ledger, summons, fusion, patron, expeditions, delves,
   presets, respec, allocation scope keys `player:{id}…`); or one of its specimens has an allocation,
   equipment or stat-mod row (a person edited it). A false "save" costs one extra visible save slot,
   named in the report. A false "Zomboss-only" would hide a player's save. So the test errs to "save".
3. **Seed every save's empires** from the new-save registry: every `players` row except a
   Zomboss-only legacy row. A pre-R3 save has exactly the human empire and Zomboss's. That is a
   historical fact about pre-R3 saves, stated in the migration and nowhere else.
4. **Rebuild the Tier A tables.** `rpg_actor_progression` and `rpg_xp_ledger` are renamed to
   `<name>__pre_save_identity` and kept. Their indexes follow the rename and keep their names
   (`ix_rpg_xp_ledger_player`, `RpgStore.cs:547`), so the new tables' indexes take new names;
   reusing an old name would fail inside the transaction. New tables are created with the widened
   key, and every row is copied with `empire_id = HumanEmpireOf(save)`. **History is never
   re-attributed.** A zombie-type or zombie-species row credited to the human before R1 stays the
   human's. That matches `ai-empire-species` (*"the human's existing zombie rows are left as history,
   never rewritten"*). Rows owned by a Zomboss-only legacy row are not copied. They stay in the
   retained legacy table and are counted in the report.
5. **`rpg_unique_actors.empire_id`** is added (`EnsureColumn`) and backfilled:
   - **A save's own specimens get `HumanEmpireOf(save)`, whatever their `origin`.** That includes a
     "Zomboss"-named save's `origin = 'zomboss'` specimens (step 2): the player could see, bind, fuse
     and equip them, so they are the player's play state, and moving them would re-attribute history.
     The report counts them.
   - A **Zomboss-only** legacy row's specimens get `empire_id = zomboss`, and `player_id` is set to a
     save by these rules, **in order**:
     - **(a) Provenance.** A `match_key` on the specimen, its lawn session, or any of its lawn XP
       receipts (`RpgStore.cs:548-590`; a receipt keeps `match_key NOT NULL` for good, while the
       specimen's own column is cleared on return to roster) joined to `runs.match_key → runs.player_id`.
     - **(b) The only save.** If exactly one save exists, that save. No other save can have hosted
       the match, because every run is stamped with a save.
     - **(c) Otherwise, unattributed.** The specimen stays on the legacy row with phase `Retired`, and
       is listed in the report.

     Re-homing moves the specimen's `rpg_unique_lawn_sessions` and `rpg_unique_actor_recovery` rows
     with it (their own `player_id` columns) and deletes nothing. Its legacy contract row is released
     (`bound = 0`), because an AI specimen holds no contract after R3.

     **Rule (c) loses no play state, checked against code.** (1) A Zomboss specimen is never used
     twice: the deploy endpoint mints fresh on every call (`ZombossDeployEndpoints.cs:40`), and no code
     reads `origin = 'zomboss'` or selects an existing Zomboss specimen (grep, 2026-09-18: the origin
     string appears only at its write, `RpgStore.ZombossDeploy.cs:41`, re-anchored 2026-09-20). (2) Nothing of the player's was
     computed from one: Zomboss specimens are zombie-side, and kill souls go only to plant-side
     specimens (`RpgStore.Souls.cs:62-64`). (3) The only surface that ever showed them is loading the
     Zomboss row as a save (D2), and step 2 classifies any row with a trace of that as a save, never as
     Zomboss-only. What (c) retires is a spent one-shot deploy token with no reader.
   - Specimens left in `Deploying` or `ActiveBound` are handled by the existing boot sweep (stale
     `ActiveBound` becomes `Roster`, `RpgStore.cs:178-179`), which runs after this migration.
6. **Legacy row fate.** If the legacy Zomboss row is a save (step 2), it stays a save with both
   empires. Otherwise `players.archived_utc` (new, via `EnsureColumn`) is set. `ListPlayers`,
   `SetCurrentPlayer` and the fallback in `GetCurrentPlayerIdUnlocked` (`RpgStore.cs:3999-4008`, which
   picks the lowest id when the setting is missing) exclude archived rows, which fixes D2. The row is
   kept, because it holds the unattributed history. Its codex rows stay on it: nothing is deleted.
7. **Write the marker** `settings['schema.save-identity']` with a JSON report: saves migrated, whether
   the legacy row was a save and which evidence decided it, specimens attributed by (a) and (b),
   specimens unattributed (ids), `origin = 'zomboss'` specimens kept on a save, legacy progression
   rows left behind, and the backup path. Mirror the report to the console. The marker is the
   transaction's last statement, so it never exists without the data it describes.

**Rollback.** Until the owner has played on the migrated save, roll back by stopping the server,
restoring the step 1 `.bak` over `rpg-hot.sqlite` (and deleting its `-wal` and
`-shm`), and running the previous build. That loses anything played after the migration. That is why
the backup is taken and never auto-deleted, and why the report names what moved. The
`__pre_save_identity` tables are a second, in-database recovery source. Purging them is a user-driven
storage action later (`data-architecture.md` §5: *"User-driven purge only — no auto GC"*). This module
never drops them. Once real play has happened on the new schema, the policy is to fix forward.

**Archive.** `archive/xp-*` segments were sliced from `rpg_xp_ledger` by player (`data-architecture.md`
§5). Every pre-migration ledger row is the save's human empire by step 4's rule, so a reader treats a
segment without `empire_id` as that. No reader exists today: the cold-path fan-in is a deferred stub
(`gk-core/src/FusionRpg.Data/Abstractions/DeferredColdPath.cs:7`). The rule is recorded so the first reader
follows it.

### Contracts: REST, SignalR, injector

**REST.** No route is renamed. That keeps the web and the injector working unchanged, and the renaming
would buy no behaviour.

| Surface | Change |
|---|---|
| Every `{playerId}` path value (50 routes, a reading) | means the `SaveId`. Documented in `docs/protocol/rest.md` at build |
| `GET /api/players` (`gk-core/src/FusionRpg.Server/Program.cs:949-953`) | excludes archived rows (D2). `currentPlayerId` means the current save |
| `POST /api/players` (`gk-core/src/FusionRpg.Server/Program.cs:954-959`) | creates the save **and** its empires in one transaction |
| `GET /api/players/{playerId}/empires` (new) | `[{ empireId, controller }]` from `rpg_save_empires` |
| `/api/aptitudes/{playerId}` (route `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:23`, projection `:155-178`) | stays **one fetch** (species-layer-delivery's requirement). The commander block is the human empire's pool; every empire-keyed section covers **all** of `EmpiresOf(save)`. No `?empire=` here, so the injector keeps a single refresh path |
| Other empire-scoped reads a consumer needs for a non-human empire: `/api/commanders/{playerId}` (`gk-core/src/FusionRpg.Server/CommanderEndpoints.cs:45`, `ProjectList` `:52`), the unique-actor list, the progression reads | optional `?empire=<empireId>` (new). When absent: `HumanEmpireOf(save)`, so every current caller is unchanged. Not added to a route before a consumer needs it |
| A Tier B route asked for a non-human empire | `409 empire_scope_not_widened` |
| `UniqueActorDto` (`gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs:15-30`) | gains `empireId` (new). `playerId` stays and means the save |
| `/api/zomboss/deploy` (`ZombossDeployEndpoints.cs:32-53`) | `matchKey` required. The save comes from the match; the owner is `(save, zomboss)` |
| `pvz.spawn.extra` command payload (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:166-182`) | gains `empireId` and `controller` (new) beside `playerId` (= the save). The injector's ownership source (below) |

**SignalR.** Payloads keep `{ playerId }`, which means the save. Empire-scoped invalidations that can
now fire for a non-human empire add `empireId` (new): `CreaturesUpdated`
(`gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:105`, `:110`, `:146-147`; Expedition and Fusion endpoints),
`RpgProgressionUpdated` (`gk-core/src/FusionRpg.Server/Program.cs:1781`) and `CommandersUpdated` (`CommanderEndpoints.cs:106-108`).
Tier B events (`SoulsUpdated`, `ContractsUpdated`, `PatronUpdated`, `DelveUpdated`,
`PassiveTreeUpdated`, `PvzStatsUpdated`) are unchanged until their table widens. Save-scoped
`PvzActivityUpdated` is unchanged. A listener that ignores `empireId` keeps today's behaviour, because
its data is the human empire's.

**Per-save routing (`notification-ssot` `player-routing`).** That program adds a SignalR group per
player, `player:{id}`, joined through `RpgHub.JoinPlayer(playerId)` and switched on
`PUT /api/players/current` (`docs/architecture/notification-ssot/spec-player-routing.md` T3). Under
R17 the id **is** the `SaveId`, so that group is the save's group, and it stays one group per save:
an empire is payload data (`empireId`), never a group of its own, because every reader of a save's
notices is the one human at the keyboard. Two consequences, both owned there and consistent with
this spec: `JoinPlayer` refuses an archived row exactly as it refuses a missing one (it asks the same
`IsLiveSave` predicate `ListPlayers` uses), and its boot catch-up walks `ListPlayers()`, which already
excludes archived rows. The group string `player:{id}` and the allocation owner key `player:{id}` share
a spelling and nothing else: one names a SignalR group, the other a store key, and neither is parsed
as the other.

**Injector ownership: a per-spawn fact, not a cache.** The first draft of this spec gave the injector
an edge-refreshed cache of the current save's empires, with the save switch as its key-set edge. That
trigger has no signal today: `PUT /api/players/current` (`gk-core/src/FusionRpg.Server/Program.cs:965-966`)
pushes nothing to the injector, and `CheatState.CurrentPlayerId` changes only when
`RefreshPowerIndexAsync` runs (session start, reconnect, or a manual `power.index.reload`,
`gk-fusion/src/FusionRpg.Injector/RpgClient.cs:81`, `:163`; `gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:101-105`).
It would also be keyed wrongly: a match keeps the save it started with (`decisions.md`
"Mid-match switch"), so "the current save" is not the question the oracle asks.

So ownership travels with the entity. `DeployAsync` already sends the owner in the `pvz.spawn.extra`
payload (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:166-182`); it adds `empireId` and `controller`
(new), read from the specimen's own row in the same call that decides the deploy. The injector stores
`ptr → (EmpireId, EmpireController)` at register (`CheatActions.cs:445`, `:514`) and never refreshes it,
because a specimen's owner cannot change during its life on the board. The oracle answers `Ally` when
the owner's controller is `Human`, `Enemy` for any other registered owner, and `null` when nothing is
registered (then the mechanical side decides, as today). `MatchHost`'s Zomboss deploy decision asks
"is this owner `EmpireId.Zomboss`?" directly, and the elimination rule
(`gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs:304-310`) is deleted.

DESIGN-GATE §2.16 therefore adds **no** new edge-refreshed cache here. The one ordering case is a
payload without the new fields (a server and injector from different builds): the entry registers as
unknown, and the mechanical side decides. That is safe: a Zomboss specimen is zombie-side, and a player's
specimen deploys plant-side (`HypnoAlly` deploy is refused today), so neither is ever misread as `Ally`. Server and
injector still ship in one deploy (`deploy-play.py`, the release zip), because an **old** injector
against a migrated server would compare two equal save ids and call Zomboss's specimen an ally.

### Onboarding: an empty save

The owner's onboarding idea is that an empty boot creates Crazy Dave as the first player and plays the
prologue. Today `SeedPlayerIfEmpty` inserts row 1 (`RpgStore.cs:4010-4024`). **Two modules edit it, and
each owns one line:** `commander-identity` changes the seed name to "Crazy Dave". This module makes the
seed also create the save's empires, through **one** function, `SeedSaveEmpiresUnlocked(db, save)`
(new), which `CreatePlayer` (`RpgStore.cs:1171-1189`) and the migration call too. There is no second
copy of "what a new save contains". The result on a fresh boot: save 1, summoner "Crazy Dave", a human
empire whose first commander displays "Crazy Dave", and an AI Zomboss empire with no player row.

### Seams this module provides to consumers (new)

```csharp
// FusionRpg.Data — the only SQL, as always
SaveId? SaveOfRunUnlocked(SqliteConnection db, long runId);        // runs.player_id
SaveId? SaveOfMatchUnlocked(SqliteConnection db, string matchKey); // runs.match_key → player_id
EmpireId HumanEmpireOf(SaveId save);
IReadOnlyList<SaveEmpire> EmpiresOf(SaveId save);
RpgProgressionDirty? TryApplyXpUnlocked(SqliteConnection db, EmpireRef owner, string kind, int typeId, …); // re-typed
RpgActorDto? ReadEmpireActorUnlocked(SqliteConnection db, EmpireRef owner, string kind, int typeId);
long CommanderLevelOf(SaveId save, EmpireId empire);               // kind 'player', type 0, on the re-keyed table
bool OwnsSpecimenUnlocked(SqliteConnection db, EmpireRef owner, string instanceId); // the one ownership predicate
IReadOnlyList<OwnerScope> OwnersForSave(SaveId save);              // atom-push owners: every empire's ActiveBound
bool IsLiveSave(long id);                                          // a players row that is not archived
string CommanderScopeKey(EmpireRef owner);                         // the one commander-pool key encoder (X9)
```

`zomboss-commander-clock` already writes against `SaveOfRunUnlocked` and `CommanderLevelOf`, and
`empire-species-container` against `(SaveId, EmpireId)`. This module supplies those seams and defines
nothing else of theirs.

### The progression gaps handed to this module: G3, G4, G5 (`species-progression`) and X9, X11, X12 (`empire-progression`)

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


Both maps' ruling passes named the same R3 consequences and assigned them here. Each is decided below.

**G3: layer 1b (`rpg_player_species_mod`) belongs to the save's human empire, not to the person.**
A fusion pick is paid from the save's own resources (souls and materials, classified as empire-scoped
above), made in that save's world, on a species that empire fields. So it cannot be human identity: a
new save must not inherit another save's picks. It is not merely save-scoped either, because
`species-layer-delivery` reads *"1b of E"* per empire, and Zomboss's 1b is empty by definition (he does
not fuse). So the owner is `EmpireRef(save, the empire whose resources paid)`, which is
`HumanEmpireOf(save)` for every fusion today. The table is new, so it is **born Tier A**:
`(save_id, empire_id, species_id, instance_id, …)`. That costs no migration. The one rule it follows
is: never key an empire asset by the person.

**G4 / X11: the run → save mapping is total, and it already exists under another name.**

- A run is stamped with the save current at `board.start`, and it keeps that save for its whole life
  (`decisions.md` rows "Players" and "Mid-match switch"; stamping at `RpgStore.cs:2855-2906`).
  `GetRunPlayerId` (`RpgStore.cs:3835`) already reads it. **`SaveOfRunUnlocked` is that function,
  typed and renamed. It is not a second lookup.**
- `ApplyRpgProgressionFromActivityUnlocked(db, playerId, runId, …)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:20-23`)
  receives the fact's `player_id`, which ingest stamped from the run. Its first parameter becomes
  `SaveId save`, and it asserts `save == SaveOfRunUnlocked(runId)` whenever `runId` is set. A mismatch
  throws, because it would mean a fact crossed saves.
- **Every award names its owner**: `new EmpireRef(save, empireOfTheAward)`. Which empire earns
  (R1: the entity's side, through `KillAttribution.EmpireOf`) is `ai-empire-species`'s crediting rule.
  This module supplies only the `EmpireRef` and the re-keyed `TryApplyXpUnlocked`. That covers both
  species XP paths: the per-placement award (`:31-45`) and the run-completion loop (`:113-120`). A fact
  whose run resolves to no save awards nothing and is reported. It is never credited to a guessed save.
- **The aptitudes fetch** (`AptitudeEndpoints.cs:155-178`): the path value is the `SaveId`, and the
  response covers every empire of that save (Contracts, above).
- **The commander roster listing** (`CommanderEndpoints.ProjectList`, `:52`; `commander-roster`'s
  `ICommanderRoster`): a roster of commanders is an **empire's**. It lists per `EmpireRef`, and the
  route defaults to `HumanEmpireOf(save)`. `ForPlayer(long)` becomes `ForEmpire(EmpireRef)`.

**G5 / X12: the ownership key for a Zomboss specimen is `EmpireRef(save of the deploy's match,
EmpireId.Zomboss)`.**

- **Storage.** `rpg_unique_actors.player_id` holds the save, and `empire_id` holds `"zomboss"`.
- **Mint.** `MintForEmpire(owner, …)` replaces `MintForZomboss` (`RpgStore.ZombossDeploy.cs:42-47`).
  The owner comes from `SaveOfMatchUnlocked(matchKey)` (section "Zomboss stops being a player row").
- **Injector.** The owner map's value is the specimen's `EmpireId`. The save is implicit, because the
  injector plays one save and gets it from the server.
- **Core.** `SpecimenOwnershipOracle` takes the human `EmpireId` and a `ptr → EmpireId?` resolver, and
  answers ally or enemy by **comparing empires**. The old code compared player ids. An unregistered
  pointer still falls back to its mechanical side, which is unchanged.
- **Kills.** `KillCredit` carries `EmpireRef? SpecimenOwner`.

`default-build` is unaffected, because its resolver keys by `instanceId` (as that map's X12 notes).

**X9: the commander pool key under R3.** The siege seam reads the human's pool as
`player:{header.PlayerId}` when the member's empire is Dave, and Empty otherwise
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:573-576`). Under R3:

- **The persisted string does not change.** `player:{save}` already means *the commander allocation of
  the human empire of that save*, and `zomboss:{save}` means Zomboss's (`CommanderId.cs:68-72`).
  `commander-identity` preserves both strings, so no allocation row migrates.
- **What moves is the key's type, and where it is built.** The commander pool string is encoded in
  **four** places today, not one: `CommanderIds.AllocationScopeKey` (`gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs:68-72`),
  `AptitudeEndpoints.ScopeKey` (`gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:123`),
  `AptitudeEndpointsScopeKey` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:432`) and the
  literal `$"player:{header.PlayerId}"` (`RpgStore.WorldTurns.cs:575`). All four route through **one**
  encoder, `CommanderScopeKey(EmpireRef)` (the directory's `AllocationScopeKey`, fed an `EmpireRef`),
  and the `empire == CommanderId.Dave` branch becomes a comparison with `HumanEmpireOf(save)`.
  `header.PlayerId` is `rpg_worlds.player_id`, the world's save. The owner-key encoders that share the
  `player:` spelling (`EffectOwnerKeys.Player`, `gk-core/src/FusionRpg.Contracts/EffectDtos.cs:162`;
  `GateCounterHost`, `gk-fusion/src/FusionRpg.Injector/Effects/GateCounterHost.cs:118`) are a different key
  (`OwnerKind.Player`, Tier B owner key above) and are not merged into it.
- **One seam, two modules, one owner each.** `species-progression` `layer-source-selector` rewrites the
  same world-turn provider (`RpgStore.WorldTurns.cs:559-591`). Its spec already consumes this module's
  two tokens: the selector takes `humanEmpire` instead of comparing with `Dave`, and the pool key comes
  from `CommanderScopeKey` (`docs/architecture/species-progression/spec-layer-source-selector.md:95-106`,
  `:151-169`). The split: **`layer-source-selector` owns the provider's shape** (which layers a member
  carries, and which empire a member counts as), and **this module owns only the two identity tokens**
  (the key encoder and `HumanEmpireOf`). Whichever lands second rebases onto the other; neither
  re-decides the other's part.
- **Behaviour is byte-identical for this module's part.** Human-empire members get the human pool, and
  other members get Empty, exactly as today. That also honours R4 (the side's pool applies whoever
  leads). Which empire a world member counts as (its side today, its owner in `layer-source-selector`'s
  design) is that module's decision and its own re-bless, not an identity change.
- **Out of scope here.** Giving Zomboss's siege members *his* pool (`zomboss:{save}`) would change
  battle numbers. It is not an identity change, so it is not done here. It belongs to the feature that
  decides what an AI empire's commander grants (`empire-progression`).

**A third meaning `commander-identity` hands over.** `commander-identity` splits `CommanderId` into
the faction (`EmpireId`) and the unit (`CommanderRef`). Its `== CommanderId.Dave` sites carry a third
meaning it cannot express yet, **"the save's human empire"**, and after `commander-identity` they read
`== EmpireId.Dave`. This module re-types each of them to `== HumanEmpireOf(save)` (or to an injected
`humanEmpire`), decided per site:

| Site | Meaning | After this module |
|---|---|---|
| `RpgStore.Aptitudes.cs:232`, `:266`; `RpgStore.WorldTurns.cs:573`; `SpeciesAllocationSource.cs:114`; `CheatState.cs:183` | only the human empire has rows / a commander pool | `HumanEmpireOf(save)` (Data) or an injected `humanEmpire` (Core, injector) |
| `CommanderEndpoints.cs:78`, `:93`; `ItemEquipEndpoints.cs:307`; `PlayerEmpireCommanders.cs:19` | the human's own commander (aura, equipment, default) | `HumanEmpireOf(save)` through the directory |
| `SpeciesAllocation.cs:29` | which persisted string shape a key uses (Dave keeps the pre-empire string) | stays `EmpireId.Dave`: it is a storage-compatibility fact about the faction, not a question about who plays |

### Consumers that must key by `(SaveId, EmpireId)`

| Program | Module | What it takes from here |
|---|---|---|
| `species-progression` | `empire-species-container` | its `(save_id, empire, species_id)` key. At build the column is spelled `empire_id` (this module's column naming) |
| `species-progression` | `zomboss-commander-clock` | `SaveOfRunUnlocked`, `CommanderLevelOf`, and the re-keyed progression store. **No player row for Zomboss** |
| `species-progression` | `species-layer-delivery` | its one fetch, `/api/aptitudes/{playerId}` with the path value = `SaveId`, serves every empire of `EmpiresOf(save)` in its empire-keyed sections; 1b is empire-keyed (G3) |
| `species-progression` | `species-mod-ledger` | G3, decided above: layer 1b is **empire-scoped** (the empire whose resources paid for the pick, today always the human's). `rpg_player_species_mod` is born keyed `(save_id, empire_id, species_id, instance_id, …)` |
| `species-progression` | `layer-source-selector` | reads "which empire" as an `EmpireId`; stores nothing |
| `empire-progression` | `ai-empire-species` | its level reader `SpeciesLevelOf` is typed `(SaveId, EmpireId, …)`. **Its separate `rpg_empire_species_progression` table is superseded**: every empire's levels live in the one re-keyed `rpg_actor_progression`. That also removes its "Dave on the old row, others on the new one" asymmetry, which is the same `empire == Dave` storage branch `commander-identity` removes from code |
| `empire-progression` | `commander-roster` | `rpg_commander_role.player_id` is already documented as *"the save"*; it becomes `save_id` beside `empire_id`. `ForPlayer(long)` becomes `ForEmpire(EmpireRef)` (X11) |
| `empire-progression` | `respec-free-counter`, `default-build`, `assign-ladder` | Tier B tables (respec, presets): human-empire only, with the API empire-typed. An AI empire's default is computed at read and never stored (that map's D1), so none of them needs a widened key |
| ↳ R18/R19 reconciliation (2026-09-18) | `empire-level`, `respec-free-counter` | **Exception to Tier B's human-only rule:** the free-respec **stock** ledger and the empire-level row are keyed for **every** empire `(SaveId, EmpireId)`, so Zomboss's empire accrues on the same track (R19). Only the **spend** stays human-only (`EmpireRef` refuses a non-human spend). Recorded as empire-progression X13 |
| `empire-progression` | `lawn-commander-seat`, `legion-commander` | specimen ownership through `rpg_unique_actors.empire_id`; the world-faction ↔ save-empire closure contract |

### The rule for a table created after this module

A **new** table follows the four classes from its first build, so no later migration is ever owed
for it: save-scoped → one `save_id` column; empire-scoped → **born Tier A**, `(save_id, empire_id, …)`,
even when only the human empire writes it today (G3's reasoning: on a new table the column costs
nothing, and it removes the later migration), with a store API that may still refuse a non-human
empire where the feature is human-only (R18's spend); instance-keyed → no owner column. Tier B exists
only for tables that predate this module. The column is spelled
`save_id`. A table specced before R17 that says `player_id` means the same value; renaming it before
its first build is the owning spec's edit, not a behaviour change.

### Cross-program keying sweep (2026-09-18)

Every spec written on 2026-09-18 in `action-enrich`, `action-skill-tiers`, `species-gear-chain`,
`species-progression`, `strain-splice-host`, `notification-ssot`, `empire-progression` and
`build-preset` was searched for `player_id`, `playerId`, `PlayerId` and `player:` keys. `action-enrich`,
`action-skill-tiers` and `strain-splice-host` key nothing by player. The new tables classify as:

| New table (spec) | Class here | Its spec |
|---|---|---|
| `rpg_notification`, `rpg_notification_save_rev`, `rpg_notification_key`, `rpg_notification_source_cursor` (`notification-ssot/spec-notify-store.md:48-90`) | save | consistent: `save_id` |
| `rpg_player_species_mod` (`species-progression/spec-species-mod-ledger.md:74-86`) | empire, born Tier A (G3) | consistent: `(save_id, empire_id, …)` |
| `rpg_species_layer_projection` (`species-progression/spec-empire-species-container.md:73-81`) | empire, born Tier A | consistent |
| `rpg_commander_role` (`empire-progression/spec-commander-roster.md:30-38`) | empire, born Tier A | consistent: `(save_id, empire_id, instance_id)`; `ForEmpire(EmpireRef)` (`:89`) |
| `rpg_empire_free_respec_ledger` (`empire-progression/spec-respec-free-counter.md:42-51`) | empire, born Tier A (R19: stock for every empire; R18: spend human-only) | consistent |
| the `empire` progression kind (`empire-progression/spec-empire-level.md:47`) | Tier A, in the rebuilt `rpg_actor_progression` | consistent |
| `rpg_allocation_respec` (`empire-progression/spec-specimen-respec-price.md:89-94`) | keyed by the allocation scope key, which already carries the save | consistent key; **mismatch 1** on its payer |
| `rpg_build_preset`, `rpg_build_preset_piece` (`build-preset/spec-preset-store.md:21-36`) | empire, born Tier B | **mismatch 2**: born Tier B (`save_id` only, `:106-120`) |
| gem-tier replay key `(playerId, correlationId)` (`species-gear-chain/spec-gem-tier.md:351`) | save-scoped idempotency over Tier B materials | consistent |

**Mismatches still open, each with its fix owner.** Several specs were re-keyed during this same pass
(`species-mod-ledger`, `ai-empire-species`, `layer-source-selector`, `empire-species-container`,
`commander-roster`, `notify-store`); what remains is below. This module edits none of those specs, and none of them
blocks this module's build.

| # | Where | Mismatch | Fix (owner) |
|---|---|---|---|
| 1 | `empire-progression/spec-specimen-respec-price.md:148` | the payer is the specimen's `UniqueActorDto.PlayerId`. After the migration a Zomboss specimen carries the same value, so the "refuse an AI empire" rule at `:150` never fires: the human would be quoted and charged for Zomboss's specimen | resolve the payer as the specimen's `EmpireRef` (`empireId`, new on the DTO) through `OwnsSpecimenUnlocked` (`empire-progression`) |
| 2 | `build-preset/spec-preset-store.md:21-28`, `:114-120` | `rpg_build_preset` is born Tier B, which leaves a future migration owed for no saving | add `empire_id TEXT NOT NULL` (always `HumanEmpireOf(save)` today) and keep the human-only API refusal (`build-preset`) |
| 3 | `species-progression-ideal.md:441` | the 1b column is marked superseded, but the 2b column still reads "empire is the `players` row … resolve Zomboss's by name" | mark the 2b column superseded by R3 too (`species-progression`) |

No mismatch was found in `notification-ssot` routing (per-save group, archived rows refused,
`spec-player-routing.md:69-70`, `:145`), in `build-preset`, or in the R18/R19 exception above.

### What this module deliberately does not do

- **No cross-save human profile.** See Decision 1.
- **No rename of wire fields** (`playerId`, `currentPlayerId`). The rename would be churn across the
  web, the injector and the tests for zero behaviour. The meaning is documented once instead.
- **No widening of Tier B tables.** Each widens when a feature needs a second empire there, through
  this module's framework.
- **No re-attribution of history** (step 4).
- **No change to the persisted strings** `commander-identity` preserves.

## Commands

```powershell
dotnet build src\FusionRpg.Server
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity|FullyQualifiedName~SpecimenOwnership|FullyQualifiedName~AiEmpireSpecimen"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ZombossDeploy|FullyQualifiedName~AtomPush"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpecimenOwnership|FullyQualifiedName~KillAttribution"
python gk-core/scripts/guard-open-identity.py      # new in commander-identity; gains I3 and I4 (below)
python gk-core/scripts/guard-dal.py
.\scripts\run-guards.ps1 -Tier ci
python scripts\audit-overflow.py --targets A3
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>
# crosses Core + Data + Server + Injector + Contracts + web: full suite once at module end (AGENTS.md point 2)
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Saves/SaveId.cs` | **new**: `SaveId`, `EmpireRef`, `EmpireController` |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SaveEmpires.cs` | **new**: schema, `SeedSaveEmpiresUnlocked`, `HumanEmpireOf`, `EmpiresOf`, `SaveOfRunUnlocked`, `SaveOfMatchUnlocked` |
| `gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs` | **new**: the one-shot migration |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` | `SeedPlayerIfEmpty` / `CreatePlayer` call the seeder; `ListPlayers` / `SetCurrentPlayer` skip archived rows; the Tier A DDL |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs` | `EnsureZombossPlayer` and `ZombossPlayerName` deleted; `MintForEmpire` |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs`, `RpgStore.UniqueActors.cs`, `RpgStore.Creatures.cs`, `RpgStore.Souls.cs`, `RpgStore.Aptitudes.cs` | `EmpireRef` on every Tier A read and write; codex skipped for AI mints |
| Tier B store files (items, charms, loot, materials, souls, summons, patron, contracts, delves, presets, respec, titles, PvzStats) | public methods take `EmpireRef` and refuse a non-human empire. **Signature change only, no SQL change** |
| `gk-core/src/FusionRpg.Core/Battle/SpecimenOwnershipOracle.cs`, `KillAttribution.cs` | ownership by `EmpireId` / `EmpireRef` |
| `gk-fusion/src/FusionRpg.Injector/CheatState.cs`, `Match/MatchHost.cs`, `CheatActions.cs` | owner map value `(EmpireId, EmpireController)` from the spawn payload; the elimination rule deleted |
| `gk-core/src/FusionRpg.Server/UniqueActorService.cs`, `AtomPushService.cs` | `empireId`/`controller` in `pvz.spawn.extra`; no `ExtraSpawnFired` for an AI empire; `OwnersForSave` |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs`, `RpgStore.Fusion.cs`, `RpgStore.Patron.cs`, `RpgStore.Expeditions.cs`, `gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs` | `OwnsSpecimenUnlocked` at every specimen-targeted write; contracts skipped for an AI empire |
| `gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs`, `Dtos.cs` | `empireId`; `SaveEmpireDto` (new) |
| `gk-core/src/FusionRpg.Server/Program.cs`, `ZombossDeployEndpoints.cs`, `AptitudeEndpoints.cs`, `CommanderEndpoints.cs`, unique-actor endpoints | contracts above |
| `gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json` | **new**, authored |
| `gk-core/scripts/guard-open-identity.py` + Guard.Tests falsifiers | rules I3 and I4 |
| `docs/architecture/data-architecture.md`, `docs/database/schema.md`, `docs/protocol/rest.md`, `docs/protocol/signalr.md` | the save/empire model, at build |
| `docs/architecture/decisions.md` | rows S1–S4 below, **before** the build — landed 2026-09-18 |

## Code style

```csharp
// Before (RpgStore.ZombossDeploy.cs:44-47): an empire found as a player row, by name, shared by every save.
var zomboss = EnsureZombossPlayer();
var (specimen, _) = MintCreature(zomboss.Id, …);

// After: the owner is an empire OF A SAVE, and the save comes from the match, never from "current".
if (SaveOfMatchUnlocked(db, matchKey) is not { } save)
    return MintResult.Refused("match_unresolved");            // never a guessed save
var owner = new EmpireRef(save, EmpireId.Zomboss);             // the faction this endpoint serves, by meaning
var specimen = MintForEmpire(owner, speciesId, seed);          // same mint mapping; no codex write for an AI empire

// Tier B: empire-typed from day one, fail loud until the key widens.
public SoulBalanceDto GetSoulBalance(EmpireRef owner)
{
    RequireHumanEmpire(owner, table: "rpg_soul_balances");     // throws EmpireScopeNotWidened, never writes Dave's row
    return ReadSoulBalanceUnlocked(owner.Save.Value);          // SQL unchanged: player_id is the SaveId
}
```

Naming: `SaveId` / `EmpireRef` in code; `save_id` / `empire_id` in new or rebuilt tables; `player_id`
in untouched tables, documented once as the `SaveId`.

## Testing strategy

All store tests run **in memory** (testing-standard), except the backup test, whose subject is the
disk. That one is `DiskSemantics`-tagged and leak-proof through the file helper.

**Migration** (`gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityMigrationTests.cs`, new). Each fixture
builds the pre-R3 layout through the **current** production calls (`CreatePlayer`, `MintCreature`,
`EnsureZombossPlayer` as it exists before deletion, `TryApplyXpUnlocked`), captured once as a fixture
script, so the input is a state real play could have produced:

- One save, plus a Zomboss row whose specimens have no provenance: all of them go to save 1 under rule
  (b). The legacy row is archived and absent from `ListPlayers`.
- Two saves, with provenance via an XP receipt and via a lawn session: each specimen lands on its
  match's save.
- Two saves, no provenance: the specimens are `Retired` on the legacy row, and the report lists each
  id.
- A human save named "Zomboss" that owns runs stays a save, with both empires.
- **The name collision, the other way round.** A save named "Zomboss" created **before** Zomboss's
  first deploy, so `EnsureZombossPlayer` minted into it; it owns no run but holds a summoned
  specimen. It stays a save (step 2's evidence), and its `origin = 'zomboss'` specimens stay on its
  human empire.
- **Each evidence kind alone** (current setting, a world, a non-Zomboss specimen, an item row, an
  allocation on one of its specimens) makes the legacy row a save; a row with only allowed Zomboss
  writes is archived.
- **Provenance survives the sweep.** A Zomboss specimen left `ActiveBound` in an open run is attributed
  by rule (a) before the sweep clears its `match_key`.
- **Re-homed children.** A re-homed specimen's lawn-session and recovery rows carry the new `save_id`,
  and its legacy contract is released.
- **Byte-identical human numbers.** For every save, every `rpg_actor_progression` value and every
  resolved allocation equals the pre-migration read, for the human empire.
- **Idempotent.** A second boot changes nothing and writes no second marker.
- **Atomic.** An injected failure at step 5 leaves the schema, the rows and the marker exactly as
  before.
- **Backup first.** The `.bak` exists before the first write, and a failed backup aborts with no write.
  A second attempt after a failed one writes a new `.bak` and leaves the first untouched.
- **Fresh database.** A first boot creates the widened tables, writes the marker at seed, and never
  renames a table.

**Contracts** (stable across generations, never counts):

- Every save has exactly one `human` empire. `EmpireController` has two members (a closed vocabulary,
  pinned with that reason).
- Every Tier A row's `(save_id, empire_id)` exists in `rpg_save_empires` (join closure). No
  `empire_id` is null after migration.
- Every `rpg_world_factions.faction_id` that names an empire resolves to an empire of its world's save.
- The human roster, progression and allocation reads never return an AI empire's row. A Zomboss
  specimen minted into save 1 is absent from save 1's human roster and present under
  `?empire=zomboss`.
- A Tier B store call with a non-human empire throws `EmpireScopeNotWidened`, and its row count is
  unchanged.
- An AI-empire mint leaves `rpg_creature_codex` unchanged.
- `/api/zomboss/deploy` with an unresolvable `matchKey` returns 409 and mints nothing.
- **An AI-empire specimen never reaches a human-only table.** A Zomboss mint writes no
  `rpg_creature_contracts` or `rpg_contract_state` row; its deploy passes without a contract (D6: a
  13th Zomboss deploy in one save still deploys); its deploy records no `ExtraSpawnFired` fact on the
  save.
- **One ownership predicate.** Each specimen-targeted write listed in "One ownership predicate"
  (fusion input, fusion pick, patron, contract bind, expedition dispatch, lawn-XP recovery, item equip)
  called by save 1's human with a Zomboss specimen of save 1 is refused with that site's existing
  reason, and its tables are unchanged. A Zomboss specimen's species award does not credit the human's
  zombie species (`RpgStore.cs:3913`).
- **Match runtime keeps every empire.** `OwnersForSave(save)` includes an `ActiveBound` Zomboss
  specimen of that save, and the human roster read of the same save does not.

**Injector and Core:**

- `SpecimenOwnershipOracle` over `EmpireId`: a third registered empire resolves as an enemy of the
  human, with no code edit. That test is the D4 fix made executable.
- The spawn payload's `empireId`/`controller` register the owner; a payload without them registers as
  unknown and the mechanical side decides, never `Ally`. A Zomboss specimen and a human specimen of
  the **same save** resolve `Enemy` and `Ally`. `MatchHost`'s Zomboss-unit test finds Zomboss's own
  specimen by `EmpireId.Zomboss` with no elimination step.

**Guard I3** (extends `commander-identity`'s `guard-open-identity`, not a new guard): no `players` row
is looked up by `Name` anywhere in `src/` (the `ListPlayers().FirstOrDefault(p => … p.Name …)` shape),
and the identifiers `EnsureZombossPlayer` and `ZombossPlayerName` do not exist. **I4:** no
`<actor|row|specimen>.PlayerId ==`/`!=` comparison in `gk-core/src/FusionRpg.Data` or `gk-core/src/FusionRpg.Server`
outside `OwnsSpecimenUnlocked` (the shape of the eight sites it replaces). I4 is a text rule and can be
evaded by renaming a variable, so the ownership contract tests above are the real gate and I4 only
stops the common shape. Falsifier tests plant each pattern and expect a failure.

**Goldens.** Human-empire numbers do not change, so no golden is **expected** to move. That is a
prediction, not a tested fact: the full suite runs once at module end. A moved golden stops the module
until it is explained.

## Boundaries

- **Always:** take an `EmpireRef` wherever the data is empire-scoped; resolve a save from a run or a
  match, never from `current_player_id`, whenever the event carries one; back up before migrating.
- **Ask first:** widening a Tier B table (that is the owning feature's decision, through this
  framework); purging the `__pre_save_identity` tables or the `.bak`; renaming a wire field.
- **Never:** look up a `players` row by name; create a player row for an empire; re-attribute history;
  let the migration run without a backup; let a Tier B write for a non-human empire fall through to
  the human's row; hard-code `"dave"` as the human empire outside the new-save registry and the
  migration's historical step; decide specimen ownership by comparing `player_id`; archive a legacy row
  on anything short of step 2's full evidence test.

## Success criteria

- [ ] `SaveId`, `EmpireRef` and `rpg_save_empires` exist. Every save has its empires from the
      registry, including a fresh boot and a new save.
- [ ] No player row represents Zomboss. `EnsureZombossPlayer` is gone, and guard I3 gates.
- [ ] Zomboss's specimens and levels are per save. Save A's Zomboss is not save B's.
- [ ] The save screen no longer offers "Zomboss" (D2).
- [ ] Ownership is read as an `EmpireId`, carried in the spawn payload. A third empire needs no code
      edit (the oracle test).
- [ ] No AI-empire specimen writes a contract, a codex row or a save activity fact, and Zomboss
      deploys past his 12th (D6).
- [ ] Every specimen-targeted write goes through `OwnsSpecimenUnlocked`; guard I4 gates.
- [ ] Migration: backed up, atomic, idempotent, reported; human numbers byte-identical.
- [ ] Consumers in both progression programs build against these seams, with no second key; the
      keying-sweep mismatches are closed by their owners or still listed there.
- [x] `decisions.md` rows S1–S4 merged before the first code commit (landed 2026-09-18, docs only).
- [ ] Full suite green at module end. No golden moved, or every move explained.

## Seedsmith and generators

**None.** This module changes identity and storage keys. It adds no seed field, reads no generated
corpus, and changes no generator's input. The one new data file,
`gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json`, is an authored registry (`**/_registry/**` is
hand-authored by rule), with no `_meta` provenance. Its validator checks the schema, closed
`controller` membership, exactly one `human` row, and `empireId` shape. It never checks a row count.

## `decisions.md` rows owed before the build

**All four landed in `decisions.md` on 2026-09-18** (owner ruling: land every drafted row before the plan phase; session `decisions-rows-20260918`), each as an in-place `⚠️ AMENDED 2026-09-18` clause keeping the struck text, or a new row: **S1** → landed in decisions.md *Players (save identity, R3 + R17, 2026-09-18)* 2026-09-18; **S2** → landed in decisions.md *RpgProgression* 2026-09-18; **S3** → landed in decisions.md *Key-widening schema migration (2026-09-18)* 2026-09-18 (beside *DAL single gate*); **S4** → landed in decisions.md *Buff/debuff scope (2026-08-29)* 2026-09-18. `data-architecture.md` §2's *"`EnsureColumn` … only"* line still owes its pointer to the S3 row, at build. The draft text below is kept as the record of what was merged.

Four rows, drafted here as the exact text to merge. This spec does not edit `decisions.md`; the build's
first commit does, before any code (`AGENTS.md`: architecture changes that lock behaviour need
`decisions.md` first).

**S1: replaces the row `Players`** (today: *"Table `players` (`id` + `name` only). Server stamps
`player_id` from `settings.current_player_id` on `board.start`. Injector never sends player id"*, which
is already stale: the table also holds `created_utc` and `world_seed`, `RpgStore.cs:198-203`).

```
| Players (save identity, R3 + R17, 2026-09-18) | **A `players` row is a save**, and its id is the `SaveId`: no id is rewritten, and a `player_id` column in a table that predates `save-identity` holds the `SaveId`. The human's identity is the row's `name` and its `rpg_user_settings`; there is no separate profile. A save owns its empires as data in `rpg_save_empires(save_id, empire_id, controller)` (`controller` closed: `human` / `ai`, exactly one `human` per save), seeded from `gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json`. **No empire is ever a player row**, and no code finds a `players` row by name (`guard-open-identity` I3). A row that is not a save is `archived_utc`-stamped and never listed or selectable. Server stamps `player_id` (the save) from `settings.current_player_id` on `board.start`; an event that carries a run or match resolves its save from that, never from the current setting. Injector never sends a save id. Spec: [spec-save-identity.md](solid-enforcement/spec-save-identity.md) |
```

**S2: replaces the row `RpgProgression`** (today: *"Per-save **type** actors `(player_id, kind,
type_id)`; …"*).

```
| RpgProgression | Per-save, **per-empire** type actors `(save_id, empire_id, kind, type_id)` (R1 + R3, 2026-09-18; `rpg_actor_progression` and `rpg_xp_ledger` rebuilt once by `save-identity`, every pre-R3 row on its save's human empire, history never re-attributed). Every award names its owner `EmpireRef(save of the fact's run, empire of the award)`; a fact whose run has no save awards nothing. Activity-driven XP; arithmetic `XpToNext`; demotion_count debt; CoR level hooks; power deferred. Specimens ≠ type actors — [unique-actor-runtime.md](unique-actor-runtime.md). See [rpg-progression.md](rpg-progression.md) |
```

**S3: new row**, beside `SQLite` and `DAL single gate`. It amends `data-architecture.md` §2's
*"`EnsureColumn` … only. No table drops"* (`data-architecture.md:109`) for exactly one case.

```
| Key-widening schema migration (2026-09-18) | Schema evolution stays additive (`EnsureColumn`, no drops) **except** when a primary or unique key must widen. That is done only by a one-shot class in `FusionRpg.Data/Sqlite/Migrations/`, run from `Init`, which (1) writes a new, never-reused file backup (`VACUUM INTO`) before any write and refuses to start the server if it fails; (2) runs every write in one transaction whose last statement writes a `settings['schema.<module>']` report marker, and is a no-op once that marker exists; (3) renames each old table to `<name>__pre_<module>` and never drops it (purging it is a user-driven storage action); (4) is exercised by an in-memory migration test built from real production calls, plus one disk test for the backup. First user: `save-identity` |
```

**S4: amends the row `Buff/debuff scope (2026-08-29)`**, whose specimen-ownership-bridge clause says
the injector caches the owning **player id** and the oracle answers `Ally` when it matches the
reactor's `myPlayerId`. Append:

```
**Amended 2026-09-18 (R3, `save-identity`):** the specimen ownership bridge carries the owning **empire**, not a player id. `pvz.spawn.extra` sends `empireId` and `controller` beside `playerId` (the save); `CheatState` maps `ptr → (EmpireId, EmpireController)` for the entity's life; `SpecimenOwnershipOracle` answers `Ally` when the owner's controller is `human`, `Enemy` for any other registered owner, `null` when none is registered (the mechanical side decides). Ownership is read, never inferred by elimination.
```

## OWNER questions

**None.** R3 and R17 settled the business questions. Everything above is a technical consequence of
them, and each choice gives its reason. In particular, retiring unattributable legacy Zomboss
specimens loses no play state (migration step 5 checks it against code), and taking AI specimens out
of contracts follows from contracts being the summoner's own mechanic, not a ruling to make.

## Self-audit — the debate

**"Just add `empire_id` to every `player_id` table now; a two-tier scheme is complexity."** Widening
all of them means about 40 rebuilds (39 tables carry `player_id` in a primary key or `UNIQUE`, a reading), each with its own
risk, for empires that do not own those assets and have no feature that would give them any. Tier B
does not leave a hole: its API is empire-typed from day one and **throws** for a second empire. So the
day an AI empire gets a soul balance, the failure is loud and the fix is one migration, with no caller
edited. Widening everything up front would pay a large, irreversible migration for no reader. That is
the opposite of this program's "green first" discipline.

**"Tier B's `player_id` still doubles as the empire. Isn't that the defect R3 removes?"** No. The
defect was that the *row* was the empire, so a second empire needed a second *player row*. After this
module, no second player row can exist (guard I3), and the owner type is `EmpireRef` everywhere. Tier B
is storage that, by contract, holds exactly one empire's rows, and the code says so at the call. That
is the same shape as `rpg_zomboss_state`, which is keyed per save and holds one named empire.

**"Why rebuild `rpg_actor_progression`? `ai-empire-species` avoided a rebuild with a second table."**
Its second table left the human's empire on the old table and every other empire on the new one. That
is two stores for one concept, and a storage-level `empire == Dave` branch, exactly the kind of branch
`commander-identity` deletes from code. R3 says every empire is keyed `(SaveId, EmpireId)`. One table,
one key, one reader is the S in SOLID. The rebuild's cost (one backed-up, transactional migration of
two tables) is paid once. The two-table cost is paid by every future reader.

**"The migration guesses when it assigns legacy specimens to 'the only save'."** It does not guess. A
Zomboss specimen is minted during a match, and every match's run carries the save that was current at
`board.start` (`decisions.md` "Players" and "Mid-match switch"). With exactly one save, no other save
can have hosted it. With two or more saves and no provenance, the rule **refuses** to attribute, and
retires the specimen instead.

**"Keep `/api/players` but call it saves: isn't the name now wrong?"** It is. Renaming it costs the web,
the injector and the E2E tests a coordinated break, and buys nothing a reader cannot get from one
documented sentence. If the owner wants the rename, it is a follow-up that renames only.

**"Is the codex really save-scoped rather than per empire?"** Its only writer outside Zomboss's mint is
the player's own collection flow (`UpsertCreatureCodex`, `RpgStore.Creatures.cs:73`). The web shows it
as the player's almanac. A Zomboss codex has no reader. Save-scoped, with AI mints excluded, is what
the data already means.

**"Why carry ownership in the spawn payload instead of the empires cache the first draft had?"** The
cache's key-set edge (a save switch) has no signal to the injector today, and the oracle's real
question is "which empire owns this entity", which the server already answers at the deploy that
creates the entity. A fact that cannot change during the entity's life needs no refresh, so it needs
no trigger set. The cost is two fields on one command payload.

**"Skipping contracts for Zomboss's specimens is a gameplay change, so it needs a ruling."** It does
not change anything a player sees. Today those contracts sit on a row no player loads, and their only
observable effect is D6, Zomboss's deploys stopping after the 12th. Contracts are the summoner's
binding slots, loyalty and tribute; giving an AI empire a contract would need a design nobody has
asked for. Keeping them would, after the migration, spend the human's own slots on Zomboss's mints.

**"The step 2 evidence test is complicated; `owns a runs row` was simpler."** It was also wrong for
the one case the brief of this module names: a player's save called "Zomboss" that was used for
summons but never started a board. `runs` alone would archive it and hand its creatures to Zomboss.
The test is an allowlist of what the Zomboss path writes, taken from the code, and it errs to "save".

## Gaps found and closed while writing

- **D2 was not in the ruling.** Reading the save screen found that Zomboss is a loadable summoner once
  he has deployed. It is fixed by archiving the non-save legacy row.
- **The human roster regression.** Moving Zomboss's specimens onto a save would have put them in the
  human's roster through the unfiltered read at `RpgStore.UniqueActors.cs:138`. It is now a named
  contract test.
- **`species-progression` G3–G5 and `empire-progression` X9, X11, X12** (both maps' gaps assigned to
  this module) are each decided in their own section above: 1b is the human empire's, the run → save
  mapping is `GetRunPlayerId` typed, Zomboss's ownership key is `EmpireRef(save of the match,
  zomboss)`, and the commander pool keeps its string while its encoder takes an `EmpireRef`.

- **Strengthen pass (2026-09-18), found by reading code:**
  - **The mint writes Tier B state.** `MintCreatureUnlocked` auto-binds a contract, and the deploy gate
    reads it (`RpgStore.Creatures.cs:88`). The first draft's blanket Tier B throw would have broken
    every Zomboss deploy after the migration; now the AI path skips contracts, and D6 goes with it.
  - **Eight ownership checks compare `player_id`.** After the migration they would all accept
    Zomboss's specimens; now one predicate and guard I4.
  - **The atom push reads the roster.** Filtering every specimen read by the human empire would have
    stripped Zomboss's `ActiveBound` specimens of their pushed atoms; reads are now classified by
    purpose.
  - **Step 2's `runs` test** could archive a real save named "Zomboss"; replaced by the evidence
    allowlist, and that save keeps its Zomboss-minted creatures.
  - **The boot sweep clears provenance.** The migration now runs before it.
  - **The injector cache's key-set trigger had no signal**; replaced by per-spawn ownership.
  - **Four encoders of `player:{save}`**, not one; X9 names all four, and splits the world-turn seam
    with `layer-source-selector`.
  - **`decisions.md`:** a fourth row (S4, the ownership bridge) was owed and missing; all four are now
    drafted as exact text.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: Data/SQL/schema, identity (saves, empires, commanders), unique actors, progression,
    injector ownership, REST/SignalR contracts.
[x] Session boundary: tasks/sessions/save-identity-spec-20260918.json (written), then
    tasks/sessions/strengthen-save-20260918.json (strengthen pass; this file, commander-identity and
    the map's save/commander rows only).
[~] Read this session: DESIGN-GATE §1 rows "Anything at all", "Stats", "Data / SQL / schema" and the
    actor-layer row; software-architecture.md §1-§3, §6-§9; data-architecture.md in full;
    contributing/session-boundary.md §1-§5; decisions.md rows "Players", "Mid-match switch",
    "RpgProgression"; spec-commander-identity.md in full; solid-enforcement-map.md; both progression
    maps; the consumer specs' keying sections. NOT read in full: stat-system.md, actor-hub-ssot.md,
    contributing/architecture-map.md. This module changes no actor number, so the Stats row's
    documents bound nothing here; the gap is stated rather than hidden.
[x] decisions.md checked; four rows owed (S1-S4, exact text drafted), none contradicted silently. Landed 2026-09-18.
    data-architecture.md:109 ("no table drops") is amended by S3 for key widening only.
[x] Every factual claim cites file:line; unbuilt files and APIs carry "(new)".
[x] audit-doc-citations.py run on this file: 0 HIGH.
[x] Claims verified against code, not comments (D1-D5 each read in code).
[x] Surrounding section read for every quoted rule.
[ ] Tested constraints: none run (docs-only sessions). "No golden moves" is a stated prediction. D6
    (Zomboss deploys refused after the 12th) is read from code, not live-proven.
[x] No §2 invariant contradicted: SQL stays in FusionRpg.Data (§2.6); the injector still originates
    no save id.
[x] No population pinned: table and route counts are readings; the closed vocabulary
    (EmpireController) is pinned with its reason.
[x] §2.16: no edge-refreshed cache is added. Injector ownership is a per-spawn fact from the deploy
    that creates the entity; the mixed-build case (payload without the fields) is tested and safe.
[x] ActorHub: no actor magnitude is produced or composed here; keys only.
[x] No SOLID-violating path: one save SSOT (players), one empire list (rpg_save_empires), one
    progression table per concept; the ai-empire-species two-table split is superseded.
```

## Plan-time defaults (2026-09-18, from `tasks/solid-enforcement-todo.md` SE4.11–SE4.43)

Recorded here so the spec and the plan say the same thing:

1. **Empires are seeded before the migration** for the current save (at boot and on a save switch) and for every
   save created normally (`SE4.12`); Zomboss's legacy row stays unseeded. Without this, a first-slice consumer such
   as `species-progression` `species-mod-ledger` (the fusion-pick fix) would find no human empire on a real save
   deployed before the migration. It fits step 2's rule that being current counts as evidence of a save.
2. **Step 2's evidence list gains one entry:** an `rpg_save_empires` row is evidence of a save (`SE4.16`), because of (1).
3. **Guard rule I4 is scoped to specimen ownership.** Presets, contract rows, expeditions and delves compare their own
   row's `PlayerId`; those comparisons are not specimen ownership. `SE4.42` measures them and scopes them out or lists
   them, never widening I4 to every `PlayerId` comparison.
4. **The ten `== CommanderId.Dave` sites split by assembly:** three in Core (`SE4.2`), seven in Data, Server and the
   injector (`SE4.3`).


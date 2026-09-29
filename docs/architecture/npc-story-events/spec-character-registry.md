# Spec: character-registry

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `character-registry`, row 7 of the [npc-story-events map](../npc-story-events-map.md) (`:213`), wave 2.
Depends on `story-ledger` (memory and fate as facts) and `narrative-vocabulary` (roles, fates, scopes). Reads the
character seed contract (`narrative-seed-ideal.md` §6.3, `narrative-seed-map.md:205`). Consumed by `cast-resolver`,
`narrative-predicates`, `narrative-text`, `outcome-routing` (`recruit`), `quest-log-contract` and the hosts. Draft
decision row **NS4** (`npc-story-events-map.md:402`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

The character store: a persistent identity for each character a save meets, bound to a **minted specimen** held
by a non-player owner row (the Zomboss precedent), with species, role, home and scope; memory and fate as story
ledger facts; an **ownership transfer** when a character joins, so the creature who talked to you is the one who
fights for you; world-scoped characters that are **frozen, never deleted or retired** when their world falls and
dormant while it hibernates (Owner ruling 2026-09-19 (round 4), replacing round 3's retirement) — every specimen
stays explained by its character row; and the anti-Nemesis rule that an enemy-role character never gains level, trait, rank or title from an encounter.

Success looks like: a cast character has exactly one row and, unless it is a lead, exactly one specimen owned by
the narrative cast row; after a join the same `instanceId` is owned by the player; a hibernating world's
characters are unchanged when the player returns; after its world falls every world-scoped character row, specimen
and fact is byte-identical to before the fall and reads as `Frozen`; an enemy-role character's specimen is
byte-identical before and after any narrative operation.

## Locked anchors

- **Mint-first under a non-player owner row** (map locked assumption 8, `:153-156`; ideal §6.3,
  `npc-story-events-ideal.md:403-410`): `EnsureZombossPlayer` finds or creates a named player row
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs:25-29`) and `MintForZomboss` mints under it through the
  shared mint (`:42-60`, `MintCreature` at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Creatures.cs:14-26`).
- **Personality is the specimen's own**: `ContractPolicy.PersonalityFor(instanceId)`
  (`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:195-196`) — no stored override, no second vocabulary
  (`CreaturePersonality`, `:18-25`).
- **Scope**: leads and companions are save-scoped; local characters are world-scoped (ideal §6.3). Owner ruling
  2026-09-19 (round 3): a world-scoped character lives as long as its world exists — active, hibernating or idle,
  contested or won — under the approved world-continuity program (`world-continuity-map.md` locked assumption 1).
  Owner ruling 2026-09-19 (round 4): and it is never deleted — a fallen world's cast is frozen, not retired (§4).
- **Leads are not creatures.** *"Every non-lead character is a creature with a name"* (ideal §6.3, `:381-386`); the
  three leads are the Garden Keeper, Hourbloom and the Rotwright (R11), referred to only by tokens (R8–R10).
- **R13 rules 1 and 3** (ideal §6.12, `:552-559`; map principle 17, `:127-130`).
- A character seed is **one seed per species that gets one** (`narrative-seed-ideal.md:348-350`); personality,
  disposition and home are not in the seed (`:360`).

## Design

### 1. Two kinds of character

| Kind | Specimen | Scope | Examples |
|---|---|---|---|
| `lead` | none | save | `lead_summoner`, `lead_companion`, `lead_antagonist` — one row each per save, created at first read |
| `creature` | exactly one, minted at casting | save (`companion`) or world (every other role) | a trader in a market, a hermit in a wildland, a warlord |

A lead row exists so that facts, casting and predicates address the leads the same way as anyone else; its
display name is always the names-registry token, never a stored string.

### 2. The narrative cast owner row

`EnsureNarrativeCastPlayer()` (new) is `EnsureZombossPlayer`'s shape with its own reserved name constant
(`NarrativeCastPlayerName`), and `MintForNarrativeCast(speciesId, ulong seed)` is `MintForZomboss`'s shape with
`Origin = "narrative"` (the Zomboss call sets `Origin = "zomboss"`, `RpgStore.ZombossDeploy.cs:41`, re-anchored 2026-09-20). Traits roll
through the shared `SummonRoller.RollTraits` on a named stream `narrative:cast:mint` (the Zomboss call uses
`"zomboss-deploy-ai:mint"`, `:46`). One row serves every save's cast; the character table (§3) keys characters by
save, so two saves never share a character even though their specimens share an owner row.

**Specimen identity is persisted, not re-derived.** `MintCreatureUnlocked` assigns `Guid.NewGuid()` as the
`instanceId` (`RpgStore.Creatures.cs:45`), so a character's personality is fixed at mint and stored with the
specimen. Casting (which characters, where) is seeded and reproducible (`cast-resolver`); the specimen id is not,
and does not need to be: the minted row is the identity from then on. Recorded under Contradictions 1.

### 3. Table (owned by `FusionRpg.Data`)

```sql
CREATE TABLE IF NOT EXISTS rpg_narrative_character (
  player_id      INTEGER NOT NULL,          -- the save this character belongs to
  character_id   TEXT    NOT NULL,          -- seed id, or lead_summoner / lead_companion / lead_antagonist
  scope          TEXT    NOT NULL,          -- 'save' | 'world'
  world_id       TEXT    NOT NULL DEFAULT '',
  kind           TEXT    NOT NULL,          -- 'lead' | 'creature'
  role           TEXT    NOT NULL,          -- NarrativeRoleCatalog id; leads use their lead role
  instance_id    TEXT,                      -- rpg_unique_actors.instance_id; NULL for leads
  home_kind      TEXT    NOT NULL,          -- 'sector-slot' | 'delve-domain' | 'homeworld' | 'none'
  home_ref       TEXT    NOT NULL DEFAULT '',
  seed_revision  INTEGER NOT NULL,          -- the character seed revision it was cast from
  cast_seq       INTEGER NOT NULL,          -- rpg_story_fact.seq of the cast fact (met or arc.started)
  revision       INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (player_id, scope, world_id, character_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_rpg_narrative_character_instance
  ON rpg_narrative_character(instance_id) WHERE instance_id IS NOT NULL;
```

- **Fate is derived, never stored** (`CharacterFate`, `spec-narrative-vocabulary.md` §3): `Joined` if a
  `character.joined` fact exists, `Fallen` if `character.fell`, `Departed` if `character.departed`, else `Present`
  — the latest of the three by `seq` wins. `CharacterState` adds `Unmet`/`Met` from the `met` fact.
- **Memory is facts**: `met`, `helped`, `refused`, `betrayed`, `spared` about `character:{id}` in the story ledger.
  The row holds identity and placement only.
- **Home** is written once at casting and changed only by a reviewed operation (`MoveCharacterHome`, used by a
  world rule, never by an encounter).

### 4. Operations

```csharp
// FusionRpg.Data — RpgStore.NarrativeCharacters.cs (new)
public NarrativeCharacterRow EnsureLeadCharacters(long playerId);                         // idempotent, three rows
public NarrativeCharacterRow CastCreatureCharacter(long playerId, CharacterCastRequest req);   // mint + row + cast fact, one tx
public NarrativeCharacterRow? GetCharacter(long playerId, StoryScope scope, string worldId, string characterId);
public IReadOnlyList<NarrativeCharacterRow> ListCharacters(long playerId, StoryScope scope, string worldId);
public TransferResult TransferCharacterToRoster(long playerId, string characterId, string sourceRef);
// Audit 2026-09-19 / Owner ruling 2026-09-19 (round 4): RetireWorldCharacters is withdrawn. A world-scoped
// character's availability is the derived WorldNarrativePhase of its world, read beside the row, never written.
```

**Cast** (`CastCreatureCharacter`): in one transaction — mint under the cast owner row, insert the row, append the
cast fact (`arc.started` or `met`, whichever caused it). A replay with the same `sourceRef` is a no-op through the
fact's dedupe key.

**Join** (`TransferCharacterToRoster`): in one transaction —
1. refuse unless the specimen's owner is the cast owner row, its phase is `Roster`, the character's derived
   fate is `Present`, and — for a world-scoped character — its world's `WorldNarrativePhase` is `Live`
   (`character.world-not-live`; Owner ruling 2026-09-19 (round 4): a dormant world is not drawn and a frozen one is
   read-only);
2. `UPDATE rpg_unique_actors SET player_id = $player, revision = revision + 1` for that one `instance_id` (the
   column at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:548-550`);
3. refuse if any per-player side row exists for the specimen (`rpg_unique_lawn_sessions`,
   `rpg_unique_actor_recovery` carry `player_id`, `RpgStore.cs:578-580`, `:596-597`) — a cast specimen has never
   been deployed, so none should; finding one is a defect, not a case to migrate;
4. upsert the receiving player's codex entry through the same statement the mint uses
   (`RpgStore.Creatures.cs:130-133`);
5. append `character.joined` (subject `character:{id}`, source `sourceRef`).
Binding a contract and its starting loyalty are the contracts program's (`BindContract`,
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:232`), called by `outcome-routing` after the transfer.

**World lifecycle — Owner ruling 2026-09-19 (round 4)** (replaces round 3's `RetireWorldCharacters`, which set a
fallen world's specimens to the terminal `Retired` phase and appended `character.departed`). World-scoped story state
is **never deleted and never rewritten**: world-continuity keeps a fallen world revisitable as hostile ground and the
reserved `world-reclaim` reads its history (`world-continuity-map.md:117`, `:127`, `:274-275`). No operation here
runs on a world transition; the character's availability is the derived `WorldNarrativePhase` of its world
(`spec-narrative-vocabulary.md` §3):

| World-continuity state | `WorldNarrativePhase` | World-scoped characters |
|---|---|---|
| attention `active` (outcome `contested` or `won`) | `Live` | present in their homes; cast, drawn, joinable |
| attention `hibernating` or `idle` (`hibernation-clock`, `idle-world`, `advance-carry`) | `Dormant` | kept intact — same rows, homes, specimens and facts; never cast or drawn; no writes except facts world-continuity's `CoarseStep` emits; met again on return |
| outcome `fallen` (`world-fall`) | `Frozen` | read-only history: rows, specimens and facts untouched; never cast, drawn or joined; `world-reclaim` may revive them later |

There is no "abandoned" state and no ask on `world-state-vocabulary`. A frozen specimen is not an orphan: it stays
owned by the cast owner row (never in any player's roster), and its character row plus its world's phase explain it.
`CharacterFate` stays the character's own story fate; a world transition never writes `Departed` or `Fallen`.

### 5. Anti-Nemesis (R13 rules 1 and 3)

An **enemy-role character** is one whose role is in the enemy-side set `character-vocab` declares
(`narrative-seed-map.md:205`, *"the enemy-side restrictions of R13"*; at minimum `warlord`).

- **No growth from an encounter.** This module exposes no operation that changes a specimen's level, xp, star,
  traits, rank or title. A source-scan guard, `NarrativeNoEnemyGrowthTests` (new, Guard.Tests), fails if any file
  under `gk-core/src/FusionRpg.Core/Narrative/**`, `src/FusionRpg.Data/Sqlite/RpgStore.Narrative*.cs` or
  `src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs` writes `rpg_unique_actors.level`/`xp`,
  `rpg_creature_profiles.star` (the write at `RpgStore.Fusion.cs:133`), trait ids, or calls a title grant. A world
  rule that grows a warlord (rule 6) lives in the world-map program and is not narrative code.
- **No personal memory.** Enemy-role characters never get relation facts written about them by this program's
  writers (a guard in `AppendStoryFact`'s narrative wrapper refuses `met/helped/refused/betrayed/spared` for an
  enemy-role subject); antagonist memory is faction-level (`relation-ledger` §2).
- **No hierarchy.** No field, table or type ranks characters against each other; the guard also fails on a type
  named `*Rank*`, `*Captain*` or `*Hierarchy*` under `Narrative/`, with `LoyaltyRank` (the contracts program's,
  outside the scan) untouched.

These are rows `ns6-no-enemy-growth`, `ns6-no-enemy-memory` and `ns6-no-enemy-hierarchy` in
`gk-core/scripts/enforcement-registry.v1.json`; `counter-doctrine` adds the faction-level rules later.

### 6. Seed catalog

`CharacterCatalog.Load(dir)` (new, Core) reads character seeds from `data/seed/narrative/characters/` (new): id,
species, role, voice, keyed name/epithet/bio, lines per (context × band), `revision`, `provenance`, `tombstone`.
It validates species against `CreatureSpeciesCatalog.IsKnown` (the mint gate uses the same catalog,
`RpgStore.Creatures.cs:33-35`), role and voice against their catalogs, and refuses a reused tombstone id. A cast
character keeps `seed_revision`; its lines resolve from that revision's text keys, which narrative-seed never
reuses.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `player_id`, `cast_seq`, `seed_revision`, `revision` | `long` | ids and counters over a save's life |
| ~~`RetireWorldCharacters` return~~ | — | Audit 2026-09-19: operation withdrawn (Owner ruling 2026-09-19 (round 4)) |

## SOLID notes

- **S:** one character store; memory and fate live in the story ledger, not in columns beside it.
- **O:** a new role or home kind is a vocabulary change; the operations do not change.
- **L:** a cast specimen is an ordinary specimen — every roster, contract and battle path treats it as one after
  the transfer, because nothing about it is special except its origin.
- **D:** hosts and casting call these operations; none writes `rpg_unique_actors` for a character directly.
- One personality vocabulary, one mint, one specimen table: no parallel NPC entity.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Data/Sqlite/RpgStore.NarrativeCharacters.cs','src/FusionRpg.Core/Narrative/Characters/CharacterCatalog.cs','tests/FusionRpg.Data.Tests/Narrative/NarrativeCharacterStoreTests.cs','tests/FusionRpg.Guard.Tests/NarrativeNoEnemyGrowthTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~NarrativeCharacter|FullyQualifiedName~ZombossDeploy"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NarrativeNoEnemy"
python gk-core/scripts/guard-dal.py ; python gk-core/scripts/guard-test-substrate.py
```

## Structure

```
src/FusionRpg.Core/Narrative/Characters/CharacterCatalog.cs            (new)
src/FusionRpg.Core/Narrative/Characters/NarrativeCharacter.cs          (new: row record, fate fold)
src/FusionRpg.Data/Sqlite/RpgStore.NarrativeCharacters.cs              (new)
tests/FusionRpg.Data.Tests/Narrative/NarrativeCharacterStoreTests.cs   (new)
tests/FusionRpg.Core.Tests/Narrative/Characters/CharacterCatalogTests.cs   (new)
tests/FusionRpg.Guard.Tests/NarrativeNoEnemyGrowthTests.cs             (new)
gk-core/scripts/enforcement-registry.v1.json                                    (edited: three ns6 rows)
```

## Testing strategy

All store tests in memory (`DataTestStore.Create()`, `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs:37-47`).

- **Mint-first:** casting creates one row and one specimen owned by the cast owner row with `origin = narrative`;
  a second cast with the same source is a no-op.
- **Personality is the specimen's:** the character's personality equals `ContractPolicy.PersonalityFor(instanceId)`;
  no personality column exists.
- **Join keeps identity:** after `TransferCharacterToRoster`, the player's roster contains the **same**
  `instanceId`; the owner row no longer owns it; one `character.joined` fact exists; a second transfer refuses; a
  transfer of a `Departed` or `Fallen` character refuses.
- **World lifecycle (Owner ruling 2026-09-19 (round 4)), one test per edge:** moving a fixture world to
  `hibernating`, to `idle`, back to `active`, and to outcome `fallen` leaves every character row, specimen (phase,
  owner, level, traits) and fact byte-identical; the derived phase reads `Dormant`, `Dormant`, `Live`, `Frozen`;
  no `character.departed` is written; a save-scoped companion reads `Live` throughout.
- **Order independence:** join then world fall, and world fall then (attempted) join, are both specified: the first
  leaves the joined creature with the player (it is roster, no longer world-scoped); the second refuses
  `character.world-not-live`. The same pair is specified for hibernation (join refused while `Dormant`, allowed again
  after the return).
- **Enemy guards:** the guard scan fails on a probe source string writing `level`; an enemy-role subject refuses a
  relation fact; an enemy specimen's `(level, xp, star, traits)` tuple is identical before and after every
  operation in this module.
- **Leads:** `EnsureLeadCharacters` creates three save-scoped rows with no specimen, idempotently.
- **No population:** tests never count characters in a seeded corpus.

## Success criteria

1. Every non-lead character is a real specimen under the cast owner row. 2. A join transfers the same specimen.
3. A fallen world freezes its cast untouched (no unexplained specimen, nothing deleted); a hibernating one keeps
its cast dormant. 4. The three ns6 guards and registry rows land. 5. Fate is derived
from facts; no fate column.

## Boundaries

- **Always:** mint through the shared mint; transfer in one transaction; derive fate; derive world availability
  from `WorldNarrativePhase`.
- **Ask first:** a second owner row (for example one per faction).
- **Never (Owner ruling 2026-09-19 (round 4)):** delete, retire or rewrite a world-scoped character, specimen or fact
  on a world transition; add an "abandoned" state.
- **Never:** grow an enemy from an encounter; store a personality or disposition; mint outside the shared mint; a
  character table per place.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `CastCreatureCharacter`, `EnsureLeadCharacters`, `ListCharacters`, `GetCharacter` | `cast-resolver` |
| derived `CharacterFate` / `CharacterState` | `narrative-predicates`, `relation-ledger` (join edge) |
| `TransferCharacterToRoster` | `outcome-routing` (`recruit` of a cast character) |
| world availability (`WorldNarrativePhase` beside each row) | `cast-resolver`, hosts, `quest-log-contract` (Owner ruling 2026-09-19 (round 4); the round-3 `RetireWorldCharacters` ask on `world-fall` is withdrawn) |
| `CharacterCatalog` | `cast-resolver`, `narrative-text` (names, lines) |

## Contradictions found (report; not fixed here)

1. **"Seeded and reproducible" and specimen ids.** Map principle 12 (`:111-114`) says seeds are cast per save,
   seeded and reproducible. The shared mint draws a random GUID for the specimen id (`RpgStore.Creatures.cs:45`),
   and personality derives from that id. The cast is reproducible; the specimen's id and personality are persisted
   state, not re-derivable from the seed. No change is proposed (the mint is shared by every creature), but the
   principle's wording should say "cast choices are seeded; minted identity is persisted".
2. **Templates versus one seed per species.** `npc-story-events-ideal.md:399-401` and map row 8 (`:214`) describe
   casting *"character templates onto concrete species"*; `narrative-seed-ideal.md:348-350` makes a character one
   seed **per species** and rejects species-agnostic templates (`:563`). This spec follows narrative-seed: a
   character's species is in its seed; casting chooses which characters a save meets and where they live
   (`spec-cast-resolver.md`). Reconciled 2026-09-19: the npc ideal §6.3, principle 12 and map row 8 now say the same.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: creatures (mint, roster, codex), contracts (reader), data/SQL, narrative state, R13.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 7, NS4; ideal §6.3, §6.12, §9; narrative-seed §6.3; RpgStore.ZombossDeploy.cs,
    RpgStore.Creatures.cs (mint, codex, roster filter), rpg_unique_actors DDL, RpgStore.Fusion.cs (Retired),
    rpg_worlds DDL and writers, ContractPolicy.PersonalityFor.
[x] Every claim cites file:line.
[x] Actor numbers: none written; the enemy guard proves it.
[x] Caches: none. Order dependence (join vs world end) specified both ways.
[x] No population pinned. No parallel entity store.
[x] Registry rows: ns6-no-enemy-growth, ns6-no-enemy-memory, ns6-no-enemy-hierarchy.
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | Round-4 owner ruling: `RetireWorldCharacters` set fallen-world specimens to the terminal `Retired` phase (the fusion-sacrifice state, `RpgStore.Fusion.cs:566-570`) and appended `character.departed` — rewriting history `world-reclaim` must be able to revive — and kept an "abandoned" trigger with an ask on `world-state-vocabulary` | **Fixed:** operation withdrawn; availability is the derived `WorldNarrativePhase`; joins refuse outside `Live`; per-edge tests |
| 2 | medium | The fate fold would have reported a fallen world's characters as `Departed` though no story event happened to them (fate and world lifecycle conflated) | **Fixed:** fate is story fate only (`spec-narrative-vocabulary.md` §3) |
| 3 | low | Map citations one line early (`:212`, `:401`, `:213`) | **Fixed** |
| 4 | low | Citations sampled: `RpgStore.ZombossDeploy.cs:25-29`, `RpgStore.Creatures.cs:45` (`Guid.NewGuid`), `ContractPolicy.cs:195-196` — hold | no change |

Checked and clean: mint-first under a non-player owner row, one personality vocabulary, ownership transfer in one
transaction, store tests in memory, SQL in Data only, R13 rules 1–3 as guards, fate derived not stored, no population
pin.

**Propagation owed (outside this fence):** `spec-quest-sources.md` §4 and `spec-quest-log-contract.md` read a fallen
world's characters/quests as retired/failed; under round 4 they are frozen.

**Proposed enforcement-registry rows** (unchanged ids, now with guards named): `ns6-no-enemy-growth`,
`ns6-no-enemy-memory`, `ns6-no-enemy-hierarchy` — guard `tests/FusionRpg.Guard.Tests/NarrativeNoEnemyGrowthTests.cs`;
R13 rule 5 (no sharing enemy data between players) — `unguardableReason`: the game has no network upload path; a
guard would scan for one that does not exist, so it is a review rule. `ns-world-scope-never-deleted` — see
`spec-story-ledger.md`.

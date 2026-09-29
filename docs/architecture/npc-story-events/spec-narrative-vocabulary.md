# Spec: narrative-vocabulary

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `narrative-vocabulary`, row 1 of the [npc-story-events map](../npc-story-events-map.md) (`:207`), wave 0.
Depends on narrative-seed's registry modules (`storylet-vocab`, `character-vocab`, `token-grammar`,
`names-registry`, `narrative-seed-map.md:204-208`), which author the shared files this module reads. Consumed by
every later module in this program. Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Give the narrative runtime its closed vocabularies and its one balance surface before any engine code reads
them, each owned exactly once:

1. **C# readers for the shared registries** narrative-seed authors under `gk-data/packs/fusion/data/seed/narrative/_registry/` (new):
   roles, choice kinds, consequence kinds, conditions, line contexts, voice registers and host kinds. The seed
   validator and the runtime read **one file each**, which is the `dungeon-registries` precedent
   (`party-dungeon/spec-dungeon-registries.md:14-24`; `gk-core/src/FusionRpg.Core/Dungeon/Registry/DungeonRegistries.cs:5-10`).
2. **Runtime-only closed vocabularies** in C#: character fate, character state, story fact kinds, host clock
   kinds, story scopes, doctrine ids (list owned by `counter-doctrine`).
3. **`gk-core/data/tuning/narrative.v1.json` (new)**: schema, a pure parser that rejects any missing key by name
   (tunables-ssot T5), a hub with no default, and the structural bounds that are deliberately not tunables.

Success looks like: `NarrativeTuningLoader.Parse(json)` with any one key deleted rejects naming that key;
`RoleCatalog.All` and the seedsmith `narrative` adapter report the same members from the same file and a test
asserts they agree; `python gk-core/scripts/audit-magic-numbers.py --domain narrative` reports no bare balance literal.

## Locked anchors

- Map principle 6, the balance surface is data (`npc-story-events-map.md:91-93`); principle 14, closed
  vocabularies are declarations and populations are readings (`:118-120`).
- The registry-file-per-vocabulary shape and the loader pattern: `DispositionCatalog`
  (`gk-core/src/FusionRpg.Core/Dungeon/Registry/DispositionCatalog.cs:4-43`) with a per-file rejection type
  (`DungeonRegistries.cs:23-29`) and kebab-case id checks (`DungeonRegistries.cs:35-60`).
- The tuning loader pattern: `ExpeditionTuningLoader.Parse` throws a named rejection on a missing key
  (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs:26-78`), `ExpeditionTuningHub.Configure` has no default
  (`:85-92`).
- The one relation ladder is the existing disposition registry (`gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`,
  four members `eager, open, wary, hostile`); this module adds **no** second ladder (map locked assumption 5,
  `:145-147`).
- Ownership split (`narrative-seed-map.md:341-342`): narrative-seed owns the seed contracts and registries;
  this program owns runtime loading and `gk-core/data/tuning/narrative.v1.json`.

## Design

### 1. Shared registries (read, never authored here)

Each file lives under `gk-data/packs/fusion/data/seed/narrative/_registry/` (new), authored by the narrative-seed module named. This
module ships one C# catalog per file with `Parse(json)`, `Validate(rows)`, `Configure(rows)`, `All`, `IsKnown`,
`Get`, copying the `DispositionCatalog` shape exactly. A catalog read before `Configure` throws, as
`DispositionCatalog.cs:10-11` does.

| File (new) | Authored by | C# catalog (new) | Members (a declaration, pinned with its reason) |
|---|---|---|---|
| `roles.v1.json` | `character-vocab` | `NarrativeRoleCatalog` | 9: `wanderer, trader, hermit, chronicler, clan-elder, warlord, captive, envoy, companion` (ideal §6.3 table; `narrative-seed-ideal.md:355`) |
| `choice-kinds.v1.json` | `storylet-vocab` | `ChoiceKindCatalog` | 8 families: `interact, leave, use, offer, fight, bring, persuade, threaten`; `use`, `offer`, `bring` carry a parameter (`narrative-seed-ideal.md:310-320`) |
| `consequence-kinds.v1.json` | `storylet-vocab` | `ConsequenceKindCatalog` | 11: `none, loot, encounter, scout` (today's four, `gk-core/src/FusionRpg.Core/Delve/Events/EventCatalog.cs:204`) plus `quest.offer, relation.shift, story.flag, battle.start, scene.play, recruit` (ideal §6.2 table) and `doctrine.setback` (Alignment 2026-09-20: `counter-doctrine` §5, now a seed row, `narrative-seed/spec-storylet-vocab.md` §3.5) — see Contradictions 1. Owner ruling 2026-09-19 (round 3): each row also carries `refForms` and `params` (`narrative-seed/spec-storylet-vocab.md` §3.5), which the catalog exposes so `storylet-contract`'s preflight validates the `{kind, ref, param}` consequence object |
| `conditions.v1.json` | `storylet-vocab` | `ConditionCatalog` | each condition id maps to a `LeafId` or a role requirement; the leaf half is validated against `LeafId` (`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46`). Audit 2026-09-19: members at first ship are `none, danger-band-is, disposition-is, story-flag-set, role-cast` (`narrative-seed/spec-storylet-vocab.md` §3.4); the seed file's `proposedLeaves` block names the runtime leaves by the names `narrative-predicates` §1 fixes. Alignment 2026-09-20: plus `character-state-is`, `lead-level-at-least`, `doctrine-studying`, each with a `usableIn` attribute (`slot`, `eligibility`); the one id → leaf table is `spec-narrative-predicates.md` §5 |
| `role-tags.v1.json` | `storylet-vocab` | `RoleTagCatalog` | Audit 2026-09-19 (was missing): `roleKinds` (`required, optional, forbidden`) and the closed `requireFamilies` (`source`, `side`, `element`, `characterRole`) that `cast-resolver` §3 filters on (`narrative-seed/spec-storylet-vocab.md` §3.6) |
| `line-contexts.v1.json` | `character-vocab` | `LineContextCatalog` | `greet, farewell, thanks, refused, spared, betrayed, joins, taunt, rumor` at first ship (`narrative-seed-ideal.md:359`); final list in `character-vocab` (Alignment 2026-09-20: which adds `doctrine` and the four homecoming contexts `return-won, return-wiped, return-lost, return-quiet` that `sanctum-hub-host` §3 plays) |
| `teaches.v1.json` | `storylet-vocab` (§3.8) | `TeachesCatalog` | Owner ruling 2026-09-20 (story is also the tutorial): the closed mechanics a storylet or spine scene may teach, each with its loop, carriers, storylet requirement and authored teaching sentence; read by `storylet-contract` (`storylet.teaches`), `storylet-selection` §4 and `scene-script-loader` §1 |
| `voice-registers.v1.json` | `character-vocab` | `VoiceRegisterCatalog` | `formal, blunt, playful, grim, sly, gentle` at first ship (`narrative-seed-ideal.md:356`); final list in `character-vocab` |
| `host-kinds.v1.json` | `storylet-vocab` (file); members set by this spec (§2) | `HostKindCatalog` | 16 (§2) |
| ~~`sector-climates.v1.json`~~ | ~~`storylet-vocab` (§3.9)~~ | ~~`SectorClimateCatalog`~~ | Owner ruling 2026-09-20 (round 6): **retired by R20** — world hosts read the sector's own `WorldSector.Climate` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`), so no catalog, file or join test exists; round 5's text (R19: one row per sector type → climate, joined to `SectorTypeCatalog`) is kept only as this trail |

The names registry (`names.en.v1.json`) and the token grammar are read by `narrative-text`, not here, because
they are locale data and text grammar rather than engine vocabularies.

A catalog member list is a **declaration**: its count is asserted with a comment naming the file and the
reason, and a change to it is a reviewed change to the registry file, never a code edit alone.

### 2. Host kinds — members defined by the runtime

Host kinds are a runtime concept (a place that decides *when* to ask, ideal §6.2) that seeds must name in
`hosts[]`. `narrative-seed-map.md:400` waits for *"the runtime [to define] the hosts"*. This spec defines the
members; `storylet-vocab` writes them into the one file both sides read.

| Host kind | Place | Host clock kind | Source |
|---|---|---|---|
| `delve.curio`, `delve.shrine`, `delve.trap`, `delve.wild`, `delve.merchant`, `delve.unknown` | Delve room kinds that hold an event | `delve.room` | ideal §6.6; room kind to event kind today at `gk-core/src/FusionRpg.Core/Delve/Events/EventFilters.cs:16-24` |
| `delve.rest` | the rest ambush pool | `delve.room` | `gk-core/src/FusionRpg.Core/Delve/Events/AmbushDraw.cs:22-30` |
| `world.shrine`, `world.anomaly`, `world.tear`, `world.vault`, `world.market`, `world.wildland` | world sectors holding that slot | `world.turn` | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:7-24` |
| `world.petition` | a held sector's turn | `world.turn` | ideal §6.6 |
| `expedition.return` | an expedition collect | `expedition.collect` | ideal §6.6 |
| `sanctum.hub` | homeworld on return | `sanctum.return` | ideal §6.6 |

Total **16**, pinned because each member is a place that exists in code. A new place is a reviewed change.

### 3. Runtime-only closed vocabularies (C# enums, never in a seed)

| Enum (new) | Members | Count and reason |
|---|---|---|
| `HostClockKind` | `DelveRoom, WorldTurn, ExpeditionCollect, SanctumReturn` | 4 — the game's three clocks plus the homeworld return (map principle 4, `:83-85`); a fourth real-time clock is forbidden, so this set only grows with a new place |
| `StoryScope` | `Save, World` | 2 — ideal §6.7 |
| `CharacterFate` | `Present, Joined, Departed, Fallen` | 4 — ideal §6.3 table. Owner ruling 2026-09-19 (round 4): fate is the character's **own story** fate, written only by a storylet outcome or a join; a world going dormant or frozen never writes `Departed` or `Fallen` — that is `WorldNarrativePhase`, read beside the fate |
| `CharacterState` | `Unmet, Met, Joined, Departed, Fallen` | 5 — `CharacterFate` plus whether a `met` fact exists; derived, never stored. It is the value domain of the `CharacterStateIs` leaf (`narrative-predicates`) |
| `WorldNarrativePhase` | `Live, Dormant, Frozen` | 3 — Owner ruling 2026-09-19 (round 4): the narrative reading of world-continuity's two axes, derived, never stored. `Live` = attention `active` (drawn, written); `Dormant` = `hibernating` or `idle` (kept intact, never drawn, no writes except the facts world-continuity's `CoarseStep` emits); `Frozen` = outcome `fallen` (read-only history; the reserved `world-reclaim` may revive it). There is no "abandoned" member: world-continuity deletes nothing and has no abandon state (`world-continuity-map.md:117`, `:127`, `:274-275`). A new member follows a new world-continuity state, a reviewed change |
| `StoryFactKind` | relation: `met, helped, refused, betrayed, spared`; story: `flag.set, chapter.reached, arc.started`; engine: `storylet.seen, choice.picked`; scene: `scene.acknowledged`; host: `sanctum.returned`; tutorial: `mechanic.first-seen`; reward: `reward.owed, reward.paid`; character: `character.joined, character.departed, character.fell`; quest: `quest.offered, quest.completed, quest.failed, quest.abandoned, quest.expired, quest.progressed`; failure: `sector.lost, delve.wiped, siege.failed` | 27 (Alignment 2026-09-20: 22 plus `sanctum.returned`, `quest.progressed`, `mechanic.first-seen`, `reward.owed`, `reward.paid`, each a reviewed addition filed by its spec) — the map's list (`:210`) plus the facts the ledger needs to derive fate, pins and scene eligibility without a second store. `quest-sources` and `failure-branches` may add members as reviewed changes |
| `DoctrineId` | empty at this module's landing | the list is `counter-doctrine`'s closed reviewed vocabulary (map row 24, `:230`); this module ships the registry file shape `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` (new) and a catalog that accepts an empty list |

Every enum has a stable kebab-case wire id (`StoryFactKindIds.ToId`/`TryParse`), following
`CreaturePersonalityIds.ToId` (`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:30-40`). Stored rows
carry the wire id, never the enum ordinal, so a member appended later never renumbers a saved row.

### 4. `gk-core/data/tuning/narrative.v1.json` (new)

The v1 file is created in this module's build change (a new domain's first version, not an edit of an existing
one); every later change goes through `gk-core/tools/tuning/publish.py narrative ...` (T4). Starting shapes follow the
ideal's §7 anchors; none is an owner question (ideal §7 header).

```jsonc
{
  "schemaVersion": 1,
  "version": 1,
  "_meta": { "owner": "docs/architecture/npc-story-events/spec-narrative-vocabulary.md",
             "rebalance": "Never hand-edit. python gk-core/tools/tuning/publish.py narrative <key>=<value>" },
  "selection": {
    "kindFrequencyBand": { "<storylet kind>": "<dropBand id>" },   // weight read from the item dropBand weight table
    "specificityStepMilli": 1000,                                   // per matched leaf; Valve "most specific wins"
    "unplayedFirst": true
  },
  "firing": {                                                       // per host kind; base + n x step, per-mille
    "world.shrine":   { "baseMilli": 50, "stepMilli": 5 },          // Stellaris 5% + 0.5% per miss
    "...": {},
    "delve.curio":    { "baseMilli": 1000, "stepMilli": 0 }         // the room kind already decided; always fires
  },
  "cooldown": {                                                     // counted on the host's own clock
    "perStorylet": { "world.turn": 10, "expedition.collect": 3, "sanctum.return": 3 },
    "perKind":     { "world.turn": 3,  "expedition.collect": 1, "sanctum.return": 1 }
  },
  "fairness": { "maxNegativeInARow": 1 },
  "relation": {
    "shiftByFactKind": { "met": 0, "helped": -1, "refused": 1, "betrayed": 2, "spared": -1 },
    "baseBandByRole":  { "<role>": "<disposition id>" },
    "baseBandByFactionKind": { "Clan": "wary", "Rival": "hostile", "Zomboss": "hostile", "Wild": "wary" },
    "topBandStoryGated": true
  },
  "casting": {
    "score": { "metBefore": 30, "perBandFriendlier": 10, "notCastRecentlyPulses": 5 },
    "residentChanceMilliBySlot": { "Market": 1000, "Shrine": 600, "Wildland": 300, "Vault": 300, "Anomaly": 200, "Tear": 200 },
    "saveCastPerRole": { "companion": 2 }                          // Audit 2026-09-19: cast-resolver §2's key, now declared here
  },
  "gates": {
    "leadLevel": { "<gateId>": 0 }                                  // Audit 2026-09-19: named level gates for narrative-predicates §1; empty at first ship
  }
}
```

The complete key list, with unit and owner module, is the table below; the loader requires **every** key.

| Key | Unit | Read by | Starting shape and source |
|---|---|---|---|
| `selection.kindFrequencyBand.{kind}` | a `dropBand` id | `storylet-selection` | each kind `staple` except `story` `occasional`; the weight comes from the item registry's `dropBand.weightTable` (1000/300/90/25/7), the one frequency vocabulary (`party-dungeon/spec-event-deck.md:44-47`), never copied |
| `selection.specificityStepMilli` | per-mille per matched leaf, `long` | `storylet-selection` | 1000: a two-leaf match weighs 3000 against 2000 for one leaf (ideal §7 row 4) |
| `selection.unplayedFirst` | bool | `storylet-selection` | true (Hades, ideal §4.1) |
| `firing.{hostKind}.{baseMilli,stepMilli}` | per-mille, `long` | `storylet-selection` | world slot hosts 50/5 (Stellaris); `world.petition` 50/5; every `delve.*` 1000/0; `expedition.return` 1000/0 (its encounter chance lives in `expeditions.v{n}`, map row 20); `sanctum.hub` 1000/0 |
| `cooldown.perStorylet.{clock}` · `cooldown.perKind.{clock}` | host-clock ticks, `long` | `storylet-selection` | CK3 per-event cooldown; Total War 5 turns. `delve.room` is absent on purpose: the Delve's own `events.noRepeatRooms` recent-cells filter is that cooldown (`EventFilters.cs:97-106`) |
| `fairness.maxNegativeInARow` | count | `storylet-selection` | 1 (no two negative storylets in a row on one host) |
| `relation.shiftByFactKind.{kind}` | signed band steps, positive toward `hostile` | `relation-ledger` | the sign convention is `Disposition.Shift`'s (`gk-core/src/FusionRpg.Core/Delve/Wild/Disposition.cs:38-44`) |
| `relation.baseBandByRole.{role}` · `relation.baseBandByFactionKind.{kind}` | disposition id | `relation-ledger` | trader/chronicler/companion `open`; hermit/wanderer/envoy/captive/clan-elder `wary`; warlord `hostile` |
| `relation.topBandStoryGated` | bool | `relation-ledger` | true (Hades' locked heart, ideal §6.4) |
| ~~`relation.joinRankByBand.{band}`~~ | — | — | **Removed — Audit 2026-09-19, applying the owner's answer (a) in `spec-relation-ledger.md`:** every join starts at the contracts program's normal bind loyalty (`ContractPolicy.BindLoyalty`, `gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:84`). A key whose every value must equal the default is not a balance number (tunables-ssot's test: a balance pass may never change it without a new owner ruling and the five actor-layer questions), so it is not in tuning |
| `casting.score.*` | score points, `long` | `cast-resolver` | Wildermyth-style additive scoring (ideal §4.2) |
| `casting.residentChanceMilliBySlot.{slot}` | per-mille, `long` | `cast-resolver` | one trader per market; residents sparse elsewhere |
| `casting.saveCastPerRole.{role}` | count, `long` | `cast-resolver` §2 | `companion` 2. Audit 2026-09-19: the cast-resolver spec added this key "in its build change"; the loader requires every key, so it is declared here |
| `gates.leadLevel.{gateId}` | summoner level, `int` | `narrative-predicates` §1 (`LeadLevelAtLeast`) | empty at first ship. Audit 2026-09-19: a seed cannot carry a number, so a level gate is named in the seed and valued here; a threshold, not a curve |
| `quest.expiry.{clock}` | turns / collects / returns, `long` | `quest-sources` §Data shapes | 20 / 5 / 5 — three of the ideal's ~7-turn threat cycles, a few returns. **Declared at wave 0 (plan §4 D4, published as `v2` 2026-09-22)**, so `quest-sources` reads it instead of adding it |
| `questLog.recentClosed.{clockKind}` | host ticks, `long` | `quest-log-contract` §2 | 3 on every `HostClockKind`: long enough to see an outcome on the next visit, short enough to stay a log of *recent* events |
| `world.offerLifetimeTurns` | turns, `long` | `world-events-host` §Data shapes | 2: the turn it appears and the next |
| `failure.priorityWindow.{clock}` | turns / returns / rooms, `long` | `failure-branches` §Data shapes | 10 / 3 / 20: a loss stays the headline for a stretch, then joins the pool |
| `doctrine.leanThresholdMilli` · `doctrine.studyRatePerTurnMilli` · `doctrine.windowTurns` · `doctrine.cooldownTurns` · `doctrine.raidSetbackMilli` · `doctrine.raidShortenTurns` | per-mille, per-mille per turn, turns, turns, per-mille, turns — all `long` | `counter-doctrine` §6 | 400 / 125 / 10 / 10 / 375 / 3, by principle and the ideal's prior art |
| `readings.minAnswers` · `readings.pickFloorMilli` · `readings.pickCeilMilli` | count, per-mille, per-mille — all `long` | `narrative-readings` §Data shapes | 20 / 50 / 900: report thresholds — they tune what the report flags, not the game |
| `casting.delveResidentsPerRole.{role}` | count, `long` | `delve-host` §Data shapes | trader 1, chronicler 1, captive 2 — a returning party meets the same few faces |

**The union (plan §4 D4).** The seven rows above belong to modules that land later, and their keys are declared
**here**, at wave 0, at the starting value each of those specs chose — because a committed version is never
hand-edited: a later module READS its key, and a change to one is a `gk-core/tools/tuning/publish.py narrative`
`v{n+1}` whose reader switches in the same commit. `v1` (2026-09-22) predates this union and is superseded by
`v2`; the reader takes the highest version.

**Structural bounds, not tunables** (a `const` with a comment saying why; map principle 7, `:94-96`):

| Const | Value | Why it is structural |
|---|---|---|
| `SelectionBounds.SpineBeatsPerPulse` | 1 | "one spine beat per pulse" is the tier rule itself; 2 would be a different design, not a tuning |
| `SelectionBounds.ConversationsPerCharacterPerReturn` | 1 | the Hades rule the hub host is built on (ideal §6.6) |
| `SelectionBounds.MaxChoices` / `MinChoices` | 4 / 2 | the storylet contract (`narrative-seed-ideal.md:337`) |
| `FireChance.CertainMilli` | 1000 | `min(1000, p0 + n × step)` is a probability bound, a bounded ratio (ideal §6.2 item 3) |

The ideal's §7 listed the pacing limits in the tuning file "stated in a comment". The map (`:94-96`) calls them
structural bounds. This spec follows the map: a value whose change would break the design contract rather than
the feel is a `const`. Reported under Contradictions 3.

### 5. Loader and hub

`NarrativeRegistryHub.Configure(string registryDir)` reads every file in §1 and hands each to its catalog;
`NarrativeTuningHub.Configure(NarrativeTuning)` is called at host start beside `ExpeditionTuningHub`. A
missing registry file, a missing tuning key, an unknown `dropBand` id, an unknown disposition id, a `gates.leadLevel` value below 0,
or a `firing`/`cooldown` key naming an unknown host kind or clock is a
`NarrativeVocabularyRejection` naming the file and key — never a default (T5).

These are **static content caches** loaded once. Their full trigger set (DESIGN-GATE §2.16): process start
(Server and Core test fixtures); nothing else, because registries and tuning change only by a new build or a
published `v{n+1}` file, both of which restart the host. No runtime path mutates them, and a test asserts that
`Configure` is the only writer.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| every `*Milli` (firing, specificity step, resident chance) | `long` | `base + n × step` grows with `n` (misses since the last fire); computed `checked` in `long`, compared to an `int` roll widened to `long` |
| cooldown lengths, host-clock ticks | `long` | a count on an unbounded clock (world turns never end, R3) |
| band steps, scores | `int` for band steps (bounded by a 4-member ladder); `long` for summed casting scores | a score sum over many facts is unbounded in principle |
| counts pinned in tests | `int` | closed vocabulary sizes |

No float is needed here; floating point would be legal (owner ruling 2026-09-15) but every quantity is an
integer rate or count.

## SOLID notes

- **S:** one catalog per registry file, one tuning file for the domain; `dungeon-registries` keeps its own
  nine files and the disposition ladder is **read** from it, not re-declared.
- **O:** a new host kind, fact kind or role is a registry row or an enum member plus its test, never a
  parallel list in a consumer.
- **D:** consumers depend on the catalogs and `NarrativeTuningHub`, never on JSON paths.
- No second vocabulary: `CreaturePersonality` (`ContractPolicy.cs:18`) is the personality vocabulary and the
  disposition registry is the relation ladder; this module declares neither.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Vocabulary/NarrativeRoleCatalog.cs','tests/FusionRpg.Core.Tests/Narrative/Vocabulary/NarrativeVocabularyTests.cs','gk-core/data/tuning/narrative.v1.json') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Vocabulary"
python scripts\audit-magic-numbers.py --domain narrative ; python scripts\audit-overflow.py
```

`gk-core/src/FusionRpg.Core/**` maps to `core-fallback` today (`gk-core/scripts/verification-boundaries.v1.json`).
`gk-core/data/tuning/narrative.v1.json` and `gk-data/packs/fusion/data/seed/narrative/**` have **no** mapping, so `verify-change.ps1` throws
`VERIFICATION BOUNDARY MISSING` for them (`scripts/verify-change.ps1:95`). This module's build change adds a
focused boundary `core-narrative` covering `gk-core/src/FusionRpg.Core/Narrative/**`, `gk-core/tests/FusionRpg.Core.Tests/Narrative/**`,
`data/tuning/narrative.v*.json` and `gk-data/packs/fusion/data/seed/narrative/_registry/**`, verified by
`python gk-core/scripts/guard-verification-boundaries.py`.

## Structure

```
gk-core/data/tuning/narrative.v1.json                                   (new)
gk-core/src/FusionRpg.Core/Narrative/Vocabulary/                        (new)
  NarrativeRegistryHub.cs · NarrativeVocabularyRejection.cs
  NarrativeRoleCatalog.cs · ChoiceKindCatalog.cs · ConsequenceKindCatalog.cs · ConditionCatalog.cs
  LineContextCatalog.cs · VoiceRegisterCatalog.cs · HostKindCatalog.cs · DoctrineCatalog.cs
  RoleTagCatalog.cs            (Audit 2026-09-19)
  NarrativeEnums.cs            HostClockKind, StoryScope, CharacterFate, CharacterState, WorldNarrativePhase, StoryFactKind + wire ids
  NarrativeTuning.cs           record tree + NarrativeTuningLoader.Parse + NarrativeTuningHub
  SelectionBounds.cs           the structural consts, each commented
tests/FusionRpg.Core.Tests/Narrative/Vocabulary/NarrativeVocabularyTests.cs     (new)
gk-core/scripts/verification-boundaries.v1.json                          (edited: core-narrative boundary)
```

## Testing strategy

- **Every missing tuning key rejects by name:** for each leaf path in the committed `narrative.v1.json`, delete it
  and assert `NarrativeTuningLoader.Parse` throws naming that path (a loop over the file's own keys, so a new key
  is covered without editing the test).
- **Cross-reference rejections:** an unknown `dropBand` id, disposition id, host kind, or
  clock each reject naming the key; a leftover `relation.joinRankByBand` key is an unknown key and rejects (Audit
  2026-09-19).
- **One file, two readers:** `NarrativeRoleCatalog.All` equals the member list the seedsmith `narrative` adapter
  loads from the same file (a Core test reads the file directly; the seedsmith pytest reads it on its side). The
  test compares against the **file**, never a literal list.
- **Declared counts:** host kinds 16, `HostClockKind` 4, `StoryScope` 2, `CharacterFate` 4, `CharacterState` 5,
  `WorldNarrativePhase` 3 (Owner ruling 2026-09-19 (round 4)), `StoryFactKind` 27 (Alignment 2026-09-20: 22 plus the five reviewed additions in §3), each with a comment naming why it is closed. Registry members authored by narrative-seed
  (roles, choice kinds, consequence kinds, voices, contexts) are asserted equal to their file, not pinned here,
  because narrative-seed's own spec pins them.
- **Wire-id round trip:** every enum member `ToId` then `TryParse` returns itself; an unknown id fails.
- **No population is asserted:** no test counts storylets, characters or seeds.
- **Configure-only writer:** reading a catalog before `Configure` throws; a reflection test finds no public
  setter other than `Configure`.

## Success criteria

1. Every missing-key and cross-reference rejection has a named test. 2. Catalogs and the seedsmith adapter agree
from one file per vocabulary. 3. `audit-magic-numbers.py --domain narrative` reports no balance literal in
`Narrative/Vocabulary/`. 4. The `core-narrative` boundary is registered and `verify-change.ps1` selects it for
the paths above. 5. No member list duplicates a narrative-seed or dungeon registry.

## Boundaries

- **Always:** read shared vocabularies from narrative-seed's files; reject, never default; wire ids in storage.
- **Ask first:** a new `HostClockKind` (it is a new clock, principle 4); adding a relation band.
- **Never:** author a shared registry file here; a second personality or relation vocabulary; a pacing limit in
  tuning that would break the design if changed; a real-time clock.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `NarrativeRoleCatalog`, `HostKindCatalog.ClockOf(hostKind)`, `ChoiceKindCatalog`, `ConsequenceKindCatalog`, `ConditionCatalog` | `storylet-contract`, `cast-resolver`, `storylet-selection`, every host |
| `StoryFactKind`, `StoryScope`, `CharacterFate`, `CharacterState`, `HostClockKind` + wire ids | `story-ledger`, `relation-ledger`, `character-registry`, `narrative-predicates` |
| `WorldNarrativePhase` + `WorldNarrativePhase.Of(attention, outcome)` (pure; Owner ruling 2026-09-19 (round 4)) | `story-ledger`, `relation-ledger`, `character-registry`, `cast-resolver`, `storylet-selection`, every world host |
| `RoleTagCatalog` (Audit 2026-09-19) | `storylet-contract`, `cast-resolver` |
| `NarrativeTuningHub.Tuning` | `storylet-selection`, `relation-ledger`, `cast-resolver` |
| `SelectionBounds` | `storylet-selection`, `sanctum-hub-host` |

## Contradictions found (report; not fixed here)

1. **`battle.start` is missing from the seed-side consequence list.** *Resolved — Audit 2026-09-19:*
   `narrative-seed/spec-storylet-vocab.md` §3.5 now lists `battle.start` (`ref: null`, `params: none`); the text below
   is kept for the trail. `narrative-seed-ideal.md:329-331` and
   `narrative-seed-map.md:204` list five new consequence kinds without `battle.start`; the runtime ideal §6.2
   table and `npc-story-events-map.md:221` route six, including `battle.start` to `BattleRequest`. The existing
   `encounter` consequence is the Delve's `Encounter.Build` path, not a world `BattleRequest`, so it does not
   cover it. One file serves both sides, so `storylet-vocab` must add `battle.start`; filed as a propagation on
   `narrative-seed-map.md`.
2. **Who defines host kinds.** `npc-story-events-map.md:207` names host kinds a runtime-only vocabulary;
   `narrative-seed-map.md:204` puts host kinds in `storylet-vocab`'s registry. Resolved here without a new rule:
   one file, authored by `storylet-vocab`, whose members this spec defines (§2), as `narrative-seed-map.md:400`
   already anticipates.
3. **Pacing limits: tuning or const.** Ideal §7 (`npc-story-events-ideal.md:601`) puts them in the tuning file;
   the map (`npc-story-events-map.md:94-96`) calls them structural bounds. This spec follows the map (§4).

## Open questions

None for the owner. Starting values are decided by principle (ideal §7).

## Design-gate checklist

```
[x] Subsystems: tunables, registries, narrative seeds (consumer), relation ladder (reader).
[x] Session boundary: tasks/sessions/narrative-programs-spec2-20260919.json lists docs/architecture/npc-story-events/**.
[x] Read this session: the map, the ideal (§0, §6, §7, §10, §11), narrative-seed ideal §6.2-§6.5b and map,
    DESIGN-GATE §1 rows and §2, spec-dungeon-registries.md (shape), spec-event-deck.md (shape).
[x] decisions.md: no lock on a narrative vocabulary; NS1-NS8 are drafted in the map, not appended.
[x] Every code claim cites file:line opened this session.
[x] No population pinned; closed vocabularies pinned with reasons.
[x] Caches: static content, full trigger set listed (process start only).
[x] Actor numbers: none produced or consumed.
[x] No parallel path: one file per vocabulary.
[ ] Registry row: none needed; no new guard rule here. (Audit 2026-09-19: proposed row below.)
```

## Standards audit (2026-09-19)

Independent adversarial audit against DESIGN-GATE §1/§2/§3/§5, AGENTS.md/CLAUDE.md hard rules, tunables-ssot,
validation-ssot, ideal §10 and the round-3/round-4 owner rulings, and the seed-side specs this module loads.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | `relation.joinRankByBand` shipped `eager → Trusted, open → Sworn, wary → Bound`, contradicting the owner's answer (a) in `spec-relation-ledger.md` (every join starts at the normal bind rank). Those ranks feed `ContractPolicy.RankBonusMilli` through `StarLoyaltySubsystem` — a relationship changing an actor number through a tuning publish, with no five-question answer (principle 9; DESIGN-GATE actor-layer row) | **Fixed:** key removed; joins use `ContractPolicy.BindLoyalty`; a leftover key rejects |
| 2 | high | Round-4 owner ruling: world scope is never deleted and has no "abandoned" state; no runtime vocabulary expressed live / dormant / frozen | **Fixed:** `WorldNarrativePhase {Live, Dormant, Frozen}` (3) added, derived, never stored; `CharacterFate` stated as story fate only |
| 3 | medium | `casting.saveCastPerRole.companion` was added by `cast-resolver` "in its build change" but the loader requires every key — the table here was the SSOT and lacked it | **Fixed:** declared in §4 |
| 4 | medium | No reader for `role-tags.v1.json`, which `cast-resolver` filters on (storylet-vocab §3.6) — a consumer would have re-read the file privately | **Fixed:** `RoleTagCatalog` |
| 5 | medium | `LeadLevelAtLeast` (narrative-predicates) needs a number no seed may carry | **Fixed:** named gates `gates.leadLevel.{gateId}` in tuning |
| 6 | low | Contradiction 1 (`battle.start`) was stale: storylet-vocab §3.5 now carries it | **Fixed:** marked resolved |
| 7 | low | Map line citations were one line early after a map insert (`:206`, `:209`, `:229`, `:220`) | **Fixed** |
| 8 | low | `conditions.v1.json`'s proposed leaf names (`RelationBandIs`, `StoryFlagIs`) differ from `narrative-predicates`' (`RelationBandAtMost`, `StoryFlagSet`); storylet-vocab's own test asserts the names | **Deferred:** propagation owed to `narrative-seed/spec-storylet-vocab.md` §3.4 (outside this fence); the runtime owns `LeafId` (`narrative-seed-map.md:342`) |

**Proposed enforcement-registry row** (not added here; shared file): `narrative-tuning-no-default` — every
`narrative.v{n}.json` key required, no built-in default; guard `NarrativeVocabularyTests` (missing-key loop).
**Verification-boundary ask:** `core-narrative` covering `gk-core/src/FusionRpg.Core/Narrative/**`,
`gk-core/tests/FusionRpg.Core.Tests/Narrative/**`, `data/tuning/narrative.v*.json`, `data/tuning/narrative-cast-catalog.v*.json`,
`gk-data/packs/fusion/data/seed/narrative/_registry/**` (today `verify-change.ps1` throws `VERIFICATION BOUNDARY MISSING` for the data paths).

## Cross-lane alignment (2026-09-20)

- Alignment 2026-09-20: §1's registry table follows the seed side — `conditions.v1.json` gains three ids and
  `usableIn`, `consequence-kinds.v1.json` gains `doctrine.setback` (11), `line-contexts.v1.json` gains the four
  `return-*` contexts, and the new `teaches.v1.json` gets `TeachesCatalog`.
- §3 `StoryFactKind` grows 22 → 27, each a reviewed addition filed by a sibling spec: `sanctum.returned`
  (`spec-sanctum-hub-host.md` §1), `quest.progressed` (`spec-quest-sources.md` §3.3), `mechanic.first-seen` (Owner
  ruling 2026-09-20, story is also the tutorial; `spec-storylet-selection.md` §4) and `reward.owed`, `reward.paid`
  (Owner ruling 2026-09-20, rewards come out of the host budget; `spec-outcome-routing.md` §3). Wire ids are appended,
  so no stored row renumbers.

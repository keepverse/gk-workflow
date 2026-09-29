# Spec: delve-live-start

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `delve-live-start`, row 28 of the [npc-story-events map](../npc-story-events-map.md), **wave 1**. Created by
**Owner ruling 2026-09-19 (round 3): npc-story-events absorbs the Delve live-path wiring** from party-dungeon. It is a
prerequisite of `delve-live-rooms` (row 29) and of `delve-host` (row 17), and is placed before both in the build
order. Depends on `host-content-theta` for the one `ParentWorldTerms` producer (Audit 2026-09-19: was "no
npc-story-events module"; §3). Transfer note: the top of `tasks/party-dungeon-todo.md`.

## Objective

Make a real delve **startable** in production, using only machinery party-dungeon already built:

1. **Import the domain corpus at boot.** `ImportDungeonDomains` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs:225`)
   has no production caller, so `dungeon_domain` is always empty and `POST /api/delve/start` refuses before
   `CreateDelve` (`gk-core/src/FusionRpg.Server/DelveEndpoints.cs:175-176`).
2. **Let `/start` reach `CreateDelve`.** Five delegates of the live start path throw `NotImplementedException`
   today (`DelveEndpoints.cs:229`, `:236`, `:245`, `:247`, `:249`): `StalenessFor`, `ComposeRungs`,
   `ProvisioningPriceFor`, `ContentTermsJsonFor`, `RollAndPreflight`.
3. **Offer the Delve's quests at `CreateDelve`** and expose them. `WriteQuestOffer`
   (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:517`) is called only by tests, and no route serves the tracker.

Success looks like: with the committed domain corpus, a server boot imports every domain that passes
`DomainPreflight` (or records why none did, without failing the boot); `POST /api/delve/start` with a real player and
domain creates a delve row with `content_terms_json`, a first decision and a persisted quest offer; `GET
/api/delve/{delveId}/quests` returns the offer as `QuestDto`s — all through real routes against real rows.

## Locked anchors

- **Party-dungeon designed this path; this module wires it.** The entry orchestration is
  `docs/architecture/party-dungeon/spec-domain-catalog.md` §6 (refusal order, frozen parent terms, one transaction)
  and `DelveStart.Run` implements it (`gk-core/src/FusionRpg.Core/Delve/Domains/DelveStart.cs:111`). The quest offer is
  `spec-delve-quests.md` §2 (2–3 offered at entry on `dungeon:quest`). Nothing here re-decides a rule.
- **The boot-import precedent**: content boot runs `SeedImportRunner.RunSelfHealing` and, independently, the
  passive-tree catalog through `PassiveTreeImportRunner.RunSelfHealing` — each *"never throws"* and never gates the
  other (`gk-core/src/FusionRpg.Server/Program.cs:777`, `:833`; runner at `gk-core/src/FusionRpg.Data/Seed/PassiveTreeImportRunner.cs:61`).
- **The import is validate-first, all-or-nothing** (`RpgStore.Domains.cs:225-240`, D4.16's own design); real
  content refusing today is the correct verdict, not a defect (party-dungeon's D4.17 rows).
- **RPG Server debug rule** (`docs/contributing/live-probe-standard.md`): the live proof uses real routes and real
  rows; nothing is fabricated.
- **Standalone-first**: the Delve runs with the game closed (party-dungeon map, *What it is not*).

## Design

### 1. Boot import — `DungeonDomainImportRunner`

`DungeonDomainImportRunner.RunSelfHealing(store, searchStartDir)` (new, `gk-core/src/FusionRpg.Data/Seed/`) — the
`PassiveTreeImportRunner` shape:

- finds `gk-data/packs/fusion/data/seed/dungeon/` with `SeedImportRunner.FindUp` (the helper the passive-tree runner uses,
  `PassiveTreeImportRunner.cs:68`);
- reads domains, room palettes, quest pools, loot bindings and provenance through the built readers
  (`DomainSeedFile.LoadAll`, `LoadRoomPalettes`, `LoadQuestPools`, `LoadLootBindings`, `LoadProvenanceJson`,
  `gk-core/src/FusionRpg.Core/Delve/Domains/DomainSeedFile.cs:23`, `:57`, `:78`, `:100`, `:131`);
- composes `DomainPreflightInputs` from the bridges party-dungeon built (graph, encounter, quest) and calls
  `ImportDungeonDomains` once;
- **never throws**: a refusal or a missing tree logs its reason and leaves `dungeon_domain` as it was, exactly like
  the two runners beside it. `Program.cs` calls it after `PassiveTreeImportRunner` and prints the outcome in the same
  `[content]` voice.

Only domains that pass preflight reach the table; which ones do today is party-dungeon's content state (D4.17's
rows, D4.30's corpus), a reading this module prints, never a number it asserts.

### 2. The five `/start` delegates

Each delegate is filled from a built piece, never a new rule. Only the live start path (`BuildDelveStartLive`,
`DelveEndpoints.cs:223-249`) is in scope; the three display delegates of `GET /domains` (`RungLabelFor`,
`BossDisplayNameFor`, `ProvisionableFor`, `:213-219`) stay party-dungeon's (D4.19; `spec-delve-stage.md` §18 ask
6) and do not block `/start`.

| Delegate (today) | Filled from | Spec rule |
|---|---|---|
| `StalenessFor` (`:229`) | the stored `validated_json` parsed to `DomainValidatedFacts` and compared to the live facts through `DomainStaleness.Of` (`gk-core/src/FusionRpg.Core/Delve/Domains/DomainStaleness.cs:29`) | domain-catalog §6 refusal 1 (`domain.stale`) |
| `ComposeRungs` (`:236`) | `RungOffer.For` over the domain row, dungeon tuning and the frozen `ParentWorldTerms` of §3 | domain-catalog §6 refusal 2 |
| `ProvisioningPriceFor` (`:245`) | `DelvePrices` at the composed row-0 Θ, from the bank | domain-catalog §6 refusal 4 |
| `ContentTermsJsonFor` (`:247`) | `ParentWorldTerms` (§3) serialized once | domain-catalog §6 step 5 |
| `RollAndPreflight` (`:249`) | `DomainAnchorBuilder.From(domain, roomsById, palette)` (`gk-core/src/FusionRpg.Core/Delve/Roll/RoomPaletteSeedFile.cs:57-66`), then `DelveGraphRoll.Roll` and `ObjectPreflight.Run` on this graph | domain-catalog §6 step 6 |

### 3. Parent terms — read once, frozen

`ParentWorldTerms(WorldTier, ZombossLevel, RealmsAdvanced)` (`gk-core/src/FusionRpg.Core/Delve/Difficulty/RoomTheta.cs:12`)
is read **once** at start and frozen on the header as `content_terms_json`: *"Sanctum entry reads the player's
terms, a map-door entry the parent world's"* (`spec-domain-catalog.md` §6 step 5). This module adds one read,
`DelveParentTerms.For(playerId, parentWorldId?)` (Server), which only **chooses** the world (the player's sanctum
context or the parent world) and calls `ParentWorldTermsSource.For` (`spec-host-content-theta.md` §2), the one place a
`ParentWorldTerms` is built from state; it constructs and composes nothing. Audit 2026-09-19: the first draft read "the
power program's content-side inputs" itself — a second producer beside `host-content-theta`'s, which that spec's
one-producer scan forbids. `RealmsAdvanced` is whatever that program supplies — today `0`
(`gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs:49`), with world-continuity's recommendation to source it
from worlds won (`world-continuity/spec-world-victory.md` §5) left to the power program.

### 4. Quests at entry and the tracker route

- **Offer.** Inside `DelveStart`'s one transaction (domain-catalog §6 step 7), draw the offer with
  `QuestOffer.Draw` (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestOffer.cs:107`) over the domain's quest pool and persist it
  with `WriteQuestOffer`'s unlocked variant. A replayed start (same `correlationId`) returns the stored offer and
  draws nothing — *"the stored offer is truth"* (party-dungeon D4.14's own round-trip test).
- **Tracker.** `GET /api/delve/{delveId:long}/quests?playerId=` returns `ReadQuestOffer(delveId)`
  (`RpgStore.Delve.cs:535`) projected through `QuestDtoProjection.Project` (`QuestDto`, no `Θ`, rung id or
  `PartyIndex`, `gk-core/src/FusionRpg.Core/Delve/Quests/QuestDto.cs:3-8`). Ownership is checked like `HandleGetDelve`
  (`DelveEndpoints.cs:119`).
- **Not here:** computing verdicts and calling `WriteQuestVerdicts` at `CloseDelve` stays party-dungeon's (the
  half of D4.14 not transferred): it needs a live `DelveReport` whose `Kills` slice has no persisted source yet, and
  `CloseDelve` itself has no production caller (`RpgStore.Delve.cs:762`; party-dungeon's extraction route).
  `quest-log-contract` shows the Delve's open quests from the stored offer meanwhile.

### 5. Live proof

After the full suite (AGENTS.md verification boundary, point 3), RPG Server scope only: boot the server against the
committed corpus and read `[content]`'s domain line; `GET /api/delve/domains/{playerId}` for a real player lists the
imported domains (with display fields still `Pending` where party-dungeon's D4.19 delegates are unbuilt — a reading,
not a failure of this module); `POST /api/delve/start` with a real roster creates a delve; `GET /api/delve/{id}` and
`GET /api/delve/{id}/quests` read it back. No `debug.*` command, no hand-inserted `dungeon_domain` row.

## Data shapes

No new table. `dungeon_domain`/`dungeon_domain_pool` (D4.16), `rpg_delves.content_terms_json` and `quests_json`
(`RpgStore.Delve.cs:107` for `quests_json`) are party-dungeon's existing columns; this module writes them through existing store calls.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| Θ inputs (`WorldTier`, `ZombossLevel`, `RealmsAdvanced`) | `int`, as `ParentWorldTerms` declares | passed through, never computed here |
| provisioning price | `long` | `DelvePrices`' own type; a soul amount |
| quest `need`/`have` | `int` in `QuestJsonRow` | the Delve's existing column shape (`RpgStore.Delve.cs:511-517`) |

## SOLID notes

- **S:** wiring only — every rule is party-dungeon's built code; this module adds callers, one boot runner and one
  read (`DelveParentTerms`).
- **O:** a new domain is seed data; the runner does not change.
- **D:** the endpoint depends on `DelveStart.Run`'s delegate record, filled by store reads.
- No second start path, no second import, no second quest catalog.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Data/Seed/DungeonDomainImportRunner.cs','gk-core/src/FusionRpg.Server/DelveEndpoints.cs','gk-core/src/FusionRpg.Server/Program.cs','gk-core/tests/FusionRpg.Server.Tests/DelveDomainsAndStartEndpointsTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~DelveDomainsAndStart|FullyQualifiedName~DelveQuestTracker"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~DungeonDomainImportRunner|FullyQualifiedName~Delve"
python gk-core/scripts/guard-dal.py ; python gk-core/scripts/guard-test-substrate.py
```

## Structure

```
src/FusionRpg.Data/Seed/DungeonDomainImportRunner.cs                 (new: boot import, never throws)
gk-core/src/FusionRpg.Server/Program.cs                                      (edited: one call after PassiveTreeImportRunner)
gk-core/src/FusionRpg.Server/DelveEndpoints.cs                               (edited: five start delegates; GET {delveId}/quests)
src/FusionRpg.Server/Delve/DelveParentTerms.cs                       (new: the frozen terms read)
tests/FusionRpg.Data.Tests/Seed/DungeonDomainImportRunnerTests.cs    (new; in-memory store, fixture tree)
gk-core/tests/FusionRpg.Server.Tests/DelveDomainsAndStartEndpointsTests.cs   (edited: start reaches CreateDelve)
tests/FusionRpg.Server.Tests/DelveQuestTrackerEndpointTests.cs       (new)
```

## Testing strategy

Game closed; in-memory store (`DataTestStore.Create()`); a fixture seed tree for the runner.

- **Boot import:** a fixture tree of passing domains imports them; a tree with one refusing domain imports none and
  the runner returns the refusal without throwing; a missing tree returns `SeedTreeNotFound`-style status; running
  twice is idempotent (revision bump only on change, D4.16's upsert).
- **Start reaches `CreateDelve`:** against an imported fixture domain, `HandleStart` returns `{delveId, worldId}` and
  the header carries `content_terms_json`, the first decision and a non-empty `quests_json`; a replay returns the
  same delve and the same offer.
- **Each delegate:** a stale fixture refuses `domain.stale`; an unoffered rung refuses `rung.not-offered`; an
  unaffordable provisioning refuses `delve.souls-insufficient` — each through the real handler, not the delegate
  alone.
- **Tracker:** the route returns the stored offer as `QuestDto`s; another player's delve is refused; the reflection
  scan for engine words over `QuestDto` stays green.
- **No population:** tests never count the committed domain corpus.

## Success criteria

1. A boot imports the passing domains without ever failing the boot. 2. `/start` reaches `CreateDelve` through the
five filled delegates. 3. A delve's quests are offered at entry and served by a route. 4. The live proof in §5 passes
through real routes against real rows.

## Boundaries

- **Always:** reuse party-dungeon's built rules; never throw from boot; one transaction per start.
- **Ask first:** a rule change in `DelveStart.Run` or `DomainPreflight`; a new column.
- **Never:** hand-insert a domain row as evidence; build `GET /domains`' display delegates here (D4.19's); write quest
  verdicts at `CloseDelve` (party-dungeon's); change domain content (party-dungeon's corpus, D4.30).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| a real delve row after `POST /api/delve/start` | `delve-live-rooms`, `delve-host` (G5), `quest-log-contract` |
| `GET /api/delve/{delveId}/quests` | `delve-stage`'s quest tracker (FE), `quest-log-layer` |
| `DungeonDomainImportRunner` | server boot |

## Transferred from party-dungeon (Owner ruling 2026-09-19 (round 3))

| party-dungeon task | What moves here | What stays with party-dungeon |
|---|---|---|
| **D4.16** (checked done; its production caller was never built) | the boot caller of `ImportDungeonDomains` (§1) | the import arm itself and its tests |
| **D4.22** (checked partial) | the five live-start delegates (§2) | the three `GET /domains` display delegates (D4.19) |
| **D4.14** (open) | the offer at `CreateDelve` and the tracker route (§4) | verdicts at `CloseDelve` and the live `DelveReport` they need |

## Contradictions found (report; not fixed here)

1. **"The Delve's live path" never included extraction.** Every earlier list of the live path (the npc-story-events
   map's cross-program table, narrative-seed map §7) names import, room marking, the draw, the answer route and the
   quest offer, but not the extraction route: `CloseDelve` (`RpgStore.Delve.cs:762`) has no production caller either
   (party-dungeon's D3.11/D3.16/D3.17 notes: *"no close/extraction/room-clear route at all"*). This ruling's transfer
   is read as the listed wiring; extraction and room-clear stay party-dungeon's. A delve started here can be played
   room by room (`delve-live-rooms`) but not yet extracted.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: the Delve (start path, domain import, quests), server boot, live probe.
[x] Session boundary: this change is docs only, under the narrative spec session's record.
[x] Read this session: npc-story-events map, party-dungeon map, tasks/party-dungeon-todo.md entries D3.3, D3.5, D3.9,
    D4.14, D4.16, D4.17 (row notes), D4.19, D4.21, D4.22, D4.30; spec-domain-catalog.md §6; code: DelveEndpoints.cs,
    RpgStore.Domains.cs, RpgStore.Delve.cs, DomainSeedFile.cs, DomainStaleness.cs, DelveStart.cs, RoomTheta.cs,
    RoomPaletteSeedFile.cs, QuestOffer.cs, Program.cs content boot, PassiveTreeImportRunner.cs,
    ServerPowerIndexProvider.cs.
[x] Every claim cites file:line; the no-caller claims re-checked by grep over src/.
[x] No population pinned. No cache. No actor number: Θ terms are passed through.
[x] No parallel path: one import, one start orchestration, one quest catalog.
[ ] Registry row: none; the boot runner's never-throw rule is tested locally.
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | `DelveParentTerms.For` read parent terms directly — a second `ParentWorldTerms` producer beside `host-content-theta`'s `ParentWorldTermsSource` (SOLID S/D; that spec's source scan would fail) | **Fixed:** delegates; dependency on `host-content-theta` stated here and in map row 28 |
| 2 | low | Citations re-checked against code this audit: the five throwing delegates at `DelveEndpoints.cs:229`, `:236`, `:245`, `:247`, `:249`; `/start` returning before `CreateDelve` (`:175-176`); `DelvePrices.Provisioning` exists (`gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:103`) | no change |
| 3 | low | `SealSeed` is `Random.Shared` today (`DelveEndpoints.cs:248`) — a run seed sealed once and stored, not a narrative roll, so map principle 12 is not engaged; every draw derives from the stored seed on named streams | no change (party-dungeon's) |

Round-4 ruling (world scope): not engaged — a delve row is delve-scoped, not world-scoped narrative state.

Checked and clean: wiring only (no rule re-decided), boot import never throws and never gates another runner (the
`PassiveTreeImportRunner` precedent), the live proof is RPG Server scope through real routes against real rows (no
`debug.*`, no hand-inserted domain row — live-probe standard), store tests in memory, no population pin, SQL via
existing store calls only.

**Proposed enforcement-registry row:** `ns-delve-boot-import-never-throws` — `unguardableReason`: a behavioural
property of one runner, covered by `DungeonDomainImportRunnerTests`; a static guard cannot see "never throws".
**Verification-boundary ask:** map `src/FusionRpg.Data/Seed/DungeonDomainImportRunner.cs` and
`src/FusionRpg.Server/Delve/**` to a focused delve boundary.

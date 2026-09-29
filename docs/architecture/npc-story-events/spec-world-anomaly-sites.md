# Spec: world-anomaly-sites

Status: **DRAFT for owner review, 2026-09-20. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Owner ruling 2026-09-20 (round 6): **R21 — add the Anomaly slot to some sector types, pulled into npc-story-events.**
Module `world-anomaly-sites`, row 31 of the [npc-story-events map](../npc-story-events-map.md), wave 1. A
**prerequisite** of `world-events-host` (row 18: the `world.anomaly` host) and `counter-doctrine` (row 24: study sites
are `Anomaly` and `Vault`). **Reviewed with world-map-program**, which owns `SectorTypeCatalog`, the world templates and
their goldens, and with world-continuity, which owns template versions (`world-creation`). This spec edits no world-map
file; the world-map side records the change in its own docs when the build lands. Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

> **Owner ruling 2026-09-20 (R23): add Vault placements in the same new template versions.** No shipped
> template places a `Vault` slot, so doctrine study sites could only be Anomalies. The same new template
> versions that place the three unguarded Anomaly slots also place a few **guarded** Vault slots (a guard
> wave, as vault slots use today), on sector types that already allow `vault` (verify each in
> `SectorTypeCatalog.cs` before placing; no allow-list change is needed where it already allows it). New
> worlds only, the same template-version gate as the anomalies (it waits on world-continuity's
> `WorldCreation.Rebuild`). Study sites then use Anomaly and Vault ground. The plan phase picks the exact
> sectors by the same fit-and-spread rule as §1 and adds a test that each new template version places at
> least one Vault reachable from the start sector.

Make `Anomaly` a slot a real world can hold, in **new worlds only**, so the `world.anomaly` storylet host and the
doctrine study sites exist somewhere a player can reach.

Success looks like: with the game closed, a newly created `first-light` world (current template version) has an
`anomaly` slot on its nexus and its barren sector, a new `two-hearths` world has one on a barren corridor, both
validate, and a `world.anomaly` fixture storylet fires there; a world created before this change rebuilds and replays
byte-identically.

## Why a module of its own (not folded into `world-claim-loot`)

`world-claim-loot` is a mint in the End-Turn commit path, reviewed with the item program; this is world **content**
(a catalog allow-list and template slots), reviewed with world-map and gated by world-continuity's template-version
rule. They share no file, no test and no dependency, and neither needs the other to ship. One module each keeps each
review to one owner (SOLID S); folding them would make a loot change re-review map content.

## Locked anchors (verified)

- **Nothing can hold an anomaly today.** `SlotTypeCatalog` declares `anomaly` (`Kind = SlotKind.Anomaly`, not
  buildable, no yield — `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:76`), but no `SectorTypeDef.AllowedSlotTypes` lists
  it (`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:55-102`) and no template places one
  (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:86-160`, `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs`).
  Neither template places a `vault` either; the only fixtures are the homeworld markets
  (`WorldTemplateCatalog.cs:147`, `WorldTemplateCatalog.TwoHearths.cs:47`).
- **The allow-list is validation only.** Its one reader is `WorldValidation`, which refuses a slot its sector type does
  not allow (`gk-core/src/FusionRpg.Core/World/WorldValidation.cs:246-248`). Widening a list therefore changes no existing world;
  it only permits a template to place the slot.
- **Templates are authored code, rebuilt on replay.** `WorldTemplateCatalog.Build(templateId, seed, worldId)`
  (`WorldTemplateCatalog.cs:39-44`) builds a world; replay rebuilds from it (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:769`).
  Editing a template's slots in place would change every existing world's replay.
- **The template-version rule** (world-continuity `world-creation`, `docs/architecture/world-continuity/spec-world-creation.md`
  §5 rule 1): *"Every content edit to a shipped template is a new template version under the per-world stamp, with its
  golden re-bless in the same commit; replay rebuilds from the stamped version … A legacy world rebuilds its old
  version."* Rule 2: the production path creates the current version only.
- **AI valuation already prices it**: `SlotValueCatalog` gives `SlotKind.Anomaly` 200 (`gk-core/src/FusionRpg.Core/World/Ai/SlotValueCatalog.cs:47`),
  summed per believed slot by `ValueMap` (`gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:140-150`). No new number.
- **An unguarded slot never blocks a claim**: a slot's `GuardState` defaults to `Cleared` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:113`),
  and a claim waits only on `Intact` guards (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:88-93`).

## Design

### 1. Which sector types gain `anomaly` — by fit and spread

An anomaly is a **rift phenomenon**: a place where the Fracture is visibly unstable, which the Rotwright studies and the
player can raid. **Fit:** a type gains it only if the Fracture itself defines the type. **Spread:** at least one type
present in each shipped template, and at least one type that can host a Seat and one that cannot, so study sites sit both
on contested ground and on no-man's-land.

| Sector type | Gains `anomaly`? | Reason |
|---|---|---|
| `storm` | **yes** | the Rift Storm is the Fracture at its most active; it already allows a `tear` (`SectorTypeCatalog.cs:83`) |
| `nexus` | **yes** | where clusters join, the rift folds; a chokepoint (`SectorTypeFlags.Nexus`) makes a study-site raid a contested choice; can host a Seat |
| `barren` | **yes** | ground the Fracture stripped; `NoBase`, so an anomaly there is a site to raid, never to settle; the only fitting type present in **both** shipped templates (`WorldTemplateCatalog.cs:90`, `WorldTemplateCatalog.TwoHearths.cs:97-186`) |
| `homeworld` | no | the one sector the Fracture never touched (`SectorTypeFlags.Home`) |
| `stable`, `rich` | no | settled and economic ground; a study site there would read as a resource and move AI valuation of the richest ground |
| `warcamp` | no | an AI seat; a raid there is already a siege |
| `boss-lair` | no | already allows a `vault`, the other study site (`SectorTypeCatalog.cs:100`) |

### 2. Where the slots go — new template versions only

Under world-creation's rule 1, each template gets a **new version**; the old version stays buildable for legacy worlds.

| Template (new version) | Sector | Change |
|---|---|---|
| `first-light` | `black-gate` (nexus) | append `anomaly` at the next slot index (3), unguarded |
| `first-light` | `ash-waste` (barren) | append `anomaly` at index 3, unguarded |
| `two-hearths` | `corridor-4` (barren, danger 4, the deepest corridor, `WorldTemplateCatalog.TwoHearths.cs:130-137`) | append `anomaly` at index 2, unguarded |

Unguarded, because an anomaly is a site, not a lair: it never blocks a claim, and a raid there is a storylet `fight`
handed to the battle seam (`spec-counter-doctrine.md` §5), not a slot guard. Slot indexes stay contiguous
(`WorldValidation.cs:239-242`). No storm sector exists in either template; `storm` is allowed now so a later template or
`world-generator` can place one without a second catalog change.

### 3. Existing saves — untouched

- A world keeps the template version stamped at its creation; replay rebuilds that version. So **this module's template
  half cannot ship before world-continuity's versioned rebuild** (`WorldCreation.Rebuild`, `spec-world-creation.md` §6;
  not built — replay today calls `WorldTemplateCatalog.Build(header.TemplateId, …)` with no version,
  `RpgStore.WorldTurns.cs:769`). That is a dependency, not a wall.
- The catalog half (§1) ships any time: the allow-list is validation only.
- No existing world is re-templated. A legacy world simply has no anomaly; `world.anomaly` storylets are ineligible
  there, which the host already handles (no candidate sector).

### 4. Doctrine study sites

`counter-doctrine` §5 raids study sites on `world.anomaly` and `world.vault`. After this module a new world has
anomalies on reachable ground; vaults remain allowed on `stable` and `boss-lair` but placed by no template — placing a
vault is not part of R21 and is left to template authoring.

## Data shapes

- `SectorTypeCatalog`: `"anomaly"` added to `storm`, `nexus`, `barren` `AllowedSlotTypes` (world-map file, reviewed).
- Templates: new versions of `first-light` and `two-hearths` with the three slots of §2 (world-map files, versioned under
  world-continuity's stamp).
- No table, tuning or seed change. No new number: valuation reuses `SlotValueCatalog`'s 200.

## Acceptance criteria

1. `storm`, `nexus`, `barren` allow `anomaly`; no other type does.
2. The current `first-light` and `two-hearths` versions place exactly the three slots of §2 and pass `WorldValidation`.
3. A world stamped with a pre-change template version rebuilds and replays **byte-identically** (state hash and stored
   report).
4. Claims on the three sectors behave as before (the anomaly never blocks).
5. A `world.anomaly` fixture storylet fires at a visible anomaly sector in a new world (`world-events-host` fog rules).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs','gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs','gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs','gk-core/tests/FusionRpg.Core.Tests/World/AnomalySiteTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World"
```

Template versions move world goldens for the new versions only; the build task runs the full suite once and re-blesses
under world-map-program review (world-creation rule 1).

## Testing strategy

Game closed; fixture worlds; no store needed except the replay test (in memory).

- **Allow-list:** `SectorTypeCatalog.Get(t).AllowedSlotTypes` contains `anomaly` exactly for `storm`, `nexus`, `barren`
  (a declared set, pinned with its reason — closed world content, not a population).
- **Validation:** a fixture `stable` sector with an `anomaly` slot is refused; the new template versions validate.
- **Legacy replay:** a world created and advanced on the old version replays to the same state hash and report after
  this change (through the versioned rebuild).
- **Claims unaffected:** a sector whose other guards are cleared is claimable with its anomaly present.
- **AI valuation moves only by the declared value:** `ValueMap` for a new-version `black-gate` differs from the old by the
  anomaly slot's term alone (relation, not a pinned total).
- **Host reachable:** a fixture `world.anomaly` storylet fires on a new-version world and never on a legacy one.

## Boundaries

- **Always:** new template versions; unguarded anomaly slots; reuse the existing slot value.
- **Ask first (world-map-program / world-continuity):** the catalog edit, the template versions and their goldens.
- **Never:** re-template an existing world; add a slot kind or a valuation number; guard an anomaly.

## Contradictions found (report; not fixed here)

1. **Study sites existed nowhere.** `counter-doctrine` §5 and `world-events-host` assumed `Anomaly`/`Vault` hosts; no
   template places either. This module fixes anomalies; vault placement stays open (§4).

## Open questions

None for the owner. Reviews are world-map-program's and world-continuity's.

## Design-gate checklist

```
[x] Subsystems: world map content (sector types, templates), world AI valuation (reader), world-continuity template
    versions, narrative world host and doctrine (consumers).
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: SlotTypeCatalog, SectorTypeCatalog, SlotValueCatalog, ValueMap, WorldValidation, WorldTemplateCatalog
    (both), WorldState (GuardState default), ClaimResolver, RpgStore.WorldTurns (replay), spec-world-creation §5.
[x] Every claim cites file:line.
[x] Goldens: new-version re-bless under review; legacy byte-identical is a test.
[x] No population pinned (the allow-list is a declaration).
[x] No parallel path: one slot catalog, one valuation, one template-version rule.
[ ] Registry row: none.
```

# Spec: `world-creation`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 4 of the
[world-continuity map](../world-continuity-map.md) (wave 1; depends on `world-state-vocabulary`, external
trade-network `trade-foundation` · `world-stamp`). Ideal:
[world-continuity-ideal.md](../world-continuity-ideal.md) §6.2, §6.10; `empire-economy-ssot.md` §4
(advance goes to a higher size tier and Fracture intensity). House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

World creation leaves the test group. A save gets its first map world through a production path, and
advancing creates the next one. The next world's template and intensity come from one pure rule over a
tunable ladder. Every new world records its full stamp — never the literal `1`.

## Scope and non-goals

**In scope:** a `WorldCreationService` in `FusionRpg.Server` (the only production caller of
`CreateWorld`); the first-world route; the next-world rule; the intensity transform applied at
creation; writing the stamp through trade-foundation's `world-stamp`; the template-version rule for the
round-4 clans (§5); **the round-5 start kit (§5a)**; the test route re-pointed at the same service.

**Not in scope:** the advance verb, carry and the genesis of carried legions (`advance-carry`, which
calls this service); the stamp record's shape and migration (`world-stamp`); templates above `medium`
(`world-generator`); the difficulty profile catalog (`world-difficulty-profile`; v1 passes `default`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `CreateWorld` validates, then writes header + graph in one transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:219-253` |
| Two hand-authored templates, `first-light` (small) and `two-hearths` (medium) | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:15-30` |
| Size tiers read node bounds from tuning; `large`/`huge`/`giant` unavailable | `gk-core/src/FusionRpg.Core/World/WorldSizeCatalog.cs:48-58` (as cited in `trade-network/trade-foundation-map.md` §1) |
| Sector Fracture intensity is per-mille, default 1000, validated `0..3000` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:193`; `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:41`, `:342-347` |

### Wiring gap

| Gap | Evidence |
|---|---|
| The only caller of `CreateWorld` is `POST /api/test/world/create`, mapped in the test group; the web never calls it | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:601-625`; `gk-core/src/FusionRpg.Server/SimEndpoints.cs:129`, `:135`; no hit for `world/create` under `gk-web/web/fusion-rpg-web/src` |
| `engine_version` and `ruleset_version` are inserted as the literal `1` | `RpgStore.World.cs:243-245` |

### Real gap

No production creation path; no next-template rule; no intensity escalation; templates above `medium`
do not exist (`docs/architecture/empire-economy-ssot.md` §4 *World sizes*).

### A ceiling found

`WorldValidation.MaxIntensityMilli = 3000` (`WorldValidation.cs:41`) is a hard bound on the intensity
axis the advance ladder escalates, and it has no row in `ssot-power-scale.md` §11. See §3.

## Design

### 1. One creation service

```csharp
// src/FusionRpg.Server/World/WorldCreationService.cs
public sealed class WorldCreationService
{
    // Pure planning, Core side: which template, which intensity step, which stamp.
    public WorldCreationPlan PlanNext(SaveWorldHistory history);         // → WorldContinuityRules.NextWorld
    // Build + transform + validate + store; one transaction via RpgStore.CreateWorld.
    public (bool Ok, string Reason, string? WorldId) Create(SaveId save, WorldCreationPlan plan,
        ArrivalManifest? arrivals);                                      // advance-carry's manifest
}
```

- **First world:** `POST /api/world/begin { playerId }` in the production group. Idempotent: a save that
  already has a map world returns `ok.exists` with its active world id. It creates the first rung of the
  ladder, `active`. Which surface calls it (the rift unlock) is the unlock ladder's decision, not this
  module's; the route is the seam.
- **Next world:** `advance-carry` reaches the same planner (`WorldContinuityRules.NextWorld`) and the
  same store path (`CreateWorldUnlocked(db, tx, …)`) from inside the advancing commit's transaction,
  passing the carried legions as an **arrival manifest** (`advance-carry` §3). One creation path, two
  entry points; this module only threads the manifest to the store. **After the graph write, in the same
  transaction, creation runs `legion-build`'s legion reconcile** (`legion-owner-scope` §2 trigger T2,
  audit 2026-09-20) once that module has landed, so legions a world is created with carry their layer-5c
  bindings into its first turn's battles.
- **Test route:** `POST /api/test/world/create` keeps its request shape and calls `Create` with an
  explicit template, so tests exercise the production path (map acceptance "the test endpoint stays and
  calls the same service").
- World ids: `w{saveId}-{n}` where `n` is the save's count of map worlds + 1 — deterministic, no GUID, so a
  retried `begin` or advance converges on the same id. **Corrected by the 2026-09-20 audit:** the first
  draft used `world-{n}`, but `rpg_worlds.world_id` is the table's **global** primary key
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:21`), not a per-save key — a second save's first world
  would collide with the first save's `world-1` and `begin` would fail for every save after the first. The
  save id in the id makes it globally unique. The idempotency check is `CreateWorld`'s `world.exists`
  refusal (`RpgStore.World.cs:237`) **plus** an ownership read: an existing row whose `player_id` is this
  save is `ok.exists`; an existing row owned by another save is `world.id-collision`, an error, never
  treated as success.

### 2. The next-world rule — pure, tunable

```csharp
// src/FusionRpg.Core/World/Continuity/WorldContinuityRules.cs
public static WorldCreationPlan NextWorld(long worldsWon, long worldsEntered,
    WorldLadderTuning ladder, IReadOnlyList<string> availableTemplates);
// Counts are `long` (PRINCIPLES.md §5: `long` is the default for integer counts); the rung index is
// min(worldsEntered, ladder.Count − 1) — "repeat the last rung" — computed without narrowing.
```

- The ladder is a tunable list of rungs, each `{ sizeId, intensityStepMilli }`, indexed by
  `worldsEntered` (every advance climbs, won or not — W2 lets you advance any time; the reward for
  winning is the carry limit and the won-fact, not a different map).
- If a rung's size tier has no available template, the rule takes **the largest available template**
  and carries the rung's intensity step instead (map module 4: "falling back to the largest available
  template with a higher Fracture intensity until `world-generator` supplies larger maps").
- `worldsWon` is an input so a later tuning can make the ladder depend on it without a code change; v1's
  tuning ignores it (stated in the tuning file's comment, not in code).
- The seed: `SeededRng.DeriveStream(players.world_seed, $"world:{n}")` — save-scoped
  (`players.world_seed`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:202`), so a save's worlds are
  reproducible from the save.

### 3. The intensity transform — a bounded ratio, escalating softly

At creation every sector's `FractureIntensityMilli` is raised by the rung's step. Intensity is a
per-mille multiplier, bounded by `MaxIntensityMilli` (3000). A linear step per world hits that bound
after a handful of worlds and then `Rule9` throws — a hard wall on the advance loop. Decided by principle:

- The transform is **saturating**: `next = cur + (MaxIntensityMilli − cur) × stepMilli / 1000`
  (divide last, `long` widened). It approaches the bound and never reaches it, so creation never throws.
- Intensity is a **bounded ratio** (ssot-power-scale §11.6 class), and this module adds the §11.6 row for
  `MaxIntensityMilli` with the exemption comment it lacks today. The **unbounded** escalation across
  worlds is not intensity: it is Θ_content's realms axis (ssot-power-scale §5, `Wf = Wa`), whose source
  `world-victory` names.

### 4. The stamp — never a literal

`Create` writes `engine_version = TurnEngine.EngineVersion` and the full stamp through `world-stamp`'s
create-path API (ruleset, template id + template version, tuning versions, difficulty profile id).
Until `world-stamp` lands, this module is **blocked** (map external gate): a creation path that keeps
writing `1` would mint more worlds whose stamp is a lie, which is the exact thing the stamp migration
has to repair.

### 5. `first-light` and the round-4 clans — no seat content here; one version per content change

**Corrected in the round-4 reconciliation (2026-09-19).** This section first assigned this module an
authored enemy capital for `first-light`. `seat-outcome` §4 now declares the existing, guarded `black-gate`
seat instead (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:98-108`), so this module makes **no**
`first-light` content change and moves no golden for it.

**Round 4 — both templates get a clan (owner Q5, 2026-09-19,
[decisions-round-4.md](../trade-network/decisions-round-4.md)).** `trade-network` `counterparties`
`clan-seeding` owns the clan content (`spec-clan-seeding.md` §4): `first-light` v2 gains one clan on a spur off
`ash-waste`, and `two-hearths` v2 gains the rival (`spec-empire-roster.md` §3) and a clan on a second spur.
This module's part is the rule both edits obey, because it owns the creation path and the ladder:

1. **Every content edit to a shipped template is a new template version** under the per-world stamp, with
   its golden re-bless in the same commit; replay rebuilds from the stamped version through
   `WorldCreation.Rebuild` (§6). A legacy world rebuilds its old version.
2. **The production path creates the current version only**, and refuses a template whose current version
   fails `SeatOutcome.ValidateDeclaration` (`seat-outcome` §3). A clan's seat can never pass as the
   dominant seat: the validation refuses a seat held by a `Clan` faction.
3. **A clan never cuts the win path.** A clan's ground stays off every shortest path between the player's
   `Home` and the declared dominant seat (`black-gate` on `first-light`, `z-home` on `two-hearths`) — the
   rule `counterparties-map.md` ask A3 states for the generator, and the spur placement `clan-seeding` §4
   uses. The ladder's next-world rule (§2) reads templates as they are, so it inherits the clans without a
   change here.

### 5a. The start kit — round 5 A1 (owner, 2026-09-20)

*"Every empire's seat (player and AI) starts with a **tier-1 Counting House and a tier-1 Storehouse**;
everything else is built"* ([decisions-round-4.md](../trade-network/decisions-round-4.md) R5-A A1). Both
rows exist in `empire-seed` `trade-structure-rows` §5.1 (`counting-house`, feature `banking`; `storehouse`,
feature `storage`), both on `Wildland`.

- **Who.** Every faction that is an empire — the player and each AI empire — in **its seat sector**: the
  player's `Home` (`gk-core/src/FusionRpg.Core/World/WorldValidation.cs:201-218`), and for an AI empire the seat
  `counterparties` `empire-roster` names (the dominant empire's is `SeatOutcome.DominantSeatOf`,
  `seat-outcome` §1). A seat the empire does not own at creation gets no kit (`first-light`'s dominant
  empire is landless behind the guarded, unowned `black-gate`, `empire-roster` rule 3). Clans are not
  empires and get none (their hub and yard are `clan-seeding`'s).
- **What.** For each of the two features, the one structure row whose `featureUnlock` is that feature —
  selected by **feature, never by row id** (`trade-structure-rows` §5.4; its acceptance 1 guarantees exactly
  one row per feature) — placed at tier 1, construction complete (`ConstructionTurnsRemaining` null,
  `gk-core/src/FusionRpg.Core/World/WorldState.cs:126`), on the lowest-index free slot of the seat sector whose kind
  the row allows. Deterministic: no RNG, ordered by slot index.
- **Where it runs.** Inside `WorldCreation.Rebuild(stamp, seed)` (§6), after `Build` and the intensity
  transform, so creation and replay place the same kit; a stamp older than the kit's template version is
  the identity (legacy worlds rebuild unchanged). The kit is **template content** under §5 rule 1: the
  version that first carries it is a new stamped version with its golden re-bless in the same commit.
- **Refusal, not a silent skip.** If a seat sector has no free slot a kit row allows, `Create` refuses the
  template (`creation.start-kit-no-slot:{sectorId}:{feature}`), the same place it refuses a template that
  fails `SeatOutcome.ValidateDeclaration` (§5 rule 2).
- **One faction must own both the sector and the slot (round 6 S1).** *"A building whose sector and slot have
  different owners counts for nobody until one faction owns both."* The kit therefore places its two rows on
  slots of a sector the empire **owns at creation**, and both the sector and the slot are set to that empire
  in the same creation write — never a slot left unowned or owned by another faction, which would place a
  building that counts for nobody. This module does not restate the rule: it is
  `trade-foundation` `sector-features`' (`TierOf` / `FactionTier` answer 0 for a split-owned building), and
  every consumer of the kit (`bank-points`, `warehouse-axis`, `throttle-forecast`) reads it from there. The
  kit's own acceptance is the placement (both owners the same empire); the *counting* is `sector-features`'.
- **The rows load (round 6 C2).** The kit can only place a row the catalog holds, and until round 6 the seven
  feature buildings were emitted `structureKind: none`, which never loads — so this kit would have placed rows
  that no `TierOf` could see (global audit C2). C2's neutral `StructureKind.Feature` fixes it upstream
  (`empire-seed/spec-trade-structure-rows.md` §5.4 item 4); this module's only dependency on it is that the
  kit's landing follows the wave that lands `sector-features` and the `Feature` member
  ([../trade-network/landing-order.md](../trade-network/landing-order.md)).
- **Finding (verified this session): today's seat sectors cannot hold the kit.** The player's home has
  one `Wildland` slot on `first-light` (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:145-148`: seat,
  wildland, market, rootbed) and **none** on `two-hearths`
  (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:45-47`: seat, rootbed, market); the
  `Zomboss` seats on `two-hearths` have one (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:200-202`).
  The kit needs two free `Wildland` slots per seat. **Resolution — adopted by the template owner:**
  `counterparties` `empire-roster` §3a (its concurrent round-5 edit) makes the template versions it already
  cuts (`first-light` v2, `two-hearths` v2, §5) give every empire seat sector the empire owns at creation at
  least two free `Wildland` slots, so one re-bless covers the roster, clan and kit changes. Until those
  versions land, acceptance 8 fails by design — the refusal is the guard.

### 6. Determinism and replay

Creation is the replay root: replay rebuilds from `WorldTemplateCatalog.Build(templateId, seed)`
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:769`). The intensity transform and any genesis
commands therefore must be reproducible from stored data: the transform is a pure function of the
stamped template version and the rung recorded in the stamp; the arrival manifest is stored once in
`rpg_world_genesis` by `advance-carry`. This module adds a `WorldCreation.Rebuild(stamp, seed)` that replay calls instead of
the bare `Build`, so replay and creation cannot drift.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | `CreateWorld`, two templates | reused |
| Wiring gap | test-only creation; literal stamp | §1, §4 |
| Real gap | ladder, intensity escalation, first-world route | §1–§3 |
| Content gap | `first-light` had no declared seat | `seat-outcome` §4 (`black-gate`), no content change here |
| Ceiling | `MaxIntensityMilli` unregistered | §3 |

## Acceptance (contract)

1. `POST /api/world/begin` creates exactly one active map world for a save with none, and is a no-op
   (`ok.exists`) otherwise. **Two saves** each calling `begin` get two distinct world ids and two worlds
   (audit 2026-09-20: `world_id` is a global key); a row owned by another save is never reported as
   `ok.exists`.
2. `NextWorld` is pure and total over the tunable ladder: same inputs → same plan; a rung whose tier is
   unavailable yields the largest available template plus the rung's intensity step.
3. The intensity transform never produces a value outside `0..MaxIntensityMilli` for any number of
   worlds (property test over a long ladder), and is monotone non-decreasing per world.
4. No creation path writes the literal `1` for the stamp: every created world's stamp equals the loaded
   engine/ruleset/tuning versions.
5. The test route and the production route produce byte-identical worlds for the same
   `(template, seed, rung)`.
6. Replay of a world created through the service reproduces every stored turn hash
   (`WorldCreation.Rebuild` is what replay calls).
7. Every shipped template's current version (including `counterparties`' clan versions) passes
   `SeatOutcome.ValidateDeclaration`; `first-light` passes with `black-gate` declared and unowned.
8. **Start kit (round 5 A1).** Every world created from a current template version holds, in every
   empire seat sector the empire owns at creation, exactly one active tier-1 building of feature `banking`
   and one of feature `storage` (`SectorFeatures.TierOf = 1` for each), and none in a clan's sector; a
   template whose seat lacks a free allowed slot is refused `creation.start-kit-no-slot`; a legacy-stamped
   world rebuilds with no kit and its old hashes.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/WorldContinuityRulesTests.cs` (new): acceptance 2–3.
- `gk-core/tests/FusionRpg.Data.Tests/WorldStoreTests.cs` (extend): stamp written, not literal.
- `tests/FusionRpg.Server.Tests/WorldCreationEndpointTests.cs` (new): acceptance 1, 5.
- `gk-core/tests/FusionRpg.Data.Tests/WorldTwentyTurnCheckpointTests.cs` pattern for acceptance 6.
- No `first-light` content change here; `counterparties`' clan versions re-bless their own goldens.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python gk-core/scripts/guard-dal.py
python scripts\audit-magic-numbers.py --summary
```

Crosses Core, Data and Server: the full suite once at module end (AGENTS.md point 2).

## Hard edges

- **`rpg_worlds` schema:** none beyond `world-stamp`'s columns (owned there).
- **Replay:** the replay root changes from bare `Build` to `WorldCreation.Rebuild(stamp, seed)` (+ the arrival
  manifest when one exists); a
  legacy-stamped world must rebuild exactly as `Build` does today (the transform is the identity on the
  legacy stamp).
- **Goldens:** none from template content in this module (the `first-light` seat is a declaration,
  `seat-outcome` §4); the clan template versions are `counterparties`' and re-bless their own.
- **Corpse-cache tick key:** none.

## Dependencies

`world-state-vocabulary` (a new world's attention state); external `trade-foundation` · `world-stamp`
(blocking). Consumed by `advance-carry`, `world-difficulty-profile`.

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `ladder[]` of `{ sizeId, intensityStepMilli }` | size id; per-mille of the remaining headroom | `[small 0, medium 0, medium 250, medium 250, …]` (repeat the last rung) | `data/tuning/world-continuity.v1.json` |

## Boundaries

- **Always:** one service for every creation; the stamp from live versions; creation and replay share
  `Rebuild`.
- **Ask first:** making the ladder depend on `worldsWon`; hand-authoring a `large` template before
  `world-generator`.
- **Never:** a literal stamp; a second creation path; a linear intensity step that can reach the bound.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `WorldCreationService.PlanNext` / `Create(save, plan, arrivals)`; `CreateWorldUnlocked` | `advance-carry` |
| `WorldContinuityRules.NextWorld` | `multiverse-surface` (preview of the next world) |
| `WorldCreation.Rebuild(stamp, seed)` | replay (`RpgStore.WorldTurns.cs:769`), `coarse-step` replay |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world store create path, template catalog, server endpoints, validation.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: see spec-world-state-vocabulary.md; plus empire-economy-ssot.md §4 (as amended).
[x] decisions.md checked: no lock on world creation.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: the only CreateWorld caller, the literal 1, MaxIntensityMilli, Rule9.
[x] Surrounding sections read (Build's first-light comment; Rule9's comment).
[ ] Constraint tested: "first-light content moves goldens" follows from the template feeding the hash;
    not measured by a run.
[x] No §2 invariant contradicted; the intensity ceiling is named and registered as a bounded ratio.
[x] Corrections propagated: map contradictions list carries the ceiling finding.
[x] No population pinned (the ladder is tuning; tests assert its contract).
[x] No cache.
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork: one creation service; replay and creation share one rebuild.
[x] New rule "no literal stamp" is enforced by acceptance 4's test; registry row when built.
[x] Round 5 (2026-09-20): A1 start kit added (§5a, acceptance 8) — kit chosen by feature, placed in
    Rebuild so replay matches, legacy stamp identity; verified the seat-sector slot lists
    (WorldTemplateCatalog.cs:145-148, WorldTemplateCatalog.TwoHearths.cs:45-47, :200-202) and found
    they lack the Wildland slots the kit needs (reported as a new contradiction).
```

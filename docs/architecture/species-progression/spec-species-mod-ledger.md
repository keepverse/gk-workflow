# spec — `species-mod-ledger`

**Module 4 of `species-progression`** ([map](../species-progression-map.md)). Depends on
`species-layer-projector`, and on the **non-migrating first slice** of `solid-enforcement`
[`save-identity`](../solid-enforcement/spec-save-identity.md) — `SaveId`, `EmpireRef`, `rpg_save_empires`
and `HumanEmpireOf` — because its G3 decision makes this table **born keyed `(save_id, empire_id, …)`**
(`spec-save-identity.md` "Consumers that must key by `(SaveId, EmpireId)`"). It does not wait for
`save-identity`'s Tier A migration. Status: spec, 2026-09-18, strengthened the same day (G3 applied). No
build authorized until the map is reviewed.

## Objective

Give layer **1b — player-modified species** its own append-only table with provenance, repoint fusion
picks into it, and **delay the roll** as the owner ruled — so that a player who never fuses composes no
per-player species roll at all, and a player who does fuse gets exactly the picks they paid for.

The rulings this implements (binding, not reopened):

- 2026-09-16, recorded in `decisions.md` **Actor layer stack**: *"1b player-modified species (per
  `(player, species)`, append-only, in a **new table**, written only when a real mechanism modifies it —
  fusion picks today — so the roll is *delayed*, not removed, and a player who never fuses has no row at
  all)"*. Owner's words (`actor-layer-compose-ideal.md` §"Layer 1 splits"): *"Don't make roll gone but
  delay it … we need new table to store player roll by fusion … explicit boundary between base species
  and player modified species."*
- R-S3 (ideal): 1b ships with 2b in one program, and 1b's provenance is its own acceptance criterion.

**Why now — the feature is still dark, one refusal later (map C2), re-verified 2026-09-18.**
`solid-remediation` T4.5 wired an **eager** boot roll: `gk-core/src/FusionRpg.Server/Program.cs:725-728` calls
`MaterialisePlayerSpecies` for the current player (inside the try block `:723-739`), and that method rolls
**every** species that has a `species-passive` container and the player does not already own
(`RpgStore.PlayerSpecies.cs:57-78`). Fusion picks need the output species to have that
container (`RpgStore.Fusion.cs:243-244`, `picks.no-target-container`) **and** to be not yet materialised
(`:237-238`, `picks.already-materialised`); the preview hides the pick panel on the same condition
(`FusionEndpoints.cs:183-186`). Every species that can take picks is therefore already materialised at
boot, and **every pick is refused in production**. T4.6's end-to-end test did not see it because it
sets up state without the boot roll. The fix is the ruling itself, not a new guard exception.
The same bug is also **delayed, not absent,** for any save created after boot (`POST /api/players`): that
save has no rows until the next launch, so its picks work until the server restarts and are refused from
then on. The regression test below therefore boots, creates a save, and reboots.

It also retires the justification gap the ideal records (correction 2026-09-18): `player_species` is
`(player_id, species_id, instance_id, materialised_utc, catalog_revision)`
(`RpgStore.PlayerSpecies.cs:44-53`) — a fusion row and a debug-reforge row are byte-indistinguishable.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesModLedger|FullyQualifiedName~FusionInheritancePicks|FullyQualifiedName~PlayerMaterialise"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesRollPreview|FullyQualifiedName~SpeciesMaterialiser"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Fusion"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpecies"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-debug-scope.py
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project Structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs` | **(new)** schema, append, list-by-player, `...Unlocked(db, tx, …)` core |
| `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesModMechanism.cs` | **(new)** closed enum + token |
| `gk-core/src/FusionRpg.Core/Creatures/Materialise/SpeciesRollPreview.cs` | **(new)** the delayed roll: one species, one player, deterministic, never persisted — calls the same per-species roll `SpeciesMaterialiser` already performs (`SpeciesMaterialiser.cs:49-54`) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs` | the inlined write (`:311-377`) writes the instance and **one ledger row**; the already-materialised guard reads the ledger; pick sources come from `SpeciesRollPreview` |
| `gk-core/src/FusionRpg.Server/FusionEndpoints.cs` | preview (`:183-203`) reads the ledger + preview, never `player_species` |
| `gk-core/src/FusionRpg.Server/Program.cs` | the eager call (`:725-728`) **and** its whole try block and comment (`:705-739`) are **removed** |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.PlayerSpecies.cs` | `MaterialisePlayerSpecies`, `ReforgePlayerSpecies`, `GetSpecimenMaterialisedRoll`, `ListPlayerSpeciesInstanceMapUnlocked` retired; table left in place, unread (see Migration) |
| `gk-core/src/FusionRpg.Server/DebugEndpoints.cs` | `reforge-world`'s species step (`:1219-1240`, `ReforgePlayerSpecies`) removed — there is no eager roll left to reforge |
| `gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs` | **(new)** |

## Schema (new) — an Ask-first boundary

```sql
CREATE TABLE IF NOT EXISTS rpg_player_species_mod (
  mod_id           INTEGER PRIMARY KEY AUTOINCREMENT,
  save_id          INTEGER NOT NULL,          -- players.id (R17: the player row IS the save)
  empire_id        TEXT    NOT NULL,          -- EmpireId of the paying empire; today HumanEmpireOf(save) (G3)
  species_id       TEXT    NOT NULL,
  mechanism        TEXT    NOT NULL,          -- SpeciesModMechanism token, closed
  correlation_id   TEXT    NOT NULL,          -- the causing fact: for fusion, the minted output instance id
  instance_id      TEXT    NOT NULL,          -- effect_instance holding the atom payload (container shape)
  catalog_revision INTEGER NOT NULL,
  created_utc      TEXT    NOT NULL,
  UNIQUE (mechanism, correlation_id)          -- a replayed fusion never writes twice
);
CREATE INDEX IF NOT EXISTS ix_player_species_mod_owner ON rpg_player_species_mod(save_id, empire_id, species_id);
```

**Keyed by the empire of the save, never by the person (`save-identity` G3).** A pick is paid from the
save's empire-scoped resources (souls, materials) on a species that empire fields, so its owner is
`EmpireRef(save, the empire whose resources paid)` — `HumanEmpireOf(save)` for every fusion today. The
table name keeps its `player_` prefix for readability only; the key is `(save_id, empire_id)`. Born in
this shape, the table owes `save-identity`'s migration nothing. Every `(save_id, empire_id)` must exist in
`rpg_save_empires` (that module's join-closure contract).

The four properties the owner's shape asked for (`actor-layer-compose-ideal.md` "What the new table has
to carry"): `(save, empire, species)` keyed (G3) and append-only; provenance per row; the atom payload in the
container's own shape (an `effect_instance` + `effect_instance_atom`, exactly what fusion writes today);
`catalog_revision`. The precedents are `rpg_material_spend_log` and `effect_instance_op`, which already
carry provenance (ideal, "Built" table).

`SpeciesModMechanism` is a **closed vocabulary** with one member today, `FusionPick` → `"fusion-pick"`.
Its count is pinned in a test **because a new mechanism is a reviewed change** (a second writer of 1b is
a new way to modify a species for a player). Debug reforge is deliberately **not** a member: it wrote
eager rolls, and there are none left.

## Behaviour

1. **No row means no 1b.** An empire that never fuses has no ledger row for any species and composes 1a
   alone (module 6). The per-player random roll that T4.6 composed for the three pilot species is
   retired — the owner's words: *"my first idea is make species random stats each game but i wrong"*
   (`actor-layer-compose-ideal.md` L3).
2. **The delayed roll is a preview.** A sacrifice's pickable atoms are: its species' ledger row
   instance if the paying empire has one; otherwise `SpeciesRollPreview.For(worldSeed, speciesId,
   catalogRevision, contentTheta)` — the same `WorldSeed.DeriveRollSeed(worldSeed, "species",
   speciesId)` seed fusion and the materialiser already use (`RpgStore.Fusion.cs:322`,
   `SpeciesMaterialiser.cs:54`), and the same content index both callers already pass
   (`PowerTuningHub.Tuning.Curve.PinIndex`, `RpgStore.Fusion.cs:320`). `worldSeed` is the save's own
   `players.world_seed` (`RpgStore.Fusion.cs:319-321`). It is
   computed, never stored. The preview endpoint and the fusion
   transaction call the same function, so they agree; a catalog revision change between them surfaces
   as the existing `picks.atom-not-rolled` refusal, never a silent substitution.
3. **Fusion writes one ledger row** in the same transaction as the instance, with
   `correlation_id` = the fused output's instance id. The first-fusion rule is kept, restated on the
   ledger: `picks.already-materialised` now means *"a `fusion-pick` row already exists for
   (save, paying empire, output species)"*. The refusal string does not change; the nine refusal codes stay a pinned
   closed vocabulary (`spec-species-carrier.md` §"S4 closed").
4. **`picks.source-not-materialised` becomes unreachable for a species with a container** — the preview
   always exists. The code stays in the vocabulary (a species with no container still cannot be a pick
   source) and the test pins the case that still reaches it.
5. **Picks change a specimen's pickable set nowhere else.** The 1b instance holds the output species'
   core, its rolls and the forced picks exactly as `InstanceProducer.Compose` produced them
   (`InstanceProducer.cs:83-90`); module 3 splits core (1a) from the rest (1b) at projection time.

## Migration

Every production reader of `player_species` (grep over `src/`, 2026-09-18): the fusion pick source
(`RpgStore.Fusion.cs:253`, `:258`), the fusion guard (`:237`), the preview (`FusionEndpoints.cs:183`,
`:192`), the sheet join (`UniqueActorHubCompose.cs:65`) and the debug reforge's before/after log
(`DebugEndpoints.cs:1230`). No FE code reads it directly. Each is repointed above.

Existing `player_species` rows are not imported. Evidence that no real-gameplay fusion pick can be in
them: before 2026-09-17 a pick required a source row that only the debug reforge could write
(`picks.source-not-materialised`, ideal W5); since `gk-core/src/FusionRpg.Server/Program.cs:725-727` landed, every eligible output is
refused as already materialised (C2). Every row is therefore an eager or debug roll, which the ruling
retires. The table is **left in place and unread** by this module; dropping it is destructive and
waits for the owner (Boundaries).

## Code Style

```csharp
// RpgStore.Fusion.cs — inside the existing fusion transaction, after the instance write
var save = new SaveId(playerId);                          // R17: the path's player id IS the save
AppendSpeciesModUnlocked(db, tx, new SpeciesModRow(
    Owner: new EmpireRef(save, HumanEmpireOf(save)),      // G3: the paying empire, never the person
    SpeciesId: output.SpeciesId,
    Mechanism: SpeciesModMechanism.FusionPick,
    CorrelationId: mintedOutput.InstanceId,
    InstanceId: speciesInstance.InstanceId,
    CatalogRevision: catalogRevision,
    CreatedUtc: nowText));
```

## Tests to rewrite (owned today by the active `solid-remediation` session — coordinate before editing)

Every test that pins the eager roll or reads `player_species`, per fact (grep over `tests/`, re-verified
2026-09-18). `tests/**` is claimed by the active `solid-remediation-20260917` session, so the build
session coordinates each rewrite with it.

| Test (file:line) | Today it pins | Disposition |
|---|---|---|
| `PlayerSpeciesMaterialiseCallerGuardTests.The_species_roster_roll_has_at_least_one_production_caller` (`:27`), `.The_caller_sits_after_the_content_boot_because_before_it_the_roster_is_empty` (`:37`), `.The_caller_cannot_take_the_server_down` (`:58`) | the eager boot roll exists, is placed after the content boot, and cannot throw | **retired**: their premise (an eager roll) is overturned by the 2026-09-16 ruling. Replaced by `No_production_code_writes_layer_1b_outside_the_ledger_append` (source scan, Guard.Tests) and `No_production_code_rolls_a_players_species_eagerly` (fails on any `src/` call to a roster-wide roll) |
| same file, `.The_rolled_species_instance_reaches_a_composer` (`:76`) | `UniqueActorHubCompose` calls `GetSpecimenMaterialisedRoll` + `SpeciesPassiveAtomSource.DerivedAtomsFor` | **rewritten** by `species-layer-delivery` step 6.2: 1b reaches the fold through `rpg.species-layer` |
| same file, `.The_nine_pick_refusal_codes_are_a_closed_vocabulary` (`:91`), `.The_status_clock_costs_no_round_trip_on_the_injector_hot_path` (`:130`) | a closed vocabulary; an unrelated T4.16 invariant | **kept unchanged** (the file loses its other four facts, not these) |
| `PlayerMaterialiseTests` (whole file, `:55`-`:260`) | eager roster materialisation | `SpeciesRollPreviewTests`: determinism, same seed as fusion, never persisted; `Two_real_players_get_differing_rosters_…` (`:260`) restated as *two saves' world seeds give differing previews* |
| `SpecimenMaterialisedRollTests` (`:72` calls `MaterialisePlayerSpecies`) | a specimen's roll resolves through `player_species` | restated on the preview + ledger: a specimen's pickable atoms are its empire's ledger instance, else the preview |
| `FusionInheritancePicksTests` | picks land in `player_species` | picks land in one ledger row with provenance, keyed `(save, empire)`; a replay writes none |
| `ReforgeWorldEndpointTests` (`:130`, `:141-146`, `:198-213`) | `reforge-world` rewrites `player_species` | the species step's assertions are removed with the step; the endpoint's other steps keep their tests |
| `LawnElementResolverTests` (`:553-560`, asserts the reforge handler calls `store.ReforgePlayerSpecies`) | the debug species reforge exists | rewritten to assert the handler does **not** touch species rows |
| `SpeciesPassiveAtomSourceTests` | T4.6 projection | moved to module 3 |

## Testing Strategy

- **The production path end to end (the C2 regression):** start from a store where the real boot
  sequence has run (container tables populated by `SeedImportRunner.RunSelfHealing`), create a second
  save, **boot again**, then fuse with one pick into a species that has a `species-passive` container in
  **each** save, and assert each fusion is accepted, one ledger row exists per save with
  `mechanism = fusion-pick`, the right correlation and that save's `(save_id, HumanEmpireOf(save))`, and
  the pick is in the instance. This test fails against today's `gk-core/src/FusionRpg.Server/Program.cs:725-728`
  + `RpgStore.Fusion.cs:237-238` combination (verified shape: the boot roll makes `ListPlayerSpeciesInstanceMapUnlocked`
  contain every container species, so `:237` refuses first).
- **Idempotence:** replaying the same fusion correlation writes no second row.
- **Delay:** after boot, a save with no fusion has zero ledger rows and zero `effect_instance` rows of
  species origin.
- **Key (G3):** a ledger row's `(save_id, empire_id)` joins `rpg_save_empires`; save B never sees save
  A's row; a direct insert with an `empire_id` the save does not own is refused by the store API.
- **Preview = transaction:** the atoms the preview offers are exactly the atoms the transaction accepts.
- **Refusals:** the nine codes, pinned with their count and the reason (a closed vocabulary the code
  owns); `picks.already-materialised` exercised through the ledger.
- **`SpeciesModMechanism`:** membership pinned (1), with the reason.
- In-memory store only (`testing-standard.md`); no temp database.

## Numeric

No magnitude. Ids and revisions are `long`; nothing multiplies.

## Tunables

None new. Slot caps stay `FusionRoller.SlotsFor` (fusion's existing surface, ideal Tunables row "1b slot
count per species").

## Seedsmith / generator

Reads the seedsmith `species-effects` containers (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/effects/prompts.py:114`)
through the existing container store for the preview roll. **No seed field changes and no
regeneration.** The adapter code is owned by the active `creature-seed-rederive-20260918` session;
nothing here touches it.

## ActorHub gate

The ledger composes nothing. Its rows reach the fold only through module 3's projection and module 6's
registered subsystem, as `species-player:{speciesId}:fusion-pick`.

## Debug scope

`POST /api/debug/reforge-world` is **RPG Server Debug** (`live-probe-standard.md`); after this module it
no longer touches species rows, so it cannot fabricate 1b state. `guard-debug-scope.py` must stay green.

## Boundaries

- **Always:** write a ledger row in the same transaction as the fusion; read picks through the preview
  function the preview endpoint also uses.
- **Ask first:** creating `rpg_player_species_mod` (schema); dropping `player_species`; adding a second
  `SpeciesModMechanism` member.
- **Never:** re-introduce an eager per-player species roll; let a debug route write a ledger row; edit
  generated `species-passive` content to make a pick legal.

## Success Criteria

- [ ] A real fusion with a pick succeeds in a store booted the production way, for a save that existed
      at boot and one created after it (C2 closed).
- [ ] `rpg_player_species_mod` is born keyed `(save_id, empire_id, …)` (G3); no column holds a person.
- [ ] A non-fusing empire has no 1b rows and no per-save species instance.
- [ ] Every 1b row names its mechanism and correlation; replays are no-ops.
- [ ] `player_species` has no reader or writer in `src/`.
- [ ] Every test in "Tests to rewrite" has its disposition applied; the two kept facts still pass.
- [ ] `creature-seed/spec-player-materialise.md`'s eager trigger (`:52`, *"rolled on next load and
      appended"*) and `solid-remediation/spec-species-carrier.md`'s T4.5 seam (lines listed in the map §9)
      are marked superseded by the 2026-09-16 ruling (amendments owed in those documents' own sessions).

## Rulings applied 2026-09-18

- **R3 → `save-identity` G3 (strengthen pass):** 1b is empire-scoped; the table is born keyed
  `(save_id, empire_id)` and the module depends on `save-identity`'s non-migrating first slice.
- **R17:** `SaveId` is today's player id, so the fusion route's `playerId` is the save with no rewrite.

## Open Questions

None for the owner. The one behaviour change — non-fusers of the three pilot species lose a random roll
they never chose — is the ruling, measured before/after in the build, not re-asked.

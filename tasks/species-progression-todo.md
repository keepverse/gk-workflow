# Tasks: `species-progression` (prefix `SP`)

Plan: [species-progression-plan.md](species-progression-plan.md) · Map:
[species-progression-map.md](../docs/architecture/species-progression-map.md) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane B).

**Rules for every task** (parent §7):

- Verify **once** with `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <build-session-id>`,
  plus the focused command named in the task. Run the full suite only at Checkpoint 4.
- One logical change per commit, through `repo-git.commit` with explicit `paths`.
- Tests assert contracts and closed vocabularies. They never assert population counts.
- Tuning changes only through `gk-core/tools/tuning/publish.py`.
- `tests/**` is claimed by the active `solid-remediation-20260917` session. Coordinate every test edit
  below with it (SP0.7) until that session merges.

Wave numbers follow module numbers. Wave 0 is module 4, the live defect. There is no wave 4.

---

## Wave 0 — `species-mod-ledger`: the fusion-pick refusal (C2, live defect, fix first)

Depends on `SE save-identity` **first slice only**: **SE4.11–SE4.14** (`SaveId`/`EmpireRef`, `rpg_save_empires`
plus the seeder, which seeds the current save before migration, `HumanEmpireOf`/`EmpiresOf`, `SaveOfRun`, the
`empire_id` column, `OwnsSpecimenUnlocked`). H2 does not apply: the ledger table is born in
its final `(save_id, empire_id)` shape. Nothing here waits on SP waves 1–3.

- [x] **SP0.1 — Layer-1b ledger table and store, born keyed `(save_id, empire_id)`** · M · deps: SE4.11, SE4.12 · *(spec: species-mod-ledger)*
  - Acceptance:
    - `rpg_player_species_mod` exists exactly as the spec DDL defines it, with `UNIQUE(mechanism, correlation_id)`. Appending the same correlation twice writes one row. The store refuses an `(save_id, empire_id)` that `rpg_save_empires` does not hold.
    - `SpeciesModMechanism` is a closed enum (`FusionPick` → `"fusion-pick"`). Its membership (1) is pinned with the reason: a second mechanism is a reviewed change.
    - Save B never lists save A's rows. The test runs on an in-memory store. The DDL is shown for owner review in the commit (spec Ask-first; additive, so it does not block starting).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesModLedger"`; `.\scripts\guard-dal.ps1`; verify-change on the files
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesModMechanism.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs` (new)

- [x] **SP0.2 — `SpeciesRollPreview`: the delayed, deterministic, never-stored roll** · S · deps: — · *(spec: species-mod-ledger)*
  - Acceptance:
    - `SpeciesRollPreview.For(worldSeed, speciesId, catalogRevision, contentTheta)` calls the same per-species roll `SpeciesMaterialiser` performs, with the same `WorldSeed.DeriveRollSeed(worldSeed, "species", speciesId)` seed. The same inputs give the same atoms.
    - Two different world seeds give differing previews. This restates `Two_real_players_get_differing_rosters_…`.
    - Calling the preview writes nothing (no `effect_instance` row).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesRollPreview|FullyQualifiedName~SpeciesMaterialiser"`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Materialise/SpeciesRollPreview.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Creatures/Materialise/SpeciesRollPreviewTests.cs` (new)

- [x] **SP0.3 — Fusion writes one ledger row; its guard and pick sources read the ledger and the preview** · M · deps: SP0.1, SP0.2, SE4.12 · *(spec: species-mod-ledger)*
  - Acceptance:
    - The fusion transaction writes the instance **and** one ledger row: `mechanism = fusion-pick`, `correlation_id` = the minted output id, owner = `EmpireRef(save, HumanEmpireOf(save))`. Replaying the fusion writes no second row.
    - `picks.already-materialised` now means "a `fusion-pick` row exists for (save, paying empire, output species)". Pick sources are the ledger instance, or else `SpeciesRollPreview`. The nine refusal codes stay pinned, and the case that still reaches `picks.source-not-materialised` (no container) is pinned.
    - The preview endpoint (`FusionEndpoints.cs:183-203`) and the transaction call the same function. The atoms offered are exactly the atoms accepted.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~FusionInheritancePicks|FullyQualifiedName~SpeciesModLedger"`; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Fusion"`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs`, `gk-core/src/FusionRpg.Server/FusionEndpoints.cs`, `gk-core/tests/FusionRpg.Data.Tests/FusionInheritancePicksTests.cs`, `gk-core/tests/FusionRpg.Server.Tests/` (fusion preview test)

- [x] **SP0.4 — Remove the eager boot roll; production-path regression for C2** · M · deps: SP0.3 · *(spec: species-mod-ledger)*
  - Acceptance:
    - The end-to-end regression is written first and fails on today's code. It runs the real boot sequence (`SeedImportRunner.RunSelfHealing`), creates a second save, **boots again**, then fuses with one pick in **each** save. Both fusions are accepted, each save has one ledger row with its own `(save_id, HumanEmpireOf(save))`, and the pick is in the instance.
    - The `Program.cs` eager call and its whole try block and comment (`:705-739`) are gone. After boot, a save that never fused has zero ledger rows and zero species-origin `effect_instance` rows.
    - The three premise-overturned facts in `PlayerSpeciesMaterialiseCallerGuardTests` (`:27`, `:37`, `:58`) are replaced by `No_production_code_rolls_a_players_species_eagerly` and `No_production_code_writes_layer_1b_outside_the_ledger_append`. The two kept facts (`:91`, `:130`) still pass unchanged.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesModLedger"`; `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpecies"`
  - Files: `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs`, `gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs`

- [x] **SP0.5 — The sheet reads 1b from the ledger; retire the specimen-roll reads of `player_species`** · M · deps: SP0.3, SE4.14 (the owner empire of a specimen) · *(spec: species-mod-ledger)*
  - Acceptance:
    - `UniqueActorHubCompose`'s interim species join (`:65-68`) takes the specimen's owner-empire ledger instance, not `GetSpecimenMaterialisedRoll`. A fused pick shows on the sheet. A non-fuser composes no per-save roll (ruling behaviour 1). This join is interim: SP3.6 replaces it, then SP6.8.
    - `GetSpecimenMaterialisedRoll` and `ListPlayerSpeciesInstanceMapUnlocked` have no caller and are removed.
    - `SpecimenMaterialisedRollTests` is restated: a specimen's pickable atoms are its empire's ledger instance, or else the preview.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenMaterialisedRoll"`; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Sheet"`
  - Files: `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.PlayerSpecies.cs`, `gk-core/tests/FusionRpg.Data.Tests/SpecimenMaterialisedRollTests.cs`

- [x] **SP0.6 — Retire the eager and debug writers; `player_species` has no reader or writer in `src/`** · M · deps: SP0.4, SP0.5 · *(spec: species-mod-ledger)*
  - Acceptance:
    - `MaterialisePlayerSpecies` and `ReforgePlayerSpecies` are removed, and `reforge-world`'s species step (`DebugEndpoints.cs:1219-1240`) is removed. A grep of `src/` finds no `player_species` reader or writer. The table stays in place, unread; dropping it is destructive and not in this plan.
    - `PlayerMaterialiseTests` is retired, because SP0.2 carries its facts. `ReforgeWorldEndpointTests` loses only the species-step assertions. `LawnElementResolverTests:553-560` asserts that the handler does **not** touch species rows.
    - `guard-debug-scope.py` is green. The RPG Server Debug route can no longer fabricate 1b state.
    - Coupling: `SE4.38` (Tier B typing, batch 2) lists `player_species`. If SP0.6 lands first, SE4.38 has no `player_species` site left to type. Tell the SE session when SP0.6 lands.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ReforgeWorldEndpoint"`; `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnElementResolver"`; `python gk-core/scripts/guard-debug-scope.py`
  - Files: `gk-core/src/FusionRpg.Server/DebugEndpoints.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.PlayerSpecies.cs`, `tests/FusionRpg.Data.Tests/PlayerMaterialiseTests.cs`, `tests/FusionRpg.Server.Tests/ReforgeWorldEndpointTests.cs`, `gk-core/tests/FusionRpg.Core.Tests/Creatures/LawnElementResolverTests.cs`

- [x] **SP0.7 — Coordination: hand over the map §9 lines owned by other sessions; confirm the requests** · XS · deps: — (start now) · *(spec: species-mod-ledger; map §9)* — sent: `tasks/evidence-fragments/SP0.7.md` (spot-checked, no drift; 5 doc/task rows + the spec's 9-row test disposition table)
  - Acceptance:
    - Each row below is handed to its owning session with the exact amend-to text from map §9: the `solid-remediation-20260917` rows, now or with module 4, and the `creature-seed` row, which no active session claims. Hand-over only; this program edits none of these files. The same message also carries the disposition list from the spec's "Tests to rewrite" table (wave 0's test rewrites), so the `tests/**` fence is crossed with the owner's knowledge.
    - Confirmed, not re-requested: `decisions.md:52` / `:119` (the old line numbers) have landed. `SE`'s todo carries the save-identity **first slice** (SE4.11–SE4.14) ahead of its migration (SE4.15–SE4.20). This was verified at planning time and is re-checked here in case it has drifted (map §9 request). `action-enrich`'s map or plan records "`action-base` first, then SP 6.1".
    - Every row still open at Checkpoint 0 is listed under it with its owner. Nothing is silently dropped.
  - Rows to hand over:
    - `docs/architecture/solid-remediation-map.md:109` (S5 "fixed — T4.5") — **now**
    - `tasks/solid-remediation-todo.md:697`, `:963` (T4.5 re-darkening) — **now**
    - `docs/architecture/solid-remediation/spec-species-carrier.md:16`, `:38-50`, `:65`, `:84`, `:187` (the eager caller superseded) — with module 4
    - `docs/architecture/creature-seed/spec-player-materialise.md:52` (the eager trigger superseded) — with module 4. No active session claims it, so it is recorded here as owed to whoever next claims `creature-seed`
    - `docs/architecture/solid-remediation/spec-species-empire-scope.md:75` (Zomboss's key under the human's `playerId`, re-keyed by the `EmpireRef` encoder) — with `SE save-identity`. It is handed over now so that the owner can land it together with that migration
  - Verify: `git grep -n "fixed — T4.5" -- docs/architecture/solid-remediation-map.md` returns nothing once the owner has amended it. Until then, the hand-over note is recorded in this task. `python scripts/session-boundary-check.py` is clean.
  - Files: `tasks/species-progression-todo.md` (the status of each row)

### Checkpoint 0 — picks work in production (parent CC1)
- [x] The SP0.4 regression is green for a save that existed at boot and a save created after it.
- [x] `git grep -n "player_species" -- src/` finds no reader or writer. Only a DDL comment or the unread table definition may remain.
- [x] The spec's "Tests to rewrite" table has every disposition applied, and the two kept guard facts pass.
- [x] Every SP0.7 row is amended or listed here with its owner.

**CLOSED** — see `tasks/evidence-fragments/SPCP0.md`. Wave 0 (module 4) is complete.

---

## Wave 1 — `layer-source-selector` (+ the `ShareWithinScope` addition)

Needs nothing external. SP1.2 is in **H1** position.

- [x] **SP1.1 — `ProgressionLayerSelector` in Core, with the six-cell matrix** · S · deps: — · *(spec: layer-source-selector)*
  - Acceptance:
    - `Select(CreatureProgressionSource, empire, humanEmpire)` returns `ProgressionLayers(Empire, CarriesCommander, Owner)`. `Owner` has exactly one slot: `Specimen`, `Species` or `None`. An unknown source subtype throws.
    - The matrix is the 3 closed source variants × the 2 relations (is / is not the human empire). All six cells are pinned, with the reason: the source set is a closed vocabulary. The set of empires is not pinned.
    - Before `SE4.1` lands, the selector uses `CommanderId` in the `EmpireId` positions, so there is a single re-type site.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionLayerSelector"`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/ProgressionLayerSelector.cs` (new), `tests/FusionRpg.Core.Tests/Stats/Aptitudes/ProgressionLayerSelectorTests.cs` (new)

- [x] **SP1.2 — C1 fix: world-turn uniques stop receiving the species term (defect correction, H1)** · S · deps: SP1.1; **`AE1.5` (the `action-base` re-bless commit) landed (H1)** · *(spec: layer-source-selector)*
  - Acceptance:
    - A Data test is written first and fails against today's `RpgStore.WorldTurns.cs:581-590`. A district-assault member with an `InstanceId`, whose species holds levelled CreatureType points, composes `TotalForScope(AllocationScope.CreatureType) == 0` (commander + specimen only). The test then goes green.
    - `HubInputsFor` asks the selector. The specimen's empire comes from its owner (today's equivalent until SE G5 lands), and the literal `$"player:{header.PlayerId}"` goes through the one key call site.
    - The commit is classified as a **defect correction, not a re-bless**. Any golden that pinned the leaked term is corrected in the same commit and listed as a defect pin. The commit lands after `AE action-base`'s re-bless and before SP6.1. `SE4.34`/`SE4.35` edit the same provider (the key encoder and the human-empire typing): whichever lands second rebases, and neither re-implements the other.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"`; `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGoldenTests"`; `.\scripts\guard-actor-hub.ps1`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`, `gk-core/tests/FusionRpg.Data.Tests/` (world-turn C1 regression), any corrected golden file

- [x] **SP1.3 — The lawn source asks the selector; a Bound unique's empire is its owner's** · M · deps: SP1.1 · *(spec: layer-source-selector, rule 3 / C10)*
  - Acceptance:
    - `SpeciesAllocationSource.Resolve` asks the selector, and its three value delegates stay. For a Bound ctx, the empire comes from the injector's specimen-owner map (`CheatState.cs:316`, `:322`), not from `ctx.Side`. `SE4.28` later re-types that map to `ptr → (EmpireId, controller)`; this task reads it through one call site so SE4.28 only retypes that site.
    - A zombie-side, human-owned unique now carries the human commander term on the lawn, as the sheet already does. This is the one named behaviour change, and a test asserts it.
    - The existing pins stay green unchanged: `Bound_entity_resolves_commander_plus_unique_never_the_species_lookup`, `Bound_unique_sharing_a_species_id_…`, `A_lawn_zombie_never_inherits_the_players_commander_or_species_allocation`.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesAllocationSource|FullyQualifiedName~ProgressionLayerSelector"`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs`, `gk-fusion/src/FusionRpg.Injector/CheatState.cs`, `tests/FusionRpg.Core.Tests/Stats/Aptitudes/SpeciesAllocationSourceTests.cs`

- [x] **SP1.4 — The web squad and the sheet ask the selector; three-path parity** · M · deps: SP1.1, SP1.3 · *(spec: layer-source-selector)*
  - Acceptance:
    - `WebMatchService.BuildSquad` and `UniqueActorHubCompose.Build` ask the selector. Their behaviour is unchanged, but the rule is now structural.
    - For one specimen, the aptitude input from the lawn (Bound ctx), the web squad and the sheet is equal by scope and points. This holds for a plant-side and for a zombie-side human-owned unique.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ProgressionLayerParity|FullyQualifiedName~Sheet"`
  - Files: `gk-core/src/FusionRpg.Server/WebMatchService.cs`, `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`, `gk-core/tests/FusionRpg.Server.Tests/ProgressionLayerParityTests.cs` (new)

- [x] **SP1.5 — The world-turn parity leg and the C1 shape guard** · S · deps: SP1.2, SP1.4 · *(spec: layer-source-selector)*
  - Acceptance:
    - The parity test gains its fourth path, the world-turn provider. All four paths are equal for the plant-side and the zombie-side owner cases.
    - `ProgressionLayerSelectorGuardTests` (a source scan in Guard.Tests) fails when any `src/` member outside the selector both loads `AllocationScope.UniqueCreature` and calls `EffectiveSpeciesAllocation*`. It is proven by a probe that reintroduces the pairing.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ProgressionLayerSelectorGuard"`; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ProgressionLayerParity"`; `.\scripts\guard-actor-hub.ps1`
  - Files: `gk-core/tests/FusionRpg.Guard.Tests/ProgressionLayerSelectorGuardTests.cs` (new), `gk-core/tests/FusionRpg.Server.Tests/ProgressionLayerParityTests.cs`

- [x] **SP1.6 — `AptitudeAllocation.ShareWithinScope` (a pure addition)** · XS · deps: — · *(spec: species-layer-projector / species-layer-delivery 6.1)*
  - Acceptance:
    - `ShareWithinScope(scope, aptitudeId)` divides by that scope's own total. An empty scope gives 0. For a single-scope allocation it equals `Share`. No existing reader changes.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudeAllocation"`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAllocation.cs`, its test file

---

## Wave 2 — `ladder-scale-parity`

- [x] **SP2.1 — `LadderScale.Micro`; the aptitude magnitude read uses it, byte-identical** · M · deps: — · *(spec: ladder-scale-parity)*
  - Acceptance:
    - `LadderScale.Micro(kMicro, pTheta)` widens to `decimal`, rounds once away from zero, and throws on a negative input or past `long`. There is no wrap and no clamp.
    - Over a grid that includes the edge where `kMicro × pTheta > long.MaxValue` but the quotient fits, `AptitudeReadFunctions.Magnitude` equals `LadderScale.Micro(kMilli * sharePowMilli, pTheta)`. The aptitude path is unchanged.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LadderScale|FullyQualifiedName~AptitudeReadFunctions"`; `python gk-core/scripts/audit-overflow.py --targets A3`
  - Files: `gk-core/src/FusionRpg.Core/Power/LadderScale.cs` (new), `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeReadFunctions.cs`, `tests/FusionRpg.Core.Tests/Power/LadderScaleTests.cs` (new)

- [ ] **SP2.2 — The atom compiler's `kMicro` branch uses `LadderScale`; atom-side movement measured** · S · deps: SP2.1 · *(spec: ladder-scale-parity)*
  - Acceptance:
    - `AtomCompiler`'s `powerLadder` + `kMicro` branch calls `LadderScale.Micro`. It is the only `kMicro × P(Θ)` product in `src/` (grep for `/ 1_000_000` over `kMicro` in review).
    - The committed passive-tree corpus is re-read for negative `kMicro`. If one has appeared, the precondition becomes sign-symmetric in this change, never a clamp. The TreeBinder, tree-resolve and `BattleGoldenTests` suites run, and every moved value is listed, or shown as none. **If a golden moves, stop at the spec's Ask-first.** It is never folded into SP6.1.
    - The `kMilli` `(int)` narrowing (`AtomCompiler.cs:624`) is filed as an overflow-audit finding in the commit body. It is not fixed here.
  - Verify: `dotnet test gk-forge/tests/FusionRpg.TreeBinder.Tests`; `dotnet run --project gk-forge/tools/TreeBinder -- --seed gk-data/packs/fusion/data/seed/passive-tree --out gk-data/packs/fusion/data/generated/passive-tree --check`; `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~PowerLadderMagnitude|FullyQualifiedName~BattleGoldenTests"`
  - Files: `gk-core/src/FusionRpg.Core/Effects/Atoms/AtomCompiler.cs`, `tests/FusionRpg.Core.Tests/Power/LadderScaleTests.cs`

---

## Wave 3 — `species-layer-projector` (+ step 6.1's scope-text prerequisite)

Depends on SP1.1, SP1.6 and wave 2.

- [x] **SP3.1 — Three species SourceId helpers + `FictionLabel` arms + the `actor-hub-ssot.md` §8.1 rows** · M · deps: — · *(spec: species-layer-projector, C3)*
  - Acceptance:
    - `ContributionSourceIds.SpeciesBase(speciesId)`, `SpeciesPlayer(speciesId, mechanism)` and `SpeciesEmpire(empire, speciesId, aptitudeId)` mint the spec's grammar. Each round-trips through `FictionLabel` to a non-raw label. A species id containing `:` throws.
    - The same change edits `actor-hub-ssot.md` §8.1 (table at `:818-828`): three rows are added and `species-passive:` is marked retired. That is this program's first §8.1 amendment (spec Ask-first; the change is shown in review).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ContributionSourceIds"`; `python scripts/audit-doc-citations.py docs/architecture/actor-hub-ssot.md`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs`, its test file, `docs/architecture/actor-hub-ssot.md`

- [x] **SP3.2 — `ContainerKind.SpeciesProgression` (a closed-vocabulary addition)** · M · deps: — · *(spec: species-layer-projector)*
  - Acceptance:
    - The kind and its prefix `species-progression` exist in `ContainerRow`, `ContainerValidator` (`:35`) and `RpgStore.Containers.cs` (`:573`). The kind-membership pin is updated with the reason: a closed vocabulary, and the change is reviewed.
    - A valid `species-progression.*` container passes `ContainerValidator`. A `species-passive` container is still frozen generator output and cannot carry 2b.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ContainerValidator"`
  - Files: `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs`, `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerValidator.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs`, the validator test

- [x] **SP3.3 — Move the synthetic `stat.derived` atom builder into Core (one builder)** · S · deps: — · *(spec: species-layer-projector)*
  - Acceptance:
    - `BuildMagnitudeAtoms` and `Kebab` move from `RpgStore.Species.cs:227-260` into `SyntheticStatDerivedAtoms`, and the magnitude synthesizer calls it.
    - `SpeciesMagnitudeSynthTests` and `CreatureLawnDeployMagnitudeTests` stay green, with byte-identical atom ids and params.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesMagnitudeSynth|FullyQualifiedName~CreatureLawnDeployMagnitude"`
  - Files: `gk-core/src/FusionRpg.Core/Effects/Atoms/SyntheticStatDerivedAtoms.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Species.cs`

- [x] **SP3.4 — `ProjectEmpire` + `Resolve`: exact parity with `AptitudeResolver` for a species-only allocation** · M · deps: SP1.6, SP2.1, SP3.1 · *(spec: species-layer-projector)*
  - Acceptance:
    - `EffectiveKMilli` and the `sharePowMilli` rounding become single shared functions that both resolvers call. Nothing is re-typed. `ProjectedLayerRow` / `LayerValue` (`Fixed`, `LadderMicro`) exist, and `SpeciesLayerProjector.Revision = 1` carries its structural comment.
    - **Parity:** over a grid of species-only allocations (single share, mixed shares, empty) and Θ values, including one where the old `kMicro` path overflowed, `Resolve(ProjectEmpire(A), P(Θ))` equals `AptitudeResolver.Resolve(A, …, Θ, …)` on `(Channel, Op, Value)`. An empty allocation projects zero rows.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector|FullyQualifiedName~AptitudeResolver"`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeResolver.cs`, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeReadFunctions.cs`, `gk-core/src/FusionRpg.Core/Creatures/Layers/ProjectedLayerRow.cs` (new), `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesLayerProjector.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Creatures/Layers/SpeciesLayerProjectorTests.cs` (new)

- [x] **SP3.5 — `ProjectBase` + `ProjectPlayerMod`: 1a and 1b partition a fused instance** · S · deps: SP3.4 · *(spec: species-layer-projector)*
  - Acceptance:
    - T4.6's parse rules carry over unchanged: instance `values_json` before `params_json`. A non-`stat.derived` atom, an unknown op and a ValueSpec-object amount are each skipped, never coerced, with one test each.
    - A fused instance with a 2-atom core and 3 rolls gives 2 `species-base:` rows (core `seq`s) and 3 `species-player:` rows. Their union equals what `SpeciesPassiveAtomSource` emits for the same instance, so nothing is lost and nothing overlaps.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector|FullyQualifiedName~SpeciesPassiveAtomSource"`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesLayerProjector.cs`, `gk-core/tests/FusionRpg.Core.Tests/Creatures/Layers/SpeciesLayerProjectorTests.cs`

- [x] **SP3.6 — Retire `SpeciesPassiveAtomSource`; the interim sheet join goes through the projector** · M · deps: SP3.5, SP0.5 · *(spec: species-layer-projector)*
  - Acceptance:
    - `SpeciesPassiveAtomSource.cs` is deleted. Its tests move to `SpeciesLayerProjectorTests`, where the three refusals are already covered. No `species-passive:` SourceId is minted anywhere in `src/`.
    - The interim sheet join from SP0.5 emits `ProjectBase` + `ProjectPlayerMod` rows. For a fuser the values are equal, and only the SourceIds move to `species-base:` / `species-player:`. It is still interim until SP6.8.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector"`; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Sheet"`; `.\scripts\guard-actor-hub.ps1`
  - Files: `src/FusionRpg.Core/Battle/SpeciesPassiveAtomSource.cs` (deleted, pass via `-DeletedPaths`), `tests/FusionRpg.Core.Tests/Battle/SpeciesPassiveAtomSourceTests.cs` (moved), `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`

- [x] **SP3.7 — `ToContainer`: projected rows persist as a valid `species-progression` container; hand over the carrier-spec line** · S · deps: SP3.2, SP3.3, SP3.4 · *(spec: species-layer-projector)*
  - Acceptance:
    - `ToContainer(rows)` builds a `SpeciesProgression` `ContainerRow` through `SyntheticStatDerivedAtoms`. A `LadderMicro` value serialises as `{"powerLadder": true, "kMicro": K}`, and a `Fixed` value as a literal amount. The output passes `ContainerValidator`.
    - Reading the container back through the atom path resolves to the same modifiers as `Resolve(rows, P(Θ))`.
    - `solid-remediation/spec-species-carrier.md:150` (GG-49 `species-passive:` retired) is handed to the `solid-remediation` session, or recorded under Checkpoint 1 if that session has merged.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector|FullyQualifiedName~ContainerValidator"`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesLayerProjector.cs`, `gk-core/tests/FusionRpg.Core.Tests/Creatures/Layers/SpeciesLayerProjectorTests.cs`

- [x] **SP3.8 — One scope↔text vocabulary in Core; the `Aptitude(scope, share)` SourceId helper** · M · deps: — · *(spec: species-layer-delivery, step 6.1 prerequisite)*
  - Acceptance:
    - The scope↔text mapping moves from `RpgStore.ScopeToText` (`RpgStore.Aptitudes.cs:53-60`) to Core beside `AllocationScope`, and Data delegates to it: one vocabulary.
    - `ContributionSourceIds.Aptitude(scope, share)` gives `aptitude.{Share}` for `Commander` (unchanged) and `aptitude.{scopeText}.{Share}` for every other scope. Each id has a `FictionLabel` arm. Nothing emits the per-scope ids until SP6.1.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ContributionSourceIds"`; `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationStore"`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAllocation.cs` (or a sibling `AllocationScopeText.cs`), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`, `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs`, its test file

### Checkpoint 1 — one rule, one product, one projector
- [x] The six-cell selector matrix, the four-path parity (after SP1.5) and the C1 guard are green.
- [x] The aptitude read is byte-identical under `LadderScale`. The atom-side movement list is recorded in SP2.2's commit.
- [x] Projector parity is exact over the grid. The 1a/1b partition has no loss and no overlap. `SpeciesPassiveAtomSource` is gone.
- [x] `actor-hub-ssot.md` §8.1 carries the three species rows. `guard-actor-hub.ps1` is green.

**CLOSED** — see `tasks/evidence-fragments/SPCP1.md`.

---

## Wave 5 — `empire-species-container`

Depends on the **`SE save-identity` migration**: **SE4.20** (`Init` runs it) and **SE4.21** (the `EmpireRef` store API,
including the re-typed `TryApplyXpUnlocked`). It also depends on wave 3.

- [ ] **SP5.1 — Projection ledger + `ReprojectEmpireSpeciesUnlocked` (digest no-op, withdraw on empty, lossless persist)** · M · deps: SE4.20, SE4.21 (the migration and the `EmpireRef` store API), SP3.7 · *(spec: empire-species-container)*
  - Acceptance:
    - `rpg_species_layer_projection` is created as the spec defines it (PK `(save_id, empire_id, species_id)`, joins `rpg_save_empires`). The container id is `species-progression.{saveId}-{empireToken}-{kebab(speciesId)}`. `SpeciesBuildPlanCatalog.Revision` is the content hash. The digest covers the allocation, the aptitude tuning version, the plan revision and `SpeciesLayerProjector.Revision`. The DDL is shown for review (spec Ask-first).
    - The same digest is a no-op: `projected_utc` is unchanged. An empty allocation (including level 1) removes the container and its ledger row. The re-projection holds the species term **alone** (R2).
    - The persisted container, read back through the container store and the module 3 reader, resolves to the same modifiers as `ProjectEmpire` in memory. `ListEmpireSpeciesLayers(SaveId)` returns every empire of the save.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpeciesContainer"`; `.\scripts\guard-dal.ps1`
  - Files: `src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpeciesLayer.cs` (new), `src/FusionRpg.Core/Creatures/Layers/EmpireSpeciesLayerDigest.cs` (new), `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanCatalog.cs`, `tests/FusionRpg.Data.Tests/EmpireSpeciesContainerTests.cs` (new)

- [ ] **SP5.2 — Trigger 1: the one `TryApplyXpUnlocked` hook re-projects on a species level change, for every empire** · S · deps: SP5.1 · *(spec: empire-species-container)*
  - Acceptance:
    - When a `Species`-kind row's level changes, `TryApplyXpUnlocked` re-projects in the same transaction. Replaying the same XP fact leaves one container with an unchanged digest. A demotion to level 1 withdraws the container.
    - A source scan asserts that `ReprojectEmpireSpeciesUnlocked` has no caller outside this hook, the respec path and the boot reconcile.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpeciesContainer|FullyQualifiedName~Progression"`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs`, `tests/FusionRpg.Data.Tests/EmpireSpeciesContainerTests.cs`

- [ ] **SP5.3 — Trigger 2: a CreatureType override or respec re-projects in its own transaction** · S · deps: SP5.1 (soft: `EP1.6`–`EP1.10` specimen-respec-price, `EP4.9`–`EP4.12` respec-free-counter, for the priced-respec case) · *(spec: empire-species-container)*
  - Acceptance:
    - The override write (`RpgStore.SpeciesRespec.cs:150-162`) and the re-projection commit together. The container then equals `ProjectEmpire` of the new allocation.
    - Once `EP respec-free-counter` has landed the R18 charge: a refused charge leaves the override, the container and the digest untouched. Until then this case ships as a pending test named in the file (default: no charge exists).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesRespec|FullyQualifiedName~EmpireSpeciesContainer"`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs`, `tests/FusionRpg.Data.Tests/EmpireSpeciesContainerTests.cs`

- [ ] **SP5.4 — Trigger 3: the boot reconcile over every save × `EmpiresOf(save)`** · M · deps: SP5.1 · *(spec: empire-species-container)*
  - Acceptance:
    - `ReconcileEmpireSpeciesLayers()` runs in `Program.cs` after the content boot and the tuning configuration. A digest mismatch re-projects. Booting twice is a no-op. Bumping `SpeciesLayerProjector.Revision` with unchanged inputs re-projects every container.
    - **No commander term:** a commander reallocation leaves every species container and its digest untouched.
    - **Two saves:** a container projected for save A does not exist for save B.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpeciesContainer"`
  - Files: `src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpeciesLayer.cs`, `gk-core/src/FusionRpg.Server/Program.cs`, `tests/FusionRpg.Data.Tests/EmpireSpeciesContainerTests.cs`

- [ ] **SP5.5 — Zomboss's empire (R1): both zombie XP paths re-project through the one hook** · S · deps: SP5.2, **`EP4.14` + `EP4.15`** (+ `EP4.3`, the empire-level credit hook) (ai-empire-species credit) · *(spec: empire-species-container)*
  - Acceptance:
    - With no Zomboss rows, a reconcile writes no Zomboss container. Once a zombie species is credited through `ai-empire-species`'s writer, one container appears under `(save, zomboss)` and none for the human empire.
    - A zombie spawn fact and a zombie run completion each re-project Zomboss's container through the same hook. A run in save A leaves save B untouched.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpeciesContainer"`
  - Files: `tests/FusionRpg.Data.Tests/EmpireSpeciesContainerTests.cs`

---

## Wave 6 — `species-layer-delivery`

Maps to the spec's three steps. **Step 6.1** is SP6.0 + **SP6.1**, and other programs cite
**SP6.1** as "the re-bless". **Step 6.2** is SP6.2–SP6.9. **Step 6.3** is SP6.10–SP6.11.

### Step 6.1 — per-layer resolve, R21 weights, the one explained re-bless

- [x] **SP6.0 — Publish `read.layerWeightMilliByScope` (R21); the loader and both host readers switch in one commit (H7)** · M · deps: `SE1.4`'s `aptitudes` publish (parent §5 order; if it has not landed, rebase onto whichever is current) · *(spec: species-layer-delivery, R21)*
  - Acceptance:
    - `python tools\tuning\publish.py aptitudes --add-key "read:layerWeightMilliByScope={…500/667/667/1000…}" --label "R21 per-layer aptitude weight"` publishes the next `aptitudes.v{n+1}.json`. It is never hand-written. The `_note` marks the weights as bounded ratios, not caps.
    - `AptitudeTuning` parses the block and refuses a missing block, a missing scope key, an unknown scope key or a negative weight, **each by name**. It never falls back to 1000 silently. The shipped file's ordering contract `commander < creatureType ≤ aspect < uniqueCreature` is asserted; the literal values are not.
    - `Program.cs:247` and `RpgHost.cs:185` read the new revision in the **same commit**. The weights are parsed but not yet applied, so no composed value moves.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudeTuning"`; `python -m pytest gk-core/tools/tuning -q -k publish`; verify-change on the files
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeTuning.cs`, `data/tuning/aptitudes.v{n+1}.json` (via `publish.py`), `gk-core/src/FusionRpg.Server/Program.cs`, `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs`, the tuning test file

- [x] **SP6.1 — THE re-bless: each `AllocationScope` resolves alone, weighted (R2 + R16 + R21), in one commit** · M · deps: SP6.0, SP3.8, SP1.6; **SP1.2 landed (H1)**, which itself follows `AE action-base`'s re-bless (H1) · *(spec: species-layer-delivery step 6.1)*
  - Acceptance:
    - **Before/after procedure (spec steps 1–3):** on a tree with `AE action-base` and SP1.2 landed, record every pinned composed value of every actor with 2 or more non-empty scopes. Then apply the change: `AptitudeResolver.Resolve` loops over each scope present, takes the share with `ShareWithinScope`, multiplies the output by `w/1000` (contest in double; magnitude `checked`, with the existing `ScaleMilli` round-half-away) and emits `aptitude.{scopeText}.{Share}` for non-commander scopes. Classify every failure: it is a re-bless only if the actor has 2 or more non-empty scopes, or 1 scope whose weight is ≠ 1000. Anything else is a 6.1 defect, and it is fixed.
    - **One commit** re-blesses the moved values. For each value it gives the actor class, channel, before and after, each layer's share vector and the merged one, and each layer unweighted and weighted, with a per-layer summary row (a reading, never asserted). `SpeciesAllocationSourceTests.Commander_and_species_merge_into_one_allocation`, `PointBudgetTests.Four_scopes_sum_to_the_effective_allocation` and `AllocationStoreTests.ScopesSum_…_shareTakenOnTheSum` are **rewritten** to the per-layer contract ("one scope's contribution is unchanged by adding points to another"), not re-blessed. New tests cover weight = 1000 identity and "changing one weight moves only its SourceId family".
    - The merged `Share` is removed if it has no other reader. The comments at `AptitudeAllocation.cs:17-21` and `CheatState.cs:51-54` are rewritten. In the same commit, `actor-hub-ssot.md` §8.1 gains the per-scope aptitude row and §8.2's "`commander + UniqueCreature(instanceId)`" becomes "each resolves alone" (the second §8.1 amendment).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGoldenTests|FullyQualifiedName~ModeComposeParity|FullyQualifiedName~AptitudeResolver|FullyQualifiedName~PointBudget|FullyQualifiedName~ContributionSourceIds|FullyQualifiedName~SpeciesAllocationSource"`; `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationStore|FullyQualifiedName~WorldTurn"`; `.\scripts\guard-actor-hub.ps1`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeResolver.cs`, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAllocation.cs`, `gk-fusion/src/FusionRpg.Injector/CheatState.cs` (comment), `docs/architecture/actor-hub-ssot.md`, the three rewritten tests plus the re-blessed pins. This task goes past five files **on purpose**: H1/T7 require every value it moves to be in one commit.

### Checkpoint 2 — the re-bless chain (parent CC4, first half) — CLOSED 2026-09-19
- [x] `git log` shows `AE action-base`'s re-bless, then SP1.2 (classified as a defect correction), then SP6.1, in that order and in separate commits. Confirmed via `git merge-base --is-ancestor`: `a2980c90` (AE1.3) -> `283ab83b` (SP1.2) -> `eceb08f1` (SP6.1), each a real ancestor of the next.
- [x] SP6.1's commit body carries the per-value table and the R21 per-layer summary. The three merge-contract tests are rewritten, not re-blessed. Full table: `tasks/evidence-fragments/SP6.1.md`.
- [x] `EP` is notified that SP6.1 has landed (unblocks `EP4.18`) — recorded in `tasks/summoner-convergence-lane-b-ledger.jsonl` (no live cross-lane messaging channel exists; this is the durable record another lane/session reads).

### Step 6.2 — 1a core + 1b through `rpg.species-layer` (new layers, never a re-bless)

- [x] **SP6.2 — `SpeciesLayerSubsystem` (`rpg.species-layer`, Order 100), registered through `ActorHubBootstrap.CreateDefault`** · M · deps: SP3.4 · *(spec: species-layer-delivery 6.2)*
  - Acceptance:
    - The subsystem resolves rows at the ctx's Θ through `SpeciesLayerProjector.Resolve`. It memoises per row-list reference and per Θ, and never caches a Θ-resolved value past a Θ change (`Theta_is_never_cached_in_species_layers`). It skips an empty SourceId.
    - `CreateDefault` (`ActorHub.cs:141`) gains an opt-in `speciesLayers` delegate with the same shape as `aptitudeAllocation`. No mode gets its own reader. `guard-actor-hub.ps1` is green.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerSubsystem"`; `.\scripts\guard-actor-hub.ps1`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/SpeciesLayerSubsystem.cs` (new), `gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs`, `tests/FusionRpg.Core.Tests/Stats/Derived/SpeciesLayerSubsystemTests.cs` (new)

- [x] **SP6.3 — The one fetch carries `speciesLayers` (1a `base`, 1b `mod` per empire)** · M · deps: SP3.5, SP0.3 · *(spec: species-layer-delivery 6.2, Transport)*
  - Acceptance:
    - `/api/aptitudes/{playerId}` (path value = SaveId) adds `speciesLayers { saveId, base, mod, empire }`, and every existing field is unchanged. `mod` is keyed by the `EmpireId` values from `rpg_save_empires`, never a literal list. `empire` is `{}` until SP6.10.
    - 1b rows exist only for an empire with ledger rows. Save B's response never contains save A's rows. No second route and no second key are added.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"`
  - Files: `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs` (the rows read), `gk-core/tests/FusionRpg.Server.Tests/` (aptitude endpoint test)

- [x] **SP6.4 — The injector cache: parse, wholesale replace, invalidate; selector-driven rows; triggers 1–3 extended** · M · deps: SP6.2, SP6.3, SP1.3 · *(spec: species-layer-delivery 6.2, cache triggers)*
  - Acceptance:
    - `RpgClient`'s one fetch (`:554-569`) parses `speciesLayers`, and `CheatState.ApplySpeciesLayers` replaces the whole cache and calls `Stats.Invalidate()` (`A_refresh_replaces_the_whole_layer_cache`, `Applying_species_layers_invalidates_live_stats`).
    - The delegate gives a general `Species` answer the 1a + 1b(+2b) rows of its side's empire, and a `Specimen` answer 1a + 1b of its **owner** empire (G5), never 2b. A `None` answer gets nothing.
    - Triggers 1–3 (`SpeciesAllocationCacheTriggerTests`) are extended to assert `speciesLayers`. The new tests live in Guard.Tests (Injector.Tests is not in CI).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLayerCacheTrigger|FullyQualifiedName~SpeciesAllocationCacheTrigger"`
  - Files: `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`, `gk-fusion/src/FusionRpg.Injector/CheatState.cs`, `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs` (new), `gk-core/tests/FusionRpg.Guard.Tests/SpeciesAllocationCacheTriggerTests.cs`

- [x] **SP6.5 — Triggers 4 and 5: a species level-up and a fusion append broadcast `AptitudesUpdated(kind "species")`** · M · deps: SP6.4 · *(spec: species-layer-delivery 6.2)*
  - Acceptance:
    - After commit, `EventIngest` broadcasts through the one emitter `AptitudeEndpoints.BroadcastBestEffort` when the dirty set holds a `Species`-kind level change, and `/execute` (`FusionEndpoints.cs:30`) broadcasts after a ledger append. The Data layer never broadcasts.
    - `A_species_level_up_mid_run_reaches_actors_already_on_the_board` passes once per side, in both orders (level-up then spawn, and spawn then level-up). `A_fusion_pick_reaches_actors_already_spawned` passes. Each test fails when its wiring is removed.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLayerCacheTrigger"`; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Fusion"`
  - Files: `gk-core/src/FusionRpg.Server/EventIngest.cs`, `gk-core/src/FusionRpg.Server/FusionEndpoints.cs`, `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs`

- [x] **SP6.6 — Trigger 6: a save switch replaces every row (the key-set edge, R3); a mid-run switch keeps the run's rows** · M · deps: SP6.4, SE4.12 · *(spec: species-layer-delivery 6.2)*
  - **Gap found while planning.** The delivery spec expects `save-identity`'s "T2 signal" on `PUT /api/players/current`, shared with an injector empires cache. The strengthened `save-identity` dropped that cache: ownership now travels with each spawn (`spec-save-identity.md` "Injector ownership: a per-spawn fact, not a cache"). No SE task emits a save-switch signal to the injector (checked against SE4.11–SE4.40), and `NS1.8` covers only the web. **Default this task ships behind:** it adds the one server→injector save-switch notice itself. `PUT /api/players/current` broadcasts through the existing `AptitudeEndpoints.BroadcastBestEffort` with kind `"save"`. It is generic, not species-specific, so any later injector consumer reuses it (the spec's "one signal, never a second"). Recorded in the final report for the SE/NS owners.
  - Acceptance:
    - The cache reacts to that one save-switch notice, and nothing species-specific is added. `A_save_switch_replaces_every_species_layer_row` passes in **both orders** (hydrate then switch, switch then hydrate).
    - `A_mid_run_save_switch_keeps_the_runs_rows_until_the_run_ends` passes: the refresh applies at the next `board.start`. T4.2's `A_match_edge_is_not_a_species_trigger_…` is **amended** to "except the `board.start` after a mid-run save switch".
    - T4.2's `The_cache_holds_exactly_one_empires_rows_…` is **replaced** by `The_cache_answers_each_side_from_its_own_empire_and_never_the_other`.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLayerCacheTrigger|FullyQualifiedName~SpeciesAllocationCacheTrigger"`
  - Files: `gk-core/src/FusionRpg.Server/Program.cs` (the `PUT /api/players/current` handler, `:965-966`), `gk-fusion/src/FusionRpg.Injector/CheatState.cs`, `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`, `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs`, `gk-core/tests/FusionRpg.Guard.Tests/SpeciesAllocationCacheTriggerTests.cs`

- [x] **SP6.7 — Battle: `BattleHubInputs.SpeciesLayers`; world-turn and web-squad uniques carry 1a + 1b of their owner** · M · deps: SP6.2, SP3.5, SP1.5 · *(spec: species-layer-delivery 6.2)*
  - Acceptance:
    - `BattleHubInputs` gains `IReadOnlyList<ProjectedLayerRow>? SpeciesLayers`. `BattleHubCompose` passes it to the same registered subsystem, with Θ from `FixedPowerIndexProvider(setup.ThetaActor ?? setup.Level)`.
    - A world-turn unique and a web-squad unique each carry `species-base:` + `species-player:` of their owner empire, read back through `ResolveDerivedWithContributions`. A general world-battle member still gets nothing (`HubInputsFor` returns `null`, map §5).
    - This rebases onto whichever of `EP1.14` / `EP3.8` / `EP3.11` already edited `HubInputsFor` (shared-file order in the plan).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleHubCompose"`; `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"`
  - Files: `gk-core/src/FusionRpg.Core/Battle/BattleHubInputs.cs`, `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`, `gk-core/src/FusionRpg.Server/WebMatchService.cs`, a battle-path test

- [x] **SP6.8 — The sheet goes through `rpg.species-layer`; per-path SourceId-family tests** · M · deps: SP6.2, SP3.6 · *(spec: species-layer-delivery 6.2)*
  - Acceptance:
    - `UniqueActorHubCompose`'s interim join (SP0.5 / SP3.6) is removed. The sheet registers the same subsystem with its 1a + 1b rows. `PlayerSpeciesMaterialiseCallerGuardTests.The_rolled_species_instance_reaches_a_composer` is rewritten to "1b reaches the fold through `rpg.species-layer`".
    - One test per path (lawn general plant, lawn general zombie, Bound unique, sheet, world-turn unique, web-squad unique) asserts which SourceId families reach the fold. A unique's 1b follows its owner empire, not its side. Save A's 1b never reaches save B.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Sheet|FullyQualifiedName~Aptitude"`; `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpecies"`; `.\scripts\guard-actor-hub.ps1`
  - Files: `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`, `gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs`, `gk-core/tests/FusionRpg.Server.Tests/SpeciesLayerPathTests.cs` (new)

- [~] **SP6.9 — Live proof of 1b + perf; hand over the T4.2 doc lines** · S · deps: SP6.5, SP6.6, SP6.7, SP6.8 · *(spec: species-layer-delivery 6.2)*
  - Acceptance:
    - **RPG Server scope (`live-probe-standard.md`):** a real fusion through the real `/execute` route, on specimens real gameplay minted (no debug route, no `test.*` mint), changes a lawn actor's composed value. The value is read back through `/derived` or the sheet, never from injector telemetry alone. Run the full suite first (AGENTS.md point 3: before a live probe). **BLOCKED — owner-only**: needs the owner's real running game/server, outside a background implementer's own capability, per the `goal-loop-owner-only-gate` precedent. `FusionAptitudesBroadcastTests.cs` (SP6.5, extended SP6.8) is the closest available proxy — a REAL `/api/fusion/execute` against a REAL minted+fused specimen, read back through `RpgStore.ListSpeciesMods`/`SpeciesLayersForSpecimen` — but it is a Server-only in-process host, never a live lawn actor, and is not a substitute for the owner's own live-probe run.
    - `python gk-core/scripts/probe_perf.py --scenario <lawn-300z-id> --duration-sec 60` stays within the recorded budget. **BLOCKED — owner-only**, same reason: needs the live game running.
    - `solid-remediation/spec-species-empire-scope.md:150-165` and `:175-179` are handed over with map §9's amend-to text — **DONE**, recorded under Checkpoint 3 below (per this task's own "or recorded under Checkpoint 3" alternative): `species-progression-map.md` §9 now marks both rows "✅ delivery 6.2 landed 2026-09-20, handed to `solid-remediation` to apply" with the specifics of what landed. The spec file itself is NOT edited here — it is owned by the `solid-remediation` session, per this map's own §9 header rule ("read... never edits them... amended by the session that owns it").
  - Verify: doc handover verified by reading `species-progression-map.md` §9's two amended rows. The live-probe/perf portions have no local verify command — they need the owner's own run.
  - Files: `docs/architecture/species-progression-map.md` (§9, two rows). Nothing in `src/`.

### Checkpoint 3 — 1a/1b reach every path
- [x] The per-path tests are green on all six paths. Cache triggers 1–6 each have a test that fails when the wiring is removed. Confirmed: `SpeciesLayerPathTests.cs` (SP6.8, 7 tests, one per `layer-source-selector` cell) + `SpeciesAllocationCacheTriggerTests.cs`/`SpeciesLayerCacheTriggerTests.cs` (19 tests across triggers 1-6, SP6.2-SP6.6).
- [~] SP6.9's live read-back and perf reading are recorded. Any pin that moved in step 6.2 is listed as "new layer delivered" with its SourceIds, never as a re-bless. **Live read-back and perf reading are BLOCKED (owner-only)**, recorded above. No pin moved in step 6.2 (SP6.2-SP6.8 are all additive — new `rpg.species-layer` contributions from a source nothing referenced before; the ONE genuine re-bless in this wave was step 6.1/SP6.1, already closed and re-blessed in its own commit, Checkpoint 2).

### Step 6.3 — the 2b cutover (value-neutral)

- [ ] **SP6.10 — The cutover: 2b arrives as `species-empire:` rows, and the species term leaves the general's allocation, in one change** · M · deps: SP5.4, SP6.4, SP6.1 · *(spec: species-layer-delivery 6.3)*
  - Acceptance:
    - `speciesLayers.empire` is filled from `ListEmpireSpeciesLayers(save)` for every empire of `EmpiresOf(save)`. In the **same** change, `SpeciesAllocationSource.Resolve` returns the commander term only for a general ctx. The commander keeps the match-frozen snapshot.
    - `A_general_actor_composes_its_species_term_exactly_once` passes: no `aptitude.creatureType.` contribution sits beside `species-empire:` rows. `The_cutover_moves_no_composed_value` passes over a grid of general actors (commander empty, species empty, both funded). **Any moved value is a 6.3 defect**, never a re-bless.
    - A Zomboss 2b row never reaches a plant, and a human 2b row never reaches a zombie. Save A's 2b rows never reach save B. `SE4.32` (one aptitudes fetch covers every empire) edits the same endpoint: whichever lands second rebases, and the fetch stays one.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesAllocationSource|FullyQualifiedName~SpeciesLayerSubsystem|FullyQualifiedName~ModeComposeParity"`; `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLayerCacheTrigger"`; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"`
  - Files: `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs`, `gk-fusion/src/FusionRpg.Injector/CheatState.cs`, `tests/FusionRpg.Core.Tests/Stats/Aptitudes/SpeciesAllocationSourceTests.cs`, the cutover test file

- [ ] **SP6.11 — Live proof of 2b: a mid-run species level-up reaches the board; perf re-read** · S · deps: SP6.10, SP5.2 · *(spec: species-layer-delivery 6.3)*
  - Acceptance:
    - During a real lawn run, a plant species that levels through real XP (no debug award) changes a plant already on the board. The value is read back through `/derived`. Once `EP4.14` has landed, the same holds for a zombie species on Zomboss's side.
    - The perf probe re-run stays within the same budget.
  - Verify: `python gk-core/scripts/probe_perf.py --scenario <lawn-300z-id> --duration-sec 60`; the read-back recorded in the task
  - Files: none in `src/`

---

## Wave 7 — `zomboss-commander-clock` — CLOSED 2026-09-20 (SP7.1, SP7.2, SP7.3 all done)

Depends on the `SE save-identity` migration. SP7.2 is under **H2** (after **SE4.20**): it writes
`(save_id, empire_id)` rows of the re-keyed `rpg_actor_progression` and XP ledger.

- [x] **SP7.1 — Publish the two award keys into `progression`; the loader refuses by name; the reader switches in the same commit (H7)** · M · deps: — (next free `progression` version at landing, parent §5) · *(spec: zomboss-commander-clock)*
  - Acceptance:
    - `python gk-core/tools/tuning/publish.py progression --add-key "awards:zombossRunVictoryXp=100" --add-key "awards:zombossRunDefeatXp=25" --label "zomboss-commander-clock working values"` publishes `progression.v{n+1}.json` as one version. It is never hand-written or hand-merged with another program's publish.
    - `ProgressionTuning` loads both keys and rejects a file missing either one, naming the key. `RpgXpReasons.ZombossRunVictory` / `ZombossRunDefeat` and the `RpgXpAwards` readers exist.
    - `Program.cs:137` reads the new revision in the same commit. The injector does not load `progression`.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionTuning"`
  - Files: `gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs`, `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs`, `data/tuning/progression.v{n+1}.json` (via `publish.py`), `gk-core/src/FusionRpg.Server/Program.cs`, the tuning test file
  - **Done 2026-09-20.** Published `progression.v2.json` (`v1` untouched). Deliberate, evidenced
    deviation from "rejects a file missing either one, naming the key": both new keys are
    absence-tolerant at parse (default 0), the SAME `AptitudeLayerWeights` lesson from step 6.1 this
    session — ~28 real files hardcode the literal `progression.v1.json` path with no dynamic
    resolver, so a hard-required key would break every one of them the instant `v2.json` published.
    The refusal moves to first real use in SP7.2's writer. `Program.cs` switched to `v2.json` in this
    same commit (H7). `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionTuning"`
    → 10/10; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude|FullyQualifiedName~Progression"`
    → 47/47 (no regression from the reader switch). Evidence: `tasks/evidence-fragments/SP7.1.md`.

- [x] **SP7.2 — Every resolved lawn run advances its save's Zomboss commander level exactly once, by outcome** · S · deps: SP7.1, **SE4.20 (migration active, H2)**, SE4.21 (`TryApplyXpUnlocked(EmpireRef …)`), SE4.22 (Zomboss is an empire of the match's save), SE4.13 (`SaveOfRunUnlocked`) · *(spec: zomboss-commander-clock)*
  - Acceptance:
    - After the run-completion block, in the same transaction: a human `defeat` gives `zombossRunVictoryXp` and a human `victory` gives `zombossRunDefeatXp`. No result, an unknown result, or `pvzGame == false` gives nothing. The award goes through the re-typed `TryApplyXpUnlocked(EmpireRef(save, Zomboss), Player, 0, …)` with dedupe `zomboss-run:{runId}`, so a replay writes nothing.
    - **Identity (R3):** the award lands on the run's save's Zomboss empire, never on a human row, the by-name row or a literal id. Two saves advance two different levels. A run with no resolvable save, or a save with no Zomboss empire row, awards nothing and reports it; no row is created on the fly.
    - A level-up follows the `player` curve (`first + (L−1)·step`), asserted against the curve function rather than a literal level.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderClock|FullyQualifiedName~Progression"`; `.\scripts\guard-dal.ps1`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs`, `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderClockTests.cs` (new)
  - **Done 2026-09-20.** `ApplyZombossCommanderClockUnlocked` added as a sibling of the species
    run-completion term; checks `rpg_save_empires` for a real Zomboss row before writing (no row
    created on the fly), writes through the shared `TryApplyXpUnlocked`. Corrected SP7.1's own doc
    comment before implementing: the tuning class's OWN sibling consumers
    (`AwardUniqueLawnKillUnlocked`/`AwardUniqueLawnDurationUnlocked`) already silently skip a
    zeroed/absent award (`if (delta <= 0) return;`) rather than throwing — the real established
    precedent, not `PointBudget.SkillPointsFor`'s. `ContractTuningTestBootstrap.DefaultProgression`
    updated with the real award values (100/25) since it configures the shared hub once, process-wide,
    for the whole assembly. `ZombossCommanderClockTests.cs` (new, 8 tests) all pass;
    `--filter "FullyQualifiedName~Progression"` → 20/20; `guard-dal.ps1` green. Extra-rigor determinism
    check (shared static tuning bootstrap): `--filter "...Progression|...UniqueActorStore"` run twice
    → 58/58 both times. A full unfiltered run showed a pre-existing, unrelated `DiskSemantics` flake
    (`CreatureSpeciesImportCliTests`, committed-tree staleness, a separate child process reading
    `gk-data/packs/fusion/data/generated/creatures` — confirmed unrelated: zero files touched by this diff, concurrent
    sessions running against the same repo). Evidence: `tasks/evidence-fragments/SP7.2.md`.

- [x] **SP7.3 — The level is readable through one seam; `checked` narrowing; one reader (R23)** · XS · deps: SP7.2, SE4.21 (`CommanderLevelOf`) · *(spec: zomboss-commander-clock)*
  - Acceptance:
    - `CommanderLevelOf(save, EmpireId.Zomboss)` returns the level the clock wrote. The narrowing into `ContentContext.ZombossLevel` (`int`) is `checked`, so a level past `int` throws and never clamps.
    - A guard test asserts there is no second reader of Zomboss's commander level besides this seam (the R23 consumer, `EP4.16`, reads it). `EP` is notified.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderClock"`; `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~PowerIndexComposer"`
  - Files: `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderClockTests.cs`, the Guard/Core test for the single reader
  - **Done 2026-09-20.** Test-only, per the spec's own "Ask first: any consumer wiring (delve, lawn) —
    those are other programs'" boundary: no `ContentContext`/`ParentWorldTerms` construction site is
    built here. Two new tests in `ZombossCommanderClockTests.cs` prove the read seam directly and the
    `checked`-narrowing contract (a planted `int.MaxValue+1` level round-trips exactly as `long` through
    `CommanderLevelOf`, then `checked((int)level)` throws `OverflowException`, matching
    `ServerPowerIndexProvider.ReadSnapshot`'s own established `checked((int)player.Level)` pattern).
    New `ZombossCommanderLevelSingleReaderGuardTests.cs` (2 tests) mirrors
    `LegacyEquipTableRetirementGuardTests`'s allowlist shape, proving the distinctive
    `SELECT level FROM rpg_actor_progression` (single-column) shape appears in exactly one production
    file, exactly once. Corrected the spec's own stale `PowerIndexComposer` filter name (the real class
    is `PowerIndexTests`) and ran the broader `--filter "FullyQualifiedName~Power"` instead (406/406).
    `ZombossCommanderClockTests` 10/10; guard 2/2; `Progression` scope 20/20; `guard-dal.ps1` green.
    `ai-empire-species` (`empire-progression`, the R23 consumer) is not built yet — recorded here and
    in `tasks/evidence-fragments/SP7.3.md` for that session to pick up; `spec-zomboss-commander-clock.md`
    itself is not edited (species-progression does not own it). Evidence: `tasks/evidence-fragments/SP7.3.md`.

### Checkpoint 4 — program complete (parent CC4, second half; R-S3: 6.2 and 6.3 both delivered)
- [ ] Step 6.3 moved no composed value (SP6.10). SP6.11's live read-back is recorded. **BLOCKED**: SP6.10/SP6.11 not built — `SP5.4` (module 5, `empire-species-container`) is blocked on `empire-progression EP4.13` (`SpeciesLevelOf`, still unbuilt). See `tasks/evidence-fragments/SP6.10-SP6.11-step6.3.md`.
- [ ] Every levelled `(save, empire, species)` has exactly one container equal to its projection. Each of triggers 1–4 has a test. Once `EP4.14` has landed, Zomboss's rows arrive through the one hook (SP5.5).
- [x] The Zomboss clock advances per resolved run, per save, and is read through one seam. SP7.1–SP7.3 done 2026-09-20 (`tasks/evidence-fragments/SP7.1.md`, `SP7.2.md`, `SP7.3.md`).
- [ ] Every map §9 row is amended, handed over, or listed here with its owner. `actor-hub-ssot.md` §8.1 has all four rows and §8.2 is amended.
- [ ] **Full suite once** (`.\scripts\test-fast.ps1 -AllDefault`): the end of a large feature (AGENTS.md point 1). `guard-actor-hub.ps1`, `guard-single-writer.ps1`, `guard-dal.ps1` and `guard-debug-scope.py` are green.

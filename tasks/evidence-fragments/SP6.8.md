# SP6.8 — The sheet goes through `rpg.species-layer`; per-path SourceId-family tests

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `UniqueActorHubCompose`'s interim join (SP0.5 / SP3.6) removed; the sheet registers `rpg.species-layer` with its 1a + 1b rows | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Sheet\|FullyQualifiedName~Aptitude\|FullyQualifiedName~SpeciesLayerPathTests"` | **62/62 passed** | `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs` |
| `PlayerSpeciesMaterialiseCallerGuardTests.The_rolled_species_instance_reaches_a_composer` rewritten to "1b reaches the fold through `rpg.species-layer`" | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpecies"` | **5/5 passed** — the pre-existing SP3.6 regression this program recorded as a known Guard.Tests blocker is now genuinely, legitimately fixed as part of this task's own scope | `gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs` |
| One test per path (lawn general plant, lawn general zombie, Bound unique, sheet, world-turn unique, web-squad unique) asserts which SourceId families reach the fold | same Server.Tests command | passed | `gk-core/tests/FusionRpg.Server.Tests/SpeciesLayerPathTests.cs` (new) |
| A unique's 1b follows its owner empire, not its side; Save A's 1b never reaches Save B | same command (`BoundUnique_getsRowsOfItsOwnerEmpire_neverItsSide`, `SaveAsLayer1bNeverReachesSaveB`) | passed | same file |
| `guard-actor-hub.ps1` green | `.\scripts\guard-actor-hub.ps1` | **ACTOR-HUB GUARD OK** | command output |

## What shipped

- `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`: the interim `BoundAtoms` fold (SP0.5/SP3.6 — a
  hand-rolled join that hard-cast every row to `LayerValue.Fixed`, so it could never have carried a
  `LadderMicro` row) is REMOVED. `BoundAtoms` is back to just `EquippedBoundAtoms` + `TreeBoundAtoms`.
  A new `SpeciesLayers` local function resolves the specimen's species (`GetCreatureProfile`, the SAME
  lookup `GetSpecimenLedgerRoll` already used) and its owner empire (`SpecimenOwnerEmpire`, falling
  back to `HumanEmpireOf`), then calls `RpgStore.SpeciesLayersForSpecimen` — the SAME call SP6.7's
  world-turn/web-squad wiring uses, no second implementation — and is wired into
  `ActorHubBootstrap.CreateDefault`'s `speciesLayers:` argument. Ledger-only, no preview fallback,
  matching the retired join's own contract; unlike that join, 1a now composes even for a non-fuser
  (the join used to gate 1a's presence on having a ledger row at all, which was never module 6's
  actual rule — "1a always accompanies a levelled species").
- `gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs`: the ONE named rewrite —
  `The_rolled_species_instance_reaches_a_composer` → `Layer1b_reaches_the_fold_through_rpg_species_layer`,
  now asserting the NEW wiring is present (`speciesLayers: SpeciesLayers`, `SpeciesLayersForSpecimen(`)
  and the OLD interim path is genuinely gone (`GetSpecimenLedgerRoll`, `SpeciesPassiveAtomSource.DerivedAtomsFor`
  both absent) rather than merely renamed again.
- `gk-core/tests/FusionRpg.Server.Tests/SpeciesLayerPathTests.cs` (new): one test per cell of
  `layer-source-selector`'s own six-path table. Lawn general plant/zombie and a Bound unique have no
  reachable injector code from this test project, so those three are proven against
  `SpeciesLayerSource` directly with fake resolvers (the SAME mechanism `CheatState.SpeciesLayer`
  wraps, SP6.4) — this file's own contribution is the PATH-SPECIFIC SourceId-family claim, not a
  restatement of the mechanism `SpeciesLayerSourceTests` (Core.Tests) already proves. Sheet, world-turn
  and web-squad each go through their REAL production seam (`UniqueActorHubCompose.Build`,
  `RpgStore.WorldTurnHubInputsFor`, `RpgStore.SpeciesLayersForSpecimen` respectively) against a real
  minted + fused specimen. Two cross-cutting tests close the acceptance's remaining claims: a Bound
  unique's 1b follows its OWNER empire even when its side disagrees, and a save's 1b never leaks into
  a query scoped to a different save's owner.

## A real post-merge regression found and fixed while finishing this task

While verifying SP6.8, the pre-existing `FusionAptitudesBroadcastTests.cs` (SP6.5, committed BEFORE
this session's `origin/features/mega-merge` merge) started failing with `Unable to resolve service for
type 'FusionRpg.Server.PlayerConnectionRegistry'` — the merge brought in a NEW `RpgHub` constructor
dependency (`NS1.6`, another lane's work) that this test's own hand-built `WebApplication` DI container
never registered, since the file predates that change. `AptitudesInjectorBroadcastTests.cs` (also
pre-existing, but apparently already carrying the fix from a different merge path) already had
`builder.Services.AddSingleton<PlayerConnectionRegistry>();` — added the SAME line here. This is a
narrow, mechanical DI-registration fix, not a species-progression change, and is bundled into this
commit because it was found and is fully verified as part of finishing THIS task's own verify pass, per
this program's own "found and fixed" convention for a small pre-existing/adjacent issue discovered
while doing the current task.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.

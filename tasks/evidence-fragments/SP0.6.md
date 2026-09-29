# SP0.6 — Retire the eager and debug writers; `player_species` has no reader or writer in `src/`

Spec: species-mod-ledger, Migration ("the table stays in place, unread; dropping it is destructive
and not in this plan").

**Correction against the acceptance's literal text.** "`reforge-world`'s species step
(`DebugEndpoints.cs:1219-1240`) is removed" and "`ReforgeWorldEndpointTests` loses only the
species-step assertions" both presuppose the endpoint does more than species. It does not: today
`/reforge-world`'s ENTIRE body is `RpgStore.ReforgePlayerSpecies` — there is no other "step" to keep.
So the whole route is removed, not narrowed, and `ReforgeWorldEndpointTests.cs` is retired wholesale
(deleted) rather than partially trimmed — there is no route left for any of its tests to exercise.
`LawnElementResolverTests`'s Trigger4 test is similarly restated (not merely trimmed): it now proves
the STRONGER fact that the route does not exist at all, rather than that its handler "does not touch"
something.

**What was actually removed from `RpgStore.PlayerSpecies.cs`:** `MaterialisePlayerSpecies`,
`ReforgePlayerSpecies`, the public reader `ListPlayerSpecies`, and their now-orphaned private helpers
(`ListPlayerSpeciesInstanceMapUnlocked`, `ListPlayerSpeciesIdsUnlocked`, `ListSpeciesPassiveContainerIdsUnlocked`)
plus the `PlayerSpeciesRow`/`PlayerSpeciesMaterialiseOutcome` records. `ListPlayerSpecies` itself is a
reader of `player_species` with zero remaining production callers once `/reforge-world` is gone, so it
had to go too even though the acceptance text did not name it explicitly — leaving it would fail the
acceptance's own literal grep check. Kept: `EnsurePlayerSpeciesSchemaUnlocked` (schema-only, no row
read/write) — the table stays, per the spec's own instruction.

**`SpecimenMaterialisedRollTests.cs` (SP0.5's restated file) updated in this commit too**, because its
test-only bridge used `MaterialisePlayerSpecies` — now deleted. Replaced with a small raw-SQL fixture
(`InsertRealInstance`) mirroring the exact `effect_instance`/`effect_instance_atom` INSERT shape
`ExecuteFusion` itself writes, so the file keeps its narrow scope instead of growing into a second
`FusionInheritancePicksTests`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `MaterialisePlayerSpecies`/`ReforgePlayerSpecies` removed; `reforge-world`'s only content (the species step) removed | `git grep -n "MaterialisePlayerSpecies\|ReforgePlayerSpecies\|/reforge-world" src/` | zero hits except this file's own retirement doc comments (prose, not calls) and `RpgStore.Fusion.cs`'s pre-existing historical note | `RpgStore.PlayerSpecies.cs`, `DebugEndpoints.cs` |
| A grep of `src/` finds no `player_species` reader or writer | `git grep -n "player_species" src/` | only `CREATE TABLE`/`CREATE INDEX` (schema) and doc-comment mentions remain — no SELECT/INSERT/UPDATE/DELETE against the table | `RpgStore.PlayerSpecies.cs`, `RpgStore.cs:951` |
| `PlayerMaterialiseTests` retired (SP0.2 carries the facts that still matter — roll determinism/differentiation via `SpeciesRollPreview`; the rest were DAL plumbing specific to the deleted method) | `ls tests/FusionRpg.Data.Tests/PlayerMaterialiseTests.cs` | file removed | — |
| `ReforgeWorldEndpointTests` retired (no route left to test) | `ls tests/FusionRpg.Server.Tests/ReforgeWorldEndpointTests.cs` | file removed | — |
| `LawnElementResolverTests:553-560` restated: the handler cannot touch species rows because it no longer exists | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnElementResolver" --nologo` | pass 30/30 | `LawnElementResolverTests.cs` |
| No regression: sheet compose, item equip, species-mod ledger, fusion picks, restated specimen-roll tests, PlayerSpecies guard | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenMaterialisedRoll\|FullyQualifiedName~FusionInheritancePicks\|FullyQualifiedName~SpeciesModLedger" --nologo`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Sheet\|FullyQualifiedName~ItemEquip" --nologo`; `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpecies" --nologo` | pass 20/20, 49/49, 5/5 | — |
| `guard-debug-scope.py` is green; the RPG Server Debug route can no longer fabricate 1b state | `python gk-core/scripts/guard-debug-scope.py` | pass — 102 routes classified, 0 mismatches, `/reforge-world` no longer listed at all | `DebugEndpoints.cs` |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
| Build | `dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj`, all 4 touched test projects, `--nologo` | Build succeeded, 0 errors, only pre-existing unrelated warnings | — |

**Coupling note (acceptance's own):** SE4.38 (Tier B typing, batch 2) listed `player_species` as a
site to type. SP0.6 landed first — SE4.38 now has no `player_species` site left to type. This is
recorded here for the SE session (same lane, sequential); no cross-session message needed since both
waves are owned by this lane.

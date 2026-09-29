# EP4.13 (increment) - `SpeciesLevelOf`: the one species-level reader, and the Guard over it

**Row stays OPEN on one clause, with a finding below.** The reader, its Data tests and the Guard test all
landed and are green; the Guard's allow-list still names the two pre-existing aptitude sites, which is
`EP4.15`'s own deliverable. Commit `@EP4.13` (partial) - session `empire-progression-3` - branch
`cmdc/ep-3` - spec `spec-ai-empire-species.md` section "Reading"

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| One read over the re-keyed `rpg_actor_progression`, no `empire == Dave` storage branch | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpecies"` | `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs` (new) |
| A Dave read equals the pre-migration value (test 1) | same | `Passed: 4` - `A_dave_read_equals_the_row_the_progression_writer_kept` writes a species row at level 7 and asserts the reader's answer equals the row the progression API returns | same |
| Save A's crediting leaves save B at 1 (test 2) | same | `Passed: 4` - `One_saves_crediting_leaves_another_save_at_level_one` (save 1 at 12, save 2 at 1) and `Zomboss_and_the_human_are_read_separately_within_one_save` (3 vs 9 in one save) | same |
| The Guard allows only `SpeciesLevelOf` and the progression writer to make a direct species-level read (test 7) | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLevelReader"` | `Passed! - Failed: 0, Passed: 3, Skipped: 0, Total: 3` - the scan finds no offender outside {`RpgStore.EmpireSpecies.cs`, `RpgStore.Progression.cs`, `RpgStore.Aptitudes.cs`}, and a planted-drift case proves the predicate fires on a synthetic direct read while ignoring a write, a kind comparison and a parameter binding | `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLevelReaderGuardTests.cs` (new) |

**Finding for the manager (the clause that cannot pass as written yet).** Test 7 as written allows only
`SpeciesLevelOf` and the progression writer. The tree has exactly two other direct species-level reads -
`RpgStore.Aptitudes.cs:237` (`ReadActorDtoUnlocked(db, playerId, RpgActorKinds.Species, creatureTypeId)`) and
`:275` (`GetRpgActor(playerId, RpgActorKinds.Species, creatureTypeId)`) - and **converting them is EP4.15's
deliverable** ("The two `Empty` guards become level reads"), which depends on EP4.14 and designs the empire
each caller threads through. So the Guard is green now with those two files named as *debt with an owner and
a task id*, and it shrinks to the literal two-file allow-list the moment EP4.15 lands; a NEW file making such
a read fails today. Either the erratum is granted (the debt entry is acceptable while EP4.13 precedes
EP4.15), or EP4.13 and EP4.15 should be taken as one row by whoever holds the Data fence.

**Fixtures note:** the test seeds species rows with a direct INSERT, which must supply `updated_utc` (the one
NOT NULL column without a default). That is state, not a result - the reader is what each assertion exercises.

---

**Addendum (ep-4, 2026-09-21) - test 7's last clause, and the one blocker.**

EP4.15 converted both `RpgStore.Aptitudes.cs` sites to `SpeciesLevelOf`/`SpeciesLevelOfUnlocked`, so no
direct species-level read exists outside the reader and the writer any more, and the reader itself was
re-pointed at the store's wide row read (EP-F1). Measured on the EP4.14+EP4.15 commit:

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| No direct species-level read outside `SpeciesLevelOf` and the writer | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLevelReader"` | `Passed! - Failed: 0, Passed: 3, Skipped: 0, Total: 3` | `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLevelReaderGuardTests.cs` |
| The seam's own guard (EP-F1) | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~ZombossCommanderLevel"` | `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs` |

**Blocker (recorded, not worked around).** The Guard's `AllowedFiles` still names
`RpgStore.Aptitudes.cs` alongside the reader and writer. That entry now matches no read at all, so the
guard is green either way, but the row's test 7 says "only `SpeciesLevelOf` and the progression writer".
Shrinking the list needs an edit to `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLevelReaderGuardTests.cs`, which
the pipeline guard refuses as a protected guard file. Requested of the orchestrator rather than routed
around: the one-line change is `AllowedFiles` := { `RpgStore.EmpireSpecies.cs`, `RpgStore.Progression.cs` }.
Until it lands, test 7 closes in substance (no offender), not literally (an unused allow-list entry).

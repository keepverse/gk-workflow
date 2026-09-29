# EP-F1 - the second commander-level reader, removed

The EP4 batch's `RpgStore.EmpireSpecies.cs` held its own `SELECT level FROM rpg_actor_progression`, the
exact narrow shape `zomboss-commander-clock` SP7.3 keeps to one seam (`RpgStore.CommanderLevelOf`, query
text only in `RpgStore.Progression.cs`). It now projects the store's existing wide row read,
`ReadEmpireActorUnlocked` (`RpgStore.Progression.cs`), to `.Level`. The guard was not touched: no allow-list
entry, no pattern change. Commit `@EP-F1` - session `empire-progression-4` - branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The guard is green; no second narrow-shape reader anywhere in `src/` | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ZombossCommanderLevel"` | `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs` |
| The species reader still answers the same four facts | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpecies"` | `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4` | same |

**Decision (brief's literal fix text vs the code).** The row and the brief name `CommanderLevelOf` as the
seam to read through. `CommanderLevelOf` returns the `kind='player', type_id=0` commander row, which is not
a species level, so it cannot answer `SpeciesLevelOf`; the spec's own code-style block
(`spec-ai-empire-species.md` "Code style") prescribes exactly the fix landed here. The guard's actual
constraint - one holder of the narrow query text - is satisfied either way; nothing was relaxed.

**NOT proved:** that the two Aptitudes sites no longer need a direct read - that is EP4.15, and until it
lands `SpeciesLevelReaderGuardTests` still names `RpgStore.Aptitudes.cs` as debt.

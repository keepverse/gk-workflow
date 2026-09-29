# SE4.13 — `SaveOfRunUnlocked` / `SaveOfMatchUnlocked`

Spec: docs/architecture/solid-enforcement/spec-save-identity.md (G4/X11)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `GetRunPlayerId` renamed and typed to `SaveOfRunUnlocked`, its callers moved, **no second lookup** | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveOfRun\|FullyQualifiedName~SaveEmpires" -v q --nologo` | pass — 8/8; the helper now returns `SaveId?`; `git grep GetRunPlayerId` in `src/` returns nothing (both callers read `SaveOfRunUnlocked(db, …)?.Value`, still the one lookup on `runs.player_id`) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` |
| `SaveOfMatchUnlocked` reads `runs.match_key → player_id` | same filter | pass — `An_unknown_or_blank_match_resolves_to_no_save_never_the_current_one` | `RpgStore.cs` |
| Unknown run or match → `null`, never the current save; tests for both | same filter | pass — both tests assert a live current save (`IsLiveSave(1)`) exists while the unknown run/match still resolves to `null` | `gk-core/tests/FusionRpg.Data.Tests/Saves/SaveOfRunTests.cs` |
| Path-owned verification | `dotnet test tests\FusionRpg.Data.Tests -c Release -v q --nologo --filter "Category!=DiskSemantics&Category!=Heavy"` | pass — **1555/1555**, exit 0 (the plan's `data` selection for `RpgStore.cs`) | gate recorded |

Public wrappers `SaveOfRun(long)` / `SaveOfMatch(string?)` open their own connection, matching the
`EffectiveSpeciesAllocation` → `…Unlocked` pair this store already uses; the unlocked forms are what
SE4.21/SE4.22 and the progression programs call inside their transactions.

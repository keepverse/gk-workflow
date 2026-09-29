# ST4.5c — trigger frequencies as seed data (the frequency half of the zeroed price)

**Status: done.** Manager ruling on the ST4.5a diagnosis, item (1): *"Trigger frequencies become SEED
DATA beside coefficients.v1.json (e.g. gk-data/packs/fusion/data/seed/power/trigger-frequencies.v1.json, values taken
verbatim from PowerTables.Authored() so nothing retunes), imported by the same seed path into
power_trigger_frequency. Predicate frequencies: same treatment if they have the same gap -- check."*

## What changed

| File | Change |
|---|---|
| `gk-data/packs/fusion/data/seed/power/trigger-frequencies.v1.json` | new — the five rows of `PowerTables.Authored()`, verbatim (`OnDamageDealt 60`, `OnDamageTaken 40`, `OnSpawn 4`, `OnDeath 6`, `OnTimer 12`) |
| `gk-core/src/FusionRpg.Core/Effects/Atoms/AtomSeedFile.cs` | new `SeedEntryKind.TriggerFrequency`, `SeedContent.TriggerFrequencies`, `ReadTriggerFrequency`, the `power-trigger-frequency` kind spelling |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Power.cs` | `WriteTriggerFrequenciesUnlocked` — the sibling of the coefficients writer, same overlay-and-skip-when-unchanged discipline |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Import.cs` | `ValidateFrequencies` + the write call, so `ImportContent` actually reads `content.TriggerFrequencies` (`SeedContentCoverageTests` enforces this by reflection) |
| `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj` | a copy rule for `gk-data/packs/fusion/data/seed/power/*.json` — the same missing-copy-rule defect the actions/loot/items/structures rules above already name |
| `tests/FusionRpg.Core.Tests/Atoms/AtomSeedFileTriggerFrequencyTests.cs` | 4 reader tests, including the non-positive-rate refusal |
| `gk-core/tests/FusionRpg.Data.Tests/Power/PowerTableSeedTests.cs` | 4 import tests, including the end-to-end "a triggered atom no longer prices at 0" |

`perMinute` must be positive, at both boundaries (reader and import): `Conditionality` multiplies a
triggered atom's price by `perMinute/60`, so a zero row *is* the silent 0 this kind exists to close.

## Predicate frequencies — checked, and they do NOT have the gap

`power_predicate_frequency` is empty in the deployed DB, but unlike the frequency table that is not a
defect: `PowerTables.Authored()` passes **no** predicate frequencies either, and
`PowerTables.PredicateFrequencyOf` returns `PowerMath.One` (`1000‰`) for an unlisted leaf/arg — its own
doc calls that "the safe default: an unauthored row can only ever FAIL to give a deserved discount,
never hand out an undeserved one". So an empty predicate table prices *neutrally*, not at zero, and
there is no authored value to seed. No change; recorded here because the ruling asked for the check.

## Verification — no golden and no budget moved

| Command | Result |
|---|---|
| `dotnet test tests\FusionRpg.Core.Tests -c Release --verbosity minimal` | **14196/14197** — the one failure is the named CRLF worktree artifact `DungeonLootTableSeedFileTests` (main 1230 CR bytes vs worktree 0, measured in ST4.5b) |
| `dotnet test tests\FusionRpg.Data.Tests -c Release --verbosity minimal` | **1606/1607** — the one failure is `CreatureSpeciesImportCliTests.A_real_import_against_the_real_committed_tree...` ("904 species stale against gk-data/packs/fusion/data/generated/creatures"): `gk-data/packs/fusion/data/generated/creatures`, `gk-data/packs/fusion/data/seed/creatures`, `gk-forge/tools/CreatureSpeciesImport` and `RpgStore.Creatures.cs` are **unmodified vs HEAD** (`git status --porcelain` empty for all four), so the drift is committed, not mine, and not a worktree artifact (906 files present, identical to HEAD) |
| `dotnet test tests\FusionRpg.Server.Tests -c Release --verbosity minimal` | **534/552** — all 18 failures are the pre-existing wall below |
| `dotnet test tests\FusionRpg.E2E.Tests -c Release --verbosity minimal` | **226/226** — the host-booting project, so the seed import really ran and nothing moved |
| focused: `--filter "FullyQualifiedName~PowerTableSeed\|...~SeedContentCoverage\|...~ContentBoot"` | **8/8** |
| focused: `--filter "FullyQualifiedName~AtomSeedFileTriggerFrequency"` | **4/4** |

## Pre-existing red found while running the boundary: Server.Tests, one cause

`dotnet test tests\FusionRpg.Server.Tests` fails **18** of 552, and every one of them is the same
cause: `System.InvalidOperationException : ActionBaseTuningHub.Configure(...) has not run. Read
data/tuning/action-base.v{n}.json at startup — there is no built-in default to fall back to.`
(`AptitudeChannelModsTests.RealBattle_...` and `RolledItemEquipRuntimeTests.An_equipped_items_...`
surface it directly; the `DelveBattleSession*` classes show its consequence — the fight task `Faulted`
instead of `Canceled`, or "condition never became true within the test timeout").

The cause is a gap in that assembly's own bootstrap, and it is provable without running anything:
`grep -n ActionBaseTuningHub gk-core/tests/FusionRpg.Server.Tests/**` returns **zero** hits, while
`ActionBaseTuningHub.Tuning` is read on the basic-attack path (`BasicAttack.cs:381`).
`PowerAndAptitudeTuningTestBootstrap`'s `[ModuleInitializer]` covers Power/Aptitude/DerivedStatPolicy
and a list of battle hubs, never this one. AE1.1/AE2.2 added the hub and wired `Program.cs`,
`RpgHost.cs`, `Core.Tests`, `Data.Tests` and `Injector.Tests` — **not** `Server.Tests`. This lane's own
`verify-change` never selected the `server` project (ST4.5b's run fell at `core` first), so the wall
was invisible until this task ran the boundary the manager asked for.

This is a lane-A-adjacent gap (AE owns the hub) and `gk-core/tests/FusionRpg.Server.Tests/**` is outside this
session's `paths`, so it is recorded as a finding for the manager rather than fixed here. **None** of
the 18 mentions power, a budget, or a golden — so the pricing question this boundary was run for is
answered: no budget moved.

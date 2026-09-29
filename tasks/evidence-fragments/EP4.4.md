# EP4.4 — Publish `species-build` (sequence order 5): `freeRespecsPerEmpireLevel`; tuning field; `EmpireLevelTuning` wiring

Commit `@EP4.4` · session `empire-progression-3` · branch `cmdc/ep-3` · spec `docs/architecture/empire-progression/spec-respec-free-counter.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The key is published at the working value 1 | `python gk-core/tools/tuning/publish.py species-build --label "respec-free-counter (R18): freeRespecsPerEmpireLevel" --add-key ':freeRespecsPerEmpireLevel=1'` | `freeRespecsPerEmpireLevel ADDED`; `published species-build (v5 -> v6, 1 change(s)); v5 stays on disk for revert`; exit 0 | `gk-core/data/tuning/species-build.v6.json` (new; v1–v5 untouched) |
| It is a `long`, at least 0, and a missing key is a load rejection | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildTuning"` | `Passed! - Failed: 0, Passed: 22, Skipped: 0, Total: 22` — incl. `The_shipped_v6_file_publishes_the_free_empire_respec_grant`, `A_v6_document_missing_the_grant_is_refused_naming_it`, `A_v6_document_soiling_the_grant_is_refused` (−1 and 1.5 refused; **0 accepted**), `A_pre_v6_document_without_the_grant_still_loads_and_states_the_absence` | `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs` (`FreeRespecsPerEmpireLevel`, `FreeRespecsRequiredFromVersion = 6`, `FreeRespecs(...)`) |
| `respecFreeCount` is never published | same | `Passed: 22` — the shipped document contains no `respecFreeCount` substring and the tuning type declares no member whose name is `respecFreeCount` (case-insensitive) | same |
| Every pin moves | `rg -n "species-build\.v[0-9]+\.json" src tools tests --glob "*.cs"` | 7 files / 9 mentions now read `species-build.v6.json` and **zero reads of v1–v5 remain**. The only v1 mentions left are two historical comments about where a value originally came from (`PassiveTreeTuning.cs:52`, `AptitudeAutoAssign.cs:87`), which is the same call EP4.2 made for its four comment-only mentions | `gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/_TempSeedSpecies`, `gk-forge/tools/CreatureBuildPlanGen`, `gk-forge/tools/ProveHubCombat`, 3 Core test files |
| `CreatureBuildPlanGen --check` stays byte-identical | `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check` (also as `script: gen-build-plan` inside the boundary run) | `--check: clean, 904 species match .../_species-build-plan.json and .../_species-build-measure.json`, exit 0 | — |
| The host builds `EmpireLevelTuning` from this key | read + `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | `Program.cs` parses `species-build.v6.json` ONCE into a local, configures `SpeciesBuildTuningHub` from it, then builds `EmpireLevelTuningHub` from the same value (a null there throws, because only a pre-v6 document returns null and v6 must carry the key). Server suite `772/772`, exit 0 | `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/src/FusionRpg.Core/Progression/EmpireLevelGrants.cs` (`EmpireLevelTuningHub`) |
| The credit actually pays the grant now (EP4.3's deferred half) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireLevel"` | `Passed! - Failed: 0, Passed: 8, Skipped: 0, Total: 8` — every queued `EmpireLevelUpEvent` carries one `FreeEmpireRespec` grant of 1 | `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs` |
| Path-owned boundary | `.\scripts\verify-change.ps1 -Paths @(<the 15 changed paths>) -Session empire-progression-3` | exit 1, entirely the known TVB-F6 misreport: `DAL GUARD OK`, `TEST SUBSTRATE GUARD OK`, `script: gen-build-plan` clean (904 species), all twelve core shards green (`12764`, `15`, `498`, `31`, `1351`, `30`, `210`, `7`, `12`, `238`, `4`, `9`), then the Data sharded runner printed its shard counts with no failure line and an empty exit code, aborting before `test: e2e` and `test: server` | — |
| The steps that abort skipped, run directly | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "Category!=DiskSemantics&Category!=Heavy"`; `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release`; `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release`; `dotnet build gk-forge/tools/_TempSeedSpecies gk-forge/tools/CreatureBuildPlanGen gk-forge/tools/ProveHubCombat -c Release` | `1745/1745 exit 0`; `231/231`; `772/772`; `Build succeeded` ×3 | — |
| The Core consumers of this tuning still pass | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuild\|FullyQualifiedName~BuildFavour"` | `Passed! - Failed: 0, Passed: 56, Skipped: 0, Total: 56` | — |

**Where the wiring lives, and why it is a Core hub rather than a store property.** The tuning is parsed into a local in
`Program.cs` before any `RpgStore` exists (the store is DI-constructed ~270 lines later), so a store slot could only be filled by a
second read of the same file. `EmpireLevelTuningHub` is the repo's own hub convention applied to this one number: the host configures
it, the Data credit reads it, one read of one key. **Unconfigured means an empty grant list** — the pre-EP4.4 behaviour, and what a
host that never wired the key gets; it is deliberately not a throw, because the credit runs inside a transaction and a host wiring
gap must not roll back a player's XP. It is also not a silent default for a MISSING KEY: the loader refuses a v6+ document without
`freeRespecsPerEmpireLevel` outright (tunables-ssot.md T5), so the only route to "no grants" is a host that never asked. The three
test bootstraps configure it with the shipped 1, so the tests exercise the granted path.

**One stale pin moved with the publish, deliberately.** `The_shipped_v5_file_publishes_the_caps_chosen_from_the_current_measure`
read the SHIPPED file and asserted its version was 5; a shipped file's version moves with every publish, so it is renamed
`The_shipped_file_publishes_the_caps_...` and asserts `Version == 6`. The per-version contracts of v1–v5 stay pinned by that file's
own `VersionJson(n)` cases, which is exactly why each superseded version is kept on disk.

**Not proved** (owner of the next step):
- The stock itself: nothing spends or stores a free respec yet. EP4.5 adds `rpg_empire_free_respec_ledger` (a migration before the
  code that writes it — H2) and applies each queued grant in the level-change transaction; this row only prices it.
- The wire shape: `EmpireLevelUp`'s broadcast (with `freeRespecStock`) is EP4.7's.
- `species-build` has one more prospective publisher in the plan's own table (no number is pinned above v6), so the next publisher
  takes v7 on top of this file — the pins moved here are the ones it will move again.

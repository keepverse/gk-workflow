# NS5.6 — Publish catalog v2 with both load sites (H7)

| Criterion | Command | Result |
|---|---|---|
| v2 via `publish.py` adds the eight `world-notify` ids + `territory.lost`, `promotions.toast = TOAST_TIER`; `Program.cs` and `catalog.ts` move to v2 in the same commit (H7) | `python gk-core/tools/tuning/publish.py notification-catalog --add-category ... --promote-toast ...` then `grep -rn notification-catalog.v1\|v2` (every reader) | v2 published with 9 rows; `Program.cs:382` and `catalog.ts:4` both load `v2` — no reader left on v1 except `NotificationCatalogTests.cs`'s own deliberate historical-v1 test (documented) |
| migration-equivalence: `promotions.toast == TOAST_TIER`, each of the 8 ids keeps its old default channel | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/catalogMigration.test.ts` | `Test Files 1 passed, Tests 2 passed` |
| Guard coherence join: every classifier category registered with domain `world`, every `world` category emitted by a row or the forecast | `dotnet test tests\FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~WorldNotifyCatalogCoherence"` | `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2` |
| coverage guard (NS2.7) green over v2 | `npx vitest run src/shell/notify/format/coverageGuard.test.ts` | `Test Files 1 passed, Tests 10 passed` — real dynamic cases now run (v2 is no longer empty) |
| `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"` | | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7` |
| `guard-dal.ps1` | | `DAL GUARD OK` |
| scoped `verify-change.ps1` (added `notification-catalog.v2.json` to the `notify-tuning` registry row it was missing from) | `dotnet test tests\FusionRpg.Core.Tests -c Release` (module boundary) | `Passed! - Failed: 0, Passed: 14335, Total: 14335` |
| `Program.cs` -> `server-fallback` boundary | `dotnet test tests\FusionRpg.Server.Tests -c Release` | `Passed! - Failed: 0, Passed: 604, Total: 604` |

**Two real gaps the coverage guard caught while wiring v2** (not part of ask A6's own hint list):
`growth.pulse`, `develop.completed`, `development.raised` (`GrowthPhases.cs:65,132,141`) had no
`playbackTable.ts` row at all — the classifier (NS5.1) already mapped them, so once v2 made the
`growth` category real, the coverage guard's live render check failed on the fallback marker.
Added the three rows in the same commit (reviewed inventory bump 23→26 event prefixes,
`playbackTable.test.ts`'s own pinned closed-vocabulary count). `growth.pulse`'s wording avoids the
literal word "growth" (the category id itself), matching the coverage guard's raw-token check the
same way `sustain`/`halt` are already excluded from the file's blanket scan.

Also updated two now-stale wave-1/4 assertions that assumed v1's empty catalog:
`catalog.test.ts` ("v1 ships empty" → a registered-but-unpromoted category still defaults rail,
plus a new test that `loam.shortfall` is now toast) and `channelSettings.test.ts` (same shape).
`coverageGuard.test.ts`'s own direct catalog import switched to v2 (a SEPARATE reader from
`catalog.ts` — missing this would have left the guard silently checking an orphaned empty file).
`NotificationCatalogContractTests.cs` (the redundant C#-side structural guard) switched to v2 for
the same reason; `NotificationCatalogTests.cs`'s `The_shipped_v1_file_parses_as_a_valid_empty_catalog`
stays on v1 deliberately — it is testing v1's own eternal shape, not "whatever is current".

**Honest finding (unrelated, not caused by this task):** the whole `FusionRpg.Guard.Tests` project
run (triggered once because `Program.cs` also maps into it via `verify-change.ps1`'s project-level
boundary) failed 2 of its own tests, `ClassSystemBaselineRegenTests.EveryBaselineParsesAndCarriesMeta`
and `...RegeneratingTwiceReproducesIdenticalPayloads` — both invoke `CombatSim`/`DominanceBaseline`
`.exe`s from their `bin/Debug/net8.0` output, which had never been built in this worktree (only
`Release` existed). Building `gk-core/tools/CombatSim` in Debug unblocked the first step; `DominanceBaseline`
needs the same treatment (not done here — out of scope for a notification-catalog change; this
worktree's Debug-config gap is a pre-existing environment issue unrelated to any file this task
touched, confirmed zero relation to `ClassSystemBaselineRegenTests.cs`/`regen-class-system-baselines.ps1`).
Verified in isolation instead: `notify-catalog-guard`'s own 7 tests all pass on a focused filter.

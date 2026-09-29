# NS6.4 — Publish catalog v3 with both load sites (H7)

| Criterion | Command | Result |
|---|---|---|
| v3 via `publish.py` adds `cache.created` and `cache.decayed` (domain `corpse-cache`), no promotion; published from the current version | `python gk-core/tools/tuning/publish.py notification-catalog --add-category ... --add-category ...` | v3 published (v2 -> v3, 3 changes); `promotions` unchanged (both categories default to rail, per spec §Objective — neither toast nor critical) |
| `Program.cs` and `shell/notify/catalog.ts` move to v3 in the same commit (H7); coverage guard and Guard catalog contract green over v3 | every reader grepped and switched: `Program.cs`, `catalog.ts`, `coverageGuard.test.ts`, `NotificationCatalogContractTests.cs`, `WorldNotifyCatalogCoherenceTests.cs`, `verification-boundaries.v1.json`'s `notify-tuning` row | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"`: `7/7`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldNotifyCatalogCoherence"`: `2/2`; `cd web\fusion-rpg-web; npx vitest run src/shell/notify src/stages/world/cacheClaim src/stages/world/notify src/stages/world/playbackTable.test.ts src/features/notices src/lib/bus`: `42 files, 266 tests` |
| `guard-dal.ps1`; `npm run build` | | `DAL GUARD OK`; `✓ built in 11.81s` |

The coverage guard now genuinely exercises the `corpse-cache` domain end to end for the first time
(`cacheNotifyTranslator`'s `samples()` render through the real v3 catalog, not a fabricated one).
`NotificationCatalogTests.cs`'s one deliberate v1-specific test stays on v1 (unaffected — a
different, historical assertion, not "whatever is current").

# NS1.4 — Host loads (Server) and typed web catalog

| Criterion | Command | Result |
|---|---|---|
| `Program.cs` loads both files beside the other tuning loads, registers the two Hubs; injector never loads either | code review | inserted right after `charmAttunementTuning` (the tail of the tuning prelude), before `builder.Services.AddSingleton(new RpgStore(...))`; `FusionRpg.Injector/**` has no reference to `FusionRpg.Core.Notify` |
| `shell/notify/catalog.ts` exports `NotifyCategoryId`, `NotifyChannel`, `NotifySeverity`, `defaultChannelOf` (unpromoted -> rail), TS mirror of the wire DTOs | code review | matches the spec's own code block; `NotificationItem`/`NotifyArg` added per this task's own acceptance |
| web test + build | `cd web\fusion-rpg-web; npx vitest run shell/notify/catalog` | `Test Files 1 passed (1)`, `Tests 2 passed (2)` |
| | `npm run build` | `✓ built in 10.18s`, exit 0 (pre-existing >500kB chunk warnings, unrelated - owner ruling 2026-09-16 withdrew the entry-chunk size gate) |
| C# side still green after the Program.cs edit | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` | `Passed! - Failed: 0, Passed: 561, Skipped: 0, Total: 561` - Server.Tests boots the whole `Program.cs`, so this doubles as the smoke test for the two new Configure calls |

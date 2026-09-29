# NS6.2 — `CacheNotificationSource` on the world-turn pump

| Criterion | Command | Result |
|---|---|---|
| window `[t, t+1]`, keys `cache:{id}:created` / `cache:{id}:decay:{tick}`, `worldTurn = ctx.ResolvedTurn`, recipient `ctx.Header.PlayerId`; a real `CommitWorldTurn` tick falls inside the window (pinned by test); overlapping runs store each event once, including after the first row was pruned at `retainPerCategory = 1` | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~CacheNotifySourceTests"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` |
| emptying tick → `important` with subject `cache:{id}:emptied`; survivors → `routine` with subject `cache:{id}`; no destruction → nothing | same run | `A_tick_that_empties_the_cache_is_important_with_an_emptied_subject_a_partial_loss_is_routine`, `A_tick_with_no_destruction_yields_nothing` (real retry-until-destroyed loops, matching `CacheDecayTests.cs`'s own convention at 994/1000 survival, never assumed) |
| `guard-dal.ps1`; determinism (Notifications suite run twice) | | `DAL GUARD OK`; `43/43` both runs |
| no regression | full `Core.Tests` / `Server.Tests` | `14335/14335`, `610/610` |

**Real gap found and fixed en route:** the spec's own `Args.Count(...).Count(...).Place(tick)` code
style implied a fluent args builder that did not exist yet — built as `NotifyArgsBuilder`/`Args`
(`FusionRpg.Core.Notify`), the FIRST real producer of a `Ref`-kind `NotifyArg`. Discovered and fixed
a real wire-shape bug while building it: `NotificationPublisher.SerializeArgs`'s
`JsonSerializer.SerializeToElement(a.Value)` call carries no camelCase naming policy, so a named
PascalCase record's properties would have serialized `RefKind`/`Id`, never matching the web's
`{refKind, id}` read (`kit.ts`'s `ref()`). Fixed by building the ref value as an anonymous object
with pre-lowercased field names instead — proven end to end by
`A_world_sector_place_carries_a_ref_whose_wire_shape_is_camelCase`, which reads the value back
through the real publisher + store, not just the in-memory object.

`Program.cs`'s placeholder `AddSingleton<IEnumerable<IWorldTurnNotificationSource>>(Array.Empty<...>())`
registration is replaced with a plain `AddSingleton<IWorldTurnNotificationSource, CacheNotificationSource>()`
— the textbook DI pattern that lets `IEnumerable<T>` collect every registered source automatically,
so a future `world-notify-source` registration is one more line, never touching this one or the pump.

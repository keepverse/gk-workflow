# NS3.1 — Core drafts and the publisher's contract validation

| Criterion | Command | Result |
|---|---|---|
| `NotificationDraft`/`NotifyArg` in Core, no transport types | code review | `gk-core/src/FusionRpg.Core/Notify/{NotificationDraft,NotifyArg}.cs` - plain records, `NotifyArg.Value` is `object`, never `JsonElement` |
| `NotificationContract.Validate` refuses an unregistered category, an undeclared key, a severity above `CeilingOf`, an unknown arg kind - each throws `NotificationContractException` naming category+key | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~Notifications.NotificationContractTests"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` |

`NotificationCatalogHub`/`NotificationTuningHub` are process-wide statics every notify-service test
configures with its own scenario; every test class below lives in the serialized `[Collection("NotificationHub")]`
(extra rigor) rather than risk a cross-class race.

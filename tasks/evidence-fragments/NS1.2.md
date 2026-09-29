# NS1.2 — Closed enums and wire DTOs in Contracts

| Criterion | Command | Result |
|---|---|---|
| `NotificationDtos.cs` holds the closed enums + DTOs, `Seq`/`Rev`/`PlayerId` `long`, `WorldTurn` `int?` | code review | `NotifySeverity`(3), `NotifyArgKind`(5), `NotifyRefKind`(6), `NotifyDelivery`(2); `NotificationDto`/`Batch`/`StateChanged`/`StateChange`/`NotifyArgDto`/`NotificationEvents` match the spec's own code block verbatim |
| enums serialize as camelCase strings, round-trip proven | `dotnet test tests\FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~Notify"` | `Passed! - Failed: 0, Passed: 36, Skipped: 0, Total: 36` (`NotificationDtoTests.cs`, includes a full round-trip per enum + DTO) |
| member counts pinned as closed vocabularies, with the reason | test source | `NotifySeverity_has_exactly_3_members` etc. name "a new member is a reviewed change" |
| whole-project regression | `dotnet test tests\FusionRpg.Core.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` (verify-change.ps1's own module fallback) | `Passed! - Failed: 0, Passed: 14295, Skipped: 0, Total: 14295` |

**No existing Contracts DTO used a camelCase string enum converter** (checked: zero
`JsonStringEnumConverter` hits in `src/`), so `NotifyCamelCaseEnumConverter` is new, non-generic
(Contracts targets `net6.0`; the generic `JsonStringEnumConverter<T>` needs net7+), applied per
enum via `[JsonConverter(...)]` rather than a global `JsonSerializerOptions` change.

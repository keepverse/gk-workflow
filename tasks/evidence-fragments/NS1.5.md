# NS1.5 — Guard: C#/TS enum parity and no self-promotion over the real files

| Criterion | Command | Result |
|---|---|---|
| Guard test reads `NotificationDtos.cs` and `catalog.ts`, asserts identical members for every shared enum | `dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~NotificationCatalog"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7` (4 enum-parity theory cases: `NotifySeverity`, `NotifyArgKind`, `NotifyDelivery`, `NotifyRefKind`; `NotifyChannel` correctly excluded - web-only, no C# side) |
| over the real catalog: no row has channel/severity; every `promotions.*` id registered; `critical` subset of `toast`; every row has non-empty `domain`+`messageKeys` | same run | `No_category_row_carries_a_channel_or_a_severity_field`, `Every_category_has_a_non_empty_domain_and_messageKeys`, `Every_promotions_id_is_a_registered_category_and_critical_is_a_subset_of_toast` green over the shipped (empty) v1 file; no category count asserted |

This test project carries no `ProjectReference` (by design), so it reads the shipped files as
text/JSON directly rather than through `NotificationCatalogLoader`/`catalog.ts` - a redundant check
independent of either parser having a bug.

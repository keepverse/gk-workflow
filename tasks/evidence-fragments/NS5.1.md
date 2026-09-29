# NS5.1 — Core classifier: the closed table and recipient rules

| Criterion | Command | Result |
|---|---|---|
| `WorldTurnNotificationClassifier` maps each row of spec §2 (except `claim.lost:`) to `(category, severity, rule, subjectKey)`, longest prefix wins, unmapped → `null` | `dotnet test tests\FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~WorldTurnNotification"` | `Passed! - Failed: 0, Passed: 23, Skipped: 0, Total: 23` |
| each row tested with an entry built from the same prefix literal and argument shape as its cited producer (verified against real call sites via agent research); closed enum `WorldRecipientRule` (5 members) | same run | one test per producer line (`Loam_shortfall_...`, `Legion_runway_...`, `Supply_restored_...`, `Growth_lines_...`, `Build_started_...`, `Intel_new_...`, `Loam_lost_...`, `Every_command_dropped_reason_...`, `A_sector_battle_...`, `A_lane_battle_...`) all pass |
| unmapped: `calendar`, `command.accepted`, `legion.starved:`, cache-retrieval outcomes, `claim.lost:` (A3) → `null` | same run | `Calendar_is_unmapped`, `Command_accepted_is_unmapped`, `Legion_starved_is_unmapped_...`, `Cache_retrieval_outcomes_are_unmapped`, `Claim_lost_is_unmapped_pending_ask_A3` all pass |

The release forecast's `loam.release` row is deliberately NOT part of this table (documented in the
class doc comment): it is never classified from a `TurnReportEntry` — `WorldReportNotificationSource`
(NS5.3, blocked on A2) calls `LoamForecast.WillRelease` directly. `SubjectKey` picks the id that
names the real-world thing a notification is about (R-N5), which is not always the field the
recipient RULE reads (e.g. `legion.topup:`'s rule is `Audience` but its Subject IS the faction id,
so its key is `faction:{Subject}`; `supply.restored`'s Subject is instead the legion entity id) —
each choice is reasoned in the row table's own comment.

# NS5.3 — `WorldReportNotificationSource`: recipients, dedup keys, release forecast

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| recipients resolved per rule through `IWorldFactionSaves` (v1: the `Player` faction -> `header.PlayerId`, AI -> nothing); an enemy watching my shortfall sector gets no `loam.shortfall`; a `battle` reaches exactly the factions the turn GET shows it to (same moved function); a dropped order reaches only its commander | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify"` | `Passed! - Failed: 0, Passed: 10, Skipped: 0, Total: 10` — `An_enemy_watching_my_shortfall_sector_gets_no_notification_though_it_sees_the_line` (asserts `WorldReportVisibility.VisibleTo(entry, "wild", …)` is TRUE and the only draft goes to the save), `A_battle_line_reaches_exactly_the_factions_the_turn_GET_shows_it_to`, `A_dropped_order_reaches_only_its_commander` (real `SubmitWorldCommand` rows for `dave` and `wild`), `An_AI_factions_own_shortfall_yields_no_draft`, `A_sector_owned_line_reaches_the_current_owner_only`, `An_audience_line_reaches_only_its_audience` | gk-core/src/FusionRpg.Server/Notifications/WorldReportNotificationSource.cs, gk-core/src/FusionRpg.Server/Notifications/WorldFactionSaves.cs |
| keys `world:{worldId}:t{turn}:e{index}` over the persisted report and `…:release:{sectorId}`; the same report classified twice yields identical keys; `loam.release` only when `IsLatestResolved` | same run | `A_loam_shortfall_reaches_its_save_and_is_keyed_by_its_persisted_index` (index `e1` after an unmapped calendar line at `e0`), `The_same_report_classified_twice_yields_identical_keys` (`first == second`, 3 keys), `The_release_forecast_is_published_only_for_the_latest_resolved_turn` (single `loam.release` at `t2` for the latest; empty for the lagging turn), `A_trimmed_turn_yields_nothing` | gk-core/src/FusionRpg.Server/Notifications/WorldReportNotificationSource.cs |
| DI: the source and the faction->save seam are registered in the real host | `.\scripts\verify-change.ps1 -Paths 'gk-core/src/FusionRpg.Server/Notifications/WorldReportNotificationSource.cs','gk-core/src/FusionRpg.Server/Notifications/WorldFactionSaves.cs','gk-core/src/FusionRpg.Server/Program.cs','gk-core/src/FusionRpg.Contracts/NotificationDtos.cs','gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldNotifySourceTests.cs' -Session notification-ssot-20260920` | `DAL GUARD OK`; scopes `guard: dal`, `test: core`, `test: server`; core scope `Failed: 4, Passed: 14903, Total: 14907` (pre-existing, see NS5.2); **re-read 2026-09-21**
on the integration head 4bce1fe5: `Failed: 4, Passed: 15047, Total: 15051` — the same four, none of
them in the registry's `knownRed` | gk-core/src/FusionRpg.Server/Program.cs |
| the boundary's server scope, run directly to keep its tally | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | `Passed! - Failed: 0, Passed: 751, Skipped: 0, Total: 751, Duration: 2 m 34 s` | — |

**Decision recorded in code:** the forecast passes `ceded: null`. Orders are filed against the OPEN
turn, so right after a commit there is no pending `cede` to read; the `/state` panel reads a live one.
The forecast already sent was true when it was sent (spec §1), and the code comment says so.

Also corrected `NotifyArgDto`'s own doc comment, which said `DomainToken = string`: shared code never
reads it, and the world domain's token is the entry object (`worldTranslator.ts` owns that shape)
while the cache domain's is a bare place-kind string.

**NOT proved:** the forecast half runs over a synthetic starving world state (the shipped template has
no release candidate at turn 0), so it proves the rule, key and gating — not a real committed turn's
forecast; the commit -> one routed batch end-to-end path is NS5.12; no live probe (NS5.13).

**Correction 2026-09-21 (head 287a3256):** the Core scope is green now — `Passed! 13180/13180` for the
whole project, and `41/41` for the three classes whose four reds this fragment recorded.

**Superseded 2026-09-21 by tvb58's Core test-project split:** see the post-split re-measure in `tasks/evidence-fragments/NS-reverify-20260921.md` Addendum 8 — this lane's tests stayed in `gk-core/tests/FusionRpg.Core.Tests` (83/83 on our scope), while the project total is now 12,704 with 2,404 more across eleven split projects.

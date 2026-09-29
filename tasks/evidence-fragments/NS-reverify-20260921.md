# NS merged-head re-verification (2026-09-21, head `8ad4620d`)

This lane's 12 landed rows were re-run at the merged head after three merges, because the queue's
remaining rows are all externally blocked and the strongest available check is "does what landed still
pass". Every number below is from a command run in this session.

| Scope | Command | Numbers printed |
|---|---|---|
| Core — the fog rule and the classifier | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldReportVisibility\|FullyQualifiedName~WorldTurnNotification"` | `Passed! - Failed: 0, Passed: 30, Skipped: 0, Total: 30, Duration: 86 ms` |
| Data — the notification store | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"` | `Passed! - Failed: 0, Passed: 11, Skipped: 0, Total: 11, Duration: 915 ms` |
| Server — routing, publisher, pump, both sources, endpoints | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify\|FullyQualifiedName~CacheNotify\|FullyQualifiedName~Notification\|FullyQualifiedName~PlayerRouting"` | `Passed! - Failed: 0, Passed: 63, Skipped: 0, Total: 63, Duration: 9 s` |
| Web — the rail, the feed, the world stage, the volume rows | `cd gk-web/web/fusion-rpg-web; npx vitest run src/shell/notify src/stages/world src/ui/volumeMatrix` | `Test Files 98 passed (98)`, `Tests 863 passed (863)` |
| Web build (type errors fail it) | `cd gk-web/web/fusion-rpg-web; npm run build` | `✓ built in 8.16s` |
| Boundary command over this lane's landed C# paths | `.\scripts\verify-change.ps1 -Paths 'gk-core/src/FusionRpg.Core/World/Intel/WorldReportVisibility.cs','gk-core/src/FusionRpg.Server/Notifications/WorldReportNotificationSource.cs','gk-core/src/FusionRpg.Server/Notifications/WorldFactionSaves.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Notifications.cs','gk-core/src/FusionRpg.Server/RpgHub.cs','gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldNotifySourceTests.cs','gk-core/tests/FusionRpg.Core.Tests/World/Intel/WorldReportVisibilityTests.cs' -Session notification-ssot-20260920` | `DAL GUARD OK` · `TEST SUBSTRATE GUARD OK` · Core scope `Failed! - Failed: 4, Passed: 15047, Skipped: 0, Total: 15051, Duration: 58 s` |

**One procedure fact this re-run establishes:** `verify-change` **aborts after the Core scope's red**, so
the `data`/`server` scopes it planned never ran in that command — which is why this lane's per-row
evidence quotes the direct scoped runs above rather than the boundary command's exit status. The four
Core reds are pre-existing, are the same four as before the merges, are **not** in `knownRed`, and the
manager's own board already routes them (`ISG-F1`, registration `TVB-F9`).

**Still unmapped:** no FE path can be verified by the boundary command — `gk-web/web/fusion-rpg-web/**` has zero
rows in `gk-core/scripts/verification-boundaries.v1.json`, so the command throws
`VERIFICATION BOUNDARY MISSING`; the FE half above is the row's own `vitest` + `build` lines (filed as
`NS-fence-3` here and `TVB-F1` by the boundary program).

**NOT proved:** no live probe (G2's blocker is unchanged: no real world-creation route), and the full
suite is still `not_run` — three attempts, each killed with no output.

## Addendum — the catalog-coherence contracts (2026-09-21, head `59ea9964`)

The table above filtered Core by the fog rule and the classifier, which silently skipped this program's
own catalogue-coherence contracts (`WorldNotifyCatalogCoherence`, `NotificationCatalog`) — the joins
`NS5.6`/`NS6.4` own (every classifier category registered with domain `world`, every `world` category
emitted, `promotions.toast == TOAST_TIER`, both hosts on the same `vN`). Closed here:

| Scope | Command | Numbers printed |
|---|---|---|
| Core — catalogue coherence + parser | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldNotifyCatalogCoherence\|FullyQualifiedName~NotificationCatalog"` | `Passed! - Failed: 0, Passed: 17, Skipped: 0, Total: 17, Duration: 46 ms` |
| Guard — the C#/TS contract join over the real catalogue | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7, Duration: 23 ms` |
| Core — the whole `Notify` namespace | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Notify"` | `Passed! - Failed: 0, Passed: 76, Skipped: 0, Total: 76, Duration: 127 ms` |

So the Guard project's two reds (which is why a docs path cannot read green through `verify-change`) are
**not** this program's: the notification-catalogue guard filter is 7/7 green, and the two reds are
`PlantSideStatusGuardTests` (`CAI-guard-1`) and `SubprocessPipeDrainGuardTests` (offender
`gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs`, `TVB-F2`) — which the boundary program's own
`TVB-F13` now carries as an explicit re-measure row, so no duplicate row is filed from here.

## Addendum 2 — the web bus layer (2026-09-21, head `30c585de`)

The FE runs above covered `src/shell/notify`, `src/stages/world` and `src/ui/volumeMatrix`; the **bus**
half of this program's web work (`NS1.8`'s player routing triggers T1–T5 and `NS4.1`/`NS6.10`'s
notification subscription, catch-up pager and history hook) lives in `src/lib/bus/`, which those filters
never reached. Closed here:

| Scope | Command | Numbers printed |
|---|---|---|
| the two files this program owns | `cd gk-web/web/fusion-rpg-web; npx vitest run src/lib/bus/playerRouting.test.ts src/lib/bus/notifications.test.ts` | `Test Files 2 passed (2)`, `Tests 19 passed (19)` |
| the whole bus layer (its neighbours share `keys.ts`, `mutations.ts` and `hub-provider.tsx` with it) | `cd gk-web/web/fusion-rpg-web; npx vitest run src/lib/bus` | `Test Files 18 passed (18)`, `Tests 102 passed (102)` |

That completes this lane's FE verification picture at the merged head: `shell/notify` + `stages/world` +
`ui/volumeMatrix` `98 files / 863 tests`, the bus `18 files / 102 tests`, and `npm run build` clean.

## Addendum 3 — a ticked claim that had never been re-run (2026-09-21, head `a36e90af`)

Checkpoint 4's first line (`tasks/notification-ssot-todo.md:262`) asserts `npm run build` **and**
`npm run check:bundle` green, and it is ticked. The build has been re-run several times this session;
`check:bundle` had never been run by this lane, so it was run now at the merged head:

| Scope | Command | Numbers printed |
|---|---|---|
| Phaser stays off the entry chunk (NS4.5's own Verify line, Checkpoint 4) | `cd gk-web/web/fusion-rpg-web; npm run check:bundle` | `check-bundle: Phaser is absent from the entry chunk (assets/index-CQBud_SI.js) — OK` |

The script (`gk-web/web/fusion-rpg-web/scripts/check-bundle.mjs`) reads the built entry chunk, so it also
confirms the `npm run build` that preceded it produced the artefact the check inspects. The tick on
Checkpoint 4 therefore stands on a fresh reading, not on the earlier lane's word.

## Addendum 4 — fresh reading at `a36e90af` (the head that merged SSH5.12's 66-file corpus rewrite)

The earlier addenda were taken at `59ea9964` / `30c585de`. Re-run here so every layer has a reading at
the current head, since the merge that produced it touched 66 files elsewhere in the tree:

| Scope | Command | Numbers printed |
|---|---|---|
| Core — catalogue, parsers, classifier, fog rule | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Notify\|FullyQualifiedName~WorldReportVisibility"` | `Passed! - Failed: 0, Passed: 83, Skipped: 0, Total: 83, Duration: 153 ms` |
| Data — notification store | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"` | `Passed! - Failed: 0, Passed: 11, Skipped: 0, Total: 11, Duration: 853 ms` |
| Server — routing, publisher, pump, both sources, endpoints | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify\|FullyQualifiedName~CacheNotify\|FullyQualifiedName~Notification\|FullyQualifiedName~PlayerRouting"` | `Passed! - Failed: 0, Passed: 63, Skipped: 0, Total: 63, Duration: 7 s` |
| Guard — the catalogue contract join | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7, Duration: 21 ms` |
| Web — rail, feed, world stage, volume rows, bus | `cd gk-web/web/fusion-rpg-web; npx vitest run src/shell/notify src/stages/world src/ui/volumeMatrix src/lib/bus` | `Test Files 116 passed (116)`, `Tests 965 passed (965)` |
| Web build | `cd gk-web/web/fusion-rpg-web; npm run build` | `✓ built in 8.55s` |
| Boundary command over this lane's changed paths | `.\scripts\verify-change.ps1 -Paths 'tasks/evidence-fragments/NS-reverify-20260921.md','tasks/notification-ssot-ledger.jsonl' -Session notification-ssot-20260920` | both map to `session-and-program-records`; `doc-citations` `D1 0 (0 HIGH)`, `D3 0 (0 HIGH)`; `guard: session-boundary`; `test: guard` -> `Failed! - Failed: 2, Passed: 578, Skipped: 0, Total: 580, Duration: 7 m 1 s` (the two reds are `CAI-guard-1`'s baseline and `TVB-F2`'s offender, neither this program's) |

## Addendum 5 — the accepted merge (2026-09-21, head `b45e70ff` from `2d69edf4`)

The manager merged this lane's 17 commits at `2d69edf4` and accepted tip `ed4a5a8a` **GREEN**: its own
record (`.claude/cmdc-agents/acceptance/ns-1-ed4a5a8a.json`, `verdict: GREEN`) lists `boundary` exit 0,
`core-fog` `Passed! 88/88`, `server-notify` `Passed! 57/57`, `ledger` exit 0, `contendedTree: false`.

Two things this addendum adds that the acceptance does not:

| Claim | Command | Numbers printed |
|---|---|---|
| The merge did **not** alter this lane's artifacts | `git diff --stat ed4a5a8a..HEAD -- tasks/notification-ssot-todo.md tasks/notification-ssot-anchor.md tasks/notification-ssot-plan.md tasks/notification-ssot-ledger.jsonl docs/architecture/notification-ssot/ docs/architecture/notification-ssot-map.md tasks/evidence-fragments/NS5.11.md` | empty output — every one of those files is byte-identical to the accepted tip |
| The accepted work still passes at the merged head | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Notify\|FullyQualifiedName~WorldReportVisibility\|FullyQualifiedName~Intel"` | `Passed! - Failed: 0, Passed: 163, Skipped: 0, Total: 163, Duration: 267 ms` |
| | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification\|FullyQualifiedName~WorldNotify\|FullyQualifiedName~CacheNotify\|FullyQualifiedName~PlayerRouting"` | `Passed! - Failed: 0, Passed: 63, Skipped: 0, Total: 63, Duration: 7 s` |
| | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"` | `Passed! - Failed: 0, Passed: 11, Skipped: 0, Total: 11, Duration: 890 ms` |
| | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7, Duration: 21 ms` |
| | `cd gk-web/web/fusion-rpg-web; npx vitest run src/shell/notify src/stages/world src/ui/volumeMatrix src/lib/bus` | `Test Files 116 passed (116)`, `Tests 965 passed (965)` |
| | `npm run build` ; `npm run check:bundle` | `✓ built in 9.42s` ; `Phaser is absent from the entry chunk (assets/index-CQBud_SI.js) — OK` |
| Boundary command over this lane's changed paths | `.\scripts\verify-change.ps1 -Paths 'tasks/evidence-fragments/NS-reverify-20260921.md','tasks/notification-ssot-ledger.jsonl' -Session notification-ssot-20260920` | `doc-citations` `D1 0 (0 HIGH)` / `D3 0 (0 HIGH)`; `[session-boundary] other sessions' drift (3) — not 'notification-ssot-20260920''s, does not block it`; `test: guard` -> `Failed! - Failed: 2, Passed: 578, Skipped: 0, Total: 580, Duration: 6 m 56 s` (the two reds are `CAI-guard-1`'s baseline and `TVB-F2`'s offender) |

## Addendum 6 — the tuning/source audits this program's rows name (2026-09-21)

Two Verify-line obligations of this program had never been run by this lane — the `gk-core/data/tuning` audit
the lane contract requires when that tree is touched (NS1.3/NS5.6/NS6.4 published
`gk-core/data/tuning/notification.v1.json`, `gk-core/data/tuning/notification-catalog.v2.json` and
`gk-core/data/tuning/notification-catalog.v3.json`), and `NS1.3`'s own magic-number check:

| Scope | Command | Numbers printed |
|---|---|---|
| tuning ownership (read-only; `gk-core/data/tuning/**` is in this lane's fence) | `python gk-core/tools/tuning/resource_ownership.py --check` | `OK -- 166 generated edges match aptitudes.v10.json's 166 resource edges exactly` |
| magic numbers in the notification domain (`NS1.3`'s Verify line) | `python gk-core/scripts/audit-magic-numbers.py --domain notification` | `M1=0  M2=0  M3=0  M4=0`, `total 0 finding(s), 0 high` |

Neither audit had a finding against this program's tuning files or its `Core/Notify` surface, so those
two Verify lines now rest on a run rather than on an assumption.

| Boundary command over this lane's changed paths | `.\scripts\verify-change.ps1 -Paths 'tasks/evidence-fragments/NS-reverify-20260921.md','tasks/notification-ssot-ledger.jsonl' -Session notification-ssot-20260920` | `doc-citations` `D1 0 (0 HIGH)` / `D3 0 (0 HIGH)`; `[session-boundary] other sessions' drift (3) — not 'notification-ssot-20260920''s, does not block it`; `test: guard` -> `Failed! - Failed: 2, Passed: 578, Skipped: 0, Total: 580, Duration: 7 m 22 s` (the two reds are `CAI-guard-1`'s baseline and `TVB-F2`'s offender) |

## Addendum 7 — the Core reds this track recorded are fixed (2026-09-21, head `287a3256`)

Every earlier addendum here reports the boundary's Core scope as red with four failures. That is no
longer true: `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` prints
`Passed! - Failed: 0, Passed: 13180, Skipped: 0, Total: 13180, Duration: 1 m 8 s`, and the three affected
classes pass `Passed! 41/41` on their own filter. The Guard project is also down to one red from two
(`SubprocessPipeDrainGuardTests`, `TVB-F2`'s offender, now passes; `PlantSideStatusGuardTests` —
`CAI-guard-1` — remains). The Server project now carries two reds of its own, both other programs'
work: `CombinationImportTests.A_refused_recipe_is_never_seeded` and
`BaseTypeSocketMaxCorpusTests.A_base_row_above_its_role_ceiling_is_refused_at_load`.

## Addendum 8 — post-split re-measure (2026-09-21, head `5d835b27`, tvb58's Core test-project split)

`tvb58` split `gk-core/tests/FusionRpg.Core.Tests` into a remainder plus eleven focused projects. This lane's own
tests did **not** move — they are still under `gk-core/tests/FusionRpg.Core.Tests/` (`Notify/`, `World/Notify/`,
`World/Intel/`) — so every command in these fragments still resolves, but the project *totals* they quote
no longer describe one project. Re-measured:

| Scope | Command | Numbers printed |
|---|---|---|
| this program's Core scope | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~Notify\|FullyQualifiedName~WorldReportVisibility"` | `Passed! - Failed: 0, Passed: 83, Skipped: 0, Total: 83, Duration: 171 ms` (unchanged) |
| the remainder project | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` | `Passed! - Failed: 0, Passed: 12704, Skipped: 0, Total: 12704, Duration: 45 s` |
| the eleven split projects | one `dotnet test <proj> -c Release` each | all green: ActorHub 498 · Atoms 1351 · ClassSystem 238 · Balance 209 · ActorSurface 31 · Aura 30 · AchievementTitles 15 · BoardProjection 7 · CapPolicy 12 · CombatCounter 4 · CombatDot 9 = **2404** |
| Data / Server scopes | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"` ; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify\|FullyQualifiedName~CacheNotify\|FullyQualifiedName~Notification\|FullyQualifiedName~PlayerRouting"` | `Passed! 11/11` ; `Passed! 63/63` |

So "the Core project is green" is now "**every Core test project is green**" (12,704 + 2,404), and the
earlier `13180/13180` readings in this file and in `NS5.2`/`NS5.3` are superseded by that split.

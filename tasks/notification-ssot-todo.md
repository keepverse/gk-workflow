# Task list: `notification-ssot` (prefix `NS`)

Plan: [notification-ssot-plan.md](notification-ssot-plan.md) · Map:
[notification-ssot-map.md](../docs/architecture/notification-ssot-map.md) · Specs:
[notification-ssot/](../docs/architecture/notification-ssot/) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane D).

Task ids are `NS<wave>.<n>`. Cross-program references are `<prefix><id>` (`SE…`, `TVB…`). Order
inside a wave is **suggested, not enforced**; only the `deps:` line and the parent's hard edges
(marked `H#`) are real orders. `<build-session>` is the id of the session that builds the task.

**Rule for every task that adds a path:** the path is covered by a row in the verification registry
(`scripts/verification-boundaries.v*.json`, whichever schema `SE0.7` / `TVB` registry-contract has
current) in the same change. `NS1.1` maps the program's path families up front so this is usually
already true. An unmapped path is a verification-boundary defect, never a reason to run the full suite.

---

## Wave 0 — coordination asks (map §G0). Parallel with everything; none blocks waves 1–4

The resolver for every ask is the repo owner, speaking for the owning program. None is irreversible.
Each task is done when the answer (or the default, once the wave that needs it starts) is written into
the map's §G0 asks table with a date. These are sequencing edges into waves 5–6, not gates.

- [x] **NS0.1 — Ask A1: relocate `world-notify` to `shell/notify/rail/`** · XS · deps: — · *(spec: world-notify-source; map G0 A1)* — **Answered 2026-09-21 (owner): ACCEPTED — NS5.7–NS5.11 released**
  - Acceptance: world-stage (`world-notify`, `world-stage-map.md:78`) answers: the move of `categories.ts`, `notifyRailStore.ts`, `channelSettings.ts`, `NotifyRail.tsx`, `RailItem.tsx`, `ChannelControl.tsx` + the click-budget tests, the widened `NotifyCategory`, and the `world-stage-map.md:241` volume reason (all six GONE/moved as of NS5.7–NS5.11, after the owner accepted A1 — see the map §G0 answer)
  - Acceptance: answer + date recorded in the map §G0 row. **Default if unanswered: none — NS5.7–NS5.11 wait** (they edit another program's shipped module). Every other wave-5 task proceeds
  - Verify: `Select-String -Path docs/architecture/notification-ssot-map.md -Pattern "A1"` shows the answer
  - Files: docs/architecture/notification-ssot-map.md (answer line only)

- [x] **NS0.2 — Ask A2: move the fog rule into Core `WorldReportVisibility`** · XS · deps: — · *(spec: world-notify-source; map G0 A2)* — **Answered 2026-09-21 (owner): ACCEPTED — NS5.2/NS5.3 released, and NS5.12, NS5.13, NS6.5 with them**
  - Acceptance: world-stage (`world-wire`, `world-stage-map.md:70`) answers the move of `VisibleTo(TurnReportEntry, …)`, `IsStaticFact`, `StaticFactDetailPrefixes` unchanged from `WorldEndpoints.cs:565-587`
  - Acceptance: answer + date recorded. **Default if unanswered: none — NS5.2 and NS5.3 wait**
  - Verify: `Select-String -Path docs/architecture/notification-ssot-map.md -Pattern "A2"`
  - Files: docs/architecture/notification-ssot-map.md (answer line only)

- [x] **NS0.3 — Ask A3: `claim.lost:{sectorId}` producer line (audience = previous owner)** · XS · deps: — · *(spec: world-notify-source §Debt; map G0 A3)*
  - Acceptance: world-map (`ClaimResolver.cs:122`) + world-stage `world-playback` answer
  - Acceptance: answer recorded. **Default: declined** — the capture-loss notice stays as the §Debt adapter (NS5.10); NS7.3 runs only if accepted and landed
  - Verify: `Select-String -Path docs/architecture/notification-ssot-map.md -Pattern "A3"`
  - Files: docs/architecture/notification-ssot-map.md (answer line only)

- [x] **NS0.4 — Ask A4: `audience` on `legion.starved:`** · XS · deps: — · *(spec: world-notify-source; map G0 A4)*
  - Acceptance: loam (`loam-legions`, `LegionSupply.cs:138-139`) answers
  - Acceptance: answer recorded. **Default: declined** — `legion.starved:` stays unmapped (report-only); NS7.4 runs only if accepted and landed
  - Verify: `Select-String -Path docs/architecture/notification-ssot-map.md -Pattern "A4"`
  - Files: docs/architecture/notification-ssot-map.md (answer line only)

- [x] **NS0.5 — Ask A5: two read-only methods on `RpgStore.CacheDecay.cs`** · XS · deps: — · *(spec: cache-notify-source §1; map G0 A5)*
  - Acceptance: deployment-hierarchy (`cache-decay-void`) answers
  - Acceptance: answer recorded. **Default: accepted** (additive, read-only, no schema or tick change) — NS6.1 proceeds on the default and runs that program's `CacheDecay` tests
  - Verify: `Select-String -Path docs/architecture/notification-ssot-map.md -Pattern "A5"`
  - Files: docs/architecture/notification-ssot-map.md (answer line only)

- [x] **NS0.6 — Ask A6: a `supply.besieged` row in `playbackTable.ts`** · XS · deps: — · *(spec: world-notify-source; map G0 A6)*
  - Acceptance: world-stage (`world-playback`) answers
  - Acceptance: answer recorded. **Default: accepted** — NS5.4 adds the row in its own change
  - Verify: `Select-String -Path docs/architecture/notification-ssot-map.md -Pattern "A6"`
  - Files: docs/architecture/notification-ssot-map.md (answer line only)

---

## Wave 1 — `notify-vocabulary` ∥ `player-routing`

- [x] **NS1.1 — Verification mapping for the notify path families** · XS · deps: — · *(spec: notify-vocabulary §Commands)*
  - Acceptance: registry rows cover `gk-core/src/FusionRpg.Core/Notify/**`, `gk-core/src/FusionRpg.Core/World/Notify/**`, `gk-core/src/FusionRpg.Server/Notifications/**`, `gk-core/src/FusionRpg.Server/NotificationEndpoints.cs`, `gk-core/src/FusionRpg.Server/PlayerPush.cs`, `gk-core/src/FusionRpg.Server/PlayerConnectionRegistry.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Notifications.cs`, `gk-core/src/FusionRpg.Data/Notifications/**`, `gk-web/web/fusion-rpg-web/src/shell/notify/**`, `gk-web/web/fusion-rpg-web/src/features/notices/**`, `data/tuning/notification*.json`, each selecting the focused filters the specs name (`~Notify`, `~Notification`, `~PlayerRouting`, `~NotificationCatalog`, vitest paths)
  - Acceptance: the registry's own validation (whatever `SE0.7`/`TVB` registry-contract ships) passes
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json -Session <build-session>` (use the current registry file name)
  - Files: the verification registry file

- [x] **NS1.2 — Closed enums and wire DTOs in Contracts** · S · deps: — · *(spec: notify-vocabulary §3)*
  - Acceptance: `NotificationDtos.cs` holds `NotifySeverity` (ordered 0..2), `NotifyArgKind`, `NotifyRefKind`, `NotifyDelivery`, `NotifyArgDto`, `NotificationDto`, `NotificationBatchDto`, `NotificationStateChangedDto`, `NotificationStateChangeDto`, `NotificationEvents`; `Seq`/`Rev`/`PlayerId` are `long`, `WorldTurn` is `int?`
  - Acceptance: enums serialize as camelCase strings (round-trip test); member counts pinned **as closed vocabularies**, with the reason in the test (3/5/6/2)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Notify"`; `.\scripts\verify-change.ps1 -Paths <files> -Session <build-session>`
  - Files: gk-core/src/FusionRpg.Contracts/NotificationDtos.cs, tests/FusionRpg.Core.Tests/Notify/NotificationDtoTests.cs

- [x] **NS1.3 — Catalog v1 + tuning v1 + Core parsers** · M · deps: NS1.2 · *(spec: notify-vocabulary §1, §2, §4)*
  - Acceptance: `notification-catalog.v1.json` (`categories: []`, empty `promotions`) and `notification.v1.json` (`retainPerCategory: 100`, `repeatWindowWorldTurns: 3`, "working values" note) exist; an empty catalog parses and every query answers "unknown"
  - Acceptance: the parser rejects a duplicate id, a promotion naming an unregistered id, `critical ⊄ toast`, empty `messageKeys`, and any row carrying `channel` or `severity`; a missing tuning key throws naming the key (T5), no built-in default
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Notify"`; `python scripts\audit-magic-numbers.py --domain notification`
  - Files: gk-core/data/tuning/notification-catalog.v1.json, gk-core/data/tuning/notification.v1.json, gk-core/src/FusionRpg.Core/Notify/NotificationCatalog.cs, gk-core/src/FusionRpg.Core/Notify/NotificationTuning.cs, tests/FusionRpg.Core.Tests/Notify/NotificationCatalogTests.cs

- [x] **NS1.4 — Host loads (Server) and typed web catalog** · S · deps: NS1.3 · *(spec: notify-vocabulary §4, Code style)*
  - Acceptance: `Program.cs` loads both files beside the other tuning loads and registers `NotificationCatalog` / `NotificationTuning` singletons (no injector load: the injector never receives a notification)
  - Acceptance: `shell/notify/catalog.ts` imports v1 JSON, exports `NotifyCategoryId = string`, `NotifyChannel`, `NotifySeverity`, `defaultChannelOf` (unpromoted → `rail`), and the TS mirror of the wire DTOs (`NotificationItem`, `NotifyArg`)
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/catalog; npm run build`; `.\scripts\verify-change.ps1 -Paths <files> -Session <build-session>`
  - Files: gk-core/src/FusionRpg.Server/Program.cs, gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts, gk-web/web/fusion-rpg-web/src/shell/notify/catalog.test.ts

- [x] **NS1.5 — Guard: C#/TS enum parity and no self-promotion over the real files** · S · deps: NS1.4 · *(spec: notify-vocabulary Testing 1–3)*
  - Acceptance: the Guard test reads `NotificationDtos.cs` and `catalog.ts` and asserts identical members wherever both hold an enum
  - Acceptance: over the real catalog: no row has `channel`/`severity`; every `promotions.*` id is registered; `critical ⊆ toast`; every row has non-empty `domain` and `messageKeys` — no category count asserted
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"`
  - Files: gk-core/tests/FusionRpg.Guard.Tests/NotificationCatalogContractTests.cs

- [x] **NS1.6 — `JoinPlayer` and the connection registry** · S · deps: — · *(spec: player-routing §1)*
  - Acceptance: `RpgConstants.PlayerGroupPrefix` / `PlayerGroup(id)`; `RpgHub.JoinPlayer(long)` returns `false` and joins nothing for an id with no `players` row, never reads `current_player_id`, and moves a connection out of its previous player group (at most one)
  - Acceptance: `PlayerConnectionRegistry` (singleton, in-memory, never persisted); `OnDisconnectedAsync` removes the entry (one line)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~PlayerRouting"`; `.\scripts\guard-dal.ps1`
  - Files: gk-core/src/FusionRpg.Contracts/Dtos.cs, gk-core/src/FusionRpg.Server/PlayerConnectionRegistry.cs, gk-core/src/FusionRpg.Server/RpgHub.cs, gk-core/tests/FusionRpg.Server.Tests/PlayerRoutingTests.cs

- [x] **NS1.7 — `IPlayerPush` seam and the isolation test (R-N1)** · S · deps: NS1.6 · *(spec: player-routing §1, Testing)*
  - Acceptance: `IPlayerPush` + fire-and-forget `HubPlayerPush` shaped like `IDelveLivePush`; DI singletons in `Program.cs`
  - Acceptance: a fake `IHubContext` shows the push goes to `PlayerGroup(id)` and never to `WebGroup`/`Clients.All`; two connections joined as saves 1 and 2 — a push to 1 reaches only the first
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~PlayerRouting"`
  - Files: gk-core/src/FusionRpg.Server/PlayerPush.cs, gk-core/src/FusionRpg.Server/Program.cs, gk-core/tests/FusionRpg.Server.Tests/PlayerRoutingTests.cs

- [x] **NS1.8 — Web joins the shown save on start, reconnect and save switch** · S · deps: NS1.6 · *(spec: player-routing §2 T1–T5)*
  - Acceptance: `lib/bus/playerRouting.ts` `joinCurrentPlayer` invoked after every `Join("web")` (T1, T2 on `onreconnected`) and on `useSelectPlayer` success (T3, no reconnect); emits `player-joined(id)` only when the server returns `true`
  - Acceptance: T2-then-T3 and T3-then-T2 both end on the shown save; a second session that did not switch keeps its group; T5 (refused) logs once and emits no `player-joined`
  - Verify: `cd web\fusion-rpg-web; npm test -- lib/bus/playerRouting; npm run build`
  - Files: gk-web/web/fusion-rpg-web/src/lib/bus/playerRouting.ts, gk-web/web/fusion-rpg-web/src/lib/bus/playerRouting.test.ts, gk-web/web/fusion-rpg-web/src/lib/bus/hub-provider.tsx, gk-web/web/fusion-rpg-web/src/lib/bus/mutations.ts

### Checkpoint 1 — vocabulary and routing
- [x] NS1.2–NS1.5 green; the empty v1 catalog loads in the Server and types in the web
- [x] Isolation test (NS1.7) quoted: a push to save 1 never reaches save 2's connection
- [x] `guard-dal.ps1` green (wave 1 adds no SQL); `npm run build` green

---

## Wave 2 — `notify-store` ∥ `notify-format`

- [x] **NS2.1 — Store schema and idempotent append with the key ledger and per-save rev** · M · deps: NS1.2 · *(spec: notify-store §1, §2; properties 1, 4)*
  - Acceptance: the four tables (`rpg_notification`, `rpg_notification_save_rev`, `rpg_notification_key`, `rpg_notification_source_cursor`) created by `EnsureNotificationSchemaUnlocked` on fresh and existing hot DBs; column `save_id` (R17); `seq`/`rev`/`save_id` `long`, rev bump `checked`
  - Acceptance: `AppendNotificationTurn` (without prune/cursor yet): ledger `INSERT OR IGNORE` decides "new", row insert second; same key twice → second call returns empty, count stays 1; same key for two saves → two rows; rev counter is a row, never `MAX(rev)`
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"`; `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py`
  - Files: gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Notifications.cs, gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs, gk-core/src/FusionRpg.Data/Notifications/NotificationRow.cs, gk-core/tests/FusionRpg.Data.Tests/Notifications/NotificationStoreTests.cs

- [x] **NS2.2 — Per-category retention prune and ledger ageing in the append's transaction** · S · deps: NS2.1 · *(spec: notify-store §1 ledger, §2 prune; tests 2, 4, 10)*
  - Acceptance: after every append each touched `(save, category)` keeps its newest `retainPerCategory` rows by `seq`, state ignored; a call inserting 3 into one category at N=2 returns only the 2 survivors; pruning the highest-rev row never makes the next rev smaller
  - Acceptance: a key pruned from the rows is still refused within `DedupKeyMemoryWorldTurns` (structural const with its comment); ledger rows older than `appendTurn − DedupKeyMemoryWorldTurns` are aged out; the retention-tail exemption comment is verbatim
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"`; `python scripts\audit-magic-numbers.py --targets M1` shows nothing new in the file
  - Files: gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Notifications.cs, gk-core/tests/FusionRpg.Data.Tests/Notifications/NotificationStoreTests.cs

- [x] **NS2.3 — Source cursor, atomic per turn** · S · deps: NS2.2 · *(spec: notify-store property 3, 5; tests 5, 9)*
  - Acceptance: `AppendNotificationTurn(..., cursor)` upserts the cursor in the same transaction; a failure forced after the inserts and before the cursor leaves no row, no ledger key, no rev bump, cursor unchanged
  - Acceptance: `GetNotificationCursor` reads `null` when absent; `InitNotificationCursor` round-trips and is the only non-append writer
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"`
  - Files: gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Notifications.cs, gk-core/tests/FusionRpg.Data.Tests/Notifications/NotificationStoreTests.cs

- [x] **NS2.4 — Store reads and state moves** · S · deps: NS2.1 · *(spec: notify-store §2; tests 6, 7, 8)*
  - Acceptance: `ListNotificationChanges(save, sinceRev, limit)` returns strictly increasing revs `> since` with no gap/repeat across pages, and an old row whose state changed reappears after the cursor; `ListNotificationsByCategory` pages by `seq` descending
  - Acceptance: `SetNotificationState`: unread→read, unread|read→dismissed, dismissed→read (undo) bump rev; every other move and a pruned seq is a no-op absent from the result
  - Acceptance: `HasRecentNotification` true at `fromTurn = world_turn`, false at `world_turn + 1`
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"`; `.\scripts\guard-dal.ps1`
  - Files: gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Notifications.cs, gk-core/src/FusionRpg.Data/Notifications/NotificationRow.cs, gk-core/tests/FusionRpg.Data.Tests/Notifications/NotificationStoreTests.cs

- [x] **NS2.5 — Format kit and translator contract (R-N3, primitives first)** · S · deps: NS1.4 · *(spec: notify-format §1, §2; tests 1, 2)*
  - Acceptance: `NotifyTranslator` / `NotifyText` / `NotifyTarget` types; kit primitives `magnitude` (through `formatMagnitude`), `count`, `turn` / `turnsFrom`, `ref(arg, resolver)`, `categoryName`; **no** `domainToken` primitive
  - Acceptance: the kind set is read from the vocabulary union, so a new kind without a primitive fails; an unresolvable `ref` renders `Pending` and the output does not contain the id
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/format; npm run build`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/format/translator.ts, gk-web/web/fusion-rpg-web/src/shell/notify/format/kit.ts, gk-web/web/fusion-rpg-web/src/shell/notify/format/kit.test.ts

- [x] **NS2.6 — Translator registry, `renderNotification` and the designed fallback** · S · deps: NS2.5 · *(spec: notify-format §3, §4; test 4)*
  - Acceptance: `registerTranslator` / `translatorFor(domain)`; `translators.ts` is the one import-list index (empty in v1, no logic); `renderNotification` is the only render entry point
  - Acceptance: an unknown domain or a `null` translation renders `categoryName` + neutral body (never the id) and logs once in development
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/format`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/format/registry.ts, gk-web/web/fusion-rpg-web/src/shell/notify/format/translators.ts, gk-web/web/fusion-rpg-web/src/shell/notify/format/render.ts, gk-web/web/fusion-rpg-web/src/shell/notify/format/render.test.ts

- [x] **NS2.7 — Coverage guard over the live catalog** · XS · deps: NS2.6 · *(spec: notify-format test 3)*
  - Acceptance: for every catalog category and each of its `messageKeys`, the domain translator's `samples(key)` is non-empty and every sample renders non-`null` with no category id or raw engine token in the output; a key with no samples fails
  - Acceptance: loops over the catalog at test time (no pinned number); green over the empty v1 catalog
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/format/coverageGuard`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/format/coverageGuard.test.ts

### Checkpoint 2 — durable log and shared words
- [x] Store tests 1–10 green on the in-memory store; `guard-dal.ps1` and `guard-test-substrate.py` green
- [x] `shell/notify/format/` holds no domain vocabulary except the import list; coverage guard green

---

## Wave 3 — `notify-service`

- [x] **NS3.1 — Core drafts and the publisher's contract validation** · S · deps: NS1.3 · *(spec: notify-service §1, §2 step 1; test 4)*
  - Acceptance: `NotificationDraft` and `NotifyArg` in Core (no transport types); `NotificationContract.Validate` refuses an unregistered category, an undeclared message key, a severity above `CeilingOf`, an unknown arg kind — each throws `NotificationContractException` naming category and key
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Notify"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification"`
  - Files: gk-core/src/FusionRpg.Core/Notify/NotificationDraft.cs, gk-core/src/FusionRpg.Core/Notify/NotifyArg.cs, gk-core/src/FusionRpg.Server/Notifications/NotificationContractException.cs, gk-core/src/FusionRpg.Server/Notifications/NotificationContract.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationContractTests.cs

- [x] **NS3.2 — `NotificationPublisher`: durable first, then one ordered batch per save** · M · deps: NS3.1, NS2.3, NS2.4, NS1.7 · *(spec: notify-service §2; tests 1, 2, 3, 5, 6, 8)*
  - Acceptance: repeat window drops a non-Critical draft with subject + turn when `HasRecentNotification(..., WorldTurn − repeatWindowWorldTurns)`; Critical and subject-less drafts are never dropped
  - Acceptance: one `AppendNotificationTurn` call per publish; the fake push sees rows **and** cursor already stored; a re-publish pushes nothing; saves 1 and 2 get separate batches to their own `PlayerGroup`, nothing to `WebGroup`
  - Acceptance: batch order severity desc then `seq` asc (two input orders tested); every batch carries `delivery`; a push that throws after the append leaves rows + cursor and a re-run pushes nothing
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification"`
  - Files: gk-core/src/FusionRpg.Server/Notifications/NotificationPublisher.cs, gk-core/src/FusionRpg.Server/Program.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationPublisherTests.cs

- [x] **NS3.3 — World-turn pump and the source seam** · M · deps: NS3.2 · *(spec: notify-service §3 steps 1–4; tests 7, 9)*
  - Acceptance: `IWorldTurnNotificationSource`, `AddressedDraft`, `WorldTurnNotificationContext`; non-`map` worlds skipped; absent cursor → `InitNotificationCursor(R)` with no publish; cursor at `R−2` publishes two turns in order, ends at `R`
  - Acceptance: reads `GetWorldTurnLog(...).ReportJson` first; a trimmed turn gets `Report = null`, advances the cursor, and never calls `GetWorldTurnReport` (fake fails the test if it does); a throwing source does not stop another source or the cursor
  - Acceptance: `Live` only for `trigger == Commit && t == R`, else `CatchUp`; a per-world lock serialises runs
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification"`
  - Files: gk-core/src/FusionRpg.Server/Notifications/IWorldTurnNotificationSource.cs, gk-core/src/FusionRpg.Server/Notifications/WorldTurnNotificationPump.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldTurnPumpTests.cs

- [x] **NS3.4 — Commit trigger: pump after an advancing commit** · S · deps: NS3.3 · *(spec: notify-service §3 Triggers; test 10; success criterion 2)*
  - Acceptance: the only change to `WorldEndpoints.cs` is one `pump.Run(worldId, Commit)` after `CommitWorldTurn` returns `Advanced`, outside its transaction
  - Acceptance: a pump that throws still lets `/commit` return `Ok` with `Advanced = true`; the failure is logged and the cursor stays
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification"`; `.\scripts\verify-change.ps1 -Paths <files> -Session <build-session>`
  - Files: gk-core/src/FusionRpg.Server/WorldEndpoints.cs, gk-core/src/FusionRpg.Server/Program.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldTurnPumpCommitTests.cs

- [x] **NS3.5 — Boot catch-up step** · S · deps: NS3.3 · *(spec: notify-service §3 Triggers; test 9)*
  - Acceptance: hosted startup step runs `Run(…, Boot)` for each save's active map world (`ListPlayers` → `GetActiveWorld`); every batch it pushes is `CatchUp`
  - Acceptance: a boot run and a commit run on the same world, in either order, end at `R` with each row stored once
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification"`
  - Files: gk-core/src/FusionRpg.Server/Notifications/NotificationBootCatchUp.cs, gk-core/src/FusionRpg.Server/Program.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationBootCatchUpTests.cs

- [x] **NS3.6 — REST: catch-up, history, state** · M · deps: NS2.4, NS1.7 · *(spec: notify-service §4; test 11)*
  - Acceptance: `GET /api/notifications/{playerId}?since=&limit=` (rev asc, new rows **and** state changes), `GET …/history?category=&before=&limit=` (seq desc; 400 `category.unknown`), `POST …/state` returning `{changed:[{seq,rev}]}`; unknown save → 404; `limit` bounded by structural `MaxPageSize` with its comment
  - Acceptance: the state POST pushes `NotificationStateChanged` to that save's group only; `since` paging has no gap/repeat and shows another session's state change after the cursor
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification"`; `.\scripts\guard-dal.ps1`
  - Files: gk-core/src/FusionRpg.Server/NotificationEndpoints.cs, gk-core/src/FusionRpg.Server/Program.cs, gk-core/src/FusionRpg.Contracts/NotificationDtos.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationEndpointsTests.cs

- [x] **NS3.7 — Gate G1 end to end: routed and durable** · S · deps: NS3.4, NS3.5, NS3.6 · *(spec: map G1; notify-service success criterion 4)*
  - Acceptance: with routing, store, publisher and pump composed (fake sources, in-memory store): a draft for save A is stored before any push, reaches only `player:A`; re-publishing, including after its row was pruned, stores and pushes nothing
  - Acceptance: a crash injected between commit and push leaves rows + cursor, and the catch-up GET delivers them; a connection that joins after the push gets the row by GET; a boot run pushes only `CatchUp`
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~NotificationG1"`
  - Files: gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationG1Tests.cs

### Checkpoint 3 — G1 routed and durable
- [x] NS3.7 green, output quoted; notify-service tests 1–11 green
- [x] `git diff` of `WorldEndpoints.cs` for wave 3 is the one pump call
- [x] `guard-dal.ps1` green; `verify-change.ps1` green on every wave-3 path

---

## Wave 4 — `notify-client` (touches no world-stage file)

- [x] **NS4.1 — `lib/bus/notifications.ts`: subscription, catch-up pager, state mutation** · S · deps: NS3.6, NS1.8 · *(spec: notify-client §1)*
  - Acceptance: subscribes to `NotificationBatch` and `NotificationStateChanged` via `getHubConnection()` (no new `HubProvider` handler); pages `GET …?since=` until `hasMore = false`
  - Acceptance: `useSetNotificationState()` is a TanStack mutation; features call it only through `lib/bus`
  - Verify: `cd web\fusion-rpg-web; npm test -- lib/bus/notifications; npm run build`
  - Files: gk-web/web/fusion-rpg-web/src/lib/bus/notifications.ts, gk-web/web/fusion-rpg-web/src/lib/bus/notifications.test.ts

- [x] **NS4.2 — Feed reducer and store (dedup, higher rev wins, per save)** · S · deps: NS1.4 · *(spec: notify-client §2; tests 1 (reducer half), 2)*
  - Acceptance: pure `applyItems`, `applyStateChange`, `resetForPlayer`; `byKey` on `dedupKey`; a merge keeps the higher `rev`; another save's items are ignored (F7)
  - Acceptance: push-then-GET and GET-then-push end with one item; a page fetched before a dismiss that lands after its F5 leaves it dismissed
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/feed`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/feed/feedReducer.ts, gk-web/web/fusion-rpg-web/src/shell/notify/feed/feedReducer.test.ts, gk-web/web/fusion-rpg-web/src/shell/notify/feed/feedStore.ts

- [x] **NS4.3 — Toast selection: Critical first at the cap (R-N4, R-N6)** · S · deps: NS1.4 · *(spec: notify-client §4; test 3)*
  - Acceptance: `ToastEntry.severity?` additive (mutation-feedback toasts count as routine); `Toasts.tsx` uses pure `selectVisibleToasts(toasts, VISIBLE_CAP)` — Critical newest first, then the rest newest first, remainder behind "+N more"
  - Acceptance: three routine then one Critical → Critical visible, one routine behind the count; the same set pushed in reverse gives the same visible set
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/toastSelection shell/Toasts`
  - Files: gk-web/web/fusion-rpg-web/src/shell/toastSelection.ts, gk-web/web/fusion-rpg-web/src/shell/toastSelection.test.ts, gk-web/web/fusion-rpg-web/src/shell/toastStack.ts, gk-web/web/fusion-rpg-web/src/shell/Toasts.tsx

- [x] **NS4.4 — Open-id channel settings and toast routing** · S · deps: NS4.2, NS2.6 · *(spec: notify-client §3, §4; test 4)*
  - Acceptance: `shell/notify/channelSettings.ts` reuses storage key `fusionrpg.world-notify.channels.v1` (settings saved by the world copy are read), defaults from `defaultChannelOf`, change event keeps two controls in step
  - Acceptance: `toastRouting.ts` pushes only items first seen in a `live` batch whose channel is `toast`, text from `renderNotification`; `off` never toasts, Critical included; a later live copy of a held item does not re-toast
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/channelSettings.ts, gk-web/web/fusion-rpg-web/src/shell/notify/channelSettings.test.ts, gk-web/web/fusion-rpg-web/src/shell/notify/feed/toastRouting.ts, gk-web/web/fusion-rpg-web/src/shell/notify/feed/toastRouting.test.ts

- [x] **NS4.5 — `NotificationWire`: app-level wiring, triggers F1–F7, error state** · M · deps: NS4.1, NS4.3, NS4.4 · *(spec: notify-client §1, §2; tests 1, 2, 7)*
  - Acceptance: mounted beside `<Toasts />` in `App.tsx`, renders nothing; F1 (`player-joined`), F2 (reconnect, no reset), F3 (save switch: old items gone before the new catch-up lands), F4 live, F4b catch-up (never toasts), F5, F6 (pending control, server state painted after return) — one test each
  - Acceptance: a failed catch-up sets `status = "error"` and exposes the designed failed state with retry (GG-17), never an empty feed
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify; npm run build; npm run check:bundle`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/NotificationWire.tsx, gk-web/web/fusion-rpg-web/src/shell/notify/NotificationWire.test.tsx, gk-web/web/fusion-rpg-web/src/app/App.tsx

- [x] **NS4.6 — Rail mount policy, rail selector, target-action registry** · M · deps: NS4.2, NS4.4 · *(spec: notify-client §5, §6; tests 5, 6)*
  - Acceptance: `RailMountPolicy` + `worldLatestTurn` (items of `worldId` at `lastResolvedTurn` only; a non-advancing commit leaves the selection; a feed restored by catch-up selects the same items)
  - Acceptance: `railItemsFrom(feed, policy, ctx, channels)` maps unread/read/dismissed/minimized per §5 and excludes `off`; `TargetActionResolver` registry — an item gets a button only when a resolver is registered for its target kind
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/rail shell/notify/targetActions`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/rail/mountPolicies.ts, gk-web/web/fusion-rpg-web/src/shell/notify/rail/mountPolicies.test.ts, gk-web/web/fusion-rpg-web/src/shell/notify/rail/railItems.ts, gk-web/web/fusion-rpg-web/src/shell/notify/rail/railItems.test.ts, gk-web/web/fusion-rpg-web/src/shell/notify/targetActions.ts

### Checkpoint 4 — every stage can be told
- [x] notify-client tests 1–7 green; `npm run build` and `npm run check:bundle` green
- [x] `git diff --stat` of wave 4 shows no file under `stages/world/`
- [x] Parent CC7 "notifications wave 1–4" evidence line filled from Checkpoints 1–4

---

## Wave 5 — `world-notify-source` (first consumer)

Map: A1 and A2 hold wave 5. Per task below, A2 holds NS5.2–NS5.3 and A1 holds NS5.7–NS5.11 — the
world-stage-owned edits the asks are about. NS5.1 and NS5.4–NS5.6 touch no file those asks cover
(NS5.4's `playbackTable.ts` row is A6, default accepted) and may start once wave 3–4 deps are met.

- [x] **NS5.1 — Core classifier: the closed table and recipient rules** · M · deps: NS3.1 · *(spec: world-notify-source §2; test 1)*
  - Acceptance: `WorldTurnNotificationClassifier` maps each row of spec §2 (except `claim.lost:`, which waits on A3) to `(category, severity, rule, subjectKey)`, longest prefix wins, unmapped (`calendar`, `command.accepted`, `legion.starved:`, cache-retrieval outcomes) → `null`
  - Acceptance: each row tested with an entry built from the **same prefix literal and argument shape** as its cited producer; closed enum `WorldRecipientRule` (5 members, pinned as a closed vocabulary)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTurnNotification"`
  - Files: gk-core/src/FusionRpg.Core/World/Notify/WorldTurnNotificationClassifier.cs, gk-core/src/FusionRpg.Core/World/Notify/WorldRecipientRule.cs, gk-core/tests/FusionRpg.Core.Tests/World/Notify/WorldTurnNotificationClassifierTests.cs

- [x] **NS5.2 — Move the fog rule into Core `WorldReportVisibility` (ask A2)** · S · deps: NS0.2 (accepted) · *(spec: world-notify-source ask A2; test 3)*
  - Acceptance: `VisibleTo(TurnReportEntry, …)`, `IsStaticFact`, `StaticFactDetailPrefixes` moved unchanged; `WorldEndpoints.cs` calls the Core type and the moved code is removed
  - Acceptance: `WorldTurnReportFogTests` pass **without edits** (diff of the test file is empty)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldTurnReportFog"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldReportVisibility"`
  - Files: gk-core/src/FusionRpg.Core/World/Intel/WorldReportVisibility.cs, gk-core/src/FusionRpg.Server/WorldEndpoints.cs, gk-core/tests/FusionRpg.Core.Tests/World/Intel/WorldReportVisibilityTests.cs

- [x] **NS5.3 — `WorldReportNotificationSource`: recipients, dedup keys, release forecast** · M · deps: NS5.1, NS5.2, NS3.3 · *(spec: world-notify-source §1, §2 recipients/keys; tests 2, 4, 5)*
  - Acceptance: recipients resolved per rule through `IWorldFactionSaves` (v1: the `Player` faction → `header.PlayerId`, the save; AI factions → nothing); an enemy watching my shortfall sector gets no `loam.shortfall`; `battle` reaches exactly the factions the turn GET shows it to (same moved function); a dropped order reaches only its commander
  - Acceptance: keys `world:{worldId}:t{turn}:e{index}` over the persisted report and `…:release:{sectorId}`; the same report classified twice yields identical keys; `loam.release` only when `IsLatestResolved` (catch-up over `R−2…R` → only `R`)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify"`
  - Files: gk-core/src/FusionRpg.Server/Notifications/WorldReportNotificationSource.cs, gk-core/src/FusionRpg.Server/Notifications/WorldFactionSaves.cs, gk-core/src/FusionRpg.Server/Program.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldNotifySourceTests.cs

- [x] **NS5.4 — Web world translator + the `supply.besieged` playback row (ask A6)** · S · deps: NS2.7, NS0.6 (default accepted) · *(spec: world-notify-source §3, ask A6; test 8 part)*
  - Acceptance: `worldTranslator.ts` (domain `world`) is the one reader of the entry token, body via `describePlaybackEntry`, title from the catalog `displayName`, `target` = sector ref; `samples()` for `world.turn-entry` (one per mapped prefix) and `world.release-forecast`
  - Acceptance: `playbackTable.ts` gains the `supply.besieged` row beside `supply.cut`; registered in `translators.ts`; no raw token reaches rendered output
  - Verify: `cd web\fusion-rpg-web; npm test -- stages/world/notify stages/world/playback shell/notify/format; npm run build`
  - Files: gk-web/web/fusion-rpg-web/src/stages/world/notify/worldTranslator.ts, gk-web/web/fusion-rpg-web/src/stages/world/notify/worldTranslator.test.ts, gk-web/web/fusion-rpg-web/src/stages/world/playbackTable.ts, gk-web/web/fusion-rpg-web/src/shell/notify/format/translators.ts

- [x] **NS5.5 — `publish.py`: `notification-catalog` domain with a row-append operation** · S · deps: NS1.3 · *(spec: world-notify-source §4 Catalog v2; notify-vocabulary §1)*
  - Acceptance: `publish.py notification-catalog` can append a category row and set a `promotions.*` list, publishing `v{n+1}` from whatever the current version is (never a hard-coded expected number), keeping the old file (T4)
  - Acceptance: pytest covers append, promotions set, refusal of a row carrying `channel`/`severity`
  - Verify: `python -m pytest gk-core/tools/tuning/test_publish_notification_catalog.py -q`
  - Files: gk-core/tools/tuning/publish.py, gk-core/tools/tuning/test_publish_notification_catalog.py

- [x] **NS5.6 — Publish catalog v2 with both load sites (H7)** · M · deps: NS5.4, NS5.5, NS5.1 · *(spec: world-notify-source §4 Catalog v2; tests 7 step 1, 9; parent §5 notify catalog row)*
  - Acceptance: v2 via `publish.py` adds the eight `world-notify` ids + `territory.lost` with `displayName` and `messageKeys`, and `promotions.toast = TOAST_TIER`; `Program.cs` load line and `shell/notify/catalog.ts` import move to v2 **in the same commit** (H7)
  - Acceptance: migration-equivalence test reads `categories.ts` and v2: `promotions.toast == TOAST_TIER`, each of the eight ids keeps its old default channel; Guard coherence join: every classifier category is registered with domain `world`, every `world` category is emitted by a row or the forecast (no count) (`categories.ts` is GONE as of NS5.11 — that migration test was deleted with it)
  - Acceptance: coverage guard (NS2.7) green over v2
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"`; `cd web\fusion-rpg-web; npm test -- shell/notify`; `.\scripts\verify-change.ps1 -Paths <files> -Session <build-session>`
  - Files: gk-core/data/tuning/notification-catalog.v2.json, gk-core/src/FusionRpg.Server/Program.cs, gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts, web/fusion-rpg-web/src/shell/notify/catalogMigration.test.ts, gk-core/tests/FusionRpg.Guard.Tests/NotificationCatalogContractTests.cs

- [x] **NS5.7 — Move the rail store to `shell/notify/rail/railStore.ts` (ask A1)** · S · deps: NS0.1 (accepted), NS4.6 · *(spec: world-notify-source §4 move table)*
  - Acceptance: `notifyRailStore.ts` → `shell/notify/rail/railStore.ts`; `RailItem.category` is `NotifyCategoryId` and gains `dedupKey`, `seq`, `worldId`, `worldTurn`, `severity`; `flush` / `onCommit` retired (their intent ported to `worldLatestTurn` tests in NS4.6)
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/rail; npm run build`
  - Files: web/fusion-rpg-web/src/stages/world/notify/notifyRailStore.ts (moved), web/fusion-rpg-web/src/stages/world/notify/notifyRailStore.test.ts (moved), gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts, gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.test.ts

- [x] **NS5.8 — Move `NotifyRail` and `RailItem` components (ask A1)** · S · deps: NS5.7 · *(spec: world-notify-source §4 move table)*
  - Acceptance: both components (+ colocated tests) under `shell/notify/rail/`, props unchanged except the category type; text from `renderNotification`
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/rail; npm run build`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/rail/NotifyRail.tsx, gk-web/web/fusion-rpg-web/src/shell/notify/rail/NotifyRail.test.tsx, gk-web/web/fusion-rpg-web/src/shell/notify/rail/RailItem.tsx, gk-web/web/fusion-rpg-web/src/shell/notify/rail/RailItem.test.tsx (each a move from `stages/world/notify/`)

- [x] **NS5.9 — Move `ChannelControl` + the click-budget suites (ask A1)** · S · deps: NS5.8, NS4.4 · *(spec: world-notify-source §4; test 7 last clause)*
  - Acceptance: `ChannelControl` under `shell/notify/rail/` reading `shell/notify/channelSettings.ts`
  - Acceptance: moved `clickBudget.test.tsx` and `noBandThree.test.tsx` pass **with the same intent** (routine = 0 clicks, act = 1, clear = 0, change channel = 1; no band-3 opener)
  - Verify: `cd web\fusion-rpg-web; npm test -- shell/notify/rail`
  - Files: gk-web/web/fusion-rpg-web/src/shell/notify/rail/ChannelControl.tsx, gk-web/web/fusion-rpg-web/src/shell/notify/rail/ChannelControl.test.tsx, gk-web/web/fusion-rpg-web/src/shell/notify/rail/clickBudget.test.tsx, gk-web/web/fusion-rpg-web/src/shell/notify/rail/noBandThree.test.tsx (each a move)

- [x] **NS5.10 — `WorldStage` reads the feed; capture-loss debt adapter** · M · deps: NS5.9, NS4.5, NS5.6 · *(spec: world-notify-source §4 WorldStage, §Debt step 1; tests 8; success criteria 1, 4)*
  - Acceptance: `useState<RailItem[]>` removed; the rail reads the feed through `worldLatestTurn({ worldId, lastResolvedTurn: dto.currentTurn − 1 })`; open / dismiss / undo call `useSetNotificationState` (`read` / `dismissed` / `read`); the world mount registers its sector/legion `TargetActionResolver`
  - Acceptance: `legacyCaptureLoss.ts` keeps the capture-loss notice rendering in the world rail under `territory.lost`, never injected into the feed, never durable
  - Acceptance: `volumeMatrix.test.ts` "World notification rail" keeps `render-all` with the new `worldLatestTurn` reason
  - Verify: `cd web\fusion-rpg-web; npm test -- stages/world shell/notify ui/volumeMatrix; npm run build`
  - Files: gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx, gk-web/web/fusion-rpg-web/src/stages/world/notify/legacyCaptureLoss.ts, gk-web/web/fusion-rpg-web/src/stages/world/notify/legacyCaptureLoss.test.ts, gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts

- [x] **NS5.11 — Retire the world copies (`categories.ts`, world `channelSettings.ts`)** · S · deps: NS5.10, NS5.6 (equivalence green) — **PARTIAL 2026-09-21**: the five deletions and the in-fence citation re-anchors landed; the `world-stage-map.md:241` volume row is a DENIED PATH (outside this lane's allowed paths) and is filed as NS-fence-2, so this row stays open · *(spec: world-notify-source §4, test 7 step 2; notify-client §3 one-wave overlap)* — both GONE (deleted as of NS5.11)
  - Acceptance: `stages/world/notify/categories.ts`, `channelSettings.ts` and their tests deleted; the migration-equivalence test (NS5.6) deleted in the same change (it is a migration check; `notify-vocabulary` test 2 is the permanent guard)
  - Acceptance: `world-stage-map.md:241` volume reason updated, as ask A1 agreed; nothing imports the deleted files (`npm run build` green)
  - Verify: `cd web\fusion-rpg-web; npm test -- stages/world shell/notify; npm run build`; `.\scripts\verify-change.ps1 -Paths <files> -DeletedPaths <deleted files> -Session <build-session>`
  - Files: web/fusion-rpg-web/src/stages/world/notify/categories.ts (+ test, deleted), web/fusion-rpg-web/src/stages/world/notify/channelSettings.ts (+ test, deleted), web/fusion-rpg-web/src/shell/notify/catalogMigration.test.ts (deleted), docs/architecture/world-stage-map.md

- [x] **NS5.12 — Server end-to-end: a real commit's shortfall reaches only its player** · S · deps: NS5.3, NS5.6, NS3.4 · *(spec: world-notify-source test 6)*
  - Acceptance: in-memory store with the existing world-endpoint fixtures: a commit that starves a component → exactly one `NotificationBatch` to the world's save, `delivery = live`, carrying a `loam.shortfall` item whose `worldTurn` is the resolved turn; nothing to any other save
  - Acceptance: running the pump again over the same turn pushes nothing
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify"`
  - Files: gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldNotifyEndToEndTests.cs

- [ ] **NS5.13 — Gate G2 live probe (RPG Server Debug scope)** · S · deps: NS5.10, NS5.11, NS5.12 — **BLOCKED 2026-09-21**: no real world-creation path exists (owning program: **world-continuity**, `docs/architecture/world-continuity/spec-world-creation.md`; `RpgStore.CreateWorld`'s only caller is the SIM route `/api/test/world/create`, `WorldEndpoints.cs:602`, filed as WS-live-1 in `tasks/world-stage-todo.md`), no route can make a component starve, and the full suite was interrupted twice with no output (`not_run`). Evidence: `tasks/evidence-fragments/NS5.13.md` · **Runbook: `tasks/notification-ssot-probe-runbook.md`** (its prerequisites, the exact probe steps on an own instance, the evidence the live-probe standard requires, cleanup, and the dead ends already measured) — **MEASURED 2026-09-21 (head 287a3256)**: the default
  set is 16,922 tests with **three reds, all in other programs' rows** (Core `Passed! 13180/13180`; Data
  `Passed! 1797/1797`; Server `Failed: 2, Passed: 761` — `CombinationImportTests` +
  `BaseTypeSocketMaxCorpusTests`; Guard `Failed: 1, Passed: 579` — `CAI-guard-1`). The live half stays
  blocked on **two** prerequisites, both now measured rather than assumed: the real creation route
  (`world-continuity`) and an **authored** starvation scenario — no player command sequence can produce
  `loam.shortfall` on the shipped world (one sector, production 50 vs upkeep 16, `develop` net-positive,
  nothing sets `danger`). Runbook: `tasks/notification-ssot-probe-runbook.md` · *(spec: map G2; world-notify-source Live probe)*
  - Acceptance: full suite once (`.\scripts\test-fast.ps1 -AllDefault` — wave 5 crosses Core, Server and Web, and precedes a live probe: AGENTS.md points 2 and 3), output quoted
  - Acceptance: on a world created through the real path, a real `POST /api/world/{worldId}/commit` that starves a component produces a `loam.shortfall` toast for the committing save and no one else; `GET /api/notifications/{playerId}` reads it back; the world rail shows exactly the just-resolved turn and a reload rebuilds it from catch-up alone; the real screen is looked at. No `debug.*` fabricator used anywhere in the chain
  - Verify: the probe transcript per `docs/contributing/live-probe-standard.md` (commands, response bodies, read-back, screenshot)
  - Files: none (evidence in the commit body / checkpoint)

### Checkpoint 5 — G2: the world tells you
- [ ] NS5.13 evidence recorded; `WorldTurnReportFogTests` unmodified and green — **fog half met** (`WorldTurnReportFogTests` 5/5 with the file unmodified, NS5.2); `NS5.13`'s evidence is recorded but as **BLOCKED** (no real world-creation route; `tasks/evidence-fragments/NS5.13.md`), so this line stays open
- [x] `WorldStage.tsx` holds no notification state; `stages/world/notify/` holds only the translator, the debt adapter and their tests — **verified 2026-09-21**: no `notifyItems`/`setNotifyItems` in `WorldStage.tsx` (grep; it renders `useNotificationFeed` → `railItemsFrom` → `worldLatestTurn`), and `stages/world/notify/` is exactly `worldTranslator.*` + `legacyCaptureLoss.*` (NS5.10/NS5.11)
- [x] Catalog v2 is the only version either host loads (H7 check: `Program.cs` and `catalog.ts` name the same `vN`) — **verified 2026-09-21**: the version is **v3** now (NS6.4's H7 bump) and both hosts name it (`gk-core/src/FusionRpg.Server/Program.cs:417`, `gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts:4`), which is what this check asks

---

## Wave 6 — `cache-notify-source` ∥ `notify-centre`

### cache-notify-source

- [x] **NS6.1 — Two read methods on `RpgStore.CacheDecay.cs` (ask A5)** · S · deps: NS0.5 (default accepted) · *(spec: cache-notify-source §1; test 1)*
  - Acceptance: `ListCacheClocksStarted(owner, from, to)` and `ListCacheDecayTicks(owner, from, to)`, read-only, inclusive range, in the owning partial; no schema change, no change to the tick
  - Acceptance: ticks at 4, 5, 6 with range `[5, 6]` return exactly those for that owner and none of another's; destroyed/remaining reconcile with `outcomes_json`; deployment-hierarchy's existing `CacheDecay` tests stay green
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CacheDecay"`; `.\scripts\guard-dal.ps1`
  - Files: gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheDecay.cs, gk-core/tests/FusionRpg.Data.Tests/Items/CacheDecayReadTests.cs

- [x] **NS6.2 — `CacheNotificationSource` on the world-turn pump** · M · deps: NS6.1, NS3.3 · *(spec: cache-notify-source §2; tests 2, 3, 4)*
  - Acceptance: window `[t, t+1]`, keys `cache:{id}:created` / `cache:{id}:decay:{tick}`, `worldTurn = ctx.ResolvedTurn`, recipient `ctx.Header.PlayerId`; a real `CommitWorldTurn` tick falls inside the window (pinned by test); overlapping runs store each event once, including after the first row was pruned at `retainPerCategory = 1`
  - Acceptance: emptying tick → `important` with subject `cache:{id}:emptied`; survivors → `routine` with `cache:{id}`; no destruction → nothing; an emptying tick one turn after a partial loss is still stored
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~CacheNotify"`
  - Files: gk-core/src/FusionRpg.Server/Notifications/CacheNotificationSource.cs, gk-core/src/FusionRpg.Server/Program.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/CacheNotifySourceTests.cs

- [x] **NS6.3 — Web cache translator** · S · deps: NS2.7 · *(spec: cache-notify-source §3; test 5)*
  - Acceptance: `cacheNotifyTranslator.ts` (domain `corpse-cache`) with authored sentences over `fmt.count` and `fmt.ref` (`sectorLabel`; lanes follow `laneLabel`'s rule, never splitting the id; unresolvable lane → `Pending`); registered in `translators.ts`; `samples()` for `cache.created` and `cache.decayed`
  - Verify: `cd web\fusion-rpg-web; npm test -- stages/world/cacheClaim shell/notify/format; npm run build`
  - Files: gk-web/web/fusion-rpg-web/src/stages/world/cacheClaim/cacheNotifyTranslator.ts, gk-web/web/fusion-rpg-web/src/stages/world/cacheClaim/cacheNotifyTranslator.test.ts, gk-web/web/fusion-rpg-web/src/shell/notify/format/translators.ts

- [x] **NS6.4 — Publish catalog v3 with both load sites (H7)** · S · deps: NS5.6, NS6.3, NS5.5 · *(spec: cache-notify-source Project structure; notify-vocabulary §1; parent §5 notify catalog row)*
  - Acceptance: v3 via `publish.py` adds `cache.created` and `cache.decayed` (domain `corpse-cache`), no promotion; published from the current version (rebases if another publish landed first)
  - Acceptance: `Program.cs` and `shell/notify/catalog.ts` move to v3 in the same commit (H7); coverage guard and Guard catalog contract green over v3
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"`; `cd web\fusion-rpg-web; npm test -- shell/notify`
  - Files: gk-core/data/tuning/notification-catalog.v3.json, gk-core/src/FusionRpg.Server/Program.cs, gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts

- [x] **NS6.5 — Gate G3 first half: cache items ride the same batch as the turn's world items** · S · deps: NS6.2, NS6.4, NS5.3 · *(spec: map G3; cache-notify-source success criterion 1)*
  - Acceptance: in-memory store: a legion death that starts a cache produces `cache.created`, and a destroying tick produces `cache.decayed`, each in the **same** `NotificationBatch` as that turn's world items (one pump run, R-N6)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~CacheNotify"`
  - Files: gk-core/tests/FusionRpg.Server.Tests/Notifications/CacheNotifyEndToEndTests.cs

### notify-centre (R14: a "Notices" tab in Chronicle)

- [x] **NS6.6 — `/idea-ui` pass over `spec-notify-centre.md`** · S · deps: — (may run any time; suggested during wave 4 so review does not idle wave 6) · *(spec: notify-centre §2 step 1; gui-lego-authoring step 0)*
  - Acceptance: `docs/architecture/notify-centre-ideal.md` per `idea-ui-phase.md`: the bug/shape-to-module map naming the reused pieces (`tool-search` category filter, `chip` for severity/state, ERM **Row**) and any piece that does not exist yet; R14's home taken as ruled, not reopened
  - Verify: `python scripts\audit-doc-citations.py --scope docs/architecture --strict` reports no HIGH for `notify-centre-ideal.md`
  - Files: docs/architecture/notify-centre-ideal.md

- [x] **NS6.7 — Ask: the `notices` row in the GUI Lego menu-refactor queue** · XS · deps: NS6.6 · *(spec: notify-centre §2 step 2)*
  - Acceptance: the gui-lego program (resolver: the owner) accepts a queue row in `docs/architecture/gui-lego/menu-refactor-queue.md`, or the owner adds it. **Default if unanswered when NS6.8 starts: the row is added with the notify-centre spec as its brief**, since the queue is the authoring procedure's index, not an approval
  - Verify: `Select-String -Path docs/architecture/gui-lego/menu-refactor-queue.md -Pattern "notices"`
  - Files: docs/architecture/gui-lego/menu-refactor-queue.md
  - Owner 2026-09-23: the existing `P4 · Notices` row stands as the owner-added queue row — NS6.8 unblocked to start; the piece review itself still gates NS6.11 only.

- [ ] **NS6.8 — Recipe `notices.json`, then the owner piece review** · S · deps: NS6.7 · *(spec: notify-centre §2 steps 3, 7)* — **resolver named 2026-09-21 (owner): the gui-lego program accepts the queue row**; NS6.11/NS6.12 stay gated until that row is accepted and dated. Step 6's drafts landed here on 2026-09-21 so the review has something to look at: `docs/design/gui-lego/recipes/notices.html` (assembled, all five situations) and `docs/design/gui-lego/recipes/notices.ACCEPTANCE.md` (the checkpoint: artifacts, `notice-row`'s field set at the Row rung, what is asked, the gate effect, and the two green test readings). What remains is the **resolver's dated acceptance** — a real external act, not something this lane can record
  - Acceptance: `docs/design/gui-lego/recipes/notices.json` beside the existing recipes, using only pieces from NS6.6's map; any new piece or density is an ERM amendment named, not invented
  - Acceptance: the owner has reviewed pieces, payloads and the assembled look (GUI Lego step 7), recorded with a date in the recipe's meta or the queue row. This review holds **only NS6.11** (React); NS6.9, NS6.10 and NS6.12's fixture work proceed
  - Verify: `cd web\fusion-rpg-web; npm test -- features/gui-lego` (recipe schema tests)
  - Files: docs/design/gui-lego/recipes/notices.json

- [x] **NS6.9 — Pure fold, closed bus catalog, selection store** · S · deps: NS4.2, NS4.4, NS2.6 · *(spec: notify-centre §2 steps 4–5; tests 1, 2)*
  - Acceptance: `foldNoticesVm` lists every registered category (zero rows and `off` included) with its channel and unread count; rows newest first; every row's text via `renderNotification`, no id in it
  - Acceptance: `noticesBus.ts` holds exactly the seven events of spec §2.5, each calling exactly its effect; `selectedCategory` lives in module-level `noticesUiStore.ts`, not component state
  - Verify: `cd web\fusion-rpg-web; npm test -- features/notices`
  - Files: gk-web/web/fusion-rpg-web/src/features/notices/foldNoticesVm.ts, gk-web/web/fusion-rpg-web/src/features/notices/foldNoticesVm.test.ts, gk-web/web/fusion-rpg-web/src/features/notices/noticesBus.ts, gk-web/web/fusion-rpg-web/src/features/notices/noticesBus.test.ts, gk-web/web/fusion-rpg-web/src/features/notices/noticesUiStore.ts

- [x] **NS6.10 — `useNotificationHistory(category)` in the bus** · XS · deps: NS4.1, NS3.6 · *(spec: notify-centre §2 step 4)*
  - Acceptance: pages `GET /api/notifications/{playerId}/history?category=&before=` newest first; `load-older` passes the last `seq` as `before`; a failed page surfaces the error state
  - Verify: `cd web\fusion-rpg-web; npm test -- lib/bus/notifications`
  - Files: gk-web/web/fusion-rpg-web/src/lib/bus/notifications.ts, gk-web/web/fusion-rpg-web/src/lib/bus/notifications.test.ts

- [ ] **NS6.11 — `NoticesSurface` + the Chronicle "Notices" tab** · M · deps: NS6.8 (owner review), NS6.9, NS6.10 · *(spec: notify-centre §1, §3; tests 3, 4, 6; success criteria 1, 2, 4)*
  - Acceptance: one `TABS` entry `{ id: "notices", label: "Notices", Component: NoticesSurface }` — no rail entry, key, route or layer (R14); `bindSurface(recipe, vm, themes)`, no fetch or SignalR read inside a piece
  - Acceptance: designed states loading / empty / failed-with-retry / category routed `off` (rows + channel shown), each queried by role; selected category survives unmount/remount (GG-51)
  - Acceptance: a dismiss in the centre shows dismissed on the world rail and vice versa; copy extracted (`npm run extract`, locales committed if changed)
  - Verify: `cd web\fusion-rpg-web; npm test -- layers/chronicle features/notices shell/notify; npm run build; npm run extract`
  - Files: web/fusion-rpg-web/src/features/notices/NoticesSurface.tsx, web/fusion-rpg-web/src/features/notices/NoticesSurface.test.tsx, gk-web/web/fusion-rpg-web/src/layers/chronicle/ChronicleLayer.tsx, gk-web/web/fusion-rpg-web/src/i18n/locales (extract output)

- [ ] **NS6.12 — Volume: centre row `virtualize`, proven at 10/100/1000** · S · deps: NS6.11 · *(spec: notify-centre §4; test 5; success criterion 3)*
  - Acceptance: `volumeMatrix.test.ts` gains "Notification centre (per-category list)" = `virtualize` with the tunable-bound reason; the declared-surface count moves with it (a closed registry the code owns, not a population pin)
  - Acceptance: e2e volume fixture renders a windowed node count at 10, 100 and 1000 rows
  - Verify: `cd web\fusion-rpg-web; npm test -- ui/volumeMatrix; npm run test:e2e -- volume-fixtures`
  - Files: gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts, gk-web/web/fusion-rpg-web/e2e/volume-fixtures.spec.ts

### Checkpoint 6 — G3: a second domain and a history (program close)
- [ ] NS6.5 green, quoted; the centre lists one category's history capped at `retainPerCategory` — **NS6.5 met** (`Passed! 7/7`; one batch carries `loam.shortfall` + `cache.created` + `cache.decayed`); the centre half is `NS6.11`, gated, so this line stays open. **Refreshed 2026-09-21:** the centre half is now buildable in every respect except the gate — `NS6.8`'s entry criteria 1–4 are met (surface, piece draft, piece spec, index rows all landed) and only the resolver's dated acceptance is missing
- [ ] Owner piece review (NS6.8) dated before NS6.11's first React commit — **not recorded** (checked 2026-09-21: the gui-lego P4 row carries no acceptance date and the recipe no review), so `NS6.11`/`NS6.12` stay gated. **Refreshed 2026-09-21:** everything the review is *of* now exists — `surfaces/notices.html`, `pieces/notice-row.html`, `spec-notice-row.md`, the recipe and the index rows — so the missing item is one dated line from the named resolver (the gui-lego program)
- [ ] Full suite once (program's final checkpoint), output quoted; `notification-catalog` v3 is what both hosts load — **catalog v3 met** (both hosts, see Checkpoint 5); the full suite is **`not_run`**: `test-fast.ps1 -AllDefault` never produced output (killed three times mid-command, infrastructure; `NS5.13.md`), so it was measured project by project instead: 16,922 tests with **three reds, all in other programs' rows** — Server `CombinationImportTests` + `BaseTypeSocketMaxCorpusTests` (filed `SSH-RED-1`) and Guard `PlantSideStatusGuardTests` (`CAI-guard-1`); the Core picture is green and, after `tvb58`'s test-project split, spans `gk-core/tests/FusionRpg.Core.Tests` (`12704/12704`) plus eleven focused projects (2404 tests, all green — this program's own tests stayed in `Core.Tests`, 83/83 on its scope), and Data is green (`1797/1797`); the four Core reds earlier fragments recorded are fixed
- [x] Parent CC7 "notifications" line updated — 2026-09-21 (`tasks/summoner-convergence-plan.md`, CC7 row: waves 1–6 landed except Gate G2 and the gated centre)

---

## Wave 7 — follow-ups triggered by other programs (each runs only when its trigger lands)

- [x] **NS7.1 — `JoinPlayer` refuses an archived save** · XS · deps: `SE` save-identity's `players.archived_utc` + `ListPlayers` filter · *(spec: player-routing §1, Testing "Archived row")*
  - Acceptance: `JoinPlayer` on an archived row returns `false`, reading the same filter `ListPlayers` uses; the boot catch-up (NS3.5) skips the legacy Zomboss row by that same filter (assert it is not visited)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~PlayerRouting|FullyQualifiedName~NotificationBootCatchUp"`
  - Files: gk-core/src/FusionRpg.Server/RpgHub.cs, gk-core/tests/FusionRpg.Server.Tests/PlayerRoutingTests.cs, gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationBootCatchUpTests.cs

- [x] **NS7.2 — Adopt the `SaveId` type on server and data parameters** · S · deps: `SE` save-identity's `SaveId` type · *(map §Identity: "the type swap is mechanical")*
  - Acceptance: `saveId` parameters in `IPlayerPush`, `RpgStore.Notifications.cs`, `AddressedDraft` and the publisher take `SaveId`; wire names (`playerId`, `player:{id}`, `JoinPlayer`, routes) unchanged (R17)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification|FullyQualifiedName~PlayerRouting"`; `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"`
  - Files: gk-core/src/FusionRpg.Server/PlayerPush.cs, gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Notifications.cs, gk-core/src/FusionRpg.Server/Notifications/IWorldTurnNotificationSource.cs, gk-core/src/FusionRpg.Server/Notifications/NotificationPublisher.cs

- [x] **NS7.3 — `claim.lost:` row; remove the capture-loss debt** · S · deps: NS0.3 accepted **and** the `claim.lost:` producer line landed in world-map · *(spec: world-notify-source §Debt step 2)* — **Withdrawn 2026-09-21 (manager erratum): A3 was declined with its stated default (`NS0.3`, map §G0), and this row's own text says it runs only if accepted and landed. It does not run; the §Debt adapter (NS5.10) stays.**
  - Acceptance: classifier row `claim.lost:` → `territory.lost`, `Audience`; `legacyCaptureLoss.ts` and the toast half of `captureNotice.ts` deleted; `captureHeader` stays
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTurnNotification"`; `cd web\fusion-rpg-web; npm test -- stages/world; npm run build`
  - Files: gk-core/src/FusionRpg.Core/World/Notify/WorldTurnNotificationClassifier.cs, gk-core/tests/FusionRpg.Core.Tests/World/Notify/WorldTurnNotificationClassifierTests.cs, gk-web/web/fusion-rpg-web/src/stages/world/notify/legacyCaptureLoss.ts (deleted), gk-web/web/fusion-rpg-web/src/stages/world/cacheClaim/captureNotice.ts, gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx

- [x] **NS7.4 — `legion.lost` category** · S · deps: NS0.4 accepted **and** the `audience` on `legion.starved:` landed in loam · *(spec: world-notify-source ask A4)* — **Withdrawn 2026-09-21 (manager erratum): A4 was declined with its stated default (`NS0.4`, map §G0); the row runs only if accepted and landed, so `legion.starved:` stays report-only.**
  - Acceptance: classifier row `legion.starved:` → `legion.lost`, `Audience`; translator sample; next catalog version published from the current one (v4 if nothing else published; rebase otherwise) with both load sites in the same commit (H7)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTurnNotification"`; `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"`; `cd web\fusion-rpg-web; npm test -- shell/notify stages/world/notify`
  - Files: gk-core/src/FusionRpg.Core/World/Notify/WorldTurnNotificationClassifier.cs, gk-web/web/fusion-rpg-web/src/stages/world/notify/worldTranslator.ts, data/tuning/notification-catalog.v{n+1}.json, gk-core/src/FusionRpg.Server/Program.cs, gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts

---

## Fence findings (filed 2026-09-21, wave 5)

- [ ] **NS-fence-4** (2026-09-21) Gate G2 (NS5.13) is blocked on a PRODUCT gap this lane cannot close:
  no real world-creation route exists (`RpgStore.CreateWorld`'s only caller is the SIM route
  `/api/test/world/create`, `WorldEndpoints.cs:602`; real `MapWorld` maps none) — the route is the
  **world-continuity** program's own wiring gap (`spec-world-creation.md` §Wiring gap / §Real gap), so this
  is another program's unmerged work, not a product gap this lane can close. **And the subject itself needs
  an authored scenario** (measurement 3): no player action starves a component on the shipped world, so a
  route alone would still not make this probe runnable — the two ways out are an authored scenario or a
  re-worded acceptance (the in-process equivalent `NS5.12`/`NS6.5` already prove), and no route can make a
  component starve, so the acceptance's "a world created through the real path" and its `loam.shortfall`
  subject are unreachable live. Routed to world-stage `world-wire` as **WS-live-1** in
  `tasks/world-stage-todo.md`. Also `not_run`: `test-fast.ps1 -AllDefault` was interrupted twice
  mid-command with no output (infrastructure), and the lane contract places the full suite with CC8 /
  the program's final checkpoint — NS5.13 needs a manager ruling on that line.

- [x] **NS-fence-3 — ROUTED 2026-09-21 to the boundary program's own row (`TVB-F1`, `tasks/test-verification-boundary-todo.md:406`, which carries the same finding: no `gk-web/web/fusion-rpg-web/**` owner boundary).** (verification-boundary defect, found 2026-09-21 by NS5.11) `gk-core/scripts/verification-boundaries.v1.json`
  has **no `gk-web/web/fusion-rpg-web/**` rows at all** — 278 boundaries, zero FE path patterns (checked by
  parsing the file) — so `verify-change.ps1` throws `VERIFICATION BOUNDARY MISSING` for every FE path,
  including `gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts`, the deleted
  `stages/world/notify/categories.test.ts`, and the deleted `shell/notify/catalogMigration.test.ts`.
  **NS1.1 is ticked `[x]` while its own acceptance asks for registry rows covering
  `gk-web/web/fusion-rpg-web/src/shell/notify/**` and `gk-web/web/fusion-rpg-web/src/features/notices/**` with vitest
  paths — those rows do not exist.** Every FE task in this lane (NS5.7–NS5.11) therefore verified through
  its row's own `npx vitest` + `npm run build` lines instead of the boundary command. Repair needs an edit
  to `gk-core/scripts/verification-boundaries.v1.json`, which is outside this lane's allowed paths — the manager
  should either route the registry repair to a lane that owns `scripts/**`, or widen this one.

- [x] **NS-fence-1** `docs/architecture/notification-ssot-ideal.md` — **DONE 2026-09-21**, by the same work
  that closed the routed row `TVB-F15`: the doc's 14 dead citations (`notifyRailStore.ts` at `:61`,
  `:127`, `:221`, `:276`, `:285`; `categories.ts` at `:57`, `:223`, `:276`, `:285`, `:424`, `:510`, — both files GONE as of NS5.7/NS5.11
  `:511`) are re-anchored inline, and the document opens with a dated citation note naming the
  successors — `shell/notify/rail/railStore.ts` and `shell/notify/catalog.ts` +
  `gk-core/data/tuning/notification-catalog.v3.json`. Readings: the scoped audit went `14 HIGH` to
  `D1 0 (0 HIGH) · D2 0 · D3 0 · D4 0`, the CI guard now reports no HIGH inside this program's
  documents, and `verify-change` on that path is green (`guard: doc-boundary` `Passed! 4/4`). The
  "outside the lane's allowed paths" premise was also answered: `verify-change`'s fence is the session
  record, which is in this lane's paths, so the file was added to it in the same commit. Evidence:
  `tasks/evidence-fragments/TVB-F15.md`.
- [x] **NS-fence-2 — DISCHARGED 2026-09-21 by NS5.11 itself.** NS5.11's acceptance asks for the volume reason at
  `docs/architecture/world-stage-map.md:243` to be updated to the `worldLatestTurn` reason (ask A1's own
  terms). **The real blocker is ownership, not the fence** (corrected 2026-09-21): the file is
  world-stage's own capability map, and the session-record fence — which is in this lane's paths — could
  be widened for it as it was for `notification-ssot-ideal.md`. Queued with its owner as **WS-vol-1**
  (`tasks/world-stage-todo.md`), which quotes the replacement reason that is already live in
  `gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts`. It landed from this lane in the same change (ask A1's accepted text names the row as part of this
  program's change set), so `WS-vol-1` is annotated as landed rather than left for world-stage to redo.

---

## Finding routed from `test-verification-boundary` (TVB-F15, 2026-09-21)

- [x] **TVB-F15 (your share) — `doc-citations` is red on this program's docs at the merged head** — **DONE 2026-09-21**: `docs/architecture/notification-ssot-ideal.md` went from 14 D1 HIGH to 0 (`audit-doc-citations.py --scope`, and `guard-doc-citations.ps1 -Strict` now reports no HIGH inside this program's documents); the doc opens with a dated citation note and each cited line says the file is GONE, which is the audit's own exemption. Boundary command green on that path (`guard: doc-boundary` `Passed! 4/4`, citations 0 HIGH). The remaining 8 HIGH are other programs' documents, each filed: npc-story-events DOC-NS5.7 (2), trade-network DOC-NS5.7 (3), legion-build DOC-NS5.2 (1, the D2 NS5.2's move caused), world-stage WS-cite-1 (1). Evidence: `tasks/evidence-fragments/TVB-F15.md` ·
  `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` exits 1 with HIGH findings in this program's
  documents: citations of `notifyRailStore.ts` / `categories.ts` / `notify/clickBudget.test.tsx` resolve to no — both GONE as of NS5.7/NS5.11
  tracked file at the cited path (D1), and `docs/architecture/legion-build/spec-legion-count-cost.md:26`
  cites a line past the end of `gk-core/src/FusionRpg.Server/WorldEndpoints.cs` (D2: the file is 1003 lines; its owner re-anchors it, filed as DOC-NS5.2). The guard is gating in CI, so
  CC8 stays red until the citations are re-anchored to the file's current path or the line says the file
  moved. Full list: `tasks/verification-boundaries-todo.md`'s TVB-F15 row (owning program:
  test-verification-boundary). Owning program here: this one.

- [x] **`NSS-join-keys` — every category a producer emits now declares the message key the client
  formats from** · S · deps: — · *(filed by manager adjudication 2026-09-26 from the `cmdc/ns-1`
  worktree, then landed the same turn — see the correction below)* — **LANDED as one unit.** The lane
  `cmdc/ns-1` left this change in its worktree in **three** files, and none of the three is useful
  alone:

  - `WorldReportNotificationSource.cs` — `TurnEntryMessageKey` and `ReleaseMessageKey` promoted from
    `private const` to `public const` (the values were already right: `"world.turn-entry"`,
    `"world.release-forecast"`), and `public const string ReleaseCategory = "loam.release"` added
    with its `CategoryId:` catalogue row.
  - `CacheNotificationSource.cs` — `public const string CreatedMessageKey = "cache.created"` and
    `DecayedMessageKey = "cache.decayed"` added, separate from the category ids, with their
    `MessageKey:` rows.
  - `gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationProducerJoinTests.cs` — 80 lines, 3 tests.

  **The correction, because the first reading was wrong.** Rescuing the test on its own produced nine
  `error CS0117` lines, and this row was first filed as *the API is owed*. That was a misread: the
  per-file line comparison had already reported both production files as `diverged` with 7
  worktree-only lines each, and those lines were the missing half. Keeping the test would have landed
  part of a change whose other half was real. All three applied together build with **0 errors**,
  `NotificationProducerJoin` passes **3/3**, and the whole `Notification` surface passes **63/63**.

  **Acceptance met:** a producer's message key is a named public const rather than a literal a test
  re-types, and `NotificationProducerJoinTests` fails if any world or cache category stops declaring
  one — which is `notify-vocabulary §1`'s publish-time refusal, made checkable.

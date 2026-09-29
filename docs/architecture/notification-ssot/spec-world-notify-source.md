# Spec: world-notify-source

**Status: BUILT 2026-09-21 — wave 5 landed except Gate G2, which is BLOCKED (see the gate status
below).** Module `world-notify-source` of the
[notification-ssot map](../notification-ssot-map.md), wave 5. Depends on `notify-service`,
`notify-client` and `notify-format`. **The G0 gate on this module is closed:** asks A1 and A2 were
ACCEPTED by the owner on 2026-09-21 (map §G0 answers), so the rail relocation and the Core fog rule
both landed (NS5.2, NS5.7–NS5.11) and this module's own half shipped — the classifier (NS5.1), the
source (NS5.3), the world translator (NS5.4) and the server end-to-end (NS5.12). The producer-line
asks (A3, A4) were declined with their stated defaults, which withdrew NS7.3/NS7.4 (todo). **G2's
live probe (NS5.13) is blocked, not done:** `RpgStore.CreateWorld` has exactly one caller in `src/` —
the SIM route `/api/test/world/create` (`WorldEndpoints.cs:602`) — so no world can be created through
the real path, and no route can make a component starve (the in-memory fixtures mutate the world
before `CreateWorld`). Filed as `WS-live-1` in world-stage's todo and `NS-fence-4` here.

**Strengthen pass 2026-09-18:** recipients are saves (R17); the asks carry their real owners (the
`legion.starved:` line belongs to the loam program); `supply.besieged:` needs a playback row that does
not exist yet; the forecast's `cede` input and the dedup key's stability are stated exactly (map
§Strengthen pass S4, S8, S10).

**Loops:** Place 3 (farm, hunt, defend) and Place 5 (world stage empire), `the-loops.md`.

---

## Objective

The first real consumer. After every world turn, the player learns what that turn did **to them**,
on whatever stage they are standing:

- A toast for the three top-tier categories (loam shortfall, ground released next turn, legion runway)
  from `promotions.toast`.
- The world rail for everything else, flushed by turn through `worldLatestTurn` (`notify-client` §6).
- The centre for all of it, capped at `retainPerCategory` per category.

It also finishes the migration the ideal recommends (§Does `world-notify` get migrated or coexist?):
`WorldStage.tsx` stops holding a local `notifyItems` array that nothing feeds
(`gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx:142`, rendered at `:524-535`) and reads the
shared feed.

## Design

### 1. Two inputs, both already durable

| Input | Source | When |
|---|---|---|
| **Report entries** for the resolved turn | `RpgStore.GetWorldTurnReport(worldId, turn)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:731`). The report "IS the log: nothing in the engine writes anywhere else" (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:34-35`) | Every turn the pump visits |
| **The release forecast** | `LoamForecast.WillRelease(world, component, ceded)` (`gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:76`), the same call the state projection makes (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:934`), so the warning and the event cannot disagree (`spec-world-notify.md` §4). `ceded` is the faction's pending `cede` order for the next turn, read the way the projection reads it. Right after a commit there is usually none. If the player files a `cede` afterwards, the state panel's forecast moves and the notification, already sent, does not: it was true when sent, and the panel is the live reading | Only when `ctx.IsLatestResolved`, because a forecast is about the next turn |

### 2. The classifier (Core, pure) — a closed table

`gk-core/src/FusionRpg.Core/World/Notify/WorldTurnNotificationClassifier.cs` (new) maps one
`TurnReportEntry` to `(category, severity, recipientRule, subjectKey)` or to `null`. An unmapped entry
stays in the turn report and the playback panel, and it is **not** a notification. Adding a row means
adding one row here plus that category's catalog row.

| Entry (producer) | Category | Severity | Recipient rule |
|---|---|---|---|
| `event` `loam.shortfall:` (`LoamPhases.cs:186`) and `loam.shortfall.unresolved:` (`:180`) | `loam.shortfall` | important | `SubjectFaction` |
| forecast `WillRelease` (above) | `loam.release` | important | the owning faction of the component |
| `event` `legion.runway:` (`MovementPhase.cs:116`) | `legion.runway` | important | `Audience` |
| `battle` (`BattleReporting.cs:79`) | `battle.result` | routine | `FogVisible` |
| `event` `legion.topup:` (`LegionSupply.cs:105`), `supply.restored` (`:119`) | `supply.change` | routine | `Audience` |
| `event` `supply.cut:`, `supply.besieged:` (`SupplyGraph.cs:119`, `:113`) | `supply.change` | routine | `SubjectFaction`. `supply.besieged:` has no `playbackTable.ts` row today (its dev render is the unrecognised-token marker); this module adds one (map G0 A6) |
| `event` `growth.pulse:`, `develop.completed:`, `development.raised:` (`GrowthPhases.cs:65`, `:132`, `:141`) | `growth` | routine | `SectorOwner` |
| `event` `build.started:` (`BuildResolver.cs:170`) | `growth` | routine | `SubjectCommand` |
| `event` `intel.new:` (`TurnEngine.cs:389`) | `intel.new` | routine | `SubjectFaction` |
| `command.dropped` (every resolver's drop, e.g. `TurnEngine.cs:225`, `BuildResolver.cs:199`; includes `wonder.cap-reached`, `BuildResolver.cs:120`) | `command.dropped` | routine | `SubjectCommand` |
| `event` `loam.lost:` (`LoamPhases.cs:214`, subject = the previous owner) | `territory.lost` | important | `SubjectFaction` |
| `event` `claim.lost:` (**new producer line**, §Cross-program asks A3) | `territory.lost` | important | `Audience` |

**Unmapped on purpose in v1** (they stay in the report and the playback panel): `calendar` lines,
`command.accepted`, `legion.starved:` until ask A4 gives it an audience, and the post-Step
cache-retrieval outcomes (`cache.retrieved:`, `retrieval.failed`, `retrieval.expired:`,
`RpgStore.CacheRetrieval.cs:399-529`). Those outcomes are a natural next row for the cache domain, but
their subject is a mission id with no recipient rule yet, so they are named here and not mapped.

**Recipient rules (closed enum `WorldRecipientRule`).** A notification is about **you**. That is
stricter than the fog rule, which decides what you may *see*. For example, an enemy watching my sector
may see its shortfall line in the turn report, but it is not their `loam.shortfall`.

| Rule | The faction is… |
|---|---|
| `Audience` | `entry.Audience` |
| `SubjectFaction` | `entry.Subject` (the producer puts the faction id there) |
| `SubjectCommand` | the `CommanderId` of the turn's command whose id is `entry.Subject` (`RpgStore.ListWorldCommands`, `RpgStore.WorldTurns.cs:436`), which is the turn GET's "your own orders always" rule (`WorldEndpoints.cs:589-592`) |
| `SectorOwner` | the current owner of `entry.SectorId` |
| `FogVisible` | every human faction for which `WorldReportVisibility.VisibleTo(entry, faction, believed)` holds. That is the turn-report GET's own rule (`WorldEndpoints.cs:565-588`), **moved** to Core unchanged so the two cannot drift (map §Cross-program dependencies) |

**Faction to save.** A notification goes to a save (R17, map §Identity). v1 has one human per world:
the `Player`-kind faction maps to `header.PlayerId`, which is the save (`RpgStore.World.cs:737-740`).
An AI faction maps to no save and gets nothing. Once `save-identity` ships, the rule reads "the
faction whose empire is the save's human empire", and a Zomboss or other `ai` empire still gets
nothing. The mapping sits behind `IWorldFactionSaves`, so a future multi-empire world
(`empire-development-map.md` "Not multiplayer…") only has to replace the implementation.

**Dedup keys (R-N5)** are deterministic and stable across re-runs:

- report entry: `world:{worldId}:t{turn}:e{index}`, where `index` is the entry's position in the
  **persisted** report (`report_json`, `RpgStore.WorldTurns.cs:49`), which does not change once
  committed. A replayed report is not the same list: replay runs `TurnEngine.Step` alone and drops the
  post-Step lines, so its indexes can differ. That is why the pump never reads a replayed report
  (`notify-service` §3 step 4), and why a turn is published in one transaction, so no key is ever
  computed twice from two different lists
- forecast: `world:{worldId}:t{turn}:release:{sectorId}`

**Subject keys** (for the repeat window): `faction:{id}`, `legion:{entityId}`, `sector:{id}`,
`command:{id}`. A command id is unique, so a dropped order is never throttled.

### 3. Drafts carry tokens, and the web world translator owns them

A report-entry draft uses message key `world.turn-entry` with one `domainToken` argument, the entry as
`{kind, subject, detail, sectorId}`, and one `ref` argument (`sector`) when a sector is named. The
forecast uses `world.release-forecast` with a `ref` `sector` argument.

The web world translator (`stages/world/notify/worldTranslator.ts`, new) is the **one** reader of
that token. For the body it calls `describePlaybackEntry` (`stages/world/playbackTable.ts:247`), the
existing authored table. That makes it one vocabulary with two consumers, as
`spec-world-notify.md` §4 requires, and nothing is re-parsed. The title is the catalog `displayName`.
`target` is the sector reference, which the world mount resolves to its existing select/centre
handler (`notify-client` §6).

### 4. The relocation and the WorldStage migration (one change, behind G0)

**The move.** It happens here rather than in `notify-client`, because it is the world-stage-owned
change the G0 sign-off covers:

| From `stages/world/notify/` | To `shell/notify/rail/` | Change |
|---|---|---|
| `notifyRailStore.ts` | `railStore.ts` | `RailItem.category` becomes `NotifyCategoryId`, and it gains `dedupKey`, `seq`, `worldId`, `worldTurn`, `severity`. `flush` / `onCommit` are retired in favour of `worldLatestTurn` (`notify-client` §6). Their tests are ported there |
| `NotifyRail.tsx`, `RailItem.tsx`, `ChannelControl.tsx` | same names | Props unchanged except the category type. Text comes from `renderNotification` |
| `channelSettings.ts` | deleted | Replaced by `shell/notify/channelSettings.ts` (`notify-client` §3), which uses the same storage key |
| `categories.ts` | deleted | Replaced by catalog **v2** (below) |
| `clickBudget.test.tsx`, `noBandThree.test.tsx` | move with the rail | Must pass **with the same intent**: routine = 0 clicks, act = 1, clear = 0, change channel = 1; no band-3 opener |

**Catalog v2**, published through `gk-core/tools/tuning/publish.py` (T4). v2 is this module's; v1 is
`notify-vocabulary`'s and v3 is `cache-notify-source`'s (`notify-vocabulary` §1). `publish.py` has no
catalog domain today, so this module adds the `notification-catalog` domain with a row-append
operation, the way `aptitudes` added its bracket selector. It adds the eight existing ids with
their `displayName` rows, `territory.lost`, and their `messageKeys` (`world.turn-entry`, plus
`world.release-forecast` for `loam.release`). It sets `promotions.toast = TOAST_TIER`
(the world's old `categories.ts:23`, GONE as of NS5.11 — v2 sets `promotions.toast` itself).

**The GG-50 row.** `ui/volumeMatrix.test.ts` "World notification rail" keeps `render-all` and gets a
new reason: *"structurally one resolved turn's notifications for one player (`worldLatestTurn`), the
same one-turn bound as the playback keyframe rail; the visible toast stack is capped at three."* That
replaces today's claim of an End Turn flush that nothing calls.

**WorldStage:**

| Today | After |
|---|---|
| `useState<RailItem[]>([])` (`WorldStage.tsx:142`) | Removed. The rail reads `feed` through `worldLatestTurn({ worldId, lastResolvedTurn: dto.currentTurn - 1 })` |
| `onOpen` / `onDismiss` / `onUndoDismiss` edit local state (`:526-535`) | `useSetNotificationState()` with `read` / `dismissed` / `read` |
| `CacheClaimPrompt` → `onNotify` appends a web-derived `RailItem` (`:595-608`; built by `captureLoserToast`, `stages/world/cacheClaim/captureNotice.ts:48-62`, filed under the wrong category, `command.dropped`, `:56`) | See §Debt |

### Debt — the web-derived capture-loss notice (named, sequenced)

`captureLoserToast` tells a player their vault changed hands by comparing live owner reads on the web.
It is a second source outside the SSOT. It stays, as named debt, until the server says it through
`claim.lost:`:

1. **Until the producer line lands:** the item keeps rendering in the world rail through a world-local
   adapter (`stages/world/notify/legacyCaptureLoss.ts`, new). It is not durable, and it is never
   injected into the feed. Its category is corrected to `territory.lost`.
2. **When `claim.lost:` ships:** delete the adapter and the toast half of `captureNotice.ts`. The
   server row replaces it. `captureHeader` (the vault header's own live read) is not a notification
   and stays.

The SOLID rule (DESIGN-GATE §2 invariant 15) allows grandfathered debt only with a named fix, and
step 2 is that fix, gated on the ask below.

## Cross-program asks (gate G0)

| Ask | Owner | Change | Why here |
|---|---|---|---|
The ids are the map's (§G0 asks), where each also has its default.

| # | Ask | Owner | Change | Why here |
|---|---|---|---|---|
| A1 | Relocate `world-notify` + widen `NotifyCategory` | world-stage, `world-notify` (`world-stage-map.md:78`) | The move in §4, plus the volume row reason at `world-stage-map.md:241` | The ideal's filed ask (§Ask filed on owning program) |
| A2 | Move the fog rule to Core | world-stage, `world-wire` (`world-stage-map.md:70`) | `VisibleTo(TurnReportEntry, …)`, `IsStaticFact` and `StaticFactDetailPrefixes`, unchanged (`WorldEndpoints.cs:565-587`), into `gk-core/src/FusionRpg.Core/World/Intel/WorldReportVisibility.cs`. The endpoint calls it. `WorldTurnReportFogTests` pass unmodified | One rule, two consumers (SOLID S) |
| A3 | `claim.lost:{sectorId}` with `audience = previousOwner` | world-map, `ClaimResolver` (`ClaimResolver.cs:122`, beside `claim.held:`); its playback row is world-stage `world-playback` | One additional `report.Add` when the claimed sector had another owner, and one `playbackTable.ts` row. `IsStaticFact` treats every `claim.` line as a static fact (`WorldEndpoints.cs:583`), but `VisibleTo` checks `Audience` first (`:569`), so the new line reaches only the loser | Removes the §Debt. The loser has no audience-scoped line today |
| A4 | `audience: entity.OwnerFactionId` on `legion.starved:` | loam, `loam-legions` (`LegionSupply.cs:138-139`; [loam-map.md](../loam-map.md)) | Add the named argument | A starved legion is destroyed that turn, so no later read can find its owner. With the audience, a `legion.lost` category row is added (classifier row, translator sample and the next catalog version, in one change by whoever lands second). Until then, a starved legion is unmapped (it stays in the report) |
| A6 | A `supply.besieged` row in `playbackTable.ts` | world-stage, `world-playback` | One authored row beside `supply.cut` (`playbackTable.ts:105`) | The world translator reuses that table, and the coverage guard needs every mapped prefix to render |

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests   --filter "FullyQualifiedName~WorldTurnNotification|FullyQualifiedName~WorldReportVisibility"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify|FullyQualifiedName~WorldTurnReportFog"
dotnet test tests\FusionRpg.Guard.Tests  --filter "FullyQualifiedName~NotificationCatalog"
cd web\fusion-rpg-web; npm test -- stages/world shell/notify; npm run build
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

This module crosses Core, Server and Web in one change, so run the full suite **once** before the G2
live probe (AGENTS.md "When the whole suite is actually the right call", points 2 and 3).

## Project structure

```
gk-core/src/FusionRpg.Core/World/Notify/WorldTurnNotificationClassifier.cs   → the closed table (§2)
gk-core/src/FusionRpg.Core/World/Notify/WorldRecipientRule.cs
gk-core/src/FusionRpg.Core/World/Intel/WorldReportVisibility.cs              → moved fog rule (ask)
gk-core/src/FusionRpg.Server/Notifications/WorldReportNotificationSource.cs  → IWorldTurnNotificationSource
gk-core/src/FusionRpg.Server/Notifications/WorldFactionSaves.cs              → IWorldFactionSaves (v1: header.PlayerId, the save)
gk-core/src/FusionRpg.Server/WorldEndpoints.cs                               → calls WorldReportVisibility (moved code removed)
gk-core/data/tuning/notification-catalog.v2.json                             → the world rows + territory.lost + promotions.toast (published, §4)
gk-core/tools/tuning/publish.py                                              → notification-catalog support (row append), first bump
gk-core/src/FusionRpg.Server/Program.cs                                      → catalog load line moves to v2; DI for the source
gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts                       → import moves to v2
gk-web/web/fusion-rpg-web/src/stages/world/playbackTable.ts                 → the supply.besieged row (ask A6)
gk-web/web/fusion-rpg-web/src/shell/notify/rail/*                           → the moved rail (§4)
gk-web/web/fusion-rpg-web/src/stages/world/notify/{categories,channelSettings,notifyRailStore}.ts → deleted (§4)
gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts                       → the rail's new reason (§4)
gk-web/web/fusion-rpg-web/src/stages/world/notify/worldTranslator.ts        → + samples() per mapped prefix
gk-web/web/fusion-rpg-web/src/stages/world/notify/legacyCaptureLoss.ts      → §Debt step 1
gk-web/web/fusion-rpg-web/src/shell/notify/format/translators.ts            → registers the world translator
gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx                   → §4
gk-core/tests/FusionRpg.Core.Tests/World/Notify/*.cs
gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldNotifySourceTests.cs
```

## Code style

```csharp
// One row per mapped producer line; the table IS the spec. Unmapped ⇒ null ⇒ report-only.
static readonly WorldNotifyRow[] Rows =
{
    Row.Event("loam.shortfall:",            "loam.shortfall", NotifySeverity.Important, WorldRecipientRule.SubjectFaction),
    Row.Event("loam.shortfall.unresolved:", "loam.shortfall", NotifySeverity.Important, WorldRecipientRule.SubjectFaction),
    Row.Event("legion.runway:",             "legion.runway",  NotifySeverity.Important, WorldRecipientRule.Audience),
    Row.Kind(TurnReportKinds.CommandDropped, "command.dropped", NotifySeverity.Routine, WorldRecipientRule.SubjectCommand),
    // …
};
// Longest prefix wins, so "loam.shortfall.unresolved:" is never swallowed by "loam.shortfall:".
```

## Testing strategy

1. **Classifier (Core).** For each row, an entry built with the **same prefix literal and argument
   shape** as its cited producer maps to the row's category, severity and rule. Longest-prefix
   precedence holds. Unmapped kinds (`calendar`, `command.accepted`) return `null`.
2. **Recipients.** An enemy faction that watches my shortfall sector gets no `loam.shortfall`
   (`SubjectFaction`), yet the turn-report GET still shows it the line. A `battle` line reaches exactly
   the factions the GET shows it to, through the same moved function. A dropped order reaches only its
   commander. An AI faction yields no draft. Every draft is addressed to `header.PlayerId`, the save.
3. **Moved fog rule.** `WorldTurnReportFogTests` pass without edits after the move.
4. **Dedup stability.** The same persisted report classified twice yields identical dedup keys, and
   the pump running twice pushes once (reusing `notify-service` test 2 on real entries).
5. **Forecast.** A release forecast appears only for the latest resolved turn. When the pump catches
   up over turns `R-2 … R`, only `R` carries `loam.release`.
6. **End to end (Server.Tests, in-memory store).** Reusing the fixtures the world endpoint tests
   already build: a commit that produces a shortfall → one `NotificationBatch` to the world's player,
   carrying a `loam.shortfall` item whose `worldTurn` is the resolved turn.
7. **Migration equivalence.** This is a two-step task. Before `categories.ts` is deleted, a test reads
   both it and catalog v2 and asserts that `promotions.toast` equals `TOAST_TIER` and that every one of
   the eight ids keeps its old default channel. The deletion lands only after that test is green, and
   the test goes with it: equivalence is a migration check, not a permanent guard, and the permanent
   guard is `notify-vocabulary` test 2. The moved `clickBudget` / `noBandThree` suites pass.
8. **Web.** The world rail shows the resolved turn's feed items and nothing older. Open, dismiss and
   undo call the state mutation. The capture-loss adapter still renders under `territory.lost`. The
   world translator's samples pass `notify-format`'s coverage guard. No raw token reaches the DOM.
9. **Catalog coherence (Guard).** Every category the classifier emits is registered with domain
   `world`, and every `world` category is emitted by at least one row or by the forecast. This is a
   join check, not a count.
   The join is per domain and has a **closure**: `NotificationCatalogCoherenceTests`
   (`gk-core/tests/FusionRpg.Server.Tests/Notifications/`) joins the `corpse-cache` domain the same way and fails
   any catalogue category whose domain has no join, so this check cannot silently skip a new domain.

**Live probe (map G2), RPG Server Debug scope** (`docs/contributing/live-probe-standard.md`): drive a
real world to a shortfall through `POST /api/world/{worldId}/commit` on a world created through the
real path, then read `GET /api/notifications/{playerId}` and look at the real screen. No `debug.*`
command fabricates a notification, a report line or a feed item.

## Boundaries

- **Always:** map through the closed table; route by the recipient rule; key by the persisted report
  index; reuse `describePlaybackEntry` for the words.
- **Ask first:** a new row that promotes a category (edit `promotions`); any change to the moved fog
  rule's behaviour.
- **Never:** parse a world token outside `worldTranslator.ts`; notify an AI faction; edit
  `TurnEngine.cs` or `CommitWorldTurn` for this module (the pump runs after the commit); make the
  capture-loss debt durable or feed it into the SSOT feed.

## Success criteria

1. `WorldStage.tsx` holds no notification state of its own, and its rail reads the feed.
2. Tests 1–9 green; `WorldTurnReportFogTests` unmodified and green.
3. G2 passes as a real-path live probe.
4. The §Debt adapter exists with its removal step tied to the `claim.lost:` ask.

## Seedsmith / generator

None. The classifier is a closed code table. The words are `playbackTable.ts`'s authored rows, reused
as they are, and the catalog rows are authored.

## Open questions

None owner-facing. The five asks above are cross-program (map §G0 asks), each with an owner and a default, not product questions.

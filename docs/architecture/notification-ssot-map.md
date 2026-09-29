# Capability map: notification SSOT

**Status: Draft — Phase 0 (capability map), awaiting owner review.** Written 2026-09-18 from the
ideal and its six owner rulings (R-N1 to R-N6). Module specs sit beside it in
[notification-ssot/](notification-ssot/), one per module id below. **Plan / tasks:** written after this
map is approved, at `tasks/notification-ssot-plan.md` · `tasks/notification-ssot-todo.md` (the
prefixed pair; the bare `tasks/plan.md` pair belongs to the perf stream and is never a fallback).

**Strengthen pass 2026-09-18.** An adversarial audit re-checked every citation against current code,
applied R14 and R17, and fixed the crash, replay and reconnect paths. What changed and why is in
§Strengthen pass 2026-09-18 at the end.

**Ideal it implements:** [notification-ssot-ideal.md](notification-ssot-ideal.md). Where the ideal's
pre-ruling text and a ruling disagree, the ruling wins, and this map says which one it follows.

---

## What this program is

One path from "something happened to this player" to "the player was told", whichever stage they are
standing on:

1. A **domain source** (the world turn today, the corpse-cache clock next) turns its own events into
   structured notification drafts: a category, a severity, a stable dedup key, a message key and typed
   arguments. It never writes text.
2. One **publisher** checks each draft against the category catalog, writes it durably for that
   player, and only then pushes it to **that player's** SignalR group as one `NotificationBatch`.
3. The web keeps one **feed** per player. It dedups by key, routes each item to toast, rail or off by
   the player's channel setting, and turns message keys into words through **per-domain translators**
   built from **shared formatting primitives**.
4. A **notification centre** holds the history, capped at a tunable 100 rows per category.

## Which loop it extends

Cross-cutting infrastructure, as the ideal says (§Which loop this extends). The first consumers are
on **Place 3 — Farming, hunting and defending the empire** and **Place 5 — World stage empire** of
[the-loops.md](../guide/the-loops.md): loam shortfall and release, legion runway, supply, lost ground,
and the corpse-cache clock that `cargo-fate` starts when a legion dies. All of them run on the **world
map / empire** clock, one of the three clocks that page names. No fourth clock is added.

## What it is not

- **Not a second hub.** One more named event on `RpgHub`
  (`gk-core/src/FusionRpg.Server/RpgHub.cs:9`), which the `decisions.md` "Web UI kit / bus" row (line 11)
  already fixes at "one SignalR hub (live)".
- **Not a rewrite of `world-notify`.** Its rail, five item states, channel control and click budget
  (`gk-web/web/fusion-rpg-web/src/stages/world/notify/*`) **move** to `shell/notify/` and are fed from the
  server. This is the move its own spec promised (`world-stage/spec-world-notify.md:189-191`), and it
  still needs the world-stage program's sign-off (ideal §Ask filed on owning program; gate G0 below).
- **Not a centralised text service.** R-N3 refuses one service that knows every domain's vocabulary.
  The server sends keys and typed arguments; each domain's web translator writes the sentence.
- **Not a retrofit of the ~50 existing id-only pushes.** They carry ids, not content, so they stay
  correct under R-N1 as the ideal states (R-N1, "id-only pushes stay correct today"). Moving them onto
  per-player groups is follow-up work, not a module here.
- **Not a change to the PvZ game.** No Unity write and no injector surface. The injector never
  receives a notification (standalone-first, DESIGN-GATE §2 invariant 9).
- **No actor numbers.** Nothing here produces or reads an actor combat or derived magnitude, so the
  ActorHub gate does not apply.

## Identity: `playerId` means the save (R3, R17)

The `solid-enforcement` program's `save-identity` module
([spec-save-identity.md](solid-enforcement/spec-save-identity.md), Decision 1) rules that **the
`players` row is the save and its id is the `SaveId`**, with no id rewrite. This program follows it
everywhere:

| Surface | Name used | Means |
|---|---|---|
| Wire: hub method `JoinPlayer`, group `player:{id}`, REST `/api/notifications/{playerId}`, DTO `playerId` | `player` | The save. `save-identity` §Contracts applies the same rule to the existing `{playerId}` routes and payloads: no wire name is renamed |
| New table columns (`notify-store`) | `save_id` | The save. `save-identity`'s naming rule is that new tables name the column `save_id` |
| Server and Data parameters | `saveId`, typed `SaveId` (landed by NS7.2, 2026-09-20) | The save. The type swap was mechanical now that `save-identity` has shipped its type; the wire keeps `playerId`, `player:{id}`, `JoinPlayer` and the routes unchanged (R17) |

**Who receives a notification.** A notification is addressed to a **save**, and within it to the
save's **human empire**. `save-identity` guarantees every save has exactly one `human` empire (its
§Testing, "Every save has exactly one `human` empire"). An empire whose controller is `ai`, Zomboss's
included, gets nothing. So the routing key is the save and nothing finer. If a save ever holds two
human empires, the key widens to `(SaveId, EmpireId)`. That change is named here and not built.

**Which save a connection gets.** A web connection joins the group of **the save it is showing**, not
the server-wide `current_player_id` setting. Two browsers showing two saves get two groups. Today the
web shows the save that `/api/players` reports as current (`gk-web/web/fusion-rpg-web/src/app/SaveSelect.tsx:26`),
so in practice both follow that setting, and the routing stays correct if that ever changes. An LLM
playing "as another player" (R-N1) is served the same way: its own save, its own connection, its own
group.

## Rulings → where each lands

| Ruling | What it requires | Module that owns it |
|---|---|---|
| **R-N1** per-player routing is a prerequisite | A per-save SignalR group (R17: the player row is the save) and a push seam that routes on that id. Nothing pushes content until it exists | `player-routing` (wave 1, blocks `notify-service`) |
| **R-N2** open category registry, 100 per category, and the word is *category* | The category catalog is open (a feature adds its own rows) and defaults every category to the rail. Toast and Critical are promotions made in one reviewed block. The 100 is a tunable retention tail, marked with the exemption comment | `notify-vocabulary` (catalog + promotions), `notify-store` (per-category prune) |
| **R-N3** per-domain translators on shared formatting primitives, primitives first | The shared primitives and the translator contract are built **before** any domain translator | `notify-format` (wave 2, before either source) |
| **R-N4** Critical preempts at the three-toast cap, and marking a category Critical is a reviewed change | `NotifySeverity` is a closed enum. The catalog's `promotions.critical` block is the only way to raise a category's ceiling. The toast selection puts Critical first | `notify-vocabulary`, `notify-client` |
| **R-N5** a stable dedup id from day one | Every draft carries a `dedupKey`. The store keeps `UNIQUE(save_id, dedup_key)` plus a short key ledger that outlives the retention prune, and the client dedups on the same key | `notify-vocabulary` (field), `notify-store` (constraint + ledger), `notify-client` (dedup) |
| **R14** (2026-09-18) the history screen is a "Notices" tab in the Chronicle layer | No rail entry, no key, no change to the nine player layers | `notify-centre` |
| **R17** (2026-09-18) the player row is the save | Every `playerId` here is the `SaveId`, and new columns are `save_id` (§Identity) | `player-routing`, `notify-store`, `notify-service` |
| **R-N6** a same-turn burst goes out as one `NotificationBatch` | Each turn a pump run publishes is one batch per save, in a fixed order, and every push is a batch (a single item is a batch of one) | `notify-service`, `notify-client` |

**Where this map departs from the ideal's pre-ruling text, and why:**

- The ideal's §The shape rework 3 says *"the server decides category, severity and text"*. R-N3
  replaces "text": translation mirrors `world-playback`, which lives on the web
  (`stages/world/playbackTable.ts:247`). The server still decides category, severity, audience and
  dedup, because those drive retention and routing. The words are the web's, which also keeps them
  translatable (`i18n/magnitude.ts:15` takes a locale; the server has no i18n).
- The ideal's §The shape rework 2 says *"a single closed registry"*. R-N2 overrules that: the registry
  is **open**, and the closed parts are the severities, channels, argument kinds and the promotions
  block.
- The ideal's §The shape rework 1 has new mounts default to *"dismiss-only (no auto-flush)"*, and its
  §Real gap C1 flags that this loses the GG-50 bound. This map does **not** adopt dismiss-only. The
  rail is mounted on the world stage only in v1, and there its filter is "the most recently resolved
  turn". That is the existing flush rule expressed as a filter, and it survives a reload. Every other
  stage gets toasts and the centre. A later rail mount on another stage must declare its own bound in
  `ui/volumeMatrix.test.ts` first (`notify-client` §Boundaries).

## Modules

Stable kebab-case ids, chosen once.

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `notify-vocabulary` | Every vocabulary the program shares, in one place. The **open** category catalog `gk-core/data/tuning/notification-catalog.v1.json`: each row has an id, owning domain, player display name and its message keys, plus the reviewed `promotions` block (toast, critical). v1 ships empty, and each source's module adds its rows alongside its translator. The tunables `gk-core/data/tuning/notification.v1.json`: retention per category, repeat window in world turns. The closed enums `NotifySeverity`, `NotifyChannel`, `NotifyArgKind`, `NotifyRefKind`, `NotifyDelivery`. The wire DTOs in `FusionRpg.Contracts`. The Core parser and the host loaders | — | 1 |
| 2 | `player-routing` | R-N1. A per-save SignalR group `player:{id}` (the wire keeps the word "player", §Identity), `RpgHub.JoinPlayer(playerId)`, and an `IPlayerPush` seam built like `IDelveLivePush`. The web joins on connect, reconnect and save switch | — | 1 |
| 3 | `notify-store` | `rpg_notification`, `rpg_notification_key` (the dedup ledger) and `rpg_notification_source_cursor` in `FusionRpg.Data`. Idempotent append on `UNIQUE(save_id, dedup_key)`. The per-category retention prune and the source-cursor advance run in the **same** transaction as the insert. A per-save `rev` that every insert and every state change bumps, so one `since` cursor catches up both new rows and state changes. Read, dismiss, catch-up and per-category history reads | `notify-vocabulary` | 2 |
| 4 | `notify-format` | R-N3's shared half on the web, built first: the argument primitives (magnitude through `formatMagnitude`, counts, turns, references rendered as `Pending` and never as a raw id), the `NotifyTranslator` contract and a registry keyed by owning domain, and a guard that every catalog `(category, messageKey)` pair resolves through a registered translator | `notify-vocabulary` | 2 |
| 5 | `notify-service` | The server application layer. `NotificationPublisher` validates drafts, applies the repeat window, appends, and **then** pushes one batch per save. The `IWorldTurnNotificationSource` seam and the world-turn pump: a cursor per world, advanced in the same transaction as that turn's rows, run after every advancing commit and once at boot. Only the newest turn of a commit-triggered run is delivered **live**. A boot run and any lagging turn are delivered as **catch-up**, which never toasts. The REST catch-up and state endpoints | `notify-vocabulary`, `player-routing`, `notify-store` | 3 |
| 6 | `notify-client` | The web feed per save. Subscribes to `NotificationBatch` and `NotificationStateChanged` through `lib/bus`. Catch-up by `rev` after every join. Dedup on `dedupKey`, and the higher `rev` wins a merge. Channel routing (open-id `channelSettings`, same storage key). Toast selection with Critical first (R-N4). The rail mount-policy type with `worldLatestTurn`, and the feed-to-rail state selector. The app-level toast bridge. It touches no world-stage file | `notify-vocabulary`, `notify-format`, `notify-service`, `player-routing` | 4 |
| 7 | `world-notify-source` | **First consumer.** A pure Core classifier from committed `TurnReport` entries, plus the post-commit loam-release forecast, to drafts, with recipients chosen by the world fog rule (moved unchanged from `WorldEndpoints.cs` into Core `WorldReportVisibility`, NS5.2 — not rewritten). The web world translator over `playbackTable.ts`. The A1/A2-gated migration, landed 2026-09-21: the `world-notify` rail moved to `shell/notify/rail/`, catalog v2 (the world rows plus `promotions.toast = TOAST_TIER`) and then v3 (the cache rows, NS6.4) are what both hosts load, and the world's `categories.ts`/`channelSettings.ts` are GONE (NS5.11). `WorldStage.tsx` renders the feed through `worldLatestTurn` (NS5.10) | `notify-service`, `notify-client`, `notify-format` | 5 |
| 8 | `cache-notify-source` | **First non-world-report consumer**, on the same world-turn pump. Reads the durable `rpg_corpse_cache_decay_log` outcomes and newly started decay clocks for the turns since the cursor. Produces `cache.created` and `cache.decayed` drafts. Web translator | `notify-service`, `notify-format` | 6 |
| 9 | `notify-centre` | The band-2 history surface, a "Notices" tab in the Chronicle layer (R14). One category at a time, with at most `retainPerCategory` rows each: read, dismiss, reopen. Authored through GUI Lego as recipe + fold + bus, behind the `/idea-ui` → owner piece gate | `notify-client`, `notify-service` | 6 |

**Dependency direction, no cycles.** `notify-vocabulary` and `player-routing` have no dependencies.
`notify-store` and `notify-format` read only the vocabulary. `notify-service` joins
vocabulary + routing + store. `notify-client` joins the service's wire with format and routing. The
two sources and the centre are leaves.

## Build order

```
Wave 1  notify-vocabulary ∥ player-routing
Wave 2  notify-store ∥ notify-format                       (format before ANY domain translator — R-N3)
Wave 3  notify-service
Wave 4  notify-client
Wave 5  world-notify-source                                (first consumer; migrates world-notify)
Wave 6  cache-notify-source ∥ notify-centre
```

**Why this order.** `player-routing` is in wave 1 because R-N1 makes it a prerequisite: no module
that pushes content can merge before it exists. `notify-format` is in wave 2, ahead of both sources,
because R-N3 says translators written first do not converge. The world source comes before the cache
source because it migrates a surface that already ships and is already unfed (`WorldStage.tsx:142`),
so it proves the whole path against real events before a second domain joins. The centre is last
because it is a band-2 menu under GUI Lego's owner piece gate, and nothing earlier depends on it: the
data it shows is in the store from wave 3.

## Gates

| Gate | Proves | After |
|---|---|---|
| **G0 — asks answered** | Every ask in §G0 asks below has an answer, or its stated default applies. A1 and A2 block wave 5, and A5 blocks wave 6. Nothing else blocks | before wave 5 (A1, A2) and wave 6 (A5) |
| **G1 — routed and durable** | A draft published for save A is stored **before** any push. It reaches only connections that joined `player:A`, and a connection joined as B receives nothing. Publishing the same draft again stores nothing and pushes nothing, **including after its row was pruned**. A crash injected between a turn's commit and its push leaves the rows stored and the cursor advanced, and the catch-up GET delivers them. A connection that joins after the push still gets the row through the catch-up GET, and receiving it both ways renders it once. A boot catch-up run produces no toast | wave 3 |
| **G2 — the world tells you** | One real `POST /api/world/{worldId}/commit` that starves a component produces a `loam.shortfall` toast for the committing player and no one else. The world rail shows exactly the just-resolved turn's items. A reload shows the same rail from the catch-up alone. Tested as RPG Server Debug scope: a real commit on a real world row, read back through `GET /api/notifications/{playerId}`, never through a debug fabricator (live-probe standard) | wave 5 |
| **G3 — a second domain and a history** | A legion death that starts a cache produces `cache.created`, and a decay tick that destroys items produces `cache.decayed`, both through the same pump and in the same batch as that turn's world items. The centre lists one category's history, capped at `retainPerCategory` | wave 6 |

**Gate status (2026-09-21).** **G1 is green** (`NS3.7`, and reproduced end to end by `NS5.12` through
the real `/commit` route). **G2 is BLOCKED, not met:** its live probe (`NS5.13`) needs a world created
through the real path, and `RpgStore.CreateWorld`'s only caller in `src/` is the SIM route
`/api/test/world/create` (`WorldEndpoints.cs:602`); no route can make a component starve either (the
in-memory fixtures mutate the world before `CreateWorld`). Filed as `WS-live-1` (world-stage,
`world-wire`) and `NS-fence-4`. What the chain proves without the live install: `NS5.12` (real commit →
real pump → the real source → the real publisher → one live batch for the world's own save only, read
back through the shipped catalogue) and `NS6.5` (both real sources, one batch, R-N6). **G3's first half
is green** (`NS6.5`); its second half is the centre, gated behind the gui-lego acceptance (`NS6.8` →
`NS6.11`/`NS6.12`).

## G0 asks — each with its owner and its default

The resolver for every ask is the repo owner, speaking for the owning program. None of these is
irreversible, so each has a default that applies if it is still unanswered when its wave starts. A
gate only holds work back on an irreversible act that has a named resolver and a default.

| # | Ask | Owning program / module | Blocks | Default if unanswered |
|---|---|---|---|---|
| A1 | Relocate `world-notify` (store, rail, channel settings, click-budget tests) to `shell/notify/rail/` and replace `NotifyCategory`'s closed union with the catalog. Also update the volume row at `world-stage-map.md:241` to the `worldLatestTurn` reason | world-stage, `world-notify` (`world-stage-map.md:78`) | wave 5 | None. Wave 5 edits another program's shipped module, so it waits for the answer |
| A2 | Move `VisibleTo(TurnReportEntry, …)`, `IsStaticFact` and `StaticFactDetailPrefixes` unchanged from `WorldEndpoints.cs:565-587` into a Core `WorldReportVisibility` | world-stage, `world-wire` (`world-stage-map.md:70`) | wave 5 | None, for the same reason. `WorldTurnReportFogTests` must pass unmodified |
| A3 | Add `claim.lost:{sectorId}` with `audience = previousOwner` beside `claim.held:` (`ClaimResolver.cs:122`), plus a playback row for it | world-map, `ClaimResolver` ([world-map-program.md](world-map-program.md)); the playback row belongs to world-stage `world-playback` | nothing | Declined: the web-derived capture notice stays as the `world-notify-source` §Debt adapter, and the loser is told only through it |
| A4 | Add `audience: entity.OwnerFactionId` to `legion.starved:` (`LegionSupply.cs:138-139`) | loam, `loam-legions` ([loam-map.md](loam-map.md)) | nothing | Declined: a starved legion stays report-only (unmapped) |
| A5 | Two read-only methods on `RpgStore.CacheDecay.cs`: decay ticks, and clock starts, by owner save and turn range | deployment-hierarchy, `cache-decay-void` ([deployment-hierarchy-map.md](deployment-hierarchy-map.md) module 4) | wave 6 | Accepted: additive and read-only, with no schema change and no change to the tick. The author runs that program's `CacheDecay` tests |
| A6 | A playback row for `supply.besieged:` (`SupplyGraph.cs:113`). The producer ships, and `playbackTable.ts` has no row for it, so the playback panel already shows the unrecognised-token marker in development | world-stage, `world-playback` | nothing | Accepted: `world-notify-source` adds the row in its own change, because `notify-format`'s coverage guard needs it for `supply.change` |

A report line is not world state. `StateHasher.Hash` is taken over the world
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:653`), so A3 and A4 move no state hash. They do
change report output, so the owning program runs its own turn-report tests.

### Answers

| # | Answer | Date | Note |
|---|---|---|---|
| A1 | Accepted (owner, 2026-09-21) | 2026-09-21 | The move of `categories.ts`, `notifyRailStore.ts`, `channelSettings.ts`, `NotifyRail.tsx`, `RailItem.tsx`, `ChannelControl.tsx` + click-budget tests, the widened `NotifyCategory` and the `world-stage-map.md:241` volume row all stand. Landed: the store, rail and control live in `shell/notify/rail/` now (the old `notifyRailStore.ts` is GONE, and so are the world `categories.ts`/`channelSettings.ts`, NS5.11) — releases NS5.7–NS5.11 (`notification-ssot-todo.md` NS0.1) |
| A2 | Accepted (owner, 2026-09-21) | 2026-09-21 | `VisibleTo(TurnReportEntry, …)`, `IsStaticFact` and `StaticFactDetailPrefixes` move unchanged from `WorldEndpoints.cs:565-587` into a Core `WorldReportVisibility`; releases NS5.2/NS5.3 and transitively NS5.12, NS5.13, NS6.5 (`notification-ssot-todo.md` NS0.2) |
| A3 | Declined (default applied) | 2026-09-19 | Reversible ask, unanswered when NS0.3 ran; the `world-notify-source` §Debt adapter stays, per this row's own stated default |
| A4 | Declined (default applied) | 2026-09-19 | Reversible ask, unanswered when NS0.4 ran; `legion.starved:` stays unmapped, per this row's own stated default |
| A5 | Accepted (default applied) | 2026-09-19 | Reversible ask, unanswered when NS0.5 ran; wave 6 proceeds, per this row's own stated default |
| A6 | Accepted (default applied) | 2026-09-19 | Reversible ask, unanswered when NS0.6 ran; `world-notify-source` adds the `supply.besieged` playback row, per this row's own stated default |

## Cross-program dependencies

| Dependency | Owning map / module | What this program needs | Gate |
|---|---|---|---|
| `world-notify` relocation + source swap | [world-stage-map.md](world-stage-map.md) row 78, module `world-notify` | Sign-off to move `categories.ts`, `notifyRailStore.ts`, `channelSettings.ts`, `NotifyRail.tsx`, `RailItem.tsx`, `ChannelControl.tsx` into `shell/notify/`, and to replace `NotifyCategory`'s closed union with the catalog. **Granted and landed** (NS5.7–NS5.11): the old `notifyRailStore.ts` and the world `categories.ts`/`channelSettings.ts` are GONE; the rail lives at `shell/notify/rail/` | G0 |
| Fog rule reuse | `world-stage`, `world-wire` (`WorldEndpoints.cs:565-587`) | Move `VisibleTo(TurnReportEntry, …)` and `IsStaticFact` unchanged into a Core `WorldReportVisibility`, so the turn-report GET and the notification source share one rule. `WorldTurnReportFogTests` must stay green unmodified | G0 (A2) |
| **A real world-creation route** (added 2026-09-21) | world-continuity, [world-continuity-map.md](world-continuity-map.md), `spec-world-creation.md` (§Wiring gap) | Gate G2's live probe must run on a world created through the real path, and today the only caller of `RpgStore.CreateWorld` is the SIM route `/api/test/world/create` (`WorldEndpoints.cs:602`) — the fabricator the probe's own acceptance forbids. The route is that program's spec'd deliverable, so `NS5.13` waits on its work, not on anything this program can build | G2 (`NS5.13`) |
| `claim.lost:` producer line | world-map `ClaimResolver` (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:122`) | When a claim takes a sector from another faction, add one more line scoped to the previous owner, so the loser is told from the server. Until then, the web-derived capture-loss notice (`stages/world/cacheClaim/captureNotice.ts:48-62`) is kept as named debt (`world-notify-source` §Debt) | G0 (A3) |
| `legion.starved:` audience | [loam-map.md](loam-map.md), `loam-legions` (`LegionSupply.cs:138-139`) | One named argument, so the starved legion's owner can be told | G0 (A4) |
| Corpse-cache reads | [deployment-hierarchy-map.md](deployment-hierarchy-map.md) module `cache-decay-void` (`RpgStore.CacheDecay.cs`) | Two read methods on that program's own partial: decay outcomes by owner save and tick range, and caches whose decay clock started in a turn range. Read-only, and no change to the tick | G0 (A5) |
| Save identity | `solid-enforcement`, `save-identity` ([spec-save-identity.md](solid-enforcement/spec-save-identity.md)) | Nothing to wait for. This program uses the save's id as it is today and adopts the `SaveId` type once it exists (§Identity). `ListPlayers` skipping archived rows (that spec, D2) is what keeps the legacy Zomboss row out of the boot catch-up | — |
| Player-facing gates on feeders | [deployment-hierarchy-map.md](deployment-hierarchy-map.md) G2/G4 (ideal §Real gap C3) | Named, not required: once `cache-notify-source` ships, "the player is told" can become a gate criterion there. `injury-tiers` is unbuilt (no `WoundTier` symbol in `src/`), so wound worsening is a future source with no module in this map | — |

## What the consuming specs get from here

Three sibling specs already name this program as the future home of their "notification hook". This
map and its specs are the SSOT they consume. What each one gets:

| Consuming spec | Its event | Served by |
|---|---|---|
| `loam-relics-and-wonders/spec-wonder-build-flow.md` §Notification hook (697-706) | A `build` refused on `wonder.cap-reached`. A Wonder whose construction begins | `world-notify-source`: `command.dropped` from `BuildResolver.cs:120` → `:199`, and `growth` from `build.started:` (`BuildResolver.cs:170`) |
| `scoped-inventory-hierarchy/spec-sector-storage.md` §Notification hook (376-385) | A sector's vault changing hands on capture | `world-notify-source`: `territory.lost` from the requested `claim.lost:` line. Until that line exists, the named debt adapter |
| `scoped-inventory-hierarchy/spec-cargo-fate.md` §Notification hook (245-252) | A dead legion's cargo becoming a decaying cache | `cache-notify-source`: `cache.created` read from the cache's started clock, exactly as that spec expects ("read… the same way it would any other `corpse-cache` creation") |
| `empire-development-map.md` open item (110-119) | All three above | As above |

**Lines in those documents that these specs now contradict.** The strengthen pass added a one-line
cross-reference note under each of the three passages, pointing here. It did not rewrite them: each
owner fixes its own text.

1. `empire-development-map.md:117-119`: *"every event already fires a real
   `TurnReportEntry`/report line a future notification consumer can read, nothing needs to be
   re-plumbed, only picked up."* That is false for two of the three events. A legion's cargo moving to
   a cache writes **no** report line: `MoveLegionCargoToCorpseCacheUnlocked`
   (`RpgStore.CargoFate.cs:47`) takes no report, and `RpgStore.WorldGraphDiff.cs` never touches one.
   `cache-notify-source` reads the cache rows instead. A sector changing hands writes `claim.held:`
   with no audience for the **loser** (`ClaimResolver.cs:122`), so telling the loser needs one new
   producer line (`claim.lost:`, map G0). Something does have to be re-plumbed.
2. `loam-relics-and-wonders/spec-wonder-build-flow.md:699-700`: *"a Wonder finishing construction (a
   `TurnReportEntry` already fires — `"build.started:{structureId}"`…)"*. `build.started:` fires when
   construction **starts**: `BuildResolver.cs:161` sets `ConstructionTurnsRemaining =
   structure.BuildTurns`, and `:169-170` reports it. The writes to `ConstructionTurnsRemaining` are
   that set-at-start, the per-turn countdown in `DecrementConstruction` (`LoamPhases.cs:103-115`) and
   the clear-on-loss (`LoamPhases.cs:223`). The countdown takes no report, so no line marks a slot
   reaching zero. (Strengthen pass: the first draft said the grep found only the set and the clear,
   and missed the countdown. The conclusion stands.) A "Wonder finished" notification
   therefore needs a completion producer that does not exist. It is not a notification-ssot gap, and
   it is named here so the wonder program does not assume it.
3. `scoped-inventory-hierarchy/spec-sector-storage.md:378-380`: *"…with zero signal to the player who
   lost or gained it."* That is stale. A web-derived capture-loss notice already ships
   (`gk-web/web/fusion-rpg-web/src/stages/world/cacheClaim/captureNotice.ts:48-62`, wired at
   `WorldStage.tsx:595-608`), misfiled under `command.dropped` (`captureNotice.ts:56`).
   `world-notify-source` §Debt names it and sequences its replacement.

`spec-cargo-fate.md` §Notification hook is **consistent** with these specs, and nothing in it needs
changing.

## Seedsmith / generators

No module in this program produces or consumes generated content. Per module:

| Module | Generator involved? | Why |
|---|---|---|
| `notify-vocabulary` | No | The category catalog is a hand-authored **runtime catalog** (tunables-ssot §1 "Runtime catalog" row). A feature authors its own rows the way `status-catalog` rows are authored. Numbers publish `v{n+1}` through `gk-core/tools/tuning/publish.py` (T4) |
| `player-routing` | No | Transport code, with no content |
| `notify-store` | No | A schema with runtime rows only |
| `notify-format` | No | Shared primitives are code, and the copy they format is authored |
| `notify-service` | No | Validation and transport, with no content |
| `notify-client` | No | Web state and routing, with no content |
| `world-notify-source` | No | The sentences are `playbackTable.ts`'s authored rows, reused as they are. The classifier is a closed code table |
| `cache-notify-source` | No | Authored translator copy over durable decay-log rows |
| `notify-centre` | No | A GUI Lego recipe and fold, with authored chrome copy |

## DESIGN-GATE §5 checklist (this session, 2026-09-18)

- [x] Subsystems identified: web shell and world stage (UI), Server/SignalR, Data/SQL, world turn, and
      corpse-cache.
- [x] Session boundary recorded (`tasks/sessions/notification-ssot-spec-20260918.json`; the strengthen
      pass under `tasks/sessions/strengthen-notify-20260918.json`). The boundary check flags drift only
      in other sessions' records.
- [x] §1 rows read this session: Anything at all (software-architecture, decisions, SOLID §2.15,
      session-boundary); Product vision (`the-game.md`, `the-loops.md`); Data/SQL (data-architecture);
      UI (game-gui-principles GG-1/5/9/16/50/53/62, information-architecture §1/§3/§4); Player menus
      (gui-lego-ideal, gui-lego-authoring). Also tunables-ssot and `spec-world-notify.md`.
- [x] `decisions.md` checked: no notification lock. "one SignalR hub" (line 11) is honoured.
- [x] Every factual claim cites file:line, verified against code, not comments.
- [x] `audit-doc-citations.py` reports no HIGH on the map, the 9 specs or the ideal.
- [x] No constraint claimed without evidence: "no `onCommit` caller", "one `CommitWorldTurn` caller",
      "no report line on cargo-fate", "no construction completion line" are each repo greps run this
      session.
- [x] No §2 invariant contradicted. Invariant 16's full trigger sets are enumerated in
      `player-routing`, `notify-service` and `notify-client`, including the key-set edge (player switch;
      a world with no cursor).
- [x] No population count pinned. Pinned literals are closed enums only (`notify-vocabulary` test 1,
      with the reason).
- [x] Where order varies in real play (push vs catch-up, reconnect vs player switch), the criteria say
      order-independent and both orders are tested.
- [x] No actor magnitude: the ActorHub box does not apply.
- [x] No SOLID-violating parallel path. The one grandfathered path (the web-derived capture-loss
      notice) has a named, sequenced removal (`world-notify-source` §Debt). The one-wave
      `channelSettings` overlap has a removal step (`notify-client` §3).

## Open questions carried to the owner

1. ✅ **Ruled 2026-09-18 (R14, [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md)): a "Notices" tab inside the Chronicle layer.** No rail entry,
   no key, no change to the nine player layers. `notify-centre` is written against exactly this.

Everything else the ideal left open is settled here, as a decision rather than a question:

- **Which categories are Critical?** None ship Critical. This follows the hard-block list precedent,
  which also "defaults to empty and every addition is argued" (`spec-world-notify.md` §5). R-N4 makes
  each addition a reviewed edit to `promotions.critical`.
- **Does Critical override a player's "off"?** No. The player's channel setting stays authoritative
  (`spec-world-notify.md` §6: player settings, not tunables). Critical changes only the order within
  the toast cap.
- **Can unread rows be pruned?** Yes. R-N2's bound is a count per category, so the 101st-oldest row
  goes whatever its state. Losing an unread row takes 100 newer rows of the **same** category, which
  is the per-category property R-N2 asked for (ideal §R-N2, property 1).
- **Which deployment-hierarchy candidate goes first?** Corpse-cache decay (ideal Open question 3).
  It is built and its durable log already exists (`RpgStore.CacheDecay.cs:47`, `:193`). Injury
  worsening is unbuilt.
- **Does catch-up toast?** Never. Toasts are for things arriving now. Items that arrive through
  catch-up go to the rail and the centre (`notify-client` §2). "Catch-up" covers two paths: the
  client's GET after a join, and a server push the pump marks `catch-up` (a boot run, or a turn the
  pump reached late). See `notify-service` §3.

## OWNER questions (strengthen pass 2026-09-18)

None. Every finding below was either a code-truth correction or a technical choice, resolved on SOLID
and the existing rulings. The G0 asks are cross-program acknowledgements with stated defaults, not
product questions.

## Strengthen pass 2026-09-18 — what changed

| Id | Severity | What was wrong | Fix |
|---|---|---|---|
| S1 | HIGH | Crash window: the pump appended a turn's rows, then set its cursor in a separate call. A crash in between re-ran the turn. Because the prune may already have deleted some of those rows, the re-run could re-insert them and push them again | `notify-store` §2: one store call per turn writes every save's rows, the prune and the cursor in one transaction. A key ledger keeps a pruned row's key long enough that no source can re-insert it |
| S2 | HIGH | The boot catch-up pushed live batches. A web client that reconnected before the boot step ran would toast stale news | `notify-service` §3: a batch carries `delivery = live \| catch-up`. Boot runs and lagging turns are `catch-up`, and `notify-client` never toasts them |
| S3 | HIGH | A reconnect only fetched new rows (`since = maxSeq`). A dismiss made by another session while this one was offline was never seen. A slow catch-up page could also overwrite a newer live state change | `notify-store` §1: a per-save `rev`, bumped by every insert and state change, is the catch-up cursor. `notify-client` §2: a merge keeps the higher `rev` |
| S4 | MED | R17: the player row is the save. New table column was `player_id`, against `save-identity`'s rule that new tables name it `save_id` | §Identity; `notify-store` column renamed; wire names unchanged, as `save-identity` §Contracts rules |
| S5 | MED | `GetWorldTurnReport` does not return `null` past the hot tail: it **replays from turn zero** (`RpgStore.WorldTurns.cs:731-771`). A lagging pump would trigger one full replay per turn, and a replayed report lacks the post-Step lines (`AddPostStep`, e.g. `RpgStore.CacheRetrieval.cs:399`), so its entry indexes differ from the stored report | `notify-service` §3: the pump checks the stored body first (`GetWorldTurnLog(...).ReportJson`, `RpgStore.WorldTurns.cs:701`) and skips a trimmed turn, so it never triggers a replay |
| S6 | MED | R14 landed, but `notify-centre` still carried the "OWNER question: where the centre lives" and an "its own layer" alternative | `notify-centre` rewritten against R14 |
| S7 | MED | `notify-centre` kept the selected category in "local VM state". `PanelShell` is a Radix `Dialog`, which unmounts its content on close, so the selection would reset and break GG-51 | `notify-centre` §2: the selection lives in a small module store |
| S8 | MED | `supply.besieged:` (`SupplyGraph.cs:113`) has no `playbackTable.ts` row, so the world translator could not render it and the coverage guard would fail | G0 A6; `world-notify-source` adds the row |
| S9 | MED | Save switch (T3) named a `Health` push as a trigger. `PUT /api/players/current` pushes nothing (`gk-core/src/FusionRpg.Server/Program.cs:1077`), and `Health` is pushed only on an injector heartbeat (`RpgHub.cs:177`) | `player-routing` T3: the switching session's own `useSelectPlayer` success (`lib/bus/mutations.ts:184-194`); the group is the save the connection shows |
| S10 | MED | G0 named asks without owners or defaults, and missed the `legion.starved:` ask's real owner (loam, not world-map) | §G0 asks table |
| S11 | LOW | Contradiction 2 said the grep found no countdown write. `DecrementConstruction` counts down (`LoamPhases.cs:103-115`) | Corrected; the conclusion stands |
| S12 | LOW | Stale line numbers: in the ideal (`LoamPhases.cs:160,166`, `WorldStage.tsx:445-452`, `:135`, `:446`, `RpgHub.cs:47-48`, `WorldEndpoints.cs:210-224`, `:348`, `RpgStore.Souls.cs:142`) and in `player-routing` (`hub-provider.tsx:204-207`, `:211-216`) | Corrected in place |
| S13 | LOW | Catalog versions: `cache-notify-source` published "v{n+1}", which left the order with `world-notify-source`'s v2 implicit, and neither named the two load sites a bump must update | `notification-catalog` publishes are sequenced: v1 `notify-vocabulary`, v2 `world-notify-source`, v3 `cache-notify-source`. Each bump updates `Program.cs` and `shell/notify/catalog.ts` in the same change |

Every citation in this map and its specs was re-checked against the tree on 2026-09-18.

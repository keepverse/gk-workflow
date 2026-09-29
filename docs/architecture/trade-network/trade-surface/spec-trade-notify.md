# Spec: `trade-notify`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 9, wave 3). Not a UI-gate module: the rail, toasts and the Notices tab are
world-stage's and notification-ssot's. Every `file:line` below was opened this session. Docs only.

## Objective

Trade reaches the player through the one notification pipeline: a fixed, reviewed set of trade categories
in the open catalog, a pure Core classifier over committed report lines, a source on the world-turn pump,
and a web translator on the shared formatting primitives. A routine turn — goods banked, nothing lost
or stuck — produces **no** notification.

## Locked anchors

- **The catalog is open** (notification-ssot ruling R-N2, [notification-ssot-map.md](../../notification-ssot-map.md)
  §Rulings). Trade declares its own rows as a **fixed, reviewed list** and guards that list; it does not
  close the catalog (map §4 item 4, contradiction 1 — reconciled).
- **Every category defaults to the rail.** A promotion to toast or Critical is a reviewed change in the
  catalog's `promotions` block (R-N2, R-N4).
- **Translators compose shared primitives, primitives first** (R-N3): trade's translator is built on
  `notify-format`'s primitives, never its own formatter.
- **Stable dedup id from day one** (R-N5), **one batch per same-turn burst** (R-N6).
- **Fog:** a draft goes only to the audience that can see its source line — the visibility rule
  (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-576`), which notification-ssot's `world-notify-source` moves
  into Core; reused, never re-implemented.
- **No second report vocabulary.** Trade report lines are the providers' `TurnReportKinds` members
  (`logistics-flow` `logistics-facts`: `lane.cut`, `logistics.loss`, `logistics.strand`,
  `logistics.overflow`; `sector-yield`'s halt and banking lines; `exchange`, `counterparties`, `fleet` as
  they land). This module reads them; it mints no `trade.` report prefix. (Correction to map §6.9, which
  proposed one: the provider maps chose typed kinds.)

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Rail feed flushed on an advancing commit | `gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts:18-23` |
| Counted click budget over the rail | `web/fusion-rpg-web/src/stages/world/notify/clickBudget.test.tsx:50,59,75,85` |
| Report lines with sector and audience | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:30-31` |
| Report visibility rule | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-576` |

### Wiring gap

The rail's items are local component state (`gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx:142`);
notification-ssot `world-notify-source` moves it onto the feed. Trade rides that work.

### Real gap

No trade category, classifier, source or translator; no trade report line exists until the providers
land. The notification service itself is specced, not built
([spec-notify-service.md](../../notification-ssot/spec-notify-service.md) §3).

## Design

### 1. Trade's categories (fixed, reviewed list)

| Category | Reads (provider report kind) | Message keys |
|---|---|---|
| `trade.halt` | `sector-yield` production-halt line; the forecast halt of the latest committed turn (a Server read after commit, never hashed state) | `halted`, `will-halt` |
| `trade.waste` | `logistics.overflow` | `wasted` |
| `trade.stranded` | `logistics.strand`, `lane.cut` | `stranded`, `cut` |
| `trade.caravan` | `fleet` `caravan.intercepted`, `caravan.lost` ([spec-interception.md](../fleet/spec-interception.md)) | `intercepted`, `lost` |
| `trade.price` | `exchange` price-band crossing at a hub the viewer holds or trades at | `spike`, `crash` |
| `trade.treaty` | `counterparties` / `exchange` treaty facts (signed, ended, broken; war, peace) | `signed`, `ended`, `broken`, `war`, `peace` |
| `trade.embargo` | embargo set / lifted | `imposed`, `lifted` |

Seven categories, all default `rail`. `logistics.loss` does **not** notify: attrition is the status
line's (`trade-status`) job; a notification per leaking lane is the spam GG-53 forbids. A row whose
provider has not landed is not published. Rows are added to `data/tuning/notification-catalog.v{n}.json`
through `gk-core/tools/tuning/publish.py`, in the change that adds the matching translator (the notify-vocabulary
sequencing rule).

### 2. The classifier (Core, pure)

```csharp
// src/FusionRpg.Core/World/Logistics/TradeNotifyClassifier.cs (new)
public static class TradeNotifyClassifier
{
    // Pure. Committed report entries (+ the latest-turn forecast when IsLatestResolved) → drafts,
    // each with (category, messageKey, args, audience, dedupKey). Recipients chosen by the Core fog rule.
    public static IReadOnlyList<TradeDraft> Classify(string worldId, int turn, TurnReport report,
                                                     IReadOnlyList<Throttle>? latestForecast);
}
```

**Dedup key** from the durable fact: `trade:{worldId}:{turn}:{reportKind}:{subjectId}:{goodId}` for
report lines, where `subjectId` is the line's own subject — the sector or lane, **or** the caravan's legion
id (`trade.caravan`) or the counterparty id (`trade.treaty`, `trade.embargo`), which carry no sector —
(audit 2026-09-20: keyed on sector-or-lane only, two treaties signed in one turn, or two caravans lost on
one lane, shared a key and the second notification was dropped); `trade-forecast:{worldId}:{turn}:{sectorId}:{goodId}` for a forecast halt. Args are
references (sector, lane, good, faction) and magnitudes in `goodsUnits`, never pre-rendered text.

### 3. The source

`TradeNotificationSource : IWorldTurnNotificationSource` (`gk-core/src/FusionRpg.Server/Notifications/`, new),
registered in DI beside `world-notify-source` and `cache-notify-source`; it calls the classifier and
addresses drafts by save. It never writes and never pushes (the interface contract,
`spec-notify-service.md` §3). Forecast drafts are produced only when `IsLatestResolved` is true.

### 4. The translator (web)

`web/fusion-rpg-web/src/features/trade/notify/tradeTranslator.ts` (new), registered under the owning
domain `trade` in `notify-format`'s registry; every `(category, messageKey)` pair resolves (notify-format's
coverage guard). Words come from `trade-lexicon`.

### 5. Turn report entries

The turn report's trade section renders from `trade-status`'s fold for the same turn (one fold), plus these
categories' lines in playback order. No separate trade report store.

## Contract exposed

Seven category ids and their message keys; `TradeNotifyClassifier`; `TradeNotificationSource`; the trade
translator. Consumers: notification-ssot pump and client; `trade-click-budget`.

## Acceptance (contract level)

1. **Coverage:** every trade `(category, messageKey)` has a translator (notify-format guard passes).
2. **Dedup:** every draft carries a dedup key derived from its source line; re-running the pump over a
   turn appends nothing new.
3. **Fog:** a fixture with a foreign halt line yields no draft for the viewer; an own line yields one.
4. **Quiet steady state:** a turn whose only trade lines are banking and loss produces zero trade drafts.
5. **Batch:** a turn with several trade drafts is delivered in the turn's one batch (R-N6, asserted at the
   pump boundary with the trade source registered).
6. **Rail default:** every trade row's default channel is `rail`; no trade row appears in `promotions`
   without a reviewed change.
7. **Fixed list:** the trade rows in the catalog equal the declared list (the seven ids, a declaration with
   its reason); an extra `trade.*` row fails the test.

## Test plan and verification boundary

- Core classifier (dedup, fog, quiet) — `core-fallback`.
- Server source registration and pump batch — `server-fallback`.
- Catalog rows — the notification catalog's own boundary as notify-vocabulary defines it (none mapped
  today; that program's spec owns adding it).
- Web translator coverage — vitest. **Gap, stated:** no `web/` verification boundary
  (`gk-core/scripts/verification-boundaries.v1.json`); report, never run the full suite instead.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- Blocked on notification-ssot `notify-vocabulary`, `notify-format`, `notify-service` being built.
- A promotion to toast/Critical is a reviewed catalog change, never a code default.
- The rail component is world-stage's; this module never touches it.

## Dependencies

`trade-lexicon`, `trade-status`, `throttle-forecast`; notification-ssot `notify-vocabulary`,
`notify-format`, `notify-service`, `world-notify-source` (Core fog rule); report producers in
`sector-yield`, `logistics-flow`, `exchange`, `counterparties`, `fleet`.

## Boundaries

- **Always:** rail default; dedup from the durable fact; audience from the fog rule.
- **Ask first:** any promotion; an eighth trade category.
- **Never:** a notification for routine banking or loss; a second report prefix family; a private formatter.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: notification SSOT (consumer), world report (read), fog rule.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: notification-ssot-ideal (rulings R-N1..R-N6 headings and text in the map), notification-ssot-map
    modules, spec-notify-service §3, spec-notify-vocabulary §1, GG-53.
[x] decisions.md: Game GUI (:110) — interruption budget.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: VisibleTo, TurnReportEntry, rail onCommit, local notifyItems state.
[x] Surrounding sections read (R-N2 reconciliation note in the map).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: "no trade. report prefix" correction recorded in the map.
[x] No population pinned: 7 categories is trade's declaration; the catalog stays open.
[x] Cache: none (the pump's cursor is notify-service's).
[x] No ordering criterion (batch order is the pump's fixed order).
[x] No actor magnitude.
[x] No parallel path: one pipeline, one fog rule, one formatter set.
[ ] Registry row: "trade declares a fixed category list" needs a guard row when built.
```

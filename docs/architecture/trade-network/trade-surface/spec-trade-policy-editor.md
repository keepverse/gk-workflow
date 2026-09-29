# Spec: `trade-policy-editor`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 6, wave 4). **UI-gate:** data, the fold, the bus, command filing and acceptance
are fixed here; the layout of both homes is not (see *Layout pending `/idea-ui`*). Every `file:line` below
was opened this session. Docs only.

## Objective

Where standing trade orders are set — automation policy, never per-turn micromanagement (trade-network
ideal §6 lesson 8). Two homes, one fold:

- **(a) At a hub or bank-point sector:** its order policy — what it buys and sells, limits, and the route
  priority of flows leaving it — as a sibling inspector opened from the `trade` block.
- **(b) On a legion:** a caravan's standing trade route, as a `route` tab on the legion sheet.

Every edit files a **policy command**; policy commands set policy and move nothing themselves (ideal
§8.7). Auto-banking is on by default: a new hub needs no edit to bank.

## Locked anchors

- **Filing is not resolving** (GG-15). The filer answers *filed / replayed / refused-at-submit*; the turn
  report and the next read answer the result — the split `CargoTab` already ships
  (`gk-web/web/fusion-rpg-web/src/stages/world/legionSheet/CargoTab.tsx:16-19`).
- **Command kinds are the providers'.** `route-set`, `route-clear` (`logistics-flow` `auto-banking`);
  `order-set` and cancel (`exchange` `order-book`); the trade-route standing order on a legion (`fleet`
  `trade-route-order`, re-emitted through `legion-build` `standing-orders`). This module files them and
  adds none.
- **Legion sheet tabs are closed and reserved** (`gk-web/web/fusion-rpg-web/src/stages/world/legionSheet/LegionSheet.tsx:34-35`:
  *"Future tabs by reservation only"*). The `route` tab is a reservation filed on
  empire-inventory-surfaces `legion-sheet` ([spec-legion-sheet.md](../../empire-inventory-surfaces/spec-legion-sheet.md)).
- **Recipe + fold + closed bus; inspect in-pane** (GG-63); **no silent disable** (GG-55).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| A legion-sheet tab built as recipe + fold + closed bus, with filed/resolved notes | `CargoTab.tsx:13-28` |
| Tab rail closed to `overview` + `cargo`, reservation rule | `LegionSheet.tsx:34-35` |
| Command filing hook | `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:629` (`useSubmitWorldCommands`) |

### Real gap

No policy commands (all owned by `logistics-flow`, `exchange`, `fleet`/`legion-build`, none landed); no
policy read on `trade-wire`; no editor.

## Design

### 1. Policy read

`trade-wire` gains a W4 field per own trade sector, `Policy`: current route priorities and destinations
per good (from `auto-banking`), standing orders at this hub (from `order-book`), and for a legion the
standing trade route (from `trade-route-order`). Read-only, own faction only.

### 2. The fold

```ts
// web/fusion-rpg-web/src/features/trade/policy/foldTradePolicy.ts (new) — pure
export function foldHubPolicy(input: { sector: TradeSectorView; policy: HubPolicyView; access: AccessView[];
                                        pending: PendingCommand[]; catalog: TradeCatalogView }): HubPolicyVm;
export function foldCaravanRoute(input: { legion: LegionView; route: CaravanRouteView | null;
                                          depots: DepotView[]; pending: PendingCommand[];
                                          catalog: TradeCatalogView }): CaravanRouteVm;
```

Each editable control carries `enabled` and, when false, a `reason` (catalog copy) — a hub where the
faction's `LevelAt` is below `market`, a good that is not tradeable, a legion that is not at a depot, and
since round 4 ([decisions-round-4.md](../decisions-round-4.md)) the **missing building**: hub orders need a Trading Post (clan hubs) or a Market
(empire hubs), the caravan route needs a Caravan Yard — and, for a leg to a **foreign** hub, the hub
owner's Caravan Yard in that sector (round 5 B3, `fleet` `depot` `ForeignSite.Of`, refusal
`depot.no-foreign-yard`; reason *"This hub has no caravan yard"*) — the hold needs a Treasury (`trade-unlock` §2 flags;
reason copy *"Build a Trading Post to trade with clans"* and its siblings). Pending commands
render as *filed* on the control they came from.

### 3. The bus (closed)

| Event | Payload | Files |
|---|---|---|
| `trade.policy.route.set` | `{ sectorId, goodId, priority, destinationSectorId? }` | `route-set` |
| `trade.policy.route.clear` | `{ sectorId, goodId }` | `route-clear` |
| `trade.policy.order.set` | `{ hubSectorId, goodId, side, limit, quantity }` | `order-set` |
| `trade.policy.order.cancel` | `{ hubSectorId, goodId, side }` | `order-set` with quantity 0 — `order-book` has **no** cancel kind and **no** order id (an order is keyed by commander, hub, good and side; corrected in the round-4 reconciliation) |
| `trade.policy.hold.set` (round 4) | `{ sectorId, goodId, quantity? }` (absent = the default — round 5 A4: *keep enough to fill other traders' open buy orders at this hub*, `order-book` `OpenSellNeed`) | the `bank-hold` policy command, owned by `logistics-flow` `auto-banking` (`sector-yield` `spec-banking-fact.md` §3a; round 4 Q2 — enabled only with a Treasury, banking tier ≥ 2, in that sector) |
| `trade.policy.caravan.set` | `{ legionId, fromDepotId, toSectorId, goodIds }` | the trade-route standing order |
| `trade.policy.caravan.clear` | `{ legionId }` | clearing that standing order |

Payload shapes follow each provider's command contract as it lands; this table names the intent and is
amended to match, never the other way round.

## Contract exposed

`foldHubPolicy`, `foldCaravanRoute`, the seven bus events (round 4 adds `hold.set`), the `route` tab reservation. Consumers: the
`trade` block (`trade.block.policy.open`), the legion sheet, `trade-click-budget`.

## Acceptance (contract level)

1. **Round trip:** each bus event files exactly one command of the named kind; the next state read shows
   the policy the command set; the turn report states its effect.
2. **Defaults bank:** a new hub with no policy edit banks its goods (auto-banking), asserted on a fixture.
3. **No silent disable:** every disabled control has a reason (GG-55 scan).
4. **Filed ≠ resolved:** before the commit, the control shows *filed*; no policy value changes in the view
   until the next read.
5. **Pure folds:** no React, no fetch, deep-equal output for equal input.
6. **Own only:** a foreign hub never opens the editor; the policy read never includes another faction.

## Layout pending `/idea-ui`

Not decided here: the sibling inspector's recipe and pieces, the order row and limit editor, the route
priority control, the caravan route picker, and the `route` tab's slot tree. Through
[idea-ui-phase.md](../../idea-ui-phase.md) (queue row, piece contracts, drafts, owner accept) before build.

## Test plan and verification boundary

- Web: fold arms, bus-to-command mapping, GG-55 scan — vitest. **Gap, stated:** no `web/` verification
  boundary (`gk-core/scripts/verification-boundaries.v1.json`); report, never run the full suite instead.
- Command admission tests are the owning providers' (`core-fallback` in their specs).

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- If the `route` tab reservation is refused, caravan routes are set from the hub side only (map §8
  default).
- No command kind is added here.

## Dependencies

`trade-panel`, `trade-wire`, `trade-lexicon`, `trade-unlock` (`Routes` flag); `logistics-flow`
`auto-banking`; `exchange` `order-book`, `trade-access`; `fleet` `trade-route-order`, `depot`;
`legion-build` `standing-orders`; empire-inventory-surfaces `legion-sheet` (reservation ask).

## Boundaries

- **Always:** policy commands only; reasons on disables; filed/resolved split.
- **Ask first:** a per-turn manual transfer (that is `cargo-transfer`'s, not policy).
- **Never:** a new command kind; editing another faction's policy; a dialog for reading.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world commands (filer), legion sheet, GUI Lego menus.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: gui-lego-ideal, idea-ui-phase, GG-15/55/63, logistics-flow-map §7, fleet-map module table,
    exchange-map module table. NOT read: gui-lego-authoring.md and the legion-sheet spec body — owed by /idea-ui.
[x] decisions.md: GUI Lego (:132).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: CargoTab recipe comment, LegionSheet tab reservation, submit hook.
[x] Surrounding sections read.
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: none beyond this file.
[x] No population pinned.
[x] Cache: none owned (trade-wire refetch on own command filed).
[x] Ordering: none fixed.
[x] No actor magnitude.
[x] No parallel path: provider commands only.
[x] Registry row: none new.
[x] Round 4 reconciliation (2026-09-19): building reasons on disabled controls; cancel is order-set 0
    (no cancel kind, no order id — a contradiction with order-book fixed); Treasury hold control.
[x] Round 5 (2026-09-20): A4 default wording on hold.set; B3 foreign-hub yard reason on the caravan
    route control (reads fleet depot ForeignSite.Of through the wire, no FE derivation).
```

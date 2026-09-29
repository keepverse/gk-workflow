# Spec: `trade-panel`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 5, wave 3). **UI-gate:** this spec fixes the block's data, fold, bus, placement
in the block order and acceptance; its layout is not decided here (see *Layout pending `/idea-ui`*). Every
`file:line` below was opened this session. Docs only.

## Objective

A `trade` block on the sector inspector for any sector with a trade structure the viewer can see: the hub
(its **tier** on the Trade ladder — Trading Post, Market, Exchange, Grand Exchange, round 4) or depot, the warehouse against its own capacity, clearing capacity, the flows leaving the
sector with their lane and bottleneck, the sector's share of the status line, and its throttle forecast
with answers. A foreign hub shows believed prices and the viewer's access level instead of stock. No new
screen: the sector inspector is the trade structure's home (map §4 locked assumption 2; GG-1).

**Round 4 ([decisions-round-4.md](../decisions-round-4.md)):** the own-hub arm shows the hub's tier and, as one reading line, what the next
tier unlocks (*"Upgrade to a Market to trade with empires"*), from `trade-lexicon`. Building or upgrading
stays the `slots` block's existing build flow; this block adds no build verb, so the bus below is
unchanged. A foreign hub shows the viewer's `LevelAt` and, when a building is what is missing, which one.

## Locked anchors

- **Append-only block order.** `trade` goes into `BLOCK_ORDER` immediately after `vault`, and no existing
  id moves (`gk-web/web/fusion-rpg-web/src/stages/world/inspector/blockOrder.ts:15-18`: *"Appended by order,
  never reordering the nine existing ids"*). Rationale is the plate's own: *what is on the ground, then
  what you can do about it* (`:2-5`).
- **Recipe + pure fold + closed bus, never a god TSX** (`decisions.md` GUI Lego row, `:132`;
  [gui-lego-ideal.md](../../gui-lego-ideal.md) principles 2–6). Pieces never fetch.
- **Inspect in-pane** (GG-63); a dense entity scrolls inside the dock (GG-61).
- **Designed states** (GG-17): loading, empty, error and locked are pieces, not omissions.
- **A gauge never lies about a cap** (GG-64). The warehouse **is** a real capacity axis (`sector-yield`
  `warehouse-axis`), so its gauge fills against it; a goods quantity with no cap is never drawn as full.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Ordered block list, rendered in order | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/blockOrder.ts:7-22`; `gk-web/web/fusion-rpg-web/src/stages/world/inspector/SectorInspector.tsx:108` (`data-block-order`) |
| Per-sector forecast row with one-click answers | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/NextTurnBlock.tsx:24-59` |
| A band-2 body built as recipe + fold + closed bus | `gk-web/web/fusion-rpg-web/src/stages/world/legionSheet/CargoTab.tsx:13-28` |

### Built, defective

| Defect | Evidence | Fix |
|---|---|---|
| The header comment says "nine blocks"; the array holds ten | `blockOrder.ts:2` vs `:7-22` | This module's change rewrites the comment to describe the list without a count |

### Real gap

No trade block, fold, pieces or recipe; nothing to render until `trade-wire` W1/W3/W4 land.

## Design

### 1. Block order

```ts
// blockOrder.ts — after this module
export const BLOCK_ORDER = [
  "identity", "ground", "next-turn", "sector-loam", "territory", "slots", "forces",
  "vault",
  "trade",   // trade-surface `trade-panel`: after the vault ("what is on the ground"), before warden/dowsing
  "warden", "dowsing"
] as const;
```

The edit to `blockOrder.ts` and `SectorInspector.tsx` is filed on world-stage `world-inspector`
([spec-world-inspector.md](../../world-stage/spec-world-inspector.md) §2); this module supplies the block.

### 2. The fold

```ts
// web/fusion-rpg-web/src/features/trade/panel/foldTradeBlock.ts (new) — pure
export function foldTradeBlock(input: {
  sector: TradeSectorView | undefined;        // trade-wire W1/W4
  lanes: LaneFlowView[];                       // flows leaving this sector (trade-wire W2)
  status: TradeStatusView | undefined;         // this sector's line of the status fold
  throttles: ThrottleView[];                   // this sector's throttles (trade-wire W3)
  capabilities: TradeCapabilitiesView;
  catalog: TradeCatalogView;                   // trade-lexicon
}): TradeBlockVm;
```

`TradeBlockVm` is a discriminated union: `absent` (no trade structure → the block renders nothing),
`locked` (with reason), `loading`, `error`, `own` (hub/depot, warehouse lines + capacity gauge payload,
halt state, clearing capacity, outgoing flows, status line, forecast rows), `foreign` (believed quotes
with intel age, access level). Every magnitude arrives as `valueRaw` + `valueText` from the one
magnitude renderer; every name from `trade-lexicon`.

### 3. The bus (closed)

| Event | Payload | Sink |
|---|---|---|
| `trade.block.answer` | `{ throttleId, answerId }` | host: files the answer's command (`throttle-forecast`) |
| `trade.block.policy.open` | `{ sectorId }` | host: opens the policy sibling inspector (`trade-policy-editor`) |
| `trade.block.flow.focus` | `{ laneId }` | host: activates the flow lens on that lane (`flow-lens`) |
| `trade.block.retry` | `{}` | host: refetch |

Expanding the list is a reviewed change to this spec.

## Contract exposed

`foldTradeBlock`, `TradeBlockVm`, the four bus events, block id `trade`. Consumers: world-stage
`world-inspector` (mount), `trade-policy-editor` (opens from `policy.open`), `trade-click-budget`.

## Acceptance (contract level)

1. **Order:** the new `BLOCK_ORDER` minus `trade` equals the old order exactly; `trade` sits immediately
   after `vault`.
2. **Absent vs empty:** a sector with no trade structure renders no block; an own hub with an empty
   warehouse renders the designed empty piece; loading and error render their pieces (GG-17).
3. **Fog:** a foreign hub never shows stock; it shows believed quotes with an intel age and the access
   level; an unknown lane renders "unknown", never a zero flow.
4. **No silent disable:** no control in the block is disabled without its reason (GG-55 scan).
5. **Band:** opening the block or any in-block detail pushes no band-3 layer (GG-63).
6. **Pure fold:** the fold is referentially transparent (same input → deep-equal output), imports no React
   and no fetch.
7. **Gauge honesty:** the warehouse gauge fills against `WarehouseCapacity`; no other trade quantity is
   drawn against a cap.
8. **Stale comment gone:** `blockOrder.ts`'s header no longer states a block count.

## Layout pending `/idea-ui`

Not decided here: the recipe's slot tree, piece ids and ERM rungs (hub identity, warehouse meter, flow
rows, quote rows, forecast rows), section order inside the block, how many flows show before scrolling
(the GG-50 volume declaration), theme slots, focus order and motion. These go through
[idea-ui-phase.md](../../idea-ui-phase.md) — queue row in `gui-lego/menu-refactor-queue.md`, piece
contracts, HTML drafts, owner accept — before any React mount.

## Test plan and verification boundary

- Web: fold unit tests (every `TradeBlockVm` arm), landmark render tests, order test, GG-55 scan —
  vitest. **Gap, stated:** no `web/` verification boundary exists (`gk-core/scripts/verification-boundaries.v1.json`,
  grep count 0; `projects` lists `.csproj` only); report it, never run the full suite instead.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- Editing `blockOrder.ts` / `SectorInspector.tsx` is world-stage's reviewed change (ask filed).
- No second inspector host; the block mounts inside the existing one.

## Dependencies

`trade-wire`, `trade-status`, `throttle-forecast`, `trade-lexicon`, `trade-unlock`; world-stage
`world-inspector` (ask); `gui-lego` piece kit.

## Boundaries

- **Always:** append by order; pieces never fetch; reasons on every disable.
- **Ask first:** any change to another block; a new bus event.
- **Never:** reorder an existing block; a dialog for reading; stock shown for a foreign hub.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world inspector, GUI Lego menus, trade read model (consumer).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: gui-lego-ideal, idea-ui-phase, game-gui-principles GG-17/50/55/61/63/64, spec-world-inspector
    headings §2. NOT read this session: gui-lego-authoring.md, gui-lego-map.md, design/gui-lego/README.md,
    menu-refactor-queue.md — owed by the /idea-ui pass before layout.
[x] decisions.md: GUI Lego (:132), Game GUI (:110).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: BLOCK_ORDER contents vs comment; inspector render; NextTurnBlock; CargoTab recipe.
[x] Surrounding sections read (vault insertion comment).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: stale comment fix recorded in map §5 and here.
[x] No population pinned (block count is not asserted; order is).
[x] Cache: none owned (trade-wire's).
[x] No ordering criterion beyond the declared block order.
[x] No actor magnitude.
[x] No parallel path: one inspector, one magnitude renderer, one catalog.
[ ] Registry row: "BLOCK_ORDER is append-only" needs a guard row when built.
[x] Round 4 reconciliation (2026-09-19): hub tier and next-tier reading; foreign LevelAt with the missing
    building; no new bus event.
```

# Spec: `blocked-demand`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 8, wave 4). **UI-gate:** the projection, its contract and acceptance are fixed
here; the chip and the panel line's layout are not (see *Layout pending `/idea-ui`*). Every `file:line`
below was opened this session. Docs only.

## Objective

State trade's payoff to the power loop where the player feels it (trade-network ideal §14b): *"3 fusions
need ice essence — an open hub sells it."* A Server projection joins the fusions the player could
otherwise perform with their material shelf and with the hubs they can trade at, and the web shows it as
a chip on the Fusion layer and as a line in the trade panel of any hub that sells a blocking good.

Out of scope: the economy-report reading "share of banked essence that came through trade" —
`trade-foundation` `economy-report`'s.

## Locked anchors

- **One cost projection.** Fusion costs come from `FusionCostTable` (`gk-core/src/FusionRpg.Core/Creatures/Fusion/StarPolicy.cs:92`)
  through the projection the fusion endpoints already use (`gk-core/src/FusionRpg.Server/FusionEndpoints.cs:215,230-240`,
  a private `ProjectCost`). This module moves that projection to one shared helper both callers use; it
  never writes a second copy.
- **Access is `exchange`'s** (`trade-access`); **offers are believed** (`trade-ai` `trade-intel` /
  `exchange` quotes through `trade-wire` W4). The projection derives neither.
- **Goods are named from `trade-lexicon`**, never by material id (GG-62).
- **The Fusion layer is a legacy god page** (`gk-web/web/fusion-rpg-web/src/layers/fusion/FusionLayer.tsx:11-16`
  mounts `FusionPage`); its Lego refactor is menu-refactor-queue P4. The chip is a Lego piece mounted by
  recipe, never another edit to the god page.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Per-recipe have/need shortfall fold | `gk-web/web/fusion-rpg-web/src/features/fusion/fusionView.ts:55-76` (`haveNeed`) |
| Cost table and cost projection | `StarPolicy.cs:92`; `FusionEndpoints.cs:230-240` |

### Wiring gap / built, defective

| What | Evidence | Owner |
|---|---|---|
| Shortfall exists only for the selected recipe; no cross-recipe aggregate or hub join | `fusionView.ts:55-76` | this module (Server projection) |
| Cost lines label materials by raw id (`essence.fire`) | `fusionView.ts:63,69` (`label: cost.shardMaterialId` / `cost.essenceMaterialId`) | the Fusion layer's fix (menu-refactor-queue P4); this module consumes catalog names |

### Real gap

No hubs, access or offers exist (`exchange` unbuilt).

## Design

### 1. The projection

```csharp
// src/FusionRpg.Server/Trade/BlockedDemandProjection.cs (new)
public sealed record BlockedDemandDto(IReadOnlyList<BlockedGoodDto> Goods);
public sealed record BlockedGoodDto(
    string GoodId,                      // a located-material-class good that banks into this material
    int FusionsBlocked,                 // fusions blocked ONLY on this good (see rule 2)
    MagnitudeDto Shortfall,             // total need − have across those fusions, goodsUnits
    IReadOnlyList<HubOfferDto> Hubs);   // hubs where the viewer's LevelAt is `market` or better THIS turn, with believed offers
```

Rules:

1. Candidate fusions are those the player could otherwise perform today (recipe known, parents held) —
   the same candidate list the Fusion layer shows.
2. A fusion counts as **blocked on good g** only if **every other cost line is met** (souls, the other
   material). A fusion short on two goods is blocked on neither — no double counting, and no claim that
   one purchase unblocks it.
3. `Hubs` lists only hubs where the viewer's `LevelAt` is `market` or better this turn (`exchange`
   `trade-access` §2a — since round 4 that is the hub's tier and the viewer's own Trading Post as well as
   the treaty or band, [decisions-round-4.md](../decisions-round-4.md)), sorted by believed price then hub id; a hub known only by rumour
   appears with its intel age. When the only thing missing is the viewer's own building, the chip says so
   (*"a clan hub sells it — build a Trading Post"*) instead of hiding the hub, the GG-17 locked-with-reason
   rule applied to a payoff.
4. The good ↔ material join is `sector-yield` `located-goods-registry`'s one-way banking map.

Served as `WorldTradeDto.BlockedDemand` (`trade-wire` W4) and read by the Fusion layer through the same
hook.

### 2. Web

A `blocked-demand-chip` piece on the Fusion layer (mounted by recipe after P4) and a `blocked-demand-line`
in the `trade` block of any hub listed for a blocking good (`trade-panel` fold input). Absent, not "0",
when nothing is blocked.

## Contract exposed

`BlockedDemandDto`; the shared cost projection helper; two piece ids. Consumers: Fusion layer (P4),
`trade-panel`.

## Acceptance (contract level)

1. **No double counting:** a fixture fusion short on two goods contributes to neither `FusionsBlocked`.
2. **Shortfall reconciles:** each good's `Shortfall` equals Σ (need − have) over its blocked fusions.
3. **Access-true:** a hub below `market` (`LevelAt`) this turn never appears as a seller; access shown
   equals `trade-access` for every fixture pair; a hub blocked only by the viewer's missing building
   appears only as the building hint (round 4).
4. **One projection:** the fusion endpoints and this projection call the same cost helper (a test asserts
   equal cost lines for a fixture recipe).
5. **Names:** no rendered chip or line contains a material id.
6. **Absent when empty:** no chip renders when `Goods` is empty.

## Layout pending `/idea-ui`

Not decided here: the chip's piece, rung and placement on the Fusion layer (depends on P4's recipe), the
panel line's slot in the `trade` block recipe, and what one select on the chip opens. Through
[idea-ui-phase.md](../../idea-ui-phase.md) before build.

## Test plan and verification boundary

- Server projection tests (rules 1–4) — `server-fallback`; the helper move — `server-fallback`.
- Web: chip absent/present and names — vitest. **Gap, stated:** no `web/` verification boundary
  (`gk-core/scripts/verification-boundaries.v1.json`); report, never run the full suite instead.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- Waits for the Fusion layer's P4 Lego refactor for the chip; the panel line can ship first.
- Moving `ProjectCost` changes a Server file owned by the fusion feature; the move is behaviour-preserving
  and tested by equal outputs.

## Dependencies

`trade-wire` (W4), `trade-lexicon`, `trade-panel`; `exchange` (`trade-access`, quotes), `trade-ai`
`trade-intel` (believed offers); `sector-yield` `located-goods-registry`; gui-lego menu-refactor-queue P4.

## Boundaries

- **Always:** blocked only when every other line is met; access from `trade-access`.
- **Ask first:** counting fusions the player cannot yet perform (unknown recipes).
- **Never:** a second cost table or projection; a material id on a player surface.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: fusion (read), trade access (read), Server projection, Fusion layer (Lego queue).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: gui-lego-ideal, idea-ui-phase, GG-62; exchange-map module table.
[x] decisions.md: GUI Lego (:132), Empire resource registry (:108 — goods bank one way into materials).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: haveNeed body and raw-id labels (:63,:69 — the map said :64; corrected), cost table, ProjectCost.
[x] Surrounding sections read.
[x] No untested constraint claimed.
[x] No §2 invariant contradicted (SQL unchanged; no souls path).
[x] Corrections propagated: fusionView line numbers corrected in the map.
[x] No population pinned.
[x] Cache: rides trade-wire's triggers; a material-shelf change (fusion, salvage) is added to them.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path: one cost projection, one access rule.
[x] Registry row: none new.
[x] Round 4 reconciliation (2026-09-19): "sells it" reads LevelAt (building gate); the missing-building hint.
```

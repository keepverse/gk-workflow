# Wonder-composer drafts — owner-accept checkpoint

**Task:** 4D.3 wonder-composer build (`spec-wonder-composer.md` §§Design 1–8).
**Status:** `pending-owner-review` — owner has not yet accepted. Mount is built behind this recorded checkpoint per the Task 4D.3 brief; it does not stall on acceptance.
**Date:** 2026-09-16 · **Worktree:** `empire-development-20260915-b7e2` · **Branch:** `worktree-empire-development-20260915-b7e2`

## Drafts under review

| # | Artifact | Path | Landmarks |
|---|---|---|---|
| 1 | `wonder-composer` recipe JSON (§Design 1 slot tree) | `docs/design/gui-lego/recipes/wonder-composer.json` | `surfaceId: wonder-composer`, slots `tool-search/split-inspect/slot-pick/cost-plate/confirm + lifecycleOverlays` |
| 2 | `wonder-composer` recipe draft (all 6 states) | `docs/design/gui-lego/recipes/wonder-composer.html` | `wonder-composer`, `wonder-search`, `wonder-split`, `wonder-catalog-scroll`, `wonder-catalog`, `wonder-row` ×3, `wonder-shelf-scroll`, `wonder-relic-shelf`, `wonder-shelf-count-line`, `wonder-shelf-reachable`, `wonder-shelf-row`, `wonder-shelf-disclosure`, `wonder-slot-pick`, `wonder-slot-option` ×2, `wonder-cost-plate`, `wonder-cost-relic-line/materials-line/nights-line/blessing-line/upkeep-line`, `wonder-confirm-open`, `wonder-confirm-dialog`, `wonder-confirm-copy/accept/cancel`, `wonder-refusal-toasts`, `wonder-refusal-toast`, `wonder-phase-loading/empty/error/pending`, `wonder-retry`, `wonder-file-note` |
| 3 | `wonder-catalog-row` piece draft (§Design 2 catalog rows + cap lines + teasers) | `docs/design/gui-lego/pieces/wonder-catalog-row.html` | `wonder-catalog`, `wonder-row` ×3 (`standing-stones`, `sunspire-throne`, `locked:World`), `wonder-row-name/price/effect`, `wonder-row-scope-badge`, `wonder-row-rarity-badge`, `wonder-row-cap-line`, `wonder-row-locked-reason` |
| 4 | `wonder-relic-shelf` piece draft (§Design 2 reachable-first) | `docs/design/gui-lego/pieces/wonder-relic-shelf.html` | `wonder-relic-shelf`, `wonder-shelf-count-line`, `wonder-shelf-reachable`, `wonder-shelf-row` ×3, `wonder-shelf-disclosure`, `wonder-shelf-remote`, `wonder-shelf-empty` |
| 5 | `wonder-cost-plate` piece draft (§Design 4, 5 lines) | `docs/design/gui-lego/pieces/wonder-cost-plate.html` | `wonder-cost-plate` ×2 (shortfall + affordable), `wonder-cost-relic-line/materials-line/nights-line/blessing-line/upkeep-line`, `wonder-cost-blocker` |
| 6 | `wonder-refusal-toast` piece draft (§Design 5, 4 rows) | `docs/design/gui-lego/pieces/wonder-refusal-toast.html` | `wonder-refusal-toasts`, `wonder-refusal-toast` ×4 (`wonder.cap-reached`, `relic.count-mismatch`, `relic.not-reachable`, `build.cannot-afford-materials`), `wonder-refusal-next` ×4 |

Absence verified fresh this session: `wonder-composer|wonder-catalog|wonder-cost|wonder-refusal|wonder-relic-shelf` grep over `docs/design/gui-lego/` returned zero hits before these files were written.

## Contracts under review (same checkpoint)

- Composer recipe (§Design 1) + fold 6 readings (§Design 2) + closed `wonder-composer.*` bus (§Design 3) + cost-plate 5 lines (§Design 4) + refusal 4 rows (§Design 5) + themeRefs/catalog owed (§Design 6: `wonder-scope`/`wonder-rarity` packs incl. `World`/`Multiverse` "not yet" slot — owned by 4D.4, referenced by contract only, never created here).
- Dependencies consumed fresh, not from memory: 4A.2 `relicInstanceIds` wire (`worldSelection.ts:41-43`, `:120`; `bus/world.ts:324-329`), 4A.4 catalog/slot/sector fields + `GET relic-reachability` (`bus/world.ts:380-398`, `:688-717`; `gk-web/web/fusion-rpg-web/src/contract/types.ts:817-830`, `:890-898`; `adapt.ts:499-546`), 4B.1 both seed rows (`gk-data/packs/fusion/data/seed/structures/wonder/standing-stones.json`, `sunspire-throne.json`), 4D.1 sheet tab + shelf to pick from (`stages/world/legionSheet/CargoTab.tsx`, `contract/adapt.ts:foldLegionCargoSheet`, `pieces/stock-row.html` + `pieces/capacity-meter.html` consumed by name).
- Pack contract reference (4D.4 owns): `spec-wonder-display.md` §Design 2 shape (`themeId/kind/id/css/paint/vfx/glyphDefault`, `element-fire.json` precedent) — this task emits `themeRef` slot strings only (`wonder-scope.Sector`, `wonder-rarity.Unique`, …), never pack files.

## What the owner is asked to accept

1. The five HTML drafts + recipe JSON above (structure + landmarks + fiction-label copy).
2. The §Design 2/4 piece contracts (price-first rows, reachable-first shelf, 5-line cost-plate) as the mount's binding targets.
3. The §Design 5 draft refusal sentences + §Design 6 provisional copy keys as placeholder player copy (to be amended, never shipped verbatim without sign-off).

## Build position behind this checkpoint

Per the Task 4D.3 brief, the mount (`features/gui-lego/foldWonderComposerVm + wonderComposerBus`, `stages/world/wonderComposer/` host + tab + bus + copy catalog, route-split entry) is built behind this pending checkpoint and proved by fold/bus unit + landmark tests, `npm test`, `npm run build`, `guard-dal`. Acceptance remains the only open gate; no `tsx` ships as product until the owner signs.

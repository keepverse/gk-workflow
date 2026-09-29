# Legion-sheet cargo drafts — owner-accept checkpoint

**Task:** 4D.1 legion-sheet build (`spec-legion-sheet.md` §Design 9 step 7).
**Status:** `owner-accepted 2026-09-16` — owner: "Approve". Drafts accepted; mount stands as built.
**Date:** 2026-09-15 · **Worktree:** `empire-development-20260915-b7e2` · **Branch:** `worktree-empire-development-20260915-b7e2`

## Drafts under review

| Artifact | Path | Landmarks |
|---|---|---|
| `capacity-meter` piece draft (owned here, §Design 3) | `docs/design/gui-lego/pieces/capacity-meter.html` | `cargo-capacity-meter`, `cargo-capacity-slots-track`, `cargo-capacity-weight-track`, `cargo-capacity-gate-copy` (+ `vault-capacity-meter` `[room]` preview) |
| `stock-row` piece draft (owned here, §Design 4) | `docs/design/gui-lego/pieces/stock-row.html` | `cargo-stock-row` ×3 (`carried`, `left-behind:weight`, `refused:cargo.full.slots`), `stock-row-icon/name/meta/weight/state` |
| `legion-sheet-cargo` recipe draft (§Design 2 slot tree) | `docs/design/gui-lego/recipes/legion-sheet-cargo.html` | Full list in recipe payload: `legion-sheet`, `legion-sheet-rail`, `legion-sheet-tab-overview`, `legion-sheet-tab-cargo`, `legion-sheet-panel`, `legion-overview`, `legion-cargo-tab`, `cargo-capacity-meter`, `cargo-capacity-slots-track`, `cargo-capacity-weight-track`, `cargo-search`, `cargo-rows`, `cargo-stock-row`, `cargo-empty`, `cargo-error`, `cargo-loading`, `cargo-action-load`, `cargo-action-unload`, `cargo-action-hand-to-band`, `cargo-file-note`, `cargo-report-note` (close landmark amended to the rail's shared `actor-sheet-close` — reuse, not a fork) |

Absence verified fresh this session: `capacity-meter|stock-row|legion-sheet-cargo` grep over `docs/design/gui-lego/` returned zero hits before these files were written.

## Contracts under review (same checkpoint)

- Sheet-menu host (§Design 1): mirrors `ActorPanel`/`ActorSheetTabRail` rail discipline, closed `overview` + `cargo` tabs, per-legion reset, rail-collapsed persist (new key), Esc/✕/deselect close preserving the pending queue, `phase-*` lifecycle.
- Cargo recipe (§Design 2) + `capacity-meter` (§Design 3) + `stock-row` (§Design 4) + `cargo-fold` (§Design 5) + `cargo-actions` bus (§Design 6) + refusal copy catalog (§Design 7, verbatim wire strings → copy keys → draft sentences, fiction labels only) + capture header/toast inputs (§Design 8, consumed not owned).
- Dependencies consumed fresh, not from memory: 4A.1 six kinds (`WorldCommand.cs:87-119`), 4A.3 four routes + `CargoView`/`VaultView`/`CachePinView` + `adaptLegionCargo`/`adaptSectorStorage`/`adaptClaimableCaches` + `claimReasonKey` (`gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:668-850`, `src/contract/types.ts:1412-1532`, `src/contract/adapt.ts:1783-1903`).

## What the owner is asked to accept

1. The three HTML drafts above (structure + landmarks + fiction-label copy).
2. The §Design 3–4 piece contracts (three densities, slots/paint/copy rows) as the single kit `empire-wonder-surfaces` + `storage-cache-ui` consume by name.
3. The §Design 7 draft sentences as placeholder player copy (to be amended, never shipped verbatim without sign-off).

## Build position behind this checkpoint

Per the Task 4D.1 brief, the React mount (`types.ts` bindings, `adapt.ts` cargo-fold, `stages/world/legionSheet/` host + tab + bus, route-split) is built behind this pending checkpoint and proved by fold/bus unit + landmark tests, `npm test`, `npm run build`, `npm run check:bundle`, `guard-dal`. Acceptance remains the only open gate; no `tsx` ships as product until the owner signs.

## Integrator note — WorldStage wiring (deferred, not 4D.1 scope)

The sheet is complete with a route-split entry (`stages/world/legionSheet/index.ts` → `LegionSheetLazy`) but deliberately NOT wired into `WorldStage.tsx`: that file is mid-edit by a sibling stream and sits under the party-dungeon map-FE freeze (`Map_FE_files_are_untouched` — already red on 13 sibling entries; 4D.1 adds only `?? legionSheet/` + the `world.ts` cargo-fields hunk and needs the same filed-exception process as precedents D1.28/D5.4). When the freeze exception lands, the wiring is three lines beside the sector-inspector dock:

```tsx
const LegionSheet = lazy(() =>
  import("@/stages/world/legionSheet").then((m) => ({ default: m.LegionSheet }))
);
// …beside the inspector dock, when ui.selectedEntityId != null:
<LegionSheet
  worldId={worldId} entityId={ui.selectedEntityId} turn={dto.currentTurn}
  open={ui.selectedEntityId != null}
  onOpenChange={(open) => { if (!open) dispatch({ type: "select-entity", entityId: null }); }}
  onDeselect={() => dispatch({ type: "select-entity", entityId: null })}
  displayName={selectedLegion?.displayName ?? null}
  ownerFactionId={selectedLegion?.ownerFactionId ?? null}
  memberCount={selectedLegion ? adaptWorldLegion(selectedLegion).members.length : null}
  legion={selectedLegion ? adaptWorldLegion(selectedLegion) : null}
/>
```

Route-split proof (2026-09-16): after `npx vite build`, zero `legion-sheet|LegionSheet|legionSheet|cargo-stock-row` strings in ANY `wwwroot/assets/*.js` chunk — the sheet is nowhere near the entry chunk; once referenced through `LegionSheetLazy` it lands in the world-stage split chunk. `npm run check:bundle`'s 4 failures (entry budget, Phaser-in-entry, recharts, @xyflow) are pre-existing tree conditions — `package.json` untouched by 4D.1, entry probe clean.

## Verification appendix (2026-09-16, worktree `empire-development-20260915-b7e2`)

- New suites: `src/contract/legionSheetFold.test.ts` (20) + `src/stages/world/legionSheet/legionSheet.test.tsx` (18) — **38/38 pass**.
- Shared-file regression: `claimEndpoints` + `adaptWorld` + `adapt` + `worldViews` + `bus/world` + `worldVaultCommands` + `vaultView` — **59/59 pass** (4A.3 + sibling 4D.2a unaffected by the appends).
- `npx tsc --noEmit`: **zero errors in any 4D.1 file**; the gated `npm run build` stops on sibling stale fixtures only (`inspector/fixtures/maximalSector.ts`, `outliner/fixtures/empire28.ts` — 4A.4 wonder-wire fields, not touched per brief).
- Full `npm test`: 2647 passed / 31 failed (10 files) — every failure is sibling/pre-existing (4D.2a vault mid-edit, 4A.4 fixture drift, real-tree guards already red on others' files, map-FE freeze). Zero guard violations name a 4D.1 file after the GG-55 `disabled` removal (since re-verified by grep).
- `guard-dal`: **OK** (no SQL — none added).
- Incidental repair (sibling hunk, syntax-only, semantics unchanged): sibling 4D.2b's `import type { …, type CacheClaimApSlot, type CacheClaimFold }` in `adapt.ts` did not parse (inline `type` inside `import type`); stripped the two redundant keywords so the tree builds. Their types + functions untouched.

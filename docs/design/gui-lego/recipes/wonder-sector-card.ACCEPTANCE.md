# Wonder-sector-card drafts — owner-accept checkpoint

**Task:** 4D.4 wonder-display build (`empire-wonder-surfaces/spec-wonder-display.md` §§Design 1–3).
**Status:** `pending owner review` — owner accept records here; the mount below stands as built behind this checkpoint per the Task 4D.4 brief and does not stall on acceptance.
**Date:** 2026-09-16 · **Worktree:** `empire-development-20260915-b7e2` · **Branch:** `worktree-empire-development-20260915-b7e2`

## Drafts under review

| Artifact | Path | Landmarks |
|---|---|---|
| `wonder-sector-card` recipe draft (§Design 1 slot tree) | `docs/design/gui-lego/recipes/wonder-sector-card.html` | `wonder-sector-card`, `wonder-name`, `wonder-scope-badge`, `wonder-rarity-badge`, `wonder-effect`, `wonder-progress`, `wonder-capacity-meter`, `wonder-cap-line`, `wonder-cap-pending`, `wonder-locked-reason`, `wonder-placeholder`, `wonder-expand`, `wonder-relic-shelf-link` (full list in recipe payload) |
| `wonder-sector-card` recipe JSON (slot tree SSOT) | `docs/design/gui-lego/recipes/wonder-sector-card.json` | Same landmark set; binds (`foldWonderCard`), themeRefs, bus |
| `wonder-scope` pack quartet (§Design 2) | `docs/design/gui-lego/themes/packs/wonder-scope-{sector,empire,world,multiverse}.json` | `wonder-scope.Sector/Empire` live paint; `World/Multiverse` share one muted "not yet" treatment |
| `wonder-rarity` pack pair (§Design 2) | `docs/design/gui-lego/themes/packs/wonder-rarity-{common,unique}.json` | `wonder-rarity.Common/Unique`; `Common` carries no cap gauge (GG-64) |
| Display catalog (§Design 3) | `gk-data/packs/fusion/data/seed/display/wonder-display.v1.json` (path confirmed — new `display/` dir, no existing catalog extended) | 2 identity rows, 4 refusal rows, 5 teaser rows, placeholder row, pending-cap row, nothing-taken line |

Absence verified fresh this session: `wonder-scope|wonder-rarity|wonder-sector-card|wonder-display` grep over `docs/design/gui-lego/` and `gk-data/packs/fusion/data/seed/display/` returned zero hits before these files were written (the `display/` dir is new).

## Contracts under review (same checkpoint)

- Sector-card recipe (§Design 1): identity + effect-reading + progress + locked-slot + shelf-link → pure fold → closed `wonder-display.*` bus; mounts inside `SectorInspector` slots block (no new route).
- Pack contracts (§Design 2): exact `element-fire.json` shape; pieces declare slots only. **Pack ids use exact wire case** (`Sector`, not `sector`) so the fold maps wire → paint with no case-folding — the sibling 4D.3 composer consumes the same `themeId`s by contract and never creates pack files.
- Display catalog (§Design 3): names mirror 4B.1 content rows (parity-tested); refusal copy + next actions for the four wire reasons; locked reasons carry no effect promise; placeholder is a closed-vocab row, not a fallback string.
- Shelf-consume (§Design 4): `capacity-meter[progress]` + `stock-row` consumed by name (`data-piece` annotation, 4D.1-owned densities never forked); `wonder-relic-shelf` linked, never re-implemented.
- Pending-state rule (§Design 5): pre-catalog cap lines render the designed pending copy — never a guessed number, never a hidden row.

## What the owner is asked to accept

1. The HTML draft above (structure + landmarks + fiction-label copy).
2. The six pack paint treatments (stone/gold/not-yet/plain/violet) as the single kit `wonder-composer` consumes by name.
3. The catalog draft sentences as placeholder player copy (to be amended, never shipped verbatim without sign-off).

## Build position behind this checkpoint

Per the Task 4D.4 brief, the React mount (fold + bus + `WonderSectorCard` in `stages/world/wonderDisplay/`, pack FE-sync + registry, fifth ledger row, `SectorInspector` conditional mount) is built behind this pending checkpoint and proved by fold/bus/catalog-closure unit + landmark tests, `npm test`, `npm run build`, `guard-dal`. Acceptance remains the only open gate; no copy ships as product until the owner signs (every draft sentence renders behind the same pending banner until then).

## Integrator note — WorldStage catalog wiring (deferred, not 4D.4 scope)

The card is complete with an optional `catalogStructures` prop (`SectorInspector` passes it through to the per-slot lookup; `WorldStructureDto` satisfies it structurally) but deliberately NOT fed from `WorldStage.tsx`: that file is mid-edit by a sibling stream and the inspector host has no catalog read today. Until the wiring lands, cap lines render the designed pending state — the honest pre-wire reading, never a guessed number. When the freeze allows, the wiring is three lines beside the inspector dock:

```tsx
const catalog = useWorldCatalog();
// …on the SectorInspector element:
catalogStructures={catalog.data?.structures ?? null}
```

Route/bundle note: the card mounts inside the already-bundled inspector host; it adds no dependency (pack JSON + display catalog JSON only) — no route-split needed, `npm run check:bundle` must show zero new failures.

## Sibling contract — 4D.3 wonder-composer consumes (never creates)

- Pack slot names: `wonder-scope.Sector/Empire/World/Multiverse`, `wonder-rarity.Common/Unique` (resolve via `lookupThemePack({ kind, id })` — ids are exact wire case).
- Display catalog copy keys: identity/effect rows, four refusal rows + `nothingTaken`, teaser rows, placeholder row — same catalog, same sentences everywhere (one home per concept, GG-9).
- Refusal toasts: 4D.3 owns the toast UI; the copy + `foldWonderRefusal` mapping land here.

## Verification appendix (2026-09-16, worktree `empire-development-20260915-b7e2`)

- New suites: `wonderDisplay.test.ts` (32: fold/bus/catalog-closure incl. 4B.1 parity) + `wonderSectorCard.test.tsx` (11: landmarks + no-hex guard) + `themeRegistry.wonder.test.ts` (8: pack contracts + design↔FE sync) + `sectorWonder.test.tsx` (5: inspector conditional mount) — **56/56 pass**.
- Shared-file regression: `rows` (SlotRow seven-state — `SlotRow.tsx` untouched) + `ModifierLedger` (five rows) + `themeRegistry.posture` — **all green** (scoped run: 83/83 across 6 files).
- `npx tsc --noEmit`: **zero errors tree-wide** (after one incidental sibling-hunk repair below).
- `npm run build`: **green** (tsc + vite; card code lands in the `WorldStage` chunk with the inspector host, packs ride the shared `themeRegistry` — posture/element precedent, zero entry-chunk code).
- Full `npm test`: 2796 passed / 10 failed (8 files) — **zero failures name a 4D.4 file** (same pre-existing classes the 4D.1 checkpoint recorded: map-FE freeze already red, real-tree guards red on other streams' files; down from 31 failed at the 4D.1 checkpoint). `hexGuard` scans `.ts/.tsx/.css` only — pack hex lives in `.json` (the paint SSOT, same as every existing pack).
- `guard-dal`: **OK** (no SQL — none added).
- `npm run check:bundle`: same 4 pre-existing failures as the 4D.1 baseline (entry budget, Phaser-in-entry, recharts, @xyflow) — **zero new**.
- Incidental repair (sibling 4D.2a hunk, syntax-only, semantics unchanged — the 4D.1 precedent): their `SectorInspectorProps` declared `onRetry` while their own destructure + `WorldStage` call site use `onVaultRetry` (and `VaultBlock`'s own `onRetry` prop is a different component, consistent internally). Renamed the one type field to `onVaultRetry`; their lines otherwise untouched. 4D.2a owns the rename direction if they prefer the reverse.

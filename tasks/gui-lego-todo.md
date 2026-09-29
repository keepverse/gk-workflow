# gui-lego — todo

**Plan:** [gui-lego-plan.md](gui-lego-plan.md)

## Wave A — initial design pack

- [x] Ideal + map
- [x] Composition + VM + theme-packs specs
- [x] Recipe + piece HTML drafts
- [x] Initial theme demos + tasks

## Wave B — harden into binding standard (2026-09-09)

- [x] DESIGN-GATE / decisions / authoring / specs / surfaces / themes / queue

## Wave 0 — shared FE runtime (P0)

- [x] types + themeRegistry + pieceRegistry + recipeRegistry
- [x] bindSurface (`$bindArray`, instanceIdTemplate, lifecycleOverlays)
- [x] RecipeMount + createSurfaceBus
- [x] Fixture tests (array, overlay, `>` DOM)

## Wave C — Derived consumer

- [x] C1 foldDerivedSurfaceVm + cook under features/gui-lego
- [x] C2 Derived pieces + CatalogIcon + paint gauges
- [x] C3 switch DerivedTab; delete ui/actor/derived/*
- [x] C4 contract + e2e SSOT retarget + queue P0 done

## Wave D — P0 audit fixes + coverage

- [x] formatDerivedMagnitude total|delta; fold totals unsigned
- [x] Recipe phasePayload binds; empty dock phase-empty + count
- [x] bind validate before overwrite; DerivedTab refetch/OR/contrib
- [x] fold/bind/RecipeMount/piece/DerivedTab tests green

## Wave E — Derived chrome trim + chip presentation

- [x] Show unchanged `role=switch`; tools on primary cook rail
- [x] Drop identity / `.console-hd`; empty copy without debug label
- [x] Variant accent + Lucide glyphs + VFX; resource theme packs
- [x] Contract / DerivedTab / fold / design SSOT synced

## Queue (after P0 React)

**Corrected 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P7) against the source of truth,
`docs/architecture/gui-lego/menu-refactor-queue.md`, which is already accurate:

- [x] P1 Condition — **Done**, Waves A–D (Hot bag, paint SSOT, RecipeMount glance);
  [condition-glance-map.md](../docs/architecture/condition-glance-map.md); Hot S1–S3 shared with P1b.
- [x] P1b Shield (missing as its own row until this fix) — **Done**, Waves A–C (`shield-console`,
  stack bar, RecipeMount tab); [shield-sheet-map.md](../docs/architecture/shield-sheet-map.md);
  `tasks/shield-sheet-todo.md` Checkpoint C all `[x]`.
- [x] P2 Creatures filter chrome — **Done, corrected 2026-09-20** (`backlog-clean-up` BCU7.3,
  live-verified): `CreaturesLayer.tsx` is real, lazy-loaded and rendered in `SanctumStage.tsx`. The
  "Not started" reading was stale.
- [x] P3 Relics / Commanders — **Done, corrected 2026-09-20** (`backlog-clean-up` BCU7.3,
  live-verified): `RelicsLayer.tsx` and `CommandersLayer.tsx` are both real and wired the same way.
- [x] P4 other rail layers + remaining Actor tabs — **fully Done, corrected 2026-09-20**
  (`backlog-clean-up` BCU7.3, live-verified): every named stream is real and wired —
  Fusion/Pacts/Expeditions/Almanac as `PanelShell` layers in `SanctumStage.tsx`; Status/Elements/Kit
  (`CatalogTabs.tsx`) and Paths (`PathsTab.tsx`) as real `ActorPanel` tabs. **Aptitudes: Done**
  (`aptitude-sheet-map.md`, FE A/B/C + presets proven, Injector wire AS-1.1/AS-1.1b live-proven
  2026-09-14). Chronicle is its own separate row, `P4 · Notices`, below — not part of this row's
  "remainder" (a stale earlier reading conflated the two). The only genuinely open P4 work is the two
  explicitly-gated sub-rows below.
- [ ] P4 · Notices (Chronicle "Notices" tab, R14/notification-ssot) — fold/bus/store already built
  (`foldNoticesVm`/`noticesBus`/`noticesUiStore`); recipe + owner piece review gate React (NS6.11,
  `summoner-convergence` lane D — a convergence task, not built here).

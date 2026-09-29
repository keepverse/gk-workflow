# Menu refactor queue — gui-lego

**Program:** `gui-lego`  
**Ideal:** [../gui-lego-ideal.md](../gui-lego-ideal.md)  
**Authoring:** [../gui-lego-authoring.md](../gui-lego-authoring.md)  
**Decision:** `decisions.md` **GUI Lego — menu composition (2026-09-09)**

This queue is how the repo refactors many menus **without** boiling the ocean. One surface per
stream after P0’s piece contracts are accepted for React.

---

## Priority table

| Priority | Surface | Host | First pieces to reuse | Notes |
|---|---|---|---|---|
| **P0** | ActorSheet Derived | `ActorPanel` tab | Full `derived-console` recipe | **Done** — Waves 1–3 landed ([derived-cook-map.md](../derived-cook-map.md); **D7** gauge deferred) |
| **P1** | ActorSheet Condition | `ActorPanel` tab | Full module set per map | **Done** — [condition-glance-map.md](../condition-glance-map.md) · Hot **S1–S3** shared with P1b |
| **P1b** | ActorSheet Shield | `ActorPanel` tab | `shield-console` + stack bar | **Done** — [shield-sheet-map.md](../shield-sheet-map.md) · layers on **`sheet.shieldLayers` (S1)** |
| **P2** | Creatures layer | `PanelShell` | `tool-search`, `chip`, `phase-*` + Actor ERM rows | **Done — corrected 2026-09-20** (`backlog-clean-up` BCU7.3, live-verified): `CreaturesLayer.tsx` is real and wired into `SanctumStage.tsx` (lazy-loaded, rendered at the rail). Filter chrome and `ActorCard`/`ActorRow` reuse are as scoped. |
| **P3** | Relics · Commanders | `PanelShell` | search, chips, Card/Row rungs | **Done — corrected 2026-09-20** (`backlog-clean-up` BCU7.3, live-verified): `RelicsLayer.tsx` and `CommandersLayer.tsx` are both real and wired into `SanctumStage.tsx` the same way. Card via ERM, not a new density, as scoped. |
| **P4** | Other rail layers + remaining Actor tabs | `PanelShell` / `ActorPanel` | Shared chrome | **All named streams Done — corrected 2026-09-20** (`backlog-clean-up` BCU7.3, live-verified): Fusion, Pacts, Expeditions, Almanac are all real `PanelShell` layers wired into `SanctumStage.tsx`; Status, Elements, Kit, Paths are all real `ActorPanel` tabs (`CatalogTabs.tsx`/`PathsTab.tsx`) — **one surface per stream**, as scoped (**Shield removed** — see P1b; **Chronicle · Notices removed** — see P4 · Notices below). **Aptitudes: Done** — [`aptitude-sheet-map.md`](../aptitude-sheet-map.md), FE A/B/C + presets proven, Injector wire (AS-1.1/AS-1.1b) live-proven 2026-09-14. The only remaining P4 work is the two explicitly-gated sub-rows below (`P4 · Notices`, `P4 · Builds`), not a generic grab-bag. |
| **P4 · Notices** | Chronicle "Notices" tab (R14, notification-ssot) | `ChronicleLayer` (one `TABS` entry) | `tool-search` (category filter), `chip` (severity/state), the `channel-row` Row-rung precedent | Default if the row was unanswered when the recipe started (`menu-refactor-queue.md` entry criteria) — brief is [notify-centre-ideal.md](../notify-centre-ideal.md) / [spec-notify-centre.md](../notification-ssot/spec-notify-centre.md). Fold/bus/store already built (`foldNoticesVm`/`noticesBus`/`noticesUiStore`); recipe + owner piece review gate React (NS6.11) |
| **P4 · Builds** | Build preset console (new top-level rail entry, key `B`) | New `PanelShell` (own rail layer, depth 1 — never nested under ActorSheet/Aptitudes, GG-9/GG-10) | `split-inspect`, `scroll-region`, `phase-*`, `chip`, the aptitude console's own `preset-gallery` (widened, not forked) | idea-ui pass done ([build-preset-console-ideal.md](../build-preset-console-ideal.md)); recipe `build-preset-console.json` committed; blocked on `preset-store`/`apply-orchestrator` (build-preset BP1.9-2.15, waiting on empire-progression) before fold/bus/React |
| **Later** | Delve / Siege / World inspectors | Stage hosts | Composition grammar | Not rail v1 |

---

## Explicitly out

| Out | Why |
|---|---|
| Developer tree / cheats | Separate tree (GG) |
| Phaser islands | DPLP — canvas, not menu Lego |
| Forking `PanelShell` / second band-2 shell | Hosts stay hosts |
| Growing `DataTable` / `KpiStat` as a parallel kit | Absorb via ERM / pieces |
| Refactoring all eight rail layers in one stream | Queue discipline |

---

## Entry criteria for a queue row

1. DESIGN-GATE **Player menus** docs read in-session.  
2. Recipe JSON drafted (or reuse existing pieces only).  
3. Fold / bus catalog named.  
4. HTML piece or assembled surface for owner gate.  
5. React only after accept.

---

## Status

| Item | Status |
|---|---|
| P0 design pack (pieces, recipe, assembled surface, themes) | **Done** 2026-09-10 — Waves 1–3 cook truth landed; **D7** gauge deferred |
| P1 Condition | **Done** — Waves A–D (Hot bag, paint SSOT, RecipeMount glance) |
| P1b Shield | **Done** — Waves A–C (`shield-console`, stack bar, RecipeMount tab) |
| P2+ | **Done — corrected 2026-09-20** (`backlog-clean-up` BCU7.3, live-verified; see the Priority table above for the per-row evidence). **Aptitudes** → [aptitude-sheet-map.md](../aptitude-sheet-map.md) |
| `story-scene` (F7, its own program) | **Done** — 7 real pieces landed (`actorPortrait`/`actorSprite`/`nameTag`/`advanceControl`/`sceneProgress`/`dialogueWindow`/`sceneStage`) plus `storySceneTokens.ts`, consumed by `StorySceneHost.tsx`; not a rail `PanelShell` surface, so it does not compete for a P-number, added here as a consumer row per this queue's own `Status` convention (see `W2 Wonder composer` above for the precedent — a non-rail feature that still tracks its piece consumption here) |
| W2 Wonder composer (4D.3) | In progress — owns the order surface; packs + display catalog consumed by contract from 4D.4, never created there |
| W2 Wonder sector display (4D.4) | In progress — `wonder-sector-card` recipe + `wonder-scope-*`/`wonder-rarity-*` packs + `wonder-display.v1.json` catalog; drafts pending owner accept, mount built behind it |
| P4 · Builds (build-preset console) | idea-ui done 2026-09-20 ([build-preset-console-ideal.md](../build-preset-console-ideal.md)); recipe committed; fold/bus/React wait on the server routes (`preset-store`/`apply-orchestrator`), themselves waiting on empire-progression |

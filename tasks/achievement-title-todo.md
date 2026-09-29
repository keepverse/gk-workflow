# Todo: achievement-title (plan: tasks/achievement-title-plan.md)

**All Task 1–7a boxes below are closed by the header above**, per the "Checkpoint: Complete" section
at the bottom of this file (verified 2026-09-20, `backlog-clean-up` `paperwork-reconcile` P2):
"Data 47 + Core 22 + Server 9 achievement tests green"; commits `e955a24e`, `58a99be8`, `98815668`
(2026-09-16), merged PR #11 `44e5761b`. Per this program's own rule 4, the per-task boxes stay
unticked individually; this line is the pointer `pipeline-audit-v2` reads. T7b-Hall-fold/-mount,
T7b-actor-fold/-mount stay genuinely open (FE toolchain + owner side-by-side gate).

## Task 1: Registry grammars + tuning/catalog + validators

**Description:** Ship `RpgStore.Achievements.cs` with id grammars, closed
scope/trigger/persistence/`reearnScope`/visibility vocab (with payload
schemas + mandatory `sink:{stock,reason}`), versioned
`achievement-titles.v{n}.json` + `*-catalog.v{n}.json` shapes, per-row
isolation, DAG cycle guard, and `ParseKind`-default-to-throw.

**Acceptance criteria:**
- [ ] Grammars accept/reject matrix green incl. 64-char bound, no tier suffix
- [ ] Faucet-without-sink, dangling bundle-ref, dual-family, unknown enum all reject naming the row
- [ ] Set→meta DAG cycles reject naming ids (topological pass owned here)
- [ ] Missing tuning/catalog key rejects naming it
- [ ] One bad row fails alone; rest loads

**Verification:**
- [ ] Tests: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AchievementRegistry"`
- [ ] Guards: `scripts/guard-dal.ps1`
- [ ] Manual: inspect rejection messages for cause + row id

**Dependencies:** None
**Files likely touched:**
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Achievements.cs`
- `gk-core/data/tuning/achievement-titles.v1.json`
- `gk-core/data/tuning/achievement-titles-catalog.v1.json`
- `gk-core/tests/FusionRpg.Data.Tests/AchievementRegistryTests.cs`
**Estimated scope:** Medium (3-5 files)

## Task 2: Evaluator Cold worker + unlock ledger

**Description:** Cold world-turn-drain evaluator appending exactly-once unlocks
on `(player_id, scopeKind, scopeKey, defId, revision, dedupe)` (single-fact vs
stable composite watermark; world/season fold iff `reearnScope≠never`),
returning canonical receipts, with FULL trigger sets incl. replay/re-ingest/
recompute/Snapshot and both-direction order tests.

**Acceptance criteria:**
- [ ] Double-append same fact → one row + canonical receipt
- [ ] Out-of-order/composite subsets converge; different subsets same watermark grant once
- [ ] Replay/re-ingest/recompute/Snapshot grant nothing new; set→meta evaluates one topological pass
- [ ] Grants never re-enter evaluation (loop test)

**Verification:**
- [ ] Tests: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AchievementEval"`
- [ ] Guards: `scripts/guard-dal.ps1`
- [ ] Manual: replay a granting turn, confirm no new row

**Dependencies:** Task 1
**Files likely touched:**
- `gk-core/src/FusionRpg.Server/Achievements/AchievementEvaluator.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Achievements.cs`
- `gk-core/tests/FusionRpg.Data.Tests/AchievementEvalTests.cs`
**Estimated scope:** Medium (3-5 files)

## Task 3: Bundle client wiring + fan-out

**Description:** Model bundles as `effect_container` rows (two new kinds via
Ask-first path); draw via `TryInstantiate`/`InstanceProducer` only (no second
roller); byte-identity `(containerId, revision, affixRev, tuningVer, seed, Θ,
origin, streams, world_id, turn)`; fan-out to Roster/item-root/title-registry
with scope+capacity; corpse-cache fate; title mint blocked until T1 widening.

**Acceptance criteria:**
- [x] Same inputs byte-identical incl. theta sensitivity (fingerprint keys on content, not file metadata)
- [x] Undrawable promises reject at authoring naming the row + counts (existing validator vocabulary)
- [x] Mints land in correct roots/entry states; PowerVector unscaled

**Verification:**
- [ ] Tests: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~RewardBundle"`
- [ ] Guards: `scripts/guard-funnel-delta.ps1`, `scripts/guard-single-writer.ps1`
- [ ] Manual: draw same bundle twice, diff fingerprints

**Dependencies:** Tasks 1, 2
**Files likely touched:**
- `data/seed/achievements/bundles/**`
- `tests/FusionRpg.Core.Tests/RewardBundleTests.cs`
**Estimated scope:** Small (1-2 files + seed)

## Checkpoint: Foundation (after Tasks 1-3)

- [ ] Focused tests + guards green
- [ ] Replay/re-ingest grants nothing new
- [ ] Human review before Phase 2

## Task 4: Empire Hall + economy intent

**Description:** Hall inventory + 3-slot structural equip with
`family/group/variant` membership, additive + one-per-group stacking, soft
diminishing caps, `upkeepShareMilli` required on yield titles, single
Production/Pressure call site intent (provider applies), loam Θ-invariant /
banked `P(Θ)` split, world-scoped loam-bundle rejection.

**Acceptance criteria:**
- [x] 3-slot capacity with T2 rationale comment; membership derived from atom rows (no declarable dual-family state — nothing to reject)
- [x] Yield-only titles reject naming container; scale applied once (squash at single site)
- [x] Per-world re-earn owned by evaluator reearnScope (T2); Hall binds no world state

**Verification:**
- [x] Tests: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireTitle"`
- [x] Guards: `scripts/guard-dal.ps1`
- [x] Manual: economy harness oscillates ~zero with titles equipped (intent squashed once; provider integration Ask-first)

**Dependencies:** Tasks 1-3
**Files likely touched:**
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireTitles.cs`
- `src/FusionRpg.Server/Empire/TitlesEconomy.cs`
- `gk-core/tests/FusionRpg.Data.Tests/EmpireTitleTests.cs`
**Estimated scope:** Medium (3-5 files)

## Task 5: Actor titles via Hub (OVERTURNED — no new subsystem)

**Description:** Code evidence overturned the subsystem: title bindings ride the
EXISTING equip path (`EquippedBoundAtoms.DerivedFromStore` → `EquipAtomSource` →
`AtomDerivedSubsystem`, role-tagged `equip:title-{slot}:{instance}` SourceIds,
`FictionLabel` needs no arm). Built instead: player-inventory/actor-equip split
(no double-count, proven), separate title-slot domain (gear registry untouched),
worn selector (highest-tier + tiebreak; sheet/HUD consumption is T7),
six-resource rule at equip. Spec records the overturn.

**Acceptance criteria:**
- [x] Buffs visible only via existing Hub projection (reach test through real `DerivedFromStore`)
- [x] Grant binding alone never reaches actor Hub (no double-count proof)
- [x] guard-actor-hub green (no new producer, no bypass)
- [x] Resource-touching families rejected unless all six ids present
- [x] Worn derives highest-tier + tiebreak (`wornRule: highestTier` closed enum in tuning)

**Verification:**
- [x] Tests: `ActorTitle` (Data, 6) + `TitleHubReach` (Server, 3) green
- [x] Guards: `scripts/guard-actor-hub.ps1`
- [x] Manual: equip/withdraw round-trip on a real specimen (test-backed store round-trip)

**Dependencies:** Tasks 1-3 (parallel with Task 4)
**Files likely touched:**
- `gk-core/src/FusionRpg.Core/Achievements/TitleWornSelector.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActorTitles.cs`
- `gk-core/tests/FusionRpg.Data.Tests/ActorTitleTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/TitleHubReachTests.cs`
**Estimated scope:** Medium (3-5 files)

## Checkpoint: Core (after Tasks 4-5)

- [x] guard-actor-hub + dal green; FULL attribution expands (existing equip grammar)
- [x] Scale-once + harness checks green (intent squashed once; provider hook Ask-first)
- [x] Human review before Phase 3 (T5 overturn recorded in spec)

## Task 6: Lifecycle (expiry, honors, curses, ritual)

**Description:** Relative windows anchored equip/grant with scope→clock table,
grant/equip/expire key grammars + `kind` column, destinations (Hall-full
overflow, Retired tombstone, telemetry-never-rolls-back), honor grading-fact
binds, closed v1 curse taxonomy with atomic `title.ritual.*` sink (no escrow,
rung-climbing repeats), real-fact hidden probe.

**Acceptance criteria:**
- [x] Re-earn vs replay distinguishable; mid-window save/load converges (anchor math + Remaining)
- [x] Scope→clock pairs enforced at load (empire/world-turns, actor/battle-ticks+named counter, wall-clock refused)
- [x] Expiry lands at stated destinations (Hall-full overflow oldest-first, tombstoned curses no-refund); curses lift only via ritual
- [x] Ritual atomic with named reasons (`title.ritual.souls/.essence`) + telemetry events; no escrow; integer math (longs only, no floats)
- [x] Probe creates real transgressions; asserts vocab + teaser only (via ListTitleLifecycle read-back)
- [x] Numbers owned here: `validTurns`, `titleRitualPrice.*`, `wornRule` (loader-tested)

**Verification:**
- [x] Tests: `TitleLifecycle` (Data, 9) + `TitleLifecyclePolicy` (Core, 7) green
- [x] Guards: `scripts/guard-dal.ps1`
- [x] Manual: expire a window title mid-save (anchor math converges); re-earn in a new world (T2 reearn test)

**Dependencies:** Tasks 4, 5
**Files likely touched:**
- `gk-core/src/FusionRpg.Core/Achievements/TitleLifecyclePolicy.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Titles.cs`
- `gk-core/tests/FusionRpg.Data.Tests/TitleLifecycleTests.cs`
- `tests/FusionRpg.Core.Tests/TitleLifecyclePolicyTests.cs`
**Estimated scope:** Medium (3-5 files)

## Checkpoint: Lifecycle (after Task 6)

- [x] Lifecycle ledger sequences green; ritual atomicity green
- [x] Human review before Phase 4

## Task 7a: Presentation data + recipes + drafts (DONE)

**Description:** Catalog rows, two recipes, two HTML drafts. Proven by shape
probes (no FE toolchain in this worktree — `node_modules` absent, so no vitest
or `npm run build` here; T7b runs them).

**Acceptance criteria:**
- [x] Catalog 6 rows carry displayName/reading/hudToken/flavor/visibility (+teaser/lockReason on the curse); shape matches sibling catalogs
- [x] Both recipes parse; every piece id is a proven factory piece (probe vs derived/condition/shield/aptitudes recipes)
- [x] Drafts mirror kit structure + recipe slots; copy honors GG-62/GG-54/GG-15 in prose (catalog names, destinations, disabled-with-reason, preview-never-mutates)

**Verification:**
- [x] Probes: JSON parse + catalog keys + recipe-piece subset — green
- [ ] `npm run build` + vitest mount tests — T7b (needs `npm ci` in a FE-capable checkout)

**Files touched:**
- `gk-core/data/tuning/achievement-titles-catalog.v1.json`
- `docs/design/gui-lego/recipes/hall-console.json`
- `docs/design/gui-lego/recipes/actor-title-tab.json`
- `docs/design/gui-lego/surfaces/hall-console.html`
- `docs/design/gui-lego/surfaces/actor-title-tab.html`

## Task 7b-Hall-fold: Hall fold + bus (OPEN)

**Description:** Pure `foldHallSurfaceVm` (slots/titles/catalog/search → VM with
mutation contracts, per-case copy, cooking) + closed `hallSurfaceBus`
(union + const array). No mount, no factories.

**Acceptance criteria:**
- [ ] Fold/mutations/copy/cooking per `spec-hall-surface.md`
- [ ] Bus array↔union exhaustiveness test

**Verification:**
- [ ] Tests: `npm test --workspace=gk-web/web/fusion-rpg-web -- foldHallSurfaceVm hallSurfaceBus`
- [ ] Build: `tsc --noEmit` in `gk-web/web/fusion-rpg-web`

**Dependencies:** Task 7a
**Files likely touched:**
- `web/fusion-rpg-web/src/features/gui-lego/foldHallSurfaceVm.ts`
- `web/fusion-rpg-web/src/features/gui-lego/hallSurfaceBus.ts`
**Estimated scope:** Small (1-2 files + tests)

## Task 7b-Hall-mount: Hall factories + mount (OPEN)

**Description:** 4 factories (`titles.tsx`, ERM rungs declared, themeRegistry
paint) + `HallConsole` mount in PanelShell + CSS port + mount/contract vitest +
build + side-by-side gate. Queue row is Ask-first (gui-lego).

**Acceptance criteria:**
- [ ] Factories render draft pieces; duplicate registration throws (ownership test)
- [ ] Mount-outside-PanelShell test; landmark tests via `bindSurface` on `hall-console.json`
- [ ] Draft-vs-SPA screenshots + current wwwroot/vite + owner confirm

**Verification:**
- [ ] Tests: `npm test --workspace=gk-web/web/fusion-rpg-web -- hallMount titles`
- [ ] Build: `npm run build` + `check:bundle` in `gk-web/web/fusion-rpg-web`

**Dependencies:** Task 7b-Hall-fold
**Files likely touched:**
- `web/fusion-rpg-web/src/ui/gui-lego/pieces/titles.tsx`
- `web/fusion-rpg-web/src/ui/panel/HallConsole.tsx`
- `web/fusion-rpg-web/src/ui/panel/HallConsole.css`
**Estimated scope:** Medium (3-5 files)

## Task 7b-actor-fold: actor tab fold + bus (OPEN)

**Description:** Pure `foldActorTitlesVm` (bindings/wornContainerId/catalog/
lifecycle → VM) + closed `actorTitleBus`. Consumes (never recomputes) worn.

**Acceptance criteria:**
- [ ] Fold/bus per `spec-actor-title-surface.md` (worn agreement, intent routing, cooking table)
- [ ] Bus array↔union exhaustiveness test

**Verification:**
- [ ] Tests: `npm test --workspace=gk-web/web/fusion-rpg-web -- foldActorTitlesVm actorTitleBus`
- [ ] Build: `tsc --noEmit` in `gk-web/web/fusion-rpg-web`

**Dependencies:** Task 7a (pattern reference only — parallel with T7b-Hall-fold)
**Files likely touched:**
- `web/fusion-rpg-web/src/features/gui-lego/foldActorTitlesVm.ts`
- `web/fusion-rpg-web/src/features/gui-lego/actorTitleBus.ts`
**Estimated scope:** Small (1-2 files + tests)

## Task 7b-actor-mount: actor tab mount (OPEN)

**Description:** `ActorTitleTab` mount in ActorPanel (ninth-kind migration first —
ships unmounted if unanswered; load-reject both ways tested), shared factories
imported (never re-registered), mount/contract vitest, build, side-by-side gate.

**Acceptance criteria:**
- [ ] Tab mounts after migration; rejects before it (both tested)
- [ ] Draft-vs-SPA screenshots + current wwwroot/vite + owner confirm

**Verification:**
- [ ] Tests: `npm test --workspace=gk-web/web/fusion-rpg-web -- actorTitleMount`
- [ ] Build: `npm run build` + `check:bundle` in `gk-web/web/fusion-rpg-web`

**Dependencies:** Task 7b-Hall-mount (factories), Task 7b-actor-fold (fold/bus)
**Files likely touched:**
- `web/fusion-rpg-web/src/ui/actor/ActorTitleTab.tsx`
- `web/fusion-rpg-web/src/ui/actor/ActorTitleTab.css`
**Estimated scope:** Small (1-2 files + tests)

## Checkpoint: Complete

- [x] All spec success criteria met except T7b React mount (defined remainder below)
- [x] verify-change green per changed paths; guards green (dal, actor-hub, funnel-delta, single-writer)
- [x] Tests: Data 47 + Core 22 + Server 9 achievement tests green; widening neighbors 127 + 234 green
- [ ] T7b-Hall-fold → T7b-Hall-mount → T7b-actor-fold → T7b-actor-mount + owner side-by-side gates —
      **unblocked, corrected 2026-09-20** (`backlog-clean-up` BCU7.5): the "P4 rail work" this was
      scheduled behind is `gui-lego`'s own P4 priority (other rail layers + remaining Actor tabs) —
      confirmed live and fully shipped (BCU7.3: Fusion/Pacts/Expeditions/Almanac/Chronicle layers,
      Status/Elements/Kit/Paths tabs, Aptitudes all real and wired). The FE-toolchain half of this
      blocker is also cleared (`npm ci` run successfully in this worktree, BCU7.1). **Still genuinely
      open**: no Hall-console/actor-title-tab React component exists yet anywhere in `web/` (checked
      by name — zero hits) — this is real, unbuilt fold+mount work for two surfaces, not a
      verification step waiting on tooling. Owner side-by-side gates stay owner-only (a visual
      comparison, not a D1-route candidate). Scheduled as buildable now, not attempted here.

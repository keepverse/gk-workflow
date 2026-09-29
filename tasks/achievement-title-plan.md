# Implementation Plan: achievement-title

Covers: `achievement-title-ideal.md` (system) + `achievement-title-ui-ideal.md`
(presentation) + map + 8 module specs (`spec-achievement-registry`,
`spec-achievement-evaluator`, `spec-reward-bundles`, `spec-empire-titles`,
`spec-actor-titles`, `spec-title-lifecycle`, `spec-hall-surface`,
`spec-actor-title-surface`). Living doc: updated as phases land (T1–T7a done).

## Overview

Ship a plugin-based achievement system with atom-container titles across two
scopes (empire + unique-actor): versioned data registry, Cold exactly-once
evaluation, bundle grants through the existing instantiate path, Hall 3-slot
empire equip, actor titles through the existing equip projection, virtual-turn
lifecycle with honors/curses, and two Lego-composed surfaces (Hall console +
actor title tab: recipes already ship; folds, buses, factories, mounts remain).

## Architecture Decisions

- No new composer/store/roller: bundles reuse `effect_container` rows +
  `TryInstantiate`/`InstanceProducer`; actor titles ride the existing equip
  projection (subsystem overturned T5 — a second fold would be the
  BattleStatComposer defect class); empire math at the Production/Pressure call
  site; one unlock/lifecycle ledger with namespaced reasons.
- Unlock key `(player_id, scopeKind, scopeKey, defId, revision, dedupe)` with
  `reearnScope never|world|season`; grant/equip/expire distinct keys.
- Loam: Θ-invariant shares only, never in world-scoped bundles; banked Tier-2
  may read `P(Θ)` once. Every faucet names its sink; yield titles carry upkeep.
- UI: two recipes sequenced Hall-first (shipped), shared pieces + 4 new factories
  owned by hall-surface (actor imports, duplicate registration throws), themeRefs
  from existing packs, catalog copy only, folds consume (never recompute).
  Queue/host/pack/tab-migration are Ask-first follow-ups with reversible
  defaults — not pre-work gates (nothing irreversible; unmounted recipe/draft
  still merges).

## Dependency Graph

```
achievement-registry (grammars, tuning/catalog, validation, DAG guard)
    ├── achievement-evaluator (Cold worker, unlock ledger, watermarks)
    │       └── reward-bundles (TryInstantiate client, determinism tuple, fan-out,
                container-kind widening + ParseKind-throw same change)
    │               ├── empire-titles (Hall bindings, economy intent, upkeep, P(Θ) split)
    │               └── actor-titles (existing equip path, slots, worn selector — subsystem overturned)
    │                       └── title-lifecycle (expiry, honors, curses, ritual)
    │                               ├── T7a DONE (catalog rows, recipes, drafts)
    │                               ├── T7b-Hall-fold → T7b-Hall-mount (fold/bus, then factories/mount)
    │                               └── T7b-actor-fold → T7b-actor-mount (fold/bus, then mount; imports factories)
```

## Task List (index — detail in tasks/achievement-title-todo.md)

### Phase 1: Foundation
- [x] T1: Registry grammars + tuning/catalog files + validators
- [x] T2: Evaluator Cold worker + unlock ledger + watermarks
- [x] T3: Bundle client wiring + determinism + fan-out roots

### Checkpoint: Foundation
- [x] Focused tests green, guards (dal/funnel/single-writer) green
- [x] Replay/re-ingest grants nothing new (receipt test)
- [x] Human review before Phase 2

### Phase 2: Titles Core
- [x] T4: Empire Hall bindings + economy intent + upkeep + stacking
- [x] T5: existing equip path + slots + worn selector (subsystem overturned, recorded)

### Checkpoint: Core
- [x] guard-actor-hub green; FULL attribution expands (existing equip grammar)
- [x] Scale-once proven both legs; intent squashed once
- [x] Human review before Phase 3

### Phase 3: Lifecycle
- [x] T6: Expiry/honors/curses/ritual + destinations + probe

### Checkpoint: Lifecycle
- [x] Re-earn vs replay distinguishable; curse lift atomic
- [x] Human review before Phase 4

### Phase 4: Presentation data (DONE)
- [x] T7a: catalog rows + recipes + drafts (shape probes green)

### Phase 5: Presentation React (OPEN — Hall first, one surface per stream)
- [ ] T7b-Hall-fold: Hall fold/bus (pure, no mount)
- [ ] T7b-Hall-mount: 4 factories + HallConsole mount + side-by-side gate
- [ ] T7b-actor-fold: tab fold/bus (consumes worn, never recomputes)
- [ ] T7b-actor-mount: ActorTitleTab mount (migration first or ships unmounted) + side-by-side gate

### Checkpoint: Complete
- [ ] Both mounts green (`npm test` + `npm run build` + `check:bundle`)
- [ ] Draft-vs-SPA screenshots + current wwwroot/vite + owner confirm per surface
- [ ] Ready for review; no specs/plans/code beyond scope

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Vocab widening needs effect-pipeline change | Med | Shipped inside T3 same change (convention + validator regex + ParseKind-throw; 3 pins bumped with comments) |
| FE toolchain absent in worktree (`node_modules`) | Med | `npm ci` in a FE-capable checkout before T7b; no vitest/build claims until then |
| Hardcoded player copy bypassing lingui | Low | No hardcoded copy (catalog only); `npm run extract` if any UI string added, commit locales |
| Ninth tab grammar owned by actor-sheet | Low | Tab ships unmounted if unanswered (recipe/draft/fold/bus still merge); mount waits on migration |
| `panel-rail` host mount wiring owned by gui-lego | Low | Recipe declares host; mount implementation follows gui-lego direction at build |
| Second factory copy for shared piece ids | Med | Ownership test (duplicate registration throws) in T7b-Hall |
| hudToken strings unresolvable in FE | Low | Tokens are catalog strings for `title-card`, not the actor-hud registry; T7b proves render |
| Composite watermark convergence | Med | Stable function of fact ids + both-direction tests in T2 (done) |
| Soft-cap tuning without live data | Low | Tunable defaults now, harness measures later |

## Open Questions

None blocking — UI-ideal OQ1–OQ4 (queue placement, Hall host, rarity pack,
worn-display confirm) are Ask-first follow-ups tracked in T7b with reversible
defaults (Hall-first, empire rail, packs-only, single-worn).

## Parallelization

- T4 ∥ T5 after T1–T3 (done — binding APIs were the contract).
- T7b-Hall-fold ∥ T7b-actor-fold after T7a (folds share the pattern, no code).
- Strictly sequential: T7b-Hall-mount → T7b-actor-mount (factories), mounts after
  their folds, side-by-side gates last per surface.

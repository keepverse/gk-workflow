# Capability map: `backlog-clean-up`

**Status: APPROVED 2026-09-20 (owner: "approve").** The owner approved the module boundaries, the
dependency direction and the build order.

- **Ideal:** [backlog-clean-up-ideal.md](backlog-clean-up-ideal.md)
- **Evidence:** [../research/backlog-clean-up/](../research/backlog-clean-up/README.md)
- **Plan / tasks:** [tasks/backlog-clean-up-plan.md](../../tasks/backlog-clean-up-plan.md) ·
  [tasks/backlog-clean-up-todo.md](../../tasks/backlog-clean-up-todo.md)
- **Specs:** `docs/architecture/backlog-clean-up/spec-<module-id>.md`, written for the four modules
  that have no home spec: `paperwork-reconcile`, `orphan-plan-authoring`, `owner-decision-batch`,
  `pipeline-audit-v2`. Every other module schedules work whose spec already exists in its owning
  program. Each row names that spec.
- **Session record:** `tasks/sessions/backlog-clean-up-20260920.json`.
- **Owner rulings:** [backlog-clean-up/rulings-2026-09-20.md](backlog-clean-up/rulings-2026-09-20.md)
  (D1: R28 extended to all programs; D2: lawn combat stays on, plus a new `lawn-combat-ai`; D3: Task 17
  closed; D4: four corpus-run groups authorized, each under its own charter).

**Relationship to `summoner-convergence`.**
- Independent of it, and never edits its 11 programs' files.
- Two convergence tasks gate modules here: `SP6.6` (the save-switch notice), and `SE4.31`–`SE4.36`
  (the save-identity SignalR `empireId`).
- Several convergence documents delegate work *to* programs this map schedules. For example,
  `species-progression-map.md` §5 names `lawn-tuning-profile` as the owner of Θ freshness L5.

---

## 1. Modules

| # | Module id | Responsibility | Spec | Depends on |
|---|---|---|---|---|
| 1 | `paperwork-reconcile` | Close every stale box, header, gate line and duplicate row the lanes listed. Each close gets a pointer (commit, program or ruling). Document edits only, no code. Covers 30+ files: rift-gate, onboarding-rift, debug-mcp, game-control, live-probe-screenshot, story-scene, data-test-substrate, aura-skill map, drop-tables map, world-map program/todo, phaser-kernel, overlay-switch, gui-lego queue, actor-sheet trail specs, battle-derived-wire / combat-math-dedup (absorbed rows), backlog-clear phases 3/4/6/7/9/10, creature-progression, creature-seed T13 + GAPs, species-build, creature-corpus-self-heal, item phase 7 module 23 + D39, and more. | [spec-paperwork-reconcile](backlog-clean-up/spec-paperwork-reconcile.md) | — |
| 2 | `owner-decision-batch` | One packet of every genuinely owner-only question, each with a stated default and the rows it releases. Includes: the scope of R28; the `rider-default-on` scale debt; live-probe Task 17 closure; the model-calling runs; the live visual gates; the balance passes; the battle-UI call for T6/T10; promotion of `war-feedback` ideas. | [spec-owner-decision-batch](backlog-clean-up/spec-owner-decision-batch.md) | 1 (so the packet lists only true remainders) |
| 3 | `orphan-plan-authoring` | Write the missing plan pairs, in each owning program's own name and the parent-plan template, **for work that already has specs**: `lawn-playable` + `lawn-tuning-profile` (one lawn plan), `deployment-hierarchy`, `effect-pipeline`, and `battle-wire-remainder`. The last merges the true remainder of `battle-derived-wire` and `combat-math-dedup`. It also writes the two missing lawn specs (`lawn-combat-baseline`, and `zombie-power-source` narrowed to a wiring task). | [spec-orphan-plan-authoring](backlog-clean-up/spec-orphan-plan-authoring.md) | 1 |
| 4 | `lawn-signal-ownership` | Before any lawn build, record the `PUT /api/players/current` split in `lawn-playable-map.md` and `spec-actor-liveness-refresh.md`. `SP6.6` owns the save-switch notice. `actor-liveness-refresh` extends it with its own invalidation kinds (Ladder, CommanderAllocation, UniqueAllocation, Equip, Tree) and a reserved `empireId`, so `SE4.31`–`SE4.36` never retrofit it. A cross-program note goes to lane B; its files are not edited here. | lawn-playable `spec-actor-liveness-refresh.md` (amended) | — |
| 5 | `aura-close-out` | Clear the `backlog-clear` Phase 1–2 chain: the BP1 spec review (by the module 2 ruling or an independent agent review), BP2–BP4 `aura-binding-producer`, AU1 decision-5 propagation, AU2 aura containers, `AuraBudget`, and SR-14 (`battle-derived-wire` W6/W7, owned by aura-skill T13). | aura-skill `spec-aura-binding-producer.md`, `spec-aura-content.md`, `spec-aura-magnitude.md` | 2 (BP1 review route) |
| 6 | `creature-remainders` | Route the creature leftovers: `creature-seed` Tasks 1–12 (`CreatureRank`), after an overlap check with convergence `species-progression`; `creature-progression` D2.3 sweep; `creature-lawn-deploy` T4.1/T4.4 + Checkpoint 4; the `creature-standalone` F2.3 test (now unblocked); roster-balance's handed-off species findings (file a task); `party-dungeon` F4 `CreatureMintSpec.Level` and F5 `poolFilter`; F1 threat-audit → `creature-seed` module 7. | owning programs' todos / specs | 1 |
| 7 | `world-remainders` | Confirm `world-stage`'s status and adopt or re-home loam L44/L45/L46/L50, which may have no owner at all. Split `party-dungeon` D4.30 into real tasks. Cover: the D2.16/D5.11 `Resume` auto-policy; F8 entrance placement; F10 contract prices not Θ-scaled; the base-defense siege loadout bridge (`Assembled`); and a re-check of `ActionStockCommit` general dispatch against convergence `action`. | owning programs' todos / specs | 1 |
| 8 | `item-remainders` | Cover: item modules 24 `equipment-activation` and 25 `set-requirement-reconciliation` (unowned; 23 shipped in `species-gear-chain`); re-verify the ~12-line "seed→concrete" cluster against live `effect_container` rows; re-check the X7 `ContainerKind` citations; the named internal residuals (forge mint, reroll/transfer, socket-imbue recipe, `SetDisclosure` multi-set, recipe listing route). | `item-map.md`, item specs | 1 |
| 9 | `ui-remainders` | Cover: gui-lego queue P2/P3 and the P4 remainder; the orphaned `GearTab.tsx` — deleted 2026-09-20, BCU7.1, no longer exists; the GG1 Checkpoint I reframe (a design call); the `disabledReasonGuard` fixes (GG-55 = party-dungeon F9); actor-hud boss tier + perf B2 write-up; shield-sheet D8a/b; story-scene F3/F6/F7/F8 and the T27b FE→injector cue bridge; achievement-title T7b once "P4 rail work" is identified; player-guide PG-F2/F3/F5/F6. | owning programs' todos / specs | 1 |
| 10 | `infra-remainders` | Cover: data-test-substrate BU1–BU4; deletion of battle-timeline's legacy `FUSIONRPG_KERNEL_GRIDS` + `_dotAccum` (B27 passed 2026-09-04); combat-math-dedup **D17** (a live bug: `nerve.*` VFX rows missing); the injector write-path honesty sites (three bare clamps + D22 parity test); live-probe Task 21 (item provenance DTO); the seedsmith naming-grammar module (generator, never hand-edit); the passive-tree H5 `tree_seed_roots` wiring; the passive-tree-repair P11 stale gate (branch merged) and the status-atom executor extension; the missing-reader channel families (one finding from two audits) → `class-system` P9 / battle-wire. | owning programs' todos / specs | 1 |
| 12 | `lawn-combat-ai` (added by ruling D2) | An RPG-AI-layer caster for lawn actors. It triggers on basic-attack count and a timer, reuses `StubIntentSource` / `IIntentSource` over `BoardSnapshotAdapter`, and keeps a reserve floor so the basic attack keeps working. Hot loop only; decisions only on trigger edges. It becomes a module of the lawn plan; this program only owns taking it through `/idea` → map/spec inside that plan. | [combat-ai-ideal.md](combat-ai-ideal.md) (idea phase; widened 2026-09-20 to the shared lawn/battle/delve/siege core; the lawn is one profile) | 3 (lawn plan), 4 |
| 11 | `pipeline-audit-v2` | Extend `gk-core/scripts/audit-program-pipeline.py` with the four blind spots the audit hit: blockquote status headers; completion recorded in the todo header, a ledger or a merged session; a header claiming completion while boxes stay unticked; and missing pointers when a spec's module is cited as built by another program. It stays read-only and asserts no population counts. | [spec-pipeline-audit-v2](backlog-clean-up/spec-pipeline-audit-v2.md) | — |

## 2. Dependency direction and build order

```
paperwork-reconcile ──┬──► owner-decision-batch ──► aura-close-out
                      ├──► orphan-plan-authoring ──► (the orphan programs build under their own plans)
                      ├──► creature-remainders
                      ├──► world-remainders
                      ├──► item-remainders
                      ├──► ui-remainders
                      └──► infra-remainders
lawn-signal-ownership (independent; must land before any lawn build task)
pipeline-audit-v2     (independent)
```

- **Suggested order:**
  - First, `paperwork-reconcile`, `lawn-signal-ownership` and `pipeline-audit-v2`, in parallel. They
    touch disjoint files.
  - Next, `owner-decision-batch` and `orphan-plan-authoring`.
  - Then the five remainder modules, in parallel. Each touches its own programs' files.
- **The one hard edge:** a lawn build task (from the lawn plan that `orphan-plan-authoring` writes)
  never starts before `lawn-signal-ownership` has landed in the documents. It also never adds a second
  `Player`-kind notice before `SP6.6` has shipped.

## 3. Build-first defects (named so the plan puts them early)

| Defect | Module | Why first |
|---|---|---|
| combat-math-dedup **D17**: `VfxCatalog.cs` has no `nerve.unsettled/shaken/afflicted` rows | `infra-remainders` | Live player-visible drift, one file |
| `rider-default-on` shipped on the cost gate only; no `lawn-perf-budget` tunable; scale gate never ran | `owner-decision-batch` → lawn plan | The combat loop is on in production on half its contract |
| `deploy-carry`: `CarryInPools` has zero production assignments | `orphan-plan-authoring` (deployment-hierarchy plan) | Built logic that nothing calls |
| `BattleHubCompose.cs:92` calls `ResolveDerived`, never `Resolve` (W17), so `progression.bonus.*` never reaches battle | `orphan-plan-authoring` (battle-wire-remainder) | A one-compose/one-read gap in the ActorHub rule's own territory |

## 4. Design gate checklist (DESIGN-GATE §5, completed 2026-09-20)

```
[x] Subsystems: process documents (tasks/**, docs/architecture/** status lines), one read-only
    script (gk-core/scripts/audit-program-pipeline.py). Build work is only routed; it is specced in its
    owning programs.
[x] Session boundary: tasks/sessions/backlog-clean-up-20260920.json. session-boundary-check shows
    crossings only against convergence lane B's broad docs/** and tasks/** globs; no active session
    claims these paths.
[~] §1 "Anything at all" row: decisions.md was checked for a lock (none covers backlog/todo
    conventions or R28's scope). software-architecture.md was NOT re-read this session. That is an
    honest gap; nothing here changes an architectural invariant.
[x] Factual claims cite file:line or a commit, through the lane reports.
[x] audit-doc-citations: 0 HIGH on every new document. The lane reports carry LOW "file does not
    exist" hits that are deliberate absence statements (e.g. "no ActorLivenessRevision.cs").
[x] Claims verified against code: lanes A–G read code and git. The headline corrections were
    re-checked in this session: DefaultEnabled = true at LawnBasicAttackFeature.cs:56; the
    roster-balance banners.
[x] No golden, test or sign-off constraint is asserted here. Goldens are named only as H1 edges
    inside the plans this program will write.
[x] No §2 invariant is contradicted. The one live collision (SP6.6 vs actor-liveness-refresh) is
    resolved toward one notice.
[x] Corrections propagated: program-pipeline-audit-2026-09-20.md revision 3.
[x] No population counts are pinned. Counts in this map are readings; pipeline-audit-v2 tests use
    fixtures.
[n/a] No event-refreshed cache is introduced here. actor-liveness-refresh's trigger set is its own
    spec's concern.
[n/a] No ordering-sensitive acceptance criterion.
```

## 5. Out of scope

See [ideal §6](backlog-clean-up-ideal.md#6-out-of-scope). In short: the convergence programs, new
mechanics, `identity-rename`/`ip-censor`, `keepverse-split`, and the 2026-09-19 spec round.

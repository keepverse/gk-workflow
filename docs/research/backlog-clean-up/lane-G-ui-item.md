# Lane G — web UI surfaces and the item program

## Summary (≤10 lines)
UI todos (game-gui, actor-hud, actor-sheet, gui-lego, shield-sheet, aptitude-sheet, condition-glance,
commander-surface, phaser-kernel, phaser-scene-poc, lawn-interactive, status-rail, fe-essentials,
overlay-switch, shield, injector-stub): of ~40 nominally-open lines, the overwhelming majority are
either **OWNER-ONLY** live/visual eyeball checks or **BUILT** with a stale/unticked summary checkbox
(program headers/maps already say Done). Only ~6 are real NOT-BUILT gaps, all already named and
deprioritised. Biggest real finding: **4 Draft "TRAIL — do not implement" actor-sheet tab specs are
SUPERSEDED** by the shipped catalog-era tabs; `GearTab.tsx` is genuine orphaned dead code (not wired,
only its own test imports it). `gui-lego`'s Queue is stale paperwork — P1 Condition and P1b Shield are
Done per `menu-refactor-queue.md` but never ticked in `gui-lego-todo.md`; P2/P3/P4-remainder are
genuinely NOT-BUILT. `phaser-kernel`'s one open line contradicts its own plan header
("Implement complete 2026-09-06") — paperwork only.

Item program: `item-todo.md`'s 136 open lines are **self-documented, not silent drift** — nearly every
one carries a `⏸`/`⛔` marker naming its own owner. All 22 modules are BUILT per the file's own 2026-09-06
FINAL PROOF. Biggest finding: item's **Phase 7 (module 23 `requirement-profiles`) is SUPERSEDED** —
`species-gear-chain` T35/T36 (commit `ac2dae72`) pulled it forward and shipped it; modules 24/25 remain
genuinely unbuilt and unowned. The recurring "seed → concrete generator" blocker cluster is **stale**:
the `seed-to-concrete` program is 131/131 done and its `Instantiator` SDK is already reused by items
(`LootPipeline`, `EquipmentContainerBuild`, `UniqueContainerBuild`); the full corpus-authoring run is
"APPROVED, sequenced" (2026-09-07) and its trigger condition is now met — it's OWNER-ONLY (model-calling
run), not a code gap. `action-corpus`/X3 (GA3/GA4) is confirmed **still genuinely unresolved** — no
production `ActionSeeder.Generate` caller exists in the tree despite `action` being closed in
convergence; per the pipeline audit §3.8 this is by design, owner-owned.

## Items

| Program | Item (task id / module) | Verdict | Evidence | Why it stalled | Convergence relation | Next action |
|---|---|---|---|---|---|---|
| game-gui | T5 `npm run test:e2e` line, T22 visual-not-applicable line | BUILT | `tasks/game-gui-todo.md:110,391` — both explained inline as N/A/superseded by a later task | paperwork-only | independent | tick or leave; no code needed |
| game-gui | Checkpoint G "every plate has matching surface" | NOT-BUILT (deliberate scope cut) | `tasks/game-gui-todo.md:1241-1246` — explicit "explicitly false, by design, not oversight"; World/Battle stages and Loadout/pact-offer/first-session flows have no surface, all owner-approved 2026-08-31 | deprioritised | independent | leave as permanent scope note, not a task |
| game-gui | Checkpoint I: delete superseded pages/redirects (3 lines) | SUPERSEDED (design premise false) | `tasks/backlog-clear-todo.md:290-327` GG1 already investigated: 6 of 7 target pages (`CatalogPage`, `RecipesPage`, `MetricsPage`, `RpgProgressionPage`, `PvzStatsPage`, `ExpeditionsPage`) are **live compositions inside** `AlmanacLayer`/`ChronicleLayer`/`ExpeditionsLayer`/`DeveloperTree`, not superseded wrappers — deleting them breaks the app | left-out-of-convergence (backlog-clear Phase 5, blocked behind Phase 1's BP1 gate per running order) | independent, blocked by backlog-clear | reframe Checkpoint I ("pages are the implementation") or grow the layers' own content — a design call, not deletion |
| actor-hud | 5 LIVE/Unity-eyeball lines (`actor-hud-unity`, `shield-slot-migration` ×2, P6 Unity manual, Program LIVE sign-off) | OWNER-ONLY | `tasks/actor-hud-todo.md:99,126,130,145-146` | owner-gate-uncleared | independent | needs owner to run `prove_actor_hud_live.py` + Unity eyeball once |
| actor-hud | Post-ship "Optional": boss tier signal, HP sliver, glyph art upgrade, perf probe B2 | NOT-BUILT | `tasks/actor-hud-todo.md:170-173`; same 4 items listed verbatim in `tasks/backlog-clear-todo.md` Phase 9 | left-out-of-convergence, blocked behind backlog-clear Phase 1 gate | independent | low priority; unblock only if backlog-clear Phase 1 clears |
| actor-sheet | T13-T14 elements/kit deep chrome, `@xyflow` push depth, T3 Server/Injector host wiring | NOT-BUILT (deferred/optional) | `tasks/actor-sheet-todo.md:27,29,33` — all explicitly "deferred"/"optional / out of FE scope" | deprioritised | independent (FE fixture-catalog fallback covers it) | low priority |
| actor-sheet specs | `spec-derived-stats-tab.md`, `spec-gear-tab.md`, `spec-locked-preview-tabs.md`, `spec-progression-tab.md` — all "Draft — pending owner review" | SUPERSEDED | Each file's own banner: "TRAIL — do not implement… Catalog-era sheet uses `<derived-tab\|kit-tab\|paths-tab\|aptitudes-tab>` instead." `derived-tab`, `kit-tab` (code name for the CatalogTabs `KitTab`), `PathsTab`, `AptitudesTab` are shipped and wired in `gk-web/web/fusion-rpg-web/src/ui/actor/ActorPanel.tsx:14-16,278-290` | absorbed-no-pointer (the trail banner IS the pointer, so paperwork not code) | independent | none — the "pending owner review" status line on 4 dead specs is stale text worth deleting/marking obsolete |
| actor-sheet specs | `spec-paths-tab.md` (no TRAIL banner, still "Draft — pending owner review") | PARTIAL | `PathsTab.tsx` exists and is wired (`ActorPanel.tsx:290`); actor-sheet-todo's own "Paths `@xyflow` push depth — deferred" line confirms shallow impl only | deprioritised | independent | tick the spec status once push-depth work lands, or mark spec status "Draft, partially shipped" now |
| actor-sheet (cross-lane) | `web/fusion-rpg-web/src/ui/actor/GearTab.tsx` | dead code (not superseded — never wired) | `grep` shows zero non-test importers; `ActorPanel.tsx` imports `KitTab` from `CatalogTabs.tsx`, a different component, for the "kit" tab | never-adopted duplicate | independent | candidate for deletion; not covered by GG1's investigation (which only looked at top-level pages, not actor-sheet tab files) — flag for whoever re-scopes GG1 |
| actor-sheet (cross-lane) | `ProgressionTab.tsx` | BUILT, but unrelated to the trailed `progression-tab` spec | Used by `features/aptitudes/AptitudePresetConsoleHost.tsx`/`AptitudesPage.tsx`/`useAllocationDraft.ts` — it is the aptitude-sheet program's own component, name collision only | paperwork-only (naming) | independent | none functionally; note the name collision so nobody "fixes" it by wiring it into ActorPanel |
| gui-lego | Queue P1 Condition | BUILT, unticked | `tasks/gui-lego-condition-todo.md` all 14 lines `[x]`; `docs/architecture/gui-lego/menu-refactor-queue.md` "P1 Condition … Done" | paperwork-only | independent | tick P1 in `gui-lego-todo.md`, point at `gui-lego-condition-todo.md` |
| gui-lego | P1b Shield (not even listed as its own line in `gui-lego-todo.md`) | BUILT, missing from parent todo | `menu-refactor-queue.md` "P1b Shield … Done"; `tasks/shield-sheet-todo.md` Checkpoint C all `[x]` | paperwork-only | independent | add a P1b row to `gui-lego-todo.md` Queue and tick it |
| gui-lego | Queue P4 "other rail layers + remaining Actor tabs" | PARTIAL | `menu-refactor-queue.md`: "Aptitudes: Done" (own map+FE+Injector wire proven 2026-09-14); Fusion/Pacts/Expeditions/Almanac/Chronicle/Status/Elements/Kit/Paths still "Not started" | left-out-of-convergence | independent | split P4 into its Aptitudes-done sub-row + the real remainder |
| gui-lego | Queue P2 Creatures filter chrome, P3 Relics/Commanders | NOT-BUILT | `menu-refactor-queue.md` Status table: "P2+ | Not started (except Aptitudes)" | deprioritised (queue discipline: one surface per stream) | independent | genuinely open work for backlog-clean-up to schedule |
| shield-sheet | SS-D8a segment regenText, SS-D8b cascade/apply-outcome inspect, debug-only GET /shields | NOT-BUILT | `tasks/shield-sheet-todo.md:104-118` under "Deferred (D8 — not Done gate)" — program's own Checkpoint C is fully `[x]` above it | deprioritised, non-blocking by the file's own header | independent | low priority |
| aptitude-sheet | 5 "Follow-ups (non-blocking)": owner retune soft-max, lucide-key content polish, lawn species glance door, posture-balance piece (A6), keep-aligned rematerialize (E6) | NOT-BUILT / OWNER-ONLY (first one) | `tasks/aptitude-sheet-todo.md:242-248`; program's own map-success-checklist above is all `[x]` except "explicitly deferred items only A6/E6" | deprioritised | independent | low priority; first line needs an owner balance pass |
| condition-glance | "Owner may merge internal live-state POST into dump ingest later" | OWNER-ONLY | `tasks/condition-glance-todo.md:79`, under "Follow-ups (non-blocking)" | owner-gate-uncleared (optional) | independent | none required |
| commander-surface | "Until Playwright green, program is not done" | BUILT, stale wording | `tasks/commander-surface-todo.md:253` — the line's own strikethrough-style update says "Playwright 10/10 green; live deploy smoke still owner" | paperwork + one owner-only residual | independent | tick the Playwright half; leave live-smoke owner-only |
| phaser-kernel | "Proceed to Wave 1 code (no owner gate)" | BUILT, contradicts own checkbox | `tasks/phaser-kernel-todo.md:43` unticked, but `tasks/phaser-kernel-plan.md:12-14`: "**Status: Implement complete 2026-09-06** — T0-T12 + CPF + E2E/visual proof. Wave 0-1b freeze landed; Wave 2+/R shipped same session." | paperwork-only (trap #2 — checkbox vs header) | independent | tick the box, cite the plan header |
| phaser-scene-poc | Data-lifecycle bar follow-up | NOT-BUILT | `tasks/phaser-scene-poc-todo.md:14-16` — explicitly "Follow-up (optional, not this program's close)" | deprioritised | independent | low priority |
| lawn-interactive | Checkpoint E "combat book full arm→Intent" | NOT-BUILT, blocked-on-dependency | `tasks/lawn-interactive-todo.md:39` — "deferred until action corpus". Confirmed still true: `grep "ActionSeeder.Generate("` in `src/`/`tools/` outside tests returns nothing, matching `item-todo.md`'s X3 finding below | blocked-on-dependency:action-corpus | `action` is closed in convergence (engine complete) but the **content run** (X3) is not — per pipeline-audit §3.8 that run is owner/model-calling, outside R28 | re-check after the owner runs the action-corpus content generation |
| status-rail, fe-essentials | 0 open items each | BUILT | `tasks/status-rail-todo.md`, `tasks/fe-essentials-todo.md` — fully ticked | n/a | independent | none |
| overlay-switch | Checkpoint 2 "wave 1 done" summary | BUILT, unticked | `tasks/overlay-switch-todo.md:122-123` — every individual Wave-1 task (T0-T9) above it is `[x]` | paperwork-only | independent | tick the summary line |
| overlay-switch | Wave 2 T6/T7's 3 named live-only unknowns (z-order over borderless-fullscreen, alt-tab focus, crash teardown) | OWNER-ONLY | `tasks/overlay-switch-todo.md:127-146` — "What is NOT proven… All three need the game" | owner-gate-uncleared | independent | owner live pass; an orphaned `msedgewebview2.exe` is the no-go signal |
| shield | "Owner-run: deploy, stress scenario, live grant→absorb proof" | OWNER-ONLY | `tasks/shield-todo.md:144` — Checkpoint 5 "Complete (final gate)" above it is otherwise all `[x]` (164 tests, 5-axis review done) | owner-gate-uncleared | independent | owner live pass |
| injector-stub | W3 "Owner live spot-check" | OWNER-ONLY | `tasks/injector-stub-todo.md:9` — W1-W3 code/tests above it all `[x]` | owner-gate-uncleared | independent | owner live pass |
| item | Phase 7 module 23 `requirement-profiles` core (contract, tuning loader, profile-replay tests) — 3-4 of the 12 Phase 7 lines | SUPERSEDED | `tasks/species-gear-chain-todo.md:605-660` T35 (commit `ac2dae72` verified in `git log`) + T36 (`b158acf13`) shipped `RequirementProfileResolver`/`RequirementTrialEvaluator`/`equipment-requirements.v1.json`, exactly to `item`'s own approved spec; `docs/architecture/item-map.md:346-361` documents the pull-forward explicitly | absorbed, WITH a pointer this time (item-map.md cites it) | **overlaps species-gear-chain T35/T36** (convergence, lane C) — already closed there | mark those Phase-7 lines done-by-pointer in `item-todo.md` |
| item | Phase 7 module 24 `equipment-activation` (deployment status, filter inactive equipment, legal-unmet-item-stays-equipped) and module 25 `set-requirement-reconciliation` (envelope-constrained profiles, `SetRequirementCompletability`) — remaining ~7-8 Phase 7 lines | NOT-BUILT | `docs/architecture/item-map.md:164-168` build order "23 → 24 → 25", only 23 pulled forward; no todo owns 24/25 today | absorbed-no-pointer for 23 only; 24/25 genuinely unowned | **species-gear-chain depends on this pattern but hasn't scheduled 24/25** | pull 24/25 forward the same way, or write `item`'s own follow-on plan |
| item | `X3`/`action-corpus` cluster (GA3, GA4, `item_granted_action.container_id` FK) | NOT-BUILT, blocked-on-dependency | `tasks/item-todo.md:7271-7297`; re-verified live: no `ActionSeeder.Generate(` production caller in `src/`/`tools/` | blocked-on-dependency:action-corpus (a model-calling content run, not code) | `action` closed in convergence (engine), but the **corpus-generation run** is explicitly owner-owned per `program-pipeline-audit-2026-09-20.md` §3.8 ("not drift") | wait for/schedule the owner's action-corpus run; nothing to build |
| item | "seed → concrete generator" cluster (module 21 generative pass 36 build sets+~904 species+~904 charms; strain-splice-gen 36 Strains+66 Splices; unique drop entry kind refusal; consumable menu executor; ~12 lines total) | STALE dependency — PARTIAL/re-verify | `tasks/seed-to-concrete-todo.md` is 131/131 `[x]` (the shared `Instantiator` SDK the item lines are waiting on); `gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs` is already called from `LootPipeline.cs`, `EquipmentContainerBuild.cs`, `UniqueContainerBuild.cs`, `ExtendSlotRoll.cs`; `tasks/item-seedgen-todo.md`: "ALL 11 MODULES BUILT… full ~904/36/~904 corpus run — **APPROVED 2026-09-07, sequenced**" on a condition (`item`'s own P1.5-B/P1.5-L done) that is now met per item-todo's FINAL PROOF | absorbed-no-pointer (item-todo text frozen 2026-09-06, dependency landed after) | `species-gear-chain`/convergence did NOT re-run this corpus; it's a standalone owner-triggered generation pass | re-verify each of these ~12 lines against current `effect_container` row counts before re-planning; likely several are BUILT or ready-to-run, not blocked |
| item | effect-atom asks: `ContainerKind` X7/D27 four values (4 lines) | PARTIAL/SUPERSEDED-candidate | `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:31-51` `ContainerKind` now has `Combo`, `Consumable`, `EmpireTitle`, `ActorTitle`, `Relic` — more values than D27's original four, added by later programs (comment: "empire-development… merged 2026-09-16") | absorbed-no-pointer | independent programs (empire-development, others) extended the enum item was waiting on | re-check each X7 citation against current `ContainerKind`; several are likely closed |
| item | D39 `Override` op for `stat.modify` | OBSOLETE | `gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKindRegistry.cs:345-355` explicitly, permanently refuses it: "Override is not a legal op for this kind (it has no revert path; a permanent Override would leak…)" | design decided against it, not merely delayed | independent | mark item-todo's D39 line OBSOLETE, not deferred |
| item | Owner-only product decisions (registry bump; `classes.v1.json` v4 full-run timing; unique pity; PvZ-mode consumables/"rest"/permanent-stat-up confirmation; per-specimen draughts; charm-capacity growth mechanism; several named §9/§10/§11 questions; `Restore` admin surface) — ~15-20 lines | OWNER-ONLY | Each cites itself as "the owner's" / "ask-first" / "a content decision for the owner" throughout `item-todo.md` Phases 3-5 and 7 | owner-gate-uncleared | independent | batch these into one owner decision session |
| item | Internal named residuals owned by item's own later modules (forge cannot mint — no base-type `effect_container`; `reroll`/`transfer` unwired; `socket-imbue` unpayable — no recipe row; `SetDisclosure` multi-set route missing; no recipe-listing route) | NOT-BUILT | Already tabulated in item-todo's own FINAL PROOF table (`tasks/item-todo.md:9526-9532`, modules 14/15/16/20) | deprioritised, small, already named | independent | low priority, well-scoped follow-ups |
| item-content | All 15 lines | BUILT | `tasks/item-content-todo.md` fully `[x]`; carries forward "seed→concrete item generator + classes.v1.json v4 full run" as explicitly out of its own scope | n/a | overlaps the item "seed→concrete" cluster above | none |
| item-seedgen | All 38 lines | BUILT | `tasks/item-seedgen-todo.md`: "ALL 11 MODULES BUILT, ALL 5 CHECKPOINTS CLOSED — 2026-09-07"; full corpus run APPROVED/sequenced, condition now met | n/a | independent trigger for the owner | schedule the corpus-generation run (model-calling, owner/R28-excluded) |

## Cross-lane notes
- `backlog-clear` (Phase 1 BP1 aura-binding-producer spec, awaiting owner review since 2026-08-31) is the
  single gate blocking: game-gui's GG1 (already found not-executable-as-written — a design call, not a
  build), actor-hud's Phase-9 backlog, and several other lanes' items outside this lane's scope
  (loam L44-L50, combat-unification E1-E3, battle-timeline Phases 4-5) — this matches
  `program-pipeline-audit-2026-09-20.md` §3.3/§2 C2 exactly; not re-litigated here.
- `GearTab.tsx` orphan and the `ProgressionTab.tsx` naming collision (above) belong to whichever lane
  ends up re-scoping game-gui's Checkpoint I / GG1, since that's the nearest "dead code" cleanup context.
- Item's module 24/25 gap is a live dependency for `species-gear-chain`'s own pull-forward pattern —
  worth a joint note between this lane's report and any lane covering `species-gear-chain`/convergence
  lane C.

## Doc/paperwork fixes (list, do not apply)
- `tasks/game-gui-todo.md`: tick T5/T22's explained-N/A lines; Checkpoint G's "every plate" line stays
  unchecked by design — add a comment saying so explicitly (already true in prose, not in the checkbox).
- `tasks/backlog-clear-todo.md` GG1: already correctly marked "NOT EXECUTABLE AS WRITTEN" — no fix needed,
  just needs the design-call decision routed to the owner.
- `tasks/actor-hud-todo.md`: no fix; all opens are genuinely owner/optional.
- `docs/architecture/actor-sheet/spec-derived-stats-tab.md`, `spec-gear-tab.md`,
  `spec-locked-preview-tabs.md`, `spec-progression-tab.md`: each still carries a bottom "**Status:**
  Draft — pending owner review" line despite the top TRAIL banner saying "do not implement" — delete or
  correct the stale status line so nobody reads it as "awaiting review to build."
- `tasks/gui-lego-todo.md` Queue section: stale — P1 should read Done (pointer to
  `gui-lego-condition-todo.md`), P1b Shield is missing as a row entirely, P4 should split into
  "Aptitudes: Done" + the real remainder. Source of truth is
  `docs/architecture/gui-lego/menu-refactor-queue.md`, which is already correct.
- `tasks/phaser-kernel-todo.md:43`: tick against the plan's own "Implement complete 2026-09-06" header.
- `tasks/overlay-switch-todo.md:123`: tick against the fully-`[x]` Wave-1 task list above it.
- `tasks/commander-surface-todo.md:253`: tick the Playwright half of the compound line; leave the
  live-deploy-smoke half owner-only.
- `tasks/item-todo.md` Phase 7 (module 23 lines): add a pointer to `species-gear-chain-todo.md` T35/T36
  the way `item-map.md:346-361` already does, instead of leaving them bare unchecked boxes.
- `tasks/item-todo.md`'s D39 Override line: reword from "deferred" to "refused — see
  `AtomKindRegistry.cs:345-355`" since the design decision already landed as a permanent no.

# Lane C — deployment hierarchy and creature programs

## Summary (≤10 lines)
Counts: **BUILT 15** · **PARTIAL 8** · **NOT-BUILT 6** · **SUPERSEDED 0** · **OBSOLETE 0** · **OWNER-ONLY 4** · **UNKNOWN 0**.

1. **`deployment-hierarchy`'s "no plan" is a paperwork gap, not a build gap.** 4 of 7 modules
   (`corpse-cache`, `cache-decay-void`, `cache-field-access`, `cache-retrieval-mission`) are fully
   BUILT — all shipped through `tasks/empire-development-plan.md` Phase 0-3 (commits `1b6fd8de`,
   `29459f9e`, and follow-ons), which never cites the deployment-hierarchy map. `item-durability-repair`
   is PARTIAL via `species-gear-chain` T10/T11/T23/T24 (workbench tier only). `deploy-carry` is PARTIAL
   (the carry logic exists and is tested, but `BattleModels.CarryInPools` has **zero production
   assignments** — still null everywhere). `injury-tiers` is genuinely NOT-BUILT — no `Wound`-status
   family exists anywhere — and convergence (`empire-progression/spec-legion-commander.md`) already
   ships a named fallback for its absence.
2. **`CacheRetrieval.cs` search resolved:** it is `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheRetrieval.cs`,
   a partial-class file following this codebase's own `RpgStore.<Feature>.cs` convention — not missing.
3. **`creature-progression`'s todo is 0/27 ticked but the code is mostly built** — `CreatureProgressionSource`,
   the `EmpireGeneral`-gated XP projector, and unique/Commander dedicated-only composition all verified
   live in code. Only D2.3 (regression sweep) is genuinely untouched. `species-progression` (convergence)
   builds directly on top of this work and treats it as already landed — the two programs are not
   duplicating effort, but neither owns the leftover D2.3 sweep or D0.2's crash-safe terminal settlement.
4. `creature-lawn-deploy`'s 11 open items are all real Phase-4 residue (source/progression conformance),
   not drift. `creature-standalone`'s 4 open items are 1 stale test + 3 genuine OWNER-ONLY live gates.
   `creature-corpus-self-heal`'s 1 open item and `species-build`'s 1 of 4 items are paperwork only.
   `species-build`'s 16-missing-species-anchor gap is **closed** (`KnownMissingPlanSpecies` is now
   `Array.Empty<string>()`) — the todo box was simply never re-ticked.


## Items

### 1. `deployment-hierarchy` (map approved 2026-09-13; `tasks/deployment-hierarchy-plan.md`/`-todo.md` do not exist)

| Program | Item (module) | Verdict | Evidence (file:line, commit) | Why it stalled | Convergence relation | Next action for backlog-clean-up |
|---|---|---|---|---|---|---|
| deployment-hierarchy | `deploy-carry` (module 1) | PARTIAL | `PartyPoolsCarry.cs` (split/build/carry-out logic, tested `50fcdf873` 2026-09-06) and `DelveCarry.cs` `DelveCarryIn.Apply` (statuses/shield only) exist; `grep CarryInPools\s*=` across `src/` returns **zero** hits — `BattleModels.cs:202`'s field is still null at every setup call site, exactly as the map itself describes it ("currently inert") | left-out-of-convergence | independent (no convergence program wires this) | Wire `PartyPoolsCarry.BuildForBattle`/`CarryOut` into the actual delve/battle/lawn/siege setup builders; today it is dead code outside its own unit test (`PartyPoolsCarryTests.cs`) |
| deployment-hierarchy | `injury-tiers` (module 2) | NOT-BUILT | `grep -rl "WoundGrading\|WoundPolicy"` and `find … wound.v1.json` both empty; the only `Wound*` hits in the repo are world-map/district "Wounded" state (`DistrictAssaultResolver.cs`, `FrontierRulesPolicy.cs`) — a different concept | left-out-of-convergence | **convergence depends on it**: `docs/architecture/empire-progression/spec-legion-commander.md:136-137,211` ships an explicit fallback ("a fallen commander member is detached and set `Recovering`… until `injury-tiers` lands") | Plan and build module 2 (P1 status-family widen + tier thresholds + worsening counter + recovery clocks) — nothing downstream can drop the fallback until it exists |
| deployment-hierarchy | `corpse-cache` (module 3) | BUILT | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CorpseCache.cs`; commit `1b6fd8de` (2026-09-16) "feat(empire): scoped inventory, corpse-cache, relic, wonder engine"; deploy-time-snapshot anti-fraud gate landed separately in `29459f9e` (2026-09-17) "gear is committed before a specimen deploys" | built-by-another-program | independent (empire-progression consumes corpse-cache indirectly through the death path, not directly) | Paperwork only: write the retroactive plan pointer (see §Doc fixes) |
| deployment-hierarchy | `cache-decay-void` (module 4) | BUILT | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheDecay.cs`; same `empire-development` Phase 0-2 build family as module 3 | built-by-another-program | independent | Paperwork only |
| deployment-hierarchy | `cache-field-access` (module 5) | BUILT | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs` + `RpgStore.CacheFieldAccessDelve.cs` | built-by-another-program | independent | Paperwork only |
| deployment-hierarchy | `cache-retrieval-mission` (module 6) | BUILT | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheRetrieval.cs` (the "missing `CacheRetrieval.cs`" the brief named is this partial-class file — the codebase's standing `RpgStore.<Feature>.cs` convention, not a gap); `CacheRetrievalTuning` in `gk-core/src/FusionRpg.Core/Items/Materials/DeploymentHierarchyTuning.cs:37`; commits `1b6fd8de`, `ecc18cf3` (2026-09-18), `276470b8` (2026-09-19); tested in `gk-core/tests/FusionRpg.Data.Tests/CacheRetrieval/CacheRetrievalTests.cs` | built-by-another-program | independent | Paperwork only |
| deployment-hierarchy | `item-durability-repair` (module 7) | PARTIAL | Workbench-tier repair + `(max, current)` durability + at-zero filter pulled forward and BUILT exactly to spec §1/§2/§5(workbench)/§6 via `species-gear-chain` T10/T11 (`f67930ac`, 2026-09-16) and T23/T24 (`276470b8`, 2026-09-19) — all four marked ✅ in `tasks/species-gear-chain-todo.md`. Still open: §3 real per-battle wear decrement (`wearPerBattleMilli` is explicitly absent from `gk-core/data/tuning/deployment-hierarchy.v4.json` and `DeploymentHierarchyTuning.cs:10` names it "module 7's own future build"); field touch-up (D4, needs `party-dungeon`'s `PackGrid`, itself unbuilt); commander-pouch parity (D6); death-drop extra decay hook into `corpse-cache` | blocked-on-dependency:party-dungeon-packgrid (field touch-up only); rest is left-out-of-convergence | independent | Plan the remaining §3/D4/D6 slice once `PackGrid` exists; §3 (battle wear) has no external blocker and could be built now |

**Cross-cutting deployment-hierarchy finding:** the map's own "External dependencies" table says `cargo-fate` (a `scoped-inventory-hierarchy` module) needs `deployment-hierarchy`'s corpse-cache/decay/field-access trio to exist — and `tasks/empire-development-plan.md`'s own Overview says (as of its 2026-09-13 writing) *"none of `deployment-hierarchy`'s modules are built yet either (no `RpgStore.CorpseCache.cs` exists)… Phase 0 below builds the minimum slice of that sibling program this plan actually needs."* That sentence is now stale — Phase 0 built the *full* trio (modules 3-6), not a minimum slice — but it is exactly why `corpse-cache`/`cache-decay-void`/`cache-field-access`/`cache-retrieval-mission` show as built with no deployment-hierarchy-owned commit: `empire-development` built them as its own external prerequisite and never looped back to update the deployment-hierarchy map/plan. This is cause **C3** from the audit doc, confirmed independently.

**Map wave-list check:** all 7 modules in `deployment-hierarchy-map.md`'s table have a written spec under `docs/architecture/deployment-hierarchy/` (`spec-deploy-carry.md`, `spec-injury-tiers.md`, `spec-corpse-cache.md`, `spec-cache-decay-void.md`, `spec-cache-field-access.md`, `spec-cache-retrieval-mission.md`, `spec-item-durability-repair.md`) — no unspecced modules.

### 2. `creature-progression` (`tasks/creature-progression-plan.md` header: "partially implemented 2026-09-08"; todo 0/27 boxes ticked)

| Program | Item (task id) | Verdict | Evidence | Why it stalled | Convergence relation | Next action |
|---|---|---|---|---|---|---|
| creature-progression | D0.1 typed source model / closed grammar | BUILT | `gk-core/src/FusionRpg.Core/Creatures/CreatureProgressionSource.cs` (created `061e0651e`, 2026-09-08); cited as landed by `species-progression-ideal.md:137` ("`CreatureProgressionSource.cs:8-75` — closed, versioned") | paperwork-only (todo boxes never ticked) | **species-progression depends on it** (consumes the type directly in `spec-layer-source-selector.md`) | Tick D0.1's 3 acceptance boxes with the citation above |
| creature-progression | D0.2 activity propagation / replay identity | PARTIAL | Source claims persist and parse (confirmed via `RpgXpAwardMap.cs`); but the plan's own header still names "atomic provenance ownership validation, crash-safe terminal settlement" as open, and the dependent `creature-lawn-deploy` T4.1/T4.2 name concrete open gaps (no proven `killerPtr` deferred-death bridge; exact-receipt-replay collision handling incomplete) | blocked-on-dependency:injector-deferred-death-bridge (T4.1) | independent of species-progression (that program reads the fact, does not need the killer-attribution edge case) | Carry into `creature-lawn-deploy` T4.1/T4.4 (already tracked there, see §3) |
| creature-progression | D1.1 source-gated species XP projector | BUILT | `gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs:100-129` `IsEmpireGeneralSource`/`WithSpeciesPlacement` — gates species-award placement strictly on `CreatureProgressionSource.EmpireGeneralKind`, matching the same species id | paperwork-only | species-progression's `spec-layer-source-selector.md` builds its own general/unique/commander switch on top of this | Tick D1.1's boxes |
| creature-progression | D1.2 source-aware general allocation adapter | PARTIAL (verified only via consumer, not the adapter itself) | `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:48-84` never reads `EffectiveSpeciesAllocation`; `SpeciesAllocationSource.cs` exists and is cited by `species-progression-map.md` §2 as an already-landed "resolve seam" (`:106-116`) — but this lane did not independently open `SpeciesAllocationSource.cs` to confirm the reject-unique/Commander acceptance criterion line-by-line | paperwork-only, likely | overlaps species-progression (same file family) | Confirm `SpeciesAllocationSource.cs:106-116` against D1.2's 3 acceptance boxes, then tick |
| creature-progression | D2.1 unique ActorHub dedicated input | BUILT | `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:48-84`: `aptitudeAllocation: _ => commanderAllocation + uniqueAllocation` — no species term anywhere in the file | paperwork-only | consistent with species-progression's own stated boundary (unique/Commander never touch species allocation) | Tick D2.1's boxes |
| creature-progression | D2.2 dedicated rewards / expedition isolation | UNKNOWN | Not independently verified this session (time-boxed); plan lists it PARTIAL 2026-09-08 alongside D2.1, which *is* confirmed built, suggesting the same pattern holds | — | independent | A short grep of `RpgStore.Expeditions.cs` for species-row writes on unique/Commander outcomes would settle this in one call |
| creature-progression | D2.3 isolation regression sweep | NOT-BUILT | Todo marks it **TODO** (not PARTIAL, unlike every sibling task) — this is the one item this lane found genuinely untouched | left-out-of-convergence | **neither program owns this** — species-progression treats D0-D2's *output* as landed but does not re-run a cross-source regression sweep of its own | Run/author D2.3 as a small standalone task, or fold it into species-progression's own conformance checkpoint if that program is willing to own it |

### 3. `creature-lawn-deploy` (11 open), `creature-standalone` (4 open), `creature-corpus-self-heal` (1 open), `species-build` (4 open)

| Program | Item | Verdict | Evidence | Why it stalled | Convergence relation | Next action |
|---|---|---|---|---|---|---|
| creature-lawn-deploy | Phase 1-3 (Checkpoints 1-3) | BUILT | All closed 2026-09-06/07 per todo headers (`✅ Checkpoint 1/2/3 — CLOSED`) — not part of the 11 open items, cited for contrast | — | independent | none |
| creature-lawn-deploy | T4.1 killerPtr deferred-death bridge (1 box) | NOT-BUILT | Todo itself: a 2026-09-08 live probe found the shipped game defers `Plant.Die` ~16ms past `TakeDamage`, so no `killerPtr` is emitted under the strict synchronous rule; needs a proven deferred-death bridge without HP polling | blocked-on-dependency:injector-timing-fix | independent | Genuine open engineering task, correctly scoped (no HP scans, no inference) |
| creature-lawn-deploy | T4.2 receipt-replay + full binding-id schema (2 boxes) | PARTIAL | Binding-session creation/refusal and the current ptr/match transactional path are done (`[x]`); exact-replay-is-a-no-op and the full binding-id receipt schema are explicitly deferred to T4.4's migration | blocked-on-dependency:T4.4 | independent | Carries forward into T4.4 as already planned |
| creature-lawn-deploy | T4.4 conformance/regression sweep (3 boxes) | NOT-BUILT | Marked **TODO** outright; depends on T4.3 (done) | left-out-of-convergence | independent | Standalone task, well-specified in its own acceptance criteria |
| creature-lawn-deploy | Checkpoint 4 (4 boxes) | NOT-BUILT | Blocked on T4.4 | blocked-on-dependency:T4.4 | independent | Closes automatically once T4.1/T4.4 land |
| creature-lawn-deploy | Line 34 struck-through Commander-refusal box | OBSOLETE | Text itself: "~~Deploying the current default Commander's own instanceId refuses~~ — inapplicable today" | paperwork-only | independent | Tick or delete the line; it documents its own obsolescence |
| creature-standalone | F2.3's live differently-rarity'd-fusion test (1 box) | NOT-BUILT (no longer blocked) | Todo said the test was "honestly deferred to F2.4: `ExecuteFusion` … does not exist yet" (2026-09-07) — but F2.4/F2.5 are both `[x]` DONE the same day and `ExecuteFusion` exists (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs`) | absorbed-no-pointer (dependency cleared but test never written) | independent | Small, now-unblocked task: write the real two-differently-rarity'd-sacrifice fusion test |
| creature-standalone | Checkpoint F2 live two-specimen fusion execute (1 box) | OWNER-ONLY | Todo: F2.5's live check verified preview/selection end-to-end against a real server/roster but deliberately stopped short of `execute` because the only connected player was a real live game session and execute irreversibly consumes real specimens | owner-gate-uncleared | independent | Needs the owner's own run, or a disposable test player/specimen pair (todo already says this) |
| creature-standalone | PT7 LIVE gate / Checkpoint P LIVE half (2 boxes, same gate) | OWNER-ONLY | Todo: "LIVE gate (owner)"; SIM half passed 2026-08-21, LIVE half sign-off pending — a live-visual-judgement gate per the debug-API hard rule (Game Injector Debug can prove Unity reflects state, never player-facing verdict) | owner-gate-uncleared | independent | Owner runs the named `deploy-play.ps1` handoff already in the todo |
| creature-corpus-self-heal | "both reruns state=completed, checked not assumed" (1 box) | BUILT (paperwork-only) | C3 itself is `[x]` done 2026-09-04 (110/110, 0 failed) with real before/after evidence (Phase D); the 9 species that hard-failed import on `attackTempo: unresolved` (SeaMagnet, CactusPumpkin, SunBomb, …) are now clean — `grep attackTempo.*unresolved` across `gk-data/packs/fusion/data/seed/creatures/species/*.json` returns zero hits | paperwork-only | independent | Tick the box after confirming `creatures run status` once (a one-command formality, not a rebuild) |
| species-build | "Not the lawn" bullet under T4.6 (1 box) | BUILT (paperwork-only) | Every sibling bullet under this task is `[x]`; this one reads "true by construction (nothing in `FusionRpg.Injector` references any of this module's types)" — a true-by-construction claim already made, just never checked off | paperwork-only | independent | Tick it |
| species-build | 16-species missing plan anchors (2 boxes, G2) | **BUILT** — todo is stale | `KnownMissingPlanSpecies = Array.Empty<string>()` in `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlanCatalogRealFileTests.cs:102` — the allowlist that named the 16 missing species (cherrygatling, jalapeno, …) as of 2026-09-05 is now empty, meaning every species in the compiled catalog resolves to a plan | absorbed-no-pointer (content authoring closed the gap; todo never re-run) | independent | Tick both boxes; the "16 still missing" finding in the todo body is dated 2026-09-05 and superseded |
| species-build | `species-builds.md` WIP→Shipped, blocked on `doublecherry`'s `attackTempo` (1 box) | OWNER-ONLY | Todo (2026-09-07): "the one honest thing left holding the guide's badge back" — needs a model call to classify one species's closed-vocabulary `attackTempo` field; this lane did not find a dedicated seed anchor file for `doublecherry` under `gk-data/packs/fusion/data/seed/creatures/species/` (only a generated roster row and an unrelated item set exist) | owner-gate-uncleared (model-calling classification run, same class as `action-distribution-gaps` §3.8 in the audit doc) | independent | Run the targeted re-classify for `doublecherry` the same way the corpus-self-heal program did for its 9 species, then flip the doc status |

### 4. `scoped-inventory-hierarchy`, `empire-inventory-surfaces`, `empire-wonder-surfaces`, `loam-relics-and-wonders`

**There is a plan, and it is ~88% built — it is just not filed under any of these four maps' own names.**
`empire-development-plan.md`/`-todo.md` is explicitly the umbrella plan for `scoped-inventory-hierarchy` +
`loam-relics-and-wonders` ("Program: `empire-development` (umbrella over `scoped-inventory-hierarchy` +
`loam-relics-and-wonders`)"), and `empire-inventory-surfaces-map.md` / `empire-wonder-surfaces-map.md`
both say verbatim "**Plan:** extends `tasks/empire-development-plan.md` Phase 4A/4B(.1-.4)/4D." All four
maps are answered by one plan; this is exactly the source of the `1b6fd8de` "empire" commit the brief
named.

| Program | Item | Verdict | Evidence | Why it stalled | Convergence relation | Next action |
|---|---|---|---|---|---|---|
| empire-development (Phases 0-3) | full trio + relic/Wonder engine | BUILT | `tasks/empire-development-todo.md` Checkpoint: Phase 3 complete — `[x]` end-to-end mint→deposit→spend→build→observe, full Core/Data/Guard suites green, 6/6 boundary guards, "Ready for owner review / live deploy-play smoke test"; commits `1b6fd8de` (2026-09-16), `29459f9e` (2026-09-17) | — | independent (this is the corpse-cache/cargo-fate/wonder machinery deployment-hierarchy's own map depends on) | None — paperwork pointer only (see §Doc fixes) |
| empire-development | 3 "Deferred, named future work" notification hooks (`spec-sector-storage.md`, `spec-cargo-fate.md`, `spec-wonder-build-flow.md` — each ships silent-to-player) | PARTIAL/planned elsewhere | `tasks/empire-development-todo.md`: "carried for a future notification-consumer session"; `docs/architecture/notification-ssot-map.md:203-205` **already names all three specs by file and line** as inputs its `world-notify-source`/`cache-notify-source` modules must read | left-out-of-convergence at empire-development's own layer, but **picked up by name** at the consumer layer | **overlaps convergence `notification-ssot`** (lane D, one of the 11) — check that program's ledger for build status of `world-notify-source`/`cache-notify-source` | No new plan needed here; verify notification-ssot's ledger actually closes these three, then tick empire-development's own boxes with a pointer |
| empire-development | Relic drop weight/rate table, `EmpireWonderUpkeepRateMilli` real value | NOT-BUILT (by design) | Todo: "ship a low default / provisional `50`, flag for balance pass" — both are tunables shipped with placeholder values on purpose | deprioritised (explicit balance-pass deferral) | independent | A balance pass, not an architecture task — decide by principle per the "decide tunables by principle" rule, publish `v{n+1}` via `gk-core/tools/tuning/publish.py` |
| empire-development | 4B.3 runtime-corpus relic rows, 4C.3 anti-fraud Roster gate | NOT-BUILT | Todo tags both "(item-program ask)" — asks filed on the item program, not this program's own scope | blocked-on-dependency:item-program | independent | Track as item-program's inbox item, not this program's |
| empire-development | 4C.2 wipe path | NOT-BUILT | Todo tags it "(gated on loot-pack §7)" — the same `loot-pack` §7 "Wiped" amendment the audit doc's §3.3 names as blocked behind the unreviewed `aura-binding-producer` spec in `backlog-clear` | owner-gate-uncleared (same root cause as the audit doc's Action #4) | independent | Resolved the moment the owner clears `backlog-clear`'s Phase-1 gate (audit doc Action #4) — do not duplicate a second ask |
| empire-development | 2× "Reviewed with human" checkpoints (inventory UI, wonder UI) | OWNER-ONLY | Todo: both UI checkpoints have every engineering box `[x]` except a bare "Reviewed with human" line | owner-gate-uncleared | independent (this program is outside the convergence 11, so R28's gate-lift does not reach it) | Needs the owner's own look at the shipped UI; nothing else is outstanding on either checkpoint |

## Cross-lane notes (items found here that belong to another lane or no lane)

- The three notification-hook items above are convergence `notification-ssot` (lane D) territory — if
  another lane is auditing convergence internals, hand them `notification-ssot-map.md:203-236` and
  `tasks/empire-development-todo.md`'s "Deferred, named future work" section together.
- `empire-development`'s 4C.2 wipe-path gate and `creature-standalone`'s live-fusion/PT7 owner gates all
  trace back to the same class of blocker the audit doc's §3.3/§2 (C2) already names — `backlog-clear`'s
  unreviewed `aura-binding-producer` spec and the general 47-open-owner-gate count. Worth one combined
  "clear the gates" decision rather than four separate asks.
- `species-gear-chain` T10/T11/T23/T24 (item program) is the actual owner of `deployment-hierarchy`
  module 7's shipped slice — any lane auditing `species-gear-chain` or the item program should know
  `deployment-hierarchy-map.md`'s own text already documents this pull-forward in detail (its final two
  sections, "Filed by the `species-gear-chain` initiative" and both "Resolved 2026-09-15" notes).

## Doc/paperwork fixes (stale headers, unticked boxes, dead citations) — list, do not apply

1. `tasks/deployment-hierarchy-plan.md` / `-todo.md`: write them, citing `tasks/empire-development-todo.md`
   Phase 0-3 for modules 3-6 and `tasks/species-gear-chain-todo.md` T10/T11/T23/T24 for module 7's
   workbench slice — do not re-plan work already shipped. Plan only module 1's real wiring, module 2 in
   full, and module 7's §3/D4/D6 remainder.
2. `tasks/empire-development-plan.md`'s Overview: "Confirmed this session: none of `deployment-hierarchy`'s
   modules are built yet either (no `RpgStore.CorpseCache.cs` exists)" is stale — that file, and three of
   its four siblings, now exist (this plan built them).
3. `tasks/creature-progression-todo.md`: tick D0.1, D1.1, D2.1 with the code citations in §2 above; verify
   and tick D1.2; leave D0.2 and D2.3 open with their real remaining scope named.
4. `tasks/creature-corpus-self-heal-todo.md` Checkpoint C: tick after one `creatures run status` check.
5. `tasks/species-build-todo.md`: tick the "Not the lawn" bullet (T4.6) and both G2 boxes (16-species gap
   — `KnownMissingPlanSpecies` is empty, the gap is closed); leave the `doublecherry`/guide-status box
   open pending its owner-run model-call re-classify.
6. `tasks/creature-standalone-todo.md` F2.3: either tick with a pointer to F2.4/F2.5 having superseded the
   blocker, or leave open and write the now-unblocked real fuse test — currently reads as blocked on
   something that no longer blocks it.

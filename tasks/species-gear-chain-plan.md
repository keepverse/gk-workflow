# Plan: `species-gear-chain` — implementation plan

**Spec:** 20 module specs (19 + `craft-assurance`, added 2026-09-18) under `docs/architecture/species-gear-chain/`, indexed by
[species-gear-chain-map.md](../docs/architecture/species-gear-chain-map.md) (audited, corrected,
owner-reviewed 2026-09-13). **Tasks:** [species-gear-chain-todo.md](species-gear-chain-todo.md) —
this pair, never the bare `tasks/plan.md`/`tasks/todo.md` (the perf stream's).

**Revision 2 (2026-09-13):** a three-agent `/plan`-audit pass found and fixed 6 structural defects
in revision 1. See § Round-2 corrections. 34 tasks now, up from 29 — the increase is one genuine
scope addition the owner approved (a durability slice pulled forward from `deployment-hierarchy`
module 7), not padding.

**Revision 3 (2026-09-13):** a full sweep of every open question and blocked item across all 19
specs, presented to the owner for sealing. Eight real decisions made, the largest being a second
pull-forward — `item` module 23 `requirement-profiles` — that **fully un-defers `item-upgrade-tree`**.
**The deferred list is now empty.** 39 tasks, up from 34 (T18b, T35–T38). See § Round-3 decisions.

**Revision 4 (2026-09-18, session `plan-sgc-20260918`) — amended under the parent
[summoner-convergence-plan.md](summoner-convergence-plan.md), lane C.** The parent owns cross-program
order, the hard edges (H1–H7) and the shared tuning ledger (§5); this pair owns `species-gear-chain`'s
own tasks. What changed: **24 tasks ticked shipped** with their commit hashes (checked on `HEAD`, not
on the map's word); the new 20th module **`craft-assurance`** got its tasks, with the **free-ward fix
first** (T39, a live defect); **T34 rewritten** for R9 (species 2 · family 8 · general 0, a deterministic
trophy planner, `species-material-run.v1.json`, `perGeneral` refused) and R22 (per-kill family roll;
the species counts in every family), split T34–T34d plus T30b; T23/T24/T29–T33/T37 amended to the
strengthened specs; every in-place tuning bump replaced by a `v{n+1}` publish in the parent §5 order;
T47 (creature-seed ask 4 coordination) and T48 (a stale comment) added. **54 tasks: 24 shipped, 30
open.** Existing ids are unchanged; new ids are T30b, T34b–T34d, T39–T49. See § Architecture decisions *Added by revision 4* and the sections after it.

---

## Overview

Four idea-phase docs were audited into one capability map and 19 module specs, then a five-agent
audit fixed ~35 defects across them, then this plan turned the 19 specs into an ordered, checkpointed
task list, then a second three-agent audit fixed 6 more defects **in the plan itself** — the
map→task translation did not fully inherit the rigor the module-level audit already established.

The specs are unusually complete: each already carries its own Design, Tunables, Numeric types,
ActorHub gate, Testing strategy, Boundaries and Success criteria. This plan's job is **not** to
re-derive that content — it is to (a) fix the build **order**, (b) slice each module into S/M-sized
vertical tasks, (c) separate what is buildable now from what is blocked on other programs' unbuilt
code, and (d) checkpoint often enough that a reviewer never has to trust more than a few tasks' worth
of unverified work at a time.

## Round-2 corrections (2026-09-13, three-agent `/plan` audit)

| # | Defect in revision 1 | Fix |
|---|---|---|
| 1 | ⛔ **`craft-risk-ladder`'s own spec states Stage 1 may not ship alone** without (a) stage 2's decay, (b) a restore verb, or (c) an explicit owner verdict accepting a temporary hard stop (`AGENTS.md`'s no-hard-progression-ceiling rule) — the plan shipped none of the three | **Owner chose (a)/pull-forward, 2026-09-13.** A minimal slice of `deployment-hierarchy` module 7 (durability storage + derivation + workbench repair, **not** field touch-up or death-drop decay) is now built inside this plan. This fully un-defers `craft-risk-ladder` Stages 2–4 — see the new Phase 2 tasks and § Cross-program pull-forward below |
| 2 | ⛔ **`craft-executor-completion`'s own spec header says "Depends on: nothing... runs beside `rarity-promotion`, not after it"** — the plan sequenced it behind `rarity-promotion` anyway, needlessly stalling 14 stranded recipes | Moved to Phase 1 (T14–T15); dependency corrected to none. The map's own build order had the same error and is fixed too |
| 3 | ⛔ **The "contested sixth `MaterialClass`" claim was a misreading.** `deployment-hierarchy-map.md:89` says *"shard-leg material class **at high rungs**"* — reusing the existing `Shard` class, not proposing a new one. There is no collision | Struck from the map, the plan's Risks table, and `species-materials`' task |
| 4 | **`gem-tier`'s single task covered only 3 of 10 spec success criteria** — the upcycle verb, `recipegen` content, and the mirror-reconciliation test were silently dropped, not deferred | Split into two tasks (T8, T9); the second covers the missing half |
| 5 | **`wave-species-roll` and `wild-species-spawn` both claimed to share a `CreatureAdmission` policy type, but only one spec's code sample actually calls it** — a live inconsistency between two governing specs, not just a task-sequencing risk | New tiny task (T5) creates the shared type first; T6/T7 both depend on it and are corrected to call it, overriding the one spec's stale inline sample |
| 6 | **`set-species-binding`'s tasks omitted the C# runtime side** (`FusionRpg.Data` importer, `ItemSeedValidator` closure check) the spec's own Objective ("make the field **queryable**") requires | Added to T28 |

Also fixed, lower severity: T2/T3 now explicitly sequenced (both touch
`anchor/schema.py`); Phase 1 and Phase 3 gained interior checkpoints (skill guidance: every 2–3
tasks, not once per phase); several tasks' Acceptance Criteria restored qualifiers the coverage audit
found dropped (e.g. "proven across a shuffled catalog order," "no shipped `rarityGrant` row edited").

## Round-3 decisions (2026-09-13, full open-questions and blocked-items sweep)

The owner reviewed every open question and every blocked item across all 19 specs in one sitting.
Eight produced a real change; the rest are recorded in § Open questions below, sealable at any time,
none blocking.

| # | Decision | Consequence |
|---|---|---|
| 1 | `gem-tier`'s upcycle stays **same-family only** (not cross-family) | Spec's own recommendation confirmed; no task change |
| 2 | `wild-species-spawn`'s members take their **species' own `P(Θ)`**, not the flat `UnmadeMemberHp` | New task **T18b** (Phase 2) — kept out of T7 (Phase 1) to avoid pulling a Phase-1 task behind a Phase-2 dependency; T7 ships with the flat value as a named interim |
| 3 | ⭐ **`creature-drop-tables` carries `Equipment`-kind drops in v1, not materials-only** — **reverses this plan's own recommendation** | New success criterion 3a; `DropEntryKind.Equipment` is already a built mint arm (`LootMintAt.cs:77-87`), so this is not a new equipment-roll design — only a `thetaContent` input, shared with E3a's species-rung derivation for the shard |
| 4 | The species-cost multiplier **applies to `elevate`**, not just enhance/temper | No new task — `elevate` must resolve through the same shared cost-resolution function every verb uses (T26 confirms this); T32 (Phase 4) wires the multiplier into that function once, and `elevate` inherits it automatically |
| 5 | `socket-combat-wiring`'s insert binds at the **host's existing role**, socket index carried in the SourceId | Confirms the spec's own recommendation; no task change |
| 6 | `socket-combat-wiring` ships **arm 1 alone, then arm 2** (combination/resonance grants as a follow-on) | Confirms the spec's own recommendation; T21/T22 stay scoped to arm 1 |
| 7 | `enhance-track-wiring` grants follow the **authored track below +20, a fixed stride above it** | Confirms the spec's own recommendation; no task change |
| 8 | ⭐⭐ **`item` module 23 `requirement-profiles` is pulled forward**, exactly as the durability slice was — it already has a complete, approved spec with zero code. **This fully un-defers `item-upgrade-tree`.** Its non-armour successor spine is a new authored `successorOf` field per base type (weapon/offhand/jewel), never derived from the class ladder | New tasks **T35–T38** (Phase 1: the resolver/evaluator/tuning; Phase 3: the upgrade executor + `successorOf`). **The deferred list is now empty.** Filed into `item-map.md` |

## Cross-program pull-forward — read before Phase 1/2's durability tasks

Building `craft-risk-ladder` Stages 2–4 requires *some* form of durability, which is
`deployment-hierarchy` module 7's territory, not this initiative's. The owner approved building a
**minimal slice** of it here rather than deferring the whole risk ladder or inventing a parallel
mechanism:

- **Built here:** storage (`durability_max`/`durability_current` columns), derivation
  (`DurabilityTable.Build` over `class`/`rarity`/`tags`), the at-zero enforcement filter, and
  **workbench-only** repair (`RepairPolicy.Resolve`, the `Repair` `op_kind`/`CraftOperation` members,
  the destruction-on-repair-attempt chance) — all built **exactly as
  `deployment-hierarchy/spec-item-durability-repair.md` §1/§2/§5/§6 already specify**, not a parallel
  invention.
- **Not built here, still deployment-hierarchy's own future work:** field touch-up (needs
  `party-dungeon`'s `PackGrid`, itself unbuilt), death-drop extra decay (needs `corpse-cache`,
  unbuilt), commander-pouch parity (D6).
- **This is filed back into `deployment-hierarchy-map.md`** so that program's own eventual plan does
  not duplicate the slice — see the todo's task notes.
- **Consequence:** `craft-risk-ladder` Stages 2–4 are **no longer deferred**. The second
  pull-forward in this plan (see § Round-3 decisions #8 — `item` module 23
  `requirement-profiles`, T35/T36) likewise fully un-defers `item-upgrade-tree`, so **the
  deferred list is now empty** — see § Deferred.

## Architecture decisions

- **`rarity-promotion` sits after `craft-risk-ladder` Stage 1 and after the durability pull-forward's
  `Repair` op_kind lands** (not merely after Stage 1, as revision 1 said) — it needs the next enum
  ordinal after `Repair` claims the eleventh slot, and both land inside this same plan now, so the
  ordering is enforced by task dependency, not by hoping two separate programs coordinate.
- **`craft-executor-completion` runs in Phase 1**, per its own spec's correction — it needs zero enum
  members and nothing else in this plan blocks it.
- **`item-upgrade-tree` is no longer deferred** — revision 3 pulls forward `item` module 23
  `requirement-profiles` (T35/T36, built exactly to its own approved spec) and adds the
  upgrade executor + `successorOf` (T37/T38). ⚠ *Revision 4:* one open task now waits on another
  program — T34c's **content** on `creature-seed` ask 4 (T47, shipped behind a default) — and T34d's
  publish precedes `SSH socket-pricing` in the parent §5 order.
- **No enum-slot pre-work gate**, beyond the ordering above. `MutationOpKind`/`CraftOperation` slot
  additions are reversible (git-level ordering), not an irreversible collision.
- **`themes.v2.json` + migration is a task, not a gate** — the owner already decided this.

### Added by revision 4 (rulings — not re-litigated)

- **R9** — trophy materials are **species 2 · family 8 · general 0**; the general layer is removed
  outright (no ids, no leg, no planner branch, no `perGeneral`). **R22** — a multi-family species rolls
  one family per kill with equal odds on `item.trophy-family.{tableId}.{groupKey}`, and counts as a
  member of every listed family for recipes. **R-SC2** — the species-cost threshold is one default plus
  an explicit per-verb override. **R-G1** — one durability pool, one unit, two wear formulas; a
  boss-farmed consumable layer (`craft-assurance`). **R10** — *protect* never covers a repair's destroy
  chance. **R20** — `forge-gem`'s souls coefficient is repriced only by `SSH combo-budget`'s report,
  published by `SSH socket-pricing`.
- **Tuning revisions are new files** (`tunables-ssot.md` T4; map § Corrections #11 reversed): every
  change is `v{n+1}` through `gk-core/tools/tuning/publish.py`, host reader switched in the same commit (parent
  **H7**). T4's and T6's in-place edits are grandfathered history, never a template.
- **Combination binding (arm 2) is not this program's** — `SSH combo-bind` owns it on the
  `EquipProjector` seam T21 shipped. No task here.

## Dependency graph — remaining work (revision 4)

Shipped modules are omitted (✅ list below). Arrows are task dependencies; `Hn` marks a parent hard edge.

```
Wave 0 (no deps)          T39 free-ward fix ⛔ live defect · T47 creature-seed ask 4 (coordination) · T48 stale comment

Phase 2 (remaining)       T21 ─► T22 socket withdraw/orphan
                          T11 ─► T23 durability repair  ──(materials v{n+1}, H7)
                          T10,T11 ─► T24 craft wear  ──(deployment-hierarchy v3 only if the table changes, H7)
                          T10,T23 ─► T25 ─► T26 rarity promotion

Phase 3                   T16 ─► T27 ─► T28 set-species-binding
                          T18 ─► T29 E2 credit
                          T18 ─► T30 E1 ninth source_kind ─► T31 E3a shard-by-rung (creature-yield v1)
                          T26,T24,T36 ─► T37 ─► T38 item-upgrade-tree

Phase 4                   T28 ─► T32 species-cost-shaping (materials v{n+1} — first in the §5 ledger, H7)

Phase 5                   T33 Trophy class (no deps; shares the `27` canary with T40)
                          T33 ─► T34 trophy planner (species-material-run v1)
                          T32,T33,T34 ─► T34b injected catalog + recipe legs (R22 cost side)
                          T30,T34 ─► T30b parametric entry shape
                          T30b,T31,T34 (+ content: T47) ─► T34c trophy legs + R22 family roll
                          T32,T34b,T34c ─► T34d materials v{n+1} + D5 + end-to-end (then SSH socket-pricing)

Phase 6 craft-assurance   T40 Assurance class · T41 assure + craft-assurance v1
                          T39,T40,T41 ─► T42 paid ward/assure (lines, one transaction)
                          T24,T42 ─► T43 protect vs craft wear
                          T23,T40,T41 ─► T44 repair leg, R10 refusal
                          T40,T29 ─► T45 boss-only rule + first boss entries
                          T24,T41,T45 ─► T46 report ─► T49 one-pass balance (with T43,T44)
```

No cycles. **Parent hard edges that apply here: H7 only** (reader switch in the publish's commit) — on
T23, T24/T49, T31, T32, T34d, T41. Nothing in this program writes an H2-rekeyed table, touches a golden
in the H1 chain, or edits `sockets` (H3). The §5 publish order is the parent's tie-break ledger, not a
hard edge.

## Suggested order and parallel lanes — **suggested, not enforced**

Two lanes inside this program; they share no files except `CostClassMatrix.cs`/`MaterialCatalog.cs`
(T33/T40 and T43/T44 — land those pairs in sequence, not in parallel) and `ItemWorkbench.cs` (T23, T26,
T37, T42–T44, T34d — rebase, one verb per commit).

| Lane | Suggested sequence | Why this order |
|---|---|---|
| **C-craft** | **T39** → T40 → T41 → T42 · T23 → T44 · T24 → T43 · T25 → T26 → T37 → T38 · T45 → T46 → T49 · T22 anywhere | T39 is the lane's (and the parent lane C's) first task — a live defect with no dependencies. Assure + paid ward need nothing unbuilt; protect and repair follow the two durability tasks |
| **C-species** | T29 → T30 → T31 · T27 → T28 → T32 → T33 → T34 → T34b → T30b → T34c → T34d | The spine: credit, source, rung, binding, cost, then the materials that make it earned. T34c's **content** waits on T47; its code does not |
| anytime | T47 (ask), T48 (comment) | Independent XS |

## Phases — status and remaining tasks

| Phase | Modules | Shipped (✅) | Open | Sizes (open) | Parallel-safe |
|---|---|---|---|---|---|
| 0 | `craft-assurance` (defect), `delve-species-wiring` (comment), coordination | — | T39, T47, T48 | S, XS, XS | yes |
| 1 | tier-propagation, threat-band, socket allowance, admission, wave roll, wild spawn, gem-tier, risk ladder 1, durability a, enhance track, executors, requirement profiles | ✅ T1–T15, T35, T36 | — | — | — |
| 2 | ladder repair, magnitude synth, wild HP, delve wiring, socket combat, durability b, risk ladder 2–3, rarity promotion | ✅ T16–T21, T18b | T22, T23, T24, T25, T26 | S, M, M, M, M | T22 ∥ T23 ∥ T24; T25 after T23 |
| 3 | set binding, creature drop tables, upgrade tree | — | T27, T28, T29, T30, T31, T37, T38 | S, M, M, M, M, M, S | two lanes |
| 4 | species cost shaping | — | T32 | M | — |
| 5 | species materials (R9/R22), parametric entry | — | T33, T34, T34b, T30b, T34c, T34d | M ×6 | T33 ∥ T34 chain start |
| 6 | `craft-assurance` | — | T40, T41, T42, T43, T44, T45, T46, T49 | M, M, M, S, S, S, S, M | T40 ∥ T41; T45 ∥ T42 |

**Shipped commits** (each ticked in the todo with its evidence): T1 `7e7b3456b` · T2 `73817463a` ·
T3 `bbf6e1e39` + `0faad36e9` + `18ed440e1` · T4 `72607c136` · T5 `cb43a0049` · T6 `63b9e8eb9` ·
T7 `d2361c761` · T8 `15ffb5f97` · T9 `50368b576` + `eddd9e11b` · T10 + T11 `f67930ace` ·
T12 `876641fc7` · T13 `f9d81a965` · T14 `e66618a3e` · T15 `99e413984` · T16 `2b1d24642` ·
T17 `e866b9bef` · T18 `4feb57419` · T18b `ee09f9d7a` · T19 `937390c3b` · T20 `50a054c1e` ·
T21 `0bcdbc332` · T35 `ac2dae72e` · T36 `b158acf13`.

## Checkpoints (review points, not gates)

Phase 1's checkpoint and sub-checkpoints: tasks all shipped; the filed-note evidence lines are ticked,
the suite-green lines are left for the parent's CC8. Then, in the todo:

| Checkpoint | Evidence |
|---|---|
| Wave 0 | `wardLoaded: true` refused, checkbox gone — the parent's **CC1** line for lane C |
| Phase 2 | the 10 `elevate` recipes run; socket withdraw leaves no orphan; craft wear decays, never destroys |
| Phase 3 | set entries carry `speciesId`; a drawn material credits the shelf; manifests byte-identical |
| Phase 4 | below-threshold costs byte-identical; `materials.v{n+1}` read by the host |
| Phase 5 | a species-bound piece enhanced with its own species' trophy, end to end; `--check` green; no general id |
| Phase 6 | 100% reachable by consumables; free ward gone; R10 refusal; boss-only sourcing; report prints |
| Complete | the parent's **CC6** ("species materials 2/8/0") for this program's half; full suite at **CC8** |

## Cross-program edges

| Edge | Direction | Kind |
|---|---|---|
| `SSH combo-bind` | owns `socket-combat-wiring` arm 2 | ownership — no task here |
| `SSH socket-pricing` | publishes `materials` **after** T34d (incl. R20's `forge-gem` coefficient from `SSH combo-budget`) | §5 ledger order |
| `SSH circuit-topology` → `SSH combo-budget` | own `sockets` v2/v3; this program plans no `sockets` publish (T9's `upcycleInputPerOutput` is unchanged) | §5 ledger |
| `creature-seed` ask 4 | T47 → T34c's content | parent §3 coupling (soft) |
| `TVB python-test-lane` | T34 adds a seedsmith `--check` step to `ci.yml`, the file TVB also edits | coordinate, rebase |
| `item-seedgen` module 3 | owns the trophy planner (T34 files the ask) and `materialgen` (T33/T40) | ask-first rows |
| `deployment-hierarchy` module 7 | T23/T24 build its slice; field touch-up and death-drop decay stay its own | filed note, `deployment-hierarchy-map.md:168-186` |
| `item` module 20 `item-surfaces` | owns the odds panel that will load assurance lines; T39 only deletes the free checkbox | no task here |

## Tuning publishes this program owns (parent §5 rows)

Every row: `gk-core/tools/tuning/publish.py` (`--add-key` for new keys), `v{n}` kept on disk, host reader
(`gk-core/src/FusionRpg.Server/Program.cs`; the injector loads none of these) switched in the same commit.

| File | Revision | Task | Parent §5 row |
|---|---|---|---|
| `materials` | `v{n+1}` — `operations.repair` | T23 | ⚠ **not in the ledger** (its row is `T32 → T34 → SSH`); lands whenever T23 does, later publishers rebase |
| `materials` | `v{n+1}` — species-cost multiplier, threshold, per-verb override `{}` | T32 | `materials` — first |
| `materials` | `v{n+1}` — trophy `operations` legs + D5 exchange (one publish) | T34d | `materials` — second, then `SSH socket-pricing` |
| `materials` | `v{n+1}` — upgrade cost row, only if added | T37 | after T34d (map § Tuning revisions) |
| `deployment-hierarchy` | `v3` — craft wear | T24 if the table changes, else T49 | `deployment-hierarchy` v3 (T24) |
| `creature-yield` | `v1` created — rung → shard map | T31 | last row |
| `species-material-run` | `v1` created — `perSpecies` 2, `perFamily` 8 | T34 | last row |
| `craft-assurance` | `v1` created (T41) → `v2` (T49) | T41, T49 | last row |
| `enhancement` | `v2`, only if T49 moves the bands | T49 | ⚠ **not in the ledger** (the map says "none from this map") — flagged |

## Defaults shipped behind (no gates)

- **Free ward:** refused now (T39); paid protection arrives with T42. No player loses anything — level
  loss starts at `+17`, unreachable by shipped item levels.
- **Excluded species (ask 4):** T34c's trophy **content** is not authored until `CreatureAdmission`
  refuses them; everything else ships.
- **Trophy spend verbs:** `Elevate` and `Temper` only (spec Open question 2's recommendation).
- **Per-verb threshold override:** ships `{}` — every verb at the default rung.
- **`craftWearPerAttemptMilli` 50, first `assureBonusMilli`/`repairCoverageBonusMilli`, first boss
  weights:** shipped values, explicitly not balance, until T49.
- **Ask-first rows** (`Trophy`, `Assurance`, §7.6, ninth `source_kind`, planner ownership) are filed
  in the owning maps in the same commit as the change, citing the owner ruling that answers them
  (R-SC1/R9, R-G1, the plan approval) — filing is recorded, not waited on.

## Task list — index

Full per-task detail is in [species-gear-chain-todo.md](species-gear-chain-todo.md).

- **Wave 0:** T39 free-ward fix · T47 creature-seed ask 4 · T48 stale comment
- **Phase 1** ✅ — T1–T15, T35–T36
- **Phase 2** — ✅ T16–T21, T18b · open T22, T23, T24, T25, T26
- **Phase 3** — T27–T28 `set-species-binding` · T29–T31 `creature-drop-tables` · T37–T38 `item-upgrade-tree`
- **Phase 4** — T32 `species-cost-shaping`
- **Phase 5** — T33, T34, T34b, T34c, T34d `species-materials` · T30b `creature-drop-tables`
- **Phase 6** — T40–T46, T49 `craft-assurance`

## Revision-1–3 dependency graph (history)

```
Phase 1 — foundations, 17 tasks, 3 sub-checkpoints
  1a: tier-propagation-contract(a,b) · threat-band-fill · socket-allowance-by-kind
  1b: CreatureAdmission · wave-species-roll · wild-species-spawn · gem-tier(a,b)
  1c: craft-risk-ladder(Stage1) · durability-slice(a) · enhance-track-wiring(a,b)
      · craft-executor-completion(a,b) · requirement-profiles-pullforward(a,b)

Phase 2 — 12 tasks
  ladder-consistency-repair(a,b) ← tier-propagation-contract
  species-magnitude-synth ← threat-band-fill
  wild-species-spawn HP wiring ← wild-species-spawn, species-magnitude-synth
  delve-species-wiring(a,b) ← threat-band-fill, CreatureAdmission
  socket-combat-wiring(a,b) ← gem-tier(a)
  durability-slice(b) ← durability-slice(a)
  craft-risk-ladder(Stage2-3) ← craft-risk-ladder(Stage1), durability-slice(a)
  rarity-promotion(a,b) ← craft-risk-ladder(Stage1), durability-slice(b)

Phase 3 — 7 tasks
  set-species-binding(a,b) ← ladder-consistency-repair
  creature-drop-tables(a,b,c) ← species-magnitude-synth + one selection module
  item-upgrade-tree(a,b) ← rarity-promotion, craft-risk-ladder(Stage2-3), requirement-profiles-pullforward

Phase 4 — 1 task
  species-cost-shaping ← set-species-binding

Phase 5 — 2 tasks  (superseded by revision 4's Phase 5: six tasks)
  species-materials(a,b) ← species-cost-shaping, creature-drop-tables
```

## Deferred

None — see the todo's § Deferred (content gaps named there; arm 2 is `SSH combo-bind`'s).

## Risks and coordination (not gates)

| Risk | Impact | Mitigation |
|---|---|---|
| T2 and T3 both edit `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py` | Low — different fields, but same file | Land T2 first within sub-checkpoint 1a; rebase T3 if both are in flight |
| Durability-slice columns (T11) and `craft_potential` columns (T10) both `ALTER TABLE effect_instance` | Low — idempotent additive migrations | Both in sub-checkpoint 1c; review together at that checkpoint |
| Building a slice of `deployment-hierarchy` module 7 inside this initiative | Medium — a second program's territory | Filed back into `deployment-hierarchy-map.md`; scope is explicitly bounded (no field touch-up, no death-drop decay) |
| `species-rank` (unlisted 19th `creature-seed` module) overlaps T3/T6 | Low — a display axis, not a build blocker | Filed in `creature-seed-map.md`'s asks table already |
| ~~`creature-yield.v1.json` created independently by T30 and T34~~ | — | **Resolved 2026-09-18:** one owner — T31 creates it (the rung → shard map); `species-materials` reads nothing from it |
| Golden fixture drift from T6 (wave roll) or T3 (threatBand rewrite) | Medium if it happens | Each spec states which goldens should be unaffected; a moved golden is investigated, never auto-re-blessed |
| Building a slice of `item` module 23 inside this initiative | Medium — a second program's territory, same shape as the durability slice | Filed back into `item-map.md`; scope is explicitly bounded to the spec's own v1 (no activation, no resource charging, no set reconciliation) |
| The free ward stays exploitable until T39 lands | Low today (level loss starts at `+17`, unreachable), but it is the exact shape R-G1 forbids | T39 is Wave 0 and the parent lane C's first task |
| Excluded species kill → trophy id absent → loot refused | High once T34c's content ships | T34c's content waits on T47 (`creature-seed` ask 4); only the content waits |
| Trophy registry drifts behind the species corpus | Medium — new species refuse their loot | T34's `--check` in CI, like every other generated tree |
| `ci.yml` edited by T34 and by `TVB` | Low | Rebase; TVB owns the file's structure |
| D5 exchange vs R-SC2's *"never a fallback currency"* | Medium — a souls→trophy exchange could read as the price R-SC2 warned against | D5 is recorded as settled and undisputed (`tier-system-ideal.md`); T34d writes the exchange's shape into the spec's D5 row and it is reviewed at Checkpoint 5 before code — surfaced, not a gate |
| Two `materials` / one `enhancement` revisions not in the parent §5 ledger (T23, T37; T49's bands) | Low — `publish.py` takes `n` from disk | Flagged to the parent; later publishers rebase |
| `CostClassMatrix.cs` / `MaterialCatalog.cs` touched by T33, T40, T43, T44 | Low | Land in sequence; each adds one arm |

## Open questions — full sweep, sealed 2026-09-13

Every open question across all 19 specs was reviewed in one sitting (see § Round-3 decisions for the
8 that changed something). **Everything not listed below is sealed as its spec's own stated
recommendation** — each spec already carries that recommendation as its adopted design, so there is
nothing left to override unless you want to revisit a specific one by name.

**Genuinely still open — balance/content values with no number yet, none blocking, each resolved
inside its own task:**

1. `RaiseResolver.SpeciesFor`'s own fix (a second, ~6-species-reachable selection site) — ships as
   its own follow-up task, not folded into T7. *(Not yet its own task — file when picked up.)*
2. ~~`species-materials`' per-species material count (1–2, or 0 for general creatures) — T34.~~
   ✅ **Ruled.** R-SC1 (2026-09-17) then **R9** (2026-09-18): **2 per species, 8 per family, no general
   layer** (and general *creatures* are not zeroed — R-S1), as seedsmith generation parameters
   `perSpecies`/`perFamily` in `gk-core/data/tuning/species-material-run.v1.json`; `perGeneral` is removed, not
   0. **R22** closed the multi-family question. Built by T34–T34d.
3. `species-cost-shaping`'s threshold rung value — T32. *(The shape is ruled — R-SC2: one default plus
   an explicit per-verb override map that ships empty; only the rung value is balance data.)*
4. Durability-slice's repair cost curve (`repairRatioMilli`) — T23.
4a. `craft-assurance`'s `assureBonusMilli` / `repairCoverageBonusMilli` and the boss drop weights —
    first values in T41/T45, set with the craft-wear table and the bands in **one** pass (T49, R-G1).
5. `gem-tier`'s upcycle drain (`upcycleInputPerOutput: 3`, unchanged unless play says otherwise) —
   T9.
6. `gem-tier`'s `rung` input for `forge-gem` pricing (the output tier feeds it) — T9, one line of
   tuning prose.
7. `gem-tier`'s ladder width (`[2..4]` today; whether `gemgen` ever authors t1/t5) — not this
   initiative's call; named so it is not silently assumed settled.
8. `enhance-track-wiring`'s per-ordinal milestone tier ladder (starting shallow) — T13.
9. `item-upgrade-tree`'s potential consumption on upgrade, and whether the successor inherits the
   used fraction — T37.
10. `rarity-promotion`'s potential consumption on promotion vs. a plain temper — T26.

Nothing on this list blocks a phase. Each is a tuning value or a small follow-up task, decided by
whoever picks up the owning task, using the recommendation already in that task's spec unless you
say otherwise.

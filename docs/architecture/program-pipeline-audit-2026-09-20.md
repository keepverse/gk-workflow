# Program pipeline audit — 2026-09-20

**Question:** which features did we specify and then forget — never plan, never build, or build without
the documents noticing — and **why did each one stop?**

**Method.** `gk-core/scripts/audit-program-pipeline.py` lists the gaps in the ideal → map → spec → plan → todo
chain. Each candidate was then checked by hand:

- the spec's new files and type names against `src/`, `tools/`, `tests/` and `web/`;
- the owning todo's task ids (a spec's module id is often not the word the plan uses);
- the commit history of the code and of the documents;
- `tasks/sessions/*.json`;
- every mention of the program in the `summoner-convergence` programs' maps, specs and todos.

**Revision 3 (agent drift audit, same day).** Eight read-only audit lanes deepened this file; their
evidence is in [../research/backlog-clean-up/](../research/backlog-clean-up/README.md), and the work
they found is scheduled in [backlog-clean-up-map.md](backlog-clean-up-map.md). They corrected two claims
below, and each is marked in place:

- **§3.1:** `LawnBasicAttackFeature.DefaultEnabled` is **`true`** since `9f985313` (2026-09-16), not
  false.
- **§3.6:** the six `roster-balance` specs already carry a SUPERSEDED banner.

**Revision 2.** The first pass of this file (commit `d5ed561b`) listed two modules as "not built" that
are built. It also read four todos as stalled when their headers record completion. Both errors are
corrected below; §6 shows what caused them.

---

## 1. The boundary that explains most of this

`summoner-convergence` (plan 2026-09-18, handoff the same day) is the one program being built now. Its
scope is closed: **11 programs**, listed in `tasks/summoner-convergence-plan.md` §1.

`action` · `action-skill-tiers` · `action-enrich` · `solid-enforcement` (+ `save-identity`) ·
`species-progression` · `empire-progression` · `build-preset` · `species-gear-chain` ·
`strain-splice-host` · `notification-ssot` · `test-verification-boundary`

It runs in four lanes (A actions · B identity & progression · C items · D infrastructure) under two
rules that matter here:

- **R28 (full autonomy)** removes every *owner-review / owner-run / ask-first* gate — **only inside
  those 11 programs.** Any program outside keeps its human gates.
- **Nothing outside §1 is scheduled.** The parent plan orders only its own sub-plans. A program the
  2026-09-18 spec round did not touch has no lane, no builder and no checkpoint.

Every forgotten item below sits **outside that boundary**. Most of them stop for one of four reasons,
named in §2.

## 2. Why they stopped — four causes

| Cause | What happened | Programs |
|---|---|---|
| **C1. Specced just before the convergence round, then left out of it** | Written 2026-09-16. Solid-remediation ran on 2026-09-17, and the convergence spec round on 2026-09-18 took every builder. The round chose its 11 programs from the rulings R1–R28; these were not among them. Their maps name plan files that were never written. | `lawn-playable`, `lawn-tuning-profile`, `battle-derived-wire`, `combat-math-dedup` |
| **C2. A human gate that no one cleared** | The task waits on "⛔ owner review" or "owner live proof". R28 lifted such gates only for convergence. **47 open owner-gated tasks** remain in non-convergence todos (base-defense 10, item 9, backlog-clear 8, story-scene 3, data-test-substrate 3, …). | `backlog-clear` → `aura-binding-producer`, plus the rest of that sequence |
| **C3. Built in slices by other programs, so the owning plan was never written** | Three different programs each built the slice they needed. Each pointed at "that program's own eventual plan", which never came. | `deployment-hierarchy` |
| **C4. Absorbed without a pointer** | A later program did the work but never cited the earlier plan, so the earlier plan still reads "unbuilt". | `battle-derived-wire` and `combat-math-dedup` (by `solid-remediation`), the `roster-balance` original target (by its own revision) |

## 3. Per program: what is true now, and why

### 3.1 `lawn-playable` — specced, not planned, not built (C1)

- **State.** Six specs, map 2026-09-16. `tasks/lawn-playable-plan.md` / `-todo.md` are named by the map and
  do not exist. None of its artefacts exist: `ActorSnapshotCache`, `ActorLivenessRevision`,
  `lawn-perf-budget.v1.json` (new), `lawn-drain.v1.json` (new), `SummonPoolPlantabilityTests`.
- **Why it matters.** ~~The RPG combat loop on the lawn ships **off** (`DefaultEnabled = false`), at
  26.7–37% of the frame pipeline against a 6% ceiling.~~ **Corrected (revision 3):** it ships **on**.
  `LawnBasicAttackFeature.cs:56`, `DefaultEnabled = true`, has been in place since `9f985313`
  (2026-09-16). An owner-directed perf pass (`83054adb`, `5a3e941c`, `b48f0e7e`) brought
  `effect.onCapture` to 3.46%, which satisfied the **cost** gate. The **scale** gate
  (`lawn-scale-live-proof`, M2 stamina) never ran, and the ceiling is still not a tunable. So
  `hub-snapshot-cache` and `rider-hit-cost` are superseded, and `rider-default-on` is partial. The
  owner's framing still holds: *"wire our rpg to pvz and make it playable before we ship new feature."*
- **Why it stopped.** Its four commits all fall on 2026-09-16. The convergence round started two days
  later and did not include it. No convergence document names it.
- **Collision to resolve before anyone builds.** Its module `actor-liveness-refresh` owns the
  server → injector signal for `PUT /api/players/current` (defect P4: *"a player switch never reaches the
  injector"*). Convergence builds the same signal as **`SP6.6`**: *"one generic server→injector notice on
  `PUT /api/players/current`"* (parent plan §3). `solid-enforcement` and `notification-ssot` are told to
  reuse it. Neither side cites the other. If `lawn-playable` is later built as specced, the repo gets two
  invalidation channels for one event. The ActorHub/SOLID rule forbids that.
  **Resolution:** `actor-liveness-refresh` should extend `SP6.6`'s notice instead of adding its own. Its
  other half, the per-actor revision the cache keys on, stays its own.

### 3.2 `lawn-tuning-profile` — specced, not planned, not built (C1)

- **State.** Seven specs, plus two modules the map lists but never specced (`lawn-combat-baseline`,
  `zombie-power-source`). There is no plan pair.
- **Correction to the first pass.** `mode-profile` is **not** built; that pass matched a tool path
  (`gk-core/tools/tuning/publish.py`) as the new file. `data/tuning/mode-profiles.v1.json` does not exist.
- **The one thing that did ship.** `2b9fb2c2` (2026-09-16) removed the injector's attack write into PvZ
  on an owner ruling. That narrowed `base-relative-read` to its hp/armour half.
- **Why it stopped.** Same window as `lawn-playable`. After 2026-09-16 the program only gained *rulings*,
  seven doc commits through 2026-09-18 (R-LT1 armour retracted, `summonLevel` is zombie Θ). Its map says
  "Open questions: none", so the specs are buildable, but no one owns building them.
- **Convergence leans on it without scheduling it.** `species-progression-map.md` §5 names
  `lawn-tuning-profile` as the owner of **Θ freshness (L5) and lawn zombie Θ**, and of the general-lawn
  carrier for layer-1a magnitudes (`species-flavour-lawn`). `action-enrich-map.md` and
  `empire-progression/spec-ai-empire-species.md` cite it too. So convergence delegates work to a
  program that has no plan.

### 3.3 `aura-skill/aura-binding-producer` — planned, blocked at a human gate (C2)

- **Correction.** It *is* planned, as **`backlog-clear` BP1–BP4** (Phase 1). It is not missing from every
  todo.
- **Why it stopped.** BP1 reads "spec-first — ⛔ owner review before BP2". The spec was written
  2026-08-31 with the header "⛔ Owner review required before BP2". No review followed, so BP2–BP4
  never started. `AuraBindingPlan` and `AuraBindingProducer` do not exist.
- **The wider effect.** `backlog-clear` (2026-08-31) is a *running order* across programs, and Phase 1
  is its first phase. With Phase 1 blocked, nothing after it ran either:
  - aura containers (AU1–AU2);
  - kernel drive B27;
  - Zomboss momentum;
  - game-gui dead-code deletion (GG1);
  - loam L44–L50 (Sustain/Build/Ward UI);
  - combat-unification waves E1–E3;
  - battle-timeline Phases 4–5 (T6–T8, T10, T11);
  - the actor-hud backlog;
  - 49 seedsmith items.

  Its todo also says "git hands-off — never commit", a rule from before the 2026-09-19 retirement.
- **The aura-skill map is stale in the other direction.** It still reads "Pending owner approval. No
  build authorized". Meanwhile its todo is 78/78 ticked, and `AuraMagnitude`, `AuraContentCatalog`,
  `aura.v1.json`, `DerivedContributionBag` and `CommanderAllocationSource` exist.

### 3.4 `deployment-hierarchy` — built in slices, never planned (C3)

- **State.** Map approved 2026-09-13. The map names `tasks/deployment-hierarchy-plan.md` / `-todo.md`;
  neither exists.
- **Who built what:**
  - `corpse-cache` came from `1b6fd8de` "feat(empire): scoped inventory, corpse-cache, relic, wonder
    engine" (2026-09-16), and `29459f9e` added its phase gate.
  - `item-durability-repair` (module 7) was pulled forward into `species-gear-chain` T10/T11, then
    T23/T24.
  - `cache-decay-void` and `cache-field-access` have every new file present.
- **Why the plan never came.** `species-gear-chain-plan.md` built module 7 "exactly to the spec" and
  deferred the rest to "that program's own eventual plan". The other builders did the same. Nobody owned
  the remainder.
- **Unbuilt, and now depended on.** `injury-tiers`: `WoundGrading`, `WoundPolicy` and `wound.v1.json`
  do not exist. Convergence already depends on it. `empire-progression/spec-legion-commander.md` ships a
  fallback "until `injury-tiers` lands" (a fallen commander member is set `Recovering`).
  `notification-ssot-map.md` names it as a future gate feeder.

### 3.5 `battle-derived-wire` and `combat-math-dedup` — audits absorbed without a pointer (C1 + C4)

- **State.** Both were written 2026-09-16 from two audits. Their todos read 0/107 and 0/64, and their
  headers read "unbuilt" and "ready for owner review".
- **What actually happened.** `solid-remediation` (plan 2026-09-17, 96 done / 1 open) did much of
  battle-derived-wire's Phase 1 and Phase 4:
  - `OverlayCombatMath` on battle, with reflect pinned to it;
  - battle's trigger raises (`OnDamageTaken`, `OnSpawn`, `OnDeath`);
  - `setup.ActiveAuras` traced as the only production writer.

  It touches parts of combat-math-dedup too (`StrikeMixture`). Neither audit is cited by name in
  `solid-remediation-todo.md`.
- **What is likely still open.**
  - battle-derived-wire Phase 3: delve and siege setups carrying real `HubInputs` (W9), and a
    `Draughts` producer (W8);
  - `Host.AddDerivedContribution` has no production invoker (W6);
  - combat-math-dedup D4 (siege kill estimate), D6/D9 (pool regen) and D7/D8 (CombatSim → Core).

  None of those names appears in any open plan.
- **Next step.** Reconcile each plan task against `solid-remediation`'s commits. Tick what landed with a
  pointer, and move the rest into a live plan. Convergence lane D (`solid-enforcement`) is the nearest
  owner.

### 3.6 `roster-balance` — superseded specs left unmarked (C4)

- On 2026-09-06 the map was revised: *"the original target was wrong, found before any module was built."*
- The replacement modules `usage-stats` and `usage-direction` shipped.
- ~~Six specs from the old target still have no status line.~~ **Corrected (revision 3):** all six
  (`balance-policy`, `coverage-index`, `distribution-stats`, `pipeline-direction`, `plan-apply`,
  `rebalance-plan`) already open with `> ⛔ **SUPERSEDED 2026-09-06.**`. This file's scan missed the
  blockquote form of the header.
- **Fix:** none needed. The real leftover is the creature-species roster findings (grid occupancy
  65/252, non-monotone rarity) that were handed to `creature-seed` and never filed there
  (`backlog-clean-up` module `creature-remainders`).

### 3.7 `creature-progression` — partially built, remainder unowned

- Its header (2026-09-08) reads "partially implemented". The source grammar, general-species gate,
  dedicated isolation and replay identity have landed.
- Open: full provenance diagnostics, and the lawn consumer's atomic terminal settlement, which is handed
  to `creature-lawn-deploy`.
- The todo shows 0 ticked because the ticks were never recorded, not because nothing ran.
- Overlap check owed: `species-progression` (convergence) reworks the same progression sources.

### 3.8 `action-distribution-gaps` — tooling done, runs are the owner's

- `action-skill-tiers-map.md` §3 records its tooling as built (`bdd91b68`, `d49d2640`).
- The two remaining real runs are model-calling corpus runs. R28 explicitly leaves a full corpus run
  **outside** the orchestrator's authority.
- It waits on the owner by design. That is not drift.

## 4. Not drift (the first pass got these wrong)

| Item | First pass said | Actually |
|---|---|---|
| `action/duration-resolver` (A14) | Unplanned, unbuilt | `action-todo.md` Phase 8 **T28 done 2026-08-28**. `IDurationResolver`, `BattleDurationResolver` and `DurationResolverRegistry` exist in `gk-core/src/FusionRpg.Core/Actions/Duration/`. |
| `battle/readiness-model` (T3) | Unbuilt | `battle-timeline-todo.md` **B9 T3a closed 2026-08-28**. It exists as `Battle/Timeline/TurnReadiness.cs` + `ReadinessDriver.cs`. The spec's strategy class names were never used. |
| `rift-gate` | Todo 0/134, stale | Todo header: **"Build complete 2026-09-15: all 13 tasks gated PASS."** The boxes were never ticked; the header is authoritative. |
| `onboarding-rift` | Todo 0/110 | Todo header records its implementation status (2026-09-14). The same pattern applies. |
| `debug-mcp`, `game-control` | Stalled 3/60, 6/31 | Built. `gk-fusion/tools/debug-mcp/server.py` registers `debug_click`, `debug_cursor`, `debug_inspect`, … and the server runs in this session. The todos were never ticked. |
| `live-probe-screenshot` | Stalled 11/22 | Session `lawn-screenshot-20260914` is **merged**. The todo links into a worktree path, so the ticks stayed on the branch. |

Also waiting for their plan, and not drift (approved 2026-09-19): the ten trade-network sub-programs,
`empire-seed`, `legion-build`, `world-continuity`, `narrative-seed` and `npc-story-events`. One thing to
fix before they are planned: the trade-network maps disagree on plan file names (`fleet-plan` vs
`trade-network-fleet-plan`).

The 18 ideals the tool flagged were all absorbed by named programs. The first pass of this file
tabulated them, and that table still holds. `creature-scope` and `creature-mechanism-gaps` still need a
status line.

## 5. What to do — in order, and where each lands relative to convergence

| # | Action | Relation to convergence |
|---|---|---|
| 1 | **Settle the `PUT /api/players/current` signal ownership** (§3.1): `lawn-playable` extends `SP6.6`, never a second channel. Add one line to both maps. | A document edit before either side builds. `SP6.6` is lane B and still open. |
| 2 | **Plan `lawn-playable` and `lawn-tuning-profile` as one program** (they share the lawn surface and a cross-gate at `rider-default-on`). | New work outside the 11. Either add a **lane E — lawn** to the parent plan, or run it as its own program after lane B's `SP6.6`. `lawn-tuning-profile` also owns what `species-progression` §5 delegates (Θ freshness L5). |
| 3 | **Write the `deployment-hierarchy` plan pair**: record the shipped slices, and plan `injury-tiers` + `CacheRetrieval`. | `empire-progression` (lane B) ships behind its absence. It is a natural follow-on to lane C (`species-gear-chain` already owns module 7). |
| 4 | **Clear or re-home the `backlog-clear` gate**: either review `aura-binding-producer` or pass it under an R28-style agent review. Then split the sequence back into its programs. | Outside convergence. R28 does not reach it unless the owner extends it. |
| 5 | **Reconcile `battle-derived-wire` / `combat-math-dedup` against `solid-remediation`**. Tick with pointers, then carry W6/W8/W9 and D4/D6–D9 into a live plan. | Nearest owner: lane D (`solid-enforcement`). |
| 6 | **Header-only fixes:** the `aura-skill` map; the six `roster-balance` specs → SUPERSEDED; tick or close the `rift-gate`, `onboarding-rift`, `debug-mcp`, `game-control`, `live-probe-screenshot` and `creature-progression` todos. | No code. |

Item 4 is the one decision only the owner can make: whether R28's no-human-gate autonomy extends beyond
the convergence programs. §2 C2 counts the 47 tasks it would release.

## 6. Why the first pass was wrong, and what the tool now does

- **Spec names are not code names.** A spec's proposed class names (`SpeedScaledReadiness`) and the
  names actually built (`TurnReadiness`) often differ. A module id (`duration-resolver`) and the plan's
  task id (`A14`/`T28`) differ too. A name miss is a lead, not a verdict. Check the owning todo's task
  ids and the map's "built" notes before calling anything unbuilt.
- **Checkboxes are not the status.** Several programs record completion in the todo header, a ledger
  (`summoner-convergence-*ledger.jsonl`) or a merged session record, and never tick the boxes. The
  cut-paperwork ruling of 2026-09-19 makes this the norm.
- **Tool change.** The `map-plan-missing` check was added in `d5ed561b`. It is the check that surfaced
  `deployment-hierarchy`, `lawn-playable` and `lawn-tuning-profile`, the three real C1/C3 cases. The
  tool still reports document-chain gaps only; §3 needed the manual method above.

```powershell
python gk-core/scripts/audit-program-pipeline.py --only map-plan-missing --only spec-no-plan
```

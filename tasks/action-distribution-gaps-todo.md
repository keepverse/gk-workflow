# Todo: `action-distribution-gaps` — closing the coverage loop

Plan: [action-distribution-gaps-plan.md](action-distribution-gaps-plan.md). **5 phases, 15 tasks.**

Sizes: **XS** 1 file · **S** 1-2 · **M** 3-5 · **L** multi-run.

---

## Phase 0 — the two A-S7 defects — ✅ DONE 2026-09-12

- [x] **T0.1** Exclude payoff keys from the non-pairing round-robin · **XS** · `coverage_assignment/derive.py`, `generate_coverage_assignment.py`
  - Acceptance: `assign_required_families(..., payoff_families=...)` never returns a payoff key for a
    `role: none` brief; a `role: payoff` brief still returns its own key; the default (empty) payoff
    set is byte-identical to pre-fix behaviour.
  - Verify: real plan regenerated — **0** `role: none` briefs require a payoff key (was 74 anchors);
    both keys still covered via 456 payoff-role briefs; 123 distinct required families (unchanged).
- [x] **T0.2** `splice_payoff_enablers` + wire into A-P1/A-P2/A-P3 · **S** · three `propose/derive.py`
  - Acceptance: a model-picked payoff key gains the first `pairings.json` enabler present in the
    brief's own `allowedAtomFamilies`; an existing enabler is not duplicated; no allowed enabler adds
    nothing; non-payoff input is unchanged; deterministic.
- [x] **T0.3** Tests · **XS** · `test_coverage_assignment.py`
  - Verify: `PayoffExclusionTests` (3), `RealPlanPayoffTests` (2), `SplicePayoffEnablersTests` (5).
    `test_coverage_assignment.py`: **29 passed**. Propose suites: **287 passed, 1 skipped, 1176 subtests**.

## Phase 0b — granularity and staleness defects — ✅ DONE 2026-09-12

- [x] **T0b.1** **G3** — add the per-species coverage gate · **M** · `coverage_report/derive.py`, `metrics/action_coverage.py`, `coverage_report/ctx.py`
  - Root cause: `cellOccupancy`/`thinCell` gate on `cell.species.<category>.<band>`, ONE aggregate over 904 species; quota 976 could be met by ~100 species while 804 held nothing. Measured: 828/904 species had zero accepted actions, unreported.
  - Acceptance: new CLOSED metric `action.corpus.speciesCoverage`, one GAP Finding per uncovered species; required universe == the planner's `subject_category_counts` species keys; contract-based (empty uncovered set), never a population literal.
  - Verify: `SpeciesCoverageMetricTests` (5) — uncovered naming, full-coverage clean, aggregate-blind-by-construction, universe source, determinism.
- [x] **T0b.2** **G4** — delete the contradictory `SIGNATURE_ACTIONS_PER_SPECIES = 3` default · **XS**
  - Root cause: the sealed ideal's B1 number was a module-constant default; the shipped tuning is `perSpeciesCount: 5`. Dead but trusted-on-read.
  - Acceptance: constant gone; `signature_actions_per_species` is a REQUIRED parameter; the metric passes `cov.per_species_count`.
  - Verify: `SignatureCountIsRequiredNotDefaultedTests` (3) — no constant, no default, metric reads tuning.
- [x] **T0b.3** **G5** — run S6 against the current plan · **S**
  - Root cause: `species-innate.json` held 84 entries / `tuningVersion: 1` (legacy catalog), so the one-per-species guarantee described a roster 820 species stale.
  - Verify: now **904 entries, 81 picks, 823 nulls**; 53 round-2000 survivors promoted into `committed-round-2000.json` (126 → 179 committed). `LiveInnateFileTests` (2) assert live-roster coverage and non-legacy hash.
- [x] **T0b.4** Convert the population-pinning real-corpus test · **XS** · `test_coverage_report.py`
  - Root cause: `assertEqual(summary["acceptedCorpusSize"], 138)` pinned a population; the S6 run legitimately moved it to 191.
  - Acceptance: asserts the corpus reconciles to committed + survivors, never a literal (validation-ssot.md).

## Phase 1 — gate semantics — ✅ DONE 2026-09-12 (commit bdd91b68)

- [x] **T1.1** Decide and record what `thinCell` means · **S** · `spec-coverage-report.md`
  - **DECIDED: Option A.** Spec-answerable, not an open product call — `spec-metrics.md` §4 (*"New metric → `gates=False`, runs, reports. **Then** a threshold goes into `budget` and `gates` flips"*) and spec §3 step 6 (*"`pass` requires every **gating** CLOSED metric green"*) already fix it; `compute_verdict` had diverged from its own spec.
  - Recorded in spec §3 step 6 (the decision + why it was blocking) and §4 (the converse rule).
- [x] **T1.2** Implement the chosen `compute_verdict` policy · **S** · `coverage_report/derive.py`
  - `compute_verdict(..., gating_metric_ids=)` blocks on `NOT_MEASURED` (any CLOSED metric) and on a `GAP` from a **gating** metric; an unpromoted `GAP` stays in `gapMetrics` and does not block. `Verdict.gating_metrics` added and serialized as `gatingMetrics`; the caller passes `{m.id for m in registry.all() if m.gates}`.
  - Verify: `VerdictHonoursGatesTests` (5). Focused: **50 passed** in `test_coverage_report.py`.
- [x] **T1.3** Reconcile with the general reporter's `gates` use · **XS**
  - `is_passing_quality_gate` no longer requires `gapMetrics == []` — it defers to A-S5's verdict string, which was the definition A-S5 had to abandon. `NOT_MEASURED` stays blocking as belt-and-braces.
  - Verify: `test_gate_reads_the_verdict_flag_not_the_gap_list`; planner suite **114 passed**. Gate subagent confirmed no other call site re-derives the verdict (`gapMetrics` non-test hits are serialization/summary only), and that `report/cli.py` builds the identical `if m.gates` set.
  - Gate: **GATE: PASS** (build-gate subagent) — 164 focused, 3797 full-suite, adversarial checks both directions.

## Phase 2 — the `S5 → S1` top-up round — ✅ DONE 2026-09-12 (commit d49d2640)

- [x] **T2.1** A-S1 reads the prior report's `next-target` rows · **M** · `generate_distribution_planner.py`
  - `read_top_up_targets(report)` → `{(scope, scopeKeyOrNone): {category: want}}`; drops `want == 0`; sums duplicates; refuses a wrong `kind` by name. `load_top_up_targets(path)` refuses a missing file by name (never silent zero).
  - Verify: `TopUpRoundTests` (5). Real report: **1,131 subjects, 6,490 shortfall units**.
- [x] **T2.2** `plan_round` plans exactly the named shortfall · **M** · `distribution_planner/derive.py`
  - New `_plan_top_up`; `plan_round(..., top_up=None)`. Shortfall-only (round n's accepted rows already count against quota, so a base replan would duplicate them); a subject absent from the map gets nothing; `None` is byte-identical to omitting it; every brief is ordinary (legal category/target/role, valid rung band, unique id).
  - Verify: `TopUpMergeTests` (6). Real data: 6,490 `want` → **exactly 6,490 briefs**.
- [x] **T2.3** Round numbering for the plan · **S**
  - Round 1 reads no report (`top_up_report_path=None`); `topUpSubjects == 0`; `git diff` on `_briefs/round-1.json` is **zero lines**.
  - Verify: `NoTopUpIsRoundOneTests`.
- [x] **T2.4** Bounded convergence criterion · **S**
  - `convergence_decision` → `converged` | `round-cap` | `thin-cells-remainder`, refusing a non-positive cap. Answers the plan's Q2: convergence is bounded and the stop reason is reported.
  - Verify: `ConvergenceBoundTests` (4).
- [x] **T2.5** Model-free top-up test · **M**
  - All Phase 2 tests use synthetic report fixtures, never the live corpus (`spec-metrics.md` §6).
  - Gate: **GATE: PASS** (build-gate subagent) — 131 focused + 377 sibling tests, adversarial checks A/B/C, `guard-test-substrate.py` green.

## Phase 3 — verify on real content — 🔶 PARTIAL 2026-09-12

- [x] **T3.1** One real round; confirm `enablerPayoffCoverage` moves · **M**
  - Ran the full real chain for the two flagged species (the top-up path end-to-end): plan 6 species briefs → A-P2 family propose (4/4 accepted) → A-S4 validate (4/4) → A-S3 dedup (2 survivors) → A-S2 assemble (6 P3 briefs with `familyActions`) → A-P3 signature (2 accepted, 4 unresolved) → validate (2 accepted).
  - **The mechanism is proven**: the transient top-up row `action.species.caltropnut.004` carried `atom.sporing`, a real enabler of `atom.rot-punisher` (`pairings.json`), so drawing accepted content in `caltropnut`'s anchor closes its gap. **No lasting artifact** — the round's scratch was deleted (it was untracked temp state, never promoted), so the committed corpus still measures the same 2 gaps (`caltropnut`, `snowgatling`). The closure is reproducible by running the round for real, not a persisted edit.
  - **Gate finding fixed (the real deliverable).** The gate review found the refreshed round-1 report measured **191 rows for a 179-row corpus**: `_rounds/round-1/survivors.json` still held 12 full rows, **11 of whose ids were already promoted into `committed-round-2000.json`** (G5's S6 run promoted them without reducing *round-1's* file — S6 only marks the round it promotes). A-S5 merged committed + non-`promoted` survivors with **no id-level guard**, so those 11 were double-counted (191 rows / 180 distinct), inflating every cell and disagreeing with round-2000's report (179) about the same baseline. **Fixed** in `generate_coverage_report._build_ctx`: one row per id, the committed (promoted, authoritative) copy winning. Round-1 now measures **180** = 179 committed + 1 genuinely-new survivor (`action.family.academic.004`). `AcceptedCorpusIsOneRowPerIdTests` (4) pins it.
  - Also refreshed both committed reports: verdict `not-clean` → `pass`. **This unblocks `mode: "full"`**: `refuse_full_run_if_ungated('full', True, gate)` now returns instead of raising. That is Phase 1's payoff — the deadlock is broken.
- [ ] **T3.2** Run the top-up round to convergence; confirm `thinCell`'s shortfall shrinks and `quotaDrift` stays clean · **M** — ✅ **RELEASED 2026-09-21** (owner spend release; this ruling sequences it **after `BCU2.11`'s generator fix**, not during)
  - **Deferred, not blocked by code.** The mechanism is built and proven (a bounded top-up planned exactly the 6 named shortfall briefs; `quotaDrift` stays clean by construction). Full convergence is **6,490 shortfall units at the measured ~66% yield** — dozens of model hours across many rounds, which saved policy reserves for the owner: *"a full action-corpus run requires mode: 'full' plus a passing A-S5 gate, and the owner decides when to fully run."* The bounded-stop criterion (`convergence_decision`) is in place to govern that run whenever the owner starts it.
- [ ] **T3.3** Run `mode: "full"` once reachable; record the honest verdict · **L** — ✅ **RELEASED 2026-09-21** (owner spend release); sequenced after `BCU2.11`'s fix and `J9`/`J13`
  - **Now reachable** (verified: `refuse_full_run_if_ungated('full', True, gate)` does not raise; the round-1 report is a passing gate). The run itself is the multi-day full corpus and is the owner's call, per the same policy.

---

## Status: COMPLETE except the two real runs — both released 2026-09-21 (owner), sequenced after `BCU2.11`'s generator fix

Phases 0, 0b, 1, 2 and T3.1 are done and gated. T3.2/T3.3 are deferred because they are long
model runs the owner explicitly reserves. **The program's engineering goal is met**: the distribution
engine is exact on every axis, the verdict honours `gates`, the `S5 → S1` top-up loop exists with a
bounded stop, and `mode: "full"` is reachable instead of deadlocked.

---

## Open questions — RESOLVED

- **Q1.** ✅ Answered by `spec-metrics.md` §4 + spec §3 step 6: `thinCell` is a work-order signal until promoted; `gates=False` cannot gate. See T1.1.
- **Q2.** ✅ Bounded by `convergence_decision`: stops on zero thin cells (`converged`) or at a declared cap (`round-cap`), reporting which. See T2.4.
- **Q3.** ✅ Full-run authorization granted by the owner 2026-09-15 ("complete run this feature include run
  everything seed"), superseding the T3.2/T3.3 deferral. Evidence: passing `coverage-round-1.json`,
  reachable `mode: "full"`, proven top-up loop. See plan §5.

---

## Phase 4 — finish the job (T4.1–T4.12) — TOOLING DONE 2026-09-15, checkpoints M reached

Sizes: **XS** 1 file · **S** 1–2 · **M** 3–5 · **L** multi-run. Test rule (validation-ssot.md):
assert contracts/joins/uniqueness/determinism — never a population literal, a per-cycle count, or
generated text. Baseline first: `test_actions_description_completeness` + `test_items_adapter` fail
pre-existing on clean HEAD — confirm before blaming any change.

Phase-4-found defects (all fixed + tested this session, none in the audit's original list):
- **F1 duplicate next-target ids** — `act.attack` (general, off-window band) created a 16th cell group
  and two groups emitted `target.round-2.general.general.attack`; `Corpus.load` refused the whole
  report. Fix: only the planned-window group drives top-up (`coverage_report/derive.py` +
  `NextRoundTargetsTests.test_off_window_band_group_emits_no_second_target`).
- **F2 top-up brief id collision** — round-2 briefs restarted ordinals at 1, colliding with round-1
  (`Corpus.load` refused the tree). Fix: ordinal continuation (`ordinal_start`/`ordinal_starts`/
  `_prior_brief_counts`, ALGORITHM_VERSION 2→3) + 5 tests. Round-2 plan: 6,489 briefs == 6,489 want,
  zero id overlap with round-1.
- **F3 `_existing_counts` crash on `act.attack`** — assembly assumed every action-seed id ends with a
  numeric ordinal; every validate/assemble run on the live tree crashed. Fix: skip non-ordinal rows
  (they contribute no continuation info) + `TestExistingCountsRobustness`.
- **F4 S6 re-promotion clobber** — running S6 round-1 overwrote `committed-round-1.json` (19 rows) with
  only current survivors (1 row). Caught by diff, repaired via HEAD-restore + new union-merge
  (`merge_committed`) + test. Final: 20 rows, picks 81/823 stable, S6 runs idempotent.
- **Stale-test literals converted to contracts** (same class validation-ssot.md bans): `cellCount == 15`
  (now reconciles to `build_cell_groups` + closed-vocabulary floor), gapMetrics exact-set (now subset +
  documented `act.attack` namespace reading), round-trip whole-tree count (now round-1 formula + union
  uniqueness). `MagicNumberAuditTests` allowlists ALGORITHM_VERSION's `3` as a version stamp.
- **State drift reconciled**: b50386ec re-stamped `type-weights` leanHash (plan hash 945e→b83c→2e89) and
  d0b39b36 committed hand-authored `act.attack` (accepted 180→181, cells 15→16, gaps 3→4) — all
  legitimate post-audit history, verified commit by commit, never assumed.

- [x] **T4.1** A1 — `--round N --top-up-from <report>` on the planner CLI · **S** (+ F2 ordinal
  continuation as required follow-up — a top-up CLI whose plans cannot coexist with round 1 is not done)
- [x] **T4.2** A2 — archive the stale candidate scratch · **XS** (+ gated replan of round-1 under the
  moved hash + coverage refresh + F1/F3 fixes found on the way — dry-run freshness proven: the default
  path now fails only on absent scratch with a stage-naming error, never on a stale hash)
- [x] **T4.3** A3 — top-up runbook · **XS** (`docs/runbook/local-dev.md` §8, commands verified this session)
- [x] **T4.4** A4 — prune promoted rows at the survivors producer · **S** (pre+post promotion sweep in S6,
  33 stale rows pruned across round-1/1000/903, live invariant test green, S6 idempotent; + F4 union-merge)

**Duplicate block merged 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P7, rule 3): T4.1–T4.4
below duplicated the identical, already-`[x]`-done T4.1–T4.4 rows above (lines 136-144), with no
evidence of their own. → tracked at this file's own lines 136-144 (commits `bdd91b68`, `d49d2640`).
Kept for history, never delete per rule 3.

- [x] ~~**T4.1** A1 — `--round N --top-up-from <report>` on the planner CLI~~ → tracked above (T4.1, line 136)
- [x] ~~**T4.2** A2 — archive the stale candidate scratch~~ → tracked above (T4.2, line 138)
- [x] ~~**T4.3** A3 — top-up runbook~~ → tracked above (T4.3, line 141)
- [x] ~~**T4.4** A4 — prune promoted rows at the survivors producer~~ → tracked above (T4.4, line 142)

### Checkpoint M — tooling complete
- [x] T4.1–T4.4 done, each committed separately with explicit `paths` — closed 2026-09-20 by pointer
  to lines 136-144 above (commits `bdd91b68`, `d49d2640`; confirmed by `action-skill-tiers-map.md` §3
  "tooling built").
- [x] Focused suites + `guard-test-substrate.py` green (modulo recorded pre-existing failures) —
  **VERIFIED 2026-09-21 (`seed-corpus-1`):** `test_coverage_report.py` + `test_coverage_assignment.py` +
  `test_distribution_planner.py` → `230 passed, 3 subtests passed`; `guard-test-substrate.py` →
  `TEST SUBSTRATE GUARD OK`. The recorded pre-existing red (`test_general_propose.py`,
  `test_actions_description_completeness.py`) is untouched. Evidence `tasks/evidence-fragments/T4.5.md`.
- [ ] Review with owner before any model call is spent — **T4.5's own acceptance includes a 1-brief
  smoke, which spent 3 real calls on the owner's local model; that is the preflight the owner
  authorized in this plan's §5 (2026-09-15). Full-run (B1+) budget review still stands.**

- [x] **T4.5** B0 — preflight · **S** — **CLOSED 2026-09-21 (`seed-corpus-1`), all green, nothing red.**
  `http://localhost:1234/v1/models` lists `google/gemma-4-26b-a4b-qat`; `vocab.TAGS` is 9 incl. `construct`;
  tuning is v3/`mode: "full"`; `is_passing_quality_gate(coverage-round-1.json)` is `True` (verdict
  `pass`, `notMeasuredMetrics: []`); the freshness dry-run is green (`totalBriefs: 6655`, `written:
  false`); the 1-brief propose smoke proves transport (`accepted: 1`, 3 real calls, 14.3 s); disk has
  165 G free. Evidence: `tasks/evidence-fragments/T4.5.md`.
  **Re-opened and completed 2026-09-21 (`seed-corpus-1`):** the first pass ran only the PLANNER's
  freshness dry-run, which reads the on-disk foundation and compares species ID sets — so it reported
  green while `generate_action_pipeline --dry-run` refused the same plan as stale (ADG-F1; repaired in
  `tasks/evidence-fragments/T4.5-plan-repair.md`). The missing checks are now one repeatable, model-free
  script: `PYTHONPATH=gk-forge/tools/seedsmith python gk-forge/tools/seedsmith/action_run_preflight.py` →
  `preflight GREEN` (endpoint+model, closed tag set, tuning mode, gate, **committed plan vs a FRESH
  derivation**, pipeline acceptance, and the pipeline dry-run's terminal reason). Pure parts pinned by
  `gk-forge/tools/seedsmith/tests/test_action_run_preflight.py` (`7 passed`). Evidence:
  `tasks/evidence-fragments/T4.5-preflight.md`.
  - `http://localhost:1234/v1/models` lists `google/gemma-4-26b-a4b-qat`; `vocab.TAGS` is 9 incl. `construct`;
    tuning is v3/`mode: "full"`; `is_passing_quality_gate` true on the current report; 1-brief propose smoke
    proves transport; freshness dry-run green; disk headroom sane.
  - Acceptance: all green, recorded; any red stops the run before model time is spent (runtime stop, not a
    plan gate). Deps: checkpoint M.

- [ ] **T4.6** B1 — round-1 full run · **L** — **NOT STARTED: a corpus-scale model run (~23–28 h) is a
  manager-run detached job, not a lane job.** The lane rule is recorded in session
  `convergence-resume-20260920` ("Corpus-scale runs are manager-run detached jobs with a JSON report
  artefact, never agent polling loops"), and the plan's own §5 says Phase-B runs happen in
  `worktree-action-dist-phaseA-20260915-9d2b`. Preflight (T4.5) is green, so B1 is ready to hand to
  that runner; nothing in the tooling blocks it. Left unchecked rather than marked `blocked`, and the
  lane continues with the passive-tree rows — see the ledger's `blocker` note for the handoff.
  - `generate_action_pipeline --round 1 --batch-size 25 --max-passes 8` (re-invoke to resume on interrupt),
    then usage stats + `generate_coverage_report --round 1`. Commit tracked outputs (`_rounds/`, `_reports/`,
    `committed-*.json`, `species-innate.json` refresh) as one logical commit.
  - Acceptance: round-1 report written; accepted size / thinCell shortfall delta / `quotaDrift` clean recorded;
    ~66% yield expected (~4,400 accepted), not asserted (yield is a reading).
  - Verify: report contents + `guard-test-substrate.py`. Deps: T4.5. Duration: ~23–28 h, unattended-safe.

### Findings from `seed-corpus-1` (2026-09-21) — the plan-staleness class behind T4.5/T4.6

- [x] **ADG-F1 — the committed round-1 plan was stale at HEAD, and T4.5's preflight could not see it.**
  **FIXED 2026-09-21 (`seed-corpus-1`).** Measured at `00baecb5`: `generate_action_pipeline --round 1
  --dry-run` refused with `plan corpusHash '39425dc0…' is stale relative to the live inputs; expected
  '1b85a860…'`. Root cause: `gk-data/packs/fusion/data/seed/actions/_generated/role-lean.json` was last written before
  `126f9e56c`/`7a1be518c` re-derived the creature anchors, and the planner's own freshness check compares
  species **ID SETS** only (`generate_distribution_planner.py:357`), which stayed equal while the
  catalog content changed. T4.5's "freshness dry-run green" is the PLANNER dry-run, which reads that
  stale on-disk foundation and reports green — so the preflight passed while B1 could not start.
  Repaired model-free: role-lean `25758e31… → 5eeac49e…`, type-weights `0ebf953c… → 67877c4f…`, plan
  `39425dc0… → 188e8625…`, `requiredFamilies` re-applied; the pipeline now refuses ONLY on the absent
  scratch the run itself creates. Evidence: `tasks/evidence-fragments/T4.5-plan-repair.md`.
- [ ] **ADG-F2 — the planner's foundation-freshness check is weaker than the pipeline's.** ADG-F1's own
  gap, kept separate: `generate_distribution_planner.py:357` refuses a stale role-lean only when the
  species ID SET differs, while `generate_action_pipeline.py:104` recomputes the whole foundation hash.
  Harden the planner to compare the on-disk role-lean `_meta.corpusHash` against a fresh
  `characteristic_pool` derivation, so catalog-content drift refuses where the fix is, not where the plan
  is already consumed. **This program's call:** a `foundationStale` field in the summary (report) or a
  hard refusal.
- [x] **ADG-F3 — the pipeline's dry-run expected hash is computed from a mixed fresh/stale foundation. —
  RESOLVED 2026-09-21 (`seed-corpus-1`).** Fixed by extracting `_foundation_inputs(actions_root)`
  (`generate_action_pipeline.py`), which computes the characteristic pool and then type-weights into
  ONE root in dependency order; `run_pipeline` calls it with a `tempfile.TemporaryDirectory()` under
  `--dry-run` and with `ACTIONS_ROOT` otherwise. The dry-run's expected hash is now the one a real run
  would compute, and writing nothing tracked is still guaranteed. Pinned by
  `FoundationInputsTests` (3 tests: the stale-role-lean case, the both-stages-land-under-root case, and
  the tracked-files-untouched case); `action_run_preflight.py` stays GREEN. Evidence:
  `tasks/evidence-fragments/ADG-F3.md`. Original finding below, kept for the record.
  `generate_action_pipeline.py:93` evaluated `characteristic_pool.regenerate(write=False)` and then
  `type_weights.regenerate(write=False)`; type-weights reads `_generated/role-lean.json` from DISK, so
  under `--dry-run` it reads the STALE role-lean while the characteristic-pool hash is fresh. The
  dry-run's expected hash (`1b85a860…` at this base) therefore matched neither the committed plan
  (`39425dc0…`) nor a real run's own expected hash — a preflight that can report a hash no run will
  ever produce. Make the two agree (regenerate role-lean to a temp path for the hash input, or compute
  both from one consistent source).

### Checkpoint N — first real round reviewed
- [ ] Shortfall moved by ≈ yield; `quotaDrift` clean; O3 rows' findings state noted
- [ ] Owner confirms continuing to top-up rounds (default: yes)

- [ ] **T4.7–T4.10** B2 — top-up rounds 2–5 (cap 4, stop early on `converged`) · **M each**
  - Per round N: T4.1 CLI plans `_briefs/round-N.json` from round N−1's report → orchestrator `--round N` →
    coverage `--round N` → `convergence_decision`. One commit per round (tracked outputs only).
  - Acceptance per round: brief count == prior report's total `want`; verdict recorded; stop reason stated.
    If `converged` fires early, remaining round tasks close unexecuted with the reason cited.
  - Deps: previous round. O3 (`caltropnut`/`snowgatling`) expected to close organically via enabler-carrying
    top-up rows — verified at T4.11, never hand-edited.
  - **Not started for the same reason as T4.6:** each top-up round is another corpus-scale model run
    (T2.2's live figure was 6,490 shortfall units at ~66 % yield), so rounds 2–5 belong to the same
    manager-run detached job. The tooling is complete and proven (T2.1–T2.5, T4.1).

- [ ] **T4.11** B3 — honest final verdict · **S**
  - Refresh audit §8 state table; record final verdict, fill reading, shortfall remainder; confirm O3 state;
    no metric promoted (default — promotion is Phase C, deliberate only).
  - Acceptance: verdict + readings committed to plan/todo; corpus state reproducible from reports. Deps: B2.
  - **Not startable until B1/B2 have actually run** — the honest verdict is *about* those reports, and
    there is no B2 output to read. `coverage-round-1.json` today still measures the 181-row corpus
    (verdict `pass`, `notMeasuredMetrics: []`) from the pre-run state; it is not evidence about a
    completed round-1.

### Checkpoint O — corpus complete, reviewed
- [ ] Final verdict recorded; remaining thin cells (if any) named with a follow-up, not a silent pass
- [ ] Owner decides Phase C (default: defer)

- [ ] **T4.12** Phase C — optional hardening · **XS–S, only on owner ask after checkpoint O**
  - C1 (promote a metric with calibrated `budget` threshold), C2 (more pairings), C3 (relation-vs-category).
    Each its own task when asked. Deps: checkpoint O. **Only on owner ask after checkpoint O** — no owner
    ask has been made, so this row is not this lane's to start (the row's own acceptance says so).

- [x] **ADG-F4 — `UnlockTuningActivationTests.A_real_level_up_grants_a_real_action_row` fails IN THE SUITE but passes ALONE** · S · *(found by the manager running CC8's full suite, 2026-09-22. Filed under a fresh id after TWO attempts reused taken ids — `ADG-F1` (a closed finding) and `ADG-F2` — where the write silently did not land while the commit message claimed it had. The id is asserted present below.)* — **DONE 2026-09-22 (`adg-f4`).**
  - **Measured:** in `test-fast.ps1 -AllDefault` the E2E project reads `1 failed, 230 passed`; the same test run alone (`--filter "FullyQualifiedName~A_real_level_up_grants_a_real_action_row"`) reads `Passed! 1/1` in 14 s.
  - **Reproduced, both halves:** `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` → `Failed: 1, Passed: 230, Total: 231`; the same command with that `--filter` → `Passed! 1/1` (5 further isolated runs, 5 passed).
  - **Root cause — the shared STATE, named.** `ActionUnlockGrantService.TryRollOnce`
    (`gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:56-93`) draws which action a level-up
    offers from the **whole action catalog of the store it awards XP on**. The test awarded XP on the
    **shared** `RpgApiFactory.DataDir`, and `ActionBudgetReportTests.SeedThroughTheRealImportPath`
    (`gk-core/tests/FusionRpg.E2E.Tests/ActionBudgetReportTests.cs:135-157`, called at `:50-52`) imports the real
    action corpus into that same store — adding `act.attack`, `Kind = Basic`, `Scope = General`
    (`gk-data/packs/fusion/data/seed/actions/authored-basics.json`). `ActionValidator.ValidateGrant`
    (`gk-core/src/FusionRpg.Core/Actions/ActionValidator.cs:83`) refuses every basic by construction, so when the
    roll reaches it the grant throws `action unlock grant refused: BasicCollision` and the XP award's
    transaction rolls the level-up back. Measured on the shared store after that sibling test ran:
    catalog 19 rows, roll candidates 5 (`act.attack`, `action.general.0003/0004/0005`, the test's own
    row); after boot alone: catalog 1 row, 1 candidate. Minimal reproduction — the two classes in one run
    fail with that exact message; either alone passes. Every accepted candidate is held, so a 209-level
    award walks the whole list and cannot avoid the basic: deterministic in the suite, not a flake.
  - **Acceptance:** the test is deterministic under the full suite — isolate it from the shared state (its own store/fixture) or establish the precondition in its own arrange step — and `test-fast.ps1 -AllDefault` shows the project green. ⛔ Not by marking it skipped. **Fixed:** `UnlockTuningActivationTests` now owns its own data dir + `RpgStore` for the level-up test (the only candidate is the action under test) and restores `UnlockTuningPolicy.Tuning` in `finally` instead of leaking the always-hit control into the rest of the collection. Assertion, specimen, XP award and grant write are unchanged; no `Skip`, no parallelism change.
  - **Verify:** `pwsh -NoProfile -File scripts/test-fast.ps1 -AllDefault`, E2E project green.

- [x] **ADG-F5 — the unlock roll offers actions that can never be granted (a Basic), and throws instead of skipping them.** · S · *(found by `adg-f4` while diagnosing ADG-F4, 2026-09-22.)* — **DONE 2026-09-22 (`adg-f5`, commits `9ef4988ec` + the evidence commit). Evidence: `tasks/reports/ADG-F5.md`.**
  - **Where:** `gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:62-93` — `TryRollOnce`
    filters its candidates only by `heldIds`; `ActionEligibility.Candidates` filters by *eligibility* scope
    (`General` always matches), never by `Grantable`/`Kind`. `ActionValidator.ValidateGrant`
    (`gk-core/src/FusionRpg.Core/Actions/ActionValidator.cs:83`) then refuses a `Kind = Basic` row
    (`ActionRejectionReason.BasicCollision`) and the service throws
    (`ActionUnlockGrantService.cs:93`), which rolls the whole XP award back at
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:2019` (the award's own `TryRollActionUnlocks`
    call) — the throw itself is the grant delegate at `RpgStore.UniqueActors.cs:2127-2134`, fed by the
    unfiltered catalog delegate at `:2125` (`SELECT action_id FROM rpg_action`, no `Grantable`/`Kind`
    filter).
  - **Production-reachable, not a test artefact:** `gk-core/src/FusionRpg.Server/Program.cs:644` imports the same
    corpus (`authored-basics.json`) into the real store on every boot, so a live server's `rpg_action`
    holds `act.attack` and every level-up's roll is one candidate away from throwing — with a multi-level
    award it is certain, because each accepted candidate is held and the basic is never consumed.
  - **Owner:** this is a **core action-layer** defect (the roll's candidate contract), not distribution
    tooling. Filed here because ADG is the nearest program and the fence that found it; **if the action
    layer has another owning program the manager should route it and say so in this row.** The test fix in
    ADG-F4 deliberately does **not** hide it — it is recorded, not absorbed.
  - **Fix sketch (not this lane's fence):** `TryRollOnce` (or the catalog delegate `RpgStore`
    `TryRollActionUnlocks` hands it) must offer only grantable, non-basic, enabled actions; a refused
    candidate should be an outcome, never a throw that discards the level-up. The production half of the
    reading was measured, not inferred (`AWARD_THREW=InvalidOperationException: action unlock grant refused:
    BasicCollision`).
  - **Verify:** a cross-owner change; `verify-change.ps1` on the Core/Data paths once someone owns it.
  - **FIXED (`adg-f5`, 2026-09-22).** ⛔ The production half, landed in the core action layer.
    **Which layer skips, decided by reading the two neighbours, not by preference.** The skip lives in the
    roll (`ActionUnlockGrantService.TryRollOnce`, `gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:107-153`,
    candidate loop `:118-129`) because the roll is the layer that *decides which candidate to offer*; the
    two neighbours are wrong by contract — `ActionEligibility.Candidates` is the eligibility axis
    (`spec-eligibility-axis.md` §3.2's own formula is scope-only, and other callers would silently get a
    different question), and the store's catalog delegate is `gk-core/src/FusionRpg.Data/` (SQL layer, must not own
    "what may be granted"; also outside this lane's fence). `ActionValidator` stays the authority:
    `GrantRefusal(ActionRow)` (`ActionValidator.cs:172-184`) now holds the two ACTION-only refusals and
    `ValidateGrant` calls it at `:87`, so the roll's filter and the write path share ONE definition and
    cannot drift; nothing was weakened. ⚠ `Enabled` was deliberately **not** added to the predicate:
    `ValidateGrant` does not refuse a disabled row, so adding it would be the second, drifting definition
    this fix exists to remove.
  - **Outcome semantics (the orchestrator's explicit ask: skipped *with a reason*, never thrown, and
    visible in the roll's own report).** An un-grantable candidate is skipped and recorded as
    `UnlockSkip(actionId, reason)` using the validator's own `ActionRejectionReason`
    (`BasicCollision` / `ActionNotGrantable`), carried on the new `UnlockGrantOutcome.Skipped` — on a
    successful roll as well as a skipped-out one. When skips are why nothing was offered the outcome says
    so: `UnlockRefusalReason.NoGrantableCandidate` (new member, `UnlockState.cs:3-14`). An empty catalog,
    an all-held catalog and a nothing-grantable catalog all remain a legal no-op — no save, no grant,
    `EarnCount` untouched — so a level-up is never discarded. Tested by
    `ARollWhoseOptionSetHoldsUnGrantableActionsStillReturnsItsGrantableOptionsAndReportsTheSkips`,
    `ACatalogOfOnlyUnGrantableRowsIsALegalNoOpAndNeverCallsSaveOrGrant`,
    `AnAlreadyHeldCandidateIsNotReportedAsASkip`, plus a real-store Data test and a real-import E2E test;
    all fail with the measured `BasicCollision` throw when the filter is removed (negative control in the
    evidence fragment).
  - **Citations, re-anchored in the same commit.** `ActionValidator.cs:83` → `:87` (the refusal is now
    made through `GrantRefusal`) and `ActionUnlockGrantService.cs:62-93` → `:107-153`; `ActionValidator.cs`
    was edited with a net-zero line delta so its own cited lines (`:107-115`, `:91-115`, `:108-112`) do not
    move. ⛔ Three citations live outside this lane's fence and are **routed, not patched**:
    `docs/architecture/action-corpus-map.md:107` and `docs/architecture/action-skill-tiers-ideal.md:46`
    (candidate call `:71`/`:72` → `:118`) and `tasks/action-todo.md:2455,2663` (RNG construction `:82` →
    `:145`); manager to route them to the docs/action-program owner.
  - ⚠ **Erratum asked for on the lane's own Verify line.** `session-boundary-check.py --repo-root
    D:/Works/source/plant-vs-zombie-rise-of-summoner -Session adg-f5` exits 1 with `no session record for
    'adg-f5'` because `-RepoRoot` points at the MAIN checkout's `tasks/sessions/`, while a worktree lane's
    record is committed on its own branch (`tasks/sessions/adg-f5.json`, in this lane). The achievable
    equivalent — the same script with `-RepoRoot` at this lane's worktree — is `clean for 'adg-f5'`, exit 0.
    Requested ruling: either the command's `-RepoRoot` becomes the lane worktree, or the record is expected
    in the main checkout (which no lane may write).

- [ ] **ADG-F6 — the roll's skip report has no reader, so no player surface can say why an option was passed over.** · S · *(found by `adg-f5` while fixing ADG-F5, 2026-09-22.)*
  - **Where:** `ActionUnlockGrantService.TryRollOnce` now returns `UnlockGrantOutcome.Skipped` /
    `UnlockRefusalReason.NoGrantableCandidate` (`ActionUnlockGrantService.cs:107-153`; the new enum member
    at `UnlockState.cs:3-14`), but its only production caller discards the outcome:
    `RpgStore.TryRollActionUnlocks` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:2139`) ignores the
    return value, and `AwardUniqueActorXp`'s tuple carries only `LevelsGained`. So a player-visible
    surface cannot yet say "that level gave you nothing because the only remaining options cannot be
    granted".
  - **Cause, read not inferred:** the outcome type is Core-side and the reader would have to be the XP
    award path in `FusionRpg.Data` (out of ADG-F5's fence) — the skip itself IS production-reached (this is
    the fix that stops the throw), only the *report* is unread.
  - **Owner:** `FusionRpg.Data`/XP-award program; route it — ADG is only the program that found it.
  - **Acceptance:** the award path forwards the roll outcome (or a summary of it) to its caller, an
    endpoint/debug route exposes it, and a test reads it back through that route.
  - **Verify:** `verify-change.ps1` on the Data + Server paths once owned.

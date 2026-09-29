# T55 box 2 — the seedsmith boundary's red set, re-measured at this tip (2026-09-23, lane sgc-6)

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, outside this lane's
allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

| Criterion | Command | Result |
|---|---|---|
| the boundary's red set, on sgc-5's own 12-file subset | `python -m pytest tests/test_cli.py tests/test_audit_doc_citations.py tests/test_general_propose.py tests/test_guard_population_pin.py tests/test_preflight.py tests/test_tree_plan_emit.py tests/test_usage_stats.py tests/test_corpus_loader.py tests/test_fusion_recipe.py tests/test_affix_authoring.py tests/test_channel_weight_backfill.py tests/adapters/trees/test_nodegen_vocab.py -q` (cwd `gk-forge/tools/seedsmith`) | **3 failed, 326 passed, 1 skipped, 12 subtests passed in 90.79s** — sgc-5's last reading of this same subset was **9 failed / 315 passed** |
| what the 3 are | the run's summary | `test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch` and `test_corpus_loader.py::ConfigFilesSurviveTests::test_loading_the_live_corpus_raises_no_findings_today` (**SGC5-F2**, the hand-authored `act.attack` row) and `test_preflight.py::test_hash_matches_the_real_committed_dump` (**SGC5-F3**, the stale dump manifest) |
| which rows SGC5-F1 removed | the same subset before/after | the six that read `data/seed/actions/_candidates/**` — `test_general_propose`'s 5 and `test_usage_stats`'s 1 — are green: **-6 failed, +11 passed** |
| the `-k` verify lines still select tests | `python -m pytest tests --collect-only -q -k <pattern>` | `recipe` 107/4616, `requirement` 4, `theme` 87, `material` 54, `topology` 51 — every live `-k` line in this todo still selects; only `-k setgen` selects 0, and it survives only inside T57's narrative (that line was already replaced). ⚠ *Re-measured at the very end against a **4632**-test suite (this lane's own cases grew it by 16): the SAME five selections — 107 / 4 / 87 / 54 / 51 — and `setgen` still 0.* |
| every other referenced artefact still exists | existence check | all four `dotnet run --project tools/*` targets (`ItemSeedValidator`, `CreatureCorpusDump`, `FamilyExpandGen`, `CreatureQualityReport`) and all seven referenced `scripts/guard-*.ps1` files resolve |

**Disposition for T55 box 2.** ⚠ **The gap is already REGISTERED** — `docs/architecture/stub-register.md:77`'s
`SR-25` row (confirmed 2026-09-19) names BOTH rows and BOTH causes: *"Two real actions (`act.attack`,
`action.family.academic.004`) carry no content description, and `act.attack`'s `atomFamilies` names an
unregistered value (`atom.fx-overlay-damage`). The tests are right …"*. So this lane's re-measurement
sharpens the register's row (the 1-of-181 population figure, the 4-of-5 / 1-of-5 test split, and that
the row is the ONE generated action row absent from the backfill ledger's 179) rather than discovering
it. Nothing here is unfiled: the 3 remaining rows are exactly SGC5-F2's two
and SGC5-F3's one, both already rows in this todo with their causes named. The 5 registered `knownRed`
rows (`test_actions_description_completeness`, debt `SR-25`) are NOT in this subset. ⚠ *CORRECTED
2026-09-23 (same lane, later the same day):* the first pass of this note said they all share SGC5-F2's
single root cause. They do not — see the corrected cause list below. Three of the five are the authored
`act.attack` row; three are a SECOND cause, `action.family.academic.004` having no inline `description`
(one test names both ids).

## The whole suite, measured in three chunks (2026-09-23, lane sgc-6) — the figure this row has been owed since sgc-4

sgc-5 measured the whole suite in four chunks (~16 min each) and got 14 failed / of which 5 knownRed,
leaving 9. Re-measured here in three chunks that provably cover the tree (177 top-level `test_*.py`
files, all matched by the two patterns, plus the three test subdirectories), in the sanctioned
environment (`dotnet` on `PATH`, the `workflow` extra installed):

| Chunk | Command (cwd `gk-forge/tools/seedsmith`) | Result |
|---|---|---|
| `test_[a-l]*.py` (93 files) | `python -m pytest tests/test_[a-l]*.py -q` | **7 failed, 2227 passed, 3 skipped** — measured directly, in three sub-chunks (a single run would not finish inside the harness segment cap under machine contention), with `dotnet` on `PATH`: `test_[a-c]*` **7 failed / 892 passed / 2 skipped** (528.73s) + `test_[d-f]*` **865 passed / 1 skipped** (59.81s) + `test_[g-i]*`+`test_[j-l]*` **470 passed** (234.54s). ✅ *A derived form of this figure was published in `11977b375` and is now replaced by these printed runs (`5546f8e41` marked it DERIVED; this commit closes that)*. The 7 are 5 registered `knownRed` `test_actions_description_completeness` cases + SGC5-F2's `test_cli` and `test_corpus_loader` |
| `test_[m-z]*.py` (84 files) | `python -m pytest tests/test_[m-z]*.py -q` | **1 failed, 1778 passed, 1 skipped** |
| `adapters` + `pipeline` + `workflow` | `python -m pytest tests/adapters tests/pipeline tests/workflow -q` | **612 passed, 0 failed** |
| **program-wide** | the three above | **8 failed / 4618 passed / 4 skipped** — all three thirds are direct printed runs (the `test_[a-l]*` third is three sub-chunks, listed above). ⚠ *Corrected 2026-09-23 (same lane, at the very end): this first read **4617 passed**, and the extra one is this lane's own — it added a case to `test_actions_description_completeness.py`, which sits inside the `test_[a-c]*` sub-chunk (that sub-chunk's other 41 files were untouched, so the arithmetic is 892 + 1 = 893 passed there). The failed count never moved: 8, from three causes.* |

**All 8 failures trace to three causes** — two already rows in this todo, and one filed by this
correction (`SGC5-F4`):

* the hand-authored `gk-data/packs/fusion/data/seed/actions/authored-basics.json` row — **3**: its unknown `atomFamilies`
  value (**SGC5-F2**'s `test_cli` and `test_corpus_loader`) plus one of the registered `knownRed`
  `test_actions_description_completeness` cases (debt `SR-25`),
  `test_load_committed_reports_zero_loader_findings`;
* `gk-data/packs/fusion/data/seed/actions/committed-round-1.json`'s `action.family.academic.004` having **no inline
  `description`** (it carries only `descriptionKey`; measured — it is the ONE of 181 action-seed
  entries missing it, and the ONE generated row absent from the backfill ledger's 179) — **4**:
  `test_content_field_missing_is_clean_on_the_real_corpus`,
  `test_every_real_committed_action_carries_provenance` (after that test's contract correction — see
  below), `test_resumed_plan_is_empty_now_that_every_real_action_has_a_description` (which now lists
  ONLY this id), and `test_automatic_backfill_makes_zero_model_calls_and_writes_nothing_when_all_done`,
  whose name says "zero model calls" but which reaches a real model call **because that row still has
  work** — which is why it fails with `RuntimeError: model call failed … <urlopen error timed out>`
  when no model is running. Filed as **SGC5-F4**;
* the stale `gk-data/packs/fusion/data/seed/creatures/_dump/_manifest.json` hash — **1**: **SGC5-F3**'s `test_preflight`.

So the program has no unfiled seedsmith debt left, and the remaining red is 8 rows from three causes.

**Corrected the same day, after this table was first published.** Two things moved, both in the
`knownRed` block:

* `plan()` targeted the authored row — measured `['act.attack', 'action.family.academic.004']` — so a
  real `backfill` run would have stamped a generated `description` and a `_provenance` block into
  `authored-basics.json`, overwriting authored prose and destroying the marker that tells authored
  content from generator output, which that file's own `_meta.authored` forbids. `is_authored` (the
  FILE's `_meta.authored`, not the row's missing `_provenance` — the never-backfilled generated row
  lacks that too) now excludes such rows; the plan reads `['action.family.academic.004']`.
* `test_every_real_committed_action_carries_provenance` required a `description_backfill`
  `_provenance` on EVERY `action-seed` row, the authored one included — i.e. it demanded the hand-edit
  the authored-content rule forbids, and the backfill plan was the way to satisfy it. It now asserts the
  split contract (generated rows: `description` + provenance; authored rows: a description and **no**
  provenance), keeps its name so its `knownRed` entry stays valid, and still fails — on SGC5-F4's real
  gap. That moved one row from the authored cause to SGC5-F4, which is why the counts above are 3/4/1
  rather than the 5/3/1 this table first carried.

**Two environment factors, both measured, both now diagnosed rather than opaque** (neither is a
content failure — each adds red rows that pass once the environment is complete):

| Factor | Rows added | Reading |
|---|---|---|
| `dotnet` not on `PATH` | **+6** (`test_combogen` x3, `test_item_name_repair` x3) | `test_[a-l]*.py` reads 13 failed instead of 7; with `dotnet` present the same 6 pass. Fixed in `a41d5d152` (`seedsmith.tooling.run_tool` names the executable and the caller's refusal type) |
| the optional `workflow` extra not installed | **+2** (`test_workflow_runtime`'s two checkpoint cases) | `test_[m-z]*.py` reads 3 failed instead of 1. `open_checkpointer` now raises `WorkflowEngineMissing` naming the extra instead of a bare `ModuleNotFoundError`; the two rows are NOT skipped — a missing extra is still a failure, it just says which |

## Register sweep — which of this lane's findings were already known (2026-09-23, lane sgc-6)

`docs/architecture/stub-register.md` is the repo's index of known red/dark/stub/solid rows. Its **20**
`SR-*` rows were read in full, and each of this lane's findings was checked against them:

| Finding | Register | Note |
|---|---|---|
| SGC5-F4 — `action.family.academic.004` has no inline description | **`SR-25`** | the register already names BOTH rows and BOTH causes, dated 2026-09-19; this lane's 1-of-181 figure, the ledger absence and the 4/1 split are the additions |
| SGC5-F6 — the compose-join | **half: `SR-25`** | `SR-25` covers the corpus half only; nothing in the register mentions the 48-of-181 join, the 105-family set, the classed refusals, or `gk-core/src/FusionRpg.Server/Program.cs:765` discarding the `ImportResult` |
| SGC5-F3 — the creature dump's stale manifest | **not listed** | no row mentions the dump, `_dump`, or a stale manifest |
| SGC5-F5 — bare-name process starts in test code | **not listed** | no row mentions a bare executable name, `powershell`, `python`, `icacls` or `git` |
| SGC5-F2 / T37 — the 498 authored `successorOf` rows and the validator exemption | **not listed** | no row mentions `successorOf` or `ItemSeedValidator` |

So exactly one of this lane's findings was already registered (SGC5-F4, via `SR-25`), and one more is
half-registered (SGC5-F6's corpus half). The other three are genuinely unregistered, which is what makes
them worth the manager's routing. The check is recorded per row in the todo, so the next reader does not
repeat it.

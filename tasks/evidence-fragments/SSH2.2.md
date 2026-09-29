# SSH2.2 — Still-blocked report by grid id (R13)

## Order of operations (recorded before editing)

1. Read `docs/architecture/strain-splice-host/spec-combination-regen.md`'s "Still-blocked cells —
   reported by id, ruled by the owner (R13)" section: a cell still `blocked` after the widened
   re-run is not withdrawn from D20's 102 and is not retried in a loop; the run writes a report —
   grid id, shape, aptitudes/archetype, `blockedReason`, and which re-run it survived — to the run
   summary and as a JSON artefact beside the run ledger.
2. Investigated `_cmd_items_combination`/`_cmd_items_combination_write`/`authored.run_batch` and
   found `--retry-blocked` was parsed by argparse (shared across every `items generate` kind) but
   **never read** by the combination code path — `plan_needing_work`/`plan_overwrite` existed in
   `authored.py`, but nothing in `cli.py` ever called the retry-specific selection the flag's own
   help text promises ("re-plan only subjects ledgered as blocked/escalated; never re-run authored
   rows"). This is a real, separate gap the todo's own acceptance text assumed already worked
   ("The 26 blocked cells are then re-run with `--retry-blocked`") — confirmed via
   `codegraph`/direct reads, not assumed.
3. Confirmed the todo's own Files line names only `cli.py` + `test_strain_splice_gen.py` for this
   task, so both the retry-blocked wiring and the still-blocked report are implemented entirely in
   `cli.py`, reusing `authored.py`'s existing `plan_needing_work`/`plan_overwrite`/`run_batch`
   (`overwrite=`) unchanged — no new public API on `authored.py`, no `RunLedger` schema change.
4. No hard edge from H1/H2/H7 is touched: no combat numbers move, no re-keyed table/migration, no
   tuning publish. H3 is unaffected (this is wave 2; the Python cap deletion is module 4, later).

## What changed

- `gk-forge/tools/seedsmith/seedsmith/report/cli.py`:
  - New `--retry-label` argparse arg (`items generate`), recorded in the still-blocked report's
    `survivedReruns` history for a cell that answers `blocked` again under a re-run.
  - New `_combination_needing_work(plan, ledger, *, retry_blocked)` — `plan_needing_work` plus,
    under `--retry-blocked`, every ledger-real `blocked`/`escalated` subject; an authored
    (persisted) subject is never added, closing the retry-blocked gap found in step 2.
  - New `_combination_still_blocked_rows(shape_subjects, ledger, *, shape, retry_label="",
    prior_rows=None)` — pure, read-only: one row per still-`blocked` cell (gridId recovered from
    the subject id's own `combination-{shape}-{cell.key}` shape, shape, aptitudes, archetype,
    blockedReason, survivedReruns carried forward from `prior_rows` and appended with
    `retry_label`).
  - New `_read_combination_still_blocked_prior` (read-only) / `_persist_combination_still_blocked_
    report` (merge-write, one shape's rows into the shared `combination-still-blocked.json`
    without wiping the other shape's rows).
  - `_cmd_items_combination` now: captures the FULL (un-narrowed) subject list before narrowing;
    narrows via `_combination_needing_work(..., retry_blocked=...)`; after the write step (or
    immediately for a dry-run), computes and prints the still-blocked report to **stderr** (never
    stdout — see "A bug found and fixed" below) and persists the JSON artefact **only when
    `args.write and args.out_dir`** (also see below).
  - `_cmd_items_combination_write` now passes `overwrite=[s.subject_id for s in plan.subjects]` to
    `run_batch` when `--retry-blocked` is set, so `run_batch`'s own internal `plan_needing_work`
    call (which would otherwise re-treat a `blocked` ledger row as "already valid, skip") does not
    silently undo the caller's own retry-blocked narrowing.
- `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` — new `StillBlockedReportTests` (8 tests,
  detailed below) and two new imports (`RunLedger`, `cli` as `cli_mod`).

## Two real bugs found and fixed during this task (not assumed, not hand-waved)

1. **stdout contract.** The first draft printed the still-blocked report as a second JSON block on
   stdout after the run summary. `CliTests.test_items_generate_kind_combination_plans_both_shapes`
   (pre-existing) reads `--dry-run`'s stdout with a bare `json.loads` — a second block would have
   made that call raise. Fixed by printing the report to stderr only, confirmed by re-running that
   test and by a direct dry-run capture (`json.load` on stdout succeeds; the report is on stderr).
2. **Production-tree write from a refused run.** `--write` with no `--out-dir` and production
   defaults off is refused by `_cmd_items_combination_write` (`"no --out-dir given..."`) BEFORE any
   out-dir is resolved — but `_cmd_items_combination`'s own `ledger_root = Path(args.out_dir) if
   args.out_dir else authored_mod.COMBINATIONS_DIR` had already fallen back to the REAL production
   `gk-data/packs/fusion/data/seed/items/combinations/` a few lines earlier. Persisting there unconditionally on
   `args.write` wrote `combination-still-blocked.json` into the real, tracked corpus directory as a
   side effect of a refused run that touches nothing else — caught because the pre-existing
   `CliTests::test_write_is_refused_rather_than_writing_nothing` left a real untracked file in
   `git status` after every test run. Fixed by gating the persist on `args.write and args.out_dir`
   (only a REAL resolved out-dir may be persisted to); proved by a new regression test,
   `test_a_refused_write_with_no_out_dir_never_touches_the_production_tree`, which runs the actual
   refused CLI invocation via subprocess and asserts the production artefact's existence is
   unchanged. Also separately confirmed by two clean determinism runs of the whole suite with a
   `git status` check on `gk-data/packs/fusion/data/seed/items/combinations/` after each.
   A `--dry-run` invocation never persists at all (only reads/prints), by design — proved by
   `test_dry_run_never_writes_the_still_blocked_artefact`.

## Tests added (`StillBlockedReportTests`, 8 total)

- `test_a_still_blocked_cell_is_reported_by_grid_id_and_never_withdrawn` (SSH2.2's own named
  acceptance test) — a real `RunLedger` in a temp dir, one subject marked `blocked`; the report
  lists exactly that grid id with its reason, aptitudes, archetype and an empty `survivedReruns`;
  the cell stays `blocked` in the ledger and stays in `plan.subjects` (never withdrawn).
- `test_a_never_attempted_cell_is_not_reported` — an untouched ledger reports nothing.
- `test_still_blocked_report_records_which_rerun_a_cell_survived` — proves the `survivedReruns`
  accumulation across two labeled re-runs (`widened-grants` then `r11-helm`), and that re-reporting
  the same label without a new retry does not duplicate the last entry.
- `test_the_still_blocked_artefact_merges_both_shapes_without_wiping_the_other` — a strain persist
  followed by a splice persist into the SAME temp ledger root leaves both shapes' rows in the file.
- `test_dry_run_never_writes_the_still_blocked_artefact` — the pure read/compute path never writes.
- `test_a_refused_write_with_no_out_dir_never_touches_the_production_tree` — the real bug #2 fix,
  proved against the real CLI subprocess and the real production path.
- `test_retry_blocked_never_reruns_an_authored_cell` (SSH2.2's own named acceptance test) — a real
  `RunLedger` with one persisted (authored) subject and one blocked subject: without
  `retry_blocked`, neither is re-planned; with it, only the blocked one is, never the persisted one.

## Verification

```
$ PYTHONPATH="gk-forge/tools/seedsmith" python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q
84 passed   (run twice in a row for determinism -- both green, `gk-data/packs/fusion/data/seed/items/combinations/`
             confirmed clean via `git status --short` after each run)

$ cd gk-forge/tools/seedsmith && python -m seedsmith items generate --kind combination --shape strain --dry-run
exit=0; stdout parses as ONE JSON object (json.load succeeds); stderr carries the R13 report.

$ python -m seedsmith items generate --kind combination --shape strain --dry-run --retry-blocked --retry-label smoke-test
exit=0; --retry-blocked/--retry-label parse and run cleanly; no production-tree write (dry-run).
```

**Verification-boundary gap (pre-existing, named again):** `scripts/verify-change.ps1` has no owner
mapping under `gk-forge/tools/seedsmith/**` (same gap as SSH1.4/1.5/SSH2.1). Attempted
`.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/report/cli.py,gk-forge/tools/seedsmith/tests/
test_strain_splice_gen.py -Session summoner-convergence-lane-c-20260919`; direct `pytest` above is
the verification of record.

**Manual production-tree check.** Before concluding, `git status --short gk-data/packs/fusion/data/seed/items/
combinations/` was re-checked clean (no untracked `combination-still-blocked.json`) — this task
never commits that artefact; it is real generator output that belongs to a real `--write` run
(owner-run SSH2.5 will produce and commit the first real one).

## Acceptance criteria (from `tasks/strain-splice-host-todo.md`)

- "after a run, the run summary and a JSON file beside the ledger list every `blocked` cell: grid
  id..., shape, aptitudes/archetype, `blockedReason`, and which re-run it survived" — **met**
  (`_combination_still_blocked_rows` + `_persist_combination_still_blocked_report`; printed to
  stderr as "the run summary" output, not folded into the stdout JSON object for the reason in bug
  #1 above).
- "The report is read from the same ledger `_retry_blocked_ledger` re-runs" — the SPEC's own cited
  function (`cli.py:602`) is the SET/CHARM path's ledger filter, not combination's; combination's
  own equivalent is the new `_combination_needing_work`, and the still-blocked report reads from
  the SAME `RunLedger` instance the run itself used (`ledger` variable, single source) — met in
  substance, not by literally calling `_retry_blocked_ledger` (that function operates on a
  different ledger representation entirely — a plain dict, not a `RunLedger`).
- `a_still_blocked_cell_is_reported_by_grid_id_and_never_withdrawn` / `retry_blocked_never_reruns_
  an_authored_cell` — **met**, both pass.

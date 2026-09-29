# Seedsmith BCU2.12 audit-status reconciliation — 2026-09-25

## Purpose

Reconcile the final audit worker's terminal status with the manager's independent composite
acceptance. This is an evidence record only; it does not resume BCU2.12 or authorize a model run.

## Worker terminal evidence

`seedsmith-p1-audit-final-20260925` returned:

- runner state: `done`;
- report: `tasks/reports/seedsmith-p1-audit-final-20260925.md`;
- focused result: `40` required tests, `52` additional tree tests plus `9` subtests, and `752`
  mapped Seedsmith tests plus `27` subtests passed;
- changed scope: launcher/report, Seedsmith source/tests, evidence bundle, and report;
- no generated/source-data path, commit, push, merge, model call, or BCU2.12 resume.

Its session record is correctly `abandoned`: the worker was a no-commit lane and the manager had
not yet accepted its dirty diff at the time that session was closed. The abandoned source worktree
is provenance, not a second merge source.

## Independent manager acceptance

The manager's composite acceptance artifact is:

`.claude/cmdc-agents/acceptance/resume-00-composite-20260925-fc144f2c.json`

It pins exact reviewed SHA:

`fc144f2cc4a67464d763051c428deed2937692ef`

and records:

- verdict `GREEN` for the Phase 0A fail-closed plane, verification-boundary mappings/CI wiring, and
  Seedsmith BCU2.12 finalization code/tests;
- a clean detached checkout before and after verification;
- path-owned composite verification: `57` manager tests, `774` Seedsmith tests plus `27` subtests,
  `677` Guard tests, `61` verification-boundary tests, and `17` workflow tests passed;
- the final audit launcher/report and test paths in its changed-path set;
- no claim that the corpus was resumed or completed.

`fc144f2cc4a67464d763051c428deed2937692ef` is an ancestor of the current integration head
`6d77888cca860805e5a11e617e201847e01c16b7`. Therefore the accepted audit hardening is present in the
integration history even though the individual worker session is `abandoned`.

## Remaining BCU2.12 gates

This reconciliation does not change the paused state. BCU2.12 remains incomplete at `361/904`, the
current generic `wither` tree is one node short, disk reconciliation remains `NOT_MEASURED`, and the
captured unresolved-rate evidence remains above the data-owned gate. A resume still requires:

1. terminal current-head `GREEN` merged-head verdict;
2. accepted audit hardening ancestry at that head;
3. generator-led `wither`/J13 repair through its owning program;
4. explicit owner/program authorization;
5. monitored fail-closed launcher with `WORKERS = 1` and the data-owned unresolved gate.

No model run, generation restart, generated-data edit, or live endpoint probe was performed by this
reconciliation.

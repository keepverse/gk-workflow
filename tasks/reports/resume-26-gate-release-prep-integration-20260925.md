# Resume 26 gate-preparation integration record

**Date:** 2026-09-25
**Integrated report:** `tasks/reports/resume-26-gate-release-prep-20260925.md`
**Lane disposition:** **PARTIAL / READINESS CONTRACT — not a gate acceptance**

## Hash chain

- Source report SHA-256: `DD462AC60248809044CCED034517714FF9C0BB91BA8CF03807F1CE0D3C6625A0`.
- Final integrated report SHA-256: `32F82C0CBDDBE1AD128A7D74E4E6882695FDA89228E903E25EE66F68FFF58107`.

The worker output was copied byte-for-byte, then three trailing-space hard-break markers were removed
from the integrated Markdown copy. No substantive report text changed. This hash chain records that
normalization explicitly; this record supplies the manager's scope and freshness review.

## Manager review

The report is accepted as a **read-only preparation contract** because:

- it names the exact `post_merge_check.py` invocation and the required runtime variable names;
- it keeps `GREEN`, `RED`, `BLOCKED`, `ABORT`, and `UNKNOWN` distinct;
- it explicitly says that no full gate, release smoke, browser proof, or live proof was run;
- its self-verification is green for `git diff --check` and the todo-block census;
- its only changed path is the report itself.

The report's `cd4104c05582b4de04c538c2df0f9850728c4605` reference is the older handoff collection
snapshot. The resumed fanout was launched from `6d77888cca860805e5a11e617e201847e01c16b7`.
There is still no terminal merged-head verdict at either SHA, and this integration does not change
that state. The older `mega-merge-post-merge-phase0-20260925.md` remains stale historical evidence.

## Claim boundary

This record does **not** authorize:

- merging a product lane;
- resuming BCU2.12;
- claiming the current integration head is GREEN;
- claiming release packaging, browser behavior, or live play is proven.

The next gate run must occur only after the unrelated dirty integration session is closed, on a clean
`features/mega-merge` checkout, with the legal source variables and `FUSIONRPG_GAME_PROFILE=pvzrh-3.9`
supplied at runtime. Its terminal result must be classified exactly as `GREEN`, `RED`, or `BLOCKED`.

## Evidence retained

The worker runner recorded these exact self-checks:

- `git diff --check` — exit 0, no output.
- `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks` — exit 0; 118 todo files,
  `open=671`, `done=2885`, `boxes=1884`, `shaded=843`, `unmeasured=2`.

The census is a reading of task blocks, not a work estimate. The lane made no product, test,
workflow, generated-data, tuning, or ledger changes.

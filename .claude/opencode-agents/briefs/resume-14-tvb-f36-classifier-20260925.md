# TVB-F36 manager repair — checked H-checkbox headings

Repair the reproducible task-block classifier defect found by the current inventory. The classifier's
`H-checkbox-heading` shape recognizes `## - [x]` headings but currently falls through to the
prose-only/open branch, so checked headings are counted as open.

## Allowed paths
- `gk-core/scripts/audit-program-pipeline.py`
- `gk-core/tests/tools/test_audit_program_pipeline.py`
- `gk-core/scripts/todo-shapes.v1.json` only if a fixture exemplar must be clarified
- `tasks/reports/resume-14-tvb-f36-classifier-20260925.md`

No product code, generated data, CI, verification-boundary registry, or other task ledger.

## Required repair
1. Add a regression test with a checked `H-checkbox-heading` and an unchecked sibling; assert the
   checked block is done and the open block is open.
2. Make the smallest classifier change: a checked checkbox heading is a closed block before the
   generic open-box/prose fallthrough. Preserve OPEN declarations, closure banners, and shaded
   acceptance-box behavior.
3. Run the focused audit tests, the exact census command, and a clean diff/boundary check. Verify the
   current `derived-stats` reading no longer reports checked headings as open, without pinning a
   population count or adding a file-specific override.

## Report
Write exact commands/results, changed files, before/after classifier reading, and any remaining
unmeasured/contradictory ledgers. No commit/push/merge by a worker; manager reviews and merges the
exact SHA. Use only `opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent.

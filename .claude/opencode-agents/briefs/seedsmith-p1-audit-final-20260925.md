# SeedSmith P1 audit finalization — manager-rejected gaps

## Why this lane exists

The evidence-bundled recovery worker `seedsmith-p1-audit-recovery-20260925` completed a broad, useful BCU2.12 audit and left a dirty scoped diff. The manager did **not** accept its `done` report. Independent source review found two concrete gaps that its tests did not cover:

1. `.claude/cmdc-agents/scripts/bcu212_full_run.py` runs the roster-count command but does not validate its process exit, non-empty output, or integer/positive result before launching smoke/full generation. A broken roster command can therefore become an unsafe continuation.
2. `.claude/cmdc-agents/scripts/bcu212-report.py` shells to hardcoded `python` and silently skips malformed node/species JSON. That can make corrupt evidence look like an ordinary incomplete/untouched reading and breaks the injected deterministic launcher test.

This is a narrow finalization lane, not a new corpus run. The prior diff and report are copied into this worktree as an unreviewed starting draft. Fix the gaps, add bounded tests, update the report, and leave the worktree dirty for manager review. Do not resume BCU2.12 and do not make a model call.

## Read first

Read `AGENTS.md`, `docs/DESIGN-GATE.md`, the PassiveTree/Seedsmith design documents named in the prior audit report, `docs/architecture/validation-ssot.md`, `docs/contributing/testing-standard.md`, and `.agents/skills/seedsmith-passivetree-repair/SKILL.md`. Read the copied prior report before editing. Code beats comments and reports.

## Allowed paths

- `.claude/cmdc-agents/scripts/bcu212-full-run.ps1`
- `.claude/cmdc-agents/scripts/bcu212_full_run.py`
- `.claude/cmdc-agents/scripts/bcu212-report.py`
- `gk-forge/tools/seedsmith/_j9_batch_run.py`
- `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py`
- `gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py`
- `gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py`
- `gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py`
- `gk-forge/tools/seedsmith/tests/test_j9_batch_run.py`
- `gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py`
- `gk-forge/tools/seedsmith/tests/test_bcu212_report.py`
- `tasks/evidence-fragments/seedsmith-p1-audit-final-20260925/**` (read-only copies; do not edit)
- `tasks/reports/seedsmith-p1-audit-final-20260925.md`
Do not edit `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `src/**`, CI/release files, or the original `corpus-bcu212` worktree. Do not commit, push, or merge.

## Required repairs

### Roster fail-closed lifecycle

- Capture the roster command's exit code immediately.
- Reject nonzero, empty, non-integer, zero, or negative roster counts with a named nonzero failure before smoke/full/model work.
- Add deterministic launcher tests for each rejected shape and for the valid fake path. Preserve the existing stale-artifact and smoke/full lifecycle behavior.

### Truthful report interpreter/evidence

- Do not hardcode the report's interpreter. Use the active Python executable (`sys.executable`) or an explicit injected command propagated by the launcher/report interface. The fake launcher test must prove the selected command is used.
- `node_counts()` and `resolved_species_ids()` must not silently swallow malformed JSON. Return explicit malformed/error readings in the report (or fail the report with a named nonzero status); do not turn corrupt evidence into a clean zero/untouched result.
- Add a bounded fixture for malformed node JSON and malformed species JSON, and assert the artifact names the failure. Keep the report diagnostic-only where the existing contract says so; do not invent a corpus completion claim.

### Preserve the accepted prior work

- Keep serial `WORKERS = 1`, atomic result checkpoints, hard-gate propagation, resume metadata/mark correctness, collision-attempt persistence, and the existing report completeness join unless a test proves a defect.
- Do not hand-edit generated seed JSON. The captured evidence bundle is read-only and its hashes must remain unchanged.
- Do not alter the data-owned 50‰ gate or retry bounds to make tests pass.

## Verification

Run focused tests for the launcher/report and the touched Seedsmith paths, for example:

```powershell
$env:PYTHONPATH='gk-forge/tools/seedsmith'
python -m pytest gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py gk-forge/tools/seedsmith/tests/test_bcu212_report.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py -q
python -m py_compile gk-forge/tools/seedsmith/_j9_batch_run.py gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py .claude/cmdc-agents/scripts/bcu212-report.py
 git diff --check
```

Run the prior report's additional focused tree tests if a changed seam requires them. Do not run an unfiltered suite. Record exact commands, exit codes, changed files, evidence hashes, and the known verification-boundary mapping gap.

## Required report

Write `tasks/reports/seedsmith-p1-audit-final-20260925.md` with:

- the two manager-rejected findings and their reproductions;
- exact repairs and tests, including malformed evidence and roster failure cases;
- all prior audit findings carried forward, with no false claim that the 904-species corpus is complete;
- evidence hash before/after and proof no generated data changed;
- remaining risks, including the missing verification-boundary owner mapping and the separate generic-tree issue;
- a clear recommendation: safe to resume only after manager accepts this exact diff, or blocked/partial.

End with exactly:

```text
<<<REPORT {"status":"done|partial|blocked","summary":"...","changed_files":["..."],"verification":["..."],"open_issues":["..."],"next_steps":["..."]} REPORT>>>
```

Use `done` only when both manager-rejected gaps and the prior scoped repairs are actually covered. No model generation or live endpoint probe is authorized.

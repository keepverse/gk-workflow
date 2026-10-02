# SeedSmith P1 recovery audit — evidence-bundled retry

## Goal

Complete the interrupted Seedsmith/PassiveTree audit for BCU2.12 before any resume. The first audit worker was auto-rejected when it tried to read the separate `corpus-bcu212` worktree; this retry receives read-only copies of the captured log, ledger, and stale report inside its own worktree. Do not attempt external-directory access.

## Goal and hard rules

- Audit and repair only; do not resume or launch BCU2.12.
- Never edit `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `src/**`, CI/release files, or the original `corpus-bcu212` worktree.
- Generated seed JSON is disposable evidence, never a repair target.
- Use `opencode/space-bunny-free#max`; no fallback and no model-call cap.
- Make the smallest confirmed code/test/report fix, add a deterministic regression test, and leave the worktree dirty for manager review. Do not commit, push, or merge.

## Read first

Read `AGENTS.md`, `docs/DESIGN-GATE.md`, `docs/architecture/creature-seed-map.md`, `docs/architecture/creature-seed/spec-classify-pipelines.md`, `docs/architecture/creature-seed/spec-anchor-emit.md`, `docs/architecture/creature-seed/spec-run-control.md`, `docs/architecture/passive-tree-map.md`, `docs/architecture/passive-tree-ideal.md`, the PassiveTree content-completeness specs, `docs/architecture/validation-ssot.md`, `docs/contributing/testing-standard.md`, and `.agents/skills/seedsmith-passivetree-repair/SKILL.md`.

## Evidence bundle

The setup for this lane copies these files, read-only, to `tasks/evidence-fragments/seedsmith-p1-audit-recovery-20260925/`:

- `BCU2.12-run.log` — the interrupted detached-run log;
- `BCU2.12-run.err` — its stderr capture;
- `tree-language.ledger.json` — the persisted PassiveTree ledger;
- `BCU2.12-full-run.json` — the stale report artifact.

These copies are evidence, not corpus source. Do not edit them. The original files remain in the registered `corpus-bcu212` worktree. The first manager read found approximately 65,398 `call complete` records, 23 HTTP 500 lines, 22 HTTP 400 lines, 7 degenerate-generation aborts, 19 give-up lines, progress through species 361/904, 326 metadata writes, 35 non-writes, and 26 unresolved codex votes. Re-run the measurements rather than trusting these figures.

## Allowed paths

- `gk-forge/tools/seedsmith/_j9_batch_run.py`
- `gk-forge/tools/seedsmith/seedsmith/pipeline/**`
- `gk-forge/tools/seedsmith/seedsmith/adapters/trees/**`
- `gk-forge/tools/seedsmith/seedsmith/workflow/**`
- `gk-forge/tools/seedsmith/tests/**`
- `.claude/cmdc-agents/scripts/bcu212_full_run.py`
- `.claude/cmdc-agents/scripts/bcu212-report.py`
- `tasks/evidence-fragments/seedsmith-p1-audit-recovery-20260925/**` (read-only evidence; do not edit)
- `tasks/reports/seedsmith-p1-audit-recovery-20260925.md`

If the root cause needs another path, report the exact path and blocker; do not widen the fence.

## Investigation requirements

1. Parse the bundled log and quantify successful calls, streaming progress, HTTP 400/500, retries/give-ups, degenerate output, species progress, metadata writes, and unresolved codex/favour results. Map every material category to a source line.
2. Trace `_j9_batch_run.py` → `run_species_tree` → `run_language_stage` → LLM caller/retry → ledger → codex vote/metadata. Quantify expected calls per species and test the four-worker/one-request-endpoint hypothesis with a fake transport. Do not assume the hypothesis is true.
3. Reconcile ledger rows, node/species files, and progress. Classify each discrepancy as A generator, B persistence/wiring, C metric/gate, D stale evidence, or E incomplete run. A stopped process alone is not a generator defect.
4. Verify that retries do not duplicate a committed subject, that resume uses the ledger rather than regenerating completed subjects, and that codex retry/metadata persistence is truthful. Add focused failing-first tests for every confirmed defect.
5. Inspect the launcher/report lifecycle. Fix only a demonstrated stale-report, checkpoint, or process-observability defect; do not start a run.
6. Do not weaken error visibility, retry bounds, quality gates, or provenance rules. Do not pin population counts or generated text in tests.

## Verification

Run focused tests for the touched surface, at minimum:

```powershell
$env:PYTHONPATH='gk-forge/tools/seedsmith'
python -m pytest gk-forge/tools/seedsmith/tests/test_llm_caller.py gk-forge/tools/seedsmith/tests/test_run_ledger.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_codex.py -q
git diff --check
git status --porcelain
```

Run additional focused tests required by a real fix and record exact commands and exit codes. Do not run an unfiltered suite. Do not make live LM Studio calls unless a deterministic reproduction cannot answer a question; if one tiny probe is essential, cap it at one species and record the spend.

## Required report

Write `tasks/reports/seedsmith-p1-audit-recovery-20260925.md` containing exact evidence commands/readings, an A–E root-cause table with `file:line`, changed files, tests, before/after measurements, untouched-data proof, remaining environment failures, and a clear recommendation: safe to resume, not safe, or blocked pending a named fix.

End with exactly:

```text
<<<REPORT {"status":"done|partial|blocked","summary":"...","changed_files":["..."],"verification":["..."],"open_issues":["..."],"next_steps":["..."]} REPORT>>>
```

`done` means this scoped audit/fix is complete, not that the 904-species corpus is complete. Use `partial` or `blocked` when evidence does not support a fix or safe-resume conclusion.

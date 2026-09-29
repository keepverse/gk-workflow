# SeedSmith P1 recovery audit — BCU2.12 PassiveTree run

## Goal

Before any resume or relaunch, determine why the interrupted BCU2.12 species-tree run accumulated so many model calls and failures, fix only confirmed generator/runtime defects, and leave a falsifiable recovery recommendation. This is an audit-and-repair lane, not a generation lane.

The old run is in the registered worktree named `corpus-bcu212` on branch `corpus/bcu212`. Discover its absolute path with `git worktree list --porcelain`; read its files through `git -C`/read-only filesystem calls. Do not edit that worktree or any generated seed there.

## Binding context already loaded by the manager

Read these in this worktree before editing, and verify their claims against code and the captured evidence:

- `AGENTS.md`
- `docs/DESIGN-GATE.md` (especially §1, §2.15, §3, and §5)
- `docs/architecture/creature-seed-map.md`
- `docs/architecture/creature-seed/spec-classify-pipelines.md`
- `docs/architecture/creature-seed/spec-anchor-emit.md`
- `docs/architecture/creature-seed/spec-run-control.md`
- `docs/architecture/passive-tree-map.md`
- `docs/architecture/passive-tree-ideal.md` (especially D13–D16, D23–D24, §6, §17)
- `docs/architecture/seedsmith-content-standard/spec-content-completeness-passive-tree.md`
- `docs/architecture/seedsmith-content-standard/spec-passive-tree-identity-content.md`
- `docs/architecture/validation-ssot.md`
- `docs/contributing/testing-standard.md`
- `.agents/skills/seedsmith-passivetree-repair/SKILL.md`

## Evidence to reproduce (do not trust these numbers without re-running the read-only probes)

The manager's read-only audit found the following in `corpus-bcu212`:

- `tasks/reports/BCU2.12-run.log` is about 10 MB, with about 114,000 lines and 65,398 `call complete` records. It also contains HTTP 400/500 retries and degenerate-generation aborts. Treat these as log readings, not as a one-to-one request count.
- The log has no final `full_exit`, `FINISHED`, or `VERDICT JOB END` marker. Its last progress record is species 361 of 904 (`IronGargantuar`).
- The run ledger `gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json` has persisted rows and mixed terminal outcomes. The generated `nodes/` and `species/` trees are partial and must not be treated as complete.
- The run used `google/gemma-4-26b-a4b-qat` through LM Studio. The old launcher says the local model serves one request at a time while the J9 driver declares a worker pool; investigate that mismatch as a hypothesis, not as a conclusion.
- The existing `tasks/reports/BCU2.12-full-run.json` is stale relative to the log. Determine whether that is an expected pre-run snapshot or a reporting defect.
- No live `_j9_batch_run.py` process was present at audit time. Do not infer the cause of termination beyond “not currently running”; PC restart and abrupt process death remain hypotheses.

## Allowed paths

Edit only these paths in this lane:

- `gk-forge/tools/seedsmith/_j9_batch_run.py`
- `gk-forge/tools/seedsmith/seedsmith/pipeline/**`
- `gk-forge/tools/seedsmith/seedsmith/adapters/trees/**`
- `gk-forge/tools/seedsmith/seedsmith/workflow/**`
- `gk-forge/tools/seedsmith/tests/**`
- `.claude/cmdc-agents/scripts/bcu212-full-run.ps1`
- `.claude/cmdc-agents/scripts/bcu212-report.py`
- `tasks/reports/seedsmith-p1-audit-20260925.md`

Do not edit `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `src/**`, `gk-core/scripts/verification-boundaries.v1.json`, CI/release files, or any other Seedsmith domain. Generated corpus files are disposable evidence, never repair targets. If the root cause requires an out-of-fence change, report the exact file and blocker instead of widening this lane.

## Required investigation

1. Reproduce the log measurements with a bounded parser and identify the exact source lines for every material failure category: HTTP 400, HTTP 500, degenerate generation, retry/give-up, unresolved favour, unresolved codex vote, missing metadata, and process interruption.
2. Trace the call graph from `gk-forge/tools/seedsmith/_j9_batch_run.py` through `run_species_tree`, `run_language_stage`, the LLM caller, retry policy, codex voting, ledger writes, and metadata persistence. Quantify the expected calls per species and compare that contract with the observed run. Do not infer “one request per species” from the species count.
3. Determine whether the worker pool violates the endpoint's concurrency contract, whether retries are correctly classified as transient versus quality failures, and whether a retry can duplicate a paid/committed subject. Reproduce each suspected defect with a fake transport or deterministic fixture before changing code.
4. Reconcile ledger rows, generated node/species files, and progress records. Classify each discrepancy as generator (A), persistence/wiring (B), metric/gate (C), stale evidence (D), or incomplete run (E). A process stop alone is not a generator bug.
5. Verify the bounded codex retry and metadata write path. Explain every `metadataWritten=false`/unresolved result as either expected bounded failure, persistence defect, or unresolved quality; never hide it by weakening a gate.
6. Inspect the launcher/report lifecycle. If a fix is needed, make the smallest code/report change that makes an interrupted run observable and its report truthful, without starting a run.
7. Add focused regression tests for every fix. Tests must assert contracts and relationships, never pin a population count or generated text. Preserve the generator-first rule and existing provenance semantics.

## Repair policy

- Fix only a defect demonstrated by a failing deterministic test or a direct code/log contradiction.
- Do not “fix” an external LM Studio outage by hiding HTTP errors, infinite-retrying, clamping failures, or deleting hard cases.
- Do not change balance/tuning values, vocabulary meanings, or C# resolver behavior in this lane.
- Do not run the 904-species job, do not resume BCU2.12, and do not make unbounded live model calls. Prefer fake transports, dry runs, and log fixtures. If one tiny live probe is truly necessary, cap it at one species, record the exact command and spend, and stop.
- Leave the worktree dirty for manager review. Do not commit, push, or merge.

## Verification

Run focused tests for the touched surface, including the existing LLM-caller, ledger, J9, and species-tree tests. Also run:

```powershell
$env:PYTHONPATH='gk-forge/tools/seedsmith'
python -m pytest gk-forge/tools/seedsmith/tests/test_llm_caller.py gk-forge/tools/seedsmith/tests/test_run_ledger.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_codex.py -q
git diff --check
git status --porcelain
```

Run any additional focused test file required by a real fix and record it. Do not run an unfiltered suite. The manager will run path-owned acceptance after reviewing the diff.

## Required disk report and handoff

Write `tasks/reports/seedsmith-p1-audit-20260925.md` with:

- the exact captured-log commands and readings;
- a root-cause table classified A–E with `file:line` evidence;
- every changed file and why it is the responsible layer;
- exact test commands, exit codes, and relevant output;
- before/after measurements, clearly distinguishing log readings from code/test results;
- whether any generated evidence was touched (it must be `none`);
- unresolved environment failures, owner decisions, and next steps;
- a clear recommendation: safe to resume, not safe to resume, or blocked pending a named fix.

End the agent response with a machine-readable block exactly in this shape:

```text
<<<REPORT {"status":"done|partial|blocked","summary":"...","changed_files":["..."],"verification":["..."],"open_issues":["..."],"next_steps":["..."]} REPORT>>>
```

`done` means the scoped investigation and any confirmed fixes are complete; it does not mean BCU2.12 is finished. Use `partial` or `blocked` when the evidence does not support a fix or resume recommendation.

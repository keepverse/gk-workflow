# Manager acceptance review — Seedsmith BCU2.12 finalization

**Reviewed worker:** `seedsmith-p1-audit-final-20260925`  
**Review worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/review-seedsmith-p1-audit-20260925`  
**Review state:** **BLOCKED — not accepted and not merged**

## Evidence reviewed

The worker's disk-backed report was read in full. The manager copied the exact dirty code/test/report set into this clean worktree and independently checked the read-only evidence bundle. The evidence SHA-256 values remain:

- `BCU2.12-full-run.json`: `62BBFA53FED83959BEBECA101E786B1DD0984D880E7C1550B0AB59E63DB960A6`
- `BCU2.12-run.err`: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`
- `BCU2.12-run.log`: `8D92344AD00DE386EDABC571366D224E94BFE0C746CBB68D8902AAA9DBC3096F`
- `README.txt`: `21DCCC7831F4FB5191FACA9A4CC9C0D73C556AAA3B5C0B6CFC61AE22FC7F99AD`
- `tree-language.ledger.json`: `4F1D40CE071905AE10E855FD53EAFFB958AC17B1CEEBF0123FE787D918A2F13E`

`git diff --name-only -- gk-data/packs/fusion/data/seed gk-data/packs/fusion/data/generated src` and the corresponding untracked check returned no paths. No generated corpus or source data was changed.

## Manager review of the repaired code

The final source and focused tests were read. The two previously rejected gaps are covered in the copied source:

- the launcher captures roster output and `$LASTEXITCODE`, rejects nonzero/empty/non-integer/non-positive counts before smoke/full work, and propagates the selected interpreter to the report;
- the report preserves command status, accepts an explicit Python command, records malformed node/species artifacts, excludes them from complete/untouched readings, writes diagnostics, and returns nonzero after writing the report.

The prior serial worker, atomic checkpoints, hard-gate propagation, resume metadata/mark handling, collision-attempt persistence, and ledger/codex completeness join remain present. The captured run is still only a reading at 361/904; this review makes no corpus-completion claim and authorizes no resume.

## Independent commands run in this review worktree

```powershell
$env:PYTHONPATH='gk-forge/tools/seedsmith'
python -m pytest gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py gk-forge/tools/seedsmith/tests/test_bcu212_report.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py -q
# 40 passed, exit 0

python -m pytest gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py -q
# 52 passed, 9 subtests passed, exit 0

python -m py_compile gk-forge/tools/seedsmith/_j9_batch_run.py gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py .claude/cmdc-agents/scripts/bcu212-report.py gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py gk-forge/tools/seedsmith/tests/test_bcu212_report.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py
git diff --check
# exit 0
```

A refined path-owned verification excluding the two unmapped manager/launcher paths completed:

```powershell
$changed=@(
  'gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py',
  'gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py',
  'gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py',
  'gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py',
  'gk-forge/tools/seedsmith/tests/test_j9_batch_run.py',
  'gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py',
  'gk-forge/tools/seedsmith/tests/test_bcu212_report.py'
)
.\scripts\verify-change.ps1 -Paths $changed -Session seedsmith-p1-audit-acceptance-20260925
# 774 passed, 27 subtests passed, exit 0
```

## Blocking verification findings

1. The first path-owned attempt that included `gk-forge/tools/seedsmith/_j9_batch_run.py` selected `seedsmith-fallback (module)` and exceeded both the 120-second and 600-second command limits while running a broad Seedsmith selection. This is not accepted as evidence and was not retried as a broad suite.
2. The all-changed selection is explicitly blocked by the missing owner mapping for `.claude/cmdc-agents/scripts/bcu212-full-run.ps1`, as recorded in the worker report.
3. The current review worktree is intentionally dirty and has no exact manager commit/SHA or schema-valid acceptance artifact. Therefore this review cannot be GREEN or merged yet.

## Required next gate

The verification-topology owner must repair the launcher mapping and replace the broad `_j9_batch_run.py` fallback with a bounded owner mapping (without weakening the no-broad-fallback rule). Then the manager must rerun `verify-change.ps1` with every changed concrete path, commit the reviewed set at one exact SHA, verify a clean checkout, write/validate the acceptance artifact, and only then merge. Until then: **BLOCKED; do not resume BCU2.12.**

## Report marker

<<<REPORT {"status":"blocked","summary":"Manager independently reviewed the final Seedsmith code and direct deterministic tests, but cannot accept it because the path-owned verifier still selects a broad Seedsmith fallback for _j9_batch_run.py and the launcher has no owner mapping; no exact-SHA artifact or merge is claimed.","changed_files":["tasks/reports/seedsmith-p1-audit-acceptance-20260925.md"],"verification":["40 focused tests passed","52 tree tests and 9 subtests passed","27-test mapped verifier selection passed after excluding the two unmapped paths","py_compile and git diff --check passed","all-changed verifier remains blocked/timed out at the broad fallback boundary"],"open_issues":["verification-boundary owner mapping missing for bcu212-full-run.ps1","_j9_batch_run.py resolves to an overly broad seedsmith-fallback selection","no exact manager SHA or schema-valid acceptance artifact yet"],"next_steps":["repair the two verification-boundary mappings in the owning lane","rerun all changed paths through verify-change","commit and clean-checkout the reviewed SHA","write and validate acceptance artifact before merge","keep BCU2.12 resume blocked"]} REPORT>>>

# SeedSmith P1 audit finalization — BCU2.12

**Date:** 2026-09-25
**Scope:** close the two manager-rejected gaps in the evidence-bundled BCU2.12 audit. No BCU2.12 resume, model call, live endpoint probe, generated-data edit, commit, push, or merge was performed.

**Recommendation:** **safe to resume only after the manager accepts this exact dirty diff.** The repaired launcher is fail-closed, but the captured run is still incomplete at 361/904 and must not be described as a completed 904-species corpus. The separate generic-tree issue remains open.

## 1. Boundary and evidence

The session boundary was already recorded at `tasks/sessions/seedsmith-p1-audit-final-20260925.json` and the boundary check was clean before editing:

```powershell
python scripts/session-boundary-check.py --session seedsmith-p1-audit-final-20260925
```

Exit code: `0`; result: `clean for 'seedsmith-p1-audit-final-20260925'`.

The read-only evidence bundle is `tasks/evidence-fragments/seedsmith-p1-audit-final-20260925/`. No file in that bundle was edited. The copied report was read before editing. The prior report's stale report head was `b02f70bd1`; its 2,200-row ledger and absent batch-results file are not current truth.

### Evidence hashes

The hashes captured before this finalization and recomputed after the code/test work are identical. The after command was:

```powershell
Get-ChildItem -LiteralPath 'tasks/evidence-fragments/seedsmith-p1-audit-final-20260925' -File | Sort-Object Name | ForEach-Object { $h = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash; '{0} {1}' -f $_.Name,$h }
```

Exit code: `0`.

| Evidence file | Before SHA-256 | After SHA-256 |
|---|---|---|
| `BCU2.12-full-run.json` | `62BBFA53FED83959BEBECA101E786B1DD0984D880E7C1550B0AB59E63DB960A6` | `62BBFA53FED83959BEBECA101E786B1DD0984D880E7C1550B0AB59E63DB960A6` |
| `BCU2.12-run.err` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BCU2.12-run.log` | `8D92344AD00DE386EDABC571366D224E94BFE0C746CBB68D8902AAA9DBC3096F` | `8D92344AD00DE386EDABC571366D224E94BFE0C746CBB68D8902AAA9DBC3096F` |
| `README.txt` | `21DCCC7831F4FB5191FACA9A4CC9C0D73C556AAA3B5C0B6CFC61AE22FC7F99AD` | `21DCCC7831F4FB5191FACA9A4CC9C0D73C556AAA3B5C0B6CFC61AE22FC7F99AD` |
| `tree-language.ledger.json` | `4F1D40CE071905AE10E855FD53EAFFB958AC17B1CEEBF0123FE787D918A2F13E` | `4F1D40CE071905AE10E855FD53EAFFB958AC17B1CEEBF0123FE787D918A2F13E` |

The following read-only check produced no paths, proving that this lane changed no generated or source data:

```powershell
git diff --name-only -- gk-data/packs/fusion/data/seed gk-data/packs/fusion/data/generated src; git status --short -- gk-data/packs/fusion/data/seed gk-data/packs/fusion/data/generated src
```

Exit code: `0`; output: no path lines.

## 2. Manager-rejected finding 1 — roster command was not fail-closed

### Reproduction in the copied pre-fix source

`bcu212-full-run.ps1` previously assigned the roster command's stdout directly to `$rosterCount` and immediately announced it. It did not capture `$LASTEXITCODE`, reject empty or non-integer output, or reject a non-positive count. A fake roster command with any of these shapes could therefore reach the smoke and full phases:

- process exit `9` with output `904`;
- exit `0` with empty output;
- exit `0` with output `not-a-count`;
- exit `0` with output `0`;
- exit `0` with output `-1`.

That was an unsafe continuation because the count controls the unbounded run.

### Repair

At `.claude/cmdc-agents/scripts/bcu212-full-run.ps1:55-83`, the launcher now:

1. captures the roster command output and `$LASTEXITCODE` immediately;
2. normalizes the output to one trimmed string;
3. rejects nonzero exit, empty output, non-integer output, and values `<= 0` with named `ROSTER_FAILURE` statuses;
4. exits `1` before smoke, full, resume, census, or report work for every rejected shape.

The existing stale-artifact invalidation and smoke/full lifecycle checks remain in place. The report invocation at `.claude/cmdc-agents/scripts/bcu212-full-run.ps1:118` now receives the same selected Python command through `--python`.

### Deterministic coverage

`gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py` covers all five rejected shapes and the valid path. Each rejection asserts one roster call, no smoke marker, nonzero exit, the named failure, and removal of stale results/report artifacts. The valid fake-path test asserts roster, smoke, full, resume, census, and report exits are zero and records the selected `python.cmd` plus `--python` in the fake command's argument log.

## 3. Manager-rejected finding 2 — report interpreter and malformed evidence were untruthful

### Reproduction in the copied pre-fix source

`bcu212-report.py` previously shelled to a literal `python` for roster and family-check commands. A launcher-injected interpreter was not propagated into those reads. `node_counts()` and `resolved_species_ids()` caught every exception and used `continue`, so malformed node or species JSON disappeared from the maps. A corrupt file could consequently become an apparent zero-node, untouched, or ordinary unresolved reading.

### Repair

At `.claude/cmdc-agents/scripts/bcu212-report.py:61-145`:

- `sh()` now preserves both output and process status;
- `roster_ids()` accepts the selected command and fails explicitly on command failure or empty output;
- `node_counts()` and `resolved_species_ids()` validate document shape and route every malformed artifact to an error sink;
- direct callers without a sink raise `MalformedEvidenceError` rather than silently skipping;
- relative artifact names and exception details are retained in the report.

At `.claude/cmdc-agents/scripts/bcu212-report.py:148-279`, `main()` uses `sys.executable` by default, accepts explicit `--python`, propagates that command to roster and family-check subprocesses, excludes malformed roster artifacts from `untouched`/`complete`, writes `evidenceErrors`, `census.malformedEvidence`, `commandErrors`, `evidenceStatus`, and `reportStatus`, then returns nonzero after saving the diagnostic artifact. No corpus completion claim is made by the report.

### Bounded fixtures and coverage

`gk-forge/tools/seedsmith/tests/test_bcu212_report.py` now proves:

- the selected command reaches `roster_ids()` and the family-check subprocess;
- malformed node JSON names `BrokenNode.json`, returns report status `error`, and cannot become `untouched` or `complete`;
- malformed species JSON names `BrokenSpecies.json`, returns report status `error`, and cannot become `untouched` or `complete`;
- the report still writes its artifact before returning the named nonzero status.

The report remains diagnostic-only with respect to corpus health: it records readings and explicit failures; it does not declare the 904-species run complete.

## 4. Prior audit findings carried forward

The following findings from the recovery audit remain valid and are not erased by this finalization:

| Class | Finding carried forward | Current disposition |
|---|---|---|
| A — generator | No confirmed generator-content defect was established. The captured 9 favour and 26 codex outcomes are named bounded outcomes; seven degenerate-generation events are visible. | Keep retry bounds and the data-owned gate; do not hand-edit seeds or weaken thresholds. |
| B — persistence/wiring | The captured run used four concurrent workers against a one-request endpoint. | `gk-forge/tools/seedsmith/_j9_batch_run.py:62-66` keeps `WORKERS = 1`; the deterministic overlap test remains. |
| B — resume truth | The old path redrew completed favour/codex work and calculated marks from only current outcomes. | `generate_tree.py` reuses validated persisted state, computes marks from the full emitted tree, and preserves unchanged supplement bytes/mtime. |
| B — collision persistence | Same-batch name collisions previously returned before `record_attempt`, losing unresolved attempt rows. | `nodegen/run.py:1217-1229` persists the named unresolved attempt with `record: null`; the collision regression remains. |
| C — hard gate | `run_language_stage` recorded the `PassiveTree/UnresolvedCount` result but the species caller ignored a non-PASS report. | `SpeciesTreeGateFailure` stops before codex, checkpoints the failure row, and propagates a nonzero batch exit. The 50‰ data-owned gate is unchanged. |
| C — report completeness | File existence alone could count a named null-summary failure as complete, and ledger backing was not required. | The report requires a real codex summary, at least 40 ledger-backed accepted nodes, and 40 node rows. Named hard-gate rows remain visible. |
| C — lifecycle | Smoke/full/resume/check/report failures and stale artifacts were not all fail-closed. | Smoke failure stops; failed full skips resume; all lifecycle exits are aggregated; stale batch/report artifacts are invalidated. This finalization adds the roster gate and selected-interpreter propagation. |
| D — stale evidence | The copied `BCU2.12-full-run.json` is stale and cannot replace the captured log/ledger join. | Never use it as a current census. |
| E — incomplete run | The captured full segment reached result 361/904; 352 species reached tree/codex, 9 favour outcomes were unresolved, and 26 codex outcomes reached the six-draw bound. | Resume work remains ledger-backed and fail-closed. The 904 roster is a population reading, not a completion claim. |
| E/C — generic tree | `gk-data/packs/fusion/data/seed/passive-tree/nodes/wither.json` has 39 nodes while its plan requires 40; `skill.wither-def-t9-n1` is absent. | Separate generator-led J13 follow-up; no hand edit and no regeneration in this lane. |

The captured ledger contains 15,597 rows: 13,918 species rows across 352 reached species, 8,485 accepted species rows, 5,433 `record: null` rows, and 62 superseded rows. The structural 40-node plan for those 352 reached species leaves 162 rows absent in the historical evidence. The current 352 node/species files are not present in the read-only bundle, so their disk-level reconciliation remains `NOT_MEASURED`.

The first known current-pass hard-gate offender remains `BlackFootball_c2` at 3/40 unresolved (75‰). The captured run has 268 current-pass rows above the data-owned 50‰ threshold; the repaired execution is expected to stop non-zero at the first reproduced offender. No threshold or retry bound was changed.

## 5. Preserved prior repairs and changed files

The accepted prior changes remain present and were not reverted:

- serial worker selection;
- atomic empty/prefix result checkpoints;
- hard-gate propagation and failed-row visibility;
- resume metadata reuse and full-tree mark calculation;
- collision-attempt ledger persistence;
- report ledger/codex completeness join and hard-gate visibility;
- stale-artifact invalidation and smoke/full lifecycle behavior.

This finalization changed only the launcher/report and their focused tests, plus this report. It did not edit `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `src/**`, CI, release files, retry bounds, or the 50‰ gate.

## 6. Verification record

### Required focused pytest

The requested focused launcher/report/Seedsmith command was run in this worktree:

```powershell
$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py gk-forge/tools/seedsmith/tests/test_bcu212_report.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py -q
```

Exit code: `0`; result: **40 passed**.

### Additional prior tree/report coverage

```powershell
$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py -q
```

Exit code: `0`; result: **52 passed, 9 subtests passed**.

### Scoped verification boundary

The mapped Seedsmith tree/test paths were run through the path-owned verifier:

```powershell
$changed = @(
  'gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py',
  'gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py',
  'gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py',
  'gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py',
  'gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py',
  'gk-forge/tools/seedsmith/tests/test_bcu212_report.py'
)
.\scripts\verify-change.ps1 -Paths $changed -Session seedsmith-p1-audit-final-20260925
```

Exit code: `0`; result: **752 passed, 27 subtests passed**. The verifier labelled this `seedsmith-trees (focused)` and stated that full evidence is CI/nightly/release-owned. No unfiltered suite was used as a fallback.

### Syntax and whitespace

```powershell
python -m py_compile gk-forge/tools/seedsmith/_j9_batch_run.py gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py .claude/cmdc-agents/scripts/bcu212-report.py gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py gk-forge/tools/seedsmith/tests/test_bcu212_report.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py
```

Exit code: `0`.

```powershell
git diff --check
```

Exit code: `0`.

The final scoped state was recorded with:

```powershell
git status --short --branch
```

Exit code: `0`; output contained only the allowed BCU2.12 scripts, Seedsmith source/tests, the read-only evidence bundle, and this report. No generated or source-data path was present.

### Known verification-boundary mapping gap

The all-changed scoped verifier was also attempted:

```powershell
.\scripts\verify-change.ps1 -Paths $changed -Session seedsmith-p1-audit-final-20260925
```

with `$changed` containing the launcher/report, Seedsmith source/tests, and this report. Exit code: `1`, with the exact blocker:

```text
VERIFICATION BOUNDARY MISSING: .claude/cmdc-agents/scripts/bcu212-full-run.ps1. Add an owner mapping; do not run a broad suite as a fallback.
```

The mapping file is outside this lane's allowed paths, so this is recorded as an open verification-topology issue. The direct focused pytest and mapped Seedsmith verifier results above are the evidence for this lane; no broad retry was attempted.

## 7. Remaining risks and recommendation

1. The current 352 species node/species files are absent from the evidence bundle; disk reconciliation is `NOT_MEASURED`, not `PASS`.
2. The generic `wither` tree remains one node short of its 40-node plan and needs a separate generator-led J13 repair.
3. The captured run has 268 current-pass rows over the 50‰ unresolved-rate gate. A resumed run must stop non-zero at the first reproduced failure; that is intended behavior.
4. The launcher path has no verification-boundary owner mapping. The mapping must be repaired by its owning verification-topology lane; it is not safe to compensate with an unfiltered suite.
5. No live model endpoint was probed. The serial-worker conclusion is based on the captured HTTP burst and a deterministic fake one-request transport, not a new endpoint claim.

**Recommendation:** do not resume in this worktree. After manager acceptance of this exact diff and integration into the intended corpus worktree, a monitored resume may use the repaired launcher, retain `WORKERS = 1`, and accept an early non-zero hard-gate stop. Do not call the corpus complete until the 904-species census is actually reconciled and the separate generic-tree gap is resolved. Do not hand-edit generated JSON.

The worktree is intentionally dirty for manager review. No commit, push, merge, generation run, or live model call was performed.

<<<REPORT {"status":"done","summary":"Closed both manager-rejected BCU2.12 gaps: roster-command exit/output/positive-integer validation now fails before smoke/full work, and the report uses the propagated selected interpreter while naming malformed node/species evidence and returning a named error after saving diagnostics. Prior serial, checkpoint, resume, collision-ledger, hard-gate, and completeness repairs remain covered. The captured run is still incomplete at 361/904; resume is gated on manager acceptance of this exact diff.","changed_files":[".claude/cmdc-agents/scripts/bcu212-full-run.ps1",".claude/cmdc-agents/scripts/bcu212-report.py","gk-forge/tools/seedsmith/_j9_batch_run.py","gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py","gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py","gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py","gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py","gk-forge/tools/seedsmith/tests/test_j9_batch_run.py","gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py","gk-forge/tools/seedsmith/tests/test_bcu212_report.py","tasks/reports/seedsmith-p1-audit-final-20260925.md"],"verification":["required focused pytest: 40 passed, exit 0","additional tree pytest: 52 passed, 9 subtests passed, exit 0","mapped Seedsmith verify-change: 752 passed, 27 subtests passed, exit 0","py_compile of changed Python files: exit 0","git diff --check: exit 0","git status --short --branch: exit 0, only allowed scoped paths dirty","evidence SHA-256 before/after: identical; generated/source diff check: no paths","session-boundary-check: clean for seedsmith-p1-audit-final-20260925","all-changed verify-change: exit 1, known missing mapping for bcu212-full-run.ps1"],"open_issues":["current 352 species node/species files are absent from the evidence bundle; disk reconciliation is NOT_MEASURED","generic wither tree lacks skill.wither-def-t9-n1 and requires a separate generator-led J13 follow-up","captured run has 268 current-pass rows above the data-owned 50‰ UnresolvedCount threshold; resumed execution must stop fail-closed","verification-boundary owner mapping is missing for .claude/cmdc-agents/scripts/bcu212-full-run.ps1","no live endpoint probe or corpus completion claim was made"],"next_steps":["manager reviews and accepts this exact dirty diff","verification-topology owner repairs the launcher mapping","only then resume from the intended corpus worktree with the repaired fail-closed launcher; do not launch the old four-worker command"]} REPORT>>>

# SeedSmith P1 audit recovery — BCU2.12

**Date:** 2026-09-25
**Scope:** evidence-bundled audit and deterministic repair only; no BCU2.12 resume was launched.
**Recommendation:** **safe to resume only through the repaired, fail-closed launcher after manager review**. It is not safe to resume with the pre-fix four-worker launcher, and a resumed run must not be treated as a completed 904-species corpus. The repaired run is expected to stop at the first reproduced unresolved-rate gate failure; that is the intended safety behavior.

## 1. Boundary and evidence

The audit used only the read-only copies under `tasks/evidence-fragments/seedsmith-p1-audit-recovery-20260925/`. The original `corpus-bcu212` worktree and external directories were not read. No model call was made. No `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `src/**`, CI, release, or generated corpus file was edited.

Evidence hashes before and after the audit were identical:

| Evidence file | SHA-256 |
|---|---|
| `BCU2.12-run.log` | `8D92344AD00DE386EDABC571366D224E94BFE0C746CBB68D8902AAA9DBC3096F` |
| `BCU2.12-run.err` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `tree-language.ledger.json` | `4F1D40CE071905AE10E855FD53EAFFB958AC17B1CEEBF0123FE787D918A2F13E` |
| `BCU2.12-full-run.json` | `62BBFA53FED83959BEBECA101E786B1DD0984D880E7C1550B0AB59E63DB960A6` |
| `README.txt` | `21DCCC7831F4FB5191FACA9A4CC9C0D73C556AAA3B5C0B6CFC61AE22FC7F99AD` |

`BCU2.12-run.err` is empty apart from its zero-length-file hash. The copied report is explicitly stale: its head is `b02f70bd1`, it reports only 2,200 ledger rows, 12 started-incomplete species, and an absent batch-results file. The log's last completed result is species 361, so that report is not current truth.

### Exact measurement commands

The following in-worktree command was run with exit code `0`. It parsed only the bundled log, ledger, and report, split the log at `=== full run`, and emitted the following readings:

```powershell
@'
from collections import Counter
from pathlib import Path
import hashlib, json, re
root = Path('tasks/evidence-fragments/seedsmith-p1-audit-recovery-20260925')
log = root / 'BCU2.12-run.log'
rows = []
segment = 'smoke'
counts = {'smoke': Counter(), 'full': Counter()}
for line_no, line in enumerate(log.open(encoding='utf-8-sig'), 1):
    if line.startswith('=== full run'):
        segment = 'full'
    for key, marker in {
        'calls': 'call complete,', 'progress': 'chars received so far',
        'http400': 'HTTP Error 400', 'http500': 'HTTP Error 500',
        'giveups': 'giving up', 'degenerate': 'DegenerateGenerationError',
    }.items():
        if marker in line:
            counts[segment][key] += 1
    match = re.match(r'^\[(\d+)/(\d+)\]\s+(\{.*\})$', line.rstrip())
    if match:
        row = json.loads(match.group(3)); row['_line'] = line_no; row['_segment'] = segment
        row['_progress'] = int(match.group(1)); row['_total'] = int(match.group(2)); rows.append(row)
full = [r for r in rows if r['_segment'] == 'full']
done = json.loads((root / 'tree-language.ledger.json').read_text(encoding='utf-8-sig'))['done']
generic = {
    'agility','air','blight','bond','bulwark','butter','charm_pulse','cold','command','composure',
    'dark','earth','ember','expose','ferocity','fire','focus','fortitude','freeze','hypno','ice',
    'jala','kelp','leech','light','might','nerve.afflicted','nerve.shaken','nerve.unsettled',
    'onslaught','pact_mark','pierce','poison','precision','rally','retribution','rot','shatter',
    'spark','spore','vigor','wither',
}
species = {k.split(':', 1)[0] for k in done if k.split(':', 1)[0] not in generic}
print(json.dumps({
    'hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest().upper() for p in sorted(root.iterdir()) if p.is_file()},
    'segments': {k: dict(v) for k, v in counts.items()},
    'fullRows': len(full), 'progress': f'{full[-1]["_progress"]}/{full[-1]["_total"]}',
    'metadataWritten': sum(bool(r.get('metadataWritten')) for r in full),
    'metadataNotWritten': sum(not bool(r.get('metadataWritten')) for r in full),
    'favourUnresolved': [r['speciesId'] for r in full if r.get('favourUnresolvedReason')],
    'codexUnresolvedCount': sum(bool(r.get('codexUnresolvedReason')) for r in full),
    'ledgerRows': len(done), 'speciesTrees': len(species),
    'speciesRows': sum(k.split(':', 1)[0] in species for k in done),
    'missingSpeciesRows': len(species) * 40 - sum(k.split(':', 1)[0] in species for k in done),
}, indent=2))
'@ | python
```

The exact output included:

- smoke/full successful calls: `21 / 65,377` (`65,398` total);
- smoke/full streaming progress markers: `3 / 48,376` (`48,379` total);
- HTTP 400: `0 / 22`; HTTP 500: `2 / 21` (`23` total);
- give-ups: `0 / 19`; degenerate-generation aborts: `0 / 7`;
- full result rows: `361`; progress: `361/904`;
- metadata: `326` writes and `35` non-writes in the full segment;
- favour unresolved: `9`; codex unresolved: `26`;
- ledger: `15,597` rows, `352` reached species trees, `13,918` species rows, `162` missing rows against the structural 40-node plans.

A second in-worktree parser counted the material log categories and structural call minimum with exit code `0`. It found all full-run HTTP errors in lines `17,523–17,682`: `43` records (`22` HTTP 400, `21` HTTP 500, including all `19` give-ups). The first current-pass unresolved-rate gate failure is result row `29`, `BlackFootball_c2`, at log line `1,754`, with `3/40` unresolved (`75‰`). There are `268` such current-pass rows. The structural minimum for the observed pass is `37,242` successful calls (`361*3` favour samples + `11,336*3` node samples + `717*3` codex samples), versus `65,377` observed; the `28,135` excess is bounded quality-repair output, not evidence of a silent retry loop.

## 2. Flow and source trace

1. `gk-forge/tools/seedsmith/_j9_batch_run.py:206-275` loops roster species, calls `run_species_tree`, finalizes codex, and checkpoints the result prefix. The pre-fix `WORKERS = 4` was at line 62; it is now `WORKERS = 1` at line 66.
2. `gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py:193-209` now reads a persisted mechanical favour/codex supplement before spending a new favour call. A resolved supplement is reused; a named null-summary failure reuses its favour but retries codex.
3. `generate_tree.py:216-244` builds the species plan and calls `run_language_stage`; `nodegen/run.py:1245-1284` applies outcomes in deterministic subject order and writes the ledger before emitting the node document (`run.py:1286-1302`).
4. `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:282-289` emits streaming progress and raises `DegenerateGenerationError`; `:358-374` emits successful completion and performs bounded transport/degenerate retry handling.
5. `generate_tree.py:285-329` computes `speciesUniqueNodeIds` from the full emitted node document, not only the current pass. An unchanged resolved supplement is read without rewriting (`generate_tree.py:303-311`).
6. `generate_codex.py:37-50` keeps the six-draw total bound. `_j9_batch_run.py:125-160` retries only the unresolved species; `finalize_codex` writes either a resolved supplement or a named null-summary failure.
7. The language-stage hard gate is calculated at `nodegen/run.py:1304-1314`. The pre-fix species caller ignored that report. It now raises `SpeciesTreeGateFailure` before codex at `generate_tree.py:98-99,260-271`; the batch driver checkpoints that named failure and re-raises at `_j9_batch_run.py:243-249`.

Expected call shape per fresh species is `3` favour samples + `3*40` node samples + `3` codex samples = `126` successful samples when codex resolves on draw 1. Draw `d` costs `123 + 3d`; the six-draw bound is `141`. An unresolved favour costs three samples and never reaches nodes. A fake one-request transport test (`tests/test_j9_batch_run.py:93-132`) observed all three codex samples in flight together under `workers=4`; the production BCU2.12 driver is now serial. This is evidence for the endpoint/wiring diagnosis, not a live endpoint claim.

## 3. Reconciliation

### Species and metadata

The full segment reconciles exactly at the species level:

- `361` completed result rows = `352` species that reached tree/codex + `9` unresolved favour rows;
- the copied ledger contains exactly those same `352` reached tree species, with no completed tree species missing from the ledger and no ledger tree species missing from the completed result set;
- `326` rows have a real resolved codex summary and metadata write; `35` do not;
- the `35` non-writes partition into `26` named codex bound failures and `9` unresolved favour rows. The 26 codex rows all carry `codexAttempts == 6`, a non-empty failure reason, and `failureRecordWritten == true`; the 9 favour rows carry no codex attempt and no metadata write;
- full-pass codex draw distribution is `{0: 9, 1: 208, 2: 59, 3: 29, 4: 12, 5: 8, 6: 36}`.

Unresolved favour species:

`CherryPaperZombie`, `CornBlover`, `CornUmbrella`, `DarkThreePeater`, `DoomZombie`, `GarlicCorn`, `GatlingPaper_c`, `GoldZombie`, `HelmetGatling`.

Unresolved codex species at the six-draw bound:

`Apple`, `ArmoredImpZombie`, `CabbageMelon`, `Caltrop`, `CaltropKelp_land`, `CherryHypno`, `DeathChomper`, `DoomFume`, `DoomSeed`, `DoomSniper`, `DoubleShooter`, `Extract_single`, `FireSunshroom_b`, `FireSunshroom_c`, `FlagZombie`, `Gargantuar`, `GoldIceShroom`, `GoldMagnet`, `GreenGargantuar`, `HypnoDoom`, `IFVPumpkin`, `IFVStar`, `IceBean`, `IceCherry`, `IceFurnace`, `IceSquash`.

These are named bounded outcomes, not silently accepted content. The first 26 are retried by the bounded codex path on resume; the 9 favour rows have no tree and are retried from favour. `137` resolved metadata rows had fewer than eight current-pass marks because the old code calculated marks from only current outcomes. The full emitted-tree regression now proves eight marks on a resumed species and preserves the existing supplement bytes/mtime when unchanged.

### Ledger and node files

The copied ledger has:

- `15,597` total rows;
- `1,679` generic rows;
- `13,918` species rows across `352` reached species;
- `8,485` accepted species rows, `5,433` `record: null` rows, and `62` superseded rows;
- `352*40 = 14,080` structural species subjects, leaving `162` rows absent.

The `162` discrepancy is attributed to the same-batch name-collision branch: before the repair it returned an in-memory unresolved outcome before `record_attempt`; the current code persists that attempt at `nodegen/run.py:1217-1229`. The focused regression now requires the unresolved subject to exist in the ledger with `record: null`, `outcome: unresolved`, and `attempts: 1`. The copied corpus itself was not regenerated, so the measured historical count remains 162.

The current species node/species files are **NOT_MEASURED** from this evidence bundle: it contains no 352 current node documents or current species supplements. The stale report cannot fill that gap. The report script now refuses to call a species complete unless it has at least 40 nodes, at least 40 ledger-backed accepted rows, and a non-empty codex summary (`bcu212-report.py:60-75,110-127`).

A separate read-only check of the checked-in local baseline found `gk-data/packs/fusion/data/seed/passive-tree/nodes/wither.json` has 39 nodes and lacks `skill.wither-def-t9-n1`; the 42 generic plans each contain 40 nodes. This is a real incomplete generic-tree gap, but it is outside the BCU2.12 species run (the launcher explicitly excludes J13) and was not edited or regenerated.

The interrupted process was in the next species after result 361. Its absence from the result/ledger join is therefore an **incomplete-run** condition, not evidence of a lost committed subject.

## 4. A–E root-cause classification

| Class | Finding | Evidence and source | Disposition |
|---|---|---|---|
| A — generator | No confirmed generator-content defect was established. The 9 favour and 26 codex results are named bounded outcomes; seven degenerate generations are visible and bounded. | Log rows; `llm_caller.py:282-289,358-374`; `generate_codex.py:37-50` | Do not hand-edit seed JSON or weaken retries/threshold. |
| B — persistence/wiring | Four concurrent workers were sent to a one-request endpoint. | Pre-fix `_j9_batch_run.py:62`; HTTP burst isolated to log lines 17,523–17,682; fake overlap test `test_j9_batch_run.py:93-132` | Serial BCU2.12 driver; retry bounds unchanged. |
| B — persistence/wiring | Resume redrew completed favour/codex work and calculated marks from only current outcomes. | `generate_tree.py:193-209,285-329`; observed 137 short-mark rows; resume regression | Reuse validated metadata, compute from full emitted tree, do not rewrite unchanged supplements. |
| B — persistence/wiring | Same-batch collision returned before `record_attempt`, losing 162 attempt rows. | `nodegen/run.py:1217-1229`; ledger count reconciliation; collision regression | Persist named unresolved attempt while keeping `record: null` for retry. |
| C — metric/gate | `run_language_stage` recorded `PassiveTree/UnresolvedCount`, but the species caller ignored a non-PASS report. | `run.py:1304-1314`; 268 current-pass rows over 50‰; first `BlackFootball_c2` at 75‰; hard-gate regression | Raise before codex and make the batch exit non-zero. The threshold remains the data-owned 50‰ value. |
| C — metric/gate | Stale report treated any metadata file, including a named null-summary failure, as complete; it also did not require ledger backing. | `bcu212-report.py:60-75,110-127`; report regression | Require real codex + 40 ledger-backed nodes; expose hard-gate rows. |
| C — process/gate | Launcher could continue after smoke failure and could finish green despite full/resume/check/report failures; old result/report artifacts could survive an attempt. | `bcu212-full-run.ps1:42-99`; launcher smoke/full failure tests | Invalidate artifacts, inject testable Python command, stop on smoke, aggregate all lifecycle exits. |
| C/E — completeness | Generic `wither` has one missing planned node although all 42 plans require 40. | Read-only local `wither.json` count 39; plan count 40; no edit | Separate J13 follow-up; not silently repaired in this audit. |
| D — stale evidence | Report head `b02f70bd1` and ledger count 2,200 predate the run log head/content; batch file is absent from that report. | Evidence hashes and stale report fields above | Never use the stale report as current census; launcher invalidates it. |
| E — incomplete run | Progress is 361/904; 5,433 species ledger rows remain null; 9 favour and 26 codex outcomes remain named work; one species was in flight. | Log/ledger/result reconciliation above | Resume ledger-backed work; do not call the corpus complete. |

## 5. Changes made (all uncommitted)

- `gk-forge/tools/seedsmith/_j9_batch_run.py`: serial worker, atomic empty/prefix result checkpoints, hard-gate propagation, and visibility of the failed gate row.
- `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py`: persist same-batch collision attempts.
- `gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py`: validate/reuse persisted favour/codex state, calculate marks from the full tree, preserve unchanged metadata, and enforce the language hard gate.
- `.claude/cmdc-agents/scripts/bcu212-report.py`: distinguish real codex supplements from named failures, require ledger backing, and report hard-gate rows.
- `.claude/cmdc-agents/scripts/bcu212-full-run.ps1`: invalidate stale artifacts, make the Python command injectable for a deterministic lifecycle test, stop on smoke failure, skip resume after failed full, and return non-zero on any lifecycle failure.
- `gk-forge/tools/seedsmith/tests/test_j9_batch_run.py`: serial-endpoint proof, result checkpoint/empty-file regressions, hard-gate propagation, and retry-bound coverage.
- `gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py`: resume/full-mark/mtime regression and hard-gate regression.
- `gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py`: collision attempt-ledger regression.
- `gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py`: smoke-failure and failed-full lifecycle regressions.
- `gk-forge/tools/seedsmith/tests/test_bcu212_report.py`: completeness join and hard-gate visibility regression.

No LLM caller, retry-bound, model/provenance, or generated-data file was changed.

## 6. Before/after evidence

| Defect | Before | After (deterministic proof) |
|---|---|---|
| Worker/endpoint wiring | BCU2.12 driver selected 4; all 43 full HTTP error records were one 160-line cluster with all 19 give-ups. | Driver selects 1; fake `workers=4` test still proves overlap, while the driver assertion proves serial selection. No live endpoint claim. |
| Result durability | Old driver wrote only at the end; interrupted run had no current result artifact. | Atomic empty file at invocation start and replace after every terminal species; interruption tests preserve the completed prefix and clear stale smoke rows. |
| Resume marks | 137 resolved metadata rows in the captured pass had fewer than 8 current-pass marks. | Full emitted tree produces 8 marks on resume; unchanged metadata bytes and fixed mtime are preserved. |
| Collision attempts | 162 planned species rows were absent from the copied ledger. | Synthetic collision regression requires the unresolved attempt row; historical corpus remains untouched. |
| Report completeness | Named null-summary failure files could be counted as complete; stale report could be reused. | Regression requires non-empty codex plus 40 ledger-backed nodes; stale artifacts are invalidated and hard-gate rows are visible. |
| Launcher lifecycle | Smoke/full failure paths were not fail-closed; old artifacts could look current. | Fake smoke exits 7 and full exits 9; both return non-zero, skip unsafe continuation, remove stale artifacts, and emit the failed verdict. |
| Hard gate | 268 current-pass rows exceeded the data-owned 50‰ threshold while the run continued. | Regression lowers the threshold only in an isolated fixture, proves `UnresolvedCount` failure, and proves no codex call occurs. The production threshold was not changed. |

## 7. Verification record

### Passing focused tests

The required command from the brief was run exactly:

```powershell
$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/test_llm_caller.py gk-forge/tools/seedsmith/tests/test_run_ledger.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_codex.py -q
```

Exit code: `0`; result: **93 passed**.

Additional focused tree/report/launcher coverage:

```powershell
$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py gk-forge/tools/seedsmith/tests/test_bcu212_report.py gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py -q
```

Exit code: `0`; result: **55 passed, 9 subtests passed**.

The path-owned tree verification command was run with the session id:

```powershell
$changed = @(
  'gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py',
  'gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py',
  'gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py',
  'gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py',
  'gk-forge/tools/seedsmith/tests/test_j9_batch_run.py',
  'gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py',
  'gk-forge/tools/seedsmith/tests/test_bcu212_report.py'
)
.\scripts\verify-change.ps1 -Paths $changed -Session seedsmith-p1-audit-recovery-20260925
```

Exit code: `0`; result: **765 passed, 27 subtests passed in 91.00s**. The script labels this `seedsmith-trees (focused)` and states that full evidence is CI/nightly/release-owned.

Syntax compilation of all changed Python files and new tests exited `0`:

```powershell
python -m py_compile gk-forge/tools/seedsmith/_j9_batch_run.py gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py .claude/cmdc-agents/scripts/bcu212-report.py gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py gk-forge/tools/seedsmith/tests/test_bcu212_report.py gk-forge/tools/seedsmith/tests/test_j9_batch_run.py gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py
```

### Failing-first and verification-boundary record

- Baseline before edits: **87 passed**.
- The earlier focused failing-first batch recorded **4 expected failures, 22 passed** before the corresponding repairs.
- The new hard-gate test failed before its repair with `ValueError not raised`; the new stale-result test failed before its repair with the stale row still present. Both pass after their fixes.
- The all-changed `verify-change.ps1` attempt, including the launcher/report paths, exited `1` with `VERIFICATION BOUNDARY MISSING: .claude/cmdc-agents/scripts/bcu212-full-run.ps1`. The session fence does not allow repairing the mapping file, so this remains an environment/verification-topology failure rather than a reason to run a broad suite.
- A separate attempt that included `_j9_batch_run.py` selected its `seedsmith-fallback (module)` and began an unfiltered seedsmith run; it was terminated by the 120-second tool timeout at 13% and is **not** used as evidence. No full suite result is claimed.

`git diff --check` and the final `git status --porcelain` were run after this report was written:

```text
$ git diff --check
EXIT_CODE=0

$ git status --porcelain=v1
 M .claude/cmdc-agents/scripts/bcu212-full-run.ps1
 M .claude/cmdc-agents/scripts/bcu212-report.py
 M gk-forge/tools/seedsmith/_j9_batch_run.py
 M gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py
 M gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py
 M gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py
 M gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py
 M gk-forge/tools/seedsmith/tests/test_j9_batch_run.py
?? tasks/evidence-fragments/seedsmith-p1-audit-recovery-20260925/
?? tasks/reports/seedsmith-p1-audit-recovery-20260925.md
?? gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py
?? gk-forge/tools/seedsmith/tests/test_bcu212_report.py
EXIT_CODE=0

$ forbidden-path check
NO_FORBIDDEN_PATH_CHANGES
EXIT_CODE=0
```

## 8. Remaining issues and resume recommendation

1. The current 352 species node/species files are absent from the evidence bundle. Their disk-level reconciliation is explicitly `NOT_MEASURED`; the stale report cannot substitute for them.
2. The checked-in generic `wither` tree is one node short of its 40-node plan (`skill.wither-def-t9-n1`). This is a separate J13 completeness issue and requires a generator-led follow-up; no hand edit is permitted here.
3. The `UnresolvedCount` threshold is a data-owned starting value and was not weakened. The captured run has 268 current-pass failures above it, so the repaired driver will fail closed rather than silently continue. The first known reproduced offender is `BlackFootball_c2` at 3/40 unresolved.
4. No live LM endpoint probe was run. The one-request/concurrency conclusion is supported by the captured burst plus a deterministic overlapping fake transport, as allowed by the brief.
5. The 26 codex failures and 9 favour failures remain named work for the ledger-backed resume; they are not fabricated successes.

**Recommendation: safe to resume as a monitored, fail-closed continuation after manager review and integration of this uncommitted diff into the corpus worktree.** Use the repaired launcher, keep the serial worker, and accept an early non-zero hard-gate stop as correct. Do not launch the old four-worker command, do not call the run complete until the 904-species census and the separate generic-tree gap are resolved, and do not hand-edit any generated JSON.

## 9. Final worktree state

The worktree is intentionally dirty for manager review. No commit, push, merge, generation run, or live model call was performed.

<<<REPORT {"status":"done","summary":"Evidence-bundled BCU2.12 audit and confirmed repairs are complete. Serial endpoint wiring, durable result checkpoints, ledger/metadata resume truthfulness, collision attempt persistence, report completeness, launcher fail-closed behavior, and the previously ignored UnresolvedCount hard gate now have deterministic regressions. The captured run remains incomplete at 361/904; safe to resume only through the repaired fail-closed launcher after manager review, not as a completion forecast.","changed_files":[".claude/cmdc-agents/scripts/bcu212-full-run.ps1",".claude/cmdc-agents/scripts/bcu212-report.py","gk-forge/tools/seedsmith/_j9_batch_run.py","gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py","gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py","gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py","gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py","gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py","gk-forge/tools/seedsmith/tests/test_bcu212_report.py","gk-forge/tools/seedsmith/tests/test_j9_batch_run.py","tasks/reports/seedsmith-p1-audit-recovery-20260925.md"],"verification":["required pytest command: 93 passed, exit 0","additional focused tree/report/launcher pytest: 55 passed, 9 subtests passed, exit 0","focused verify-change.ps1 tree boundary: 765 passed, 27 subtests passed, exit 0","py_compile changed Python files: exit 0","git diff --check: final exit 0","git status --porcelain: final scoped dirty worktree recorded"],"open_issues":["current 352 species node/species files are not present in the evidence bundle; disk reconciliation is NOT_MEASURED","generic wither tree lacks skill.wither-def-t9-n1 and requires a separate generator-led J13 follow-up","captured run has 268 current-pass rows above the 50‰ UnresolvedCount threshold; repaired execution must stop fail-closed at the first reproduced failure","verify-change mapping is missing for .claude/cmdc-agents/scripts/bcu212-full-run.ps1 and the _j9 production path falls back to a broad module boundary"],"next_steps":["manager reviews the uncommitted scoped diff and integrates it into the corpus worktree","resume only through the repaired launcher with WORKERS=1; treat a hard-gate non-zero exit as expected safety behavior","rerun the model-free PassiveTree census/report after the resumed attempt and separately repair the generic wither node through its generator"]} REPORT>>>

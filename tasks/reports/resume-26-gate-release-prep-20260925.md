# Resume 26 — merged-head gate and release preparation

**Date:** 2026-09-25
**Nature:** read-only readiness assessment. No full merged-head gate was run. This report does **not** claim that the current integration head is green.

## Sources and current truth

Read for this assessment:

- `.claude/cmdc-agents/scripts/post_merge_check.py` — the repaired fail-closed gate.
- `tasks/reports/resume-00b-final-acceptance-20260925.md` — the Phase 0B acceptance report.
- `tasks/reports/legal-interop-preflight-20260925.md` — the legal interop preflight.
- `tasks/reports/mega-merge-program-resume-20260925.md` — the current manager handoff.
- `tasks/reports/mega-merge-post-merge-phase0-20260925.md` — the older merged-head attempt, retained only as historical BLOCKED evidence.
- `gk-core/tests/core-test-projects.v1.json` — the declared post-split test surface.

The current manager handoff records a snapshot of `features/mega-merge` at `cd4104c05582b4de04c538c2df0f9850728c4605` and explicitly says that no terminal current-head merged-head verdict exists. The older report is for the different, older SHA `9220192f45a579f8dc1b6c120b701a65dbc0aea3`; it is BLOCKED evidence only and is stale after the Phase 0B merge. The worktree used for this report is not the required integration branch, so it is not a valid gate candidate.

The legal preflight proves that the two individual host projects can compile against separate owner-supplied legal sources. It does not prove the merged-head gate, release packaging, or a live game. The Phase 0B report is scoped and partial: it records the release/publish contract repairs and focused checks, but explicitly does not record a current-head terminal gate, remote CI/release run, browser proof, or live proof.

## Exact final gate command shape

Run this from a clean checkout of `features/mega-merge`, in the same PowerShell process that supplies the environment:

```powershell
$env:FUSIONRPG_GAME_DIR = '<owner-supplied BepInEx source root>'
$env:FUSIONRPG_ML_GAMEDIR = '<owner-supplied MelonLoader 3.9 source root>'
$env:FUSIONRPG_GAME_PROFILE = 'pvzrh-3.9'

.\.claude\cmdc-agents\scripts\post_merge_check.py
```

The equivalent child-process form is:

```powershell
pwsh -NoProfile -NonInteractive -File .claude/cmdc-agents/scripts/post_merge_check.py
```

Do not add `-SkipBuild` or `-SkipGuards`; either is explicitly BLOCKED and cannot be a release gate. `-TestProject` is optional and additive only: the declared projects in `gk-core/tests/core-test-projects.v1.json`, including its residual project, are always included and cannot be replaced. Use `-Dotnet` or `-Repo` only for a deliberate diagnostic invocation; a real release run must point at the clean integration checkout and must not hide the child process's exit status.

## Required legal-source environment and profile

| Variable | Required runtime value | What the gate checks or consumes |
|---|---|---|
| `FUSIONRPG_GAME_DIR` | Owner-supplied BepInEx source root | Directory, `BepInEx/core/BepInEx.Core.dll`, and `BepInEx/interop/Assembly-CSharp.dll`. |
| `FUSIONRPG_ML_GAMEDIR` | Owner-supplied MelonLoader 3.9 source root | Directory, `MelonLoader/net6/MelonLoader.dll`, and `MelonLoader/Il2CppAssemblies/Assembly-CSharp.dll`. |
| `FUSIONRPG_GAME_PROFILE` | `pvzrh-3.9` | The gate script does not validate this variable directly; the MelonLoader build consumes it. The preflight found that the default `pvzrh-3.8.1` profile mismatches the 3.9 source and fails at the `SetZombie` overload, while `pvzrh-3.9` succeeds. |

The two source roots are separate. Pointing `FUSIONRPG_GAME_DIR` at the MelonLoader-only source is an environment-selection error, not a product diagnosis. Record only variable names and the profile value in tracked evidence; never record machine-local source values, game binaries, loader DLLs, or interop DLLs.

`FUSIONRPG_GAME_POOL` and `FUSIONRPG_GAME_SOURCE` are live-slot inputs, not inputs to `post_merge_check.py`. They remain separate from this gate.

## Branch and clean-checkout preconditions

The script requires all of the following before it can produce a meaningful verdict:

1. The checkout branch is exactly `features/mega-merge`; any other branch is rejected.
2. `git rev-parse HEAD` returns a full 40-character SHA. The script records that SHA and checks that the branch and HEAD do not change during the run.
3. `git status --porcelain=v1 --untracked-files=all` is empty. It checks this initially, before the build phase, before the Guard phase, before every declared test project, and after all checks.
4. No concurrent test process is using the checkout. This is a reliability precondition from the manager handoff; a contended run is not valid evidence even if the process happens to return zero.
5. The checkout is stable while the gate runs. Do not merge, reset, stash, or edit it between phases.

A tracked report cannot be written before the final clean check. Capture the gate transcript to an external log, let the gate finish, then write the tracked report. The script's `.tmp-post-merge-build.txt` is internal and removed; it is not durable evidence. A guard-failure transcript is written below `%TEMP%` and must be retained externally with its hash, without putting its machine-local path into the tracked report.

## What the gate actually covers

The repaired script performs these checks in order:

1. Resolves the repository and `dotnet` executable.
2. Identifies and pins the full merged HEAD and exact integration branch.
3. Builds `FusionRpg.slnx` in `Debug` and requires a successful build summary.
4. Runs `gk-core/tests/FusionRpg.Guard.Tests` with a 20-minute hang timeout, requiring a summary and a positive executed-test count.
5. Resolves every declared project in `gk-core/tests/core-test-projects.v1.json` plus the residual project, and runs each test project with a 10-minute hang timeout. Each requires a summary, positive executed-test count, and zero process exit.
6. Rechecks the clean checkout, branch, and HEAD after the checks.

A build error confined to `FusionRpg.Injector*` is treated as legal-game/interop evidence being unavailable and is recorded as BLOCKED unless another failure makes the overall result RED. A non-Interceptor build error is RED. Missing manifests, ambiguous or missing test projects, missing summaries, zero-test runs, failed test processes, and checkout movement are not green.

## Verdict semantics

| Result | Meaning | Process status | Release interpretation |
|---|---|---:|---|
| `GREEN` | No failures, no blocked conditions, and at least one check ran. | `0` | The only acceptable terminal gate result. It still does not prove packaging, browser behavior, or live play. |
| `RED` | Any build, Guard, test, manifest, summary, zero-test, or other failure was recorded. | `1` | Fix the cause and rerun. Never treat printed `RED` text as success. |
| `BLOCKED` | Legal sources/interops are unavailable, an interop-only build failure is present, or a build/Guard phase was skipped. | `1` | Not green. Supply the legal environment and rerun; do not merge dependent work or resume a gated program. |
| `ABORT` | Repository, `dotnet`, full-SHA, branch, or phase checkout preconditions cannot be established. | `1` or `9` | Precondition failure, not a pass or a usable release verdict. |
| `UNKNOWN` | The script reached its final block with no check having run. | `1` | Never a pass; diagnose the empty/manifest/skip condition before rerunning. |

Failure precedence is deliberate: if any failure is recorded, the result is `RED` even when a legal/interop `BLOCKED` condition is also present. A legal limitation alone is `BLOCKED`; it is not converted to GREEN. A printed verdict and a zero process exit must both be captured.

## Known blockers and readiness gaps

- **No current terminal merged-head verdict:** the handoff has no current-head GREEN, and the only merged-head report is stale BLOCKED evidence for an older SHA.
- **Legal gate environment is a runtime dependency:** the successful individual preflight does not substitute for the final merged-head invocation. Both source variables and `pvzrh-3.9` must be present in the gate process.
- **Current-head aggregate evidence is still separate:** the manager handoff calls for the full local aggregate only after the current gate reaches GREEN. The gate's declared-project run is not `scripts/test-fast.ps1 -AllDefault`.
- **Release/packaging smoke is absent:** no current `publish-player.ps1` plus `smoke-player-pack.ps1` result, package layout, smoke hash, or package-manifest hash is recorded.
- **Browser and live proof are absent:** the handoff requires a real connected-injector proof, normal-path persistence read-back, active-match recovery, and cross-match isolation after the deterministic gate. These are separate from the gate's GREEN.
- **Topology and final reconciliation are absent:** session-boundary, lane-signal, pipeline-census, and final evidence-descendant checks still need current-head records.
- **Program progression remains paused:** BCU2.12 cannot resume until the current integration head has a terminal GREEN result and its other named preconditions are satisfied. No report in this task authorizes that resume.
- **Any later product or infrastructure merge invalidates the gate:** a later evidence-only descendant is allowed only under the handoff's exact commit/path manifest proof. A non-evidence change requires a new gate run.

The Phase 0B acceptance report's exact-SHA/clean-checkout and merged-head items were open at the time that report was written. The later manager handoff records a Phase 0B reviewed SHA and merge in its accepted set; that is separate lane-acceptance evidence, not a current-head `GREEN` claim. A manager must validate the artifact named for the actual SHA before relying on it.

## Release smoke and packaging evidence still missing

The post-merge script does not run the release package, smoke, browser, or live flows. After the current gate is GREEN and the required deterministic/live prerequisites are met, the handoff's packaging shape is:

```powershell
$packagedHead = (git rev-parse HEAD).Trim()
if ((git branch --show-current).Trim() -ne 'features/mega-merge') { throw 'packaging ran off features/mega-merge' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -gt 0) { throw 'packaging started from a dirty checkout' }

$env:FUSIONRPG_GAME_DIR = '<owner-supplied BepInEx source root>'
$env:FUSIONRPG_ML_GAMEDIR = '<owner-supplied MelonLoader 3.9 source root>'
$env:FUSIONRPG_GAME_PROFILE = 'pvzrh-3.9'
$env:FUSIONRPG_VERSION = '<candidate-version>'

.\scripts\publish-player.ps1
.\scripts\smoke-player-pack.ps1
if ((git rev-parse HEAD).Trim() -ne $packagedHead) { throw 'packaging changed HEAD' }

Get-FileHash -Algorithm SHA256 -LiteralPath 'artifacts/player-pack-smoke.json'
$pack = (Resolve-Path 'dist/FusionRpg').Path
$packManifest = Get-ChildItem -LiteralPath $pack -File -Recurse | ForEach-Object {
  $relative = [IO.Path]::GetRelativePath($pack, $_.FullName).Replace('\', '/')
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
  "$relative`t$hash"
} | Sort-Object
$packManifest | Set-Content -LiteralPath 'artifacts/player-pack-manifest.txt'
Get-FileHash -Algorithm SHA256 -LiteralPath 'artifacts/player-pack-manifest.txt'
```

The future release report must record, at minimum:

- `testedHead`, `deployedHead` (when applicable), and `packagedHead`, with the branch and clean status before and after;
- the candidate `FUSIONRPG_VERSION`, exact publish and smoke commands, exit codes, and package layout;
- the SHA-256 of `artifacts/player-pack-smoke.json` and the sorted relative-path `artifacts/player-pack-manifest.txt`, plus the underlying package-file hashes;
- the full aggregate test log path/hash, external gate/build/Guard logs and hashes, and any remote CI/release run identifier if a remote release is claimed;
- the tracked release report path, without committing `dist/` or `artifacts/`.

The handoff names the intended tracked release report as `tasks/reports/mega-merge-release-current-20260925.md` and the topology report as `tasks/reports/mega-merge-topology-current-20260925.md`. Neither should be treated as present evidence until the run creates and records it. The intended live/browser report is `tasks/reports/mega-merge-live-browser-current-20260925.md`, also a planned evidence path, not an existing result.

## Evidence a future manager run must record

### Required gate record

Create a tracked post-merge gate report at a manager-selected repo-relative path (the current handoff requires a tracked report but does not prescribe a filename). It must contain:

- the full pre-run `gatedHead` and `features/mega-merge` branch, plus the post-run HEAD proving equality;
- the exact invocation, the three environment-variable names, `FUSIONRPG_GAME_PROFILE=pvzrh-3.9`, and no machine-local values;
- start/finish timestamps, the `dotnet` version/command identity without an absolute machine path, and the complete build, Guard, and declared-test summaries and process exits;
- the legal-file presence result, any interop classification, all RED/BLOCKED reasons, and the exact terminal verdict/process exit;
- the external gate log path placeholder and SHA-256, plus any guard transcript placeholder and SHA-256;
- an explicit statement that a `RED`, `BLOCKED`, `ABORT`, or `UNKNOWN` result did not authorize merge, BCU2.12 resume, or a live claim.

Do not reuse `tasks/reports/mega-merge-post-merge-phase0-20260925.md` as current evidence; it is pinned to the older SHA. Do not treat a lane artifact in `.claude/cmdc-agents/acceptance/` as a merged-head gate artifact.

### Evidence-only descendants and final integration

For a GREEN gate, the manager must also record:

- the external JSON commit-to-path manifest path and SHA-256;
- the terminal/merge transcript path and SHA-256, including the final integration SHA;
- proof that `gatedHead` is an ancestor of the final clean `features/mega-merge` head;
- proof that every post-gate commit/path is one of the allowlisted evidence/report paths, or a new gate run on the new non-evidence head.

The durable report paths expected by the handoff are:

- `tasks/reports/mega-merge-program-resume-20260925.md` — current manager handoff;
- `tasks/reports/legal-interop-preflight-20260925.md` — legal host-build preflight;
- `tasks/reports/resume-00b-final-acceptance-20260925.md` — Phase 0B scoped acceptance;
- `tasks/reports/mega-merge-release-current-20260925.md` — planned release report;
- `tasks/reports/mega-merge-topology-current-20260925.md` — planned topology report;
- `tasks/reports/mega-merge-live-browser-current-20260925.md` — planned live/browser report;
- `tasks/reports/mega-merge-post-merge-phase0-20260925.md` — stale historical gate only.

External evidence is intentionally represented by placeholders and hashes in tracked reports. Machine-local source, log, install, and pool paths do not belong in the report.

## Readiness conclusion

The repaired gate is ready to be run only on a clean, stable `features/mega-merge` checkout with the three legal/profile environment values above. The legal interop preflight is a prerequisite success, not the gate verdict. The current head remains **not claimed green**. Release readiness remains incomplete until the current-head gate is terminal GREEN, packaging/smoke and topology evidence are recorded, live/browser proof is complete, and the evidence-only descendant proof is clean.

## Local verification

- `git diff --check` — exit `0`; no output from the requested check.
- `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks` — exit `0`; `118` todo files, `open=671`, `done=2885`, `boxes=1884`, `shaded=843`, `unmeasured=2`.

<<<REPORT {"status":"partial","summary":"Read-only gate and release-preparation assessment completed. The repaired gate requires a clean features/mega-merge checkout, three legal/profile environment values, and a nonzero process result for every non-GREEN outcome. The current head is not claimed green; merged-head, release smoke/packaging, topology, browser, and live evidence remain open.","changed_files":["tasks/reports/resume-26-gate-release-prep-20260925.md"],"verification":[{"command":"git diff --check","result":"exit 0; no output"},{"command":"python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks","result":"exit 0; 118 todo files; open=671; done=2885; boxes=1884; shaded=843; unmeasured=2"}],"open_issues":["No terminal current-head merged-head verdict is recorded.","The final legal environment and pvzrh-3.9 profile must be supplied to the actual gate process.","Release/player-packaging smoke, topology, browser, and live evidence are still missing.","BCU2.12 remains paused and no merge or resume was performed."]} REPORT>>>

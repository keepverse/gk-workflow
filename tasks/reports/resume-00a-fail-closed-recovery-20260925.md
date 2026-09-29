# Phase 0A recovery — fail-closed merge/acceptance plane

**Session:** `resume-00a-fail-closed-recovery-20260925`
**Worktree:** `.claude/worktrees/opencode-resume-00a-fail-closed-recovery-20260925`
**Branch at handoff:** `opencode/resume-00a-fail-closed-recovery-20260925`
**HEAD (no commit made by this recovery):** `21f5776951ab962029c10b16c3eee74241912d4a`
**Status:** scoped plane implemented and process-tested; manager review/harvest is still required.

## Scope and starting evidence

The allowed fence was honored. The recovery started with the four dirty files supplied by setup and added only this report:

- `.claude/cmdc-agents/scripts/post_merge_check.py`
- `.claude/cmdc-agents/scripts/accept-lane.ps1`
- `.claude/cmdc-agents/scripts/merge-lanes.py`
- `.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py`
- `tasks/reports/resume-00a-fail-closed-recovery-20260925.md`

The initial `git status --porcelain=v1 --untracked-files=all` was:

```text
 M .claude/cmdc-agents/scripts/accept-lane.ps1
 M .claude/cmdc-agents/scripts/merge-lanes.py
 M .claude/cmdc-agents/scripts/post_merge_check.py
?? .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py
```

The initial tracked diff was 881 insertions and 321 deletions across the three tracked scripts. Its deterministic diff hash was:

```text
git diff --no-ext-diff --binary -- .claude/cmdc-agents/scripts/accept-lane.ps1 .claude/cmdc-agents/scripts/merge-lanes.py .claude/cmdc-agents/scripts/post_merge_check.py | git hash-object --stdin
c193360ea85712d16137b876b9109a10f15634bd
```

The starting untracked regression file was 399 lines / 15,835 bytes, blob `8bfd8fe408caf63b539d2699517db9bb2a3799c2`, SHA-256 `3F133FA11E86971E21D0CB482623B47B4C05F202F8484CE1141D89C9449BC484`. It was not included in the tracked diff hash above.

The abandoned session record and the supplied brief agree on the failure: the prior worker session terminated when a read tool failed, and the record identifies the failed read as an out-of-scope helper. No more precise runtime exception was available in this worktree, so this report does not invent one.

## Required reading and boundary evidence

Read in this session before editing:

- `AGENTS.md`
- `docs/DESIGN-GATE.md` (including the SOLID invariant and pre-proposal checklist)
- `docs/architecture/software-architecture.md`
- `docs/architecture/decisions.md`
- `docs/contributing/agent-git.md`
- `docs/contributing/session-boundary.md`
- `docs/architecture/test-verification-boundary-map.md`
- `docs/architecture/test-verification-boundary-ideal.md`
- `tasks/reports/mega-merge-deep-audit-20260924.md`
- `tasks/reports/mega-merge-phase0-acceptance-plan-20260925.md`
- the current four draft files, `gk-core/tests/core-test-projects.v1.json`, the executable wrapper `.claude/cmdc-agents/scripts/_accept-sim-slice0.ps1`, and all repository call-site matches for the four entry points.

The repository-wide caller search found:

- `_accept-sim-slice0.ps1` as the only executable `accept-lane.ps1` wrapper; it still supplies an 8-character SHA and requests `-Merge`.
- no executable caller of `post_merge_check.py` or `merge-lanes.py` in the current tree; references elsewhere are documentation/briefs.
- the new focused regression script as the direct test caller of all three real entry points.

The active session boundary was already recorded at `tasks/sessions/resume-00a-fail-closed-recovery-20260925.json`. This command was run before editing:

```powershell
python scripts/session-boundary-check.py --session resume-00a-fail-closed-recovery-20260925
```

Result: `clean for 'resume-00a-fail-closed-recovery-20260925'`.

## Investigation findings and repairs

### Before-repair evidence

The supplied draft's original focused suite passed:

```text
python .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py
Ran 13 tests in 16.165s
OK
FOCUSED_SUITE_EXIT=0
```

That was not accepted as proof. After adding process-level cases for the missing boundary conditions, the pre-repair suite exposed seven real defects:

```text
python .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py
Ran 29 tests in 28.580s
FAILED (failures=7)
EXPANDED_RED_SUITE_EXIT=1
```

The failures were: merging from a dirty manager tree, accepting a `GREEN` artifact containing failed-test details, merging while on the wrong branch, silently replacing the declared Core surface with `-TestProject`, silently deduplicating a malformed manifest, treating malformed manifest evidence as `UNKNOWN` instead of `RED`, and reporting `GREEN` when the build phase was explicitly skipped.

A subsequent read-only independent review found six additional high-confidence gaps: a zero-exit command could still produce `GREEN` after printing a parsed failure; the merged-head script did not pin a clean checkout/HEAD across the long run; acceptance did not reject a dirty detached review checkout; both merge paths allowed a staged acceptance artifact; direct `accept-lane -Merge` allowed a caller-selected non-integration branch; and non-empty but non-existent legal-game paths could be treated as available. A follow-up review also found explicit failed-summary and zero/skipped-test-count false-greens. Each gap now has a focused regression and a fail-closed repair; the final read-only review returned no required findings.

### Repaired behavior

- `post_merge_check.py:285-300` refuses a non-integration branch and a dirty checkout before any check starts; `Get-MergedCheckoutError`/`Assert-MergedCheckout` recheck the clean tree, full HEAD, and branch before/after every phase. `:302-399` makes skipped build evidence `BLOCKED`, requires a positive build-success summary, treats explicit failed summaries as RED, requires a positive Passed/Failed count for Guard and every test project (skipped-only/zero-test output is RED), validates both legal-game roots and their required BepInEx/MelonLoader marker files, and preserves a nonzero status. `:111-170` validates the declared manifest, rejects malformed/duplicate/ambiguous entries, and `:330-380` always includes the declared surface; `-TestProject` is additive only. `:383-395` gives failures precedence over `UNKNOWN`/`BLOCKED` and returns nonzero for every non-green verdict. Guard failure transcripts are written outside the checkout so a failed run cannot itself dirty the tree.
- `accept-lane.ps1:12-25` makes the full SHA and non-empty check set mandatory at the parameter boundary. `:48-211` validates schema version, lane, full SHA, timestamp, verdict, attribution, check fields, failed summaries, and GREEN consistency. `:216-253` resolves the full commit and proves it is an ancestor of the named lane branch. `:297-394` pins the review checkout, requires it to be clean and detached at the exact SHA before and after every check, and treats parsed failures/compiler errors/explicit failed summaries as RED even when the command exits zero. `:438-469` revalidates evidence, refuses a staged artifact, enforces `features/mega-merge` for direct `-Merge`, and refuses red, dirty, wrong-branch, or merge-conflict states.
- `merge-lanes.py:110-221` strictly validates the machine-readable artifact for the exact full SHA, including failed summaries and all failure-detail arrays. `:243-275` preflights the lane tip and evidence, `:301-318` refuses staged acceptance evidence, and `:399-467` preflights the whole batch, requires `features/mega-merge`, refuses unmerged/dirty state, reparses evidence immediately before each merge, and merges the immutable SHA rather than a moving branch tip. The pre-existing registry-conflict union gate remains in place.
- `test_fail_closed_pipeline.py` now exercises the actual PowerShell and Python entry points in temporary Git repositories. It covers build RED, Guard RED, test RED, explicit failed summaries with zero exit, zero/skipped-only executed counts, missing summaries, empty/malformed/duplicate manifests, skipped-phase BLOCKED, missing or invalid legal-game paths, missing/full/malformed/stale/mismatched acceptance evidence, unrelated SHAs, dirty/wrong-branch merges, staged evidence, inconsistent GREEN evidence, dirty review checkouts, and the real acceptance-artifact-to-merge-consumer path.

The final focused regression run was:

```text
python .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py
Ran 53 tests in 71.859s
OK
FINAL_FOCUSED_SUITE_EXIT=0
```

## Verification commands and outputs

The following checks were run in this worktree after the final code edits:

```text
pwsh -NoProfile -File .claude/cmdc-agents/scripts/post_merge_check.py -?
POST_MERGE_HELP_FINAL_EXIT=0
```

The help output showed the fail-closed synopsis and syntax; the script did not start a gate run.

```text
pwsh -NoProfile -NonInteractive -Command '$paths = @(".claude/cmdc-agents/scripts/post_merge_check.py", ".claude/cmdc-agents/scripts/accept-lane.ps1"); foreach ($path in $paths) { $tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $path), [ref]$tokens, [ref]$errors) | Out-Null; if ($errors.Count -gt 0) { Write-Output ("PARSE_FAIL " + $path); $errors | ForEach-Object { Write-Output $_.Message }; exit 1 }; Write-Output ("PARSE_OK " + $path) }'
PARSE_OK .claude/cmdc-agents/scripts/post_merge_check.py
PARSE_OK .claude/cmdc-agents/scripts/accept-lane.ps1
POWERSHELL_PARSE_FINAL_EXIT=0
```

```text
python -c "import ast, pathlib; paths=[pathlib.Path('.claude/cmdc-agents/scripts/merge-lanes.py'), pathlib.Path('.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py')]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in paths]; print('PYTHON_AST_OK')"
PYTHON_AST_OK
PYTHON_PARSE_FINAL_EXIT=0
```

```text
git diff --check
GIT_DIFF_CHECK_EXIT=0
```

The path-owned repository planner was also attempted as required by `AGENTS.md`:

```powershell
.\scripts\verify-change.ps1 -Paths @('.claude/cmdc-agents/scripts/post_merge_check.py','.claude/cmdc-agents/scripts/accept-lane.ps1','.claude/cmdc-agents/scripts/merge-lanes.py','.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py','tasks/reports/resume-00a-fail-closed-recovery-20260925.md') -Session resume-00a-fail-closed-recovery-20260925
```

It failed closed at the existing registry boundary:

```text
VERIFICATION BOUNDARY MISSING: .claude/cmdc-agents/scripts/accept-lane.ps1. Add an owner mapping; do not run a broad suite as a fallback.
VERIFY_CHANGE_FIVE_PATHS_EXIT=1
```

The mapping belongs in `gk-core/scripts/verification-boundaries.v1.json`, outside this lane's fence. No full suite was run as a workaround.

At the time of the pre-report status check:

```text
git rev-parse HEAD
21f5776951ab962029c10b16c3eee74241912d4a
```

After writing this report, the final required checks produced:

```text
git diff --check
FINAL_GIT_DIFF_CHECK_EXIT=0

git status --porcelain=v1 --untracked-files=all
 M .claude/cmdc-agents/scripts/accept-lane.ps1
 M .claude/cmdc-agents/scripts/merge-lanes.py
 M .claude/cmdc-agents/scripts/post_merge_check.py
?? .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py
?? tasks/reports/resume-00a-fail-closed-recovery-20260925.md
FINAL_GIT_STATUS_EXIT=0

git rev-parse HEAD
21f5776951ab962029c10b16c3eee74241912d4a
FINAL_GIT_REV_PARSE_EXIT=0
```

`git diff --no-index --check -- /dev/null .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py` and the equivalent check for this report each returned the expected no-index difference status `1` with no whitespace-error output (`UNTRACKED_CHECKS=test:1 report:1`); the tracked `git diff --check` result above is the required clean check.

## What this evidence does and does not prove

It proves the process contract in isolated fixtures: a RED verdict is a nonzero process result; a zero-exit command with parsed failure or explicit failed-summary output is still RED; zero/skipped-only test output, missing summaries, absent checks, malformed/stale/mismatched evidence, missing lane ancestry, dirty or moving checkouts, staged evidence, wrong-branch merges, and skipped required phases all refuse; and a real acceptance artifact can be consumed by the real merge entry point only when its exact SHA and schema agree.

It does **not** prove a real FusionRpg solution build, the real Guard suite, the real 68-project Core surface, or a legal-game/interops build. The recovery worktree is intentionally not the integration branch, and no legal game directory was used. A real merged-head run on `features/mega-merge` must still be performed by the manager; without both legal-game environment values it must report explicit `BLOCKED` evidence and nonzero status, never GREEN.

## Known limitations and open questions

1. `verify-change.ps1` has no owner mapping for the changed manager scripts. This is an executable verification-topology defect, but its registry repair is outside the four-file fence and was not attempted.
2. `.claude/cmdc-agents/scripts/_accept-sim-slice0.ps1` still passes `b37ac7e04` (8 characters) and invokes `-Merge`. The repaired `accept-lane.ps1` correctly rejects that invocation; the wrapper must be updated or retired by its owning manager/session. `tasks/manager-handoff-20260922.md` also contains an old 8-character example. Both are outside this fence.
3. Existing acceptance JSON files created by the old harness are not backward-compatible with schema version 2. They must be regenerated by the repaired harness; silently accepting them would defeat the evidence contract.
4. The merged-head gate now requires a clean checkout and a stable integration HEAD throughout its run. The manager must commit or otherwise clean manager-owned acceptance artifacts before invoking it; this is intentional fail-closed behavior, not a reason to weaken the checkout check.
5. Legal-game evidence is checked for the required BepInEx and MelonLoader marker files, but the isolated regression uses fixture marker files. It is still not a real game/interops build; the manager must run the gate against a legal install.
6. Artifact authenticity is trusted to the local manager process and repository filesystem. The merge consumer validates the artifact schema, full SHA, verdict, and check fields, but does not cryptographically sign artifacts or re-read the referenced temporary log file.
7. The lane/artifact naming and `features/mega-merge`/`cmdc/` conventions remain hard-coded because they are the current manager contract. A future topology change must update the manager owner and its verification mapping together.

## Next steps for manager harvest

1. Review this exact dirty worktree and the four allowed code/test paths; do not accept a worker status label as a verdict.
2. Commit/harvest only after manager review, then run `accept-lane.ps1 -Lane <lane> -ExpectSha <40-char-sha> -Check <non-empty array>` on the reviewed commit and retain the schema-2 artifact.
3. Repair the verification-boundary owner mapping in the verification-topology owner lane, and update/retire `_accept-sim-slice0.ps1` and stale handoff examples.
4. Commit or clean the manager-owned acceptance artifact, then on `features/mega-merge` run `post_merge_check.py` with the legal-game environment and required marker files available. Treat `RED` and `BLOCKED` as nonzero failures; do not merge product lanes on a printed-but-zero or `BLOCKED` result.
5. Keep product lanes staged until the manager has a schema-valid artifact for the exact reviewed SHA and a successful merged-head gate.

No commit, push, branch creation, or merge was performed in the recovery worktree; temporary fixture branches were confined to disposable test repositories.

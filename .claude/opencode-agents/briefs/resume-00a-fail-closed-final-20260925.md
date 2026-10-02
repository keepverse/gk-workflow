# Phase 0A final fail-closed correction — no alternate-model review

The prior recovery lane `resume-00a-fail-closed-recovery-20260925` was stopped after it invoked an unspecified-model subagent twice despite the owner charter. Its dirty four-file draft and report are preserved and copied into this worktree as an unreviewed starting point. Do not use the subagent tool, another runtime, or another model. Work only in the current OpenCode CLI `opencode/space-bunny-free#max` session.

## Allowed paths

- `.claude/cmdc-agents/scripts/post_merge_check.py`
- `.claude/cmdc-agents/scripts/accept_lane.py`
- `.claude/cmdc-agents/scripts/merge-lanes.py`
- `.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py`
- `tasks/reports/resume-00a-fail-closed-final-20260925.md`

Do not edit CI, release, product, registry, generated, or other paths. Do not commit, push, or merge.

## Confirmed manager findings to close

1. `accept-lane.ps1` still validates the verdict with `^(GREEN|RED|RED-KNOWN|UNATTRIBUTED)` without a terminating anchor. A value such as `GREENjunk` can pass schema parsing and be written as a GREEN artifact. Use an exact closed-vocabulary match and add an end-to-end acceptance regression for a junk suffix.
2. `merge-lanes.py` has the same prefix regex. Even though its later GREEN check blocks merging `GREENjunk`, the evidence consumer must reject the malformed schema rather than rely on a later comparison. Use `fullmatch`/an anchored pattern and add a consumer regression.
3. The merge plane does not prove that the reviewed lane SHA descends from the current `features/mega-merge` integration branch. Add a fail-closed ancestry preflight for the exact reviewed SHA in both the direct acceptance/merge path and the batch merge path, with a fixture that creates an unrelated history and proves refusal. Do not weaken the existing exact-SHA, clean-tree, wrong-branch, or schema checks.
4. Preserve the repaired behavior already present: nonzero RED/BLOCKED status, clean merged checkout before/between/after phases, legal-game/interops limitations as BLOCKED, non-empty declared Core surface, zero-exit parsed-failure rejection, and no alternate-model evidence.
1. `accept_lane.py` still validates the verdict with `^(GREEN|RED|RED-KNOWN|UNATTRIBUTED)` without a terminating anchor. A value such as `GREENjunk` can pass schema parsing and be written as a GREEN artifact. Use an exact closed-vocabulary match and add an end-to-end acceptance regression for a junk suffix.
2. `merge-lanes.py` has the same prefix regex. Even though its later GREEN check blocks merging `GREENjunk`, the evidence consumer must reject the malformed schema rather than rely on a later comparison. Use `fullmatch`/an anchored pattern and add a consumer regression.
3. The merge plane does not prove that the reviewed lane SHA descends from the current `features/mega-merge` integration branch. Add a fail-closed ancestry preflight for the exact reviewed SHA in both the direct acceptance/merge path and the batch merge path, with a fixture that creates an unrelated history and proves refusal. Do not weaken the existing exact-SHA, clean-tree, wrong-branch, or schema checks.
4. Preserve the repaired behavior already present: nonzero RED/BLOCKED status, clean merged checkout before/between/after phases, legal-game/interops limitations as BLOCKED, non-empty declared Core surface, zero-exit parsed-failure rejection, and no alternate-model evidence.

```powershell
python .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['.claude/cmdc-agents/scripts/merge-lanes.py','.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py']]"
pwsh -NoProfile -NonInteractive -Command '$paths=@(".claude/cmdc-agents/scripts/post-merge-check.ps1",".claude/cmdc-agents/scripts/accept-lane.ps1"); foreach($p in $paths){$t=$null;$e=$null;[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $p),[ref]$t,[ref]$e)|Out-Null;if($e.Count){throw "$p parse errors: $e"}}'
git diff --check
```

Do not run an unfiltered repository suite. Record exact commands and exit codes. If the existing verification-boundary mapping is missing, report that honestly; do not edit the registry in this lane.

## Required report

Write `tasks/reports/resume-00a-fail-closed-final-20260925.md` with the findings, repairs, tests, exact changed files, open questions, and next steps. End exactly with:

```text
<<<REPORT {"status":"done|partial|blocked","summary":"...","changed_files":["..."],"verification":["..."],"open_issues":["..."],"next_steps":["..."]} REPORT>>>
```

Use `done` only if all three confirmed findings are covered and the focused fixture is green. No model fallback/subagent and no merge are authorized.

# Worktree retirement — the cleanup phase that was missing

**Session:** `worktree-retire-20260926` (worktree `feat/worktree-retire-20260926`, path
`.claude/worktrees/worktree-retire-20260926`, forked from `features/mega-merge@a2168ca76`).
**Owner authorization (2026-09-26):** *"remove worktree that already merge and finish they work, we
have a lot of stale or finish worktree, the document already update and merge but we forget to clean
up them, or the project manager pipeline is never define clean up process, add that phase to project
manager skill, we already have clean up check tool, project manager already merge have context and
should clean finish worktree."*

## 1. What shipped

| Path | Change |
|---|---|
| `gk-core/scripts/retire_worktrees.py` | **new.** Decides which worktrees are BOTH merged and finished and may be removed outright. Read-only by default; `--apply` removes, `--dry-run` previews, `--why` explains one. |
| `gk-core/tests/tools/test_retire_worktrees.py` | **new.** 19 tests, one per keep-reason plus the fail-closed cases. |
| `.agents/skills/project-manager/SKILL.md` | **new step 7** in "Running a program": retire the worktree in the same round you merge it, with the exact commands and the three rules that matter. |
| `AGENTS.md` | the tool added to the manager/lane tooling table. |
| `gk-core/scripts/verification-boundaries.v1.json` | **new `worktree-cleanup-tooling` owner** — see §4, this was a real gap. |

## 2. The decision rule, and why each clause is there

Retirable requires **all five** proven, each reported as its own reason:

1. **No active session record names the path or its branch.** Read from the tracked
   `tasks/sessions/*.json`, not from a runner registry. This is the check the marker tool's own
   acceptance could not make: its tests drive *synthetic* lane records, never a real running lane, so
   a lane that registers nothing is invisible to it. Reading the records directly is what makes the
   tool safe for OpenCode-native lanes, which write no `meta.json` — measured on this repo:
   **0 branches claimed by any lane registry, 10 active session records**, so the record check is
   carrying the entire safety weight here.
2. **Not locked.**
3. **No live lane registry claims the branch** — `.claude/{opencode,cmdc}-agents/agents/*/meta.json`
   plus the legacy `.kilo/agent-manager.json`. Inert on this repo today, kept because it is the only
   signal for a runner that registers itself.
4. **Clean working tree, untracked included.** A generated corpus nobody merged is local work *by
   definition*; this is why the 706-file BCU2.12 corpus and the 6 single-file generated leftovers are
   all kept rather than decided by a cleanup pass.
5. **Fully integrated** — `git cherry <integration> <branch>` reports no unique patch.

`--apply` still refuses every one of them. Nothing is removed without it, and the tool prints the
plan first either way.

## 3. The reading on this repo, and what it found about my own bookkeeping

```
198 worktrees (excluding the main checkout) · 108 retirable · 90 kept
integration features/mega-merge · 10 active session records · 0 lane-registry branches
```

Spot-checked every worktree that matters, and the safety property holds:

| Worktree | Verdict | Reason |
|---|---|---|
| `merge/actor-hud-bottom-anchor-20260926` (live lane) | KEEP | 35 commit(s) not integrated |
| `port/verify-change-python-20260926` (live lane) | KEEP | 3 local path(s) incl. 3 untracked |
| `manage/program-status-tool-20260926` (merged) | KEEP | 1 local path(s) |
| `fix/citation-dotpath-guard-20260926` (merged) | KEEP | **active session record owns it** |
| `accept-program-status-a3843c5` (my review checkout) | RETIRABLE | no active owner; integrated; clean |

That fourth row is the tool catching **my own** bookkeeping: I closed the
`program-status-tool-20260926` record when it merged but left `citation-dotpath-guard-20260926`
`active`, so its worktree is protected for a session that is actually finished. Fixed in the same
commit that lands this tool.

It also confirmed the evidence question before I removed anything: **0 acceptance artefacts and 0
evidence fragments reference any retirable worktree path**, so removal destroys no evidence trail.

## 4. A verification-boundary gap this found

Registering the tool surfaced a real defect: **the entire worktree-cleanup toolchain had no owner in
`gk-core/scripts/verification-boundaries.v1.json`.** `worktree_cleanup_core.py`, `cleanup-worktrees.py`,
`mark-worktree-cleanup.py`, `inspect-worktrees.py` and both of their test files were unmapped, so a
change to any of them selected no test and no guard. Per AGENTS.md an unmapped production path is a
verification-boundary defect, and the honest repair is to add the mapping rather than run a broad
suite — so `worktree-cleanup-tooling` now owns all of it, plus `docs/contributing/worktree-cleanup.md`
and the project-manager skill.

## 5. Three bugs my own tests caught, recorded because two were silent

- **The plan silently dropped the last worktree.** The parser appended a record only when the *next*
  `worktree ` line appeared, so the final one was never emitted — a plan that omits a worktree can
  omit a **live** one. On this repo that was a difference between 197 and 198. Fixed by flushing after
  the loop, and `test_json_carries_counts_and_one_row_per_worktree` now pins the count with three
  worktrees so it cannot regress.
- **`git cherry` ran in the wrong repository.** The integration check inherited the tool's own repo as
  cwd, so in any other repository every worktree read as "git cherry failed" — a false **KEEP** that
  looks exactly like a safety check passing. A false KEEP is safe; a false *reason* is corrosive,
  because it trains the reader to ignore the reason column. `cwd` is now explicit and commented.
- **`sys.stdout.reconfigure` crashed when output was captured.** Unconditional call, so any caller
  redirecting stdout got an `AttributeError` instead of a report. Now guarded.

## 6. Verification

| Check | Command | Result |
|---|---|---|
| New tests | `python -m pytest gk-core/tests/tools/test_retire_worktrees.py -q` | **19 passed** |
| Sibling tooling tests | `python -m pytest gk-core/tests/tools -q` | 79 passed (60 + 19) |
| Registry integrity | `guard-verification-boundaries.py --skip-coverage-walk` | **OK**, exit 0 |
| Registry coverage walk | `guard-verification-boundaries.py` | recorded on completion |
| Live safety spot-check | `--why` on four worktrees, §3 | all four KEPT with correct reasons |
| Evidence safety | artefact/fragment paths vs retirable set | **0 references** |

## 7. What this tool cannot prove

- That a runner **outside** this repository's registries is not using a worktree. Ownership is the
  tracked session records plus lane `meta.json` files; a lane that registers nothing is invisible.
  This is measured, not hypothetical: **0 registry branches on this repo today.** That is why `--apply`
  is a separate, deliberate step and why the manager reviews the plan.
- That an integrated commit was *correct*. Integration is containment, not quality; acceptance is a
  separate artefact.
- Anything about a worktree on a filesystem git cannot list. It is not in the plan, so it is not
  removed — but it is also not reported.

## 8. Next steps

1. Review and merge this row, then run `python gk-core/scripts/retire_worktrees.py --apply --dry-run`, then
   `--apply` — 108 worktrees, none of them a live lane, a dirty tree, or a corpus.
2. Every future merge runs the same two commands (skill step 7), so the count stops growing.
3. The **verification-plane port** lane (`verify-change-python-20260926`) is in flight and owns
   `verify-change`; the `verify-change.ps1` testhost race is recorded in
   `tasks/reports/mega-merge-manager-resume-20260925.md` §E.3 with the reproduction.

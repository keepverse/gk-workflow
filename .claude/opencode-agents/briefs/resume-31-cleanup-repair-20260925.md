# Resume 31 — worktree-cleanup runner discovery repair (fail-closed)

## Task

Fix the confirmed fail-open defect in the worktree-cleanup tool and prove the fix with tests. This is
the owner-directed repair for `TVB-F37` (`tasks/test-verification-boundary-todo.md`).

The defect: `gk-core/scripts/worktree_cleanup_core.py`'s `_runner_evidence(main_root)` reads **only**
`.kilo/agent-manager.json` and returns an empty list when that file is absent. The runners this
repository actually uses write lane ownership elsewhere:

- OpenCode lanes: `.claude/opencode-agents/agents/<lane>/meta.json` — carries `cwd` (the lane's
  worktree), `branch`, `base`, and lifecycle; `status.json` alongside it carries `state`.
- cmdc lanes: `.claude/cmdc-agents/agents/<lane>/` (`meta.json`, `status.json`).

So a linked worktree whose tracked session record is stale or missing can be classified `should-clean`
while a live runner still owns its path. The tool's removal path is destructive; discovery must fail
**closed**.

## Exact fence

Only these paths may change:

1. `gk-core/scripts/worktree_cleanup_core.py`
2. `gk-core/scripts/mark-worktree-cleanup.py` (only if a signature must follow the core)
3. `gk-core/scripts/cleanup-worktrees.py` (only if a signature must follow the core)
4. `gk-core/scripts/test_worktree_cleanup.py`
5. `docs/contributing/worktree-cleanup.md` (the policy text must match the code)

Do not edit anything else. Do not touch `.claude/cmdc-agents/**`, CI, guards, the pipeline plane, or
any session record other than reading them.

## Required behaviour

1. `_runner_evidence(main_root)` returns one record per **runner-owned** worktree path, reading all
   three sources: the legacy `.kilo/agent-manager.json` (unchanged behaviour), 
   `.claude/opencode-agents/agents/*/meta.json`, and `.claude/cmdc-agents/agents/*/meta.json`.
   A record with a resolvable `cwd`/`path` counts as an owner of that path.
2. A worktree owned by ANY runner record is **never** `should-clean`; it is held for manual review
   with the owning runner named in the item's `runnerEvidence` (the field already exists — keep its
   shape and the existing `path_key` comparison).
3. A missing or malformed runner file is **not** an error that aborts discovery — it simply
   contributes no owner (but see 4). Never raise out of `_runner_evidence` on unreadable JSON;
   a broken record must not crash the tool.
4. **Live state matters**: an OpenCode/cmdc record whose `status.json` `state` is a non-terminal state
   (e.g. `running`, `spawning`, `retrying`, `blocked`) forces `manual-review`; a terminal state
   (`done`, `partial`, `failed`, `stopped`, `budget_exhausted`, `quota`) still counts as an owner
   (the tool is conservative — a stale owner is a human decision, not an automatic removal).
   Read `status.json` when present; absent means "owner, unknown state" → held.
5. No new destructive behaviour. Do not add a `--force`, do not remove a marker check, do not touch
   the Recycle-Bin `remove_worktree` path.

## Required tests (the current suite has 10 and none covers this reader)

Add to `gk-core/scripts/test_worktree_cleanup.py`, using the existing tmp-repo harness style
(`self.git(...)`, `self.write_session(...)`):

- one test that creates `.claude/opencode-agents/agents/<lane>/meta.json` pointing at the linked
  worktree (`cwd` = the linked path) plus a `status.json` with `state=running`, and asserts the
  worktree is held as `manual-review` (never `should-clean`) with the owner surfaced;
- one test that does the same for `.claude/cmdc-agents/agents/<lane>/`;
- one test proving a **terminal** runner record still holds the worktree (conservative owner);
- one test proving a malformed runner file does not raise and does not make the worktree clean
  (either it holds, or it proceeds exactly as before the fix — state which and why in a comment);
- one test proving the legacy `.kilo/agent-manager.json` behaviour still holds (regression).

Every test must run with no network and no live checkout.

## Required verification

```powershell
python -m unittest gk-core/scripts/test_worktree_cleanup.py -v
python -m unittest gk-core/scripts/test_inspect_worktrees.py -v
python gk-core/scripts/mark-worktree-cleanup.py --help
python -m py_compile gk-core/scripts/worktree_cleanup_core.py gk-core/scripts/mark-worktree-cleanup.py gk-core/scripts/cleanup-worktrees.py
```

All must pass and the compile step must be a step that gates your claim — do not report a
verification you did not run.

## Hard rules

- Never run the cleanup tool against any live worktree, the main checkout, or any real repository
  path. Tests use temporary directories only.
- Never commit, push, or create a branch. Leave the tree dirty; the manager harvests.
- If a rule blocks you, write `BLOCKED: <what, why>` and continue with other eligible work.

## End with

```
<<<REPORT {"status":"done|blocked","summary":"...","changed_files":[...],"commits":[],"verification":[{"command":"...","result":"..."}],"not_proved":["..."]} REPORT>>>
```

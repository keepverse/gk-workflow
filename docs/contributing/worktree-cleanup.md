# Worktree completion markers and cleanup

This workflow has two explicit phases:

1. **Mark** every registered worktree with fresh Git evidence.
2. **Clean** only a `should-clean` marker after the tool revalidates the same evidence.

It is intentionally conservative. A clean checkout is not enough, and a filename that looks like test output is not disposable by inference.

## Completion policy

A linked worktree is marked `should-clean` only when all of these are true:

- It is registered, existing, non-bare, and not the main worktree.
- It has a normal branch and is not detached, locked, or prunable.
- `git status --porcelain=v1 -z --untracked-files=all --ignored=matching` is readable and empty.
- No active tracked session record owns its worktree or branch.
- No runner record in any of the registries below claims its worktree path.
- Its exact `HEAD` is an ancestor of the configured integration ref, or is contained by the configured upstream remote-tracking ref.

A missing or unreadable ref, missing upstream, dirty file, ignored file, untracked file, conflict, active owner, runner owner, or malformed session or runner record produces `manual-review`. `manual-review` is never consumable by the cleanup command.

The tool uses only local Git evidence. It does not fetch, push, merge, permanently delete worktree directories, force-remove, prune, delete branches, or edit `tasks/sessions/*.json`. Branches and session history are preserved.

## Runner ownership sources

Discovery reads **every** registry the runners in this repository actually write, not just one:

| Source | File | Ownership field |
|---|---|---|
| Legacy Kilo manager | `.kilo/agent-manager.json` | `worktrees[<id>].path`, reached through `sessions[<id>].worktreeId` |
| OpenCode lanes | `.claude/opencode-agents/agents/<lane>/meta.json` | `cwd` (or `path`), relative paths resolved against the main worktree |
| cmdc lanes | `.claude/cmdc-agents/agents/<lane>/meta.json` | `cwd` (or `path`), relative paths resolved against the main worktree |

A record that resolves a worktree path **owns that path**, and an owned worktree is never `should-clean`. The lane's sibling status file (`.claude/opencode-agents/agents/<lane>/status.json`, or `.claude/cmdc-agents/agents/<lane>/status.json`) supplies the lane `state`:

- A state in the terminal set (`done`, `partial`, `failed`, `stopped`, `budget_exhausted`, `quota`) adds the `managed-runner-session` blocker only. A finished lane is a **stale owner, not a removal permission** — deciding whether to recycle it stays a human call.
- Any other state — `running`, `spawning`, `retrying`, `blocked`, a state name this tool does not recognise, or a **missing/unreadable** status file (`unknown`) — adds `runner-lane-not-finished` as well. An unreadable state is never treated as finished.
- A well-formed lane record that resolves no worktree owns none. Review-only lanes are real records in this estate; they are not corruption and must not be reported as such.

A lane record that **cannot be read at all** (unparseable JSON, or a `cwd`/`path` that is not a non-empty string) is a registry error, not a silent absence: it is listed in `runnerRecordErrors` and every candidate is held under `runner-record-errors`, because a corrupt record hides its own worktree and there is no path to hold individually. That is the fail-closed reading — proceeding as if an unreadable registry proved absence is the defect this gate exists to prevent. An unreadable `.kilo/agent-manager.json` is handled the same way.

Because ownership feeds the evidence fingerprint, a lane appearing or changing invalidates any earlier marker (`show` reports it `stale`), so a newly claimed worktree cannot be consumed under a pre-change marker.

## Phase 1: mark

Run from the main checkout:

```powershell
python gk-core/scripts/mark-worktree-cleanup.py mark `
  --repo . `
  --integration-ref features/mega-merge
```

For branches that are pushed but not merged, pass the local remote-tracking ref explicitly:

```powershell
python gk-core/scripts/mark-worktree-cleanup.py mark `
  --repo . `
  --integration-ref features/mega-merge `
  --upstream-ref my-feature=refs/remotes/origin/my-feature
```

The command writes markers under the Git common directory at `.git/worktree-cleanup/markers/`, outside every worktree. A marker therefore cannot make a candidate dirty. Use `--json` for machine-readable output.

The report includes the exact marker ID, evidence fingerprint, branch, HEAD, owner records, completion evidence, blockers, and changed paths. A `should-clean` item includes the confirmation token required by phase 2. `sessionRecordErrors` and `runnerRecordErrors` list the records discovery could not read.

## Phase 2: show and clean

Inspect markers without modifying anything:

```powershell
python gk-core/scripts/mark-worktree-cleanup.py show `
  --repo . `
  --integration-ref features/mega-merge
```

`show` reports a marker as `stale` when the current branch, status, owner evidence, refs, or registry no longer matches the marker fingerprint. A stale marker is not deleted automatically.

Revoke a marker without touching its worktree:

```powershell
python gk-core/scripts/mark-worktree-cleanup.py revoke --repo . --marker wt-<id>
```

Recycle exactly one still-valid marker’s worktree:

```powershell
python gk-core/scripts/cleanup-worktrees.py `
  --repo . `
  --marker wt-<id> `
  --confirm confirm-<token>
```

The cleanup command requires a named marker and its exact token. It re-runs discovery, session/runner checks across all three registries, full status including ignored paths, branch/HEAD checks, lock/prunable checks, and ancestry/upstream checks under a marker lock. It moves the worktree directory to the **Windows Recycle Bin** first, then unregisters only that worktree from Git. It does not permanently delete the directory, use `--force`, delete the branch, or edit the session record. A successful marker becomes `recycled`, records a recycle receipt, and rerunning the same command is idempotent.

If the directory is recycled but Git unregistration fails, the marker becomes `cleanup-failed`, records `recoveryRequired: true`, and the command tells the operator to restore the recycled directory before retrying. The tool never treats that partial state as a successful cleanup.

## Refusal examples

The tool refuses to clean:

- the main worktree;
- a missing, bare, detached, locked, or prunable worktree;
- any worktree with a dirty, untracked, conflicted, or ignored path;
- a worktree owned by an active session, or claimed by any legacy-manager, OpenCode-lane, or cmdc-lane record — finished lane or not;
- every worktree, while any runner registry record is unreadable;
- a branch that is neither merged nor verifiably contained by the configured upstream;
- a marker whose evidence changed after marking;
- a marker from another repository/common Git directory;
- a wrong or missing confirmation token.

Do not use `git stash`, `git checkout`, `git reset`, `git clean`, or `git worktree prune` to force a candidate into a clean state. Resolve the session record or inspect the exact files first. A future reviewed tool may approve specifically named disposable artifacts, but this workflow has no filename heuristic and no implicit force path.

## Tests

Run the focused standard-library tests:

```powershell
python -m unittest gk-core/scripts/test_inspect_worktrees.py gk-core/scripts/test_worktree_cleanup.py -v
```

The tests use temporary Git repositories and do not remove live worktrees. Successful cleanup is tested only against a temporary registered worktree; branch and session-record preservation are asserted. Runner-ownership coverage writes OpenCode-lane, cmdc-lane, and legacy-manager records into the temporary repository: a live lane, a finished lane, a lane with no status file of its own, a lane whose record cannot be parsed, a pathless review lane, and a lane recording its worktree under `path` instead of `cwd`.

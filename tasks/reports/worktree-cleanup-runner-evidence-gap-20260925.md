# Worktree cleanup runner-evidence gap

**Date:** 2026-09-25 (finding) · **reconciled:** 2026-09-26
**Receiving session:** `worktree-cleanup-20260925`
**Disposition:** **RESOLVED — repaired, reviewed and merged at `6b36c52cd` (TVB-F37 closed).**
The `OPEN FINDING` line this report carried until 2026-09-26 was stale: it described the state before
the repair landed, and was never updated when the repair merged. Kept below as the original finding,
with the closure evidence appended, so the record shows what was wrong and what fixed it.

## Finding (as first recorded — now closed)

`worktree_cleanup_core.py:_runner_evidence` reads only `.kilo/agent-manager.json` and classifies a
worktree as runner-owned only when that legacy file contains a matching managed path. The active
OpenCode CLI runner in this program writes lane metadata under
`.claude/opencode-agents/agents/<lane>/meta.json`; those records contain the lane `cwd`, `branch`,
`base`, and lifecycle state, but the cleanup reader never enumerates them.

Therefore the documented “no managed runner session still claims it” gate is not mechanically true
for the currently active OpenCode lanes. A worktree with a missing/stale tracked session record could
be classified `should-clean` even while an OpenCode runner still owns its path. This is a fail-closed
safety defect, not a request to clean any current worktree.

## Evidence

- `gk-core/scripts/worktree_cleanup_core.py:157-184` (**new**; cleanup-owned untracked path) —
  `_runner_evidence` opens only `.kilo/agent-manager.json` and returns an empty list when it is absent.
- `.claude/opencode-agents/agents/resume-28b-effect-pipeline-epl1-1-20260925/meta.json` (**new**;
  runtime record not tracked) — a real active-lane record identifies the OpenCode runner, its `cwd`,
  branch, and base.
- `docs/contributing/worktree-cleanup.md:17-23` — the completion policy requires active managed
  runner evidence to hold a worktree.
- `python -m unittest gk-core/scripts/test_worktree_cleanup.py -v` — 10/10 tests passed, but no test creates
  an OpenCode-style `.claude/opencode-agents/agents/*/meta.json` owner; the suite does not cover this
  reader.

## Safety boundary

The six cleanup-owned paths remain untouched. No marker was written, no worktree was recycled, no
session record was edited, and no cleanup command was run against the live checkout. The main
integration boundary therefore remains blocked by both the cleanup-owned dirty files and the three
owner-routed `.commandcode` paths.

## Required receiving-owner follow-up

The cleanup owner must extend runner discovery (or provide an equivalent manager-owned registry
adapter) and add a deterministic temporary-repository test proving that an OpenCode runner record
forces `manual-review`. The existing ten tests are not sufficient evidence for the current runner
ecosystem. Acceptance remains blocked until that repair has its own exact-SHA review.

---

## Closure evidence (verified 2026-09-26, on this head)

Each leg below was re-checked against this tree, not taken from the repair lane's own report.

1. **Runner discovery was extended.** `gk-core/scripts/worktree_cleanup_core.py` now carries a **registry
   table** of runner lane directories (`:25-29`) that includes
   `("opencode", .claude/opencode-agents/agents)`, and `_runner_evidence` (`:280`) enumerates
   `*/meta.json` under each (`:250`). The "reads only `.kilo/agent-manager.json`" claim above is no
   longer true of the code.
2. **The missing test exists and asserts the fail-closed outcome.**
   `gk-core/scripts/test_worktree_cleanup.py:214` `test_live_opencode_lane_holds_its_worktree` — "a `running`
   OpenCode lane owns its `cwd`; the worktree is manual-review, never clean" — plus a second case at
   `:250` for a lane that no longer appears in the tracked session records.
3. **The repair is in this head.** `git merge-base --is-ancestor 6b36c52cd… HEAD` → exit 0.
4. **The acceptance artefact is GREEN and names that SHA.**
   `.claude/cmdc-agents/acceptance/resume-31-cleanup-repair-20260925-6b36c52c.json` — `verdict: GREEN`,
   `cleanCheckout: true`, 19 unittest + 3 inspect-worktree tests, and a before/after reproduction
   showing the OLD core returning `should-clean []` where the NEW core returns
   `manual-review [managed-runner-session, runner-lane-not-finished]`.
5. **The session record is closed.** `tasks/sessions/resume-31-cleanup-repair-20260925.json` →
   `status: merged`.

**Limitation carried forward from the acceptance, unchanged:** those new tests drive `build_report` on
*synthetic* lane records, not on live runner output. So the repair is proven against constructed
evidence, not against a real running OpenCode lane.

**Still true, and still the reason no cleanup has run:** the tool must not be run against live
worktrees until that synthetic-record limitation is closed with a real-lane case. No cleanup command
has been executed against any worktree at any point.

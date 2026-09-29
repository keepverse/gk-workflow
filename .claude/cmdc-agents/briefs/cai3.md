# Lane `cai3` — combat-ai: the rotation of `cai2` (fresh session, same program)

**Session:** `combat-ai-3` · **Program:** `combat-ai` · **Mode:** worktree
**Program brief:** `.claude/cmdc-agents/briefs/cai2.md` — **read it as your own.** Its `## Work`, `## Rules that bind this program`, `## Verification`, `## Evidence contract` and `## Boundaries` sections all apply to you unchanged.
**Todo (the authority):** `tasks/combat-ai-todo.md`
**Fence:** `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Server/**`, `gk-fusion/src/FusionRpg.Injector/**`, `tests/**`, `gk-core/data/tuning/**`, `tasks/combat-ai-todo.md`, `docs/architecture/combat-ai/**`, `tasks/reports/**`
**Protected, granted to this lane:** `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/scripts/enforcement-registry.v1.json`, `scripts/run-guards.ps1`

## Why this lane exists

You are a **proactive rotation**, not a new assignment. Lane `cai2` was retired at a **3.88 MB session**
with all of its commits merged, because two lanes died to exactly that this session: `tvb58` at 4.99 MB and
`narrative-seed-1` at 4.39 MB both began answering `400 status code (no body)` on every request and could no
longer do any work. You start with a fresh session and `--rotate-at-tokens` is on, so the same wall cannot
take this program. Nothing was lost: `cai2`'s worktree was empty and its commits are on the integration head.

## Work

The rows are the same ones `cai2` was on, and each row records **which half landed** — read the row before
acting, because the title alone will mislead you:

- **`CAI2.2` — `replay-identity` B: pin the profile at match start, refuse rather than drift.** Filed, not attempted.
- **`CAI2.3` — `action-schedule-twin`: the analytic model follows the core policy.** The **identity half landed**; find and finish the remainder.
- **`CAI2.5` — `decision-inspector` B: the lawn ring, default off.** The **core half landed** (lane `combat-ai-2`); the injector half is yours.
- **`CAI2.6` — the reserve floor's rule: the shipped seam and the ideal disagree.** ⚠ **This row needs an owner ruling.** Do **not** close it and do **not** pick a side: sharpen the question to one line with the evidence on both sides and leave it open. That sharpened line is the row's deliverable.

Then the remaining rows in the todo's own order, `deps:` respected.

## Standing notes (all four matter)

- **Every segment ends with the report block.** Without it the runner restarts the segment labelled
  `report_missing` and burns its context for nothing.
- On `429 GoUsageLimitError` (or a `400`, which is what a drained session looks like from outside) **end the
  segment with your report** instead of retrying in a loop.
- One commit per row, evidence **in** the same commit; tick the row and assert the row id is still present
  after the tick; a row you end still open must name **exactly** what blocks it.
- Merge `features/mega-merge` freely — it moves several times an hour. A registry conflict is resolved with
  `.claude/cmdc-agents/scripts/union-registry-sides.py` (it unions the merge sides from git and reports
  differences); never hand-edit a conflicted registry.

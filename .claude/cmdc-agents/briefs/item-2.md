# Lane `item-2` — item system: the rotation of `item-1` (fresh session, same program)

**Session:** `item-2` · **Program:** `item` · **Mode:** worktree
**Program brief:** `.claude/cmdc-agents/briefs/item-1.md` — **read it as your own.** Its Program, Hard rules,
Fence, Verification, Evidence contract and Boundaries sections all apply unchanged.
**Todo (the authority):** `tasks/item-todo.md` (10,124 lines)

## Why this lane exists

You are a **proactive rotation**, not a new assignment. Lane `item-1` was retired at a **4.33 MB session**,
right at the drain wall where two lanes died this session (`tvb58` at 4.99 MB, `narrative-seed-1` at
4.39 MB — both began answering `400 status code (no body)` on every request). All of its commits are
merged. You start fresh with `--rotate-at-tokens` so the same wall cannot take this program.

## Work

`tasks/item-todo.md` in order, `deps:` respected. The program's shape from the predecessor lane: schema
slices, store/schema work, endpoint surfaces, and the chaff-chassis measurement rows it was closing
last — read the row before acting.

## Standing notes (all four matter)

- **Every segment ends with the report block.** Without it the runner restarts the segment labelled
  `report_missing` and burns its context for nothing.
- On `429 GoUsageLimitError` (or a `400`, which is what a drained session looks like from outside)
  **end the segment with your report** instead of retrying in a loop.
- One commit per row, evidence **in** the same commit; tick the row and assert the row id is still present
  after the tick; a row you end still open must name **exactly** what blocks it.
- Merge `features/mega-merge` freely. A registry conflict is resolved with
  `.claude/cmdc-agents/scripts/union-registry-sides.py` (it unions the merge sides from git and reports
  differences); never hand-edit a conflicted registry. Generated seed data is never hand-edited —
  regenerate via the generator and commit the diff.

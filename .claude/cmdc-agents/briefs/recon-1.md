# Lane `recon-1` — backlog reconciliation: measure the truth, propose the metric

**Session:** `backlog-recon-20260921` · **Program:** cross-program (measurement) · **Mode:** worktree
**Fence:** `tasks/reports/**` **only.** Read anything; write one report. Do not edit a program todo, a
`docs/**` file, a script, a source file or another session's record — propose those changes in the report
and the manager applies them.

## Why this lane exists (read this before deciding how to measure)

The manager's burn-down counts `- [ ]` **lines**. That is not work. A line is usually an
acceptance-condition box *inside* a task, and `tasks/species-gear-chain-todo.md`'s own header states:

> *"A ticked task's acceptance boxes are its original contract; the commit's own verification is the
> evidence, and they were not re-run one by one in this planning pass."*

So a **shipped** task contributes roughly 6–10 permanently-unchecked lines. The repo-wide reading of
"524 open / 967 done" therefore overstates the real backlog, and the manager almost made lane-count and
program-split decisions on it. The owner asked for the truth before those decisions. That is this lane.

The manager already verified this pattern on **one** program (`species-gear-chain`: 25 task headings, 24
shipped by name, **7 open**) and on **one** task inside it (T28: every acceptance box `[x]` while the
board listed it as an open heading). Nobody has checked whether other programs carry the same clause.
That unknown is the point of item 2 below.

## Deliverable — `tasks/reports/backlog-reconciliation-20260921.md`

1. **Per program: the true remaining work, measured as open TASK headings/blocks**, with the
   unchecked-line count printed beside it and explicitly labelled *non-indicative*. Cover every
   `tasks/<program>-todo.md`. **State the method you used to identify a "task" in each file** — the files
   do not share one row shape (some use `#### Task T##:` headings, some use `- [ ] **ID**` rows), and
   assuming one shape is exactly how the manager got this wrong three times in a row. Where a file has no
   reliable task marker, say so rather than inventing a count.

2. **How far the "boxes are the original contract, not re-ticked" clause spreads.** For each program
   header: does it say this, does it tick boxes as work lands, or is it silent? Quote the header line with
   `file:line`. This decides whether the metric is repairable or must be replaced — and it is the single
   most valuable number in the report.

3. **Spot-check the tick state against the tree.** For each large program, take ≥3 ticked tasks and ≥3
   open tasks and check them against `git log --grep`, the named file on disk, or the evidence fragment.
   Report every disagreement between a tick and the tree. Do not correct the ticks — report them.

4. **The manager's actual load** (this is what decides whether a sub-leader is worth deploying): how many
   programs currently have live lanes; how many lane merges are pending; and **acceptance turnaround** —
   read `.claude/cmdc-agents/acceptance/*.json` and `.claude/cmdc-agents/agents/*/status.json` and measure
   how long lanes sat idle after reaching an actionable state, waiting for a manager acceptance artefact to
   be written. Report the distribution, not an average alone.

5. **A proposed replacement metric**, written so it can land in one commit: what to count, what to print
   beside it, which file(s) change, and what guard (if any) should pin it. ⛔ Do **not** propose pinning a
   population count — `docs/architecture/validation-ssot.md` forbids it. Say explicitly what your metric
   **cannot** prove.

## Evidence contract (binding — the manager accepts on exactly this)

- Exact command text and the numbers it printed; `file:line` for every claim. A summary is not evidence.
- A **NOT-proved** list: everything you could not measure, and why.
- Findings belonging to another program are **listed with the owning program named** and left unfixed; the
  manager routes them. You do not route, and you do not open rows.
- No code, no todo edits, no metric change: one report, plus your own session record.

## Verification

```powershell
# the report exists and every program appears in it
Select-String -Path tasks/reports/backlog-reconciliation-20260921.md -Pattern '<program>' -SimpleMatch
# your own boundary
python scripts/session-boundary-check.py --session backlog-recon-20260921
```

`verify-change.ps1` selects nothing useful for a markdown-only change; say so in your fragment rather than
running an unrelated suite.

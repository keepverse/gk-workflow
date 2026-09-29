# Deep audit retry 01 — merged interaction seams

## Goal

Perform a focused independent review of the highest-risk cross-lane merge seams. Do not survey the whole repository. Choose at most three concrete seams from recent mega-merge history and try to break their assumptions.

## Read first

- `docs/DESIGN-GATE.md`
- `docs/architecture/software-architecture.md`
- `docs/architecture/decisions.md`
- the three or four source files directly involved in each chosen seam

## Bounds and method

- Read-only: no edits, generated-data changes, commits, branches, deployment, or background tasks.
- Stay inside the current worktree; use relative paths.
- Do not run a full suite, recursive repository inventory, or broad unbounded grep.
- Within 18 steps, select the seams, inspect the code and focused tests, then write the report. Exploration must stop when the evidence is sufficient.

## Required report

Report: (1) exact audited SHA; (2) up to five findings ordered P0-P3 with `file:line`, impact, exact command evidence, confidence, and falsification; (3) which existing QC claims you confirmed or rejected; (4) open questions; (5) an ordered next plan with stop conditions. Distinguish defect, risk, stale-doc, and unknown. `changed_files` must be `[]`.

## Verification

- `git status --porcelain`
- `git rev-parse --short HEAD`
- `git log -12 --oneline --decorate`

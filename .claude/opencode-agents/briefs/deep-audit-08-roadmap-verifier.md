# Follow-up audit 08 — roadmap and verification-plan verifier

## Goal

Turn the accepted audit findings into a dependency-aware next plan for the repository, while checking that the plan respects the actual capability maps, task ledgers, hard edges, session ownership, and verification boundaries. Do not implement anything.

## Read first

- `docs/DESIGN-GATE.md`
- `docs/architecture/software-architecture.md`
- `docs/architecture/decisions.md`
- `docs/contributing/session-boundary.md`
- `docs/contributing/agent-git.md`
- `tasks/reports/mega-merge-deep-audit-20260924.md`
- the capability maps and plan/todo files for each accepted finding's program
- the current session records and verification-boundary registry

## Method

- Read-only and worktree-local. No edits, commits, branch changes, generated-data changes, or broad full-suite run.
- Accept a candidate only when the initial evidence and the cross-domain falsifier agree, or mark it unresolved with the missing proof.
- Map every proposed task to one owning program/path, prerequisite, hard edge, focused verification command, and stop condition. Do not turn unchecked residue rows into work units.
- Identify owner/product decisions, live/browser/environment prerequisites, and tasks that are already owned by active lanes. Never propose a parallel composer, SSOT, SQL owner, or test boundary.
- Prefer the smallest falsification or contract test before implementation. Separate immediate defect containment from structural debt.

## Required report

Return: (1) accepted findings and dispositions; (2) unresolved questions requiring owner/product input; (3) an ordered plan grouped into immediate containment, contract/falsification work, structural repair, and later program work; (4) path/session ownership matrix; (5) verification commands and stop conditions; (6) explicit non-goals and risks of doing the plan in the wrong order. End with the runner's `<<<REPORT {...} REPORT>>>` block; `changed_files` must be `[]`.

## Verification

- `git status --porcelain`
- `git rev-parse --short HEAD`
- `python .claude/cmdc-agents/scripts/convergence-census.py`

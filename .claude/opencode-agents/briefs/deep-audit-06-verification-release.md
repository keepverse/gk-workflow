# Deep audit lane 06 — Verification topology, QC, release, and operational safety

## Goal

Audit whether the repository's gates, CI topology, test selection, deployment/live evidence, and release process can actually detect cross-lane and merged-state defects. Treat mega-merge's trust-and-merge process as an explicit attack surface.

## Read first

- `docs/DESIGN-GATE.md`
- `docs/architecture/software-architecture.md`
- `docs/architecture/decisions.md`
- `docs/contributing/testing-standard.md`
- `docs/contributing/agent-git.md`
- `docs/contributing/live-probe-standard.md`
- `docs/runbook/local-dev.md`
- `.github/workflows/ci.yml`
- `scripts/verify-change.py`
- `scripts/test_fast.py`
- all `scripts/guard-*.ps1` and the current QC index/reports

## Method

- Work read-only. Do not edit, create, delete, stage, commit, push, deploy, launch a game, or start a server.
- Use only paths inside the current worktree and prefer relative paths. Do not inspect the main checkout or any absolute path outside this worktree; `.claude/cmdc-agents` is not required for this audit.
- Map each changed production path to its owning test/guard/CI job. Identify unmapped paths, shared-worktree selection errors, baseline masking, stale gates, flaky-test false greens, and report claims without reproducible commands.
- Inspect whether post-merge checks prove the merged head rather than one lane's checkout. Check release packaging, legal-game-dir assumptions, local paths, secrets, and machine portability.
- Run only bounded static checks or focused tests. Do not run the full suite or a live probe in this lane.

## Required report

Return a self-contained audit with:

1. Executive verdict and confidence.
2. Findings ordered P0/P1/P2/P3 with `file:line`, failure mode, evidence, and a focused reproduction command.
3. Coverage matrix: risk surface, owning check, what it proves, and blind spots.
4. Release/operational risks and environment assumptions.
5. Open questions and an ordered next plan with stop conditions.

End with the runner's `<<<REPORT {...} REPORT>>>` block. `changed_files` must be `[]`; verification entries must be commands actually run.

## Verification

- `git status --porcelain`
- `git rev-parse --short HEAD`
- `git log -20 --oneline -- .github scripts tasks/reports`

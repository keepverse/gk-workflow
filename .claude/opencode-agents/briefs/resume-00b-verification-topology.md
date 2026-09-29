# Resume Phase 0B — verification topology and release superset

## Goal

Close the remaining false-green verification/release paths identified by the deep audit, without overlapping the active `build-preset-bp1` worktree. This lane owns the executable topology; the split-Core registry file is explicitly deferred until that active lane closes.

## Read first

- `AGENTS.md`
- `docs/DESIGN-GATE.md`
- `docs/contributing/session-boundary.md`
- `docs/contributing/testing-standard.md`
- `docs/architecture/validation-ssot.md`
- `tasks/reports/mega-merge-deep-audit-20260924.md` (P1 findings 3–6 and Phase 2)
- current workflow, guard, verification, and guard-test callers

## Allowed paths

- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `.github/workflows/nightly.yml`
- `scripts/run-guards.ps1`
- `gk-core/scripts/guard-generated-seed.py`
- `scripts/verify-change.ps1`
- `scripts/session-boundary-check.py`
- `gk-core/scripts/enforcement-registry.v1.json`
- `scripts/publish-player.ps1`
- `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs`
- `gk-core/tests/FusionRpg.Guard.Tests/VerificationTopologyTests.cs`

**Do not edit `gk-core/scripts/verification-boundaries.v1.json` in this lane.** `tasks/sessions/build-preset-bp1.json` is active and currently dirty in that exact path. Report the precise registry rows needed for split-Core ownership as a handoff; do not overlap or reset that worktree.

## Required behavior

1. Make CI and release topology explicit and fail closed. Release must be a declared superset of CI, with every native/content/web/E2E/Server/importer/guard gate visibly represented; no caller may infer green from a partial list.
2. Wire the guard runner, generated-seed guard, session-boundary check, and acceptance/merge checks into the appropriate CI/release gates. A missing or unparsable check is RED.
3. Make generated-seed protection inspect the complete relevant push/range, never a silent `HEAD~1..HEAD` default. Fetch-depth and range selection must be explicit and testable.
4. Make filtered verification reject zero executed tests; a filter matching nothing is not green. Preserve scoped verification and do not compensate with an unfiltered suite.
5. Make operational/tool/Python roots either path-owned with a real check or an explicit registry exemption. Do not broaden a path boundary just to silence a guard.
6. Make the session-boundary check usable in CI/release and able to reject a reviewed diff that escapes the session fence. Preserve the existing direct/worktree semantics.
7. Make native packaging commands propagate failure; no packaging step may print a warning and continue.
8. Add focused regression coverage for release/CI parity, zero-test filters, full-range generated-seed checks, missing/empty guard evidence, and native command failure. Keep tests structural/contract-based; do not pin a project population count.

## Dependency and report contract

The lane must not wait silently on `build-preset-bp1`. Complete all independent work, then report the exact split-Core registry follow-up and any owner decision still required. Leave the tree dirty for manager review; no commit, push, or merge. Report the full SHA, changed files, exact commands/results, browser/live limitations, open questions, and next plan.

## Verification

- `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <every changed path> -Session mega-merge-program-resume-20260925`
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests --no-restore --filter \"FullyQualifiedName~WorkflowExitCheckTests|FullyQualifiedName~VerificationTopologyTests\"`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -?`
- `python gk-core/scripts/guard-generated-seed.py -?`
- `git diff --check`
- `git status --porcelain`
- `git rev-parse --short HEAD`

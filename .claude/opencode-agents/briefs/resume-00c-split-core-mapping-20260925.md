# Phase 0C split-Core verification mapping repair

The deep audit confirmed that Activity, Delve, Expeditions, PassiveTree, Progression, Scope, and Vfx production paths resolve to `core-residual` even though split Core owner groups exist. The build-preset owner that previously dirtied the shared registry is now abandoned; this lane owns the registry repair.

## Allowed paths

- `gk-core/scripts/verification-boundaries.v1.json`
- `gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs`
- `tasks/reports/resume-00c-split-core-mapping-20260925.md`

Do not edit CI, generated/data, product code, existing test files, or any other path. Do not commit, push, or merge.

## Requirements

1. Inspect the current production-path globs and existing `core-area-*` owner groups before editing. Map each of the seven named areas to the narrowest existing owner group; do not invent a population-count assertion or a new composer.
2. Add a focused structural/planner regression that proves a representative production file from each area resolves to its intended owner and not `core-residual`; preserve a neighboring path's existing owner as a control.
3. Keep the registry schema valid, preserve fallback ordering, and do not weaken the verification-boundary guard.
4. Run JSON parse, the new Guard tests, and `verify-change.ps1` with every concrete executable path. If a project/test file is absent, report the precise mapping dependency rather than using an unscoped fallback.
5. Write the disk-backed report with exact commands, outputs, changed files, open issues, and next steps. End with the required report marker. Leave the worktree dirty for manager review.

No alternate model, subagent, or product merge is authorized.

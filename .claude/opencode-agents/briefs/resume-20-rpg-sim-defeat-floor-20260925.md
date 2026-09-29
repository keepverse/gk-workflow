# Resume 20 — RS-F27 real defeat-award floor

## Task

Implement the already-approved RS-F27 follow-up in a fresh worktree. The measured scenario must
remain legal-empty for victory/stalemate, but a sampled real `defeat` must read a real
`player` / `defeat` progression-ledger row. Reproduce the current failure shape first, then make the
smallest test/report change that proves the policy.

## Boundary

- Edit only `gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs` and
  `tasks/reports/resume-20-rpg-simulator-defeat-floor-20260925.md`.
- Do not rewrite the already accepted `tasks/reports/resume-13-rpg-simulator-rsf27-20260925.md`.
- Do not edit generated data, tuning, product seed seams, CI, or unrelated tests.
- Do not fabricate outcomes or insert ledger rows.
- Commit the code, report, and any new evidence as explicit paths; one logical commit.

## Required report

Record the exact test command and sample count, the observed outcome/ledger distribution, the
`player:defeat` assertion, changed files, commit SHA, and what this does not prove. End with the
runner report block.

## Verification

`$env:FUSIONRPG_RSF27_SAMPLES = '20'; dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --nologo --no-restore --filter "FullyQualifiedName~RS_F27_measures_progression_ledger_non_vacuity_across_real_runs" --logger "console;verbosity=detailed"`

`git diff --check`

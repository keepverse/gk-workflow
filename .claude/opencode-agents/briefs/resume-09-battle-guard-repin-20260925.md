# Manager H1 repair — re-pin BattleEffects baseline after accepted battle change

The current merged-head Guard run found one real red:
`PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline`.
The accepted P1 battle change at exact reviewed SHA `7b4e8ef582a0744e20f501562a4b28167e402c89`
changed `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs`; the guard's prior pin still names the
pre-P1 hash. This is an H1 deliberate re-pin, not a reason to weaken the guard.

## Allowed paths

- `gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs`
- `tasks/combat-ai-todo.md` (append the reopened CAI-guard-1 cause/ruling; do not rewrite history)
- `tasks/reports/resume-09-battle-guard-repin-20260925.md`

No production code, no other guard, no CI/verification scripts, no generated data, no commit from a
worker. The manager owns this protected H1 repair.

## Required work

1. Verify the current SHA-256 of `BattleEffects.cs` and the exact accepted P1 commit that changed it.
2. Re-pin the guard to that full hash and update its adjacent comment to name the P1 battle acceptance
   as the cause. Do not widen or skip the assertion.
3. Run the focused PlantSideStatus guard test and the relevant battle guard(s) from a clean checkout.
4. Append a dated CAI-guard-1 note to `tasks/combat-ai-todo.md` with old/new hash, cause SHA, command,
   and result. Keep the earlier historical re-pin record intact.
5. Write the report with exact commands, hashes, clean-checkout evidence, and any remaining H1 risk.
   Commit the reviewed change at an exact SHA and merge only after manager review.

Use the existing manager worktree boundary; do not touch another lane's files.

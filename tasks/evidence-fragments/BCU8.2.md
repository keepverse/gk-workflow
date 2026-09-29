# BCU8.2 — Injector write-path honesty

Routed the three bare-clamp sites (4 calls) through `EntityStatWriter.ClampToInt32Reporting`, the one
path that emits `stat.writer.clampBoundary` on int32 saturation: the LimHealth gate
(`EntityStatWriter.cs`, `plant.maxHp`/`plant.hp`, src `limhealth.gate`) and the plant/zombie
`TakeDamage` prefixes (`GameHooks.cs`, `plant.damage`/`zombie.damage`). The wrapper went `private` →
`internal` so the hooks share it instead of a second copy. Added `InjectorWritePathHonestyGuardTests`:
the route guard (only the wrapper may call the raw clamp) plus the D22 parity test for both
`ZombieCombatFields.ClampToInt32` bodies, with non-vacuity pins (bounds present; scan actually ran).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Route the three bare clamps | `rg -n "\.ClampToInt32\(" gk-fusion/src/FusionRpg.Injector/` | 1 hit — the wrapper's own body, `EntityStatWriter.cs:56` | `gk-fusion/src/FusionRpg.Injector/Stats/EntityStatWriter.cs`, `gk-fusion/src/FusionRpg.Injector/GameHooks.cs` |
| D22 parity of both clamp bodies | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~InjectorWritePathHonesty"` | Passed — 2/2 | `gk-core/tests/FusionRpg.Guard.Tests/InjectorWritePathHonestyGuardTests.cs` |
| Guard catches a re-introduced bare clamp | same filter with temp `src/FusionRpg.Injector/__ClampMutationProbe.cs` (removed after) | Failed — named `__ClampMutationProbe.cs:4`; re-run clean 2/2 | same |
| `guard-single-writer.ps1` | `pwsh -NoProfile -File scripts/guard-single-writer.ps1` | OK, exit 0 | — |
| `guard-funnel-delta.ps1` | `pwsh -NoProfile -File scripts/guard-funnel-delta.ps1` | OK, exit 0 | — |
| `guard-secondary-no-unity.ps1` | `pwsh -NoProfile -File scripts/guard-secondary-no-unity.ps1` | OK, exit 0 | — |
| BalanceGuard | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "Category=BalanceGuard"` | Passed — 25/25 | — |
| `verify-change.ps1` | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('gk-fusion/src/FusionRpg.Injector/Stats/EntityStatWriter.cs','gk-fusion/src/FusionRpg.Injector/GameHooks.cs','gk-core/tests/FusionRpg.Guard.Tests/InjectorWritePathHonestyGuardTests.cs') -Session bcu8"` | 572 passed / 3 failed — all 3 pre-existing, none in this diff | — |

Pre-existing failures, proven unrelated (the guard's verdict is a pure function of inputs this diff
does not touch; `injector-compile` skipped — no MelonLoader game dir in this worktree):
- `SubprocessPipeDrainGuardTests.No_test_file_reads_stdout_then_stderr_synchronously` names
  `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs:262-263` (lane D, `fb4794e1`/`e4227ef1`).
- `VerificationBoundaryWorkflowTests.Integrity_guard_passes_on_the_current_registry` and
  `P6_the_real_registry_resolves_seedsmith_and_tuning` both hit the harness's 120 s timeout;
  `python gk-core/scripts/guard-verification-boundaries.py --root <worktree>` prints
  `VERIFICATION BOUNDARY GUARD OK` in 3m05s (environmental — 11 active sessions).

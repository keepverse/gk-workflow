# BCU8.3 — delete the legacy `FUSIONRPG_KERNEL_GRIDS` switch + accumulator grids

Deleted `KernelDriveHost.GridsOnKernel`/`DrivingGrids` and the `Dispatch` kill-switch return,
`EffectRuntime.TickDots`/`TickShields`/`_dotAccum`/`_shieldAccum`, and `InjectorLoop`'s fallback call.
**A real defect surfaced and was fixed in the same commit:** D15's effect-clock advance lived only in
`TickDots`, which B26 had already gated behind `!KernelDriveHost.DrivingGrids` — true on a live board —
so `AdvancedEffectClock` was frozen on every board since T4.14 landed 2026-09-17 (status `ExpiresAt`
never passed, `NextPulse` never reached). The advance moved to `KernelDriveHost.Tick`, off the same
scaled delta the kernel advances by; `effect.tickDots` moved onto `PulseDotsNow` so the section keeps a
producer. Owning-program rows opened in the same commit: `tasks/solid-remediation-todo.md` (T4.14),
`tasks/backlog-clear-todo.md` (B25/B26 + Checkpoint 2), `battle-engine-ssot.md` (D15).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| No accumulator grid survives | `rg -n "_dotAccum\|_shieldAccum\|TickDots\|TickShields" gk-fusion/src/FusionRpg.Injector/` | 2 hits, both comments | `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs` |
| Kill switch + fallback call gone | `rg -n "DrivingGrids\|GridsOnKernel\|FUSIONRPG_KERNEL_GRIDS" gk-fusion/src/FusionRpg.Injector/` | 1 hit, a comment | `.../Effects/KernelDriveHost.cs`, `.../Host/InjectorLoop.cs` |
| Clock advance pinned to the kernel tick | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~InjectorKernelGridsGuard\|FullyQualifiedName~InjectorWritePathHonesty"` | Passed — 5/5 | `gk-core/tests/FusionRpg.Guard.Tests/InjectorKernelGridsGuardTests.cs` (new) |
| `guard-single-writer.ps1` | `pwsh -NoProfile -File scripts/guard-single-writer.ps1` | OK, exit 0 | — |
| `guard-funnel-delta.ps1` | `pwsh -NoProfile -File scripts/guard-funnel-delta.ps1` | OK, exit 0 | — |
| `guard-secondary-no-unity.ps1` | `pwsh -NoProfile -File scripts/guard-secondary-no-unity.ps1` | OK, exit 0 | — |
| Citations re-anchored | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | 0 HIGH — 1679 docs, 24798 citations | `docs/**`, `tasks/**` |
| `verify-change.ps1` | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs','gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs','gk-fusion/src/FusionRpg.Injector/Effects/EventDrainHost.cs','gk-fusion/src/FusionRpg.Injector/Host/InjectorLoop.cs','gk-core/tests/FusionRpg.Guard.Tests/InjectorKernelGridsGuardTests.cs') -Session bcu8"` | 575 passed / 3 failed — the same 3 pre-existing, unrelated to this diff (see BCU8.2's fragment: lane D's `FusionRpg.FileMove.Tests/SplitExecutorTests.cs:262-263`, plus two `VerificationBoundaryWorkflowTests` 120 s timeouts vs a 3m05s guard script) | — |

`injector-compile` guard: **SKIPPED** — no `FUSIONRPG_ML_GAMEDIR` in this worktree, so the injector was
not compiled locally. The change is text-verified by the new guard tests; CI / the owner's game dir
owns the compile.

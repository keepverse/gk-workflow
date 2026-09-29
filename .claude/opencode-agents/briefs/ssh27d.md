# Lane brief — `ssh27d` (fix the BalanceGuard test's CS0165, then re-report)

## Why this lane exists

`ssh27c` staged the full SSH6.8 publish but its new guard test does not
compile. This lane inherits its tree (`--base opencode/ssh27c`) and fixes
exactly that. No new scope.

⛔ Read `docs/DESIGN-GATE.md` §1 first. No-shell protocol is binding (your
bash refuses): file work only, quote orchestrator-run commands tagged
`UNPROVED-BY-LANE`, never claim a run.

## The defect (manager-measured, exact)

`tests/FusionRpg.Core.Balance.Tests/Balance/ComboPricingBalanceGuardTests.cs:93`
declares `maxRatio` via `is { } maxRatio` inside `Assert.True(...)`. xUnit's
`Assert.True` carries no does-not-return contract, so the compiler treats
`maxRatio` as maybe-unassigned at its uses (`:136`, `:144`): error CS0165,
whole `FusionRpg.Core.Balance.Tests` project uncompilable.

Fix with a construct that gives definite assignment, e.g.
`if (sockets.ComboPricingMaxRatioToRarityRouteMilli is not { } maxRatio) throw new Xunit.Sdk.XunitException("<same message>");`
— or any equivalent you verify BY READ against the language rules. Keep the
no-default semantics: a missing bound must still fail loudly, never fall back.

## Goal

One compilable guard test, semantics unchanged. Re-report.

## Allowed paths

- `tests/FusionRpg.Core.Balance.Tests/Balance/ComboPricingBalanceGuardTests.cs`

## Off limits

Everything else — the publish, readers, adapters, evidence, todo are staged.
Commit nothing, push nothing, create no branches — leave the tree dirty.

## Definition of done

1. The file compiles under the evident definite-assignment rule; no other
   file differs vs `opencode/ssh27c`.
2. REPORT states the chosen construct and why it is definitely assigned.

## Verification (orchestrator-run; quote verbatim, tag UNPROVED-BY-LANE)

- `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests -c Release --verbosity minimal --filter "FullyQualifiedName~ComboPricingBalanceGuard"` — must print `Failed: 0`.

## Report

`<<<REPORT {...} REPORT>>>`, every claim already a change in this worktree.

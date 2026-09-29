# Resume 12 — PassiveTree P11.1r primary `stat.modify` fan-in

**Session:** `resume-12-passive-tree-p11-1r-20260925`
**Date:** 2026-09-25
**Status:** **BLOCKED** — no production or test path was changed because the requested mapping has no lossless seam inside this fence.

## Scope and baseline

The accepted binder/report parity repair is the baseline:

- `TreeAtomSource.TryReadOp` is the shared kind/op admission predicate (`gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:87-94`).
- `TreeResolveReport.Build` uses the same predicate through `HasReadableAtom` (`gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeResolveReport.cs:105-111`), so a binder-emitted `stat.modify` is currently not falsely reported as a derived contribution.
- The accepted report and exact-SHA artifact are `tasks/reports/resume-08-passive-tree-binder-20260925.md` and `.claude/cmdc-agents/acceptance/resume-08-passive-tree-20260925-1984dfcd.json`.

No generated seed/generated data, tuning, Server, CI, guard, or new subsystem path was touched. No corpus was regenerated.

## Finding: the existing fan-in cannot carry a primary node atom

The binder preserves the primary kind and primary channel:

- `TreeBinderRun.BindNode` keeps `r.KindId` in the emitted `NodeAtom` (`gk-core/src/FusionRpg.Core/PassiveTree/Binding/TreeBinderRun.cs:62-87`). The worked binder result is `stat.modify` on `atk` with `PTheta`/`GameUnits`.
- `NodeAtom` documents `stat.modify` as the primary kind and allows `Flat | Increased | More`; `More` is explicitly not a derived operation (`gk-core/src/FusionRpg.Core/PassiveTree/Catalog/NodeAtom.cs:10-14,26-35,57-70`).
- The existing `ResolveAmount` arithmetic already has the three stored scale branches (`PTheta`, `Theta`, `FlatPermille`) and applies the existing `fMilli` contract (`gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:104-118`). The unresolved issue is not a missing KMicro formula; it is the channel namespace and operation meaning when a primary atom is sent through a derived-only shape.

`BoundDerivedAtom` is a derived-side carrier, not a generic primary modifier:

1. `BoundAtomsFor` feeds the result to the `boundDerivedAtoms` delegate and constructs `BoundDerivedAtom` (`gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:66-75`).
2. `ActorHubBootstrap.CreateDefault` registers that delegate only as `AtomDerivedSubsystem` (`gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs:146,171-172`).
3. The `IActorStatSubsystem` contract itself exposes only `ContributeDerived`; it has no primary-bag contribution method (`gk-core/src/FusionRpg.Core/Stats/Derived/IActorStatSubsystem.cs:5-10`).
4. `AtomDerivedSubsystem.ContributeDerived` turns each row into a `DerivedModifier` (`gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/AtomDerivedSubsystem.cs:51-63`).
5. `DerivedComposer.Compose` validates every channel against `DerivedStatRegistry` before folding (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedComposer.cs:34-47`), and `ValidateChannel` rejects an unregistered channel (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatRegistry.cs:425-428`).

A real `stat.modify` node targets a primary id such as `atk`; that id is in the primary `StatChannels` vocabulary (`gk-core/src/FusionRpg.Core/Stats/ModifierOp.cs:68-75`), not the derived registry. Lifting the kind filter alone would therefore make the producer emit a row and the report call the node live, then the existing lawn/battle Hub read would reject it as an unknown derived channel. That is not a valid fan-in and would violate report/read agreement at runtime.

There is no lossless operation mapping either:

- `DerivedModifierOp` has `Flat | Increased | Replace | Flag` (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedModifier.cs:10-16`).
- `AtomDerivedSubsystem.TryParseOp` deliberately refuses `more` (`gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/AtomDerivedSubsystem.cs:66-81`).
- `spec-mechanism-wiring.md:288-293` explicitly says a primary `more` must not be silently coerced to a derived operation.

The real primary consumers are separate: lawn primary compose is `StatSystem.Resolve`/`StatComposer` (`gk-core/src/FusionRpg.Core/Stats/StatSystem.cs:147-166`), while battle live primary modifiers enter `BattleStatModifierLedger` as sourced `StatModifier` rows (`gk-core/src/FusionRpg.Core/Battle/BattleStatModifierLedger.cs:6-13,28-58`). `BattleHubCompose` passes `HubInputs.BoundAtoms` into the same derived-only `AtomDerivedSubsystem` seam (`gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs:78-88`). There is no existing tree-to-`StatSystem`/primary-ledger delegate or production call site in the allowed fence.

## Exact missing production seam / decision

P11.1r needs one reviewed primary-side route before `TreeAtomSource` can emit a live row. It must choose and implement one of these contracts outside this lane's allowed paths:

1. a primary carrier/delegate that feeds the existing `StatSystem` primary bag on lawn and the existing battle primary ledger, while retaining one ActorHub composition; or
2. an explicitly approved primary-channel-to-derived-channel/operation mapping with a lossless contract for every legal `stat.modify` op (including `More`) and a real reader for the target derived channel.

Neither option can be expressed by changing only the kind filter in `TreeAtomSource`, and neither may be fabricated by renaming `atk` to a combat-derived channel. `progression.bonus.atk` is retired and is not a valid substitute (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatRegistry.cs:72-75`).

The row's `TreeResolveReport`/`BoundAtomsFor` agreement is currently correct for the existing derived route. Widening only the shared predicate would make both projections agree on a row that the production fan-in cannot compose, so the shared predicate was deliberately left unchanged.

## Verification

The focused test projects were restored first. The split Core test projects do not set `IsTestProject`; the diagnostic `dotnet test -v diag` run explicitly reported `Skipping running test ... no IsTestProject`. The actual focused runs were therefore executed directly against the built test assemblies with `dotnet vstest`.

| Command | Result |
|---|---|
| `dotnet restore FusionRpg.slnx` | Passed; test assets restored in this worktree. |
| `dotnet build gk-core/tests/FusionRpg.Core.PassiveTree.Tests/FusionRpg.Core.PassiveTree.Tests.csproj --no-restore -p:UseSharedCompilation=false` | Passed; 0 errors, two existing xUnit analyzer warnings. |
| `dotnet vstest tests/FusionRpg.Core.PassiveTree.Tests/bin/Debug/net8.0/FusionRpg.Core.PassiveTree.Tests.dll --TestCaseFilter:"FullyQualifiedName~TreeAtomSource"` | 22 passed, 0 failed, 0 skipped. |
| `dotnet vstest tests/FusionRpg.Core.PassiveTree.Tests/bin/Debug/net8.0/FusionRpg.Core.PassiveTree.Tests.dll --TestCaseFilter:"FullyQualifiedName~TreeFanInTests\|FullyQualifiedName~TreeBinderResolverParityTests"` | 6 passed, 0 failed, 0 skipped. |
| `dotnet vstest tests/FusionRpg.Core.PassiveTree.Tests/bin/Debug/net8.0/FusionRpg.Core.PassiveTree.Tests.dll` | 406 passed, 0 failed, 0 skipped. |
| `dotnet build gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj --no-restore -p:UseSharedCompilation=false` | Passed; 0 errors, existing warnings. |
| `dotnet vstest tests/FusionRpg.Core.Tests/bin/Debug/net8.0/FusionRpg.Core.Tests.dll --TestCaseFilter:"FullyQualifiedName~TreeAtomSourceParityTests"` | 5 passed, 0 failed, 0 skipped. |
| `dotnet build gk-core/tests/FusionRpg.Core.Balance.Tests/FusionRpg.Core.Balance.Tests.csproj --no-restore -p:UseSharedCompilation=false` | Passed; 0 errors, existing warnings. |
| `dotnet vstest tests/FusionRpg.Core.Balance.Tests/bin/Debug/net8.0/FusionRpg.Core.Balance.Tests.dll` | 211 passed, 0 failed, 0 skipped. |
| `dotnet build gk-core/tests/FusionRpg.Core.Stats.Tests/FusionRpg.Core.Stats.Tests.csproj --no-restore -p:UseSharedCompilation=false` | Passed; 0 errors, 0 warnings. |
| `dotnet vstest tests/FusionRpg.Core.Stats.Tests/bin/Debug/net8.0/FusionRpg.Core.Stats.Tests.dll --TestCaseFilter:"FullyQualifiedName~DerivedComposerShapeTests\|FullyQualifiedName~AtomDerivedSubsystemTests"` | 27 passed, 0 failed, 0 skipped. |
| `.\scripts\guard-actor-hub.ps1` | `ACTOR-HUB GUARD OK`. |
| `python gk-core/scripts/guard-power.py` | `POWER GUARD OK — one ladder, pin holds, no private f(level)`. |
| `python scripts/session-boundary-check.py --session resume-12-passive-tree-p11-1r-20260925` | Clean for this session. |
| `$changed = @('gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs','gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeAtomSourceTests.cs','gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeBinderResolverParityTests.cs'); .\scripts\verify-change.ps1 -Paths $changed -Session resume-12-passive-tree-p11-1r-20260925 -PlanOnly` | Passed; selected `core-area-passivetree`, `core-passivetree`, and `unique-allocation-reader-seam`. |

The tests prove the current derived fan-in and the accepted report/read parity. They do not prove a primary `stat.modify` contribution because the production seam that would accept one is absent.

## Changed files

- `tasks/reports/resume-12-passive-tree-p11-1r-20260925.md` — this evidence and blocker report.

No source or test path was edited. The worktree was clean before this report was created.

## Open issues and next steps

1. `mechanism-wiring`/the primary-stat owner must approve the primary carrier/delegate and its exact operation contract; changing only `TreeAtomSource.TryReadOp` is not sufficient.
2. A production implementation must prove the same real `stat.modify` node through lawn `StatSystem` and battle primary-ledger/Hub read shapes, then keep the shared report predicate aligned with that real read.
3. `More` needs an explicit primary-route treatment; it cannot be coerced to a derived op.
4. The existing `TreeBinder` corpus and generated data remain outside this lane and were not regenerated.

<<<REPORT {"status":"blocked","summary":"P11.1r cannot be implemented honestly inside the allowed fence. stat.modify is a primary StatModifier/StatSystem and battle-ledger operation, while the requested BoundDerivedAtom/AtomDerivedSubsystem path is validated by DerivedStatRegistry and has no More operation or primary channel bridge. Lifting only the shared kind filter would create report/read drift or an unknown-derived-channel failure. The accepted parity repair remains unchanged; focused tests, guards, and PlanOnly all pass.","changed_files":["tasks/reports/resume-12-passive-tree-p11-1r-20260925.md"],"verification":["dotnet restore FusionRpg.slnx — passed","dotnet vstest tests/FusionRpg.Core.PassiveTree.Tests/bin/Debug/net8.0/FusionRpg.Core.PassiveTree.Tests.dll --TestCaseFilter:\"FullyQualifiedName~TreeAtomSource\" — 22 passed","dotnet vstest tests/FusionRpg.Core.PassiveTree.Tests/bin/Debug/net8.0/FusionRpg.Core.PassiveTree.Tests.dll --TestCaseFilter:\"FullyQualifiedName~TreeFanInTests|FullyQualifiedName~TreeBinderResolverParityTests\" — 6 passed","dotnet vstest tests/FusionRpg.Core.PassiveTree.Tests/bin/Debug/net8.0/FusionRpg.Core.PassiveTree.Tests.dll — 406 passed","dotnet vstest tests/FusionRpg.Core.Tests/bin/Debug/net8.0/FusionRpg.Core.Tests.dll --TestCaseFilter:\"FullyQualifiedName~TreeAtomSourceParityTests\" — 5 passed","dotnet vstest tests/FusionRpg.Core.Balance.Tests/bin/Debug/net8.0/FusionRpg.Core.Balance.Tests.dll — 211 passed","dotnet vstest tests/FusionRpg.Core.Stats.Tests/bin/Debug/net8.0/FusionRpg.Core.Stats.Tests.dll --TestCaseFilter:\"FullyQualifiedName~DerivedComposerShapeTests|FullyQualifiedName~AtomDerivedSubsystemTests\" — 27 passed","guard-actor-hub.ps1 — passed","guard-power.py — passed","verify-change.ps1 -PlanOnly — passed","session-boundary-check.py — clean"],"open_issues":["No existing production seam routes a tree stat.modify primary channel into the lawn StatSystem and battle primary ledger while preserving one ActorHub composition.","DerivedModifierOp/AtomDerivedSubsystem has no More operation; coercing it would be wrong.","No KMicro/ScaleAxis arithmetic defect was found; the unresolved mapping is primary channel namespace and operation semantics.","No generated corpus was regenerated or edited."],"next_steps":["Obtain the primary-route design/owner decision and widen the fence to the real primary carrier/delegate and its tests.","Prove one real stat.modify node through both lawn and battle primary read paths.","Preserve TreeResolveReport and BoundAtomsFor parity only after the real read seam exists."]} REPORT>>>

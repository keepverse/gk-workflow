# TVB5.8.45 precondition — the `GateCounterBoundaryGuardTests` path literal (a BLOCKS SPLIT finding)

`core-split-apply`'s own rule: "an own-path string literal in a test … is fixed in its own commit **before** the
increment (analyzer `BLOCKS SPLIT`), because a move never edits content." This is that commit for the PassiveTree
increment.

| Criterion | Command | Result |
|---|---|---|
| the defect, read from the code | `tests/FusionRpg.Core.Tests/PassiveTree/GateCounters/GateCounterBoundaryGuardTests.cs:96-97` | `File.ReadAllText(Path.Combine(root, "tests/FusionRpg.Core.Tests/PassiveTree/tests-PassiveTree/PassiveTreeTuningTests.cs"))` — a hardcoded residual path, which stops resolving the moment the folder moves |
| the fix | same file | the file is now located by name under `tests/` (skipping `bin`/`obj`) with `Assert.NotNull`, so it resolves in the residual **and** after the move |
| the test | `dotnet test gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj -c Release --filter "FullyQualifiedName~GateCounterBoundaryGuardTests"` | see the run's numbers in the commit message |
| why it blocked | the increment-45 apply gate reverted on it | `Failed FusionRpg.Core.Tests.PassiveTree.GateCounters.GateCounterBoundaryGuardTests.The_rate_divergence_refusal_is_already_covered_at_the_loader_level_not_duplicated_here [43 ms]` — the residual's own run, before any move was kept |

Also checked while diagnosing: the pre-check's other hit, `TreeAtomSourceTests` "used by"
`Creatures/Patron/PatronAbsorptionGridEqualityTests.cs`, is a **comment** reference (`grep` shows it at line 23
inside `///` prose), not a code dependency — so no `links` entry is needed for the PassiveTree increment.

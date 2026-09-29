# CAI4.2 — `lawn-held-actions` A: the per-match frozen sets (Core/Match half)

Lane `cai4` (session `combat-ai-4`). Row: `tasks/combat-ai-todo.md` CAI4.2.
Spec: `docs/architecture/combat-ai/spec-lawn-held-actions.md`.

**Canonical fragment.** The first half of this row's evidence was written at
`tasks/reports/CAI4.2.md` before the manager widened this lane's fence to include
`tasks/evidence-fragments/**`; this file is the complete fragment and supersedes it.

## What landed

`gk-core/src/FusionRpg.Core/Match/Ai/LawnHeldActionSets.cs` — the per-match store: `PushSpecies`/`PushBound`
freeze once per key per match through `FrozenActionSet.FreezeAtRunStart`, compile every assembled id
through the supplied `ActionCatalog`, order once by `ActionTagPreference.Compare`, and hand the frozen
set out by reference. `HeldFor(speciesKey, boundInstanceKey)` prefers the instance key and returns
**empty** for an unknown pair — never the basic-attack row. `BeginMatch()` is the lawn's
`RefreshAtNextRunStart` boundary. An id the catalog does not know refuses the **whole** key, loudly,
once, and every later push returns the same empty refusal without reporting again.

Tests: `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnHeldActionSetsTests.cs` — 13 tests.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| Assembling the same `(basics, liveGrants)` twice yields the same ids in the same order | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnHeldActionSets"` | **13 passed / 0 failed** |
| A grant added after the freeze is absent from `Snapshotted()`; present after the next match | same | 13/0 |
| N pushes of one key share one `FrozenActionSet`; a Bound key resolves to its own set | same | 13/0 (`Assert.Same`, `AssemblyCount == 1`, the eligibility delegate called once) |
| No pushed set ⇒ empty held list, never the basic-attack row | same | 13/0 |
| A compile failure reports once and returns empty on every later call; an unknown id refused loudly | same | 13/0 |
| **spec Success criterion 5, second half** — *"an unknown species yields empty, and `StubIntentSource` answers `None` for it"* | same | **13/0** — `An_unknown_species_answers_None_through_the_shipped_stub_policy` (a board fake whose every member throws, so the test proves WHERE the shipped stub stopped), plus its mirror `A_species_with_a_pushed_set_gets_past_step_one_and_asks_the_board` |
| **Mutation**: remove `StubIntentSource`'s `heldActions.Count == 0` early return | planted in that file, run, reverted | **1 red** (the new test); 13/13 green after revert, and the file is byte-identical after (`git diff --stat` empty) |
| **Mutation**: make a second push re-assemble | planted, run, reverted | **3 red**; green after revert |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | 5 passed / 0 failed |
| `verify-change` — the store | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Match/Ai/LawnHeldActionSets.cs','tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnHeldActionSetsTests.cs') -Session combat-ai-4` | exit 0, **15560 passed / 0 failed** across 35 runs (at the pre-merge tip) |
| `verify-change` — the criterion-5 test | `verify-change.ps1 -Paths @('tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnHeldActionSetsTests.cs') -Session combat-ai-4` | exit 0, **279 passed / 0 failed** (`core-balance`) |
| `guard-dal.ps1` | `pwsh -NoProfile -File ./scripts/guard-dal.ps1` | exit 0 |

## Re-verified at the merged head

After `features/mega-merge` was picked up (88 commits), every file this row owns and every dependency
its store reads (`ActionSetAssembler`, `FrozenActionSet`, `CompiledAction`, `ActionCatalog`,
`ActionTagPreference`, `ActionRow`) was confirmed **untouched** by that merge, and the whole lane's
paths were re-verified there:

`verify-change.ps1 -Paths @(<all 7 Core/Match/Ai files + all 7 Balance test files>) -Session combat-ai-4`
→ **exit 0, 15698 passed / 0 failed across 40 project runs**.

## Row state

**Open, by the program's own precedent (CAI2.5, CAI4.1): no production host reaches the store until
CAI4.3 lands `LawnHeldActionRegistry` + the Cold push + the `InjectorEntityRegistry` drops —
`gk-fusion/src/FusionRpg.Injector/**` and `gk-core/src/FusionRpg.Server/**`.** Every acceptance line of this row is run
and green, and spec test rows 6 and 7 (the ptr registry's `Remove`/`Clear`) are CAI4.3's by the row's
own Files list.

Two stated deviations: the tests live in `tests/FusionRpg.Core.Balance.Tests/CombatAi/` (this lane's
fence does not include `gk-core/tests/FusionRpg.Core.Tests/**`), and the store is fed the **raw** inputs (a
`SpeciesBasicsRow` + live grant rows) rather than a pre-compiled list — `CompiledAction` carries an
`ICompiledPredicate` tree and cannot ride the Cold push's JSON, so the same Core type runs the
assemble→compile→order pipeline on the injector side.

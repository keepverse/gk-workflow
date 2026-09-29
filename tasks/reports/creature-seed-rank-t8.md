# Task 8 — fusion floors (in-fence half) — row left OPEN on two denied-path blockers

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 8. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §6.
Landed: NEW `gk-core/src/FusionRpg.Core/Creatures/CreatureRankFloors.cs` (the per-gate floor policy),
`CreatureRecipeCatalog.EligibleOutputs`, `RpgStore.Fusion.cs` (promotion gate + inherit-pick gate),
`gk-core/tests/FusionRpg.Core.Tests/Creatures/Fusion/FusionRankFloorTests.cs`,
`gk-core/tests/FusionRpg.Core.Tests/Creatures/Fusion/SyntheticSpecies.cs` (a `rank` fixture parameter),
`gk-core/tests/FusionRpg.Data.Tests/FusionStoreTests.cs`, `gk-core/tests/FusionRpg.Data.Tests/FusionInheritancePicksTests.cs`.
**The row is NOT closed:** its preview-parity half and the floors' boot wiring both need paths this lane's
fence denies (proven below).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Rank floor at the fusion PROMOTION enforcing site | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~FusionStoreTests"` | **Passed! — Failed 0, Passed 21, Total 21, 1 s**; the new test raises the `fusionPromotion` floor and gets `promotion.rank-floor`, with the specimen's rarity untouched (the refusal lands before any cost is spent) | `RpgStore.Fusion.cs` |
| Rank floor at the recipe-eligibility + INHERIT-PICK enforcing site | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~FusionInheritancePicks"` | **Passed! — Failed 0, Passed 11, Total 11**; the new test raises `fusionRecipeEligibility` and gets `picks.source-below-rank-floor` with the soul balance unchanged | same |
| Rank floor at recipe eligibility (`EligibleOutputs`) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~FusionRankFloorTests"` | **Passed! — Failed 0, Passed 6, Total 6, 66 ms** — a floor above bottom narrows the eligible roster to the ranked species only; the rarity floor and capture-only rule still decide | `CreatureRecipeCatalog.cs` |
| null→bottom at each gate | same run | `Passes(gate, null)` is TRUE at the shipped bottom floor and FALSE at a raised one — the mapping happens once, inside the policy, so a gate never hands a null to the ladder | `CreatureRankFloors.cs` |
| Shipped floors are a pass-through (zero behavior change) | same run — `The_shipped_floors_are_the_bottom_rung_and_pass_every_rung_and_null` + `An_unconfigured_policy_is_the_same_pass_through_as_a_bottom_floor` | all five gates read the bottom rung from the REAL `creature-rank.v1.json`, and an unconfigured policy is behaviorally identical to it | same |
| Gate id vocabulary is the tuning file's own | same run — `The_declared_gate_vocabulary_is_the_tuning_files_own_gate_ids` | `CreatureRankFloors.DeclaredGates == CreatureRankTuning.GateIds`; a tuned file missing a gate is REFUSED at `Configure` (own falsifier) | same |
| No recompute on promotion | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~FusionStoreTests"` (the same new test) | after a successful promotion the SPECIES' rank is unchanged — stated in the gate's own comment and asserted | `RpgStore.Fusion.cs` |
| Task 8's own Verify line | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~Fusion"` | **Passed! — Failed 0, Passed 9516, Skipped 0, Total 9516, 1 m 20 s, EXIT=0** (note: the filter selects the WHOLE project — the assembly namespace is `FusionRpg.Core.Tests`, so `~Fusion` matches everything) | — |
| Static guards | `guard-dal` · `guard-test-substrate` · `guard-magic-numbers` · `guard-population-pin` | `DAL GUARD OK` · `TEST SUBSTRATE GUARD OK` · `M1=0 M2=0 M3=0 M4=0` · `total 1 finding` — that one is **CS-R2**, `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs:220`, another lane's file, unchanged from the previous task | — |

## What blocks this row (exact, and proven)

1. **Preview parity — `gk-core/src/FusionRpg.Server/FusionEndpoints.cs` is outside this lane's fence.**
   `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/FusionEndpoints.cs')
   -Session creature-seed-rank -PlanOnly"` →
   `path is outside session scope (creature-seed-rank): gk-core/src/FusionRpg.Server/FusionEndpoints.cs`.
   The runner's own allowed-path list for this lane (`gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`,
   `gk-forge/tools/seedsmith/**`, `tests/**`, `gk-data/packs/fusion/data/seed/creatures/**`, `gk-core/data/tuning/**`, `tasks/…`) excludes it too,
   so a change there fails the run whatever the hook does. **The exact two-line edit needed:** beside
   `StarPolicy.CanPromote` in the promote preview and inside the pickable-atoms loop in the recipe preview,
   call the SAME `CreatureRankFloors.Passes(<gate>, CreatureSpeciesCatalog.Get(speciesId)?.Rank)` the
   enforcing sites now call — the FE then never offers a pick execute would refuse
   (`promotion.rank-floor` / `picks.source-below-rank-floor`). One row or one fence grant from the manager
   closes it.
2. **The floors' boot wiring — `gk-core/src/FusionRpg.Server/**` and `gk-fusion/src/FusionRpg.Injector/**` are both outside
   the fence.** No production host reads `creature-rank.v1.json` today, so a floor tuned above bottom in
   that file has no effect until a host calls `CreatureRankFloors.Configure(CreatureRankTuningLoader.Parse(…))`
   at boot (the Server already parses its other tuning files there; the Injector likewise). The policy, its
   validation and every in-fence gate are wired and tested; this one line per host is the missing wire, and
   per the repo's own rule a mechanism no host reaches is not "done" — which is why this row stays open.

## NOT proved / declared gaps

- The four non-fusion gates (`expeditionWildBand`, `waveBand`, `cageEligibility`) are Tasks 10-12 by the
  todo's own dependency graph; their floors are declared and configurable but have no gate site yet.
- `verify-change.ps1` was not run for this task: two of its five paths are Core/Data (mapped) but the task's
  own acceptance needs the Server preview, which the fence refuses — the strongest achievable check is the
  focused suites above plus the full Core project run.
- The `~Fusion` filter is effectively "the whole Core project" (assembly-namespace match), which is why the
  number above is 9516 rather than a fusion-only subset; that is a property of the filter, not of the change.

# SP1.2 — C1 fix: world-turn uniques stop receiving the species term (defect correction, H1)

Spec: `layer-source-selector`, map C1. **H1 position 4** (`ST2.3` → `ST1.3` → `AE1.5` → **SP1.2** →
SP6.1 → EP4.18). `AE1.5` confirmed merged into this branch before starting
(`git merge-base --is-ancestor 04b8daa0 HEAD` = yes).

**Red-then-green, as the acceptance demands.** `HubInputsFor`'s inline body was extracted verbatim
(bug included) into `RpgStore.WorldTurnHubInputsForUnlocked` — a directly-testable unit instead of a
closure only reachable through a full district-assault turn-commit simulation. The new regression test
was run against the UNFIXED extraction first and failed for exactly the predicted reason
(`TotalForScope(CreatureType)` read 500, the leaked species term, not 0) — proving the falsifier is
real, not a test that passes by construction. The fix (ask `ProgressionLayerSelector`, derive the
empire from ownership via `SpecimenOwnerEmpireUnlocked` instead of species side) then turned it green.

**Classification: defect correction, not a re-bless** — the leaked species term for a district-assault
unique is exactly the C1 defect, corrected here per the spec's own instruction. **No golden moved**:
`BattleGoldenTests` is unaffected because it exercises the LAWN/battle path, never
`RpgStore.WorldTurns.cs`'s district-assault provider — confirmed by running it green (5/5) after the
fix, not merely assumed. H1's re-bless-in-the-same-commit rule has nothing to re-bless this time.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A Data test is written first and fails against today's code | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurnHubInputsFor" --nologo` (run against the unfixed extraction) | RED, as designed: `A_unique_specimen_with_a_levelled_species_composes_commander_and_its_own_allocation_only` expected 0, got 500 (the leaked species term); `A_specimen_with_no_empire_id_stamped_yet_falls_back_to_the_human_empire` expected 999, got 0 (proves the OLD empire-by-side derivation, not just the species leak) | `WorldTurnHubInputsForTests.cs` |
| `HubInputsFor` asks the selector; specimen's empire from ownership; the literal `$"player:{header.PlayerId}"` goes through one call site | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn" --nologo` (after the fix) | GREEN — pass 18/18 | `RpgStore.WorldTurns.cs` (`WorldTurnHubInputsForUnlocked`), `RpgStore.SaveEmpires.cs` (`SpecimenOwnerEmpireUnlocked`, new — the unlocked counterpart `SpecimenOwnerEmpire` now delegates to) |
| Defect correction, not a re-bless; any golden that pinned the leaked term corrected in the same commit | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGoldenTests" --nologo` | pass 5/5 — no golden moved (this provider is world-turn-only, never on the lawn/battle golden path) | — |
| No regression: every `SpecimenOwnerEmpire` caller | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenOwnership\|FullyQualifiedName~AiEmpireSpecimen\|FullyQualifiedName~ZombossDeployStore\|FullyQualifiedName~UniqueActorStoreTests" --nologo` | pass 63/63 | — |
| `guard-actor-hub.ps1` green | `.\scripts\guard-actor-hub.ps1` | pass | — |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
| Build | `dotnet build gk-core/src/FusionRpg.Data/FusionRpg.Data.csproj --nologo` | Build succeeded, 0 errors (3 pre-existing unrelated warnings) | — |

**Note for SE4.34/SE4.35** (same provider, key encoder and human-empire typing): `$"player:{playerId}"`
is now built at exactly ONE call site inside `WorldTurnHubInputsForUnlocked` (was already one site
before this change; unchanged by this task, X9's own job to retire it behind `CommanderScopeKey`).

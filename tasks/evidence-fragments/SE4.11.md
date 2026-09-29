# SE4.11 — `SaveId`, `EmpireRef`, `EmpireController`, and the new-save registry

Spec: docs/architecture/solid-enforcement/spec-save-identity.md

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The three types in `FusionRpg.Core.Saves`; `EmpireController` pinned at two members **with the closed-vocabulary reason** | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Saves\|FullyQualifiedName~NewSaveEmpires" -v q --nologo` | pass — 22/22; `The_controller_vocabulary_is_the_two_the_spec_names` asserts 2 members and both tokens | `gk-core/src/FusionRpg.Core/Saves/SaveId.cs` |
| The authored registry has the two rows (`dave`/`human`, `zomboss`/`ai`) | same filter | pass — `The_shipped_registry_has_exactly_one_human_and_the_two_well_known_empires` | `gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json` |
| Its validator checks schema, closed `controller` membership, exactly one `human` row and `empireId` shape, **never a row count**; a falsifier per rule | same filter | pass — `A_wrong_schema_version_is_refused`, `An_unknown_or_miscased_controller_is_refused` (3 cases), `A_second_human_row_is_refused`, `No_human_row_is_refused`, `An_empire_id_that_is_not_a_bare_faction_token_is_refused` (2 cases). No assertion counts rows | `gk-core/src/FusionRpg.Core/Saves/NewSaveEmpires.cs` |
| The debt ledger gains the `solid` row "empire is a player row / Zomboss is a player found by name" (next SR id), struck by SE4.43 | (read) `docs/architecture/solid-enforcement/spec-debt-ledger.md` | pass — `SR-24` added (SE4.43 strikes it) | spec-debt-ledger.md |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Saves/SaveId.cs,gk-core/src/FusionRpg.Core/Saves/NewSaveEmpires.cs,gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json,tests/FusionRpg.Core.Tests/Saves/NewSaveEmpiresTests.cs,gk-core/scripts/verification-boundaries.v1.json,docs/architecture/solid-enforcement/spec-debt-ledger.md -Session summoner-convergence-lane-b-20260919` | Core 14235/14236 — the one red is the **named pre-existing CRLF worktree artifact** `DungeonLootTableSeedFileTests…_byte_for_byte_no_hand_edits`; `-PlanOnly` resolved every path to exactly one owner. Run directly: `guard-verification-boundaries` 14/14 and the integrity guard OK | gate recorded with that named exception |

Boundary additions this task: owner `new-save-empires-registry` (`gk-data/packs/fusion/data/seed/saves/**`) and `solid-enforcement-specs`
(`docs/architecture/solid-enforcement/**`), both previously `VERIFICATION BOUNDARY MISSING`.

# EP2.1 — `AnchorRow` carries `speciesKind` (closed vocabulary, consumed)

Spec: `docs/architecture/empire-progression/spec-favour-detector.md` ("The population is real
creatures only"). **Premise already satisfied**: `creature-seed` CS13 (commit `be3ac8a6`) landed
`AnchorRow.SpeciesKind` (raw string, parsed by `AnchorRowReader`) with the runtime interpreter
`CreatureAdmission.ExcludedKind`. No field was added. This commit lands the part that was missing —
the generation layer's one read of the mark — plus the three-member pin.

| Criterion | Command | Result | Artifact |
| --- | --- | --- | --- |
| The reader exposes `speciesKind` (the field, and this task, are consumed) | `git show be3ac8a6 --stat` / `git log -1 --format=%h%x20%s be3ac8a6` | `be3ac8a6 creature-seed CS13: the speciesKind "excluded" mirror, refused at the one declaring site` — `AnchorRow.cs` +51/−?, `AnchorSpeciesKind` therefore adds no field | `gk-core/src/FusionRpg.Core/Creatures/Generation/AnchorRow.cs` |
| A closed vocabulary read, its three members pinned, with the reason | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AnchorRow"` | pass — 16 passed / 0 failed. `The_vocabulary_is_the_three_ruled_members_and_nothing_else` pins `creature · mimic · excluded` (a code-owned vocabulary, R-CS4/`SPECIES_KIND`; the species roster is a population and is never pinned this way) | `gk-core/tests/FusionRpg.Core.Tests/Creatures/AnchorRowReaderTests.cs` (new) |
| Exclusion is never inferred; `mimic` is roster | same run | pass — `A_pre_mark_anchor_reads_null_and_is_never_inferred_excluded`, and the 6-case theory: absent/empty/`Excluded`/`exclud`/`creature`/`mimic` → false, `excluded` → true | same file |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Creatures/Generation/AnchorSpeciesKind.cs,gk-core/tests/FusionRpg.Core.Tests/Creatures/AnchorRowReaderTests.cs -Session empire-progression-20260920` | **no focused boundary**: both paths resolve `core-fallback (module)` → whole Core project, `Failed: 4, Passed: 14907, Total: 14911` — the four are the pre-existing ISG-F1 set (socket-words corpus untracked, FamilyExpandGen byte drift, a uniques count, an omni gem); none touches this change, and EP2.1's own 16 tests are inside `Passed`. `gk-core/scripts/verification-boundaries.v1.json` is outside this lane's fence → reported, not compensated | — |
| Not proved | — | The read is not yet reached by a production host: `BuildFavourMeasure`'s population filter (EP2.2, next commit) is its first caller. No live/game evidence; this is offline generation code | — |

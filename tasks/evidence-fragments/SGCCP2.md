# SGCCP2 — species-gear-chain Phase 2 checkpoint (five of six boxes; the sixth is the owner review)

The todo's `### Checkpoint — Phase 2`. Every row was re-run in this session on this branch and the
numbers are copied from those runs. The sixth box ("Review with owner before Phase 3") is external and
stays open by rule.

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| All ten authored `elevate` recipes execute end to end (T26) | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Every_authored_elevate" -v minimal --nologo` | exit=0 :: `Passed: 1, Failed: 0` — the corpus-read loop climbs every authored recipe exactly one rung, no count pinned | gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs |
| A socketed gem measurably changes a combat number, proven through `ActorHub` (T21–22) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~EquipAtomSourceIdTests" -v minimal --nologo`; `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EquipProjection" -v minimal --nologo` | exit=0 :: Core `Passed: 4` — the NEW `A_socketed_insert_moves_the_channel_through_ActorHub_and_is_attributed_to_the_insert` reads the channel 5 → 50 with the contribution `insert:armament-primary:item-stem#1`, value 45; Data `Passed: 5` | gk-core/tests/FusionRpg.Core.Tests/Battle/EquipAtomSourceIdTests.cs, gk-core/tests/FusionRpg.Data.Tests/Items/EquipProjectionSocketsTests.cs |
| `craft-risk-ladder` is complete, Stages 1–4 (T10/T24) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CraftRisk\|FullyQualifiedName~Potential" -v minimal --nologo` | exit=0 :: `Passed: 21, Failed: 0` | gk-core/src/FusionRpg.Core/Items/Materials/CraftRiskPolicy.cs |
| `guard-actor-hub.ps1`, `guard-dal.ps1` green | `powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/guard-actor-hub.ps1`; same for `./scripts/guard-dal.ps1` | `ACTOR-HUB GUARD OK`; `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data` | — |
| `themes.v2.json` published; 844 bound set entries unaffected | read-only python sweep over `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v1.json`, `…/themes.v2.json` and `gk-data/packs/fusion/data/seed/items/sets/*.json` | 904 rows in BOTH registries — **0 keys dropped, 0 added**, so no `themeKey` was renamed; 844 `creature.*`-bound entries, **0 unresolved** against v2 (and 0 against v1); the other 66 are `build.*` 36 + `theme.*` 30 | gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json |
| Review with owner before Phase 3 | — | **stays open** — external (owner), per the todo's own Phase 1→2 precedent at `:677` | — |

Notes
- The socket box was the one with no test to point at before this run: the Data projector proved a
  binding exists, and `EquipAtomSource`'s insert arm had no test anywhere — only the comment at
  `gk-core/src/FusionRpg.Core/Battle/EquipAtomSource.cs:155`. The new test is the first in the repo to drive an
  `insert:` contribution through `ActorHub.ResolveDerivedWithContributions` and read the channel back.
- `verify-change.ps1 -Paths gk-core/tests/FusionRpg.Core.Tests/Battle/EquipAtomSourceIdTests.cs` -> exit 0,
  Core **14900 passed / 0 failed** (the new test is the 14900th; the suite was 14899 before it).
- NOT proven: none of these is a live-game reading — every box is a unit/test-level reading, which is
  what this checkpoint's own wording asks for. The sixth box is not this lane's to close.

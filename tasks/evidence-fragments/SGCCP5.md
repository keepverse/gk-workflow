# SGCCP5 — species-gear-chain Phase 5 checkpoint (`species-materials`)

The todo's `### Checkpoint — Phase 5` (four boxes, none owner-gated). Every row below was re-run in
this session, on this branch, with the number quoted from that run's own output. Phase 5 follows T34d,
whose fragment (`tasks/evidence-fragments/T34d.md`) carries the publish itself.

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| A species-bound set piece above the threshold rung is enhanced with its own species' material, end to end (T34d) | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchSpeciesWiringTests" -v minimal --nologo` | exit=0 :: `Passed: 3, Failed: 0` — runs against the real `materials.v4.json`, no synthetic mutation | gk-core/src/FusionRpg.Server/ItemWorkbench.cs, gk-core/data/tuning/materials.v4.json |
| Trophy registry reconciles, `--check` green in CI, no `trophy.general.*` id anywhere | `cd gk-forge/tools/seedsmith; python -m seedsmith.adapters.items.trophyplan.run --check` (the command `.github/workflows/ci.yml:418` runs) | exit=0 :: `"drift": 0`, 1784 species / 1816 family entries; `grep -c "trophy.general" gk-data/packs/fusion/data/seed/items/materials/trophy-registry.json` -> `0` | gk-data/packs/fusion/data/seed/items/materials/trophy-registry.json |
| Expedition manifests byte-identical with and without trophy groups; a replayed kill credits once | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ExpeditionResolverTests\|FullyQualifiedName~LootPipelineTrophyTests\|FullyQualifiedName~MaterialTrophyResolveTests" -v minimal --nologo` | exit=0 :: `Passed: 28, Failed: 0` — the four locked tier goldens are unchanged with trophy groups present; `LootPipelineTrophyTests` carries the replay-credits-once case | gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs, gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs |
| `materials` revisions on disk in ledger order; the host reads the latest | `ls data/tuning/materials.v*.json` + `grep -n "materials.v" gk-core/src/FusionRpg.Server/Program.cs` | v1, v2, v3, v4 all present and unretired; the host reads `materials.v4.json` (`gk-core/src/FusionRpg.Server/Program.cs:343`) — same order T34d's fragment records (`v3 -> v4`) | gk-core/src/FusionRpg.Server/Program.cs:343 |

Notes
- Box 2's `--check` is the CI gate itself (`.github/workflows/ci.yml:418`), so "green here" is the
  same evidence CI would read; the run is the tool's own `--check`, not a re-implementation.
- Not re-pinned anywhere: every row above is an executed reading, and no test was added or moved by this
  checkpoint — it only records what the four boxes ask.
- The sibling `### Checkpoint — Phase 6 (craft-assurance)` is already wholly ticked in the todo; Phases
  2-4 carry open boxes this lane did not close (Phase 2 box 2 needs a socket-contribution-through-
  `ActorHub` test this lane could not point at, and each of Phases 2-4 ends in "Review with owner").

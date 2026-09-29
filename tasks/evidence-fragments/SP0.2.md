# SP0.2 — `SpeciesRollPreview`: the delayed, deterministic, never-stored roll

Spec: docs/architecture/species-progression/spec-species-mod-ledger.md (behaviour 2)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `SpeciesRollPreview.For(worldSeed, speciesId, catalogRevision, contentTheta)` calls the same per-species roll `SpeciesMaterialiser` performs, with the same `WorldSeed.DeriveRollSeed(worldSeed, "species", speciesId)` seed; the same inputs give the same atoms | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesRollPreview\|FullyQualifiedName~SpeciesMaterialiser" -v q --nologo` | pass — 5/5; `The_same_inputs_give_the_same_atoms` (fingerprint equality) and `The_preview_is_the_same_roll_the_materialiser_performs` (equality with `SpeciesMaterialiser.Materialise` on the same seed/revision, i.e. the parity is proven, not asserted from source) | `gk-core/src/FusionRpg.Core/Creatures/Materialise/SpeciesRollPreview.cs` |
| Two different world seeds give differing previews (restates `Two_real_players_get_differing_rosters_…`) | same filter | pass — `Two_different_world_seeds_give_differing_previews` asserts the derived `RollSeed` differs | same |
| Calling the preview writes nothing (no `effect_instance` row) | same filter | pass by construction + test — the function is pure (`seed + catalog in, one instance out`), takes no store and holds no state (`The_preview_holds_no_state_between_calls`). The **row-level** half — a save that never fused has zero species-origin `effect_instance` rows — is SP0.4's own production-path regression, since only a store can observe a table. The Guard.Tests purity guard scans `SpeciesMaterialiser.cs` only, so it is **not** cited as covering this file | same |
| Signature note | — | the refusal for a species with no container is the endpoint's named code `picks.source-not-materialised` (the case SP0.3 pins), carried in a small result record; `AtomRejection`'s enum reason cannot carry a `picks.*` code | same |

`Path-owned`: Core paths resolve to `core-fallback` / `core-tests-fallback` (the same owners the task's Verify line names).

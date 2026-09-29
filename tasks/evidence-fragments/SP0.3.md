# SP0.3 — Fusion writes one ledger row; its guard and pick sources read the ledger and the preview

Spec: docs/architecture/species-progression/spec-species-mod-ledger.md (behaviour 3–5)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The fusion transaction writes the instance **and** one ledger row: `mechanism = fusion-pick`, `correlation_id` = the minted output id, owner = `EmpireRef(save, HumanEmpireOf(save))`; a replay writes no second row | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~FusionInheritancePicks\|FullyQualifiedName~SpeciesModLedger" -v q --nologo` | pass — 14/14; `A_valid_affordable_pick_set_…` asserts the row's mechanism, `Empire == Dave` and `CorrelationId == outcome.Minted.Profile.InstanceId`; idempotency is the table's `UNIQUE(mechanism, correlation_id)` (SP0.1) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs` |
| `picks.already-materialised` now means "a `fusion-pick` row exists for (save, paying empire, output species)"; the nine refusal codes stay pinned; the case that still reaches `picks.source-not-materialised` (no container) is pinned | same filter | pass — `A_pick_set_is_refused_when_the_empire_already_holds_a_1b_row_for_the_output_species` (the gate now reads the ledger), `A_source_species_with_no_container_still_reaches_source_not_materialised`. The nine codes are untouched strings, and `Guard.Tests`' closed-vocabulary test passes (8/8 on the `PlayerSpecies\|SpeciesMaterialiser` filter) | `RpgStore.Fusion.cs` |
| The preview endpoint and the transaction call the same function; the atoms offered are exactly the atoms accepted | same filter | pass — both call `store.PickSourceAtoms`, and `Every_atom_the_preview_offers_is_one_the_transaction_accepts` drives the endpoint's own list through `ExecuteFusion` and asserts every offered atom lands in the ledger instance | `gk-core/src/FusionRpg.Server/FusionEndpoints.cs`, `RpgStore.SpeciesMods.cs` |
| No `player_species` reader/writer in the fusion path | `git grep -n "player_species\|GetSpecimenMaterialisedRoll" src/` | the fusion path no longer reads or writes it; the remaining production reader is the sheet join `UniqueActorHubCompose.cs:65` (SP0.5 repoints it) and the retired `RpgStore.PlayerSpecies.cs` writers (SP0.6) | — |
| Verify | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Fusion" -v q --nologo` · `.\scripts\guard-dal.ps1` | pass — Server 552/552; DAL guard OK | — |

`PickSourceAtoms(saveId, speciesId)` is the one shared function: the empire's ledger instance if it has
one, else `SpeciesRollPreview` — so an empire that has never fused offers a preview, and one that has
offers exactly what it accepted.

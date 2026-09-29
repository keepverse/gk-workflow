# SP0.1 — Layer-1b ledger table and store, born keyed `(save_id, empire_id)`

Spec: docs/architecture/species-progression/spec-species-mod-ledger.md

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `rpg_player_species_mod` exists exactly as the spec DDL defines it, with `UNIQUE(mechanism, correlation_id)`; appending the same correlation twice writes one row | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesModLedger" -v q --nologo` | pass — 5/5; `Appending_the_same_correlation_twice_writes_one_row` (second append returns false, one row) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs` |
| The store refuses an `(save_id, empire_id)` that `rpg_save_empires` does not hold | same filter | pass — `An_empire_that_is_not_the_saves_is_refused` throws `SpeciesModEmpireNotInSave` | same |
| `SpeciesModMechanism` is a closed enum (`FusionPick` → `"fusion-pick"`), membership pinned with the reason | same filter | pass — `The_mechanism_vocabulary_is_closed_at_the_one_the_spec_names` (1 member, token) | `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesModMechanism.cs` |
| Save B never lists save A's rows (in-memory store) | same filter | pass — `Save_B_never_lists_save_A_rows`, `An_empire_of_the_same_save_with_no_rows_lists_none` | same |
| `guard-dal` · path-owned verification | `.\scripts\guard-dal.ps1` · `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesModMechanism.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs,gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs -Session summoner-convergence-lane-b-20260919 -PlanOnly` | guard OK; plan exit 0, every path one owner (core + data + the dal/test-substrate guards) | — |

DDL as shipped (the spec's Ask-first boundary, shown for review in the commit):

```sql
CREATE TABLE IF NOT EXISTS rpg_player_species_mod (
  mod_id INTEGER PRIMARY KEY AUTOINCREMENT, save_id INTEGER NOT NULL, empire_id TEXT NOT NULL,
  species_id TEXT NOT NULL, mechanism TEXT NOT NULL, correlation_id TEXT NOT NULL,
  instance_id TEXT NOT NULL, catalog_revision INTEGER NOT NULL, created_utc TEXT NOT NULL,
  UNIQUE (mechanism, correlation_id));
CREATE INDEX IF NOT EXISTS ix_player_species_mod_owner
  ON rpg_player_species_mod(save_id, empire_id, species_id);
```

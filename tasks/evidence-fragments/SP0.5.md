# SP0.5 — The sheet reads 1b from the ledger; retire the specimen-roll reads of `player_species`

Spec: species-mod-ledger, ruling behaviour 1 ("a non-fuser composes no per-save roll").

**Reconciled two readings before writing code.** Acceptance line 1 requires the sheet join to show
NOTHING for a non-fuser (no preview fallback); line 3 requires `SpecimenMaterialisedRollTests` to
prove "a specimen's pickable atoms are its empire's ledger instance, or else the preview" (preview
fallback expected). These are not in tension: they describe two different, already-distinct seams —
the sheet-compose join (strict, ledger-only) and the fusion pick-source join (`PickSourceAtoms`,
ledger-or-preview, built in SP0.3). The restated test file now proves both, side by side, so the
distinction is visible to the next reader instead of merged by accident.

**Correction against the acceptance's literal text.** "`GetSpecimenMaterialisedRoll` and
`ListPlayerSpeciesInstanceMapUnlocked` have no caller and are removed" is true only for the first
method. `ListPlayerSpeciesInstanceMapUnlocked` still has one real caller,
`ReforgePlayerSpecies:157` — SP0.6 removes both together when it retires `ReforgePlayerSpecies`
itself. Removing the helper now would break a live method; left in place with a doc comment pointing
at SP0.6.

**Also closed SP0.4's own named blocker.** SP0.4's evidence (`tasks/evidence-fragments/SP0.4.md`)
recorded `gk-core/tests/FusionRpg.Guard.Tests/**` as refused to a prior write attempt and left an exact,
pre-specified replacement for `PlayerSpeciesMaterialiseCallerGuardTests.cs`'s three stale tests. This
session's own write to that file went through with no refusal, so the pre-specified replacement was
applied verbatim (test names, scan targets) rather than left red for a second pass.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `UniqueActorHubCompose`'s join reads the specimen's owner-empire LEDGER instance, not `GetSpecimenMaterialisedRoll`; a non-fuser composes nothing | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenMaterialisedRoll" --nologo` | pass 5/5 — `A_real_specimens_own_instanceId_resolves_to_its_empires_ledger_instance`, `A_specimen_whose_species_has_no_ledger_row_composes_nothing_ruling_behaviour_1`, plus the two null-safety facts | `RpgStore.PlayerSpecies.cs` (`GetSpecimenLedgerRoll`), `UniqueActorHubCompose.cs:65` |
| No regression: fusion pick-source (ledger-or-preview) and the ledger itself | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~FusionInheritancePicks\|FullyQualifiedName~SpeciesModLedger" --nologo` | pass 15/15, unchanged | — |
| `GetSpecimenMaterialisedRoll` removed; `ListPlayerSpeciesInstanceMapUnlocked` kept (still has a real caller — see correction above) | `git grep -n "GetSpecimenMaterialisedRoll" src/ tests/` | zero code hits (doc comments only, all correctly say "retired") | `RpgStore.PlayerSpecies.cs` |
| `SpecimenMaterialisedRollTests` restated: pickable atoms are the ledger instance, or else the preview | same Data.Tests run above | pass — `A_specimens_pickable_atoms_are_its_empires_ledger_instance_or_else_the_preview` proves `PickSourceAtoms` previews before a ledger row exists and switches to the ledger instance after `AppendSpeciesMod` | `SpecimenMaterialisedRollTests.cs` |
| Sheet composes correctly through the new join (no regression) | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Sheet" --nologo` | pass 12/12 | `UniqueActorHubCompose.cs` |
| Guard: the composer still reaches a species-passive join | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpecies" --nologo` | pass 5/5 — `The_rolled_species_instance_reaches_a_composer` repointed to `GetSpecimenLedgerRoll`; SP0.4's own two blocked tests (`No_production_code_rolls_a_players_species_eagerly`, `No_production_code_writes_layer_1b_outside_the_ledger_append`) applied and green, closing that blocker too | `PlayerSpeciesMaterialiseCallerGuardTests.cs` |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
| Build | `dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj --nologo` | Build succeeded, 0 errors (5 pre-existing unrelated warnings) | — |

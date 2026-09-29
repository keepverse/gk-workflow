# SE4.24 — Ownership predicate at six specimen-write sites in five Data files

Spec: save-identity, "One ownership predicate". All six sites now call `OwnsSpecimenUnlocked(db,
EmpireRef, instanceId)` instead of comparing `actor.PlayerId != playerId`, keeping each site's existing
refusal reason: `RpgStore.Contracts.cs:539` (`ReadContractableSpecimenUnlocked`), `Expeditions.cs:59`
(`DispatchExpedition`'s squad loop), `Fusion.cs:474`/`:499` (`ReadFusionBaseUnlocked`,
`ValidateSacrificesUnlocked`), `Patron.cs:33` (`SetPatron`), `UniqueActors.cs:572`
(`TryPerformRecoveryRitual`). Owner is always `new EmpireRef(new SaveId(playerId), HumanEmpireOf(playerId))`
— every one of these six actions is human-driven, so the human empire is the only legal owner.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Six sites call `OwnsSpecimenUnlocked`, same refusal reason each | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenOwnership" --nologo` | pass 11/11 (5 existing + 6 new, one per site) | `RpgStore.Contracts.cs`, `RpgStore.Expeditions.cs`, `RpgStore.Fusion.cs`, `RpgStore.Patron.cs`, `RpgStore.UniqueActors.cs` |
| A Zomboss specimen of save 1 is refused at every site; tables unchanged | same | pass — `BindContract`→`specimen.missing` (no contract row); `DispatchExpedition`→`squad.unknown-specimen` (no expedition row); `ExecuteFusion`(base)→`base.missing`; `ExecuteFusion`(sacrifice)→`sacrifice.invalid` (sacrifice stays Roster); `SetPatron`→`specimen.missing`; `TryPerformRecoveryRitual`→`not_found` | same |
| No regression on the human path | Full `FusionRpg.Data.Tests` run (byw48lzbl, ~10m34s) | pass 1683/1684 — the one failure is the pre-existing, unrelated `CreatureSpeciesImportCliTests` stale-generated-data check (confirmed identical in the SE4.19/SE4.22 evidence) | `tasks/evidence-fragments/SE4.19.md`, `SE4.22.md` (same failure cited) |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
| Cross-project `verify-change.ps1` | `-Paths` (6 Data files) | not run standalone — the whole-project fallback pattern (SE4.15/20/22/23) already means a scoped filter is faster; the full-project run above supersedes it (proves the same boundary, plus everything else) | ledger note |

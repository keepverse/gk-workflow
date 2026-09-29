# SE4.21 — Tier A store API takes `EmpireRef`; every award names its owner (G4)

Spec: save-identity G4/X11. `TryApplyXpUnlocked(EmpireRef)`, `ReadEmpireActorUnlocked`,
`CommanderLevelOf(SaveId, EmpireId)` are new; `ApplyRpgProgressionFromActivityUnlocked` takes
`SaveId` and throws when `save != SaveOfRunUnlocked(runId)`; both species-XP paths
(per-placement, run-completion) award to the same `owner`. Empire choice stays the human empire
(EP ai-empire-species owns the rule); a run resolving to no save awards nothing.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Fact for another save's run refused, rolled back | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ProgressionEmpireAwardTests" --nologo` | pass 4/4 — mismatch throws `InvalidOperationException` naming both saves, neither gains a row | `tests/.../ProgressionEmpireAwardTests.cs` (new) |
| Unknown run awards nothing; own run awards | same | pass — empty `Progression` + no row; positive control awards | same |
| Commander level reads the named empire's row | same | pass — equals the human player row; empire without a row reads 1 | `RpgStore.Progression.cs` |
| Existing progression/species suites green | `--filter "FullyQualifiedName~Progression\|FullyQualifiedName~SaveEmpires"`; `...~Allocation\|~Watermark\|~ColdArchive\|~SpeciesProgression` | pass 26/26; pass 55/55 (`SpeciesProgressionTests` now starts real runs — `RunId = 1` placeholders awarded nothing under the new guard) | `tests/.../SpeciesProgressionTests.cs` |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
| Full Data project | `verify-change.ps1 -Paths <files>` | **orchestrator-owned** — paths map to `data-fallback` (SE4.20 precedent, over agent cap). Two full runs hit a PRE-EXISTING flake: SE4.15/19 arming process-wide `FailureInjectorForTests`/`FailAfterStepForTests` races any parallel class ctor calling `Init→Migrate` (victims: SpeciesProgressionTests, WonderReachTests; stacks entirely in pre-existing code, untouched by this diff) | ledger note |

| Affecting | Unaffected (null `RunId` skips the guard) |
|---|---|
| `SpeciesProgressionTests` (10 `RunId = 1` → real runs) | `PvzActivityFactsPagingTests`, `RpgStoreDalSmokeTests`, capture path with same-save run |

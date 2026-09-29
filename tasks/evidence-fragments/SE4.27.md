# SE4.27 — Core ownership by empire: `SpecimenOwnershipOracle`, `KillCredit`

Spec: save-identity D4/G5. `SpecimenOwnershipOracle` constructor drops `myPlayerId`; the resolver is
`Func<string, EmpireController?>` and `RelationOf` answers Ally iff `Controller == Human`, Enemy for
any other registered controller, null when unregistered — no elimination, no "my id". `KillCredit`'s
`long? PlayerId` becomes `EmpireRef? SpecimenOwner` (a save id alone no longer names an empire after
SE4.22). Pure Core; zero production callers today (confirmed by grep) — SE4.28 wires the first one,
landing immediately after in this same session since it must fix `MatchHost.cs`'s existing construction
call to keep compiling (the Injector build cannot be verified locally, no MelonLoader game dir here).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Ally iff controller is Human; Enemy otherwise; null when unregistered | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpecimenOwnership" --nologo` | pass 9/9 (rewritten off the old id-comparison shape) | `SpecimenOwnershipOracle.cs` |
| A third registered empire resolves as an enemy with no code edit | same | pass — `A_third_registered_empire_resolves_as_an_enemy_with_no_code_edit`: two `Ai`-controlled ptrs (one literally named "a third empire's") both resolve Enemy off the same oracle, which never branches on which empire | same |
| `KillCredit` carries `EmpireRef? SpecimenOwner` | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~KillAttribution" --nologo` | pass 9/9 (renamed `PlayerId`→`SpecimenOwner`, `long?`→`EmpireRef?`; two specimens of the SAME save now used, matching the SE4.22 shape) | `KillAttribution.cs` |
| No regression | `--filter "FullyQualifiedName~Battle"` (Core.Tests, ~1400 tests) | pass 1398/1398 | — |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |

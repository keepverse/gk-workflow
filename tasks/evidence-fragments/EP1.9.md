# EP1.9 — The by-hand routes go through the gate; `POST /api/aptitudes/respec-quote`; the one-writer architecture test

Spec: docs/architecture/empire-progression/spec-specimen-respec-price.md

| Criterion | Command | Result |
|---|---|---|
| `/allocate` and `/unique/allocate` call `TryReallocate`; body gains `correlationId?`; response gains `priced`/`priceAmount`/`respecCount`/`soulBalance`; refusals reuse `correlation.missing`/`souls.insufficient` | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"` | pass (55/55) |
| `respec-quote` equals what the save then charges, for counts 0 to 3 (test 8) | same run — `RespecQuote_matchesWhatTheSubsequentAllocateThenCharges_forCounts0To3` (toggles one point between `Might`/`Vigor` so it needs only `Budget >= 1`, never a pinned commander-budget size) | pass |
| Architecture test 9: outside `RpgStore.AllocationRespec.cs`, the only writers of `Commander`/`UniqueCreature` are `RpgStore.Aptitudes.cs` and `DerivedAuditActor.Seed` | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~AllocationWriter"` | pass (2/2) — `RpgStore.AptitudePresets.cs` is a NAMED temporary allowance closed by EP1.10 (next task), not a silent exception |
| `GetAllocationRespecCount` (new, on `RpgStore.AllocationRespec.cs`) and every other AllocationRespec case | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationRespec"` | pass (13/13) |
| `guard-dal.ps1` (SQL stays inside `FusionRpg.Data`) | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` |
| Existing Aptitude surface (Get/Post commander+unique, species, speciesLayers) unaffected by the route rewrite | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudeEndpointsTests"`, run before this task's new tests were added | pass (17/17), confirmed pre-change baseline |

**On verification scope (2026-09-20 correction):** `verify-change.ps1 -Paths <the 4 touched files>` was
started but its resolved boundary fanned `RpgStore.AllocationRespec.cs` into the sharded Data.Tests run
(completed, `TEST-SHARDED OK: 4 shards, 1648 tests, no overlap`, exit 0) and then fanned the two Guard
paths into an UNFILTERED `FusionRpg.Guard.Tests` project run, which this machine's concurrent-session
load (30+ live `dotnet.exe` processes at the time) stretches well past ten minutes — confirmed
separately by running the whole Guard.Tests project directly, which itself exceeded a 280s foreground
window. Per the coordinator's correction, both backgrounded invocations were stopped (`TaskStop`) and
verification was completed instead as the four scoped, foreground commands actually listed in this
table above (the exact filters this task's own Verify line names) plus `guard-dal.ps1` for the SQL
boundary. No fan-out full-project run backs this evidence; the four rows above are the complete,
literal record of what ran and passed.

## Notes

- `GetAllocationRespecCount` (added this task, mirroring `GetSpeciesRespecCount`'s shape) reads
  `SpeciesBuildTuningHub.Tuning.UniqueRespec.DecayDays` on every `/respec-quote` call regardless of
  whether the proposed change is itself a respec — so every Server.Tests fixture that exercises this
  file now configures `SpeciesBuildTuningHub` in `InitializeAsync`, not only the species-respec tests.
- The additive (non-respec) path never reads `SpeciesBuildTuningHub` at all (`TryReallocateUnlocked`
  returns before the tuning read when `IsRespec` is false), so the pre-existing 17 Aptitude endpoint
  tests — none of which exercise a take-back — were unaffected by the route rewrite; confirmed by
  running them green before writing any new test.
- Test 8's "counts 0 to 3" parity loop toggles one point between two aptitudes (`Might`/`Vigor`)
  rather than draining a fixed budget size, so it needs only `Budget >= 1` — already guaranteed by the
  shipped tuning per the pre-existing `Post_withinBudget_...` test — and never pins the commander
  budget's own magnitude (population-pin discipline).
- `AllocationWriterGuardTests`'s allowlist names `RpgStore.AptitudePresets.cs` as a **temporary**,
  commented entry with an explicit `EP1.10 TODO` pointer (same idiom as
  `ActionBaseNoAtkReadGuardTests.cs`'s `LiveAtk` allowlist) — EP1.10 removes that one line once preset
  activation's commander/unique branches route through `TryReallocateUnlocked`.

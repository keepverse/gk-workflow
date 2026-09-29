# Manager acceptance review — build-preset BP1.11/BP1.12

**Reviewed lane:** `resume-11-build-preset-bp1112-20260925`

**Verdict:** GREEN for the two requested build-preset rows and their focused verification mapping.
The first-use schema ensure and SE4.37 policy consolidation remain explicit follow-ups.

## Review findings

BP1.11 adds only the two additive tables in `FusionRpg.Data`. Public operations ensure the schema on
their open connection, require the existing human `EmpireRef` for the save, filter by the strict
`(save_id, empire_id)` pair, validate through the shipped `BuildPresetShape`, apply the shipped soft
maximum only on create, replace/delete pieces transactionally, and project every stored piece on read.
Unknown or retired references remain visible as `missing`; they are never silently removed. The test
store proves reopen persistence and no cascade into the aptitude/item libraries.

BP1.12 maps GET/POST/PUT/DELETE under `/api/build-presets`; the wire `playerId` is the save id and
`EmpireScopeRequests.HumanOwnerOf` is the only empire source. `Program.cs` composes the route beside
the existing preset routes. The server tests exercise the real in-process host, second-save isolation,
owner mismatch, and no-write-on-refusal.

The worker's reported verification-registry gap is repaired in this review: focused `data-build-preset`
and `server-build-preset` owners now cover the new source/test paths, the Server test carries the
matching `server.build-preset` trait, and shared `Program.cs` remains on the non-feature-specific
Server fallback. `guard-verification-boundaries.py` and the focused mapping tests pass.

No Contracts, Core BuildPreset types, tuning/generated data, CI, or unrelated paths changed.

## Independent checks

```text
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~BuildPreset" --no-restore
# exit 0 (worker count: 10/10)

dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetEndpoints" --no-restore
# exit 0 (worker count: 14/14)

dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "VerificationId=guard.unique-allocation-reader" --no-restore
# exit 0 (worker count: 2/2)

dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary" --no-restore
# exit 0

scripts/guard-dal.ps1
# DAL GUARD OK; exit 0

gk-core/scripts/guard-test-substrate.py
# TEST SUBSTRATE GUARD OK; exit 0

gk-core/scripts/guard-verification-boundaries.py
# VERIFICATION BOUNDARY GUARD OK

verify-change.ps1 -Paths <five executable feature paths>
  -Session resume-11-build-preset-bp1112-20260925 -PlanOnly -Format json
# exit 0; focused data.build-preset and server.build-preset owners selected;
# shared Program.cs remains server-fallback; fullEvidenceOwner CI/nightly/release

git diff --check
# exit 0
```

The first PlanOnly attempt included the registry path before its new acceptance session record was
present in the isolated review worktree; the harness correctly failed closed on scope. The five-path
retry passed after the mapping repair, and the registry guard separately passed. This is recorded as
harness setup evidence, not a product failure. External log SHA-256:
`2464A677C2EA0BCC78C4CF911232131F1EC0AD2CD4EB52E2C83211454BD56F1A`.

## Open boundaries

- `RpgStore.cs` boot-time schema registration was outside the worker fence; first-use ensure is
  idempotent and reopen-tested. A one-line boot hook may be a separately authorized follow-up.
- The local human-empire exception should be replaced when SE4.37's shared helper lands.
- The full unfiltered aggregate remains CI/nightly/release-owned; no full-suite claim is made.
- No generated data or population count was changed.

## Exact-SHA steps remaining

1. Commit the feature, mapping, trait, and report set at an exact SHA.
2. Run the focused checks and registry guard from a clean detached checkout.
3. Write a schema-v2 acceptance artifact and merge only that SHA.
4. Keep boot-hook/SE4.37 decisions open in the owning ledgers.

<<<REPORT {"status":"done","summary":"Accepted BP1.11/BP1.12 with the focused verification-boundary repair. The Data store provides additive human-empire-scoped preset/piece CRUD, shipped shape/soft-max refusals, validate-on-read missing projections, non-cascading delete, and reopen persistence; the four Server routes use save-scoped playerId and preserve structural refusals. Focused Data 10/10, Server 14/14, unique-allocation 2/2, verification-boundary tests, DAL/test-substrate guards, registry guard, PlanOnly, and diff checks passed. First-use schema ensure and SE4.37 consolidation remain open.","changed_files":["gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs","gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs","gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs","gk-core/src/FusionRpg.Server/Program.cs","gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs","gk-core/scripts/verification-boundaries.v1.json","tasks/reports/resume-11-build-preset-bp1112-20260925.md","tasks/reports/resume-17-build-preset-acceptance-20260925.md"],"verification":["focused Data tests exit 0; worker count 10/10","focused Server tests exit 0; worker count 14/14","unique-allocation guard test exit 0; worker count 2/2","VerificationBoundary tests exit 0","DAL guard exit 0","test-substrate guard exit 0","guard-verification-boundaries exit 0","path-owned PlanOnly for five executable paths exit 0; focused owners selected","git diff --check exit 0","external log SHA-256 2464A677C2EA0BCC78C4CF911232131F1EC0AD2CD4EB52E2C83211454BD56F1A"],"open_issues":["exact-SHA clean checkout and artifact remain","RpgStore.cs boot-time schema hook and SE4.37 shared helper remain follow-ups","full aggregate remains CI/nightly/release-owned"],"next_steps":["commit exact reviewed SHA","clean-checkout focused verification and registry guard","merge exact SHA and record schema-v2 artifact"]} REPORT>>>

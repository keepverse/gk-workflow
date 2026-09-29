# Manager acceptance review — RS-F27 progression-ledger measurement

**Reviewed lane:** `resume-13-rpg-simulator-rsf27-20260925`

**Verdict:** GREEN for the RS-F27 real-run measurement and the legal-empty policy. A deterministic
victory/stalemate selection seam remains an open owner decision; no production outcome behavior was
changed.

## Review findings

The heavy test creates a fresh `RpgApiFactory` for each sample, drives the checked-in scenario, and
reads the ordinary `read.runs` and `read.progression.ledger` routes. It accepts only the closed
`victory`/`defeat`/`stalemate` vocabulary, records the read sources and ledger rows, and applies a
non-vacuity floor only when a real read-back outcome is `defeat`. It does not inject rows, call a
simulator shortcut, or require a particular outcome distribution.

The fixture note records the measured policy rather than a population assertion: empty progression is
legal for victory/stalemate, while a real defeat must produce the player XP row. The 20 samples were
all defeats because the expedition and summon seeds are still minted by the Server; the report keeps
that coverage limitation open instead of fabricating the missing outcomes.

## Independent checks

```text
dotnet run --project gk-core/tools/RpgSim/RpgSim.csproj -- --scenario gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json --validate
# ok:true; 36 steps, 7 reads, 22 expects, 1 digest; exit 0

FUSIONRPG_RSF27_SAMPLES=20 dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --no-restore --filter FullyQualifiedName~RS_F27_measures_progression_ledger_non_vacuity_across_real_runs
# exit 0; 20/20 samples passed; all defeat; ledger lengths 1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1

dotnet test gk-core/tests/FusionRpg.Core.RpgXpAwardMapTests.Tests/FusionRpg.Core.RpgXpAwardMapTests.Tests.csproj --filter FullyQualifiedName~RpgXpAwardMapTests
# exit 0; 20 passed

dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --no-restore --filter FullyQualifiedName~RpgScenarioSlice0E2ETests|FullyQualifiedName~RpgSimInProcHostTests|FullyQualifiedName~RpgSimFormatContractTests
# exit 0; 26 passed

dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --no-restore --filter FullyQualifiedName~RpgSimRunnerTests|FullyQualifiedName~RpgSimVerdictContractTests
# exit 0; 20 passed

verify-change.ps1 -Paths <two executable paths> -Session resume-13-rpg-simulator-rsf27-20260925 -PlanOnly
# exit 0; e2e scenario-fixture and e2e fallback owners, test-substrate guard, fullEvidenceOwner CI/nightly/release

verify-change.ps1 -Paths <two executable paths> -Session resume-13-rpg-simulator-rsf27-20260925
# TEST SUBSTRATE GUARD OK; E2E boundary 281 passed, 0 failed, 0 skipped; exit 0

git diff --check
# exit 0
```

External scoped log SHA-256:
`D87C5E523E9534E9260024242801D2E051D6C79E7603710E26E1E73163ED48DD`.

## Open boundaries

- The current scenario does not cover victory or stalemate; the Server-minted seed seam is not in
  this fence and remains an owner/design follow-up.
- The full unfiltered aggregate remains CI/nightly/release-owned; the scoped 281-test E2E result is
  the accepted local evidence.
- No production `RpgXpAwardMap`, generated data, CI, or Seedsmith path changed.

## Exact-SHA steps remaining

1. Commit the two changed executable/fixture paths and report at an exact SHA.
2. Run the same validation/measurement/focused E2E checks from a clean detached checkout.
3. Write a schema-v2 acceptance artifact and merge only that SHA.

<<<REPORT {"status":"done","summary":"Accepted the RS-F27 measurement and legal-empty policy: fresh-host real read-backs over 20 samples measured defeat-only coverage, a conditional non-vacuity floor for real defeats, and documented that victory/stalemate ledgers may legally be empty. Scenario validation, 20-sample measurement, Core XP-map 20/20, focused E2E 26/26, runner 20/20, scoped E2E 281/281, PlanOnly, and diff checks passed. Deterministic victory/stalemate selection remains open; no production outcome or generated data changed.","changed_files":["gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs","gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json","tasks/reports/resume-13-rpg-simulator-rsf27-20260925.md","tasks/reports/resume-18-rpg-simulator-rsf27-acceptance-20260925.md"],"verification":["scenario validation exit 0","20-sample RS-F27 measurement exit 0; all defeat; recorded ledger-length vector","RpgXpAwardMapTests 20/20","focused E2E contracts 26/26","RpgSim runner/verdict contracts 20/20","path-owned PlanOnly exit 0","scoped verify-change E2E boundary 281/281, 0 failed, 0 skipped; test-substrate guard passed","git diff --check exit 0","external log SHA-256 D87C5E523E9534E9260024242801D2E051D6C79E7603710E26E1E73163ED48DD"],"open_issues":["victory/stalemate outcome coverage and deterministic seed seam remain open","full aggregate remains CI/nightly/release-owned","exact-SHA clean checkout and artifact remain"],"next_steps":["commit exact reviewed SHA","clean-checkout rerun and status proof","merge exact SHA and record schema-v2 artifact"]} REPORT>>>

# RS-F27 exact defeat-floor acceptance — 2026-09-25

## Verdict

**GREEN for the exact reviewed SHA:** `4f78ed6c9ebe744c2b69232d325a67348161326f`

This is lane acceptance for the test-only RS-F27 follow-up. It is not a current-head post-merge
`GREEN`, release acceptance, browser proof, or live proof. Integration remains deferred while the
unrelated `worktree-cleanup-20260925` session owns dirty paths in the main checkout.

## Exact reviewed change

Base SHA: `6d77888cca860805e5a11e617e201847e01c16b7`

The reviewed commit changes exactly:

- `gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs`
- `tasks/reports/resume-20-rpg-simulator-defeat-floor-20260925.md`
- `tasks/sessions/resume-20-rpg-sim-defeat-floor-review-20260925.json`

The test replaces the weak non-empty defeat condition with an exact wire-contract check for
`kind=player && reason=defeat`. It does not force outcomes, insert ledger rows, change the scenario
fixture, or modify the accepted `resume-13` report.

## Review and verification

The manager created a fresh review worktree from the exact base and a separate detached checkout at
the reviewed SHA. The older dirty `resume-19` review draft was not adopted.

### Worker evidence

The worker report is retained in the reviewed commit. It records the original false-green shape, the
conditional policy, the 20-sample output, and the explicit limitations.

### Manager checks

```powershell
dotnet restore gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --nologo
```

Exit `0`; the E2E project and dependencies restored.

```powershell
$env:FUSIONRPG_RSF27_SAMPLES = '20'
dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --nologo --no-restore --filter "FullyQualifiedName~RS_F27_measures_progression_ledger_non_vacuity_across_real_runs" --logger "console;verbosity=detailed"
```

Exit `0`; `Passed: 1`, `Failed: 0`, `Total: 1`. All 20 real fresh-host samples were `defeat`, and
all 20 normal progression-ledger reads contained the exact `player:defeat` row.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs','tasks/reports/resume-20-rpg-simulator-defeat-floor-20260925.md') -Session resume-20-rpg-sim-defeat-floor-review-20260925
```

Exit `0`:

- test-substrate guard passed;
- E2E boundary: `281` passed, `0` failed, `0` skipped;
- Guard boundary: `689` passed, `0` failed, `0` skipped;
- full unfiltered evidence remains CI/nightly/release-owned.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-sim-fabrication.ps1
```

Exit `0`; `SIM FABRICATION GUARD OK` (`1` scenario, `36` steps, `7` reads, `1` sanctioned
`test.*` step).

```powershell
python scripts/audit-doc-citations.py --scope tasks/reports/resume-20-rpg-simulator-defeat-floor-20260925.md --strict
```

Exit `0`; `6` resolvable citations, `0 HIGH` findings.

### Clean checkout

The detached checkout was exactly:

- HEAD: `4f78ed6c9ebe744c2b69232d325a67348161326f`;
- branch: detached `HEAD`;
- status before and after: `CLEAN`;
- diff from the base: exactly the three paths listed above;
- `git diff --check`: exit `0`.

An external evidence bundle was retained outside the repository with SHA-256
`22C10568A43B063BA8F1F4BD5D93CA62ECA314B750CFA9962CAA8B2498752880`.

## Limitations and routing

- The 20 samples covered `defeat` only. The legal-empty `victory` and `stalemate` branches remain
  unexercised.
- Deterministic outcome selection remains an open simulator seam.
- No production outcome, generated seed, scenario fixture, live-game, browser, or current-head gate
  behavior was accepted by this artifact.
- The exact SHA may be merged only after the dirty integration cleanup boundary is closed and the
  normal merged-head gate is rerun. The accepted prior RS-F27 artifact remains historical; this is
  a separate follow-up SHA.

The machine-local acceptance artifact is
`.claude/cmdc-agents/acceptance/resume-20-rpg-sim-defeat-floor-review-20260925-4f78ed6c.json`.
It pins the full SHA, clean checkout, commands, outputs, attribution, and known limitations.

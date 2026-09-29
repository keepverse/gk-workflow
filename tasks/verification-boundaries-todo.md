# Verification boundaries — implementation tasks

## v1 delivered

- [x] Registry v1: C# production-owner fallbacks plus the first curated focused Data socket
  boundary and test-source mappings.
  - Verify: `gk-core/scripts/guard-verification-boundaries.py`.
- [x] Positive `VerificationId` selection: `data.item-socket` selects only the socket family.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj -c Release --filter "VerificationId=data.item-socket"`.
- [x] Path planner/runner: explicit added/modified paths, deleted-path support, mandatory session
  scope by default, deterministic owner resolution, additive seam support, and no broad fallback.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release --filter "FullyQualifiedName~VerificationBoundaryWorkflowTests"`.
- [x] Integrity gate: schema/allowlist/path checks, source-owner coverage, duplicate-owner-pattern
  rejection, and zero-match `VerificationId` detection; run by CI and by the runner before use.
  - Verify: `gk-core/scripts/guard-verification-boundaries.py`.
- [x] Workflow adoption: `test-fast.ps1` requires an explicit project or `-AllDefault`; AGENTS and
  the testing standard make session-scoped `verify-change.ps1` the agent default.

## Follow-on adoption slices

~~Add curated focused groups...~~ — **SUPERSEDED 2026-09-20** (`backlog-clean-up` `paperwork-reconcile`
P7): this whole section is superseded by `test-verification-boundary` (`summoner-convergence` lane D
— a convergence file, read-only here). That program's own map explicitly supersedes this one
(`docs/architecture/test-verification-boundary-map.md:5-8` "Predecessor program, whose decisions this
one keeps"). No separate action here; the 4 rows below stay for history.

- [ ] Add curated focused groups when a C# migration fallback proves too broad. Each new boundary
  needs a behavior trait and a registry rationale; do not guess from project references.
- [ ] Add a real cross-module seam only when a named contract needs additional proof; fixture-only
  seams are not justification to invent one.
- [ ] Add web/tools/generated/config roots with their own fixed validators. They must not be
  misrepresented as C# `dotnet test` ownership.
- [ ] Integrate `-VerificationPaths` into `deploy-play.ps1` after reconciling its concurrently owned
  deployment regions.

## v1 proof record

```powershell
# Representative focused production change (two guards + eight socket tests):
.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs -AllowUnscoped

# Normal agent invocation (session is required):
.\scripts\verify-change.ps1 -Paths gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs `
  -Session verification-boundaries-20260913-6f31
```

CI/nightly/release remain the unfiltered full-evidence owners; neither command authorizes a broad
suite after a failure or an unmapped path.

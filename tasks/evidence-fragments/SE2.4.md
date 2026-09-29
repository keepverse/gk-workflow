# SE2.4 — `guard-repo-boundary.py` (B1-B3)

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| B1 graph read from csproj at build time, pinned as measured | `grep ProjectReference` on all 5 csproj | matches the spec's table exactly (Contracts: none; Core/CheatCore: Contracts; Data: +Core+CheatCore; Server: +Data) | gk-core/scripts/guard-repo-boundary.py |
| B1/B2 XML element parse, never substring; InternalsVisibleTo non-regression | `dotnet test --filter "FullyQualifiedName~RepoBoundaryGuardTests"` | **10/10 pass**: out-of-graph edge fails B1; `InternalsVisibleTo Include="FusionRpg.Data.Tests"` passes (the `core-data-guard-substring-scan` regression); `using UnityEngine`/`PackageReference HarmonyLib` fail B2 | gk-core/tests/FusionRpg.Guard.Tests/RepoBoundaryGuardTests.cs |
| B3 frozen paths, diff-based, temp git repo | same test run | modifying `tasks/plan.md` fails; adding `tasks/widget-plan.md` passes; adding root `SPEC.md` fails | gk-core/scripts/guard-repo-boundary.py |
| Real tree passes; lands directly `ci`/`gating` | `powershell gk-core/scripts/guard-repo-boundary.py`; `run-guards.ps1 -Tier ci` | `REPO BOUNDARY GUARD OK`; **16/16 CI guards green** | gk-core/scripts/enforcement-registry.v1.json |
| Two invariant rows | read registry | `dg-9-standalone-first` -> `guards:["repo-boundary"]` (was `unguardableReason`-only; the assembly-boundary half is now scannable); new `claude-plan-paths` -> `["repo-boundary"]` | gk-core/scripts/enforcement-registry.v1.json |

# TVB5.5 — Author `gk-core/tests/core-test-projects.v1.json`

No owner review of the grouping happened in this session, so per the task's own acceptance ("the
clean-SCC default if unanswered") this is TVB1.10's analyzer proposal at `analyzerCommit`
`274824c9c955f31856200ed2843c462fe1eb4173` (post the SplitPlanner Links/Content fix below), authored by
hand into the manifest shape TVB5.2 validates — the manifest is authored data (A1: "new, authored"),
never generated output, so every judgment call below is named rather than left implicit.

## What the analyzer gave for free, and what it could not see

Re-ran `TestSplitAnalyzer` fresh (`dotnet run --project gk-core/tools/TestSplitAnalyzer -c Release --
--project gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj --configuration Release --format json`):
68 clean candidates (unchanged from TVB5.1.k's reading), `blocksSplit: []`, `coreInternals` per-candidate
(7 true: Atoms, Balance, Commanders, Expeditions, Items, Match, Power — cross-checked against
`internalUsages`' 13 candidates, the other 6 being the residual's own Actions/Battle/Combat/Creatures/
Delve/World).

The analyzer's own `projects` array left `references`/`links`/`content` empty for all 68 — by design,
since grouping/dependency judgment is a human call (`spec-core-split-apply.md`'s own words: "the tool
never decides groupings"). Filled by hand:

- **`references`** — default `gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj` for all 68. `requiredAssemblies`
  (414 entries) showed exactly one candidate needing a DIRECT `FusionRpg.Data` reference beyond Core:
  **Match** (`ModsAbsorptionTests.cs` uses `DataTestStore`/`RpgStore` types). Five more (**Balance**,
  **ClassSystem**) need tool `ProjectReference`s the analyzer's Roslyn-based scan structurally cannot
  see: the residual csproj's own comment says "Nine test classes shell out to these tools with a
  no-build Release invocation" via `ToolProcess.Run(repoRoot, "<ToolName>", ...)` — a subprocess launch
  by string name, not a `using`/type reference. Grepped every `ToolProcess.Run(` call site and its
  containing folder directly: **Balance** needs `CombatSim`, `DominanceBaseline`, `ProvePredictor`,
  `RealDataAggregate`, `ResidualFitLoop`; **ClassSystem** needs `CombatSim`, `ProveAptitude`. The other
  three shelling-out folders (`Battle`, `Combat`, `Creatures`) are already part of the 10-item residual,
  so they need no manifest entry.
- **`links`** — grepped every real TYPE usage (not just a comment mention) of the three residual-linked
  Injector files. Only **Hud** uses them (`ActorHudCache` in `ActorHudCacheTests.cs`,
  `InjectorDerivedOverride` in two Derived/LevelBand tests, `ActorHudUniqueFlags` in its own test) — a
  fourth file, `Atoms/ParamParityGuardTests.cs`, only MENTIONS them in a comment, so `Atoms` gets no link.
- **`content`** — the analyzer's `contentRequirements` (22 entries, a generic string-literal scan that
  also independently re-found the Balance/ClassSystem/Creatures tool names above) named
  `fixtures/effects/scenarios` for **Atoms**, **EffectPluginLifecycleTests**, **EffectScenarioRunnerTests**
  — mapped to the residual's own exact convention (`../fixtures/effects/**/*` with Link metadata, the
  whole tree rather than the one subfolder, matching what the residual already does for itself). The
  scanner did not catch `Goldens/actor-hud` (read via `Path.Combine`, not a literal matching its pattern)
  — found by grep instead, used only by **Hud** (`ActorHudBuilderTests.cs`); moved physically into Hud's
  own `include` (`Goldens/actor-hud/**` alongside `Hud/**`) with a project-relative `content` entry
  mirroring the residual's own no-Link convention for it.

## A real defect found while authoring, fixed before the manifest could rely on it

`SplitPlanner.BuildProjectCsproj`'s `links` handling (TVB5.3) assumed every linked file lived inside the
residual folder — wrong for both real cases (Injector files under `src/`, `DataTestStore.cs` under a
sibling test project). Fixed in a separate commit (`274824c9`) before authoring this manifest: `links`
entries are now repo-relative paths anywhere in the tree, and outside-project `content` entries get Link
metadata mirroring the residual's own convention. Two new `SplitPlannerTests` cases prove both paths
generate correctly — this code path had zero coverage before (every prior test used empty
`links`/`content` lists), which is exactly how the bug went unnoticed until real content forced it.

## A second real defect, mechanical, found and fixed in the authored manifest itself

40 of the 68 candidates are root FILES (`gk-core/tests/FusionRpg.Core.Tests/<Name>.cs`), not folders. The
analyzer's own `projects` array proposed `include: ["<Name>/**"]` for every candidate uniformly — a
folder-glob that matches nothing for a root file. Confirmed programmatically (`os.path.isdir`/`isfile`
per candidate) and corrected each root-file candidate's `include` to `["<Name>.cs"]` in the authored
manifest. This is a mechanical glob-syntax fix, not a grouping decision — the analyzer's own file→
candidate assignment is untouched, only the pattern that expresses it.

## A third finding, also mechanical: A1's own `.Tests` check is a literal substring

Named `FusionRpg.Core.<Candidate>` for a candidate whose name already ends in the word "Tests" (e.g.
`StatSystemTests` → `FusionRpg.Core.StatSystemTests`) at first, to avoid a "...TestsTests" stutter. This
FAILS `SplitManifestValidator`'s literal `EndsWith(".Tests", Ordinal)` check (the dot is required) — the
40 root-file candidates already ending in "Tests" have no dot before it. Reverted to the unconditional
rule: every project name is `FusionRpg.Core.<Candidate>.Tests`, stutter included where it occurs. A
naming cosmetic is not worth inventing a smarter rule outside this task's authority ("the tool never
decides groupings" extends to naming judgment too).

## CLI gap closed: A1 validation was never wired into the `split` verb

TVB5.3 built `SplitManifestValidator` (TVB5.2) and `SplitPlanner` (TVB5.3) but `Program.cs`'s `split`
verb only ever called the planner directly — a hand-authored manifest with a real A1 violation would
have silently reached `SplitPlanner.Plan` and failed there with a less specific message (or, for a
violation `SplitPlanner` does not itself check, like a double-claimed file across two DIFFERENT
`--project` invocations, not been caught until the second one). Wired `SplitManifestValidator.Validate`
into `RunSplit`, called once against the WHOLE manifest before planning any single project, using real
delegates (`referenceExists`/`fileExists` off disk, `residualReferences` parsed fresh from the residual
csproj's own `<ProjectReference>` lines). A deliberately-broken manifest (bad name, dead include pattern)
confirmed the refusal fires with both violations named; every real path below confirmed it does NOT
fire for the authored manifest.

## Verification

| Criterion | Command | Result |
|---|---|---|
| Analyzer re-run | `dotnet run --project gk-core/tools/TestSplitAnalyzer -c Release -- --project gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj --format json` | 68 clean, `blocksSplit: []`, matches TVB5.1.k's reading |
| Build | `dotnet build gk-core/tools/FileMove/FileMove.csproj -v q` | exit 0 |
| Focused run | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests -c Release` | 38/38 (2 new Links/Content regression tests + 36 prior) |
| A1 validation fires on a broken manifest | `dotnet exec ... split <manifest-with-bad-project> --project Bogus` | `REFUSED: manifest fails 2 A1 rule(s)` naming both |
| **Every one of the 68 real manifest projects dry-runs clean** | `dotnet exec tools/FileMove/bin/Release/net8.0/FileMove.dll split gk-core/tests/core-test-projects.v1.json --project <name>` for all 68 names | 68/68 exit 0, zero refusals |
| Whole affected project via the boundary tool | `.\scripts\verify-change.ps1 -Paths gk-core/tests/core-test-projects.v1.json,gk-core/tools/FileMove/Program.cs,gk-core/scripts/verification-boundaries.v1.json -Session tvb-wave5-20260920` | not obtained — see note below |

`gk-core/scripts/verification-boundaries.v1.json` gained one additive line: `gk-core/tests/core-test-projects.v1.json`
added to the existing `filemove-fallback` boundary's `paths` (the manifest is validated by the same tool
that owns it; no new boundary id, no removed path).

**`VerificationBoundaryWorkflowTests` cross-check not run.** This class spawns `scripts/verify-change.ps1`
as a child process per test and, under today's machine contention (25+ concurrent `dotnet` processes
observed from other lanes at the time), fails on a harness timeout in `ExternalProcess.Run` rather than
an assertion — a coordinator measurement an hour prior found 6/75 failing that way, and confirmed the
underlying planner call itself still produces a correct plan by hand (415s for two paths under the same
load). That class would read as red regardless of what this task did, so it is not evidence about this
change either way; the planner's own latency is a real but separate defect the coordinator assigned to
the other TVB agent, not this lane. The two facts that actually bound TVB5.5's own change are the 68/68
real dry-run and the 38/38 direct `FusionRpg.FileMove.Tests` run above, both obtained directly against
the real tool and the real repo tree, not through `verify-change.ps1`'s own orchestration.

## Ordering risk carried forward (not this task's job to resolve)

`Workspace` is one of the 68 (needs no special references/links/content — a clean, ordinary candidate)
but collides with `tasks/sessions/keepverse-split.json`'s live claim on
`tests/FusionRpg.Core.Tests/Workspace/**` for an unrelated change (recorded in `tvb5-1.md`). TVB5.7's
first real increment must not pick `Workspace` while that session is active — already noted in this
session's own record (`tasks/sessions/tvb-wave5-20260920.json`).

Files: `gk-core/tests/core-test-projects.v1.json` (new, 68 projects), `gk-core/tools/FileMove/Program.cs` (A1 validation
wired into `split`), `gk-core/scripts/verification-boundaries.v1.json` (additive path).

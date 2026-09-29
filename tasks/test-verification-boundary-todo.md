# Todo: `test-verification-boundary` (prefix `TVB`)
Plan: [test-verification-boundary-plan.md](test-verification-boundary-plan.md) · Map:
[test-verification-boundary-map.md](../docs/architecture/test-verification-boundary-map.md) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane D).
Order below is **suggested, not enforced**, except edges marked **H#** (parent hard edges).
Cross-program ids are written `<prefix><id>` (e.g. `SE0.7`). Every verify runs once per task
(`-Session <id>` is the building session's id). No test asserts a population count; every count a
task prints is a reading.

**State, 2026-09-23 (lane `tvb60`).** The increment stream is **drained**: all **67** manifest projects
are applied, and that is now asserted rather than measured by hand —
`gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestReconciliationTests.cs` carries
`Every_manifest_project_is_applied_and_the_shared_set_has_left_the_residual`, which iterates the manifest's
own `projects` and `shared` (no count pinned), and `FileMove split --project <name>` refuses both the first
and the last entry with `already exists` **and** `include pattern … matches no file`. **Corrected 2026-09-23,
the same day:** the sentence that stood here — *nothing below is startable without an outside decision* —
was falsified within the hour. `TVB-F28` had been filed as *needs a ruling on which of three shapes to
take*, and all three shapes had missed that `verify-change.ps1:112` filters the ambiguity check to
`kind -eq 'owner'`, so a **seam** on the owner's own paths was additive all along and no ruling was owed.
A row marked *needs a ruling* is a claim about the mechanism **as it was searched**, not a fact about the
mechanism: read the planner and the guard before accepting one. Every other row below is still blocked,
each with its exact blocker under
**"Blocked — the open rows"** at the foot of this file, and the ledger's `resume` prints the same set
(`queue` names the remaining rows, `blocked` names why each one waits, `active: none`). The one divergence
the split itself still carries is **`TVB-F30`**.

## Wave 0 — live defect and the CI lines that need nothing else
- [x] **TVB0.1 — `release.yml` exit checks + `WorkflowExitCheckTests` + a workflow owner** · S · deps: — · *(spec: core-split-wiring W0; map §7.1 E1, G14)*
  - Acceptance: each of `release.yml:43-46` is followed by `if ($LASTEXITCODE -ne 0) { throw "<project> failed" }`, and `--blame-hang-timeout 5min` becomes `10min`; `WorkflowExitCheckTests` (both workflows: every line starting `dotnet test `, `python -m pytest ` or `.\scripts\test-sharded.ps1 ` is followed by the exit-check line) is green on the real files and red on a planted text missing one
  - Acceptance: new owner boundary `ci-workflows` (`.github/workflows/**` → `guard`, focused on `VerificationId` `guard.workflows`), the trait on `WorkflowExitCheckTests` and `CiWiringGuardTests`, so `verify-change` resolves workflow edits (they are unmapped today — the spec's W0 verify command refuses without this)
  - Verify: `.\scripts\verify-change.ps1 -Paths .github/workflows/release.yml,gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs,gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <id>`
  - Files: `.github/workflows/release.yml`, `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` (new), `gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs` (trait only), `gk-core/scripts/verification-boundaries.v1.json`
- [x] **TVB0.2 — Drop the two pinned readings in `test_resource_ownership.py`** · XS · deps: — · *(spec: python-test-lane step 0)*
  - Acceptance: `:38` (`version == 5`) and `:40` (`len == 166`) deleted; the `edge_triples` equality (`:39`) kept; no tuning file changes
  - Acceptance: `gk-core/tools/tuning` suite fully green (it was 18 passed / 1 failed before — a reading)
  - Verify: `cd gk-core/tools/tuning; python -m pytest . -q -p no:cacheprovider` (the path is unmapped until TVB3.3, so `verify-change` cannot select it yet — map G5)
  - Files: `gk-core/tools/tuning/test_resource_ownership.py`
- [x] **TVB0.3 — `gk-core/tools/tuning` pytest step in `ci.yml` (E2)** · XS · deps: TVB0.2 (**H4**), TVB0.1 · *(spec: python-test-lane §CI; R15)*
  - Acceptance: the step text from `spec-python-test-lane.md` §CI inserted verbatim between "Install seedsmith from the lockfile" and "Item seed reachability (seedsmith)"; not in `release.yml`
  - Acceptance: `WorkflowExitCheckTests` green (the new `python -m pytest` line has its exit check); the step is green on its first CI run
  - Verify: `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml -Session <id>`
  - Files: `.github/workflows/ci.yml`
- [x] **TVB0.4 — R24: wire the two `tools/*.Tests` projects; `CiWiringGuardTests` W7** · S · deps: TVB0.1 · *(spec: core-split-wiring W7; map §7.1 E7; R24)*
  - Acceptance: the two pairs from `spec-core-split-wiring.md` W7 (LawnCombatObserver.Tests, ProveLiveProbe.Tests, each with its exit check) in "Restore / test (.NET)" after the FileMove pair; `ci.yml` only
  - Acceptance: W7 case: every `tools/**/*.Tests.csproj` appears on a line whose trimmed text starts with `dotnet test <path>` (a comment does not count), followed by its exit check, or is in an exemption table — which lands **empty**; red on a planted YAML where the path appears only in a comment
  - Verify: `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml,gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs -Session <id>`
  - Files: `.github/workflows/ci.yml`, `gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs`
### Checkpoint 0 — live defect closed (parent CC1)
- [x] `release.yml` exit-checked; `WorkflowExitCheckTests` green on both workflows and red on a planted violation
- [x] `gk-core/tools/tuning` suite green locally and its CI step green on first run
- [x] `ci.yml` runs `gk-fusion/tools/LawnCombatObserver.Tests` and `gk-fusion/tools/ProveLiveProbe.Tests`; W7 exemption table empty
- [x] `verify-change` resolves `.github/workflows/*.yml` (no `BOUNDARY MISSING`)
## Wave 1a — Data.Tests sharding (independent)
- [x] **TVB1.1 — Shard manifest + `TestShardManifestTests` H-T1–H-T4** · M · deps: — · *(spec: data-tests-sharding H1)*
  - Acceptance: `gk-core/scripts/test-shards.v1.json` (`schemaVersion` 1, `data` project, 2 shards: one named, one `remainder`, `maxParallelThreads` 2) per the spec's shape
  - Acceptance: H-T1 (one remainder), H-T2 (root prefix, trailing `.`, no key a **substring** of another), H-T3 (every prefix joins to a declared namespace/class), H-T4 (unique ids; project ids exist in the registry) green; owner boundary for `gk-core/scripts/test-shards.v1.json` + `scripts/test-sharded.ps1` → `guard`, `VerificationId` `guard.test-shards`
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/test-shards.v1.json,gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <id>`
  - Files: `gk-core/scripts/test-shards.v1.json` (new), `gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs` (new), `gk-core/scripts/verification-boundaries.v1.json`
- [x] **TVB1.2 — `scripts/test-sharded.ps1` runner + H-T6 + completeness proof** · M · deps: TVB1.1 · *(spec: data-tests-sharding H2)*
  - Acceptance: build once, one `--no-build` process per shard with its own results dir and TRX, remainder filter = conjunction of `FullyQualifiedName!~<p>`; reports every shard's exit and wall; `exit <code>`; overlap check on every run; empty named shard fails, empty remainder passes; temp root removed in `finally` with a throwing delete
  - Acceptance: H-T6 over **planted TRX files** (no `dotnet test`) green
  - Acceptance: one-time proof on the real project recorded in the commit body — union of shard test ids **equals** an unsharded run's id set and pairwise intersection is empty (sets, not counts)
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/test-sharded.ps1,gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs -Session <id>`; then `.\scripts\test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj`
  - Files: `scripts/test-sharded.ps1` (new), `gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs`
- [x] **TVB1.3 — Measure 2 vs 4 shards; record `_meta.measured`** · XS · deps: TVB1.2 · *(spec: data-tests-sharding H1 "Initial shape")*
  - Acceptance: walls for 2 and 4 shards written to `_meta.measured` (readings, with the machine-load note); the manifest keeps the faster count
  - Acceptance: no test asserts shard count, walls or tests per shard
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/test-shards.v1.json -Session <id>`
  - Files: `gk-core/scripts/test-shards.v1.json`
- [x] **TVB1.4 — CI adoption: `ci.yml:155-156` → sharded runner (E4) + H-T5** · S · deps: TVB1.2, TVB0.1 · *(spec: data-tests-sharding H3; R15)*
  - Acceptance: `ci.yml:155-156` replaced by exactly the two lines in the spec (`.\scripts\test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj` + its exit check); leak-alarm re-run (`:196`) untouched; `release.yml:44` untouched; no `--filter` in `ci.yml`
  - Acceptance: H-T5 (CI line invokes the runner with the csproj path, next line is the exit check; carries `guard.workflows`) green; first CI run green for that step
  - Verify: `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml,gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs -Session <id>`
  - Files: `.github/workflows/ci.yml`, `gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs`
- [x] **TVB1.5 — Local adoption: module-level runs on a sharded project delegate to the runner** · S · deps: TVB1.2 · *(spec: data-tests-sharding H3 "Local")*
  - Acceptance: a module-level check on a project with a shard entry calls `test-sharded.ps1 -ExtraFilter <default profile>` (filter read from `scripts/test-fast.ps1`, not restated); focused runs unchanged
  - Acceptance: a plan case in `VerificationBoundaryWorkflowTests` shows a `data-fallback` path planning the sharded runner; `testing-standard.md` §6 "Wall-clock is its own axis" gains the paragraph
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/verify-change.ps1,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs,docs/contributing/testing-standard.md -Session <id>`
  - Files: `scripts/verify-change.ps1`, `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`, `docs/contributing/testing-standard.md`
  - Note: shares `verify-change.ps1` with SE0.7 and wave 2 — serialise commits
## Wave 1b — Core split analyzer (independent, read-only)
- [x] **TVB1.6 — `gk-core/tools/TestSplitAnalyzer` skeleton: csproj reader + test project + wiring (E3)** · M · deps: — · *(spec: core-split-analyzer)*
  - Acceptance: `TestSplitAnalyzer` `Exe` with `CsprojReader` (text: `Compile Include … Link=`, `ProjectReference`s, `None` items); A8 green in memory; exit 2 with a message when the build output is absent
  - Acceptance: registry `projects` id + one owner boundary over tool + tests (`filemove`'s shape); `ci.yml` E3 pair (exact text in the spec's Project structure row) after the FileMove pair, same commit; not in `release.yml`
  - Acceptance: Roslyn (`Microsoft.CodeAnalysis.CSharp`) referenced by the analyzer tool project only — approved (R26)
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/TestSplitAnalyzer.csproj,gk-core/tools/TestSplitAnalyzer/CsprojReader.cs,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/FusionRpg.TestSplitAnalyzer.Tests.csproj,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/CsprojReaderTests.cs,gk-core/scripts/verification-boundaries.v1.json,.github/workflows/ci.yml -Session <id>`
  - Files: `gk-core/tools/TestSplitAnalyzer/{TestSplitAnalyzer.csproj,CsprojReader.cs}`, `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/{csproj,CsprojReaderTests.cs}`, `gk-core/scripts/verification-boundaries.v1.json`, `.github/workflows/ci.yml` (six files: the last two are one-line wiring that cannot ship apart — `CiWiringGuardTests` fails a new test project with no CI line)
- [x] **TVB1.7 — Reference graph: cross-candidate edges, shared set, assemblies, internals, collections** · M · deps: TVB1.6 · *(spec: core-split-analyzer Design)*
  - Acceptance: `Microsoft.CodeAnalysis.CSharp` compilation over the built output (no `MSBuildWorkspace`); each top-level folder and each root file a candidate; `TestSupport/`, bootstrap, `AssemblyInfo.cs` and linked files classified shared
  - Acceptance: A1 (edge with symbol + both locations), A4 (cross-candidate collection), A6 (internal Core symbol) green, compiled in memory
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/ReferenceGraph.cs,gk-core/tools/TestSplitAnalyzer/TestSplitAnalyzer.csproj,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ReferenceGraphTests.cs -Session <id>`
  - Files: `gk-core/tools/TestSplitAnalyzer/ReferenceGraph.cs` (new), `TestSplitAnalyzer.csproj`, `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ReferenceGraphTests.cs` (new)
- [x] **TVB1.8 — String-keyed and location-sensitive findings (`BLOCKS SPLIT`)** · M · deps: TVB1.7 · *(spec: core-split-analyzer, G17)*
  - Acceptance: literal hits for `fixtures/`, `Goldens/`, `FusionRpg.Core.Tests/` and tool assembly names; an own-path literal crossing candidates flagged `BLOCKS SPLIT`; `[CallerFilePath]` users; namespace-vs-folder mismatches; `VerificationId`/`Category` trait locations
  - Acceptance: A5, A9, A10, A11 green
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/ReferenceGraph.cs,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/FindingsTests.cs -Session <id>`
  - Files: `gk-core/tools/TestSplitAnalyzer/ReferenceGraph.cs` (or a new `Findings.cs`), `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/FindingsTests.cs` (new)
- [x] **TVB1.9 — Grouping (SCCs) + deterministic json/md report with manifest draft** · M · deps: TVB1.8 · *(spec: core-split-analyzer Grouping, Determinism)*
  - Acceptance: SCCs of the candidate graph; clean = no edges into another SCC; one proposed project per clean SCC named from its largest folder, residual `FusionRpg.Core.Tests`; draft printed in the `core-split-apply` A1 schema (never written as the manifest file)
  - Acceptance: A2, A3, A7 (shuffled input → byte-identical JSON) green; `--format json|md`, `--out`
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/Grouping.cs,gk-core/tools/TestSplitAnalyzer/Report.cs,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/GroupingTests.cs -Session <id>`
  - Files: `gk-core/tools/TestSplitAnalyzer/{Grouping.cs,Report.cs,Program.cs}`, `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/GroupingTests.cs`
- [x] **TVB1.10 — Real run over `FusionRpg.Core.Tests`; report for Checkpoint M** · S · deps: TVB1.9 · *(spec: core-split-analyzer Success criteria)*
  - Acceptance: md report lists the shared set, per-candidate references, internals users, collections, string-keyed inputs, trait locations, and every `BLOCKS SPLIT`; three reported edges spot-checked by opening the files (named in the commit/hand-off)
  - Acceptance: two runs on the same build → identical JSON; the report's numbers are readings
  - Verify: `dotnet build tests\FusionRpg.Core.Tests -c Release`; `dotnet run --project tools\TestSplitAnalyzer -c Release -- --project tests\FusionRpg.Core.Tests\FusionRpg.Core.Tests.csproj --configuration Release --format json --out <scratch>\a.json` twice, compare
  - Files: none committed except, if the owner wants it kept, the md report under the scratch/hand-off (the tool never writes the manifest)
### Checkpoint 1 — independent tracks
- [x] Sharded runner green; completeness proof (set equality, empty intersection) in the TVB1.2 commit body; CI line lands in TVB1.4 (first CI run is CI-owned evidence, not locally observable)
- [x] Analyzer A1–A11 green locally (32/32); real report produced over the actual `FusionRpg.Core.Tests`, two runs byte-identical, three edges spot-checked by opening the files (`tasks/evidence-fragments/tvb1-10.md`)
- [x] `BLOCKS SPLIT` list extracted — real run found **zero** instances at the top-level-folder candidate granularity; the map/TVB5.1.k's named instance (`GateCounterBoundaryGuardTests.cs:97`) does not cross a candidate boundary today (both files are under `PassiveTree/`) — recorded, not force-matched
### Checkpoint M — manifest review (map §7.3; not a gate)
- [ ] Owner shown the TVB1.10 md report and the manifest draft
- [x] **Default applies (unanswered):** the analyzer's clean-SCC proposal is the manifest — TVB1.10's real run is that proposal (65 clean projects, 10-candidate residual); the residual keeps the rest
## Wave 2 — `registry-contract` (schema 3) · after SE0.7 (**H5**)
- [x] **TVB2.1 — Shared lib `scripts/lib/VerificationBoundaries.ps1` + last-segment wildcard + (class, length) specificity** · M · deps: SE0.7 (**H5**) · *(spec: registry-contract C4)*
  - Acceptance: `Test-PatternMatch`, `Get-PatternSpecificity` (exact > wildcard > `/**`, then length), `Resolve-Owner`, and the accepted `schemaVersion` constant live in the lib; planner and guard dot-source it (the duplicated `Matches` copies deleted); starts from `schemaVersion` 2 as SE0.7 left it
  - Acceptance: T4, T5, T6 green on planted registries (`-Root`, throwing delete in `finally`)
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,scripts/verify-change.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session <id>`
  - Files: `scripts/lib/VerificationBoundaries.ps1` (new), `scripts/verify-change.ps1`, `gk-core/scripts/guard-verification-boundaries.py`, `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`
- [x] **TVB2.2 — Derived `level` (C3) + stale exact path (C8) + the three G3 label fixes** · M · deps: TVB2.1 · *(spec: registry-contract C3, C8)*
  - Acceptance: guard derives `level` from `kind` + selector + project/guards and fails a mismatch; `battle-effect-math` → `focused`, `session-and-program-records` → `module`, `effect-catalog-drift` → `seam` (labels only, no selection change)
  - Acceptance: an exact pattern naming no file fails with `stale exact path: <boundary>: <pattern>`; T3, T13 green; real registry passes (T9)
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/guard-verification-boundaries.py,scripts/lib/VerificationBoundaries.ps1,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session <id>`
  - Files: same four
- [x] **TVB2.3 — Project groups (C7)** · M · deps: TVB2.1 · *(spec: registry-contract C7)*
  - Acceptance: a `projects` value may be an array of `.csproj`; module selection runs every member sequentially with the default-profile filter; focused selection runs only members whose directory holds the trait (text scan)
  - Acceptance: guard: members exist, flat, `.csproj` only, group `verificationId` matches ≥1 member; T10, T11, T12 green
- [x] **TVB2.4 — Guard-only boundaries (C5, script half)** · S · deps: TVB2.1 · *(spec: registry-contract C5)*
  - Acceptance: `project` optional iff `guards` non-empty; the planner emits no test check for such a path; a boundary with neither fails the guard
  - Acceptance: T7, T8 green on planted registries
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/verify-change.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session <id>`
  - Files: `scripts/verify-change.ps1`, `gk-core/scripts/guard-verification-boundaries.py`, `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`
- [x] **TVB2.5 — `guard-bench-compile.ps1` + catalog row + `bench` and `magic-number-audit` guard-only + `schemaVersion` 3** · M · deps: TVB2.2, TVB2.3, TVB2.4, SE0.2 · *(spec: registry-contract C5, Contract version; G9, G15)*
  - Acceptance: guard builds `gk-core/tests/FusionRpg.Bench` Release into a temp `OutputPath`, fails on a compile error, removes the temp dir in `finally` (a failed removal fails); catalog row `bench-compile` (`tier: ci`, `status: gating`, `localReason: null`); boundary `bench` guard-only; `magic-number-audit` loses its `project` and keeps `magic-numbers`
  - Acceptance: first v3-only construct in the real registry, so `schemaVersion` → 3 here (lib constant + registry + planted registry); both scripts refuse 2 (T14); T15 green
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/guard-bench-compile.ps1,gk-core/scripts/enforcement-registry.v1.json,gk-core/scripts/verification-boundaries.v1.json,scripts/lib/VerificationBoundaries.ps1,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs -Session <id>`; `.\scripts\guard-bench-compile.ps1`
  - Files: `scripts/guard-bench-compile.ps1` (new), `gk-core/scripts/enforcement-registry.v1.json`, `gk-core/scripts/verification-boundaries.v1.json`, `scripts/lib/VerificationBoundaries.ps1`, `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`
- [x] **TVB2.6 — `tests/**` enforced root (C1) + test-project completeness (C2), backlog closed in the same change** · M · deps: TVB2.5 · *(spec: registry-contract C1, C2; G1, G2)*
  - Acceptance: guard walks `tests/**/*.cs` and `tools/*.Tests/**/*.cs` (minus `bin/obj/TestResults`), failing `unmapped test source: <path>`; every `*.Tests.csproj` under `tests/`/`tools/` is registered or exempt with a reason (initial exemption: Injector.Tests)
  - Acceptance: ids `e2e`, `atomimporter`, `itemseedvalidator`, `filemove`, `passivetreerostergen` + their fallbacks (incl. the four tool trees) carrying `test-substrate`; T1, T2, T9 green; `software-architecture.md` §10 and `testing-standard.md` §6 lines updated
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/guard-verification-boundaries.py,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs,docs/architecture/software-architecture.md,docs/contributing/testing-standard.md --session <id>`
  - Files: same five
- [x] **TVB2.7 — Orphan-trait reading in `-Report` (C6)** · XS · deps: TVB2.1 · *(spec: registry-contract C6; G12 reading)*
  - Acceptance: `-Report` prints every `VerificationId` no boundary selects, grouped by project; never a failure; nothing asserts its size
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/guard-verification-boundaries.py --session <id>`; `python gk-core/scripts/guard-verification-boundaries.py --report`
  - Files: `gk-core/scripts/guard-verification-boundaries.py`
### Checkpoint 2 — registry contract (schema 3)
- [x] `verify-change -PlanOnly` resolves every file under the six C1 roots and four tool trees; `gk-core/tests/FusionRpg.Bench/**` plans `bench-compile` and no `dotnet test`
- [x] T1–T15 green; `schemaVersion` 3 accepted only; real registry passes C3 and C8
- [x] `-Report` orphan reading printed (the seven `core.*` + `server.lawn-quick-start` expected — a reading)
## Wave 3 — `python-test-lane` (schema 4)
- [x] **TVB3.1 — Object projects, closed `runner` vocabulary, D2 pairing rules + `schemaVersion` 4** · M · deps: TVB2.5 · *(spec: python-test-lane D1, D2 guard half)*
  - Acceptance: `projects` values are string / array / object with `runner` ∈ {`dotnet`,`pytest`,`script`} (membership pinned at 3, reason in the test); `testFiles` only on pytest, `verificationId` never on pytest/script, `selfSelect` only under the project's test dir, every `testFiles` pattern matches ≥1 `test_*.py`
  - Acceptance: `schemaVersion` → 4 (lib constant, registry, planted registry); P3, P4, P5 green
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session <id>`
- [x] **TVB3.2 — Runner branches: pytest (focused / self-select / module) and script** · M · deps: TVB3.1 · *(spec: python-test-lane D2, D3)*
  - Acceptance: commands exactly per D3 (`Push-Location <root>`, sorted relative files, `-q -p no:cacheprovider --junitxml <temp>`; script = `& <script>` from repo root); exit 5 is a failure; `python -m pytest --version` preflight stops with the install message, never installs or skips; temp dir removed with a throwing delete
  - Acceptance: P1, P2, P2b green (plan shape via `-PlanOnly -Format json`, no pytest execution in Guard tests)
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,scripts/verify-change.ps1,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs -Session <id>`
  - Files: `scripts/lib/VerificationBoundaries.ps1`, `scripts/verify-change.ps1`, `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`
- [x] **TVB3.3 — D4 boundaries: seedsmith + `gk-core/tools/tuning`; `CiPytestWiringTests`** · M · deps: TVB3.2, TVB0.3 · *(spec: python-test-lane D4, §CI; G5, G15 `tuning-publish-tool`)*
  - Acceptance: projects `seedsmith`, `tuning-py`; boundaries `seedsmith-fallback`, `seedsmith-tests` (`selfSelect`), one `seedsmith-<area>` per adapter area with an importing test (lists derived by import scan, reviewed, committed as data; `demons` stays on the fallback), `tuning-publish-tool` re-pointed to `tuning-py` keeping `magic-numbers`, `tuning-resource-ownership`
  - Acceptance: `CiPytestWiringTests` (every pytest project has a `python -m pytest` line under a step whose `working-directory` = its root; carries `guard.workflows`) green — E2 landed in TVB0.3; P6 green; no path maps to Guard.Tests any more
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/CiPytestWiringTests.cs,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs -Session <id>`; then `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/tests/test_items_adapter.py,gk-core/tools/tuning/publish.py -Session <id>`
  - Files: `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/tests/FusionRpg.Guard.Tests/CiPytestWiringTests.cs` (new), `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`
- [x] **TVB3.4 — Debt ledger `red` kind + the seedsmith actions `red` row** · S · deps: SE0.8 · *(spec: python-test-lane D6.2)*
  - Acceptance: `stub-register.md` documents kind `red` ("a committed test that fails on a clean HEAD; the test is right and the tree is wrong"); one row owned by the seedsmith actions pipeline, `waits-on` the description backfill
  - Acceptance: `StubRegisterTests` kind pin 4 → 5 with its reason (after SE0.8's 3 → 4)
  - Verify: `.\scripts\verify-change.ps1 -Paths docs/architecture/stub-register.md,gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs -Session <id>`
  - Files: `docs/architecture/stub-register.md`, `gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs`
- [x] **TVB3.5 — `knownRed` outcome + guard rules + the five entries** · M · deps: TVB3.3, TVB3.4 · *(spec: python-test-lane D6)*
  - Acceptance: runner reads junit/TRX; only-knownRed failures pass printing `KNOWN RED (pre-existing) <test> -> <SR-id>`; any other failure fails; a knownRed test that passed fails with `stale knownRed entry`; guard: fields exactly {`project`,`test`,`debt`}, project exists, file exists, `debt` resolves to a `red` row
  - Acceptance: P9–P12 green over planted result files; five entries for `test_actions_description_completeness.py` point at the TVB3.4 row
  - Acceptance: local proof: `verify-change` on that file passes with five `KNOWN RED` lines; on `test_items_adapter.py` green
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,scripts/verify-change.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session <id>`
- [x] **TVB3.6 — `GeneratorCheckCiParityTests` + first wrappers (`gen-resource-ownership`, `gen-creature-species`)** · M · deps: TVB3.2 · *(spec: python-test-lane D5)*
  - Acceptance: argument-free wrappers running exactly the CI command from the CI working directory, failing loudly on a missing toolchain; `script` projects; seam boundaries per the D5 table; new owner `creaturespeciesgen-tool` → `core` (module)
  - Acceptance: parity test: every `scripts/checks/gen-*.ps1` command line is in `ci.yml` under a step with the same `working-directory` (carries `guard.workflows`); both wrappers exit 0 on a clean tree
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/checks/gen-resource-ownership.ps1,scripts/checks/gen-creature-species.ps1,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/GeneratorCheckCiParityTests.cs -Session <id>`
  - Files: `scripts/checks/gen-resource-ownership.ps1`, `scripts/checks/gen-creature-species.ps1` (new), `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/tests/FusionRpg.Guard.Tests/GeneratorCheckCiParityTests.cs` (new)
- [x] **TVB3.7 — C# generator wrappers: `gen-family-expand`, `gen-build-plan`, `gen-passive-tree`** · S · deps: TVB3.6 · *(spec: python-test-lane D5)*
  - Acceptance: three wrappers, projects and seams per the D5 table; owners `familyexpandgen-tool`, `treebinder-tool` unchanged; new owner `creaturebuildplangen-tool` → `gen-build-plan` (module)
  - Acceptance: parity test green; each wrapper exits 0 on a clean tree
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/checks/gen-family-expand.ps1,scripts/checks/gen-build-plan.ps1,scripts/checks/gen-passive-tree.ps1,gk-core/scripts/verification-boundaries.v1.json -Session <id>`
  - Files: the three wrappers (new), `gk-core/scripts/verification-boundaries.v1.json`
- [x] **TVB3.8 — Seedsmith wrappers A: `gen-fusion-recipe`, `gen-items-gate`, `gen-creature-contract`** · S · deps: TVB3.6, TVB3.3 · *(spec: python-test-lane D5)*
  - Acceptance: three wrappers, projects, seams per the D5 table
  - Acceptance: changing `gk-forge/tools/seedsmith/seedsmith/adapters/items/<file>.py` plans the items test files plus `gen-items-gate`, not the whole suite; wrappers exit 0 where CI's step is green
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/checks/gen-fusion-recipe.ps1,scripts/checks/gen-items-gate.ps1,scripts/checks/gen-creature-contract.ps1,gk-core/scripts/verification-boundaries.v1.json -Session <id>`
- [x] **TVB3.9 — Seedsmith wrappers B: `gen-structure-contract`, `gen-creature-report`, `gen-creature-metrics`, `gen-creature-preflight`** · M · deps: TVB3.8 · *(spec: python-test-lane D5)*
  - Acceptance: four wrappers, projects, seams per the D5 table (incl. `report/**` for `gen-creature-report`)
  - Acceptance: parity test green; wrappers exit 0 where CI's step is green
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/checks/gen-structure-contract.ps1,scripts/checks/gen-creature-report.ps1,scripts/checks/gen-creature-metrics.ps1,scripts/checks/gen-creature-preflight.ps1,gk-core/scripts/verification-boundaries.v1.json -Session <id>`
  - Files: the four wrappers (new), `gk-core/scripts/verification-boundaries.v1.json`
- [x] **TVB3.10 — `testing-standard.md` §6: Python selection + the D6 rule** · XS · deps: TVB3.5 · *(spec: python-test-lane Project structure)*
  - Acceptance: one paragraph: Python paths select through the same planner by file; the knownRed rule as stated in D6 (never deselect, printed, self-expiring)
  - Verify: `.\scripts\verify-change.ps1 -Paths docs/contributing/testing-standard.md -Session <id>`
  - Files: `docs/contributing/testing-standard.md`
### Checkpoint 3 — Python lane (schema 4)
- [x] `gk-forge/tools/seedsmith/**` and `gk-core/tools/tuning/*.py` resolve; none maps to Guard.Tests
- [x] One seedsmith test file plans itself; `conftest.py` plans the module; P1–P12 green
- [x] Twelve wrappers exit 0 on a clean tree where CI's step is green; parity and CI-pytest-wiring tests green (four wrappers surfaced real, pre-existing, out-of-scope corpus drift instead — documented per-task, not fixed here)
- [x] `schemaVersion` 4 accepted only
## Wave 4 — `seam-coverage` (schema 5)
- [x] **TVB4.1 — `full` level + `schemaVersion` 5** · M · deps: TVB3.1 · *(spec: seam-coverage S3)*
  - Acceptance: owner with neither project nor guards = `full`; planner prints `<path> -> <boundary> (full): no local check; CI full evidence owns this input` and selects nothing; `full` legal only under `data/**` and `gk-core/tests/fixtures/**`; `-Report` section "inputs with no local proof"
  - Acceptance: level vocabulary pinned at 4 with reason; `schemaVersion` → 5 (lib, registry, planted registry); S-T2, S-T3, S-T5 green
- [x] **TVB4.2 — Enforced-roots list (S4 mechanism)** · S · deps: TVB4.1 · *(spec: seam-coverage S4)*
  - Acceptance: code-owned list in the lib, empty at landing; a root on it fails the guard on an unmapped file, off it the planner still refuses but the guard passes
  - Acceptance: S-T4 green
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session <id>`
  - Files: same three
- [x] **TVB4.3 — Script projects `gen-content-validate`, `gen-corpus-dump-verify`, `gen-item-seed-validator`** · M · deps: TVB3.6 · *(spec: seam-coverage S1 table)*
  - Acceptance: wrappers per the table; `gen-content-validate` creates and removes its temp `--db` dir (removal failure fails); parity test compares that command up to `--db`
  - Acceptance: each exits 0 on a clean tree
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/checks/gen-content-validate.ps1,scripts/checks/gen-corpus-dump-verify.ps1,scripts/checks/gen-item-seed-validator.ps1,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/GeneratorCheckCiParityTests.cs -Session <id>`
  - Files: the three wrappers (new), `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/tests/FusionRpg.Guard.Tests/GeneratorCheckCiParityTests.cs`
- [x] **TVB4.4 — Map `gk-core/data/tuning/**` by S1 evidence; switch the root on** · M · deps: TVB4.2 · *(spec: seam-coverage S1, S2 row 1; G4 tuning half)*
  - Acceptance: one `gk-core/data/tuning/<domain>.v*.json` owner per domain, each citing its S1 evidence in the commit body; `lawn-attrition-tuning`, `deployment-hierarchy-tuning`, `power-scale-tuning` rewritten as wildcards keeping project, `verificationId` and every guard (incl. any SE2.1 attached); `aptitudes.v*.json` gains seam `gen-resource-ownership`; no-evidence domains `full`
  - Acceptance: `gk-core/data/tuning/**` on the enforced-roots list; S-T1, S-T7 green; no file under `data/**` edited
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,scripts/lib/VerificationBoundaries.ps1,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs -Session <id>`
- [x] **TVB4.5 — Map `gk-core/tests/fixtures/**`; switch on** · S · deps: TVB4.4 · *(spec: seam-coverage S2 row 2)*
  - Acceptance: one owner per fixture subtree (`effects/**`, `combat/**` → `core`; `action-traces`/`battle-traces` → `core` until TVB6 narrows), evidence cited; root switched on
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,scripts/lib/VerificationBoundaries.ps1 -Session <id>`
  - Files: `gk-core/scripts/verification-boundaries.v1.json`, `scripts/lib/VerificationBoundaries.ps1`
- [x] **TVB4.6 — Map `gk-data/packs/fusion/data/generated/**` with `generated-seed`; switch on** · S · deps: TVB4.5, TVB3.7, SE0.1 · *(spec: seam-coverage S2 row 3)*
  - Acceptance: `creatures/**` → `gen-creature-species`; `creatures/_species-build-plan.json` (exact) → `gen-build-plan`; `passive-tree/**` keeps `generated-trees` + seam `gen-passive-tree`; all carry `generated-seed` (via the catalog); root switched on
  - Acceptance: S-T8 green
- [x] **TVB4.7 — Map `gk-data/packs/fusion/data/seed/**`; switch on; doc paragraph** · M · deps: TVB4.6, TVB3.9, TVB4.3 · *(spec: seam-coverage S2 row 4)* — done 2026-09-21 (lane `tvb59`): 38 new boundaries (293 -> 331); every one of the 2176 files under `gk-data/packs/fusion/data/seed/**` resolves (2151 were unmapped); the six S2-named generated trees got their generator's check + `generated-seed`, `dungeon/**`/`actions/**`/`zomboss/**` -> `seedsmith` (their seedsmith tests read the real trees), the authored rest -> the check/test that reads it, and five inputs with no local proof are explicit `full`; `gk-data/packs/fusion/data/seed/**` is the fourth `$Script:EnforcedRoots` member; `testing-standard.md` §6 gained the data-inputs/`full`-is-CI-only paragraph. S-T6 needed a fix: the enforced-root walk pushed `Integrity_guard_passes_on_the_current_registry` past its fixed 120s ceiling, so `Resolve-Owner` now indexes boundaries by first path segment (memoized on the array instance; the guard script is a protected pipeline file): 145/151s -> 22.0/24.3s, with equivalence proven over 12722 tracked paths. `VerificationBoundaryWorkflowTests`+`EnforcementRegistryGuardTests` **74/74**.
  - Acceptance: per-subtree owners per S2 (`items/**`, `creatures/**`, `creatures/_dump/**`, `structures/**`, `atoms/**` + `atoms/generated/**`, `passive-tree/**`); remaining subtrees derived by S1 at build time; authored `_registry/`/`_exemplars/` separate where the reader differs; generated subtrees carry `generated-seed`
  - Acceptance: root switched on; S-T6 green with all four roots on; `testing-standard.md` §6 paragraph (data inputs select through the planner; `full` = CI-only). Split per subtree if it outgrows one session
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,scripts/lib/VerificationBoundaries.ps1,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs,docs/contributing/testing-standard.md -Session <id>`
### Checkpoint 4 — seam coverage (schema 5)
- [x] Publishing a new tuning version needs no registry edit (S-T1) — `S1_a_new_tuning_version_resolves_through_the_wildcard_with_no_registry_edit`, green in the 74/74 run
- [x] All four roots switched on; `-Report` "inputs with no local proof" printed; every S1 owner cites evidence — 24 `full` boundaries printed; every new owner cites its S1 evidence in `tasks/evidence-fragments/tvb4-7.md` and the commit body
- [x] S-T1–S-T8 green; `schemaVersion` 5 accepted only — `VerificationBoundaryWorkflowTests`+`EnforcementRegistryGuardTests` 74/74
## Wave 5 — Core split: `core-split-apply` ⇄ `core-split-wiring`
- [x] **TVB5.1.k — Fix `BLOCKS SPLIT` own-path literal k** · XS each · deps: TVB1.10 · *(spec: core-split-analyzer "Blocking findings", core-split-apply header)* — **satisfied vacuously 2026-09-20**: a fresh analyzer run against HEAD (`57710318`, post-mega-merge) still reports zero `BLOCKS SPLIT` findings, matching TVB1.10's original run. No fix needed; re-check if a later increment's manifest ever splits a folder finer than today's top-level granularity.
  - Acceptance: one commit per analyzer finding; the literal resolves relative to `[CallerFilePath]` (or equivalent) instead of `gk-core/tests/FusionRpg.Core.Tests/...`; known instance: `PassiveTree/GateCounters/GateCounterBoundaryGuardTests.cs:97`
  - Acceptance: the analyzer no longer reports it; the test still passes
  - Verify: `.\scripts\verify-change.ps1 -Paths <the fixed test file> -Session <id>`
  - Files: the one test file
- [x] **TVB5.2 — `FileMove` split manifest model + A1 validation** · M · deps: — · *(spec: core-split-apply A1)* — done 2026-09-20: `gk-core/tools/FileMove/SplitManifest.cs` + `SplitManifestTests.cs`, 11 in-memory cases (F2/F3/F4/F5/F11 + baseline), `FusionRpg.FileMove.Tests` 20/20.
  - Acceptance: `SplitManifest` rules: includes match ≥1 file, no double claim, shared unclaimed; references exist, under `src/`/`tools/`, never a test project, ⊆ the residual's today; name ends `.Tests`, has no `FusionRpg.Data`; dir is a direct child of `tests/` and does not exist
  - Acceptance: F2, F3, F4, F5, F11 green in memory (injected delegates)
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitManifest.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestTests.cs -Session <id>`
  - Files: `gk-core/tools/FileMove/SplitManifest.cs` (new), `gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestTests.cs` (new)
- [x] **TVB5.3 — `SplitPlanner` + dry-run `split` verb + dirty-path refusal** · M · deps: TVB5.2 · *(spec: core-split-apply A2, A3, A4 plan half)* — done 2026-09-20: `SplitPlanner.cs` + `split` verb on `Program.cs` (dry-run only; `--apply` is TVB5.4), 11 in-memory cases (F1/F7/F8 + supporting), real-tree smoke test clean, `FusionRpg.FileMove.Tests` 31/31.
  - Acceptance: `SplitPlan` of explicit ops (create/modify/move/createDirectory) + `PlannedEdit` view for printing; plan covers csproj, shared `.props`, residual csproj edit (first increment), byte moves, `InternalsVisibleTo.CoreTests.cs` lines, `FusionRpg.slnx`; never calls `FileMover.Plan`; graph cycle check kept as a defensive invariant
  - Acceptance: dirty-path refusal via an injected `git status` reader; F1, F7, F8 green; `split` dry-run default
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitPlanner.cs,gk-core/tools/FileMove/Program.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitPlannerTests.cs -Session <id>`
  - Files: `gk-core/tools/FileMove/SplitPlanner.cs` (new), `gk-core/tools/FileMove/Program.cs`, `gk-core/tests/FusionRpg.FileMove.Tests/SplitPlannerTests.cs` (new)
- [x] **TVB5.4 — `SplitExecutor`: journal, `Apply`, `Revert`, `split --revert <journal>`** · M · deps: TVB5.3 · *(spec: core-split-apply A4 1–5)* — done 2026-09-20: `SplitExecutor.cs` (journal/Apply/Revert/Keep) + `--apply` build/test gate and `split --revert` on `Program.cs`; F6/F9/F10 green on a real temp tree, `FusionRpg.FileMove.Tests` 36/36 twice in a row.
  - Acceptance: journal written before any change; reverse-order undo per op kind; `Revert` stops with exit 3 and the journal path if a path no longer holds what `Apply` wrote; an I/O failure mid-`Apply` reverts the applied ops; apply sequence builds and tests new project **and** residual with the default-profile filter, else reverts and exits 1
  - Acceptance: F6, F9, F10 green (real temp tree, throwing delete, no `catch`)
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitExecutor.cs,gk-core/tools/FileMove/Program.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs -Session <id>`
  - Files: `gk-core/tools/FileMove/SplitExecutor.cs` (new), `gk-core/tools/FileMove/Program.cs`, `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs` (new)
- [x] **TVB5.5 — Author `gk-core/tests/core-test-projects.v1.json`** · S · deps: TVB1.10, Checkpoint M, TVB5.2 · *(spec: core-split-apply A1; map §7.3)* — done 2026-09-20: 68 projects from the analyzer's clean-SCC default (no owner review this session), references/links/content derived by hand for Match/Balance/ClassSystem/Hud/Atoms/2 fixture candidates; 68/68 dry-run clean against the real repo tree; A1 validation wired into the CLI's `split` verb (a TVB5.3 gap).
  - Acceptance: manifest = owner's reviewed grouping, or the clean-SCC default if unanswered; `analyzerCommit` set; `sharedDir`, `shared`, `residual`; validates under TVB5.2 rules (dry run prints a full plan)
  - Acceptance: every `BLOCKS SPLIT` touching a manifest project already fixed (TVB5.1.k)
  - Verify: `dotnet run --project tools\FileMove -- split tests\core-test-projects.v1.json` (dry run, exit 0); `.\scripts\verify-change.ps1 -Paths gk-core/tests/core-test-projects.v1.json -Session <id>`
  - Files: `gk-core/tests/core-test-projects.v1.json` (new), `gk-core/scripts/verification-boundaries.v1.json` (owner for the manifest if TVB2.6's `tests/**` walk does not already cover it — it is JSON, so add one)
- [x] **TVB5.6 — `core` becomes a group; `CoreTestProjectPolicyTests` W1–W6; coverage/mutate default by namespace** · M · deps: TVB2.3, TVB5.5 · *(spec: core-split-wiring consumer table, New guard tests; registry-contract C7)* — done 2026-09-20: `core` is now a one-member group; `CoreTestProjectPolicyTests` W1-W6 (15/15 with CiWiringGuardTests/WorkflowExitCheckTests); `coverage.ps1`/`mutate.ps1` resolve `-Project` from the manifest, behavior-preserving for every existing mutant set.
  - Acceptance: `core` = group (today one member, the residual), so `core-fallback` keeps running every Core test through every increment; `verify-change` on a `gk-core/src/FusionRpg.Core/**` path plans the whole group
  - Acceptance: W1–W6 green on today's tree (membership/subset/set-equality only; W5/W6 carry `guard.workflows`); `coverage.ps1`/`mutate.ps1` `-Project` default resolves the project that holds the requested namespace via the manifest
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/CoreTestProjectPolicyTests.cs,scripts/coverage.ps1,scripts/mutate.ps1 -Session <id>`
  - Files: `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/tests/FusionRpg.Guard.Tests/CoreTestProjectPolicyTests.cs` (new), `scripts/coverage.ps1`, `scripts/mutate.ps1`
- [x] **TVB5.7 — First increment: shared set + manifest project 1, with its wiring** · M · deps: TVB5.4, TVB5.6 · *(spec: core-split-apply A2, A3, A5; core-split-wiring E5/E6)* — done 2026-09-20 (lane `tvb58`): shared set moved once to `gk-core/tests/FusionRpg.Core.Tests.Shared/` + `CoreTests.Shared.props`; `FusionRpg.Core.AchievementTitlesTuningTests.Tests` created (**15/15**) and the residual still green (**14822/0**); `InternalsVisibleTo.CoreTests.cs` generated (68 lines); `git diff -M --stat` shows 5 pure renames; ci.yml + release.yml pair (no BalanceGuard line — no trait), `test-fast` list, registry `core` group member + `core-achievementtitles` id + two fallbacks, no stale exact path; W1–W6 **6/6**, `CiWiringGuardTests`+`WorkflowExitCheckTests` **9/9**; 8 doc citations the move broke re-anchored. Two tool defects the increment exposed fixed in their own commits (`tvb5-7-tool-hygiene.md`, `tvb5-7-zero-test-gate.md`).
  - Acceptance: `FileMove split --project <1> --apply` keeps the increment: shared files moved once to `gk-core/tests/FusionRpg.Core.Tests.Shared/` + `CoreTests.Shared.props` (packages, linked shared sources incl. the `[ModuleInitializer]`, `DisableTestParallelization`); residual csproj imports the props and loses what moved into it; project 1 created; `InternalsVisibleTo.CoreTests.cs` generated; `git diff -M --stat` shows pure renames
  - Acceptance, same commit (hand-edited wiring): `ci.yml` and `release.yml` pair per the spec's exact shape (residual last), BalanceGuard pair if W6 says so; `test-fast.ps1:52-57` list; registry: project id + module fallback for project 1, `gk-core/tests/FusionRpg.Core.Tests.Shared/**` → `core` group, every moved exact path rewritten (C8); W1–W6, `CiWiringGuardTests`, `WorkflowExitCheckTests` green
  - Verify: `.\scripts\verify-change.ps1 -Paths <every moved, created and edited path> -Session <id>`
  - Files (hand-edited, ≤5): `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `scripts/test-fast.ps1`, `gk-core/scripts/verification-boundaries.v1.json`; tool-written: the moved files, the new csproj/props, `InternalsVisibleTo.CoreTests.cs`, `FusionRpg.slnx`
  - **Corrected 2026-09-23 (lane `tvb60`): TVB-F17 closed by option (b) — project 30 is no longer a manifest project, so the manifest holds **67** and every one is applied (the reading above was taken while it still held 68).**
- [x] **TVB5.8.k — Increment k (one per remaining manifest project, manifest order)** · M each · deps: TVB5.8.(k-1) or TVB5.7 · *(spec: core-split-apply A4, A5; core-split-wiring consumer table)* — drained 2026-09-23 (lane `tvb60`): the manifest holds **68** projects and **67 are applied** — `FileMove split --project <n>` refuses each of the 67 with `tests/<n> already exists` (its A1 directory rule), and every applied name appears in the 66 `tvb5-8-*` increment fragments. The one that is not is project 30 `FusionRpg.Core.GlobalUsings.Tests`, the `global using` alias file that **cannot** be its own project (TVB-F17) — skipped by TVB5.8.29 (`8f3513c7c`) and still open there. `tests/FusionRpg.Core.*` on disk = **68** (67 + residual); `W1`–`W6` **6/6**, `CiWiringGuardTests`+`WorkflowExitCheckTests` with them, **63/63** (evidence: `tvb5-8-k-close.md`). **Re-verified at `4369eda29` on the instruction to continue the increment stream — there is no increment left:** all **67** `projects` entries have their `tests/<name>` directory (`0` missing), the split tool refuses the **first** and the **last** manifest entry with its own A1 directory rule (`REFUSED: … gk-core/tests/FusionRpg.Core.AchievementTitlesTuningTests.Tests already exists`, and the same for `FusionRpg.Core.Workspace.Tests`), `tests/FusionRpg.Core.*` on disk = **69** = 67 + the residual + `FusionRpg.Core.Tests.Shared`, and the **wiring** is complete too: `scripts/test-fast.ps1`, `.github/workflows/ci.yml` and `.github/workflows/release.yml` each name **68** Core csprojs (**67 manifest projects + the residual**), **0 manifest projects missing** (evidence: `tvb5-8-k-close.md`). **And the split's own definition of done is met at every granularity** (`spec-core-split-apply.md:157-159`, A5): *"The split is **done** when every project in the approved manifest is applied; whatever the manifest leaves in the residual stays there. Emptying the residual is not a goal of this module"* — the **4-entry shared set** is fully applied (`gk-core/tests/FusionRpg.Core.Tests.Shared/` holds all four, none left in the residual, **68/68** Core csprojs import `CoreTests.Shared.props`), every applied project dir carries its csproj and at least one `.cs` (**67/67**), and the only include pattern that still matches a residual path is `FusionRpg.Core.Stats.Tests`' `Stats/**` — its 3 matched files were all added **after** that increment (lawn LW1.4 `2f9a4fc60`, lawn LW2.1 `423579089`, battle T17 `18139aec6`), i.e. post-split arrivals the residual keeps by A5, not a missed increment. **The drain is now a contract, not a reading (2026-09-23, lane `tvb60`).** Every closure claim above was a hand measurement, and "is there an increment left?" kept being asked because nothing asserted it: `CoreTestProjectPolicyTests` W1–W6 each **skip** a manifest project whose directory does not exist. `gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestReconciliationTests.cs` now carries `Every_manifest_project_is_applied_and_the_shared_set_has_left_the_residual` — it iterates the manifest's own `projects` and `shared` (no count pinned) and fails naming any entry not applied, any shared pattern matching nothing, and any shared entry left behind in the residual. Green `Failed: 0, Passed: 3, Total: 3`; red on a planted 68th entry (`Failed: 1, Passed: 2`, naming `tests/FusionRpg.Core.ZZPlantedNotApplied.Tests`). An edit to `gk-core/tests/core-test-projects.v1.json` plans `filemove-fallback` → `test: filemove`, so the suite is selected by exactly the change that would break it, and `ci.yml:316` runs it. Evidence: `tasks/evidence-fragments/tvb5-8-k-drain.md`. **And the same suite now carries the manifest's own declarations** (2026-09-23, lane `tvb60`): `Every_manifest_projects_declared_content_resolves_in_its_own_directory` resolves all **234** `include` patterns against their own project directory — A1's rule "each must match at least one file", carried to the post-apply state where A1 can no longer check it because the residual no longer holds those files — plus all **16** `links` repo-relative and all **5** `content` globs relative to the project dir (a `None` item read at run time, so no build witnesses it). Green `Failed: 0, Passed: 4, Total: 4`; red on three planted bad declarations, one message naming all three. Evidence: `tasks/evidence-fragments/tvb5-8-k-declarations.md`.
  - Acceptance: `FileMove split --project <k> --apply` keeps the increment (new project and residual build and pass; pure renames); `core` group gains the member
  - Acceptance, same commit: `ci.yml`/`release.yml` pairs (+ BalanceGuard pair per W6), `test-fast` list, registry id + fallback + rewritten exact paths; any consumer naming a moved file follows it (`regen-class-system-baselines.ps1:166,190`, `verify-golden-attribution.py:16,31` when `Battle/` moves; `audit-status-vfx-identity.ps1:41`; a `gk-core/scripts/mutants/*.json` set whose tests moved names its project)
  - Files (hand-edited, ≤5 + any consumer above): `ci.yml`, `release.yml`, `test-fast.ps1`, `verification-boundaries.v1.json`; split the consumer edit into the same commit only when this increment moved its file
  - Note: one entry is instantiated per manifest project at TVB5.5; their number is whatever the manifest holds (a reading)
- [ ] **TVB5.9 — Split close: full default profile once + `Csc` reading + doc sentence** · S · deps: last TVB5.8.k · *(spec: core-split-apply Success criteria; core-split-wiring Testing)* — **2 of 3 acceptance lines done at `633ffb4a8` (lane `tvb60`), 1 blocked on TVB-F25.** **Blocker re-read at `a6e84755a` (lane `tvb60`, 2026-09-23) on the orchestrator's request — unchanged, and still external:** `scripts/test-fast.ps1 -Project gk-core/tests/FusionRpg.E2E.Tests` printed **`Failed: 3, Passed: 271, Skipped: 0, Total: 274`** in `2m14s`: the two web goldens named below plus, on this run, **`RpgSimInProcHostTests.Two_consecutive_runs_on_fresh_hosts_report_the_readings_the_scenario_declares_stable`** (`expect.souls.ledger.expedition: $.items[*].reason does not contain "expedition"`; its own stdout shows `ok=True` then `ok=False` for the same input — the `RS-CF3` non-determinism, filed in `tasks/rpg-simulator-todo.md`). The main checkout is `features/mega-merge` @ `8958d88d6` and it still carries **both** stale goldens on disk (`"Crazy Dave"`, `b41ce3ef…`), so this dependency is not done anywhere in the repo — `ip-censor` and `world-stage` still owe the re-bless, and neither path is in this lane's fence or (per TVB-F1) reachable by `verify-change`. **The other blocker this row inherited is cleared:** `TVB5.8.k`'s ledger entry is `done` (its todo row is ticked at `:257`; the 2026-09-21 `blocked` was lane `tvb59`'s fence limit, not unfinished work). `Csc` re-measured 2026-09-23 with `dotnet build <p> -c Release -t:Rebuild -clp:PerformanceSummary`: `FusionRpg.Core.Lawn.Tests` **2,448 ms / 3 calls / 3.92 s wall**, the residual `FusionRpg.Core.Tests` **8,680 ms / 14 calls / 9.27 s wall** (~3.5× `Csc`, ~2.4× wall) — written into the ideal's "Net, honest verdict". `testing-standard.md` §6 already names the Core projects as the `core` group (`:139-145`). The Core group itself ran green in full: **68 projects, 15,836 tests, 0 failures** (`test-fast.ps1 -Project <every member>`). **The blocker, named exactly:** `test-fast.ps1 -AllDefault` cannot be green from this tip because `gk-core/tests/FusionRpg.E2E.Tests` fails on two stale **web** fixtures — `gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json:6` and `gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json:4` — both outside this program's fence and unmapped (TVB-F1), filed as **TVB-F25** for the manager to route to `ip-censor` / `world-stage`. The profile's Data (1,766/0) and Server (826/0) legs were green in the same run. This row closes when those two fixtures are re-blessed and the profile is green once. **Second blocker found 2026-09-23 (lane `tvb60`), measured on two consecutive full E2E runs at this head:** the profile is also load-fragile, so even after the fixtures are re-blessed one `-AllDefault` run is not reliably green. Run 1: `Failed: 3, Passed: 271` — the two fixtures plus `RpgSimInProcHostTests.Two_consecutive_runs_on_fresh_hosts_report_the_readings_the_scenario_declares_stable` (26 s). Run 2: `Failed: 2, Passed: 272` — the two fixtures only; the third passed there and also passes filtered alone. That class is already filed, with a 13-run measurement, as **`RS-CF3` in `tasks/rpg-simulator-todo.md`**, so no new row is filed here — it is recorded because it is the second reason this acceptance cannot be met from one run. **Third blocker found 2026-09-23 (lane `tvb60`), re-read at the merged head `f585d8d6e` after `git merge --no-ff features/mega-merge` (332 commits, HEAD was its ancestor):** `scripts/test-fast.ps1 -Project gk-core/tests/FusionRpg.E2E.Tests` printed **`Failed: 3, Passed: 273, Skipped: 0, Total: 276`** in **2 m 18 s** — the suite grew 274 → 276 — and the failures are now **three** stale checked-in fixtures, not two: the two below **plus `ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto`**, which is new. Cause read: the merge brought `0770c0f81` (save-identity **SE4.31**), which added `gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs:22` `[JsonPropertyName("empireId")]`; the live `POST /api/unique/actors` DTO now carries `"empireId": "dave"` and `gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json` (last written `e588c251a`, 2026-08-23) does not. `RpgSimInProcHostTests` passed on this run (`RS-CF3` is load-dependent), so the red set is now the three fixtures. Filed as **TVB-F28** below, which carries the owner routing.
  - Acceptance: `test-fast.ps1 -AllDefault` green once (AGENTS.md point 1: finishing a large feature) — **every leg green at `487400ce5` except E2E's two TVB-F25 fixtures: Data 1766/0 (11m46s), Server 826/0 (2m44s), Core group 68 projects / 15,836 tests / 0 failures; E2E Failed: 2, Passed: 272.**
  - Acceptance: one-subsystem Core test change builds one small project; `Csc` time via `/clp:PerformanceSummary` recorded as a **reading** in the ideal's "Net, honest verdict"; `testing-standard.md` §6 names the Core test projects as a group
  - Verify: `.\scripts\test-fast.ps1 -AllDefault`; `.\scripts\verify-change.ps1 -Paths docs/architecture/test-verification-boundary-ideal.md,docs/contributing/testing-standard.md -Session <id>`
  - Files: `docs/architecture/test-verification-boundary-ideal.md`, `docs/contributing/testing-standard.md`
### Checkpoint 5 — split landed
- [x] Every manifest project applied — **67/67** since TVB-F17's option (b) removed the one project that could not be (it is 68/67 only in the historical reading above); residual green; no test→test `ProjectReference` (W3); every csproj's references ⊆ its manifest `references` (W2)
- [x] CI and release list every Core test project with exit checks (W5); BalanceGuard lines match W6; no stale exact path (`guard-verification-boundaries.py` OK)
- [ ] `test-fast -AllDefault` green once (**blocked twice over: TVB-F25's two stale web fixtures are deterministic reds, and the profile is load-fragile — `RpgSimInProcHostTests.Two_consecutive_runs_on_fresh_hosts…` failed in one of two consecutive full runs and passes alone, an instance of `RS-CF3`**; the Core group is 68/68 green, 15,836 tests, and Data/Server are green); `Csc` reading recorded (**done** — 2,448 ms vs 8,680 ms at this tip); **re-read at `a6e84755a`: `Failed: 3, Passed: 271, Total: 274` (2m14s) — the same two goldens plus `RS-CF3`, and the main checkout @ `8958d88d6` still carries both stale goldens**)
## Wave 6 — `core-registry-rekey`
- [x] **TVB6.1 — Analyzer `--production-map`** · S · deps: TVB1.9 · *(spec: core-registry-rekey K1)* — done 2026-09-21 (lane `tvb59`): `ProductionMap.cs` (area index from the production compilation's own declared types, `AreasReferencedBy` from each test compilation's semantic model) + a `--project <Core csproj> --production-map [--test-projects <dir>]` mode reusing the analyzer's one `BuildCompilation`; both modes are read-only and share the same model. K-T1 runs as `--production-map --self-check` (one synthetic production area `Alpha` referenced from two synthetic test compilations, `Beta` from one) → **K-T1 PASS**. Real run at this head: 2709 declared types, 34 areas, 7 areas referenced by the two Core split projects with Debug output (`Battle`/`Power`/`Stats` from BOTH - the evidence K1 needs not to map by name); 24 other test projects skipped with no build output. **Erratum requested**: the task's own Files line names a new `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ProductionMapTests.cs`, but this lane's fence is `tools/**`,`scripts/**`,`docs/**`,`tasks/**`,`gk-data/packs/fusion/data/seed/**` - `tests/**` is tvb58's single-writer surface. K-T1 is therefore proven by the in-tool fixture; the xunit port is routed as TVB-F17. **ERRATUM SATISFIED 2026-09-23 (lane `tvb60`): the port landed** as `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ProductionMapTests.cs`, so this row's Files line is now true as written and no ruling is needed.
  - Acceptance: for each `gk-core/src/FusionRpg.Core/<dir>`, the test projects referencing its symbols; same compilation model, read-only
  - Acceptance: K-T1 green
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/ProductionMap.cs,gk-core/tools/TestSplitAnalyzer/Program.cs,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ProductionMapTests.cs -Session <id>`
  - Files: `gk-core/tools/TestSplitAnalyzer/ProductionMap.cs` (new), `gk-core/tools/TestSplitAnalyzer/Program.cs`, `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ProductionMapTests.cs` (new)
- [x] **TVB6.2 — K1: per-area Core production owners from the production map** · M · deps: TVB6.1, TVB5.9, TVB2.6 · *(spec: core-registry-rekey K1)* — done 2026-09-23 (lane `tvb60`), after fixing **TVB-F18** (the map now prints `compilation errors: 0` at 35 areas / 83 projects, two runs byte-identical). All **35 areas** now have an owner derived from the map, never by name: `core-area-*` rows **8 → 32**, plus `notify-core-domain`, `core-server-clock` and `core-narrative` re-pointed at their area's group (the guard's `ambiguous owner pattern` rule refused a duplicate row for a pattern that already had one). Boundaries **438 → 462**, projects **106 → 137** (31 new C7 groups). The 8 area rows that predated this were derived from the UNDER-reporting map and named a project narrower than the referencing set — each was widened to the map's exact set. K-T3: `Lawn/MoveQueue.cs` → `core-area-lawn-owners` (2 projects, was `core-fallback`'s 68), `Events/EventDrain.cs` → `core-events` (1), `Effects/DamageFx.cs` → 32, `Stats/ModifierBag.cs` → 29. K-T4: `gk-core/src/FusionRpg.Core/SimModels.cs` (a root file under no area) still plans `core-fallback` → the full 68-member `core` group. `core-fallback` unchanged; focused rows still win on their own paths. `-Report` orphans **7 → 8**, none `core.*`. Evidence: `tasks/evidence-fragments/tvb6-2.md`.
  - Acceptance: `gk-core/src/FusionRpg.Core/<A>/**` → the project (or exact group) the production map shows, never by name alone; `core-fallback` stays on the full `core` group
  - Acceptance: K-T3, K-T4 green; `-Report` before/after readings in the commit body
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs -Session <id>`
  - Files: `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`
- [x] **TVB6.3 — K2: re-key the existing focused `core.*` boundaries** · S · deps: TVB6.2 · *(spec: core-registry-rekey K2; G11)* — done 2026-09-23 (lane `tvb60`, split 67/68): the trait scan finds **24** focused boundaries still on the full `core` group — the 7 the acceptance names plus 17 the identical rule finds — and all 24 now name the project (or C7 group) holding their trait: 15 → `core-residual`, `keepverse-roots` → `core-workspace`, `core-advanced-effect-clock` → `core-effectclock`, `core-vocabulary-single-declaration` → `core-vocabulary`, `creature-kill-loot` → `core-items`, `creature-yield-tuning` → `core-expeditions`, `tools-prove-predictor` → `core-balance`, and two new groups (`core-combat-sim-tests` = Balance+ClassSystem, `core-drop-tables-tests` = Items+residual). Only `project` changed — no path string, no `level`, no guard (`battle-effect-math` keeps `battle-responsibility` + `funnel-delta`). K-T2 is the guard's own C7 rule (`:151-161`, ≥1 group member carries the trait) → `VERIFICATION BOUNDARY GUARD OK`; K-T4 still plans the full 68-member `core` group for an unmapped Core path. Evidence: `tasks/evidence-fragments/tvb6-3.md` (carries the 2026-09-21 no-op reading above it). **K1 (TVB6.2) is not a prerequisite for this row** — K2 only narrows `project`, and the split has landed.
  - Acceptance: each of `battle-effect-math`, `elemental-resolver`, `core-lawn-attrition`, `core-creature-catalog-generator`, `core-creature-corpus-dump`, `tools-combat-sim`, `tools-prove-predictor` names the project or smallest group holding its trait; every guard kept (`battle-effect-math` keeps `battle-responsibility`, `funnel-delta`)
  - Acceptance: K-T2 green
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json -Session <id>`
  - Files: `gk-core/scripts/verification-boundaries.v1.json`
- [x] **TVB6.4 — K3: orphan `core.*` traits + ideal line** — **K3 complete 2026-09-21 (lane `tvb59`)**: all six orphan
  `core.*` traits now have focused owner boundaries, each read out of its test class - `core-advanced-effect-clock`
  (`Effects/AdvancedEffectClock.cs`), `core.battle-mode-parity` (`Battle/BasicAttack.cs` + `Effects/Atoms/AtomKind.cs`),
  `core.kill-attribution` (`Battle/KillAttribution.cs`), `core.siege-estimator-parity`
  (`Battle/Siege/SiegeExpectedDamage.cs`), `core.species-term-compose` (`Battle/BattleHubCompose.cs` + `Stats/Derived/ActorHub.cs`),
  `core.vocabulary-single-declaration` (`Combat/Element/ElementTable.cs` + `Status/StatusCategoryRegistry.cs`). Guard OK at
  **370 boundaries**; `-Report` lists **7 orphans, none `core.*`**. The ideal's "Core half done" line is NOT written:
  the Core half includes K1, gated by TVB-F18. · S · deps: TVB6.3 · *(spec: core-registry-rekey K3; G12)*
  **COMPLETED 2026-09-23 (lane `tvb60`): the ideal now carries "R-TV2 execution — Core half done, 2026-09-23".**
  K1 was the gate and it landed (TVB-F18 fixed, TVB6.2 done), so the section states what the Core half
  actually is: 35 areas owned from the production map, 24 focused boundaries re-keyed, 8 orphans and none
  `core.*`, and the `Csc` reading beside the corrected projection. `core.species-passive-atoms` — one of the
  seven this row named — no longer exists as a trait anywhere under `tests/**`, so the orphan set K3 closed
  is six plus the `siege-estimator-parity` boundary that followed in the same lane.
  - Acceptance: a focused boundary for each of the seven orphans that has a production file its tests directly prove (read the test class); the rest stay in the `-Report` reading
  - Acceptance: fixture narrowing from TVB4.5 (`action-traces`/`battle-traces`) re-keyed to their project; ideal "R-TV2 execution" gains "Core half done"
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json,docs/architecture/test-verification-boundary-ideal.md -Session <id>`
  - Files: `gk-core/scripts/verification-boundaries.v1.json`, `docs/architecture/test-verification-boundary-ideal.md`
- [x] **TVB6.5 — reading: `Core/Stats` + `Core/Effects` production paths still plan `core-fallback`** · XS · — before-reading recorded and re-measured 2026-09-21 (lane `tvb59`): the seven paths still resolve to `core-fallback`/`core-tests-fallback` at this head, because K1 has not landed (it needs the split, and TVB6.2 depends on TVB5.9, still in flight on lane `tvb58`). The after-reading is TVB6.2's own acceptance (`-Report` before/after); this row is a reading, not a task with a separate deliverable, and closes when TVB6.2's numbers are recorded.
  added 2026-09-20 (`scope-side-wide` SSW2, measured, not inferred). A seven-path change inside
  `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs` and `gk-core/src/FusionRpg.Core/Effects/**` planned:
  `EffectBag.cs -> battle-effect-math (focused)`, the other four -> `core-fallback (module)`, both test
  files -> `core-tests-fallback (module)` — i.e. the run executed the **whole** Core project
  (**14 852 tests, 1 m 37 s**) plus the `battle-effect-math` group, which is exactly the cost K1/K2
  exist to remove. Two guards did select correctly (`battle-responsibility`, `funnel-delta`).
  - This is TVB6.2's own acceptance, recorded here as the before-reading for that task (K-T3/K-T4's
    `-Report` before/after pair), not a new defect: no production path in this change is unmapped to
    *something*, they are all mapped to the module fallback.
  - Acceptance: after TVB6.2, re-planning these same seven paths selects a group narrower than `core`.
  - **MET 2026-09-23 (lane `tvb60`), the after-reading of the same seven paths:**
    `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs -> core-area-stats (module)` -> `core-area-stats-owners`
    (**29** members, was the 68-member `core` group); `gk-core/src/FusionRpg.Core/Effects/CombatHitEmitPolicy.cs`
    and `gk-core/src/FusionRpg.Core/Effects/DamageFx.cs -> core-area-effects (module)` -> `core-area-effects-owners`
    (**32**, was `core-fallback`); `gk-core/src/FusionRpg.Core/Effects/AdvancedEffectClock.cs ->
    core-advanced-effect-clock (focused)` (K3); `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs ->
    battle-effect-math (focused)` (unchanged); **both test files -> `battle-effect-math` (focused)**, where
    the before-reading had them on `core-tests-fallback (module)` — i.e. the whole Core project. Both guards
    still select (`battle-responsibility`, `funnel-delta`). So the change that used to run the whole Core
    project plus the `battle-effect-math` group now runs three narrowed groups.
  - Files: `gk-core/scripts/verification-boundaries.v1.json`.
### Checkpoint 6 — program close (parent CC7)
- [x] A one-area Core production change plans that area's project/group, not every Core test — `Lawn/MoveQueue.cs` plans 2 projects, `Events/EventDrain.cs` 1, `Effects/DamageFx.cs` 32, `Stats/ModifierBag.cs` 29 (all were the full `core` group before K1)
- [x] Every pre-existing `core.*` focused boundary still selects its tests — `guard-verification-boundaries.py` OK (its C7 rule checks ≥1 group member carries each boundary's trait) and the planner prints the narrowed project for `LawnPermadeathLadder.cs`, `EffectBag.cs` and `gk-core/tools/CombatSim/Program.cs`
- [x] K-T1–K-T4 green; the map's §2 gaps G1–G18 each closed by a task above or named out of scope (map §6) — **verified 2026-09-23 (lane `tvb60`), each with its own reading:** K-T1 = `--production-map --self-check` PASS plus the xunit port `ProductionMapTests` (36/36 in that project); K-T2 = the guard's own C7 rule (`:151-161`) green at 462 boundaries; K-T3 = `Lawn/MoveQueue.cs` → 2 projects, `Events/EventDrain.cs` → 1, `Effects/DamageFx.cs` → 32, `Stats/ModifierBag.cs` → 29; K-T4 = `gk-core/src/FusionRpg.Core/SimModels.cs` (a root file under no area) still plans the full 68-member `core` group. G1–G18 each name an owning task in the map's §2 table and **every one of those tasks is ticked** (G1/G2 TVB2.6, G3 TVB2.2, G4 TVB2.1, G5–G7 the python lane, G8 TVB4.x, G9 TVB2.5, G10 the split, G11 TVB6.3, G12 TVB6.4, G13 TVB1.1–1.5, G14 TVB0.1, G15 TVB2.5, G16 TVB0.4, G17 the analyzer, G18 TVB5.4). One reading inside G12 has moved since it was taken: it lists `core.species-passive-atoms` among seven orphan traits, and that trait no longer exists anywhere under `tests/**` (`grep` finds none), so the orphan set is the six TVB6.4 owned — `-Report` prints **8 orphans, none `core.*`**. Out of scope is named where the map names it (§6: `npm test`/vitest and the web tree, TVB-F1).



### Findings from the TVB5.7 session (2026-09-20, `tvb57`)

- [x] **TVB-F1 — the brief's `gk-web/web/fusion-rpg-web` mapping item contradicts the program's own map** ·
  The brief orders the gap repaired, and `docs/architecture/test-verification-boundary-map.md:231`
  names Web out of scope ("`npm test`/`vitest`, a separate adoption slice per the predecessor map §7").
  Repairing it means inventing a `script`-runner wrapper (`npm test`) plus a `web` project, because the
  runner vocabulary is closed at `dotnet|pytest|script` (`gk-core/scripts/guard-verification-boundaries.py`
  `$validRunners`) — an architecture addition the map deliberately deferred. Needs an erratum ruling
  before a lane builds it.
  **RESOLVED 2026-09-23 (lane `tvb60`), re-read at the merged head `f585d8d6e`:** the erratum was given
  in practice — `ITEM-verify-2` built exactly the deferred slice, and as a `script` project rather than a
  new runner kind: `projects["web-fusion-rpg-web"]` (`gk-core/scripts/verification-boundaries.v1.json:192`, runner
  `script`, `scripts/checks/web-fusion-rpg-web.ps1` — `npm test` then `npm run build`) plus the owner
  boundary at `:5775` over `gk-web/web/fusion-rpg-web/**`. `verify-change -PlanOnly` on this row's own example
  path now prints `gk-web/web/fusion-rpg-web/src/features/aptitudes/autoAssign.test.ts -> web-fusion-rpg-web
  (module)` where it threw `VERIFICATION BOUNDARY MISSING`, and `guard-verification-boundaries.py` is
  `OK`. Nothing is owed here.
- [x] **TVB-F2 — `gk-forge/tools/seedsmith/tests/**` is already mapped; the brief's claim is stale** · The
  registry has `seedsmith-tests` (`gk-core/scripts/verification-boundaries.v1.json:2568-2578`) over
  `gk-forge/tools/seedsmith/tests/**` with `selfSelect: true`, on the `seedsmith` pytest project. No action;
  recorded so the row is not re-opened. — **re-verified 2026-09-23 (lane `tvb60`)**: the boundary is
  still exactly that (`paths: ["gk-forge/tools/seedsmith/tests/**"]`, `project: "seedsmith"`, `selfSelect: true`,
  `level: focused`), so the reading holds and the row is closed as recorded.
- [x] **TVB-F3 — the `VerificationBoundaryWorkflowTests` timeouts are the guard's coverage walk under
  load, not a fixed cost** · The failing cases (`Integrity_guard_passes_on_the_current_registry`,
  `P6_the_real_registry_resolves_seedsmith_and_tuning`,
  `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`) call
  `RunBoundaryGuard`, which runs the FULL `guard-verification-boundaries.py` including its
  repo-wide coverage walk; `Resolve-Owner` (`scripts/lib/VerificationBoundaries.ps1:130-147`) re-scans
  every owner boundary and pattern per file, so the walk is O(files × patterns). Measured this session
  under low load: `pwsh -NoProfile -File scripts/verify-change.ps1 -PlanOnly` on one path returned in
  9.5s, while the same class timed out at 2 min under the load the brief recorded (415s for two
  paths). Fix: index `Resolve-Owner` (exact-path dictionary + prefix trie) or pass `-SkipCoverageWalk`
  where the test does not assert the walk — never raise the timeout. Both
  `gk-core/scripts/guard-verification-boundaries.py` and `scripts/verify-change.ps1` are pipeline-protected,
  so this needs a ruling (or lane permission) before it can land.
  **Re-measured 2026-09-20 (lane `tvb58`)**: one tree, one session — the guard standalone under `pwsh`
  = **50 s** (`time python gk-core/scripts/guard-verification-boundaries.py`); the same guard
  through `VerificationBoundaryWorkflowTests.RunPowerShell` = **~105 s** (two cases isolated, 3 m 31 s
  total); with 15 concurrent `dotnet.exe` hosts from other lanes it exceeds the helper's 120 s budget
  and fails as `verification-boundary script timed out` (`Integrity_guard_passes_on_the_current_registry`
  on two runs, `P6_the_real_registry_resolves_seedsmith_and_tuning` on one), while the same cases pass
  on other runs and the guard was green standalone (50 s) between them. The 120 s → 300 s budget change
  was attempted and **REFUSED by the pipeline guard**
  (`gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs` is also a protected file; blocker
  note in `tasks/tvb-wave5-ledger.jsonl`), so indexing `Resolve-Owner` is the only route left.
  **CLOSED 2026-09-23 (lane `tvb60`) — the index landed, in the one file that was never protected.**
  `scripts/lib/VerificationBoundaries.ps1` now carries `New-OwnerPatternIndex` (owner boundaries bucketed by
  their pattern's FIRST path segment — a sound pre-filter, since `Test-ValidPatternGrammar` allows `*` only
  in the final segment) plus a reference-identity memo (`Get-OwnerPatternIndex`), and `Resolve-Owner`
  consumes it without changing the resolution: the same `Test-PatternMatch` + specificity rule still
  decides, the index only narrows the candidates. The fix therefore needed no edit to either protected
  script, which is why the refusal recorded above is no longer a blocker. **Readings at this head:** the
  guard standalone is **14.1 s** (`guard-verification-boundaries.py`, was 50 s on 2026-09-20) and **16.0 s**
  with `-Report`; the two cases that used to time out under load
  (`Integrity_guard_passes_on_the_current_registry`, `P6_the_real_registry_resolves_seedsmith_and_tuning`)
  are **2/2 in 1 m 17 s** (~38 s each through `RunPowerShell`, comfortably under the 120 s helper budget
  that 15 concurrent hosts used to exceed); the whole
  `VerificationBoundary|CoreTestProjectPolicy` filter is **63/63 in 5 m 32 s**. No timeout was raised and no
  `-SkipCoverageWalk` was passed — the walk still runs.
- [x] **TVB-F4 — the split tool leaves `<temp>/filemove-split-<guid>/` behind after a REVERT** · — **FIXED 2026-09-23 (lane `tvb60`)**: a revert that COMPLETED now deletes the journal directory (`SplitExecutor.Revert` calls `Keep` on `result.Ok`), because the tree then holds exactly what it held before `Apply` and the directory is a pure temp leak; a revert BLOCKED by a path mismatch still keeps it, which is the exit-3 recovery path (F10's own assertion is unchanged and still passes). Pinned by `A_successful_revert_deletes_the_journal_directory` in `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs` (48/48 green). The A4 sentence in `docs/architecture/test-verification-boundary/spec-core-split-apply.md` still reads "deleted only after a kept increment" and is now narrower than the code — that path is **outside this lane's allowed paths** (`docs/architecture/test-verification-boundary-*` does not match the `test-verification-boundary/` directory), so it is left for whoever holds it; the code's own doc comment records the widening.
  `gk-core/tools/FileMove/SplitExecutor.cs`: `Keep` removes the journal directory, `Revert` does not. A4 says the
  journal "is deleted only after a kept increment", which is deliberate for the exit-3 recovery path,
  but a *successful* auto-revert after a failed build/test leaves it too — found while re-applying
  TVB5.7 (a reverted apply left a 100 KB `journal.json`; `%TEMP%` held 47 `filemove-split-*` dirs).
  Low severity (KB, not the 65.5 GB class) but it is a temp leak in the tool this program owns: decide
  whether a successful `Revert` deletes the directory and whether A4's sentence needs to say so.
  Owning program: test-verification-boundary.
  **Second instance + the pre-gate check (2026-09-21, TVB5.8.13 `Commanders`)**: `Battle/KillAttributionTests.cs`
  in the residual has `using FusionRpg.Core.Tests.Commanders;` and reads `ShippedCommanders.Directory`, so the
  `Commanders` project could not take `ShippedCommanders.cs`; it now moves 8 explicit files and `links` that
  one. The general pre-check is to grep the moving files for the **namespace** form
  (`using FusionRpg.Core.Tests.<Folder>` or `FusionRpg.Core.Tests.<Folder>.`) — a grep for the file PATH misses
  a one-line `using`, which is exactly how this round's first attempt failed after reverting.
- [x] **TVB-F5 — `dotnet test` exits 0 over zero discovered tests, and only the split gate now knows** · — **audited 2026-09-23 (lane `tvb60`), no second instance found, row closed as recorded.** The audit the row asks for: every runner chosen by a path, filter or trait in this program's own surface was read — `scripts/test-fast.ps1` (explicit `-Project`/`-AllDefault`, its own count check), `scripts/test-sharded.ps1` (H-T6 reads the TRX files and fails an empty NAMED shard; an empty remainder passes by design, which is the partition's own construction), `scripts/verify-change.ps1` (a focused check runs `dotnet test` with a `VerificationId` filter and the boundary guard separately proves the trait exists in the project), and the split gate itself (`SplitExecutor.TestsReported`, pinned by `A_test_run_that_discovered_nothing_reports_no_count_rather_than_a_pass`). Only the split gate can silently run nothing; the others either count or partition. Recorded, not re-opened.
  The first real increment was kept with its new project running **zero** tests: the shared props had
  been built from self-closing `<PackageReference … />` elements only, so `xunit.runner.visualstudio`
  stayed in the residual, the new project had no test adapter, and `dotnet test` printed `No test is
  available in …` and **exited 0** (fixed in `gk-core/tools/FileMove`; see `tasks/evidence-fragments/tvb5-7-zero-test-gate.md`).
  The general shape — an exit code that cannot tell "the suite passed" from "no suite was wired" — is
  worth auditing anywhere a runner is chosen by a path, filter or trait; no second instance has been
  observed today. Owning program: test-verification-boundary.
- [x] **TVB-F17 — manifest project 30 (`FusionRpg.Core.GlobalUsings.Tests`) is not a splittable project: the
  file is a `global using` alias file** · `gk-core/tests/FusionRpg.Core.Tests/GlobalUsings.cs` declares
  `global using ActionRelation = FusionRpg.Contracts.RelationKind;` / `ActionRelations = RelationKinds` and says
  in its own header why: "global using is per-compilation, not propagated across project references — FusionRpg.Core's own alias does not reach this test project, so it needs its own copy". So it must be compiled into
  **every** Core test assembly (it is a shared file by definition) and it cannot both leave the residual and be
  its own project: moving it out breaks the residual, and a project holding only that file would have no tests.
  The manifest's "each root file is its own candidate" rule has no answer for this shape. Fix options: (a) put it
  in the manifest's `shared` set — which needs a props-regeneration path in `gk-core/tools/FileMove` (today the props is
  written only on the first increment), or (b) keep it in the residual and declare it out of the candidate model.
  Until then increment 30 is SKIPPED and increments 31+ proceed around it; the residual still compiles because
  the file never moved. Owning program: test-verification-boundary (tool/manifest decision).
  **Narrowed 2026-09-23 (lane `tvb60`), still open — and now the LAST open item of the whole split.** Option
  (a) is the correct one (the file is a `global using` alias set, i.e. shared by definition, and the manifest's
  `shared` set is exactly "compiled into every Core test project"), and it needs **one** thing that does not
  exist: a way for a plan to carry a SHARED-SET DRIFT. `SplitPlanner.Plan` writes the props, the shared moves
  and the residual edit only when `isFirstIncrement` (`:120`, `:158-181`), and `isFirstIncrement` is false for
  every project today — 67 of 68 are applied, and A1 refuses an applied project's directory (`tests/<n> already
  exists`), so **no `split --project <n> --apply` can carry the change**. The fix is therefore a new entry point
  (`split --shared` or an always-on drift diff), not a flag on the existing verb. Until it lands, project 30
  stays in `projects` as a live trap: `split --project FusionRpg.Core.GlobalUsings.Tests --apply` is NOT refused
  by A1 (its pattern still matches the file, and its directory does not exist) and would plan 5 operations that
  move the file out of the residual. Nothing else in the manifest is affected.
  **CLOSED 2026-09-23 (lane `tvb60`) by option (b), the cheap and correct one.** `GlobalUsings.cs` stays in the
  residual (its own header explains why: a `global using` is per-compilation, and every Core test assembly that
  needs the aliases needs its own copy — the residual's default glob compiles it, and no split project uses
  either alias, which every increment's own apply gate proved) and is declared **out of the candidate model**:
  the manifest's `projects` no longer holds project 30. Measured after the edit: `projects` = **67**, every one
  applied, `CoreTestProjectPolicyTests` **W1–W6 6/6** (W1 is the rule that would catch an unlisted csproj), the
  tool still refuses an applied project with only its own directory/include messages (no manifest complaint),
  and `guard-verification-boundaries.py` is OK. Option (a) — moving the file into the `shared` set — is the
  more elegant answer and stays available, but it needs the shared-set DRIFT entry point described above, and
  nothing depends on it now: the trap this row filed is gone (there is no `--project` target for it any more).
- [x] **TVB-F19 — `VerificationBoundaryWorkflowTests.InScopeFile` only looks for `.cs` files, so a docs-only
  active session record makes the whole class fail** · Observed 2026-09-21 in TVB5.8.33's verify run:
  `Planner_accepts_an_explicit_path_within_the_active_session_scope` failed in 12 ms with
  `System.InvalidOperationException: active session 'backlog-recon-20260921' claims no resolvable path`
  (`VerificationBoundaryWorkflowTests.cs:137`, called from `:144`). Cause read from the code: `InScopeFile`
  takes each active record's `paths` entries ending in `/**`, and for each one requires
  `Directory.EnumerateFiles(..., "*.cs", AllDirectories)` to find a C# file; it throws when none does. The
  `backlog-recon-20260921` record (`tasks/sessions/backlog-recon-20260921.json`, program "cross-program
  (measurement)", worktree `cmdc/recon-1`) claims exactly one path, `tasks/reports/**`, which holds Markdown
  reports and no `.cs` — a legitimate docs-only lane, and the test cannot express it. This is that lane's
  record meeting a test assumption, not a defect in either lane's work, and it is deterministic (not
  load-dependent), so it will fail every lane's Guard run until one of the two moves. Fix (in this program's
  test, which the pipeline hook currently protects): `InScopeFile` should accept any resolvable path — prefer a
  `.cs` file, but fall back to any file under the claimed directory — or skip a record whose claims contain no
  file at all rather than throwing for the whole class. Owning program: test-verification-boundary.
  **DONE 2026-09-23 (lane `tvb60`), and the row was stale**: the prepared change is already in the file. `VerificationBoundaryWorkflowTests.InScopeFile` enumerates `"*"` (skipping `obj`/`bin`), prefers a `.cs` file and falls back to the first file (`:131-146`), returns `null` instead of throwing (`:148`), has the `internal static string? InScopeFile(string root, …)` overload with the repo-root one delegating (`:121`), `ActiveSessionWithScope()` selects the first ACTIVE record whose fence resolves (`:154-169`), and `Planner_accepts_an_explicit_path_within_the_active_session_scope` returns early when none does (`:206-210`). The rule is pinned on a planted temp tree by `In_scope_file_search_prefers_a_code_file_but_accepts_a_documentation_fence` (`:175-198`, throwing `Directory.Delete` in `finally`, no assertion reads this repo's records or file counts). The brief's whole Guard filter is **63/63** green at `01e0dd525`, this class among them.
  `gk-core/tests/FusionRpg.Guard.Tests/**` applies, verbatim:
  1. widen the search in `InScopeFile`: enumerate `"*"` (still skipping `obj`/`bin`), prefer a `.cs` file with
     `FirstOrDefault(f => f.EndsWith(".cs"))` and fall back to `files.FirstOrDefault()`;
  2. give it an overload `internal static string? InScopeFile(string root, (string Id, string[] Paths) session)`
     with the existing one delegating (`=> InScopeFile(RepoRoot(), session)`), and return `null` instead of
     throwing when nothing resolves;
  3. add `ActiveSessionWithScope()` which walks the active records in the same order as `ActiveSession()` and
     returns the first whose `InScopeFile` is non-null, plus `if (session is null) return;` at the top of
     `Planner_accepts_an_explicit_path_within_the_active_session_scope` (its sibling rejects-outside-scope test
     is unaffected — it never calls `InScopeFile`);
  4. pin the rule with a planted-temp-tree fixture (create `tasks/reports/note.md` only → expect that Markdown;
     then add `tasks/reports/Helper.cs` → expect the `.cs`; a fence whose directory does not exist → `null`),
     deleting the temp tree in a `finally` with the throwing `Directory.Delete` this repo mandates. No assertion
     may read this repo's records or file counts.
- [x] **TVB-F6 (erratum requested; called "TVB-F3" in the manager's queue — that id is this file's
  `VerificationBoundaryWorkflowTests` timeout row, so the two must not share one) — the four pre-existing
  Core reds cannot be registered in `knownRed` from THIS tip: three of them are already repaired here,
  and a `knownRed` entry whose test passes is itself a guard failure** · — **MOOT AND CLOSED 2026-09-23 (lane `tvb60`)**: the erratum asked which tip's four reds to register. None: all four are GREEN at this head — the Core test group ran **68 projects, 15,836 tests, 0 failures** (`test-fast.ps1 -Project <every member>`, default profile), `SocketOperationsTests`, `UniqueCorpusTests` and `FamilyExpansionTests` among them — so registering them would now be exactly the guard failure this row warned about. `knownRed` keeps its 5 seedsmith/SR-25 entries and gains nothing.
  The audit is right about the **integration branch**: `gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs:329`
  (`No_shipped_gem_declares_an_omni_affinity`), `:340`
  (`The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement`),
  `gk-core/tests/FusionRpg.Core.Items.Tests/Items/UniqueCorpusTests.cs:524`
  (`Three_shipped_uniques_carry_a_family_their_own_frame_cannot_execute`) and
  `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/Generation/FamilyExpansionTests.cs:198`

  `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/Generation/FamilyExpansionTests.cs:193`
  (`Committed_generated_files_match_the_generator_byte_for_byte`) are red there (independent audit +
  `live-qa`'s `cc2/core-tests.txt` at 14833/14837).
  **On this tip they are green**: `1fa3cef0` repaired the first three — renaming two of them to their
  positive contract (`The_legacy_socket_word_corpus_is_retired_and_combination_is_the_only_kind`,
  `No_shipped_unique_carries_a_family_its_own_frame_cannot_execute`) — and `be986658` regenerated
  `gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json` for the fourth. Measured now:
  `dotnet test gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SocketOperationsTests|FullyQualifiedName~UniqueCorpusTests|FullyQualifiedName~FamilyExpansionTests"`
  → **77 passed / 0 failed**; the whole residual is **14822/0** in TVB5.7's own `verify-change` run. Two
  of the four names do not exist on this tip at all.
  **Why no `knownRed` entry can be added here**: `scripts/lib/VerificationBoundaries.ps1` D6 rule 3 fails
  any entry whose test RAN and PASSED (`stale knownRed entry <test>: remove it and its red row`), so
  registering the three would turn a green tip red — and CI with it. The deliverable is therefore
  refused, not skipped: **no `knownRed` change rides in this commit** (H7 is satisfied the other way —
  the publish and its readers are both untouched).
  **Erratum asked**: either cherry-pick `1fa3cef0` + `be986658` onto the integration branch (then no lane
  needs a `knownRed` entry), or name the tip at which the three are red and they will be registered there
  with a `red` debt row. The fourth (sockwords) is routed as a stale test to `tasks/item-todo.md`
  `ITEM-sockword-1` as instructed — on this tip it is already the retirement guard.
  Owning program: test-verification-boundary.
---
## Received from `backlog-clean-up` BCU8.5 (2026-09-20) — routing verdict
`backlog-clean-up`'s `infra-remainders` BCU8.5 asked whether this program covers
`data-test-substrate`'s BU2–BU4, and to route them here if it does.
- **BU2 (shard Data.Tests across processes) — THIS PROGRAM, and it is already delivered.**
  TVB1.1–TVB1.5 built and adopted it: `gk-core/scripts/test-shards.v1.json`,
  `scripts/test-sharded.ps1`, the id-set completeness proof (TVB1.2), the
  `_meta.measured` 2-vs-4-shard readings (TVB1.3), CI adoption at
  `.github/workflows/ci.yml:152` (TVB1.4), and the local module-level delegation
  (TVB1.5). `data-test-substrate-todo.md`'s BU2 row is ticked against exactly those
  artifacts — no work moved here, and nothing here is waiting on that row.
- **BU3 (`EnsureHotSchema` 46 ms gap) and BU4 (re-measure on an idle machine) — NOT
  this program's.** They are `FusionRpg.Data` store-timing questions with no
  boundary/sharding content; they stay `data-test-substrate`'s open rows, and BCU8.5
  recorded that routing there.
### Found defects (filed by `ep-autoassign`, 2026-09-20)
- [ ] **TVB-F1 — the registry has no owner boundary for any `gk-web/web/fusion-rpg-web/**` path, and none
  for a brand-new `gk-core/data/tuning/*-catalog.v*.json`.** `grep -c fusion-rpg-web
  gk-core/scripts/verification-boundaries.v1.json` is **0**, and `registry.projects` has no `web` entry, so
  `.\scripts\verify-change.ps1 -Paths <any web path> -Session ep-autoassign` throws
  `VERIFICATION BOUNDARY MISSING: gk-web/web/fusion-rpg-web/src/features/aptitudes/autoAssign.test.ts. Add
  an owner mapping; do not run a broad suite as a fallback.` (`scripts/verify-change.ps1:114`). Every
  other `gk-core/data/tuning` domain is mapped explicitly (`tuning-aptitude-catalog` →
  `data/tuning/aptitude-catalog.v*.json`, …) with no `gk-core/data/tuning/*.v*.json` catch-all, so a new
  catalog is unmapped too: the same call for `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json`
  throws the same message for that path. Cause: this is the still-open `web/tools/generated/config
  roots with their own fixed validators` slice (this file's own "Follow-on adoption slices", now
  superseded by `test-verification-boundary`), plus a per-catalog mapping style that cannot cover a
  file added by a lane whose fence excludes `scripts/`. Consequence for this lane: `verify-change.ps1`
  can only be run over the C#/docs subset of its changed paths; the FE half is proven by the
  `npm test` / `npm run build` / `npm run test:e2e` commands instead. Fix: add a `web` project with
  a vitest runner and a `gk-web/web/fusion-rpg-web/**` root boundary, plus a `gk-core/data/tuning/*-catalog.v*.json`
  fallback owner (like `tuning-fallback` for `gk-core/tools/tuning/**`). Not fixed here: `scripts/**` is
  outside this lane's fence.
  **Half closed 2026-09-23 (lane `tvb60`), which holds `scripts/**`, re-read at the merged head
  `f585d8d6e`:** the **web** half is done — `projects["web-fusion-rpg-web"]`
  (`gk-core/scripts/verification-boundaries.v1.json:192`) and the owner boundary at `:5775` resolve this row's own
  example path (`-> web-fusion-rpg-web (module)`; the guard is `OK`). The **tuning-catalog** half is **not**
  done and is **not** a missing mapping: `grep -n '"gk-core/data/tuning/\*\*"'` finds no catch-all while **122**
  explicit `gk-core/data/tuning/<domain>.v*.json` rows exist, and `gk-core/data/tuning/**` is an `EnforcedRoots` member
  (`scripts/lib/VerificationBoundaries.ps1:46`) precisely so a new file must name its own owner. A
  `gk-core/data/tuning/*-catalog.v*.json` fallback would make that root vacuous — every future tuning file would
  resolve to a project that does not consume it, turning a red into a *wrong green* — and it contradicts
  the rule this program already settled in **TVB-F8** ("a lane that adds a `gk-core/data/tuning/**` file must add
  its owner row in the same commit"). **Blocker, named exactly: a ruling.** Either keep the per-file rule
  (this half then closes as recorded, and a lane that adds a catalog asks the manager for the row) or rule
  that a catch-all is wanted (which needs an enforced-root exemption mechanism in the guard first).
- [x] **TVB-F2 — `gk-core/tests/FusionRpg.Guard.Tests` is red (3 of 573) on this tree, plus two registry-guard
  timeouts.** Found while verifying an EP1.21 docs change through
  `.\scripts\verify-change.ps1` (which selects the `guard.doc-boundary` boundary → the whole
  `FusionRpg.Guard.Tests` project): `Failed: 3, Passed: 570, Total: 573`, 7m19s.
  - `gk-core/tests/FusionRpg.Guard.Tests/SubprocessPipeDrainGuardTests.cs:55`
    `No_test_file_reads_stdout_then_stderr_synchronously` flags
    `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs`: that test file still does sequential
    `ReadToEnd()` on stdout then stderr, which is the pipe deadlock the guard exists to ban. Cause
    read: the FileMove split tooling is this program's TVB3.x wave and its test was written before (or
    without) `TestSupport/ExternalProcess.Run`; fix by switching it to the concurrent-drain helper.
    **Resolved 2026-09-20 (lane `tvb58`)**: `SplitExecutorTests.RunDotnetBuild` now drains both pipes
    concurrently (the same shape `TestSupport/ExternalProcess.Run` uses, inlined because test projects here
    do not reference each other) — `SubprocessPipeDrainGuardTests` is **1 passed / 0 failed** (was 1
    failed) and the FileMove suite stays **47/47**. Evidence: `tasks/evidence-fragments/tvb-f2-drain.md`.
  - `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs:214`
    (`Integrity_guard_passes_on_the_current_registry`) and `:1051`
    (`P6_the_real_registry_resolves_seedsmith_and_tuning`) both fail with
    `verification-boundary script timed out` from `gk-core/tests/FusionRpg.Guard.Tests/TestSupport/ExternalProcess.cs:42` — a fixed
    subprocess timeout that this machine's load exceeded (both were re-run alone and the same guard
    script completes; the registry is also being edited concurrently by the `tvb-wave5-20260920` and
    `keepverse-split` sessions). Cause: timeout vs a loaded machine, not a registry defect.
  Not fixed here: `gk-core/tests/FusionRpg.Guard.Tests/**` and `gk-core/tests/FusionRpg.FileMove.Tests/**` are outside
  this lane's fence.
  - **Manager evidence, 2026-09-21 at the post-merge head** (Guard suite run `b11c9249e`, 4 failed / 573+ passed): the pipe-drain guard is still red for a LIVE offender it names itself —
    `tests\FusionRpg.FileMove.Tests\SplitExecutorTests.cs` ("sequential stdout-then-stderr
    ReadToEnd() is a pipe deadlock and makes WaitForExit unreachable"). The first half of this row
    (the FileMove helper at `31df0398`) is done; this file is the remaining site. The Guard project
    is a **protected** path, so the fixing lane needs `--allow-protected gk-core/tests/FusionRpg.Guard.Tests/**`
    only if it must edit the guard; the offender itself is ordinary test code.
  - Two *other* reds in the same run were a walker defect, not a lane defect, and the manager fixed
    them on the guards plane (see the `SafeFiles` note below): `CiWiringGuardTests` and
    `CoreTestProjectPolicyTests` threw `UnauthorizedAccessException` on
    `tools/seedsmith/.tmp-seedsmith-pytest-audit` from `Directory.GetFiles(..., AllDirectories)`.
- [ ] **TVB-F3 — `verify-change.ps1` printed failing test runs and still exited 0, in two separate
  runs** (observed by `ep-autoassign`, 2026-09-20; reported, not diagnosed — `scripts/**` is outside
  that lane's fence and its instructions forbid probing the runner):
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-change.ps1 -Paths <20 changed paths> -Session ep-autoassign`
    → exit **0**, with `Failed! - Failed: 4, Passed: 14834, Total: 14838 - FusionRpg.Core.Tests.dll`
    in the same output.
  - `... -Paths tasks/empire-progression-todo.md,tasks/evidence-fragments/EP1.21.md,tasks/evidence-fragments/CP2.md -Session ep-autoassign`
    → exit **0**, with `Failed! - Failed: 3, Passed: 570, Total: 573 - FusionRpg.Guard.Tests.dll`.
  Cause not established. The visible contradiction is that the execution loop ends each `dotnet test`
  branch with `if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`, so a failing run should propagate a
  non-zero process exit; the exit-code mechanism itself was verified working on this host
  (`powershell -File` on a script containing `exit 5` returns 5, both redirected and not). Why it does
  not here needs a lane that owns `scripts/` to read the loop and reproduce — a gate that reports a
  failure but exits 0 would let a red change pass a caller that trusts the exit status alone.


  **Re-measured 2026-09-20 (lane `tvb58`, which owns `scripts/**`)**: the shape does **not** reproduce.
  On the pre-merge tip `verify-change.ps1 -Paths gk-core/tests/FusionRpg.Guard.Tests/SubprocessPipeDrainGuardTests.cs -Session tvb58`
  printed `Failed: 1, Passed: 572, Total: 573` and exited **1**; after re-merging `features/mega-merge`
  the same command printed `Failed: 3, Passed: 577, Total: 580` and exited **1**. The exit path is
  `scripts/verify-change.ps1:309`, `:313`, `:317` (one after every `dotnet test`) and `:322` (after every
  guard / doc-citations / script check), and a *guard* check's failure propagates too (the knownRed run
  above exited 1 at `doc-citations`). **The real hole in this family is a zero-test run**: `dotnet test`
  exits **0** when it discovers nothing (`No test is available in …`), measured live this session, so a
  selected check that runs no tests cannot be told from a pass — `verify-change.ps1` has no such check
  and is pipeline-protected for this lane. Erratum asked: the original command line + tip for the two
  exit-0 observations (a test-host crash that prints `Failed!` while VSTest exits 0 is the remaining
  candidate). Evidence: `tasks/evidence-fragments/tvb-f3-exit.md`.
  **Narrowed 2026-09-23 (lane `tvb60`), still open — one hole left, and it is hook-blocked.** The exit-0 shape
  still does not reproduce (my own runs: `verify-change` exits 1 on the two pre-existing Guard reds, and the
  sharded Data path exits 0 with four `exit 0` shards — see TVB-F12). What remains is the hole `tvb58` named:
  `dotnet test` exits 0 when it discovers NO tests, so a selected check that runs nothing is indistinguishable
  from a pass. The fix belongs in `scripts/verify-change.ps1` (parse the discovered count per `dotnet test`
  branch, the way `SplitExecutor.TestsReported` already does for the split gate — TVB-F5's audit found the
  split gate to be the ONLY runner in this program that can silently run nothing). `scripts/verify-change.ps1`
  is a pipeline-protected file: the hook refused an edit to it for this lane, and `anchor-ledger.py` carries
  the blocker note. Whoever holds the scripts plane: the change is one helper plus one call after each
  `dotnet test`, and it closes both this row and TVB-F12's family.
- [x] **TVB-F4 — `TuningRevisionLiteralGuardTests.No_reader_names_a_sockets_revision_literal`
  fails intermittently at `TuningRevisionLiteralGuardTests.cs:52`, and the failure is the guard's own
  walk, not an offender.** Found by the `ssh27` lane
  (`tasks/evidence-fragments/SSH5.2-merge-red.md`) at merged head `0dc4b307`, where the same filter is
  **2/2 GREEN** (`dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter
  "FullyQualifiedName~TuningRevisionLiteral"`), against the manager's earlier merged-head run that saw
  `Failed: 1, Passed: 1`. ssh27's predicate finds **0 offenders** across `c9ce309c`, `62db8f48`,
  `8aba2900` and main — only `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs:21` (the constant itself, skipped) plus
  comment lines — so no committed reader names a `sockets.v{n}.json` literal, and the red is the
  enumeration at `:52`: `Directory.EnumerateFiles(..., SearchOption.AllDirectories)` throwing on an
  absent top directory or an inaccessible/locked subdirectory *before* the `bin`/`obj` skip.
  - Mechanism evidence (hypothesis, to be confirmed by reading `:40-60`): the run that saw the failure
    had several concurrent `dotnet test` processes in that tree, and a later re-run in the main tree
    could not even build — `error MSB3027: Could not copy "obj\Debug
et8.0\FusionRpg.Guard.Tests.dll"
    ... The file is locked by: "testhost (75436)"` — i.e. a concurrently running suite holds files
    under the very tree this guard walks. So the enumeration meets a transient IO error under
    `bin/`, `obj/`, or `.claude/worktrees/**` while another process is writing there.
  - Fix: skip `bin`, `obj`, `.git`, `.claude`, `node_modules` **during** the walk (not after it) and
    tolerate `IOException` / `UnauthorizedAccessException` / `DirectoryNotFoundException` per
    directory, while still failing on a real offender. A guard that cannot separate "clean" from
    "could not read the tree" is not a guard: it turns a loaded machine into a false red and blocks
    every acceptance run that selects `guard.doc-boundary`.
  - Owner: this program (the Guard suite is its subject). The fixing lane needs `--allow-protected`:
    `ssh27` was refused by the pipeline hook when it tried to touch `gk-core/tests/FusionRpg.Guard.Tests/**`.


    **Measured on this tip 2026-09-21 (against manager baseline job b6712875b)**: the same guard project's
    `CoreTestProjectPolicyTests.W3`, `CiWiringGuardTests.Every_tools_test_project_is_wired_and_exit_checked`
    and `SubprocessPipeDrainGuardTests` are **3 passed / 0 failed** under one filter naming the three. The
    drain half is `31df0398` (not an ancestor of the baseline's `48fd754e`, so the baseline ran before the
    fix); W3/W7 are not reproducible from this branch — `tools/*.Tests` is exactly the two projects that are
    already wired, identical at `48fd754e` and here, and no commit in `48fd754e..3da77ab4` touched `ci.yml`
    or `tools/`. The baseline table itself is not in this branch, so the tips must be compared.
- [ ] **TVB-F5 — `decisions.md` citations have a second, unaudited form (the `(:N)` shorthand), and
  two ADR rows truncate themselves with an unescaped `|` inside a code span.** Found while closing
  `CV.3` (the `decisions.md:<N>` re-point, lane `docs-citations-1`, base `d12dcb90`). Two defects,
  one file:
  - **The `(:N)` shorthand.** Beside `` `decisions.md:<N>` `` the docs also cite rows as
    `decisions.md … (:N)` — e.g. `docs/architecture/trade-network/sector-yield/spec-banking-fact.md:370`
    (`(:7)`, `(:108)`), `docs/architecture/trade-network/trade-stories/spec-trade-predicates.md:123`
    (*"Atom attach points row (:113)"*) and
    `docs/architecture/legion-build/spec-general-member-hub.md:236`. Same drift class, same
    unattended file: `scripts/audit-doc-citations.py:57`'s `CITATION` regex matches only backticked
    code extensions, so neither form is audited. Three are already wrong — `(:112)`/`(:113)` cite
    *"Atom attach points"*, which is row 131 in the merged file, and `(:125)` at
    `docs/architecture/empire-inventory-surfaces/spec-legion-sheet.md:503` cites *GUI Lego*, which is
    132. `CV.3` deliberately re-pointed only the `` `decisions.md:<N>` `` form (its stated scope);
    this row is the rest.
  - **An unescaped `|` inside a code span truncates two ADR rows.** `docs/architecture/decisions.md:54`
    holds `` `combat.shield.capacity|toughness|pen|regen` `` and `:120` holds
    `` `2 − K/(K + |defense|)` ``. GFM splits a table row on an unescaped `|` *before* inline parsing,
    so each row parses as more cells than the 2-column header and every character after that pipe is
    dropped from the rendered page — the *Injector never writes a term of the damage equation* and
    *Combat mitigation shapes* decisions are silently truncated for every reader. The fix is `\|` in
    both code spans (4 characters); it is left out of `CV.3` because that lane's brief forbids
    rewriting unrelated `decisions.md` rows.
  - Owner: this program (doc-citation integrity is its subject); the fix needs a lane holding
    `docs/**`.
- [ ] **TVB-F6 — `verify-change.ps1` applies the `docs/` citation bar to `tasks/**` paths, and the
  repo guard does not, so one unrelated edit to a `tasks/*.md` file turns verification red on a
  pre-existing finding.** Found by lane `docs-citations-1` while closing `CV.3` (base `d12dcb90`).
  `scripts/audit-doc-citations.py:372` defaults `--scope` to `docs/`, so
  `scripts/guard-doc-citations.ps1 -Strict` audits only `docs/` — measured this session: 1681
  documents / 24859 citations, `D3 ambiguous basename 57 (0 HIGH)`, exit 0. At `--scope tasks/` the
  same audit reports **485 HIGH** over 728 documents (`D1 1286 / 357 HIGH`, `D2 15 / 15 HIGH`,
  `D3 113 / 113 HIGH`). `verify-change.ps1` then selects a per-path `doc-citations` check for every
  changed `.md`, which runs `audit-doc-citations.py --strict --scope <that file>` — a stricter bar
  than the guard it sits next to. Reproduced on a one-line, non-citation edit: re-pointing
  `tasks/ip-censor-plan.md:299` (a `decisions.md:<N>` cite, `CITATION`-invisible) made verify-change
  exit 1 at `tasks/ip-censor-plan.md:448  D3  \`_index.json:382-387\`  - 8 files share this name`,
  a line the diff does not touch (`git diff -U0 tasks/ip-censor-plan.md` = one hunk at `:299`).
  - Fix, one of: exempt non-`docs/` paths from the per-path citation check; make the guard and
    verify-change share one scope; or gate `tasks/**` deliberately and take the 485-HIGH burn-down as
    its own program. The gap is a gate-design gap either way — the guard's green and verify-change's
    red describe the same tree.
  - Owner: this program. The fix needs `scripts/**`, outside a `docs/**` + `tasks/**` fence.
  **Reproduced live 2026-09-23 (lane `tvb60`), at the merged head `f585d8d6e`:** appending one findings row
  to `tasks/summoner-convergence-todo.md` (an unrelated program's file, as the findings rule requires)
  made `verify-change` exit 1 on `tasks/summoner-convergence-todo.md:78  D3` — a citation **17 lines above
  anything the append touched** (`git diff -U0` shows only the append at `:125`), because the Core split
  this program landed moved `tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs` to
  `gk-core/tests/FusionRpg.Core.Items.Tests/`. The repo guard (`guard-doc-citations.ps1`, `--scope docs/`) is green
  on the same tree. This is the gap exactly as the row states it: **one file's edit turns verification red
  on a pre-existing finding in another program's document** — and the finding was this program's own move.
  Fixed here (paths re-anchored in that file, plus the reading that the four facts are green), which is the
  per-instance burn-down this row says cannot substitute for the gate fix.
- [ ] **TVB-F7 — the `N < 118` band of `decisions.md:<N>` citations is drifted too, and 6 of its
  occurrences sit outside `docs/**` + `tasks/**`.** `CV.3`'s brief bounded the re-point at
  `N >= 118`, so the band below it keeps the same defect. Measured this session over tracked files:
  **56 occurrences** with `N` in 110-117 (distinct `N` 110, 112, 113, 114, 115, 116) over 25 files -
  docs 47, `src` 5, tasks 3, web 1. The rows at those lines today are 110 *Game GUI* (correct),
  112 *Creature program*, 113 *Creature progression source and spawn ownership*, 114 *Unique lawn XP
  receipts*, 115 *Commander role*, 116 *Empire level* — so ~54 of the 56 name a decision other than
  the one their line holds: `decisions.md:112`/`:113` are cited for *"Atom attach points"* (row 131),
  `:114` for *"World store — delve worlds"* (133) and the delve-stage row (132), `:115` for
  *"Status SSOT + Resource model — nerve"* (134), `:116` for *"Action model — extended action
  slots"* (135).
  - Outside this lane's fence, left alone (all `decisions.md:114`, all describing the delve-worlds
    row, which is 133): `gk-core/src/FusionRpg.Core/Delve/RoomTypeCatalog.cs:9`,
    `gk-core/src/FusionRpg.Core/Delve/Attrition/DelveMemberState.cs:9`,
    `gk-core/src/FusionRpg.Core/World/Movement/LaneGate.cs:5`, `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:52`,
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:200`,
    `gk-web/web/fusion-rpg-web/src/stages/delve/graph/FightInPlace.tsx:9`.
  - Owner: this program for the doc side; the `src/**` + `web/**` occurrences need a lane holding
    those fences. Removing this cutoff also removes the reason the drift could survive a re-point
    pass that touched the same files.
  - **The `gk-core/src/FusionRpg.Core/**` half is DONE 2026-09-23 (lane `tvb60`), which holds that fence:**
    four citations re-pointed after reading the ADR rows themselves — `Delve/Attrition/DelveMemberState.cs:9`
    (`decisions.md:115` → **:134**, "Status SSOT + Resource model — nerve (2026-09-05)", the row its own
    comment is about), and `Delve/RoomTypeCatalog.cs:9`, `World/Movement/LaneGate.cs:5`,
    `World/WorldValidation.cs:52` (`:114` → **:133**, "World store — delve worlds (2026-09-05)", whose text
    names the `RoomTypeCatalog`/`DoorTypeCatalog` pair and `WorldValidation.Validate`'s delve profile
    exactly as those comments describe). Verified: `grep -oE 'decisions\.md:1[0-9][0-9]'` over
    `git ls-files 'gk-core/src/FusionRpg.Core/*'` now returns those four and nothing else, and each points at the
    row it names. `test-fast.ps1 -Project` on the two affected Core groups' own members is green
    (residual **9600/0**, `Items` **1468/0**). **What remains is out of this lane's fence:** 47 occurrences
    under `docs/**`, 3 under `tasks/**`, 1 under `gk-core/src/FusionRpg.Data/**`
    (`RpgStore.World.cs:200`, the same `:114` → `:133` re-point) and 1 under `web/**`
    (`stages/delve/graph/FightInPlace.tsx:9`). The docs half also needs `docs/architecture/decisions.md`
    itself — it is the file this row says "needs the whole band re-derived", and it is not in this lane's
    allowed paths.
- [x] **TVB-F8 — a tuning catalog shipped without an owner row, so the boundary guard and two Guard
  tests went red on `features/mega-merge`.** `guard-verification-boundaries.py` failed with
  `unmapped enforced-root file: gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` — the file arrived
  with the `ep-autoassign` merge (`741f5b01`) and no `boundaries[]` row owned it, while `gk-core/data/tuning/**`
  is an `EnforcedRoots` member (`scripts/lib/VerificationBoundaries.ps1:36`), so every file under it
  must resolve to an owner. The same omission is what failed
  `FusionRpg.Guard.Tests.VerificationBoundaryWorkflowTests.Integrity_guard_passes_on_the_current_registry`
  and `…P6_the_real_registry_resolves_seedsmith_and_tuning` (2 failed / 60 passed, 6 m 46 s) in `tvb58`'s
  runner verification — one root cause, not two lane defects.
  - Fixed at the manager plane (`tuning-aptitude-auto-assign-catalog`, project `server`,
    `verificationId server.derived-surface`, level `focused`, sibling of `tuning-aptitude-catalog`);
    `guard-verification-boundaries.py` is OK after the fix.
  - Remaining work for this program: a lane that adds a `gk-core/data/tuning/**` file must add its owner row in
    the same commit. **Corrected 2026-09-21:** the per-path check I first assumed was missing already
    exists — `scripts/verify-change.ps1:114` has thrown `VERIFICATION BOUNDARY MISSING: <path>` for any
    unmapped path since `fc1532a6b` (2026-09-14), for every root, not just the enforced ones. So the
    check did not fire for `ep-autoassign` because it only ever sees the paths its caller passes:
    the lane's own `-Paths` call must include the new file. The real remaining work is that the guard
    (which walks every file under an enforced root) stays the only net for a *missed* path, and CI is
    where it runs.
- [x] **TVB-F9 — the four Core reds behind `ISG-F1` are unregistered, so every acceptance that touches
  them reads `RED (unregistered failure(s))`.** Measured 2026-09-21 at the integration head `0a5c7415`
  (and reproduced at `ssh27`'s tip `4e94fd92` for the socket pair):
  `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketOperationsTests|FullyQualifiedName~UniqueCorpusTests|FullyQualifiedName~FamilyExpansionTests"`
  → **4 failed / 73 passed**: `SocketOperationsTests.The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement`,
  `SocketOperationsTests.No_shipped_gem_declares_an_omni_affinity`,
  `UniqueCorpusTests.Three_shipped_uniques_carry_a_family_their_own_frame_cannot_execute`,
  `FamilyExpansionTests.Committed_generated_files_match_the_generator_byte_for_byte`.
  - **Why this program and not the finding's owner:** the four are already routed with causes in
    `tasks/item-seedgen-todo.md` (`ISG-F1`), but *registration* is this program's — `knownRed` in
    `gk-core/scripts/verification-boundaries.v1.json` is the only way a boundary can report "pre-existing, owned"
    instead of "unregistered", and two manager acceptances (`cai-sink`, `ssh27`) plus CC8's inventory
    each had to be explained in prose because no entry exists.
  - **Acceptance:** each of the four is either fixed (then the entry is not needed) or carries a
    `knownRed` entry whose `debt` names `ISG-F1`, added with the measurement above as its evidence — and
    the entry is removed in the same commit that fixes the test (`knownRed` is debt, not a graveyard).


  - **Re-measured 2026-09-21 by lane `tvb58` at the merged head `386a29c4`**: the same filter prints
    **77 passed / 0 failed**, and the one failure in the whole Guard suite is CAI-guard-1 — so all four are
    already on the acceptance's first branch ("fixed … then the entry is not needed") and **no `knownRed`
    entry is added**. Adding one would be refused by the tooling anyway: `scripts/lib/VerificationBoundaries.ps1`
    D6 rule 3 fails any entry whose test RAN and PASSED (`stale knownRed entry <test>: remove it and its red
    row`). The repairs are `1fa3cef0` (two of the four renamed to their positive contract, `Assert.Empty`)
    and `be986658` (the regenerated `family-expand.g-evade.json`); `features/mega-merge` carries equivalent
    repairs for the socket/unique pair, and the merge kept its prose (identical assertions, 22/19 test
    methods). What remains is CC8 inventory wording: cite this measurement and its tip for the four, and
    keep `ISG-F1`'s routing unchanged for tips that lack those commits. Evidence:
    `tasks/evidence-fragments/TVB-F9-core-reds.md`.
- [ ] *(Rows TVB-F10..F12 were renumbered by the manager 2026-09-21: lane ep2-1 filed them as its own
TVB-F4/F5/F6, ids this program had already used. A union merge kept both sides, so two different
findings briefly shared one id.)*
**TVB-F10 — the seedsmith boundary's `module` fallback runs the whole pytest file set, which
  contains a test that makes a real model call and times out here.** **Filed by:** lane `cmdc-ep2-1`
  (`empire-progression`), 2026-09-20, while verifying EP2.12.
  **Cause:** the path→boundary mapping resolves most `gk-forge/tools/seedsmith/seedsmith/**` paths to
  `seedsmith-creatures (focused)` / a focused test file, but `gk-forge/tools/seedsmith/seedsmith/report/cli.py`
  resolves to **`seedsmith-fallback (module)`**, and that fallback selects `pytest: seedsmith` over the
  **whole** `gk-forge/tools/seedsmith/tests` tree. Two consequences, both observed:
  - the run takes **9m27s** and reports `22 failed, 4142 passed, 3 skipped, 4994 subtests passed` on a
    tree where the focused selection reported `9 failed, 939 passed` — so the counts a lane quotes
    depend on whether its changed path happens to hit the fallback, which is not visible from the path
    list alone;
  - `tests/test_actions_description_completeness.py::RealCommittedCorpusCleanPassTests::test_automatic_backfill_makes_zero_model_calls_and_writes_nothing_when_all_done`
    **attempts a real model call** despite its name and dies on `URLError: urlopen error timed out`
    (line ~190 of the boundary log), which is a network-dependent test inside a verification gate.
  **Fix:** either map `report/cli.py`-shaped paths to a focused selection that names the CLI test files,
  or exclude the network-dependent node from the boundary's pytest selection so a gate cannot hang or
  fail on a local-model timeout. The other 21 failures are repo-wide suite state in subsystems this lane
  never touched (actions corpus, items adapter, tree plan, usage stats, corpus loader, general propose,
  preflight, doc citations); 8 of them were independently proven pre-existing by removing this lane's
  files (see `tasks/evidence-fragments/EP2.9.md`).
  **HALF DONE 2026-09-23 (lane `tvb60`), still open on the second half.** The first option landed:
  `seedsmith-report` (`paths: ["gk-forge/tools/seedsmith/seedsmith/report/**"]`, `project: "seedsmith"`,
  `testFiles: ["gk-forge/tools/seedsmith/tests/test_cli.py"]`, `level: focused`) now owns that tree, and
  `verify-change.ps1 -Paths @('gk-forge/tools/seedsmith/seedsmith/report/cli.py') -PlanOnly` answers
  `seedsmith-report (focused)` instead of `seedsmith-fallback (module)`. Measured: the focused selection is
  **1 failed, 23 passed in 17.9 s** against the fallback's **22 failed / 4142 passed in 9m27s** — and that
  single failure, `test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch`, is
  pre-existing and already filed in `tasks/action-corpus-todo.md`. **What is left is the second option:**
  the network-dependent node is reachable through `seedsmith-actions`' own `testFiles` (it names
  `tests/test_actions_description_completeness.py`), so a change to `seedsmith/adapters/actions/**` still
  runs it. It is already a `knownRed` entry (debt SR-25), so the boundary *reports* it as pre-existing —
  what no lane can do today is keep it out of the selection, because that needs a pytest-exclusion field,
  i.e. a schema change in `guard-verification-boundaries.py` (pipeline-protected) plus the planner. That
  is the exact remaining item.
- [x] **TVB-F11 — the whole anchor tree `gk-data/packs/fusion/data/seed/creatures/species/**` has no verification boundary at
  all.** — **CLOSED 2026-09-23 (lane `tvb60`), resolved by the root mapping rather than a one-off row:** `seed-creatures-corpus` owns `gk-data/packs/fusion/data/seed/creatures/**` (`gk-core/scripts/verification-boundaries.v1.json`), so every path under the anchor tree resolves and `guard-verification-boundaries.py` is `VERIFICATION BOUNDARY GUARD OK` at 462 boundaries. The boundary-equivalent evidence this row recorded while blocked (its own 23-file reader set) is superseded by the real row. **Filed by:** lane `cmdc-ep2-1` (`empire-progression`), 2026-09-20, verifying EP2.13/EP2.14's
  corpus regeneration. **Cause:** `verify-change.ps1` refuses outright — `VERIFICATION BOUNDARY MISSING:
  gk-data/packs/fusion/data/seed/creatures/species/plant/artillery-flora.json. Add an owner mapping; do not run a broad suite
  as a fallback.` Any lane whose change regenerates the anchors (pass 2, the re-derivation pass, a
  threat-band refit) therefore cannot run the boundary command over its own changed paths, even though
  the tree is guarded on the generated side (`guard-generated-seed` inspected all 195 changed files
  clean in the same run). **Fix:** an owner mapping for the anchor tree — the honest check is the
  seedsmith contract/parity suite plus `guard-generated-seed`, not a broad run. `scripts/**` is outside
  this lane's fence, so this row is the report rather than the edit.
- [x] **TVB-F12 — the Data sharded runner reports every shard as failed with an empty exit code while the
  project is green.** **Filed by:** lane `cmdc-ep2-1` (`empire-progression`), 2026-09-20, verifying
  EP3.1. **Evidence:** `verify-change.ps1` for two `gk-core/src/FusionRpg.Data/**` paths + one Data test printed
  `shard a: exit , 63.3s, 437 tests`, `shard b: exit , 63.3s, 40 tests`, `shard c: exit , 63.3s, 83 tests`,
  `shard rest: exit , 63.2s, 1120 tests`, then `TEST-SHARDED FAILED` for all four — with **no `Failed!`
  line and no failing node named anywhere**. The same tree run directly
  (`dotnet test gk-core/tests/FusionRpg.Data.Tests`) is **1771 passed / 0 failed**. This is the same
  exit-code-propagation defect TVB-F3 recorded for the non-sharded runner ("printed Failed! runs yet
  exited 0"; here the exit code comes back empty, so a green run is reported as four failures).
  **Cause:** in the sharded path the per-shard exit status is read as an empty/`$null` value and
  compared as a failure — the placeholder in `shard a: exit ,` is where the code should be. **Fix:** a
  lane owning `scripts/` should check how the shard runner captures `$LASTEXITCODE` (the same class F3
  named) so a shard that printed no failures is not reported as a failure. A gate that fails a green
  run trains callers to ignore it.
- [ ] **TVB-F?** (routed by notification-ssot, 2026-09-21) **`tasks/run-board-20260920.md` fails its own
  doc-citation check.** `.\scripts\verify-change.ps1 -Paths 'tasks/run-board-20260920.md' -Session
  notification-ssot-20260920` selects `doc-citations` for that path and reports **4 HIGH (D1, file does
  not exist)**:
  - `:23` `InternalsVisibleTo.CoreTests.cs` — no such tracked file; the CoreTests/Data.Tests grants live
    in `gk-core/src/FusionRpg.Core/InternalsVisibleTo.Fusion.cs` (the only tracked `InternalsVisibleTo*`).
  - `:424` and `:428` `status.json` — the runner's own per-lane files, untracked and outside the repo.
  - `:430` `tasks/reports/BCU2.10-round-1.json` — not written yet (the lane watcher exits when it
    appears).
  Each wants the audit's own exemption: say on that line that the file is gone/untracked. **Note for
  whoever takes this: the board is a RUNNER-OWNED file — the pipeline guard refuses a lane's rewrite of
  it ("shell write to runner-owned pipeline files"), so the fix has to be the manager's own edit, not a
  lane's.** The same file also carries a stale count for this program (`notification-ssot | 26 | 55`
  against the measured `12 / 73`), which is why the manager's own dispatch notes keep calling finished
  rows open.
- [x] **TVB-F13 — re-measure the Guard suite at the head: the walker fix and the boundaries row have landed
  since the last full run, and the manager could not produce this number.** — **RE-MEASURED 2026-09-23 (lane `tvb60`)** at `01e0dd525`: `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~CoreTestProjectPolicy"` → `Passed! Failed: 0, Passed: 63` (5 m 32 s), and the FULL suite via `verify-change` → **`Failed: 2, Passed: 667, Skipped: 0, Total: 669, Duration: 6 m`** (the suite has grown 580 → 669 since the row's own reading). Both failures are attributed and neither is new: `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (W11 / `battle-derived-wire`) and `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary` (creature-seed T8), both investigated and routed in `tasks/reports/findings-2-head-guard-reds.md`; the walker defect, the drain offender and the two `VerificationBoundaryWorkflowTests` timeouts all stay green. Two attempts from the manager
  session failed (`b11c9249e` died holding the main tree's Guard test DLL; `bcd9e0407` exited 255 with a
  0-byte log) while six lanes were running tests, so the full-suite figure is the TVB lane's to produce —
  it owns the suite's baseline anyway.
  - **Known before the re-measure:** the four-failure list at the pre-fix head was
    `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (CAI-guard-1,
    routed, `tvb58`), `SubprocessPipeDrainGuardTests.No_test_file_reads_stdout_then_stderr_synchronously`
    (live offender `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs`, in `TVB-F2`),
    `CiWiringGuardTests.Every_tools_test_project_is_wired_and_exit_checked` and
    `CoreTestProjectPolicyTests.W3_no_test_project_references_another_test_project` — the last two were the
    walker defect (`UnauthorizedAccessException` on `tools/seedsmith/.tmp-seedsmith-pytest-audit`), fixed by
    the manager on the guards plane (`6bdd696c`, `GuardWiring.SafeFiles`) and verified at class level:
    `--filter "FullyQualifiedName~CiWiringGuardTests|FullyQualifiedName~CoreTestProjectPolicyTests"` →
    **11 passed / 0 failed**.
  - **Expected at the head (69035921 + the boundaries row `8d26f137`):** 2 failures, the two named above.
    `guard-verification-boundaries.py` is green at the head with the new `tuning-set-topology` row.
  - Acceptance: the suite's `Failed:` count and the failing names printed at the head, with any name not in
    the list above treated as new and attributed.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Guard.Tests` (do it when the machine is idle — several reds in this
    project are load-fragile, see `TVB-F2`/`TVB-F4`).
  - **Measured 2026-09-21 by lane `tvb58` at merged head `386a29c4`**: `dotnet test
    gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release` -> **Failed: 1, Passed: 579,
    Skipped: 0, Total: 580, 6 m 40 s**, and the single failure is
    `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (CAI-guard-1).
    Nothing else failed: the drain offender is GREEN here (`31df0398`, focused 1/0), W3/W7 are GREEN (the
    walker fix), and the two `VerificationBoundaryWorkflowTests` timeouts did not reproduce (the full guard
    was green standalone at 37.5 s in the same session). CAI-guard-1 is **BLOCKED** for this lane: the
    pipeline hook refused `gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs` a third time after the
    merge, so the `--allow-protected` grant this row names is not in effect at this lane's edit boundary;
    the exact two-line change is written into `tasks/combat-ai-todo.md`'s CAI-guard-1 row. Evidence:
    `tasks/evidence-fragments/TVB-F13-guard-suite.md`.

### Findings from TVB5.8.3 (lane `tvb58`, 2026-09-21)

- [x] **TVB-F14 — the analyzer's folder-SCC model misses cross-folder test inputs, and the apply gate finds
  them one revert at a time** · — **DONE 2026-09-23 (lane `tvb60`), with a recorded design deviation.** The report now prints `## Cross-candidate symbol edges (<N> — a reading)` from the `CandidateEdge` list the JSON draft has carried since TVB1.7 — measured on the real tree: **514** edges, e.g. `` `Actions` uses `FusionRpg.Core.Tests.Battle.BattleGoldenTests` from `Battle` (declared at Battle/BattleGoldenTests.cs, used at Actions/BasicAttackAdoptionTests.cs:43) ``, which is exactly the shape TVB1.10 could not see when it reported 0 `BLOCKS SPLIT`. **Deviation:** the row asked for it *as `BLOCKS SPLIT`*; it is a reading section instead, because a cross-candidate symbol edge is not always a blocker — the manifest's `links` field answers it and the SCC grouping already decides which candidates are clean, so a hard blocker would fail the tool on shapes that split perfectly well. Pinned by `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ReportTests.cs` (38/38 in that project). Evidence: `tasks/evidence-fragments/tvb-f14.md`. `gk-core/tests/core-test-projects.v1.json`'s Atoms entry needed TWO files that live
  outside the project's folder: `Atoms/EffectSeedFixtureOracle.cs` (a helper used by five files in the
  residual: `EffectBagAuditTests.cs`, `EffectBagTests.cs`, `EffectFunnelTests.cs`,
  `Combat/EffectBagMergedElementPayloadTests.cs`, `Combat/OwnerElementFallbackTests.cs`) and
  `World/StructureCatalogTestBootstrap.cs` (a `[ModuleInitializer]` the Atoms tests depend on). Each was
  found only when the gate built the residual or ran the new project (`CS0103`, then
  `StructureCatalog.Configure was never called`). TVB1.10's own run reported **0 BLOCKS SPLIT findings
  repo-wide**, so the analyzer's SCC/namespace model does not see this shape. Fix: make
  `gk-core/tools/TestSplitAnalyzer` report a project→project *file* dependency (a file in folder A referenced from
  folder B by symbol, including `[ModuleInitializer]` bootstraps and shared fixture oracles) as BLOCKS SPLIT,
  and let the manifest's existing `links` field carry the answer — which is what this increment used (74
  explicit `include` entries + 2 `links`), so the eventual fix has a worked example. Owning program:
  test-verification-boundary.
- [x] **TVB-F15 — the merged head's `doc-citations` CI guard is red for 20 HIGH findings in four other
  programs' documents** · Found while verifying TVB5.8.3 (`pwsh -NoProfile -File
  scripts/guard-doc-citations.ps1` → exit 1): `docs/architecture/notification-ssot-ideal.md` (12),
  `notification-ssot/spec-notify-vocabulary.md` (1), `npc-story-events/spec-petition-host.md` (2),
  `trade-network/trade-surface-map.md` (2), `trade-network/trade-surface/spec-trade-notify.md` (1),
  `trade-network/trade-surface/spec-trade-click-budget.md` (1), `world-stage/spec-world-notify.md` (1),
  `legion-build/spec-legion-count-cost.md` (1) — 19 D1 (all gone: `notifyRailStore.ts` / `categories.ts` /

  `legion-build/spec-legion-count-cost.md` (1) — 19 D1 there, none of them this program's (those web files no longer exist at the cited path): `notifyRailStore.ts` / `categories.ts` /
  `notify/clickBudget.test.tsx` no longer exist at the cited path) and 1 D2 (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs`
  is 1003 lines, cited at `:1013`). None is this program's; each is owned by the program whose doc it is
  (notification-ssot, npc-story-events, trade-network, world-stage, legion-build), and one row per owner is
  filed in those todos. This guard is gating in CI, so CC8 stays red until they are re-anchored. Owning
  programs: notification-ssot, npc-story-events, trade-network, world-stage, legion-build — filed as rows in the four that have a
  `tasks/<program>-todo.md`; `legion-build` has none, so its single D2 citation is tracked in this row only.
  **Extended 2026-09-21 (lane `tvb59`)**: at that head the same guard also reports four new D2 HIGH findings in
  `strain-splice-host`'s own docs (`docs/architecture/strain-splice-host-map.md:46,119`,
  `docs/architecture/strain-splice-host/spec-tier-ladder.md:19,114` — the combogen emitter cited at line 185 of a file that is now 175 lines),
  which this row's owner list did not cover; filed as `SSH-F1` in `tasks/strain-splice-host-todo.md` in the same commit.
  **Re-measured 2026-09-23 (lane `tvb60`) at `01e0dd525` — nearly drained, and the row stays open only for what is left:**
  `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` now reports **2 HIGH** (was 20 in eight documents),
  both D3 ambiguous-basename in a single other program's document:
  `docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md:76` cites `gk-forge/tools/seedsmith/seedsmith/adapters/items/fill.py:293-302`
  and `:532-540` after naming that file in full, and a second tracked
  `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/fill.py` now shares the basename, so the two short
  citations are ambiguous. That is already
  filed, with the same measurement, as **`RS-F18` in `tasks/rpg-simulator-todo.md`** (lane `sim-t3-2`,
  2026-09-23), so no new row is filed here. `D1` is 720 with **0 HIGH**, `D2` 7 with **0 HIGH** — every one of
  this row's own 19 D1 and 1 D2 findings is gone. The row closes when `RS-F18`'s two citations name a path.
  **CLOSED 2026-09-23 (lane `tvb60`), re-read at the merged head `f585d8d6e`:** `pwsh -NoProfile -File
  scripts/guard-doc-citations.ps1` → `1689 documents, 25804 resolvable citations checked`, `D1 683
  (0 HIGH)`, `D2 7 (0 HIGH)`, `D3 56 (0 HIGH)`, **exit 0**. `RS-F18`'s two D3 findings are gone, so this
  guard is green and the CC8 doc-citation clause it made red is clear. Nothing is owed here.


- [x] **TVB-F14 — `gk-data/packs/fusion/data/seed/items/combinations/**` has no owner row** — **CLOSED 2026-09-21 by TVB4.7 (lane `tvb59`)**: `seed-items-corpus` now owns `gk-data/packs/fusion/data/seed/items/**`, so `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths 'gk-data/packs/fusion/data/seed/items/combinations/strains.json' -AllowUnscoped -PlanOnly"` resolves to `seed-items-corpus` (module) with the `gen-items-gate` + `gen-item-seed-validator` script checks and the `generated-seed` guard — the remedy this row asked for, resolved by the root mapping rather than by a one-off row.
- [x] **TVB-F14 (original finding, kept for history) — `gk-data/packs/fusion/data/seed/items/combinations/**` has no owner row, so `verify-change.ps1` refuses every path on the combination corpus** · XS · deps: — · *(found by lane `ssh28`, 2026-09-21, running its SSH5.13 verification)* — **CLOSED 2026-09-23 (lane `tvb60`), same resolution as the row above it:** `seed-items-corpus` owns `gk-data/packs/fusion/data/seed/items/**`, so `gk-data/packs/fusion/data/seed/items/combinations/**` resolves; the `VERIFICATION BOUNDARY MISSING` refusal this line records no longer reproduces and the guard is OK at 462 boundaries.
  `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-data/packs/fusion/data/seed/items/combinations/strains.json') -Session strain-splice-host-20260921"` throws
  `VERIFICATION BOUNDARY MISSING: gk-data/packs/fusion/data/seed/items/combinations/combination-gen.ledger.json. Add an owner mapping; do not run a broad suite as a fallback.`
  Cause read: `gk-core/scripts/verification-boundaries.v1.json` has owner rows for other single-corpus files
  (`recipes-corpus` → `gk-data/packs/fusion/data/seed/items/recipes/recipes.json`, `status-anchor-tuning` → `…/_registry/status-anchor.v1.json`)
  and for `gk-core/data/tuning/*.v*.json`, and `seedsmith-items` owns `gk-forge/tools/seedsmith/seedsmith/adapters/items/**` — but **no
  pattern matches `gk-data/packs/fusion/data/seed/items/combinations/**`** (checked with fnmatch over every `boundaries[].paths`). All four
  files are unmapped: `strains.json`, `splices.json`, `combination-gen.ledger.json`, `combination-still-blocked.json`.
  So the very surface module 2 of `strain-splice-host` writes (`combination-regen`) cannot be verified through the
  boundary tool at all, and a corpus commit can only cite the tool runs the lane performed by hand.
  **Remedy:** one owner row `combination-corpus` → `gk-data/packs/fusion/data/seed/items/combinations/**`, project `seedsmith` (the
  gen-items gate seam already covers `gk-forge/tools/seedsmith/seedsmith/adapters/items/**`), placed by the manager or the
  pipeline lane — `scripts/**` is outside every lane's fence, which is why this is filed rather than fixed.
  **Verify:** `guard-verification-boundaries.py` green and `verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/items/combinations/strains.json --session <id>` resolving to exactly one owner.


- [x] **TVB-F17 — TVB6.1 and TVB6.2 name test files under `tests/**`, which lane `tvb59`'s fence excludes** · XS · deps: TVB6.1 · *(found by lane `tvb59`, 2026-09-21)* — **CLOSED 2026-09-23 (lane `tvb60`), which holds `tests/**`:** the K-T1 xunit port TVB6.1 could not write now exists as `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ProductionMapTests.cs` (asserting the fixture's OUTPUT — `Alpha` referenced by both synthetic projects, `Beta` by one — not only its verdict), and the analyzer's xunit side also gained `LinkedSourcePathsTests.cs`; the K1/K2 work itself landed in `gk-core/scripts/verification-boundaries.v1.json` with TVB6.2 and TVB6.3 both ticked with their readings. That project is **36/36** green.
  Both rows' Files lines name a new/edited `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ProductionMapTests.cs` and
  `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`. The runner's allowed paths for `tvb59` are
  `tools/**`, `scripts/**`, `docs/**`, `tasks/**`, `gk-data/packs/fusion/data/seed/**` — `tests/**` is tvb58's single-writer surface, so
  neither file can be written from this lane. K-T1 is instead proven by `ProductionMap.RunFixture()` through
  `dotnet run --project gk-core/tools/TestSplitAnalyzer -- --production-map --self-check` (see
  `tasks/evidence-fragments/tvb6-1.md`): the same synthetic two-project fixture, run for real.
  **Remedy:** either port that fixture into `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ProductionMapTests.cs` and
  move the K-T1/K-T2 cases of `TVB6.2` into `VerificationBoundaryWorkflowTests.cs` (lane tvb58, holds
  `--allow-protected`), or rule that the in-tool `--self-check` fixture is K-T1's standing proof and drop the test
  file from both rows' acceptance. Manager's call.
  **Verify:** `dotnet test gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests --filter "FullyQualifiedName~ProductionMap"` green, or the erratum recorded in TVB6.1/TVB6.2.


- [x] **TVB-F18 — `--production-map` under-reports: the analyzer's compilation lacks references the test projects build with** · M · deps: TVB6.1 · *(found by lane `tvb59`, 2026-09-21, by the diagnostic added in the same commit)* — **FIXED 2026-09-23 (lane `tvb60`)**: `Test projects with compilation errors: 0` at 35 areas / 83 projects scanned, and two runs are byte-identical. Four causes, each measured: (1) the linked sources (`gk-core/tests/Shared/KeepverseRoots.cs`, the shared props' four files) were never parsed — the project's own previously-built DLL supplied those types by accident, so removing that DLL ALONE made the map worse (11 erroring projects → 16; residual 16 → 57) and `CsprojReader.LinkedSourcePaths` now follows `<Import>` transitively and resolves relative includes against the declaring file; (2) `Directory.Build.props` is auto-imported, not named by an `<Import>`, and walking past the worktree root reached the MAIN checkout's own copy (duplicate `KeepverseLayout` in every project) — the walk now stops at the first file found, as MSBuild does; (3) the ASP.NET shared framework is absent from the process's TPA list (`Server.Tests` 489 errors) and is now found beside `System.Private.CoreLib`, version-matched to the project's `<TargetFramework>`, with native images refused up front (a mismatched 9.x against net8.0 and a native `aspnetcorev2_inprocess.dll` were each measured as their own error class); (4) with the shared sources parsed, the map OVER-counted — shared test infrastructure is compiled into every project, so 17 of 35 areas read 70-71 of 83 projects (the whole `core` group) until `AreasReferencedBy` was restricted to the project's own sources. `AreasReferencedBy` takes the restriction as an optional parameter, so K-T1's synthetic fixture keeps its whole-compilation shape. **The 2026-09-21 diagnosis above was wrong on its stated cause**: it read the first error as a missing framework reference and blamed the TPA list, but the TPA list was never the problem — the types that failed were test-side (`Type`/`List<>` in the 1047-error reading were the *GlobalUsings* gap fixed later the same week). Evidence: `tasks/evidence-fragments/tvb-f18.md`; the analyzer's own suite 35/35 (`LinkedSourcePathsTests` added for the three new behaviours). **TVB6.2 is now unblocked.**
  `dotnet run --project gk-core/tools/TestSplitAnalyzer -c Debug -- --production-map --project gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --test-projects tests --configuration Debug --format md` now prints
  `Test projects with compilation errors (the map UNDER-reports these): gk-core/tests/FusionRpg.Core.Atoms.Tests (1047), gk-core/tests/FusionRpg.Core.ClassSystem.Tests (421), gk-core/tests/FusionRpg.Guard.Tests (3553)`.
  **Cause, narrowed in the same commit:** each project's first error is `The type or namespace name 'Type' could not be found` (Atoms 1047, ClassSystem 421) / `'List<>'` (Guard 3553) — i.e. the test
  compilations have no core framework reference at all, even though `BuildCompilation` adds the process's
  trusted-platform-assembly list. `BuildAreaIndex` is unaffected because it reads only syntax-declared types,
  which is why the production side reports 2709 types while every test side fails. A preprocessor-symbol fix was
  tried and disproved first (error counts byte-identical), so the gap is in reference resolution, not `#if`.
  Cause read: `BuildCompilation` takes metadata from the project's own `bin/<cfg>/<tfm>/*.dll` plus the
  analyzer process's trusted-platform-assembly list (core-split-analyzer's "no MSBuild" Precondition) — that
  set is evidently not the full reference set these test projects build with, so a large part of each test
  compilation resolves to error symbols and `AreasReferencedBy` sees fewer areas than the project really
  references. The K-T1 fixture is unaffected (it supplies its own reference set); the 7-area real reading in
  `tasks/evidence-fragments/tvb6-1.md` is a floor, and **TVB6.2 must not derive an owner from it** until this
  is fixed.
  **Remedy:** resolve each project's real reference set without re-running MSBuild — the split test projects'
  own `*.deps.json` (or the csproj's `PackageReference`/`ProjectReference` set) read against the NuGet and
  project outputs — then re-run and confirm the per-project error count reaches 0 before the map is used.
  **Verify:** `--production-map` prints `Test projects with compilation errors: 0` for every scanned project, and the area list is stable across two runs.
- [x] **TVB-F15-TPL** (routed by notification-ssot, 2026-09-21) **The TVB-F15 routed row is itself a
  citation defect, in every todo it was copied into.** Its text names the gone files `notifyRailStore.ts`,
  `categories.ts` and `notify/clickBudget.test.tsx` as examples of dead citations, and quotes a spec
  line (`docs/architecture/legion-build/spec-legion-count-cost.md:26`) that cites the server endpoints
  file past its own end — so the row produces the very D1/D2 findings it is about. (This copy is now
  fixed the way the row prescribes: the files are named as gone, and the stale line is described
  instead of cited. The other programs' copies still need the same pass.) Measured: `python scripts/audit-doc-citations.py --scope tasks/world-stage-todo.md` reports
  them at lines 4294 and 4296 of that file, and the same text sits in the notification-ssot and
  npc-story-events copies. The notification-ssot copy is fixed (the line says the files are GONE, and
  the D2 is prose; commit `96927ae2`). Fix the template once — mark the examples GONE and describe the
  stale line instead of citing it — or every program that receives the row inherits a red audit.

- [x] **TVB-F16 — `gk-data/packs/fusion/data/seed/actions/**` has no boundary mapping, so a change to the action corpus's
  tracked outputs cannot be verified through `verify-change.ps1`.** Found 2026-09-21 by lane
  `seed-corpus` while committing the round-1 plan repair: `verify-change.ps1 -Paths
  gk-data/packs/fusion/data/seed/actions/_briefs/round-1.json` throws `VERIFICATION BOUNDARY MISSING: …
  Add an owner mapping; do not run a broad suite as a fallback.` The registry has `seedsmith-actions`
  (`gk-forge/tools/seedsmith/seedsmith/adapters/actions/**`) and `gen-items-gate-seam`, but **no row covers
  `gk-data/packs/fusion/data/seed/actions/**`** — the tree this runbook repeatedly commits (`_briefs/`, `_reports/`,
  `_rounds/`, `committed-*.json`, `type-weights.json`, `_generated/`, `species-innate.json`). The natural
  mapping is a focused owner row with `seedsmith-actions`' own 23 `testFiles` (every one reads this
  corpus); the filing lane could not add it because `scripts/**` is outside its session fence.
  Owning program: test-verification-boundary. Boundary-equivalent evidence recorded while blocked: the
  23-file set runs `12 failed, 1011 passed, 3 skipped, 1187 subtests passed` against this lane's
  regenerated plan, every failure pre-existing and registered in
  `tasks/seedsmith-generated-seed-repair-todo.md`.
  **Second tree, same gap (confirmed 2026-09-21, BCU2.12):** `gk-data/packs/fusion/data/seed/passive-tree/**` is unmapped
  too — `verify-change.ps1` also refuses `gk-data/packs/fusion/data/seed/passive-tree/nodes/AbyssSwordStar.json` and
  `_runs/tree-language.ledger.json`. The natural row there is a `seedsmith-trees` owner, focused on
  `gk-forge/tools/seedsmith/tests/adapters/trees/**` plus the tree metric tests; the same lane could not add it
  for the same fence reason.

- [x] **TVB-F16 — the Data test bootstrap does not configure `AptitudeTuningHub`, so the first Data-level district assault throws before it fights** · XS · deps: — · *(found by lane `ep-3`, 2026-09-21, running its EP3.12 verification)* — **FIXED 2026-09-23 (lane `tvb60`): `ContractTuningTestBootstrap` now configures `AptitudeTuningHub` from the highest shipped `data/tuning/aptitudes.v<n>.json` (never a pinned literal), and the private copies in `WorldTurnCasualtyTests` and `WorldTurnHubInputsForTests` — each with its own repo-root walk — are gone. The row's own Verify is green (`--filter "FullyQualifiedName~WorldTurnCasualty|FullyQualifiedName~WorldTurnHubInputs"` → 11/11) and the module boundary re-ran the whole sharded Data suite: 4 shards, 1741 tests, no overlap, `EXIT=0`. Evidence: `tasks/evidence-fragments/tvb-f16-aptitude-hub.md`.
  `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurnCasualty"` died with
  `AptitudeTuningHub.get_Tuning()` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeTuningHub.cs:18`) from
  `RpgStore.WorldTurnHubInputsForUnlocked` (`RpgStore.WorldTurns.cs:524`), called through
  `CommitWorldTurn`'s `HubInputsFor` delegate from `DistrictAssaultResolver.BuildAnimateSetups`.
  Cause read: `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs` configures ~20 hubs and not
  `AptitudeTuningHub`; `gk-core/tests/FusionRpg.Data.Tests/WorldTurnHubInputsForTests.cs:42` configures it in its own
  constructor for exactly this reason and says so in its comment. So NO Data test had ever committed a
  district assault through `RpgStore` — every siege test lived in Core (`TurnEngine.Step` directly) or drove
  the provider by hand. A lane that adds one must re-discover this each time (EP3.12's own test does it
  locally, with the shipped `aptitudes.v*.json` loaded by highest version, never a pinned literal).
  **Remedy:** configure the hub once in the Data bootstrap, the way
  `gk-core/tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs` does for every hub it names — a
  one-line addition plus the same "highest `aptitudes.v*.json`" loader the local fix already uses.
  **Verify:** `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurnCasualty"` green
  with the bootstrap edit and the test's own local `AptitudeTuningHub.Configure` call deleted. Owning
  program: test-verification-boundary (test substrate).

- [x] **TVB-F19 — `VerificationBoundaryWorkflowTests.InScopeFile` demands a `.cs` path from every active session, so a documentation-only lane can never pass** · S ·
  *(found by the manager's post-merge check run `bafaa803e`, 2026-09-21, from the manager's own lane `recon-1`.
  Numbered TVB-F19 because F14 was already in use twice — the id this routing first tried.)*
  - **Measured:** `Planner_accepts_an_explicit_path_within_the_active_session_scope` FAILS with
    `System.InvalidOperationException : active session 'backlog-recon-20260921' claims no resolvable path`
    (`gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs:137`, thrown from `InScopeFile`).
  - **The rule as written** (`:120-137`): a claimed path counts only if it is an existing **file**, or a `/**`
    path whose directory exists **and contains at least one `.cs` file**. A legitimate documentation-only
    session — this repo has them (`docs-citations-1` wrote docs; `recon-1` writes one report under
    `tasks/reports/**`) — therefore cannot satisfy it, and the test throws rather than skipping.
  - **Why it is the guard's defect and not the record's:** widening the record to claim a code path would grant
    a report-only lane write access it must not have, and widening the guard's allowlist is forbidden outright.
    The requirement should be *any* resolvable file the session may write (markdown included), or the test
    should skip a session whose fence contains no code path.
  - **Constraint:** `tests/**` is a single-writer chain held by one TVB lane at a time — coordinate; do not let
    two lanes edit this file.
  - **Verify:** `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundaryWorkflow"`.
  - **Measured instance cleared 2026-09-22, rule unchanged.** While the manager re-ran this class it came back
    **56/56 passed** with this test green: `recon-1` (`backlog-recon-20260921`), the documentation-only session
    whose fence `tasks/reports/**` triggered the throw, has been retired, and `InScopeFile` no longer sees a
    code-path-less active session. So the symptom is gone and the defect is not: the next lane whose fence holds
    only documentation will fail this test the moment it is active. Nothing to chase today; the row stands as
    the rule fix, not as a red.

- [x] **RECON-F3 — TVB6.1’s tick lagged its own merge, and TVB6.2 still carries residue** · XS · *(routed by the manager 2026-09-22 from `tasks/reports/backlog-reconciliation-20260921.md` §9, which lists it and deliberately does not file it: the lane's fence is `tasks/reports/**`.)* — **CLOSED 2026-09-23 (lane `tvb60`)**: TVB6.1 is ticked and its erratum satisfied (the K-T1 xunit port landed), TVB6.2 is ticked with its own reading (35 areas owned, 462 boundaries), and the residue this row names is gone — the two rows it pointed at are the two now-closed ones.
  `tasks/test-verification-boundary-todo.md:274` (fixed) and `:279`. Commit `21717632d` repaired TVB6.1’s analyzer but ticked neither row, so the merge and the tick disagree.

- [x] **RECON-F7 — `header_claims_complete` scans only the first 15 lines, so a mid-file closing banner is invisible** · XS · — **FIXED 2026-09-23 (lane `tvb60`):** the banner scan is now the whole document (`reconciled_banner_present`), and `BANNER_RE` accepts the marker-inside-bold shape that `tasks/loam-todo.md:1361` actually uses (`> **⛔ CLOSED — SUPERSEDED, 2026-09-03. …**`, which the first regex missed because `⛔` sits between `**` and the status word). Measured: `python gk-core/scripts/audit-program-pipeline.py --only todo-header-vs-boxes` prints **24 open** and `loam` is no longer among them (it was a false defect).
  `gk-core/scripts/audit-program-pipeline.py:232` (`HEADER_SCAN_LINES`). `tasks/loam-todo.md:1361`’s phase banner is its consequence: the audit reports a defect where the file has declared closure. Scan the whole file, or emit a distinct kind (`banner-closed-unticked`) when an unticked row sits under a closing banner. Whatever the fix, it needs the audit’s fixtures (`gk-core/tests/tools/test_audit_program_pipeline.py`) — assert behaviour, never a repo population count.

- [x] **RECON-F8 — three todos have no checkbox task marker, so the metric must declare them unmeasured** · XS · — **FIXED 2026-09-23 (lane `tvb60`), as the shape rather than the three names:** `gk-core/scripts/todo-shapes.v1.json` declares a shape per file, and a file that is absent from it or declared `"none"` is emitted as `unmeasured: no shape declared … (this file has no reliable task marker, so no count is invented)`. Measured at this head: **2 unmeasured** — `tasks/player-guide-todo.md` and `tasks/world-map-gaps-followup-todo.md` (both `"none"`); the report's third, `derived-stats`, is now classifiable (`H-checkbox-heading`, from the same report's S6) and `tasks/rpg-simulator-todo.md` — a todo the report predates — was added to the map as `R-bold` after reading its own marker lines, which also gives the census's 20 open blocks an independent reading.
  `tasks/derived-stats-todo.md`, `tasks/player-guide-todo.md`, `tasks/world-map-gaps-followup-todo.md`: their shapes never entered any registry. The replacement metric must report them as **unmeasured**, never default them to zero or guess.

- [x] **RECON-F9 — `session-boundary-check.py` false-positived when run from inside a worktree — FIXED by the manager 2026-09-22** · XS · *(routed by the manager 2026-09-22 from `tasks/reports/backlog-reconciliation-20260921.md` §9, which lists it and deliberately does not file it: the lane's fence is `tasks/reports/**`.)*
  `scripts/session-boundary-check.py:92` (`Test-Path $rec.worktree`): the record stores its worktree path **repo-root-relative** but the check tests it against the **current directory**, so a run from inside a lane’s own worktree probes `…/cmdc-recon-1/.claude/worktrees/cmdc-recon-1` and reports "worktree path … no longer exists" for paths that all exist — 7 records affected. From the repo root the same run reports clean. **This is not cosmetic:** it produced the boundary red the manager spent a turn attributing on `ep-3`’s acceptance, and it will keep producing them for every lane that checks its own fence. Resolve the path against the repo root before testing it.

- [x] **TVB-F20 — the replacement metric: count open TASK BLOCKS, and stop publishing a burn-down that does not reproduce** · M · deps: RECON-F7, RECON-F8 · *(design by lane `recon-1`, `tasks/reports/backlog-reconciliation-20260921.md` §7; filed by the manager 2026-09-22 because the report's fence forbade writing it, and an unfiled design is a design nobody implements)* — **DONE 2026-09-23 (lane `tvb60`):** kind `todo-task-blocks` added to `gk-core/scripts/audit-program-pipeline.py` (the existing tool, never a second one), the marker map is `gk-core/scripts/todo-shapes.v1.json` (119 files, each with its shape and a real exemplar, extracted from the report's own §3 classification and re-checked against each file), and `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks` now prints, at this head: **TOTAL open=734 done=2750 boxes=2014 (not a work count) shaded=857 · unmeasured=2 file(s)** over 117 todo files. Both routed defects landed in the same commit (RECON-F7, RECON-F8 above), and the tool prints what it cannot prove — including that the report's per-file hand overrides are deliberately not implemented, so these counts are reproducible by rule and need not equal that prototype's 858/2,705. Guard: 10 fixture cases in `gk-core/tests/tools/test_audit_program_pipeline.py` (25 passed), asserting behaviour, never a repo population. Evidence: `tasks/evidence-fragments/tvb-f20.md`.
  - **Why:** the manager's published burn-down (`524 open / 967 done`) **does not reproduce under any of 13 candidate definitions** and has no recorded provenance; the real reading is **858 open task blocks / 2,705 done** over 118 `tasks/*todo.md`, with 1,018 of 2,158 unticked lines (47%) sitting inside blocks the same file declares closed. Retired as a metric (board, 2026-09-22) until this lands.
  - **Counter — extend the existing tool, never a second one:** add kind `todo-task-blocks` to `gk-core/scripts/audit-program-pipeline.py`. Count open/done blocks per file by the block rule of §1 (a closure phrase in the body is checked **before** the boxes — checking boxes first moved 68 blocks), and print `open=<n> done=<m> boxes=<k> (not a work count) shaded=<s>`.
  - **Marker map — `gk-core/scripts/todo-shapes.v1.json` (new):** per file `{ "shape": "H-task|H-id|R-bold|R-plain|H-bracket|H-checkbox-heading|none", "exemplar": "<a real heading>" }`. A file absent from the map, or `"none"`, is reported **unmeasured** — never defaulted to zero (that is `RECON-F8`'s three files: `derived-stats`, `player-guide`, `world-map-gaps-followup`).
  - **Two defects to fix in the same commit:** (i) `header_claims_complete` (`gk-core/scripts/audit-program-pipeline.py:230`) scans only `text.splitlines()[:HEADER_SCAN_LINES]` (`:76`, 15 lines), so a mid-file closing banner is invisible and `tasks/loam-todo.md:1361` reads as a false **defect** — scan the whole file, or emit a distinct kind `banner-closed-unticked` when an unticked row sits under a closing banner (`RECON-F7`); (ii) `species-gear-chain-todo.md:16-17`'s clause *"a ticked task's acceptance boxes are its original contract"* has no banner phrase, so `RECONCILED_BANNER_RE` (`:99`) misses it and 240 unticked lines read as open work where the true count is **6 blocks** (`RECON-F6`) — recognise the clause or add the file a banner.
  - **Guard — fixtures only** in `gk-core/tests/tools/test_audit_program_pipeline.py`: a heading-task file (2 ticked, 1 open → `open=1 done=2`), a banner file (3 unticked, 0 open), and a mid-file banner with a row beneath it. ⛔ Assert the behaviour, **never a repo population count** (`docs/architecture/validation-ssot.md`).
  - **What it cannot prove, stated in the tool's own output:** that a tick is true; that an open block is unfinished rather than deferred/blocked/superseded/owner-only; that the marker map is complete; and any **size** — `L-run` and `XS` count the same, so this measures remaining rows, not remaining effort.
  - **Verify:** `python gk-core/scripts/audit-program-pipeline.py` prints the new reading; `python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q`.

- [x] **TVB-F21 — two CI-gating guards are RED at the integration head and routed nowhere: `magic-numbers` and `population-pin`** · M · — **CLOSED 2026-09-23 (lane `tvb60`), acceptance met by the reading:** `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` at `01e0dd525` prints `magic-numbers ci gating 0` and `population-pin ci gating 0` — both exit 0 at the head, so the reddening was repaired by the lanes that owned the numbers (the acceptance's alternative branch, a registry entry, was not needed). The only gating red left in the same sweep is `doc-citations`, which is TVB-F15's and now 2 HIGH in one other program's document (`RS-F18`).
  *(found by the manager 2026-09-22 while attributing tvb58's acceptance; measured with `pwsh -NoProfile -File scripts/<guard>.ps1` at HEAD and again in tvb58's review checkout -- exit 1 in BOTH, so pre-existing rather than that batch's doing.)*
  - **Measured:** `run-guards.ps1 -Tier ci` fails with `guards failed: doc-citations, magic-numbers, population-pin`. `doc-citations` is already routed (`TN-cite-1` / `NSE-cite-1` / `WS-cite-1`); the other two are not.
  - **Why it matters now:** these are `gating` entries in the CI tier, so they are exactly what CC8's `test-fast.ps1 -AllDefault` green reading will trip over. They were reported **clean earlier the same day** (`guard-magic-numbers.ps1` exit 0, `guard-population-pin.ps1` clean), so something merged in between reddened them — the first job is to find *which* commit, because a guard reddened by a merge is a finding about that merge, not about the guard.
  - **Acceptance:** both guards exit 0 at the integration head, with the reddening commit named and its cause stated; if the cause is a legitimate new balance number or a new population, the guard's registry gains the entry **with its owner** — never a bare allowlist widening and never a `knownRed` addition.
  - **Verify:** `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` and `pwsh -NoProfile -File scripts/guard-population-pin.ps1`, each exit 0; then `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`.

- [x] **TVB-F22 — `AGENTS.md` says CI runs 13 C# test projects; `ci.yml` names 60** · S · *(found by lane `sim-idea-b`, 2026-09-22, outside its fence; it asked which program should carry the row.)* — **VERIFIED FIXED 2026-09-23 (lane `tvb60`):** `AGENTS.md:156` now reads "CI (`ci.yml`, Windows) runs the test projects wired in that file -- **60 at the last count** ... **`ci.yml` is the list; this sentence is not**", which is the owner's ruling applied (the count kept as a reading, the list named). No further change; the row is closed against the ruling.
  This program owns the CI wiring statements, so it carries it: the count is a **reading, not a constant**
  (`docs/architecture/validation-ssot.md` — a guardrail validates the contract, never a population count), and
  the sentence is what agents brief each other with. **Fix:** state the invariant (every test project in
  `FusionRpg.slnx` is wired; the split manifest is the list) rather than a number that rots, or wire the
  sentence to the same source `ci.yml` is generated/checked against.
  **Owner ruling 2026-09-22:** *update stale* -- fixed in the same commit: the sentence now names `ci.yml` as the list and keeps the count only as a reading. The duplicate row `RS-CF1` in `tasks/rpg-simulator-todo.md` is cross-referenced to this one.

- [x] **TVB-F23 — `gk-core/tests/fixtures/rpg-scenarios/**` has no owner row, so `guard-verification-boundaries.py` is RED for the new scenario corpus and `verify-change.ps1` refuses its path** · XS · deps: — · *(found by lane `sim-slice0`, 2026-09-22, running RS1's verification; the lane's fence is `gk-core/tests/FusionRpg.E2E.Tests/**`, `gk-core/tests/fixtures/rpg-scenarios/**`, `tasks/**`, so it could not write the registry.)* — **CLOSED 2026-09-23 (lane `tvb60`), fixed by the lane that added the corpus:** the registry now carries `e2e-scenario-fixtures` over `gk-core/tests/fixtures/rpg-scenarios/**`, and `guard-verification-boundaries.py` is `VERIFICATION BOUNDARY GUARD OK` at 462 boundaries — so the `unmapped enforced-root file: gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` reading this row records no longer reproduces.
  - **Measured:** `python gk-core/scripts/guard-verification-boundaries.py`
    prints `VERIFICATION BOUNDARY GUARD FAILED` / `unmapped enforced-root file:
    gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`, exit 1 — and this guard is a **gating** `ci`-tier
    row (`gk-core/scripts/enforcement-registry.v1.json:68`) run as its own step
    (`.github/workflows/ci.yml:347`). `verify-change.ps1 -Paths
    'gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json' -PlanOnly` refuses with `VERIFICATION BOUNDARY
    MISSING`.
  - **Cause (read, not guessed):** `gk-core/tests/fixtures/**` is an enforced root
    (`scripts/lib/VerificationBoundaries.ps1:46` — "every file under an ENFORCED root must resolve to an
    owner"), and the registry's `core-test-fixtures` boundary (`gk-core/scripts/verification-boundaries.v1.json`)
    names only `gk-core/tests/fixtures/action-traces/**`, `battle-traces/**`, `effects/**` and `combat/**`. The new
    `rpg-scenarios` subtree is a fifth, and the house pattern is to add the subtree and its row together:
    `git show --stat 04b8daa0c` shows `gk-core/scripts/verification-boundaries.v1.json` (+11) in the same commit as
    `gk-core/tests/fixtures/battle-traces/**`.
  - **Why it matters now:** `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` is the approved home of the
    `rpg-simulator` scenario corpus (owner ruling C1 (a), 2026-09-22; row `RS1`, evidence
    `tasks/evidence-fragments/rpg-sim-rs1.md`). Every lane that adds a scenario file reddens CI until this row
    lands, and the red is attributed to that lane rather than to the registry.
  - **Fix:** add a boundary (or extend `core-test-fixtures`) owning `gk-core/tests/fixtures/rpg-scenarios/**`, with the
    owning project — the E2E project is the only consumer today
    (`gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs`), so `project: "e2e"` is the honest owner; if the
    RS2 runner (`gk-core/tools/RpgSim`, approved A1 (a)) consumes the same tree later, the boundary's level is the
    question that decides it then, not now.
  - **Acceptance:** `python gk-core/scripts/guard-verification-boundaries.py` exits 0 at a head carrying
    `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`, and
    `verify-change.ps1 -Paths 'gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json' -PlanOnly` resolves the
    path to a boundary instead of refusing it.
  - **Files:** `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`,
    `gk-core/scripts/verification-boundaries.v1.json`, `scripts/lib/VerificationBoundaries.ps1:46`.

- [x] **TVB-F22 (routing pointer) — a new program's seed tree broke the guard's completeness walk** · The guard
  refused six files with no owner row at the merged head while increment 66 of the split was landing (its own
  checks green): five under `gk-data/packs/fusion/data/seed/ip-censor/_registry/**` (routed to `tasks/ip-censor-todo.md`) and
  `gk-core/data/tuning/creature-rank.v1.json` (routed to its owner below). The recurring shape worth a program row: an
  **enforced root** (`gk-data/packs/fusion/data/seed/**`, `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/generated/**`, `gk-core/tests/fixtures/**`) means a new
  file anywhere under it fails every lane until its owner row exists — the guard is doing its job, but the
  program that lands the file pays a red it does not see. Owning program: test-verification-boundary (routing
  only). **ROUTED 2026-09-23 to `TVB-F24` (below), which carries the measurement and the fix; the six files this
  line routed were mapped in `67abbcefb` and the guard is green at the head again.**

- [ ] **TVB-F24 — a lane that adds a file under an ENFORCED root gets a GREEN `verify-change` and a RED integration guard** · S · *(found by the manager at integration, 2026-09-23, while merging `cs-rank` and `ip-censor`; independently found the same day by lane `tvb58` while increment 66 landed — see `TVB-F22` above, whose routing this row now carries)*
  `scripts/verify-change.ps1:18-28` runs the boundary guard with **`-SkipCoverageWalk`**, and the comment says why:
  the full repo-wide completeness walk cost 415 s against a 2-path call (measured TVB4.3) and is "CI/the
  standalone guard's job". The consequence was not in that tradeoff's sight: **the coverage walk is the only
  check that catches a NEW file under an enforced root**, so a lane that adds one cannot see its own omission
  locally. Measured: merging `cs-rank` (T1's `gk-core/data/tuning/creature-rank.v1.json`) and `ip-censor` (T4's
  `gk-data/packs/fusion/data/seed/ip-censor/_registry/*.json`, five files) left **six** files unmapped; both lanes' own
  `verify-change` runs were green, and the standalone guard failed at integration with
  `VERIFICATION BOUNDARY GUARD FAILED / unmapped enforced-root file: …` (exit 1). None of the three branches
  carried the mapping either (`mentions: 0`), so this is a real local-signal gap, not a merge artefact.
  **Fix (the narrowing, not the walk):** when any path this call was given lies under an enforced root
  (`$Script:EnforcedRoots` in `scripts/lib/VerificationBoundaries.ps1` — `gk-core/data/tuning/**`, `gk-core/tests/fixtures/**`,
  `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/**`), run the coverage walk **for those paths only**, or select the standalone
  guard without the skip. That keeps the fast path for every ordinary edit and closes the hole for exactly the
  edits that can open it. Evidence of the fix: a planted file under `gk-core/data/tuning/**` must fail the local verify.

- [x] **TVB-F25 — the E2E host never configured `LeadNamesHub`, so 237 of its 274 tests failed in their
  class-fixture constructor, and two stale WEB fixtures hid behind that** · S · *(found by lane `tvb60`,
  2026-09-23, running TVB5.9's `test-fast.ps1 -AllDefault`)*
  `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:117` (`SeedSpeciesRoster` → `RpgStore.Init()`) →
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:4201` (`SeedPlayerIfEmpty`) → `:4218` (`OnboardingPlayerName`) →
  `gk-core/src/FusionRpg.Core/Narrative/LeadNames.cs:319` throws `LeadNamesHub.Configure(...) has not run`. **Cause read
  from the code:** identity-rename T13 (2026-09-19) added the process-wide hub and wired it in the Core/Data/
  Server test bootstraps and the `CreatureSpeciesImport` tool, but not in
  `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs` — the one assembly whose own comment three lines
  above the insertion point already records the rule (*"`RpgApiFactory.SeedSpeciesRoster` constructs its own
  `RpgStore` and calls `Init` BEFORE `Program.cs` runs, so this assembly needs both registries configured
  here"*, SE4.12). Measured before/after the one `Configure` line: `Failed: 237, Passed: 37, Total: 274` →
  `Failed: 2, Passed: 272, Total: 274` (same filter, `Category!=DiskSemantics&Category!=Heavy`). **Fixed in this
  lane** (`tests/**` is in its fence).
  The two survivors are **web**-tree fixtures, unreachable from any lane of this program: 
  `gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json:6` still says `"Crazy Dave"` where the live DTO — and the
  ip-censor-authored `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` `lead_summoner` — says `"Garden Keeper"`,
  and `gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json:4` carries `b41ce3ef4c7c…` where the
  live opening hashes `0f685a162409…`. Both paths are outside this program's fence and, per **TVB-F1**, have no
  owner boundary at all, so `verify-change.ps1` cannot be pointed at them either. **Owning programs:** the
  rename is `ip-censor` (its report already authors `the Garden Keeper` for `crazy-dave`), the turn hash is
  `world-stage` (W20). Manager: please route both. This is the blocker named on **TVB5.9**'s green-run
  acceptance.
  **CLOSED 2026-09-23 (manager + lane `tvb-f25b`):** fixture 1 re-blessed (`"Crazy Dave"` → `"Garden Keeper"`, one line; Commander filter 41/41); fixture 2 re-blessed (six `stateHash` lines via `WorldTurnFixtureTests` + `FUSIONRPG_BLESS_WORLD_FIXTURE=1`, entries byte-identical — `WorldCanonical` hashes faction `Name`, identity-rename moved all six; clean re-run 1/1); `commander-surface.spec.ts:158` updated to Garden Keeper (only fixture-fed assertion) with the spec 10/10; guards 25/0. Ledger: `tvb-wave5-ledger.jsonl` TVB-F25 done.

### Found live by lane `tvb60` (2026-09-23) — the guard runner's verdict table under a stripped PATH

- [ ] **TVB-F26 — `run-guards.ps1` reported 5 phantom red guards when the invoking shell's PATH lacked
  the interpreters the guards shell out to** · S · *(found 2026-09-23 while running this lane's own
  verification; `scripts/run-guards.ps1` is one of this lane's granted paths)*
  The runner invokes each guard as a child host and reports **that child's exit code as the guard's
  verdict** (`scripts/run-guards.ps1:141`). A guard that shells out to an interpreter *by name* therefore
  reports **its own red** when the interpreter is simply not on PATH: `guard-narrative.py
  -RunTraitFilter` (`:105-117`) runs `dotnet test`, whose own helper spawns `powershell`
  (`gk-core/tests/FusionRpg.Guard.Tests/TestSupport/ExternalProcess.cs:34`), and `guard-magic-numbers.ps1`,
  `guard-overflow.ps1`, `guard-population-pin.ps1` and `guard-vocabulary-mirror.ps1` run `python`.
  **Measured, one machine, one tree (`a6e84755a`), two consecutive runs of `scripts/run-guards.ps1 -Tier ci`:**
  stripped PATH → `guards failed: doc-citations, magic-numbers, narrative, overflow, population-pin,
  vocabulary-mirror` (**6 red**); complete PATH → `guards failed: doc-citations` (**1 red**, the
  pre-existing `RS-F18`). All five phantoms are green under a complete PATH, and
  `guard-narrative.py -RunTraitFilter` prints `0 failed` in both projects it selects. **Cause read from
  the code:** the runner cannot know which interpreter a guard needs — that is the guard's own business —
  so it cannot pre-resolve one; and the child is resolved by name against the *caller's* PATH, which an
  agent's bash shell does not carry `C:\Windows\System32\WindowsPowerShell\v1.0` in.
  **Fix landed in this lane** (`scripts/run-guards.ps1:110-121` and `:174-180`): the runner now names the
  missing interpreters in a `WARNING (environment, not a guard verdict)` block before the table, and in
  the failure line. Deliberately **not** a hard stop — a source-only guard is still a real verdict under
  the same stripped PATH (`-Only dal` → `DAL GUARD OK`, 0 red), so the warning cannot mask a genuine red.
  **Still owed, and named exactly:** the Guard regression test. Its home is
  `gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs` (it drives the real runner against a temp registry),
  and the edit was **refused by the pipeline guard**, whose message names `guards` as the protected class
  — this lane may not write that project. Evidence without the test: `GuardRunnerTests` **8/8 passed** with
  the change in place. Manager: grant the Guard test project to a lane, or rule the test unnecessary.
  **The grant shape already exists in this repo:** `tasks/sessions/tvb58.json` records a runner-level
  `allowProtected` grant for two `gk-core/tests/FusionRpg.Guard.Tests/**` files (TVB-F19 and the CAI guard re-pin),
  so the same grant for `GuardRunnerTests.cs` is the smallest thing that unblocks this row.

- [x] **TVB-F27 — the `Vfx` increment's consumer-table row never landed, so
  `scripts/audit-status-vfx-identity.ps1` ran the residual with a filter that matched no test and
  printed `PASS`** · S · *(found 2026-09-23 by lane `tvb60` while auditing every row of the
  `core-split-wiring` consumer table; `scripts/**` is in this lane's fence)*
  `scripts/audit-status-vfx-identity.ps1:41` ran `tests\FusionRpg.Core.Tests\FusionRpg.Core.Tests.csproj`
  with `--filter "FullyQualifiedName~StatusVfxIdentity|FullyQualifiedName~VfxAuraMath"`, but those four
  test files moved to `gk-core/tests/FusionRpg.Core.Vfx.Tests/Vfx/` in the `Vfx` increment, so the filter matched
  **0** tests. Measured: `No test matches the given testcase filter … FusionRpg.Core.Tests.dll` with
  **exit 0** — and the script's only check was `if ($LASTEXITCODE -ne 0)`, so it printed
  `Static tests: PASS` while running nothing. The spec's own consumer table names this exact row
  (`docs/architecture/test-verification-boundary/spec-core-split-wiring.md:53`, "the project holding the
  status/VFX identity tests"). **Fixed in this lane:** the static step now runs
  `tests\FusionRpg.Core.Vfx.Tests\FusionRpg.Core.Vfx.Tests.csproj` and treats a zero-selection run as a
  failure, parsing the printed `Total:` exactly as `guard-narrative.py:130` does (a filter that matches
  nothing exits 0, so the printed count is the verdict). Readings through the real script:
  `Static tests: PASS (63 selected)`; the same filter on the old project gives `parsed selected=0
  exit=0` → the new check throws. Evidence: `tasks/evidence-fragments/tvb-f27.md`.
  **Second half, and it is not a footnote:** the script had **no verification boundary at all** —
  `verify-change.ps1 -PlanOnly -Paths scripts/audit-status-vfx-identity.ps1` threw
  `VERIFICATION BOUNDARY MISSING` — so a change to the file could not be scoped by the repo's own tool.
  Fixed in the same commit: `gk-core/scripts/verification-boundaries.v1.json`'s existing `core-vfx` owner row
  gains the path, and the call now plans `scripts/audit-status-vfx-identity.ps1 -> core-vfx (module)` /
  `test: core-vfx`. Boundary guard green afterwards (463 boundaries, `schemaVersion` 5).
  **The audit's other half came back clean at `4369eda29`:** `ci.yml` **68** project pairs plus its
  BalanceGuard pair naming `FusionRpg.Core.Balance.Tests` — the only project whose tests carry
  `Category=BalanceGuard` (11 occurrences in
  `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/DominanceGuardTests.cs`); `release.yml` **68**;
  `scripts/test-fast.ps1` **68**; the registry's `core` group **68** members, a bijection with the 67
  manifest projects + the residual; `FusionRpg.slnx` **68**; `scripts/coverage.ps1:55` and
  `scripts/mutate.ps1:91` both resolve their project from `gk-core/tests/core-test-projects.v1.json`; and
  `scripts/regen-class-system-baselines.ps1:173` / `gk-core/scripts/verify-golden-attribution.py:31` still name
  `Battle/BattleGoldenTests.cs`, which the split left in the residual, so those two paths are still
  correct. **CLOSED 2026-09-23 (lane `tvb60`)** — the commit that carries this row fixes the filter, the
  zero-selection refusal **and** the missing boundary (`core-vfx` now owns the script), with the readings
  in `tasks/evidence-fragments/tvb-f27.md`; nothing is owed here.

- [ ] **TVB-F28 — a `gk-core/src/FusionRpg.Contracts/**` DTO change invalidates a checked-in FE contract fixture,
  and no local check selects the test that catches it** · S · *(found 2026-09-23 by lane `tvb60` at the
  merged head `f585d8d6e`, running TVB5.9's `-AllDefault` acceptance after `git merge --no-ff
  features/mega-merge`)*
  `gk-core/tests/FusionRpg.E2E.Tests/ContractFixtureTests.cs` exists to catch exactly this: its own header says
  "A server-side DTO change that isn't re-blessed here fails in whichever project noticed first". It
  caught one — and nothing in the change's own verification pointed at it.
  - **The instance.** `0770c0f81` (save-identity **SE4.31**, 2026-09-23) added
    `gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs:22` `[JsonPropertyName("empireId")]`; the live
    `POST /api/unique/actors` DTO now carries `"empireId": "dave"` while
    `gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json` (last written `e588c251a`, 2026-08-23) does not.
    Measured: `Failed: 3, Passed: 273, Skipped: 0, Total: 276` in `scripts/test-fast.ps1 -Project
    gk-core/tests/FusionRpg.E2E.Tests`, one of the three being
    `ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto`. `0770c0f81` is **not** an
    ancestor of this lane's pre-merge head (`git merge-base --is-ancestor 0770c0f81 4f60fc741` → NO), so
    the mega-merge introduced the red.
  - **The cause, read from the registry.** `verify-change -PlanOnly -Paths
    gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs` plans `contracts-fallback (module)` / `test: core` — the
    whole 68-project group (`gk-core/scripts/verification-boundaries.v1.json:679`, `project: core`) — and **not**
    `gk-core/tests/FusionRpg.E2E.Tests`. `ContractFixtureTests` carries no `[Trait("VerificationId", …)]`, and no
    boundary names the E2E project for a Contracts path, so the one test that can see the drift is
    invisible to the change that causes it. This is the **TVB-F24 class one tree over**: local green,
    integration red, no local signal.
  - **Fix landed 2026-09-23 (lane `tvb60`) — shape (d), a `seam`.** All three shapes below missed that
    `scripts/verify-change.ps1:115`'s `VERIFICATION BOUNDARY AMBIGUOUS` throw is reached only for **`owner`**
    boundaries (`:112` filters `kind -eq 'owner'`); the seam loop (`:119-121`) appends to the selection with
    no ambiguity check, so a seam on the owner's own paths is additive by construction (`level` derives to
    `seam`, `scripts/lib/VerificationBoundaries.ps1:231`). Landed: `[Trait("VerificationId",
    "e2e.contract-fixture")]` at `gk-core/tests/FusionRpg.E2E.Tests/ContractFixtureTests.cs:18` + boundary
    `contracts-fixture-seam` (`gk-core/scripts/verification-boundaries.v1.json:6069-6079`, `kind: seam`, the same
    `gk-core/src/FusionRpg.Contracts/**` paths as the owner, `project: e2e`, `level: seam`, appended last so no
    existing registry line shifts). `verify-change -PlanOnly -AllowUnscoped -Paths
    gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs` now prints both `-> contracts-fallback (module)` /
    `test: core [68 csproj]` and `-> contracts-fixture-seam (seam)` / `test: e2e e2e.contract-fixture` —
    additive, lossless and narrow (2 tests, ~11 s) instead of a sixth TVB-F26-class guard (a), a coverage
    reduction (b) or 276 E2E tests per Contracts edit (c).
  - **Why the row stays open — blocker, named exactly.** The seam's focused check is red at this head and
    stays red until `gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json:6` (`"Crazy Dave"` vs live
    `"Garden Keeper"`, `ip-censor`) and `gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json` (no `empireId`,
    `summoner-convergence` SE4.31) are re-blessed — TVB-F25's two fixtures, already routed. Measured before
    the change: `--filter "FullyQualifiedName~ContractFixtureTests"` → `Failed: 2, Passed: 0, Total: 2`;
    after: `--filter "VerificationId=e2e.contract-fixture"` → `Failed: 2, Passed: 0, Total: 2`. CI is red on
    these already (`ci.yml:333` runs the E2E project with an exit check), so the seam moves an integration
    red to a local one; it does not create one. The row closes when the focused check is green once.
  - **Shapes ruled out by (d):** (a) a new `enforcement-registry` guard
    (`scripts/checks/contract-fixtures.ps1`, `tier: local`, referenced from `contracts-fallback.guards`)
    that runs the filter and refuses a zero-selection run the way `guard-narrative.py:130` does — additive,
    but a sixth instance of the **TVB-F26** phantom-red class under a stripped PATH; (b) a `script` project
    boundary on a narrower Contracts pattern — drops the `core` run for the DTO files it owns; (c) add the
    E2E project to the `core` **group** — additive and lossless, but runs 276 E2E tests on every Contracts
    edit.
  - **Owner: this program** (the boundary surface is its subject and `scripts/**` is in its fence); no
    ruling is owed on the shape now that (d) is landed. The fixture re-bless itself is a separate,
    web-tree row — filed against `summoner-convergence` (SE4.31) in `tasks/summoner-convergence-todo.md`,
    because `gk-web/web/fusion-rpg-web/**` is outside this lane's fence.
  - Evidence: `tasks/evidence-fragments/tvb60-register-reverify-merged-head.md`,
    `tasks/evidence-fragments/tvb-f28-contract-fixture-seam.md`.

- [x] **TVB-F29 — `tools-audit-tests` landed with tests but no CI step, so
  `CiPytestWiringTests.Every_pytest_project_has_a_ci_step_running_pytest_in_its_own_root` was red at the
  merged head** · XS · *(found 2026-09-23 by lane `tvb60` in the same re-verification; `ci.yml` is one of
  this lane's granted paths)* — **FIXED in this lane.** The merge added
  `projects["tools-audit-tests"] = {runner: pytest, root: ".", tests: "gk-core/tests/tools"}`
  (`gk-core/scripts/verification-boundaries.v1.json:183`), which the `pipeline-audit-scripts` boundary (`:3325`)
  uses to own `gk-core/scripts/audit-program-pipeline.py` and `gk-core/scripts/fix-doc-citations.py` — but `ci.yml` had no
  `python -m pytest` line under a step whose `working-directory` equals that project's `root`, and the
  guard counts nothing else (`gk-core/tests/FusionRpg.Guard.Tests/CiPytestWiringTests.cs:25`). Measured:
  `pytest project root(s) with no 'python -m pytest' CI step at that working-directory: .`. `git show
  4f60fc741:gk-core/scripts/verification-boundaries.v1.json | grep -c tools-audit-tests` = **0**, so the merge
  introduced it. The suite is green (`python -m pytest gk-core/tests/tools -q -p no:cacheprovider` → `25 passed in
  4.60s`, stdlib-only), so the step is safe on its first CI run. Added after the `gk-core/tools/tuning` step (where
  `pytest` is already installed) with the exit check `WorkflowExitCheckTests` requires. Readings:
  `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter
  "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~CoreTestProjectPolicy|FullyQualifiedName~CiPytestWiringTests|FullyQualifiedName~WorkflowExitCheckTests|FullyQualifiedName~CiWiringGuardTests"`
  → `Passed! - Failed: 0, Passed: 74, Skipped: 0, Total: 74` (5 m 48 s);
  `guard-verification-boundaries.py` → `VERIFICATION BOUNDARY GUARD OK`. Evidence:
  `tasks/evidence-fragments/tvb60-ci-pytest-wiring.md`.

- [ ] **TVB-F30 — a residual file that a manifest `include` pattern claims is a divergence nothing
  checked, and A1 makes it unrepairable** · S · *(found 2026-09-23 by lane `tvb60` at `0c7fb6c69`, by
  reconciling the real manifest against the real residual)*
  A1 resolves an `include` pattern against `gk-core/tests/FusionRpg.Core.Tests/` (its own example is
  `["World/**"]`), so a residual file a pattern matches is **claimed** by that project — the manifest
  did not leave it, and A5's "whatever the manifest leaves in the residual stays there" does not cover
  it. Nothing checked that on disk: the patterns are validated only when an increment is applied, and A1
  then requires the target directory **not** to exist (`gk-core/tools/FileMove/SplitManifest.cs:112-113`, pinned
  as a contract by `gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestTests.cs`
  `The_target_project_directory_must_still_not_exist`). So a file added to a claimed residual folder
  *after* its increment can never be moved by the tool — measured: `dotnet run --project gk-core/tools/FileMove
  -c Release -- split gk-core/tests/core-test-projects.v1.json --project FusionRpg.Core.Stats.Tests` prints
  `REFUSED: manifest fails 1 A1 rule(s): [FusionRpg.Core.Stats.Tests] gk-core/tests/FusionRpg.Core.Stats.Tests
  already exists`.
  - **Measured divergence — four files, one claimed folder.** Increment 60/68 (`cb0f048fb`) moved
    `Stats/**` into `gk-core/tests/FusionRpg.Core.Stats.Tests/`; four Stats-area test files were added to the
    residual afterwards, by four different lanes: `Stats/ActorLivenessRevisionTests.cs` (`6eb250bc4`,
    lawn LW1.5), `Stats/ActorLivenessRevisionsTests.cs` (`fcfc39789`, lawn LW1.6),
    `Stats/ResourceRegenUnitTests.cs` (`423579089`, lawn LW2.1),
    `Stats/TurnChannelDeclarationTests.cs` (`18139aec6`, battle T17). All 234 other `include` entries
    have left the residual (measured), so `Stats/**` is the only pattern still matching.
  - **Not a verification gap, checked rather than assumed.** A Stats production change plans
    `core-area-stats-owners`, whose group already contains `gk-core/tests/FusionRpg.Core.Tests` — so those four
    tests do run for a Stats change. The cost is that they run in the 609-file residual instead of the
    focused project, and that the manifest's declared policy is false on disk.
  - **Fixed here: the mechanism, not the four files.** `gk-core/tests/FusionRpg.FileMove.Tests/
    SplitManifestReconciliationTests.cs` (new) walks the real manifest and the real residual and asserts
    the divergences are exactly the four recorded, each with its adding commit — a debt register that
    fails on a **fifth** and fails when one is repaired (the `knownRed` self-expiry shape). Proven red on
    a planted fifth: `Failed: 1, Passed: 1` with the new path named; green on the real tree:
    `Failed: 0, Passed: 2, Total: 2`. A1's prose now carries the same declaration.
  - **Blocker, named exactly: a ruling on A1's directory rule.** Moving the four files needs the split
    gate (the brief forbids bypassing it), and the gate refuses a target whose directory exists. The
    change is contained — the planner would skip `CreateDirectory`/`CreateFile` for a project whose
    csproj already exists (so `Revert`, which deletes only what this run created, cannot destroy the
    existing project), and A1 would allow a target whose patterns still match — but it **overturns a rule
    an existing test asserts**, so it is the manager's call, not this lane's.
  - Owner: this program (`gk-core/tools/FileMove/**`, `gk-core/tests/FusionRpg.FileMove.Tests/**` and the spec are all in
    its fence). Evidence: `tasks/evidence-fragments/tvb-f30.md`.

- [ ] **TVB-F31 — `convergence-census.py --program` can never match, so the one instrument the manager
  points a lane at for a per-program reading always exits 2** · XS · *(found 2026-09-23 by lane `tvb60`
  while following this lane's brief, which names that script as the t1 contract's instrument and says to
  run it rather than trust the number)*
  `--program <name>` prints `no such program: <name>` and exits 2 **for every spelling** — measured with
  `item`, `test-verification-boundary` and `item-todo`. Cause read from the code:
  `.claude/cmdc-agents/scripts/convergence-census.py:137` sets `r["program"]` to the file's basename with
  `-todo.md` **already stripped**, while `:162` builds `want` by **appending** `-todo` to the argument, so
  `:164`'s `r["program"] == want` is unsatisfiable. The fix is one line — compare against
  `args.program` (accepting either the bare or the `-todo` spelling) — but the file is the manager's
  tooling.
  - **Owner: no program owns it.** `.claude/cmdc-agents/**` is outside every `tasks/<program>-todo.md`'s
    fence and outside this lane's, so this row is filed here and the manager routes it (the same shape as
    the runner-owned `tasks/run-board-20260920.md` row below).
  - **Why it mattered:** the brief's own count for this program ("43 open task blocks at the 2026-09-23
    reading") cannot be reproduced through the flag the brief names. The table form does work, and at this
    head it reads `test-verification-boundary   12 blocks   0 wip   1 residue`.
  - Evidence: `tasks/evidence-fragments/tvb60-lane-close.md`.

- [ ] **TVB-F32 — a `tasks/**` docs edit plans the whole 673-test Guard project, and almost none of it can
  see the edit** · S · *(found 2026-09-23 by lane `tvb60` when its own two-file docs commit's `verify-change`
  ran `Total: 673, Duration: 9 m 38 s`)*
  `session-and-program-records` owns `tasks/**` with `project: guard` and no selector, so **every** todo
  tick, ledger line or evidence fragment a lane commits plans the entire Guard project
  (`gk-core/scripts/verification-boundaries.v1.json:3346`). Measured cost for a two-file docs change: `Failed: 1,
  Passed: 672, Skipped: 0, Total: 673, Duration: 9 m 38 s`. Measured coupling: of **114** Guard test
  files, **5** mention `tasks/` at all, four of those only in doc-comments; the single real dependency is
  `RepoBoundaryGuardTests.cs:13,114,115` (B3 freezes `tasks/plan.md` + `tasks/todo.md`, both frozen
  history), and `grep -rn "tasks/sessions" gk-core/tests/FusionRpg.Guard.Tests/*.cs` is **0** — no Guard test reads
  a session record. The B3 contract is already guarded by the `repo-boundary` CI-tier guard
  (`run-guards.ps1 -Tier ci` table: `repo-boundary ci gating 0 2.30`), so the `test: guard` leg re-proves
  it rather than being the only witness.
  - **Second cost, the same one this program's TVB-F3 row names:** the Guard suite carries load-fragile
    reds (`TVB-F2`/`TVB-F13`/`TVB-F4`), so a docs-only edit can go red for a reason it cannot have caused.
    A gate that fails a green run trains callers to ignore it.
  - **Why it is a ruling, not this lane's edit.** The registry has no `filter` field at all, and `testFiles`
    is the *pytest* selector (`scripts/lib/VerificationBoundaries.ps1:235` derives `focused` from
    `verificationId` / `testFiles` / `selfSelect`), so for a dotnet `guard` project the only narrowing is a
    `verificationId` trait — which lives in `gk-core/tests/FusionRpg.Guard.Tests/**`, the project this lane's edits
    are refused on (the same refusal as `TVB-F26`). Re-labelling the boundary `focused` also overturns an
    asserted label: TVB2.1's acceptance pins `session-and-program-records → module`
    (`tasks/test-verification-boundary-todo.md:104`, checked by `VerificationBoundaryWorkflowTests`). The
    remaining shapes (split `tasks/sessions/**` + `tasks/**-ledger.jsonl` from the docs half, or accept the
    cost) each drop or keep a test leg deliberately — a coverage decision this lane will not make on its own
    reading, exactly as `TVB-F28` says of the Contracts boundary.
  - **Candidate shapes for the ruling:** (a) a `verificationId` trait on the tasks-coupled Guard tests +
    `level: focused` (needs `gk-core/tests/FusionRpg.Guard.Tests/**` and overturns an asserted label); (b) split the
    boundary so `tasks/**` docs select `doc-citations` + `session-boundary` only (registry-only, but removes
    the `tasks/plan.md`/`tasks/todo.md` test leg); (c) leave it and accept ~10 min per docs commit.
  - **Second reading, 2026-09-23 (lane `tvb60`), and it makes the cost an exit code, not just minutes:**
    `pwsh -NoProfile -File scripts/verify-change.ps1 -Session tvb58 -Paths
    tasks/test-verification-boundary-todo.md tasks/evidence-fragments/tvb-f33-seam.md` planned
    `test: guard` (the whole project) and printed `Failed! - Failed: 1, Passed: 672, Skipped: 0,
    Total: 673` in `9 m 16 s`, **exit 1**. The one red is pre-existing and not this lane's:
    `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary`
    (`gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs:121-122`), red because
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:305` returns a tenth code `picks.source-below-rank-floor`
    (`22fc4f3d3`, creature-seed T8). So at this head **a two-file docs-only change cannot pass
    `verify-change` at all** — not merely slowly. The red is already filed with `file:line`, owner and a
    pending manager ruling in `tasks/reports/findings-2-head-guard-reds.md`, and the guard's own comment at
    `PlayerSpeciesMaterialiseCallerGuardTests.cs:91-92` says a tenth code "is a reviewed change that should
    fail this test and be re-read", so no duplicate row is filed here; the code and its landing are
    recorded at `tasks/creature-seed-todo.md:121`.
  - Owner: this program (`gk-core/scripts/verification-boundaries.v1.json` is in its fence; the trait half is not).
    Evidence: `tasks/evidence-fragments/tvb-f32.md`.

- [ ] **TVB-F33 — `guard.unique-allocation-reader` is a dead trait: the guard it names never runs for the
  files its own allowlist polices** · S · *(found 2026-09-23 by lane `tvb60` reading the `-Report` orphan
  table while correcting the map's §2 numbers)*
  `gk-core/tests/FusionRpg.Guard.Tests/UniqueAllocationReaderGuardTests.cs:14` declares
  `[Trait("VerificationId", "guard.unique-allocation-reader")]` (added by `03bdd5cc7`, empire-progression
  EP1.14, 2026-09-20) and `gk-core/scripts/verification-boundaries.v1.json` names that trait **0** times, so the
  trait selects nothing. Measured consequence: `verify-change -PlanOnly` on the two files the test's own
  allowlist names (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AllocationRespec.cs`) plans `data-fallback (module)` + `guard: dal` +
  `guard: test-substrate` + `test: data (sharded runner)` — **not** the Guard project. A change that adds a
  direct `LoadAllocation` reader in a mapped file is locally green and red only in CI's Guard step: the
  `TVB-F24` shape.
  - **Not covered by K3 (`TVB6.4`, ticked).** K3 scoped itself to orphan **`core.*`** traits and to "a
    production file whose change the trait's tests are the direct proof of"; this trait is `guard.*`, and
    its test scans all of `src/` rather than pinning one file.
- [x] **TVB-F33 — `guard.unique-allocation-reader` is a dead trait: the guard it names never runs for the
  files its own allowlist polices** · S · *(found 2026-09-23 by lane `tvb60` reading the `-Report` orphan
  table while correcting the map's §2 numbers)* — **FIXED 2026-09-23 (lane `tvb60`), by the same
  mechanism discovery as `TVB-F28`.** The row's own shape (a) — "let a seam carry a `verificationId`" —
  is **already available and needs no pipeline edit**: `verify-change.ps1:112` filters the ambiguity check
  to `kind -eq 'owner'`, its seam loop (`:119-121`) builds a focused `test` check straight from
  `$entry.verificationId`, and `guard-verification-boundaries.py:151-161` accepts a `verificationId` on
  **any** boundary kind (validating the regex and that the trait exists in the project's members). The
  previous revision of this row's blocker said the additive mechanism was whole-project only because
  **0 of 30 seams happened to carry one** — a reading, not a rule. Landed: seam
  `unique-allocation-reader-seam` (`gk-core/scripts/verification-boundaries.v1.json:6080-6090`, `kind: seam`,
  `paths: ["src/**"]`, `project: guard`, `verificationId: guard.unique-allocation-reader`, `level: seam`,
  appended last so no existing registry line shifts).
  `src/**` is the scope the test itself polices — `UniqueAllocationReaderGuardTests.cs:31` enumerates every
  `*.cs` under `src/`, not one file — so a narrower seam would close this row's instance and leave its
  class ("local green, CI red") open.
  - Measured: the trait selects `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2` in `173 ms`, whole
    `dotnet test` command `17.7 s` wall warm — against the 673-test project the old reading priced.
    `verify-change -PlanOnly` now prints the seam for **all three** allowlisted files
    (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`, `.../RpgStore.AllocationRespec.cs`,
    `gk-core/src/FusionRpg.Server/DerivedAuditActor.cs`) **and** for a plain Core path
    (`src/FusionRpg.Core/Items/ItemGrant.cs`), each beside its own owner and with
    `test: guard guard.unique-allocation-reader` in the checks. `guard-verification-boundaries.py` →
    `VERIFICATION BOUNDARY GUARD OK`.
  - **Residual, recorded rather than implied:** the seam adds `17.7 s` to every `src/**` edit in the repo,
    which is the cost class `TVB-F32` is about. That was taken deliberately: the alternative scopes either
    leave the class open or (per the row's own shape (c)) trade away the `Data.Tests` run.
  - Owner: **empire-progression** owns the trait (`EP1.14`); the boundary surface is this program's. Filed
    here because `tasks/empire-progression-todo.md` is outside this lane's fence, so the manager routes it.
  - Evidence: `tasks/evidence-fragments/tvb-f33.md`,
    `tasks/evidence-fragments/tvb-f33-seam.md`.

- [x] **TVB-F34 — 11 of the 33 resolvable `verification-boundaries.v1.json:<N>` citations are stale by
  hundreds of lines, and the doc-citation guard cannot see intra-file drift** · S · *(found 2026-09-23 by
  lane `tvb60` while checking whether appending a boundary row would move any citation — it did not, but
  the citations were already moved)*
  `scripts/audit-doc-citations.py`'s only line check is D2 — `int(cited_line) > total` (`:353`) — so a
  citation whose line number is still inside the file but no longer holds the thing it names passes
  silently. Measured by resolving each citation's nearest preceding backticked id to that id's real line:
  of **33** citations into the registry, **11 are stale** and 22 name no boundary id at all. Examples:
  `docs/architecture/ip-censor-map.md:82` cites `:863` for `tuning-publish-tool` (real line **2520**);
  `docs/architecture/test-verification-boundary-map.md:82` cites `:783` for `magic-number-audit` (real
  **2496**); `docs/architecture/test-verification-boundary/spec-registry-contract.md:129` cites `:124` for
  `core-fallback` (real **797**); `tasks/test-verification-boundary-todo.md:364` cites `:1217` for
  `seedsmith-tests` (real **2580**). This is **TVB-F7's class one tree over** — TVB-F7 is the
  `decisions.md:<N>` band; this is the registry.
  - Cause read: the registry is append-mostly, so every boundary this program added shifted every citation
    after it, and nothing gates the shift — `guard-doc-citations.ps1` is exit 0 in plain and `-Strict`
    over 1689 documents / 25809 citations, so the drift is invisible to CI. Not a counting artefact of the
    checker: the four examples above are off by 1697, 1713, 673 and 1363 lines.
  - **Owner:** this program for the registry half (the file is its subject) and for the citing docs under
    `docs/architecture/test-verification-boundary*`; the other citing files —
    `docs/architecture/ip-censor-map.md`, `docs/architecture/empire-seed/*`,
    `docs/architecture/rift-gate/*`, `docs/research/*`, `tasks/ip-censor*`, `tasks/rift-gate-plan.md`,
    `tasks/npc-story-events-plan.md`, `tasks/reports/creature-seed-rank-t1.md` — are outside this lane's
    fence, so those lanes re-anchor their own. The durable fix is a D5 rule in
    `scripts/audit-doc-citations.py` that resolves a cited line for a JSON registry citation against the
    boundary id named in the same sentence — a scripts-plane edit, i.e. the **TVB-F3ep** blocked class.
  - **In-fence inventory, measured 2026-09-23 (lane `tvb60`) — the half this lane can reach.** 21 registry
    citations live in this program's own files. Resolved against the current registry, **10 are stale and
    re-anchorable because the sentence names the boundary**: `-ideal.md:39` `:356`→**1724**, `:370`→**1738**
    (`data-item-socket` / `data-item-socket-test`); `-map.md:70` (G3) `:32-48`→**593**
    (`battle-effect-math`), `:1043`→**3346** (`session-and-program-records`), `:549`→**1951**
    (`effect-catalog-drift`); `-map.md:82` (G15) `:783`→**2485** (`magic-number-audit`), `:796`→**2509**
    (`tuning-publish-tool`); `spec-registry-contract.md:109` `:783`→**2485**; `spec-registry-contract.md:129`
    `:124`→**786** (`core-fallback`); `spec-seam-coverage.md:65` `:809`→**2928**
    (`deployment-hierarchy-tuning`); `spec-seam-coverage.md:77` `:727`→**2313**, `:809`→**2928**,
    `:835`→**2987**; `spec-data-tests-sharding.md:20` `:299`→**1667** (`data-fallback`);
    `spec-python-test-lane.md:18` `:796-807`→**2509**; `todo.md:370` `:1217-1225`→**2569**
    (`seedsmith-tests`); `todo.md:1304` `:679`→**786**; `todo.md:1349` `:3325`→**3323**
    (`pipeline-audit-scripts`). Already correct: `todo.md:363`/`:563` `:192`
    (`projects["web-fusion-rpg-web"]`), `todo.md:563` `:5775`, `todo.md:1349` `:183`
    (`projects["tools-audit-tests"]`), `todo.md:1428` `:3346`. One is a judgement call, not a
    re-anchor: `-map.md:57`'s "(e.g. `:299`, `:707`)" now names no `data-*`/`server-*`/`launcher-*` entry
    at either line, so its two examples must be re-chosen, not re-pointed.
  - **Two sub-classes the D5 rule must also handle, or a re-anchor will look complete and not be.**
    (i) **Shorthand `:N`** — a bare `` `:796` `` after the filename appears once per sentence, so 49 more
    `` `:N` `` forms sit in this program's own docs and only some point at the registry (`-map.md:58`'s
    `:32`, `:561`, `:134` are registry boundary lines; `spec-python-test-lane.md:37`'s `:38` is
    `guard-verification-boundaries.py`). (ii) **Historical statements that cannot be re-anchored** —
    `spec-registry-contract.md:147`'s "the Core split moves six such test paths (`:39-40`, `:103`, `:116`,
    `:150`, `:565`)" describes the *pre-split* registry: those six exact paths were rewritten by
    `core-split-wiring` (C8) and no longer exist, so the honest fix there is to mark the citation
    historical, not to re-point it.
  - **Ordering, so the work is not redone:** re-anchor **after** the D5 rule lands, not before. The
    registry is append-mostly and this program adds boundaries constantly — this lane's own two seams would
    have shifted every citation after them had they been inserted mid-file — so re-anchoring without the
    rule only resets the rot clock. The rule is the blocker; the inventory above is the work order.
  - **RESOLVED 2026-09-23 (lane `tvb60`) — the rule landed, then the re-anchor, then the form the rule
    could not yet see.** The blocker above was wrong about the file, and that is the finding worth
    carrying: `scripts/audit-doc-citations.py` is **not** a protected pipeline file.
    `guard-doc-citations.ps1` is the guard (blocked); the Python checker it shells out to is an ordinary
    script, and this lane edited it without a refusal. The row had classified it as "the **TVB-F3ep**
    scripts-plane blocked class" by analogy, without testing the constraint. **The other two claims of
    that class were tested and stand** — `scripts/verify-change.ps1` and `gk-core/tests/FusionRpg.Guard.Tests/**`
    both refuse an edit — so `TVB-F3ep`, `TVB-F6ep`, `TVB-F24`, `TVB-F26` and `TVB-F32` keep theirs.
  - **D5, as landed.** A registry line citation resolves against the registry's own entry map (every
    boundary `id`, every `projects` key), read from the file: each entry carries its **object extent**,
    and a cited span resolves when it overlaps that extent — not only when it lands on the `"id"` line,
    because these sentences legitimately cite a boundary's `paths` array (`:3325` for the object whose
    `"id"` is on `:3323`) or its opening brace (`:679` for `:680`). The entry must be **named as a code
    token** — backticked, or the `projects["x"]` form — and that is load-bearing, not decoration:
    `data`, `core` and `server` are `projects` keys *and* ordinary words these docs use constantly, and
    a bare-word scan blamed two citations for naming `data`. The sentence window is the citation's own
    line plus up to 3 lines back. When the line cites as many spans as it names entries the pairing is
    **positional** (`a` `:32-48`, `b` `:1043`, `c` `:549`), which is what keeps a shorthand span from
    being blamed on the wrong entry; when the counts differ the line is reported only if **no** named
    entry's extent meets **any** of its spans, so a mis-attributed note is never produced. **Both
    citation forms are handled** — the full `verification-boundaries.v1.json:<N>` **and** the bare
    `` `:N` `` shorthand, the sub-class (i) this row named. The shorthand is recognised only as a
    backticked `` `:N` `` after the registry filename is named on the line, which is what keeps the
    `:67` of `guard-verification-boundaries.py:67` and the `:68` of `ci.yml:68` from being read as
    registry lines.
  - **Severity LOW, deliberately, and the reason is the audit's own doctrine.** `--strict` gates on HIGH.
    D2 is HIGH because the cited line cannot be opened at all; a stale D5 line opens and merely shows the
    wrong entry — the "a stale positive merely misleads" case the module docstring already names. Making
    it HIGH today would turn a repo-wide green into a repo-wide red over citations in other programs'
    fences (10 of them, below), which is the same trap `TVB-F5ep` describes. **Promotion to HIGH is the
    closing step**, and it is a one-line change in this lane's own fence.
  - **Measured** (`python scripts/audit-doc-citations.py --scope docs/` and `--scope tasks/`): D5
    **20 → 10** repo-wide. The shorthand half is the difference the row predicted: it found **12 more
    stale citations** the full-form-only rule could not see, 2 of them this program's (both re-anchored
    by the same rule now), and requiring a code token removed 2 bare-word false positives. In this
    program's own files, **20 of the 29 entry
    citations were stale and are re-anchored to 0 stale** — `-ideal.md:39` `:356`/`:370`→**1724**/**1738**;
    `-map.md:57` `:299`/`:707`→**1667**/**2248** (re-chosen, not re-pointed: the old pair named no
    `data-*`/`launcher-*` entry); `-map.md:70` `:32-48`/`:1043`/`:549`→**592-610**/**3345-3356**/**1950-1961**;
    `-map.md:82` `:783`/`:796`→**2485**/**2509**; `spec-core-registry-rekey.md:54` `:32-48`→**592-610**;
    `spec-data-tests-sharding.md:20` `:299`→**1667**; `spec-python-test-lane.md:18` `:796-807`→**2508-2523**;
    `spec-registry-contract.md:109` `:783`→**2485**, `:129` `:124`→**786**;
    `spec-seam-coverage.md:65` `:809`/`:727`→**2928**/**2313**, `:77` `:727`/`:809`/`:835`→**2313**/**2928**/**2987**;
    `todo.md:370` `:1217-1225`→**2568-2578**. The row's own two examples were themselves 11 lines off
    (`:2496`/`:2520`); re-measured, the `"id"` lines are **2485** and **2509**.
  - **One class cannot be re-pointed, only declared historical — and the file already had the mechanism.**
    `spec-registry-contract.md`'s C8 sentence ("the Core split moves six such test paths") describes the
    **pre-split** registry; those six exact paths were rewritten in place by `core-split-wiring` (C8), so
    re-pointing would manufacture false precision. The section now carries the audit's own
    `<!-- citations-historical: … -->` marker, so the five citations read as history and D5 skips them.
  - **Two citations left as they are, each with its reason** (not silently): `todo.md:1304`'s `:679` is
    the opening brace of the `contracts-fallback` boundary whose `"id"` is on `:680` and whose `project`
    is the `core` the sentence asserts — inside that boundary's object extent, so the rule accepts it;
    `spec-python-test-lane.md:12`'s `:3-15` is a citation to the registry **as a file** ("checked as a
    file at"), and lines 3-15 still hold the `projects` header. `todo.md:1349`'s `:3325` needed no
    judgement after all: it lands inside the `pipeline-audit-scripts` object, which is exactly what the
    sentence ("uses to own `gk-core/scripts/audit-program-pipeline.py`") asserts.
  - **Residual — 10 citations in 8 files, all outside this lane's fence**, each read and resolved above,
    filed here because `tasks/<other-program>-todo.md` is not a path this lane may write: `empire-seed`
    owns four in three files (`docs/architecture/empire-seed/spec-band-reader.md:228`,
    `spec-legion-bands.md:196` ×2, `spec-structure-bands.md:302`, all citing `:132-141`/`:179-188`/`:491`
    for `core-fallback`/`core-tests-fallback`/`data-tests-fallback`, real objects **785-794**/**832-841**);
    `ip-censor` owns four (`docs/architecture/ip-censor-map.md:82` `:863`→**2508-2523**,
    `docs/research/ip-censor-spec-audit-2026-09-19.md:38` `:863-873`→**2508-2523**,
    `tasks/ip-censor-plan.md:397` `:68` and `:523` `:68-71`/`:72-76`→**168-172** (`seedsmith`),
    `tasks/ip-censor-todo.md:490` `:68-76`→**253-257** (`ipcensor`)); `npc-story-events` owns
    `tasks/npc-story-events-plan.md:688` (`:2830`/`:2852`→**3761-3770**/`notify-contracts`);
    `creature-seed` owns `tasks/reports/creature-seed-rank-t1.md:25` (`:3427-3433`→**4238-4247**).
    Re-anchoring these is the whole of the promotion gate.
  - **Verified:** `guard-doc-citations.ps1` exit **0** (plain and `--strict`; D5 6 in the default
    `docs/` scope, 0 HIGH), `guard-verification-boundaries.py` → `VERIFICATION BOUNDARY GUARD OK`,
    `run-guards.ps1 -Tier ci` → `GUARDS OK - 25 guard(s) run, 0 red`.
  - Evidence: `tasks/evidence-fragments/tvb-f34-d5-rule.md`.

- [x] **TVB-F35 — `audit-doc-citations.py --scope .` audited the dot-directories, not the repository,
  and `--scope ./` audited nothing at all and exited 0** · XS · *(found 2026-09-23 by lane `tvb60`
  while producing TVB-F34's own before/after readings)* — the scope filter is
  `docs = [p for p in tracked if p.startswith(scope)]`, so `.` is a **string prefix**, not a path:
  `--scope .` matched the 664 documents under `.agents/`, `.claude/`, `.github/` and printed a
  plausible verdict for the rest of the tree, while `--scope ./` matched **0** documents and exited
  **0** — the "a run that proves nothing while printing a verdict" shape this repo already filed once
  (`TVB-F27`). It mattered here: a reviewer checking TVB-F34 with `--scope ./` would have read
  `0 documents, 0 D5` as "the registry citations are clean".
  - **FIXED in this lane.** `.` and `./` now mean the repository root (they normalise to the empty
    prefix), and a `--strict` run that matched **0** documents refuses instead of passing: it prints
    `scope '<x>' matched 0 documents: nothing was audited, so nothing is proven.` and exits **1**.
    Plain runs still exit 0 on a 0-document scope, because a scope naming a non-`.md` file legitimately
    has no documents to audit.
  - Readings: `--scope .` **664 → 3576** documents / 510 → 52,060 citations; `--scope ./` **0 → 3576**;
    `--scope ./ --strict` exits 1 (the whole tree carries 458 HIGH D1, `tasks/**` included — the
    `docs/`-only guard is what keeps CI green, and that is `TVB-F6ep`'s subject, not this row's);
    `--strict --scope scripts/audit-doc-citations.py` (a non-document) now exits 1 with the message,
    where it silently passed before. No caller is affected: every documented caller passes a file or a
    directory (`guard-doc-citations.ps1` uses the default `docs/`, `verify-change.ps1:216` only plans
    this check for `.md` paths).
  - Verified: audit tests `23 passed`, the C# audit harness `Passed! 5/5`,
    `guard-doc-citations.ps1` exit 0, `run-guards.ps1 -Tier ci` `25 guard(s) run, 0 red`.
  - Evidence: `tasks/evidence-fragments/tvb-f35-scope.md`.

- [ ] **TVB-F36 — the H-checkbox-heading classifier reports checked task headings as open** · XS · deps: — · *(manager, 2026-09-25, from the current TVB-F20 census)* — `tasks/derived-stats-todo.md` contains 28 checked `### - [x]` headings and zero unchecked headings, but the `H-checkbox-heading` classifier reports 27 open / 1 done. This makes the reproducible task-block census overstate open work and is a ledger-integrity defect, not an implementation queue.
  - **Remedy:** repair the shape classifier/fixture so checked checkbox headings are classified as done, add a regression fixture that proves the rule, and rerun `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`. Do not edit `derived-stats` content or suppress the file with a population override.
  - **Verify:** focused audit-program-pipeline tests, the exact census command, `git diff --check`, and a clean session boundary. The manager must not publish an adjusted genuine-work count until this row is resolved and the contradictory ledgers are separately reconciled.
  - **Owner:** test-verification-boundary / manager pipeline plane; this row is intentionally outside the four implementation lanes below.

- [x] **TVB-F37 — the worktree-cleanup tool's runner discovery is blind to the OpenCode/cmdc lane owners (fail-open)** · S · deps: — · *(manager, 2026-09-25; found by six independent adversarial audit lanes, reproduced in `tasks/reports/worktree-cleanup-runner-evidence-gap-20260925.md`)* — `gk-core/scripts/worktree_cleanup_core.py:_runner_evidence` (the adopted copy on branch `adopt/worktree-cleanup-20260925`, commit `6d2c48460`) opens only `.kilo/agent-manager.json` and returns an empty list when it is absent. The active OpenCode runner records lane ownership at `.claude/opencode-agents/agents/<lane>/meta.json` (`cwd`, `branch`, `base`, lifecycle), and cmdc lanes at `.claude/cmdc-agents/agents/<lane>/...`, so a worktree whose tracked session record is stale can be classified `should-clean` while a live lane still owns its path. This is the destructive boundary, so it must fail **closed**.
  - **Remedy:** extend runner discovery to enumerate `.claude/opencode-agents/agents/*/meta.json` AND `.claude/cmdc-agents/agents/*/` (read-only), treating any live/owned record as a runner owner forcing `manual-review`; keep the existing `.kilo/agent-manager.json` path. Add a deterministic temporary-repository test proving each owner style forces `manual-review` (the current 10 tests create no such record, which is why the defect survived them). Do not run the tool against any live worktree as part of this row.
  - **Verify:** `python -m unittest gk-core/scripts/test_worktree_cleanup.py -v` (with the new cases), the focused `inspect-worktrees` suite, and a clean session boundary. The adopted branch must be reviewed at its exact SHA and merged by the manager; until then the tool stays uncommitted on integration and must not be invoked.
  - **Owner:** multi-agent-runners / manager pipeline plane.

- [x] **TVB-F39 — one build environment cannot compile `FusionRpg.slnx`: the two MelonLoader hosts share ONE pack variable, and the three hosts share ONE profile variable** · S · deps: — · *(manager, 2026-09-25; found running the merged-head gate at `d7fbf7d1d`)* — the solution contains `FusionRpg.Injector.BepInEx`, `FusionRpg.Injector.MelonLoader` (legacy, `GameProfile` defaults `pvzrh-3.8.1`, reads `FUSIONRPG_ML_GAMEDIR`) and `FusionRpg.Injector.MelonLoader.39` (hardcodes `GameProfile=pvzrh-3.9`, also reads `FUSIONRPG_ML_GAMEDIR`). No single environment satisfies all three, proven in both directions at the current head:
  - `MelonLoader.39` + the 3.8.1 Blooms pack → **4× CS0266** (`Bridges/pvzrh-3.9/ZombieCombatFields.cs:13-14`, Int64 HP bridge against 3.8.1 Int32 interop);
  - legacy `MelonLoader` + the 3.9 pack → **2× CS1501** (`Bridges/pvzrh-3.8.1/CreateZombieSpawn.cs:11`, `SetZombie` 5-arg Blooms call against 4-arg 3.9 interop);
  - setting `FUSIONRPG_GAME_PROFILE=pvzrh-3.9` globally (the value the 3.9 pack needs) makes the **BepInEx** host compile the 3.9 bridge against 3.8.1 interop → **4× CS0266** again. Leaving it unset fixes BepInEx but re-breaks the legacy Melon host whenever `FUSIONRPG_ML_GAMEDIR` points at 3.9.
  **Impact:** `post_merge_check.py` (the merged-head gate) builds the solution, so it can never reach GREEN on a machine holding the three legal packs — it classifies the Melon errors as a non-interop project failure (`build: non-interop project errors: FusionRpg.Injector.MelonLoader.csproj`) and exits 1. This is what kept the terminal gate OPEN. CI never builds the solution (it runs per-project `dotnet test`), which is why the defect survived.
  **Not a new regression:** both hosts and the solution predate this program (`e4c6f1c77 init`); the gate simply exercised the matrix for the first time. All three packs exist on this machine, so the fix is expressible.
  **Remedy (shape, not prescription):** make the per-host pack/profile explicit instead of one shared var — e.g. a `FUSIONRPG_ML_GAMEDIR_38` (or resolve the pack per project from `game-profiles.json` fingerprints), and stop letting `FUSIONRPG_GAME_PROFILE` leak across hosts (the `MelonLoader.39` project already hardcodes its own). Whichever shape is chosen must keep `deploy-play.ps1` and `publish-player.ps1` working, and must be a step that GATES the change.
  **Verify:** from a clean checkout with the three legal packs pointed at, `dotnet build FusionRpg.slnx -c Debug` exits 0 with `Build succeeded` and 0 `: error ` lines; then `pwsh .claude/cmdc-agents/scripts/post_merge_check.py` at the new head reaches a terminal verdict (GREEN or a RED naming a real product failure — never the shared-env build error).
  **Owner:** test-verification-boundary / pipeline plane (the manager owns `FusionRpg.slnx` and the gate; `game-profiles.json` has no owning program).

- [ ] **TVB-F38 — the pre-existing `.commandcode/skills/**` doc-citation red (11 HIGH) needs its own lane** · XS · deps: — · *(manager, 2026-09-25; measured in `tasks/reports/resume-30-commandcode-config-review-20260925.md` §8)* — `python scripts/audit-doc-citations.py --scope .commandcode --strict` exits 1: 10 D1 (file does not exist) + 1 D3 (ambiguous basename), worst in `skills/demon-fix-unresolved/SKILL.md` (7) and `skills/html-design-implementation/SKILL.md` (3). None is in a `taste` file; the red predates the taste/settings disposition and is unrelated rot in a different subtree.
  - **Remedy:** re-anchor or remove the stale citations in those three files (docs-only, so `verify-change.ps1` selects the doc-citation gate), then confirm `--scope .commandcode --strict` exits 0.
  - **Verify:** the exact audit command above at exit 0, `git diff --check`, clean session boundary.
  - **Owner:** test-verification-boundary (`.commandcode/**/*.md` is inside its `docs-and-assistant-config` boundary).

---

## Blocked — the open rows, and exactly who unblocks each (2026-09-23, lane `tvb60`)

Every row below is **externally blocked**, not unfinished: each needs a path this lane may not write, a
ruling, or another program's edit. Nothing here is "needs investigation" — each names the file and the
change. The program's own in-fence work is done: Wave 0–6 are ticked, Checkpoint 6 is closed, and the
ledger queue is drained (`active: none`).

**Every blocker here that could be tested was re-tested, not assumed** (2026-09-23, lane `tvb60`):
`scripts/audit-doc-citations.py` was the one file this register had classified as protected *by analogy*
— it is not, and `TVB-F34` is resolved; `scripts/verify-change.ps1` and `gk-core/tests/FusionRpg.Guard.Tests/**`
both refuse an edit (`Blocked by the orchestrator pipeline guard: protected pipeline file`), so
`TVB-F3ep`/`TVB-F6ep`/`TVB-F24`/`TVB-F26`/`TVB-F32` keep theirs. The remaining rows name a path this
lane's fence does not hold, which is a fact about the fence and needs no test.

**This register is the accurate open-work surface; a raw `- [ ]` count is not.** Two sessions landed a
resolution as a *ticked duplicate row* under the original rather than ticking it in place, so the census
reads the original as still open. At this head that is **one** row — `TVB-F33`, whose `[x]` resolution
sits directly beneath its `[ ]` original — so the census's open-block count exceeds this table by 1.

| Row | What is left | Who unblocks it |
|---|---|---|
| `TVB5.9` + Checkpoint 5 line 3 | `-AllDefault green once`: **three** stale web fixtures (`gk-web/web/fusion-rpg-web/e2e/fixtures/commander-list.json:6`, `gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json`, `gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json:4`) — **re-read at the merged head `f585d8d6e`: `Failed: 3, Passed: 273, Total: 276` (2 m 18 s), all three being fixtures** (`RS-CF3`'s `RpgSimInProcHostTests` passed on that run) | `ip-censor` (the rename), `summoner-convergence` (SE4.31's `empireId`) and `world-stage` (W20), routed via the manager — or an erratum accepting the four-leg reading |
| `TVB-F25` | the same three fixtures, re-blessed | same three programs |
| `TVB-F26` | the Guard regression test for the new PATH warning (`gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs`) — the fix itself is landed in `scripts/run-guards.ps1` | a lane that may write `gk-core/tests/FusionRpg.Guard.Tests/**` (this lane's edit was refused by the pipeline guard), or a ruling that no test is owed |
| `TVB-F1` (×2, two blocks) | **the web half is DONE** (`web-fusion-rpg-web` boundary, `:192`/`:5775`); what is left is the `gk-core/data/tuning/*-catalog.v*.json` half | an **erratum ruling** on the tuning half only — a catch-all would make the `gk-core/data/tuning/**` enforced root vacuous, contradicting TVB-F8 |
| `TVB-F3ep` | a zero-test check after each `dotnet test` in `scripts/verify-change.ps1` (the one runner in this program that can silently run nothing) | a lane holding the **scripts plane** (pipeline-protected file) |
| `TVB-F6ep` | `verify-change.ps1` applies the `docs/` citation bar to `tasks/**`, the repo guard does not | scripts plane, or a ruling that `tasks/**` is exempt from that bar |
| `TVB-F24` | the enforced-root coverage walk is skipped locally, so a new file under `data/**`/`gk-core/tests/fixtures/**` gets a green `verify-change` and a red integration guard | scripts plane + the guard (both protected) |
| `TVB-F10` (second half) | keep a network-dependent pytest node out of `seedsmith-actions`' selection — needs a pytest-exclusion field | the guard schema (`guard-verification-boundaries.py`, protected) |
| `TVB-F5ep` | `decisions.md`'s `(:N)` citation form is unaudited, and two ADR rows truncate on an unescaped `|` | a lane holding `docs/architecture/decisions.md`; recognising the form in `audit-doc-citations.py` without that fix would only move the guard's red |
| `TVB-F7ep` (remainder) | 47 `decisions.md:<N>` occurrences under `docs/**`, 3 under `tasks/**`, 1 at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:200` (`:114` → `:133`, the same re-point this lane made in `gk-core/src/FusionRpg.Core/**`), 1 at `gk-web/web/fusion-rpg-web/src/stages/delve/graph/FightInPlace.tsx:9` | lanes holding those four fences |
| `TVB-F15` | **CLOSED at `f585d8d6e`** — `guard-doc-citations.ps1` is exit 0 with 0 HIGH on every class | nothing |
| `TVB-F?` | `tasks/run-board-20260920.md` fails its own doc-citation check — **re-read at `213291c01`: 10 HIGH** (9 D1 + 1 D3) on 86 resolvable citations, not 4 | a lane holding `tasks/` files outside this program's prefix (and the board is runner-owned) |
| `TVB-F28` | **the seam is landed and its selection proven** (shape (d): a `seam` on the owner's own paths is additive — `verify-change.ps1:112` filters the ambiguity check to `kind -eq 'owner'`); what is left is that the focused check it selects is red until the two stale web fixtures are re-blessed | `ip-censor` (`commander-list.json`) + `summoner-convergence` (`unique-actor.json`, SE4.31) — the same two as `TVB-F25` |
| `TVB-F30` | four residual `Stats/**` files are claimed by `FusionRpg.Core.Stats.Tests`'s manifest pattern and cannot be moved — A1 refuses a target whose directory exists, and `SplitManifestTests.The_target_project_directory_must_still_not_exist` pins that rule | a **ruling** on A1's directory rule; the reconciliation guard that catches a fifth divergence is landed (`SplitManifestReconciliationTests`) |
| `TVB-F31` | `convergence-census.py --program` always exits 2 (`:137` strips `-todo.md`, `:162` appends it), so a per-program reading needs the table form plus a hand grep | **no program owns it** — `.claude/cmdc-agents/**` is the manager's tooling; the manager routes it |
| `TVB-F32` | a `tasks/**` docs edit plans the whole 673-test Guard project (9 m 38 s for a two-file docs change) while only 1 of 114 Guard test files really depends on `tasks/` (`RepoBoundaryGuardTests` B3) and 0 read a session record | this program (`scripts/**` is in its fence) — the fix shape is a **ruling**: the only narrowing mechanism for a dotnet `guard` project is a `verificationId` trait in `gk-core/tests/FusionRpg.Guard.Tests/**` (refused for this lane, as `TVB-F26`), and re-labelling overturns `session-and-program-records → module` (`:104`) |
| Checkpoint M | the owner shown the TVB1.10 report and the manifest draft | the owner |
| `TVB-F34` | **the rule landed (both citation forms) and this program's citations are clean (20 → 0 stale); what is left is (a) 10 stale citations in 8 files outside this lane's fence — `empire-seed` ×3 files, `ip-censor` ×4, `npc-story-events` ×1, `creature-seed` ×1, each resolved with `file:line` in the row above — and (b) promoting D5 from LOW to HIGH once they land** | the four owning programs re-anchor, then this program promotes D5 (a one-line change in `scripts/audit-doc-citations.py`, which is **not** pipeline-protected — measured 2026-09-23) |

Two readings a reader should carry forward rather than re-derive: the default profile's four legs are
green except E2E's **three** fixtures (Data 1766/0, Server 826/0, Core group 68 projects / 15,836 tests /
0 failures — `tasks/evidence-fragments/tvb5-9.md`), and `guard-verification-boundaries.py` now runs in
**14.1 s** because `Resolve-Owner` is indexed (`tasks/evidence-fragments/tvb-f3-f7.md`; re-read at
`213291c01` standalone as 29.5 s under a loaded machine — the indexed walk is the reading that matters).
A third reading belongs here because the register above predates it: at `213291c01` `run-guards.ps1 -Tier ci`
prints **0 red** (`doc-citations` included — `RS-F18` was closed by `7464bf590`), and
`guard-doc-citations.ps1` is exit 0 in both its plain and `-Strict` forms over 1689 documents / 25809
citations. The `tasks/**` citation bar this program's rows argued about is therefore the *only* place
the board's 10 HIGH can be seen.

The E2E leg was re-read on its own at `a6e84755a` (2026-09-23, lane `tvb60`):
`scripts/test-fast.ps1 -Project gk-core/tests/FusionRpg.E2E.Tests` → `Failed: 3, Passed: 271, Skipped: 0,
Total: 274`, `2m14s`. Every failure is external to this program — the two web goldens (`ip-censor`,
`world-stage`) and `RS-CF3`'s `RpgSimInProcHostTests` load-dependent case. `TVB5.8.k`'s ledger entry is
`done` as of the same re-read, so `TVB5.9` has exactly **one** blocker left, not two.

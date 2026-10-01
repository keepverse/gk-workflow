# Adversarial audit — 2026-09-30

An independent attempt to **refute** the eight claims below. Every figure was re-measured from
disk; nothing is carried over from a comment, a filename, a doc, or a previous report. Where a
claim could not be reproduced, that is stated explicitly with what was obtained instead.

**Environment.** `dotnet` 10.0.303; gk-core at `1ecb5c78ef32c3a96d914a2f42ee734dec05d1be`;
source monorepo at `effc51d9b55f78aa7a5c47e14eef0e61b690e5eb`. All scratch artifacts live under
`%TEMP%\opencode\audit-20260930\` and nothing in any repository was modified. `--confirm-migration-start`
was never passed; `apply` was never run.

**Headline: 3 of 8 claims reproduced, 2 refuted, 3 could not be reproduced as stated.**
The two refutations (4 and 8) are load-bearing: both assert a property the code does not have.

---

## 1. Claim table

| # | Claim | Verdict | How measured |
|---|---|---|---|
| 1 | Guard suite = 134 failed / 586 passed / 720 total | **reproduced: 134 / 586 / 720** | TRX `ResultSummary/Counters` after deleting `bin`+`obj` and rebuilding |
| 2 | `KeepverseRoots` has 7 accessors, right repo in BOTH layouts | **reproduced: 7, correct in both** | Built both layouts in temp, called all 7 against real marker files |
| 3a | Each Bridge type declared exactly once workspace-wide | **reproduced: 1 each** | Regex over all 10 trees, plus a partial-declaration probe |
| 3b | Bodies byte-identical to pre-split except namespace | **reproduced: 1 line differs, the namespace** | `Compare-Object` per file + SHA256 |
| 3c | No `Compile Include` reaching another repo via `$(Gk*Root)` | **COULD NOT REPRODUCE — REFUTED** | Found 2 exact hits, in `gk-forge` and `gk-fusion` |
| 4 | DominanceBaseline + CreatureSpeciesImport are process-only; only CreatureCorpusDump breaks a clone | **COULD NOT REPRODUCE — REFUTED** | Standalone clone + workspace-shaped clone, tests actually run |
| 5 | Standalone clone fails with exactly 2 errors, both `CreatureCorpusDump` | **COULD NOT REPRODUCE** | MSBuild says **1**; and 6 test projects are **absent from the solution** |
| 6 | kvsplit stage reproduces the placement/residue/balance figures | **partially reproduced — placements, residue, balance all exact; the rules digest does not match** | Re-ran `stage`, read its `report.json` (a run artefact that does not exist in any repository, so the re-read is reproducible only by re-running `stage`) |
| 7 | No public repo's history contains derived content | **reproduced: 0 in all six** | `git rev-list --objects --all` × 6, with a positive control on `gk-data` |
| 8 | No test in gk-core may need gk-data | **COULD NOT REPRODUCE — REFUTED** | 184 files read a real pack path; 1470/1470 fail in a gk-data-less workspace |

### Detail

**Claim 1 — reproduced.** `bin/` and `obj/` were deleted first, so the "stale binary" hazard is
eliminated by construction rather than by a timestamp comparison. The rebuilt DLL is `18:54:08`;
newest real `.cs` is `18:31:55`.

```
dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj --nologo -v q --logger "trx;LogFileName=audit.trx"
```

Read from the TRX (copied to temp before anything else):

```
total=720 executed=720 passed=586 failed=134 error=0 timeout=0 aborted=0 inconclusive=0 notExecuted=0
distinct outcomes: Failed, Passed
UnitTestResult nodes: 720  (688 distinct methods — the rest are [Theory] rows)
```

53 of the 134 failures report a harness/exit code rather than an assertion; 42 of the 134 read a
path under `gk-core/` that another repository owns (see §3, finding F1).

**Claim 2 — reproduced.** A standalone probe program (`net6.0`, referencing the built
`FusionRpg.Core.dll`) constructed both layouts and called all seven accessors. Every accessor
resolved to a directory that exists, and each root reached a real marker file:

| | legacy | workspace |
|---|---|---|
| `Content()` | legacy root | `gk-data/packs/fusion` |
| `Core()` | legacy root | `gk-core` |
| `AuthoredContent()` | legacy root | `gk-content` |
| `Workspace()` | legacy root | workspace root |
| `Fusion()` | legacy root | `gk-fusion` |
| `Forge()` | legacy root | `gk-forge` |
| `Web()` | legacy root | `gk-web` |

Marker checks all `True` in both layouts: `Core()+data/tuning`, `Content()+data/seed`,
`AuthoredContent()+content/display/en.json`, `Fusion()+src/FusionRpg.Injector/Host/RpgHost.cs`,
`Forge()+tools/DominanceBaseline`, `Web()+web/fusion-rpg-web/src`, `Workspace()+docs`.

I could not refute it. The tests are not the only evidence here, and I did not rely on them.

**Claim 3a/3b — reproduced.** Each of the three types is declared exactly once
(`gk-core/src/FusionRpg.Bridge/{Hud/ActorHudCache.cs:28, Hud/ActorHudUniqueFlags.cs:6,
Stats/InjectorDerivedOverride.cs:9}`); no `partial` re-declarations. Non-vacuity: the same search
finds 64 / 19 / 39 total mention lines for the three names, so the search does read bodies.
Each body differs from its pre-split original by **exactly one line** — the `namespace`
(`FusionRpg.Injector.Hud` → `FusionRpg.Bridge.Hud`, and `…Injector.Stats` → `…Bridge.Stats`).

**Claim 5 — could not reproduce as stated.** Two problems.

First, the count. `dotnet build FusionRpg.slnx` on a bare clone reports `1 Error(s)`. The single
error appears on 2 log lines (build summary + failure summary), which is almost certainly how
"2 errors" was obtained — but MSBuild's own tally is **1**.

Second, and more seriously, the count is not the interesting number. See §3, finding F2: **six test
projects are not in `FusionRpg.slnx` at all**, so a solution-level build never compiles them. The
claim's own instruction — count per project — produces:

| project | standalone build | unique errors | MSB9008 (missing `$(GkForgeRoot)` ref) |
|---|---|--:|--:|
| FusionRpg.Core.Tests | **exit 1** | 1 (`CreatureCorpusDump`) | 1 |
| FusionRpg.Data.Tests | exit 0 | 0 | 1 (`CreatureSpeciesImport`) |
| FusionRpg.Guard.Tests | exit 0 | 0 | 1 (`DominanceBaseline`) |
| FusionRpg.CheatCore.Tests | exit 0 | 0 | 0 |
| FusionRpg.FileMove.Tests | exit 0 | 0 | 0 |
| FusionRpg.SquadHarness.Tests | exit 0 | 0 | 0 |
| FusionRpg.TestSplitAnalyzer.Tests | exit 0 | 0 | 0 |

So `FusionRpg.Core.Tests` is the only compile-breaking one, exactly as claimed; but two of the
others **build clean and still fail at runtime** (claim 4).

**Claim 6 — placements reproduced, digest does not match.** `stage` at the pinned import SHA
reproduces every count in the claim:

```
tracked 15020  dropped 482  unplaced 0  balanced True
  root 5108 · gk-core 3860 · gk-forge 791 · gk-web 1108 · gk-fusion 438
  gk-content 1 · gk-data 3232 · gk-tests 0 · gk-assets 0
residue 2494
  path-literal-moves 2100 · content-root-consumer 393 · content-in-public-repo 1
```

`tracked = placed + dropped + unplaced` holds: 14538 primary + 482 dropped + 0 unplaced = 15020.
(The `files[]` array holds 14563 entries; the 25 extras are `primary:false` root-owned files —
`.editorconfig`, `AGENTS.md`, `Directory.Build.props` and friends — so counting `len(files)` as
"placements" would overstate by 25.)

**The claimed rules digest does not reproduce.** The claim pins
`0fe37c774d299b735312c684fac46e6e782f5824ad67715984bd2309dde9638d`. The run produced
`6b9b3bfc77cae6df37b06f02a34d452443a1145f91fa268fe9a35132fdae5306`. `0fe37c77…` appears nowhere
in `tasks/keepverse-split-ledger.jsonl`; it does appear in three docs, and
`docs/gk-tests-topology-reconciliation.md:59-62` records it as the **pre-seal** digest whose
successor is `05e46df6…`. Neither matches the current `rules/`, whose eight commits are listed
below `bd11cc6`. So the digest in the claim is stale relative to the tree it is paired with — the
placements still match, which is itself the interesting part (they are digest-independent).

**Claim 7 — reproduced.** `git rev-list --objects --all`:

| repo | objects | `packs/fusion/data/` | `data/seed/` | `data/generated/` |
|---|--:|--:|--:|--:|
| gk-core | 5377 | 0 | 0 | 0 |
| gk-forge | 955 | 0 | 0 | 0 |
| gk-web | 1314 | 0 | 0 | 0 |
| gk-fusion | 771 | 0 | 0 | 0 |
| gk-workflow (root) | 5844 | 0 | 0 | 0 |
| gk-content | 14 | 0 | 0 | 0 |
| **gk-data** (control) | 3380 | **3365** | **2412** | **951** |

The control is the point: the identical pattern finds 3365 hits in `gk-data`, so the six zeros are
a property of those repositories, not of the search.

**Claim 8 — refuted, and the earlier "180" was also wrong.** See §2 and F3.

---

## 2. REFUTED claims

### R1 — Claim 4: "DominanceBaseline and CreatureSpeciesImport are run as processes and do not break a standalone clone"

**False for `CreatureSpeciesImport`.** Its `ProjectReference` is load-bearing at *runtime*, exactly
as the brief warned. `FusionRpg.Data.Tests.csproj:29` has a plain
`<ProjectReference Include="$(GkForgeRoot)tools\CreatureSpeciesImport\CreatureSpeciesImport.csproj" />`
— no `ReferenceOutputAssembly="false"` — and
`tests/FusionRpg.Data.Tests/CreatureSpeciesImportCliTests.cs:91-95` asserts the apphost exists
*beside the test dll* and fails by name if it does not.

Isolating the variable: I built a **workspace-shaped** clone (`gk-core` + the real `gk-data` and
`gk-content` junctioned in, `gk-forge` absent) so layout detection succeeds and content resolves.
The only variable left is the missing tool. Result:

```
CreatureSpeciesImport was not built beside the test dll
  (…\wsclone\gk-core\tests\FusionRpg.Data.Tests\bin\Debug\net8.0\);
  the test project's ProjectReference should have produced it
Failed: 2, Passed: 0   (CreatureSpeciesImportCliTests)
```

In the workspace the same directory contains `CreatureSpeciesImport.exe`; in the clone it contains
nothing. The test **builds clean and still fails** — so a green build is not evidence, as the
brief said.

**The `DominanceBaseline` half of the claim is also wrong, but for the opposite reason.**
`FusionRpg.Guard.Tests.csproj:31` *is* marked `ReferenceOutputAssembly="false"`, and the comment
claims build-order only. But `ClassSystemBaselineRegenTests` runs
`scripts/regen_class_system_baselines.py`, which launches `DominanceBaseline` and `CombatSim`. In
the clone all three of its tests fail. So the reference is load-bearing there too, and the comment
("No assembly is referenced", hence inert) does not describe the runtime dependency.

The correct classification is: **every** `$(GkForgeRoot)` reference in a gk-core test project is
load-bearing. Three put an apphost beside the test assembly (`CreatureSpeciesImport`,
`CreatureQualityReport`, `CreatureSpeciesGen` in `FusionRpg.Core.Tests:37,43`), one is
compile-coupled (`CreatureCorpusDump`), and the build-order ones hide a spawned-process dependency
inside a Python script.

### R2 — Claim 8: "No test in gk-core may need gk-data" (gk-core/AGENTS.md:15)

**The rule does not hold, and the count in circulation is wrong in both directions.**

Recount excluding comment lines: **184 files**, not 180. The naive comment-inclusive search returns
185; the single file where `KeepverseRoots.Content(` appears *only* in a comment is
`tests/FusionRpg.Guard.Tests/VerificationTopologyTests.cs`. So excluding comments moves 185 → 184,
not 180 → something. **Where 180 came from I could not reproduce**, and I will not guess: neither
185 nor 184 yields it.

Spread across **16 test projects** (Core.Tests 55, Data.Tests 39, Core.Items.Tests 34,
Server.Tests 22, Core.Atoms.Tests 10, E2E.Tests 9, and 10 more).

The decisive measurement is not the count. In a workspace with `gk-core` and `gk-content` but
**no `gk-data`**, `FusionRpg.Core.Items.Tests` reports **1470 failed / 0 passed / 1470 total**.
Because a `[ModuleInitializer]` throws, this is assembly-wide, not a subset. With `gk-data` present
but the pack **empty** (so detection succeeds and only content is missing), the same 1470/1470
failure appears, and the inner exception names a real pack file:

```
System.IO.DirectoryNotFoundException : Could not find a part of the path
  '…\gk-data\packs\fusion\data\seed\commanders\_registry\default-commanders.v1.json'.
```

That is a genuine content dependency inside
`tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs:135` — compiled into 5 assemblies
by `CoreTests.Shared.props:16-19` and by `Directory.Build.props:30`. gk-core's test suite cannot
run without private content, and `FusionRpg.Server.Tests`/`E2E.Tests` bootstraps
(`CommanderDirectoryTestBootstrap.cs:21-31`, `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs:53`) do the same.
The AGENTS.md rule is stated as fact and is not true.

### R3 — Claim 3c: "No file anywhere still contains a `Compile Include` reaching into another repository's source tree"

**False. Two hits, both live, both unconditional for every `*.Tests` project in those repos:**

```
gk-forge/Directory.Build.props:30  <Compile Include="$(GkCoreRoot)tests\Shared\KeepverseRoots.cs" …/>
gk-fusion/Directory.Build.props:30 <Compile Include="$(GkCoreRoot)tests\Shared\KeepverseRoots.cs" …/>
```

This is the same `Compile Include` that `src/FusionRpg.Bridge/FusionRpg.Bridge.csproj:11` records
as the defect it was created to eliminate ("12 CS2001 source file not found errors, measured").
The module removed the `$(GkFusionRoot)` instances and left the `$(GkCoreRoot)` ones. A clone of
`gk-forge` or `gk-fusion` without its `gk-core` sibling cannot build its test projects. Nothing
guards this: `guard-repo-boundary.py` mentions `Compile` only inside `re.compile`, and references
neither `GkCoreRoot` nor `KeepverseRoots`.

---

## 3. New findings

**F1 — 42 failing guard tests assert against files gk-core does not own. `path:line` evidence
from the TRX; the eight-site fix stopped at eight.**

`1103ba7` ("repoint eight host-path reads") is a real, well-reasoned commit, and its own message
records that two earlier bulk rewrites made things worse. But the remaining sites are still there:

| file:line | builds |
|---|---|
| `tests/FusionRpg.Guard.Tests/ZombieHpBridgeGuardTests.cs:13,43,72,89` | `Core()+src/FusionRpg.Injector` (gk-fusion) |
| `tests/FusionRpg.Guard.Tests/W11GuardCompletenessTests.cs:53` | `Core()+src/FusionRpg.Injector/GameCaptureHooks.cs` (gk-fusion) |
| `tests/FusionRpg.Guard.Tests/NotificationCatalogContractTests.cs:83` | `Core()+web/fusion-rpg-web/…/catalog.ts` (gk-web) |
| `tests/FusionRpg.Guard.Tests/RiftGateEmbedLeaveGuardTests.cs:30,58,80,93,129` | `Core()+web/fusion-rpg-web/…` (gk-web) |

Plus 20 more tests failing on `Core()+docs/…`, `Core()+scripts/…`, `Core()+.github/workflows/release.yml`,
`Core()+tasks/sessions`, `Core()+tools/LawnCombatObserver`, `Core()+tools/ItemSeedValidator` —
files owned by gk-workflow, gk-fusion and gk-forge respectively. Every one of the seven accessors
exists; these call sites simply do not use them. A single grep for
`Path.Combine(repoRoot, "src", "FusionRpg.Injector` / `"web", "fusion-rpg-web"` /
`"docs",` inside `tests/FusionRpg.Guard.Tests` finds them all — 5 and 6 sites respectively.

**F2 — Six test projects are absent from `FusionRpg.slnx`, and one of them is the guard suite
itself. This is the instrument failure the brief warned about, still live.**

```
tests\FusionRpg.CheatCore.Tests       tests\FusionRpg.FileMove.Tests
tests\FusionRpg.Core.Tests           tests\FusionRpg.Guard.Tests      ← 720 tests
tests\FusionRpg.Data.Tests           tests\FusionRpg.SquadHarness.Tests
       tests\FusionRpg.TestSplitAnalyzer.Tests
```

76 test projects on disk; 70 referenced by the solution; **69 produced a dll** after a full
solution build. A solution-wide `dotnet test` in a clean clone therefore cannot see 6 projects,
and 720 guard tests among them. `dotnet build` reporting `1 Error` is *consistent with* this: it
never tried to build the six.

**F3 — 184 gk-core test files read the private gk-data pack; the rule in AGENTS.md is false.**
Measured above (R2). Additional detail worth recording: the dependency is not confined to test
bodies. `ContractTuningTestBootstrap.cs:135,141,146,154` reads four pack registries inside a
`[ModuleInitializer]`, and `CoreTests.Shared.props:16-19` compiles that file into every project
that imports it. So the failure mode is total-assembly, and it is invisible until the content is
absent — which is exactly the situation public CI is supposed to be in.

**F4 — The rules digest paired with the reproduced placements is stale.**
`0fe37c77…` is the pre-seal digest per `docs/gk-tests-topology-reconciliation.md:59-62`; the
current `rules/` digests to `6b9b3bfc77ca…`. A reader who pairs the claim's digest with a fresh
`stage` run will get matching numbers and a non-matching digest, and has no way to tell from the
output which of the two is wrong.

**F5 — `guard-repo-boundary.py` cannot detect any of F1/R3.** It parses `<ProjectReference>`
elements only (`B1`), checks assembly names and `using` directives (`B2`), and diffs
`tasks/plan.md` / `tasks/todo.md` (`B3`). It has no notion of `Compile Include`, no notion of a
`$(Gk*Root)` property, and no notion of a source path crossing repositories. The ownership rule
that claims to be enforced has no mechanical check for either of its two observable failure modes.

**F6 — Instrument note, recorded because it nearly produced a false finding here.** My first
per-project build loop passed *relative* csproj paths while the shell's working directory was the
source monorepo, not the clone. It built `plant-vs-zombie-rise-of-summoner` and reported
`FusionRpg.Guard.Tests` with 113 `CS0234` errors — a spectacular and completely fictional result.
The corrected loop uses absolute paths. Any per-project figure in this document was taken from the
corrected run; the erroneous output was discarded, not reported.

---

## 4. Could not check, and why

- **Whether the 134 guard failures are "expected".** `docs/` has not migrated, so several failures
  are missing-documentation rather than defects. Distinguishing the two needs the pre-split
  `docs/` and a per-test baseline I was not given. I report the failures, not a verdict on them.
- **The intended correct state of the 184 gk-data-dependent tests.** I proved the dependency
  exists and violates the stated rule. Whether the fix is a fixture, a private CI job, or a rule
  amendment is a design decision, not an audit finding.
- **The 6 projects missing from `FusionRpg.slnx`: deliberate or not.** `docs/gk-tests-topology-reconciliation.md`
  shows the workspace has previously reasoned about a repo receiving zero placements, so exclusion
  may be intentional. I did not find a document that says so, and I did not run `apply` to test it.
- **Whether `gk-forge`/`gk-fusion` clones are expected to build standalone.** R3 is stated as a
  factual defect in the claim's own terms ("no `Compile Include` reaching into another repository's
  source tree"). Whether the standalone-clone requirement extends to those two repos is a
  question I could not settle from the artifacts.
- **kvsplit `apply`, residue remediation, and the ledger's own arithmetic.** `stage` only. No
  `--confirm-migration-start`, no `apply`, nothing written outside the temp tree.
- **A `gk-data`-less build of all 69 buildable projects.** R2 measures one project
  (`FusionRpg.Core.Items.Tests`, 1470 tests) because it fails completely; extrapolating a
  solution-wide figure from one project would be exactly the error this audit exists to catch.

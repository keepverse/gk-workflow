# Adversarial audit 2026-09-30b — the FusionRpg.Bridge module and its correction

Read-only audit. Nothing in any repository was edited; the only file written is this report.
Sub-agent brief: test whether the **retraction** recorded at
`tasks/keepverse-split-ledger.jsonl:135-136` is now true, and whether the correction introduced new problems.

## 0. What was measured, and against what

Both repositories were clean and at the named commits before and after the audit:

| Repo | HEAD | `git status --porcelain` before | after |
|---|---|---|---|
| `gk-core` | `f2db59f0e635b4e34b473d6e5d23c1c9c624f0d1` | 1 entry (`scripts/guard-power.py`, **another session** — see §5.7) | same 1 entry |
| `gk-fusion` | `18557ea` | 0 | 0 |
| `gk-workflow` (workspace root) | `9e1bf6a` | 0 | 0 |

Instrument rules applied, because this workspace has produced confident wrong answers before:

- **Exit code read on every external command.** Never a filtered error count alone.
- **Every `error <CODE>` counted**, not `error CS`.
- **Test counts read from TRX `<Counters>`,** never from console text.
- **Every zero backed by a known-answer probe** on the same instrument.
- Results counted from a **forced `-t:Rebuild`**, so no stale binary is possible.

Side effects outside the repository, disclosed: `dotnet build` of the four loader hosts wrote
`FusionRpg.Injector.dll` to `H:\Games\PVZ FUSION 3.8.1 FULL MOD TOOL\BepInEx\plugins\FusionRpg\`
(that is the host project's designed `OutputPath`, and it is what the first build does). Builds of
the three uncovered projects used `-p:OutputPath=<temp>`, so no game install other than the one the
project itself targets was written. All logs and scratch output went to
`C:\Users\NeneScarlet\AppData\Local\Temp\opencode\`.

---

## 1. Claim table

| # | Claim | Verdict | Exact command |
|---|---|---|---|
| 1 | `src/FusionRpg.Bridge` targets net6.0; `FusionRpg.Core` net6.0; gk-fusion's four loader hosts net6.0 | **reproduced** (all three) | `Get-ChildItem -Recurse -Filter *.csproj \| Select-String TargetFramework` in each repo |
| 2 | `dotnet build FusionRpg.slnx` exits 0 with **zero errors of any code** (CS, NU, MSB) | **reproduced, with a material qualification** — §3.1 | `$env:…=…; dotnet build FusionRpg.slnx -v:m` (3 cell vars in the same invocation) |
| 3 | `dotnet test FusionRpg.slnx` runs 230 tests in 3 projects, all passing | **reproduced: 4 + 60 + 166 = 230, 0 failed** | `dotnet test FusionRpg.slnx --logger trx`, then parse `TestRun/ResultSummary/Counters` |
| 4a | the three source files absent from gk-fusion | **reproduced** (0 files by that name anywhere in gk-fusion) | `Get-ChildItem gk-fusion -Recurse -Include ActorHudCache.cs,…` |
| 4b | each of the 3 types declared **exactly once** workspace-wide | **reproduced: 1, 1, 1** | `Select-String -Pattern "(class\|struct\|record\|interface\|enum)\s+$t\b"` over `*.cs` from the workspace root |
| 4c | no gk-fusion file declares `namespace FusionRpg.Bridge.Hud;` / `.Stats;` | **reproduced: 0** | `Select-String -Pattern '^\s*namespace\s+FusionRpg\.Bridge\.(Hud\|Stats)\b'` over gk-fusion `*.cs` |
| 4d | every gk-fusion reference resolves; no `FusionRpg.Injector.Hud.ActorHudCache`, no bare `Hud.ActorHudCache` | **reproduced: 0 / 0** | two `Select-String` passes; the bare form probed with 2 positive controls |
| 5 | gk-core: Core.Tests 9753/0, Workspace.Tests 20/0, `FusionRpg.slnx` 0 errors of any code | **reproduced: 9753/0, 20/0, 0 error lines of any code** — but "unaffected" is **REFUTED**, §3.2 | `dotnet build -t:Rebuild` then `dotnet test --no-build --logger trx`; solution via `dotnet build FusionRpg.slnx -v:m` |
| 6 | no cross-repo `<Compile Include="$(Gk…Root)…">` in any csproj/props/targets across 4 repos | **reproduced: 0 of 41 directives**, non-vacuous (130 root-var hits on other directives) | `Select-String -Pattern '<Compile\s+Include\s*="[^"]*\$\(Gk\w*Root\)'` |
| — | "three gk-core test projects" compiled the sources via `$(GkFusionRoot)` | **COULD NOT REPRODUCE — it was TWO projects / 6 directives.** §2.1 | `git grep -n GkFusionRoot b390247~1 -- '*.csproj' '*.props' '*.targets'` |
| — | "12 x CS2001 source file not found" before the move | **COULD NOT REPRODUCE** — 3 files × 2 projects = 6 items; I could not construct 12 from the tree. §2.1 | same, plus `git show b390247 --stat` |
| — | `FusionRpg.Injector.MelonLoader.40` (not in the solution) compiles | **REFUTED — it does not: exit 1, 8 × CS0234.** §3.3 | `dotnet build src\…MelonLoader.40.csproj -p:MlGameDir=H:\Games\PVZ-Fusion-4.0_MelonLoader` |
| — | `tests/FusionRpg.Injector.Tests` is a measured exclusion (exit 1) | **reproduced: exit 1**, 216 CS0103 / 1648 CS0246 / 2 CS0400 / 6 CS1061 | `dotnet build tests\FusionRpg.Injector.Tests\…csproj` |
| — | gk-fusion CI "runs the solution, 230 tests, all passing" | **REFUTED — the CI test step cannot run a test at all.** §3.4 | `python -c "yaml.safe_load(…ci.yml)"` then execute the emitted `run` string under `pwsh` |

---

## 2. Things the ledger states that do not reproduce

### 2.1 "Three gk-core test projects" / "12 x CS2001" — the count is two / six

Ledger row 111 (`bridge-module-b390247-0b1ef80-20260930`) and the `b390247` commit message both
say **three** gk-core test projects compile-linked the three moved sources. Measured at
`b390247~1`, the entire set is:

```
b390247~1:tests/FusionRpg.Core.Hud.Tests/FusionRpg.Core.Hud.Tests.csproj:13,14,15   (3 × Compile Include)
b390247~1:tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj:48,49,50          (3 × Compile Include)
```

Two projects, six directives. `FusionRpg.Core.Tests` is not a manifest entry at all — it is the
`"residual"` string in `gk-core/tests/core-test-projects.v1.json`, which is why the policy guard
only notices one of the two.

**COULD NOT REPRODUCE: 12 CS2001.** Six is what the tree supports. (MSBuild may report each missing
item once per inner build, so a doubled count is arithmetically reachable, but I did not measure
it and will not quote it.) The substance of the claim — that the source-link existed and is gone —
is correct; the figures are not.

Related unverified figure in the same commit message: *"Six other gk-core test projects reference
gk-forge tools and need the same triage."* Measured now: **5** projects, **7**
`ProjectReference` edges — `Core.Balance.Tests` (1), `Core.Tests` (4), `Data.Tests` (1),
`Guard.Tests` (1). The standalone-clone problem for gk-core was **narrowed, not solved**: 12
source-level CS2001 became 7 project-level edges into `$(GkForgeRoot)`.

---

## 3. New findings

### 3.1 The build gate covers ONE of the four loader hosts, and the two silent ones print a dll line anyway

This is the finding I would put first, because it is the retraction's own lesson one level down.

`FusionRpg.slnx` contains `Injector.BepInEx`, `Injector.MelonLoader`, `Injector.MelonLoader.39`,
`Launcher`, and three test projects. Building it with the three cell env vars set in one shell
invocation gives **exit 0, 0 errors** — and this log:

```
NOT COMPILED — skipping FusionRpg.Injector.MelonLoader.39. Cell pvzrh-3.9 x MelonLoader has no pack root: set FUSIONRPG_ML_GAMEDIR_PVZRH_3_9 …
NOT COMPILED — skipping FusionRpg.Injector.MelonLoader.   Cell pvzrh-3.8.1 x MelonLoader has no pack root: set FUSIONRPG_ML_GAMEDIR_PVZRH_3_8_1 …
FusionRpg.Injector.BepInEx -> H:\Games\PVZ FUSION 3.8.1 FULL MOD TOOL\BepInEx\plugins\FusionRpg\FusionRpg.Injector.dll
```

**Cause: the two MelonLoader cell roots named in the audit brief are BepInEx installs.**
`H:\Games\PVZ FUSION 3.8.1 FULL MOD TOOL` and `H:\Games\PVZ-Fusion-3.9` both contain
`BepInEx\`, `dotnet\`, `PlantsVsZombiesRH_Data\` — and **no `MelonLoader\` directory at all**
(`Test-Path '…\MelonLoader\net6\MelonLoader.dll'` → `False` for both). `HasMelonRefs`
(`gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj:20`) requires
`$(MlGameDir)\MelonLoader\net6\MelonLoader.dll` **and**
`$(MlGameDir)\MelonLoader\Il2CppAssemblies\Assembly-CSharp.dll`, so the env var resolves and the
cell still refuses.

Real packs exist and the recipe does not name them:

| pack | `MelonLoader\net6\MelonLoader.dll` | serves cell |
|---|---|---|
| `H:\Games\PVZ-Fusion-3.9_MelonLoader` | True | `pvzrh-3.9` (`.39`) |
| `H:\Games\PVZ-Fusion-4.0_MelonLoader` | True | `pvzrh-4.0` (`.40`) |

Two consequences, and the first is the sharp one:

1. **A skipped host still prints `FusionRpg.X -> …\FusionRpg.X.dll`.** `HasMelonRefs != 'true'`
   selects `<Compile Include="..\FusionRpg.Injector.MelonLoader\SkipStub.cs" />`
   (`FusionRpg.Injector.MelonLoader.40.csproj:47-49`, and the same shape in `.MelonLoader.csproj:39-41`
   and `.39.csproj:36-38`). `SkipStub.cs` is six lines: an empty `internal static class`. So the
   skip path produces a **real, up-to-date, green .dll from almost no source** and MSBuild reports
   it as a normal build product. This is the same failure shape as the one the retraction is about —
   an instrument that cannot tell "built" from "built nothing" — in a third disguise. It is
   *worse* than the `error CS` counter, because here the exit code is 0, the error count is 0, and
   the output line says the project built. `dotnet test`/`dotnet build` green is not evidence that a
   host compiles.

2. **The NU1201 fix is verified through exactly one consumer.** The
   `<ProjectReference Include="$(GkCoreRoot)src\FusionRpg.Bridge\…">` sits inside
   `Condition="'$(HasMelonRefs)' == 'true'"` in all three MelonLoader csprojs, so on this machine
   the net6.0/net6.0 compatibility of Bridge is exercised only by `Injector.BepInEx`. That is
   enough to prove the TFM is consumable (it compiled and linked), but "all four loader hosts" is a
   static reading of four csproj lines, not a build result. I closed the gap by building the `.39`
   cell against its real pack:

   ```
   dotnet build src\FusionRpg.Injector.MelonLoader.39\…csproj -p:MlGameDir=H:\Games\PVZ-Fusion-3.9_MelonLoader
   → EXIT 0, 0 errors of any code
   ```

   That is the only build in this workspace that compiles `Bridges/pvzrh-3.9/**` — the `pvzrh-3.9`
   bridge shims are in **no** solution and **no** other build, so before this line they had not
   been compiled at all since the namespace revert. They compile clean. Good news, and it was
   worth the 40 seconds to find out.

**Recommendation:** the skip path should not emit a `->` line that reads as a build, and a
solution-level gate should assert that each of the four cells reported a real pack
(`HasMelonRefs == 'true'`) rather than asserting only that `dotnet build` exited 0.

### 3.2 REFUTED — "gk-core's own suites are unaffected". The guard suite is red, and one failure is the bridge's own.

Claim 5 is literally true about the two suites it names. It is false as a statement about gk-core.
`FusionRpg.Guard.Tests` is in gk-core's `FusionRpg.slnx` (`FusionRpg.slnx:16`) and in its CI
(`ci.yml:333`), and right now:

```
dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj   → EXIT 1
TRX auditB.trx: total=720  passed=586  failed=134  outcome=Failed
```

Honesty about attribution, because the 134 is mostly **not** the bridge: the overwhelming majority
are post-split **repo-root resolution failures** — guards looking for files in the wrong repository.

| failing test | message | cause |
|---|---|---|
| `ActorHudHostInjectionTests.Every_injector_host_copies_the_actor_hud_element_art` | `DirectoryNotFoundException: … gk-core\src\FusionRpg.Injector.BepInEx\FusionRpg.Injector.BepInEx.csproj` | host csproj is in **gk-fusion** |
| `InjectorSeedRegistryContentTests.HostCsproj_contentIncludesBothRegistries…` (×3 hosts) | `host project not found: gk-core\src\FusionRpg.Injector.MelonLoader.39\…` | same |
| `ZombieHpBridgeGuardTests.*` (×3) | `missing gk-core\src\FusionRpg.Injector\Bridges\pvzrh-3.8.1\CreateZombieSpawn.cs` | same |
| `EnforcementRegistryGuardTests.R1_…` | `catalog script missing: single-writer -> scripts/guard-single-writer.py` | guard scripts live in **gk-workflow** |
| `PvzWriteSurfaceGuardTests.*` (×8) | `python: can't open file 'gk-core\scripts\guard-single-writer.py'` | same |
| `TestSubstrateGuardTests.Guard_exits_zero_on_the_current_tree` | `baseline entry no longer violated — remove the line (the ratchet only shrinks)` | real ratchet debt in gk-forge |

**But one failure is caused by the bridge commit, and it is a committed SSOT that nobody updated:**

```
CoreTestProjectPolicyTests.W2_each_existing_manifest_projects_references_are_a_subset_of_its_manifest_entry
  → "FusionRpg.Core.Hud.Tests references 'src/FusionRpg.Bridge/FusionRpg.Bridge.csproj',
      not declared in its manifest entry"
```

`gk-core/tests/core-test-projects.v1.json` is the manifest the `CoreTestProjectPolicyTests` W1–W6
family validates against (`tests/FusionRpg.Guard.Tests/CoreTestProjectPolicyTests.cs:78-100`). Its
`FusionRpg.Core.Hud.Tests` entry still reads:

```json
"references": [ "src/FusionRpg.Core/FusionRpg.Core.csproj" ],
"links": [
  "src/FusionRpg.Injector/Hud/ActorHudCache.cs",
  "src/FusionRpg.Injector/Stats/InjectorDerivedOverride.cs",
  "src/FusionRpg.Injector/Hud/ActorHudUniqueFlags.cs"
]
```

Two separate defects in one file:

- **`references` was not updated** for the new `ProjectReference` → this is the live W2 failure.
- **`links` still names the three files in the host repository.** That is a *second, independent*
  record of the exact coupling `FusionRpg.Bridge` was created to delete, and those three paths now
  resolve to **nothing anywhere in the workspace** (verified: the files are absent from gk-fusion —
  claim 4a — and live only at `gk-core/src/FusionRpg.Bridge/{Hud,Stats}/…`).

Claim 6's instrument cannot see this: the search matched the `<Compile Include=` **directive** in
`*.csproj|props|targets`, and this coupling is recorded in **JSON**. Any future audit that greps
MSBuild for cross-repo source links will keep reporting zero while the coupling is still written
down in the manifest that owns the split. `links` for the other five entries are intra-repo and
correct; `FusionRpg.Core.Hud.Tests` is the only one that escaped the split.

The ledger's row 137 claim that gk-core's solution omission was *fixed* (commit `637e468`) is true
for **project presence** — 76 test projects on disk, 0 missing from `FusionRpg.slnx`, guard suite
included. It did not extend to the manifest, and the build-based gate cannot see the manifest.

### 3.3 `FusionRpg.Injector.MelonLoader.40` does not compile — pre-existing, and invisible by construction

The brief asked me to try the project that is not in the solution. It fails:

```
dotnet build src\FusionRpg.Injector.MelonLoader.40\…csproj -p:MlGameDir=H:\Games\PVZ-Fusion-4.0_MelonLoader
→ EXIT 1
→ 8 × CS0234: The type or namespace name 'Bridges' does not exist in the namespace 'FusionRpg.Injector'
   CheatActions.cs(4,26)   DebugActions.cs(5,26)
   Stats\EntityApply.cs(7,26)   Stats\EntityStatWriter.cs(5,26)
```

Root cause: `.40` sets `GameProfile=pvzrh-4.0` and compile-includes
`..\FusionRpg.Injector\Bridges\$(GameProfile)\**\*.cs` (`.40.csproj:44`). That directory does not
exist — `Bridges\` contains only `pvzrh-3.8.1` and `pvzrh-3.9`, both of which declare the single
shared namespace `FusionRpg.Injector.Bridges`. The glob matches nothing, so the namespace the four
files import does not exist.

**This is pre-existing, not bridge-caused.** `using FusionRpg.Injector.Bridges;` is present at
`0b1ef80~1` in `CheatActions.cs`, and `git log -- src/FusionRpg.Injector/Bridges` shows the last
touch was an import snapshot, long before the bridge work. I am reporting it because the pvzrh-4.0
cell is a **fourth unrecorded exclusion** of the same family as `tests/FusionRpg.Injector.Tests`:
the ledger explains at length why that project is out of the solution, and says nothing about
`.40`, which is out for a different reason and would be **silently green** if added (SkipStub, §3.1).

### 3.4 REFUTED — gk-fusion's CI test step cannot run a test. The exit-code guard is fused into the command line.

`gk-fusion/.github/workflows/ci.yml:71-73`:

```
L71 lead= 6 |      - name: Run the tests|
L72 lead= 8 |        run: dotnet test FusionRpg.slnx --no-build --verbosity minimal --blame-hang --blame-hang-timeout 10min|
L73 lead=10 |          if ($LASTEXITCODE -ne 0) { throw "FusionRpg.Launcher.Tests failed" }|
```

`run:` is at indent 8; the guard line is at indent **10**. In YAML a more-indented line following a
scalar is a **plain-scalar continuation**, not a nested mapping — so the guard is folded into the
command. Parsed value, not my reading of it:

```
STEP: 'Run the tests'
  run = 'dotnet test FusionRpg.slnx --no-build --verbosity minimal --blame-hang --blame-hang-timeout 10min if ($LASTEXITCODE -ne 0) { throw "FusionRpg.Launcher.Tests failed" }'
```

Executed under the step's own `shell: pwsh`:

```
$ pwsh -NoProfile -Command '<that string>'
MSBUILD : error MSB1008: Only one project can be specified.
  Switch: if
CI_STEP_EXIT=1        elapsed=0.6s
```

**0.6 seconds, zero tests.** So:

- The gate the ledger row 137 row relies on — *"ci.yml now names the SOLUTION rather than a
  hand-maintained project list"* — is textually true and operationally dead. On every push and
  every PR this step exits 1 without testing anything.
- The recorded measurement (*"runs 230 tests across three projects, all passing"*, `ci.yml:46-47`
  and `release.yml:46`) is a **true statement about a local command** that the CI step does not run.
  Two independent readings of the right number again.
- The defect class is the retraction's own, inverted. The `error CS` counter could not see a
  failure. This guard *does* produce a non-zero exit — so the step is loudly red, not quietly green
  — but it establishes nothing about the 230 tests, and the surrounding comment block (46-67)
  reads as a verified contract.

I checked the sibling files before reporting: `gk-fusion/release.yml` uses `run: |` blocks with the
guard at the same indent (correct), and `gk-core/ci.yml:170-171` uses the same correct
`run: |` block shape. **This one occurrence is the only instance** — `ci.yml:69` (`run: dotnet build
…`, lead 8) is correct; only line 73 is over-indented.

Also in that step: the `throw` message names `FusionRpg.Launcher.Tests` while the command runs the
whole solution — misleading if it is ever fixed without also fixing the message.

### 3.5 93 stale TRX files, 22 of them failing, sit in the working trees — including one directly on claim 5's path

A glob of `TestResults/*.trx` across the workspace returns 93 files, 22 with `outcome="Failed"`.
They are gitignored (`gk-core/.gitignore:54 [Tt]est[Rr]esult*/`) so this is not a repository change,
but they are on disk and any glob-based count reads them. The dangerous ones:

- `gk-core/tests/FusionRpg.Core.Workspace.Tests/TestResults/w.trx` — **20 total, 19 passed,
  1 FAILED**, mtime 19:10, failing test
  `KeepverseRootsTests.The_fusion_root_is_its_own_sibling_and_is_not_confused_with_core`.
  This is **the exact project and the exact figure** of claim 5 (20 tests), and a fresh
  `NeneScarlet_…_20_11_59_net8.0.trx` sits beside it reading 20/20. Anyone who counted
  "Workspace.Tests" by globbing `TestResults/*.trx` gets two answers, one of them a failure. This is
  the most likely physical origin of the workspace's earlier false "the suite is non-deterministic"
  claim: it was two files, not a flaky test.
- `gk-fusion/tests/FusionRpg.Launcher.Tests/TestResults/f.trx` — 166/166 **passing**, mtime 16:16,
  beside the fresh 166/166. Two identical reads, one 4 hours stale.
- `gk-fusion/tests/FusionRpg.Injector.Tests/TestResults/f.trx` — 119 total, **15 failed**, 16:17.
- `gk-core/tests/FusionRpg.Guard.Tests/TestResults/{audit,base,now}.trx` — 720 total,
  **134 / 140 / 140 failed**; `iso.trx` 8 total **7 failed** and `iso2.trx` 8 total **1 failed**,
  two minutes apart. That 7-then-1 pair is the non-determinism signature — and the two runs are
  `StubRegisterTests` over a register that was being edited between them, not a flaky test.

**Recommendation:** a counted test figure needs a *named* run and a mtime, not a glob. A guard
should assert the freshness of the TRX it reads.

### 3.6 Namespace/directory mismatches — the shape that hid the defect. Two, and one is the file the correction edited.

I compared each file's declared namespace against its path under its project's `RootNamespace`
(excluding `obj`/`bin`/`TestResults`). My first instrument was wrong — it compared `Actions\X.cs`
against `Actions` instead of `FusionRpg.Injector.Actions` and reported 103 false mismatches; I
fixed the prefix and re-ran. Result:

- `FusionRpg.Injector` — 128 files, **8** mismatches. Six are the `Bridges/pvzrh-3.8.1/**` and
  `Bridges/pvzrh-3.9/**` shims, which declare the shared `FusionRpg.Injector.Bridges` from
  per-cell directories. Intentional, and the direct cause of §3.3. One is
  `Host/InteropUsings.Bep.cs` (no file-scoped namespace; a `global using` file).
- **`Stats/EntityApply.cs` declares `namespace FusionRpg.Injector;`** — the *parent* namespace,
  from inside the `Stats\` directory. It is the only real mismatch in the tree, and it is one of the
  two files the bridge correction touched (`git diff 0b1ef80~1 18557ea -- src/FusionRpg.Injector/Stats/EntityApply.cs`
  adds `using FusionRpg.Bridge.Hud;` and `using FusionRpg.Bridge.Stats;` and rewrites two
  `Hud.ActorHudCache.MarkDirty` sites to the fully-qualified form). **Pre-existing** — the same
  `namespace FusionRpg.Injector;` is at `0b1ef80~1` and at the defective `0b1ef80`. Not a new
  defect. It is worth knowing precisely because this is the one file in the tree where a
  `namespace` rewrite would have been invisible to a directory-shaped review.
- `FusionRpg.Bridge` — 3 files, **0** mismatches. `FusionRpg.Core` — 1127 files, 3, all benign
  (two `[assembly:]` attribute files and `Commanders/CommanderId.cs`, a deletion tombstone).

### 3.7 No other blind-`error CS` instrument, and no unguarded external command in either CI

Searched every `*.py, *.ps1, *.yml, *.cs, *.md, *.json` in the workspace for `error CS`. All 40 hits
are in three buckets: guard **test fixtures** that synthesise a CS string to test the parser
(`gk-core/tests/tools/test_guard_*.py`), a guard's own documented regex
(`gk-core/scripts/guard-bench-compile.py:11`), and prose in `tasks/reports/`. **No counting
instrument narrows to one error prefix.**

I read both CI files' external-command sites. `gk-core/ci.yml` checks `$LASTEXITCODE` after every
`dotnet test` / `dotnet run` / `npm` / `python` call (≈100 sites, all guarded, inside `run: |`
blocks). `gk-fusion/release.yml` does the same. `gk-fusion/ci.yml` has two steps: the build (line
69, correct indentation, GH's `pwsh` default propagates the exit code) and the test step
(§3.4, broken). The `.40` and `Injector.Tests` exclusions are the only projects that can be
silently skipped rather than failing, and both are described in comments.

One adjacent observation, not a defect: `gk-core/ci.yml` runs
`dotnet test tools/LawnCombatObserver.Tests/…`, `tests/FusionRpg.Launcher.Tests/…` and
`tests/FusionRpg.AtomImporter.Tests/…` — projects that live in **gk-fusion and gk-forge**. gk-core's
CI therefore depends on siblings, the same class of coupling the Bridge module removed at the
compile level. Out of scope to fix; in scope to name.

---

## 4. Verdict on the six claims

The **retraction is true and the correction is sound.** Every one of the six claims reproduces, and
the two that could have been vacuous (4c, 4d) are backed by known-answer probes on the same
instrument. Specifically:

- The Bridge TFM correction is real and load-bearing: with a real MelonLoader pack, `.39` links
  `FusionRpg.Bridge` and builds at **0 errors of any code** (§3.1).
- The namespace correction is **complete and did not over-reach**: the three types exist exactly
  once, no gk-fusion file declares a Bridge namespace, no reference resolves to the old home, and
  the 20 files that reference the moved types carry the two `using` lines and the two rewritten
  member accesses — and nothing else. `git diff 0b1ef80~1 18557ea` on the touched files is
  `using` additions plus two `Hud.ActorHudCache.MarkDirty` rewrites. No `Assert` line moved.
- Nothing is MISSING a `using` in anything the gate compiles. I closed the one real coverage hole
  (§3.1) by building the `pvzrh-3.9` cell, which nothing in this workspace builds.
- The `pvzrh-4.0` cell has never been buildable and is not the bridge's fault (§3.3).

Two figures do not reproduce: "three gk-core test projects" is **two**, and "12 x CS2001" is **six
items** (§2.1).

The correction introduced **one** new problem, and it is not a compile error — it is a stale
committed SSOT (§3.2): `core-test-projects.v1.json` still lists the three host files as `links` and
omits the new `ProjectReference`, which fails `CoreTestProjectPolicyTests.W2` today. And separately,
the standing gate that is supposed to keep the correction honest is broken (§3.4).

---

## 5. What I could not check, and why

1. **The standalone-clone claim** (12 CS2001 before, 0 after; 2 remain for a gk-forge tool). Proving
   it needs a gk-core clone with `gk-fusion`/`gk-forge`/`gk-data` absent, and a full 83-project
   build. I measured the *static* residue instead — 0 `<Compile Include="$(Gk…Root)…">` and 7
   `<ProjectReference … $(GkForgeRoot)>` — which is consistent with it but is not the measurement.
2. **`dotnet test` in Release / on CI.** Every test run here is Debug, local, single machine. CI is
   unrunnable for gk-fusion (§3.4) and I did not run gk-core's 70-command CI.
3. **The other 130 gk-core test projects** beyond Core.Tests, Workspace.Tests, Hud.Tests and
   Guard.Tests. Given 22 stale TRX files show failures in ActorHub (6), ClassSystem (11),
   Server.Tests (16), Data.Tests (3), E2E (7) and Vocabulary (2), several are **probably** red
   too. That is a reading of stale files, not a measurement, and I did not run them.
4. **gk-forge, gk-web, gk-data, gk-tests, gk-content** — searched for claim 6 and the type
   declarations, never built. `gk-forge` has failing stale TRX (AtomImporter 2, ItemSeedValidator 6,
   ElementEnumGen 1).
5. **The `pvzrh-3.8.1` MelonLoader cell.** No MelonLoader pack for 3.8.1 exists on this machine, so
   that cell is unbuildable here. It compiles the same `Bridges/pvzrh-3.8.1/**` the BepInEx host
   compiled, so coverage exists by another route.
6. **Whether the 134 guard failures are all post-split root bugs.** I sampled 7 messages; 132 remain
   unclassified.
7. **Concurrency.** `gk-core/scripts/guard-power.py` was modified at **20:14:07**, during this audit,
   by another session (I never opened it for writing; my only writes were to `%TEMP%` and to
   `bin`/`obj`). gk-core was therefore a moving target for part of the run. Every figure above is a
   reading of the tree at the time stated, and the guard-suite number especially should be
   re-measured once that session lands.

### Suggested order, cheapest first

1. Fix `ci.yml:73` (dedent to 8) — the gate is dead and the fix is one character.
2. Add `src/FusionRpg.Bridge/FusionRpg.Bridge.csproj` to the `references` of the
   `FusionRpg.Core.Hud.Tests` entry in `gk-core/tests/core-test-projects.v1.json`, and **delete the
   `links` array's three host paths** — they name files that exist nowhere.
3. Decide `.40`: give it a `Bridges/pvzrh-4.0/`, or record its exclusion beside `Injector.Tests`'s.
4. Make the skip path stop emitting a dll line that reads as a build, and add an assertion that each
   of the four cells found a real pack.
5. Re-point the 132 remaining guard tests at the right repository roots. That is the largest single
   source of red in the workspace and it is unrelated to the bridge.

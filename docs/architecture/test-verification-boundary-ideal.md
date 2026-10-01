# Test verification boundary — the ideal

**Status:** idea phase, written 2026-09-15; superseded for build purposes by the owner rulings R-TV1/R-TV2
and R15 (2026-09-18) and by the [capability map](test-verification-boundary-map.md), which is where
the build is specified. This page stays as the reasoning trail.

> **Updated 2026-09-18.** **2 owner rulings landed 2026-09-18** (R-TV1–R-TV2): the `Core.Tests` split **is authorized now** (a **projected** ~55–65% compile-time reduction per touched subsystem, paid once — projected, not measured; see the correction at §"Net, honest verdict"), and the verification registry is deepened now, unbundled — **their ordering interacts, see the note**.

> **Specified 2026-09-18:** capability map and module specs for the unbuilt remainder — [test-verification-boundary-map.md](test-verification-boundary-map.md).

## Which loop this extends

Not applicable — this is developer-tooling/CI architecture, not a player-facing RPG system. Saying
so rather than force-fitting a loop name: `docs/guide/the-loops.md` describes gameplay loops, and
none of them cover "how fast does verification run for a code change." The binding principle that
*does* apply here is the repo's own: **"the test is made to protect the repo, not burden the repo"**
(the owner's own framing for this idea phase) — a test suite exists to catch regressions cheaply; if
running it costs more than the regression it would have caught, the *verification process* is the
defect, not the tests.

## What this is

The owner's concern: `FusionRpg.Core.Tests` has 13,513 test cases in one assembly, and a scoped
verification run for a two-file change (`DebugActions.cs`, `DebugEndpoints.cs`) fell back to running
**all** of it (plus all 442 of `Server.Tests`) because the registry-driven selector
(`gk-core/scripts/verify-change.py`) had no narrower mapping for those paths. The owner asked: is this my
(the agent's) mistake, or an architecture problem, and how does the industry solve it at this scale.

## What already exists

### Built

- **`gk-core/scripts/verify-change.py` (the planner; ported 2026-09-26 from the retired `scripts/verify-change.ps1`) + `gk-core/scripts/verification-boundaries.v1.json` + `gk-core/scripts/guard-verification-boundaries.py`**
  — a hand-authored, integrity-guarded path→test mapping. This *is* a lightweight, repo-specific
  version of the Bazel-style "target graph" pattern the industry uses (see Prior art) — not a naive
  fallback. The planner (`gk-core/scripts/verify-change.py:_build_checks`, or
  `verify-change.ps1:74-92` in the retired PowerShell form) resolves each changed path to its most-specific owner boundary
  and the seams layered on it; `guard-verification-boundaries.py:84-93` fails the registry itself if
  any `src/**` file has zero owner. The mechanism **works today**, proven by the `data-item-socket` /
  `data-item-socket-test` pair (`verification-boundaries.v1.json:1755-1768`, `:1769-1781`; citations re-checked
  2026-09-18, since the registry is sorted by id and has grown): a change to
  `RpgStore.Sockets.cs` runs `dotnet test ... --filter VerificationId=data.item-socket`, not the whole
  `Data.Tests` project.
- **Category-trait exclusion** (`DiskSemantics`, `Heavy` — `docs/contributing/testing-standard.md`
  §6) — cross-cutting *concern* filtering (disk-bound? slow?) applied uniformly across every project.
  This matches the industry-standard xUnit `[Trait]` pattern for concerns that cut across every
  subsystem, as opposed to per-subsystem selection.
- **Four test profiles** (`default`/`full`/`gate`/`nightly`, same doc §6) — a clean local-loop vs.
  CI-vs-release separation, matching the common "fast inner loop, full outer loop" industry shape.
- **Two internal measurement audits already ran and ruled things out**
  (`docs/contributing/test-burden-audit.md`, `test-architecture-audit.md`, both 2026-09-13). They
  measured, on this exact repo: `Core.Tests` — 13,369 tests, **89s wall, 4.6ms mean per test** — and
  explicitly recommend *leaving its structure alone* (`test-burden-audit.md` §6, "Leave Core/Server
  serialization alone… already efficient"). The measured burden is **`Data.Tests`: 96.7% of all
  summed test time**, caused by a **process-global mutex in SQLite's in-memory VFS**
  (`sqlite3MutexAlloc(SQLITE_MUTEX_STATIC_VFS1)`, `src/memdb.c`) that serializes every in-memory
  database open in the process — proven by a 4-arm discriminator test
  (`test-architecture-audit.md` §3) and fixed *in principle* by process-level sharding (23.9s
  concurrent vs. 47.4s sequential, §5), not a thread cap and not smaller assemblies.

### Wiring gap

- The registry mechanism that already works is applied to **2 of dozens of legitimate seams** in the
  whole repo. When this was written (2026-09-15), lines 14-16 of `verification-boundaries.v1.json` held
  the only two *focused* (narrow, `VerificationId`-filtered) boundaries, and lines 17-23 held seven
  *module*-level fallbacks. Those line numbers no longer describe the file (it has 88 boundaries,
  sorted by id, a reading). The fallbacks (no `VerificationId`) cover the entirety of `gk-core/src/FusionRpg.Core/**`,
  `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`, `gk-fusion/src/FusionRpg.Injector*/**`, etc. — each one
  runs its *whole* project's default filter. This is exactly a wiring gap in the skill's sense: the
  machinery is proven and cheap to extend (one JSON entry + one `[Trait("VerificationId", …)]`
  attribute, per the working example), it is just not populated.
  **Partly closed 2026-09-18 — see "R-TV2 execution" below.** The production half is now mapped for
  `Data`, `Server` and `Launcher`; `Core` and `Injector` are still whole-project fallbacks.
- `guard-verification-boundaries.py:84-93` only walks `src/**` for unmapped-file enforcement.
  `tests/**` has **no equivalent enforcement**, so a test file can go unmapped indefinitely with
  nothing failing loudly. Found live this session: `gk-core/tests/FusionRpg.Server.Tests/LawnQuickStartEndpointTests.cs`
  had zero registry entry until today, despite `LawnQuickStartEndpointTests` itself already existing
  and being exercised repeatedly by prior sessions.
- `verification-boundaries.v1.json` has a `"seam"` boundary *kind* already defined
  (the planner applies seam matches on top of the owner match; the seam loop came from the
  retired `verify-change.ps1:89-91`, now `gk-core/scripts/verify-change.py:794-802`) and **one seam entry**
  — `effect-catalog-drift`, added 2026-09-15 by `8be05e50` (this doc said "zero" until 2026-09-18;
  it was written against an older registry). Seams are exactly what the Bazel tooling research below
  calls out as the easy thing to miss: shared fixtures, tuning JSON, generated trees — inputs outside
  the plain source-import graph, and one entry is not coverage of them.

### Real gap

- No automated "which tests actually exercise this changed code" dependency graph exists. Today's
  registry is 100% hand-authored glob matching with **no verification that a glob's claimed owner
  still covers the changed code** — a boundary can silently rot (someone adds a new subsystem folder
  under `src/FusionRpg.Core/NewThing/**`, the `core-fallback` glob still matches by coincidence, but
  nothing checks that `Core.Tests` genuinely exercises it beyond "it's in the same project").
- No per-subsystem split of `FusionRpg.Core.Tests` exists (one `.csproj`, 855 files, 26 subsystem
  folders already in place as natural boundaries — see the sibling response in this session for the
  concrete migration cost). This is a real gap **only if build-time isolation is the goal** — the
  measured evidence (above) says it is not the current bottleneck.
- Microsoft's native .NET **Test Impact Analysis** (VSTest/Azure Pipelines) is not wired here, and —
  per the research below — has a **documented incompatibility with xUnit/NUnit data-driven tests**.
  This repo has 403 `[Theory]` declarations, 1,583 `[InlineData]` rows, and 26 `[MemberData]` sources
  contributing a meaningful share of the 13,513 `Core.Tests` count. Adopting VSTest TIA directly would
  silently under-select coverage for that share. Stated explicitly so nobody proposes it later as an
  obvious automated fix.

## Prior art

- **Microsoft (internal, cited via testμ 2026 talk)**: a **100-package monorepo, 14,000 tests** —
  before optimization, every PR ran the whole suite and developers waited **3–4 hours**. The fix was
  test selection that "maps a code change to its dependencies and risk, with the team approving the
  selection rules" — a **hand-curated, team-reviewed mapping**, not a fully automatic graph. This is
  structurally the same shape as this repo's `verification-boundaries.v1.json` +
  `guard-verification-boundaries.py` integrity check (a human-authored, mechanically-validated
  registry) — the number (14,000 tests, ~100 packages) is close enough to this repo's own scale
  (13,513 tests, 26 subsystem folders across ~8 assemblies) to treat as directly comparable.
- **Google / Meta / Microsoft, cross-company study**: all three run **tens of thousands of projects**
  in single monorepos successfully — monorepos at this scale are a solved, common pattern; the
  enabling factor named across all of them is build-graph tooling (Bazel/Buck-style), not splitting
  the repo.
- **Bazel ecosystem** (`bazel-diff`, `target-determinator`, `rdeps`): the canonical implementation of
  "diff two git revisions → compute the set of affected test targets" via a real dependency graph.
  Their own stated caveat is the one most relevant here: *"[the selector] must also account for
  inputs that sit outside the ordinary import graph, such as schemas, environment templates, code
  generators, shared fixtures, container images, and CI configuration."* This is precisely the
  `"seam"` boundary kind this repo's own registry already defines but has never populated.
- **.NET-native Test Impact Analysis** (Azure DevOps / VSTest): automatic, coverage-instrumentation-based
  test selection exists as a first-party feature — but Microsoft's own docs state that **data-driven
  xUnit/NUnit tests cannot use it** (Rerun-failed-tests, multi-agent distribution, and Test Impact
  Analysis all exclude them). Given this repo's heavy `[Theory]`/`[InlineData]`/`[MemberData]` usage,
  this feature would degrade rather than solve the problem here.
- **xUnit's own documented design bias**: the framework's authors prefer *"different test types into
  different assemblies, rather than traits for filtering"* — but acknowledge the tradeoff: multiple
  assemblies raise project-maintenance overhead, and traits integrate more smoothly with
  `dotnet test`/MSBuild pipelines. This repo already chose traits for its two cross-cutting concerns
  (`DiskSemantics`, `Heavy`) — consistent with the "flexibility over purity" side of that documented
  tradeoff, for exactly the concerns traits suit (cutting across every subsystem) rather than
  subsystem boundaries (which suit projects/registry entries).

Sources: [Endor Labs — Bazel dependency management](https://www.endorlabs.com/learn/5-tips-for-managing-bazel-dependencies-without-losing-friends) ·
[Tinder/bazel-diff](https://github.com/Tinder/bazel-diff) ·
[bazel-contrib/target-determinator](https://github.com/bazel-contrib/target-determinator) ·
[QASkills.sh — affected package detection](https://qaskills.sh/blog/monorepo-testing-affected-package-detection) ·
[testμ 2026 — scaling test automation at Microsoft](https://www.testmuai.com/blog/scaling-test-automation-microsoft/) ·
[Graphite — why top tech companies move to monorepos](https://graphite.com/guides/why-top-tech-companies-are-moving-to-monorepos) ·
[Microsoft Learn — Test Impact Analysis, Azure Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/test/test-impact-analysis?view=azure-devops) ·
[xunit/xunit#610 — trait filtering discussion](https://github.com/xunit/xunit/issues/610) ·
[Span of Reference — filtering xUnit tests](https://edgamat.com/2024/03/16/Filtering-Xunit-Tests.html)

## The shape

Three **independent** levers, matching what the internal audits and the industry research both
converge on — independent because each targets a different, separately-measured cost:

1. **Deepen the existing registry (cheap, already proven, do this first).** Add focused
   (`VerificationId` + `[Trait]`) boundaries for every path that is genuinely single-concern —
   starting with every test class (test files are *always* single-concern by construction, unlike a
   1,400-line multi-route `DebugEndpoints.cs`). Extend `guard-verification-boundaries.py` to require
   an owner mapping for `tests/**` the same way it already requires one for `src/**`, closing the gap
   that let a real test file go unmapped. Populate `"seam"` entries for cross-cutting non-source
   inputs (tuning JSON, generated trees, shared fixtures) per the Bazel-diff caveat above.
2. **For the *actually measured* burden (`Data.Tests`), follow the audit's own conclusion: process
   sharding, not project splitting.** `test-architecture-audit.md` §5 already proved 2× wall-clock
   improvement from two concurrent `dotnet test` processes vs. one — because the bottleneck is a
   process-global SQLite mutex that a smaller assembly does not route around (splitting `Data.Tests`
   into N projects would just create N processes serializing on the same in-process mutex *within
   each* run unless they are literally separate `dotnet test` invocations).
3. **Splitting `Core.Tests` — corrected 2026-09-15 after a peer review caught an overclaim, then
   measured directly (see "Compile-time measurement" below).** The first draft of this doc said
   "13,369 tests in 89s at 4.6ms mean is not a burden, so don't split" — that conflated *test
   execution time* (which the burden audit measured and which splitting does not help) with *compile
   time* (which nobody had measured, and which splitting genuinely does help — see the numbers
   below). Corrected verdict: **compile time is real and scales with file count, but it is not the
   dominant cost for the specific incident that started this doc** (running whole-project *test
   execution* — 85s + 100s — dwarfs the ~2-3s compile step either way). Splitting `Core.Tests` is a
   legitimate, independently-justified lever for **incremental-build latency** and **architectural
   enforcement** (a project reference is a compiler-checked boundary; a folder is not) — it is just
   not the fix for the run-time selection problem lever 1 already fixes more cheaply. Both are worth
   doing; they solve different costs. See "What this deliberately does not decide" for the honest
   scope of what is still unmeasured (a full 26-project migration was not attempted, only the
   underlying cost model).

### Compile-time measurement (2026-09-15, this repo, this machine)

Measured directly rather than assumed, per `DESIGN-GATE.md`'s own rule ("test the constraint before
you declare it"). Method: `dotnet build <proj> -c Debug /clp:PerformanceSummary`, reading the
`CoreCompile`/`Csc` target duration (the actual C# compiler invocation) separately from total wall
time (which also includes MSBuild's restore/reference-resolution machinery). Three runs per no-op
case to check for noise; single runs for the real-recompile case since the signal was unambiguous.

| Project | Files | No-op rebuild (nothing changed) | Real recompile (1 file touched) — `Csc` time alone |
|---|---|---|---|
| `FusionRpg.Guard.Tests` | 56 | ~0.9–1.2s (×3) | **139ms** |
| `FusionRpg.Core.Tests` | 855 | ~1.4–2.2s (×3) | **1,969ms** |

Two separate, real findings, both load-bearing:

1. **`Csc` compile time scales almost exactly linearly with file count**: 855/56 ≈ 15.3× the files,
   1969/139 ≈ 14.2× the compile time. Splitting `Core.Tests` into per-subsystem projects would let a
   change to one subsystem recompile only that subsystem's slice — e.g. a ~30-file project would
   compile in roughly 30/855 × 1969ms ≈ 70ms instead of ~2s, matching the Guard.Tests-scale number
   directly. **This is the real, previously-unmeasured, genuine win the peer review identified** — my
   first draft's dismissal of "compile time: Yes" was wrong because I never measured it.
2. **But the no-op/restore overhead (~1–2s) is roughly constant regardless of project size** — Guard
   (56 files) and Core (855 files) differ by only ~30-70% on this axis despite a 15× file-count gap.
   This is `ResolveProjectReferences`/restore-graph-walk machinery, proportional to the *project
   reference graph shape*, not to source file count. It means splitting into **many** projects adds
   this fixed cost **once per project touched in a build**, which can offset or reverse the Csc
   savings for an operation that spans several of the new smaller projects at once (a full/clean
   solution build, or a change that legitimately crosses two subsystems).

**Net, honest verdict**: for the single most common case — one or a few files changed in one
subsystem, verify just that subsystem — splitting turns roughly "1.5s fixed + 2s Csc ≈ 3.2s" into
roughly "1–1.2s fixed + 0.07–0.2s Csc ≈ 1.1–1.4s." ⚠️ **Corrected 2026-09-18 — this said "a real, measured, ~55-65% reduction" and it is a
**projection**, not a measurement.** Two things were measured: today's unsplit Core.Tests build, and
Guard.Tests as a small-project comparison. The 55-65% comes from dividing the Csc time by file count
(*"a ~30-file project **would** compile in roughly 30/855 × 1969ms ≈ 70ms"*) over a split that does not
exist — and the paragraph directly above it says the **other** cost axis is explicitly **not** linear
(*"roughly constant regardless of project size"*), so the model is known not to hold on both terms.
The denominators have also moved: `Core.Tests` is **911** `.cs` files today, not 855, and
`Guard.Tests` is **85**, not 56. **The ruling stands** — the split is authorized on the architectural
argument, and even a much weaker win is worth having. What is void is calling the number measured. A
~55-65% projected reduction for that step —
genuine, but "moderate and measured," not the peer review's "potentially massively" framing, and it
is a *compile-time* win layered on top of lever 1's run-time win, not a replacement for it. The
architectural-enforcement benefit (a project reference is checked by the compiler; a folder convention
is not) is real but was not itself measured here — it is a design-quality argument, not a speed one.

**Measured 2026-09-22, the split landed (`TVB5.9`) — the projection above is now replaced by readings
from the real tree.** Taken with `dotnet build <project> -c Release -clp:PerformanceSummary` on this
machine, same session:

| Build | `Csc` | `Csc` calls | Wall |
|---|---|---|---|
| one tucked-in subsystem — `gk-core/tests/FusionRpg.Core.Lawn.Tests` (2 files) | **3,580 ms** | 3 | **4.87 s** |
| the residual `FusionRpg.Core.Tests` — the old monolith, still the largest member | **12,337 ms** | 12 | **11.62 s** |

The direction of the projection holds and its magnitude does not: the touched-subsystem build is
~3.4× faster in `Csc` and ~2.4× faster wall than the residual, not the ~28× the file-count division
implied, because fixed cost and the known non-linear term both dominate at this size. The whole-profile
claim in the same session: `scripts/test-fast.ps1 -AllDefault` ran **39 of the Core test projects, 0
failures** before the harness cut the call at ~15 minutes (`FusionRpg.Data.Tests` alone is 10m16s), and
the manager's independent run of the same command at the merged head was **Failed 0 / Passed 18273** —
so the finished-suite evidence is that run plus every increment's own apply-gate and focused verify, not
a single local full-profile run.

**Re-measured 2026-09-23 at the closing tip (`633ffb4a8`, lane `tvb60`)** — the split now holds 67 of the
68 manifest projects (the 68th is TVB-F17's `GlobalUsings.cs`, which cannot be one), and the numbers moved
with it. Same command, same machine:

| Build | `Csc` | `Csc` calls | Wall |
|---|---|---|---|
| `gk-core/tests/FusionRpg.Core.Lawn.Tests` (2 files) | **2,448 ms** | 3 | **3.92 s** |
| the residual `FusionRpg.Core.Tests` | **8,680 ms** | 14 | **9.27 s** |

The direction and the ratio both hold — ~3.5× in `Csc`, ~2.4× wall — on a residual that has since given
up more of its files. The Core test **group** ran green in full at this tip: **68 projects, 15,836 tests,
0 failures** (`scripts/test-fast.ps1 -Project <every member>`, default profile), the residual's own 9,600
among them. What is *not* green is the whole `-AllDefault` profile, and not for anything the split owns:
`gk-core/tests/FusionRpg.E2E.Tests` fails on two stale **web** fixtures (`TVB-F25`) — the profile's Data
(1,766/0) and Server (826/0) legs were green. The finished-suite evidence therefore remains the group run
above plus every increment's apply-gate, not one local `-AllDefault`.

### Alternative considered and rejected: splitting the repo into multiple smaller repos

The owner's own escalation option, raised explicitly. Rejected for now:

- This is four tightly-coupled modules (Launcher/Injector/Server/Web) plus Core/Data/Contracts/CheatCore
  underneath, per `AGENTS.md`'s own module table — a single session routinely touches Injector +
  Server + Python tooling + their tests together (this session did exactly that). A multi-repo split
  would turn every one of those ordinary cross-cutting changes into a multi-repo coordination problem,
  trading today's real-but-fixable verification-scoping cost for a permanent cross-repo
  versioning/dependency cost on the *common* case.
- Neither measured bottleneck (the registry's coverage gap; `Data.Tests`' SQLite VFS mutex) is a repo-
  boundary problem. Splitting repos fixes neither; it just relocates where the same gaps live.
- The Google/Meta/Microsoft prior art above is a direct counter-example at far larger scale: all three
  keep tens of thousands of projects in ONE repo and solve this with build-graph tooling, not
  repo-splitting.

### If lever 3 is commissioned: the recommended shape, not a blind folder→project script

A peer review of this doc's first draft proposed a concrete migration shape, reviewed here and
endorsed with one correction. **Do not** run `folder → project` as the entire algorithm — that
decides architecture by coincidence of today's folder layout. Instead, two separate, small,
deterministic tools, each doing one job:

1. **A read-only analyzer first.** Walk the existing folders (`Actions`, `Combat`, `Effects`, `Stats`,
   `World`, … — the 26 that already exist under `gk-core/tests/FusionRpg.Core.Tests/`), and for each candidate
   boundary report file count, test count, and — critically — **cross-boundary symbol references**
   (does anything in `Combat/` reach into `World/`'s internals in a way a project reference would
   refuse?). Produces a report, mutates nothing. This is the same "observe before fix" discipline this
   repo already applies elsewhere (`docs/DESIGN-GATE.md`, the goal cycle's own READ→BUILD→OBSERVE
   order).
2. **A deterministic apply step, gated on a human-approved manifest** — a policy file naming exactly
   which folders become which project and what each may reference, e.g.:
   ```json
   { "project": "Combat.Tests", "include": ["Combat/**"], "references": ["Combat", "Actor", "TestSupport"] }
   ```
   The tool then does the boring, mechanical part only: create the `.csproj`, move the files, add
   `ProjectReference`s, remove the old `Compile` items, rebuild, run the moved tests, and refuse if a
   moved file references something outside its declared boundary. **The tool never decides
   groupings** — that stays a human/design call, exactly the same separation of concerns
   `gk-core/data/tuning/*.json` + its deterministic readers already use everywhere else in this repo
   (`tunables-ssot.md`), and exactly what `verification-boundaries.v1.json` +
   `guard-verification-boundaries.py` already are for test *selection*. This is not a new pattern for
   the repo to learn — it is the existing one, applied to project structure instead of tuning numbers.

**Build on Roslyn/MSBuild's own APIs (`Microsoft.CodeAnalysis`, `MSBuildWorkspace`), not a
hand-rolled C# parser.** Roslyn is Microsoft's own compiler platform, mature and stable, and already
exposes the syntax tree, symbol/reference model, and project-reference manipulation this needs.
Existing tools reviewed and found to solve *adjacent*, not identical, problems: `Roslynator` (500+
analyzers/refactorings, general-purpose); ReSharper/Rider's "Move Types into Matching Files" (real,
mature, but a no-op here — see "What already exists → Real gap" above, this repo's giant files are
one type each, not many types in one file); `dotnet-depends`/`DotNetCobble` (dependency
*inspection*/solution *assembly*, not project *splitting*). None of these do the apply step above
end-to-end; a thin orchestration layer over Roslyn/MSBuild is the only path, matching what "build
ourselves" already meant in this doc's first draft — the correction is *what* to build (an
orchestration layer honoring a human-approved manifest) and *why* (architectural enforcement +
measured compile-time win), not "because 13,513 is scary."

## Tunables

None. Nothing here is a runtime/balance number — it is verification-process architecture (registry
entries, CI invocation shape, process count for a sharded `Data.Tests` run). Any concrete shard count
or CI parallelism setting that comes out of implementing lever 2 would be a structural/CI config value
(named and justified in its own commit), not a `gk-core/data/tuning/*.json` entry.

## What this deliberately does not decide

- The exact `Data.Tests` shard count or CI-invocation shape for process sharding — `test-architecture-audit.md`
  §6 already states the shard count was not measured (2 halves proved the principle; 4 or 8 were not
  tried). That is execution work for a `/plan`, not an idea-phase decision.
- Which specific seams/test files get focused boundaries first, or the full replacement text for
  `verification-boundaries.v1.json` — an ordered task list, not an idea.
- Whether `guard-verification-boundaries.py`'s `tests/**` enforcement (recommended above) should be a
  hard CI failure immediately or phased in with a ratchet/baseline (matching `test-substrate-baseline.txt`'s
  own precedent for a similar rollout). That is a rollout-mechanics decision for the spec/plan phase.
- The actual boundary manifest for a `Core.Tests` split (which folders become which projects, what each
  may reference) — the compile-time measurement above justifies *doing* lever 3 eventually; it does not
  by itself define the 26-project (or however many) boundary set. That is exactly what the read-only
  analyzer step (above) is for, and it has not been run.
- Whether the cross-boundary-reference check the analyzer would need (do any of `Combat/`'s tests reach
  into `World/`'s internals?) turns up violations that make some of today's 26 folders **not** clean
  boundaries yet. Not measured — the folder split was observed to exist, not verified to be
  reference-clean.

## Owner rulings — 2026-09-18

### R-TV1 — do the `Core.Tests` split now (overrides the recommendation to defer)

**Ruled: do it now.** The recommendation was to defer against a multi-day migration and a moderate
benefit; the owner's call is that the benefit compounds and the cost is one-time.

The document's own insistence is honoured — this is decided **from the numbers**: a projected (not measured — see §"Net, honest verdict") **~55–65%
compile-time reduction per touched subsystem**, paid once, against a multi-day migration. Not from
*"13,513 is scary"* and not from *"compile time obviously doesn't matter"*.

**What the ruling buys beyond speed**, and it is the half that only arrives once the split exists:
**architectural enforcement.** A subsystem cannot quietly take a dependency on another subsystem's tests
when they no longer compile together. That is a structural guarantee, not a convenience.

### R-TV2 — deepen the verification registry now, and it is NOT bundled with the split

**Ruled: now.** Cheap, already proven, and it directly fixes the failure that produced this document — an
unmapped production path is a verification-boundary defect, and a deeper registry is how that stops
recurring.

> ⚠️ **These two rulings interact, and the ordering is not stated by either.** R-TV1 moves test files;
> R-TV2 maps paths **to** test files. Deepening the registry first and then splitting means **remapping
> what was just mapped**.
>
> **The cheap resolution, offered as a sequencing note rather than a third ruling:** deepen the registry
> against *production* paths, which the split does not move, and let the test-side mapping settle after
> the split. If the registry's entries key on test project or file location, do that half last.
>
> Both were ruled "now" and neither was bundled, so this is a scheduling detail for whoever picks them
> up — but doing them in the wrong order costs the registry work twice.

### R-TV2 execution — 2026-09-18, production half only

Done against **production** paths, exactly as the sequencing note asks. `FusionRpg.Core.Tests` is
untouched: no `Core` production path got a focused boundary, because every such boundary must name the
test project that owns its `VerificationId`, and R-TV1 is about to replace `core` with per-subsystem
projects. Doing Core now would mean re-keying it after the split.

What landed:

- **34 new focused owner boundaries** over `Data`, `Server` and `Launcher` production paths, each with
  a `VerificationId` and the `[Trait]` on every test class that references the mapped file's symbols.
  Each carries at least the guards its module fallback carried (`dal` + `test-substrate` for Data,
  `dal` for Server), so a focused boundary never verifies less than the fallback it overrides.
- **A real defect fixed:** `launcher-fallback` pointed at the `guard` project. `FusionRpg.Guard.Tests`
  has **zero `ProjectReference`s** — it is a source-text guard assembly — so a change to
  `gk-fusion/src/FusionRpg.Launcher/**` never compiled or ran `FusionRpg.Launcher.Tests`, which does reference
  it and does run in CI. The owner now points at `launcher`, and a new `launcher-source-guards` seam
  keeps `Guard.Tests` running, so nothing that ran before stopped running.
- **`launcher` added to `projects`** (it was absent entirely) and `launcher-tests-fallback` added, so
  `gk-fusion/tests/FusionRpg.Launcher.Tests/**` resolves at all instead of being refused as unmapped.
- **`guard-verification-boundaries.py --report`** prints how deep the registry maps `src/**` — which
  owner each production file resolves to, and whether that owner narrows the run. It prints the scale
  and asserts nothing, per `validation-ssot.md`: these counts are a reading that moves whenever
  production code ships.

Deliberately **not** done, and still open:

- Focused boundaries for `gk-fusion/src/FusionRpg.Injector*/**` — Injector's only compiled test project is not in
  CI. (`gk-core/src/FusionRpg.Core/**` was the other one; it is done now — see "Core half done" below.)
- Test-side focused boundaries beyond the ones that already existed. `server.lawn-quick-start` is a
  trait with no boundary using it, because its natural production owner (`DebugEndpoints.cs`) is a
  multi-route file that ten test classes reference — mapping it focused would *under*-select. It stays
  module-level until that file is split; that is the honest answer, not a registry entry.
- Entries for `gk-core/data/tuning/**` beyond the exact-name ones (`power-scale.v3`, `lawn-attrition.v1`/`v2`,
  `deployment-hierarchy.v1`/`v2`, as of 2026-09-18). Still the Bazel-diff gap named above; specified
  in the map's `seam-coverage` module.

### R-TV2 execution — Core half done, 2026-09-23

R-TV2's Core half waited on R-TV1, and R-TV1 landed: `core-split-apply` moved 67 of the manifest's
projects out of the one `FusionRpg.Core.Tests` assembly (the 68th, `GlobalUsings.cs`, is a `global using`
alias set that cannot be a project — TVB-F17), and `core-registry-rekey` then re-keyed the registry
against the split tree. What that means for this document's own claim:

- **Every `gk-core/src/FusionRpg.Core/<Area>/**` path resolves to an owner derived from the production map**,
  never from a name match: 35 areas, each a C7 group of exactly the test projects whose own sources
  reference that area's symbols (`--production-map`, whose four compilation-model defects were fixed the
  same week — TVB-F18 — so the map reports `0` projects with compilation errors). A one-area production
  change therefore plans that area's group: measured, `gk-core/src/FusionRpg.Core/Lawn/MoveQueue.cs` plans **2**
  test projects where it used to plan all **68**, `Events/EventDrain.cs` **1**, `Effects/DamageFx.cs`
  **32**, `Stats/ModifierBag.cs` **29**. A path under no area (a root file such as `SimModels.cs`) still
  plans the full `core` group, so nothing verifies less than before.
- **Every pre-existing focused `core.*` boundary now names the project (or smallest C7 group) that holds
  its trait** — 24 of them, including the five the spec's K2 row knew about; only `project` changed, so
  every guard a boundary carried is still carried (`battle-effect-math` keeps `battle-responsibility` and
  `funnel-delta`).
- **The orphan reading moved rather than being asserted:** `guard-verification-boundaries.py --report`
  lists **8** orphan `VerificationId`s, **none `core.*`** — the six `core.*` orphans K3 named each got a
  focused boundary read out of its test class, and `core.species-passive-atoms` no longer exists as a
  trait at all.
- **The compile-time claim this document corrected is now measurable rather than projected.** The
  "Net, honest verdict" above carries the readings: a tucked-in subsystem's `Csc` is **2,448 ms** against
  the residual's **8,680 ms** (~3.5×), ~2.4× wall — the same ratio the first measurement found, on a
  residual that has since given up more of its files.

One thing R-TV2's Core half does **not** have: a green `test-fast.ps1 -AllDefault`. Every leg is green
(Data 1,766/0, Server 826/0, the Core group 68 projects / 15,836 tests / 0 failures) except
`gk-core/tests/FusionRpg.E2E.Tests`, which is red for two stale **web** fixtures that live outside this program's
fence and have no owner boundary at all — filed as TVB-F25 for the manager to route.

### The planner moved to Python, and the guard step stopped racing its own build — 2026-09-26

`gk-core/scripts/verify-change.py` + `gk-core/scripts/lib/verification_boundaries.py` replaced the
retired `scripts/verify-change.ps1` + `scripts/lib/VerificationBoundaries.ps1` as the **named** entry point
(AGENTS.md "Verification boundary"). Two measured reasons, both recorded because they are the kind of
defect that recurs:

1. **The guard-module step's `dotnet test` could not finish its own job.** `dotnet test` spawns
   `tests/FusionRpg.Guard.Tests/bin/Release/net8.0/testhost.exe`, which **outlived** the `dotnet test`
   call; the next build of that project then failed with `MSB3027 "Could not copy ...
   FusionRpg.Guard.Tests.dll ... The file is locked by: testhost"`, or the run died with `exit -1`.
   Reproduced twice on 2026-09-26. The port never lets a test spawn a build: `Runner._build` runs
   `dotnet build` **once per project** (memoized on the absolute project path) and every test then
   runs with `--no-build` — the shape `gk-core/scripts/test_sharded.py:273` already uses, and the same
   defect class `cold-process-test-build-20260912-e5b1` fixed for tool tests.
2. **PowerShell loses output silently.** `Write-Host` writes the INFORMATION stream, so `2>&1`
   captures *nothing* from a script that is working correctly (AGENTS.md "Language for new tooling").
   The port captures stdout AND stderr on every external call, refuses by NAME when a precondition
   fails, and takes a hard `--timeout` on each one.

**The plan is the contract, and it is unchanged.** The per-path owner selection, the selected checks,
the `full evidence: CI/nightly/release` line, the JSON plan shape and the exit codes are what agents
and downstream tools read. `gk-core/tests/tools/test_verify_change.py` proves that by running BOTH
implementations over the same inputs and failing if they disagree — the library over a planted
fragment, the planner over the real registry. Two implementations of one rule is the C4 defect, so it
is pinned rather than trusted.

**As of 2026-09-26 the PowerShell pair was still on disk, and that was a known, deliberate state.**
`guard-verification-boundaries.py` dot-sourced the retired `lib/VerificationBoundaries.ps1`,
`gk-fusion/scripts/deploy-play.py` invoked the retired `verify-change.ps1`, and four Guard test
classes used the PowerShell planner as their repo-root marker — none of which were in the porting
lane's fence, which is why deleting either file then would have broken the guard suite and CI. All
three have since moved: the guard imports the Python lib, the deploy shells
`gk-core/scripts/verify-change.py`, and the landmark classes point at the `.py`. See
`tasks/reports/verify-change-python-20260926.md` for the call list as it stood.

---

<details><summary>Original open questions, for the trail</summary>

## Open questions

None that are genuinely undecided at this phase — the owner's questions ("what caused this," "is
13,000+ tests itself the problem," "should we split the repo," and, after peer review, "does splitting
help compile time") are all answered above with measured evidence, not left open. Two real decisions
for the owner, sequencing only:

1. **Commission lever 1 (deepen the registry) now** — cheap, already proven, directly fixes what
   happened this session. Low risk either way if deferred, but there is no real reason to wait.
2. **Whether lever 3 (the `Core.Tests` split) is worth its one-time migration cost now, given the
   projected ~55-65% compile-time reduction per touched subsystem plus the architectural-enforcement
   value** — this is a real tradeoff (a multi-day-scale migration effort) against a real, now-measured,
   but moderate benefit. This doc takes no position on timing; it only insists the decision be made
   from the numbers above, not from "13,513 is scary" or "compile time obviously doesn't matter."

</details>

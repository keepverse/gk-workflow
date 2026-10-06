# Test verification boundary — capability map

**Status:** proposed 2026-09-18; owner ruling **R15** (CI edits approved) applied; adversarial
strengthen pass 2026-09-18 (§9); owner ruling **R24** (wire the two `tools/*.Tests` projects into
`ci.yml`) applied the same day — §7 item 4, §7.1 E7, §9 owner question 1. Contributor-tooling program; it adds, removes or changes no game loop. Ideal: [test-verification-boundary-ideal.md](test-verification-boundary-ideal.md)
(owner rulings **R-TV1** — split `FusionRpg.Core.Tests` now — and **R-TV2** — deepen the registry
now, not bundled with the split). Predecessor program, whose decisions this one keeps:
[verification-boundaries-map.md](verification-boundaries-map.md) §3 (path ownership is
authoritative, fail closed, only the runner builds commands, CI keeps full evidence).

This map specifies **only what is not built**. What is built is listed in §2 with its location, so
nobody re-specifies it.

## 1. Objective

A contributor who changes any path an agent routinely edits (C# production, C# tests, Python tools
and their tests, authored tuning, shared fixtures, generated trees) gets a verification plan that
(a) exists instead of `VERIFICATION BOUNDARY MISSING`, (b) names checks that genuinely exercise the
changed path, and (c) is as narrow as the evidence allows. Separately, `FusionRpg.Core.Tests`
becomes per-subsystem test projects (R-TV1), so the compiler enforces subsystem boundaries between
test code and a one-subsystem change compiles one small project.

## 2. Verified current state (2026-09-18)

> **Post-split update, 2026-09-23 (lane `tvb60`).** R-TV1 landed, so the readings in this section are
> historical where they describe `FusionRpg.Core.Tests` as one assembly — G10 below is the clearest case.
> What the tree holds now, measured: the manifest `gk-core/tests/core-test-projects.v1.json` declares **67**
> projects and **every one is applied** (the 68th, `GlobalUsings.cs`, is a `global using` alias set that
> cannot be a project — TVB-F17, declared out of the candidate model); the residual keeps the
> cross-candidate folders and the shared set lives in `gk-core/tests/FusionRpg.Core.Tests.Shared/` with
> `CoreTests.Shared.props`; `core` is a project **group** of all 68 on-disk Core test projects; the
> registry carries **463** boundaries and **137** projects; `gk-core/src/FusionRpg.Core/<Area>/**` resolves per
> area from the production map (**35** areas) instead of the whole-group fallback; and
> `guard-verification-boundaries.py --report` lists **8** orphan `VerificationId`s, **none `core.*`**.
> **Re-read at `213291c01` (lane `tvb60`), after the mega-merge brought other programs' rows:** the same
> measurements now read **475** boundaries, **141** projects, and **9** orphan `VerificationId`s — still
> **none `core.*`**. The ninth is `guard.unique-allocation-reader`, whose test never runs for the files its
> own allowlist polices; it is filed as `TVB-F33` (the fix shape needs a ruling — no `seam` boundary can
> carry a `verificationId`, so the additive option is whole-project).
> The rest of this section, §3–§7 and the §2 gap table remain the map's own contract — only the
> "one assembly" readings moved. Evidence: `tasks/evidence-fragments/tvb5-8-k-close.md`,
> `tvb6-2.md`, `tvb6-3.md`, `tvb-f17.md`, and the ideal's "R-TV2 execution — Core half done".

### Built — do not re-specify

| Capability | Where |
|---|---|
| Planner: explicit paths, session-scope check, most-specific owner + additive seams, fail on unmapped/ambiguous | `gk-core/scripts/verify-change.py:688` (session fence `:633`, unmapped throw `:771`, ambiguity `:779`, seams `:794-802`) |
| Runner: guards then `dotnet test` per selected project, `VerificationId` filter or the default-profile filter, stop at first failure | `gk-core/scripts/verify-change.py:1192` |
| Integrity guard: schema allow-list, project/guard files exist, unique owner patterns, `VerificationId` has a `[Trait]` in the named project, every `src/**/*.cs` has an owner | `gk-core/scripts/guard-verification-boundaries.py:34-93` |
| Depth reading (prints, asserts nothing) | `gk-core/scripts/guard-verification-boundaries.py:104-117` (`--report`) |
| CI runs the integrity guard in its own step | `gk-core/.github/workflows/ci.yml:435-441` |
| Default profile owns the one local filter; requires `-Project` or `-AllDefault` | `scripts/test_fast.py:24,59-61` |
| CI is unfiltered except BalanceGuard, asserted | `gk-core/.github/workflows/ci.yml:389-398` |
| Every `tests/**/*.Tests.csproj` appears in `ci.yml` or a named exemption | `gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs:35-71` |
| Text-based C# file mover with assembly-cycle refusal and dry-run default | `gk-core/tools/FileMove/Program.cs:5-11`, `gk-core/tools/FileMove/FileMover.cs:24-48` |
| R-TV2 production half for Data/Server/Launcher, the `launcher` re-point and `launcher-source-guards` seam | registry entries `data-*`, `server-*`, `launcher-*` (e.g. `data-fallback` at `gk-core/scripts/verification-boundaries.v1.json#data-fallback`, `launcher-fallback` at `:2301-2310`) |
| Core focused boundaries that already existed before R-TV2 | `battle-effect-math` (`:32`), `elemental-resolver` (`:561`), `core-lawn-attrition` (`:134`), `core-creature-catalog-generator`, `core-creature-corpus-dump`, `tools-combat-sim`, `tools-prove-predictor` |

### Gaps found by running the tools, not by reading docs

Each was reproduced with `verify-change.ps1 -PlanOnly -AllowUnscoped` or the `-Report` reading on
this commit. Counts below are **readings** from that run, printed for scale and never to be pinned
(`validation-ssot.md` §1).

| # | Gap | Evidence | Module |
|---|---|---|---|
| G1 | Six test roots have no owner: `E2E`, `AtomImporter`, `ItemSeedValidator`, `FileMove`, `PassiveTreeRosterGen` tests, and `gk-core/tests/FusionRpg.Bench`. An edit there is refused, and nothing fails until someone edits one | `verify-change` → `VERIFICATION BOUNDARY MISSING` for each csproj; the guard walks only `src/` (`guard-verification-boundaries.py:84`) | `registry-contract` |
| G2 | The matching tool trees are unmapped too: `gk-forge/tools/AtomImporter`, `gk-forge/tools/ItemSeedValidator`, `gk-core/tools/FileMove`, `gk-forge/tools/PassiveTreeRosterGen` | same planner refusal | `registry-contract` |
| G3 | `level` disagrees with the selector in three entries: `battle-effect-math` has a `VerificationId` but says `module`; `session-and-program-records` says `focused` and has none; `effect-catalog-drift` is `kind: seam` but says `focused` | `verification-boundaries.v1.json:597-615`, `:3460-3471`, `:1982-1993`; the guard checks only membership (`guard-verification-boundaries.py:67`) | `registry-contract` |
| G4 | Versioned tuning files are mapped by **exact** name, so every `gk-core/tools/tuning/publish.py` run (it writes `v{n+1}`, `publish.py:10`) produces an unmapped file. `power-scale.v1/v2`, `lawn-attrition.v3`-to-be, etc. — the entries are the defect, not the grammar: `pattern_match` accepts four shapes, one of them a final-segment wildcard, so a wildcard entry is already legal (`gk-core/scripts/lib/verification_boundaries.py:49-59`, `:104-119`) | `gk-core/scripts/lib/verification_boundaries.py:49-59`, `:104-119`; entries at `:727`, `:809`, `:835` | `registry-contract` (grammar), `seam-coverage` (entries) |
| G5 | **`gk-forge/tools/seedsmith/**` is unmapped** — the registry holds no boundary reaching it. The runner is no longer C#-only: a boundary whose project is a pytest project emits a `pytest` check (`gk-core/scripts/verify-change.py:468`, `:817-828`), one per project over the union of its selectors | planner output; `grep` of `gk-core/tests/FusionRpg.Guard.Tests` finds no `gk-core/tools/tuning` reference | `python-test-lane` |
| G6 | `gk-core/tools/tuning`'s own pytest files **do** run in CI — `gk-core/.github/workflows/ci.yml:502-508`, placed after the seedsmith lockfile install because pytest comes from it | `gk-core/.github/workflows/ci.yml:502-508` | `python-test-lane` — shipped |
| G7 | Generator `--check` and seedsmith corpus gates still run **only** in CI — `gk-core/.github/workflows/ci.yml:98`, `:108`, `:118`, `:129`, `:141`, `:466`, `:477`, `:483`, `:589`, `:599`, `:609`, `:619`, `:635`, `:654`, `:679`; a local change to a generated tree or its generator has no local lane for them | planner has no such check kind | `python-test-lane` (`seam-coverage` adds the three C# gates) |
| G8 | Most of `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**` and all of `gk-core/tests/fixtures/**` are unmapped (readings on this commit: 144 of 149, 2,215 of 2,234, 906 of 948, 79 of 79 files) | owner-pattern match over the trees | `seam-coverage` |
| G9 | `gk-core/tests/FusionRpg.Bench` is an `Exe`; `dotnet test` on it restores and **does not build**, exits 0 — so mapping it to a test project would be false evidence | ran `dotnet test gk-core/tests/FusionRpg.Bench/FusionRpg.Bench.csproj -c Release`: restore only, exit 0 | `registry-contract` (guard-only boundary + compile guard) |
| G10 | `FusionRpg.Core.Tests` is one assembly: 31 test-code folders (plus `TestSupport/` and `Goldens/`) and 45 root files (readings; the ideal's "26 subsystem folders" is an older reading), with one `[ModuleInitializer]` (`gk-core/tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs:43`), assembly-wide serialisation (`gk-core/tests/FusionRpg.Core.Tests.Shared/AssemblyInfo.cs:6`), and an `InternalsVisibleTo` grant to exactly that name (`gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:18`) | `ls`, the csproj | `core-split-*` |
| G11 | A `VerificationId` can span folders that the split will put in different projects: `core.battle-effect-math` is on `Combat/OwnerElementFallbackTests.cs` **and** `Battle/BattleEffectMathTests.cs`; a boundary names one `project` | `grep` of `Trait("VerificationId", "core.` | `core-registry-rekey` |
| G12 | Seven `core.*` traits have no boundary (`core.battle-mode-parity`, `core.kill-attribution`, `core.siege-estimator-parity`, `core.species-term-compose`, `core.species-passive-atoms`, `core.advanced-effect-clock`, `core.vocabulary-single-declaration`). The guard checks boundary→trait, never trait→boundary | same grep vs registry | `registry-contract` (reading), `core-registry-rekey` (entries) |
| G13 | `Data.Tests` is the measured burden, and one in-process run cannot parallelise its in-memory stores (`test-architecture-audit.md` §4-5); CI runs it as separate shard processes (`gk-core/.github/workflows/ci.yml:335`) and again under the leak alarm (`gk-core/.github/workflows/ci.yml:375`) | audits + CI | `data-tests-sharding` — shipped |
| G14 | **CLOSED 2026-09-19.** `release.yml` masked failures: its four `dotnet test` lines had no exit check between them, so only the last one decided the step. Every call now checks its own exit code (`gk-core/.github/workflows/release.yml:57-65` records why), and `WorkflowExitCheckTests.cs` holds the rule over every workflow file, so the pattern cannot return | read the file; `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` | `core-split-wiring` W0 — shipped |
| G15 | Two more boundaries point at a project that does not read their paths: `magic-number-audit` (`verification-boundaries.v1.json#magic-number-audit`, `gk-core/scripts/audit-magic-numbers.py`) and `tuning-publish-tool` (`:2550-2565`) both run **Guard.Tests**, and no Guard test reads either script. Their `magic-numbers` guard is the only honest check. Same defect class as G5 and the old Launcher mapping | `git grep audit-magic-numbers tests/` hits only a comment in Core.Tests | `registry-contract` C5 (`magic-number-audit` → guard-only), `python-test-lane` D4 (`tuning-publish-tool` → pytest) |
| G16 | `CiWiringGuardTests` walks only `tests/` (`CiWiringGuardTests.cs:52-56`), matches by substring (`:65`, so a path in a YAML comment satisfies it), and never reads `release.yml`. A new Core test project could be absent from the release gate with every guard green. Already true today: `gk-fusion/tools/LawnCombatObserver.Tests` and `gk-fusion/tools/ProveLiveProbe.Tests` appear in neither workflow | the test's own code; `grep` of both workflows | `core-split-wiring` W5–W7 |
| G17 | The split is not as mechanical as "move the folder" suggests. Readings on this commit: 25 source files in `gk-core/tests/FusionRpg.Core.Tests` declare a namespace their folder does not imply (`Atoms/EffectSeedFixtureOracle.cs` declares `FusionRpg.Core.Effects`; the other 24 are every file under `PassiveTree/tests-PassiveTree/`, which drop the `tests-PassiveTree` segment); 25 files locate repo files by walking `..` from `[CallerFilePath]`; `PassiveTree/GateCounters/GateCounterBoundaryGuardTests.cs:97` reads another test file by its literal `gk-core/tests/FusionRpg.Core.Tests/...` path | a namespace-vs-folder scan; `git grep CallerFilePath` | `core-split-analyzer` (reports), `core-split-apply` A2 (depth invariant) |
| G18 | `FileMove`'s `Apply` has no undo, and its `PlannedEdit` cannot express one: a moved file's edit carries the **source** text as `Before` (`gk-core/tools/FileMove/FileMover.cs:60`) and the source deletion is not an edit at all (`:113-115`). "Restore every `Before`" would write the source text to the destination and never restore the source | read the code | `core-split-apply` A4 |

### Pre-existing failures the new lanes will surface (not caused here, not hidden)

Measured 2026-09-18 on this commit:

- `gk-forge/tools/seedsmith/tests/test_actions_description_completeness.py` — **5 failures**, all in
  `RealCommittedCorpusCleanPassTests` (e.g. `act.attack` and `action.family.academic.004` lack a
  description). Because CI runs the whole seedsmith suite (`gk-core/.github/workflows/ci.yml:587`), that step is red for the
  same reason.
- `gk-forge/tools/seedsmith/tests/test_items_adapter.py` — **passes today.** `AGENTS.md` still lists it as
  failing on a clean HEAD; that line is stale (AGENTS.md is local-only, so this is reported to the
  owner rather than edited here).
- `gk-core/tools/tuning/test_resource_ownership.py::test_1_generation_reproduces_shipped_resource_edges_byte_for_byte`
  — fails, while `resource_ownership.py --check` passes against `aptitudes.v8.json`. **Diagnosed in the
  strengthen pass:** the test is stale, not the tool. It pins `version == 5`
  (`test_resource_ownership.py:38`) and `len(generated) == 166` (`:40`): both are **readings** (the
  latest published `aptitudes` version and the edge population), pinned against the validation rule.
  The contract half, `edge_triples(generated) == edge_triples(shipped)` (`:39`), passes against v8. The
  fix (drop the two pins, keep the equality) is `python-test-lane` step 0, and it lands before the CI
  pytest step (R15). The other 18 tests in `gk-core/tools/tuning` pass.
- `gk-core/scripts/mutate.py:347` refuses to run the `seedsmith` mutant set while that suite is red.

**How a lane behaves when a selected test is already red** is defined once, in
[`python-test-lane`](test-verification-boundary/spec-python-test-lane.md) D6, and applies to every
runner: the test always runs; CI is never filtered and stays red until the owning program fixes the
tree; locally, a failure counts as pre-existing only when a `knownRed` entry backed by a debt-ledger
row names it, every run prints it, and the entry fails the run the moment its test passes. No
deselect, skip marker or silent allowlist exists anywhere.

## 3. Decisions this map makes (technical, resolved here)

1. **Enforcement of `tests/**` is a hard failure from the day it lands** (the ideal left "hard vs
   ratchet" to this phase). The backlog is six project-level roots (G1), closed in the same change,
   so a ratchet would protect nothing.
2. **The registry file keeps its name. `schemaVersion` is the contract version, and one sequence
   covers both programs that edit it.** The planner already reads the field, not the file name
   (`gk-core/scripts/verify-change.py:358`), and the guard pins it (`guard-verification-boundaries.py:35`). A change
   that alters what a reader must understand bumps the version by one, in the same commit as planner
   and guard support. A stale copy of either script (another worktree) then refuses the file instead
   of misreading it. The sequence below is fixed here and cross-referenced from
   [solid-enforcement-map.md](solid-enforcement-map.md):

   | `schemaVersion` | Lands in | What a reader must now understand |
   |---|---|---|
   | 1 | today | `projects` (csproj strings), `guards` map, `boundaries` |
   | 2 | `solid-enforcement` **SE0.7** (`guard-runner`) | the `guards` section is **absent**; `boundaries[].guards` ids resolve through `gk-core/scripts/enforcement-registry.v1.json` |
   | 3 | `registry-contract` | last-segment wildcard, optional `project` (guard-only), project groups, derived `level` |
   | 4 | `python-test-lane` | object projects with `runner` ∈ {`dotnet`,`pytest`,`script`}, `testFiles`, `selfSelect`, `knownRed` |
   | 5 | `seam-coverage` | `full` level |

   SE0.7 goes first for two reasons. It is the smaller edit. And every guard this program adds
   (`bench-compile`) is then born as an enforcement-catalog row, not as a `guards`-map entry SE0.7
   would have to migrate. The cost is one dependency edge, `registry-contract` → SE0.7. Nothing else
   in this program waits on it (§4). `data-tests-sharding` and the Core-split modules change no
   registry field and bump nothing. Each bump also rewrites, in the same commit, the planted registry
   in `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`: the literal
   `"schemaVersion": 1` at `:200` and the `"guards"` map at `:202`. Renaming the file would touch every
   consumer, including other programs' specs, for no gain.
3. **Python tests are selected by file, not by `pytest -k`.** `-k` is a substring match over test
   names: a rename silently selects zero tests or extra tests. A file selector fails the integrity
   guard loudly when the file is renamed, which is the same guarantee the `[Trait]` check gives C#.
4. **Generator and corpus checks enter the planner as `script` checks, not as guards.** Each CI step
   gets one thin wrapper, `scripts/checks/gen-<id>.py`, registered as a `projects` entry with
   `"runner": "script"` and attached by owner or seam boundaries. The predecessor program forbids
   commands in JSON (`verification-boundaries-map.md` §3.5, §8), so a wrapper script is required.
   It is **not** a guard, because `solid-enforcement`'s catalog has a closed `tier` vocabulary,
   {`ci`,`local`} (`spec-enforcement-registry.md` R2). As `ci` rows, the runner would run each check a
   second time beside CI's own step. As `local` rows, `deploy-play` would run every generator check on
   every deploy. Neither fits a generator check, which proves a path, not a repo-wide invariant. (The
   first draft used `guard-gen-*.ps1`; the strengthen pass changed it for this reason.) The CI step
   and the wrapper hold the same command, and `GeneratorCheckCiParityTests` keeps them identical.
5. **The split keeps every namespace and every relative path.** New projects are direct children of
   `tests/` and set `RootNamespace` to `FusionRpg.Core.Tests`. Each file keeps its current path below
   the project directory. So no file's text changes, and every `[CallerFilePath]` `..` walk (G17)
   still lands on the same directory. The namespace-vs-folder mismatches that exist today (G17, 25
   files) are carried unchanged. That is why split mode never routes through `FileMover.Plan`, which
   would rewrite a mismatched file's namespace to match its folder (`gk-core/tools/FileMove/FileMover.cs:51-63`,
   `MovePlan.cs:54-61`).
6. **Test projects never reference test projects.** Shared test code is linked source through one
   shared `.props`, the pattern the Core.Tests csproj already uses for `DataTestStore.cs`
   (`FusionRpg.Core.Tests.csproj:51`). This is what makes the split an enforced boundary rather than a
   folder convention. No `ProjectReference` between test projects exists today.
7. **The split extends `gk-core/tools/FileMove`; it does not add a second mover** (SOLID "O"). The analyzer
   is a separate tool because it needs a semantic model and `FileMove` is text-only by design
   (`MovePlan.cs:42-45`).
8. **One Core test "project id" can mean several projects.** After the split, `core-fallback` must
   still run every Core test project, and `core.battle-effect-math` may need two. The registry gains
   project **groups** (`"core": [ … ]`) rather than a list field on every boundary — specified in
   `registry-contract` C7, because the first split increment cannot land without it.
9. **A pre-existing red test never masks a failure and never blocks an unrelated change.** The rule
   is defined in `python-test-lane` D6 and applies to every runner. The test always runs. CI is never
   filtered, so CI stays red until the owning program fixes the tree. Locally, a failure counts as
   pre-existing only if a `knownRed` entry names that exact test id and points at a `red`-kind row in
   the one debt ledger (`stub-register.md`). Every run prints each such failure. If the test
   **passes**, the run fails, so the entry has to be removed in the commit that fixes it. This is not
   the "frozen known-red allowlist" that `solid-enforcement` ruling 2 rules out: nothing is frozen,
   CI is untouched, and every entry has a named owner and a mandatory expiry. Where this program owns
   the fix, it fixes the test instead of registering it (`test_resource_ownership.py`, §2).

## 4. Capability map

| Module id | Responsibility | Depends on | Status |
|---|---|---|---|
| `registry-contract` | Integrity + planner contract additions: `tests/**` enforced root, test-project completeness, level coherence, last-segment wildcard, guard-only boundaries (+ `bench-compile` guard), project groups, orphan-trait reading, exact-path existence; closes G1–G3, G4 grammar, G9, G12 reading, G15 (`magic-number-audit`) | `solid-enforcement` SE0.7 (§3.2) | specified |
| `python-test-lane` | `pytest` and `script` runner kinds with file selectors; seedsmith and `gk-core/tools/tuning` boundaries; generator/corpus `--check` script checks; `knownRed`; the stale `gk-core/tools/tuning` test fixed, then the CI pytest step (G5–G7, G15 `tuning-publish-tool`) | `registry-contract` | specified |
| `seam-coverage` | Owner/seam entries for `gk-core/data/tuning/**`, `gk-core/tests/fixtures/**`, `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/**`, each root enforced only once fully mapped (G8) | `registry-contract`, `python-test-lane` | specified |
| `core-split-analyzer` | Read-only Roslyn report over `FusionRpg.Core.Tests`: per-folder coupling, cycles, required references, string-keyed inputs (R-TV1 step 1) | — | specified |
| `core-split-apply` | Manifest schema + `FileMove split` mode: creates projects, moves files, grants internals, builds and tests, reverts on failure (R-TV1 step 2) | `core-split-analyzer`, `registry-contract` (groups), owner-approved manifest | specified |
| `core-split-wiring` | Every consumer of the old project path: CI, release, `test-fast`, coverage/mutate/audit scripts, golden-attribution tools, solution file. W0 fixes `release.yml`'s masking (G14) before any increment | W0: none. The rest: `core-split-apply` (lands in the same increment) | specified |
| `core-registry-rekey` | Per-area Core production owners derived from an analyzer production map; re-key existing `core.*` boundaries and add the orphan ones (G11, G12) | `registry-contract`, `core-split-analyzer`, `core-split-wiring` | specified |
| `data-tests-sharding` | Class-namespace shard manifest with a remainder shard; concurrent-process runner with a per-run overlap check; CI + local module-run adoption (G13) | — | specified; CI edit approved (R15) |

```text
solid-enforcement SE0.7 ──► registry-contract ──► python-test-lane ──► seam-coverage
                                    │ (project groups)
                                    ▼
core-split-analyzer ─► [manifest checkpoint, §7.3] ─► core-split-apply ⇄ core-split-wiring ─► core-registry-rekey
core-split-wiring W0 (release.yml exit checks + WorkflowExitCheckTests): independent, lands first
data-tests-sharding: independent; its CI half is approved (R15)
```

`core-split-apply` and `core-split-wiring` land **together, one project at a time**: a new
`*.Tests.csproj` with no `ci.yml` line fails `CiWiringGuardTests` (`:45-71`), so they cannot ship
apart. The ideal's sequencing note holds: R-TV2 test-side work that keys on Core test locations
(`core-registry-rekey`) comes after the split; everything else (`registry-contract`,
`python-test-lane`, `seam-coverage`) keys on paths the split does not move.

## 5. Cross-program coupling

- **`solid-enforcement` / `enforcement-registry` + `guard-runner`**
  ([spec-enforcement-registry.md](solid-enforcement/spec-enforcement-registry.md),
  [spec-guard-runner.md](solid-enforcement/spec-guard-runner.md)). Both programs edit
  `gk-core/scripts/verification-boundaries.v1.json`, `gk-core/scripts/verify-change.py` and
  `gk-core/scripts/guard-verification-boundaries.py`. There is **one order, with no conditionals**. (The first
  draft said "a catalog row if that registry exists by then, else a `guards`-map entry": two shapes
  and no owner.)
  1. SE0.1–SE0.4 land first: the catalog (`gk-core/scripts/enforcement-registry.v1.json`, not on disk yet),
     its tests, and `run_guards.py`. SE0.3 maps the new files in this registry and changes no schema
     field.
  2. **SE0.7** removes the `guards` section and sets `schemaVersion` 2 (§3.2). Catalog ids must equal
     today's `guards` keys, all 12 of them, including `magic-numbers` and `session-boundary`.
     (`magic-numbers` was added today, together with the `magic-number-audit`, `tuning-publish-tool`
     and `deployment-hierarchy-tuning` boundaries.) If an id differs, SE0.7 renames it in
     `boundaries[].guards` in the same commit. From then on the planner runs guards through
     `run-guards.ps1 -Only`, which honours `status`: a `backlog` guard runs, reports, and never fails a
     verification.
  3. Then `registry-contract` (3), `python-test-lane` (4), `seam-coverage` (5).
     `guard-bench-compile.py` lands with a catalog row (`tier: ci`, `status: gating`), so CI runs it
     through the runner with no `ci.yml` edit. The generator checks are `script` runner projects, not
     guards (§3.4), so SE's R1 does not apply to them.
  4. A guard that `solid-enforcement` adds later and that verifies paths (e.g. SE2.1
     `tuning-immutability` on `gk-core/data/tuning/**`) is attached to boundaries by the module that creates
     it. Every later rewrite of those boundaries in this program keeps every guard the replaced entry
     carried.
- **`verification-boundaries`** (closed): its §7 already promised "a v1 registry may begin with the
  production roots it can prove, then add … tools, generated data". This map is that follow-through.

## 6. Out of scope, named

- **Injector tests.** `injector-tests-fallback` points at `guard` (`:661`), which does not compile
  `FusionRpg.Injector.Tests`. That project needs BepInEx interop to build at all (its csproj comment),
  so pointing the planner at it would fail on every machine without a game directory. The fix needs a
  skip-and-report runner mode like `guard-injector-compile.py`'s; the ideal defers Injector.
- **`DebugEndpoints.cs` focused mapping** — ideal: stays module-level until the file is split.
- **Web (`gk-web/web/fusion-rpg-web/**`).** Its validators are `npm test`/`vitest`, a separate adoption
  slice per the predecessor map §7.
- **Fixing the pre-existing red tests** listed in §2. The exception is `test_resource_ownership.py`:
  this program owns that fix, because R15's pytest step cannot land red (`python-test-lane` step 0).
- **`tools/**` as an enforced root.** Owners go only to the tool trees paired with a test project
  (G2) and to the generator trees (`python-test-lane` D5). The other `tools/*` probes and one-offs
  stay unmapped. An edit there is refused by the planner, which is visible, never silent, and
  `seam-coverage` S3 bars `full` for `tools/**`. Closing it needs a per-tool compile check, and the
  `script` runner makes that a data-only follow-up.

## 7. Owner rulings applied 2026-09-18 (R15, [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md))

1. ✅ **CI lines for new test projects — approved.** One `dotnet test` line per new project in `ci.yml`
   (and `gk-core/.github/workflows/release.yml:64-65`), the analyzer's test project, and a `gk-core/tools/tuning` pytest step, in the existing
   per-line exit-check pattern (`gk-core/.github/workflows/ci.yml:194-195`, the fix recorded at `:182-193`). The pytest step lands
   with the stale `test_resource_ownership.py` test fixed, never red.
2. ✅ **Data.Tests sharding in CI — approved.** `gk-core/.github/workflows/ci.yml:335` becomes the sharded runner; the remainder
   shard keeps the partition complete by construction.
3. **The split manifest** stays a gate with a stated default, not a question: after `core-split-analyzer`
   runs, one project per reference-clean folder group; everything else stays in a residual
   `FusionRpg.Core.Tests`. The owner reviews the manifest as a checkpoint.
4. ✅ **R24 — `gk-fusion/tools/LawnCombatObserver.Tests` and `gk-fusion/tools/ProveLiveProbe.Tests` into `ci.yml`: yes, both,**
   with exit checks; the CI wiring guard then covers `tools/`. Two `dotnet test` pairs (§7.1 E7), landing
   with `core-split-wiring` W7, whose exemption table therefore lands empty. Both projects were run
   2026-09-18 with no game directory set and passed; neither references interop, so neither is kept out.

### 7.1 The R15 edit protocol: every workflow line this program writes

Each module owns its lines, and the spec named below holds the exact text. The protocol has four
rules:

- **(a) Per-line exit check.** Every test invocation (`dotnet test …`, `python -m pytest …`,
  `python scripts/test_sharded.py …`) is followed on the very next line by
  `if ($LASTEXITCODE -ne 0) { throw "<name> failed" }`, in both workflows.
- **(b) The pattern is enforced by a test.** `WorkflowExitCheckTests` (`core-split-wiring` W0)
  asserts rule (a) over every `.yml` in `gk-core/.github/workflows`. It shipped with the
  `release.yml` fix (G14), so nothing here is a precondition any more.
- **(c) The no-filter assertion is never loosened.** No new line carries `--filter`, except a
  BalanceGuard line whose filter string is byte-identical to `gk-core/.github/workflows/ci.yml:176`. That keeps the no-filter
  assertion (`gk-core/.github/workflows/ci.yml:389-398`) true without editing it.
- **(d) Nothing lands red.** A line lands only in the commit that makes it pass locally.

As of 2026-10-02 the rows below are a **record of what R15 approved and where it landed**, not a
backlog: E1, E2, E3 and E4 are in the file; E5's per-project shape is in; E7 was withdrawn — see
the row.

| # | File · position | Line(s) | Owner spec |
|---|---|---|---|
| E1 | **shipped 2026-09-19.** `gk-core/.github/workflows/release.yml:64-199` — the exit check follows each of the 68 calls, and `--blame-hang-timeout` is `10min` | done | `core-split-wiring` W0 |
| E2 | **shipped.** `gk-core/.github/workflows/ci.yml:502-508`, between the seedsmith lockfile install (ends `:500`) and "Item seed reachability" (`:569`). pytest comes from the seedsmith lockfile (`requirements.lock:31`), so the step follows that install | done | `python-test-lane` §CI |
| E3 | **shipped.** `gk-core/.github/workflows/ci.yml:356-357`, after the FileMove pair (`:350-351`) | done | `core-split-analyzer` |
| E4 | **shipped**, as `python scripts/test_sharded.py` at `gk-core/.github/workflows/ci.yml:335` — the `test-sharded.ps1` this row named was ported away | done | `data-tests-sharding` H3 |
| E5 | `gk-core/.github/workflows/ci.yml:328-329` and `gk-core/.github/workflows/release.yml:198-199` | one pair per Core test project, manifest order, residual last | `core-split-wiring` |
| E6 | `gk-core/.github/workflows/ci.yml:176-177` | one BalanceGuard pair per Core test project that holds a `Category=BalanceGuard` trait | `core-split-wiring` |
| E7 | **withdrawn.** `gk-fusion/tools/LawnCombatObserver.Tests` and `gk-fusion/tools/ProveLiveProbe.Tests` cannot run in gk-core — the seven calls naming gk-forge and gk-fusion test projects were **removed** from this workflow because they could never have run here (`gk-core/.github/workflows/ci.yml:170-174`). Those repositories run their own solutions from their own CI | withdrawn | `core-split-wiring` W7 |

**Not in `release.yml`, deliberately:** E2, E3, E4 and E7. The release gate runs the Core test
projects only (`gk-core/.github/workflows/release.yml:54-199`), never the tool suites. It has no Python setup, and its
`Data.Tests` line stays a plain run, because its cost is not the burden R15 addresses. R15 approves
edits in both files. It does not require every approved line in both.

## 8. Design-gate record (`DESIGN-GATE.md` §5)

| Box | State |
|---|---|
| Subsystem | Contributor verification tooling; test project structure |
| Session boundary | `tasks/sessions/test-verification-boundary-spec-20260918.json` (docs only) |
| §1 row read | "Anything at all": `software-architecture.md` (§1, §10 guard table — its line for this guard says "every `src/**` file has an owner" and moves with `registry-contract`), `session-boundary.md` §1-2, `decisions.md` searched for verification/test locks (none cover this program) |
| Program docs read | the ideal, `verification-boundaries-map.md`, `testing-standard.md`, `test-burden-audit.md`, `test-architecture-audit.md`, `validation-ssot.md`, the two `solid-enforcement` specs above |
| Claims against code | every row in §2 cites the script/registry/CI line; G1, G2, G4, G5, G9 reproduced by running the planner or `dotnet test`; pytest failures reproduced by running pytest |
| Constraints tested | `dotnet test` on an `Exe` (G9); seedsmith and tuning pytest results; `resource_ownership.py --check` |
| Population pins | none — every count is labelled a reading |
| SOLID | extends the planner/guard/FileMove seams; no second planner, mover or registry; analyzer separate by responsibility |
| ActorHub / caches | not applicable (no actor magnitudes, no event-refreshed cache) |
| Strengthen pass | `tasks/sessions/strengthen-tvb-20260918.json`: every file:line in the map and the eight specs was re-checked against the tree, and the drifted ones were fixed (§9). `test_resource_ownership.py` was run and diagnosed. The Core.Tests namespace, `[CallerFilePath]` and BOM scans were run, and `FileMover.Apply`'s undo shape was read |

## 9. Strengthen pass — 2026-09-18

What the adversarial pass changed, so a reader of the first draft knows what moved:

- **One registry sequence with `solid-enforcement`** (§3.2, §5). SE0.7 goes first. Schema versions
  are 2 (SE0.7) → 3 → 4 → 5, not 2 → 3 → 4.
- **Generator checks are `script` runner projects, not `guard-gen-*.ps1` guards** (§3.4). SE's closed
  `tier` vocabulary would have run them twice in CI or on every deploy.
- **The R15 protocol is exact** (§7.1). `release.yml`'s masking (G14) is fixed first, and a test
  enforces the per-line pattern in both workflows.
- **Pre-existing reds** (§3.9): defined as `knownRed` plus a `red` ledger row, printed on every run and
  self-expiring. `test_resource_ownership.py` was diagnosed as two pinned readings, and it is fixed,
  not registered.
- **The Core split** (G17, G18): a depth invariant for `[CallerFilePath]`; split mode never rewrites
  a namespace; a string-keyed own-path literal is fixed before its increment; `Revert` works from an
  explicit create/modify/delete journal; files move byte for byte.
- **Sharding**: `FullyQualifiedName~` is a substring match, not a prefix match. Disjointness is now
  checked on every run from the result files, and completeness is proven by a set comparison, not by
  summing counts.
- **G15**: two more wrong-project mappings, `magic-number-audit` and `tuning-publish-tool`.
- **G16**: CI wiring now covers `release.yml`, `tools/*.Tests`, and a real invocation line rather than
  any substring. It found two `tools/*.Tests` projects that run nowhere (owner question 1).

### OWNER questions (strengthen pass)

1. ✅ **Ruled R24 (2026-09-18): yes, both, with exit checks; the CI wiring guard then covers `tools/`.**
   Applied in `core-split-wiring` W7 (exemption table empty) and §7.1 E7. Both build and pass without
   the game (verified 2026-09-18, no interop refs). The question as raised:
   ~~**Wire `gk-fusion/tools/LawnCombatObserver.Tests` and `gk-fusion/tools/ProveLiveProbe.Tests` into `ci.yml`?**~~ Both
   are real test projects that run in **no** workflow. Nothing noticed, because `CiWiringGuardTests`
   walks only `tests/` (G16). Adding their lines is a CI edit that R15 does not cover. **Default if
   unanswered:** they stay in the new W7 exemption table with this question as the reason. That is
   visible and no worse than today. The recommended answer is "yes, two `dotnet test` pairs in the
   §7.1 shape", because neither csproj records a reason to stay out of CI. Resolver: the owner.

Every other contradiction the pass found was technical, and each is resolved above with its SOLID
reason. One choice touches a ruling's wording: R15's pytest and analyzer lines go to `ci.yml` only,
not `release.yml`. §7.1 scopes it. R15 approves edits in both files; it does not require every line
in both.

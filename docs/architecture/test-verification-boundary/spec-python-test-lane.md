# Spec: `python-test-lane`

**Program:** [`test-verification-boundary`](../test-verification-boundary-map.md) · depends on:
[`registry-contract`](spec-registry-contract.md) (last-segment wildcard, guard-only boundaries,
derived `level`, `schemaVersion` 3) · closes map gaps G5, G6, G7, and the `tuning-publish-tool` half
of G15. It also owns the R15 `gk-core/tools/tuning` pytest step (map §7.1 E2) and the program-wide
pre-existing-red rule (D6, map §3.9).

## Objective

`verify-change.py` now runs pytest as well as `dotnet test`: a boundary whose project is a pytest
project emits a `pytest` check, one per project over the union of its selectors
(`gk-core/scripts/verify-change.py:468`, `:817-828`). What it **cannot** do is reach
`gk-forge/tools/seedsmith/**`, which no registry entry maps. Measured on this commit:

- any path under `gk-forge/tools/seedsmith/**` → `VERIFICATION BOUNDARY MISSING`;
- `gk-core/tools/tuning/publish.py` and `test_publish_add_key.py` → boundary `tuning-publish-tool`
  (`verification-boundaries.v1.json:2550-2565`) → `dotnet test` of **Guard.Tests**, which contains no
  reference to `gk-core/tools/tuning` — the check runs, passes, and proves nothing about the changed file;
- the generator `--check` and seedsmith corpus gates run only in CI
  (`gk-core/.github/workflows/ci.yml:98`, `:108`, `:118`, `:129`, `:141`, `:466`, `:477`, `:483`, `:589`, `:599`, `:609`, `:619`, `:635`, `:654`, `:679`), so a local change to a generator has no lane;
- `gk-core/tools/tuning`'s own pytest files now run in CI at `gk-core/.github/workflows/ci.yml:502-508` (map G6 — shipped).

Seedsmith is where most generated content comes from (the generated-seed hard rule: "fix the
generator and regenerate"), so a contributor changing it today either runs nothing or runs the whole
suite (`gk-core/.github/workflows/ci.yml:587`, the only invocation). This module gives Python a first-class lane with focused
selection and gives generators a local `--check` lane.

**User:** every session that edits seedsmith, `gk-core/tools/tuning`, or a `tools/*Gen` generator.

## Design

### Step 0 — fix the stale `gk-core/tools/tuning` test (lands first, alone)

`test_resource_ownership.py::test_1_generation_reproduces_shipped_resource_edges_byte_for_byte`
fails today. Diagnosed in the strengthen pass: it pins two **readings**. `version == 5` (`:38`) is
the latest published `aptitudes` version, and `len(generated) == 166 == len(shipped)` (`:40`) is the
edge population. The shipped file is `aptitudes.v8.json`, and the contract assertion
(`edge_triples(generated) == edge_triples(shipped)`, `:39`) passes against it, just as
`resource_ownership.py --check` does in CI (`gk-core/.github/workflows/ci.yml:98`).

Fix: delete the two pinned lines and keep the triple equality. The version under test is whatever
`load_shipped_resource_edges` resolves as the latest (`resource_ownership.py:204-205`), which is the
contract. It is a test-only edit, so no tuning file changes. Verified by
`cd gk-core/tools/tuning; python -m pytest . -q -p no:cacheprovider`: all tests green. On this commit that
is 18 passed and 1 failed before the fix (a reading). This is the "fix, don't register" half of D6,
because this program owns the step that needs it green.

### D1 — runner kinds

`projects` values become **string** (a `.csproj`, unchanged meaning), **array** (a group,
`registry-contract` C7), or an object:

```jsonc
"projects": {
  "seedsmith": { "runner": "pytest", "root": "gk-forge/tools/seedsmith", "tests": "tests" },
  "tuning-py": { "runner": "pytest", "root": "gk-core/tools/tuning",    "tests": "." },
  "gen-creature-species": { "runner": "script", "script": "gk-core/scripts/checks/gen-creature-species.py" }
}
```

`runner` is a closed vocabulary of three members: `dotnet` (implicit for a string), `pytest` and
`script`. The guard pins that membership, because adding a fourth is a reviewed change to the runner,
not data. A `script` project is an argument-free wrapper whose exit code is the verdict (D5). It is
**not** a guard (map §3.4). This change moves `schemaVersion` from `3` (set by `registry-contract`) to
`4` (map §3.2), in the same commit as planner and guard support, so a stale planner refuses the file
(`gk-core/scripts/verify-change.py:358`).

### D2 — file selectors, never `-k`

A boundary on a `pytest` project selects with `testFiles` (repo-relative, last-segment wildcard
allowed), never `verificationId`. A boundary on a `dotnet` or `script` project may not carry
`testFiles`, and a `script` project never takes a `verificationId`. The guard enforces the pairing,
and checks that every `testFiles` pattern matches at least one existing `test_*.py` file under
`<root>/<tests>`. `pytest -k` is not offered: it is a substring match over test names, so a rename
silently selects zero or extra tests, where a missing file fails the guard (map §3.3).

One more selector form: `"selfSelect": true` on an owner boundary whose every path lies under the
project's test directory. A changed file named `test_*.py` then selects **itself**. Any other changed
file under that directory (`conftest.py`, `fixtures/**`, a helper module) selects the **module** run
instead, because a conftest or fixture change can affect any test. Selecting a `conftest.py`
"itself" would collect nothing, and D3 treats exit 5 as a failure. The guard rejects `selfSelect`
anywhere else.

### D3 — runner behaviour

| Selected check | Command (built by the runner only) |
|---|---|
| pytest, focused (`testFiles` or a self-selected file) | `Push-Location <root>; python -m pytest <files, relative to root, sorted> -q -p no:cacheprovider --junitxml <temp>` |
| pytest, module (no selector) | `Push-Location <root>; python -m pytest <tests> -q -p no:cacheprovider --junitxml <temp>` |
| script | `& <script>` from the repo root; exit code is the verdict |

- `-p no:cacheprovider`: no `.pytest_cache` is written into the tree. That class of leftover already
  broke a Guard test (`LadderRestatementGuardTests.cs:126-140`).
- `--junitxml` goes to a per-run temp directory. D6 reads the result file, and the directory is
  removed in `finally` with a throwing delete (`testing-standard.md` R3).
- pytest exit code 5 ("no tests collected") is a **failure**. A selector that collects nothing is a
  registry defect, not a pass.
- Before the first pytest check, the runner runs `python -m pytest --version` in `<root>`. If that
  fails, it stops with "python test environment missing — install per AGENTS.md 'Seedsmith'". It
  never installs anything and never skips.
- Checks run in the existing order: guards, then tests, stopping at the first failure
  (`gk-core/scripts/verify-change.py:1192`). Guards run through `run-guards.ps1 -Only` since SE0.7.

### D4 — initial boundaries

| Boundary id | `paths` | project | selector | guards |
|---|---|---|---|---|
| `seedsmith-fallback` | `gk-forge/tools/seedsmith/**` | `seedsmith` | — (module) | — |
| `seedsmith-tests` | `gk-forge/tools/seedsmith/tests/**` | `seedsmith` | `selfSelect` (D2: `test_*.py` selects itself, anything else runs the module) | — |
| `seedsmith-<area>` for each adapter area with ≥1 importing test | `gk-forge/tools/seedsmith/seedsmith/adapters/<area>/**` | `seedsmith` | `testFiles` = test files (any depth under `tests/`) that import `seedsmith.adapters.<area>` | — |
| `tuning-publish-tool` (re-pointed) | `gk-core/tools/tuning/publish.py`, `gk-core/tools/tuning/test_publish_add_key.py` | `tuning-py` (was `guard`) | `testFiles: [gk-core/tools/tuning/test_publish_add_key.py]` | `magic-numbers` (kept, because a re-point never verifies less than before) |
| `tuning-resource-ownership` | `gk-core/tools/tuning/resource_ownership.py`, `gk-core/tools/tuning/test_resource_ownership.py` | `tuning-py` | `testFiles: [gk-core/tools/tuning/test_resource_ownership.py]` | — |

The `<area>` test lists are **derived, not guessed**. At build time, scan `gk-forge/tools/seedsmith/tests/**`
for `seedsmith.adapters.<area>` imports, review the list, and commit it as data. Readings on this
commit: `actions`, `creatures`, `dungeon`, `effects`, `items`, `structures` and `trees` each have
importing tests; `demons` has none and stays on the fallback, which is the honest answer. The
integrity guard re-checks that each listed file exists, not how many there are.

Areas outside `adapters/` (`briefkit`, `budget`, `corpus`, `metrics`, `pipeline`, `planner`,
`report`, `sampling`, `workflow`, …) stay on `seedsmith-fallback` in this module. The same
import-scan rule deepens them later without a design change.

### D5 — generator and corpus checks as `script` projects

There is one thin wrapper per CI step, `scripts/checks/gen-<id>.py` (new). Each runs exactly the CI
command from the CI working directory, takes no arguments, and fails loudly if its toolchain is
missing. Each is attached as a **seam** boundary with that `script` project, so it runs **in addition
to** the path's owner:

| Script project | Command | CI line | Seam paths (this module) |
|---|---|---|---|
| `gen-creature-species` | `dotnet run --project gk-forge/tools/CreatureSpeciesGen -- --check` | `gk-core/.github/workflows/ci.yml:108` | `gk-forge/tools/CreatureSpeciesGen/**` |
| `gen-family-expand` | `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` | `gk-core/.github/workflows/ci.yml:118` | `gk-forge/tools/FamilyExpandGen/**` (owner `familyexpandgen-tool` unchanged) |
| `gen-build-plan` | `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check` | `gk-core/.github/workflows/ci.yml:129` | `gk-forge/tools/CreatureBuildPlanGen/**` |
| `gen-passive-tree` | `dotnet run --project gk-forge/tools/TreeBinder -- --check` | `gk-core/.github/workflows/ci.yml:141` | `gk-forge/tools/TreeBinder/**` (owner `treebinder-tool` unchanged) |
| `gen-resource-ownership` | `python gk-core/tools/tuning/resource_ownership.py --check` | `gk-core/.github/workflows/ci.yml:98` | `gk-core/tools/tuning/resource_ownership.py` |
| `gen-fusion-recipe` | `python -m seedsmith.adapters.creatures.fusion.reconcile --check` | `gk-core/.github/workflows/ci.yml:654` | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/fusion/**` |
| `gen-items-gate` | `python -m seedsmith check --adapter items --gate ../../data/seed/items` | `gk-core/.github/workflows/ci.yml:589` | `gk-forge/tools/seedsmith/seedsmith/adapters/items/**` |
| `gen-creature-contract` | `python -m seedsmith creatures contract --audit` | `gk-core/.github/workflows/ci.yml:599` | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/**` |
| `gen-structure-contract` | `python -m seedsmith structures contract --audit` | `gk-core/.github/workflows/ci.yml:609` | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/**` |
| `gen-creature-report` | `python -m seedsmith report --gate --creature-dump ../../data/seed/creatures/_dump` | `gk-core/.github/workflows/ci.yml:619` | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/**`, `gk-forge/tools/seedsmith/seedsmith/report/**` |
| `gen-creature-metrics` | `python -m seedsmith creatures metrics --gate` | `gk-core/.github/workflows/ci.yml:635` | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/**` |
| `gen-creature-preflight` | `python -m seedsmith creatures preflight --skip-model` | `gk-core/.github/workflows/ci.yml:679` | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/**` |

`gk-forge/tools/CreatureSpeciesGen/**` and `gk-forge/tools/CreatureBuildPlanGen/**` have **no owner today**. This module
adds `creaturespeciesgen-tool` → `core` (module). The evidence is `FusionRpg.Core.Tests.csproj:50`,
which references the tool so that its cold-process tests run it. It also adds
`creaturebuildplangen-tool` → `gen-build-plan` (module). No test project references that tool, so its
own `--check` is the only honest proof. The same script projects attach to the **data** trees they
check in [`seam-coverage`](spec-seam-coverage.md).

**Known duplication, named with its fix:** each command exists twice, as the CI step and as the
wrapper. `GeneratorCheckCiParityTests` (new) asserts that every wrapper's command line appears in
`ci.yml` inside a step with the same `working-directory`, so the two cannot drift silently. Pointing
CI at the wrappers would remove the copy. That is a CI edit R15 did not cover, and it is not made here.

### D6 — a selected test that is already red (program-wide rule, map §3.9)

Readings from the strengthen pass on 2026-09-18:

- `test_actions_description_completeness.py` fails 5 tests, all in `RealCommittedCorpusCleanPassTests`.
  One of them (`test_automatic_backfill_makes_zero_model_calls_and_writes_nothing_when_all_done`)
  attempts a real model call and waits for the URL timeout before failing.
- `test_items_adapter.py` passes. The `AGENTS.md` note calling it pre-existing-failing is stale.
- `test_resource_ownership.py` is fixed by step 0, not registered.

The rule has five parts:

1. **Never deselect.** Every selected test runs. No skip marker, deselect list or `-k` exclusion is
   ever added to make a lane green. CI is untouched and unfiltered, so `gk-core/.github/workflows/ci.yml:587` stays red until
   the owning program fixes the tree.
2. **`knownRed` entries** (registry, `schemaVersion` 4) have the shape
   `{ "project": "seedsmith", "test": "tests/test_actions_description_completeness.py::RealCommittedCorpusCleanPassTests::test_every_real_committed_action_carries_provenance", "debt": "SR-nn" }`.
   The `test` value is the runner's own test id: the pytest node id relative to `root`, or the dotnet
   fully qualified name. Each `debt` names a row in `docs/architecture/stub-register.md` of the new
   kind **`red`**: *"a committed test that fails on a clean HEAD; the test is right and the tree is
   wrong"*. The row carries `owner` and `waits-on` like every row. A stale test is fixed, never
   registered, as step 0 shows.
3. **Outcome.** The runner reads the per-test result file (`--junitxml` for pytest,
   `--logger "trx;LogFileName=<temp>"` for dotnet). Then:
   - every failure is a `knownRed` test → the check passes, and each one is printed as
     `KNOWN RED (pre-existing) <test> -> <SR-id>`;
   - any failure that is not `knownRed` → the check fails;
   - any `knownRed` test that **passed** in this run → the check fails with
     `stale knownRed entry <test>: remove it and its red row`. The list can only shrink, and the fix
     commit must shrink it.

   A `knownRed` test that was not selected has no effect.
4. **Guard.** Every entry's `project` exists. The test's file exists under the project. Its `debt`
   resolves to a `red` row. The fields are the closed set {`project`,`test`,`debt`}. No test asserts
   how many entries exist.
5. **Accepted limit, stated rather than hidden.** A change that makes a `knownRed` test fail
   *differently* is not detected locally. That test already proves nothing until its owner fixes
   the tree. CI remains the full evidence.

The `red` kind is a reviewed vocabulary change. `StubRegisterTests` pins the kind set: `solid-enforcement`
SE0.8 moves the pin from 3 to 4 for `solid`, and this module moves it from 4 to 5 with its reason.
That lands after SE0.8, which Wave 0 ships alongside SE0.7 (map §3.2). The five initial entries point
at one `red` row owned by the seedsmith actions pipeline; its `waits-on` is the description backfill
for the committed action corpus.

## CI — map §7.1 E2 (R15, approved)

The step is inserted in `.github/workflows/ci.yml` between "Install seedsmith from the lockfile"
(ends `:321`) and "Item seed reachability (seedsmith)" (`:323`). It must follow the install, because
pytest comes from `gk-forge/tools/seedsmith/requirements.lock:31`. Exact text:

```yaml
      - name: gk-core/tools/tuning own tests (test-verification-boundary python-test-lane, R15)
        shell: pwsh
        working-directory: gk-core/tools/tuning
        run: |
          # pytest is installed by the seedsmith lockfile step above; this step must stay after it.
          python -m pytest . -q -p no:cacheprovider
          if ($LASTEXITCODE -ne 0) { throw "gk-core/tools/tuning's own test suite failed" }
```

- **Order of commits:** step 0 first (green locally), then this step, never together with an
  unverified fix. It is not added to `release.yml` (map §7.1).
- `CiPytestWiringTests` (new, Guard) asserts that every `pytest` project in the registry has a
  `python -m pytest` line in `ci.yml` under a step whose `working-directory` equals its `root`. It
  is the Python counterpart of `CiWiringGuardTests`, and it is what makes `tuning-py` unable to go
  unwired again.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/items/<file>.py -PlanOnly -AllowUnscoped -Format json
.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/tests/test_items_adapter.py -Session <id>
.\scripts\verify-change.ps1 -Paths gk-core/tools/tuning/publish.py -Session <id>
python gk-core/scripts/guard-verification-boundaries.py --report
.\scripts\checks\gen-items-gate.py
cd gk-core/tools/tuning; python -m pytest . -q -p no:cacheprovider                                  # step 0 proof
dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~VerificationBoundaryWorkflowTests|FullyQualifiedName~GeneratorCheckCiParityTests|FullyQualifiedName~CiPytestWiringTests|FullyQualifiedName~StubRegisterTests"
# seedsmith environment, once per machine (AGENTS.md "Seedsmith")
cd gk-forge/tools/seedsmith; python -m pip install -r requirements.lock; python -m pip install -e . --no-deps
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/tools/tuning/test_resource_ownership.py` | step 0: drop the two pinned readings (`:38`, `:40`) |
| `gk-core/scripts/lib/verification_boundaries.py` | project-kind resolution; `testFiles` expansion (sorted); `selfSelect` split; result-file parsing for D6 |
| `gk-core/scripts/verify-change.py` | pytest and script runner branches (D3); `knownRed` outcome (D6); accept `schemaVersion` 4 |
| `gk-core/scripts/guard-verification-boundaries.py` | object projects, runner vocabulary, D2 pairing rules, `selfSelect` rule, `testFiles` existence, `knownRed` rules |
| `scripts/checks/gen-*.py` | (new) twelve wrappers (D5) |
| `gk-core/scripts/verification-boundaries.v1.json` | `schemaVersion: 4`; two pytest and twelve script projects; D4/D5 boundaries; `knownRed` |
| `docs/architecture/stub-register.md` | `red` kind documented; one `red` row |
| `gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs` | kind pin 4 → 5, with the reason |
| `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs` | plan-shape cases; planted registry `schemaVersion` → 4 |
| `gk-core/tests/FusionRpg.Guard.Tests/GeneratorCheckCiParityTests.cs` | (new) |
| `gk-core/tests/FusionRpg.Guard.Tests/CiPytestWiringTests.cs` | (new) |
| `.github/workflows/ci.yml` | the E2 step |
| `docs/contributing/testing-standard.md` §6 | one paragraph: Python paths select through the same planner; the D6 rule |

## Code style

```powershell
function Invoke-PytestCheck($project, [string[]]$files) {
    $results = Join-Path ([IO.Path]::GetTempPath()) ("vb-pytest-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $results | Out-Null
    Push-Location (Join-Path $Root $project.root)
    try {
        & python -m pytest --version *> $null
        if ($LASTEXITCODE -ne 0) { throw "python test environment missing - install per AGENTS.md 'Seedsmith'" }
        $targets = if ($files.Count) { $files } else { @($project.tests) }
        & python -m pytest @targets -q -p no:cacheprovider --junitxml (Join-Path $results 'r.xml')
        if ($LASTEXITCODE -eq 5) { throw "pytest collected no tests for $($targets -join ', ') - registry selector defect" }
        return Resolve-KnownRed $project (Join-Path $results 'r.xml') $LASTEXITCODE   # D6
    } finally {
        Pop-Location
        Remove-Item -LiteralPath $results -Recurse -Force   # throws on failure, never caught
    }
}
```

## Testing

Guard tests assert the **plan** (`-PlanOnly -Format json`) and the D6 decision over **planted result
files**, not a pytest execution. CI's `Restore / test` step ends at
`gk-core/.github/workflows/ci.yml:364`, before the seedsmith environment exists at `:486`, so a Guard test
that shells out to pytest would fail in CI for an environment reason.

| # | Case (planted tree under `-Root`, throwing delete in `finally`) | Asserts |
|---|---|---|
| P1 | pytest project + `testFiles` boundary; change the mapped source | plan has one pytest check with exactly the expanded, sorted files |
| P2 | change a `test_*.py` under a `selfSelect` boundary | plan selects that file only |
| P2b | change `conftest.py` under the same boundary | plan selects the module run |
| P3 | `testFiles` pattern matching nothing | guard fails naming the pattern |
| P4 | `verificationId` on a pytest project / `testFiles` on a dotnet or script project | guard fails |
| P5 | `runner: "nose"` | guard fails (closed vocabulary of three, reason in the test) |
| P6 | the real registry | guard passes; `gk-forge/tools/seedsmith/**` and `gk-core/tools/tuning/**` resolve |
| P7 | `GeneratorCheckCiParityTests` | every `scripts/checks/gen-*.py` command line is in `ci.yml` under the same `working-directory` |
| P8 | `CiPytestWiringTests` | every pytest project has a CI step (fails today for `tuning-py` until E2 lands, which is why E2 lands in this module) |
| P9 | planted junit: only `knownRed` failures | check passes; `KNOWN RED` printed per entry |
| P10 | planted junit: one unregistered failure | check fails |
| P11 | planted junit: a `knownRed` test passed | check fails with `stale knownRed entry` |
| P12 | `knownRed` entry whose `debt` is not a `red` row / whose file is missing | guard fails |

Execution is proven once, locally, in Success criteria, with the pre-existing reds expected. No test
pins how many test files a boundary selects, how many seedsmith tests exist, or how many `knownRed`
entries there are.

## Boundaries

- **Always:** build every command in the runner; keep wrappers argument-free and byte-identical to
  the CI command; report red lanes as red; land step 0 before the CI step.
- **Ask first:** pointing CI at the wrappers (the D5 dedupe). It is outside R15.
- **Never:** `pytest -k`; a deselect or skip marker; a `knownRed` entry for a test this program owns
  (fix it); a `knownRed` entry with no `red` ledger row; installing packages from the runner; a
  generator command stored in JSON; registering a `gen-*` wrapper as a guard (map §3.4).

## Success criteria

- [ ] Step 0: `cd gk-core/tools/tuning; python -m pytest . -q` is fully green; the CI step lands after it and
      is green on its first CI run.
- [ ] `gk-forge/tools/seedsmith/**` and `gk-core/tools/tuning/*.py` resolve; none maps to Guard.Tests.
- [ ] Changing `gk-forge/tools/seedsmith/seedsmith/adapters/items/<file>.py` plans the items test files plus
      `gen-items-gate`, not the whole suite.
- [ ] Changing one seedsmith test file plans exactly that file; changing `conftest.py` plans the module.
- [ ] Run once locally: `verify-change.ps1 -Paths gk-forge/tools/seedsmith/tests/test_items_adapter.py` green;
      `…/test_actions_description_completeness.py` passes the plan with five `KNOWN RED` lines, and
      would fail if any sixth failure appeared.
- [ ] `scripts/checks/gen-*.py` wrappers exit 0 on a clean tree where CI's step is green.
- [ ] `schemaVersion` is 4 and both scripts accept it; P1–P12 green, verified with
      `.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>`.

## Open questions

None. The file selection vs `-k` choice, wrappers vs commands in JSON, script checks vs guards, the
CI-order constraint on test shape, and the pre-existing-red rule are technical, and each is resolved
above. The CI step was approved by R15.

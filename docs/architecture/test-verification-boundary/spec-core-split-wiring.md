# Spec: `core-split-wiring`

**Program:** [`test-verification-boundary`](../test-verification-boundary-map.md) · depends on:
W0 — nothing (lands first, alone); everything else — [`core-split-apply`](spec-core-split-apply.md),
**landing in the same commit as each apply increment** · R-TV1 · R15 (CI edits approved, map §7.1
E1, E5, E6) · **R24** (the two `tools/*.Tests` projects wired into `ci.yml`, map §7.1 E7) · closes map
gaps G14 and G16.

## Objective

Everything that names `FusionRpg.Core.Tests` by path must keep working after each increment moves
tests out of it, and must keep verifying at least as much. The failure this prevents is a quiet one:
a script that still points at the residual keeps passing, while the tests it used to run now live
somewhere it never looks.

Two workflow defects make that failure easier than it looks, so this module fixes them first:

- **`release.yml` masks failures today (G14).** Its four `dotnet test` lines (`release.yml:43-46`)
  have no exit check between them, so only the Launcher line decides the step. Adding more Core lines
  there without fixing that would add more lines whose failure nobody sees.
- **The wiring guard is weaker than its name (G16).** `CiWiringGuardTests` walks only `tests/`
  (`CiWiringGuardTests.cs:52-56`), accepts any substring (`:65`), so a path inside a YAML comment
  passes, and never reads `release.yml`. One real finding: `gk-fusion/tools/LawnCombatObserver.Tests` and
  `gk-fusion/tools/ProveLiveProbe.Tests` run in **no** workflow, and nothing reports it.

**User:** CI, the release gate, and every script a contributor runs against Core tests.

## W0 — workflow exit checks (lands first, independent of the split)

1. `release.yml:43-46`: after each `dotnet test` line, add
   `if ($LASTEXITCODE -ne 0) { throw "<project> failed" }`. Also align `--blame-hang-timeout 5min` to
   `10min`: `ci.yml:117-122` states the value must match `test.runsettings`' `TestTimeout` (10min),
   and the release gate is the one place it does not.
2. `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` (new), over both `ci.yml` and
   `release.yml`. It asserts that every line whose trimmed text starts with `dotnet test `,
   `python -m pytest ` or `python gk-core/scripts/test_sharded.py ` is immediately followed by a line matching
   `^\s*if \(\$LASTEXITCODE -ne 0\) \{ throw `. It is a contract assertion, with no line or step
   counts. One rule, one test, and it would have caught the `ci.yml` defect of 2026-08-24
   (`ci.yml:124-129`) and this one.

W0 is verified with
`python gk-core/scripts/verify-change.py --paths .github/workflows/release.yml,gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs --session <id>`.

## Consumers (verified by `git grep FusionRpg.Core.Tests` on this commit)

| Consumer | Today | After each increment |
|---|---|---|
| `.github/workflows/ci.yml:153-154` | one `dotnet test` pair for Core.Tests | one pair **per Core test project**, manifest order, residual last, exact shape below (map §7.1 E5). `CiWiringGuardTests.cs:45-71` fails the build until the line exists, which is why apply and wiring cannot ship apart |
| `.github/workflows/ci.yml:140-141` | BalanceGuard: `--filter "Category=BalanceGuard"` on Core.Tests | one pair per Core test project that holds a `Category=BalanceGuard` trait (today all four live in `Balance/`, a reading), same filter string **byte-identical**, so the no-filter assertion (`:210-219`) still exempts it (E6). **A filter that matches no test exits 0**, so this is the one consumer where a stale path fails silently: W6 guards it |
| `.github/workflows/release.yml:43` | Core.Tests in the release gate | one pair per Core test project, the same lines as `ci.yml` (E5) |
| `gk-core/scripts/test_fast.py:360` | Core.Tests in `--all-default`'s list | every Core test project (still the explicit broad option; the list stays in this one file, `:356-362`) |
| `gk-core/scripts/coverage.py:237`, `gk-core/scripts/mutate.py:455` | `--project` default `tests\FusionRpg.Core.Tests` | the default becomes the project that holds the namespace asked for; a mutant set (`gk-core/scripts/mutants/*.json`) whose tests moved names its project explicitly |
| `gk-core/scripts/audit_status_vfx_identity.py:87` | runs Core.Tests | the project holding the status/VFX identity tests |
| `gk-core/scripts/regen_class_system_baselines.py:105,416`, `gk-core/scripts/verify-golden-attribution.py:16,31` | path to `Battle/BattleGoldenTests.cs` | the moved path (the file content does not change) |
| `gk-core/scripts/verification-boundaries.v1.json` | `core` = one csproj; `core-tests-fallback` = `gk-core/tests/FusionRpg.Core.Tests/**` | `core` becomes a **group** (`registry-contract` C7) holding every Core test project, so `core-fallback` still runs all of them. Each new project gets a `projects` id and a module fallback over its directory (otherwise `registry-contract` C1 fails the guard). `gk-core/tests/FusionRpg.Core.Tests.Shared/**` → `core` group. **Every exact test path that moved is rewritten in the same increment**: today `:39-40`, `:103`, `:116`, `:150` and `:565`. `registry-contract` C8 fails the guard on a stale one |
| `FusionRpg.slnx:14` | one entry | one per project (written by the apply tool) |
| an own-path string literal in a test (e.g. `GateCounterBoundaryGuardTests.cs:97`) | reads another test file by its `gk-core/tests/FusionRpg.Core.Tests/...` path | fixed in its own commit **before** the increment (analyzer `BLOCKS SPLIT`), because a move never edits content |

The planner-side re-keying of focused `core.*` boundaries is **not** here. That is
`core-registry-rekey`, after the split.

## New guard tests

`gk-core/tests/FusionRpg.Guard.Tests/CoreTestProjectPolicyTests.cs` (new), reading
`gk-core/tests/core-test-projects.v1.json`:

| # | Asserts |
|---|---|
| W1 | every Core test csproj on disk is either a manifest project or the residual |
| W2 | each csproj's `ProjectReference`s ⊆ its manifest `references` (the declared dependency policy) |
| W3 | no `*.Tests.csproj` anywhere under `tests/` or `tools/` references another `*.Tests.csproj` |
| W4 | every manifest project name has an `InternalsVisibleTo` line iff `coreInternals` is true |
| W5 | every Core test csproj path appears in `ci.yml` **and** `release.yml` on a line whose trimmed text starts with `dotnet test <path>`. A comment does not count |
| W6 | the set of Core test projects holding a `[Trait("Category", "BalanceGuard")]` equals the set of projects named on `ci.yml` `--filter "Category=BalanceGuard"` lines (set equality both ways: no silent zero-match line, no unguarded project) |

`CiWiringGuardTests` gains one case. **W7**: every `*.Tests.csproj` under `tools/` also appears
in `ci.yml` on a line whose trimmed text starts with `dotnet test <path>` (the W5 rule — a comment does
not count), followed on the next line by its exit check, or is in its exemption table with a reason.
~~It lands with the two projects in that table, reason "not wired; owner question, map §9".~~
**Ruled R24 (2026-09-18): *"Yes, both, with exit checks; the CI wiring guard then covers `tools/`."***
W7 lands with an **empty** exemption table and these two pairs in `ci.yml`, "Restore / test (.NET)",
after the FileMove pair (`.github/workflows/ci.yml:180-181`) — map §7.1 row E7, rule (a) shape:

```powershell
dotnet test gk-fusion/tools/LawnCombatObserver.Tests/LawnCombatObserver.Tests.csproj -c Release --verbosity minimal --blame-hang --blame-hang-timeout 10min
if ($LASTEXITCODE -ne 0) { throw "LawnCombatObserver.Tests failed" }
dotnet test gk-fusion/tools/ProveLiveProbe.Tests/ProveLiveProbe.Tests.csproj -c Release --verbosity minimal --blame-hang --blame-hang-timeout 10min
if ($LASTEXITCODE -ne 0) { throw "ProveLiveProbe.Tests failed" }
```

**Verified 2026-09-18 (session `rulings-r20-r24-20260918`), without the game:** both projects build
and pass with `FUSIONRPG_GAME_DIR` / `FUSIONRPG_ML_GAMEDIR` unset — `dotnet test
gk-fusion/tools/LawnCombatObserver.Tests/LawnCombatObserver.Tests.csproj` passed (4 tests) and `dotnet test
gk-fusion/tools/ProveLiveProbe.Tests/ProveLiveProbe.Tests.csproj` passed (60 tests); the counts are readings, never
asserted. Neither needs interop refs: `LawnCombatObserver.csproj` references only `FusionRpg.Contracts`,
`ProveLiveProbe.csproj` only `FusionRpg.Contracts` and `FusionRpg.Server`, and neither test csproj has a
`HintPath` or a game-dir property. So **neither is kept out of CI**. Not in `release.yml`: the release gate runs the product test projects only, never
tool suites (map §7.1 *"Not in `release.yml`, deliberately"*); R24 names `ci.yml`. The pairs land in the
same commit as W7, so the case is green the day it exists (rule (d)); a future `tools/*.Tests` project
needs its own pair or an exemption row with a reason.

Membership, subset and set-equality checks only. No count of projects, files or tests.

## Code style

The exact pair for each Core test project, identical in `ci.yml` and `release.yml`:

```yaml
          dotnet test tests/FusionRpg.Core.World.Tests/FusionRpg.Core.World.Tests.csproj -c Release --verbosity minimal --blame-hang --blame-hang-timeout 10min
          if ($LASTEXITCODE -ne 0) { throw "FusionRpg.Core.World.Tests failed" }
```

And the BalanceGuard pair (only for a project W6 says holds the trait):

```yaml
          dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests/FusionRpg.Core.Balance.Tests.csproj -c Release --verbosity minimal --blame-hang --blame-hang-timeout 10min --filter "Category=BalanceGuard"
          if ($LASTEXITCODE -ne 0) { throw "balance-guard: a termination invariant or dominance-guard-mechanism test failed — see output above" }
```

## Commands

```powershell
python gk-core/scripts/verify-change.py --paths <moved + created + edited paths> --session <id>
dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~CoreTestProjectPolicyTests|FullyQualifiedName~CiWiringGuardTests|FullyQualifiedName~WorkflowExitCheckTests"
python gk-core/scripts/test_fast.py --all-default          # only at the last increment (AGENTS.md: finishing a large feature)
```

## Project structure

Every row of the consumer table, plus `gk-core/tests/FusionRpg.Guard.Tests/CoreTestProjectPolicyTests.cs`
(new), `WorkflowExitCheckTests.cs` (new, W0), the W7 case in `CiWiringGuardTests.cs`, and one
sentence in `docs/contributing/testing-standard.md` §6 naming the Core test projects as a group.

## Testing

W0 and W1–W7 above. Each increment is verified with `verify-change.py` over its exact paths; the full
default profile runs once, at the last increment (AGENTS.md "When the whole suite is actually the
right call", point 1).

## Boundaries

- **Always:** land W0 before any other workflow edit in this program; land each increment's CI,
  release and registry lines with it; keep BalanceGuard's filter string identical; make `core` a
  group before the first increment, so a Core production change never verifies less.
- **Ask first:** exempting any `tools/*.Tests` project from W7 (the table lands empty under R24).
  ~~Wiring `gk-fusion/tools/LawnCombatObserver.Tests` / `gk-fusion/tools/ProveLiveProbe.Tests` into CI~~ — ruled R24, wired
  by W7.
- **Never:** a wildcard or solution-wide `dotnet test` in CI to dodge listing projects (that is a
  separate CI design change, not this module's); an exemption in `CiWiringGuardTests` for a new Core
  project; a Core test line without its exit check.

## Success criteria

- [ ] W0: `release.yml` has an exit check after every test line; `WorkflowExitCheckTests` green on both
      workflows (and red on a planted workflow text missing one).
- [ ] After each increment: CI and release list every Core test project; BalanceGuard lines match W6;
      `test-fast --all-default` lists all of them; golden-attribution scripts find the moved file; no
      stale exact path in the registry.
- [ ] `verify-change.py` on a `gk-core/src/FusionRpg.Core/**` path plans every Core test project.
- [ ] W1–W7 and `CiWiringGuardTests` green.
- [ ] R24: `ci.yml` runs `gk-fusion/tools/LawnCombatObserver.Tests` and `gk-fusion/tools/ProveLiveProbe.Tests`, each followed
      by its exit check; W7's exemption table is empty.

## Open questions

None. The CI and release lines are approved by R15; wiring the two `tools/*.Tests` projects is
**Ruled R24** (map §9 owner question 1 closed) and lands with W7.

# Spec: `registry-contract`

**Program:** [`test-verification-boundary`](../test-verification-boundary-map.md) · depends on:
`solid-enforcement` **SE0.7** ([spec-guard-runner.md](../solid-enforcement/spec-guard-runner.md): the
`guards` section is gone, guard ids resolve through `gk-core/scripts/enforcement-registry.v1.json`, and
`schemaVersion` is 2 — map §3.2) · closes map gaps G1, G2, G3, G4 (grammar only), G9, G12 (reading
only), G15 (`magic-number-audit`), and provides the project groups the Core split needs (C7).

## Objective

The integrity guard today proves one thing about coverage: every `src/**/*.cs` has an owner
(`gk-core/scripts/guard-verification-boundaries.py:84-93`). Test code, tool trees and versioned tuning can
go unmapped with nothing failing until someone edits them and `verify-change.ps1` refuses
(`verify-change.ps1:83`). That is how `LawnQuickStartEndpointTests.cs` sat unmapped (ideal, "Wiring
gap"), and it is still true for six test roots today (map §2 G1).

This module makes the registry's **contract** strict enough that an unmapped test file, a test
project the registry has never heard of, a `level` that lies about the selector, or a tuning publish
all fail the guard — and it adds the two grammar features later modules need. It does **not** add
coverage for data trees (that is `seam-coverage`) or Python (that is `python-test-lane`).

**User:** every contributor who runs `verify-change.ps1`; the owner reading `-Report`.

## What changes

### C1 — `tests/**` becomes an enforced root (hard failure, from landing)

Extend the source walk (`guard-verification-boundaries.py:84`) to also walk:

- `tests/**/*.cs`
- `tools/*.Tests/**/*.cs` (today `gk-fusion/tools/LawnCombatObserver.Tests`, `gk-fusion/tools/ProveLiveProbe.Tests`)

excluding `bin/`, `obj/`, `TestResults/`. An unmatched file fails with `unmapped test source: <path>`.
Hard failure immediately, not a ratchet: the whole backlog is the six roots below, closed **in the
same change** (map §3.1).

(Five project ids and six roots: `gk-core/tests/FusionRpg.Bench` gets a boundary but no project id.)

| New `projects` id | Test project | New owner boundary (module level) | Tool tree it also owns |
|---|---|---|---|
| `e2e` | `gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj` | `e2e-tests-fallback` → `gk-core/tests/FusionRpg.E2E.Tests/**` | — |
| `atomimporter` | `gk-forge/tests/FusionRpg.AtomImporter.Tests/…csproj` | `atomimporter-fallback` | `gk-forge/tools/AtomImporter/**` |
| `itemseedvalidator` | `gk-forge/tests/FusionRpg.ItemSeedValidator.Tests/…csproj` | `itemseedvalidator-fallback` | `gk-forge/tools/ItemSeedValidator/**` |
| `filemove` | `gk-core/tests/FusionRpg.FileMove.Tests/…csproj` | `filemove-fallback` | `gk-core/tools/FileMove/**` |
| `passivetreerostergen` | `gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests/…csproj` | `passivetreerostergen-fallback` | `gk-forge/tools/PassiveTreeRosterGen/**` |
| — | `gk-core/tests/FusionRpg.Bench` (an `Exe`, no tests) | `bench` → guard-only (C5) with guard `bench-compile` | — |

Precedent for a tool and its tests sharing one boundary: `lawncombatobserver-fallback`,
`proveliveprobe-fallback`. Guards carried: `test-substrate` on all five test roots — it is the guard
that reads test sources (`E2E`'s `RpgApiFactory.cs` is baselined in its Group 2, the AtomImporter
lines in Group 4, `testing-standard.md` §7). `dal` is not carried: it scans `src/` only, so it proves
nothing about a test edit.

`PassiveTreeRosterGen.Tests` is held out of CI for a pre-existing content drift
(`ci.yml:169-172`, `CiWiringGuardTests.cs:38-41`). Mapping it locally is still correct: an edit to it
then runs it, and a red result is the honest answer.

### C2 — every test project is either registered or exempt with a reason

New rule: every `*.Tests.csproj` under `tests/` and `tools/` (excluding `bin/`/`obj/`) is a value in
`projects`, **or** listed in a guard-owned exemption table with a reason string. Initial exemption:
`gk-fusion/tests/FusionRpg.Injector.Tests/FusionRpg.Injector.Tests.csproj` — "needs BepInEx interop to compile;
see its csproj comment and map §6". Same shape and reason as `CiWiringGuardTests.cs:35-37`.

### C3 — `level` is derived, and the guard checks the derivation

| `kind` | selector present (`verificationId`, or `testFiles` once `python-test-lane` lands) | required `level` |
|---|---|---|
| `seam` | either | `seam` |
| `owner` | yes | `focused` |
| `owner` | no (with a `project`) | `module` |
| `owner` | no `project`, non-empty `guards` (C5) | `module` |

(`seam-coverage` S3 adds a fifth row later: `owner` with neither `project` nor `guards` → `full`.)

`level` stays in the file (the planner prints it, `verify-change.ps1:103`), but a mismatch fails the
guard. Fix the three entries that violate it today (map G3): `battle-effect-math` → `focused`,
`session-and-program-records` → `module`, `effect-catalog-drift` → `seam`. No selection changes —
only the label.

### C4 — last-segment wildcard

Pattern grammar gains one form: a `*` inside the **final** segment only, matching `[^/]*`
(e.g. `data/tuning/lawn-attrition.v*.json`). `/**` keeps its meaning; `*` elsewhere stays invalid.
Both `Matches` functions change together (`verify-change.ps1:38-41`,
`guard-verification-boundaries.py:23-26`); the path validator (`guard-verification-boundaries.py:16-22`) accepts the new form.

Specificity becomes an ordered pair: **(class, length)** with class `exact` > `wildcard` > `/**`,
then longer wins. Today it is length alone (`verify-change.ps1:79,84`); without the class rank an
exact file and a same-length wildcard would tie and raise `AMBIGUOUS`. The guard's report and the
planner must use the same rule — extract it to `scripts/lib/VerificationBoundaries.ps1` (new) and
dot-source it from both, so the two copies cannot drift (they are duplicated today).

### C5 — guard-only boundaries

`project` becomes optional **iff** `guards` is non-empty. The planner then emits no test check for
that path (`verify-change.ps1:97` stops being unconditional). The guard rejects a boundary with
neither. This exists for `gk-core/tests/FusionRpg.Bench`, whose only honest proof is "it still compiles":
`dotnet test` on that `Exe` restores and exits 0 without building (map G9, run on this commit), so
mapping it to any test project would be the same false evidence R-TV2 removed from the Launcher.

New guard `gk-core/scripts/guard-bench-compile.py` (ported from PowerShell 2026-09-26, contract unchanged): `dotnet build gk-core/tests/FusionRpg.Bench/FusionRpg.Bench.csproj
-c Release` into a temp `OutputPath` (the shape of `guard-injector-compile.py:30`), exit non-zero on
a compile error. The temp directory is removed in `finally`, and a failed removal fails the guard
(`testing-standard.md` R3). It needs nothing machine-specific, so it never skips. It is registered as
an enforcement-catalog row `bench-compile` (`tier: ci`, `status: gating`, `localReason: null`), so
SE's runner runs it in CI with no `ci.yml` edit, and `boundaries[].guards` names it by that id.

The second consumer of C5 is **`magic-number-audit`** (`verification-boundaries.v1.json:2485`). Its
paths are `gk-core/scripts/audit-magic-numbers.py` alone — it also listed a thin PowerShell wrapper, retired
2026-09-26 — and it names project
`guard` — but no Guard test reads either script (map G15). Its only honest check is its own guard,
`magic-numbers`. This module drops its `project`, so a change there runs the audit and nothing
pretending to test it. That is the same correction R-TV2 made for the Launcher, and it never
verifies less, because the guard stays.

### C6 — orphan-trait reading

`-Report` also prints every `VerificationId` trait value no boundary selects, grouped by project.
A **reading**, never a failure: `server.lawn-quick-start` is deliberately orphaned (ideal, "R-TV2
execution"). Today it would print the seven `core.*` orphans of map G12 plus that one.

### C7 — project groups (needed before the first Core split increment)

A `projects` value may also be an **array** of `.csproj` paths — a group, e.g.
`"core": ["gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj", "tests/FusionRpg.Core.World.Tests/…csproj"]`.
Every boundary keeps its single `project` field; the id may name a group.

- **Module selection on a group** runs every member, sequentially, each with the default-profile filter.
  This is what keeps `core-fallback` (`gk-core/src/FusionRpg.Core/**`, `verification-boundaries.v1.json:786`)
  verifying *all* Core tests while they move into new projects — a split increment must never make a
  Core production change verify less than before.
- **Focused selection on a group** runs only the members whose directory contains the
  `[Trait("VerificationId", …)]` — found by the same text scan the guard already performs
  (`guard-verification-boundaries.py:73-77`). The planner never runs a filter against a project that
  cannot match it, so the runner never depends on how `dotnet test` reports an empty filter.
- Guard: members exist, groups are flat (no group inside a group), members are `.csproj` only (a
  `pytest` project is never grouped), and a group-level `verificationId` matches a trait in ≥1 member.

Why here and not in a Core-specific module: it is a registry contract feature, and `core-split-apply`
cannot land its first increment without it (map §3.8).

### C8 — an exact pattern names a file that exists

<!-- citations-historical: the six exact Core test paths below were rewritten in place by
     core-split-wiring (C8) as the split's increments landed, so the pre-split line numbers name
     entries that no longer exist in that form. Re-pointing them would manufacture false precision. -->

Any owner or seam pattern that is neither `/**` nor a C4 wildcard must name an existing file. The
guard fails with `stale exact path: <boundary>: <pattern>`. Why: today a stale exact path matches
nothing and fails nothing, so the file it once named silently drops to a wider owner. The Core split
moves six such test paths (`verification-boundaries.v1.json:39-40`, `:103`, `:116`, `:150`, `:565`),
and C8 is what forces `core-split-wiring` to rewrite them in the same increment instead of leaving
them to rot. The tree is clean against C8 today: every exact path resolves. That was checked by
script in the strengthen pass, and it is a reading, not a pinned count.

### Contract version

C3, C4, C5, C7 and C8 change what a reader must understand, so this module moves `schemaVersion`
from `2` (set by SE0.7) to `3`, in the same commit as planner and guard support (map §3.2).
`verify-change.ps1:28` and the guard (`guard-verification-boundaries.py:35`) accept exactly `3`, so a
stale copy of either script refuses the file instead of misreading it.

## Commands

```powershell
python gk-core/scripts/guard-verification-boundaries.py            # contract; exit 1 on any failure
python gk-core/scripts/guard-verification-boundaries.py --report    # + depth and orphan-trait readings
.\scripts\verify-change.ps1 -Paths gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj -PlanOnly -AllowUnscoped
.\scripts\verify-change.ps1 -Paths gk-core/tests/FusionRpg.Bench/Program.cs -PlanOnly -AllowUnscoped
.\scripts\guard-bench-compile.ps1
dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "VerificationId=guard.verification-boundaries"
```

## Project structure

| Path | Change |
|---|---|
| `scripts/lib/VerificationBoundaries.ps1` | (new) `Test-PatternMatch`, `Get-PatternSpecificity`, `Resolve-Owner` — shared by planner and guard |
| `scripts/verify-change.ps1` | use the lib; guard-only boundaries emit no test check |
| `gk-core/scripts/guard-verification-boundaries.py` | C1 walk, C2 completeness + exemption table, C3 derivation, C4 grammar, C5 rule, C6 reading |
| `gk-core/scripts/guard-bench-compile.py` | (new; PowerShell form retired 2026-09-26) |
| `gk-core/scripts/enforcement-registry.v1.json` | one catalog row, `bench-compile` (C5) |
| `gk-core/scripts/verification-boundaries.v1.json` | `schemaVersion: 3`; five project ids, five boundaries plus `bench`, three `level` fixes, `magic-number-audit` loses its `project` |
| `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs` | new cases (Testing); its planted registry (`:200` `"schemaVersion"`) moves to `3` |
| `docs/architecture/software-architecture.md` §10 | guard line: "every `src/**` and `tests/**` source file has an owner" |
| `docs/contributing/testing-standard.md` §6 | one sentence: test sources are enforced like production sources |

## Code style

Follow the guard's existing accumulate-then-report shape (`$failures += …`, one exit at the end,
`guard-verification-boundaries.py:101`):

```powershell
foreach ($file in Get-EnforcedTestSources $Root) {
    $owner = Resolve-Owner $file $ownerBoundaries      # scripts/lib/VerificationBoundaries.ps1
    if ($null -eq $owner) { $failures += "unmapped test source: $file"; continue }
}
foreach ($csproj in Get-TestProjects $Root) {
    if ($registeredProjects -contains $csproj) { continue }
    if ($ExemptProjects.ContainsKey($csproj)) { continue }   # value = the reason, printed by -Report
    $failures += "test project not in registry: $csproj"
}
```

## Testing

Guard tests extend `VerificationBoundaryWorkflowTests.cs` and run the scripts against a **planted
tree under an explicit `-Root`**, exactly as its existing case does
(`VerificationBoundaryWorkflowTests.cs:186-222`). The filesystem is the subject here — the guard
walks directories — so a real temp tree is the permitted case (`testing-standard.md` R2), deleted in
`finally` with a throwing delete, never inside `catch { }`.

| # | Case | Asserts |
|---|---|---|
| T1 | a planted `tests/X.Tests/Foo.cs` with no owner | guard fails naming the file |
| T2 | a planted `tests/Y.Tests/Y.Tests.csproj` absent from `projects` and exemptions | guard fails naming it |
| T3 | an owner boundary with `verificationId` and `level: module` | guard fails |
| T4 | `data/tuning/foo.v*.json` owner + `gk-core/data/tuning/**` owner, path `data/tuning/foo.v3.json` | planner selects the wildcard owner |
| T5 | exact `…/foo.v2.json` + wildcard `…/foo.v*.json` on different owners | exact wins; no `AMBIGUOUS` |
| T6 | a `*` in a non-final segment | guard rejects the pattern |
| T7 | guard-only boundary | plan contains the guard and **no** `test` check |
| T8 | boundary with neither `project` nor `guards` | guard fails |
| T9 | the real registry | guard passes (existing `Integrity_guard_passes_on_the_current_registry`) |
| T10 | group `g` = two planted csprojs, trait only in the second; focused boundary on `g` | plan runs only the second member |
| T11 | module boundary on `g` | plan runs both members, default-profile filter |
| T12 | a group nested in a group / a pytest object in a group | guard fails |
| T13 | exact owner pattern naming a planted file, then the file deleted | guard passes, then fails with `stale exact path` |
| T14 | `schemaVersion: 2` registry against the new scripts | both refuse it |
| T15 | the real registry: plan for `gk-core/scripts/audit-magic-numbers.py` | one `guard` check (`magic-numbers`), no `test` check |

No test asserts how many files, projects, boundaries or orphans exist (populations). The six-root
backlog is closed by the real-registry case T9, not by a count.

## Boundaries

- **Always:** change planner and guard matching in the same commit, through the shared lib; keep
  the guard's output a list of named failures; update `software-architecture.md` §10 in the same change.
- **Ask first:** none — no CI edit (the guard's CI step is unchanged), no new package.
- **Never:** make `tests/**` enforcement a warning or ratchet; map `gk-core/tests/FusionRpg.Bench` to a test
  project; add a boundary that points at a project which does not compile the mapped path; add a
  `guards` section to the registry. It has been gone since SE0.7, which this module depends on, so a
  new guard is registered in `gk-core/scripts/enforcement-registry.v1.json`.

## Success criteria

- [ ] `verify-change.ps1 -PlanOnly` resolves every file under the six roots of C1 and the four tool trees.
- [ ] Planting an unmapped `tests/**/*.cs` file makes `guard-verification-boundaries.py` exit 1.
- [ ] A test csproj missing from the registry and the exemption table makes the guard exit 1.
- [ ] The three G3 entries carry derived levels; a mismatched `level` fails the guard.
- [ ] `gk-core/data/tuning/<domain>.v*.json` patterns resolve; exact beats wildcard beats `/**`.
- [ ] A change to `gk-core/tests/FusionRpg.Bench/**` runs `guard-bench-compile.py` and no `dotnet test`.
- [ ] `-Report` prints the orphan-trait reading; nothing asserts its size.
- [ ] A module boundary on a project group runs every member; a focused one runs only members holding the trait.
- [ ] A stale exact path fails the guard; the real registry passes C8.
- [ ] `schemaVersion` is 3 and both scripts accept only 3.
- [ ] T1–T15 green, verified with
      `.\scripts\verify-change.ps1 -Paths gk-core/scripts/guard-verification-boundaries.py,scripts/verify-change.ps1,scripts/lib/VerificationBoundaries.ps1,gk-core/scripts/verification-boundaries.v1.json,scripts/guard-bench-compile.ps1,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session <id>`.

## Open questions

None. The one decision the ideal deferred to this phase (hard failure vs ratchet) is made in C1 and
justified by the size of the backlog.

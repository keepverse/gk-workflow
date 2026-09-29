# TVB5.6 — `core` becomes a group; `CoreTestProjectPolicyTests` W1–W6; coverage/mutate default by namespace

## `core` becomes a project group (`registry-contract` C7)

`gk-core/scripts/verification-boundaries.v1.json`'s `"core"` entry changed from a bare string to a
one-element array (`["gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj"]`). C7 (the group
mechanism itself: `Get-ProjectMembers`, module-selection-runs-every-member, focused-selection-runs-only-
trait-holding-members) already landed in `TVB2.3`, merged in this session — this task only USES it: a
module check on a `gk-core/src/FusionRpg.Core/**` path already ran every Core test project before this line
(there was only one), and now it is structurally ready to keep doing that as each future
`core-split-apply` increment appends its new project's csproj to this same array — a Core production
change can never start verifying less partway through the split.

## `CoreTestProjectPolicyTests.cs` (new), W1–W6

Reads `gk-core/tests/core-test-projects.v1.json` and checks it against the real repo tree. Every case is
scoped to what **physically exists on disk today** — before `core-split-apply`'s first real increment
(`TVB5.7`) the only Core test project on disk is the residual, so W1/W2/W4 and 67 of W5's 68 manifest
projects pass vacuously; that is not a weaker test, since the same assertion starts checking a project
for real the moment an increment creates it, with no test edit required.

| # | What it checks | Result on today's tree |
|---|---|---|
| W1 | every `FusionRpg.Core.*.csproj` on disk is the residual or a manifest project | passes: only the residual exists |
| W2 | an existing manifest project's `ProjectReference`s ⊆ its manifest `references` | vacuous: no manifest project exists yet |
| W3 | no `*.Tests.csproj` under `tests/`/`tools/` references another `*.Tests.csproj` | passes for real, today, across the whole repo |
| W4 | an existing manifest project's `InternalsVisibleTo` line presence matches its `coreInternals` | vacuous: no manifest project exists yet |
| W5 | every existing Core test csproj is wired in `ci.yml` **and** `release.yml` via `dotnet test <path>` | passes: the residual is already correctly wired (pre-existing) |
| W6 | the set of projects holding `[Trait("Category","BalanceGuard")]` equals the set named on `ci.yml`'s `--filter "Category=BalanceGuard"` lines | passes: both sets are `{FusionRpg.Core.Tests}` today (the residual's own `Balance/` folder) |

W5 and W6 carry `[Trait("VerificationId", "guard.workflows")]` per the task's own acceptance note.
No count of projects, files or tests is asserted anywhere — membership/subset/set-equality only.

## `coverage.ps1` / `mutate.ps1` — `-Project` default resolves via the manifest

Both scripts' `-Project` parameter default changed from the hardcoded `tests\FusionRpg.Core.Tests` to
an empty sentinel, resolved at runtime:

- **`coverage.ps1`**: when `-Project` is not passed, derives the top-level folder from `-Namespace`
  (stripping the `FusionRpg.Core.` prefix, first remaining segment) and looks it up in the manifest's
  `include` patterns; falls back to the residual for a namespace the manifest does not name (e.g. a
  residual candidate like `World`/`Battle`, or a namespace outside `FusionRpg.Core`). An explicit
  `-Project` always overrides (the existing `-Namespace FusionRpg.Data` example in the doc header is
  unaffected — it already passes `-Project` explicitly).
- **`mutate.ps1`**: resolved **per mutant set**, since one invocation can run several sets. A set's own
  JSON gains an optional wrapper shape, `{ "project": "...", "mutants": [...] }` — an explicit override
  for "a set whose tests moved" (the task's own acceptance wording) — read by the same loader
  (`Get-MutantSetContent`) that still accepts every existing set's bare-array shape unchanged. With no
  override, the project is resolved from the set's first non-Python mutant's `file` path the same way
  `coverage.ps1` resolves a namespace. The baseline check now runs once per **distinct** resolved
  project actually needed (today, always exactly one: the residual), rather than assuming every set
  in one run shares a single project.

Both scripts still parse (`[System.Management.Automation.Language.Parser]::ParseFile`, zero errors) and
were verified with an isolated harness (no real `dotnet test`/`pytest` run needed to prove routing
logic that itself makes no test-runner call):

| Namespace / mutant file | Resolves to | Why |
|---|---|---|
| `FusionRpg.Core.World`, `FusionRpg.Core.World.Ai`, `FusionRpg.Core.Battle` | `tests\FusionRpg.Core.Tests` | residual candidates, not in the manifest's `projects` array |
| `FusionRpg.Core.Atoms` | `tests\FusionRpg.Core.Atoms.Tests` | a real manifest project |
| `FusionRpg.Core.Match` | `tests\FusionRpg.Core.Match.Tests` | a real manifest project |
| `FusionRpg.Core.GlobalUsings` | `tests\FusionRpg.Core.GlobalUsings.Tests` | a real manifest project (root-file candidate) |
| `FusionRpg.Data` (non-Core) | `tests\FusionRpg.Core.Tests` | unchanged fallback, matching today's exact behavior |
| real `gk-core/scripts/mutants/world-ai.json` (bare array, targets `World/Ai`) | `tests\FusionRpg.Core.Tests` | identical to today's hardcoded default — **behavior-preserving for every set on disk** |
| a synthetic object-wrapped set targeting `Atoms/**`, no override | `tests\FusionRpg.Core.Atoms.Tests` | proves the manifest lookup for the new wrapper shape |
| a synthetic set with an explicit `"project"` field | that field verbatim, ignoring the folder lookup | proves the override path |
| any set, with the caller's own `-Project` passed | the caller's value, ignoring both the set's field and the folder lookup | explicit always wins |

Every mutant set currently on disk (`lawn-combat`, `loam-calc`, `loam-texture`, `seedsmith`,
`status-derived`, `warden-contracts`, `world-ai`, `world-turn`) is the bare-array shape and resolves to
the exact same project it ran against before this change — **zero behavior change today**, ready for
the first time a set's tests actually move. A full live `mutate.ps1 -Set world-ai` run (55 mutants,
each requiring two full-suite passes) was not run as part of this verification: the new routing logic
makes no test-runner call itself, so it is provable in isolation, and re-proving `Invoke-DotnetSuite`'s
own (unmodified) mutation-apply/restore loop is outside what this task changed.

## `docs/contributing/testing-standard.md` §6

One paragraph added, naming the Core test projects as a `core` project group per `registry-contract`
C7, per the task's own file list.

## Verification

| Criterion | Command | Result |
|---|---|---|
| Build | `dotnet build gk-core/tests/FusionRpg.Guard.Tests -c Release -v q` | exit 0, 3 pre-existing warnings unrelated to this change |
| Registry JSON valid | `python -c "import json; json.load(open('gk-core/scripts/verification-boundaries.v1.json'))"` | valid |
| Registry integrity guard | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK`, exit 0 |
| Focused Guard run (spec's own Commands line) | `dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~CoreTestProjectPolicyTests\|FullyQualifiedName~CiWiringGuardTests\|FullyQualifiedName~WorkflowExitCheckTests"` | 15/15 passed |
| PowerShell syntax | `[System.Management.Automation.Language.Parser]::ParseFile` on both edited scripts | zero errors, both |
| Resolution logic (isolated harness, no live test run) | see table above | all 9 cases correct |

`VerificationBoundaryWorkflowTests`/`verify-change.ps1` cross-check not run, same reason as TVB5.5:
that class spawns `verify-change.ps1` per test and times out under current machine load regardless of
the change under test.

Files: `gk-core/scripts/verification-boundaries.v1.json` (`core` → group), `gk-core/tests/FusionRpg.Guard.Tests/CoreTestProjectPolicyTests.cs`
(new), `scripts/coverage.ps1`, `scripts/mutate.ps1`, `docs/contributing/testing-standard.md`.

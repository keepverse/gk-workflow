# Evidence — RS-F8's pre-read and RS7's re-measurement (two blocked rows, narrowed with their readings)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`), head `90eea1c15`. Both rows are blocked on fences this lane does not hold; what this
increment adds is the reading each owner needs, so neither fix is a guess and neither lane re-lands work that
already exists.

## RS-F8 — the Guard boundary test's budget: the fix is a FLAG, not a re-architecture

| Criterion | Read | Result |
|---|---|---|
| The test re-runs a walk its own subject does not need | `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs:41-42` | `RunBoundaryGuard` calls the guard with `-Root` only — **no `-SkipCoverageWalk`**; the budget is that helper's `120_000` ms (`:38`), and P6's subject is registry **resolution** |
| The cost is documented by the guard itself | `gk-core/scripts/guard-verification-boundaries.py:8-18` | *"measured: this walk, not process startup, is what made a 2-path `--plan-only` call take 415s under 22 concurrent dotnet.exe hosts"* — which is why `verify-change.ps1` passes `--skip-coverage-walk` on its internal pre-check |
| Passing the flag would NOT drop the completeness invariant | `ci.yml` (the guard's own step) + `VerificationBoundaryWorkflowTests.cs:340-341` | CI runs the guard unfiltered in its own step (`ciEntry: own-step`), and the same file has a planted-tree test asserting *"guard accepted an unmapped test source file"* — so the invariant has two independent homes |
| Why this lane cannot apply it | the fix is in the protected `gk-core/tests/FusionRpg.Guard.Tests/**` tree | filed for the owning program |

## RS7 — the CI lane: the fast lane is ALREADY wired, and the literal gap is one clause

| Acceptance clause | Read | Result |
|---|---|---|
| "the fast in-process scenarios run in CI **with their exit check**" | `.github/workflows/ci.yml:333` | `dotnet test gk-core/tests/FusionRpg.E2E.Tests/… -c Release` + `if ($LASTEXITCODE -ne 0) { throw … }` — **met**; the in-process scenarios are tests in that project |
| "the real-process scenarios get … a lane … that **claims no live game slot**" | same step passes no `--filter`; `ci.yml:352-368` asserts CI stays unfiltered (only BalanceGuard is filtered) | the `DiskSemantics`-tagged `RpgSimProcessHostTests` run in CI, and a headless server process claims no game-pool slot — **met in substance**; the clause's literal "**running the tool**" is not (no step invokes the CLI) |
| "the runner stays a tool and only its pure parts are referenced by the suite" | `gk-core/tools/RpgSim/RpgSim.csproj` | no `ProjectReference`, no `PackageReference`; the E2E project references IT — **met** |
| "the first CI run of the new step is green; `CiWiringGuardTests` completeness holds" | there is no new step | **moot** until the manager rules on the gap above |

**The ask, stated as an erratum rather than a lane's call:** either the E2E project's unfiltered CI step IS the
real-process lane (the tool is exercised through the E2E tests' own `ProcessHost` use, and RS-F6 decided the CLI is
a real-process front end driving that same code), or the CLI itself must be invoked by a scheduled/labelled step —
in which case RS7 waits on `.github/workflows/**`, outside this lane's paths, plus the `CiWiringGuardTests` row
for that step.

**Why this is worth a commit rather than a note:** the RS-F9 erratum cost the manager a ruling and nearly spawned a
lane to redo merged work, because a row's summary of what is wired was read instead of the wiring. RS7's summary
said "the CI lane" was unbuilt; the tree says its fast half is built and its real-process half runs unfiltered.

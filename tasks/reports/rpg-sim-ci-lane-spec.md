# Evidence — `sim-ci-lane`'s contract written (RS7's last unclaimed deliverable)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). The map's module-9 Spec cell read **NOT WRITTEN — RS7 is open and owns it**, and RS7's
own re-measurement (previous segment) showed the fast lane is already wired. So the deliverable this lane *can*
land is the contract the workflows fence is waiting for: `docs/architecture/rpg-simulator-spec-sim-ci-lane.md`.

| Criterion | Command | Result |
|---|---|---|
| The fast lane really is wired, with an exit check | `sed -n '333p' .github/workflows/ci.yml` | `dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj -c Release … ` followed by `if ($LASTEXITCODE -ne 0) { throw "FusionRpg.E2E.Tests failed" }` |
| The real-process tests really do run there, unfiltered | `grep -n "DiskSemantics\|Category!=\|filter" .github/workflows/ci.yml` | no filter on the E2E step, and `ci.yml:352-368` *asserts* CI stays the unfiltered full profile (only BalanceGuard is filtered) |
| The runner really is a tool | `grep -n "ProjectReference\|PackageReference" gk-core/tools/RpgSim/RpgSim.csproj` | no matches — and the E2E project references IT |
| The wiring is guarded for test projects, and NOT for tool steps | read: `gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs:37-60` | `Every_test_project_under_tests_appears_somewhere_in_ci_yml` walks `tests/**/*.Tests.csproj`; nothing asserts a `dotnet run --project gk-core/tools/RpgSim` line exists — the hole a shape-(b) choice would open, named in the spec |
| The spec exists, is indexed, and every citation resolves | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | exit **0**; `D1 683 (0 HIGH)`, `D2 7 (0 HIGH)`, `D3 ambiguous basename 56 (0 HIGH)` — unchanged, so the new document adds no broken citation |
| The map no longer says the module's contract is missing | read: map module row 9 | the Spec cell now names `rpg-simulator-spec-sim-ci-lane.md` (a sibling, per the file-prefix fence — RS-F5), and the "NOT WRITTEN" bullet now lists one row (`shared-store-home`) instead of two |
| Nothing else regressed | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | exit **0** — `GUARDS OK - 25 guard(s) run, 0 red` |

**What the spec records, in one paragraph each.** The **fast lane** is the E2E project and the contract is
negative: the step stays unfiltered and a new scenario lands in that project, because a scenario IS an E2E test by
another name (C3 (c)'s own words). The **slow lane** is the clause in question: today `RpgSimProcessHostTests`
boots a real server through `ProcessHost` inside the same unfiltered step, which satisfies the intent and not the
letter ("running the tool"), and the spec lays out both shapes with their cost — **(a)** the E2E step IS the lane
(nothing to build; the CLI's `--host process` path is the same `ProcessHost` code the test drives, per RS-F6), or
**(b)** a labelled step running the CLI, which needs a `ci.yml` edit *plus* a wiring assertion of its own. It does
not choose: the choice is the manager's erratum, which RS7's row carries. **"Claims no live game slot"** is
defined mechanically — a headless server process, never the game/injector/browser, so the game pool and the
three-slot live-probe protocol do not apply — and the fact that makes (b) cheap is CS-F3: a fresh data dir
self-heals, so the lane needs no provisioning step.

**Why this is worth a commit.** It is the last "NOT WRITTEN" cell this lane can fill (module 6's premise is
retired and needs a manager ruling), and it turns RS7 from "build the CI lane" — which a lane might start by
building the fast lane that already exists — into a two-option erratum with its cost measured.

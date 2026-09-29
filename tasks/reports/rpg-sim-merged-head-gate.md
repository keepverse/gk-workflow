# Evidence — the merged head's gate, run on the commit that accepted this lane (RS-F20 re-shaped; RS-F23, RS-F24 filed)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`), head `61d67f4cf` — *"merge(cmdc/sim-t3-2): accepted lane (5 commit(s))"*, i.e. the
commit on `features/mega-merge` that took this lane's work. RS-F20 was filed from a break this lane had to
repair; this run re-measures the head and **corrects the finding's shape**.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The merged head's own gate, run in full | `pwsh -NoProfile -ExecutionPolicy Bypass -File .claude/cmdc-agents/scripts/post_merge_check.py` | `build_exit=1 error_lines=1776 projects_with_errors=1`; the one project is `FusionRpg.Injector.BepInEx.csproj`, **excluded by the script by name** (needs a game dir), so the build verdict is OK; then `=== VERDICT: RED -- guards ===` | `.claude/cmdc-agents/scripts/post_merge_check.py` |
| The Guard suite on the merged head | same run | `Failed: 2, Passed: 671, Total: 673` (8 m 16 s) | — |
| Red 1, with its cause | `grep -A6 CiPytestWiringTests .tmp-post-merge-guards.log` | `pytest project root(s) with no 'python -m pytest' CI step at that working-directory: .` — the registry's `tools-audit-tests` row is `{runner: pytest, root: ".", tests: "gk-core/tests/tools"}` and `gk-core/tests/tools/test_audit_program_pipeline.py` exists, while `ci.yml`'s three pytest steps run at `gk-core/tools/tuning`, `gk-core/tools/ip-censor` and `gk-forge/tools/seedsmith` | **RS-F23** |
| Red 2, with its cause | same | `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary` → the actual set carries **`picks.source-below-rank-floor`**, a tenth code the guard's pin does not have | **RS-F24** |
| Why the gate was not run before acceptance | read: `.github/workflows/ci.yml:4-9` | `on: push: branches: [main, master]` and `pull_request: branches: [main, master]` — a merge into `features/mega-merge` is **never CI'd**, even though CI does build and test the E2E project (`ci.yml:333` with its own exit check) | `.github/workflows/ci.yml` |
| The tier this lane owns, as a contrast | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | **`GUARDS OK - 25 guard(s) run, 0 red`** | — |

**The corrected shape of RS-F20.** Its acceptance was written as a rule for lanes to remember ("a lane that adds
a required parameter … also updates every test assembly's bootstrap"). The measurement says something stronger
and more useful: the merged head's gate **exists**, it **works** (it caught two other lanes' reds on this head,
and it would have caught the `CS7036` arity breaks RS-F20 is about), and **it was not run** — because the
integration branch is outside CI's trigger set and `post_merge_check.py` is a manual step whose verdict is
recorded nowhere the next lane sees. A rule to remember is not a gate; the gate is already there and needs to
be wired to the merge, not restated in a todo.

**What this run does NOT prove.** `post_merge_check.py` also runs two `-TestProject` defaults
(`gk-core/tests/FusionRpg.Core.Lawn.Tests`, `gk-core/tests/FusionRpg.Core.LawnCoordMathTests.Tests`); its `VERDICT: RED` came
from the guards, so those two projects' results are not what this fragment reports. It is not a substitute for
a lane's own acceptance, and it is not the full suite.

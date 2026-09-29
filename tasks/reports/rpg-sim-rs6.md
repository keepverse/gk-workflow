# Evidence — rpg-simulator RS6 (`shared-store-home`) — BLOCKED, with the measurement

Lane `sim-runner`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-runner`
(branch `cmdc/sim-runner`). Module `shared-store-home`. **Not done, and not attempted.**

| Claim | Command | Result |
|---|---|---|
| The helper's home and its consumer population | `ls gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs`; `grep -rln DataTestStore tests/ --include=*.cs \| wc -l` | the file is `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs`; **314** test files reference it, across Data, Core, Core.Match, Server and E2E test projects |
| The move needs paths outside this lane's fence | compare the list below against the lane's allowed paths | 5 of the 6 needed paths are denied |

Paths a move needs, against this lane's allowed set
(`gk-core/tools/RpgSim/**`, `gk-core/tests/fixtures/rpg-scenarios/**`, `gk-core/tests/FusionRpg.E2E.Tests/**`,
`tasks/rpg-simulator-todo.md`, `tasks/rpg-simulator-plan.md`, `tasks/rpg-simulator-ledger.jsonl`,
`tasks/reports/**`):

| Path | In fence? |
|---|---|
| `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs` (the move's source) | **no** |
| `gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj` | **no** |
| `gk-core/tests/FusionRpg.Server.Tests/FusionRpg.Server.Tests.csproj` | **no** |
| `gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj` | **no** |
| `gk-core/tests/FusionRpg.Core.Match.Tests/FusionRpg.Core.Match.Tests.csproj` | **no** |
| a new shared, non-test home (a `tools/` or `src/` project) | **no** (only `gk-core/tools/RpgSim/**` is allowed, and the simulator is not the substrate's owner) |

**Second, independent reason — the premise is retired by RS2.4's shape.** The row exists so a `tools/`
consumer can reach the helper (map module 6: "the module exists for `scenario-runner`'s in-process
host"). The shipped runner takes an `HttpClient` (`gk-core/tools/RpgSim/ScenarioRunner.cs`) and opens no store;
the in-process host is `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs`, which already carries the helper via
the existing `<Compile Include>` link. **No `tools/` consumer needs the helper today**, so the move's only
remaining justification is a future one.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Nothing was moved, nothing was attempted | `git status` on the helper and the five csprojs | clean — no helper file, csproj or compile link is touched by this lane | — |
| The erratum the row asked for is filed where it can be | read `tasks/rpg-simulator-plan.md` §9.4 and the RS6 row | both name the measurement, the denied paths and the two ruling options | `tasks/rpg-simulator-plan.md` |

**No commit moves the helper: the fence denies its paths.** The commit carrying this fragment names RS6
and delivers the only artifact this lane may produce — the measurement, the erratum and the ruling
request. **Status: blocked** on a manager ruling (reassign to `data-test-substrate` with a fence covering
the five csprojs, or defer until a real `tools/` consumer exists).

# Evidence — CS-F3's premise retired from the sim tool's docs and tests (a stale premise, re-anchored)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). **CS-F3** (owner ruling 2026-09-23, `f49cd83b4`; landed as
`4bbc9d082 feat(CS-F3): the species tree ships and the boot self-heals the roster`) changed a fact this program's
docs, help text and one test were built on: **a fresh data directory now boots**, because
`Program.cs:683`'s `SpeciesImportRunner.RunSelfHealing` imports the shipped species tree on the first boot.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The test whose PREMISE the ruling retired is rewritten, not deleted | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSimProcessHostTests" --logger "console;verbosity=detailed"` | `Total tests: 3` passed. The boot failure is now made **deterministic by port**, not by content: the test holds a loopback port and passes it as `Url`, so the child cannot bind | `gk-core/tests/FusionRpg.E2E.Tests/RpgSimProcessHostTests.cs` |
| The failure still carries the server's OWN reason, not a bare timeout | same run | `the server exited with code -532462766 before answering GET /health (sim=True, data=…)` followed by the child's `Log tail:` naming the address — and the teardown still removes the data dir | same |
| The whole RpgSim set is green after the rewrite | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` | `Passed: 50, Failed: 0, Total: 50` (2 m 43 s) — it read `49/50` before this fix, the one red being this stale premise | — |
| Five prose sites carrying the retired premise are re-anchored | read: `grep -n "empty species roster\|refuses to boot" gk-core/tools/RpgSim/*.cs gk-core/tests/FusionRpg.E2E.Tests/*.cs` | `ProcessHostOptions.DataDir`'s doc, the class doc's "does not seed a world" paragraph, the nested-dir bug comment, the CLI's `--data-dir` help text, `RpgSimProcessHostTests`' class doc and `RpgSimClockOffsetTests`' provisioning comment all now state CS-F3's truth and cite `Program.cs:683` | those files |

**Why the premise's retirement is not a test deletion.** The test proves two things the row's acceptance names: a
boot that cannot come up surfaces the server's own reason, and the teardown still runs. CS-F3 removed the *cause*
the test used (an empty roster), not the property. Making the failure a **port already held** keeps both: it is
deterministic, it fails inside the child's own startup (so the log carries the reason), and it does not depend on
content the ruling now ships.

**What this is an instance of.** The repo's own rule: re-anchor the citations a change invalidates, in the same
commit as the change that breaks them. CS-F3 landed without moving this program's copies — a `docs beat comments`
failure that only surfaced because a test still asserted the old behaviour. Recorded in
`tasks/rpg-simulator-todo.md`'s RS-F20 family (a lane that changes a fact other assemblies' tests depend on also
moves those tests), and fixed here because the files are in this lane's fence.

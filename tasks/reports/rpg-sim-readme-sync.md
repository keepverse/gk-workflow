# Evidence — `gk-core/tools/RpgSim/README.md` resynced with the machine beside it

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). The map points at this README as the tool's contract-beside-the-machine, and the
program's own work had moved past it in four places. Corrected, each verified against the code.

| Claim, as written | Now | Evidence |
|---|---|---|
| "`--data-dir` must already hold a database the server can boot on — a fresh directory has no species roster and the real server refuses to start on one, so provision it first" | **CS-F3 re-anchored**: a fresh directory boots (the species tree ships; the boot self-heals the roster), and the tool still never opens a store | `gk-core/src/FusionRpg.Server/Program.cs:683` (`SpeciesImportRunner.RunSelfHealing`) |
| No mention of the golden artifact | **added**, with the two verbs and the "never the default" rule | `readback-verdict.md` §5, `GoldenVerdict.cs`, the CLI's `--golden`/`--update-golden` |
| "Exit codes: … `4` the double-run digests differ" | **`4` is also the golden's**: the digest moved, *or* no golden exists and `--update-golden` was not passed (reported, never assumed) | `RpgSimCli.cs` |
| The Contracts table listed three documents and no golden | **four rows**, and the corpus paragraph now names the golden directory and the guard's printed skip of it | `gk-core/tools/RpgSim/README.md` |
| The Tests list stopped at the process host | **`RpgSimGoldenTests.cs` and `RpgSimClockOffsetTests.cs` added**, and the closing "four referencing test projects" count replaced by the invariant — `grep -rl CombatSim tests/*/*.csproj` reads **5**, so the number had already rotted | `gk-core/tools/RpgSim/README.md` |

| Criterion | Command | Result |
|---|---|---|
| Every citation in the README resolves (a bare `Program.cs:683` would be an ambiguous basename — 42 `Program.cs` files in the tree) | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | exit **0**; `D1 683 (0 HIGH)`, `D2 7 (0 HIGH)`, `D3 ambiguous basename 56 (0 HIGH)` — unchanged, so the README adds no broken citation |
| Nothing else regressed | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | exit **0** — `GUARDS OK - 25 guard(s) run, 0 red` |

**Why this is worth a commit.** The README is the first document a reader of `gk-core/tools/RpgSim` opens, and three of
its four stale claims were *behavioural* (how to run the tool, what a data dir needs, what exit code 4 means).
The fourth is the repo's own anti-pattern in miniature: a count in prose ("four referencing test projects") that
had already become five.

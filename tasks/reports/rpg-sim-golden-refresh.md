# Evidence — the golden's refresh now reports the move it blesses (and both verbs verified end to end)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). `readback-verdict.md` §5 requires that "the refresh commit says which pointer moved and
why" — but a refresh used to overwrite the golden **silently**, which invites exactly the blind re-bless the rule
exists to prevent. Both refresh verbs now print `GoldenVerdict.Report` **before** they write, so the commit can
quote the move instead of describing it.

| Criterion | Command | Result |
|---|---|---|
| A first write says so, and a fresh EMPTY data dir boots (which independently verifies CS-F3 through the CLI) | `dotnet run --project gk-core/tools/RpgSim -c Release --no-build -- --scenario gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json --run --host process --data-dir /tmp/rpgsim-g1 --server-exe tests/FusionRpg.E2E.Tests/bin/Release/net8.0/FusionRpg.Server.exe --golden /tmp/golden-probe.verdict.json --update-golden` | exit **0**; `booted FusionRpg.Server.exe pid=60628 … (simEnabled=True, clockOffset=0s, data=…)` on a **freshly `mkdir`'d empty directory**; `no golden at … — writing the first one`; `golden REFRESHED — … (quote the move above in the commit)` |
| A compare against that golden, on a **different real process and a different fresh data dir**, is unchanged | same command without `--update-golden`, `--data-dir /tmp/rpgsim-g2` | exit **0**; `golden: … — the declared digest, the reading set and the exclusion fields are unchanged` |
| A moved digest is reported by name and fails the run | same, with the golden's `digest` overwritten to `0000…` by `sed`, `--data-dir /tmp/rpgsim-g3` | exit **4**; `golden: … MOVED at 1 field(s):` / `  digest: 00000000… -> daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e`; `rpg-sim: GOLDEN MOVED — reported, never smoothed (readback-verdict.md §5)` |
| The test lane's bless branch reports the same way, before writing | `FUSIONRPG_BLESS_RPGSIM_GOLDEN=1 dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSimGoldenTests" --logger "console;verbosity=detailed"` | `Total tests: 2` passed; `golden: … — the declared digest, the reading set and the exclusion fields are unchanged` then `golden REFRESHED — … (quote the move above in the commit)`. The refresh's volatile values (settle timings, captures) were **reverted** afterwards (`git checkout --` the golden), so the committed artifact stays the earlier run's |
| The tool still builds and the whole set is green | `dotnet build gk-core/tools/RpgSim -c Release --nologo`; `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` | `Build succeeded`; `Passed: 50, Failed: 0, Total: 50` (3 m 29 s) |
| Guards | `guard-sim-fabrication.ps1`; `guard-test-substrate.py`; `guard-doc-citations.ps1 -Strict`; `run-guards.ps1 -Tier ci` | `SIM FABRICATION GUARD OK` (`… \| golden verdicts skipped=1`); `TEST SUBSTRATE GUARD OK`; doc-citations exit **0**, `D1 683 (0 HIGH)`; the tier `GUARDS OK - 25 guard(s) run, 0 red` |

**One message fixed in the same area, because the run above found it:** `--data-dir` pointing at a path that does
not exist said only `data directory not found: <path>`. It now says **create it first — an EMPTY directory is
fine, because the server self-heals the shipped species tree on its first boot (`Program.cs:683`)** — and that
the tool never creates or opens a store. The existence check stays: a typo'd path would otherwise silently start
a new world somewhere else. (`gk-core/tools/RpgSim/ProcessHost.cs`)

**One orphan cleaned up.** The build was blocked by `FusionRpg Server (70092)` — a leftover `FusionRpg.Server.exe`
running from **this** worktree's E2E bin, from a test run the harness interrupted earlier. It was stopped **by
PID**, never by process name, so the other lanes' servers (`cmdc-live-qa`, `opencode-pd-d3b`, a `csf3pack` temp)
were untouched.

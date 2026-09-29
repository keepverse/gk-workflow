# Evidence — rpg-simulator RS2.2 §5, the golden artifact (owner ruling C2 (a): golden *and* hash)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). §5 specified the golden at `gk-core/tests/fixtures/rpg-scenarios/golden/<scenario-id>.verdict.json`
and RS2.5's row recorded it as **not yet written**; this lands it.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The golden exists and a fresh run matches it | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSimGoldenTests" --logger "console;verbosity=detailed"` | `Total tests: 2, Passed: 2`; `run: ok=True digest=daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e readings=7`; `golden: … — the declared digest, the reading set and the exclusion fields are unchanged` | `gk-core/tests/fixtures/rpg-scenarios/golden/first-session-forward.verdict.json` (34,549 bytes) |
| The comparison is **seen to fail**, and values-only moves are correctly ignored | same run, `A_moved_digest_a_dropped_reading_or_a_changed_exclusion_is_reported_by_name` | a moved digest reports `digest: abc -> def`; a dropped reading reports `readings: […] -> […]`; a changed exclusion reports `digestExclusions: [*At] -> [*Utc]`; a payload change under the SAME digest is **not** reported (§5: the golden is not the outcome oracle) | `gk-core/tools/RpgSim/GoldenVerdict.cs`, `gk-core/tests/FusionRpg.E2E.Tests/RpgSimGoldenTests.cs` |
| Refreshing is explicit, never the default | `dotnet build gk-core/tools/RpgSim -c Release --nologo`; the CLI's usage block | `Build succeeded`; `--golden <verdict.json>` compares and `--update-golden` refreshes, and a missing golden says *"pass --update-golden to write the first one"* instead of passing silently | `gk-core/tools/RpgSim/RpgSimCli.cs` |
| The whole RpgSim set, including the golden | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` | `Passed: 50, Failed: 0, Total: 50` (2 m 43 s) — was 48 before the two golden tests | — |
| The RS4 guard skips the golden subtree and says so | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-sim-fabrication.ps1` | `scenarios=1 steps=36 reads=7 test.* steps=1 \| /api/sim handlers=60 (take RpgStore: 0) \| /api/test handlers=12 (take RpgStore: 11, allowlisted: 11) \| golden verdicts skipped=1` — `SIM FABRICATION GUARD OK` | `scripts/guard-sim-fabrication.ps1` |
| The guard's own bite proof still holds | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~SimFabricationGuardTests"` | `Passed: 4, Failed: 0, Total: 4` | — |
| The test substrate stays clean | `python gk-core/scripts/guard-test-substrate.py` | `TEST SUBSTRATE GUARD OK` | — |

**What the golden pins:** the digest, the seed, the scenario id, the reading set (each read-back's name, method
and route) and the digest's exclusion fields. **What it deliberately does not:** the readings' values — an
outcome-dependent row set is asserted by the corpus's own `expect.*` rules, so a balance change must not fail the
golden for a reason that is not a regression.

**Two refresh verbs, because the CLI cannot boot in-process** (RS-F6): `--golden`/`--update-golden` for a process
or `--base-url` lane, and `FUSIONRPG_BLESS_RPGSIM_GOLDEN=1` for the test lane (the house pattern its sibling
fixtures use). §5's doc now records both, and why.

**One interaction found and resolved, not discovered later:** the RS4 guard scans
`gk-core/tests/fixtures/rpg-scenarios/**` recursively for scenarios, and a golden is not one — it has no `steps` array, no
`clock` block and no `digest` step, so scanning it produced a wall of honesty violations that said nothing. The
guard now skips the `golden/` subtree and **prints the count it skipped**, so the exclusion is visible in every
run rather than a silent filter.

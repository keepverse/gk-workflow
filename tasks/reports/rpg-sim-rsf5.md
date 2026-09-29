# Evidence — rpg-simulator RS-F5 (the map's promised spec tree, repointed)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Row RS-F5, acceptance's first branch: *"either the map's spec paths are repointed to
the tool … or the specs are moved into `docs/architecture/rpg-simulator/` by whoever holds that fence."*

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every module row names a REAL document, not a promise | `grep -n "spec-\*.md\|spec-first-session-scenario\|spec-scenario-format\|spec-inproc-host\|spec-sim-ci-lane" docs/architecture/rpg-simulator-map.md` | no promised path remains; the Spec column reads `gk-core/tools/RpgSim/scenario-format.md` (2), `readback-verdict.md` (3), `README.md` + the CLI usage block (4), `RpgApiFactory.cs` + `RpgSimInProcHostTests.cs` (5), `ProcessHost.cs` + `RpgSimProcessHostTests.cs` (7), `guard-sim-fabrication.ps1` + its registry row (8), and the two seam specs (10, 11) | `docs/architecture/rpg-simulator-map.md` |
| The header no longer promises a tree, it states the rule | read: the **Module specs** paragraph | "a contract that a machine enforces lives beside that machine … a contract that IS a mechanism lives in the file that implements it … a seam gets a sibling spec because no single machine owns it" | same |
| Two rows say NOT WRITTEN, with the reason in the cell | read: rows 6 and 9 | row 6 `shared-store-home` — its premise was retired (`gk-core/tools/RpgSim` stayed store-free; RS-F6 is the surviving question); row 9 `sim-ci-lane` — RS7 is open and owns it | same |
| The "what is missing" note is corrected, not deleted | read: the `- **No docs/architecture/rpg-simulator/spec-*.md tree exists…` bullet | names the repoint and both NOT WRITTEN rows | same |
| No citation in the map or the todo is broken by the edit | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | `D1 file does not exist 714 (0 HIGH)`, `D2 line past end of file 7 (0 HIGH)`, `D3 ambiguous basename 58 (2 HIGH)` — both HIGHs are `docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md:76` (RS-F18, another program's document) | — |

**What was NOT done, and why:** the second branch — moving the contracts into
`docs/architecture/rpg-simulator/` — was refused, not skipped. The tree is not where these contracts belong:
`gk-core/tools/RpgSim/scenario-format.md` is enforced by `ScenarioValidator.cs` and the RS4 guard in the same folder,
`ProcessHost.cs`'s contract is its own teardown behaviour, and `guard-sim-fabrication.ps1`'s allowlists *are*
the contract. Moving them into `docs/` would put the rule a machine enforces away from the machine, which is
the failure mode `gk-core/tools/CombatSim/README.md` already avoids.

# Evidence — the plan's promised spec paths repointed (RS-F5's last live pointers)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). RS-F5 closed by repointing the **map**; the **plan** still carried three live pointers
into the promised `docs/architecture/rpg-simulator/spec-*.md` tree, two of them in `-Verify` lines a lane would
paste into `verify-change.ps1`. Fixed here, with two stale bullets and one stale "Ruling asked" tail.

| Criterion | Command | Result |
|---|---|---|
| The two `-Verify` lines now name paths that RESOLVE (the old ones were unmapped) | `pwsh -NoProfile -ExecutionPolicy Bypass -Command '… verify-change.ps1 -Paths @("gk-core/tools/RpgSim/scenario-format.md","gk-core/tools/RpgSim/readback-verdict.md") -AllowUnscoped -PlanOnly'` | `gk-core/tools/RpgSim/scenario-format.md -> rpgsim-tool (module)`, `gk-core/tools/RpgSim/readback-verdict.md -> rpgsim-tool (module)` + doc-citations + test-substrate + `test: e2e` — where `docs/architecture/rpg-simulator/spec-*.md` would have been refused as unmapped |
| The RS3 gate line names the real spec and records that both gates are met | read: `tasks/rpg-simulator-plan.md` §"Wave 5 — the clock" | `docs/architecture/rpg-simulator-spec-clock-seam.md`, with its §4 agreement answered |
| The two stale bullets are corrected | read: the plan's "what this plan says differently" list | the content-root half is answered (RS-F6, the fallback the plan's own risk 2 predicted); the "no module spec exists yet" bullet now names the three sibling specs and the map's repointed cells |
| §9 item 1's "Ruling asked" is marked resolved | read: §9 item 1 | **RESOLVED 2026-09-23**: the map is repointed, its header states the rule instead of promising a tree, one row says NOT WRITTEN on purpose |
| No citation is broken by the edit | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | exit **0**; `D1 683 (0 HIGH)`, `D2 7 (0 HIGH)` |
| Nothing else regressed | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | exit **0** — `GUARDS OK - 25 guard(s) run, 0 red` |

**Why it is worth a commit.** A `-Verify` line is an instruction: the two corrected ones named a path that does
not exist, so a lane following the plan would have hit `VERIFICATION BOUNDARY MISSING` and either filed it as a
defect or reached for a broader suite — the exact wrong-tool failure the verification-boundary rules exist to
prevent. The corrected lines resolve to `rpgsim-tool` and are proven above.

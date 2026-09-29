# `CAI-route` — every open row's out-of-fence half filed as a routed row

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The population being routed is the real one | `grep -o "^- \[ \].\{0,60\}" tasks/combat-ai-todo.md \| nl` | **34** open checklist lines = 21 named task rows + 11 `CP2`-`CP5` checkpoint lines + `CAI-guard-1` (protected path) + `TVB-F16`. 40 at lane start; the six `CP1` lines closed in the previous commit | `tasks/combat-ai-todo.md` |
| Every open task row is routed to the paths a holding lane needs | read of each row's own `Files:` line, grouped | 9 routes — `R-INJ` (8 rows), `R-CORE-MATCH` (4), `R-CORE-WORLD-DATA` (2), `R-SERVER` (CAI2.1's filed Data+Server thirds, CAI2.2, CAI3.5, CAI4.9's endpoint), `R-TUNING-PUBLISH` (CAI3.1, CAI3.6 — H7), `R-DOMINANCE` (CAI2.3), `R-DOCS-RESEARCH` (CAI5.1, CAI5.2), `R-OWNER` (CAI2.6, CAI3.1, CAI3.4 — a ruling, not a path), `R-LAWN-DEPS` (CAI4.7, CAI5.1, CAI5.3) | `tasks/combat-ai-todo.md` §Executor routing |
| CAI4.7's entry condition — **measured, unmet** | `ls gk-core/data/tuning/ \| grep -iE "combat-ai\|siege\|lawn"` | only `combat-ai.v1.json`, `siege.v1.json`, `siege.v2.json` — **`lawn-perf-budget.v1.json` does not exist**, so `lawn.ai.decide`'s share has no file to read; the owner is lawn `LW1.1` (`tasks/lawn-todo.md:16`, `- [ ]`) | — |
| CAI5.3's precondition 1 — **measured, unowned** | `grep -rn "unique-deploy-cap" tasks/*-todo.md` | two hits: `backlog-clean-up-todo.md:329` (BCU2.9's *done* row, which authored the spec) and `combat-ai-todo.md:934` (a cross-program note). **No task builds it**, while `docs/architecture/creature-lawn-deploy/spec-unique-deploy-cap.md` reads *"Status: spec, 2026-09-20. Not built."* and its header says it is *"scheduled once in the backlog-clean-up lawn plan"* | `tasks/lawn-todo.md:158` |
| The routed row | `sed -n '156,175p' tasks/lawn-todo.md` | **`LW5.1`** added with the cause read, the spec's own Verify and the single existing admission gate (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:150-250`) | `tasks/lawn-todo.md` |
| The stale note that hid it is corrected | `grep -n "does not depend on any single" tasks/lawn-todo.md` | `tasks/lawn-todo.md`'s cross-program note said `combat-ai`'s wave 4 "does not depend on any single `LW*` task landing first"; corrected in place — true for `CAI4.1`/`CAI4.2`, **false** for `CAI4.7`/`CAI5.1`/`CAI5.3`, with the measurement | — |
| CAI3.1's cross-lane break is a real file, not a claim | `sed -n '528,536p' gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs`; `sed -n '468,476p' gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs` | both construct `AiTuning` with **four named arguments** (`StanceDefault:`, `AutoResolveHandicapMilli:`, …) and neither file is in any combat-ai lane's fence — so narrowing `AiTuning` to its two live members cannot land without a lane holding both test projects | `R-FOREIGN-TESTS` |
| Two `CAI1.15` deferred items are stale | `grep -n "SUPERSEDED 2026-09-21" tasks/combat-ai-todo.md` | both marked superseded: `CAI1.15` closed at `b3ffc183` and `CP1` re-measured `docs/DESIGN-GATE.md:57` and `combat-ai-ideal.md:129` | — |
| Ledger + boundary | `python gk-core/scripts/anchor-ledger.py tasks/combat-ai-ledger.jsonl check`; `python scripts/session-boundary-check.py` | ledger OK; no crossing introduced (this lane's record is worktree mode, and the two records whose fences touch `tasks/**` are worktree mode too) | — |

## Not proved

- **The route paths are the rows' own `Files:` lists, re-read — not re-verified file by file against the
  tree.** Two entries were verified by reading the file itself: the two `AiTuning` named-argument sites
  above, and `spec-unique-deploy-cap.md`'s status line. A route's path list could still name a file that
  has since moved; the row's own acceptance would catch that when it is executed.
- **No routed row was attempted.** That is the point of the route — reaching for a denied path is the
  failure this avoids — but it does mean this fragment proves routing, never the routed work.
- **`R-INJ`'s eight rows are not ordered among themselves.** The order a holding lane should take them in
  is the Injector half's own dependency chain (`CAI2.5`'s ring cleanup → `CAI4.1`'s view host →
  `CAI4.3`/`CAI4.5` → `CAI4.6` → `CAI4.8` → `CAI4.9`), which the todo's own row order already states; it
  is not restated here.

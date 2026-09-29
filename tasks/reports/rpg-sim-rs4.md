# Evidence — rpg-simulator RS4 (the scenario-honesty guard)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Module `honesty-guard`; owner ruling D4 (b) (automated guard, not a checklist).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Half A — every `read.*` names an FE-facing route; every call op is the closed table's own route; every `expect`/`digest` names a declared `read.*`; every `test.*` step is allowlisted **and** named in the scenario's `notes` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-sim-fabrication.ps1` | `scenarios=1 steps=36 reads=7 test.* steps=2` — `SIM FABRICATION GUARD OK`, exit 0 | `scripts/guard-sim-fabrication.ps1` |
| Half B — no `/api/sim` handler takes `RpgStore`; every `/api/test` direct-store handler is allowlisted; a stale entry is a violation | same command | `/api/sim handlers=60 (take RpgStore: 0)` — `/api/test handlers=13 (take RpgStore: 12, allowlisted: 12)` | same |
| The guard **bites on a planted fabricated read-back** | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~SimFabricationGuardTests"` | `Passed: 4, Failed: 0, Total: 4`; the planted case returns red naming `/api/test/snapshot`, `read.never-ran` and `not named in the scenario's own notes` | `gk-core/tests/FusionRpg.Guard.Tests/SimFabricationGuardTests.cs` |
| The guard **bites on a planted `/api/sim` handler that takes the store**, and on a **stale allowlist entry** | same run, `A_planted_sim_handler_that_takes_the_store_is_refused` / `A_stale_test_store_allowlist_entry_is_refused` | red naming `/api/sim/evil`; red naming `stale allowlist entry '/api/test/snapshot'` | same |
| The guard is wired the way every other guard is | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci -Only sim-fabrication` | `sim-fabrication ci gating 0` — `GUARDS OK - 1 guard(s) run, 0 red` | `gk-core/scripts/enforcement-registry.v1.json` (`tier: ci`, `status: gating`; invariant `pr-sim-honesty`) |
| The registry and runner contracts still hold | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~EnforcementRegistryGuardTests\|FullyQualifiedName~GuardRunnerTests"` | `Passed: 26, Failed: 0, Total: 26` | — |
| The new guard script resolves a verification owner instead of throwing | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | `gk-core/scripts/verification-boundaries.v1.json` (`sim-fabrication-guard`) |

**Two measurements the brief carried, corrected by this lane's own count** (reported, never smoothed):

- The brief says the `/api/sim` surface is **55 handlers, 0 take `RpgStore`**. This guard counts **60**:
  `54` in `SimEndpoints.cs`'s `/api/sim` group plus `6` in `SimEffectEndpoints.cs`'s `/api/sim/effect`
  group. The load-bearing fact agrees — **0 take `RpgStore`** — and the guard's allowlist for that half is
  deliberately empty, so a single new direct-store handler fails it.
- The brief names **12** `/api/test` direct-store handlers and lists exactly the 12 this guard finds
  (`reset`, `snapshot`, `seed-pvz-stats-demo`, `seed-pvz-activity-demo`, `seed-rpg-progression-demo`,
  `seed-souls-demo`, `web-match`, `expedition-due`, `seed-materials`, `mint-creature`, `contracts/settle`,
  `world/create`). `/api/test/probe` is the 13th handler and takes no store, so it is not allowlisted.

**NOT proved / deviations.**

- **`-Session sim-t3-2` could not be used**: `tasks/sessions/sim-t3-2.json` does not exist and
  `tasks/sessions/**` is outside this lane's allowed paths, so the brief's exact form throws
  `session record not found`. `-AllowUnscoped` was used for every `verify-change.ps1` call, exactly as
  the previous lane (`sim-t3-1`) recorded for the same reason.
- **The guard re-states the honesty rules; it does not call `ScenarioValidator`.** `gk-core/tools/RpgSim`'s
  validator runs inside the runner over one file; the guard runs in CI over the whole corpus without a
  build. The two share ONE copy of the op table — the guard parses
  `gk-core/tools/RpgSim/ScenarioVocabulary.cs`'s `new ScenarioOp(...)` rows — so a new op cannot land in the
  table and be invisible to the guard.
- **Half A does not re-implement the format validator's arg/source checks** (which request field comes
  from which capture). Those are shape rules, not honesty rules, and they already fail loudly in the
  runner; duplicating them would be a second implementation to drift.

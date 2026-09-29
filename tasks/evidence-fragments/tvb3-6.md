# TVB3.6 — `GeneratorCheckCiParityTests` + first wrappers (`gen-resource-ownership`, `gen-creature-species`)

| Criterion | Result |
|---|---|
| Argument-free wrappers, run exactly the CI command from the CI working directory (repo root, no `working-directory:` in either step) | added |
| Fail loudly on a missing toolchain | `python --version`/`dotnet --version` preflight, `throw` on non-zero |
| `script` projects; seam boundaries per the D5 table | `gen-resource-ownership` seam on `gk-core/tools/tuning/resource_ownership.py`; `gen-creature-species` seam on `gk-forge/tools/CreatureSpeciesGen/**` |
| New owner `creaturespeciesgen-tool` -> `core` (module) | added (the tree had no owner at all before this) |
| `GeneratorCheckCiParityTests` (every wrapper's real command line, ci.yml step at the same working-directory; carries `guard.workflows`) | new, 3 tests, all pass |
| Both wrappers exit 0 on a clean tree | `gen-resource-ownership.ps1`: **yes**, real run, exit 0 ("166 generated edges match"). `gen-creature-species.ps1`: real run correctly DETECTS a genuine, pre-existing, out-of-scope drift (see below) — proves the wrapper works exactly as designed, not a clean-tree pass |

**Real, pre-existing, out-of-scope finding (not fixed here):** running `gen-creature-species.ps1` for
real reports 11 species stale against `gk-data/packs/fusion/data/generated/creatures` (IronMelon, WaterShulk, MelonFume,
MagnetMelon, SuperSnowMonsterZombie, ArmedGargantuar, RandomGargantuar, Gargantuar, ElephantZombie_a,
SnowMonsterZombie, BlackFootball_c). Confirmed via `git log` that this is caused by another program's
recent work (`creature-seed`'s `gk-data/packs/fusion/data/seed/creatures/**` changes, e.g. `7a1be518c`
"re-derive every species anchor from the measured capture") landing without a corresponding
`gk-data/packs/fusion/data/generated/creatures/**` regeneration+commit — not anything touched by this lane, and outside
this session's `paths` fence (test-verification-boundary never edits `gk-data/packs/fusion/data/generated/creatures/**`
or `gk-forge/tools/CreatureSpeciesGen/**`). The wrapper's own correctness is proven BY this finding (it
catches real drift exactly as `--check` should); fixing the drift itself belongs to whichever program
owns the creature-species generator.

**One real bug found and fixed:** the first cut mapped only the CHECKED paths (`resource_ownership.py`,
`gk-forge/tools/CreatureSpeciesGen/**`), leaving the wrapper SCRIPT FILES themselves unmapped
(`VERIFICATION BOUNDARY MISSING: scripts/checks/gen-creature-species.ps1`) — the same class of gap
TVB2.5 found for `guard-bench-compile.ps1`. Fixed by adding a forward-looking `gen-checks-scripts`
fallback boundary (`gk-core/scripts/checks/**`, module, project `guard`), so the remaining wrappers landing in
TVB3.7-3.9 do not need this same fix repeated.

Scoped verify: `.\scripts\verify-change.ps1 -Paths scripts/checks/gen-resource-ownership.ps1,scripts/checks/gen-creature-species.ps1,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/GeneratorCheckCiParityTests.cs -Session summoner-convergence-lane-d2-20260919`
-> `guard` project whole run 501/501 (11m44s), focused `guard.verification-boundaries` 49/49 (10m58s).

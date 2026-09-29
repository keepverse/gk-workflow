# EP4.2 — Publish `progression` (v3): `xpCurve.empire` + `awards.speciesLevelUp`; move the pins; the §10.1 row

Commit `@EP4.2` · session `empire-progression-3` · branch `cmdc/ep-3` · spec `docs/architecture/empire-progression/spec-empire-level.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Published through `publish.py` on top of whichever `progression` version is current | `python gk-core/tools/tuning/publish.py progression --label "empire-level (R19): xpCurve.empire + awards.speciesLevelUp" --add-key 'xpCurve:empire={"first":10,"step":5}' --add-key 'awards:speciesLevelUp=1'` | `xpCurve.empire ADDED`, `awards.speciesLevelUp ADDED`, `published progression (v2 -> v3, 2 change(s)); v2 stays on disk for revert`, exit 0 | `gk-core/data/tuning/progression.v3.json` (new; v1/v2 untouched) |
| A missing key is a load rejection naming it | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~EmpireLevelGrants\|FullyQualifiedName~RpgActorKinds\|FullyQualifiedName~ProgressionTuning"` | `Passed! - Failed: 0, Passed: 23, Skipped: 0, Total: 23` — incl. `A_document_without_the_empire_curve_is_refused_by_name`, `A_document_without_the_species_level_up_award_is_refused_by_name`, `A_v1_shaped_document_no_longer_loads_at_all` | `gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs` (`Curve(curve, "empire")`, `RequiredPositiveLong(awards, "speciesLevelUp")`) |
| Every pin moves in this commit (H7) | `rg -n "progression\.v[0-9]+\.json" src tools tests --glob "*.cs"` | **34 files read `progression.v3.json`**; zero reads of v1/v2 remain. The only v1/v2 mentions left are four comments that are historically true (the `SpecChannelClaimTests` allow-list's own two reasons, `ProgressionTuning.cs`'s SP7.1 rationale, `EmpireLevelGrantsTests`' "v1's own shape", and `RpgStore.Progression.cs`'s "an old v1-shaped document" — Data, not edited here). Moved in one batch with a `(?<!species-)` guard so `species-progression.v1.json` was untouched (verified: 0 occurrences of `species-progression.v3.json`) | `gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/ProveHubCombat/Program.cs`, `gk-forge/tools/_TempSeedSpecies/Program.cs`, 31 test files |
| The live host loads the published file | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | `Passed! - Failed: 0, Passed: 772, Skipped: 0, Total: 772`, exit 0 | `gk-core/src/FusionRpg.Server/Program.cs` |
| The `ssot-power-scale.md` §10.1 row lands at the next free ordinal | read of the table | **row 39** (38 was the highest, added 2026-09-19); it names the cost-ladder verdict, the `xpCurve.empire` pair, and the `decisions.md` "**never** feeds `Θ`/`P(Θ)`" lock | `docs/architecture/power/ssot-power-scale.md` |
| `guard-power.py` is green | `python gk-core/scripts/guard-power.py` | `POWER GUARD OK — one ladder, pin holds, no private f(level)`, exit 0 | — |
| Tuning ownership unchanged | `python gk-core/tools/tuning/resource_ownership.py --check` | `OK -- 166 generated edges match aptitudes.v10.json's 166 resource edges exactly`, exit 0 | — |
| Both tools that pin the file still build | `dotnet build gk-forge/tools/ProveHubCombat -c Release`; `dotnet build gk-forge/tools/_TempSeedSpecies -c Release` | `Build succeeded` twice | — |
| Path-owned boundary | `.\scripts\verify-change.ps1 -Paths @(<37 code/data/doc paths>) -Session empire-progression-3` | exit 1, and the exit is entirely the known TVB-F6 misreport: `DAL GUARD OK`, doc-citation audits 0 findings (D1–D4 all 0), and **all core shards green** — `12759`, `15`, `498`, `31`, `1351`, `30`, `210`, `7`, `12`, `238`, `4`, `9` plus the `guard.doc-boundary`-tier `498` — then the Data sharded runner printed `444 + 40 + 83 + 1145` tests with no failure line and exited with an EMPTY code, which aborts the run before the `guard`/`server` steps. Those three steps were then run directly (below). The `tasks/**` paths were left out of `-Paths` on the second attempt: they select `session-and-program-records`, whose boundary check reports the worktree-path drift every worktree lane shows | — |
| The steps the abort skipped, run directly | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "VerificationId=guard.doc-boundary"`; `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "VerificationId=server.derived-audit"` | `Passed! 4/4` and `Passed! 1/1` | — |
| The Data half, re-run because the sharded runner's exit code is empty | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "Category!=DiskSemantics&Category!=Heavy"` | `Passed! - Failed: 0, Passed: 1737, Skipped: 0, Total: 1737, Duration: 10 m 49 s`, exit 0 | — |

**The deviation EP4.1 recorded is now closed, deliberately.** EP4.1 shipped the two keys as presence-tolerant at
parse and refused by name at first use, because `progression` has no "find latest" resolver: the live host read
`progression.v2.json` and ~30 fixtures pinned `progression.v1.json`, so a parse-time requirement would have made
the shipped server unloadable in the commit that added the key. **This is that commit**, so the keys become
required at parse (tunables-ssot.md T5) and the deferred refusal survives only for an in-code
`ProgressionTuning` a test bootstrap built without them — the case whose test replaces EP4.1's
`An_older_document_...` test. `spec-empire-level.md` and the EP4.1 fragment both carry the correction.

**A second doc-token collision, caught the same way as the first.** Writing `progression.v3.json` into
`spec-empire-level.md` broke `SpecChannelClaimTests.NoSpecClaimsAnUnregisteredChannel` — exactly the class of
break EP3.11's commit fixed for `progression.v2.json`. The token is now allow-listed with its own verified reason,
per-version on purpose (one line in `gk-core/tests/FusionRpg.Core.ActorHub.Tests/ActorHub/SpecChannelClaimTests.cs`).

**Not proved / observed for the next reader:**
- `docs/architecture/power/inventory.json` (the §10 mirror `guard-power`'s G3 reads) was **not** given a row 39.
  Rows 35–38 were not mirrored either, so the mirror's highest id is 34 and a lone 39 would highlight a
  pre-existing lag rather than close it; G3 does not need one (no method in this change matches its
  signature heuristic, and `RpgProgression.cs` is already listed). Left for whoever reconciles the mirror.
- No reader *outside* `src/tools/tests` reads a `progression.vN.json` file (checked repo-wide): the remaining
  mentions are docs, research notes, ledgers and evidence fragments.
- `progression.v1.json`/`v2.json` remain on disk and no longer load — deliberate, so a revert is a file restore.
  Any *future* reader must pin v3 or later; the domain has no version resolver, which is the standing hazard this
  publish documents rather than fixes.

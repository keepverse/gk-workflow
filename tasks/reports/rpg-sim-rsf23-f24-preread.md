# Evidence — RS-F23 and RS-F24 re-measured on the newest accepted head, with the owner's pre-read

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`), head `90eea1c15` (the newest `features/mega-merge` acceptance). Both rows were filed
last segment from `post_merge_check.py`'s Guard-suite red; this increment checks they are still live and hands
each owner the conclusion of the re-read, so the fix is mechanical.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Both reds are still live, not stale | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~CiPytestWiringTests\|FullyQualifiedName~PlayerSpeciesMaterialiseCallerGuardTests"` | `Failed: 2, Passed: 5, Total: 7` (401 ms) | — |
| RS-F23: the registry row is CORRECT as written | read: `gk-core/scripts/verification-boundaries.v1.json` + `gk-core/tests/tools/test_audit_program_pipeline.py:19` | `tools-audit-tests {root: ".", tests: "gk-core/tests/tools"}` means *run from the repo root, target `gk-core/tests/tools`* — matching the suite's own `REPO_ROOT = parents[2]` and the `tuning-py` shape. So the missing piece is a `ci.yml` step at `working-directory: .` with its own exit check, not a registry correction | `gk-core/scripts/verification-boundaries.v1.json`, `.github/workflows/ci.yml` |
| RS-F24: the widening is LEGITIMATE, so the pin should move | read: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:299-305` and the guard's own comment at `PlayerSpeciesMaterialiseCallerGuardTests.cs:90-93` | the producer documents the new code as a SECOND, DISTINCT gate (*"the rank floor lands BESIDE the rarity floor above, and reads the SOURCE species' own rank"*, `spec-species-rank.md` §6), so it is not a duplicate of `picks.source-below-inherit-floor`; the guard says a tenth code *"is a reviewed change that should fail this test and be re-read"* | `gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs:121` |

**RS-F23's fix, as a line:** a `python -m pytest` line under a step whose `working-directory` is `.`
(e.g. `python -m pytest gk-core/tests/tools -q -p no:cacheprovider`), with the exit check the other pytest steps carry.

**RS-F24's fix, as two lines:** add `"picks.source-below-rank-floor",` to the guard's `expected` array and change
`Assert.Equal(9, found.Count)` to `10`.

**Why this lane cannot apply either:** `ci.yml` is outside its allowed paths, and
`gk-core/tests/FusionRpg.Guard.Tests/**` is a pipeline-protected tree — the whole reason both rows are filed here for
routing rather than fixed in place. The pre-read is the part this lane CAN do, and it is done.

# species-gear-chain — 10 verify lines select nothing: the Core split broke their citations

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, outside this lane's
allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

| Criterion | Command | Result |
|---|---|---|
| the class, measured | sweep of every `dotnet test <project> --filter "FullyQualifiedName~<token>"` line in `tasks/species-gear-chain-todo.md`, checking the token against the whole named project's `.cs` sources | **10 of 76 lines named `gk-core/tests/FusionRpg.Core.Tests` while the token appears NOWHERE in that project** — so no test name there can match and the line is a green no-op (the class T57 already filed once as `-k setgen`) |
| the ten | same sweep | T10 `~Potential`, T12 `~EnhanceTrack`, T24 `~CraftRisk`, T37 `~ItemUpgrade`, T38 `~ItemUpgrade`, T33 `~CostClass`, T40 `~CostClass`, T41 `~Enhance`, T43 `~CraftRisk`, T46 `~EnhancePolicy` |
| cause | the Core split | every one of those areas moved into `gk-core/tests/FusionRpg.Core.Items.Tests`; e.g. `grep -rn ItemUpgrade gk-core/tests/FusionRpg.Core.Tests --include=*.cs \| wc -l` → **0**, `gk-core/tests/FusionRpg.Core.Items.Tests` → **55** |
| the corrected filter really selects the tests | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~ItemUpgrade"` | **Passed! — Failed: 0, Passed: 32, Skipped: 0, Total: 32** (exit 0); the row's own progress note records the same **32 passed** |
| T12's box was doubly wrong | `grep -rn EnhanceTrack tests/ --include=*.cs` | the token appears in no test NAME anywhere — only as a parameter at `ItemWorkbenchEndpointsTests.cs:1643`; the join the box wants is asserted Python-side: `python -m pytest gk-forge/tools/seedsmith/tests/test_base_types_gen.py -q -k enhance_track` → **5 passed, 67 deselected** |
| the repair | re-run of the sweep after the edits | **0 stale of 75** filter lines; `0` pytest file references missing |
| the recorded T38 count is untouched | read | the closure note's `-> **31 passed, 0 failed**` is left as recorded (a historical reading); only the project path is corrected, with the correction and today's `32 passed` named inline |

**What was changed:** the 9 wrong-project lines now name `gk-core/tests/FusionRpg.Core.Items.Tests`, T12's dead
`dotnet test` line became the pytest line that actually asserts the join, and each edit carries an inline
dated correction so the change is auditable without this fragment. T37's first verify box is now ticked —
its corrected command was run and is green.

## T37's verify block — three of five boxes measured at this head (2026-09-23, lane sgc-6)

T37 is one of the two genuinely OPEN blocks, and its verify block had five unticked boxes. Running what
is runnable in-fence turns three of them into readings:

| Box | Command | Result |
|---|---|---|
| 1 (ticked) | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~ItemUpgrade"` | **Passed! Failed: 0, Passed: 32, Skipped: 0, Total: 32** — the line the stale-citation repair above corrected (it named `FusionRpg.Core.Tests`, which holds no such test) |
| 2 (ticked) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"` | **Passed! Failed: 0, Passed: 16, Skipped: 0, Total: 16** |
| 3 | `dotnet test gk-core/tests/FusionRpg.Server.Tests` | **not run** — the whole project exceeds the harness segment cap. Last recorded reading on this head: **Failed: 1, Passed: 766**, the one failure a foreign combination-corpus case, not this row's |
| 4 (ticked) | `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1` | `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data`; `ACTOR-HUB GUARD OK` |
| 5 | `dotnet run --project gk-forge/tools/ItemSeedValidator` | **RED**, unchanged: exactly T37's 498 authored `successorOf` rows flagged `SameStageReference`. The ready patch is `tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch` and `gk-forge/tools/ItemSeedValidator/**` is a denied path for this lane |

The two remaining boxes are the two external blockers the row already names, so the block is now proven
where it can be and blocked exactly where it is blocked — nothing left "unmeasured by default".

## T37's verify block is now fully measured (2026-09-23, lane sgc-6)

The third box — `dotnet test gk-core/tests/FusionRpg.Server.Tests` — was left unrun in `f41dd5e12` as too large
for the segment. It fits once the project is built first (12s) and the run uses `--no-build`:

| Command | Result |
|---|---|
| `dotnet build gk-core/tests/FusionRpg.Server.Tests -v q --nologo` | **0 Errors**, 22 warnings, 11.92s |
| `dotnet test gk-core/tests/FusionRpg.Server.Tests --no-build` (with `powershell` on `PATH`) | **Passed! Failed: 0, Passed: 859, Skipped: 0, Total: 859** in 3m10s |
| the same run WITHOUT `powershell` on `PATH` | **Failed: 2, Passed: 857** — both `Win32Exception: … start process 'powershell' … cannot find the file specified` |

So T37's recorded `Failed: 1, Passed: 766` was **stale at this head**: the foreign combination-corpus
failure has since been fixed by a merged lane, and 93 more tests exist. The box is ticked on the
measured 859/0.

The two failures in the stripped-`PATH` run are a *different* defect, filed as **SGC5-F5**: two cases in
`RealRunCollectorTests.cs` start `powershell` by bare name (`:154`), so an environment-dependent
dependency surfaces as an opaque `Win32Exception` — the C# twin of the seedsmith hazard fixed in
`a41d5d152`. `gk-core/tests/FusionRpg.Server.Tests/**` is in this lane's fence but belongs to the server
program, and no row in this program needs it, so it is filed rather than edited.

## The bare-name-process-start class, inventoried (2026-09-23, lane sgc-6)

SGC5-F5 was filed from the Server.Tests instance; scanning `tests/**/*.cs` (`bin`/`obj` excluded) for a
bare `ProcessStartInfo.FileName` / `new ProcessStartInfo("…")` shows it is a class, not two cases:

| Executable | call-site files | test projects |
|---|---|---|
| `powershell` | 24 | `FusionRpg.Guard.Tests`, `FusionRpg.Server.Tests` |
| `dotnet` | 5 | `FusionRpg.AtomImporter.Tests`, `FusionRpg.Core.Tests.Shared`, `FusionRpg.Data.Tests`, `FusionRpg.SquadHarness.Tests` |
| `python` | 3 | `FusionRpg.Core.ClassSystem.Tests`, `FusionRpg.Guard.Tests` |
| `git` | 2 | `FusionRpg.Guard.Tests` |
| `icacls` | 1 | `FusionRpg.Guard.Tests` |
| **total** | **35 files** | **10 projects** |

Two instances are measured, not inferred:

| Run | PATH | Result |
|---|---|---|
| `dotnet test gk-core/tests/FusionRpg.Server.Tests --no-build` | `powershell` present | **Passed! Failed: 0, Passed: 859, Total: 859** |
| the same | `powershell` absent | **Failed: 2, Passed: 857** — both `Win32Exception: … start process 'powershell' …` |
| the two `python`-spawning guard classes, `--filter "FullyQualifiedName~DocCitationAudit|FullyQualifiedName~VocabRename"` | `python` present | **Passed! Failed: 0, Passed: 40, Total: 40** in 6s |
| the same filter | `python` absent | **Failed: 39, Passed: 1, Total: 40** in 105ms — every failure `Win32Exception: … start process 'python' …` |

So a lane running the suite from a stripped shell sees failures that read as content or boundary
violations, in 10 test projects — and the `python` case is not marginal: **39 of the 40 doc-citation /
vocab-rename guard cases fail**, in 105ms, while the whole project they sit in takes 8m36s, so a lane
cannot even re-run the suite to check what it just saw. The fix is a per-call-site resolution with a named failure (a shared helper
already exists at `gk-core/tests/FusionRpg.Core.Tests.Shared/TestSupport/ToolProcess.cs:45`), which is why this
is filed for the manager to route rather than fixed from a species-gear-chain lane.

## The gear-chain's whole C# surface at this head (2026-09-23, lane sgc-6)

T37's verify block was measured box by box; the two test PROJECTS this program's rows live in were then
run whole, so the claim "no in-fence C# failures at this head" is a reading rather than an inference:

| Command | Result |
|---|---|
| `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests` (whole project, 82 files) | **Passed! Failed: 0, Passed: 1470, Skipped: 0, Total: 1470** in 9s |
| `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Item\|FullyQualifiedName~InstanceOp\|FullyQualifiedName~Material\|FullyQualifiedName~Craft\|FullyQualifiedName~Socket"` | **Passed! Failed: 0, Passed: 323, Skipped: 0, Total: 323** in 2m |
| `dotnet test gk-core/tests/FusionRpg.Data.Tests` (whole project) | ⛔ **not completed** — the run exceeded the 560s segment budget after building and starting; the filtered run above covers this program's own surface instead |
| `dotnet test gk-core/tests/FusionRpg.Server.Tests --no-build` | **Passed! Failed: 0, Passed: 859, Total: 859** (see above) |
| `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "~ItemUpgrade"` | **32 passed** |
| `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "~InstanceOp"` | **16 passed** |

So the item/gear chain — the executor, the store methods, the endpoint, the corpus reader and the
catalogue — is green at this head: 1470 + 323 + 859 + 32 + 16 measured, with the whole `Data.Tests`
project the one thing not run to completion. Every remaining red row this program owns is on the
seedsmith side (8 program-wide, from three causes) or blocked on an external decision.

## The seedsmith-actions boundary re-verified at the tip, after every edit (2026-09-23, lane sgc-6)

Every seedsmith edit this lane made (the `run_tool` helper, `open_checkpointer`, `is_authored` +
`plan()`, and the two test files) lands inside the `seedsmith-actions` / `seedsmith-tests` boundaries, so
the boundary's own selected files were re-run at the tip rather than only at each intermediate step:

| Chunk | Command (cwd `gk-forge/tools/seedsmith`) | Result |
|---|---|---|
| A (7 files) | `pytest tests/test_action_generation_batches.py tests/test_actions_adapter.py tests/test_brief_assembly.py tests/test_candidate_assembly.py tests/test_characteristic_pool.py tests/test_creature_themes.py tests/test_validate_heal.py -q` | **224 passed, 2 skipped, 8 subtests passed** in 79s |
| B (14 files) | `pytest tests/test_coverage_assignment.py tests/test_coverage_report.py tests/test_dedup_select.py tests/test_distribution_planner.py tests/test_family_propose.py tests/test_generate_coverage_assignment.py tests/test_innate_picker.py tests/test_signature_propose.py tests/test_type_weights.py tests/test_usage_direction.py tests/test_usage_direction_weights.py tests/adapters/trees/test_tree_species_plan.py tests/test_general_propose.py tests/test_usage_stats.py -q` | **776 passed, 1 skipped, 1179 subtests passed** in 3m48s |
| **total** | the two chunks | **1000 passed, 3 skipped, 0 failed** |

The three files NOT in those chunks are exactly the registered reds and this lane's own blocked row:
`test_actions_description_completeness.py` (the 5 `knownRed` `SR-25` cases), `test_cli.py` and
`test_corpus_loader.py` (**SGC5-F2**). So the actions boundary is green at the tip apart from what is
already filed — which is the "a lane's `verify-change` outcome is attributable to that lane's diff" claim
T55 box 4 asks for, measured rather than argued.

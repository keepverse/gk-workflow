# CAI4.8 — the `lawn.ai.decide` section share: published, and read

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. CAI4.8's fourth acceptance line reads: *"`lawn.ai.decide`
reports its own section, **outside** `KernelDriveHost`'s budget, with a share read from
`lawn-perf-budget.v1`"*. The section itself landed with the slot (its own `PerfSection`, measured around
the slot's body); this lands the SHARE — and the file's own `_meta` says whose it is: *"a later lawn perf
section (for example `lawn.ai.decide`, **whose share the combat-ai program owes**) is added beside these
three keys, never as a second file"* and *"a new section share … is added with `--add-key`, never by
hand"*.

| Criterion | Command | Result |
|---|---|---|
| The share is published the way the file's `_meta` prescribes | `python gk-core/tools/tuning/publish.py lawn-perf-budget --add-key ceiling:sections={"lawn.ai.decide": null} --label "…"` | ONE invocation: `ceiling.sections ADDED` / `published lawn-perf-budget (v1 -> v2, 1 change(s)); v1 stays on disk for revert` |
| It is DECLARED and UNMEASURED — the honest seed | `dotnet test gk-core/tests/FusionRpg.Core.Diagnostics.Tests` | **36 passed / 0 failed** — every one of the 7 new ones: `The_shipped_revision_declares_this_programs_section_and_it_is_unmeasured` asserts `TryGetSectionShare` true, the share `null`, and `IsSectionMeasured` **false**, i.e. no gate may pass on it yet (a clean 300-zombie A/B is `CAI5.1`'s live probe) |
| A measured share is read by name; a malformed one is refused | same run | `A_measured_section_share_is_read_by_name` (2.5 reads back and `IsSectionMeasured` true) and a `[Theory]` over a string, `0` and `101` — each refused rather than defaulted (a typo in the number that decides whether a feature ships must fail loudly) |
| The three original keys did not move (the publish is an addition) | same run | `The_three_original_keys_are_unchanged_by_the_addition` — 6 / 300 / null |
| The reader names the revision through a CONSTANT, so the publish and its reader move together | `Program.cs` + `LawnPerfBudgetFiles.Current` | the one production reader (`Server/Program.cs:232`) now reads `LawnPerfBudgetFiles.Current`; the loader's own "no default" message and the test suite's file-finder use it too, so no literal `lawn-perf-budget.v1.json` remains in code |
| The move of the version pin is the one the test itself predicted | `LawnPerfBudgetTuningTests.The_shipped_budget_states_the_reference_ceiling` | its own comment said *"a pass that wants a different number publishes v2, which moves this assertion deliberately"* — so `Version` is now asserted **2** with that reason on the line, while `SchemaVersion` stays 1 because the shape change is an added optional key |
| The Server still builds and no golden moved | `dotnet build gk-core/src/FusionRpg.Server`; `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "~BattleGolden"` | Build succeeded (0 errors); **5 passed / 0 failed** |

## What the share does and does not do

It DECLARES the gate. Nothing reads it as a pass: the parser exposes `IsSectionMeasured`, and the value the
file ships is `null`, so the 300-zombie A/B that decides the feature (`CAI5.1`/`CAI5.2`) has its key to fill
in and cannot accidentally read "no gate" or "passed" from an absent or null one. The slot's own reporting
(the `PerfSection.LawnAiDecide` measurement) is what that A/B will read.

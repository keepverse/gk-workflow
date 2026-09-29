# ST5.1 — the `TuningVersionAgreement` scan + the `AuraTuning` message

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| The scan takes its roots as parameters | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningVersionAgreement"` | **5/5 pass.** `ScanVersions(IReadOnlyList<string> roots)` and `VersionsOf(repoRoot, domain)` are public and root-parameterised; `DefaultRoots(repoRoot)` is the production pair (`src`, `gk-forge/tools/seedsmith/seedsmith`). Every fixture test below points the same scan at a temp root. | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |
| It matches `<domain>.v<n>.json` inside **string literals** and skips comment lines | same command | **Passes.** `The_scan_reads_a_string_literal_and_ignores_the_same_words_in_a_comment`: a `"gk-core/data/tuning/action-rungs.v4.json"` literal is read; the same filename in a `//` line and inside a `///` doc-comment is not. The regex's lookahead (`(?=["'])`) is what keeps it to literals — a filename followed by a quote — and comment lines are skipped first, whichever marker the language uses (`//`, `///`, `#`). | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |
| It asserts one version | same command | **Passes** as a mechanism: `A_reader_naming_a_second_version_is_the_disagreement_this_refuses` shows two readers on v4/v1 reported as `[1, 4]`. The per-domain real-tree rows belong to the tasks that make each domain agree — `action-rungs` in ST5.2, `action-base` in ST5.4 — since a row asserted before the readers agree is just a red test standing in for unfinished work. | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |
| **Planted violation:** a probe holding a second version fails; the probe is written and removed inside the test, and a failed delete fails the test | same command | **Passes.** `A_probe_holding_a_second_version_turns_a_green_scan_red_then_goes_away`: the scan starts single-version, writing `Probe.cs` makes it two, `File.Delete` is followed by an explicit `Assert.False(File.Exists(probe))` — asserted, never swallowed — and the scan is single-version again. The temp root is deleted in a `finally` with no `catch`, so a failed delete fails the test. | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |
| A build artifact is not a reader | same command | **Passes.** A copy under `bin/Debug/` naming another version does not count. | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |
| `AuraTuning.cs`'s message no longer names a version | same command | **Done.** The rejection message now reads "(the loaded rung ladder's own cap)" instead of `"(action-rungs.v1.json's own cap)"` — a message naming a stale file is the drift this guard exists for. | gk-core/src/FusionRpg.Core/Aura/AuraTuning.cs |
| The real-tree `action-rungs` row is **not** added here | code read | **Holds.** No row for `action-rungs` exists in this commit; the last test only asserts the scan *reaches* the real roots. ST5.2 adds that row when every reader moves to v4; ST5.4 adds `action-base`. | gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs |

## A finding the scan produced on the real tree

Running the scan over the real roots surfaces a disagreement outside this module's declared rows:
**`power-scale` is named at `v2` and `v3`** — `Program.cs:243` and `RpgHost.cs:181` read v2, while
`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/vocab.py:154` names v3. That is the same "a retune
reaches some readers and not others" defect this guard exists for. It is recorded rather than fixed:
`power-scale` belongs to the power program, not to this module's rows.

For reference, the two domains this module does own: **`action-rungs` currently disagrees** — v1 in
`Program.cs:256`, `RpgHost.cs:227` and `pool.py:31,85`, v3 in `generate_distribution_planner.py:60` and
`generate_validate_heal.py:54` — which is exactly what ST5.2 unifies; **`action-base` agrees at v2**
(`Program.cs:263`, `RpgHost.cs:237`), which is what ST5.4's row asserts.

## Note on the first attempt

The first attempt at this file was refused on its **second** edit as a "protected pipeline file". The
orchestrator has since identified that as a pipeline bug — the add-only rule treated a brand-new
Guard.Tests file as protected — and the file was re-created after the fix and finished as above.

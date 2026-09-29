# Evidence — rpg-simulator RS2.2 (the verdict and digest contract)

Lane `sim-runner`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-runner`
(branch `cmdc/sim-runner`). Module `readback-verdict`. Contract: `gk-core/tools/RpgSim/readback-verdict.md`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every reading records its source path | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter FullyQualifiedName~RpgSimVerdictContractTests` | pass: `A_verdict_reading_without_a_source_is_refused` + the serializer test asserts `"source"` in the artifact | `ScenarioVerdict.cs` (`Validate()`), `RpgSimVerdictContractTests.cs` |
| No digest-bearing read from `/api/test/snapshot` | same run + the RS2.1 read rule | implied by the wider rule: a `read.*` may not name `/api/test/*` or `/api/sim/*` at all | `ScenarioVocabulary.IsFeFacingRead`, `ScenarioValidator.ValidateRead` |
| Exclusion list written down, a reason per field | same run (`Every_baseline_exclusion_carries_a_reason`, `A_suffix_pattern_covers_the_six_spellings_of_the_same_wall_clock`) | pass: 10 entries, every reason substantive; `*Utc` blanks all six spellings; verdicts print the list | `ReadingDigest.Baseline` |
| The digest is not vacuous | same run (`The_digest_moves_when_a_read_value_moves`, `An_excluded_field_does_not_move_the_digest`) | pass: a moved value moves the hash; an excluded field does not | `ReadingDigest.Compute` |
| Same-run double-run falsifier | same run (`A_moved_digest_names_the_pointer_and_both_values`, `A_new_pointer_or_a_changed_array_length_is_reported_by_name`) | pass: `Compare` returns `Same` **and** the named pointers with from→to values | `ReadingDigest.Compare`, `DigestComparison.Report` |
| Golden artifact + hash (C2 (a)) | read `readback-verdict.md` §5 | specified: `gk-core/tests/fixtures/rpg-scenarios/golden/<id>.verdict.json`; **not yet written** — no run reaches a golden until RS2.3/RS2.4 | `readback-verdict.md` |
| Contract tests | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter FullyQualifiedName~RpgSim` | `Failed: 0, Passed: 35, Skipped: 0, Total: 35` (177 ms) | — |
| Whole E2E boundary | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` | run A `Failed: 1, Passed: 268, Skipped: 0, Total: 269` (2 m 11 s); run B (same command, `--no-build --verbosity normal`) no `[FAIL]` line — the single failure is **RS-CF2**, filed, second reproduction | `tasks/rpg-simulator-todo.md` RS-CF2 |

**NOT proved.**

- **No run happened.** No server, no HTTP, no scenario executed, no verdict produced, no digest computed
  over a real reading — RS2.3/RS2.4 own that. Every digest number here is over a literal payload.
- **The exclusion list is incomplete by construction** and its incompleteness is the falsifier's job: a
  payload with a volatile field the list does not name will move the digest, and the falsifier reports the
  pointer. The list was NOT derived by running the corpus (it cannot be yet).
- **The golden artifact does not exist yet.** Specified only.
- **Cross-host agreement is not exercised** (RS2.5's slow lane); this contract owns the comparison it calls.
- **The clock is still `ambient`**, so every timestamp is excluded by pattern rather than by a seam; RS3
  owns the seam and is gated.
- `gk-core/tools/RpgSim/**` still has no verification boundary (**RS-F3**), so the evidence above is direct
  `dotnet test` output, not `verify-change.ps1`.

# TVB5.4 — `SplitExecutor`: journal, `Apply`, `Revert`, `split --revert <journal>`

New `gk-core/tools/FileMove/SplitExecutor.cs`: `SplitJournal` (reuses `SplitOp` itself as the journal entry
type — a journal entry is a planned op with `Before`/`After` filled in for every kind that needs it),
`SplitRevertResult`, and `SplitExecutor` with `Apply`, `Revert`, `Keep`, `ReadJournal`.

## Behavior, per A4 items 2–5

- **Journal before touch (item 2).** `Apply` reads fresh "before" bytes for every `ModifyFile` op and
  the source bytes for every `MoveFile` op (re-read at apply time, not trusted from the plan snapshot,
  since Plan and Apply can run at different times), writes the journal to
  `<temp>/filemove-split-<guid>/journal.json`, and only then executes anything.
- **Reverse-order undo (item 3).** `Revert` walks the journal back to front. Before undoing each entry
  it checks the path still holds exactly what `Apply` wrote (`MatchesApplied`); the first mismatch stops
  the whole revert and returns `SplitRevertResult(Ok: false, BlockedPath, Reason)` — nothing after that
  point is touched, and the blocking path itself is left exactly as found.
- **Partial failure is the same path (item 4).** `Apply` catches any exception, calls the same
  `RevertEntries` routine `Revert` uses (limited to the ops that actually ran), then rethrows. A test
  fault hook (`onBeforeOp`) proves this without needing a real disk failure.
- **The journal is deleted only by `Keep`** — i.e. only for a kept increment (A4 item 2's exact
  wording). Both a manual `Revert` and an `Apply`-triggered auto-revert leave the journal on disk.
- **Dirty-path refusal (item 5)** already lives in `SplitPlanner` (TVB5.3) — `Apply` throws
  `InvalidOperationException` for a refused plan before touching anything, proven directly.

## `Program.cs`

- `--apply` now: `executor.Apply(plan)` → `dotnet build`/`dotnet test` (default-profile filter,
  `Category!=DiskSemantics&Category!=Heavy`, the one `scripts/test-fast.ps1` owns) for the new project
  and the residual → any failure reverts and exits 1 (or exit 3 if the revert itself is blocked) → all
  four steps green calls `executor.Keep` and exits 0.
- New `split --revert <journal.json>` command: reads the repo root from the current directory (a
  journal lives in the OS temp dir, not under the repo, so it cannot anchor the root walk itself),
  reverts, and maps a blocked result to **exit 3** with the blocked path and journal location — the
  process-level shape F10's `SplitRevertResult` is a unit test proxy for.
- Smoke-tested the CLI error paths directly: `split --revert <missing-file>` → exit 2 ("journal not
  found"); `split --revert` with no argument → exit 2 (usage). The full build+test round trip against a
  real manifest project is intentionally **not** run here — the spec is explicit that "the real
  increments are proven by the build+test step inside `--apply` and by `verify-change.ps1` on the moved
  paths" is TVB5.7's job, against an owner-reviewed manifest project, not a synthetic smoke fixture; the
  `SplitExecutor` unit tests below already prove the journal/apply/revert mechanics the CLI wraps.

## Tests

`gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs` (new), 5 cases against a **real temp tree**
(disk is genuinely the subject here, `testing-standard.md` R2), same fixture style as
`FileMoverTests` — throwing `Directory.Delete` in `Dispose`, no `catch`:

| Case | Spec ref |
|---|---|
| `F6_apply_then_revert_restores_every_original_file_and_removes_everything_created` | F6 — includes a planted `bin/` inside the new project dir, swept by the recursive `CreateDirectory` undo |
| `F9_a_fault_on_the_third_op_undoes_the_first_two_and_the_tree_equals_the_start` | F9 |
| `F10_revert_stops_at_a_file_edited_after_apply_and_leaves_it_untouched` | F10 |
| `Apply_throws_for_a_refused_plan_and_writes_nothing` | A4 item 5 (defensive) |
| `Keep_deletes_the_journal` | A4 item 2 (defensive) |

## Verification

| Criterion | Command | Result |
|---|---|---|
| Build | `dotnet build gk-core/tools/FileMove/FileMove.csproj -v q` | exit 0, 0 Error(s) |
| Focused run | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests -c Release --filter "FullyQualifiedName~SplitExecutorTests"` | 5/5 passed |
| Whole affected project, twice in a row (determinism, real-disk fixtures) | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests -c Release` | 36/36 passed both runs; `git status --short` clean after each (no leaked temp dirs) |
| CLI error paths | `dotnet run --project gk-core/tools/FileMove -- split --revert <missing>` / `split --revert` (no arg) | exit 2 both times, correct message |
| Whole affected project via the boundary tool | `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitExecutor.cs,gk-core/tools/FileMove/Program.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs -Session tvb-wave5-20260920` | test-substrate guard OK; `FusionRpg.FileMove.Tests` 36/36 passed |

No doc citation invalidated. `gk-core/tools/FileMove/SplitPlanner.cs` and `SplitManifest.cs` untouched by this
task.

Files: `gk-core/tools/FileMove/SplitExecutor.cs` (new), `gk-core/tools/FileMove/Program.cs` (modified: `--apply`
build/test gate, `split --revert`), `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs` (new).

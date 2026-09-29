# `diskw-fix2` evidence — Target 0b's two gaps

Lane `diskw-fix2`, program `data-test-substrate`, branch `cmdc/diskw-fix2`, worktree
`D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-diskw-fix2` (from `1cfd23902dfb`).
The acceptance is **the absence of the write** — never write-then-delete. Nothing here widens a guard to
pass, adds a `knownRed` entry, or re-exempts a baselined file.

## Gap 1 — the guard's own regression case for `untagged-file-store`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the in-repo case exists | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~TestSubstrateGuardTests"` | exit 0 — `Failed: 0, Passed: 7, Skipped: 0, Total: 7` (5 pre-existing + 2 new) | `gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs` |
| **fails on a planted** untagged file-backed store | same run — `Guard_fails_on_a_planted_untagged_file_backed_store` plants `DataTestStore.CreateFileBacked()` (no memory URI, no trait) in a throwaway tree, runs the real gate with `-Root`/`-BaselinePath`, asserts exit ≠ 0 + `TEST SUBSTRATE GUARD FAILED` + `untagged-file-store` | pass | `tests/FusionRpg.Guard.Tests/bin/Release/net8.0/` |
| **passes on the fixed tree**, and the tag is what clears it | same run — `Guard_exits_zero_on_the_current_tree`; `Guard_passes_the_same_file_backed_store_once_it_carries_the_DiskSemantics_trait` (identical text + the trait ⇒ exit 0) | pass | same |
| the gate itself on this tree | `python gk-core/scripts/guard-test-substrate.py` | exit 0 — `TEST SUBSTRATE GUARD OK` | baseline 28 lines, unchanged |

**NOT proved:** nothing. This replaces the blocker BU5 carried.

## Gap 2 — BU6: the six fixtures write nothing

`StructureCorpus.Load(path)` takes a directory and the type has no rows entry point (**BU8**), so each
fixture materialised `gk-data/packs/fusion/data/seed/structures` in `%TEMP%` and dropped one synthetic row beside the copy.
`StructureCorpusOverlay.LoadWithRows` now loads the real corpus read-only and appends those rows in memory,
keeping the superset property the fixtures' own comments rely on. **Six** files, not four —
`CargoCommands/BudgetDebitTests.cs:122` and `CargoCommands/ClaimPricingTests.cs:126` carried the identical
shape and BU6 did not name them.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| a default-profile run creates no `cargo-*-test-*` / `wonder-*-test-*` / `budget-debit-test-*` / `claim-pricing-test-*` directory | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "Category!=DiskSemantics&Category!=Heavy"`, those `%TEMP%` names polled every 100 ms | exit 0 — `Failed 0, Passed 1747, Skipped 0, Total 1747`; **before 29 / duringMax 29 / after 29**, created 0, removed 0 (set difference, not a count) | `%TEMP%\diskw-fix2-default.txt` |
| the six affected suites still pass | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "FullyQualifiedName~CargoCommandResolveTests\|FullyQualifiedName~BudgetDebitTests\|FullyQualifiedName~ClaimPricingTests\|FullyQualifiedName~CargoTransferTests\|FullyQualifiedName~WonderBuildTests\|FullyQualifiedName~WonderReachTests"` | exit 0 — `Failed 0, Passed 75, Skipped 0, Total 75`; 29/29/29 directories | `%TEMP%\diskw-fix2-suite.txt` |
| the gate is green and the ratchet did not grow | `python gk-core/scripts/guard-test-substrate.py` | exit 0 — `TEST SUBSTRATE GUARD OK`; baseline **28 lines**, none added, none re-added | `gk-core/scripts/test-substrate-baseline.txt` |
| the `temp-corpus` rule bites, and clears the fixed shape | throwaway gate copy `%TEMP%\guard-substrate-probe.ps1` (declared, **not** committed): planted corpus copy in a throwaway tree ⇒ exit 1 `ZzProbeCorpusCopyTests.cs: temp-corpus (new — not in baseline)`; the same file rewritten to `StructureCorpusOverlay.LoadWithRows(...)` ⇒ exit 0; this repo's tree ⇒ exit 1 naming **only** the two files below | as stated | predicate + transcript in the BU7 row of `tasks/data-test-substrate-todo.md` |

The rule is a contract — `Path.GetTempPath` + `File.Copy(` + `EnumerateFiles(…, SearchOption.AllDirectories)`
+ a `"data","seed"` path, strings kept — and it flags exactly two files, `WorldWonderWireTests.cs:203` and
`WorldWonderRelicWireTests.cs:170`, both in `gk-core/tests/FusionRpg.Server.Tests` and both outside this lane's
allowed paths. Landing it therefore means two forbidden baseline lines or a red gate, so it is filed as
**BU7** with the predicate and the ruling options.

**NOT proved:** `temp-corpus` is not in the gate (BU7), so this shape is fixed by hand, not enforced; those
two Server.Tests files still copy the corpus on every default-profile run; 29 pre-existing leaked `%TEMP%`
directories were left in place (not this lane's fence, and deleting them would not be a fix); no device byte
delta is measured (the proof is the absence of a directory write).

## Commits and the path-owned verification run

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| commits | `git log --oneline -3` | `76e25a08e` — the guard's own `untagged-file-store` case (Gap 1); `1bf219142` — the six corpus fixtures on in-memory rows (BU6/Gap 2); `c54354405` — the session record this lane had to add (see below) | branch `cmdc/diskw-fix2` |
| path-owned verification | the exact command in the block below | **exit 0** — guards `session-boundary` (`clean for 'diskw-fix2'`) and `test-substrate` (`TEST SUBSTRATE GUARD OK`); doc-citation audit 0 HIGH; data (sharded) `4 shards, 1722 tests, no overlap`; guard `Failed: 0, Passed: 593` | `%TEMP%\diskw-fix2-verify.log` |

```
pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('tasks/sessions/diskw-fix2.json','gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs','gk-core/tests/FusionRpg.Data.Tests/StructureCorpusOverlay.cs','gk-core/tests/FusionRpg.Data.Tests/CargoCommands/BudgetDebitTests.cs','gk-core/tests/FusionRpg.Data.Tests/CargoCommands/CargoCommandResolveTests.cs','gk-core/tests/FusionRpg.Data.Tests/CargoCommands/ClaimPricingTests.cs','gk-core/tests/FusionRpg.Data.Tests/CargoTransfer/CargoTransferTests.cs','gk-core/tests/FusionRpg.Data.Tests/WonderBuild/WonderBuildTests.cs','gk-core/tests/FusionRpg.Data.Tests/WonderReach/WonderReachTests.cs','docs/contributing/testing-standard.md','tasks/data-test-substrate-todo.md','tasks/data-test-substrate-ledger.jsonl','tasks/reports/diskw-fix2-evidence.md') -Session diskw-fix2"
```

The one D1 the audit reports is pre-existing and not this lane's: `tasks/data-test-substrate-todo.md:405`,
the BU2 row's citation of a shard-runner script that does not exist (that file is planned, never created),
which belongs to the test-verification-boundary program (`diskw-fix` recorded the same one).

**The session record is part of this change**, and that is a deviation worth naming: the brief's boundary
bullet requires "your session record's `worktree` path must be ABSOLUTE" and `verify-change.ps1 -Session
diskw-fix2` refuses to run without `tasks/sessions/diskw-fix2.json`, but no such record existed and the
lane's allowed-path list does not name it (`docs/contributing/session-boundary.md` §3 requires one,
"committed with the session's first change"). Without it the brief's named verification command cannot run
at all, so it was created and committed alone (`c54354405`).

## BU8 — `StructureCorpus` gained its in-memory entrance

`StructureCorpus.Load(path)` walks a directory; `FromRows(rows)` is the entrance beside it (`Load` now routes
through it), `WithRows(extraRows)` returns a superset as a **new** corpus, and `Rows` is a read-only view — so
a fixture gets a corpus with one extra row without writing anything (BU6's six fixtures), and a corpus cannot
change under its holder. The overlay's append-through-the-backing-list workaround is gone.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the entrance is pinned; appending through `Rows` throws | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "FullyQualifiedName~StructureCorpusOverlayTests"` | exit 0 — `Failed 0, Passed 3, Skipped 0, Total 3` | `gk-core/tests/FusionRpg.Data.Tests/StructureCorpusOverlayTests.cs` |
| the six fixtures still pass on it | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "FullyQualifiedName~CargoCommandResolveTests\|FullyQualifiedName~BudgetDebitTests\|FullyQualifiedName~ClaimPricingTests\|FullyQualifiedName~CargoTransferTests\|FullyQualifiedName~WonderBuildTests\|FullyQualifiedName~WonderReachTests"` | exit 0 — `Failed 0, Passed 75, Skipped 0, Total 75` | — |
| the change's real blast radius in Core | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~World"` | exit 0 — `Failed 0, Passed 1265, Skipped 0, Total 1265` | — |
| the module boundary the registry selects for it (`core-fallback`) | `verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs -Session diskw-fix2` | run 1: **all 55** Core projects `Passed!`, 0 `Failed!` (incl. `Core.Atoms.Tests` `Failed 0, Passed 1351`); its exit code was lost when the harness truncated that 17-minute command inside its final Guard suite. Retry (60 `dotnet` hosts, CPU 100%): aborted on the wall-clock budget already filed as effect-atom **E13**, `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AtomBenchGuardTests.cs` — `median 158.34 ns/atom exceeds 75`, raw 41.84–242.04, isolated retries swinging 41→2204 ns | `%TEMP%\diskw-fix2-bu8-verify.log`, `%TEMP%\diskw-fix2-bu8-core.log` |
| guard + ledger | `python gk-core/scripts/guard-test-substrate.py`; `python gk-core/scripts/anchor-ledger.py tasks/data-test-substrate-ledger.jsonl check` | exit 0 `TEST SUBSTRATE GUARD OK`; `LEDGER OK (17 events)` | — |

**NOT proved:** a green **exit code** for `core-fallback` — unreachable on a box running 60 `dotnet` hosts
while E13's wall-clock test sits in that boundary. Not weakened, not skipped, not filtered; the change itself
is additive (a static factory plus a read-only view) and touches nothing on the atom-predicate path.

## BU7 — the `temp-corpus` rule landed, and its two offenders stopped copying

The rule proven in the first segment is in the gate, and the two files it flagged — outside the lane's
original fence, moved on the manager's 2026-09-23 steer — build their rows on `StructureCorpus`'s in-memory
entrance instead. Nothing is baselined: the ratchet is untouched at 28 lines.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the gate is green with the rule in it | `python gk-core/scripts/guard-test-substrate.py` | exit 0 — `TEST SUBSTRATE GUARD OK … or shipped-corpus copies into temp …`; `gk-core/scripts/test-substrate-baseline.txt` **28 lines**, no line added or re-added | `gk-core/scripts/guard-test-substrate.py` |
| the rule bites a planted copy and clears the in-memory shape — **the committed script**, against a throwaway tree | `python gk-core/scripts/guard-test-substrate.py --root "$env:TEMP\diskw-fix2-probe2" --baseline-path "$env:TEMP\diskw-fix2-probe2\baseline.txt"` | planted `Path.GetTempPath` + `File.Copy` corpus copy → exit 1, `…ZzProbeCorpusCopyTests.cs: temp-corpus (new — not in baseline)`; the same file rewritten to the in-memory entrance → exit 0 | `%TEMP%\diskw-fix2-probe2` |
| the same two shapes as in-repo cases | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~TestSubstrateGuardTests"` | exit 0 — `Failed 0, Passed 9, Skipped 0` (7 before + `Guard_fails_on_a_planted_corpus_copied_into_a_temp_dir` + `Guard_passes_a_fixture_that_appends_corpus_rows_in_memory_instead`) | `gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs` |
| the two fixed suites pass and create no temp directory | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~WorldWonderWireTests\|FullyQualifiedName~WorldWonderRelicWireTests"`, `%TEMP%` `wonder-wire-*` names captured before/after | exit 0 — `Failed 0, Passed 12, Skipped 0`; **15 before / 15 after, created 0** | `%TEMP%\diskw-fix2-wire.txt` |
| path-owned verification for the whole change | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/scripts/guard-test-substrate.py','gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs','gk-core/tests/FusionRpg.Server.Tests/WorldWonderWireTests.cs','gk-core/tests/FusionRpg.Server.Tests/WorldWonderRelicWireTests.cs','docs/contributing/testing-standard.md','tasks/data-test-substrate-todo.md','tasks/data-test-substrate-ledger.jsonl','tasks/sessions/diskw-fix2.json','tasks/reports/diskw-fix2-evidence.md') -Session diskw-fix2"` | **exit 0** — guards `test-substrate` + `session-boundary` (`clean for 'diskw-fix2'`); doc-citation audit 0 HIGH; guard `Failed 0, Passed 595`; server `Failed 0, Passed 803` | `%TEMP%\diskw-fix2-bu7-verify.log` |

**NOT proved:** the 15 pre-existing `wonder-wire-*` directories were left in `%TEMP%` (not this lane's
fence); the synthetic-row builder is now duplicated between `StructureCorpusOverlay` and the two
Server.Tests files, whose shared home would be `FusionRpg.TestSupport` — outside this session's fence; and
seven Core.Tests wonder/import suites still write a synthetic corpus to disk (no copy, so the rule does not
match) — filed as **BU9**.

## BU9 — the write-shaped sibling: no corpus file in `%TEMP%`, and the shape is refused

`StructureCorpus.FromJson` is the file format's in-memory entrance (`Load` routes through the same parser),
so a suite that authors its own rows hands over the text instead of writing a corpus file. All seven
Core.Tests wonder/import suites were moved onto it; the gate gained `temp-corpus-write` beside `temp-corpus`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the seven suites pass and create no temp directory | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --no-build --filter "FullyQualifiedName~WonderEmpireEffectsTests\|FullyQualifiedName~WonderUpkeepTests\|FullyQualifiedName~SectorItemCapacityTests\|FullyQualifiedName~StructureCatalogImportTests\|FullyQualifiedName~WonderBuildResolverTests\|FullyQualifiedName~WonderCatalogTests"`, their `%TEMP%` patterns polled every 100 ms | exit 0 — `Failed 0, Passed 77, Skipped 0` (74 before + 3 new `FromJson` cases); `wonder-empire-test-*` / `wonder-upkeep-test-*` / `sector-item-capacity-test-*` / `structure-corpus-import-test-*` / `wonder-build-test-*` / `wonder-catalog-test-*`: **before 0 / duringMax 0 / after 0** | `%TEMP%\diskw-fix2-bu9.txt` |
| the blast radius in Core | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --no-build --filter "FullyQualifiedName~World"` | exit 0 — `Failed 0, Passed 1265, Skipped 0, Total 1265` | — |
| the module boundary (`core-fallback`) | `verify-change.ps1 -Paths <the src file + the 6 Core.Tests files> -Session diskw-fix2` | all **55** Core projects `Passed!`, 0 `Failed!`; the run then failed on `VerificationBoundaryWorkflowTests.…` — see the timeout row below (exit code lost when the harness truncated the command) | `%TEMP%\diskw-fix2-bu9-core.log` |
| the gate refuses the write shape and clears the in-memory one | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~TestSubstrateGuardTests"` | exit 0 — `Failed 0, Passed 11, Skipped 0` (9 before + the two `temp-corpus-write` cases); `python gk-core/scripts/guard-test-substrate.py` exit 0 on this tree with the baseline still **28 lines** | `gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs` |
| the gate's own cost (fixed here, not merely observed) | `pwsh -NoProfile -Command "$sw=[Diagnostics.Stopwatch]::StartNew(); & gk-core/scripts/guard-test-substrate.py | Out-Null; $sw.Stop(); …"` | **22.8 s → 8.3 s** on this tree after one read + two strip passes per file instead of one per rule (five reads, eight strip passes); the self-test class went **2 m 8 s → 16 s** | `gk-core/scripts/guard-test-substrate.py` |
| the load timeouts in the two verification runs | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~A_data_fallback_module_check_plans_the_sharded_runner"` and `…~P6_the_real_registry_resolves_seedsmith_and_tuning` | both `verification-boundary script timed out` (their own 120 s budget) inside suites that took 11 m 55 s / 13 m 5 s on a box running 34–60 `dotnet` hosts at 84–100 % CPU (5 m 47 s measured earlier in this session); **both pass alone: 1/1, 50 s and 1 m 40 s**; both are already filed at `tasks/test-verification-boundary-todo.md:350` and `:502` | `%TEMP%\diskw-fix2-bu9-guard.log`, `%TEMP%\diskw-fix2-bu9-guardsuite.txt` |

**NOT proved:** a green exit code for the Guard suite and for `core-fallback` on this box while it runs
34–60 concurrent `dotnet` hosts — every failure in those runs is a 120 s subprocess budget in
`VerificationBoundaryWorkflowTests` (another program's tests, already filed there and isolation-green), never an
assertion about anything this lane touched. Not weakened, not skipped, not filtered, nothing baselined.

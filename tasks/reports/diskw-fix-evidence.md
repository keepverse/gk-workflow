# `diskw-fix` evidence — BU5: the memory-DB rule enforced

Lane `diskw-fix`, program `data-test-substrate`, branch `cmdc/diskw-fix` (worktree
`D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-diskw-fix`, from `2f118fe1454c`).
The owner's rule, which this lane implements and never works around: **remove the disk path — never
"write, then clean up"** (*"write on the disk will destroy ssd, delete the temporary won't help anything,
it worsen"*). The proof below is therefore the **absence** of the write, not a deleted directory.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| E2E opens no file: **no `fusionrpg-e2e-*` directory is created** | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --no-build`, with `%TEMP%` polled every 200 ms while it ran | exit 0; `Failed 0, Passed 234, Skipped 0, Total 234`; `fusionrpg-e2e-*` under `%TEMP%`: **10 before / 10 during / 10 after**; residual `e2e-file-*` under the test bin: **0** | `tests/FusionRpg.E2E.Tests/bin/Release/net8.0/diskw-e2e-run.txt` |
| The E2E test-id set is unchanged — nothing was skipped to get there | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --list-tests --no-build` | **234** ids, sha256 `b52d40b324d420f415ed960948c0ab965eb9696d0bf501eab63b2c8f23876a94`. The same scan **without** `--no-build` prints 240 lines = those 234 ids + the 6 MSBuild `-> …dll` lines, so the first capture's "240" was that build-output pollution (reproduced on the fixed tree) | `git diff -- tests/` removes no `[Fact]`/`[Theory]`/test method and adds no `Skip=` |
| The default profile opens no store file | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"`, output dir polled every 100 ms | exit 0; `Failed 0, Passed 1747, Skipped 0, Total 1747`; `teststore-*`: **0 before / 0 during / 0 after**, and 0 anywhere under `tests/` | `tests/FusionRpg.Data.Tests/bin/Release/net8.0/diskw-data-default.txt` |
| Guard exits 0 on the fixed tree, and the `RpgApiFactory` exemption is retired | `python gk-core/scripts/guard-test-substrate.py` | exit 0, `TEST SUBSTRATE GUARD OK`; baseline **29 → 28** lines and no `FusionRpg.E2E.Tests` line left (the file stopped matching `temp-store`; no exemption was re-added, no line added) | `gk-core/scripts/test-substrate-baseline.txt` |
| The new `untagged-file-store` rule bites on a planted violation | `python gk-core/scripts/guard-test-substrate.py --root "$env:TEMP/diskw-probe" --baseline-path "$env:TEMP/diskw-probe/baseline.txt"` — three planted files: untagged `DataTestStore.CreateFileBacked()`; the same **with** the trait; `new RpgStore(Path.GetTempPath())` with the trait only in a comment | **exit 1**: `ZzProbeTests.cs: untagged-file-store`, `ZzCommentOnlyTests.cs: temp-store, untagged-file-store`; the tagged probe is **not** listed. (The `obe/` prefix in the printed rel path is the guard's own display quirk with a short-form `%TEMP%` root; the codes and files are correct.) | probe tree left at `$env:TEMP/diskw-probe` (3 tiny files, re-runnable) |
| The todo row exists, with its id | `grep -c "BU5" tasks/data-test-substrate-todo.md` | `2` | `tasks/data-test-substrate-todo.md` |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths <the 20 changed paths> -Session diskw-fix` | **exit 0** — guards `dal` / `session-boundary` / `test-substrate` OK, doc-citation audit 0 HIGH, data (sharded) `4 shards, 1722 tests, no overlap`, e2e `225/225`, guard `591/591`, server `803/803` | `tests/FusionRpg.Guard.Tests/bin/Release/net8.0/diskw-verify-change.log` |

## verify-change

`.\scripts\verify-change.ps1 -Paths <the 20 changed paths> -Session diskw-fix` → **exit 0**. It maps them to
`test-substrate-guard`, `testing-standard-doc`, `server-fallback`, `session-and-program-records`,
`data-tests-fallback` and the `e2e-*` boundaries, then runs guards `dal` / `session-boundary` /
`test-substrate` (`TEST SUBSTRATE GUARD OK`, `[session-boundary] clean for 'diskw-fix'`), the doc-citation
audit (0 HIGH; one pre-existing D1 on the BU2 row's `scripts/test-shard.ps1`, which is the other program's
row and was left alone), and tests `data` (sharded: 4 shards, 1722 tests, no overlap, all exit 0), `e2e`
(225/225 — 9 file-bound tests now excluded by their new `DiskSemantics` tag), `guard` (591/591) and
`server` (803/803). Two earlier failures were fixed, not worked around: (i) `guard-dal.ps1` flagged
`src\FusionRpg.Server\Program.cs: matches /SqliteConnection/`, so the composition root now spells out the
Data-owned predicate's own two conditions instead of naming the SQLite type; (ii) the doc-citation audit's
D1 was this file not existing yet.

**Reading, explained (not a defect).** The sharded default-profile run reports 1722 tests while the
unsharded `--list-tests` reports 1747. Per shard, `--list-tests` under that shard's exact filter gives
449 / 40 / 83 / **1175** = 1747 — the partition is complete — while the runner reports 449 / 40 / 83 /
**1150**. The 25 difference is the rest shard's theory rows: the project has 12 `[Theory]` methods and 37
data attributes (37 − 12 = 25), the runner counts TRX test names (theories collapsed) and the three
prefixed shards contain no theories. So nothing is skipped; the runner's *count* is method-level.

## NOT proved

- **Bytes written.** This lane proves the absence of a directory, not a byte delta on the device. A
  sample-based byte measurement belongs to the architect lane (`diskw-arch`), which owns the design half.
- **A `gk-core/tests/FusionRpg.Guard.Tests/**` case proving the rule bites.** The brief asked for it; the pipeline
  hook refuses every edit to `gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs` ("protected pipeline
  file" — it is the gate's own self-test), so the planted-probe run above is the strongest achievable
  proof. Recorded as a blocker note; needs a ruling (unlock the file for this lane, or add the case).
- **The four Cargo/Wonder fixtures** still copy the structures corpus into a `%TEMP%` directory in the
  default profile (`CargoCommandResolveTests.cs:142`, `CargoTransferTests.cs:139`, `WonderBuildTests.cs:182`,
  `WonderReachTests.cs:154`). They construct no store, so no rule flags them; filed as **BU6**.
- **Concurrency of two hosts in one process.** Both E2E collections disable parallelization (the server
  reads `FUSIONRPG_DATA` from the process environment), so two hosts never boot at once; the tests' own
  `OpenStore()` handles sharing one named database are exercised, two live hosts are not.
- **The 10 pre-existing leaked directories (5.15 GB) were left in place** — deleting them is not this
  lane's call and is not a fix; they are the measured symptom, and `%TEMP%` is not this lane's fence.

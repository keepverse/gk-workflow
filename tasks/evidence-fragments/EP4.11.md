# EP4.11 - the stock is never trimmed; the owed section 3 registry row

**All three acceptance points are green.** The registry row landed, the architecture half is a source
scan, and the runtime half now runs on a file-backed store. Commit `@EP4.11` (partial) - session
`empire-progression-3` - branch `cmdc/ep-3` - spec `spec-respec-free-counter.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The owed `empire-resource-ssot.md` section 3 Accrual-meter row lands as the map drafted it | `python gk-core/tools/tuning/resource_ownership.py --check` | `OK -- 166 generated edges match aptitudes.v10.json's 166 resource edges exactly` | `docs/architecture/empire-resource-ssot.md:56` - free empire respec, Accrual meter, held by the empire `(SaveId, EmpireId)` surviving a world, fed by `empire-level`, sunk by a species respec at the player's choice, never a unique or commander respec, owner `empire-progression`, table `rpg_empire_free_respec_ledger` |
| No compaction or archive method references `rpg_empire_free_respec_ledger` | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireFreeRespec"` | `Passed! - Failed: 0, Passed: 14, Skipped: 0, Total: 14` - `No_compaction_or_archive_pass_names_the_free_respec_ledger` scans every `gk-core/src/FusionRpg.Data/Sqlite/*.cs` and asserts the table is named by exactly `RpgStore.EmpireFreeRespec.cs` and `RpgStore.cs`, none of which is a compaction/archive/trim file; a final assertion keeps it from passing vacuously if the table is ever renamed | `gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs` |

**The runtime half of test 12 runs on a FILE-BACKED store, and why that was necessary is itself part of the
evidence.** `CompactAfterRunClosed` and `TrimHotTailsNow` both refuse on an in-memory plan:
`StorePlanException: A memory plan has no filesystem archive; archive entry points are file-only until the
archive-target module makes the archive target memory-capable`. Every store test in this assembly runs in
memory by design (the testing standard's own rule), so "a stock read after a compaction run equals the read
before it" needs a `DataTestStore.CreateFileBacked()` store of its own - the helper exists and its dispose is
leak-proof. Recorded in the test's own doc comment rather than dropped, and the row stays open for it.

**A stale Verify command, filed rather than worked around:** the row's own Verify line says
`python scripts/audit-doc-citations.py docs/architecture/empire-resource-ssot.md`, but that script takes no
positional path - it takes `--scope`/`--targets`/`--strict`. The working form is
`python scripts/audit-doc-citations.py --targets docs/architecture/empire-resource-ssot.md`, which I ran and
which passed silently for that one document. Worth correcting in the todo if the command is meant to be
copy-pasteable.

**Not proved:** the live compaction assertion above; and the registry row's own claim that the stock "survives
a world" is asserted only through the key shape `(save_id, empire_id)` plus the `SUM(delta)` read, not by a
world-boundary test.

# Lane `diskw-fix` — enforce the memory-DB rule: stop the tests writing to disk at all

**Session:** `diskw-fix` · **Program:** `data-test-substrate` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.E2E.Tests/**`, `gk-core/tests/FusionRpg.Data.Tests/**`,
`gk-core/tests/FusionRpg.Guard.Tests/**`, `gk-core/scripts/guard-test-substrate.py` *(granted: extending this guard IS the work)*,
`gk-core/scripts/test-substrate-baseline.txt`, `docs/contributing/testing-standard.md`, `tasks/data-test-substrate-todo.md`,
`tasks/reports/**`

## The rule, and the correction that defines this brief

This repo's hard rule (`AGENTS.md`, "Test substrate"; `docs/contributing/testing-standard.md` R1/R2) is that a
store test runs **in memory**, and the disk is used **only when the disk is the thing under test**.

⛔ **The owner has ruled out the wrong fix explicitly:** *"we don't try to write on the disk and delete, it is
wrong way to fix — write on the disk will destroy ssd, delete the temporary won't help anything, it worsen."*
So: **never "write files, then clean them up."** The write is the damage; deleting adds more. **Remove the disk
path entirely.** A fix whose proof is "the temp dir was deleted" is not a fix and will be rejected.

## What is measured (do not re-derive it)

- `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:11` — `DataDir = Path.Combine(Path.GetTempPath(), "fusionrpg-e2e-" + Guid)`; `:17` and `:20` create it and hand it to the server as `FUSIONRPG_DATA`. Its `Dispose` deletes it.
- Measured on this machine: **10 leaked `fusionrpg-e2e-*` dirs, ~5.15 GB**, individual runs up to **1.7 GB**, and live writes of ~11.5 MB/s to `rpg-hot.sqlite.pre-save-identity.<ts>` plus its WAL. The owner saw it in Task Manager and stopped the work over it.
- `gk-core/src/FusionRpg.Server/Program.cs:467-472` — `Directory.CreateDirectory(dataDir); new RpgStore(dataDir)`, unconditional: booting the real server can *only* mean writing two SQLite files.
- `gk-core/scripts/test-substrate-baseline.txt:11` — `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs : temp-store`. The guard **already flags this file**; the exemption was never retired. The ratchet only shrinks.
- Five Data.Tests files build a file-backed store **without** the `DiskSemantics` tag, so they run in the default profile: `SoulLedgerTrimTests.cs`, `ExpeditionRewardApplyTests.cs`, `WebGameIsolationTests.cs`, `EmpireFreeRespecTests.cs`, `DataTestStoreTests.cs`.

## The plumbing already exists — use it

- `SqliteConnectionFactory.MemoryUri(name)` → `file:{name}?mode=memory&cache=shared` (`SqliteConnectionFactory.cs:9-17`).
- `RpgStoreOptions.InMemory` + `HotName`/`MediaName` (`RpgStoreOptions.cs:19-23`); `Resolve()` **throws** if a memory URI is passed with `InMemory:false` (the URI trap) — do not defeat that check.
- The keeper pattern: a shared-memory DB lives only while a connection is open — see `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs:80-83` (*"the store's keepers must be open before we seed, or the shared-memory database would vanish"*) and `Reopen()`.

## Work

1. **Server**: when `FUSIONRPG_DATA` is a memory URI, build the store as
   `new RpgStore(RpgStoreOptions.For(dataDir, inMemory: true).Resolve())` and **skip `Directory.CreateDirectory`**.
   A real directory path must behave exactly as today — this is a conditional, not a rewrite.
2. **E2E factory**: point `FUSIONRPG_DATA` at a **named shared-memory** URI, hold the seeding store in a **field as
   the keeper** (mirroring `DataTestStore`), and **delete the temp-dir property, both `Directory.CreateDirectory`
   calls, and the Dispose delete**. After this the temp dir does not exist, so there is nothing to leak and
   nothing to delete. The genuinely file-bound E2E cases (storage purge, archive slices, the backup sidecar)
   keep a file host **and** the `DiskSemantics` tag.
3. **Guard** (`gk-core/scripts/guard-test-substrate.py`): retire the `RpgApiFactory.cs` baseline line — by making the file
   stop matching, never by re-adding the exemption — and add the contract rule: **a `tests/**` file that constructs
   a file-backed store (`new RpgStore(<path>)`, `CreateFileBacked()`, or `Path.GetTempPath`) must carry
   `[Trait("Category","DiskSemantics")]`**. Contract, not a count and not a name list.
4. **Tag the five** Data.Tests files above `DiskSemantics` (their comments already justify the disk where it is
   justified) so the default profile opens no file.
5. **Prove it bites**: a `gk-core/tests/FusionRpg.Guard.Tests/**` case that plants the violation and fails on it.

## Proof — this is the acceptance, and it must be the *absence* of the write

- Run the E2E project and assert that **no `fusionrpg-e2e-*` directory is created during the run** (snapshot
  `%TEMP%` before/after and print the counts). *The directory never appearing is the evidence; a deleted directory
  is not.*
- `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` → print
  that **no `teststore-*` directory appears** during it.
- `gk-core/scripts/guard-test-substrate.py` exits 0, and the new rule fails on the planted violation (show both).
- The E2E suite's own pass counts, before/after, so it is clear nothing was skipped to get there.

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- a row in `tasks/data-test-substrate-todo.md` for the finding, **with the id asserted present**
- ⛔ Never widen a guard to pass; never add a `knownRed` entry; never re-add a baseline exemption
- ⛔ Do not weaken the URI trap or add a silent fallback to a file path — a test that silently writes to disk is
  the exact defect this lane exists to end

## Boundaries

- Another lane (`diskw-arch`) holds the idea/spec/plan half and is **stopped** — do not write `docs/architecture/**`
  or design docs; this lane is the enforcement and the fix.
- Your session record's `worktree` path must be **ABSOLUTE**.

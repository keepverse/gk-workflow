# Test substrate standard

**Status: binding for every automated session.** A test must not write its data to the developer's
SSD, and a cleanup that fails must never be silent. This is the policy the
[`guard-test-substrate.py`](../.scripts/guard-test-substrate.py) gate enforces.

**Why this exists.** SQLite connection pooling holds the database file handle past `Dispose`, so a
`Directory.Delete` on a test's temp dir throws `IOException` — and 153 of 154 delete sites swallowed
it with an empty `catch { }`. One full local run leaked **30,978 directories / 65.5 GB**. The defect
was not the test assertions; it was the substrate and the silent catch. Full reasoning:
[data-test-substrate-ideal.md](../architecture/data-test-substrate-ideal.md).

---

## 1. The rules

**R1 — A store test runs in memory by default.** A test for the SQL layer (schema, constraints,
upserts, watermarks, joins, migrations) constructs its store through the shared test helper in
memory. It does not create a temp directory and does not build an `RpgStore` from a path.

**R2 — Disk only when the disk is the thing under test.** A test may use a real file **only** when
what it asserts is file behaviour: a legacy `rpg.sqlite` migration and its backup sidecar, `PRAGMA
journal_mode` returning `'wal'`, `File.Exists` on hot/media, archive slices on disk, storage purge.
Those are named in the gate's baseline and must say in the test why a file is required.

**R3 — A failed cleanup is a failure.** Never `catch { }` a temp delete — not `catch { /* temp */ }`,
not `catch (Exception) { }`. If the delete fails, the test fails and says why. An empty catch around
a delete is the specific pattern that hid 65.5 GB; it is banned outright.

**R4 — The baseline only shrinks.** The gate carries a baseline of the files that predate this
standard. **Removing a line is required when the file is fixed; adding one is a review event** that
needs a reason and the owner's sign-off. A stale baseline line (fixed but not removed) fails the
gate, so the ratchet cannot quietly grow back.

**R5 — Assert the relationship, never a population count.** The leak guard and the "0 files" check
assert a delta (`before == after`) and the closed-enum/structural properties — never a fixed count of
files or tests, per [validation-ssot.md](../architecture/validation-ssot.md).

---

## 2. What the gate bans (mechanically)

| Code | Bans | Rationale |
|---|---|---|
| `swallowed-delete` | `Directory.Delete(...)` inside an empty or comment-only `catch` block, anywhere in `tests/**` | R3. This is the exact shape that hid the leak. |
| `temp-store` | A `tests/**` file that both constructs `new RpgStore(` and references `Path.GetTempPath` | R1/R2. After migration a store test is memory or an allowlisted file-semantics case — never an ad-hoc temp path. |
| `untagged-file-store` | A `tests/**` file that constructs a **file-backed** store — `DataTestStore.CreateFileBacked()`, `new RpgStore(` with the memory plan nowhere in the file, or `RpgStoreOptions.For(dir)` with one argument — and carries no `[Trait("Category", "DiskSemantics")]` | R1/R2. The trait IS the default profile's filter, so an untagged file-backed store opens a real file on every routine run. Contract, never a count and never a name list. Added 2026-09-23 (`diskw-fix`) after five Data.Tests classes built a real store through the helper's file plan — `AppContext.BaseDirectory`, so neither rule above could see them — and each run paid a full `Init()` (schema, migrations, WAL) on a real file. |
| `temp-corpus` | A `tests/**` file that copies the **shipped seed corpus** into a temp directory to get a corpus it can add rows to: a temp-rooted path + `File.Copy` + an `AllDirectories` walk of a `"data","seed"` root | R1. The corpus is data, so a suite that needs the shipped rows plus one row of its own appends them in memory (`StructureCorpus.FromRows`/`WithRows`) — the copy, its directory and its delete are a write nothing needs. Contract, never a count and never a name list (the seed root is recognised by its own literals). Added 2026-09-23 (`diskw-fix2`) after **eight** files copied all 28 files of `gk-data/packs/fusion/data/seed/structures` per run, times every lane: six in `gk-core/tests/FusionRpg.Data.Tests` and two in `gk-core/tests/FusionRpg.Server.Tests`. |
| `temp-corpus-write` | A `tests/**` file that **writes a structure-corpus document** into a temp directory and loads it back: a temp-rooted path + `File.WriteAllText` + `StructureCorpus.Load` | R1, and the same class as `temp-corpus` on the same reasoning — one copies the shipped corpus, this one authors its own rows. Both are answered by the corpus's in-memory entrances (`StructureCorpus.FromJson` for document text, `FromRows`/`WithRows` for rows). Same `DiskSemantics` escape hatch as `untagged-file-store`, because a test whose **subject** is the loader's file contract legitimately needs a file. Added 2026-09-23 (`diskw-fix2`, BU9) after seven Core.Tests wonder/import suites wrote one on every run. |

A file is exempt only by an explicit baseline entry. There is no silent allowlist.

**Added 2026-09-23 (`diskw-fix2`, BU9).** Seven Core.Tests wonder/import suites
(`World/Loam/WonderEmpireEffectsTests`, `World/Loam/WonderUpkeepTests`, `World/SectorItemCapacityTests`,
`World/StructureCatalogImportTests`, `World/WonderBuildResolverTests`, `World/WonderCatalogTests`) wrote a
synthetic corpus JSON into `%TEMP%/<suite>-test-{guid}` and loaded it back on every run — the write-shaped
sibling of the copy above. They now hand their rows to `StructureCorpus.FromJson`, which is `Load`'s own
parser fed from memory, and write nothing; the gate gained `temp-corpus-write` beside `temp-corpus`.
Nothing here is baselined: `gk-core/tests/FusionRpg.Core.Tests/World/**` is clean by construction, not by exemption.
A corpus file is still legitimate when the file contract **is** the subject — that is what the trait is for.

---

## 3. How to satisfy the gate

```csharp
// Before — the defect
_dir = Path.Combine(Path.GetTempPath(), "fusionrpg-actions-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(_dir);
_store = new RpgStore(_dir);
_store.Init();
public void Dispose() { try { Directory.Delete(_dir, recursive: true); } catch { /* temp dir */ } }

// After — in memory
using var store = DataTestStore.Create();   // in-memory, keeper held, no temp dir

// After — file semantics only, leak-proof
using var store = DataTestStore.CreateFileBacked();   // clears pools before delete; delete failure throws
```

**A fixture that needs rows the shipped corpus does not carry holds them in memory.** The shipped structure
corpus is data, not a file-system contract, so a suite that needs one synthetic depot or wonder row does not
copy `gk-data/packs/fusion/data/seed/structures` into a temp directory to get a loadable corpus:

```csharp
// After — the real rows plus the synthetic ones, written nowhere
StructureCatalog.Configure(StructureCorpusOverlay.LoadWithRows(
    StructureCorpusOverlay.Depot("test-depot", itemStorageCapacityBonus: 6)));
```

`StructureCorpus.Load(path)` reads the committed corpus, `WithRows(extraRows)` returns those rows plus the
suite's own **in memory**, and `FromJson(document)` is the same thing for a suite that authors its rows as
document text — `Load` and `FromJson` share one parser, so a literal and a committed file cannot drift apart.
The result preserves the superset property (every shipped row still present) that a suite reading the static
catalog concurrently depends on. Eight fixtures made the temp copy and
were moved onto it on 2026-09-23 (`diskw-fix2`): six in `gk-core/tests/FusionRpg.Data.Tests` through
`StructureCorpusOverlay`, and the two `gk-core/tests/FusionRpg.Server.Tests` wonder-wire files, which build their rows
directly on the entrance. Seven more (`gk-core/tests/FusionRpg.Core.Tests/World/**`) authored their own corpus file
and were moved onto `FromJson` the same day. The gate refuses both shapes: `temp-corpus` and
`temp-corpus-write`.

---

## 4. How this is enforced

- `gk-core/scripts/guard-test-substrate.py` — the gate. Run by `deploy-play.py`, CI, and
  `gk-core/tests/FusionRpg.Guard.Tests`.
- `gk-core/scripts/test-substrate-baseline.txt` — the ratchet. One line per `path : code`.
- The local instruction files (`AGENTS.md`, `CLAUDE.md`) may restate this rule in full — on purpose, because a pointer does not survive a long session — but this document is the source: when they disagree, this document wins and the local file is corrected.

Update the baseline only with `guard-test-substrate.py --update-baseline`, review the diff, and state
why any line was **added**.

---

## 5. Applying it to the rest of the suite

This standard covers `tests/**`. The store migration (in-memory substrate) is the
[data-test-substrate](../architecture/data-test-substrate-map.md) program; this gate lands first so
no new violation can be introduced while that migration proceeds.

---

## 6. Test profiles

### Verification boundaries select before profiles filter

For local agent work, first run `python gk-core/scripts/verify-change.py --paths <changed files> --session
<active-session-id>`. The
verification registry selects the focused/module/seam checks for those explicit paths; profiles then
decide whether broad selected checks exclude `DiskSemantics` or `Heavy`. CI/nightly/release remains
the owner of ordinary unfiltered full evidence. A production path without a registry mapping fails
fast as a boundary defect; it is never a reason to run every project. A failing selected check is
diagnosed at its own boundary, never retried as a broad/full suite. Use `--deleted-paths <former path>`
for a deletion; the planner can resolve its recorded owner without requiring the file to still exist.
Test sources are enforced the same way as production sources: every file under `tests/**` and
`tools/*.Tests/**`, and every `*.Tests.csproj` under `tests/` or `tools/`, has an owner or a named
exemption (`registry-contract` C1, C2) — an unmapped test file or an unregistered, non-exempt test
project fails the integrity guard, not just an unmapped `src/**` file. The Core test projects are
registered together as the `core` project **group** (`registry-contract` C7): the residual
`FusionRpg.Core.Tests` plus every `FusionRpg.Core.<Area>.Tests` project `core-split-apply` has moved out of it
— **67 projects after the split landed** (2026-09-22, `TVB5.8.68`; the manifest's 68th,
`FusionRpg.Core.GlobalUsings.Tests`, is skipped because its file is a `global using` alias file every Core
test assembly must compile, TVB-F17). A module-level check on a `gk-core/src/FusionRpg.Core/**` path runs every
member, so a Core production change never verifies less now that the split has happened: the residual still
holds 10,012 of its original 14,837 tests, and the rest run in their own projects (each listed in `ci.yml`,
`release.yml` and this file's own broad profile, `scripts/test-fast.ps1 -AllDefault`).

**Data inputs select through the planner too.** A change under one of the four enforced roots —
`gk-core/data/tuning/**`, `gk-core/tests/fixtures/**`, `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/**` — is planned by
`verify-change.py` against a registered owner exactly like a source file, not left to a whole-suite
run: a generated tree selects its generator's own check (plus the `generated-seed` guard), a schema or
fixture selects the test that loads it, and a registry/seam adds a second check without replacing the
first. An input for which no local check exists carries an explicit `full` boundary instead of a fake
project; the planner prints `<path> -> <boundary> (full): no local check; CI full evidence owns this
input` and selects nothing, and `-Report` lists every such input. `full` is legal only under `data/**`
and `gk-core/tests/fixtures/**`, and it means **CI-only**: nightly and the release gate still exercise it
unfiltered. Every file under an enforced root resolves to an owner — the guard fails on an unmapped
file there, so a new content subtree needs a registry row before it ships, and no root is switched on
until it is fully mapped.

A changed path under `gk-forge/tools/seedsmith/**` or `gk-core/tools/tuning/*.py` selects through the same registry
and the same planner, by file, as a C# change — there is no separate Python code path: an
`adapters/items/**` edit plans the items test files plus the `gen-items-gate` generator-check seam,
never the whole seedsmith suite. A selected Python test that is already red on a clean tree is never
silently dropped to make the lane green: it is registered once as a `knownRed` entry
(`{project, test, debt}`, `debt` naming a `red` row in `docs/architecture/stub-register.md`) and it
keeps running every time it is selected. A `knownRed` failure prints `KNOWN RED (pre-existing) <test>
-> <SR-id>` and the check still passes; any other failure still fails the check; and a `knownRed` test
that passes fails the check with `stale knownRed entry` — the list only shrinks, and the fix commit
that clears the debt is the one that removes the entry. CI stays unfiltered and red until the owning
program fixes the tree.

Not every test belongs on every run. A test whose **subject is the disk** (WAL mode, a legacy
`rpg.sqlite` migration and its sidecar, archive slices, purge) or that takes **≥20s** earns a trait
so it can be excluded from the routine loop and run where the disk is cheap and the wait is
acceptable — CI, nightly, and the release gate. Nothing is deleted or weakened: a tagged test still
runs in `full`.

### The two categories

| Category | Meaning | Where |
|---|---|---|
| `DiskSemantics` | The file **is** the thing under test — it must write a real fixture tree. | Excluded from `default`; runs in `full`/nightly/gate. |
| `Heavy` | ≥20s or cold-process or long-run, with no disk requirement. | Excluded from `default`; runs in `full`/nightly/gate. |

A test is tagged at the **class** level when every method qualifies, at the **method** level when
only some do. When both could apply, `DiskSemantics` wins — it is the stronger statement, and either
exclusion removes the test from the default profile.

### The four profiles

| Profile | Where | Command |
|---|---|---|
| **default** | explicit local broad validation, `deploy-play.py` | `.\scripts\test-fast.ps1 -Project <project>` → `dotnet test <proj> --filter "Category!=DiskSemantics&Category!=Heavy"` |
| **full** | CI pull-request | `dotnet test <proj> -c Release` (no filter) |
| **gate** | `release.yml` tags | `dotnet test <proj>` (no filter), required |
| **nightly** | `.github/workflows/nightly.yml` | `dotnet test <proj>` (no filter) |

**The default lives in exactly one place.** `gk-core/scripts/test_fast.py` owns the filter, so deliberate
broad local validation cannot drift. Agents use `verify-change.py` first; `deploy-play.py` still
calls the explicit default profile. CI keeps calling `dotnet test` directly with
**no** filter, so CI is `full` by construction and can never accidentally inherit the dev default.
A negative filter includes uncategorized tests, so only the *excluded* tests need a trait.

### The guards run on `full` only — except the static gate, which runs on `default` too

**The runtime leak alarm (`test_substrate_leak_alarm.py`) runs against the `full` profile only.** The
default profile *intentionally* writes the file-bound directories — those are the `DiskSemantics` tests —
so a disk-leak alarm run around it would either false-positive every time or need an ever-growing
allowlist. **Do not "optimize" the alarm onto the fast profile.**

**The static gate (`guard-test-substrate.py`) also runs in the default profile** — added 2026-09-13.
It reads *source*, so it is profile-independent and cannot false-positive on those intentional writes: it
refuses a test that **swears** a temp delete, builds a store from a temp path, or builds a file-backed
store without the `DiskSemantics` tag that would keep it out of the routine loop. `gk-core/scripts/test_fast.py`
calls it first and exits non-zero on failure ("DEFAULT PROFILE REFUSED"), which makes the dev loop
**self-guarding** — a leaking test cannot be added and then run unnoticed. Verified by planting a
leaking probe: `test_fast.py` refused with the file named, then the probe was removed.

`full` is the only profile that catches a disk regression at *runtime* — hence the nightly workflow: it
reruns everything unfiltered within a day, instead of waiting for a release tag.

### Wall-clock is its own axis — see the burden audit

The profiles above reduce what runs by *category*. **Test wall-clock is a separate axis, and the
obvious reading of it is wrong.** [test-burden-audit.md](test-burden-audit.md) (measured 2026-09-13)
records the two facts that matter before anyone tunes a "slow" test:

1. **Per-test durations in a full-suite TRX are not cost.** Under parallelism they absorb contention —
   the top 25 Data.Tests classes showed **53×–230× inflation** (median ~160×). Re-measure a suspect
   test **in isolation** before concluding anything.
2. **Data.Tests is fastest at ~2 threads, not 32** — 87s vs 367s wall, a **4.2×** difference. A pure-CPU
   control on the same machine scaled 6.58× at 8 threads, so this is a property of the store path, not
   of a busy box.

**That second fact has a cause, and the cause changes the fix.**
[test-architecture-audit.md](test-architecture-audit.md) proves it is a **process-global mutex inside
SQLite's in-memory VFS** (`SQLITE_MUTEX_STATIC_VFS1`, taken on every in-memory database open —
`src/memdb.c`), so in-memory databases cannot parallelize *within a process* at all, while **file**
databases scaled 3.25× on the same machine. The correct lever is therefore a **process** boundary, not a
thread cap: two concurrent `dotnet test` processes measured **23.9s vs 47.4s sequential**. Read that
document before touching parallelism — a thread cap treats the symptom and permanently forfeits cores.

That document also lists the hypotheses **already ruled out with numbers** (`ClearAllPools`,
shared-cache mode, GC, batch shape, raw DDL, machine load), so they are not re-tested, and the two real
defects it found (`EnsureColumn`'s swallowed `ALTER TABLE`; the `--no-build` stale-assembly trap).

**The process-boundary lever is a reusable runner, not a one-off measurement.**
`data-tests-sharding` (`test-verification-boundary`) turns "N concurrent processes over a complete,
disjoint partition" into `gk-core/scripts/test_sharded.py` plus a manifest (`gk-core/scripts/test-shards.v1.json`):
one project id per entry, named shards as class/namespace prefixes, and exactly one `remainder` shard
whose filter is the exact complement of the named ones, so completeness is a property of the
partition's construction, not of counting. It builds the project once, runs each shard as its own
`dotnet test` process against its own results directory, and checks every run for overlap (an id
executed in two shards) and for an empty named shard (a manifest defect) before reporting success.
CI adopted it for `FusionRpg.Data.Tests` (`ci.yml`, R15); a **local** `verify-change.py` module-level
check on a project the manifest owns also delegates to it, with `-ExtraFilter` set to the one default
profile filter `gk-core/scripts/test_fast.py` owns — never restated as a second copy of that string. A
**focused** (`VerificationId`) check stays a plain `dotnet test`: it is small, and the shard runner's
own bookkeeping (build the manifest view, spawn N processes, read N TRX files) would be pure overhead
for a handful of tests.

---

## 7. The baseline register — every remaining line and why

`gk-core/scripts/test-substrate-baseline.txt` is the ratchet. It holds `path : code` lines with **no inline
comments** (the parser splits on `:` and would read a comment as part of the code), so the *reasons*
live here. After T18b–T18e (2026-09-12) every remaining line falls into four honest groups. The groups
are described by **membership, not by a count** — a pinned total is a population reading that goes
stale the moment a file is fixed or a test project changes, which is the anti-pattern
[validation-ssot.md](../architecture/validation-ssot.md) bans.

### Group 1 — file-bound by subject (`gk-core/tests/FusionRpg.Data.Tests`)

| File | Why it keeps real files |
|---|---|
| `RpgStoreDalSmokeTests` | asserts `PRAGMA journal_mode == 'wal'`; memory has no WAL |
| `RpgStoreSmokeTests` | asserts `File.Exists(HotPath/MediaPath)` |
| `LegacyMonoMigratorTests` | migrates a real legacy `rpg.sqlite` and asserts a disk sidecar |
| `ColdArchiveCompactionTests` | archive `*.sqlite` slices written/listed/verified on disk |
| `StoragePurgeTests` | purge deletes real archive files |
| `CreatureSpeciesImportCliTests` | launches a cold subprocess that imports the real committed tree (owned by the `cold-process-test-build` session) |
| `SoulLedgerTrimTests` | every method drives an archive entry point (`TrimSoulLedgerTails`) that refuses the memory plan |
| `ExpeditionRewardApplyTests` | one method (`Soul_trim_keeps_a_mixed_earn_spend_ledger_consistent`) drives `TrimSoulLedgerTails`; the rest are memory |
| `WebGameIsolationTests` | one method (`Closed_web_runs_are_exempt_from_capture_archiving`) drives `CompactAfterRunClosed`; the rest are memory |
| `EmpireFreeRespecTests` | one method (`The_stock_survives_a_compaction_run_on_a_file_backed_store`) drives `CompactAfterRunClosed`/`TrimHotTailsNow`; the rest are memory |
| `DataTestStoreTests` | the helper's own file-plan proof rows (the unique `teststore-*` directory, its initialized schema, the pooled-connection delete, the throwing delete) |

These are **excluded from the default profile** via `DiskSemantics` (T26) and run at `full`/nightly/gate.
They must **not** be converted to memory — that would delete real coverage (`substrate-standard` R2).

**Added 2026-09-23 (`diskw-fix`).** Five classes were file-backed and **untagged** —
`SoulLedgerTrimTests`, `ExpeditionRewardApplyTests`, `WebGameIsolationTests`, `EmpireFreeRespecTests`,
`DataTestStoreTests` — so the default profile ran them: one real directory and one full `Init()` (schema,
migrations, WAL) per construction, per run, times every concurrent lane. The guard's third rule
(`untagged-file-store`) now refuses that shape. Note the granularity the lane chose for the four mixed
classes: the tag sits on the **class**, per the owning brief's instruction, which also removes those
classes' memory methods from the default profile — the file-bound method is named in each row above so the
reason is visible, and moving a tag down to the method is the smaller change if the owner prefers the
narrower exclusion.

**Added 2026-09-23 (`diskw-fix2`).** Six structure-corpus fixtures in this project used to copy the shipped
`gk-data/packs/fusion/data/seed/structures` corpus into `%TEMP%` on every run and layer one test row over the copy:
`CargoCommandResolveTests`, `CargoTransferTests`, `WonderBuildTests`, `WonderReachTests`, and the two BU6 did
not name — `BudgetDebitTests`, `ClaimPricingTests`. None is file-bound by subject: the depot exists only to
give a sector item capacity, and the rows are data. They now hold those rows in memory
(`StructureCorpusOverlay.LoadWithRows`) and write nothing, so they are **not** baselined and stay in the
default profile. The same shape in `gk-core/tests/FusionRpg.Server.Tests` (`WorldWonderWireTests`,
`WorldWonderRelicWireTests`) was fixed the same way and the gate gained the `temp-corpus` rule, so the copy
cannot come back in either project; the write-shaped sibling in `gk-core/tests/FusionRpg.Core.Tests` is BU9.

After T18f (2026-09-12) the four store classes among them (`RpgStoreDalSmokeTests`,
`ColdArchiveCompactionTests`, `StoragePurgeTests`, `RpgStoreSmokeTests`) route their store and cleanup
through the leak-proof **file** helper or `ClearAllPools` + a throwing delete, so their cleanup can no
longer swallow. Three then dropped off the static baseline entirely (`RpgStoreDalSmokeTests`,
`ColdArchiveCompactionTests`, `StoragePurgeTests`): their disposal is the helper's, so the scanner no
longer finds `new RpgStore(` beside a temp path. `LegacyMonoMigratorTests` and `RpgStoreSmokeTests`
keep a baseline line **only for the `temp-store` pattern** — both legitimately boot a store over a
**hand-built on-disk file** (a legacy `rpg.sqlite`; a hot-only folder whose media is recreated), which
is exactly the disk-is-the-subject case R2 permits. `CreatureSpeciesImportCliTests` remains baselined
end to end because it is another session's cold-process test, not migrated here.

**Being on the static baseline is not a defect for a file-bound class** — the baseline is what stops a
*new* file-backed store appearing anywhere else. After T18f the only `swallowed-delete` lines left
inside this program's four Store test projects are the two files the program deliberately does **not**
own: `CreatureSpeciesImportCliTests` (another session's cold-process test) and
`BaseTypeSocketMaxCorpusTests` (class C, a fixture-leak fix, not a store migration). Every other
`swallowed-delete` line is in the out-of-boundary Guard/Launcher/AtomImporter projects (Group 4).

### Group 2 — file-bound host (`gk-core/tests/FusionRpg.E2E.Tests`)

`RpgApiFactory.cs` used to be `temp-store`-baselined: it pointed `FUSIONRPG_DATA` at
`%TEMP%/fusionrpg-e2e-{guid}` and handed that directory to the real server, so **every** E2E boot wrote
`rpg-hot.sqlite`, `rpg-media.sqlite` and their WAL. Measured 2026-09-23 on this machine: **10 leaked
directories, 5.15 GB**, live writes of ~11.5 MB/s. The exemption was retired by making the file stop
matching, not by re-adding the line (`diskw-fix`, 2026-09-23):

- **`RpgApiFactory` is now the memory host.** It passes a named shared-memory URI as `FUSIONRPG_DATA`
  (`Program.cs` builds `RpgStore` on the memory plan for a memory URI, and derives the two database names
  from that URI so the host's store and the fixture's seeding keeper address the same databases). It holds
  the seed store in a field as the **keeper** — a shared-memory database exists only while a connection is
  open — exposes `OpenStore()` for a test that needs its own handle, and has no data directory, no
  `Directory.CreateDirectory` and no delete in `Dispose`. Measured: a full run (234 tests) creates **no**
  `fusionrpg-e2e-*` directory at all, before/during/after.
- **`FileBackedRpgApiFactory`** is the file-plan host for the cases where the disk **is** the subject:
  `StorageE2ETests` (the archive catalog/purge endpoints refuse the memory plan by construction) and
  `TypeIconE2ETests` (asserts the file plan's own hot/media files and the absent `icons` mirror). Both
  classes carry `DiskSemantics` and both collections disable parallelization. Its directory is under the
  test output root (not `%TEMP%`), and its delete throws rather than swallowing (R3).

### Group 3 — class-C, not a store test (`gk-core/tests/FusionRpg.Server.Tests`)

`BaseTypeSocketMaxCorpusTests.cs : swallowed-delete` — no `new RpgStore(`; it writes a real nested
JSON fixture tree for `BaseTypeSocketMaxCorpus.Load(root)`, so the fixture **is** the subject. Fixed
2026-09-13: it is now `[Trait("Category", "DiskSemantics")]` and its cleanup **throws** instead of
swallowing (R3). It writes no SQLite, which is why the gate's `temp-store` rule never applied to it.

### Group 4 — outside this program's boundary

`FusionRpg.Guard.Tests`, `FusionRpg.Launcher.Tests`, `FusionRpg.AtomImporter.Tests`. These are **not
store tests** and not in the four test projects this program owns; their `swallowed-delete` lines are
baselined and ratcheted by the gate but not migrated here. A future program can take them.

**The ratchet only shrinks.** Fixing any line above requires removing it; a stale line fails the gate.
Adding a line is a review event requiring a stated reason — and if the file is genuinely file-bound,
it belongs in a group above, not silently added.

# Lane `diskw-fix2` — close Target 0b's two gaps: the guard's own regression case, and BU6

**Session:** `diskw-fix2` · **Program:** `data-test-substrate` · **Mode:** worktree
**Fence:** `gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs` *(**PROTECTED — explicitly granted to this
lane**; the previous lane was refused it and asked for this ruling)*, `gk-core/tests/FusionRpg.Data.Tests/**`,
`gk-core/scripts/guard-test-substrate.py`, `gk-core/scripts/test-substrate-baseline.txt`, `tasks/data-test-substrate-todo.md`,
`tasks/reports/**`, `docs/contributing/testing-standard.md`

## Context — the rule, and what is already done

The owner's rule, which this program enforces: **tests use the memory DB, not real files on disk.** ⛔ Writing and
then deleting is *not* a fix (*"write on the disk will destroy ssd, delete the temporary won't help anything, it
worsen"*) — the acceptance is the **absence of the write**.

Lane `diskw-fix` already landed (merged as `6b1cd2576`, and propagated to all seven in-flight lane branches): the
server's memory plan, `RpgApiFactory` on a named shared-memory store with a keeper, the `untagged-file-store`
guard rule, the retired `RpgApiFactory` baseline line, and the five Data.Tests classes tagged. Its evidence report
(`tasks/reports/diskw-fix-evidence.md`) names **exactly two gaps** — they are your work.

## Gap 1 — the guard's own regression case

The `untagged-file-store` rule exists and bites (proven by a planted-probe run with `-Root`/`-BaselinePath`), but
the **in-repo case could not be added**: the pipeline hook refuses every edit to
`gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs` ("protected pipeline file" — the gate's own self-test).

**That refusal is lifted for this lane.** Add the case, in the shape the other guard self-tests use: it must
**fail on a planted untagged file-backed store** and **pass on the fixed tree**. If the harness still refuses the
path, stop and report that precisely rather than working around it — a guard whose own test cannot be written is
the finding.

## Gap 2 — BU6: four fixtures still write a temp corpus in the default profile

Row **`BU6`** in `tasks/data-test-substrate-todo.md` (line ~460). `CargoCommandResolveTests.cs:142`,
`CargoTransferTests.cs:139`, `WonderBuildTests.cs:182`, `WonderReachTests.cs:154` each copy the **whole**
`gk-data/packs/fusion/data/seed/structures` corpus (29 files, 128 KB) into `%TEMP%/cargo-*-test-{guid}` / `wonder-*-test-{guid}` and
layer one test depot over it, because `StructureCorpus.Load(path)` takes a **directory** and the shipped 25 rows
carry no `ItemStorage` capacity. They construct no `RpgStore`, so neither guard rule sees them.

**Fix the shape, not the symptom:**
1. Make those four tests write **nothing** in the default profile — e.g. give the loader a rows/in-memory entry
   point (the corpus is data, not a file system contract), or pass the rows the test already needs. A test that
   only needs 1 depot row must not copy 29 files to get it.
2. **Extend the guard rule** so the shape cannot come back: a `tests/**` file that copies a corpus into a temp
   directory is the same class as an untagged file-backed store. Keep it a **contract** (a shape, not a file
   list) and prove it with a case in the same self-test as Gap 1.
3. If for one of the four the disk genuinely *is* the thing under test, tag it `DiskSemantics` **and say why in
   the commit** — that is a ruling you are making, not a workaround.

## Acceptance — the absence of the write, printed

- The Guard.Tests case: **fails on a planted violation, passes on the fixed tree** (show both runs).
- A default-profile run of the affected project(s) creates **no** `cargo-*-test-*` / `wonder-*-test-*` directory:
  print the before/during/after counts.
- `python gk-core/scripts/guard-test-substrate.py` → exit 0.
- `gk-core/scripts/test-substrate-baseline.txt` **shrinks or stays** — never grows, and no line is re-added.
- `tasks/data-test-substrate-todo.md`: `BU6` ticked with the evidence; the id asserted present.

## Evidence contract

- exact command text and the numbers printed; the committed SHA; an explicit **NOT-proved** list
- ⛔ Never widen a guard to pass; never add a `knownRed` entry; never re-exempt a baselined file; never write a
  file and delete it as the "fix"

## Boundaries

- Another lane's design half (`diskw-arch`) is stopped — do not write `docs/architecture/**`.
- Your session record's `worktree` path must be **ABSOLUTE**.

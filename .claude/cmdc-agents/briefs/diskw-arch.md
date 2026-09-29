# Lane `diskw-arch` — sample-based disk testing: idea → spec → plan

**Session:** `diskw-arch` · **Program:** `data-test-substrate` · **Mode:** worktree
**Fence:** `docs/architecture/**`, `tasks/**` — **design only. No test edits, no script edits, no product code.**

## The problem, measured (do not re-derive it)

The owner watched a suite run in Task Manager and saw **heavy, sustained disk writes**, with the concern stated
plainly: *"current heavy write and it can break the ssd"*. The measurements already taken:

- `test-fast.ps1`'s default filter is `Category!=DiskSemantics&Category!=Heavy`, and its own header says the point:
  *"so a routine run writes nothing to the SSD."* So a test that touches real files is supposed to carry
  `DiskSemantics` and be excluded from routine runs.
- **Five files build a real-file store without that tag**, so they run in the **default** profile and write SQLite
  files on every routine run — and with twelve lanes running suites concurrently, every run pays it:
  `gk-core/tests/FusionRpg.Data.Tests/SoulLedgerTrimTests.cs` (file-backed in the constructor),
  `ExpeditionRewardApplyTests.cs`, `WebGameIsolationTests.cs`, `EmpireFreeRespecTests.cs`, `DataTestStoreTests.cs`.
  Each one *justifies* the disk in a comment (their subjects are archive entry points that throw on a memory plan,
  or the helper itself) — the **use** is legitimate under the standard's R2; the **tag** is missing.
- `gk-core/scripts/guard-test-substrate.py` bans only `swallowed-delete` and `temp-store` (a file with both
  `new RpgStore(` and `Path.GetTempPath`). `DataTestStore.CreateFileBacked()` uses `AppContext.BaseDirectory`, so
  it trips neither rule — that is the hole that let this drift silently.
- The heavy cost is **frequency, not volume**: each file-backed construction runs a full `Init()` (schema,
  migrations, WAL) against a real file. No test seeds anything like a million rows; the only 100k-iteration loops
  in the tree are in-memory harness loops (`AtomFormBench.cs:133`, `AtomBenchGuardTests.cs:72`,
  `AtomRunnerTests.cs:378`).

## The owner's directive for the design

> *"make idea/spec/plan to improve, we should test on the sample of data instead of try to brute force testing"*

So the design must replace **brute-force** testing — long runs, large seeds, "exercise everything by volume" —
with **sample-based** testing: the smallest fixture that still exercises the code path under test, chosen and
justified per test rather than by repeating work.

## Deliverable

1. **`docs/architecture/test-substrate-disk-idea.md`** — the idea, using `.agents/skills/idea-refine/SKILL.md` as
   the method (the owner asked for idea work; follow its understand → diverge → converge shape and label the steps).
   It must state, per disk-touching test: **what file behaviour it actually asserts** (the R2 justification), and
   what the *smallest* fixture is that still proves it.
2. **A spec** (`docs/architecture/test-substrate/spec-*.md`) for the sample-based substrate: what a disk test may
   do, what a sample must be (representative, minimal, deterministic), and how a test declares its sample.
3. **A plan** (`tasks/data-test-substrate-plan.md` or the program's existing plan): the increments, each with a
   measurable acceptance — including the guard rule below, and the **before/after measurement** of what a routine
   run writes (e.g. file-backed store constructions per default run, or bytes written where measurable). A plan
   whose improvement cannot be measured is not a plan.
4. **The enforcement contract**: a guard rule of the shape *"a `tests/**` file that constructs
   `DataTestStore.CreateFileBacked()` must carry the `DiskSemantics` trait"* — a contract check, stable across
   generations, never a count or a name list. Say how the guard should express it and how its own test proves it
   bites.

## Evidence contract

- every claim about the tree carries `file:line`; an explicit **NOT-proved** list; the docs committed
- findings routed to the owning program's todo, **with the id asserted present**
- do not propose weakening a guard to make anything pass

## Boundaries

- ⛔ Design only. Another lane (`diskw-fix`) is applying the immediate mitigation (tagging the five, adding the
  guard rule) in parallel — **do not edit those files**, and do not duplicate its work; reference it.
- Your session record's `worktree` path must be **ABSOLUTE**.

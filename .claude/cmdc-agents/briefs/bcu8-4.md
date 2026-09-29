# Lane brief — `bcu8-4` (data-test-substrate BU1: `EnsureColumn` swallows a failed `ALTER TABLE`)

## The row

`tasks/backlog-clean-up-todo.md` **BCU8.4** — `data-test-substrate` BU1 · S · deps: — ·
*Verify:* `verify-change` + `guard-test-substrate.py`.

**Manager-recorded fence (2026-09-20, still in force):** this row was blocked because
`gk-core/src/FusionRpg.Data/**` lay outside the session that found it, not because the work was unclear. It must be worked
with **`gk-core/src/FusionRpg.Data/**` and `gk-core/tests/FusionRpg.Data.Tests/**` in `--allow`**; **the fix and its test land as
one commit**; the row's Verify line stands unchanged. The remedy is yours to design.

⛔ Read `docs/DESIGN-GATE.md` §1 first (its `data-test-substrate` / Data row) and the documents it names, in this
session, then verify against code.

## The defect

`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:4304`:

```csharp
static void EnsureColumn(SqliteConnection db, string table, string column, string def)
{
    try { Exec(db, $"ALTER TABLE {table} ADD COLUMN {column} {def};"); }
    catch { /* already exists */ }
}
```

The `catch` is unconditional, so it cannot tell the two cases apart:

- **expected and harmless** — the column already exists (the idempotent re-run path every boot takes);
- **a real failure** — malformed `def`, an unknown table, a locked or corrupt database, a typo'd column name.

The second is swallowed exactly like the first, so a genuine schema error is **silent**: the boot continues and the
failure surfaces later, somewhere else, as a missing-column or a wrong-shape error far from its cause. This is the
same class the repo's own substrate standard already refuses for temp-deletes (`guard-test-substrate.py`'s
`swallowed-delete`) — *a failed operation is a failure, never `catch { }`* — and it applies to SQL identically.

## Deliverable

1. **Narrow the catch to the genuine duplicate-column case** (SQLite raises the duplicate-column error for an
   existing column; match that specific condition, e.g. via `SqliteException.SqliteErrorCode`/`SqliteExtendedErrorCode`
   and/or the message) and let **every other failure propagate**. Do not replace one blanket swallow with another —
   the test below is what proves the difference.
2. **A test in `gk-core/tests/FusionRpg.Data.Tests/**` with a planted-violation case**, proving both halves:
   - an existing column is still tolerated (the idempotent path works — e.g. call `EnsureColumn` twice);
   - a *different* failure **propagates** (e.g. a malformed definition or an unknown table throws), so the rule is
     known to bite rather than assumed to.
3. **One commit** carrying both, with the row ticked in the same commit and the row id asserted present after the edit.

## Fence (your session paths)

- `gk-core/src/FusionRpg.Data/**` — the fix
- `gk-core/tests/FusionRpg.Data.Tests/**` — the test
- `tasks/backlog-clean-up-todo.md`, `tasks/backlog-clean-up-ledger.jsonl` — the row
- `tasks/data-test-substrate-todo.md` — the owning program's row, if it carries a pointer

Anything else is another session's fence — name it as a dependency instead of reaching across.

## Hard rules

1. **Test substrate:** tests run **in memory**; disk only when the disk is the thing under test.
   `gk-core/scripts/guard-test-substrate.py` enforces it (a `tests/**` file constructing a file-backed store must carry
   `[Trait("Category","DiskSemantics")]`) — tag only what genuinely tests file behaviour.
2. **Never widen a guard, never add a `knownRed`, never re-add a baseline exemption.**
3. **No magic numbers on the balance surface** (this row should touch none).
4. **SQL lives only in `FusionRpg.Data`** (`guard-dal.ps1`) — the fix belongs where it is.

## Verification

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session bcu8-4`
- `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --nologo --filter "<your test>"` — read the printed counts; the planted violation must throw before the fix and pass after it.
- `python gk-core/scripts/guard-test-substrate.py` — must exit 0.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-dal.ps1` — must stay green.

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report

End every segment with the `<<<REPORT {...} REPORT` block (status/summary/closed/open/blocked/next); every claim in
it must already be a commit in this worktree.

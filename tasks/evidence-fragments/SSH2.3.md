# SSH2.3 — `combogen-migrate --write` verb

## Order of operations (recorded before editing)

1. Read `docs/architecture/strain-splice-host/spec-combination-regen.md`'s rename bundle #5 and
   `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py`'s own module docstring: the
   retirement is a BUNDLE (5 sites), only site 1 (the gating metric) was previously done, and the
   deletion of the 25 legacy entries (site 5) is explicitly the one gated on the real 102-entry
   corpus existing — that gate belongs to SSH2.6 (later, deps SSH2.3+SSH2.4), not this task. This
   task's job is narrower: build the `--write` VERB itself (deterministic, idempotent, ledgered),
   never invoke it against the real corpus.
2. Read the CURRENT `_cmd_items_combogen_migrate` (`cli.py`): it hard-refused anything but
   `--dry-run`, with a comment saying the real deletion was gated on full coverage — confirming (1)
   and confirming no `--write` mode existed at all yet.
3. Designed `migrate.retire_legacy_partition(*, legacy_path=None, ledger_path=None)`, injectable
   for tests (mirrors `legality_report`'s own `path` override), defaulting to the REAL production
   `LEGACY_FILE`/a new `combogen-migrate.ledger.json` beside it — so the CLI's real `--write` path
   (unexercised by any test in this task) uses the real paths, and every test stays off the real
   corpus by injecting a temp `legacy_path`/`ledger_path`.
4. No hard edge from H1/H2/H7 is touched: no combat numbers move, no re-keyed table (this is a
   Python seed-corpus file, not a DB table; H2's own scope is C#/SQLite migrations), no tuning
   publish. H3 unaffected (module 4's cap deletion is unrelated to this file retirement).

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py` — new `RetirementRecord` dataclass,
  `RETIREMENT_RULING`/`RETIREMENT_LEDGER_KEY`/`DEFAULT_MIGRATE_LEDGER` constants, and
  `retire_legacy_partition()`: deletes the legacy file (`Path.exists()` check, not
  `unlink(missing_ok=True)`, so the caller gets an honest `file_deleted_this_call` bool) and writes
  a SINGLE fixed-key `RunLedger` row with NO wall-clock field — the absence of a timestamp is what
  makes a second call byte-identical, not just "also succeeds" (matches this program's own
  `authored_utc`-is-injected precedent for reproducibility).
- `gk-forge/tools/seedsmith/seedsmith/report/cli.py`:
  - New `--write` arg on the `combogen-migrate` subparser.
  - `_cmd_items_combogen_migrate` now dispatches `--write` to `migrate_mod.
    retire_legacy_partition()` (production defaults — no path overrides at the CLI layer) before
    falling through to the existing `--dry-run` report path; refusal message updated to name both
    modes.
- `gk-forge/tools/seedsmith/tests/test_combogen.py` — new `MigrateWriteTests` (3 tests, all against an
  injected temp `legacy_path`/`ledger_path` — never the real corpus):
  - `test_the_migrate_verb_writes_a_ledger_record_and_is_idempotent` (SSH2.3's own named acceptance
    test): first call deletes the file and records a real ledger row; second call finds the file
    already gone (`deleted=False`, no error) and reproduces a BYTE-IDENTICAL ledger file.
  - `test_the_record_is_readable_through_run_ledgers_own_api_and_carries_no_clock_field` — the
    record reads back through `RunLedger.read_done()` (never a bespoke second reader), and carries
    no `deletedAtUtc`/`timestamp` field.
  - `test_deleting_an_already_gone_file_is_a_no_op_not_an_error` — simulates a file already deleted
    by a prior process; the verb still returns cleanly.

## Verification

```
$ PYTHONPATH="gk-forge/tools/seedsmith" python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q
87 passed   (run twice in a row for determinism, both green)

$ sha1sum data/seed/items/socket-words/sockwords.json           # be722ee4b0...
$ cd gk-forge/tools/seedsmith && python -m seedsmith items combogen-migrate --dry-run   # exit=0
$ sha1sum data/seed/items/socket-words/sockwords.json           # be722ee4b0... -- UNCHANGED
$ git status --short gk-data/packs/fusion/data/seed/items/                            # clean -- no ledger file created either
```

`--write` was never invoked against the real corpus in this task (per the todo's own manual Verify
line, which only exercises `--dry-run`) — its behavior is proved entirely by `MigrateWriteTests`
against injected temp paths. The real retirement is SSH2.6's own job, after SSH2.4 and the owner's
SSH2.5 regen.

**Verification-boundary gap (pre-existing, named again):** `scripts/verify-change.ps1` has no owner
mapping under `gk-forge/tools/seedsmith/**` (same gap as every prior SSH2.x task). Direct `pytest` above is
the verification of record.

Population-pin (`python gk-core/scripts/guard-population-pin.py --summary`) and doc-citations
(`python scripts/audit-doc-citations.py --strict`) re-checked clean (0/0/0; 0 HIGH) after this
change.

## Acceptance criteria (from `tasks/strain-splice-host-todo.md`)

- "`--write` deletes the legacy `socket-words` partition file and writes a run-ledger record. It is
  still a verb, never a hand deletion" — **met**.
- `the_migrate_verb_writes_a_ledger_record_and_is_idempotent` — **met**, passes.

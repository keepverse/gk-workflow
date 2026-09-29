# SSH2.6 — Retire the legacy partition with the verb; the gating metric reads one kind

Unblocked by SSH2.5 landing (95 real combinations now exist to replace the 25 legacy ones). Order
executed exactly as SSH2.4's own evidence recorded it was required: `combogen-migrate --write`
(retires the file) FIRST, then remove the `socket-word` `KindCatalog.cs` row, then re-verify.

## What changed

1. `python -m seedsmith items combogen-migrate --write` — real invocation, twice (idempotency
   check): first call `fileDeletedThisRun: true`, deletes `gk-data/packs/fusion/data/seed/items/socket-words/
   sockwords.json`; second call `fileDeletedThisRun: false`, no error. Ledger written to
   `gk-data/packs/fusion/data/seed/items/socket-words/combogen-migrate.ledger.json` (new, committed).
2. `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs` — the `socket-word` `Defined(...)` row is
   removed. `combination`'s own row (added 2026-09-07) is now the only row for the kind.
3. `gk-forge/tools/seedsmith/seedsmith/metrics/linkage.py` — `COMBINATION_KINDS` narrowed from
   `("socket-word", "combination")` to `("combination",)`; `CombinationIngredients`'s docstring
   updated to match.
4. `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py` — `load_legacy()` now returns
   `()` (not a crash) when `LEGACY_FILE` does not exist: retirement's SUCCESS state is "zero legacy
   entries," and `_cmd_items_combination`'s own unconditional `legality_report(...)` call would
   otherwise crash `items generate --kind combination` entirely the moment the file is gone.
   `MIGRATION_SITES` drops the now-retired `sockwords.json` entry (6 sites remain, not 7) — a
   retired file's own absence is the bundle's success for that site, not something
   `missing_sites()` should flag as missing.
5. Tests updated for the now-real retirement (`gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`,
   `test_linkage.py`): `test_the_kind_is_renamed_not_removed` now asserts `socket-word`'s C# row is
   GONE (was: still present, deferred); the two obsolete "prove the 25 legacy entries are illegal"
   tests are replaced by `test_the_legacy_partition_is_retired_and_legality_report_reads_it_as_
   empty` (proves the file is gone and `legality_report()` reads that as the clean, zero-entry
   success state, not a crash); `test_every_migration_site_still_exists`'s count assertion follows
   the tuple down to 6; `test_linkage.py`'s two `IngredientsTests` fixtures switch from a
   `"socket-word"`-kinded corpus row (which `COMBINATION_KINDS` no longer even reads — one of the
   two was silently passing vacuously) to `"combination"`, so they keep actually exercising the gate.

## Verification

```
$ PYTHONPATH="gk-forge/tools/seedsmith" python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_linkage.py gk-forge/tools/seedsmith/tests/test_combogen.py -q
104 passed   (run twice in a row for determinism, both green)

$ python gk-core/scripts/guard-population-pin.py --summary     -> 0/0/0
$ python scripts/audit-doc-citations.py --strict        -> 0 HIGH

$ cd gk-forge/tools/seedsmith && python -m seedsmith check ../../data/seed/items --adapter items --gate --metric Registration/IngredientUnsatisfiable
no findings

$ python -m seedsmith check ../../data/seed/items --adapter items --gate --metric Coverage/EmptyPartition
[GAP] Coverage/EmptyPartition — socket-words: partition 'socket-words' is allocated but holds no entries
(+ 6 other pre-existing empty partitions, unrelated to this task)
```

`dotnet run --project gk-forge/tools/ItemSeedValidator`: the specific regression SSH2.4 identified
(`KindUnknown`/`IdOutsideNamespace` for `socket-word`/`sockword.*`) is confirmed GONE (0 matches).
Two NEW findings appeared instead, and they are the task's own accepted, documented trade-off, not
a new defect: `NamespaceUncovered`/`NamespaceUnexpandable` on `naming.v1.json`'s
`idNamespaces.socketWords` — expected, because SSH2.6's own acceptance says "`naming.v1.json` is
untouched (dropping the allocation needs a new registry version, which is ask-first)." Fixing this
would mean bumping a `registryVersion 4, frozen: true` registry, which is explicitly out of this
task's authority.

## Acceptance criteria (from `tasks/strain-splice-host-todo.md`)

- `combogen-migrate --write` has run (deterministic, no model): `socket-words` is retired with a
  ledger record, `Coverage/EmptyPartition` reports it visibly, `naming.v1.json` untouched — **met**.
- `COMBINATION_KINDS` drops `socket-word`; `ingredient_unsatisfiable_still_gates_after_the_retire`
  passes — **met**.
- the `socket-word` row is gone from `KindCatalog.cs`, `combination` is the only row, `dotnet run`
  shows no `KindUnknown`/`IdOutsideNamespace` for `socket-word`/`sockword.*` — **met**.

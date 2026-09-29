# ISG7 — retire the `socketWords` allocation: validator 3 -> 0 errors

Sub-agent task `item-seed-gen`. The last two errors. No emitted JSON was hand-edited.

## The defect (read, not guessed)

`gk-forge/tools/ItemSeedValidator/Validator.cs:68` (`NamespaceUncovered`) and `:72` (`NamespaceUnexpandable`)
fire for any `naming.v1.json` `idNamespaces` key that `KindCatalog.ByNamespace` has no kind for —
a stop-the-fleet guard against a namespace whose ids would be validated against nothing. Both
`KindCatalog.MissingNamespaces` (KindCatalog.cs:251) and `NamespaceAllocation.Build`
(NamespaceAllocation.cs:64) already skip keys beginning with `_` and `partitionCountCheck`: the
registry's own convention for "this is a record, not a live namespace" (`_readFirst`,
`_partitionIdRule`, `_commanderStandardsRemoved`).

`socketWords` was still a live-looking key while the thing it allocated no longer exists:
`data/seed/items/socket-words/sockwords.json` was retired (SSH2.6's `combogen-migrate --write`), the
`socket-word` row is gone from `KindCatalog.cs` (SSH2.6) and from `metrics/linkage.py`
(`COMBINATION_KINDS`), and `kinds.py` renamed the kind to `combination`. SSH2.6 deferred the
allocation itself as ask-first ("dropping the allocation needs a new registry version"); the
allocation, not the file, is what kept the guard red.

## What changed

- `gk-data/packs/fusion/data/seed/items/_registry/naming.v1.json` — `idNamespaces.socketWords` ->
  `idNamespaces._socketWords` (the record is kept, with a `retiredNote` naming the ruling, the file
  deletion, both kind tables and this reason); `kindPrefixes` drops `sockword`;
  `_partitionIdRule`'s fallback-group prose drops it; `registryVersion` 9 -> 10 with the reason in
  the entry itself. `minCompatibleVersion` unchanged (2): no id any file carries is affected.
  `partitionCountCheck` is left alone — it is the historical 125-partition fleet headcount,
  `KindCatalog`/`NamespaceAllocation` skip it, and socketWords was one of those 125.
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py` — its site table and
  `MIGRATION_SITES` entry still said "ask-first, untouched"; re-anchored to the retirement.
- `gk-forge/tools/seedsmith/seedsmith/report/cli.py` — the `_cmd_items_combination_write` docstring's
  frozen-registry paragraph now records that the allocation was retired rather than worked around.
- `gk-forge/tools/seedsmith/tests/test_items_adapter.py` — the naming-version assertion was a stale literal
  (expected 8 while the file had moved to 9, then 10). It now compares the loader's read against
  each registry file's OWN declared value, which is what its own name says it tests.

## Verification

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Validator errors | `dotnet run --project gk-forge/tools/ItemSeedValidator` | **PASS — 0 errors**, 3957 entries across 1013 files (3 before: 2 namespace + 1 fusion cleared in ISG6) | stdout |
| No `NamespaceUncovered`/`NamespaceUnexpandable` | same command, `--findings-json` | 0 Error findings | stdout |
| Item adapter suite | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_items_adapter.py gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | pass | stdout |
| Guards | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | pass — 21 guards, 0 red | stdout |

## Note on the two pre-existing failures this closed

`test_items_adapter.py::RegistryVersionTests::test_versions_are_read_not_a_single_hardcoded_constant`
failed on a clean HEAD (expected naming 8, file at 9). It was a stale test, not a registry defect —
fixed at the assertion, as the repo's rule directs, and it can no longer go stale this way.

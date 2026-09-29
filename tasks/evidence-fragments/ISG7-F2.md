# ISG7-F2 — the derived snapshot's retired `socket-word` residue (resolved 2026-09-21)

The row asked for the residue to be regenerated away, and named the real obstacle: the snapshot's own
`_meta` pointed at a **human** table command, so the JSON was hand-assembled and had no one-command
regeneration. Fixed by giving the source a machine-readable mode and the snapshot a real regenerator.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The source gained a machine-readable mode | `dotnet run --project gk-forge/tools/ItemSeedValidator -- --list-partitions-json gk-data/packs/fusion/data/seed/items` | JSON `{"partitionKind": {...}}`, `1069` keys, `socket-words` absent | `gk-forge/tools/ItemSeedValidator/Program.cs` |
| The human mode is unchanged | `dotnet run --project gk-forge/tools/ItemSeedValidator --no-build -- --list-partitions gk-data/packs/fusion/data/seed/items \| head -3` | same 4-column table as before (`partition stage kind idPrefix`) | same |
| The snapshot now has a real regenerator, and reports the drift first | `python gk-forge/tools/seedsmith/refresh_allocated_partitions.py --check` | `stale: committed 126, live 1069; added 944, removed 1, changed 0` → `removed: socket-words` | `gk-forge/tools/seedsmith/refresh_allocated_partitions.py` |
| Regenerated | `python gk-forge/tools/seedsmith/refresh_allocated_partitions.py --write` | `wrote …/allocated_partitions.json (1069 partitions)` | `gk-forge/tools/seedsmith/seedsmith/adapters/items/_registry_snapshot/allocated_partitions.json` |
| Regeneration is idempotent and LF-safe | `python gk-forge/tools/seedsmith/refresh_allocated_partitions.py --check`; `grep -c $'\r' <snapshot>` | `current (1069 partitions)`; `0` CR bytes | same |
| The residue is gone | `grep -c socket <snapshot>` | `0` | same |
| The consumer contract is unchanged | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_items_adapter.py gk-forge/tools/seedsmith/tests/test_sockets_gen.py -q` | `72 passed, 80 subtests passed in 0.78s` | `registries.partition_kind_map()` |
| The C# change is green | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests --nologo -v q` | `Passed!  - Failed:     0, Passed:    97, Skipped:     0, Total:    97` | — |
| Path-owned verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-forge/tools/ItemSeedValidator/Program.cs','gk-forge/tools/seedsmith/refresh_allocated_partitions.py','gk-forge/tools/seedsmith/seedsmith/adapters/items/_registry_snapshot/allocated_partitions.json','tasks/item-seedgen-todo.md','tasks/solid-enforcement-todo.md','tasks/evidence-fragments/ISG-H5.md','tasks/evidence-fragments/ISG7-F2.md','tasks/seed-corpus-ledger.jsonl') -Session seed-corpus-20260920"` | exit `1`; doc-citations `0 HIGH` on all four docs; session-boundary clean; test-substrate OK; `pytest: seedsmith` (module) `21 failed, 4259 passed, 3 skipped` = the 20 registered pre-existing + the cwd-flake `test_audit_doc_citations.py::RealTreeTests`. verify-change stops at the first failing step, so `test: guard` / `test: itemseedvalidator` / `script: gen-items-gate` did not run in that invocation | the later groups were verified directly: ItemSeedValidator `97 passed`, validator `1129 partitions / 0 errors`, items focused `72 passed`, Guard.Tests `1 failed / 579 passed` (combat-ai:1089) |
| The validator itself is unchanged | `dotnet run --project gk-forge/tools/ItemSeedValidator --no-build` | `partitions 1129 allocated prefixes`, `errors 0`, exit `0` | — |
| Finding found while verifying, diagnosed and routed (NOT fixed here) | `cd gk-forge/tools/seedsmith && PYTHONPATH=. python -m pytest tests/test_audit_doc_citations.py::RealTreeTests -q` vs the same from the repo root | subdir cwd → `1 failed` (`0 not greater than 0`); repo root → `1 passed`. Cause: `scripts/audit-doc-citations.py:232`/`:241` run `git ls-files`/`git log` without `cwd=` | routed as **SE3.7-followup** in `tasks/solid-enforcement-todo.md` |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |

## Finding routed out (diagnosed, not fixed here)
- `scripts/audit-doc-citations.py:232`/`:241` run `git ls-files`/`git log` without `cwd=`, so the audit
  is cwd-sensitive: launched from `gk-forge/tools/seedsmith` it finds zero `docs/` documents and reports clean
  over nothing, making `test_audit_doc_citations.py::RealTreeTests` fail there and pass from the repo
  root. Routed as **SE3.7-followup** in `tasks/solid-enforcement-todo.md` (owner: solid-enforcement).
  A test-side chdir fix was tried and reverted: this test file maps to the `doc-citations-guard`
  boundary, whose whole-repo `--strict` guard is red on a pre-existing 20-HIGH `docs/**` backlog, so
  editing it aborts `verify-change.ps1` at a boundary this lane's fence cannot reach (`docs/**`).

## Not proved
- **No test gates the snapshot against the live tool.** `refresh_allocated_partitions.py --check` is the
  reproducible gate, but it shells out to `dotnet` and so is a manual/CI step, not part of the Python
  suite. Wiring it into a workflow is a separate decision (it would add a dotnet build to a Python job).
- The 944 partitions the 2026-08-23 capture never held are now present; with no production consumer of
  `partition_kind_map()` this is inert, and the alternative (dropping only `socket-words`) would leave
  the file stale against its own `_meta.regenerate`.

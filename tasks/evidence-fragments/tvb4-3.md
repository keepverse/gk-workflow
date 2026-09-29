# TVB4.3 — Script projects `gen-content-validate`, `gen-corpus-dump-verify`, `gen-item-seed-validator`

| Criterion | Result |
|---|---|
| Wrappers per the S1 table | added: `gen-content-validate` (AtomImporter `--check --validate --db`), `gen-corpus-dump-verify` (CreatureCorpusDump `--verify gk-data/packs/fusion/data/seed/creatures/_dump`), `gen-item-seed-validator` (ItemSeedValidator, no args) |
| `gen-content-validate` creates and removes its own temp `--db` dir; a removal failure fails the check | `New-Item` before, `Remove-Item -Recurse -Force` (no swallow) in `finally` — matches testing-standard.md R3 |
| Parity test compares that command up to `--db` | `GeneratorCheckCiParityTests`'s matching logic now truncates any wrapper command at (and including) `--db` before the `Contains` check, since CI's `$env:RUNNER_TEMP/atom-validate-db` and the wrapper's own local scratch path are never the same two places |
| Each exits 0 on a clean tree | `gen-content-validate`: real run, exit 0, clean (442 lints evaluated, 0 failures/all Blocking:false warnings, 0 power-drift failures, `--check: clean`). `gen-corpus-dump-verify` and `gen-item-seed-validator`: see findings below — both faithfully reproduce genuine, pre-existing CI-red state |

**Two real, pre-existing, out-of-scope findings (not fixed here):**

1. `gen-corpus-dump-verify.ps1`: exit 1, `gk-data/packs/fusion/data/seed/creatures/_dump` hash mismatch (manifest `cc322647...` vs on-disk `6181dc2d...`) — the identical hash pair TVB3.9's `gen-creature-preflight` finding already documented. Same root cause, same out-of-scope owner (creature-seed).
2. `gen-item-seed-validator.ps1`: exit 1, 3581 errors across 1031 scanned files (3963 entries) — `_runs/*.ledger.json` files missing the required envelope (`entries`/`kind`/`_meta`, an unknown `done` key), and item-set entries with IDs outside their allocated wave-1 namespace, `themeKey`s not in `themes.v1.json`, and name-grammar violations. Real, CI-would-also-fail content-corpus drift, owned by whichever program most recently authored `gk-data/packs/fusion/data/seed/items/**`, not this one.

## Perf fix folded in (separate commit `d2ff5f27`, ledger `935384d3`)

Mid-task, lane-b review measured `verify-change.ps1 -PlanOnly` at 415s for two paths under 22
concurrent `dotnet.exe` hosts — the root cause of six `VerificationBoundaryWorkflowTests` timeouts
across this session. Traced to the nested `guard-verification-boundaries.py` integrity-check
subprocess doing a full repo-wide src/tests/tools completeness walk on every call, a cost that scales
with repo size (now much larger post-merge), not with the 1-2 paths being planned. Added
`-SkipCoverageWalk` to the guard (keeps every cheap structural check; skips the expensive walks;
default unchanged for CI/`-Report`/explicit local runs); `verify-change.ps1`'s own pre-check now uses
it. Measured: 415s -> 6.96s for the exact reported reproduction (`gk-forge/tools/seedsmith/pyproject.toml` +
`gk-core/data/tuning/aptitudes.v9.json`, correct plan, exit 0). Full `VerificationBoundaryWorkflowTests` +
`GeneratorCheckCiParityTests`: 56/56 passed in 3m44s, zero timeouts — a first for this session.

Scoped verify: `GeneratorCheckCiParityTests` alone (3/3, 22ms); full class run above covers TVB4.3's
own additions too (all pass, no `S2`/`S3`/`S4`/`S5` or parity regressions).

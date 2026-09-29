# TVB4.1 — `full` level + `schemaVersion` 5

| Criterion | Result |
|---|---|
| Owner with neither `project` nor `guards` derives to `full` | `Get-DerivedLevel` (`scripts/lib/VerificationBoundaries.ps1`): `if (-not $Boundary.project -and @($Boundary.guards \| Where-Object { $_ }).Count -eq 0) { return 'full' }` |
| Planner prints the CI-owned line and selects nothing | `verify-change.ps1`'s text-mode selection printer branches on `level -eq 'full'`; the check-building loop already skips a project-less, guard-less entry (line `if (-not $entry.project) { continue }`), so zero checks were ever generated for it — no change needed there |
| `full` legal only under `data/**` and `gk-core/tests/fixtures/**` | `guard-verification-boundaries.py`'s C5 rule: a project-less, guard-less boundary now fails only when at least one of its paths does NOT start with `data/` or `gk-core/tests/fixtures/` |
| `-Report` section "inputs with no local proof" | added: lists every `full`-level owner boundary (id + paths), a reading not a pinned count |
| Level vocabulary pinned at 4, reason stated | guard's closed-set check extended to `@('focused', 'module', 'seam', 'full')`; `S5_the_level_vocabulary_is_pinned_at_exactly_four` proves both the guard's literal source string and a planted 5th value's rejection |
| `schemaVersion` -> 5 (lib, registry, planted registry) | `scripts/lib/VerificationBoundaries.ps1` (`$Script:AcceptedVerificationSchemaVersion`), `gk-core/scripts/verification-boundaries.v1.json`, and all 17 planted-registry literals in `VerificationBoundaryWorkflowTests.cs` (T14's deliberate stale-`2` planted registry and the unrelated `enforcement-registry.v1.json` schema left untouched) |
| S-T2, S-T3, S-T5 green | `S2_a_full_boundary_outside_data_or_fixtures_fails_the_guard`, `S3_a_full_boundary_under_data_prints_the_ci_owned_line_and_selects_nothing`, `S5_the_level_vocabulary_is_pinned_at_exactly_four` — all new, all pass |

## Blocking interaction handled first (separate commit `c0e9f41a`)

Mid-task, the coordinator reported `VerificationBoundaryWorkflowTests.Test_fast_requires_an_explicit_scope`
failing on lane B's merged tree, blocking an 84-commit merge. Root cause: `scripts/test-fast.ps1` has
always run the static substrate gate BEFORE validating `-Project`/`-AllDefault` were supplied (verified
via `git log` — not a recent regression); on lane B's tree, an unrelated real `guard-test-substrate.py`
failure exits before the "-Project" refusal is ever reached, masking it. The test's assertion is the
correct contract (an invocation with no scope should refuse outright, independent of unrelated guard
state), so `test-fast.ps1` was fixed to validate scope first. Three doc citations whose line numbers
shifted as a result were fixed in the same commit. Verified via the one real test that exercises the
real script (`Test_fast_requires_an_explicit_scope`, now 560ms) plus a direct `guard-test-substrate.py`
run confirming this tree's own gate is clean.

## Real proof

Scoped verify: `guard-verification-boundaries.py` OK against the real (now schema-5) registry. New
tests (`S2`/`S3`/`S5`) plus `Test_fast_requires_an_explicit_scope` run together in the foreground:
4/4 passed in 2s. Full `VerificationBoundaryWorkflowTests` class run separately per the coordinator's
foreground-only, no-idle-waiting instruction; a machine-contention timeout during an earlier full-class
attempt (30-minute internal xUnit abort, 4 unrelated pre-existing tests hit the 120s external-process
timeout) was isolated and re-confirmed clean (6/7 passed on retry, the 7th — `The_real_magic_number_audit_boundary_is_guard_only`
— timed the underlying command directly at 196.6s/exit 0, confirming pure contention, not a regression).

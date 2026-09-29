# TVB4.4 — Map `gk-core/data/tuning/**` by S1 evidence; switch the root on

## Method (S1 evidence, mechanized — 108 domains)

A per-domain string-literal scan (not a bare-word grep, which is far too noisy for common English
domain names like `world`/`ai`/`match`) found the S1 evidence for every domain: `rg -P` for
`<domain>\.v\d*(\.json)?["']` across `tests/**/*.cs`, `tools/**/*.py`, `gk-core/scripts/checks/*.ps1`, then a
second pass keeping only CODE lines (excluding `//`/`///`/`#` comment lines) to reject the exact
`ContractTuningTestBootstrap.cs`-style trap S1 itself names: many domain names appear there only as
comments explaining that a literal C# object matches a real file's shipped value, never as an actual
`File.ReadAllText`. Spot-checked several multi-domain hits (`AptitudeChannelModsTests.cs`,
`PowerAndAptitudeTuningTestBootstrap.cs`, `DelveBattleTuningTestFixture.cs`) directly: all three are
real, legitimate `Read("<domain>.vN.json")` / `File.ReadAllText(...)` integration bootstraps despite
the "Bootstrap"/"Fixture" naming — a blanket name-based exclusion would have wrongly zeroed real
evidence for `battle-board`, `siege`, `reaction-lane`, `battle`, `battle-resources`, `action-timing`,
`stats`, `combat`, `status`. Two candidates (`match`, `derived-stats`) resolved ONLY to
`FusionRpg.Injector.Tests` — unregistered and not in CI (AGENTS.md) — so neither is real local/CI
evidence; both are `full`, not attributed to a project that cannot actually verify them.

## Result

| | Count |
|---|---|
| Domains total | 108 |
| Rewritten as wildcards (existing exact-name entries) | 9 boundaries covering 10 domains (`notify-tuning` covers both `notification` and `notification-catalog`) |
| New owner, real evidence (`focused` or `module`) | 79 |
| New owner, no evidence (`full`) | 19 |

Existing entries rewritten (project/verificationId/guards preserved exactly — "a rewrite never
verifies less"): `lawn-attrition-tuning`, `deployment-hierarchy-tuning`, `power-scale-tuning` (per the
spec's own named three — `power-scale-tuning` widens from `v3` only to `v*`, closing the `v1`/`v2` gap
the spec named), plus `action-base-tuning`, `craft-assurance-tuning`, `creature-yield-tuning`,
`materials-tuning`, `notify-tuning` (found already present from other lanes' merges, not named in the
spec's own starting table).

`aptitudes.v*.json` gains seam `gen-resource-ownership-aptitudes-seam` (project
`gen-resource-ownership`) alongside its existing `aptitudes-tuning` owner.

`gk-core/data/tuning/**` added to `$Script:EnforcedRoots` (`scripts/lib/VerificationBoundaries.ps1`) — the
first of the four roots switched on.

Real proof: `guard-verification-boundaries.py` full run (no `--skip-coverage-walk`) passes clean with
every one of the 108 domains' files (~150 files) resolving against the enforced root — verified via
`-Report`'s "Inputs with no local proof" section printing exactly the 19 expected `full` ids and
nothing else.

## S-T1, S-T7

- `S1_a_new_tuning_version_resolves_through_the_wildcard_with_no_registry_edit`: a planted `x.v1.json`
  + `x.v*.json` owner resolves; adding `x.v2.json` with no registry edit resolves through the same
  wildcard.
- `S7_the_real_registry_plans_a_not_yet_published_tuning_version_with_the_same_evidence`: the real
  registry plans `gk-core/data/tuning/deployment-hierarchy.v5.json` (confirmed absent from disk today, via
  `-DeletedPaths`) and gets the same `project`(`data`)/`guards`(`magic-numbers`) as the real `v1`-`v4`
  files — proving the rewrite lost nothing.

## One real regression found and fixed in the SAME commit

TVB4.2's own `S4_an_enforced_root_fails_the_guard_on_an_unmapped_file_the_same_file_outside_one_does_not`
asserted the real lib's `$Script:EnforcedRoots` literal text was exactly `= @()` (a self-check that the
"off" half of its test starts from a genuinely-empty list) — this assumption broke the moment TVB4.4
switched `gk-core/data/tuning/**` on. Fixed to regex-match `^\$Script:EnforcedRoots = .+$` and substitute the
synthetic test value, regardless of what the real list currently holds — the test's actual subject is
the ON/OFF SWITCHING MECHANISM, not the list's current membership. Re-run in isolation: passes.

## Contention note

Two pre-existing tests that invoke the guard's FULL walk directly (`RunBoundaryGuard`, not through
`verify-change.ps1`'s now-fast `-SkipCoverageWalk` path) — `Integrity_guard_passes_on_the_current_registry`,
`P6_the_real_registry_resolves_seedsmith_and_tuning` — hit the same `ExternalProcess.Run` 120s ceiling
under this session's persistent heavy machine contention (15-20 concurrent `dotnet.exe`/`powershell.exe`
at measurement time). This is the SAME pre-existing flake class present in this file since before any
TVB4.x work — both tests call the guard's full, by-design walk, which the TVB4.3 perf fix deliberately
does NOT change (only `verify-change.ps1`'s own internal pre-check opts into the fast path). Timed the
real full-walk guard call directly: 267.3s, exit 0 — the correct result, just slow, squarely inside
this session's already-established contention range (39-415s measured for other full-repo-scope calls
under this machine's load throughout TVB3.7-4.3). Not a regression from the 108-domain expansion: the
added enforced-roots walk over `gk-core/data/tuning/**` is ~150 files against 270 boundaries, a small fraction
of the pre-existing thousands-of-files src/tests/tools walk that already dominated this cost.

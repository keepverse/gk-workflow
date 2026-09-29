# TVB4.2 — Enforced-roots list (S4 mechanism)

| Criterion | Result |
|---|---|
| Code-owned list in the lib, empty at landing | `scripts/lib/VerificationBoundaries.ps1`: `$Script:EnforcedRoots = @()`, with the fixed rollout order stated in the comment (`gk-core/data/tuning/**` TVB4.4, `gk-core/tests/fixtures/**` TVB4.5, `gk-data/packs/fusion/data/generated/**` TVB4.6, `gk-data/packs/fusion/data/seed/**` TVB4.7) |
| A root on it fails the guard on an unmapped file | new walk in `guard-verification-boundaries.py`: for each pattern in `$Script:EnforcedRoots`, every file under it must resolve via `Resolve-Owner`, else `"unmapped enforced-root file: $rel"` |
| A root off it: planner still refuses, guard passes | unchanged — the planner's existing `Resolve-Owner`/`VERIFICATION BOUNDARY MISSING` refusal is untouched; the guard's new walk only iterates `$Script:EnforcedRoots`, empty today, so it is a no-op against the real registry (confirmed: `guard-verification-boundaries.py` still `OK`) |
| S-T4 green | `S4_an_enforced_root_fails_the_guard_on_an_unmapped_file_the_same_file_outside_one_does_not` — new, passes |

**One real bug found and fixed, in the test itself, before it could ever pass meaningfully:**
`RunBoundaryGuard(root)` (the helper every other guard-focused test in this file uses) invokes the
guard via a path **relative to the real repo** (`RunPowerShell`'s `WorkingDirectory` is always
`RepoRoot()`), so it always dot-sources the **real** `scripts/lib/VerificationBoundaries.ps1` via its
own `$PSScriptRoot` — a synthetic `-Root` only changes which registry/enforcement files it reads, not
which script or lib actually runs. A first draft of S-T4 wrote a modified lib copy into the planted
root's own `gk-core/scripts/lib/` and called `RunBoundaryGuard(root)`, expecting the copy to be used; it
never was — the guard silently ran with the REAL (empty) `$Script:EnforcedRoots` and reported OK,
proving nothing. Caught immediately by the test's own first run (exit 0, not the expected failure).
Manually reproduced the exact mechanism with a hand-built fixture before touching the test, confirmed
the fix (invoke the planted root's guard by its own **absolute** path, not the relative-path helper),
then re-verified the same manual fixture flips to the correct `FAILED` result. Only then rewrote the
test to use `RunPowerShell($"-File \"{guardCopyPath}\" ...")` instead of `RunBoundaryGuard(root)`.

Real proof: guard on the real (still-empty-list) registry -> `VERIFICATION BOUNDARY GUARD OK`. `S4_*`
alone -> 1/1 pass, 7s.

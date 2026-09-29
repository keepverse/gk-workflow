# TVB3.2 — Runner branches: pytest (focused/self-select/module) and script

| Criterion | Result |
|---|---|
| pytest focused (`testFiles`/self-selected file): `Push-Location <root>`, sorted relative files, `-q -p no:cacheprovider --junitxml <temp>` | implemented |
| pytest module (no selector): same command against `<tests>` | implemented |
| script: `& <script>` from repo root, exit code is the verdict | implemented |
| exit 5 is a failure (explicit message, not silently propagated) | implemented |
| `python -m pytest --version` preflight stops with the install message, never installs/skips | implemented |
| temp results dir removed in `finally` with a throwing delete | implemented (no `-ErrorAction`/catch around `Remove-Item`) |
| P1 (testFiles boundary plans exactly its expanded, sorted files) | passed |
| P2 (changed `test_*.py` under selfSelect plans only that file) | passed |
| P2b (changed `conftest.py` under selfSelect plans the module run) | passed |

**Two real bugs found by P1/P2 themselves, both fixed:**
1. `$targets = if (cond) {@(...)} else {...}` - PowerShell collapses a one-element array to a bare
   scalar when the WHOLE if/else expression isn't itself wrapped in `@(...)` (wrapping only the
   branch's own value is not enough). P1's JSON assertion caught this for the new pytest path; the
   SAME latent bug already existed in the pre-existing dotnet `targets` construction (never surfaced
   before because the execution loop already defensively re-wraps at consumption,
   `$targets = @($check.targets)`, and no prior test asserted JSON array-ness for a single-target
   case). Fixed both by wrapping the entire `if/else` in `@(...)`.
2. `testFiles = @($owner.testFiles)` turns a MISSING field ($null) into a one-element array
   containing $null (not an empty array), so the check-building loop's
   `@($entry.testFiles).Count -gt 0` was always true - every pytest entry, including plain
   `selfSelect` boundaries with no `testFiles` at all, took the testFiles branch and crashed
   (`Where-Object`/`Test-PatternMatch` bound `-Pattern $null`, coerced to an empty string, which a
   Mandatory `[string]` parameter rejects). P2's crash caught this. Fixed with
   `@($owner.testFiles | Where-Object { $_ })`, which genuinely collapses absence to zero elements.

Full `VerificationBoundaryWorkflowTests` class: 43/43. Scoped verify:
`.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,scripts/verify-change.ps1,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs -Session summoner-convergence-lane-d2-20260919`
-> 43/43 (11m11s).

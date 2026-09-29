# TVB3.5 — `knownRed` outcome + guard rules + the five entries

| Criterion | Result |
|---|---|
| Runner reads junit (pytest); only-knownRed failures pass, printing `KNOWN RED (pre-existing) <test> -> <SR-id>` | implemented (`Get-JUnitTestCases`, `Resolve-KnownRedOutcome` in the shared lib) |
| Any other failure fails the check | implemented (`UNEXPECTED FAILURE: <classname>::<name>`, `Ok=false`) |
| A `knownRed` test that passed fails with `stale knownRed entry <test>: remove it and its red row` | implemented |
| Guard: fields exactly `{project, test, debt}`; `project` exists; file exists; `debt` resolves to a `red` row | implemented in `guard-verification-boundaries.py` (parses `stub-register.md`'s own table for `red`-kind ids) |
| P9 (only knownRed failures pass, line printed) | passed |
| P10 (unregistered failure fails) | passed |
| P11 (knownRed test that passed -> stale) | passed |
| P12a/P12b (debt not a red row / file missing -> guard fails) | passed |
| Five entries for `test_actions_description_completeness.py` point at `SR-25` | added to the real registry's `knownRed` array |
| Local proof: `verify-change.ps1` on that file passes with five `KNOWN RED` lines | proved, real pytest run, twice (104.69s and 112s) |
| Local proof: `test_items_adapter.py` green | proved, real pytest run (18 passed, 1.15s) |

**pytest-only scope, stated rather than hidden:** D3's prose also mentions dotnet/TRX result-file
reading as part of the runner's general design, but every P9-P12 test, the whole Testing section's
own note ("a Guard test that shells out to pytest would fail in CI... never a real pytest execution"),
and the two Success-criteria proofs are pytest/junit-scoped only. No `knownRed` entry exists that
needs the dotnet side, and the dotnet execution path is used by hundreds of other tests across the
whole suite — extending it here without a real entry to prove it against would be unproven, risky
surface added for nothing. `Resolve-KnownRedOutcome`/`Get-JUnitTestCases` are format-agnostic in
shape (any {Classname, Name, Failed} triples), so wiring a TRX reader in later is additive, not a
redesign.

**Four real bugs found by this task's own tests and its own real local proof, all fixed:**
1. `Resolve-KnownRedOutcome`'s `[array]$KnownRedEntries`/`$TestCases` params lacked
   `[AllowEmptyCollection()]` — the same Mandatory-rejects-empty-array PowerShell quirk found once
   already for `Resolve-Owner`. P10's empty-array case (`$entries = @()`) crashed with an empty
   stdout until fixed.
2. `guard-verification-boundaries.py`'s `foreach ($entry in @($doc.knownRed))` treated a MISSING
   `knownRed` field ($null) as a one-element array holding $null (`@($null)`, not an empty array),
   so every pre-existing planted-registry test without a `knownRed` field started failing with four
   bogus "knownRed entry '' has unknown field" messages. Found by the full-class run regressing
   several unrelated tests (T13, T11, P2b, ...). Fixed with `@($doc.knownRed | Where-Object { $_ })`.
3. `verify-change.ps1`'s pytest execution branch built `$pytestArgs` via
   `$pytestArgs = if (cond) {@(...)} else {@(...)}` — the SAME if/else-as-expression array-collapse
   bug found twice already elsewhere, here silently turning a single-target pytest invocation into
   `& python -m pytest @'the/only/file.py'`, which PowerShell's array-splat operator then splats
   CHARACTER BY CHARACTER. pytest reported `file or directory not found: t`. Found only by the real
   local proof (no Guard.Tests actually invokes pytest for real, by design). Fixed by wrapping the
   whole `if/else` in `@(...)`.
4. Even after fix 3, the real proof still exited 1 despite printing all five correct `KNOWN RED`
   lines: `$LASTEXITCODE` still held pytest's own process exit code (1, since real tests failed) at
   the point the pytest branch finished, and with no explicit `exit 0` at the bottom of the script,
   powershell.exe's own final exit code defaults to that stale `$LASTEXITCODE` once the script ends
   normally. Fixed by explicitly resetting `$global:LASTEXITCODE = 0` after a successful
   `Resolve-KnownRedOutcome`, before the `continue` that skips the shared trailing exit check.

Full `VerificationBoundaryWorkflowTests` class: 49/49, clean (10.6 min). Scoped verify:
`.\scripts\verify-change.ps1 -Paths scripts/lib/VerificationBoundaries.ps1,scripts/verify-change.ps1,gk-core/scripts/guard-verification-boundaries.py,gk-core/scripts/verification-boundaries.v1.json,gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs --session summoner-convergence-lane-d2-20260919`
-> 49/49 (11m9s).

# verify-change → Python, and the guard step's testhost race — 2026-09-26

Session `verify-change-python-20260926` · branch `port/verify-change-python-20260926` · program
`test-verification-boundary`.

## What landed

| Path | What it is |
|---|---|
| `gk-core/scripts/verify-change.py` | The planner/runner, ported from `scripts/verify-change.ps1`. This is the entry point AGENTS.md now names. |
| `gk-core/scripts/lib/verification_boundaries.py` | The shared registry library, ported from `scripts/lib/VerificationBoundaries.ps1`. |
| `gk-core/tests/tools/test_verify_change.py` | 70 tests / 5 subtests: the library, the planner over a planted root, the exit codes, the refusals, and **parity with the PowerShell original**. |
| `gk-core/scripts/verification-boundaries.v1.json` | `verify-change-tool` (owner, pytest) + `verify-change-tool-guard-seam` (seam, focused `guard.verification-boundaries`), so the two new files are mapped. |
| `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs` | Two tests: the Python planner's refusal contract, and that the instruction files name the Python tool. |
| `AGENTS.md`, `CLAUDE.md`, `docs/contributing/testing-standard.md`, `docs/architecture/test-verification-boundary-ideal.md` | The entry point is now the Python tool; the ideal doc gained a dated section recording the port and the race. |

`scripts/verify-change.ps1` and `scripts/lib/VerificationBoundaries.ps1` are **NOT deleted** — see
§4, which is the honest reason.

## 1. The contract, and how it was verified to match

The plan is the contract: agents read it, and `deploy-play.py`, the Guard tests and the doc-citation
wiring all key off its shape. So the port was verified **by running both implementations over the same
inputs and failing if they disagree**, not by reading them side by side.

**`PowerShellParityTests.test_the_real_registry_plans_identically_in_both_implementations`** runs, for
one call carrying a focused source + its test + a Markdown file + a guard script + a deleted path:

* `--format text` → the two plan texts are **byte-equal** after line-ending normalisation.
* `--format json` → the two parsed plans are **equal objects**.

`PowerShellParityTests.test_the_two_libraries_answer_the_same_questions` is the cheaper, broader net: it
generates a PowerShell script that dot-sources the **real** `VerificationBoundaries.ps1` and asks it 60
pattern-match questions, 6 grammar questions, 6 specificity questions and 12 `Resolve-Owner` questions
over a planted fragment, then asserts the Python library gives identical answers. That is
implementation-against-implementation, not a transcription of one into the other.

`PowerShellParityTests.test_both_implementations_refuse_the_same_unmapped_path_the_same_way` pins the
refusal: `README.md` (a real file, no owner, no exemption) is refused by both, with the **same exit
code**, and the original message survives verbatim inside the port's named refusal.

Three real differences were found by that comparison and each was a **port bug, fixed to match**:

1. `exemptionReason` — the original sets that key on the two selection shapes that can be exempt and
   omits it on an owner/seam selection. The port emitted `null` everywhere; the plan shape says
   otherwise.
2. `doc-citations` checks — the original carries no `runner`/`targets` on them. The port was emitting
   both as `null`.
3. `--format json` was parsed and then ignored by the port's own renderer (a first-cut bug, caught
   before the parity test existed).

### Contract preserved, item by item

| Contract | Status |
|---|---|
| CLI: `--paths`, `--deleted-paths`, `--plan-only`, `--allow-unscoped`, `--format text\|json`, `--session`, `--diff-base-ref`, `--diff-head-ref`, `--root` | preserved; `--paths`/`--deleted-paths` are repeatable **and** accept several values per flag, and `--json` is an alias for `--format json`. `--timeout` is **added** (required by the Python-tool discipline). |
| Plan text, per path and per check, including the `(full)` / `(explicit exemption)` / `(sharded runner)` / `[targets]` variants and the trailing `full evidence: CI/nightly/release` | byte-equal |
| JSON plan: `paths`, `selections`, `checks`, `fullEvidenceOwner`, and each object's key set | equal |
| Exit codes: `0` plan-only/success, `1` refusal, `1` failed check, the guard's own code propagated | preserved — the port keeps `1` rather than `program_status.py`'s `2` precisely because the exit code is the contract `deploy-play.py` and the Guard tests read |
| Refusal semantics: an unmapped path, an ambiguous owner, a path outside the session fence, a missing session, a non-existent path, a traversing path, no paths, a half-specified reviewed diff, a registry the planner does not understand | preserved, each with a **name** added |
| Order: the registry-integrity pre-check runs before anything is planned, with `-SkipCoverageWalk` | preserved (`assert_registry_integrity`) |
| Registry integrity: the port **delegates** to `guard-verification-boundaries.py` rather than reimplementing it | preserved |

### Two deliberate, reported differences

1. **A stable dedupe.** The original's `Sort-Object kind, id, verificationId -Unique` is not a stable
   sort, so when two checks tie on all three keys the survivor is whichever way the array happened to
   fall. The port's sort is stable, so the survivor is the first in the (already deterministic) plan
   order. Same key, determinate result. Grouping a pytest project's checks once per project, as the
   original does, is what keeps this from mattering for a well-formed registry.
2. **`junit_test_cases` matches elements by local name.** The original's XPath `//testcase` has no
   namespace axis, so a namespace-qualified junit document matched **nothing** and the caller refused
   with "executed zero tests". Matching by local name can only ever select *more* real test cases, never
   fewer, and never turns a refusal into a pass without real test nodes behind it.

Everything else is a copy. Nothing was "improved" silently.

## 2. The race, and the command that proves the fix

**The defect.** The guard-module step ran `dotnet test`, which spawns
`tests/FusionRpg.Guard.Tests/bin/Release/net8.0/testhost.exe`. That testhost **outlived** the `dotnet test`
call, so the next build of the same project failed with `MSB3027 "Could not copy ...
FusionRpg.Guard.Tests.dll ... The file is locked by: testhost"`, or the run died with `exit -1`.
Reproduced twice on 2026-09-26.

**The fix.** `Runner._build` runs `dotnet build <project> -c Release` **once per project**, memoized on
the absolute project path, and every `dotnet test` then runs with `--no-build`. A project is therefore
never rebuilt after its own tests have run. The sharded path was already correct
(`scripts/test-sharded.ps1:139-152` builds once and runs each shard `--no-build`) and is left alone.

**The proof.** A race is a bad thing to pin by hoping it reproduces, so the *discipline* is pinned:

```
python -m pytest gk-core/tests/tools/test_verify_change.py -q -p no:cacheprovider -k DotnetDiscipline
```

`DotnetDisciplineTests.test_a_project_is_built_once_and_every_test_against_it_runs_no_build` captures the
external `dotnet` calls for two focused checks against the same project and asserts **exactly one**
`build` and **two** `test` calls, each carrying `--no-build`. Two focused checks on one test assembly is
the ordinary case — two boundaries selecting two `VerificationId`s — and is the one that used to collide.

The same fixture drives the evidence refusals that are otherwise unreachable without a real build:
`ZERO-TESTS` (a `NotExecuted`-only TRX with a zero exit), `TEST-EVIDENCE-AMBIGUOUS` (two TRX files),
`TEST-FAILED` (non-zero test exit), `BUILD-FAILED` (a failed build stops the check before any test runs),
and `TEMP-CLEANUP` (a delete that cannot complete is a named refusal and leaves the directory visible —
never a swallow, `testing-standard.md` R3).

## 3. Python-tool discipline

| Requirement | Where |
|---|---|
| Hard timeout on every external call | `_run(..., timeout=...)`; `--timeout` (default 1800 s) with a separate, smaller budget for the integrity pre-check so a slow test cannot starve a cheap precondition |
| Named refusal the moment a precondition fails | 33 names in `REFUSALS`; `Refusal(name, detail, stage=)` raises `KeyError` on an unnamed one, so a refusal cannot be added without its meaning |
| Fail closed, never "continue and report empty" | A refusal prints to **stderr** and prints **no plan** on stdout — `PlannedFixtureTests._refused` asserts `stdout == ""` |
| Machine-readable output | `--format json` / `--json` |
| Non-zero exit that names the failing stage | `VERIFY-CHANGE REFUSED [<stage>]: <NAME>: <detail>`; the tail of the captured output is inlined, so a reader that kept only the exit code still learns why |
| stdout **and** stderr captured | `subprocess.run(capture_output=True, ...)` on every call, no shell anywhere |

**A measured illustration of the last point.** One of the three real verification runs of this change
died with `exit 4294967295` (`-1`). The original would have thrown
`"... failed with exit 4294967295"` and printed **nothing** — no idea which test, no output. The port
produced:

```
VERIFY-CHANGE REFUSED [guard]: TEST-FAILED: guard focused check (gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj)
failed with exit 4294967295. Test run for ...\FusionRpg.Guard.Tests.dll (.NETCoreApp,Version=v8.0) |
A total of 1 test files matched the specified pattern.
```

which says immediately that the **build succeeded** (a `MSB3027` would have been `BUILD-FAILED`, before
any test ran) and the **test host died** — a different failure from the one being fixed, and one only
visible because the output was captured.

## 4. Why the PowerShell pair is still on disk

The brief said to retire `verify-change.ps1` and `lib/VerificationBoundaries.ps1` in the same commit,
**only if** every in-repo caller and doc reference was updated. It could not be: the callers are outside
this lane's fence, and deleting either file today breaks the guard suite and CI. A half-retired tool is
worse than a broken one, so the pair stays, and the duplication is **pinned** by the parity tests rather
than trusted.

Live callers that must move before the deletion (all outside `paths` in
`tasks/sessions/verify-change-python-20260926.json`):

| Caller | Line | What breaks |
|---|---|---|
| `gk-core/scripts/guard-verification-boundaries.py` | 21 | dot-sources `lib\VerificationBoundaries.ps1` — **the guard stops loading**, and it is a CI gate |
| `gk-fusion/scripts/deploy-play.py` | 552 | `-File scripts/verify-change.ps1` for `--verify --paths` |
| `gk-core/tests/FusionRpg.Guard.Tests/DocBoundaryTests.cs` | 22, 27, 35 | uses the `.ps1` as the **repo-root marker** and invokes it |
| `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs` | 45, 50, 112, 135, 234, 236 | repo-root marker, planner invocations, and two `Copy(...)` into planted fixture roots |
| `gk-core/tests/FusionRpg.Guard.Tests/VerificationTopologyTests.cs` | 118, 251, 253, 275 | reads and copies the planner and the lib |
| `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs` | 20, 25, 55, 79, 214, 231, 243, 253, 263, 470, 472, 504, 523, 582, 584, 601, 664, 678, 688, 703, 716, 824, 826, 846, 867, 883, 1027, 1029, 1066, 1084, 1102, 1122, 1128, 1134, 1301, 1303, 1337, 1339, 1357, 1385, 1387, 1433, 1443, 1483, 1485, 1500, 1507, 1526, 1541 | the same, plus a `Copy` of the lib into a planted root |

Comment- or message-only references (a rename for tidiness, no behaviour): `scripts/test-fast.ps1:35`,
`scripts/session-boundary-check.py:20`, `scripts/run-guards.ps1:8`, `scripts/audit-doc-citations.py:86`,
`scripts/checks/web-fusion-rpg-web.ps1:2,4`, `gk-core/scripts/enforcement-registry.v1.json:392`,
`gk-core/tools/ip-censor/ipcensor/scan.py:10`, `gk-core/tests/FusionRpg.Guard.Tests/{ClassSystemPhase9ReadinessGateTests,DocCitationAuditTests}.cs`,
`gk-core/tests/FusionRpg.Guard.Tests/TestSupport/GuardWiring.cs`, `.claude/commands/build.md:7,28`,
`.commandcode/commands/build.md:7,28`.

`gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs` is in this lane's fence and was
**not changed**: it exercises the Core-split mapping, which this change does not touch, and the
PowerShell planner it calls is still live.

**The recommended retirement, when the fence allows:** port `guard-verification-boundaries.py` to the
Python library (it is the only other consumer of the lib), point `deploy-play.py` at
`verify-change.py`, re-point the five Guard test classes' repo-root marker and invocations at the Python
tool, and then delete the PowerShell pair in one commit. The parity tests make that commit safe to
review: the moment the Python library stops agreeing with the PowerShell one, CI goes red.

## 5. Test results

Run from the worktree root, nothing else on the machine controlled:

```
python -m pytest gk-core/tests/tools -q -p no:cacheprovider
130 passed, 5 subtests passed in 123.63s (0:02:03)      # the whole gk-core/tests/tools project, incl. the pre-existing two files

python -m pytest gk-core/tests/tools/test_verify_change.py -q -p no:cacheprovider
70 passed, 5 subtests passed                             # this lane's file alone
```

Scoped verification of this change, through the port itself, at the boundary the registry selects
(`python gk-core/scripts/verify-change.py --paths <the 5 tool/registry/test paths> --session verify-change-python-20260926`):

| Run | Result | Wall |
|---|---|---|
| 1 | **exit 0** — 69 pytest tests, then `guard focused check (…Guard.Tests.csproj): 65 test(s) executed` | 601.8 s |
| 2 | **exit 1** — pytest green, then the same focused check `exit 4294967295` (§3) | 348.9 s |
| standalone re-run of that check, `dotnet test … --no-build --filter VerificationId=guard.verification-boundaries` | **exit 0** — `Failed: 0, Passed: 65, Skipped: 0, Total: 65` | 6 m 58 s |
| 3 | **exit 0** — `guard focused check (…Guard.Tests.csproj): 65 test(s) executed` | 514.5 s |

So: **three green, one test-host crash**, on four attempts of the same command. Run 2 is a crash under
machine contention, not the lock — the build succeeded and the captured output says so, and it did not
reproduce in the standalone re-run or in runs 1 and 3. It is reported rather than smoothed over.

`python gk-core/scripts/guard-verification-boundaries.py --root <worktree>` → `VERIFICATION BOUNDARY GUARD OK`
(the full walk, coverage included), which is what proves the two new files are mapped rather than
silently unmapped.

## 6. What was NOT done

* **The PowerShell pair was not deleted.** §4 has the exact caller list and why the fence forbids it.
  This is the one deliverable deliberately left undone, and it is undone *loudly*.
* **The full unfiltered suite was not run.** No `test-fast.ps1 -AllDefault`, no `-FullTestSuite`. Every
  number above comes from a scoped boundary or from `gk-core/tests/tools`.
* **`docs/architecture/validation-ssot.md` was not edited** although it is in the fence: it carries no
  `verify-change` reference. Its own doc-citation audit is clean (exit 0).
* **The pre-existing `deploy-play.ps1` dead citations were not fixed.** `AGENTS.md` (13 findings),
  `CLAUDE.md` (7) and `docs/contributing/testing-standard.md` (5) all fail
  `audit-doc-citations.py --strict` on `deploy-play.ps1` — a file that has not existed since
  `gk-fusion/scripts/deploy-play.py` replaced it, at the base commit of this branch. Every one is on a line this
  change did not touch (`git diff -- AGENTS.md CLAUDE.md docs/contributing/testing-standard.md` is 5+1+4
  lines, all about the planner), and they belong to the `ps1-ban-manager-20260926` stream, which has
  already rewritten those sections on its own branch. Fixing them here would collide with that merge for
  no gain. **Consequence:** a scoped verification that includes a `.md` path aborts at its doc-citation
  check on this branch and will be green at the merged head.
* **A finding, not a fix: `validation-ssot-doc` is over-broad.** `docs/architecture/validation-ssot.md`
  maps to `project: core` with no `verificationId`, so planning that one doc selects a module check over
  the whole 68-project Core group. A documentation input's honest proof is the doc-boundary guard plus the
  citation audit, not 68 test assemblies. Same shape, milder, for `testing-standard-doc` →
  `project: guard` (the whole Guard suite). Neither boundary is this lane's, and re-pointing another
  program's mapping is exactly the kind of change the fence exists to prevent. Routing it to the manager.

## 7. Remaining risks

1. **Two implementations of one rule coexist** (§4). The parity tests make a drift a CI failure rather
   than a silent wrong answer, but the duplication is real until the guard is ported.
2. **The focused Guard check is slow and load-sensitive.** 65 tests in ~7 minutes, mostly because each
   spawns a PowerShell or Python planner that runs a registry integrity walk. Two of those tests are new
   here. The 120 s / 300 s internal timeouts are inherited, not raised, but a class this spawn-heavy on a
   contended machine is where a host crash will show up first.
3. **`pwsh` is preferred over `powershell`.** The original shelled out to Windows PowerShell 5.1; the
   port prefers PowerShell 7 and falls back to 5.1, matching `deploy-play.py`. A machine with only 5.1
   still works; a difference in guard-script behaviour between the two hosts would show up as a parity
   failure rather than silently.
4. **The `test: guard` module check is still reachable** and runs the whole Guard assembly. It is
   reachable through `testing-standard-doc`, which is a registry issue (§6), not a port issue.
5. **Untested by unit test:** the pytest execution path (`run_pytest`) and the sharded-runner delegation
   have no fixture test, because both need a real environment. They are exercised only by the parity and
   end-to-end runs above, and the sharded path is delegated unchanged to `test-sharded.ps1`.

# TVB-F34 — the doc-citation audit cannot see intra-file drift in an append-mostly registry

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the constraint the row declared, tested | `edit scripts/audit-doc-citations.py` | **accepted.** `guard-doc-citations.ps1` is the protected guard; the Python checker it shells out to is an ordinary script. The row's "TVB-F3ep scripts-plane blocked class" was an analogy, never a measurement | this fragment |
| the two other claims of that class, tested | `edit scripts/verify-change.ps1`, `edit gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs` | both **refused**: `Blocked by the orchestrator pipeline guard: protected pipeline file`. `TVB-F3ep`/`F6ep`/`F24`/`F26`/`F32` keep their blocker | this fragment |
| D5 before / after, repo-wide | `python scripts/audit-doc-citations.py --scope docs/` and `--scope tasks/` | D5 **20 → 10**; in this program's own files **11 → 0** | `scripts/audit-doc-citations.py` |
| the shorthand sub-class the row named | the same two commands, before and after the shorthand half landed | **12 more stale citations** the full-form-only rule could not see (2 of them this program's, both now re-anchored by the rule); requiring a code token removed 2 bare-word false positives (`data` is a `projects` key and an ordinary word) | this fragment |
| the stale examples the row quoted | `grep -n '"id": "magic-number-audit"\|"id": "tuning-publish-tool"' gk-core/scripts/verification-boundaries.v1.json` | `2485` and `2509` — the row's own `:2496` / `:2520` were themselves 11 lines off | this fragment |
| this program's entry citations, re-anchored | the 20 edits in `docs/architecture/test-verification-boundary*` and `tasks/test-verification-boundary-todo.md` | 20 stale → re-anchored; 5 marked historical (the file's own `citations-historical` marker); 2 left with a stated reason (`:679` = the boundary's own brace line, `:3-15` = a file citation) | this fragment |
| the rule is reached by the real host | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` | exit **0**; summary prints `D5 registry entry moved  6  (0 HIGH)` in the default `docs/` scope | this fragment |
| `--strict` is not moved to red by it | `python scripts/audit-doc-citations.py --strict; echo $?` | exit **0** (D5 is LOW; `--strict` gates on HIGH) | this fragment |
| the audit's own tests | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py -q` | `23 passed in 24.70s` | this fragment |
| the C# audit harness | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~DocCitationAudit"` | `Passed! - Failed: 0, Passed: 5, Skipped: 0, Total: 5, Duration: 832 ms` | this fragment |
| the named guard | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | this fragment |
| the CI guard tier | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | `GUARDS OK - 25 guard(s) run, 0 red` (`doc-citations` 0, 8.60 s) | this fragment |

Residual, and it is the promotion gate: **10 stale citations in 8 files, none of them this program's** —
`empire-seed` ×3 files (`docs/architecture/empire-seed/spec-band-reader.md:228`, `spec-legion-bands.md:196`,
`spec-structure-bands.md:302`), `ip-censor` ×4 (`docs/architecture/ip-censor-map.md:82`,
`docs/research/ip-censor-spec-audit-2026-09-19.md:38`, `tasks/ip-censor-plan.md:397`/`:523`,
`tasks/ip-censor-todo.md:490`), `npc-story-events` ×1 (`tasks/npc-story-events-plan.md:688`),
`creature-seed` ×1 (`tasks/reports/creature-seed-rank-t1.md:25`). D5 becomes HIGH once they read 0.

# TVB-F35 — `audit-doc-citations.py --scope .` audited the dot-directories, and `--scope ./` audited nothing

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the defect, measured before the fix | `python scripts/audit-doc-citations.py --scope . --summary` | `664 documents, 510 resolvable citations checked` — the filter is `p.startswith(scope)`, so `.` is a **string prefix**: it matched `.agents/`, `.claude/`, `.github/`, not the repository | this fragment |
| the silent no-op | `python scripts/audit-doc-citations.py --scope ./ ; echo $?` | `0 documents, 0 resolvable citations checked`, exit **0** — a verdict for nothing | this fragment |
| why it mattered here | TVB-F34's own evidence commands | a reviewer re-running TVB-F34 with `--scope ./` would have read `0 documents, 0 D5` as "the registry citations are clean" | this fragment |
| the fix | `edit scripts/audit-doc-citations.py` | `.` and `./` normalise to the repository root; a `--strict` run matching **0** documents refuses (`matched 0 documents: nothing was audited, so nothing is proven.`) and exits **1** | this fragment |
| the fix, measured | `python scripts/audit-doc-citations.py --scope . --summary` / `--scope ./ --summary` | **664 → 3576** documents (510 → 52,060 citations); `./` **0 → 3576** | this fragment |
| a non-document scope still passes when not strict | `python scripts/audit-doc-citations.py --scope scripts/audit-doc-citations.py ; echo $?` | exit **0** (no documents to audit is legitimate there) | this fragment |
| a non-document scope under `--strict` | `python scripts/audit-doc-citations.py --strict --scope scripts/audit-doc-citations.py ; echo $?` | exit **1** with the message, where it silently passed before | this fragment |
| no caller is affected | every `--scope` call site, read | `guard-doc-citations.ps1` uses the default `docs/`; `verify-change.ps1:216` only plans this check for `.md` paths; every documented caller passes a file or a directory | this fragment |
| the guard path is unchanged | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` | exit **0**, `D5 registry entry moved  6  (0 HIGH)` in the default `docs/` scope | this fragment |
| the audit's own tests | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py -q` | `23 passed` | this fragment |
| the C# audit harness | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~DocCitationAudit"` | `Passed! - Failed: 0, Passed: 5, Skipped: 0, Total: 5` | this fragment |
| the CI guard tier | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | `GUARDS OK - 25 guard(s) run, 0 red` | this fragment |

`--scope ./ --strict` now exits **1** over the whole tree (458 HIGH D1, `tasks/**` included). That is not
a regression: the guard audits `docs/` only, and widening it is `TVB-F6ep`'s subject, not this row's.

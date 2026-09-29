# SE2.1 — `guard-tuning-immutability.py` (T1-T4) plus temp-repo tests

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| T1-T4 pass/fail cases, temp git repo, checked cleanup | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningImmutabilityGuardTests"` | **11/11 pass**: `_meta`-only edit passes/value edit fails (T1), v3-without-v2 fails/v2 passes (T2), delete fails/delete+correction-marker-naming-this-file passes/marker-naming-a-different-file still fails (T3), denylisted domain fails/real-looking domain passes (T4) | gk-core/tests/FusionRpg.Guard.Tests/TuningImmutabilityGuardTests.cs |
| `ConvertTo-Json` key-order round-trip verified, fallback used | ran under both `powershell` (5.1) and `pwsh` (7) | **live finding, fixed**: `-AsHashtable` (the spec's own code-style snippet) does not exist on Windows PowerShell 5.1 — every other Guard.Tests fixture launches `powershell.exe`, so the guard is rewritten to plain `ConvertFrom-Json` + a `ConvertTo-Canonical` walk, verified identical on both hosts | gk-core/scripts/guard-tuning-immutability.py |
| Correction marker scoped to named files, printed loudly | same test run | `T3_the_correction_marker_scoped_to_the_named_file_passes` / `..._a_different_file_does_not_exempt...`; stdout contains "correction marker used" | gk-core/scripts/guard-tuning-immutability.py |
| Denylist is a pattern list, never a domain allowlist | read `gk-core/scripts/tuning-domain-denylist.v1.json` | 4 shape patterns (`^loop.*test`, `^tmp-`, `^scratch-`, `^test-`), `_meta.note` states why | gk-core/scripts/tuning-domain-denylist.v1.json |
| Registry row `backlog` | `dotnet test --filter "FullyQualifiedName~EnforcementRegistryGuardTests\|StubRegisterTests"` | **36/36 pass**; row added `tier:ci status:backlog backlogModule:tuning-immutability`; R8 needed a new invariant row (`pr-tuning-immutable`, PRINCIPLES.md §6) — added in the same commit | gk-core/scripts/enforcement-registry.v1.json |
| Task-boundary check | `dotnet test gk-core/tests/FusionRpg.Guard.Tests` | **440/442 pass**; 2 pre-existing failures in `VerificationBoundaryWorkflowTests` (TVB-domain `test-fast.ps1` CLI output, last touched by `TVB0.1`/`SE0.7`, untouched here, moved to a parallel TVB lane per the manager's scope change) | — |

**Live finding, out of scope, not fixed here:** `[CmdletBinding()]` makes every `$PSScriptRoot`-based
parameter default resolve empty on this host's Windows PowerShell — reproduced on the ALREADY-SHIPPED
`guard-generated-seed.py` too (masked because its own callers always pass `-Root`/`-BaseRef`
explicitly). This guard is written with no `[CmdletBinding()]`, matching `guard-class-system.py`'s
already-correct shape; `guard-generated-seed.py`'s own copy is untouched (not this task's file).

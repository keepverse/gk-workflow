# TVB-F33 — `guard.unique-allocation-reader` now runs for the files its allowlist polices

**What closed it.** The row's own shape (a) — "let a seam carry a `verificationId`" — is already
available: `verify-change.ps1:112` filters the `VERIFICATION BOUNDARY AMBIGUOUS` check to
`kind -eq 'owner'`, its seam loop (`:119-121`) builds a focused `test` check from `$entry.verificationId`,
and `guard-verification-boundaries.py:151-161` accepts a `verificationId` on any boundary kind. The old
blocker ("the only additive mechanism is whole-project") rested on a **reading** — 0 of 30 seams happened
to carry one — not on a rule. Landed: seam `unique-allocation-reader-seam`
(`gk-core/scripts/verification-boundaries.v1.json:6080-6090`, `kind: seam`, `paths: ["src/**"]`, `project: guard`,
`verificationId: guard.unique-allocation-reader`, `level: seam`), appended last — a pure append, so no
existing registry line shifts and no citation into it moves.

`src/**` is the scope the test itself polices (`UniqueAllocationReaderGuardTests.cs:31` enumerates every
`*.cs` under `src/`, not one file), so a narrower seam would close the instance and leave the class
("local green, CI red") open.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the guard runs for the two allowlisted Data files | `pwsh -NoProfile -File scripts/verify-change.ps1 -PlanOnly -AllowUnscoped -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AllocationRespec.cs` | both plan `-> unique-allocation-reader-seam (seam)` beside `data-fallback (module)`; checks include `test: guard guard.unique-allocation-reader` | — |
| it also reaches the third allowlisted file and a plain Core path | same, `-Paths gk-core/src/FusionRpg.Server/DerivedAuditActor.cs src/FusionRpg.Core/Items/ItemGrant.cs` | both plan the seam beside `server-derived-audit` / `core-area-items`; `test: guard guard.unique-allocation-reader` present | — |
| the trait selects tests and they pass | `dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release --filter "VerificationId=guard.unique-allocation-reader"` | `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2` in `173 ms`; whole command `17.7 s` wall warm | — |
| registry still validates | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | — |
| docs unchanged by the insert | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | 0 HIGH (D2 7, D3 56, both all-LOW) | — |
| a `tasks/**` docs edit at this head | `pwsh -NoProfile -File scripts/verify-change.ps1 -Session tvb58 -Paths tasks/test-verification-boundary-todo.md tasks/evidence-fragments/tvb-f33-seam.md` | plans `test: guard` (the whole project) and exits **1**: `Failed! - Failed: 1, Passed: 672, Skipped: 0, Total: 673` (9m16s) — the one red pre-existing (`PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary`, `RpgStore.Fusion.cs:305`'s tenth code), filed in `tasks/reports/findings-2-head-guard-reds.md`; recorded on TVB-F32 | — |

**Residual, recorded rather than implied:** the seam adds `17.7 s` to every `src/**` edit repo-wide — the
cost class `TVB-F32` is about. Taken deliberately: the alternative scopes either leave the class open or
(shape (c)) trade away the `Data.Tests` run. Widening or narrowing it is one line in the registry.

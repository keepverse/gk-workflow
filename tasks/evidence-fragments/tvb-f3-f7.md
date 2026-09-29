# TVB-F3 closed (the index landed) + TVB-F7ep's in-fence half

## TVB-F3 — the timeouts were the coverage walk, and the index that fixes them is in the unprotected file

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the fix | read `scripts/lib/VerificationBoundaries.ps1` | `New-OwnerPatternIndex` (first-path-segment bucket) + a reference-identity memo `Get-OwnerPatternIndex`, consumed by `Resolve-Owner` — the resolution rule is unchanged, only the candidate set is narrowed | `scripts/lib/VerificationBoundaries.ps1` |
| guard, standalone | `python gk-core/scripts/guard-verification-boundaries.py` | **14.1 s** (was **50 s** on 2026-09-20) | — |
| guard, `-Report` | `... -Report` | **16.0 s** | — |
| the two cases that timed out under load | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~Integrity_guard_passes_on_the_current_registry|FullyQualifiedName~P6_the_real_registry_resolves_seedsmith_and_tuning"` | `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2, Duration: 1 m 17 s` — ~38 s each through `RunPowerShell`, under the 120 s helper budget that 15 concurrent hosts used to exceed | — |
| the whole filter | `... --filter "FullyQualifiedName~VerificationBoundary\|FullyQualifiedName~CoreTestProjectPolicy"` | `Passed! - Failed: 0, Passed: 63, Skipped: 0, Total: 63, Duration: 5 m 32 s` | — |

No timeout was raised and no `-SkipCoverageWalk` was passed — the walk still runs. The row's blocker note
said the fix needed a ruling because both `guard-verification-boundaries.py` and `verify-change.ps1` are
pipeline-protected; the index lives in the **lib** those two share, so no protected file was touched.

## TVB-F7ep — the `gk-core/src/FusionRpg.Core/**` half, re-pointed by reading the ADR rows

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the four citations | `git ls-files 'gk-core/src/FusionRpg.Core/*' \| xargs grep -oE 'decisions\.md:1[0-9][0-9]'` | `DelveMemberState.cs:9` `:115` → **:134**; `RoomTypeCatalog.cs:9`, `LaneGate.cs:5`, `WorldValidation.cs:52` `:114` → **:133** — four occurrences, nothing else | — |
| the rows they now name | `sed -n '133p;134p' docs/architecture/decisions.md` | `:133` = "World store — delve worlds (2026-09-05)" (names the `RoomTypeCatalog`/`DoorTypeCatalog` pair and `WorldValidation.Validate`'s delve profile); `:134` = "Status SSOT + Resource model — nerve (2026-09-05)" | — |
| the affected groups' own members | `scripts/test-fast.ps1 -Project @('gk-core/tests/FusionRpg.Core.Tests/…','gk-core/tests/FusionRpg.Core.Items.Tests/…')` | `Passed! - Failed: 0, Passed: 9600` (5 m 18 s) and `Passed! - Failed: 0, Passed: 1468` (45 s), `EXIT=0` | — |
| the plan K1 now produces | `verify-change.ps1 -Paths @(the four) -PlanOnly` | `core-area-delve (module)` → 3 projects, `core-area-world (module)` → 5 projects (the whole `core` group before K1) | — |

**Still open, and out of this lane's fence:** 47 occurrences under `docs/**`, 3 under `tasks/**`, 1 under
`gk-core/src/FusionRpg.Data/**` (`RpgStore.World.cs:200` — the same `:114` → `:133` re-point) and 1 under `web/**`
(`stages/delve/graph/FightInPlace.tsx:9`). The docs half also needs `docs/architecture/decisions.md` itself,
which the row says needs the whole band re-derived.

The doc-citation audit does not scan `.cs` files (`audit-doc-citations.py --scope <a .cs file>` reads
"0 documents"), so these comment re-points cannot redden the CI-gating guard either way — which is also why
the drift survived: nothing checks them automatically.

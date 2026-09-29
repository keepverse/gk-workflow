# TVB-F27 — the `Vfx` split's consumer-table row: an audit filter that passed while running nothing

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the defect, reproduced | `dotnet test gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj --filter "FullyQualifiedName~StatusVfxIdentity\|FullyQualifiedName~VfxAuraMath" --no-restore` | `No test matches the given testcase filter … FusionRpg.Core.Tests.dll`, **EXIT=0** — the script's only check was that exit code, so it printed `Static tests: PASS` having run nothing | this fragment |
| where those tests live now | `grep -rl "StatusVfxIdentity\|VfxAuraMath" tests/ --include=*.cs` | **4** files, all under `gk-core/tests/FusionRpg.Core.Vfx.Tests/Vfx/` (`StatusVfxIdentityAuditTests.cs`, `StatusVfxIdentityCollisionTests.cs`, `UnitFrameTests.cs`, `VfxAuraMathTests.cs`); none left in the residual | this fragment |
| the fix, through the real script | `pwsh -NoProfile -File scripts/audit-status-vfx-identity.ps1 -OutJson <temp>\\tvb60-status-audit.json` | `Running static identity + aura math tests (FusionRpg.Core.Vfx.Tests)...` / `Static tests: PASS (63 selected)` / exit 0; the report went to a temp path so the repo stayed clean | this fragment |
| the same filter on the fixed project | `dotnet test gk-core/tests/FusionRpg.Core.Vfx.Tests/FusionRpg.Core.Vfx.Tests.csproj --filter "FullyQualifiedName~StatusVfxIdentity\|FullyQualifiedName~VfxAuraMath" --no-restore` | `Passed! - Failed: 0, Passed: 63, Skipped: 0, Total: 63` — was **0 selected** | this fragment |
| the new zero-selection refusal fires | the parse the script now uses, applied to the OLD selection | `parsed selected=0 exit=0` → `THROW (zero selected is a failure, never a pass)` | this fragment |
| the rest of the consumer table | see the todo row | `ci.yml` 68 pairs + BalanceGuard pair `FusionRpg.Core.Balance.Tests` (the only project carrying the trait, 11 occurrences in `DominanceGuardTests.cs`); `release.yml` 68; `test-fast.ps1` 68; the registry's `core` group 68 members, bijective with 67 manifest projects + residual; `FusionRpg.slnx` 68; `coverage.ps1:55`/`mutate.ps1:91` resolve from the manifest; `BattleGoldenTests.cs` is still in the residual, so `regen-class-system-baselines.ps1:173` and `verify-golden-attribution.py:31` are still correct | this fragment |
| the script had **no boundary at all** | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -PlanOnly -Paths @('scripts/audit-status-vfx-identity.ps1') -Session tvb58"` | before the registry edit: `VERIFICATION BOUNDARY MISSING: scripts/audit-status-vfx-identity.ps1`; after adding the path to the `core-vfx` row: `scripts/audit-status-vfx-identity.ps1 -> core-vfx (module)` / `test: core-vfx` | this fragment |
| the registry stays valid (gates the commit) | `python -c json.load(gk-core/scripts/verification-boundaries.v1.json)` then `python gk-core/scripts/guard-verification-boundaries.py` | parsed OK, `schemaVersion 5`, **137** projects / **463** boundaries; `VERIFICATION BOUNDARY GUARD OK` | this fragment |
| the scoped run | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('scripts/audit-status-vfx-identity.ps1','gk-core/scripts/verification-boundaries.v1.json','tasks/test-verification-boundary-todo.md','tasks/evidence-fragments/tvb-f27.md') -Session tvb58"` | `Failed: 2, Passed: 667, Total: 669` (4 m 44 s) — the two reds are the pre-existing routed ones (`PlantSideStatusGuardTests.BattleEffects_is_byte_identical…`, `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes…`), the same reading `tvb5-8-k-close.md` records | this fragment |

The spec's consumer table (`spec-core-split-wiring.md:53`) names this script and says it must run "the
project holding the status/VFX identity tests". The `Vfx` increment landed without it, so the static half
of the harness has been a no-op for as long as that split has existed — invisible because a filter that
matches no test exits 0. The fix mirrors the shape `guard-narrative.py:130` already uses: parse the
printed `Total:` and treat zero as a failure. The script also had **no verification boundary at all** —
`verify-change.ps1` threw `VERIFICATION BOUNDARY MISSING: scripts/audit-status-vfx-identity.ps1` — so a
change to it could not be scoped by the repo's own tool; that is half the fix, not a footnote. It now
resolves through the existing `core-vfx` owner row (`scripts/audit-status-vfx-identity.ps1 -> core-vfx
(module)`, `test: core-vfx`).

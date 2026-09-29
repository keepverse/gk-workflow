# Resume 29 — SSH7.1 revision-literal guard with SSH8.4 companion

## Task

Close the remaining deterministic reader/guard slice for `strain-splice-host` at product base
`6d77888cca860805e5a11e617e201847e01c16b7`. This lane is spawned from prepared boundary commit
`29df9959829447faba9fbf00483fe165d8555b16`, whose only addition is the manager-owned session record;
the product diff must remain relative to `6d77888cc`.

- **Primary:** SSH7.1, `every_reader_loads_the_current_strain_splice_revision`.
- **Named companion:** SSH8.4, `every_reader_loads_the_current_materials_revision`.

## Lane setup

The prepared base contains this lane's session record at
`tasks/sessions/resume-29-strain-splice-reader-guard-20260925.json`. Run the worktree-local boundary
check before editing. The manager owns the protected guard path for this exact slice; do not ask for
a second owner or broaden the fence. If the record is absent, stop as an infrastructure failure.

This is a manager-owned verification-boundary change. The manager explicitly owns the protected
`gk-core/tests/FusionRpg.Guard.Tests/**` path for this bounded slice; the worker must not route around a
refusal, add an allowlist, or widen into product/tuning/generated data.

## Read first

Read these current contracts before editing:

- `docs/DESIGN-GATE.md` §1 rows for tunables, SOLID, and design-gate procedure;
- `docs/architecture/strain-splice-host-map.md` §§2, 4, 5 and the current module status;
- `docs/architecture/strain-splice-host/spec-tier-ladder.md` §1 and its testing/boundaries;
- `docs/architecture/strain-splice-host/spec-socket-pricing.md` §5 and its testing/boundaries;
- `docs/architecture/tunables-ssot.md` §§1–4 and 7.2;
- `docs/architecture/test-verification-boundary-map.md` §§2–3 and the current guard owner;
- `tasks/strain-splice-host-plan.md` and `tasks/strain-splice-host-todo.md` rows SSH7.1/SSH8.4;
- `tasks/reports/resume-25-strain-splice-triage-20260925.md` and its integration record.

Verify the current literals against code. A prose/history literal is not a reader; a shipped test
path join is. Do not trust stale Core-test project names or unchecked-box prose.

## Exact fence

Only these implementation/test paths may change:

1. `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`
2. `gk-forge/tools/seedsmith/tests/test_combogen.py`
3. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs`
4. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs`
5. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs`
6. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs`
7. `gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs`
8. `gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs`
9. `gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs`
10. `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs`
11. `gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs`
12. `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs`
13. `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`
14. `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs`

The only additional writable path is the lane report:
`tasks/reports/resume-29-strain-splice-reader-guard-20260925.md`.

Do **not** edit `SocketTuningFiles.cs`, production readers, Server/Core runtime code, the todo,
plan, specs, `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, CI, or the verification-boundary
registry. Do not run a model, generator, publish, re-emit, live game, server, or browser.

## Required contract

### C# guard

Extend `TuningRevisionLiteralGuardTests` to scan both:

- `strain-splice.v[0-9]+\.json`
- `materials.v[0-9]+\.json`

Keep the existing sockets rule intact. The only C# filename-constant file allowed to name these
literals is `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs`. Comment/doc/prose lines are not
readers. Do not add a temporary reader allowlist, and do not add a population-count assertion. Keep
the existing stale-allowlist check meaningful. Add/adjust source-text assertions for the canonical
`SocketTuningFiles.StrainSplice` and `SocketTuningFiles.Materials` readers where the current guard
contract requires them.

### Python guard

Extend `TuningRevisionLiteralTests` in `gk-forge/tools/seedsmith/tests/test_combogen.py` so the only Python
path joins for these domains are the canonical `STRAIN_SPLICE_PATH` in
`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py` and `MATERIALS_TUNING_PATH` in
`gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/brief.py`. Scan actual path-join syntax, not
prose. Do not turn comments, exception text, or documentation into an allowlist.

### C# test-reader conversion

Replace shipped-file revision literals in the listed current test readers with
`SocketTuningFiles.StrainSplice` or `SocketTuningFiles.Materials`, preserving each test's behavior and
comments. `MaterialRecipeCatalog.cs` exception prose is not a reader and must not be changed. If a
new reader is discovered outside the fence, stop and report the ownership/fence question instead of
adding an exception.

## TDD and verification

Use a real RED → GREEN cycle:

1. Add the new guard assertions and reader conversions/tests first; run the smallest relevant tests
   and record the expected red result.
2. Make the minimal implementation/test-reader changes; rerun the focused tests.
3. Run every command below from the worker worktree and record exact output.

```powershell
python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q
```

```powershell
dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --filter "FullyQualifiedName~TuningRevisionLiteral"
```

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --filter "FullyQualifiedName~ComboContainerBuild|FullyQualifiedName~CombinationCorpus|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing|FullyQualifiedName~MaterialCorpus|FullyQualifiedName~ItemUpgradeCostContract"
```

```powershell
dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --filter "FullyQualifiedName~CraftWearInstanceOp|FullyQualifiedName~MaterialSpend"
```

```powershell
dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --filter "FullyQualifiedName~ComboPricingBoot|FullyQualifiedName~CombinationImport|FullyQualifiedName~ItemWorkbench|FullyQualifiedName~ItemUpgradeEndpoint"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs','gk-forge/tools/seedsmith/tests/test_combogen.py','gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs','gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs','gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs','gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs','gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs','gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs','gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs','gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs','gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs','gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs','gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs','gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs') -Session resume-29-strain-splice-reader-guard-20260925
```

```powershell
python scripts/audit-doc-citations.py --scope tasks/reports/resume-29-strain-splice-reader-guard-20260925.md --strict
```

```powershell
git diff --check
```

## Required report

Include base/final SHAs, every changed file, RED and GREEN commands with outputs/counts, the literal
reader inventory before/after, the exact verification-boundary result, and open questions. State
that no tuning revision, H7 publish, SSH7.7, SSH4.9, generator, model, generated corpus, or live
operation was started. End with the runner `<<<REPORT {...} REPORT>>>` block. Do not merge or push.

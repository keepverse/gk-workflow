# Resume 28b — EPL1.1 exact-SHA review and bounded repair

**Date:** 2026-09-25
**Program:** `effect-pipeline` / EPL1.1
**Worker base:** `9b27ff0ebd09761a2df59779c96fbc341d84a65e`
**Reviewed implementation SHA:** `8334a1d617cdf68edd33929262315f8502c7ea91`
**Review worktree:** `.claude/worktrees/review-resume-28b-effect-pipeline-epl1-1-20260925`

## Disposition

The worker session `resume-28b-effect-pipeline-epl1-1-20260925` ended `failed` after focused
implementation tests passed. Its broad path-owned verifier was stopped by a Bitdefender deny-write
lock on an unrelated `FusionRpg.Core.EffectGrantSessionTests` output. The worker produced no report
and no commit; its four dirty implementation files were copied into this manager review boundary.

The implementation is **reviewed and ready for exact-SHA acceptance**. The review found and fixed
one real fail-closed defect in the worker draft: `AffixPowerClassIds.OrdinalOf` documented `-1` for
an undeclared enum value but returned the raw cast. The manager also made the registry parser reject
non-object roots, unsupported schema versions, invalid `appendOnly`/`registryVersion` values, and
numeric fields other than the declared structural metadata. The public id list is now read-only.

No generated data, tuning, classifier, model, channel policy, runtime consumer, Server/Data path, or
live surface was changed.

## Exact reviewed paths

The implementation commit contains only these four product/test paths plus this review session
record:

1. `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` — new authored registry under `_registry`, not
   generated output.
2. `gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs` — new C# enum, closed parser, and registry
   mirror reader.
3. `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs` — focused C# contract tests.
4. `gk-forge/tools/seedsmith/tests/test_power_class_registry.py` — focused Python registry/mirror tests.
5. `tasks/sessions/resume-28b-effect-pipeline-epl1-1-review-20260925.json` — manager review boundary.

This report is an evidence-only descendant and is not part of the reviewed implementation SHA.

## Contract checks

- Closed ids and ordinals are exactly `filler=0`, `notable=1`, `potent=2`, `defining=3`, and
  `pinnacle=4`.
- JSON and C# ids/ordinals are checked against each other in both test languages.
- Unknown, differently-cased, padded, and out-of-range values fail closed; no default-to-`filler`
  path exists.
- `OrdinalOf` returns `-1` for an undeclared enum value.
- Registry schema (`schemaVersion=1`, positive `registryVersion`, `appendOnly=true`) is checked.
- Recursive numeric-field auditing permits only `schemaVersion`, `registryVersion`, and `ordinal`;
  a smuggled `weight`/rate/probability/magnitude is rejected by the C# reader and the Python audit.
- Power-class ids are checked against the current rarity ladder; no collision was found.
- No family, affix, or corpus population count is asserted. Any such number in validator output is
  a reading, not an EPL1.1 constant.

## Independent verification

All commands below ran in the manager review worktree unless marked **clean checkout**.

```powershell
python -m pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q
# 12 passed in 0.07s (review worktree)
# 12 passed in 0.09s (detached clean checkout)

dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --nologo --filter "FullyQualifiedName~AffixPowerClass"
# Passed: 10, Failed: 0 (review worktree)
# Passed: 10, Failed: 0 (detached clean checkout)

python gk-core/scripts/guard-generated-seed.py
# [guard-generated-seed] no changes vs working tree (clean checkout)

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/checks/gen-item-seed-validator.ps1
# validator completed with errors 0; its existing warning/report-only corpus output was not
# treated as an EPL1.1 population assertion

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/checks/gen-items-gate.ps1
# PASS — existing item gate completed; report-only warnings/notes remained non-gating
```

The clean checkout was created detached at the exact reviewed SHA, and its initial
`git status --porcelain=v1 --untracked-files=all` was empty. Build outputs created by the test
commands are ignored; no source or evidence path changed.

### Path-owned verifier

The exact scoped plan was produced with every concrete EPL1.1 path and the review session id:

```powershell
$paths = @(
  'gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json',
  'gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs',
  'gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs',
  'gk-forge/tools/seedsmith/tests/test_power_class_registry.py'
)
& .\scripts\verify-change.ps1 -Paths $paths -Session resume-28b-effect-pipeline-epl1-1-review-20260925 -PlanOnly
```

The plan selected the registry corpus/validator seams, the Core effects owners, the Core atoms
project, the focused Seedsmith test, the generated-seed guard, and the item validator/gate. The full
execution was attempted with the same path list. It passed the generated-seed guard, the focused
Python tests, the item validator, the item gate, and the first Core owner projects, then stopped at
an external output-file denial:

```text
error MSB3021: Unable to copy file
  tests/FusionRpg.Core.CombatHitEmitPolicyTests.Tests/obj/Release/net8.0/FusionRpg.Core.CombatHitEmitPolicyTests.Tests.dll
Access to the path ... is denied.
Exception: core-area-effects-owners module check failed with exit 1
```

This is the same class of Bitdefender/Windows output lock recorded in the worker failure, not an
EPL1.1 assertion failure. The independently run exact-SHA clean focused checks above are green. The
broad verifier result remains **not GREEN** and must not be represented as such.

## Review repair details

The worker draft's `OrdinalOf` implementation was:

```csharp
public static int OrdinalOf(AffixPowerClass value) => (int)value;
```

The reviewed implementation is:

```csharp
public static int OrdinalOf(AffixPowerClass value) => IsDefined(value) ? (int)value : -1;
```

The parser now rejects a non-object root before calling `TryGetProperty`, validates the registry
schema and append-only marker, and walks the document to reject numeric leaves outside the three
structural keys. Focused C# tests cover each refusal, including a smuggled numeric `weight` and a
non-object root. The Python test also checks the schema flags. These are contract checks, not
population pins.

## Non-actions and remaining gates

- No EPL1.2 classifier or `MAX` derivation was started.
- No EPL1.3 model call, family classification, coverage claim, or BCU2.12 work was started.
- No EPL2.1 channel vocabulary/policy work was started; its existing `AffixChannels` ownership
  collision remains open.
- No `gk-core/data/tuning/**` file was created or edited; no generated seed/atom output was regenerated.
- No Server/Data/runtime consumer was wired; EPL1.1 intentionally has no runtime consumer yet.
- No push, merge, browser, live-game, or release claim is made by this report.

The next manager step is to create the schema-v2 exact-SHA acceptance artifact for
`8334a1d617cdf68edd33929262315f8502c7ea91`, then merge only after the dirty integration checkout is
resolved and the current-head gate can run.

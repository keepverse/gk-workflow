# Resume 28 — EPL1.1 closed power-class registry and C# mirror

## Task

Implement **EPL1.1 — The closed enum + registry + C# mirror** for `effect-pipeline` at product base
`6d77888cca860805e5a11e617e201847e01c16b7`. This replacement is spawned from prepared boundary commit
`9b27ff0ebd09761a2df59779c96fbc341d84a65e`, whose only addition is the lane session record; the
product diff must remain relative to `6d77888cc`.

This row defines the closed structural vocabulary and its checked-in C# mirror only. It is not the
later classifier, model-call, tuning, or channel-weight work.

## Lane setup

This is a corrected replacement for the failed `resume-28` lane. The prepared base commit contains
this lane's manager-owned session record at
`tasks/sessions/resume-28b-effect-pipeline-epl1-1-20260925.json`, so the worktree-local boundary
check can run without reading outside the worktree. Run that check before editing. If the record is
still absent, stop and report an infrastructure failure; do not ask the manager to resolve a setup
defect from inside the lane.

## Read first

Read the binding design-gate row and these current contracts before editing:

- `docs/DESIGN-GATE.md` §1 row for affix/container authoring;
- `docs/architecture/effect-pipeline-map.md` modules 11–12 and build order;
- `docs/architecture/effect-pipeline/spec-affix-power-class.md` (especially the enum, identity-only
  boundary, project structure, testing strategy, and success criteria);
- `docs/architecture/effect-atom/spec-container-schema.md` for the vocabulary/reader boundary;
- `docs/architecture/validation-ssot.md` for closed-enum and population-reading rules;
- `tasks/effect-pipeline-plan.md` and `tasks/effect-pipeline-todo.md` rows EPL1.1 and CEP1.

Verify the current paths before creating anything. Do not trust a stale unchecked box or an old
project split.

## Exact fence

Only these four implementation/test paths may change:

1. `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` (**new** authored registry; not generated output)
2. `gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs` (**new** C# mirror)
3. `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs` (**new** focused tests)
4. `gk-forge/tools/seedsmith/tests/test_power_class_registry.py` (**new** focused registry tests)

You may also write the lane report at
`tasks/reports/resume-28b-effect-pipeline-epl1-1-20260925.md`.

Do not edit `tasks/effect-pipeline-todo.md`, the plan, specs, `gk-core/data/tuning/**`, any generated atom or
affix output, `gk-core/src/FusionRpg.Data/**`, Server/Core runtime code outside the new mirror, channel
policy, or any other test project. Do not run a model, classifier, `FamilyExpandGen`, generator
re-emit, or live/browser/server process.

## Contract to implement

- Exactly five append-only classes with consecutive ordinals `0..4`:
  `filler`, `notable`, `potent`, `defining`, `pinnacle`.
- The C# mirror and JSON registry must have identical ids and ordinals.
- Parsing/serialization must be closed: an unknown id fails explicitly; no default-to-`filler` path.
- The registry is identity/structure only. It must not introduce a numeric power class, weight,
  rate, probability, magnitude, or balance target. Numeric ordinals are structural metadata, not
  magnitudes.
- Power-class ids must not collide with any rarity-rung id; test this against the current rarity
  vocabulary.
- Do not pin a family/corpus population count. The later EPL1.3 model run owns real family
  classification and coverage; this row must not fake or pre-populate those results.
- Preserve the one-mirror rule: the JSON registry and `AffixPowerClass` are the only vocabulary
  homes in this slice. Do not create a second enum, classifier, channel vocabulary, or allowlist.

## TDD and acceptance

Use a real RED → GREEN cycle:

1. Add the focused Python/C# tests first and run them; record the expected failing output because
   the production registry/mirror do not yet exist.
2. Implement the smallest registry and C# mirror that make the closed-vocabulary, ordinal,
   round-trip, unknown-id, and rarity-collision contracts pass.
3. Run the focused tests again, then run the path-owned verifier with every concrete path and this
   session id.
4. Run the report citation/whitespace checks and inspect the final diff for out-of-scope files.

The registry test must validate the file's schema and the C# mirror contract without asserting a
current family count. A future classification run may report coverage as a reading; it is not this
row's constant.

## Required report

The report must include:

- base SHA and final commit SHA;
- exact changed files and confirmation that no generated data/tuning/runtime path changed;
- RED command/output and GREEN commands/output with counts;
- the exact closed ids/ordinals and rarity-collision result;
- `verify-change.ps1` command/result and `git diff --check`;
- open issues and explicit statement that EPL1.3 model calls, EPL2.1 channel SSOT, and live proof
  were not started.

## Verification

`python -m pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q`

`dotnet test gk-core/tests/FusionRpg.Core.Atoms.Tests/FusionRpg.Core.Atoms.Tests.csproj --nologo --filter "FullyQualifiedName~AffixPowerClass"`

`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json','gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs','gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs','gk-forge/tools/seedsmith/tests/test_power_class_registry.py') -Session resume-28b-effect-pipeline-epl1-1-20260925`

`python scripts/audit-doc-citations.py --scope tasks/reports/resume-28b-effect-pipeline-epl1-1-20260925.md --strict`

`git diff --check`

End with the runner `<<<REPORT {...} REPORT>>>` block. Do not merge or push.

# P1 05 recovery — repair FamilyExpand manifest closure

The manager review of the vocabulary draft found a real regression. `FamilyExpandGen --check` and its focused tests were green, but the path-owned Core selection failed 14 tests because `_family-expand.manifest.json` exposes refusal rows with `kind: ""`. `TraitMigrationParityTests`, `EventDeckGoldensTests`, and `EventSeedContentTests` reject that as `UnknownKind`. Do not hand-edit the manifest or weaken those tests.

## Allowed paths

- `gk-forge/tools/FamilyExpandGen/**`
- `gk-forge/tools/PassiveTreeRosterGen/**`
- `gk-data/packs/fusion/data/seed/passive-tree/vocabulary.json`
- `gk-data/packs/fusion/data/seed/atoms/generated/_family-expand.manifest.json` (generated output only)
- `gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests/**`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/TreeAtomSourceParityTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/Adoption/PassiveTreeMechanismRoundRecomposeTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/EquipAtomSourceIdTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Match/UniqueEquipmentAtomMappingTests.cs`
- `tasks/reports/resume-05-vocabulary-recovery-20260925.md`

No Core production, Delve, CI, unrelated fixture, commit, push, or merge.

## Required repair

1. Inspect the existing manifest reader/schema and the generator's refusal representation. Preserve every refusal and provenance record, but make the emitted manifest consumable by the existing closed-kind readers. The fix belongs in the generator/schema path; regenerate the manifest through `FamilyExpandGen` afterward.
2. Keep `FamilyExpandGen --check` and `PassiveTreeRosterGen --atom-vocab-check` green, and keep generated provenance/hash closure intact.
3. Run restored focused tests for the generator suite, `TraitMigrationParityTests`, `EventDeckGoldensTests`, `EventSeedContentTests`, and the four directly affected Core atom/passive-tree tests. Do not use a silent zero-test `--no-restore` command.
4. Run `guard-generated-seed.py`, JSON/diff checks, and path-owned verification for the concrete executable paths. If the broad Core selection is too costly, record the exact selected failure and the focused replacement; never call it green without evidence.
5. Write a disk-backed report with exact commands/results, the manifest schema cause, regenerated paths, open CI/fixture/Core handoffs, and next steps. Leave the tree dirty for manager review.

Use only OpenCode CLI `opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent, and no external-directory reads.

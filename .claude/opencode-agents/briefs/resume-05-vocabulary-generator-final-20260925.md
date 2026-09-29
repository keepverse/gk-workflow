# Resume P1 05 final — generated vocabulary and closure

The first vocabulary lane was stopped before edits because its broad `gk-core/tests/FusionRpg.Core.Tests/**` fence overlapped active Delve and battle lanes. This successor narrows Core tests to the directly affected atom/passive-tree files below. The generator-first rule is unchanged: never hand-edit emitted data; fix the generator/mirror and regenerate.

## Allowed paths

- `gk-forge/tools/FamilyExpandGen/**`
- `gk-forge/tools/PassiveTreeRosterGen/**`
- `gk-data/packs/fusion/data/seed/passive-tree/vocabulary.json`
- `gk-data/packs/fusion/data/seed/atoms/generated/**`
- `gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests/**`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/TreeAtomSourceParityTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/Adoption/PassiveTreeMechanismRoundRecomposeTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/EquipAtomSourceIdTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Match/UniqueEquipmentAtomMappingTests.cs`
- `tasks/reports/resume-05-vocabulary-generator-final-20260925.md`

## Requirements

1. Make `PassiveTreeRosterGen --atom-vocab-check` agree with the live registries; regenerate the mirror through the generator, never hand-edit emitted JSON.
2. Make FamilyExpandGen refusal, pool, version-selection, and provenance closure explicit; add fixtures for v10/version ordering and durable refusal/reconciliation behavior.
3. Identify stale real-corpus fixtures and update them through their owning fixture/generator path; do not weaken a vocabulary test.
4. If `.github/workflows/ci.yml` is actively owned by another lane, do not touch it; write a precise handoff row naming the missing CI command and owner.
5. Run both `--check` modes and focused restored tests. Report any remaining registry/CI owner blocker explicitly.

No subagent, alternate model, commit, push, or merge. Write the exact disk-backed report and marker; leave the tree dirty for manager review.

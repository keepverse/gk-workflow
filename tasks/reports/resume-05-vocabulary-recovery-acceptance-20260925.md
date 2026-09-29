# Manager acceptance review — FamilyExpand manifest recovery

**Source lane:** `resume-05-vocabulary-recovery-20260925` (worker result preserved; no direct merge)
**Review worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/review-vocabulary-recovery-20260925`
**Status:** **PARTIAL until exact-SHA clean checkout; scoped generator recovery is green**

## Root cause and repair

The prior draft emitted refusal rows in `_family-expand.manifest.json` with an empty `kind`. Existing `AtomSeedFile`/Core consumers correctly rejected the file as `UnknownKind`. The recovery changes the generator/schema layer to emit a valid closed seed envelope (`affix`, zero rows) while retaining refusal/provenance records and hashes, then regenerates the manifest and vocabulary mirror through the owning tools. No emitted JSON was hand-edited.

## Independent evidence

```text
dotnet run --project gk-forge/tools/FamilyExpandGen -- --check
# clean; provenance/output hashes and refusal manifest match; exit 0

dotnet run --project gk-forge/tools/PassiveTreeRosterGen -- --atom-vocab-check
# live registries agree; exit 0

dotnet test gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests
# 25 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.Core.Tests --filter
  "FullyQualifiedName~TraitMigrationParityTests|FullyQualifiedName~EventDeckGoldensTests|FullyQualifiedName~EventSeedContentTests|FullyQualifiedName~TreeAtomSourceParityTests|FullyQualifiedName~PassiveTreeMechanismRoundRecomposeTests|FullyQualifiedName~EquipAtomSourceIdTests|FullyQualifiedName~UniqueEquipmentAtomMappingTests"
# 52 passed, 0 failed, 0 skipped; exit 0

gk-core/scripts/guard-generated-seed.py
# clean; exit 0
gk-core/scripts/guard-test-substrate.py
# OK; exit 0
```

The exact generator output changed only the owned generated vocabulary/manifest surfaces plus their generators/tests. The prior failing Core consumer selection is now green.

## Known handoffs and limits

- `TreeBinder --check` still fails on the existing passive-tree corpus/registry mismatch (many refused rows and missing atom/pool references). That output is outside this fence and was not regenerated or hand-edited here.
- The broad executable-path `verify-change` run over-selected split Core projects and stopped on an MSB3021 artifact-copy Access Denied; it is not counted as a green aggregate. The focused 52-test replacement is the accepted evidence.
- The CI owner still needs an explicit `PassiveTreeRosterGen --atom-vocab-check` step if that topology row remains outside the merged CI change.
- No browser/live/model run was performed.

## Remaining requirements

1. Commit the reviewed generator/test/generated-output set and this report at an exact SHA.
2. Run generator checks, focused tests, and guards from a clean detached checkout.
3. Validate/write the exact-SHA artifact and merge only that SHA.
4. Route TreeBinder and CI/fixture/Core handoffs to their owners; do not expand this vocabulary fence.

<<<REPORT {"status":"partial","summary":"Manager independently verified the generator-first manifest recovery: both generator checks, 25 generator tests, 52 previously failing Core consumer tests, and seed/test-substrate guards pass. The emitted manifest now uses a valid closed seed envelope and preserves refusal/provenance data. TreeBinder drift, broad split-Core artifact-copy failure, and CI wiring remain explicit handoffs; exact-SHA clean-checkout acceptance is pending.","changed_files":["gk-data/packs/fusion/data/seed/passive-tree/vocabulary.json","gk-data/packs/fusion/data/seed/atoms/generated/_family-expand.manifest.json","gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests/FusionRpg.PassiveTreeRosterGen.Tests.csproj","gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests/FamilyExpandClosureTests.cs","gk-forge/tests/FusionRpg.PassiveTreeRosterGen.Tests/RosterMirrorTests.cs","gk-forge/tools/FamilyExpandGen/FamilyExpandGen.csproj","gk-forge/tools/FamilyExpandGen/FamilyExpandManifest.cs","gk-forge/tools/FamilyExpandGen/FamilyExpandPoolCatalog.cs","gk-forge/tools/FamilyExpandGen/Program.cs","gk-forge/tools/FamilyExpandGen/VersionedInputFile.cs","gk-forge/tools/PassiveTreeRosterGen/AtomVocabCheck.cs","gk-forge/tools/PassiveTreeRosterGen/Program.cs","tasks/reports/resume-05-vocabulary-recovery-acceptance-20260925.md"],"verification":["FamilyExpandGen --check passed","PassiveTreeRosterGen --atom-vocab-check passed","25 PassiveTreeRosterGen tests passed","52 Core manifest-consumer tests passed","guard-generated-seed passed","guard-test-substrate passed","git diff --check passed"],"open_issues":["exact-SHA clean checkout and artifact are not yet created","TreeBinder --check remains red outside this fence","broad verify-change stopped on MSB3021 artifact copy Access Denied","CI atom-vocab command and stale fixture/Core pool handoffs remain open","no live/browser proof"],"next_steps":["commit exact reviewed SHA","clean-checkout generator/focused verification and artifact","merge exact SHA","route TreeBinder/CI/fixture/Core handoffs","keep generated-data ownership with the generator"]} REPORT>>>

# SSH5.3 — Core.Tests that mean "the shipped tuning" read `SocketTuningFiles.Current`

## What changed

- The five Core test files named by the row (`BaseTypeCorpusTests`, `SocketGeometryTests`,
  `StrainSpliceGridTests`, plus `RarityBudgetKeysTests`/`SocketAllowanceTests` which carried only
  comment mentions) now read the constant. `CombinationCorpusTests` and `ComboContainerBuildTests` —
  both newer Core tests that SSH5.2's guard allowlisted — were converted too, so every Core code
  literal is gone. Comments that name `v1` as history stay (the guard allows comment lines).
- `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` — the five Core entries removed
  from the temporary allowlist (it can only shrink; leaving a converted file on it fails the guard).

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| mechanical literal → constant in the five files | `dotnet test tests.FusionRpg.Core.Tests --filter "FullyQualifiedName~BaseTypeCorpus\|FullyQualifiedName~RarityBudgetKeys\|FullyQualifiedName~SocketAllowance\|FullyQualifiedName~SocketGeometry\|FullyQualifiedName~StrainSpliceGrid\|FullyQualifiedName~CombinationCorpus\|FullyQualifiedName~ComboContainerBuild"` | 94 passed, 0 failed |
| guard allowlist shrank; still no code literal | `dotnet test tests.FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"` | 2 passed, 0 failed |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

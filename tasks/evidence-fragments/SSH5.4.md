# SSH5.4 — Data.Tests + the first Server.Tests batch read `SocketTuningFiles.Current`

## What changed

- Converted the row's five files — `gk-core/tests/FusionRpg.Data.Tests/Items/ItemCardStoreTests.cs`,
  `ItemSocketStoreTests.cs`, `gk-core/tests/FusionRpg.Server.Tests/GemTierTests.cs`,
  `ItemCardEndpointsTests.cs`, `ItemEquipEndpointsTests.cs` — plus the two other Server code literals
  SSH5.2's guard allowlisted (`BaseTypeSocketMaxCorpusTests.cs`, `CombinationImportTests.cs`) to
  `SocketTuningFiles.Current`. No behaviour change: the same file loads.
- `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` — the seven allowlist entries
  removed; the allowlist now holds only SSH5.5's files.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| literal → constant swap | `dotnet test tests.FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemCardStore\|FullyQualifiedName~ItemSocketStore"` | 34 passed, 0 failed |
| Server batch | `dotnet test tests.FusionRpg.Server.Tests --filter "FullyQualifiedName~GemTier\|FullyQualifiedName~ItemCardEndpoints\|FullyQualifiedName~ItemEquipEndpoints"` | 68 passed, 0 failed |
| guard allowlist shrank, still no code literal | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"` | 2 passed, 0 failed |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

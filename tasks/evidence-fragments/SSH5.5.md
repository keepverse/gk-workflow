# SSH5.5 — remaining Server.Tests read `SocketTuningFiles.Current`; allowlist empty

## What changed

- Converted `ItemInsertElementTests.cs`, `ItemPreviewEndpointsTests.cs`,
  `ItemWorkbenchEndpointsTests.cs` (the row's three) plus the other remaining Server code literals
  (`ItemWorkbenchAssuranceTests.cs`, `ItemWorkbenchSpeciesWiringTests.cs`, `SocketHostForTests.cs`) to
  `SocketTuningFiles.Current`. No behaviour change.
- `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` — the temporary allowlist is now
  EMPTY. Every "shipped tuning" reader in `src/`, `tools/` and `tests/` names the constant; only
  comment lines may still name a revision, and the v1-history allowlist has no members today.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| literal → constant swap | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemInsertElement\|FullyQualifiedName~ItemPreviewEndpoints\|FullyQualifiedName~ItemWorkbenchEndpoints\|FullyQualifiedName~ItemWorkbenchAssurance\|FullyQualifiedName~ItemWorkbenchSpeciesWiring\|FullyQualifiedName~SocketHostFor"` | 96 passed, 0 failed |
| guard green with an empty allowlist | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"` | 2 passed, 0 failed |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

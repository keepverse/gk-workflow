# SSH5.2 — `SocketTuningFiles.Current`; every production reader names it; literal-scan guard

## What changed

- `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs` (new) — `Current = "sockets.v1.json"`, a
  filename, not a file read (Core reads no file). The class is where a later domain's constant lands.
- `gk-core/src/FusionRpg.Server/Program.cs:366` and `gk-forge/tools/ItemSeedValidator/Checks/SocketMaxCheck.cs` (path +
  two messages) now name `SocketTuningFiles.Current`; `StrainSpliceTuning.cs`'s min-tier-plan message
  too. Behaviour unchanged: the same file loads.
- `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` (new) —
  `No_reader_names_a_sockets_revision_literal` scans `src/`, `tools/`, `tests/` for a
  `sockets.v{n}.json` literal in code, allows the constant file and any comment line, and carries a
  temporary allowlist of the test files SSH5.3–SSH5.5 convert (a converted file left on the list is
  itself a failure). `The_one_constant_is_what_the_server_and_the_validator_name` proves the two
  production readers.
- Citations into `SocketMaxCheck.cs` re-anchored (`:51`→`:52`, `:42`→`:43`).

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| guard scans and passes (allowlist = the not-yet-converted tests) | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"` | 2 passed, 0 failed |
| server + validator read the constant | same run / second test | `SocketTuningFiles.Current` in both; no `"sockets.v` literal left |
| validator behaviour unchanged | `dotnet run --project gk-forge/tools/ItemSeedValidator` | exit 1 with 41 PRE-EXISTING errors (`PartitionMetaMismatch`/`RegistryVersionBehind` on `sets/species/*`), none `SocketMax*`/`SocketCeiling*` — the socket check loaded the table and found nothing |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

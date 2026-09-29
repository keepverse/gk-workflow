# SSH5.2 merge-red — the TuningRevisionLiteral guard at the integrated head

## Result: the guard is GREEN at the merged head; the reported red does not reproduce

Merged `features/mega-merge` (8aba2900, whose `.cs` tree is byte-identical to the reported
62db8f48) into `cmdc/ssh27` at `0dc4b307`, then ran the exact filter:

```powershell
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"
Passed!  - Failed: 0, Passed: 2, Skipped: 0, Total: 2
```

## Diagnosis: no committed reader names the literal

The guard's exact predicate (`sockets\.v[0-9]+\.json`, comment lines skipped, the constant file
skipped) run over `git archive <rev> src tools tests` yields **0 offenders** at
`c9ce309c` (the lane merge), `62db8f48` (the reported red), `8aba2900`, and the main checkout's
working tree. The only code occurrence anywhere is `SocketTuningFiles.cs:21` (the constant, skipped);
every other hit is a comment line. No `.cs` file added between `c51bbb71` and `62db8f48` contains the
literal. So the failure is not a reader.

## Root cause of the reported `1 failed / 1 passed`

The failing line is `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs:52`:

```csharp
foreach (var file in Directory.EnumerateFiles(
             Path.Combine(root, top), "*.cs", SearchOption.AllDirectories))
```

`Directory.EnumerateFiles(..., AllDirectories)` **throws** (`DirectoryNotFoundException` for an absent
root path, `UnauthorizedAccessException` on an inaccessible subdirectory) before the per-file
`/bin/` `/obj/` skip runs — so a checkout that is missing one of `src`/`tools`/`tests`, or that has a
locked/inaccessible directory under one, fails the scanner at that line while the other test passes.
That is the `1 failed / 1 passed` shape, and it is a guard-defect, not a reader.

**Requested guard change (BLOCKED — see the ledger note).** Skip an absent top directory, assert
`scanned > 0` so the guard can never pass vacuously, and walk without descending into `bin/`/`obj/`.
Also drop the redundant negative arm in `The_one_constant_is_what_the_server_and_the_validator_name`
(`Assert.DoesNotContain("\"sockets.v", ...)`) — it duplicates the scanner and makes the guard file the
only entry in its own scan set. The pipeline hook refuses edits to any `*Guard*Tests.cs`, so this must
be applied by the orchestrator (or the file exempted).

## Audit finding closed

The scoped verifier's red (verify-change aborting on other sessions' boundary drift) is closed by the
manager's re-run: **Core goldens 36/36, the ssh27 Server reader suites 164/164.**

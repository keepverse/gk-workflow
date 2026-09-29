# ISG1 — stop scanning the combination still-blocked report as seed content

Sub-agent task `item-seed-gen` (worktree `cmdc-item-seed-gen`). The brief's own findings (the
coordinator's "62") were already closed in this branch's ancestry
(`e1d9103ee`/`12175b3db`/`782c74827`/`39fbed34a`/`3a59c51f7`/`c896da351`); what was live at the
worktree base `e0f1375d` is the 41 findings the earlier lane recorded as other lanes' content.
ISG1 clears the four that are a validator-scope defect, not content.

## What changed

`gk-forge/tools/ItemSeedValidator/Validator.cs` — `Discover` now skips pipeline artefacts by filename suffix
(`NonContentFileSuffixes = { ".ledger.json", "-still-blocked.json" }`), the exact analogue of
cause 7's `*.ledger.json` rule (`90d8c26d2`). `combinations/combination-still-blocked.json` is the
R13 report `_persist_combination_still_blocked_report` writes beside the run ledger
(`spec-combination-regen.md` "Still-blocked cells"): `schemaVersion` + `rows` (each with
`gridId`/`blockedReason`/`survivedReruns`), no `entries`, no `kind`, no `_meta`. It was being read
as an authored seed file, producing `EntriesMissing`, `KindMissing`, `MetaMissing`, `UnknownKey`.

No content or generator file changed.

## Verification

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The four artefact findings are gone | `dotnet run --project gk-forge/tools/ItemSeedValidator` | FAIL — 41 errors before, 37 after; `(unassigned)` 6 -> 2 | stdout below |
| Files scanned (the report no longer counted) | same command | 1014 -> 1013 | stdout |
| Existing discovery tests still green | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests` | pass (see ISG4 run) | `ValidatorDiscoverTests.cs` |

No new C# test accompanies this change: the validator's own test project lives under `tests/**`,
which is outside this session's allowed paths. The suffix rule is covered by the real `dotnet run`
reading above and by the existing `A_ledger_file_is_never_discovered_regardless_of_directory` test,
which exercises the identical code path.

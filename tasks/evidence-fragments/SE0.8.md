# SE0.8 — Debt ledger: `solid` kind and rows

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `solid` documented; the kind pin moves 3 → 4 with its reason | `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj -c Release --verbosity minimal --filter "FullyQualifiedName~StubRegisterTests"` | `Passed!  - Failed: 0, Passed: 7, Skipped: 0, Total: 7`; `allowed` is `{stub, dark, unowned, solid}` and the comment names SE0.8 as `unowned`'s successor | gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs |
| rows for atk, `CommanderId`, tuning pollution, commit-policy and god files, ids = current max + 1… | read `docs/architecture/stub-register.md` Rows table | max id was `SR-19`, so the new rows are `SR-20` (atk), `SR-21` (`CommanderId`), `SR-22` (tuning pollution), `SR-23` (commit-policy), `SR-24` (god files) — each with all six fields | docs/architecture/stub-register.md |
| every new row's `where` points at a real file | `Test-Path` on the five cited paths | 5 × `True` (`DerivedStatChannels.cs`, `CommanderId.cs`, `loopwarntest13c4c662.v1.json`, `policy.json`, `RpgStore.cs`) | — |
| the figures are measured, not guessed | line count + file scan | `RpgStore.cs` 3,979 lines; 8 C# files over 1,500; four `loopwarntest*.v{1,2}.json`; `DerivedStatChannels.cs:8` and `CommanderId.cs:20` grep-confirmed | — |
| Phase 1's close and T4.4 S7 are in Hand-off as owner items | read `docs/architecture/stub-register.md:157-165` | both recorded, neither ticked | docs/architecture/stub-register.md |
| the new fact plus its falsifier | the StubRegisterTests run above | `Every_open_solid_row_waits_on_a_module_of_the_enforcement_program` and `..._falsifier_a_row_waiting_on_no_module_is_refused` green | gk-core/tests/FusionRpg.Guard.Tests/StubRegisterTests.cs |
| the append rule states how a `solid` row closes | read `docs/architecture/stub-register.md:175-177` | struck through with the closing SHA, never deleted | docs/architecture/stub-register.md |

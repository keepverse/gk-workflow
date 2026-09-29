# BCU8.4 evidence — `EnsureColumn` tolerates only the duplicate-column error

Program `backlog-clean-up` row BCU8.4 (= `data-test-substrate` BU1). Lane `cmdc/bcu8-4`, one commit:
`fix(data): EnsureColumn reads the column set and tolerates only the duplicate-column error (BCU8.4)`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Planted violation bites before the fix (blanket `catch { }` in place; `internal` visibility only, so the test compiles) | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --nologo --filter "FullyQualifiedName~EnsureColumnTests"` | `Failed: 2, Passed: 2, Skipped: 0, Total: 4` — both propagation cases report `Assert.Throws() Failure: No exception was thrown` | this fragment |
| Both halves pass with the narrowed catch | same filter | `Failed: 0, Passed: 5, Skipped: 0, Total: 5, Duration: 416 ms` | `gk-core/tests/FusionRpg.Data.Tests/Sqlite/EnsureColumnTests.cs` |
| Existing column tolerated; added column read back | `An_existing_column_is_tolerated_and_the_added_column_reads_back_with_its_default` | old-schema row reads back `0` for the added `theta`; the re-run leaves exactly `1` `theta` column | same file |
| A *different* failure propagates | `An_unknown_table_propagates_instead_of_being_swallowed`, `A_malformed_definition_propagates_instead_of_being_swallowed` | both `Assert.Throws<SqliteException>` pass | same file |
| Tolerated shape pinned to the real driver error (not to a code — all three failure shapes are `SqliteErrorCode == 1`) | `The_tolerated_shape_is_exactly_the_duplicate_column_error` | `IsDuplicateColumnError` true for the real `duplicate column name: theta`, false for a wrong column name and for `no such table` | same file |
| Real boot path still layers the schema over an old one | `pwsh -NoProfile -ExecutionPolicy Bypass -Command "& './scripts/verify-change.ps1' -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs','gk-core/tests/FusionRpg.Data.Tests/Sqlite/EnsureColumnTests.cs') -AllowUnscoped"` | plan `data-fallback` + `data-tests-fallback`; `DAL GUARD OK`; `TEST SUBSTRATE GUARD OK`; `TEST-SHARDED OK: 4 shards, 1728 tests, no overlap` (includes `DataTestStoreTests.CreateWithPreInitHot_seeds_a_legacy_schema_that_Init_migrates_in_memory`) | — |
| `guard-test-substrate.py` | `python gk-core/scripts/guard-test-substrate.py` | exit 0 — `TEST SUBSTRATE GUARD OK` | — |
| `guard-dal.ps1` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-dal.ps1` | exit 0 — `DAL GUARD OK` | — |
| Row ticked, id present after the edit | `grep -n "^\- \[x\] \*\*BCU8.4" tasks/backlog-clean-up-todo.md` | line 763, `- [x] **BCU8.4 — …**` (3 `BCU8.4` matches in the file) | `tasks/backlog-clean-up-todo.md` |

**Deviation, stated rather than hidden:** the brief's `-Session bcu8-4` form does not run —
`scripts/verify-change.ps1:98` throws `session record not found: bcu8-4`, and no
`tasks/sessions/bcu8-4.json` exists anywhere (`tasks/sessions/**` is outside this lane's fence, so the
record was not written by this lane). The identical plan was run with `-AllowUnscoped`; the manager owes
either the record (with these paths in it) or an erratum.
